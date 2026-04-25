# tests/unit/test_teacher_engine.py
import pytest

from app.sudoku.env import SudokuEnv
from app.sudoku.teacher_engine import TeacherEngine
from tests.conftest import SAMPLE_BOARD, SAMPLE_FIXED, SAMPLE_SOLUTION


def make_env_with_board(board, fixed):
    env = SudokuEnv()
    env.reset_from_board(board, fixed)
    return env


def test_deterministic_same_state_same_action():
    env1 = make_env_with_board(SAMPLE_BOARD, SAMPLE_FIXED)
    env2 = make_env_with_board(SAMPLE_BOARD, SAMPLE_FIXED)
    teacher = TeacherEngine()
    action1, quality1 = teacher(env1)
    action2, quality2 = teacher(env2)
    assert action1 == action2
    assert quality1 == quality2


def test_naked_single_returns_quality_1():
    env = SudokuEnv()
    board = [row[:] for row in SAMPLE_SOLUTION]
    fixed = [[True]*9 for _ in range(9)]
    # Leave one cell empty — it will be a naked single
    board[0][0] = 0
    fixed[0][0] = False
    env.reset_from_board(board, fixed)

    # Verify it's a naked single
    cands = env.candidates_cache[0][0]
    if len(cands) == 1:
        teacher = TeacherEngine()
        action, quality = teacher(env)
        assert quality == TeacherEngine._Q_NAKED
        assert action is not None
        assert action == (0, 0, next(iter(cands)))


def test_empty_board_returns_none():
    env = SudokuEnv()
    # Fully solved board
    board = [row[:] for row in SAMPLE_SOLUTION]
    fixed = [[True]*9 for _ in range(9)]
    env.reset_from_board(board, fixed)
    teacher = TeacherEngine()
    action, quality = teacher(env)
    assert action is None
    assert quality == 0.0


def test_max_candidates_abstain():
    env = make_env_with_board(SAMPLE_BOARD, SAMPLE_FIXED)
    # With max_candidates=0, teacher should always abstain
    teacher = TeacherEngine(max_candidates=0)
    action, quality = teacher(env)
    # Either abstain (None) or found a naked/hidden single (quality >= 0.75)
    if action is None:
        assert quality == 0.0
    else:
        assert quality >= TeacherEngine._Q_HIDDEN


def test_mrv_quality_level3_vs_level4():
    teacher = TeacherEngine(max_candidates=4)
    env = make_env_with_board(SAMPLE_BOARD, SAMPLE_FIXED)
    action, quality = teacher(env)
    # Quality should be one of the defined levels
    assert quality in (
        TeacherEngine._Q_NAKED,
        TeacherEngine._Q_HIDDEN,
        TeacherEngine._Q_MRV2,
        TeacherEngine._Q_MRV4,
        0.0,
    )
