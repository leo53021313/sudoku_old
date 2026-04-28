"""Technique 6: Pointing Pair (box → line reduction).

Within a 3×3 box, if all candidates of digit d lie in a single row (or
column), eliminate d from the rest of that row (column) outside the box.

Returns first effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


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
