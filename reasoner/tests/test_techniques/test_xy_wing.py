"""Tests for Technique 12: XY-Wing elimination."""

import numpy as np
import pytest
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.xy_wing import find_xy_wing_elimination, justifies_xy_wing


def _empty_eng():
    return CandidateEngine(np.zeros((9, 9), dtype=np.int8))


def test_no_xy_wing_on_empty_board():
    # On a completely empty board every empty cell has candidates {1..9} (9 digits),
    # so no bivalue cells exist. XY-Wing cannot fire.
    assert find_xy_wing_elimination(_empty_eng()) is None


def test_xy_wing_eliminates():
    """Classic XY-Wing.

    Pivot at (0,0) = {1, 2}
    Wing1 at (0,3) = {1, 3}  (peer of pivot via row 0)
    Wing2 at (3,0) = {2, 3}  (peer of pivot via col 0)

    z = 3; cell (3,3) sees both wings:
      - sees Wing1 (0,3) via col 3
      - sees Wing2 (3,0) via row 3
    If (3,3) has {3,4,5}, then 3 should be eliminated.
    """
    eng = _empty_eng()

    # Clear all candidates first for surgical control
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    # Set up pivot and wings
    eng._cands[0][0] = {1, 2}   # pivot P
    eng._cands[0][3] = {1, 3}   # wing1 W1 — peer of pivot via row 0
    eng._cands[3][0] = {2, 3}   # wing2 W2 — peer of pivot via col 0

    # Target cell (3,3): sees W1 via col 3, sees W2 via row 3
    eng._cands[3][3] = {3, 4, 5}

    result = find_xy_wing_elimination(eng)
    assert result is not None, "Expected XY-Wing elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 3
    assert (r, c) == (3, 3)


def test_xy_wing_returns_none_when_no_eliminations():
    """XY-Wing pattern exists but no cell sees both wings with z in candidates.

    Pivot at (0,0) = {1, 2}
    Wing1 at (0,3) = {1, 3}
    Wing2 at (3,0) = {2, 3}

    The only cell that could see both wings is (3,3) — but we give it
    candidates {4, 5} (no 3), so no elimination is possible.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    eng._cands[0][0] = {1, 2}   # pivot
    eng._cands[0][3] = {1, 3}   # wing1
    eng._cands[3][0] = {2, 3}   # wing2

    # Potential target cell does NOT have z=3
    eng._cands[3][3] = {4, 5}

    result = find_xy_wing_elimination(eng)
    assert result is None


def test_xy_wing_in_box():
    """XY-Wing where pivot and wings share a box.

    Pivot at (0,0) = {1, 2}
    Wing1 at (0,1) = {1, 3}  (peer via row + box)
    Wing2 at (1,0) = {2, 3}  (peer via col + box)

    z = 3; cell (1,1) sees all — it's in the same box as pivot,
    same col as Wing1 (col 1), same row as Wing2 (row 1).
    But for XY-Wing we only need it to see BOTH wings (not pivot).
    (1,1) sees Wing1 (0,1) via col 1 AND sees Wing2 (1,0) via row 1.
    If (1,1) has {3,5}, eliminate 3.
    """
    eng = _empty_eng()

    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()

    eng._cands[0][0] = {1, 2}   # pivot
    eng._cands[0][1] = {1, 3}   # wing1
    eng._cands[1][0] = {2, 3}   # wing2

    eng._cands[1][1] = {3, 5}   # sees wing1 via col 1, sees wing2 via row 1

    result = find_xy_wing_elimination(eng)
    assert result is not None, "Expected XY-Wing elimination but got None"
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 3
    assert (r, c) == (1, 1)


# ---------------------------------------------------------------------------
# justifies_xy_wing tests
# ---------------------------------------------------------------------------

def test_justifies_xy_wing_positive():
    """Classic XY-Wing: P=(0,0)={1,2}, W1=(0,3)={1,3}, W2=(3,0)={2,3}. Target (3,3)."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[0][0] = {1, 2}
    eng._cands[0][3] = {1, 3}
    eng._cands[3][0] = {2, 3}
    eng._cands[3][3] = {3, 4, 5}
    assert justifies_xy_wing(eng, ('eliminate', 3, 3, 3)) is True


def test_justifies_xy_wing_rejects_wrong_mode():
    """justifies_xy_wing returns False for 'fill' actions."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[0][0] = {1, 2}
    eng._cands[0][3] = {1, 3}
    eng._cands[3][0] = {2, 3}
    eng._cands[3][3] = {3, 4, 5}
    assert justifies_xy_wing(eng, ('fill', 3, 3, 3)) is False


def test_justifies_xy_wing_rejects_wrong_digit():
    """digit 4 is NOT the z-digit — not justified by this XY-Wing."""
    eng = _empty_eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._cands[0][0] = {1, 2}
    eng._cands[0][3] = {1, 3}
    eng._cands[3][0] = {2, 3}
    eng._cands[3][3] = {3, 4, 5}
    # digit 4 is not the z-digit (3) in this XY-Wing
    assert justifies_xy_wing(eng, ('eliminate', 3, 3, 4)) is False
