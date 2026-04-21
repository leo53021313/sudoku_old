# app/sudoku/phase_manager.py
# -*- coding: utf-8 -*-
"""
PhaseManager：管理訓練階段（1→2→3）的轉換。

  Phase 1 (Bootstrap) : MRV 主導，BC 強，policy 學習基礎模式
  Phase 2 (Transfer)  : MRV 餘弦衰減，BC 與 PPO 競爭
  Phase 3 (RL-only)   : Policy 主導，BC 歸零，PolicyDemoStore 啟動

轉換觸發：success_rate（performance-based）優先，step count 作為 safety backstop。
"""

import math
import threading
from collections import deque


class PhaseConfig:
    """Phase 轉換的所有閾值與時間點，從 config 讀取後建立。"""

    def __init__(
        self,
        phase1_steps: int   = 30_000,
        phase2_steps: int   = 90_000,
        tau1: float         = 0.30,
        tau2: float         = 0.65,
        mrv_init: float     = 0.90,
        mrv_floor: float    = 0.05,
    ):
        self.T1        = phase1_steps
        self.T2        = phase2_steps
        self.tau1      = tau1
        self.tau2      = tau2
        self.mrv_init  = mrv_init
        self.mrv_floor = mrv_floor


class PhaseManager:
    """
    追蹤當前訓練 phase 並提供對應的 MRV 機率與 BC 衰減指數。

    MRV 曲線（分段餘弦）：
      Phase 1: 0.90 → 0.40  (cosine, over T1 steps)
      Phase 2: 0.40 → 0.10  (cosine, over T2-T1 steps)
      Phase 3: mrv_floor     (fixed)

    BC 衰減指數 β：
      Phase 1: 0.5  （BC 衰減比 MRV 慢，保持 imitation 主導）
      Phase 2: 1.0  （BC 與 MRV 同速）
      Phase 3: ∞    （BC 強度降為 0）
    """

    PHASE_1 = 1
    PHASE_2 = 2
    PHASE_3 = 3

    def __init__(self, cfg: PhaseConfig):
        self._cfg              = cfg
        self._phase            = self.PHASE_1
        self._success_window   = deque(maxlen=100)
        self._lock             = threading.Lock()

    # ── 記錄每個 episode 結果，回傳是否剛發生 phase transition ──────────────

    def record_episode(self, success: bool, mrv_step: int) -> bool:
        with self._lock:
            self._success_window.append(float(success))
            return self._maybe_advance(mrv_step)

    def _maybe_advance(self, mrv_step: int) -> bool:
        sr = self._rolling_success()
        if self._phase == self.PHASE_1:
            if sr >= self._cfg.tau1 or mrv_step >= self._cfg.T1:
                self._phase = self.PHASE_2
                print(f"[Phase] 1 → 2  success={sr:.2%}  step={mrv_step:,}")
                return True
        elif self._phase == self.PHASE_2:
            if sr >= self._cfg.tau2 or mrv_step >= self._cfg.T2:
                self._phase = self.PHASE_3
                print(f"[Phase] 2 → 3  success={sr:.2%}  step={mrv_step:,}")
                return True
        return False

    # ── MRV 機率（分段餘弦） ───────────────────────────────────────────────

    def mrv_prob(self, mrv_step: int) -> float:
        cfg = self._cfg
        with self._lock:
            phase = self._phase

        if phase == self.PHASE_1:
            frac  = min(1.0, mrv_step / max(cfg.T1, 1))
            cos_w = 0.5 * (1.0 + math.cos(math.pi * frac))
            # 0.90 → 0.40  (base is 0.40, not mrv_floor)
            return 0.40 + (cfg.mrv_init - 0.40) * cos_w

        if phase == self.PHASE_2:
            t_rel = max(0, mrv_step - cfg.T1)
            span  = max(cfg.T2 - cfg.T1, 1)
            frac  = min(1.0, t_rel / span)
            cos_w = 0.5 * (1.0 + math.cos(math.pi * frac))
            # 0.40 → 0.10  (base is 0.10, not mrv_floor)
            return 0.10 + (0.40 - 0.10) * cos_w

        # PHASE_3
        return cfg.mrv_floor

    # ── BC 衰減指數 ───────────────────────────────────────────────────────

    def bc_exponent(self) -> float:
        with self._lock:
            return {
                self.PHASE_1: 0.5,
                self.PHASE_2: 1.0,
                self.PHASE_3: 999.0,   # effectively 0 bc
            }[self._phase]

    # ── 狀態查詢 ──────────────────────────────────────────────────────────

    @property
    def phase(self) -> int:
        with self._lock:
            return self._phase

    def rolling_success(self) -> float:
        with self._lock:
            return self._rolling_success()

    def _rolling_success(self) -> float:
        if not self._success_window:
            return 0.0
        return sum(self._success_window) / len(self._success_window)

    # ── Checkpoint 支援 ───────────────────────────────────────────────────

    def state_dict(self) -> dict:
        with self._lock:
            return {
                "phase":           self._phase,
                "success_window":  list(self._success_window),
            }

    def load_state_dict(self, d: dict) -> None:
        with self._lock:
            self._phase = d.get("phase", self.PHASE_1)
            self._success_window = deque(
                d.get("success_window", []), maxlen=100
            )
