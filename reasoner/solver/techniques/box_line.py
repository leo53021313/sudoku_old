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
