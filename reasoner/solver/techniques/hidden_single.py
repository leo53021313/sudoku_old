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


def justifies_hidden_single(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does hidden-single reasoning justify the given action?

    True iff action is ('fill', r, c, v) where v is a candidate of (r, c) AND
    in some unit (row, col, or box) containing (r, c), no other empty cell
    has v as a candidate.
    """
    op, r, c, v = action
    if op != 'fill':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    # Row check: is (r, c) the only place v can go in row r?
    only_in_row = all(
        not (engine.is_empty(r, cc) and v in engine.get_candidates(r, cc))
        for cc in range(9) if cc != c
    )
    if only_in_row:
        return True
    # Col check
    only_in_col = all(
        not (engine.is_empty(rr, c) and v in engine.get_candidates(rr, c))
        for rr in range(9) if rr != r
    )
    if only_in_col:
        return True
    # Box check
    br, bc = (r // 3) * 3, (c // 3) * 3
    only_in_box = all(
        (rr, cc) == (r, c) or not (engine.is_empty(rr, cc) and v in engine.get_candidates(rr, cc))
        for rr in range(br, br + 3) for cc in range(bc, bc + 3)
    )
    return only_in_box
