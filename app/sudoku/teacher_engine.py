# app/sudoku/teacher_engine.py
# -*- coding: utf-8 -*-
"""
TeacherEngine：確定性 MRV teacher，回傳 (action, quality_score)。

優先級金字塔：
  Level 1 - naked single   (|candidates|=1)       quality = 1.00
  Level 2 - hidden single  (env._is_hidden_single) quality = 0.75
  Level 3 - min-count ≤ 2                         quality = 0.40
  Level 4 - min-count 3..max_candidates           quality = 0.15
  Level 5 - min-count > max_candidates            (None, 0.0)  ← 不出手

所有選擇確定性（min row → min col → min number），解決原 random.choice 的
stochastic teacher 問題：同一狀態永遠給相同 label，BC 梯度方向一致。
"""

from __future__ import annotations


class TeacherEngine:
    """
    確定性 MRV teacher。

    Parameters
    ----------
    max_candidates : int
        candidate 數超過此值時 teacher 放棄出手（Level 5）。
        預設 4：candidate≥5 的格子信度太低，不產生 BC loss。
    """

    # quality 對應各 level
    _Q_NAKED  = 1.00
    _Q_HIDDEN = 0.75
    _Q_MRV2   = 0.40   # min-count ≤ 2
    _Q_MRV4   = 0.15   # min-count 3..max_candidates

    def __init__(self, max_candidates: int = 4):
        self.max_candidates = max_candidates

    def __call__(self, env) -> tuple[tuple | None, float]:
        """
        回傳 ((row, col, num), quality) 或 (None, 0.0)。

        - Level 1: naked single，掃描順序 (r=0..8, c=0..8)，取第一個。
        - Level 2: hidden single，掃描候選數最少的格子，取第一個被
                   env._is_hidden_single() 認定的 (cell, num)。
        - Level 3-4: MRV，確定性 tie-break (min r, min c, min n)。
        - Level 5: 放棄，回傳 (None, 0.0)。
        """
        # ── Level 1: naked single ─────────────────────────────────────────
        for r in range(9):
            for c in range(9):
                if env.board[r, c] != 0:
                    continue
                cands = env.candidates_cache[r][c]
                if len(cands) == 1:
                    return (r, c, next(iter(cands))), self._Q_NAKED

        # ── Level 2: hidden single ────────────────────────────────────────
        # 從候選數最少的格子開始掃，確保先找到高信度格子
        cells_by_cnt = sorted(
            (
                (len(env.candidates_cache[r][c]), r, c)
                for r in range(9) for c in range(9)
                if env.board[r, c] == 0 and len(env.candidates_cache[r][c]) > 0
            )
        )
        for _, r, c in cells_by_cnt:
            for n in sorted(env.candidates_cache[r][c]):
                if env._is_hidden_single(r, c, n):
                    return (r, c, n), self._Q_HIDDEN

        # ── Level 3-4: MRV（確定性） ──────────────────────────────────────
        if not cells_by_cnt:
            return None, 0.0

        min_cnt, best_r, best_c = cells_by_cnt[0]

        if min_cnt > self.max_candidates:
            return None, 0.0   # Level 5: 信度不足，不出手

        quality = self._Q_MRV2 if min_cnt <= 2 else self._Q_MRV4
        num     = min(env.candidates_cache[best_r][best_c])   # 確定性：最小數字
        return (best_r, best_c, num), quality
