import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.pointing_pair import find_pointing_pair_elimination


def test_no_pointing_pair_on_empty_board():
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    assert find_pointing_pair_elimination(eng) is None


def test_pointing_pair_in_box_eliminates_from_row():
    """Box (0,0): digit 4 only appears in row 0 (cells (0,0),(0,1),(0,2)) → eliminate from rest of row 0."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Fill (1,*) and (2,*) cells of box (0,0) with non-4 digits so 4 is NOT a candidate there
    board[1, 0] = 1; board[1, 1] = 2; board[1, 2] = 3
    board[2, 0] = 5; board[2, 1] = 6; board[2, 2] = 7
    eng = CandidateEngine(board)
    # In box (0,0), 4 only in row 0 cells → eliminate 4 from (0,3..8)
    result = find_pointing_pair_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 4
    assert r == 0
    assert c in (3, 4, 5, 6, 7, 8)


def test_pointing_pair_in_box_eliminates_from_col():
    """Box (0,0): digit 4 only in col 0 (cells (0,0),(1,0),(2,0)) → eliminate from rest of col 0."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Fill cols 1 and 2 of box (0,0) with non-4
    board[0, 1] = 1; board[1, 1] = 2; board[2, 1] = 3
    board[0, 2] = 5; board[1, 2] = 6; board[2, 2] = 7
    eng = CandidateEngine(board)
    result = find_pointing_pair_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 4
    assert c == 0
    assert r in (3, 4, 5, 6, 7, 8)
