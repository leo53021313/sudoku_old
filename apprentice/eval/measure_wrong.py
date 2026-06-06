"""measure_wrong — one-off per-episode error-rate measurement for a checkpoint.

Loads a trained apprentice checkpoint and runs deterministic (greedy) rollouts,
reporting per-episode wrong_count alongside success rate. Used to baseline the
current model before any error-reduction optimization.

NOTE: deterministic=True measures the policy's actual competence. Training's
rollout/ep_wrong_mean is from stochastic sampling (exploration) and will read
higher; the two are not directly comparable.
"""

from __future__ import annotations

import numpy as np


def measure(model, env, n_episodes: int, seed: int | None = None) -> dict:
    """Run n_episodes deterministic rollouts; return aggregate error stats.

    env must expose reset(seed=)/step(action)/action_masks() and put
    is_success / wrong_count / steps into the step info dict.
    All fields are 0 when n_episodes == 0.
    """
    successes: list[bool] = []
    wrongs: list[int] = []
    steps: list[int] = []

    for i in range(n_episodes):
        ep_seed = None if seed is None else seed + i
        obs, _ = env.reset(seed=ep_seed)
        done = False
        info: dict = {}
        while not done:
            masks = env.action_masks()[np.newaxis]
            action, _ = model.predict(
                obs[np.newaxis], action_masks=masks, deterministic=True
            )
            obs, _reward, terminated, truncated, info = env.step(int(action[0]))
            done = terminated or truncated
        successes.append(bool(info.get("is_success", False)))
        wrongs.append(int(info.get("wrong_count", 0)))
        steps.append(int(info.get("steps", 0)))

    return {
        "n_episodes": len(successes),
        "success_rate": sum(successes) / len(successes) if successes else 0.0,
        "mean_wrong": float(np.mean(wrongs)) if wrongs else 0.0,
        "max_wrong": int(max(wrongs)) if wrongs else 0,
        "mean_steps": float(np.mean(steps)) if steps else 0.0,
    }
