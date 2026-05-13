"""Helpers for computing obs flag channels (naked-single, hidden-single).

These channels are added to the observation tensor in apprentice's
SudokuGymEnv (A3 change vs reasoner's 24-channel obs).
"""

from __future__ import annotations

import numpy as np


def compute_naked_single_grid(
    board: np.ndarray,
    candidates: list[list[set[int]]],
) -> np.ndarray:
    """Return a (9,9) float32 grid where cell (r,c) is 1.0 iff:
      - board[r,c] == 0 (cell is empty), AND
      - len(candidates[r][c]) == 1 (only one possible value).
    """
    grid = np.zeros((9, 9), dtype=np.float32)
    for r in range(9):
        for c in range(9):
            if board[r, c] != 0:
                continue
            if len(candidates[r][c]) == 1:
                grid[r, c] = 1.0
    return grid


def compute_hidden_single_grid(
    board: np.ndarray,
    candidates: list[list[set[int]]],
) -> np.ndarray:
    """Return a (9,9) float32 grid where cell (r,c) is 1.0 iff:
      - board[r,c] == 0, AND
      - there exists some digit v in candidates[r][c] such that within at
        least one unit (the row r, the column c, or the box containing (r,c)),
        no OTHER empty cell has v as a candidate.

    Cost: O(9 * 27) = O(243) lookups per call. Sub-millisecond.
    """
    grid = np.zeros((9, 9), dtype=np.float32)

    # Build a fast view: for each (unit_type, unit_idx, digit) → list of cells
    # We'll mark cells lazily as we discover hidden singles.
    marked = np.zeros((9, 9), dtype=bool)

    # Rows
    for r in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for c in range(9)
                if board[r, c] == 0 and d in candidates[r][c]
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                marked[rr, cc] = True

    # Columns
    for c in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for r in range(9)
                if board[r, c] == 0 and d in candidates[r][c]
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                marked[rr, cc] = True

    # Boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            for d in range(1, 10):
                cells_with_d = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if board[r, c] == 0 and d in candidates[r][c]
                ]
                if len(cells_with_d) == 1:
                    rr, cc = cells_with_d[0]
                    marked[rr, cc] = True

    grid[marked] = 1.0
    return grid
