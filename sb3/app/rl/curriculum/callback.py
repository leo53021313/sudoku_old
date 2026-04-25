# app/rl/curriculum/callback.py
# -*- coding: utf-8 -*-
"""
CurriculumCallback — 4-stage difficulty escalation for SudokuGymEnv.

Stage progression:
  1 → L1:100%  (mrv=0.80)  → advance when success_rate ≥ 0.75 or 5,000 episodes
  2 → L1:60% L2:40% (mrv=0.40) → advance when L2 success_rate ≥ 0.65 or 15,000 ep
  3 → L1:20% L2:40% L3:40% (mrv=0.20) → advance when L3 success_rate ≥ 0.55 or 30,000 ep
  4 → L1:10% L2:20% L3:35% L4:35% (mrv=0.05) — final stage, no threshold

The callback calls env.env_method('set_difficulty_distribution', dist) on all
SubprocVecEnv subprocesses when advancing a stage, and updates model.mrv_prob.

Entropy monitoring: logs a WARNING if mean_entropy < 0.3 nats.
"""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback


CURRICULUM_STAGES: list[dict[str, Any]] = [
    {
        "dist":      {1: 1.0},
        "mrv":       0.80,
        "threshold": 0.75,
        "backstop":  5_000,   # episodes
    },
    {
        "dist":      {1: 0.6, 2: 0.4},
        "mrv":       0.40,
        "threshold": 0.65,
        "backstop":  15_000,
    },
    {
        "dist":      {1: 0.2, 2: 0.4, 3: 0.4},
        "mrv":       0.20,
        "threshold": 0.55,
        "backstop":  30_000,
    },
    {
        "dist":      {1: 0.1, 2: 0.2, 3: 0.35, 4: 0.35},
        "mrv":       0.05,
        # final stage — no threshold or backstop
    },
]


class CurriculumCallback(BaseCallback):
    """
    Tracks per-difficulty success rate and advances curriculum stages.

    Parameters
    ----------
    stages : list[dict]
        Curriculum stage definitions (default: CURRICULUM_STAGES).
    window : int
        Rolling window size for success rate (default 100 episodes).
    verbose : int
        Verbosity level.
    """

    def __init__(
        self,
        stages: list[dict[str, Any]] | None = None,
        window: int = 100,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self._stages       = stages if stages is not None else CURRICULUM_STAGES
        self._window       = window
        self._stage_idx    = 0
        self._total_eps    = 0
        self._stage_eps    = 0  # episodes since last stage advance

        # Rolling window: track (is_success, difficulty) per episode
        self._success_buf: deque[bool]  = deque(maxlen=window)
        self._diff_buf:    deque[int]   = deque(maxlen=window)

        # Per-difficulty success rates (for logging + threshold check)
        self._diff_success: dict[int, deque[bool]] = {
            lvl: deque(maxlen=window) for lvl in range(1, 5)
        }

    # ── BaseCallback interface ────────────────────────────────────────────────

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        dones = self.locals.get("dones", [])

        for info, done in zip(infos, dones):
            if not done:
                continue
            success    = bool(info.get("is_success", False))
            difficulty = int(info.get("difficulty", 1))

            self._total_eps  += 1
            self._stage_eps  += 1
            self._success_buf.append(success)
            self._diff_buf.append(difficulty)
            self._diff_success.setdefault(difficulty, deque(maxlen=self._window)).append(success)

        # Check stage advancement
        if self._stage_idx < len(self._stages) - 1:
            self._maybe_advance()

        # Entropy monitoring
        entropy = self.locals.get("entropy_loss")  # set by SB3 train() locals
        if entropy is not None and -float(entropy) < 0.3:
            self.logger.warn(
                f"[Curriculum] Entropy {-float(entropy):.3f} < 0.3 nats — policy may be collapsing!"
            )

        return True

    def _on_training_end(self) -> None:
        if self.verbose >= 1:
            stage = self._stages[self._stage_idx]
            print(
                f"[Curriculum] Training ended at stage {self._stage_idx + 1}. "
                f"Total episodes: {self._total_eps}. "
                f"Final dist: {stage['dist']}"
            )

    # ── Stage management ──────────────────────────────────────────────────────

    def _maybe_advance(self) -> None:
        stage = self._stages[self._stage_idx]
        threshold = stage.get("threshold")
        backstop  = stage.get("backstop", float("inf"))

        advance = False

        if self._stage_eps >= backstop:
            advance = True
            reason  = f"backstop ({backstop} eps)"
        elif threshold is not None and len(self._success_buf) >= min(self._window, 50):
            # Use the success rate for the HIGHEST difficulty in the current mix
            top_diff = max(stage["dist"].keys())
            top_buf  = self._diff_success.get(top_diff)
            if top_buf and len(top_buf) >= 30:
                rate = float(np.mean(list(top_buf)))
                if rate >= threshold:
                    advance = True
                    reason  = f"success_rate={rate:.2f} ≥ {threshold} on L{top_diff}"

        if advance:
            self._stage_idx += 1
            self._stage_eps  = 0
            self._apply_stage(reason)

    def _apply_stage(self, reason: str = "") -> None:
        stage = self._stages[self._stage_idx]
        dist  = stage["dist"]
        mrv   = stage["mrv"]

        # Update all VecEnv subprocesses
        self.training_env.env_method("set_difficulty_distribution", dist)

        # Update MaskablePPO's mrv_prob for BC decay
        if hasattr(self.model, "mrv_prob"):
            self.model.mrv_prob = mrv

        if self.verbose >= 1:
            print(
                f"[Curriculum] → Stage {self._stage_idx + 1}: dist={dist} "
                f"mrv={mrv:.2f}  ({reason})"
            )

        self.logger.record("curriculum/stage",   self._stage_idx + 1)
        self.logger.record("curriculum/mrv_prob", mrv)
        self.logger.record("curriculum/total_episodes", self._total_eps)

    # ── Logging ───────────────────────────────────────────────────────────────

    def _on_rollout_end(self) -> None:
        if not self._success_buf:
            return

        overall_rate = float(np.mean(list(self._success_buf)))
        self.logger.record("curriculum/success_rate_overall", overall_rate)
        self.logger.record("curriculum/stage",               self._stage_idx + 1)
        self.logger.record("curriculum/total_episodes",      self._total_eps)

        for lvl, buf in self._diff_success.items():
            if buf:
                self.logger.record(
                    f"curriculum/success_rate_L{lvl}",
                    float(np.mean(list(buf)))
                )
