"""RewardComputer: solver-match reward.

Reward design (spec §6.2):
  - Wrong fill: -1, terminate if wrong_count >= MAX_WRONG (20)
  - Correct fill, board complete: +20 (terminates)
  - Correct fill matches solver's chosen action at technique T: +1 + TECH_BONUS[T]
  - Correct fill, solver suggests something else (or solver couldn't): +0.3
"""

from __future__ import annotations
import numpy as np

from reasoner.solver.human_solver import HumanSolver


MAX_WRONG = 20

TECH_BONUS: dict[int, float] = {
    1: 0.0,   # naked single
    2: 0.5,   # hidden single
    3: 0.0,   # basic elim (engine-internal)
    4: 1.0,   # naked pair
    5: 1.0,   # hidden pair
    6: 1.0,   # pointing pair
    7: 1.0,   # box-line
}


class RewardComputer:
    """Compute reward + commit fill on the env's board.

    Attached to a SudokuGymEnv (or any object exposing
    .board, .solution, .candidates_cache, .candidate_count_grid, .wrong_count).
    """

    def __init__(self, env: object) -> None:
        self._env = env
        self._solver = HumanSolver()

    def compute(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env

        # Check correctness against ORIGINAL solution (set at reset())
        is_correct = (int(v) == int(env.solution[r, c]))

        if not is_correct:
            env.wrong_count += 1
            self._commit_fill(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated

        # Compute solver suggestion BEFORE committing
        solver_action, tech_id = self._solver.suggest(env.board)

        # Commit the correct fill
        self._commit_fill(r, c, v)

        # Board complete check
        if bool(np.all(env.board != 0)):
            return 20.0, True

        # Compare to solver suggestion
        if solver_action is None:
            return 0.3, False
        if solver_action == ('fill', r, c, v):
            return 1.0 + TECH_BONUS.get(tech_id, 0.0), False
        # Correct but not the solver's choice
        return 0.3, False

    def _commit_fill(self, r: int, c: int, v: int) -> None:
        env = self._env
        env.board[r, c] = v
        env.candidates_cache[r][c] = set()
        env.candidate_count_grid[r, c] = 0

        related: set[tuple[int, int]] = set()
        for cc in range(9):
            related.add((r, cc))
        for rr in range(9):
            related.add((rr, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                related.add((rr, cc))
        related.discard((r, c))

        for rr, cc in related:
            if env.board[rr, cc] != 0:
                continue
            env.candidates_cache[rr][cc].discard(v)
            cnt = len(env.candidates_cache[rr][cc])
            env.candidate_count_grid[rr, cc] = cnt
