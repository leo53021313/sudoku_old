import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.hidden_single import find_hidden_single


def test_no_hidden_single_on_empty_board():
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    assert find_hidden_single(eng) is None


def test_hidden_single_in_row():
    # Construct: row 1 has digit 7 appearing only at (1,4)
    # Place 7 in all columns except col 4, using different rows
    board = np.zeros((9, 9), dtype=np.int8)
    board[0, 0] = 7
    board[2, 1] = 7
    board[3, 2] = 7
    board[4, 3] = 7
    board[5, 5] = 7
    board[6, 6] = 7
    board[7, 7] = 7
    board[8, 8] = 7
    eng = CandidateEngine(board)
    # Verify setup: in row 1, only (1,4) has 7 in candidates
    assert 7 in eng.get_candidates(1, 4), "7 should be in (1,4) candidates"
    for c in range(9):
        if c == 4:
            continue
        assert 7 not in eng.get_candidates(1, c), f"unexpected 7 in (1,{c})"
    result = find_hidden_single(eng)
    assert result == ('fill', 1, 4, 7)


def test_hidden_single_in_box():
    # Box (0,0) (rows 0-2, cols 0-2): 4 lives only at (1,1)
    board = np.zeros((9, 9), dtype=np.int8)
    board[0, 5] = 4   # row 0 cells in box lose 4
    board[2, 8] = 4   # row 2 cells in box lose 4
    board[5, 0] = 4   # col 0 cells in box lose 4
    board[7, 2] = 4   # col 2 cells in box lose 4
    eng = CandidateEngine(board)
    assert 4 in eng.get_candidates(1, 1)
    # Verify all other empty cells in box (0,0) have lost 4
    for rr in range(3):
        for cc in range(3):
            if (rr, cc) == (1, 1):
                continue
            if eng.is_empty(rr, cc):
                assert 4 not in eng.get_candidates(rr, cc)
    result = find_hidden_single(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'fill' and v == 4 and (r, c) == (1, 1)


def test_hidden_single_skip_filled_cells():
    # Already-filled cells should never be returned
    board = np.zeros((9, 9), dtype=np.int8)
    board[5, 5] = 7  # filled
    # No constraint that creates a hidden single elsewhere with simple setup
    # Just ensure that the filled cell itself isn't returned
    eng = CandidateEngine(board)
    result = find_hidden_single(eng)
    if result is not None:
        op, r, c, v = result
        assert (r, c) != (5, 5), "should not return filled cell"
