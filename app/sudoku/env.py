# app/sudoku/env.py
# -*- coding: utf-8 -*-
"""
SudokuEnv v3 — 改進 Reward 設計 + Hidden Single 偵測

★ Reward 重新設計原則：
  1. 裸單格（Naked Single）是最確定的填法，給最高獎勵
  2. 隱藏單格（Hidden Single）是第二層推理，次高獎勵
  3. 死局懲罰必須遠遠超過一般步的累積，讓 advantage 對比明顯
  4. env 層只給「局部」獎勵；main 層的 SUCCESS_BONUS 負責「全局」驗證獎勵

★ 數值變化：
  REWARD_STEP          =  1.0   每填一格（不變）
  REWARD_NAKED_SINGLE  =  3.0   裸單格加成 ↑（舊版 1.5）
  REWARD_HIDDEN_SINGLE =  1.5   隱藏單格加成（新增）
  REWARD_UNIT_COMPLETE =  5.0   完成一行/列/宮（不變）
  REWARD_BOARD_DONE    = 15.0   填滿所有格 ↓（舊版 30，main SUCCESS_BONUS 負責主要信號）
  PENALTY_DEAD_END     = -30.0  製造死局 ↓（舊版 -15，加強讓 PPO advantage 對比顯著）
  PENALTY_INVALID      =  -3.0  非法動作 ↑（舊版 -2）

★ 理由：
  舊版：dead_end=-15，普通步=1.0，差距僅 15。
       30 步後累積 30 獎勵 vs -15，agent 容易忽視死局。
  新版：dead_end=-30，差距 31。一個死局否定 31 步努力，PPO 學到清晰的 advantage 對比。
"""

import numpy as np


