import numpy as np
import pytest
from apprentice.solver.candidate_engine import CandidateEngine
from apprentice.solver.techniques.naked_triple import find_naked_triple_elimination, justifies_naked_triple


def _eng(board=None):
    if board is None:
        board = np.zeros((9, 9), dtype=np.int8)
    return CandidateEngine(board)


def test_no_naked_triple_on_empty_board():
    """Empty board has full candidate sets — no naked triple exists."""
    assert find_naked_triple_elimination(_eng()) is None


def test_naked_triple_eliminates_in_row():
    """Three cells in row 0 form a naked triple over {1,2,3}; digit from that
    set must be eliminated from another empty cell in the row."""
    eng = _eng()
    # Set up row 0 candidate state directly
    # Triple cells at (0,0), (0,1), (0,2) with union {1,2,3}
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {1, 3}
    # Target cell at (0,3) has one of the triple digits
    eng._cands[0][3] = {1, 4, 5}
    # Other cells don't contain 1,2,3 so they won't be targets
    for c in range(4, 9):
        eng._cands[0][c] = {4, 5, 6, 7, 8, 9}

    result = find_naked_triple_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert r == 0
    assert c == 3
    assert v in {1, 2, 3}


def test_naked_triple_returns_none_when_no_other_targets():
    """If all non-triple cells in the row unit are filled, there's nothing to
    eliminate from that row.  We also ensure no column/box unit produces a hit
    by making every other empty cell's candidates disjoint from {1,2,3}."""
    eng = _eng()
    # Wipe all candidates first so we have full control
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
            eng._board[r, c] = 1  # mark all as filled

    # Re-open only the triple cells in row 0
    for c in (0, 1, 2):
        eng._board[0, c] = 0  # mark as empty

    # Assign candidates for the triple
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {1, 3}
    # All other cells remain filled (board != 0), so is_empty returns False.
    # No other empty cell in any unit can contain 1, 2, or 3.

    result = find_naked_triple_elimination(eng)
    assert result is None


def test_naked_triple_eliminates_in_col():
    """Naked triple fires in a column."""
    eng = _eng()
    # Triple cells at (0,0), (1,0), (2,0) in col 0
    eng._cands[0][0] = {4, 5}
    eng._cands[1][0] = {5, 6}
    eng._cands[2][0] = {4, 6}
    # Target cell at (3,0) has one of the triple digits
    eng._cands[3][0] = {4, 7, 8}
    # Other cells in col 0 don't contain 4,5,6
    for r in range(4, 9):
        eng._cands[r][0] = {1, 2, 3, 7, 8, 9}

    result = find_naked_triple_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert c == 0
    assert v in {4, 5, 6}


def test_naked_triple_skips_naked_single_degenerate():
    """If a potential triple cell has only 1 candidate (naked single), it should
    not be treated as part of a naked triple."""
    eng = _eng()
    # Cell (0,0) has only 1 candidate — should be skipped by the len>=2 guard
    eng._cands[0][0] = {1}
    eng._cands[0][1] = {1, 2}
    eng._cands[0][2] = {2, 3}
    eng._cands[0][3] = {1, 3}
    # Target: (0,4) has digit 1,2,3
    eng._cands[0][4] = {1, 2, 3, 4}
    for c in range(5, 9):
        eng._cands[0][c] = {5, 6, 7, 8, 9}

    # The combination (0,0)+(0,1)+(0,2) union={1,2,3} but (0,0) has len<2 so skip
    # The combination (0,1)+(0,2)+(0,3) union={1,2,3}: all have len>=2, should fire
    result = find_naked_triple_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v in {1, 2, 3}


# ---------------------------------------------------------------------------
# justifies_naked_triple tests
# ---------------------------------------------------------------------------

def test_justifies_naked_triple_positive():
    """(0,4) has digit 1 which can be eliminated due to naked triple {1,2,3} at (0,0),(0,1),(0,2)."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    eng._board[0, 0] = 0; eng._board[0, 1] = 0; eng._board[0, 2] = 0; eng._board[0, 4] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {1, 3}
    eng._cands[0][4] = {1, 5, 6}
    assert justifies_naked_triple(eng, ('eliminate', 0, 4, 1)) is True


def test_justifies_naked_triple_rejects_wrong_mode():
    """justifies_naked_triple returns False for 'fill' actions."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    eng._board[0, 0] = 0; eng._board[0, 1] = 0; eng._board[0, 2] = 0; eng._board[0, 4] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {1, 3}
    eng._cands[0][4] = {1, 5, 6}
    assert justifies_naked_triple(eng, ('fill', 0, 4, 1)) is False


def test_justifies_naked_triple_rejects_non_triple_digit():
    """digit 5 is NOT in the naked triple {1,2,3} — justifies returns False."""
    eng = _eng()
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    eng._board[0, 0] = 0; eng._board[0, 1] = 0; eng._board[0, 2] = 0; eng._board[0, 4] = 0
    eng._cands[0][0] = {1, 2}
    eng._cands[0][1] = {2, 3}
    eng._cands[0][2] = {1, 3}
    eng._cands[0][4] = {1, 5, 6}
    # digit 5 is not in the naked triple
    assert justifies_naked_triple(eng, ('eliminate', 0, 4, 5)) is False
