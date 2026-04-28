import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine


def _empty_board():
    return np.zeros((9, 9), dtype=np.int8)


def test_empty_board_all_cells_have_full_candidates():
    board = _empty_board()
    eng = CandidateEngine(board)
    for r in range(9):
        for c in range(9):
            assert eng.get_candidates(r, c) == set(range(1, 10))


def test_given_cells_have_no_candidates():
    board = _empty_board()
    board[0, 0] = 5
    eng = CandidateEngine(board)
    assert eng.get_candidates(0, 0) == set()


def test_row_constraint_eliminates():
    board = _empty_board()
    board[0, 0] = 5
    eng = CandidateEngine(board)
    # Other empty cells in row 0 should not have 5 as candidate
    assert 5 not in eng.get_candidates(0, 1)
    assert 5 not in eng.get_candidates(0, 8)


def test_col_constraint_eliminates():
    board = _empty_board()
    board[0, 0] = 5
    eng = CandidateEngine(board)
    assert 5 not in eng.get_candidates(8, 0)


def test_box_constraint_eliminates():
    board = _empty_board()
    board[0, 0] = 5
    eng = CandidateEngine(board)
    assert 5 not in eng.get_candidates(2, 2)
    # but cell outside the box (row 0 col 0's box is rows 0-2, cols 0-2) is row-only constraint
    assert 5 not in eng.get_candidates(0, 4)  # row constraint
