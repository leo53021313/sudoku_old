"""Tests for Technique 13: XYZ-Wing elimination."""

import numpy as np
import pytest
from apprentice.solver.candidate_engine import CandidateEngine
from apprentice.solver.techniques.xyz_wing import find_xyz_wing_elimination, justifies_xyz_wing


def _empty_eng():
    return CandidateEngine(np.zeros((9, 9), dtype=np.int8))


def test_no_xyz_wing_on_empty_board():
    # On a completely empty board every empty cell has candidates {1..9} (9 digits),
    # so no bivalue or trivalue cells exist. XYZ-Wing cannot fire.
    assert find_xyz_wing_elimination(_empty_eng()) is None


def test_xyz_wing_eliminates():
    """Classic XYZ-Wing with all three cells in the same box.

    Pivot at (0,0) = {1, 2, 3}  — trivalue
    Wing1 at (0,1) = {1, 3}     — peer via row 0 + box (0,0)
    Wing2 at (1,0) = {2, 3}     — peer via col 0 + box (0,0)

    z = 3. Cell (1,1) is in the same box and:
      - sees Pivot via box
      - sees Wing1 via col 1
      - sees Wing2 via row 1
    If (1,1) has {3, 5}, eliminate 3.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    eng._cands[0][0] = {1, 2, 3}  # pivot (trivalue)
    eng._cands[0][1] = {1, 3}     # wing1 (bivalue)
    eng._cands[1][0] = {2, 3}     # wing2 (bivalue)

    # Target: sees pivot via box, wing1 via col 1, wing2 via row 1
    eng._cands[1][1] = {3, 5}

    result = find_xyz_wing_elimination(eng)
    assert result is not None, "Expected XYZ-Wing elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 3
    assert (r, c) == (1, 1)


def test_xyz_wing_returns_none_when_no_eliminations():
    """XYZ-Wing pattern exists but no cell sees all three with z in candidates.

    Pivot at (0,0) = {1, 2, 3}
    Wing1 at (0,1) = {1, 3}
    Wing2 at (1,0) = {2, 3}

    Cell (1,1) would be the only candidate, but it has {4, 5} (no z=3).
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    eng._cands[0][0] = {1, 2, 3}  # pivot
    eng._cands[0][1] = {1, 3}     # wing1
    eng._cands[1][0] = {2, 3}     # wing2

    # Potential target does NOT have z=3
    eng._cands[1][1] = {4, 5}

    result = find_xyz_wing_elimination(eng)
    assert result is None


def test_xyz_wing_row_col_geometry():
    """XYZ-Wing with wings outside the box.

    Pivot at (4,4) = {1, 2, 3}
    Wing1 at (4,7) = {1, 3}  — peer via row 4
    Wing2 at (7,4) = {2, 3}  — peer via col 4

    Cell (7,7) sees:
      - Wing1 (4,7) via col 7
      - Wing2 (7,4) via row 7
      - Pivot (4,4) NOT via row/col; NOT same box (4,4 is box center (3,3), 7,7 is box (6,6))
    So (7,7) does NOT see all three — no elimination there.

    Cell (4,4) is the pivot itself — skip.

    No cell sees all three in this geometry (pivot and wings are not in the same box,
    and no single cell can see a row-4 cell, a col-4 cell, AND (4,4) simultaneously
    unless it's in the same box as the pivot — but boxes 3-5 row x 3-5 col only).

    Result should be None.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    eng._cands[4][4] = {1, 2, 3}  # pivot
    eng._cands[4][7] = {1, 3}     # wing1
    eng._cands[7][4] = {2, 3}     # wing2

    # (7,7) sees wing1 and wing2 but NOT pivot
    eng._cands[7][7] = {3, 6}

    result = find_xyz_wing_elimination(eng)
    assert result is None


# ---------------------------------------------------------------------------
# justifies_xyz_wing tests
# ---------------------------------------------------------------------------

def test_justifies_xyz_wing_positive():
    """Classic XYZ-Wing: P=(0,0)={1,2,3}, W1=(0,1)={1,3}, W2=(1,0)={2,3}. Target (1,1)."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[0][0] = {1, 2, 3}
    eng._cands[0][1] = {1, 3}
    eng._cands[1][0] = {2, 3}
    eng._cands[1][1] = {3, 5}
    assert justifies_xyz_wing(eng, ('eliminate', 1, 1, 3)) is True


def test_justifies_xyz_wing_rejects_wrong_mode():
    """justifies_xyz_wing returns False for 'fill' actions."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[0][0] = {1, 2, 3}
    eng._cands[0][1] = {1, 3}
    eng._cands[1][0] = {2, 3}
    eng._cands[1][1] = {3, 5}
    assert justifies_xyz_wing(eng, ('fill', 1, 1, 3)) is False


def test_justifies_xyz_wing_rejects_cell_not_seeing_pivot():
    """Cell (7,7) sees wing1 and wing2 but NOT pivot at (4,4) — not justified."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[4][4] = {1, 2, 3}
    eng._cands[4][7] = {1, 3}
    eng._cands[7][4] = {2, 3}
    eng._cands[7][7] = {3, 6}
    # (7,7) sees wing1 via col 7 and wing2 via row 7, but NOT pivot (4,4)
    assert justifies_xyz_wing(eng, ('eliminate', 7, 7, 3)) is False
