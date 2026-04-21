# app/sudoku/validator.py
# -*- coding: utf-8 -*-

import numpy as np


_VALID_GROUP = frozenset(range(1, 10))

def _is_group_valid(nums):
    return {int(x) for x in nums} == _VALID_GROUP


def validate_completed_board(board, fixed=None, base_board=None):
    """
    嚴格驗證 Sudoku 完整解是否合法
    回傳 {"ok": bool, "reason": str}
    """
    board = np.asarray(board, dtype=np.int8)

    if board.shape != (9, 9):
        return {"ok": False, "reason": f"invalid_shape:{board.shape}"}

    if np.any(board == 0):
        return {"ok": False, "reason": "board_not_complete"}

    if np.any(board < 1) or np.any(board > 9):
        return {"ok": False, "reason": "board_has_out_of_range_value"}

    # Givens 不能被改動
    if fixed is not None and base_board is not None:
        fixed      = np.asarray(fixed, dtype=bool)
        base_board = np.asarray(base_board, dtype=np.int8)

        for r in range(9):
            for c in range(9):
                if fixed[r, c] and int(board[r, c]) != int(base_board[r, c]):
                    return {"ok": False, "reason": f"fixed_cell_modified:r{r}c{c}"}

    for r in range(9):
        if not _is_group_valid(board[r, :]):
            return {"ok": False, "reason": f"invalid_row:{r}"}

    for c in range(9):
        if not _is_group_valid(board[:, c]):
            return {"ok": False, "reason": f"invalid_col:{c}"}

    for br in range(3):
        for bc in range(3):
            block = board[br*3:br*3+3, bc*3:bc*3+3].reshape(-1)
            if not _is_group_valid(block):
                return {"ok": False, "reason": f"invalid_box:{br},{bc}"}

    return {"ok": True, "reason": "local_rule_check_passed"}
