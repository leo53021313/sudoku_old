# sb3/app/sudoku/teacher_engine.py
# -*- coding: utf-8 -*-
"""
TeacherEngine — Oracle teacher backed by env.solution.

For each board state, returns ((row, col, num), quality):
  - num is ALWAYS env.solution[row, col]
  - quality reflects which detection tier identified the cell:
      naked single        → 1.00
      hidden single       → 0.75
      pointing pair       → 0.50
      MRV fallback        → 0.30
  - returns (None, 0.0) only when the board has no empty cells.

This replaces the previous MRV teacher whose Level 3-4 used min(candidates) as
the value (incorrect on average). With the backtracking solver pre-computing
the unique solution at env.reset(), we always know the correct value, so BC
loss has a meaningful target across all difficulties — including L4 evil.
"""

from __future__ import annotations


class TeacherEngine:
    """Oracle teacher using env.solution as ground truth for the value."""

    _Q_NAKED    = 1.00
    _Q_HIDDEN   = 0.75
    _Q_POINTING = 0.50
    _Q_MRV      = 0.30

    def __init__(self, max_candidates: int = 4):
        # Kept for compatibility with the existing constructor signature
        # (legacy code may still pass max_candidates). With an oracle teacher
        # we don't abstain on high-candidate cells — solution is always known.
        self.max_candidates = max_candidates

    def __call__(self, env) -> "tuple[tuple[int,int,int] | None, float]":
        # ── Tier 1: naked single ─────────────────────────────────────────────
        cell = self._find_naked_single(env)
        if cell is not None:
            r, c = cell
            return (r, c, int(env.solution[r, c])), self._Q_NAKED

        # ── Tier 2: hidden single ────────────────────────────────────────────
        cell = self._find_hidden_single(env)
        if cell is not None:
            r, c = cell
            return (r, c, int(env.solution[r, c])), self._Q_HIDDEN

        # ── Tier 3: pointing pair → naked single ────────────────────────────
        cell = self._find_pointing_pair_target(env)
        if cell is not None:
            r, c = cell
            return (r, c, int(env.solution[r, c])), self._Q_POINTING

        # ── Tier 4: MRV fallback ─────────────────────────────────────────────
        cell = self._mrv_pick(env)
        if cell is None:
            return None, 0.0
        r, c = cell
        return (r, c, int(env.solution[r, c])), self._Q_MRV

    # ── Detectors ────────────────────────────────────────────────────────────

    def _find_naked_single(self, env) -> tuple[int, int] | None:
        for r in range(9):
            for c in range(9):
                if env.board[r, c] != 0:
                    continue
                if len(env.candidates_cache[r][c]) == 1:
                    return (r, c)
        return None

    def _find_hidden_single(self, env) -> tuple[int, int] | None:
        cells = sorted(
            (
                (len(env.candidates_cache[r][c]), r, c)
                for r in range(9) for c in range(9)
                if env.board[r, c] == 0 and len(env.candidates_cache[r][c]) > 0
            )
        )
        for _, r, c in cells:
            for n in sorted(env.candidates_cache[r][c]):
                if env._is_hidden_single(r, c, n):
                    return (r, c)
        return None

    def _find_pointing_pair_target(self, env) -> tuple[int, int] | None:
        """
        Pointing pair: in some 3x3 box, all candidates of digit `d` lie in one
        row (or one column). That digit can be eliminated from the rest of the
        row/column outside the box. If after elimination some other cell becomes
        a naked single, return that cell.

        MVP: only detects pointing pair (not box-line reduction). Quality stays
        at 0.50 for both per spec.
        """
        for digit in range(1, 10):
            for box_r in (0, 3, 6):
                for box_c in (0, 3, 6):
                    cells_in_box = [
                        (r, c)
                        for r in range(box_r, box_r + 3)
                        for c in range(box_c, box_c + 3)
                        if env.board[r, c] == 0
                        and digit in env.candidates_cache[r][c]
                    ]
                    if not cells_in_box or len(cells_in_box) > 3:
                        continue

                    rows = {r for r, _ in cells_in_box}
                    cols = {c for _, c in cells_in_box}

                    if len(rows) == 1:
                        r = next(iter(rows))
                        target = self._naked_single_after_eliminating(
                            env, digit, row=r, exclude_box_c=box_c
                        )
                        if target is not None:
                            return target

                    if len(cols) == 1:
                        c = next(iter(cols))
                        target = self._naked_single_after_eliminating(
                            env, digit, col=c, exclude_box_r=box_r
                        )
                        if target is not None:
                            return target
        return None

    def _naked_single_after_eliminating(
        self,
        env,
        digit: int,
        *,
        row: int | None = None,
        col: int | None = None,
        exclude_box_r: int | None = None,
        exclude_box_c: int | None = None,
    ) -> tuple[int, int] | None:
        """If we eliminate `digit` from cells in the given row/col (excluding
        the cells inside the indicated box), does any cell become a naked single?
        Return its (r, c) if so."""
        if row is not None:
            for c in range(9):
                if exclude_box_c is not None and exclude_box_c <= c < exclude_box_c + 3:
                    continue
                if env.board[row, c] != 0:
                    continue
                cands = env.candidates_cache[row][c]
                if digit in cands and len(cands) == 2:
                    return (row, c)
        if col is not None:
            for r in range(9):
                if exclude_box_r is not None and exclude_box_r <= r < exclude_box_r + 3:
                    continue
                if env.board[r, col] != 0:
                    continue
                cands = env.candidates_cache[r][col]
                if digit in cands and len(cands) == 2:
                    return (r, col)
        return None

    def _mrv_pick(self, env) -> tuple[int, int] | None:
        best: tuple[int, int, int] | None = None  # (cnt, r, c)
        for r in range(9):
            for c in range(9):
                if env.board[r, c] != 0:
                    continue
                cnt = len(env.candidates_cache[r][c])
                if cnt == 0:
                    continue
                if best is None or cnt < best[0] or (cnt == best[0] and (r, c) < (best[1], best[2])):
                    best = (cnt, r, c)
        if best is None:
            return None
        return (best[1], best[2])
