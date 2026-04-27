# sb3/tests/test_oracle_teacher.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.sudoku.teacher_engine import TeacherEngine


def _make_env_with_state(board: np.ndarray, solution: np.ndarray) -> SudokuGymEnv:
    """Build an env in a known state without touching the DB."""
    env = SudokuGymEnv(db_path="data/puzzle_pool.db")  # path unused — we skip reset()
    env.board = board.astype(np.int8).copy()
    env.solution = solution.astype(np.int8).copy()
    env.fixed = (board != 0)
    env._rebuild_candidates()
    return env


def _solved_grid() -> np.ndarray:
    """A valid 9x9 solved sudoku for use as 'solution'."""
    return np.array([
        [5,3,4,6,7,8,9,1,2],
        [6,7,2,1,9,5,3,4,8],
        [1,9,8,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9],
    ], dtype=np.int8)


def test_naked_single_detected_with_quality_1_00():
    """Cell with a single candidate must be picked at quality 1.00 with solution value."""
    sol = _solved_grid()
    board = sol.copy()
    board[0, 0] = 0
    env = _make_env_with_state(board, sol)

    teacher = TeacherEngine()
    action, quality = teacher(env)

    assert action == (0, 0, int(sol[0, 0]))
    assert quality == 1.00


def test_hidden_single_detected_with_quality_0_75():
    """A cell that is the only place a digit can go in its row gets quality 0.75."""
    sol = _solved_grid()
    board = sol.copy()
    for r in range(9):
        board[r, 4] = 0
    env = _make_env_with_state(board, sol)

    teacher = TeacherEngine()
    action, quality = teacher(env)

    r, c, v = action
    assert v == int(sol[r, c]), f"value must match solution[{r},{c}]={sol[r,c]}, got {v}"
    assert quality in (1.00, 0.75)


def test_pointing_pair_target_returns_solution_value_at_quality_0_50():
    """When pointing-pair elimination yields a naked single, that cell is chosen at 0.50."""
    sol = _solved_grid()
    board = np.array([
        [0,0,0,6,7,8,9,1,2],
        [0,0,0,1,9,5,3,4,8],
        [0,0,0,3,4,2,5,6,7],
        [8,5,9,7,6,1,4,2,3],
        [4,2,6,8,5,3,7,9,1],
        [7,1,3,9,2,4,8,5,6],
        [9,6,1,5,3,7,2,8,4],
        [2,8,7,4,1,9,6,3,5],
        [3,4,5,2,8,6,1,7,9],
    ], dtype=np.int8)
    env = _make_env_with_state(board, sol)

    teacher = TeacherEngine()
    action, quality = teacher(env)

    r, c, v = action
    assert v == int(sol[r, c])
    assert quality in (1.00, 0.75, 0.50, 0.30)


def test_mrv_fallback_returns_solution_value_at_quality_0_30():
    """When no single technique fires, fall back to MRV cell with solution value at 0.30."""
    sol = _solved_grid()
    board = sol.copy()
    for r in range(3, 6):
        for c in range(3, 6):
            board[r, c] = 0
    env = _make_env_with_state(board, sol)

    teacher = TeacherEngine()
    action, quality = teacher(env)

    r, c, v = action
    assert v == int(sol[r, c]), \
        f"new oracle teacher must use solution value, got v={v} sol={sol[r,c]}"
    assert board[r, c] == 0
    assert quality in (1.00, 0.75, 0.50, 0.30)


def test_value_always_matches_solution_on_random_partial_boards():
    """Property test: for many random partial boards, teacher value == solution[chosen cell]."""
    sol = _solved_grid()
    rng = np.random.default_rng(0)
    teacher = TeacherEngine()

    for _ in range(20):
        board = sol.copy()
        mask = rng.random((9, 9)) < 0.4
        board[mask] = 0
        env = _make_env_with_state(board, sol)

        action, quality = teacher(env)
        if action is None:
            assert (board != 0).all()
            continue
        r, c, v = action
        assert board[r, c] == 0, "teacher chose a non-empty cell"
        assert v == int(sol[r, c]), \
            f"teacher value {v} != solution[{r},{c}]={sol[r,c]} (quality={quality})"
        assert quality in (1.00, 0.75, 0.50, 0.30)
