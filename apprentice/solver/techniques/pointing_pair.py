"""Technique 6: Pointing Pair (box → line reduction).

Within a 3×3 box, if all candidates of digit d lie in a single row (or
column), eliminate d from the rest of that row (column) outside the box.

Returns first effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from apprentice.solver.candidate_engine import CandidateEngine


def find_pointing_pair_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            for d in range(1, 10):
                cells_with_d = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
                ]
                if len(cells_with_d) < 2:
                    continue
                rows = {r for r, _ in cells_with_d}
                cols = {c for _, c in cells_with_d}
                # All in same row?
                if len(rows) == 1:
                    target_r = next(iter(rows))
                    for cc in range(9):
                        if bc <= cc < bc + 3:
                            continue  # skip cells inside the box
                        if engine.is_empty(target_r, cc) and d in engine.get_candidates(target_r, cc):
                            return ('eliminate', target_r, cc, d)
                # All in same col?
                if len(cols) == 1:
                    target_c = next(iter(cols))
                    for rr in range(9):
                        if br <= rr < br + 3:
                            continue
                        if engine.is_empty(rr, target_c) and d in engine.get_candidates(rr, target_c):
                            return ('eliminate', rr, target_c, d)
    return None


def justifies_pointing_pair(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does pointing-pair reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and there exists a 3x3 box B such that all cells in B where v is
    a candidate (at least 2) lie in a single row R or column C, and (r, c) is
    in R (or C) but NOT in box B.
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            cells_with_v = [
                (rr, cc)
                for rr in range(br, br + 3)
                for cc in range(bc, bc + 3)
                if engine.is_empty(rr, cc) and v in engine.get_candidates(rr, cc)
            ]
            if len(cells_with_v) < 2:
                continue
            rows_in_box = {rr for rr, _ in cells_with_v}
            cols_in_box = {cc for _, cc in cells_with_v}
            # All candidates in same row in this box?
            if len(rows_in_box) == 1:
                target_r = next(iter(rows_in_box))
                if r == target_r and not (br <= r < br + 3 and bc <= c < bc + 3):
                    return True
            # All candidates in same col in this box?
            if len(cols_in_box) == 1:
                target_c = next(iter(cols_in_box))
                if c == target_c and not (br <= r < br + 3 and bc <= c < bc + 3):
                    return True
    return False
