"""Candidate-set state machine for sudoku boards.

Maintains per-cell candidate sets {1..9} for empty cells, updating
incrementally on fill/eliminate operations. Pure Python; no IO.
"""

from __future__ import annotations
from typing import Iterable
import numpy as np


class CandidateEngine:
    """Per-cell candidate sets, maintained incrementally."""

    def __init__(self, board: np.ndarray) -> None:
        self._board = board.astype(np.int8).copy()
        self._cands: list[list[set[int]]] = [
            [set() for _ in range(9)] for _ in range(9)
        ]
        self._rebuild_all()

    # --- Queries -------------------------------------------------------------

    def get_candidates(self, r: int, c: int) -> set[int]:
        """Read-only view (returns a fresh copy)."""
        return set(self._cands[r][c])

    @property
    def board(self) -> np.ndarray:
        return self._board

    def is_empty(self, r: int, c: int) -> bool:
        return self._board[r, c] == 0

    # --- Internal ------------------------------------------------------------

    def _rebuild_all(self) -> None:
        for r in range(9):
            for c in range(9):
                if self._board[r, c] != 0:
                    self._cands[r][c] = set()
                else:
                    self._cands[r][c] = self._compute_candidates_for(r, c)

    def _compute_candidates_for(self, r: int, c: int) -> set[int]:
        used: set[int] = set()
        used.update(int(v) for v in self._board[r, :] if v != 0)
        used.update(int(v) for v in self._board[:, c] if v != 0)
        br, bc = (r // 3) * 3, (c // 3) * 3
        used.update(
            int(self._board[rr, cc])
            for rr in range(br, br + 3)
            for cc in range(bc, bc + 3)
            if self._board[rr, cc] != 0
        )
        return {n for n in range(1, 10) if n not in used}

    def apply_fill(self, r: int, c: int, v: int) -> None:
        """Place v at (r,c). Updates board + candidate sets for related cells."""
        self._board[r, c] = v
        self._cands[r][c] = set()
        for rr, cc in self._related_cells(r, c):
            if self._board[rr, cc] == 0:
                self._cands[rr][cc].discard(v)

    @staticmethod
    def _related_cells(r: int, c: int) -> Iterable[tuple[int, int]]:
        seen: set[tuple[int, int]] = set()
        for cc in range(9):
            if (r, cc) != (r, c):
                seen.add((r, cc))
        for rr in range(9):
            if (rr, c) != (r, c):
                seen.add((rr, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                if (rr, cc) != (r, c):
                    seen.add((rr, cc))
        return seen
