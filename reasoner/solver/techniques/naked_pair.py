"""Technique 4: Naked Pair.

Two cells in a unit (row/col/box) share the SAME 2-element candidate set
{x,y}. Eliminate x and y from all OTHER empty cells in that unit.

Returns the FIRST effective ('eliminate', r, c, v) action it finds, or None.
"""

from __future__ import annotations
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


def _check_unit(eng: CandidateEngine, cells: list[tuple[int, int]]) -> tuple[str, int, int, int] | None:
    """For all pairs of cells in this unit, look for a naked pair."""
    n = len(cells)
    for i in range(n):
        ci = eng.get_candidates(*cells[i])
        if len(ci) != 2:
            continue
        for j in range(i + 1, n):
            cj = eng.get_candidates(*cells[j])
            if cj != ci:
                continue
            # Found pair: eliminate from other cells in unit
            pair_digits = ci
            for k in range(n):
                if k == i or k == j:
                    continue
                rr, cc = cells[k]
                cands = eng.get_candidates(rr, cc)
                for d in pair_digits:
                    if d in cands:
                        return ('eliminate', rr, cc, d)
    return None


def find_naked_pair_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
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
