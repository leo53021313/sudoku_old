"""Technique 1: Naked Single.

A cell with exactly one candidate must be filled with that candidate.
Returns ('fill', r, c, v) or None.
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


def find_naked_single(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    """Scan for a cell with exactly one candidate.

    Returns the first naked single in row-major order, or None if none exist.
    """
    for r in range(9):
        for c in range(9):
            if not engine.is_empty(r, c):
                continue
            cands = engine.get_candidates(r, c)
            if len(cands) == 1:
                return ('fill', r, c, next(iter(cands)))
    return None
