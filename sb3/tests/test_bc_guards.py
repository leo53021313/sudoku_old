# sb3/tests/test_bc_guards.py
"""Verify BC loss NaN guard prevents optimizer step when teacher quality is near-zero."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import torch
from unittest.mock import MagicMock, patch


def _make_ppo():
    from app.rl.models.sudoku_ppo import SudokuMaskablePPO
    from app.rl.models.features_extractor import SudokuFeaturesExtractor
    from stable_baselines3.common.vec_env import DummyVecEnv
    from app.rl.envs.sudoku_gym_env import SudokuGymEnv
    env = DummyVecEnv([lambda: SudokuGymEnv(db_path='../data/puzzle_pool.db')])
    model = SudokuMaskablePPO(
        "CnnPolicy", env, n_steps=64, verbose=0, bc_coef=1.0, mrv_prob_init=0.8,
        policy_kwargs=dict(
            features_extractor_class=SudokuFeaturesExtractor,
            features_extractor_kwargs={"features_dim": 192},
            net_arch={"pi": [], "vf": [128]},
        ),
    )
    env.close()
    return model


def test_bc_pass_tiny_quality_no_optimizer_step():
    """_bc_pass must early-return (no optimizer step) when tq.sum() < 1e-8."""
    model = _make_ppo()
    # quality = 1e-9: positive so passes teacher_mask (> 0), but sum = 1e-9 < 1e-8
    n = 1
    model._teacher_actions = np.array([[0]], dtype=np.int64)
    model._teacher_quality = np.array([[1e-9]], dtype=np.float32)

    model.rollout_buffer = MagicMock()
    model.rollout_buffer.observations = np.zeros((n, *model.observation_space.shape), dtype=np.float32)
    model.rollout_buffer.action_masks  = np.ones((n, 729), dtype=np.float32)

    step_count = [0]
    original_step = model.policy.optimizer.step

    def counting_step():
        step_count[0] += 1
        return original_step()

    model.policy.optimizer.step = counting_step

    # Mock logger to avoid AttributeError
    model._logger = MagicMock()

    # Before fix: no tq.sum() guard → optimizer steps with tiny noisy gradient
    # After fix: tq.sum() = 1e-9 < 1e-8 → early return, no optimizer step
    model._bc_pass()

    assert step_count[0] == 0, \
        f"Optimizer stepped {step_count[0]} times — tq.sum() < 1e-8 guard not working"


if __name__ == "__main__":
    test_bc_pass_tiny_quality_no_optimizer_step()
    print("PASS: test_bc_pass_tiny_quality_no_optimizer_step")
