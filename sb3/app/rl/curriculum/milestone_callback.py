# app/rl/curriculum/milestone_callback.py
# -*- coding: utf-8 -*-
"""
MilestoneCallback — abort training early if predefined health/performance
milestones aren't met. Saves wasted compute on a doomed 6.5-hour run.

Milestones (per Phase 1 design spec §6):
  100k  : approx_kl < 0.05 AND entropy_loss > -2.0    (PPO health)
  300k  : success_rate_L1 >= 0.75                      (Stage 1 finished)
  500k  : success_rate_L1 >= 0.70 AND L2 >= 0.50
  1M    : L1 >= 0.80 AND L2 >= 0.70 AND L3 >= 0.50       (warn only)
  2M    : L1, L2, L3 >= 0.80 AND L4 >= 0.30             (final pass/fail)

The callback queries the curriculum's rolling success buffers + the latest
PPO log values. On hard fail, returns False from _on_step() so SB3's
learn() loop terminates cleanly. On warn-only fail, returns True after
printing the failure message.
"""

from __future__ import annotations

from typing import Any, Callable

from stable_baselines3.common.callbacks import BaseCallback


MILESTONES: list[dict[str, Any]] = [
    {
        "step":            100_000,
        "approx_kl_max":   0.05,
        "entropy_min":     -2.0,
    },
    {
        "step":             300_000,
        "success_L1_min":   0.75,
        "warn_only":        True,
    },
    {
        "step":             500_000,
        "success_L1_min":   0.70,
        "success_L2_min":   0.50,
        "warn_only":        True,
    },
    {
        "step":             1_000_000,
        "success_L1_min":   0.80,
        "success_L2_min":   0.70,
        "success_L3_min":   0.50,
        "warn_only":        True,
    },
    {
        "step":             2_000_000,
        "success_L1_min":   0.80,
        "success_L2_min":   0.80,
        "success_L3_min":   0.80,
        "success_L4_min":   0.30,
        "warn_only":        True,
    },
]


class MilestoneCallback(BaseCallback):
    """
    Parameters
    ----------
    curriculum_callback : CurriculumCallback | None
        The curriculum callback instance -- used to read per-difficulty
        success buffers. Set after construction via .attach_curriculum().
    verbose : int
    """

    def __init__(self, curriculum_callback=None, verbose: int = 1) -> None:
        super().__init__(verbose=verbose)
        self._curriculum = curriculum_callback
        self._fired_steps: set[int] = set()
        # Allow tests to inject a metrics provider; production sources from PPO/curriculum
        self._metrics_provider: Callable[[int], dict] | None = None

    def attach_curriculum(self, curriculum_callback) -> None:
        self._curriculum = curriculum_callback

    def _on_training_start(self) -> None:
        """On resume from checkpoint, skip milestones whose step is already past.

        SB3 sets self.num_timesteps from the loaded checkpoint before _on_training_start
        is called, so this correctly populates _fired_steps to prevent re-firing
        milestones that were evaluated in a previous training session.
        """
        for ms in MILESTONES:
            if self.num_timesteps >= ms["step"]:
                self._fired_steps.add(ms["step"])
                if self.verbose >= 1:
                    print(f"[Milestone {ms['step']:,}] SKIP (already passed at resume)")

    def _gather_metrics(self) -> dict:
        """Read the latest PPO + curriculum metrics."""
        if self._metrics_provider is not None:
            return self._metrics_provider(self.num_timesteps)

        metrics: dict = {}
        # Pull approx_kl + entropy_loss from SB3 logger (recorded by PPO.train())
        log_vals = getattr(self.logger, "name_to_value", {})
        metrics["approx_kl"]    = float(log_vals.get("train/approx_kl", 0.0))
        metrics["entropy_loss"] = float(log_vals.get("train/entropy_loss", 0.0))

        if self._curriculum is not None:
            with self._curriculum._buf_lock:
                for lvl in (1, 2, 3, 4):
                    buf = list(self._curriculum._diff_success.get(lvl, []))
                    if buf:
                        rate = sum(buf) / len(buf)
                    else:
                        rate = 0.0
                    metrics[f"success_rate_L{lvl}"] = rate
        return metrics

    def _check_milestone(self, step: int) -> bool:
        """Return True to continue training, False (or raise) to abort."""
        ms = next((m for m in MILESTONES if m["step"] == step), None)
        if ms is None:
            return True

        metrics = self._gather_metrics()
        failures: list[str] = []

        if "approx_kl_max" in ms and metrics.get("approx_kl", 0.0) > ms["approx_kl_max"]:
            failures.append(
                f"approx_kl={metrics['approx_kl']:.4f} > {ms['approx_kl_max']}"
            )
        if "entropy_min" in ms and metrics.get("entropy_loss", 0.0) < ms["entropy_min"]:
            failures.append(
                f"entropy_loss={metrics['entropy_loss']:.3f} < {ms['entropy_min']}"
            )
        for lvl in (1, 2, 3, 4):
            key = f"success_L{lvl}_min"
            if key in ms:
                got = metrics.get(f"success_rate_L{lvl}", 0.0)
                if got < ms[key]:
                    failures.append(f"L{lvl} success={got:.2f} < {ms[key]}")

        if not failures:
            if self.verbose >= 1:
                print(f"[Milestone {step:,}] PASS")
            return True

        msg = (
            f"[Milestone {step:,}] {'WARN' if ms.get('warn_only') else 'FAIL'}: "
            + "; ".join(failures)
        )
        if ms.get("warn_only"):
            if self.verbose >= 1:
                print(msg)
            return True

        # Hard fail -- return False so SB3's learn() loop terminates cleanly.
        if self.verbose >= 1:
            print(msg)
        return False

    def _on_step(self) -> bool:
        # Fire each milestone once when num_timesteps first crosses its step.
        for ms in MILESTONES:
            step = ms["step"]
            if step in self._fired_steps:
                continue
            if self.num_timesteps >= step:
                self._fired_steps.add(step)
                if not self._check_milestone(step):
                    return False  # abort
        return True
