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


def test_bc_pass_masked_actions_no_nan():
    """_bc_pass must clamp log_probs to min=-1e9 to prevent -inf * 0 = NaN.

    Regression test for W3-2: PyTorch's MaskableCategoricalDistribution can return
    log_prob = -inf for masked actions. IEEE 754 says -inf * 0 = NaN (indeterminate).
    Without a clamp, NaN poisons the BC loss → NaN gradients → NaN policy parameters.

    Strategy: this test verifies the clamp is present in the source AND that the
    clamp logic produces finite, multiplication-safe values when applied to -inf.
    A full integration repro of the failure mode would require either bypassing
    the existing teacher_mask pre-filter or patching MaskableCategoricalDistribution
    deeper than this test's scope; the clamp is defensive in the same vein as the
    W1-2 tq.sum() guard.
    """
    # Part 1: source-level check — verify the clamp(min=-1e9) line exists in _bc_pass
    import inspect
    from app.rl.models.sudoku_ppo import SudokuMaskablePPO
    src = inspect.getsource(SudokuMaskablePPO._bc_pass)
    assert "clamp(min=-1e9)" in src, (
        "_bc_pass() must clamp log_probs to min=-1e9 between evaluate_actions and "
        "the BC loss line — see W3-2 stability fix"
    )

    # Part 2: behavioural check — confirm the clamp produces a multiplication-safe value
    log_probs = torch.tensor([float('-inf'), -100.0, 0.0], requires_grad=True)
    clamped = log_probs.clamp(min=-1e9)
    tq = torch.tensor([0.0, 0.5, 0.5])

    product = clamped * tq
    assert not torch.isnan(product).any(), \
        f"clamp(-1e9) * tq must not produce NaN, got {product}"
    assert torch.isfinite(product).all(), \
        f"clamp(-1e9) * tq must be finite, got {product}"

    # Part 3: behavioural check — full _bc_pass must not produce NaN params on
    # the masked-teacher-action path (smoke test that exercises the real code path)
    model = _make_ppo()
    n = 4
    model._teacher_actions = np.zeros((n, 1), dtype=np.int64)   # action 0
    model._teacher_quality = np.ones((n, 1), dtype=np.float32) * 0.5

    masks = np.ones((n, 729), dtype=np.float32)
    masks[:, 0] = 0.0  # mask action 0 — the teacher-chosen action is illegal here

    model.rollout_buffer = MagicMock()
    model.rollout_buffer.observations = np.zeros((n, *model.observation_space.shape), dtype=np.float32)
    model.rollout_buffer.action_masks  = masks
    model._logger = MagicMock()

    model._bc_pass()

    for name, p in model.policy.named_parameters():
        assert not torch.isnan(p).any(), \
            f"NaN in policy param {name!r} after _bc_pass on masked teacher action"


if __name__ == "__main__":
    test_bc_pass_tiny_quality_no_optimizer_step()
    print("PASS: test_bc_pass_tiny_quality_no_optimizer_step")
    test_bc_pass_masked_actions_no_nan()
    print("PASS: test_bc_pass_masked_actions_no_nan")
