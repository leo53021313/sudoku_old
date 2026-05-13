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
        self.last_adjustment = 0.0

        # Phase 0: handle in-flight probe (must come BEFORE regular update,
        # otherwise regular update might shadow probe rollback)
        if self._probe_target is not None:
            self._handle_active_probe(current_step)
            if self._probe_target is None:
                return  # probe just resolved; skip regular update this cycle

        # Phase 1: regular sweet-spot update
        self._regular_update(current_step)
        if self.last_advance_direction != 0:
            return  # regular update happened; no stagnation check needed this cycle

        # Phase 2: stagnation detection (only if regular update did nothing)
        self._maybe_probe_stagnation(current_step)

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

    def _maybe_probe_stagnation(self, current_step: int) -> None:
        """If target_empty hasn't advanced for stagnation_threshold_steps, probe +1."""
        if self._probe_target is not None:
            return  # already probing

        if len(self._success_window) < self._min_eps:
            return  # not enough data yet

        idle_steps = current_step - self.last_advance_step
        if idle_steps < self._stagn_threshold:
            return

        new_te = min(self._max_te, self.target_empty + self._stagn_probe_step)
        if int(round(new_te)) == int(round(self.target_empty)):
            # No-op probe (already at max)
            return

        self._probe_target = new_te
        self._probe_started_at = current_step
        # Snapshot the pre-probe target for rollback target tracking
        # (we already have it implicitly via probe_target - probe_step)

        # Apply the probe
        self.target_empty = new_te
        self.last_advance_step = current_step
        self.last_advance_direction = +1
        self.last_adjustment = float(self._stagn_probe_step)

    def _handle_active_probe(self, current_step: int) -> None:
        """If a probe is in flight, decide whether to roll back or clear it."""
        elapsed = current_step - self._probe_started_at
        if elapsed < self._stagn_rollback_window:
            return  # give the probe more time to evaluate

        sr = self.success_rate()
        if sr < self._stagn_rollback_thresh:
            # Probe failed — roll back to one step below probe_target
            rollback_te = max(self._min_te, self._probe_target - 1)
            self.target_empty = float(rollback_te)
            self.last_advance_step = current_step
            self.last_advance_direction = -1
            self.last_adjustment = -1.0
            self._probe_target = None
        elif sr >= self._lo:
            # Probe succeeded or at least not catastrophic — clear probe
            self._probe_target = None

    # ── Persistence ───────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """Serialize state to a JSON file at `path`."""
        import json
        from pathlib import Path

        state = {
            "target_empty": self.target_empty,
            "last_advance_step": self.last_advance_step,
            "last_advance_direction": self.last_advance_direction,
            "last_adjustment": self.last_adjustment,
            "probe_target": self._probe_target,
            "probe_started_at": self._probe_started_at,
            "success_window": list(self._success_window),
        }
        Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")

    def load(self, path: str) -> None:
        """Restore state from a JSON file. No-op if the file does not exist."""
        import json
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return  # leave controller at init state

        state = json.loads(p.read_text(encoding="utf-8"))
        self.target_empty = float(state["target_empty"])
        self.last_advance_step = int(state["last_advance_step"])
        self.last_advance_direction = int(state["last_advance_direction"])
        self.last_adjustment = float(state["last_adjustment"])
        self._probe_target = (
            float(state["probe_target"]) if state["probe_target"] is not None else None
        )
        self._probe_started_at = int(state["probe_started_at"])

        # Restore success window (preserve maxlen)
        self._success_window.clear()
        for v in state["success_window"]:
            self._success_window.append(int(v))
