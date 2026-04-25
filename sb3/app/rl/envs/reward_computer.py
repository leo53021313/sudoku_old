# app/rl/envs/reward_computer.py
# -*- coding: utf-8 -*-
"""
RewardComputer — technique detection + shaped reward.

Reward structure:
  Correct fill, base             +1.0
  + naked single (1 candidate)   +3.0   → +4.0 total
  + hidden single                +2.0   → +3.0 total
  + cascade: each new naked      +0.5   per new naked single created
  + unit complete (row/col/box)  +5.0   (up to +15 per step)
  + board complete               +20.0

  Wrong fill (legal but wrong)   -3.0   committed to board
  Terminal on max_wrong_fills    (no additional reward)
"""

from __future__ import annotations
import numpy as np


class RewardComputer:
    """
    Stateful reward calculator coupled to a SudokuGymEnv instance.
    All state (board, candidates_cache, solution, wrong_count) lives on env.
    """

    REWARD_BASE         =  1.0
    REWARD_NAKED_BONUS  =  3.0
    REWARD_HIDDEN_BONUS =  2.0
    REWARD_CASCADE      =  0.5   # per new naked single created
    REWARD_UNIT         =  5.0   # per row/col/box completed
    REWARD_BOARD_DONE   = 20.0
    PENALTY_WRONG       = -3.0

    def __init__(self, env: object) -> None:
        self._env = env

    # ── Public API ────────────────────────────────────────────────────────────

    def compute(self, r: int, c: int, v: int) -> tuple[float, bool]:
        """
        Compute reward for filling value v in cell (r, c).
        IMPORTANT: This method commits the fill to env.board and env.candidates_cache
        as part of reward computation (it needs pre/post candidate state).
        Returns (reward, terminated).
        """
        env = self._env
        is_correct = int(v) == int(env.solution[r, c])
        is_naked   = len(env.candidates_cache[r][c]) == 1
        is_hidden  = (not is_naked) and self._is_hidden_single(r, c, v)

        if not is_correct:
            env.wrong_count += 1
            # Commit wrong fill — agent lives with consequences
            self._commit_fill(r, c, v)
            terminated = env.wrong_count >= env.max_wrong_fills
            return self.PENALTY_WRONG, terminated

        # ── Correct fill ──────────────────────────────────────────────────────
        pre_nakeds = self._count_naked_singles()

        reward = self.REWARD_BASE
        if is_naked:
            reward += self.REWARD_NAKED_BONUS
        elif is_hidden:
            reward += self.REWARD_HIDDEN_BONUS

        # Track filled counts per unit BEFORE commit (to detect completions)
        row_pre = self._count_filled_row(r)
        col_pre = self._count_filled_col(c)
        box_pre = self._count_filled_box(r, c)

        self._commit_fill(r, c, v)

        post_nakeds = self._count_naked_singles()
        cascade = max(0, post_nakeds - pre_nakeds)
        reward += self.REWARD_CASCADE * cascade

        if self._count_filled_row(r) == 9 and row_pre < 9:
            reward += self.REWARD_UNIT
        if self._count_filled_col(c) == 9 and col_pre < 9:
            reward += self.REWARD_UNIT
        if self._count_filled_box(r, c) == 9 and box_pre < 9:
            reward += self.REWARD_UNIT

        if np.all(env.board != 0):
            reward += self.REWARD_BOARD_DONE
            return reward, True

        return reward, False

    # ── Technique detection ───────────────────────────────────────────────────

    def _is_hidden_single(self, r: int, c: int, v: int) -> bool:
        """True if v can only go in (r, c) within its row, col, OR box."""
        env = self._env
        # Row check
        row_ok = all(
            (rr == r and cc == c) or env.board[rr, cc] != 0 or v not in env.candidates_cache[rr][cc]
            for rr, cc in [(r, cc) for cc in range(9)]
        )
        if row_ok:
            return True
        # Col check
        col_ok = all(
            (rr == r and cc == c) or env.board[rr, cc] != 0 or v not in env.candidates_cache[rr][cc]
            for rr, cc in [(rr, c) for rr in range(9)]
        )
        if col_ok:
            return True
        # Box check
        br, bc = (r // 3) * 3, (c // 3) * 3
        box_ok = all(
            (rr == r and cc == c) or env.board[rr, cc] != 0 or v not in env.candidates_cache[rr][cc]
            for rr in range(br, br + 3)
            for cc in range(bc, bc + 3)
        )
        return box_ok

    def _count_naked_singles(self) -> int:
        env = self._env
        count = 0
        for r in range(9):
            for c in range(9):
                if env.board[r, c] == 0 and len(env.candidates_cache[r][c]) == 1:
                    count += 1
        return count

    def compute_hidden_single_grid(self) -> np.ndarray:
        """9×9 float32 grid: 1.0 if cell is a hidden single for any of its candidates."""
        env = self._env
        grid = np.zeros((9, 9), dtype=np.float32)
        for r in range(9):
            for c in range(9):
                if env.board[r, c] == 0:
                    for v in env.candidates_cache[r][c]:
                        if self._is_hidden_single(r, c, v):
                            grid[r, c] = 1.0
                            break
        return grid

    # ── Board helpers ─────────────────────────────────────────────────────────

    def _commit_fill(self, r: int, c: int, v: int) -> None:
        """Fill the cell and update candidate sets for all 20 related cells."""
        env = self._env
        env.board[r, c] = v
        env.candidates_cache[r][c] = set()
        env.candidate_count_grid[r, c] = 0
        env.single_candidate_grid[r, c] = 0.0

        related: set[tuple[int, int]] = set()
        for cc in range(9):
            related.add((r, cc))
        for rr in range(9):
            related.add((rr, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for rr in range(br, br + 3):
            for cc in range(bc, bc + 3):
                related.add((rr, cc))
        related.discard((r, c))

        for rr, cc in related:
            if env.board[rr, cc] != 0:
                continue
            env.candidates_cache[rr][cc].discard(v)
            cnt = len(env.candidates_cache[rr][cc])
            env.candidate_count_grid[rr, cc] = cnt
            env.single_candidate_grid[rr, cc] = 1.0 if cnt == 1 else 0.0

    def _count_filled_row(self, r: int) -> int:
        return int(np.count_nonzero(self._env.board[r, :] != 0))

    def _count_filled_col(self, c: int) -> int:
        return int(np.count_nonzero(self._env.board[:, c] != 0))

    def _count_filled_box(self, r: int, c: int) -> int:
        br, bc = (r // 3) * 3, (c // 3) * 3
        return int(np.count_nonzero(self._env.board[br:br + 3, bc:bc + 3] != 0))
