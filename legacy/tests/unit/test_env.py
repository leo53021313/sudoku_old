# tests/unit/test_env.py
import numpy as np
import pytest

from app.sudoku.env import SudokuEnv
from tests.conftest import SAMPLE_BOARD, SAMPLE_FIXED, SAMPLE_SOLUTION


def make_env(board=None, fixed=None):
    env = SudokuEnv()
    b = board if board is not None else SAMPLE_BOARD
    f = fixed if fixed is not None else SAMPLE_FIXED
    env.reset_from_board(b, f)
    return env


def test_reset_initializes_candidates():
    env = make_env()
    # Every empty cell must have at least one candidate
    for r in range(9):
        for c in range(9):
            if SAMPLE_BOARD[r][c] == 0:
                assert len(env.candidates_cache[r][c]) >= 1
            else:
                assert len(env.candidates_cache[r][c]) == 0


def test_valid_move_reduces_candidates():
    env = make_env()
    # Find a valid move
    valid = env.get_valid_actions()
    assert len(valid) > 0
    r, c, n = valid[0]
    _, _, done, info = env.step((r, c, n))
    assert info["valid"] is True
    assert env.board[r, c] == n
    # Cell is now filled — candidates should be empty
    assert len(env.candidates_cache[r][c]) == 0


def test_invalid_move_returns_penalty():
    env = make_env()
    # Find an occupied fixed cell and try to fill it
    for r in range(9):
        for c in range(9):
            if SAMPLE_FIXED[r][c]:
                _, reward, _, info = env.step((r, c, 5))
                assert reward == SudokuEnv.PENALTY_INVALID
                assert info["valid"] is False
                return
    pytest.skip("No fixed cells")


def test_invalid_count_accumulates_and_terminates():
    env = make_env()
    # Force max_invalid invalid moves
    env.max_invalid = 2
    for r in range(9):
        for c in range(9):
            if SAMPLE_FIXED[r][c]:
                env.step((r, c, 5))
                env.step((r, c, 5))
                break
    assert env.done is True


def test_dead_end_returns_penalty_and_done():
    # Create a board with a dead-end: set a cell to have no candidates
    env = SudokuEnv()
    # Minimal board where we can force a dead-end by filling all candidates for one cell
    board = [[0]*9 for _ in range(9)]
    fixed = [[False]*9 for _ in range(9)]
    # Fill row 0 with 1-8, leaving col 8 open for 9 only
    for c in range(8):
        board[0][c] = c + 1
        fixed[0][c] = True
    # Fill col 8 with 1-8 for rows 0-7 (except row 0)
    for r in range(1, 8):
        board[r][8] = r
        fixed[r][8] = True
    env.reset_from_board(board, fixed)
    # Now check that cell (0,8) has exactly one candidate: 9
    assert env.candidates_cache[0][8] == {9}
    # Fill (0,8) with 9 — should succeed and complete row 0
    _, reward, done, info = env.step((0, 8, 9))
    assert info["valid"] is True


def test_naked_single_gives_bonus():
    env = SudokuEnv()
    # Build a board where exactly one cell is empty, with only one candidate
    board = [row[:] for row in SAMPLE_SOLUTION]
    fixed = [[True]*9 for _ in range(9)]
    # Leave cell (8,8) empty
    board[8][8] = 0
    fixed[8][8] = False
    env.reset_from_board(board, fixed)
    cands = env.candidates_cache[8][8]
    assert len(cands) == 1  # naked single
    n = next(iter(cands))
    _, reward, done, info = env.step((8, 8, n))
    assert info["naked"] is True
    assert reward >= SudokuEnv.REWARD_STEP + SudokuEnv.REWARD_NAKED_SINGLE


def test_board_complete_gives_done_reward():
    env = SudokuEnv()
    board = [row[:] for row in SAMPLE_SOLUTION]
    fixed = [[True]*9 for _ in range(9)]
    board[8][8] = 0
    fixed[8][8] = False
    env.reset_from_board(board, fixed)
    n = next(iter(env.candidates_cache[8][8]))
    _, reward, done, _ = env.step((8, 8, n))
    assert done is True
    assert reward >= SudokuEnv.REWARD_BOARD_DONE


def test_unit_complete_gives_bonus():
    env = SudokuEnv()
    board = [row[:] for row in SAMPLE_SOLUTION]
    fixed = [[True]*9 for _ in range(9)]
    # Leave last cell in row 0 empty
    board[0][8] = 0
    fixed[0][8] = False
    env.reset_from_board(board, fixed)
    n = next(iter(env.candidates_cache[0][8]))
    _, reward, done, _ = env.step((0, 8, n))
    # Row 0 just completed → should include REWARD_UNIT_COMPLETE
    assert reward >= SudokuEnv.REWARD_UNIT_COMPLETE
