# app/sudoku/torch_agent.py
# -*- coding: utf-8 -*-
"""
TorchAgent v4 — Bug Fixes + 改進版

★ 與 v3 相比的修正：

[Fix 1] MRV log_prob 錯誤（嚴重 Bug）
  舊版：MRV 選的 action 的 log_prob = log(1/n_legal)（均勻假設）
        → PPO importance ratio 完全錯誤，policy 學到的是假信號。
  新版：即使 MRV 決定選哪個 action，log_prob 仍從 policy network 的 softmax 取得。
        → old_log_prob 是真實 policy 概率，PPO ratio 正確。

[Fix 2] _mrv_step 計數單位錯誤
  舊版：在 finish_episode() 呼叫，每個 episode 只計 1 次。
        設 mrv_decay_steps=200000 意指 200000 episodes，幾乎不會衰減。
  新版：在 select_action() 呼叫，每個 action 計 1 次。
        200000 steps ÷ ~30 steps/episode ≈ 6667 episodes 後完成衰減。

[Fix 3] RolloutBuffer push 覆寫問題
  舊版：buffer 滿後繼續 push（circular overwrite），
        導致 is_ready 觸發時 buffer 內容已被舊 episode 的後半段覆蓋。
  新版：buffer 滿後停止 push，等待 _ppo_update() 重置後再填。

[Fix 4] GAE bootstrap 缺少 last_value
  舊版：rollout 最後一步的 next_val 硬設為 0.0。
        若 rollout 在 mid-episode 結束（done=False），Value 低估，
        導致後面幾步的 advantage 偏負。
  新版：RolloutBuffer.set_last_value() 讓 finish_episode 傳入
        最後一個 pending_state 的 V(s) 作為 bootstrap。

[Fix 5] dead_end commit_step 遺漏（main_train.py 的 Bug）
  → 見 main_train_fixed.py 的修改說明。

[Fix 6] finish_episode 中移除 _mrv_step 計數
  → 改至 select_action。
"""

import os
import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
from torch.amp import GradScaler, autocast


# ═══════════════════════════════════════════════════════
# Running Statistics
# ═══════════════════════════════════════════════════════

class RunningMeanStd:
    def __init__(self, epsilon: float = 1e-4):
        self.mean  = 0.0
        self.var   = 1.0
        self.count = epsilon

    def update(self, x: np.ndarray):
        x = np.asarray(x, dtype=np.float64).flatten()
        n = len(x)
        if n == 0: return
        batch_mean = x.mean()
        batch_var  = x.var()
        new_count  = self.count + n
        delta      = batch_mean - self.mean
        self.mean += delta * n / new_count
        m_a = self.var * self.count
        m_b = batch_var * n
        self.var = (m_a + m_b + delta ** 2 * self.count * n / new_count) / new_count
        self.count = new_count

    @property
    def std(self) -> float:
        return float(np.sqrt(max(self.var, 1e-8)))

    def normalize(self, x: np.ndarray, clip: float = 10.0) -> np.ndarray:
        normed = (np.asarray(x, dtype=np.float32) - self.mean) / self.std
        return np.clip(normed, -clip, clip)


# ═══════════════════════════════════════════════════════
# Network（與 v3 相同）
# ═══════════════════════════════════════════════════════

class ConstraintHead(nn.Module):
    def __init__(self, cell_dim: int, head_dim: int):
        super().__init__()
        self.fc   = nn.Linear(cell_dim, head_dim)
        self.gate = nn.Linear(cell_dim * 9, head_dim)

    def forward(self, cells: torch.Tensor) -> torch.Tensor:
        B     = cells.size(0)
        local = F.relu(self.fc(cells))
        ctx   = self.gate(cells.reshape(B, -1)).unsqueeze(1)
        return local + torch.sigmoid(ctx) * local