class SudokuEnv:

    REWARD_STEP          =  1.0
    REWARD_NAKED_SINGLE  =  3.0
    REWARD_HIDDEN_SINGLE =  1.5
    REWARD_UNIT_COMPLETE =  5.0
    REWARD_BOARD_DONE    = 15.0
    PENALTY_DEAD_END     = -30.0
    PENALTY_INVALID      =  -3.0

    def __init__(self, page=None, max_invalid=3):
        self.page        = page
        self.max_invalid = max_invalid

        self.board  = np.zeros((9, 9), dtype=np.int8)
        self.fixed  = np.zeros((9, 9), dtype=bool)

        self.invalid_count = 0
        self.done          = False

        self.candidates_cache      = [[set() for _ in range(9)] for _ in range(9)]
        self.candidate_count_grid  = np.zeros((9, 9), dtype=np.int8)
        self.single_candidate_grid = np.zeros((9, 9), dtype=np.float32)

        self.action_history = []

    # ── Reset ──────────────────────────────────────────────────────────────

    def reset_from_web(self):
        if self.page is None:
            raise ValueError("reset_from_web() 需要 page")
        from app.web.reader import WebSudokuReader
        reader = WebSudokuReader(self.page)
        board, fixed, _ = reader.read_board()
        self.board = np.array(board, dtype=np.int8).copy()
        self.fixed = np.array(fixed, dtype=bool).copy()
        self.invalid_count = 0
        self.done = False
        self.action_history = []
        self._rebuild_all_candidates()
        return self.board.copy()

    def reset_from_board(self, board, fixed):
        self.board = np.array(board, dtype=np.int8).copy()
        self.fixed = np.array(fixed, dtype=bool).copy()
        self.invalid_count = 0
        self.done = False
        self.action_history = []
        self._rebuild_all_candidates()
        return self.board.copy()

    # ── Internal helpers ───────────────────────────────────────────────────

    def _get_box_start(self, r, c): return (r // 3) * 3, (c // 3) * 3

    def _iter_related_cells(self, row, col):
        related = set()
        for c in range(9): related.add((row, c))
        for r in range(9): related.add((r, col))
        br, bc = self._get_box_start(row, col)
        for r in range(br, br+3):
            for c in range(bc, bc+3):
                related.add((r, c))
        return related

    def _compute_candidates_for_cell(self, row, col):
        if self.fixed[row, col] or self.board[row, col] != 0:
            return set()
        used = set()
        used.update(int(v) for v in self.board[row, :] if v != 0)
        used.update(int(v) for v in self.board[:, col] if v != 0)
        br, bc = self._get_box_start(row, col)
        used.update(
            int(self.board[r, c])
            for r in range(br, br+3)
            for c in range(bc, bc+3)
            if self.board[r, c] != 0
        )
        return {n for n in range(1, 10) if n not in used}

    def _update_cached_cell(self, row, col):
        cands = self._compute_candidates_for_cell(row, col)
        self.candidates_cache[row][col] = cands
        cnt = len(cands)
        self.candidate_count_grid[row, col] = cnt
        self.single_candidate_grid[row, col] = 1.0 if cnt == 1 else 0.0

    def _rebuild_all_candidates(self):
        for r in range(9):
            for c in range(9):
                self._update_cached_cell(r, c)

    def _refresh_related_candidates(self, row, col):
        for r, c in self._iter_related_cells(row, col):
            self._update_cached_cell(r, c)
        self.candidates_cache[row][col] = set()
        self.candidate_count_grid[row, col] = 0
        self.single_candidate_grid[row, col] = 0.0

    def _count_filled_in_row(self, r): return int(np.count_nonzero(self.board[r, :] != 0))
    def _count_filled_in_col(self, c): return int(np.count_nonzero(self.board[:, c] != 0))

    def _count_filled_in_box(self, r, c):
        br, bc = self._get_box_start(r, c)
        return int(np.count_nonzero(self.board[br:br+3, bc:bc+3] != 0))

    def _has_dead_end(self):
        empty = (self.board == 0)
        if not np.any(empty): return False
        return bool(np.any(self.candidate_count_grid[empty] == 0))

    # ── ★ Hidden Single 偵測 ────────────────────────────────────────────────

    def _is_only_place_in_group(self, row, col, num, group_cells):
        """
        在 group_cells 中，num 是否只有 (row, col) 可以填。
        （隱藏單格的定義）
        """
        for r, c in group_cells:
            if r == row and c == col:
                continue
            if self.board[r, c] == 0 and num in self.candidates_cache[r][c]:
                return False
        return True

    def _is_hidden_single(self, row, col, num):
        """
        判斷填入 (row, col, num) 是否為隱藏單格：
        在所在行、列、宮中，num 只有此格可以填。
        """
        # 行
        if self._is_only_place_in_group(row, col, num,
                                         [(row, c) for c in range(9)]):
            return True
        # 列
        if self._is_only_place_in_group(row, col, num,
                                         [(r, col) for r in range(9)]):
            return True
        # 宮
        br, bc = self._get_box_start(row, col)
        if self._is_only_place_in_group(row, col, num,
                                         [(br + dr, bc + dc) for dr in range(3) for dc in range(3)]):
            return True
        return False

    # ── Public queries ─────────────────────────────────────────────────────

    def get_candidates(self, r, c): return sorted(self.candidates_cache[r][c])
    def get_candidate_count_grid(self): return self.candidate_count_grid.copy()
    def get_single_candidate_grid(self): return self.single_candidate_grid.copy()

    def is_valid_number(self, r, c, n):
        return (0 <= r < 9 and 0 <= c < 9 and 1 <= n <= 9
                and n in self.candidates_cache[r][c])

    def get_valid_actions(self):
        if self.done: return []
        return [
            (r, c, n)
            for r in range(9) for c in range(9)
            if self.board[r, c] == 0
            for n in self.candidates_cache[r][c]
        ]

    def get_action_mask(self):
        mask = np.zeros(729, dtype=bool)
        if self.done: return mask
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0: continue
                for n in self.candidates_cache[r][c]:
                    mask[(r * 9 + c) * 9 + (n - 1)] = True
        return mask

    def count_empty(self): return int(np.count_nonzero(self.board == 0))

    # ── Step ──────────────────────────────────────────────────────────────

    def step(self, action):
        if self.done:
            return self.board.copy(), 0.0, True, {"valid": False, "reason": "already_done"}

        row, col, num = action

        if not (0 <= row < 9 and 0 <= col < 9 and 1 <= num <= 9):
            self.invalid_count += 1
            if self.invalid_count >= self.max_invalid: self.done = True
            return self.board.copy(), self.PENALTY_INVALID, self.done, {
                "valid": False, "reason": "out_of_range"}

        if self.fixed[row, col] or self.board[row, col] != 0:
            self.invalid_count += 1
            if self.invalid_count >= self.max_invalid: self.done = True
            return self.board.copy(), self.PENALTY_INVALID, self.done, {
                "valid": False, "reason": "occupied_or_fixed"}

        if num not in self.candidates_cache[row][col]:
            self.invalid_count += 1
            if self.invalid_count >= self.max_invalid: self.done = True
            return self.board.copy(), self.PENALTY_INVALID, self.done, {
                "valid": False, "reason": "rule_violation"}

        # ── ★ 填格前判斷 Reward 類型（必須在修改 board 前執行）──────────────
        is_naked  = (len(self.candidates_cache[row][col]) == 1)
        is_hidden = (not is_naked) and self._is_hidden_single(row, col, num)

        row_before = self._count_filled_in_row(row)
        col_before = self._count_filled_in_col(col)
        box_before = self._count_filled_in_box(row, col)

        # ── Fill ──────────────────────────────────────────────────────────
        self.board[row, col] = num
        self.action_history.append((int(row), int(col), int(num)))
        self._refresh_related_candidates(row, col)

        # ── ★ Reward 組合 ─────────────────────────────────────────────────
        reward = self.REWARD_STEP

        if is_naked:
            reward += self.REWARD_NAKED_SINGLE
        elif is_hidden:
            reward += self.REWARD_HIDDEN_SINGLE

        if row_before < 9 and self._count_filled_in_row(row) == 9:
            reward += self.REWARD_UNIT_COMPLETE
        if col_before < 9 and self._count_filled_in_col(col) == 9:
            reward += self.REWARD_UNIT_COMPLETE
        if box_before < 9 and self._count_filled_in_box(row, col) == 9:
            reward += self.REWARD_UNIT_COMPLETE

        # ── 終止條件 ──────────────────────────────────────────────────────
        if not np.any(self.board == 0):
            self.done = True
            reward += self.REWARD_BOARD_DONE
            return self.board.copy(), reward, True, {
                "valid": True, "completed": True, "reason": "completed",
                "naked": is_naked, "hidden": is_hidden}

        if self._has_dead_end():
            self.done = True
            reward += self.PENALTY_DEAD_END
            return self.board.copy(), reward, True, {
                "valid": True, "completed": False, "reason": "dead_end",
                "naked": is_naked, "hidden": is_hidden}

        return self.board.copy(), reward, False, {
            "valid": True, "reason": "continue",
            "naked": is_naked, "hidden": is_hidden}