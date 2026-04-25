# app/rl/models/sudoku_ppo.py
# -*- coding: utf-8 -*-
"""
SudokuMaskablePPO — MaskablePPO subclass with BC (behavioral cloning) loss.

How BC works:
  1. collect_rollouts() captures teacher_action + teacher_quality from info dicts
     returned by SudokuGymEnv.step() (teacher runs inside the subprocess).
  2. After the standard PPO update in train(), a separate BC optimization step
     computes weighted cross-entropy loss over steps where teacher_quality > 0.
  3. mrv_prob (updated by CurriculumCallback) controls BC strength:
       eff_bc = bc_coef × (mrv_prob / mrv_prob_init)

The BC pass is intentionally separate from PPO to avoid gradient interference.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from sb3_contrib import MaskablePPO
from stable_baselines3.common.utils import obs_as_tensor


class SudokuMaskablePPO(MaskablePPO):
    """
    MaskablePPO with quality-weighted behavioral cloning auxiliary loss.

    Extra constructor args
    ---------------------
    bc_coef : float
        Maximum BC loss coefficient (when mrv_prob == mrv_prob_init).
    mrv_prob_init : float
        The initial MRV probability set in Stage 1 (denominator for decay).
    """

    def __init__(self, *args, bc_coef: float = 1.0, mrv_prob_init: float = 0.80, **kwargs):
        super().__init__(*args, **kwargs)
        self.bc_coef       = bc_coef
        self.mrv_prob_init = mrv_prob_init
        self.mrv_prob      = mrv_prob_init  # updated by CurriculumCallback

        # Teacher data captured during collect_rollouts: shape (n_steps, n_envs)
        self._teacher_actions: np.ndarray | None = None
        self._teacher_quality: np.ndarray | None = None

    # ── Rollout collection ────────────────────────────────────────────────────

    def collect_rollouts(self, env, callback, rollout_buffer, n_rollout_steps, use_masking=True):
        """Extend parent's collect_rollouts to capture teacher data from infos."""
        teacher_a_buf: list[list[int]]   = []  # per step: list of n_envs values
        teacher_q_buf: list[list[float]] = []

        # Monkey-patch callback.on_step to intercept infos BEFORE returning
        _orig_on_step = callback.on_step

        def _patched_on_step() -> bool:
            locs = callback.locals
            infos = locs.get("infos", [])
            teacher_a_buf.append([
                int(info.get("teacher_action", -1)) for info in infos
            ])
            teacher_q_buf.append([
                float(info.get("teacher_quality", 0.0)) for info in infos
            ])
            return _orig_on_step()

        callback.on_step = _patched_on_step
        try:
            result = super().collect_rollouts(
                env, callback, rollout_buffer, n_rollout_steps, use_masking=use_masking
            )
        finally:
            callback.on_step = _orig_on_step  # always restore

        if teacher_a_buf:
            self._teacher_actions = np.array(teacher_a_buf, dtype=np.int64)    # (T, n_envs)
            self._teacher_quality = np.array(teacher_q_buf, dtype=np.float32)  # (T, n_envs)
        else:
            self._teacher_actions = None
            self._teacher_quality = None

        return result

    # ── Training step ─────────────────────────────────────────────────────────

    def train(self) -> None:
        """Standard PPO training + auxiliary BC loss pass."""
        super().train()
        self._bc_pass()

    def _bc_pass(self) -> None:
        """One extra optimization step on teacher-labeled steps."""
        if self._teacher_actions is None or self._teacher_quality is None:
            return

        eff_bc = self.bc_coef * (self.mrv_prob / max(self.mrv_prob_init, 1e-8))
        if eff_bc < 1e-6:
            return

        # After super().train(), rollout_buffer.observations is swap_and_flattened:
        # shape (n_envs * n_steps, *obs_shape), indexed as [env_idx * n_steps + step_idx].
        # Our teacher arrays are (n_steps, n_envs). Transpose + flatten to align.
        teacher_q_flat = self._teacher_quality.T.flatten()   # (n_envs * n_steps,)
        teacher_a_flat = self._teacher_actions.T.flatten()   # (n_envs * n_steps,)

        teacher_mask = (teacher_q_flat > 0) & (teacher_a_flat >= 0)
        if not teacher_mask.any():
            return

        obs_np = self.rollout_buffer.observations[teacher_mask]
        obs_t  = obs_as_tensor(obs_np, self.device)
        ta     = torch.tensor(teacher_a_flat[teacher_mask], dtype=torch.long,  device=self.device)
        tq     = torch.tensor(teacher_q_flat[teacher_mask], dtype=torch.float32, device=self.device)

        self.policy.set_training_mode(True)

        # evaluate_actions without action masking (teacher actions are always legal)
        _, log_probs, _ = self.policy.evaluate_actions(obs_t, ta)

        bc_loss = -(log_probs * tq).sum() / tq.sum()

        self.policy.optimizer.zero_grad()
        (eff_bc * bc_loss).backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
        self.policy.optimizer.step()

        self.logger.record("train/bc_loss",     bc_loss.item())
        self.logger.record("train/bc_coef_eff", eff_bc)
        self.logger.record("train/mrv_prob",    self.mrv_prob)
