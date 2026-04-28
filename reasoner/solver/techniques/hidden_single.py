"""Technique 2: Hidden Single.

Within some unit (row/col/box), a digit has only one cell where it can go.
Returns ('fill', r, c, v) or None.

Scan order: rows first (smallest r,c), then cols, then boxes. Within each
scan, first cell-digit pair wins (deterministic).
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


def find_hidden_single(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    # Rows
    for r in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for c in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                return ('fill', rr, cc, d)
    # Cols
    for c in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for r in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                return ('fill', rr, cc, d)
    # Boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            for d in range(1, 10):
                cells_with_d = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
                ]
                if len(cells_with_d) == 1:
                    rr, cc = cells_with_d[0]
                    return ('fill', rr, cc, d)
    return None
