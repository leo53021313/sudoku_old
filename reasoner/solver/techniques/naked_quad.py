"""Technique 9: Naked Quad.

Within a unit (row/col/box), four empty cells whose **union of candidates
has exactly 4 distinct digits**. Eliminate those 4 digits from all OTHER
empty cells in the unit.

Each participating cell must have at least 2 candidates (naked singles are
not subsumed into a naked quad).

Returns the FIRST effective ('eliminate', r, c, v) action found, or None.
"""

from __future__ import annotations
from itertools import combinations
from reasoner.solver.candidate_engine import CandidateEngine


def _empty_cells_in_row(eng: CandidateEngine, r: int) -> list[tuple[int, int]]:
    return [(r, c) for c in range(9) if eng.is_empty(r, c)]


def _empty_cells_in_col(eng: CandidateEngine, c: int) -> list[tuple[int, int]]:
    return [(r, c) for r in range(9) if eng.is_empty(r, c)]


def _empty_cells_in_box(eng: CandidateEngine, br: int, bc: int) -> list[tuple[int, int]]:
    return [
        (r, c)
        for r in range(br, br + 3)
        for c in range(bc, bc + 3)
        if eng.is_empty(r, c)
    ]


def _check_unit(
    eng: CandidateEngine, cells: list[tuple[int, int]]
) -> tuple[str, int, int, int] | None:
    """Look for a naked quad among the empty cells of this unit."""
    n = len(cells)
    cands_cache = [eng.get_candidates(*cell) for cell in cells]

    for i, j, k, l in combinations(range(n), 4):
        # Skip degenerate naked singles
        if (
            len(cands_cache[i]) < 2
            or len(cands_cache[j]) < 2
            or len(cands_cache[k]) < 2
            or len(cands_cache[l]) < 2
        ):
            continue
        union = cands_cache[i] | cands_cache[j] | cands_cache[k] | cands_cache[l]
        if len(union) != 4:
            continue
        # Found a naked quad; eliminate its digits from other cells in unit
        quad_indices = (i, j, k, l)
        for m in range(n):
            if m in quad_indices:
                continue
            rr, cc = cells[m]
            for d in union:
                if d in cands_cache[m]:
                    return ('eliminate', rr, cc, d)
    return None


def find_naked_quad_elimination(
    engine: CandidateEngine,
) -> tuple[str, int, int, int] | None:
    # Rows
    for r in range(9):
        result = _check_unit(engine, _empty_cells_in_row(engine, r))
        if result is not None:
            return result
    # Cols
    for c in range(9):
        result = _check_unit(engine, _empty_cells_in_col(engine, c))
        if result is not None:
            return result
    # Boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            result = _check_unit(engine, _empty_cells_in_box(engine, br, bc))
            if result is not None:
                return result
    return None
