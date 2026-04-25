# tests/conftest.py
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data.pool_db import PuzzlePoolDB
from app.sudoku.env import SudokuEnv

# A known valid, partially-filled Sudoku board (level 1 easy)
SAMPLE_PUZZLE_STR = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

SAMPLE_SOLUTION_STR = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)


def _str_to_board(s):
    return [[int(s[r * 9 + c]) for c in range(9)] for r in range(9)]


SAMPLE_BOARD = _str_to_board(SAMPLE_PUZZLE_STR)
SAMPLE_FIXED = [[SAMPLE_BOARD[r][c] != 0 for c in range(9)] for r in range(9)]
SAMPLE_SOLUTION = _str_to_board(SAMPLE_SOLUTION_STR)


@pytest.fixture
def tmp_db(tmp_path):
    """Fresh SQLite DB for each test."""
    return PuzzlePoolDB(str(tmp_path / "test.db"))


@pytest.fixture
def simple_env():
    """SudokuEnv reset to the sample puzzle."""
    env = SudokuEnv()
    env.reset_from_board(SAMPLE_BOARD, SAMPLE_FIXED)
    return env


@pytest.fixture
def naked_single_env():
    """Board where (0,2) has exactly 1 candidate (naked single = 4)."""
    env = SudokuEnv()
    # Use the sample board — cell (0,2) is empty and has only {4} remaining
    env.reset_from_board(SAMPLE_BOARD, SAMPLE_FIXED)
    return env
