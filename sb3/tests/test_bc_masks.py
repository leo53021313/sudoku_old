# sb3/tests/test_bc_masks.py
"""Verify that evaluate_actions accepts action_masks and produces different log_probs."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import torch
from stable_baselines3.common.vec_env import DummyVecEnv
from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.models.sudoku_ppo import SudokuMaskablePPO
from app.rl.models.features_extractor import SudokuFeaturesExtractor


def _make_env():
    return SudokuGymEnv(db_path='../data/puzzle_pool.db')


def test_bc_logprob_differs_with_masks():
    env = DummyVecEnv([_make_env])
    model = SudokuMaskablePPO(
        "CnnPolicy", env, n_steps=64, verbose=0,
        policy_kwargs=dict(
            features_extractor_class=SudokuFeaturesExtractor,
            features_extractor_kwargs={"features_dim": 192},
            net_arch={"pi": [], "vf": [128]},
        ),
    )
    n_channels = env.observation_space.shape[0]
    obs_np = np.random.rand(4, n_channels, 9, 9).astype(np.float32)
    obs_t  = torch.as_tensor(obs_np, device=model.device)
    actions = torch.zeros(4, dtype=torch.long, device=model.device)

    # Full mask (no restriction)
    full_masks = torch.ones(4, 729, dtype=torch.bool, device=model.device)
    # Restricted: only action 0 is valid
    restricted = torch.zeros(4, 729, dtype=torch.bool, device=model.device)
    restricted[:, 0] = True

    _, lp_full,       _ = model.policy.evaluate_actions(obs_t, actions, action_masks=full_masks)
    _, lp_restricted, _ = model.policy.evaluate_actions(obs_t, actions, action_masks=restricted)

    # With only action 0 valid, log_prob(action 0) must be 0.0 = log(1.0)
    assert (lp_restricted.detach().cpu().numpy() > lp_full.detach().cpu().numpy()).all(), \
        "Restricted mask should give higher log_prob for the only valid action"
    print("PASS")
    env.close()


if __name__ == "__main__":
    test_bc_logprob_differs_with_masks()
