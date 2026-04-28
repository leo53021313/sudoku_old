import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.naked_single import find_naked_single


def test_no_naked_single_on_empty_board():
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    assert find_naked_single(eng) is None


def test_naked_single_when_8_of_9_filled_in_row():
    # row 0: cells (0,0)..(0,7) filled with 1..8 → (0,8) candidate set is {9}
    board = np.zeros((9, 9), dtype=np.int8)
    for c in range(8):
        board[0, c] = c + 1  # 1..8
    eng = CandidateEngine(board)
    result = find_naked_single(eng)
    assert result == ('fill', 0, 8, 9)


def test_naked_single_picks_first_in_scan_order_when_multiple():
    # Construct two naked-single cells; verify deterministic pick of (smaller row, then smaller col)
    board = np.zeros((9, 9), dtype=np.int8)
    # Make (0,1) a naked single for 1: fill row 0 except (0,1) with 2-9
    board[0, 0] = 2
    for c in range(2, 9):
        board[0, c] = c  # 2,3,4,5,6,7,8 at cols 2-8
    # Fill column 1 rows 1-8 with 2-9
    for r in range(1, 9):
        board[r, 1] = (r % 8) + 2  # 2-9
    # Fill box 0 remaining cells
    board[1, 0] = 3
    board[1, 2] = 4
    board[2, 0] = 5
    board[2, 2] = 6

    # Make (5,5) a naked single for 1: fill row 5 except (5,5) with 2-9
    for c in range(9):
        if c != 5:
            board[5, c] = (c % 8) + 2
    # Fill column 5 rows 0-4,6-8 with 2-9
    for r in range(9):
        if r != 5:
            board[r, 5] = ((r + 1) % 8) + 2
    # Fill box 4 (rows 3-5, cols 3-5) remaining
    board[3, 3] = 3
    board[3, 4] = 4
    board[4, 3] = 5
    board[4, 4] = 6
    board[4, 5] = 7

    eng = CandidateEngine(board)
    result = find_naked_single(eng)
    # Scan is row-major; (0,1) comes before (5,5), so (0,1) wins
    assert result == ('fill', 0, 1, 1)


def test_naked_single_skips_filled_cells():
    board = np.zeros((9, 9), dtype=np.int8)
    board[0, 0] = 5  # already filled
    eng = CandidateEngine(board)
    # (0,0) is filled (no candidates) — the function must not "find naked single" there
    # Check by ensuring all empty cells have multi-candidate (i.e. function returns None)
    result = find_naked_single(eng)
    assert result is None