class SudokuPPONet(nn.Module):
    def __init__(self, in_channels: int = 8, cell_dim: int = 128, head_dim: int = 64):
        super().__init__()
        self.in_channels = in_channels
        self.cell_dim    = cell_dim
        self.head_dim    = head_dim

        self.cell_embed = nn.Sequential(
            nn.Linear(in_channels, cell_dim),
            nn.LayerNorm(cell_dim),
            nn.ReLU(),
            nn.Linear(cell_dim, cell_dim),
            nn.LayerNorm(cell_dim),
            nn.ReLU(),
        )
        self.row_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])
        self.col_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])
        self.box_heads = nn.ModuleList([ConstraintHead(cell_dim, head_dim) for _ in range(9)])

        fused = head_dim * 3
        self.policy_head = nn.Sequential(
            nn.Linear(fused, 128), nn.ReLU(), nn.Linear(128, 9),
        )
        self.value_head = nn.Sequential(
            nn.Linear(cell_dim, 128), nn.ReLU(), nn.Linear(128, 1),
        )

    def forward(self, x: torch.Tensor):
        B    = x.size(0)
        emb  = self.cell_embed(x.permute(0, 2, 3, 1).reshape(B, 81, self.in_channels))
        emb_ = emb.reshape(B, 9, 9, self.cell_dim)

        row_out = torch.stack([self.row_heads[r](emb_[:, r]) for r in range(9)], dim=1)
        col_out = torch.zeros(B, 9, 9, self.head_dim, device=x.device)
        for c in range(9):
            col_out[:, :, c, :] = self.col_heads[c](emb_[:, :, c, :])
        box_out = torch.zeros(B, 9, 9, self.head_dim, device=x.device)
        for b in range(9):
            br, bc = (b // 3) * 3, (b % 3) * 3
            out = self.box_heads[b](emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim))
            box_out[:, br:br+3, bc:bc+3, :] = out.reshape(B, 3, 3, self.head_dim)

        fused = torch.cat([
            row_out.reshape(B, 81, self.head_dim),
            col_out.reshape(B, 81, self.head_dim),
            box_out.reshape(B, 81, self.head_dim),
        ], dim=-1)

        logits = self.policy_head(fused).reshape(B, 729)
        value  = self.value_head(emb.mean(dim=1))
        return logits, value


# ═══════════════════════════════════════════════════════
# Rollout Buffer（修正版）
# ═══════════════════════════════════════════════════════

class RolloutBuffer:
    """
    ★ Fix 3：push 時若 buffer 已滿，直接 return，不覆寫舊資料。
    ★ Fix 4：新增 last_value（GAE bootstrap）和 set_last_value()。
    """

    def __init__(self, capacity: int, in_channels: int, device: torch.device):
        self.capacity    = capacity
        self.in_channels = in_channels
        self.device      = device
        self._ptr        = 0
        self._full       = False
        self.last_value  = 0.0  # ★ Fix 4: bootstrap value for truncated rollout

        self.states    = torch.zeros(capacity, in_channels, 9, 9, dtype=torch.float32)
        self.actions   = torch.zeros(capacity, dtype=torch.long)
        self.log_probs = torch.zeros(capacity, dtype=torch.float32)
        self.values    = torch.zeros(capacity, dtype=torch.float32)
        self.rewards   = torch.zeros(capacity, dtype=torch.float32)
        self.dones     = torch.zeros(capacity, dtype=torch.float32)

    def push(self, state, action, log_prob, value, reward, done):
        # ★ Fix 3：滿了就停，不覆寫
        if self._full:
            return

        i = self._ptr
        self.states[i]    = state.cpu()
        self.actions[i]   = action
        self.log_probs[i] = float(log_prob)
        self.values[i]    = float(value)
        self.rewards[i]   = float(reward)
        self.dones[i]     = float(done)
        self._ptr += 1
        if self._ptr >= self.capacity:
            self._full = True

    def set_last_value(self, v: float):
        """★ Fix 4：設定 bootstrap value，在 PPO update 前呼叫。"""
        self.last_value = float(v)

    @property
    def is_ready(self) -> bool:
        return self._full

    def reset(self):
        self._ptr       = 0
        self._full      = False
        self.last_value = 0.0

    def size(self) -> int:
        return self.capacity if self._full else self._ptr

    def compute_gae_and_returns(
        self,
        gamma: float,
        gae_lambda: float,
        return_rms: RunningMeanStd,
        normalize_returns: bool = True,
    ):
        T = self.size()
        rewards = self.rewards[:T].numpy()
        values  = self.values[:T].numpy()
        dones   = self.dones[:T].numpy()

        advantages = np.zeros(T, dtype=np.float32)
        gae = 0.0
        for t in reversed(range(T)):
            if t + 1 < T:
                next_val = values[t + 1]
            else:
                # ★ Fix 4：用 last_value 做 bootstrap（不再硬設 0）
                next_val = self.last_value
            next_val *= (1.0 - dones[t])
            delta = rewards[t] + gamma * next_val - values[t]
            gae   = delta + gamma * gae_lambda * (1.0 - dones[t]) * gae
            advantages[t] = gae

        returns = advantages + values

        if normalize_returns:
            return_rms.update(returns)
            returns_normed = return_rms.normalize(returns)
        else:
            returns_normed = returns.copy()

        adv_mean = advantages.mean()
        adv_std  = advantages.std()
        if adv_std > 1e-8:
            advantages = (advantages - adv_mean) / (adv_std + 1e-8)

        return (
            torch.from_numpy(advantages).float(),
            torch.from_numpy(returns_normed).float(),
            float(adv_mean),
        )

    def get_tensors(self):
        T = self.size()
        return (
            self.states[:T],
            self.actions[:T],
            self.log_probs[:T],
            self.values[:T],
        )


