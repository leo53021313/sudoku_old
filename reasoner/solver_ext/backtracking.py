# app/rl/envs/sudoku_solver.py
# -*- coding: utf-8 -*-
"""
Backtracking Sudoku solver with MRV (minimum remaining values) heuristic
and forward-checking (candidate propagation at each branch).

Usage:
    from reasoner.solver_ext.backtracking import solve
    solution = solve(board)   # board: np.ndarray (9,9) int8, 0=empty
    # Returns np.ndarray (9,9) or None if unsolvable / multiple solutions
"""

from __future__ import annotations
import numpy as np


def solve(board: np.ndarray) -> np.ndarray | None:
    """
    Return the unique solution for `board`, or None if none / multiple exist.
    Works on a copy — the input board is not modified.
    """
    board = np.array(board, dtype=np.int8).copy()
    candidates = _build_candidates(board)
    result = _backtrack(board, candidates)
    return result


# ── Internal helpers ──────────────────────────────────────────────────────────

def _build_candidates(board: np.ndarray) -> list[list[set[int]]]:
    cands: list[list[set[int]]] = [[set() for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            if board[r, c] == 0:
                cands[r][c] = _compute_cell_candidates(board, r, c)
    return cands


def _compute_cell_candidates(board: np.ndarray, r: int, c: int) -> set[int]:
    used: set[int] = set()
    used.update(int(v) for v in board[r, :] if v != 0)
    used.update(int(v) for v in board[:, c] if v != 0)
    br, bc = (r // 3) * 3, (c // 3) * 3
    used.update(
        int(board[rr, cc])
        for rr in range(br, br + 3)
        for cc in range(bc, bc + 3)
        if board[rr, cc] != 0
    )
    return {n for n in range(1, 10) if n not in used}


def _pick_mrv_cell(board: np.ndarray, cands: list[list[set[int]]]) -> tuple[int, int] | None:
    best_r, best_c, best_n = -1, -1, 10
    for r in range(9):
        for c in range(9):
            if board[r, c] == 0:
                n = len(cands[r][c])
                if n == 0:
                    return None  # dead end: no legal value
                if n < best_n:
                    best_n, best_r, best_c = n, r, c
    if best_r == -1:
        return None  # all filled
    return best_r, best_c


def _propagate(board: np.ndarray, cands: list[list[set[int]]], r: int, c: int, v: int) -> bool:
    """Remove v from all related cells' candidate sets. Returns False on dead-end."""
    board[r, c] = v
    cands[r][c] = set()

    related: set[tuple[int, int]] = set()
    for cc in range(9):
        related.add((r, cc))
    for rr in range(9):
        related.add((rr, c))
    br, bc = (r // 3) * 3, (c // 3) * 3
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            related.add((rr, cc))

    for rr, cc in related:
        if (rr, cc) == (r, c):
            continue
        if board[rr, cc] != 0:
            continue
        cands[rr][cc].discard(v)
        if len(cands[rr][cc]) == 0:
            return False  # dead end
    return True


def _backtrack(board: np.ndarray, cands: list[list[set[int]]]) -> np.ndarray | None:
    """Recursive backtracking with MRV + forward checking."""
    cell = _pick_mrv_cell(board, cands)
    if cell is None:
        # All cells filled → check for remaining empty cells
        if np.all(board != 0):
            return board.copy()
        return None  # dead end reached

    r, c = cell
    for v in sorted(cands[r][c]):
        # Save state
        board_copy = board.copy()
        cands_copy = [[s.copy() for s in row] for row in cands]

        ok = _propagate(board, cands, r, c, v)
        if ok:
            result = _backtrack(board, cands)
            if result is not None:
                return result

        # Restore state
        board[:] = board_copy
        for rr in range(9):
            for cc in range(9):
                cands[rr][cc] = cands_copy[rr][cc]

    return None  # no value works → backtrack
