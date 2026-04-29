"""RewardComputer: solver-aware reward for fill + eliminate actions.

Reward structure (route II — fill OR eliminate action):

FILL path:
  - Wrong fill (v != solution[r,c]): -1, wrong_count++, terminate if >= MAX_WRONG.
    The wrong value is still committed to the board (agent lives with it).
  - Correct fill, board complete: +20 (terminates).
  - Correct fill matching solver's fill suggestion at tech T: +1 + TECH_BONUS[T].
  - Correct fill not matching solver: +0.3 (lucky/correct but suboptimal path).

ELIMINATE path:
  - "Bad" eliminate (v == solution[r,c]): -1, wrong_count++, terminate if >= MAX_WRONG.
    The candidate is still removed (board becomes unsolvable; agent lives with it).
  - Valid eliminate matching solver's eliminate suggestion at tech T: +1 + TECH_BONUS[T].
    Techniques 4-7 (pair/pointing/box-line) finally have reachable bonuses.
  - Valid eliminate but not matching solver: +0.1 (legal candidate removal but not on
    the priority-loop's path; small reward to encourage exploration without spam).

Action mask in the env permits ANY (r,c,v) where v is a current candidate at empty
(r,c), so the legality check above mirrors what the agent could possibly send.
"""

from __future__ import annotations
import numpy as np

from reasoner.solver.human_solver import HumanSolver


MAX_WRONG = 20

TECH_BONUS: dict[int, float] = {
    1: 0.0,   # naked single (fill)
    2: 0.5,   # hidden single (fill)
    3: 0.0,   # basic elim (engine-internal)
    4: 1.0,   # naked pair (eliminate)
    5: 1.0,   # hidden pair (eliminate)
    6: 1.0,   # pointing pair (eliminate)
    7: 1.0,   # box-line (eliminate)
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

    # ── Fill path (route I logic, unchanged) ──────────────────────────────────

    def _compute_fill(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_correct = (int(v) == int(env.solution[r, c]))

        if not is_correct:
            env.wrong_count += 1
            self._commit_fill(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated

        # Solver suggestion is computed BEFORE committing the fill so it
        # reflects the same state the agent saw when picking its action.
        solver_action, tech_id = self._solver.suggest(env.board)

        self._commit_fill(r, c, v)

        if bool(np.all(env.board != 0)):
            return 20.0, True

        if solver_action == ("fill", r, c, v):
            return 1.0 + TECH_BONUS.get(tech_id, 0.0), False

        # Correct fill, but not the solver's first-priority choice (or solver had no fill).
        return 0.3, False

    # ── Eliminate path (new in route II) ──────────────────────────────────────

    def _compute_eliminate(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_bad = (int(v) == int(env.solution[r, c]))

        if is_bad:
            # Removing the correct answer destroys solvability; treat as wrong.
            env.wrong_count += 1
            self._discard_candidate(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated

        # Solver suggestion before applying the eliminate (same rationale as fill path).
        solver_action, tech_id = self._solver.suggest(env.board)

        self._discard_candidate(r, c, v)

        if solver_action == ("eliminate", r, c, v):
            return 1.0 + TECH_BONUS.get(tech_id, 0.0), False

        # Valid candidate removal but not on the solver's priority path.
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
