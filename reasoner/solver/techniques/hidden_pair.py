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


def _iter_units(eng: CandidateEngine):
    """Yield each unit's cell list: 9 rows, 9 cols, 9 boxes."""
    for r in range(9):
        yield _empty_cells_in_row(eng, r)
    for c in range(9):
        yield _empty_cells_in_col(eng, c)
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            yield _empty_cells_in_box(eng, br, bc)


def justifies_hidden_pair(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does hidden-pair reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and there exists a unit U containing (r, c) where some pair of
    digits {x, y} appears in EXACTLY 2 empty cells of U, (r, c) is one of them,
    and v ∉ {x, y} (v is an extra digit being stripped from the pair cell).
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    for cells in _iter_units(engine):
        if (r, c) not in cells:
            continue
        for x, y in combinations(range(1, 10), 2):
            cells_with_x = [(rr, cc) for rr, cc in cells if x in engine.get_candidates(rr, cc)]
            cells_with_y = [(rr, cc) for rr, cc in cells if y in engine.get_candidates(rr, cc)]
            if len(cells_with_x) == 2 and cells_with_x == cells_with_y:
                # Hidden pair {x, y} at these two cells
                if (r, c) in cells_with_x and v not in {x, y}:
                    return True
    return False
