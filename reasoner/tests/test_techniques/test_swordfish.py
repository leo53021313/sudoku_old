"""Tests for Technique 11: Swordfish elimination."""

import numpy as np
import pytest
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.swordfish import find_swordfish_elimination, justifies_swordfish


def _empty_eng():
    return CandidateEngine(np.zeros((9, 9), dtype=np.int8))


def test_no_swordfish_on_empty_board():
    # On a completely empty board every row has 9 candidate positions for each
    # digit — each row has len 9 which is > 3, so no row qualifies (need 2–3).
    assert find_swordfish_elimination(_empty_eng()) is None


def test_swordfish_in_rows_eliminates():
    """Classic row-based Swordfish.

    For digit 2:
    - Row 0: d=2 at cols {1, 4}         (2 cells)
    - Row 3: d=2 at cols {1, 7}         (2 cells)
    - Row 6: d=2 at cols {4, 7}         (2 cells)
    Union = {1, 4, 7} → exactly 3 cols → Swordfish.

    Elimination target: row 8, col 1 has d=2.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(2)

    # Swordfish base rows
    eng._cands[0][1].add(2)
    eng._cands[0][4].add(2)

    eng._cands[3][1].add(2)
    eng._cands[3][7].add(2)

    eng._cands[6][4].add(2)
    eng._cands[6][7].add(2)

    # Elimination target: row 8 col 1
    eng._cands[8][1].add(2)

    result = find_swordfish_elimination(eng)
    assert result is not None, "Expected a Swordfish elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 2
    assert r not in (0, 3, 6), "Should not eliminate from Swordfish base rows"
    assert c in (1, 4, 7), "Should eliminate from one of the Swordfish columns"
    assert (r, c) == (8, 1)


def test_swordfish_in_cols_eliminates():
    """Col-based Swordfish (symmetric).

    For digit 9:
    - Col 0: d=9 at rows {2, 5}
    - Col 3: d=9 at rows {2, 8}
    - Col 7: d=9 at rows {5, 8}
    Union = {2, 5, 8} → exactly 3 rows → Swordfish on cols.

    Elimination target: row 2, col 5 has d=9.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(9)

    # Swordfish base cols
    eng._cands[2][0].add(9)
    eng._cands[5][0].add(9)

    eng._cands[2][3].add(9)
    eng._cands[8][3].add(9)

    eng._cands[5][7].add(9)
    eng._cands[8][7].add(9)

    # Elimination target: row 2, col 5
    eng._cands[2][5].add(9)

    result = find_swordfish_elimination(eng)
    assert result is not None, "Expected a cols Swordfish elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 9
    assert c not in (0, 3, 7), "Should not eliminate from Swordfish base cols"
    assert r in (2, 5, 8), "Should eliminate from one of the Swordfish rows"
    assert (r, c) == (2, 5)


def test_swordfish_no_elimination_when_only_base_cells():
    """When no non-base cells have the digit in target columns, return None."""
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(6)

    # Swordfish rows for d=6
    eng._cands[1][0].add(6)
    eng._cands[1][3].add(6)

    eng._cands[4][0].add(6)
    eng._cands[4][6].add(6)

    eng._cands[7][3].add(6)
    eng._cands[7][6].add(6)

    # No other rows have d=6 in cols {0, 3, 6} → nothing to eliminate
    result = find_swordfish_elimination(eng)
    assert result is None


def test_swordfish_row_with_three_cells_still_qualifies():
    """A row having exactly 3 cells for d (all within the 3-col union) is valid.

    For digit 1:
    - Row 0: d=1 at cols {2, 5, 8}     (3 cells — valid)
    - Row 3: d=1 at cols {2, 5}         (2 cells — valid)
    - Row 6: d=1 at cols {5, 8}         (2 cells — valid)
    Union = {2, 5, 8} → exactly 3 cols → Swordfish.

    Elimination target: row 1, col 2 has d=1.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(1)

    eng._cands[0][2].add(1)
    eng._cands[0][5].add(1)
    eng._cands[0][8].add(1)

    eng._cands[3][2].add(1)
    eng._cands[3][5].add(1)

    eng._cands[6][5].add(1)
    eng._cands[6][8].add(1)

    # Elimination target: row 1, col 2
    eng._cands[1][2].add(1)

    result = find_swordfish_elimination(eng)
    assert result is not None, "Expected Swordfish elimination with a 3-cell row"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 1
    assert r not in (0, 3, 6)
    assert c in (2, 5, 8)
    assert (r, c) == (1, 2)


# ---------------------------------------------------------------------------
# justifies_swordfish tests
# ---------------------------------------------------------------------------

def test_justifies_swordfish_positive():
    """Row-based swordfish: rows 0,3,6 with d=2 union cols {1,4,7}. Eliminate from (8,1)."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(2)
    eng._cands[0][1].add(2); eng._cands[0][4].add(2)
    eng._cands[3][1].add(2); eng._cands[3][7].add(2)
    eng._cands[6][4].add(2); eng._cands[6][7].add(2)
    eng._cands[8][1].add(2)
    assert justifies_swordfish(eng, ('eliminate', 8, 1, 2)) is True


def test_justifies_swordfish_rejects_wrong_mode():
    """justifies_swordfish returns False for 'fill' actions."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(2)
    eng._cands[0][1].add(2); eng._cands[0][4].add(2)
    eng._cands[3][1].add(2); eng._cands[3][7].add(2)
    eng._cands[6][4].add(2); eng._cands[6][7].add(2)
    eng._cands[8][1].add(2)
    assert justifies_swordfish(eng, ('fill', 8, 1, 2)) is False


def test_justifies_swordfish_rejects_base_row():
    """Cell (0,1) is a swordfish base row — elimination there is not justified."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(2)
    eng._cands[0][1].add(2); eng._cands[0][4].add(2)
    eng._cands[3][1].add(2); eng._cands[3][7].add(2)
    eng._cands[6][4].add(2); eng._cands[6][7].add(2)
    eng._cands[8][1].add(2)
    # (0,1) is a base row cell — swordfish does not eliminate there
    assert justifies_swordfish(eng, ('eliminate', 0, 1, 2)) is False
