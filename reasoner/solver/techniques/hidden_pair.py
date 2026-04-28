"""Technique 5: Hidden Pair.

Within a unit, two digits {x,y} appear in candidate sets of EXACTLY two cells
(no more, no less). Those two cells must be x and y — strip all other digits
from those two cells' candidate sets.

Returns the first effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from itertools import combinations
from reasoner.solver.candidate_engine import CandidateEngine


def _check_unit_hidden_pair(eng: CandidateEngine, cells: list[tuple[int, int]]) -> tuple[str, int, int, int] | None:
    # For each pair of digits {x, y}: find cells in unit where x ∈ cands or y ∈ cands.
    # If EXACTLY 2 cells contain x AND those same 2 cells contain y, AND those cells have additional digits beyond {x,y},
    # we found a hidden pair.
    for x, y in combinations(range(1, 10), 2):
        cells_with_x = [(r, c) for r, c in cells if x in eng.get_candidates(r, c)]
        cells_with_y = [(r, c) for r, c in cells if y in eng.get_candidates(r, c)]
        if len(cells_with_x) == 2 and cells_with_x == cells_with_y:
            # Hidden pair {x,y} at these two cells
            for rr, cc in cells_with_x:
                cands = eng.get_candidates(rr, cc)
                extras = cands - {x, y}
                if extras:
                    # Return first extra digit to eliminate
                    return ('eliminate', rr, cc, min(extras))
    return None


def _empty_cells_in_row(eng, r):
    return [(r, c) for c in range(9) if eng.is_empty(r, c)]


def _empty_cells_in_col(eng, c):
    return [(r, c) for r in range(9) if eng.is_empty(r, c)]


def _empty_cells_in_box(eng, br, bc):
    return [(r, c) for r in range(br, br + 3) for c in range(bc, bc + 3) if eng.is_empty(r, c)]


def find_hidden_pair_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    for r in range(9):
        result = _check_unit_hidden_pair(engine, _empty_cells_in_row(engine, r))
        if result is not None:
            return result
    for c in range(9):
        result = _check_unit_hidden_pair(engine, _empty_cells_in_col(engine, c))
        if result is not None:
            return result
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            result = _check_unit_hidden_pair(engine, _empty_cells_in_box(engine, br, bc))
            if result is not None:
                return result
    return None
