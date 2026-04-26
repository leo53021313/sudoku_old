# sb3/tests/test_obs_encoding.py
"""Tests for the new 26-channel observation encoding."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from app.rl.envs.sudoku_gym_env import SudokuGymEnv


def get_env_and_obs():
    env = SudokuGymEnv(db_path='../data/puzzle_pool.db')
    obs, _ = env.reset()
    return env, obs


def test_obs_shape():
    env, obs = get_env_and_obs()
    assert obs.shape == (26, 9, 9), f"Expected (26,9,9), got {obs.shape}"
    env.close()
    print("test_obs_shape: PASS")


def test_one_hot_board_channels():
    """Channels 0-8: one-hot for digit v+1; empty cells should be all-zero in these channels."""
    env, obs = get_env_and_obs()
    for r in range(9):
        for c in range(9):
            v = env.board[r, c]
            if v != 0:
                assert obs[v - 1, r, c] == 1.0, \
                    f"board[{r},{c}]={v}: obs[{v-1},{r},{c}]={obs[v-1,r,c]} != 1.0"
                for other in range(9):
                    if other != v - 1:
                        assert obs[other, r, c] == 0.0, \
                            f"board[{r},{c}]={v}: obs[{other},{r},{c}]={obs[other,r,c]} != 0.0"
            else:
                for ch in range(9):
                    assert obs[ch, r, c] == 0.0, \
                        f"empty [{r},{c}]: obs[{ch},{r},{c}]={obs[ch,r,c]} != 0.0"
    env.close()
    print("test_one_hot_board_channels: PASS")


def test_candidate_channels():
    """Channels 9-17: per-digit binary masks for candidate sets."""
    env, obs = get_env_and_obs()
    for r in range(9):
        for c in range(9):
            for v in range(1, 10):
                expected = float(
                    env.board[r, c] == 0 and v in env.candidates_cache[r][c]
                )
                actual = obs[9 + v - 1, r, c]
                assert actual == expected, \
                    f"candidates[{r},{c}][{v}]: obs[{9+v-1}]={actual} != {expected}"
    env.close()
    print("test_candidate_channels: PASS")


def test_fixed_channel():
    """Channel 18: 1.0 for given cells, 0.0 for empty cells."""
    env, obs = get_env_and_obs()
    expected = env.fixed.astype(np.float32)
    np.testing.assert_array_equal(obs[18], expected)
    env.close()
    print("test_fixed_channel: PASS")


def test_empty_channel():
    """Channel 19: complement of filled cells."""
    env, obs = get_env_and_obs()
    expected = (env.board == 0).astype(np.float32)
    np.testing.assert_array_equal(obs[19], expected)
    env.close()
    print("test_empty_channel: PASS")


def test_fill_ratio_channels():
    """Channels 20-22: row/col/box fill ratios in [0,1]."""
    env, obs = get_env_and_obs()
    # Check row ratios (ch 20): each row value should equal filled_count/9
    for r in range(9):
        expected_ratio = float(np.count_nonzero(env.board[r, :] != 0)) / 9.0
        np.testing.assert_allclose(obs[20, r, :], expected_ratio, atol=1e-6,
            err_msg=f"Row {r} fill ratio mismatch")
    # Check col ratios (ch 21)
    for c in range(9):
        expected_ratio = float(np.count_nonzero(env.board[:, c] != 0)) / 9.0
        np.testing.assert_allclose(obs[21, :, c], expected_ratio, atol=1e-6,
            err_msg=f"Col {c} fill ratio mismatch")
    # Bounds check
    assert obs[20].min() >= 0.0 and obs[20].max() <= 1.0
    assert obs[21].min() >= 0.0 and obs[21].max() <= 1.0
    assert obs[22].min() >= 0.0 and obs[22].max() <= 1.0
    env.close()
    print("test_fill_ratio_channels: PASS")


def test_candidate_count_channel():
    """Channel 23: candidate_count_grid / 9.0."""
    env, obs = get_env_and_obs()
    expected = env.candidate_count_grid.astype(np.float32) / 9.0
    np.testing.assert_allclose(obs[23], expected, atol=1e-6)
    env.close()
    print("test_candidate_count_channel: PASS")


def test_naked_single_channel():
    """Channel 24: 1.0 only for cells with exactly 1 candidate."""
    env, obs = get_env_and_obs()
    expected = env.single_candidate_grid
    np.testing.assert_array_equal(obs[24], expected)
    env.close()
    print("test_naked_single_channel: PASS")


def test_obs_bounds():
    """All values must be in [0.0, 1.0]."""
    env, obs = get_env_and_obs()
    assert obs.min() >= 0.0, f"obs.min()={obs.min()} < 0"
    assert obs.max() <= 1.0, f"obs.max()={obs.max()} > 1"
    env.close()
    print("test_obs_bounds: PASS")


if __name__ == "__main__":
    test_obs_shape()
    test_one_hot_board_channels()
    test_candidate_channels()
    test_fixed_channel()
    test_empty_channel()           # new
    test_fill_ratio_channels()     # new
    test_candidate_count_channel() # new
    test_naked_single_channel()    # new
    test_obs_bounds()
    print("\nAll obs encoding tests PASSED")
