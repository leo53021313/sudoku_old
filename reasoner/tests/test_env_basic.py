import numpy as np
import pytest
from reasoner.env.sudoku_gym_env import SudokuGymEnv


@pytest.fixture
def db_path():
    return "data/puzzle_pool.db"


def test_obs_shape_is_24_channels(db_path):
    env = SudokuGymEnv(db_path=db_path)
    assert env.observation_space.shape == (24, 9, 9)


def test_action_space_is_729(db_path):
    env = SudokuGymEnv(db_path=db_path)
    assert env.action_space.n == 729


def test_max_wrong_fills_default_is_20(db_path):
    env = SudokuGymEnv(db_path=db_path)
    assert env.max_wrong_fills == 20


def test_no_teacher_info_in_step_info(db_path):
    env = SudokuGymEnv(db_path=db_path)
    obs, _ = env.reset()
    masks = env.action_masks()
    legal = np.where(masks)[0]
    if len(legal) == 0:
        pytest.skip("no legal actions")
    obs2, r, term, trunc, info = env.step(int(legal[0]))
    assert "teacher_action" not in info
    assert "teacher_quality" not in info