# ═══════════════════════════════════════════════════════
# PPO Agent v4
# ═══════════════════════════════════════════════════════

class TorchAgent:

    def __init__(
        self,
        device: str = "cpu",
        policy_mode: str = "sample",
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        entropy_coef: float = 0.05,
        target_entropy: float = 0.5,
        adaptive_entropy: bool = True,
        entropy_lr: float = 3e-4,
        min_entropy_coef: float = 0.001,
        max_entropy_coef: float = 1.0,
        entropy_decay: float = 1.0,
        value_coef: float = 0.5,
        normalize_returns: bool = True,
        ppo_clip_eps: float = 0.2,
        ppo_epochs: int = 10,
        ppo_minibatch: int = 64,
        rollout_steps: int = 512,
        grad_clip: float = 0.5,
        cell_dim: int = 128,
        head_dim: int = 64,
        use_fixed_channel: bool = True,
        use_empty_channel: bool = True,
        use_row_fill_channel: bool = True,
        use_col_fill_channel: bool = True,
        use_box_fill_channel: bool = True,
        use_candidate_count_channel: bool = True,
        use_single_candidate_channel: bool = True,
        mrv_mix_prob: float = 0.0,
        mrv_decay_steps: int = 5000,
        mrv_min_prob: float = 0.0,
        model_path: str = None,
        reset_optimizer_on_load: bool = False,
        reset_counters_on_load: bool = False,
        print_update_log: bool = True,
        use_fp16: bool = True,
        batch_episodes: int = 1,
        hidden: int = 128,
        n_res: int = 4,
        normalize_advantages: bool = True,
    ):
        if device == "cuda" and not torch.cuda.is_available():
            print("警告：CUDA 不可用，改用 CPU。")
            device = "cpu"

        self.device      = torch.device(device)
        self.policy_mode = policy_mode
        self.gamma       = gamma
        self.gae_lambda  = gae_lambda
        self.value_coef  = value_coef
        self.grad_clip   = grad_clip
        self.ppo_clip_eps = ppo_clip_eps
        self.ppo_epochs   = ppo_epochs
        self.ppo_minibatch = ppo_minibatch
        self.rollout_steps = rollout_steps
        self.normalize_returns = normalize_returns
        self.print_update_log  = print_update_log

        self.adaptive_entropy  = adaptive_entropy
        self.target_entropy    = target_entropy
        self.min_entropy_coef  = min_entropy_coef
        self.max_entropy_coef  = max_entropy_coef
        self.entropy_decay     = entropy_decay
        self.entropy_coef      = float(entropy_coef)

        self.use_fixed_channel            = use_fixed_channel
        self.use_empty_channel            = use_empty_channel
        self.use_row_fill_channel         = use_row_fill_channel
        self.use_col_fill_channel         = use_col_fill_channel
        self.use_box_fill_channel         = use_box_fill_channel
        self.use_candidate_count_channel  = use_candidate_count_channel
        self.use_single_candidate_channel = use_single_candidate_channel

        self.mrv_mix_prob    = float(mrv_mix_prob)
        self.mrv_decay_steps = int(mrv_decay_steps)
        self.mrv_min_prob    = float(mrv_min_prob)
        self._mrv_step       = 0  # ★ Fix 2：以 action 為單位計數

        self.in_channels = self._compute_in_channels()

        self.model = SudokuPPONet(
            in_channels=self.in_channels,
            cell_dim=cell_dim,
            head_dim=head_dim,
        ).to(self.device)

        self.optimizer = torch.optim.Adam(
            self.model.parameters(), lr=lr, eps=1e-5
        )
        self.lr = lr
        self.reset_optimizer_on_load = reset_optimizer_on_load
        self.reset_counters_on_load  = reset_counters_on_load

        self._log_alpha = torch.tensor(
            math.log(max(entropy_coef, 1e-8)), dtype=torch.float32,
            device=self.device, requires_grad=True
        )
        self._alpha_optimizer = torch.optim.Adam([self._log_alpha], lr=entropy_lr)

        self.return_rms = RunningMeanStd()

        self.rollout_buf = RolloutBuffer(
            capacity=rollout_steps,
            in_channels=self.in_channels,
            device=self.device,
        )

        self._use_fp16 = use_fp16 and (device == "cuda" or str(self.device) == "cuda")
        self.scaler       = GradScaler('cuda', enabled=self._use_fp16)
        self._alpha_scaler = GradScaler('cuda', enabled=self._use_fp16)

        self._pending_state    = None
        self._pending_action   = None
        self._pending_log_prob = None
        self._pending_value    = None

        self.episode_counter     = 0
        self.update_counter      = 0
        self.last_loss_value     = None
        self.last_entropy_value  = None
        self.last_advantage_mean = None
        self.batch_episodes      = 1

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    # ──────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────

    def _compute_in_channels(self) -> int:
        n = 1
        if self.use_fixed_channel:            n += 1
        if self.use_empty_channel:            n += 1
        if self.use_row_fill_channel:         n += 1
        if self.use_col_fill_channel:         n += 1
        if self.use_box_fill_channel:         n += 1
        if self.use_candidate_count_channel:  n += 1
        if self.use_single_candidate_channel: n += 1
        return n

    def _action_to_index(self, r, c, n): return (r * 9 + c) * 9 + (n - 1)
    def _index_to_action(self, idx):
        cell = idx // 9; return (cell // 9, cell % 9, idx % 9 + 1)

    def _get_mask(self, env) -> torch.Tensor:
        raw = env.get_action_mask()
        t = torch.as_tensor(raw, dtype=torch.bool, device=self.device).view(-1)
        return t if t.numel() == 729 else torch.zeros(729, dtype=torch.bool, device=self.device)

    def _board_to_tensor(self, board, env=None) -> torch.Tensor:
        b = np.asarray(board, dtype=np.float32)
        fx = env.fixed.astype(np.float32) if (env and hasattr(env, "fixed")) else np.zeros((9,9), dtype=np.float32)
        ch = [b / 9.0]
        if self.use_fixed_channel:            ch.append(fx)
        if self.use_empty_channel:            ch.append((b == 0).astype(np.float32))
        if self.use_row_fill_channel:
            ch.append(np.repeat(((b != 0).sum(1) / 9.0)[:, None], 9, 1))
        if self.use_col_fill_channel:
            ch.append(np.repeat(((b != 0).sum(0) / 9.0)[None, :], 9, 0))
        if self.use_box_fill_channel:
            out = np.zeros((9, 9), dtype=np.float32)
            for br in range(3):
                for bc in range(3):
                    out[br*3:br*3+3, bc*3:bc*3+3] = np.count_nonzero(b[br*3:br*3+3, bc*3:bc*3+3]) / 9.0
            ch.append(out)
        if self.use_candidate_count_channel:
            ch.append(env.get_candidate_count_grid().astype(np.float32) / 9.0 if (env and hasattr(env, "get_candidate_count_grid")) else np.zeros((9,9), dtype=np.float32))
        if self.use_single_candidate_channel:
            ch.append(env.get_single_candidate_grid().astype(np.float32) if (env and hasattr(env, "get_single_candidate_grid")) else np.zeros((9,9), dtype=np.float32))
        return torch.from_numpy(np.stack(ch, 0).astype(np.float32)).to(self.device, non_blocking=True)

    # ──────────────────────────────────────────────────
    # MRV curriculum
    # ──────────────────────────────────────────────────

    def _effective_mrv_prob(self) -> float:
        if self.mrv_decay_steps <= 0:
            return self.mrv_min_prob
        frac = min(1.0, self._mrv_step / self.mrv_decay_steps)
        return self.mrv_mix_prob * (1.0 - frac) + self.mrv_min_prob * frac

    def _mrv_action(self, env):
        if not hasattr(env, "candidate_count_grid"):
            acts = env.get_valid_actions()
            return random.choice(acts) if acts else None
        best, min_cnt = [], None
        for r in range(9):
            for c in range(9):
                if env.board[r, c] != 0: continue
                cnt = int(env.candidate_count_grid[r, c])
                if cnt <= 0: continue
                if min_cnt is None or cnt < min_cnt: min_cnt, best = cnt, [(r, c)]
                elif cnt == min_cnt: best.append((r, c))
        if not best: return None
        r, c = random.choice(best)
        cands = sorted(env.candidates_cache[r][c])
        return (r, c, random.choice(cands)) if cands else None

    # ──────────────────────────────────────────────────
    # Episode management
    # ──────────────────────────────────────────────────

    def start_episode(self):
        self.episode_counter += 1
        self._pending_state    = None
        self._pending_action   = None
        self._pending_log_prob = None
        self._pending_value    = None

    def record_reward(self, reward: float):
        pass  # Legacy no-op

    def commit_step(self, reward: float, done: bool):
        """
        在 env.step() 返回後呼叫，把 (state, action, log_prob, value, reward, done)
        寫入 RolloutBuffer。
        """
        if self._pending_state is None:
            return
        self.rollout_buf.push(
            self._pending_state,
            self._pending_action,
            self._pending_log_prob,
            self._pending_value,
            reward,
            done,
        )
        self._pending_state = None

    def finish_episode(
        self,
        success: bool = False,
        summary: dict = None,
        do_update: bool = True,
        rewards: list = None,
        dones: list = None,
    ):
        """
        Episode 結束。
        ★ Fix 4：在觸發 PPO update 前，計算 last_value（bootstrap）。
        ★ Fix 6：移除 _mrv_step 計數（已移至 select_action）。
        """
        # Legacy Mode B fallback
        if rewards is not None and len(rewards) > 0:
            if self._pending_state is not None:
                r = float(rewards[0])
                d = bool(dones[0]) if dones else False
                self.rollout_buf.push(
                    self._pending_state, self._pending_action,
                    self._pending_log_prob, self._pending_value,
                    r, d,
                )
                self._pending_state = None

        if do_update and self.policy_mode == "sample":
            if self.rollout_buf.is_ready:
                # ★ Fix 4：設定 last_value
                # 若 episode 是 done=True 結束 → last_value=0（已在 push 中以 done=True 處理）
                # 若 rollout 在 mid-episode 被截斷 → 估計最後一個 pending state 的 V(s)
                self._set_bootstrap_value()
                info = self._ppo_update()
                if info and self.print_update_log:
                    print(
                        f"[PPO {self.update_counter:5d}] "
                        f"p={info['policy_loss']:.4f} "
                        f"v={info['value_loss']:.4f} "
                        f"ent={info['entropy']:.4f} "
                        f"adv_std={info['adv_std']:.4f} "
                        f"T={info['T']} "
                        f"mrv={self._effective_mrv_prob():.3f} "
                        f"ent_c={self.entropy_coef:.5f}"
                    )

    def _set_bootstrap_value(self):
        """
        ★ Fix 4：計算 RolloutBuffer 末尾的 bootstrap value。
        若最後一個 step 是 done=True，GAE 已通過 dones 處理，last_value 無影響。
        若最後一個 step 是 done=False（mid-episode 截斷），需要 V(s_T) 作為 bootstrap。
        """
        T = self.rollout_buf.size()
        if T == 0:
            self.rollout_buf.set_last_value(0.0)
            return

        last_done = self.rollout_buf.dones[T - 1].item()
        if last_done > 0.5:
            # Episode 正常結束，last_value = 0
            self.rollout_buf.set_last_value(0.0)
            return

        # Mid-episode 截斷：用最後一個 pending state 估計 V(s)
        # （此時 _pending_state 是下一個 action 還未被 commit 的 state）
        if self._pending_state is not None:
            x = self._pending_state.to(self.device).unsqueeze(0)
            with torch.no_grad():
                _, v = self.model(x)
            self.rollout_buf.set_last_value(v.item())
        else:
            # 沒有 pending state（episode 剛好在 rollout 邊界結束）
            self.rollout_buf.set_last_value(0.0)

    # ──────────────────────────────────────────────────
    # Action selection
    # ──────────────────────────────────────────────────

    def select_action(self, env, state):
        is_train = (self.policy_mode == "sample")
        self.model.train() if is_train else self.model.eval()

        # ★ Fix 2：_mrv_step 在 select_action 中計數（每個 action +1）
        if is_train:
            self._mrv_step += 1

        # MRV curriculum
        if is_train and self._effective_mrv_prob() > 0.0:
            if random.random() < self._effective_mrv_prob():
                action = self._mrv_action(env)
                if action is not None:
                    x = self._board_to_tensor(state, env=env)
                    mask = self._get_mask(env)

                    # ★ Fix 1：從 policy network 取得真實 log_prob
                    with torch.no_grad():
                        with autocast('cuda', enabled=self._use_fp16):
                            logits, value = self.model(x.unsqueeze(0))
                        logits = logits.float().squeeze(0)
                        value  = value.float().squeeze()

                    masked = logits.clone()
                    masked[~mask] = -1e9
                    probs = F.softmax(masked, dim=0)

                    action_idx = self._action_to_index(*action)
                    # 確保 action_idx 在 mask 範圍內
                    if not mask[action_idx]:
                        # MRV 選的 action 不在 mask 內（理論上不應發生，但防禦）
                        legal = torch.where(mask)[0]
                        action_idx = legal[torch.randint(len(legal), (1,))].item()
                        action = self._index_to_action(action_idx)

                    # ★ 真實 policy log_prob（不再是均勻假設）
                    lp = torch.log(probs[action_idx].clamp(min=1e-8))

                    self._pending_state    = x.cpu()
                    self._pending_action   = action_idx
                    self._pending_log_prob = lp.item()
                    self._pending_value    = value.item()
                    return action

        x = self._board_to_tensor(state, env=env)
        mask = self._get_mask(env)
        if not mask.any():
            return None

        with torch.no_grad():
            with autocast('cuda', enabled=self._use_fp16):
                logits, value = self.model(x.unsqueeze(0))
            logits = logits.float().squeeze(0)
            value  = value.float().squeeze()

        masked = logits.clone()
        masked[~mask] = -1e9
        probs  = F.softmax(masked, dim=0)

        if torch.isnan(probs).any() or not torch.isfinite(probs).all():
            legal = torch.where(mask)[0]
            idx   = legal[torch.randint(len(legal), (1,))].item()
            if is_train:
                self._pending_state    = x.cpu()
                self._pending_action   = idx
                self._pending_log_prob = math.log(1.0 / len(legal))
                self._pending_value    = value.item()
            return self._index_to_action(idx)

        if self.policy_mode == "greedy":
            return self._index_to_action(probs.argmax().item())

        dist   = Categorical(probs=probs)
        sample = dist.sample()
        self._pending_state    = x.cpu()
        self._pending_action   = sample.item()
        self._pending_log_prob = dist.log_prob(sample).item()
        self._pending_value    = value.item()
        return self._index_to_action(sample.item())

    # ──────────────────────────────────────────────────
    # PPO Update
    # ──────────────────────────────────────────────────

    def _ppo_update(self) -> dict:
        T = self.rollout_buf.size()
        if T == 0:
            self.rollout_buf.reset()
            return None

        advantages, returns, adv_mean = self.rollout_buf.compute_gae_and_returns(
            gamma=self.gamma,
            gae_lambda=self.gae_lambda,
            return_rms=self.return_rms,
            normalize_returns=self.normalize_returns,
        )

        states, actions, old_log_probs, _ = self.rollout_buf.get_tensors()

        states        = states.to(self.device, non_blocking=True)
        actions       = actions.to(self.device, non_blocking=True)
        old_log_probs = old_log_probs.to(self.device, non_blocking=True)
        advantages    = advantages.to(self.device, non_blocking=True)
        returns       = returns.to(self.device, non_blocking=True)

        adv_std = float(advantages.std().item())

        total_p, total_v, total_ent, n_upd = 0.0, 0.0, 0.0, 0

        for _epoch in range(self.ppo_epochs):
            perm = torch.randperm(T, device=self.device)
            for start in range(0, T, self.ppo_minibatch):
                idx = perm[start: start + self.ppo_minibatch]
                if len(idx) == 0:
                    continue

                mb_s   = states[idx]
                mb_a   = actions[idx]
                mb_olp = old_log_probs[idx]
                mb_adv = advantages[idx]
                mb_ret = returns[idx]

                with autocast('cuda', enabled=self._use_fp16):
                    logits, vals = self.model(mb_s)
                    vals = vals.squeeze(-1).float()

                    probs   = F.softmax(logits.float(), dim=-1)
                    dist    = Categorical(probs=probs)
                    new_lp  = dist.log_prob(mb_a)
                    entropy = dist.entropy().mean()

                    ratio = torch.exp(new_lp - mb_olp)
                    s1    = ratio * mb_adv
                    s2    = ratio.clamp(1 - self.ppo_clip_eps, 1 + self.ppo_clip_eps) * mb_adv
                    p_loss = -torch.min(s1, s2).mean()
                    v_loss = F.mse_loss(vals, mb_ret)

                    loss = p_loss + self.value_coef * v_loss - self.entropy_coef * entropy

                self.optimizer.zero_grad()
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
                self.scaler.step(self.optimizer)
                self.scaler.update()

                if self.adaptive_entropy:
                    with autocast('cuda', enabled=self._use_fp16):
                        alpha_loss = -(self._log_alpha.exp() * (entropy.detach() - self.target_entropy))
                    self._alpha_optimizer.zero_grad()
                    self._alpha_scaler.scale(alpha_loss).backward()
                    self._alpha_scaler.step(self._alpha_optimizer)
                    self._alpha_scaler.update()
                    new_coef = self._log_alpha.exp().item()
                    self.entropy_coef = float(np.clip(new_coef, self.min_entropy_coef, self.max_entropy_coef))

                total_p   += p_loss.item()
                total_v   += v_loss.item()
                total_ent += entropy.item()
                n_upd     += 1

        if not self.adaptive_entropy and self.entropy_decay < 1.0:
            self.entropy_coef = max(self.min_entropy_coef, self.entropy_coef * self.entropy_decay)

        self.rollout_buf.reset()
        self.update_counter     += 1
        self.last_loss_value     = (total_p + self.value_coef * total_v) / max(n_upd, 1)
        self.last_entropy_value  = total_ent / max(n_upd, 1)
        self.last_advantage_mean = float(adv_mean)

        return {
            "policy_loss": total_p / max(n_upd, 1),
            "value_loss":  total_v / max(n_upd, 1),
            "entropy":     total_ent / max(n_upd, 1),
            "adv_std":     adv_std,
            "T":           T,
        }

    # ──────────────────────────────────────────────────
    # Save / Load
    # ──────────────────────────────────────────────────

    def save_model(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        torch.save({
            "arch":                 "ppo_v4_fixed",
            "model_state_dict":     self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "log_alpha":            self._log_alpha.item(),
            "alpha_optim":          self._alpha_optimizer.state_dict(),
            "return_rms_mean":      self.return_rms.mean,
            "return_rms_var":       self.return_rms.var,
            "return_rms_count":     self.return_rms.count,
            "in_channels":          self.in_channels,
            "cell_dim":             self.model.cell_dim,
            "head_dim":             self.model.head_dim,
            "lr":                   self.lr,
            "gamma":                self.gamma,
            "gae_lambda":           self.gae_lambda,
            "entropy_coef":         self.entropy_coef,
            "target_entropy":       self.target_entropy,
            "adaptive_entropy":     self.adaptive_entropy,
            "value_coef":           self.value_coef,
            "ppo_clip_eps":         self.ppo_clip_eps,
            "ppo_epochs":           self.ppo_epochs,
            "ppo_minibatch":        self.ppo_minibatch,
            "rollout_steps":        self.rollout_steps,
            "mrv_mix_prob":         self.mrv_mix_prob,
            "mrv_decay_steps":      self.mrv_decay_steps,
            "mrv_min_prob":         self.mrv_min_prob,
            "_mrv_step":            self._mrv_step,
            "episode_counter":      self.episode_counter,
            "update_counter":       self.update_counter,
            "last_loss_value":      self.last_loss_value,
            "last_entropy_value":   self.last_entropy_value,
            "last_advantage_mean":  self.last_advantage_mean,
            "use_fixed_channel":            self.use_fixed_channel,
            "use_empty_channel":            self.use_empty_channel,
            "use_row_fill_channel":         self.use_row_fill_channel,
            "use_col_fill_channel":         self.use_col_fill_channel,
            "use_box_fill_channel":         self.use_box_fill_channel,
            "use_candidate_count_channel":  self.use_candidate_count_channel,
            "use_single_candidate_channel": self.use_single_candidate_channel,
        }, path)
        print(f"[TorchAgent v4] 已儲存：{path}")

    def load_model(self, path: str):
        p = torch.load(path, map_location=self.device, weights_only=False)
        arch = p.get("arch", "unknown")
        saved_ch = p.get("in_channels")
        if saved_ch is not None and saved_ch != self.in_channels:
            raise ValueError(f"in_channels 不符：檔案={saved_ch} Agent={self.in_channels}")

        self.model.load_state_dict(p["model_state_dict"])
        if not self.reset_optimizer_on_load and "optimizer_state_dict" in p:
            try: self.optimizer.load_state_dict(p["optimizer_state_dict"])
            except Exception as e: print(f"[TorchAgent] optimizer 載入失敗：{e}")

        if "log_alpha" in p:
            with torch.no_grad():
                self._log_alpha.fill_(p["log_alpha"])
        if "alpha_optim" in p:
            try: self._alpha_optimizer.load_state_dict(p["alpha_optim"])
            except: pass
        if "return_rms_mean" in p:
            self.return_rms.mean  = p["return_rms_mean"]
            self.return_rms.var   = p["return_rms_var"]
            self.return_rms.count = p["return_rms_count"]

        for attr in ("gamma","gae_lambda","entropy_coef","target_entropy",
                     "adaptive_entropy","value_coef","ppo_clip_eps","ppo_epochs",
                     "ppo_minibatch","rollout_steps","mrv_mix_prob","mrv_decay_steps",
                     "mrv_min_prob"):
            if attr in p: setattr(self, attr, p[attr])

        if not self.reset_counters_on_load:
            for attr in ("episode_counter","update_counter","_mrv_step",
                         "last_loss_value","last_entropy_value","last_advantage_mean"):
                if attr in p: setattr(self, attr, p[attr])

        print(f"[TorchAgent v4] 已載入：{path} (arch={arch}, ep={self.episode_counter})")