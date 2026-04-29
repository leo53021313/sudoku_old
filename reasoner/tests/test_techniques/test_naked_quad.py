import numpy as np
import pytest
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.naked_quad import find_naked_quad_elimination, justifies_naked_quad


def _eng(board=None):
    if board is None:
        board = np.zeros((9, 9), dtype=np.int8)
    return CandidateEngine(board)


def test_no_naked_quad_on_empty_board():
    """Empty board has full candidate sets — no naked quad exists."""
    assert find_naked_quad_elimination(_eng()) is None


def test_naked_quad_eliminates_in_row():
    """Four cells in row 0 form a naked quad over {1,2,3,4}; a digit from
    that set must be eliminated from another empty cell in the row."""
    eng = _eng()
    # Quad cells at (0,0)..(0,3) with union {1,2,3,4}
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {3, 4}
    eng._cands[0][3] = {1, 4}
    # Target cell at (0,4) has one of the quad digits
    eng._cands[0][4] = {1, 5, 6}
    # Remaining cells have no quad digits
    for c in range(5, 9):
        eng._cands[0][c] = {5, 6, 7, 8, 9}

    result = find_naked_quad_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert r == 0
    assert c == 4
    assert v in {1, 2, 3, 4}


def test_naked_quad_returns_none_when_no_other_targets():
    """If all non-quad cells in the unit are filled, there's nothing to eliminate."""
    eng = _eng()
    # Quad at (0,0)..(0,3)
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {3, 4}
    eng._cands[0][3] = {1, 4}
    # All other cells in row 0 are filled
    for c in range(4, 9):
        eng._board[0, c] = c + 1
        eng._cands[0][c] = set()

    result = find_naked_quad_elimination(eng)
    assert result is None


def test_naked_quad_eliminates_in_col():
    """Naked quad fires in a column."""
    eng = _eng()
    # Quad cells at rows 0..3, col 0, union {5,6,7,8}
    eng._cands[0][0] = {5, 6}
    eng._cands[1][0] = {6, 7}
    eng._cands[2][0] = {7, 8}
    eng._cands[3][0] = {5, 8}
    # Target at (4,0) has one of the quad digits
    eng._cands[4][0] = {5, 1, 2}
    # Other cells in col don't contain quad digits
    for r in range(5, 9):
        eng._cands[r][0] = {1, 2, 3, 4, 9}

    result = find_naked_quad_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert c == 0
    assert v in {5, 6, 7, 8}


def test_naked_quad_skips_naked_single_degenerate():
    """Cells with only 1 candidate (naked singles) are excluded from quad combinations."""
    eng = _eng()
    # (0,0) has only 1 candidate — degenerate, should not form part of a quad
    eng._cands[0][0] = {1}
    eng._cands[0][1] = {1, 2}
    eng._cands[0][2] = {2, 3}
    eng._cands[0][3] = {3, 4}
    eng._cands[0][4] = {1, 4}
    # Target has one of {1,2,3,4}
    eng._cands[0][5] = {1, 2, 5, 6}
    for c in range(6, 9):
        eng._cands[0][c] = {5, 6, 7, 8, 9}

    # (0,1)+(0,2)+(0,3)+(0,4) union={1,2,3,4}: all len>=2, should fire
    result = find_naked_quad_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v in {1, 2, 3, 4}


# ---------------------------------------------------------------------------
# justifies_naked_quad tests
# ---------------------------------------------------------------------------

def test_justifies_naked_quad_positive():
    """(0,4) has digit 1 which can be eliminated due to naked quad {1,2,3,4} at (0,0)..(0,3)."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    for c in range(5):
        eng._board[0, c] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {3, 4}
    eng._cands[0][3] = {1, 4}
    eng._cands[0][4] = {1, 5, 6}
    assert justifies_naked_quad(eng, ('eliminate', 0, 4, 1)) is True


def test_justifies_naked_quad_rejects_wrong_mode():
    """justifies_naked_quad returns False for 'fill' actions."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    for c in range(5):
        eng._board[0, c] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {3, 4}
    eng._cands[0][3] = {1, 4}
    eng._cands[0][4] = {1, 5, 6}
    assert justifies_naked_quad(eng, ('fill', 0, 4, 1)) is False


def test_justifies_naked_quad_rejects_non_quad_digit():
    """digit 5 is NOT in the naked quad {1,2,3,4} — justifies returns False."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    for c in range(5):
        eng._board[0, c] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {3, 4}
    eng._cands[0][3] = {1, 4}
    eng._cands[0][4] = {1, 5, 6}
    assert justifies_naked_quad(eng, ('eliminate', 0, 4, 5)) is False
