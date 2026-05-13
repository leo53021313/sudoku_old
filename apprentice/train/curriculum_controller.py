"""Adaptive curriculum controller for apprentice training.

Tracks per-episode success rate over a sliding window and adjusts
target_empty using a sweet-spot formula:

  sr > tolerance_band[1] → too easy, increase difficulty
  sr < tolerance_band[0] → too hard, decrease difficulty
  else                   → in sweet spot, no change

Plus a stagnation detector (see _check_stagnation) that probes upward
when target_empty hasn't moved for stagnation_threshold_steps, and
auto-rolls-back if the probe fails.

State (target_empty, success_window, etc.) is persistable to JSON for
training resume — see save() / load() in Task 12.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class CurriculumController:
    """See module docstring."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self.target_empty: float = float(config["initial_target_empty"])
        self._min_te: int = int(config["min_target_empty"])
        self._max_te: int = int(config["max_target_empty"])

        self._target_rate: float = float(config["target_rate"])
        self._lo: float = float(config["tolerance_band"][0])
        self._hi: float = float(config["tolerance_band"][1])
        self._step_size: float = float(config["step_size"])

        self._window_size: int = int(config["window_size"])
        self._min_eps: int = int(config["min_episodes_before_update"])
        self._min_steps_between: int = int(config["min_steps_between_updates"])

        self._stagn_threshold: int = int(config["stagnation_threshold_steps"])
        self._stagn_probe_step: int = int(config["stagnation_probe_step"])
        self._stagn_rollback_thresh: float = float(config["stagnation_rollback_threshold"])
        self._stagn_rollback_window: int = int(config["stagnation_rollback_window_steps"])

        self._success_window: deque[int] = deque(maxlen=self._window_size)
        self.last_advance_step: int = 0
        self.last_advance_direction: int = 0      # -1, 0, +1
        self.last_adjustment: float = 0.0
        self._probe_target: float | None = None    # set when probing
        self._probe_started_at: int = 0

    # ── Public API ────────────────────────────────────────────────────────

    @property
    def target_empty_rounded(self) -> int:
        return int(round(self.target_empty))

    def record_episode_outcome(self, success: bool) -> None:
        self._success_window.append(1 if success else 0)

    def success_rate(self) -> float:
        """0.0 if window is empty."""
        if not self._success_window:
            return 0.0
        return sum(self._success_window) / len(self._success_window)

    def update(self, current_step: int) -> None:
        """Possibly adjust target_empty based on recent success rate."""
        # Reset last_adjustment by default
        self.last_adjustment = 0.0

        # Phase 1: regular sweet-spot update
        self._regular_update(current_step)

        # Phase 2: stagnation detection / probe / rollback (implemented in Task 11)
        # (no-op for now; Task 11 fills this in)

    def in_sweet_spot(self) -> bool:
        sr = self.success_rate()
        return self._lo <= sr <= self._hi

    # ── Internals ─────────────────────────────────────────────────────────

    def _regular_update(self, current_step: int) -> None:
        if len(self._success_window) < self._min_eps:
            return

        if (current_step - self.last_advance_step) < self._min_steps_between and self.last_advance_step > 0:
            return

        sr = self.success_rate()

        if sr > self._hi:
            adj = (sr - self._hi) * self._step_size
            new_te = min(self._max_te, self.target_empty + adj)
            if int(round(new_te)) != int(round(self.target_empty)):
                self.target_empty = new_te
                self.last_advance_direction = +1
                self.last_advance_step = current_step
                self.last_adjustment = adj
            else:
                # Adj rounded to 0; treat as no-op
                self.last_advance_direction = 0

        elif sr < self._lo:
            adj = (self._lo - sr) * self._step_size
            new_te = max(self._min_te, self.target_empty - adj)
            if int(round(new_te)) != int(round(self.target_empty)):
                self.target_empty = new_te
                self.last_advance_direction = -1
                self.last_advance_step = current_step
                self.last_adjustment = -adj
            else:
                self.last_advance_direction = 0

        else:
            # In sweet spot
            self.last_advance_direction = 0
