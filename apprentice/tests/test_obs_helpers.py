"""Tests for env/obs_helpers.py."""

import numpy as np
import pytest

from apprentice.env.obs_helpers import (
    compute_naked_single_grid,
    compute_hidden_single_grid,
)


def _empty_candidates():
    """9x9 list of sets — initial: every empty cell has {1..9}."""
    return [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]


def _empty_board():
    return np.zeros((9, 9), dtype=np.int8)


def test_compute_naked_single_grid_no_naked():
    board = _empty_board()
    candidates = _empty_candidates()
    grid = compute_naked_single_grid(board, candidates)
    assert grid.shape == (9, 9)
    assert grid.dtype == np.float32
    assert grid.sum() == 0.0


def test_compute_naked_single_grid_one_naked():
    board = _empty_board()
    candidates = _empty_candidates()
    # Cell (3,4) has only {7} as candidate → naked single
    candidates[3][4] = {7}
    grid = compute_naked_single_grid(board, candidates)
    assert grid[3, 4] == 1.0
    # All other cells: 0.0
    assert grid.sum() == 1.0


def test_compute_naked_single_grid_filled_cell_not_marked():
    board = _empty_board()
    candidates = _empty_candidates()
    # Board cell (1,1) is filled with 5
    board[1, 1] = 5
    candidates[1][1] = set()  # filled cells have empty candidate set
    grid = compute_naked_single_grid(board, candidates)
    # Should not mark a filled cell even though its candidate count is "1"
    assert grid[1, 1] == 0.0


def test_compute_hidden_single_grid_row():
    board = _empty_board()
    candidates = _empty_candidates()
    # Make digit 5 only possible in cell (0, 3) within row 0:
    # Remove 5 from candidates of all other cells in row 0
    for c in range(9):
        if c != 3:
            candidates[0][c].discard(5)
    grid = compute_hidden_single_grid(board, candidates)
    assert grid.shape == (9, 9)
    assert grid.dtype == np.float32
    assert grid[0, 3] == 1.0


def test_compute_hidden_single_grid_col():
    board = _empty_board()
    candidates = _empty_candidates()
    # Make digit 7 only possible in cell (5, 8) within col 8:
    for r in range(9):
        if r != 5:
            candidates[r][8].discard(7)
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[5, 8] == 1.0


def test_compute_hidden_single_grid_box():
    board = _empty_board()
    candidates = _empty_candidates()
    # Box (0,0) to (2,2) — make 3 only possible in (1,1)
    for r in range(3):
        for c in range(3):
            if not (r == 1 and c == 1):
                candidates[r][c].discard(3)
    # ALSO remove 3 from row 1 elsewhere and col 1 elsewhere so it's hidden
    # *only* by the box constraint... but the function should still flag it.
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[1, 1] == 1.0


def test_compute_hidden_single_grid_empty_no_hidden():
    board = _empty_board()
    candidates = _empty_candidates()  # every cell has {1..9}, no hidden singles
    grid = compute_hidden_single_grid(board, candidates)
    assert grid.sum() == 0.0


def test_compute_hidden_single_grid_filled_cells_not_marked():
    board = _empty_board()
    candidates = _empty_candidates()
    board[2, 2] = 9
    candidates[2][2] = set()
    # Even if the algorithm theoretically thinks (2,2) is hidden-single
    # for some digit (shouldn't, since it's empty candidates), it must not mark filled cells
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[2, 2] == 0.0
