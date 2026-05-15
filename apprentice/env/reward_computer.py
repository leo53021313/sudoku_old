"""RewardComputer: action-justification reward for fill + eliminate actions.

Reward structure (action-justification model):

For ANY action ('fill' or 'eliminate'):
  1. If the action would destroy the puzzle (wrong fill, or eliminate the
     correct solution value): -1, wrong_count++, terminate if >= MAX_WRONG.
  2. If correct fill completes the board: +50 (terminates).
  3. Otherwise, ask the human-style solver: what is the SIMPLEST cookbook
     technique that JUSTIFIES this action? Reward = 1.0 + TECH_BONUS[that_tech].
     - "Justifies" means: technique T's reasoning, applied to the current
       board state, would produce exactly this (mode, r, c, v) action.
     - The simplest justifier wins (lowest tech_id), so an agent always
       gets credit at least as high as the easiest reasoning.
  4. If no technique justifies the action (legal candidate-state change but
     not on any cookbook path): small reward — +0.3 for fills, +0.1 for
     eliminates. Discourages spam without prohibiting exploration.

This replaces the earlier "match solver.suggest()" reward model. Under the
old model, only the FIRST-priority technique's bonus was reachable, which
meant high-tier bonuses (X-Wing, XY-Wing, XYZ-Wing, T&E) were unreachable
whenever an easier technique fired anywhere else on the board.

Action mask in the env permits ANY (r, c, v) where v is currently a
candidate at empty (r, c). Solution-correctness is checked here, not in
the mask, to avoid leaking the answer.
"""

from __future__ import annotations
import numpy as np

from apprentice.solver.human_solver import HumanSolver


MAX_WRONG = 20

TECH_BONUS: dict[int, float] = {
    # Fill techniques
    1: 0.0,   # naked single
    2: 0.5,   # hidden single
    3: 0.0,   # basic elim (engine-internal)
    # Pair / locked-candidate techniques
    4: 1.0,   # naked pair
    5: 1.0,   # hidden pair
    6: 1.0,   # pointing pair
    7: 1.0,   # box-line reduction
    # Tier A.2-A.3: harder pattern techniques get larger bonuses
    8:  1.5,  # naked triple
    9:  1.5,  # naked quad
    10: 2.0,  # X-Wing
    11: 2.5,  # Swordfish
    12: 2.5,  # XY-Wing
    13: 3.0,  # XYZ-Wing
    # Last-resort technique
    17: 3.0,  # Trial & Error (backtracking-based search)
}


class RewardComputer:
    """Compute reward + commit (fill or eliminate) on the env's board state.

    Attached to a SudokuGymEnv (or any duck-typed env exposing
    .board, .solution, .candidates_cache, .candidate_count_grid, .wrong_count).
    """

    def __init__(self, env: object) -> None:
        self._env = env
        self._solver = HumanSolver()

    # ── Public dispatch ───────────────────────────────────────────────────────

    def compute(self, mode: str, r: int, c: int, v: int) -> tuple[float, bool]:
        if mode == "fill":
            return self._compute_fill(r, c, v)
        if mode == "eliminate":
            return self._compute_eliminate(r, c, v)
        raise ValueError(f"Unknown action mode: {mode!r}")

    # ── Fill path ─────────────────────────────────────────────────────────────

    def _compute_fill(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_correct = (int(v) == int(env.solution[r, c]))

        if not is_correct:
            env.wrong_count += 1
            self._commit_fill(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated

        # Find the simplest technique that justifies this fill BEFORE committing,
        # so the engine state seen by justifies_* reflects the agent's decision context.
        tech_id = self._solver.find_simplest_justifier(env.board, ("fill", r, c, v))

        self._commit_fill(r, c, v)

        if bool(np.all(env.board != 0)):
            return 50.0, True

        if tech_id is not None:
            return 1.0 + TECH_BONUS.get(tech_id, 0.0), False

        # Correct fill but no cookbook reasoning produces it (lucky correct).
        return 0.3, False

    # ── Eliminate path ────────────────────────────────────────────────────────

    def _compute_eliminate(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_bad = (int(v) == int(env.solution[r, c]))

        if is_bad:
            env.wrong_count += 1
            self._discard_candidate(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated

        # Same justifier-based grading as the fill path.
        tech_id = self._solver.find_simplest_justifier(env.board, ("eliminate", r, c, v))

        self._discard_candidate(r, c, v)

        if tech_id is not None:
            return 1.0 + TECH_BONUS.get(tech_id, 0.0), False

        # Legal candidate removal but no cookbook technique justifies it.
        return 0.1, False

    # ── Mutators ──────────────────────────────────────────────────────────────

    def _commit_fill(self, r: int, c: int, v: int) -> None:
        env = self._env
        env.board[r, c] = v
        env.candidates_cache[r][c] = set()
        env.candidate_count_grid[r, c] = 0

        for rr, cc in self._related_cells(r, c):
            if env.board[rr, cc] != 0:
                continue
            env.candidates_cache[rr][cc].discard(v)
            env.candidate_count_grid[rr, cc] = len(env.candidates_cache[rr][cc])

    def _discard_candidate(self, r: int, c: int, v: int) -> None:
        """Remove v from (r,c)'s candidate set. Does not touch board[r,c]."""
        env = self._env
        env.candidates_cache[r][c].discard(v)
        env.candidate_count_grid[r, c] = len(env.candidates_cache[r][c])

    @staticmethod
    def _related_cells(r: int, c: int):
        seen: set[tuple[int, int]] = set()
        for cc in range(9):
            seen.add((r, cc))
        for rr in range(9):
            seen.add((rr, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                seen.add((rr, cc))
        seen.discard((r, c))
        return seen
