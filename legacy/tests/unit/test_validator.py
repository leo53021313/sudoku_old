# tests/unit/test_validator.py
import numpy as np
import pytest

from app.sudoku.validator import validate_completed_board
from tests.conftest import SAMPLE_SOLUTION, SAMPLE_BOARD, SAMPLE_FIXED


def _valid_solution():
    return [row[:] for row in SAMPLE_SOLUTION]


def test_valid_board_passes():
    result = validate_completed_board(_valid_solution())
    assert result["ok"] is True


def test_incomplete_board_fails():
    board = _valid_solution()
    board[0][0] = 0
    result = validate_completed_board(board)
    assert result["ok"] is False
    assert "not_complete" in result["reason"]


def test_wrong_shape_fails():
    result = validate_completed_board([[1, 2, 3]])
    assert result["ok"] is False
    assert "shape" in result["reason"]


def test_duplicate_in_row_fails():
    board = _valid_solution()
    # Put a 5 in position [0][1], creating a duplicate in row 0
    board[0][1] = board[0][0]
    result = validate_completed_board(board)
    assert result["ok"] is False
    assert "row" in result["reason"] or "col" in result["reason"] or "box" in result["reason"]


def test_duplicate_in_col_fails():
    board = _valid_solution()
    # Swap two cells in same column to create a duplicate
    board[1][0], board[2][0] = board[2][0], board[1][0]
    result = validate_completed_board(board)
    assert result["ok"] is False


def test_fixed_cell_modified_fails():
    board = _valid_solution()
    fixed = [[SAMPLE_FIXED[r][c] for c in range(9)] for r in range(9)]
    base = [[SAMPLE_BOARD[r][c] for c in range(9)] for r in range(9)]
    # Modify a fixed cell
    for r in range(9):
        for c in range(9):
            if fixed[r][c]:
                original = board[r][c]
                board[r][c] = (original % 9) + 1  # change to a different value
                result = validate_completed_board(board, fixed, base)
                assert result["ok"] is False
                assert "fixed_cell" in result["reason"]
                return
    pytest.skip("No fixed cells found")


def test_out_of_range_value_fails():
    board = _valid_solution()
    board[0][0] = 10
    result = validate_completed_board(board)
    assert result["ok"] is False
