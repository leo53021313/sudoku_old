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
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver_ext.backtracking import solve


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
