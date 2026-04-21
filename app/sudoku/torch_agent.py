# app/sudoku/torch_agent.py
# -*- coding: utf-8 -*-

import os
import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
from torch.amp import GradScaler, autocast

from app.sudoku.phase_manager import PhaseManager, PhaseConfig
from app.sudoku.teacher_engine import TeacherEngine
from app.sudoku.policy_demo_store import PolicyDemoStore


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


class RolloutBuffer:
    def __init__(self, capacity: int, in_channels: int, device: torch.device):
        self.capacity    = capacity
        self.in_channels = in_channels
        self.device      = device
        self._ptr        = 0
        self._full       = False
        self.last_value  = 0.0  

        self.states          = torch.zeros(capacity, in_channels, 9, 9, dtype=torch.float32)
        self.actions         = torch.zeros(capacity, dtype=torch.long)
        self.log_probs       = torch.zeros(capacity, dtype=torch.float32)
        self.values          = torch.zeros(capacity, dtype=torch.float32)
        self.rewards         = torch.zeros(capacity, dtype=torch.float32)
        self.dones           = torch.zeros(capacity, dtype=torch.float32)
        self.is_mrvs         = torch.zeros(capacity, dtype=torch.bool)
        self.quality_weights = torch.zeros(capacity, dtype=torch.float32)

    def push(self, state, action, log_prob, value, reward, done, is_mrv, quality: float = 1.0):
        if self._full:
            return

        i = self._ptr
        self.states[i]          = state.cpu()
        self.actions[i]         = action
        self.log_probs[i]       = float(log_prob)
        self.values[i]          = float(value)
        self.rewards[i]         = float(reward)
        self.dones[i]           = float(done)
        self.is_mrvs[i]         = bool(is_mrv)
        self.quality_weights[i] = float(quality)
        self._ptr += 1
        if self._ptr >= self.capacity:
            self._full = True

    def set_last_value(self, v: float):
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

        # ★ Bug Fix：Value 反歸一化
        # 如果網路已經學會預測歸一化後的 Returns，在跟原始 rewards 運算 GAE 前，
        # 必須將其「反歸一化」，否則 GAE 的維度跟尺度會徹底崩壞。
        if normalize_returns and return_rms.count > 1.0:
            std = return_rms.std
            mean = return_rms.mean
            values_unnorm = values * std + mean
            last_val_unnorm = self.last_value * std + mean
        else:
            values_unnorm = values.copy()
            last_val_unnorm = self.last_value

        advantages = np.zeros(T, dtype=np.float32)
        gae = 0.0
        for t in reversed(range(T)):
            if t + 1 < T:
                next_val = values_unnorm[t + 1]
            else:
                next_val = last_val_unnorm
                
            next_val *= (1.0 - dones[t])
            delta = rewards[t] + gamma * next_val - values_unnorm[t]
            gae   = delta + gamma * gae_lambda * (1.0 - dones[t]) * gae
            advantages[t] = gae

        # 這裡的 returns 是原始分數的 Returns
        returns = advantages + values_unnorm

        # 計算完真實的 Returns 後，再更新並歸一化給 Value Network 當 Target
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
            self.is_mrvs[:T],
            self.quality_weights[:T],
        )


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
        bc_coef: float = 1.0,
        model_path: str = None,
        reset_optimizer_on_load: bool = False,
        reset_counters_on_load: bool = False,
        print_update_log: bool = True,
        use_fp16: bool = True,
        normalize_advantages: bool = True,
        # ── Phase / Teacher / Demo 參數 ──────────────────────────────────
        phase1_steps: int        = 30_000,
        phase2_steps: int        = 90_000,
        phase1_tau: float        = 0.30,
        phase2_tau: float        = 0.65,
        teacher_max_cand: int    = 4,
        policy_demo_capacity: int  = 2048,
        policy_demo_weight: float  = 0.30,
    ):
        if device == "cuda" and not torch.cuda.is_available():
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
        self.bc_coef         = float(bc_coef)
        self._mrv_step       = 0  

        self.in_channels = self._compute_in_channels()

        self.model = SudokuPPONet(
            in_channels=self.in_channels,
            cell_dim=cell_dim,
            head_dim=head_dim,
        ).to(self.device)

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, eps=1e-5)
        self.lr = lr
        self.reset_optimizer_on_load = reset_optimizer_on_load
        self.reset_counters_on_load  = reset_counters_on_load

        self._log_alpha = torch.tensor(
            math.log(max(entropy_coef, 1e-8)), dtype=torch.float32,
            device=self.device, requires_grad=True
        )
        # Alpha optimizer 不需要 GradScaler 以避免不穩定
        self._alpha_optimizer = torch.optim.Adam([self._log_alpha], lr=entropy_lr)

        self.return_rms = RunningMeanStd()

        self.rollout_buf = RolloutBuffer(
            capacity=rollout_steps,
            in_channels=self.in_channels,
            device=self.device,
        )

        self._use_fp16 = use_fp16 and (device == "cuda" or str(self.device) == "cuda")
        self.scaler    = GradScaler('cuda', enabled=self._use_fp16)

        self._pending_state    = None
        self._pending_action   = None
        self._pending_log_prob = None
        self._pending_value    = None
        self._pending_is_mrv   = False
        self._pending_quality  = 0.0

        self.episode_counter     = 0
        self.update_counter      = 0
        self.last_loss_value     = 0.0
        self.last_entropy_value  = 0.0
        self.last_advantage_mean = 0.0

        # ── Phase / Teacher / Demo ────────────────────────────────────────
        _phase_cfg = PhaseConfig(
            phase1_steps = phase1_steps,
            phase2_steps = phase2_steps,
            tau1         = phase1_tau,
            tau2         = phase2_tau,
            mrv_init     = float(mrv_mix_prob),
            mrv_floor    = float(mrv_min_prob),
        )
        self.phase_manager    = PhaseManager(_phase_cfg)
        self.teacher_engine   = TeacherEngine(max_candidates=teacher_max_cand)
        self.policy_demo_store = PolicyDemoStore(
            capacity    = policy_demo_capacity,
            in_channels = self.in_channels,
            demo_weight = policy_demo_weight,
        )

        # episode 級別的 policy demo 暫存（Phase 3 用）
        self._demo_states:  list[torch.Tensor] = []
        self._demo_actions: list[int]           = []
        self._demo_total_steps: int             = 0

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

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

    def _effective_mrv_prob(self) -> float:
        """PhaseManager 的餘弦分段衰減曲線，供外部 logging 使用。"""
        return self.phase_manager.mrv_prob(self._mrv_step)

    def start_episode(self):
        self.episode_counter += 1
        self._pending_state    = None
        self._pending_action   = None
        self._pending_log_prob = None
        self._pending_value    = None
        self._pending_is_mrv   = False
        self._pending_quality  = 0.0
        # Phase 3: 每個 episode 重新開始收集 policy steps
        self._demo_states       = []
        self._demo_actions      = []
        self._demo_total_steps  = 0

    def commit_step(self, reward: float, done: bool):
        if self._pending_state is None:
            return

        self.rollout_buf.push(
            self._pending_state,
            self._pending_action,
            self._pending_log_prob,
            self._pending_value,
            reward,
            done,
            self._pending_is_mrv,
            self._pending_quality,
        )

        # Phase 3：收集 policy-only steps，成功時存入 PolicyDemoStore
        if (self.phase_manager.phase == PhaseManager.PHASE_3
                and not self._pending_is_mrv
                and self._pending_state is not None):
            self._demo_states.append(self._pending_state.clone())
            self._demo_actions.append(int(self._pending_action))

        self._demo_total_steps += 1
        self._pending_state    = None
        self._pending_is_mrv   = False
        self._pending_quality  = 0.0

    def finish_episode(
        self,
        success: bool = False,
        summary: dict = None,
        do_update: bool = True,
        rewards: list = None,
        dones: list = None,
    ):
        # Phase 3 自我改善：成功且 policy 主導 → 存入 PolicyDemoStore
        if success and self.phase_manager.phase == PhaseManager.PHASE_3:
            added = self.policy_demo_store.try_add_episode(
                self._demo_states,
                self._demo_actions,
                self._demo_total_steps,
            )
            if added > 0 and self.print_update_log:
                print(f"[Demo] 存入 {added} 步  store={self.policy_demo_store.size}")

        # Phase 轉換偵測（每 episode 觸發一次）
        self.phase_manager.record_episode(success, self._mrv_step)

        if do_update and self.policy_mode == "sample":
            if self.rollout_buf.is_ready:
                self._set_bootstrap_value()
                info = self._ppo_update()
                if info and self.print_update_log:
                    print(
                        f"[PPO {self.update_counter:5d}] "
                        f"ph={self.phase_manager.phase} "
                        f"p={info['policy_loss']:.4f} "
                        f"v={info['value_loss']:.4f} "
                        f"ent={info['entropy']:.4f} "
                        f"adv_std={info['adv_std']:.4f} "
                        f"mrv={info['mrv_ratio']:.2f} "
                        f"bc={info['bc_loss']:.4f} "
                        f"bc/p={info['bc_ppo_ratio']:.2f} "
                        f"ent_c={self.entropy_coef:.5f}"
                    )

    def _set_bootstrap_value(self):
        T = self.rollout_buf.size()
        if T == 0:
            self.rollout_buf.set_last_value(0.0)
            return

        last_done = self.rollout_buf.dones[T - 1].item()
        if last_done > 0.5:
            self.rollout_buf.set_last_value(0.0)
            return

        if self._pending_state is not None:
            x = self._pending_state.to(self.device).unsqueeze(0)
            with torch.no_grad():
                _, v = self.model(x)
            self.rollout_buf.set_last_value(v.item())
        else:
            self.rollout_buf.set_last_value(0.0)

    def select_action(self, env, state):
        is_train = (self.policy_mode == "sample")
        self.model.train() if is_train else self.model.eval()

        if is_train:
            self._mrv_step += 1

        if is_train and self._effective_mrv_prob() > 0.0:
            if random.random() < self._effective_mrv_prob():
                # TeacherEngine：確定性，回傳 (action, quality) 或 (None, 0.0)
                action, quality = self.teacher_engine(env)
                if action is not None:
                    x    = self._board_to_tensor(state, env=env)
                    mask = self._get_mask(env)

                    with torch.no_grad():
                        with autocast('cuda', enabled=self._use_fp16):
                            logits, value = self.model(x.unsqueeze(0))
                        logits = logits.float().squeeze(0)
                        value  = value.float().squeeze()

                    masked = logits.clone()
                    masked[~mask] = -1e9
                    probs = F.softmax(masked, dim=0)

                    action_idx = self._action_to_index(*action)
                    if not mask[action_idx]:
                        # teacher action 不在合法 mask（理論上不應發生），fallback 到 policy
                        legal      = torch.where(mask)[0]
                        action_idx = legal[torch.randint(len(legal), (1,))].item()
                        action     = self._index_to_action(action_idx)
                        quality    = 0.0   # fallback 不算 teacher

                    lp = torch.log(probs[action_idx].clamp(min=1e-8))

                    self._pending_state    = x.cpu()
                    self._pending_action   = action_idx
                    self._pending_log_prob = lp.item()
                    self._pending_value    = value.item()
                    self._pending_is_mrv   = (quality > 0.0)
                    self._pending_quality  = quality
                    return action
                # Teacher 放棄（Level 5 信度不足）→ fall through to policy

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
                self._pending_is_mrv   = False
            return self._index_to_action(idx)

        if self.policy_mode == "greedy":
            return self._index_to_action(probs.argmax().item())

        dist   = Categorical(probs=probs)
        sample = dist.sample()
        self._pending_state    = x.cpu()
        self._pending_action   = sample.item()
        self._pending_log_prob = dist.log_prob(sample).item()
        self._pending_value    = value.item()
        self._pending_is_mrv   = False
        return self._index_to_action(sample.item())

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

        states, actions, old_log_probs, _, is_mrvs, quality_weights = \
            self.rollout_buf.get_tensors()

        states         = states.to(self.device, non_blocking=True)
        actions        = actions.to(self.device, non_blocking=True)
        old_log_probs  = old_log_probs.to(self.device, non_blocking=True)
        advantages     = advantages.to(self.device, non_blocking=True)
        returns        = returns.to(self.device, non_blocking=True)
        is_mrvs        = is_mrvs.to(self.device, non_blocking=True)
        quality_weights = quality_weights.to(self.device, non_blocking=True)

        adv_std = float(advantages.std().item())

        # 計算本次 update 的有效 bc_coef
        # eff_bc = bc_coef × (mrv_prob / mrv_init)^β
        #   Phase 1: β=0.5  → BC 衰減比 MRV 慢（保持 imitation 主導）
        #   Phase 2: β=1.0  → BC 與 MRV 同速
        #   Phase 3: β=999  → BC ≈ 0（phase_manager 確保 mrv_prob ≤ floor）
        _cur_mrv_prob = self._effective_mrv_prob()
        _bc_exp       = self.phase_manager.bc_exponent()
        _mrv_ratio    = _cur_mrv_prob / max(self.mrv_mix_prob, 1e-8)
        eff_bc        = self.bc_coef * (_mrv_ratio ** min(_bc_exp, 10.0))

        total_p, total_v, total_ent, total_bc, n_upd = 0.0, 0.0, 0.0, 0.0, 0

        for _epoch in range(self.ppo_epochs):
            perm = torch.randperm(T, device=self.device)
            for start in range(0, T, self.ppo_minibatch):
                idx = perm[start: start + self.ppo_minibatch]
                if len(idx) == 0:
                    continue

                mb_s       = states[idx]
                mb_a       = actions[idx]
                mb_olp     = old_log_probs[idx]
                mb_adv     = advantages[idx]
                mb_ret     = returns[idx]
                mb_is_mrv  = is_mrvs[idx]
                mb_quality = quality_weights[idx]

                with autocast('cuda', enabled=self._use_fp16):
                    logits, vals = self.model(mb_s)
                    vals = vals.squeeze(-1).float()

                    probs   = F.softmax(logits.float(), dim=-1)
                    dist    = Categorical(probs=probs)
                    new_lp  = dist.log_prob(mb_a)
                    entropy = dist.entropy().mean()

                    ratio  = torch.exp(new_lp - mb_olp)
                    s1     = ratio * mb_adv
                    s2     = ratio.clamp(1 - self.ppo_clip_eps, 1 + self.ppo_clip_eps) * mb_adv
                    p_loss = -torch.min(s1, s2).mean()
                    v_loss = F.mse_loss(vals, mb_ret)
                    loss   = p_loss + self.value_coef * v_loss - self.entropy_coef * entropy

                    # Quality-weighted BC loss（只對 teacher steps）
                    bc_loss_val = 0.0
                    if mb_is_mrv.any() and eff_bc > 1e-6:
                        w        = mb_quality[mb_is_mrv].clamp(0.0, 1.0)
                        bc_raw   = -(new_lp[mb_is_mrv] * w).sum() / (w.sum() + 1e-8)
                        bc_loss_val = bc_raw.item()
                        loss    += eff_bc * bc_raw

                    # Phase 3 PolicyDemoStore soft BC（在外層 autocast 內，不需再包一層）
                    if self.phase_manager.phase == PhaseManager.PHASE_3:
                        demo = self.policy_demo_store.sample(
                            min(self.ppo_minibatch, 64), self.device
                        )
                        if demo is not None:
                            demo_s, demo_a = demo
                            demo_logits, _ = self.model(demo_s)
                            demo_probs = F.softmax(demo_logits.float(), dim=-1)
                            demo_lp    = Categorical(probs=demo_probs).log_prob(demo_a)
                            pd_loss = -demo_lp.mean()
                            loss   += self.policy_demo_store.demo_weight * pd_loss

                self.optimizer.zero_grad()
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
                self.scaler.step(self.optimizer)
                self.scaler.update()

                if self.adaptive_entropy:
                    # ★ Bug Fix：修正梯度方向。當 H < H0 時，必須增加 alpha。
                    # 對 _log_alpha 偏微分為 (H - H0)，若 H < H0，梯度為負，這樣才有效提高 alpha！
                    alpha_loss = self._log_alpha * (entropy.detach() - self.target_entropy)
                    self._alpha_optimizer.zero_grad()
                    alpha_loss.backward()
                    self._alpha_optimizer.step()
                    new_coef = self._log_alpha.exp().item()
                    self.entropy_coef = float(np.clip(new_coef, self.min_entropy_coef, self.max_entropy_coef))

                total_p   += p_loss.item()
                total_v   += v_loss.item()
                total_ent += entropy.item()
                total_bc  += bc_loss_val
                n_upd     += 1

        if not self.adaptive_entropy and self.entropy_decay < 1.0:
            self.entropy_coef = max(self.min_entropy_coef, self.entropy_coef * self.entropy_decay)

        self.rollout_buf.reset()
        self.update_counter     += 1
        self.last_loss_value     = (total_p + self.value_coef * total_v) / max(n_upd, 1)
        self.last_entropy_value  = total_ent / max(n_upd, 1)
        self.last_advantage_mean = float(adv_mean)

        return {
            "policy_loss":  total_p / max(n_upd, 1),
            "value_loss":   total_v / max(n_upd, 1),
            "entropy":      total_ent / max(n_upd, 1),
            "adv_std":      adv_std,
            "T":            T,
            "mrv_ratio":    is_mrvs.float().mean().item(),
            "bc_loss":      total_bc / max(n_upd, 1),
            "bc_ppo_ratio": (total_bc / total_p) if total_p > 1e-8 else 0.0,
            "eff_bc":       eff_bc,
            "phase":        self.phase_manager.phase,
        }

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
            "bc_coef":              self.bc_coef,
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
            "phase_manager":                self.phase_manager.state_dict(),
            "policy_demo_store":            self.policy_demo_store.state_dict(),
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
                     "mrv_min_prob", "bc_coef"):
            if attr in p: setattr(self, attr, p[attr])

        if not self.reset_counters_on_load:
            for attr in ("episode_counter","update_counter","_mrv_step",
                         "last_loss_value","last_entropy_value","last_advantage_mean"):
                if attr in p: setattr(self, attr, p[attr])

        if "phase_manager" in p:
            try: self.phase_manager.load_state_dict(p["phase_manager"])
            except Exception as e: print(f"[TorchAgent] phase_manager 載入失敗：{e}")
        if "policy_demo_store" in p:
            try: self.policy_demo_store.load_state_dict(p["policy_demo_store"])
            except Exception as e: print(f"[TorchAgent] policy_demo_store 載入失敗：{e}")

        print(f"[TorchAgent v4] 已載入：{path} (arch={arch}, ep={self.episode_counter})")