"""Technique-tiered curriculum: strict advance, demote on stuck."""

from __future__ import annotations
from typing import Optional

from stable_baselines3.common.callbacks import BaseCallback


# Stage definitions: stage N includes max_tech in (STAGE_MAX_TECH[N-1], STAGE_MAX_TECH[N]].
# None means "no upper bound" — final stage catches everything else (incl. tech 17 T&E
# and any puzzle where the v1 solver couldn't conclude with deterministic techniques).
#
# 5 stages mapping the technique tiers from the spec:
#   Stage 1: tech 1-3   — naked / hidden single, basic pencil marks
#   Stage 2: tech 4-7   — naked/hidden pair, pointing pair, box-line reduction
#   Stage 3: tech 8-9   — naked triple/quad
#   Stage 4: tech 10-13 — X-Wing, Swordfish, XY-Wing, XYZ-Wing
#   Stage 5: tech 14-17 — chains/coloring/AIC/T&E (incl. unsolvable-by-v1 catchall)
STAGE_MAX_TECH: dict[int, Optional[int]] = {
    1: 3,
    2: 7,
    3: 9,
    4: 13,
    5: None,
}


class TechniqueCurriculumCallback(BaseCallback):
    """Advance only on real reserved-eval success.

    Parameters
    ----------
    puzzle_labels : dict[str, int]
        Mapping puzzle_id (str) → max_tech (int). -1 means v1 solver failed.
    eval_threshold : float
        success_rate threshold to count as a "passing" eval (default 0.80).
    consec_pass_required : int
        Consecutive passing evals to advance (default 3).
    demote_window_steps : int
        Steps of no progress (vs entry success_rate) before demotion (default 50_000).
    verbose : int
    """

    def __init__(
        self,
        puzzle_labels: dict[str, int],
        eval_threshold: float = 0.80,
        consec_pass_required: int = 3,
        demote_window_steps: int = 50_000,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self._labels = puzzle_labels
        self._threshold = eval_threshold
        self._consec_pass_required = consec_pass_required
        self._demote_window = demote_window_steps

        self._stage_idx = 0  # 0-indexed; stage_idx=0 → Stage 1
        self._consec_pass = 0
        self._stage_entry_step = 0
        self._stage_entry_rate = 0.0

    @property
    def stage_idx(self) -> int:
        return self._stage_idx

    @property
    def current_stage(self) -> int:
        return self._stage_idx + 1

    def puzzle_ids_for_stage(self, stage: int) -> list[int]:
        """Return integer puzzle ids whose max_tech labels match this stage."""
        upper = STAGE_MAX_TECH[stage]
        prev_upper = STAGE_MAX_TECH.get(stage - 1, 0) if stage > 1 else 0

        result: list[int] = []
        for pid_str, mt in self._labels.items():
            pid = int(pid_str)
            # Stage 3: catches mt == -1 OR mt > prev_upper
            if upper is None:
                if mt == -1 or mt > prev_upper:
                    result.append(pid)
            else:
                if mt != -1 and prev_upper < mt <= upper:
                    result.append(pid)
        return result

    def record_eval(self, stage: int, success_rate: float) -> None:
        """Called externally (e.g., by SudokuEvalCallback) after each eval."""
        if stage != self.current_stage:
            return
        if success_rate >= self._threshold:
            self._consec_pass += 1
        else:
            self._consec_pass = 0
        if self._consec_pass >= self._consec_pass_required:
            self._advance()

    def _advance(self) -> None:
        if self._stage_idx + 1 >= len(STAGE_MAX_TECH):
            return
        self._stage_idx += 1
        self._consec_pass = 0
        self._stage_entry_step = self.num_timesteps if hasattr(self, "num_timesteps") else 0
        self._stage_entry_rate = 0.0
        if self.verbose >= 1:
            print(f"[Curriculum] Advanced to Stage {self.current_stage}")

    def _demote(self) -> None:
        if self._stage_idx == 0:
            return
        self._stage_idx -= 1
        self._consec_pass = 0
        if self.verbose >= 1:
            print(f"[Curriculum] Demoted to Stage {self.current_stage}")

    def _on_step(self) -> bool:
        return True  # event-driven via record_eval()
