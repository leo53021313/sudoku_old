"""Technique 7: Box-Line Reduction (line → box).

Within a row (or column), if all candidates of digit d lie within a single
3×3 box, eliminate d from the rest of that box outside the row (column).

Returns first effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


def find_box_line_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    # Row → box reduction
    for r in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for c in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            ]
            if len(cells_with_d) < 2:
                continue
            cols = [c for _, c in cells_with_d]
            box_col = cols[0] // 3
            if all(c // 3 == box_col for c in cols):
                # All in one box-column band; box is at row band r//3, col band box_col
                br = (r // 3) * 3
                bc = box_col * 3
                for rr in range(br, br + 3):
                    if rr == r:
                        continue
                    for cc in range(bc, bc + 3):
                        if engine.is_empty(rr, cc) and d in engine.get_candidates(rr, cc):
                            return ('eliminate', rr, cc, d)

    # Col → box reduction
    for c in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for r in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            ]
            if len(cells_with_d) < 2:
                continue
            rows = [r for r, _ in cells_with_d]
            box_row = rows[0] // 3
            if all(r // 3 == box_row for r in rows):
                br = box_row * 3
                bc = (c // 3) * 3
                for rr in range(br, br + 3):
                    for cc in range(bc, bc + 3):
                        if cc == c:
                            continue
                        if engine.is_empty(rr, cc) and d in engine.get_candidates(rr, cc):
                            return ('eliminate', rr, cc, d)
    return None


def justifies_box_line(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does box-line reduction justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and there exists a row R (or col C) such that all cells in R
    (or C) where v is a candidate (at least 2) lie in a single 3x3 box B, and
    (r, c) is in B but NOT in R (or C).
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    # Row → box check
    for row in range(9):
        cells_with_v = [
            (row, cc) for cc in range(9)
            if engine.is_empty(row, cc) and v in engine.get_candidates(row, cc)
        ]
        if len(cells_with_v) < 2:
            continue
        cols = [cc for _, cc in cells_with_v]
        box_col = cols[0] // 3
        if all(cc // 3 == box_col for cc in cols):
            # All candidates in row lie in single box column band
            br = (row // 3) * 3
            bc = box_col * 3
            # (r, c) must be in that box but NOT in the row
            if br <= r < br + 3 and bc <= c < bc + 3 and r != row:
                return True

    # Col → box check
    for col in range(9):
        cells_with_v = [
            (rr, col) for rr in range(9)
            if engine.is_empty(rr, col) and v in engine.get_candidates(rr, col)
        ]
        if len(cells_with_v) < 2:
            continue
        rows = [rr for rr, _ in cells_with_v]
        box_row = rows[0] // 3
        if all(rr // 3 == box_row for rr in rows):
            # All candidates in col lie in single box row band
            br = box_row * 3
            bc = (col // 3) * 3
            # (r, c) must be in that box but NOT in the col
            if br <= r < br + 3 and bc <= c < bc + 3 and c != col:
                return True

    return False
