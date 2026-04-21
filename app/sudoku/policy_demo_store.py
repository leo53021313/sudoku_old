# app/sudoku/policy_demo_store.py
# -*- coding: utf-8 -*-
"""
PolicyDemoStore：Phase 3 的自我改善回路。

當 policy 自己解出一道題（success=True，且該 episode 超過半數步驟由
policy 而非 teacher 主導），把 policy-only steps 存入 ring buffer。

下一輪 _ppo_update() 從這裡採樣，計算 soft BC loss（weight=demo_weight），
形成正反饋飛輪：policy 越強 → 存越多優質示範 → BC 強化成功行為。
"""

import threading
import torch


class PolicyDemoStore:
    """
    Thread-safe ring buffer，儲存成功 policy episode 的 (state, action) pairs。

    Parameters
    ----------
    capacity    : int   ring buffer 大小（步數）
    in_channels : int   state tensor 的 channel 數（必須與 RolloutBuffer 一致）
    demo_weight : float soft BC loss 的權重（預設 0.30）
    min_ratio   : float episode 中 policy steps 佔比的最低門檻（預設 0.50）
    """

    def __init__(
        self,
        capacity:    int   = 2048,
        in_channels: int   = 8,
        demo_weight: float = 0.30,
        min_ratio:   float = 0.50,
    ):
        self.capacity    = capacity
        self.in_channels = in_channels
        self.demo_weight = demo_weight
        self.min_ratio   = min_ratio

        self._lock = threading.Lock()
        self._ptr  = 0
        self._size = 0

        self.states  = torch.zeros(capacity, in_channels, 9, 9, dtype=torch.float32)
        self.actions = torch.zeros(capacity, dtype=torch.long)

    # ── 儲存一個成功 episode 的 policy steps ──────────────────────────────

    def try_add_episode(
        self,
        states:       list[torch.Tensor],
        actions:      list[int],
        total_steps:  int,
    ) -> int:
        """
        嘗試把 policy-only steps 加入 store。

        Parameters
        ----------
        states      : policy steps 的 state tensors（CPU）
        actions     : 對應動作 index
        total_steps : 整個 episode 的總步數（用於計算 policy ratio）

        回傳：實際加入的步數（0 表示未加入）。
        """
        n = len(states)
        if n == 0 or total_steps == 0:
            return 0
        if n / total_steps < self.min_ratio:
            return 0   # policy 佔比不足，示範品質不夠

        with self._lock:
            for s, a in zip(states, actions):
                self.states[self._ptr]  = s.cpu() if s.device.type != "cpu" else s
                self.actions[self._ptr] = int(a)
                self._ptr  = (self._ptr + 1) % self.capacity
                self._size = min(self._size + 1, self.capacity)
        return n

    # ── 採樣（PPO update 時使用） ─────────────────────────────────────────

    def sample(
        self,
        n:      int,
        device: torch.device,
    ) -> tuple[torch.Tensor, torch.Tensor] | None:
        """
        隨機採樣 n 個 steps。

        回傳 (states [n,C,9,9], actions [n]) 或 None（store 太空）。
        要求 store 至少有 n//2 個步驟才採樣，避免高度重複。
        """
        with self._lock:
            sz = self._size
        if sz < max(n // 2, 1):
            return None
        actual_n = min(n, sz)
        idx      = torch.randint(sz, (actual_n,))
        with self._lock:
            s = self.states[idx].clone()
            a = self.actions[idx].clone()
        return s.to(device, non_blocking=True), a.to(device, non_blocking=True)

    # ── 狀態查詢 ──────────────────────────────────────────────────────────

    @property
    def size(self) -> int:
        with self._lock:
            return self._size

    # ── Checkpoint 支援 ───────────────────────────────────────────────────

    def state_dict(self) -> dict:
        with self._lock:
            return {
                "states":  self.states[:self._size].clone(),
                "actions": self.actions[:self._size].clone(),
                "ptr":     self._ptr,
                "size":    self._size,
            }

    def load_state_dict(self, d: dict) -> None:
        states  = d.get("states")
        actions = d.get("actions")
        if states is None or actions is None:
            return
        n = min(len(states), self.capacity)
        with self._lock:
            self.states[:n]  = states[:n]
            self.actions[:n] = actions[:n]
            self._ptr        = d.get("ptr", n % self.capacity)
            self._size       = d.get("size", n)
