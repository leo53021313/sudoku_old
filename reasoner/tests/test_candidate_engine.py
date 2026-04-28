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


def test_apply_fill_updates_board():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    assert eng.board[0, 0] == 5


def test_apply_fill_clears_filled_cell_candidates():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    assert eng.get_candidates(0, 0) == set()


def test_apply_fill_propagates_to_row():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    assert 5 not in eng.get_candidates(0, 5)


def test_apply_fill_propagates_to_col():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    assert 5 not in eng.get_candidates(5, 0)


def test_apply_fill_propagates_to_box():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    assert 5 not in eng.get_candidates(2, 2)


def test_apply_fill_does_not_touch_unrelated_cells():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_fill(0, 0, 5)
    # cell (4,4) is not in row 0, col 0, or box (0,0)
    assert 5 in eng.get_candidates(4, 4)


def test_apply_eliminate_removes_one_candidate():
    board = _empty_board()
    eng = CandidateEngine(board)
    assert 5 in eng.get_candidates(0, 0)
    eng.apply_eliminate(0, 0, 5)
    assert 5 not in eng.get_candidates(0, 0)


def test_apply_eliminate_no_op_when_already_absent():
    board = _empty_board()
    board[0, 1] = 5  # row 0 has 5 → (0,0) lost 5
    eng = CandidateEngine(board)
    assert 5 not in eng.get_candidates(0, 0)
    # eliminating again is harmless
    eng.apply_eliminate(0, 0, 5)
    assert 5 not in eng.get_candidates(0, 0)


def test_apply_eliminate_does_not_touch_board_value():
    board = _empty_board()
    eng = CandidateEngine(board)
    eng.apply_eliminate(0, 0, 5)
    assert eng.board[0, 0] == 0  # eliminate is candidate-only
