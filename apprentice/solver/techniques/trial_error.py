"""Technique 17: Trial & Error elimination via backtracking.

This is a LAST RESORT technique — it should only fire when all simpler
deterministic techniques have failed to make progress.

For each empty cell (r, c) — iterated in ascending candidate-count order —
hypothesise each candidate value v:
  - Clone the board, set board[r,c] = v, run the backtracking solver.
  - If solve() returns None (no solution exists with that hypothesis),
    v cannot be the answer at (r, c) and can be eliminated.
  - Return the first such ('eliminate', r, c, v) found.

Returns None if every candidate is consistent with at least one solution.
"""

from __future__ import annotations
import numpy as np
from apprentice.solver.candidate_engine import CandidateEngine
from apprentice.solver_ext.backtracking import solve


def justifies_trial_error(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does trial-and-error reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and hypothesising board[r,c] = v leads to no solution.
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False
    board_copy = engine.board.copy()
    board_copy[r, c] = v
    return solve(board_copy) is None


def find_trial_error_elimination(
    engine: CandidateEngine,
) -> tuple[str, int, int, int] | None:
    """Return ('eliminate', r, c, v) for the first candidate that provably
    leads to a contradiction, or None if all candidates are consistent."""

    # Collect empty cells with 2+ candidates (naked singles are handled by
    # simpler techniques and excluded here to avoid redundant backtracking).
    cells: list[tuple[int, int, int, set[int]]] = []
    for r in range(9):
        for c in range(9):
            if engine.is_empty(r, c):
                cands = engine.get_candidates(r, c)
                if len(cands) >= 2:
                    cells.append((len(cands), r, c, cands))

    # Fewest candidates first — more likely to trigger an early contradiction.
    cells.sort(key=lambda t: t[0])

    for _, r, c, cands in cells:
        for v in sorted(cands):
            board_copy = engine.board.copy()
            board_copy[r, c] = v
            if solve(board_copy) is None:
                # Placing v at (r,c) leads to no valid solution → eliminate.
                return ('eliminate', r, c, v)

    return None
