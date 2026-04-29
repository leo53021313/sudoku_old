"""Tests for Technique 10: X-Wing elimination."""

import numpy as np
import pytest
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.x_wing import find_x_wing_elimination


def _empty_eng():
    return CandidateEngine(np.zeros((9, 9), dtype=np.int8))


def test_no_x_wing_on_empty_board():
    # On a completely empty board every row has 9 candidate positions for each
    # digit, so no row has exactly 2. X-Wing cannot fire.
    assert find_x_wing_elimination(_empty_eng()) is None


def test_x_wing_in_rows_eliminates():
    """Classic row-based X-Wing.

    For digit 5:
    - Row 0: d=5 appears only at cols 1 and 4  → pair (1, 4)
    - Row 3: d=5 appears only at cols 1 and 4  → same pair (1, 4)
    - All other rows have d=5 only at cols other than 1/4 in their candidate
      sets, EXCEPT row 6 which still has d=5 at col 1.

    Expected elimination: ('eliminate', 6, 1, 5)
    """
    eng = _empty_eng()
    # Remove digit 5 from every cell's candidates except the specific ones we want.
    # Strategy: use _cands mutations for surgical control.

    # First, clear 5 from ALL cells
    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(5)

    # Row 0: d=5 only at cols 1 and 4
    eng._cands[0][1].add(5)
    eng._cands[0][4].add(5)

    # Row 3: d=5 only at cols 1 and 4 (same columns → X-Wing pair)
    eng._cands[3][1].add(5)
    eng._cands[3][4].add(5)

    # Another row (row 6) has d=5 at col 1 — this is the elimination target
    eng._cands[6][1].add(5)

    result = find_x_wing_elimination(eng)
    assert result is not None, "Expected an X-Wing elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 5
    assert r not in (0, 3), "Should not eliminate from X-Wing base rows"
    assert c in (1, 4), "Should eliminate from one of the X-Wing columns"
    # Specifically row 6, col 1
    assert (r, c) == (6, 1)


def test_x_wing_in_cols_eliminates():
    """Cols-based X-Wing (symmetric).

    For digit 7:
    - Col 2: d=7 appears only at rows 0 and 5
    - Col 6: d=7 appears only at rows 0 and 5
    - Row 0, col 8 still has d=7 — elimination target.
    """
    eng = _empty_eng()

    # Clear 7 from all cells
    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(7)

    # Col 2: d=7 only at rows 0 and 5
    eng._cands[0][2].add(7)
    eng._cands[5][2].add(7)

    # Col 6: d=7 only at rows 0 and 5 (same rows → X-Wing cols pattern)
    eng._cands[0][6].add(7)
    eng._cands[5][6].add(7)

    # row 0 has d=7 at col 8 — elimination target
    eng._cands[0][8].add(7)

    result = find_x_wing_elimination(eng)
    assert result is not None, "Expected a cols X-Wing elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 7
    assert c not in (2, 6), "Should not eliminate from X-Wing base cols"
    assert r in (0, 5), "Should eliminate from one of the X-Wing rows"
    assert (r, c) == (0, 8)


def test_x_wing_no_elimination_when_only_base_cells():
    """When only the X-Wing base cells have the digit, no other cells to eliminate from."""
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(3)

    # Row 1: d=3 only at cols 2 and 7
    eng._cands[1][2].add(3)
    eng._cands[1][7].add(3)

    # Row 4: d=3 only at cols 2 and 7
    eng._cands[4][2].add(3)
    eng._cands[4][7].add(3)

    # No other cells have d=3 → nothing to eliminate
    result = find_x_wing_elimination(eng)
    assert result is None


def test_x_wing_requires_exactly_two_cells_per_row():
    """A row with 3 candidates for d does NOT participate in X-Wing."""
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c].discard(4)

    # Row 0: d=4 at cols 1, 4, 7 (THREE columns — not a valid X-Wing row)
    eng._cands[0][1].add(4)
    eng._cands[0][4].add(4)
    eng._cands[0][7].add(4)

    # Row 3: d=4 only at cols 1 and 4 (valid pair)
    eng._cands[3][1].add(4)
    eng._cands[3][4].add(4)

    # Row 6: potential elimination target at col 1
    eng._cands[6][1].add(4)

    # Row 0 is NOT a valid X-Wing row (3 candidates), so no X-Wing fires
    result = find_x_wing_elimination(eng)
    assert result is None
