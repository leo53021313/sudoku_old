"""Tests for measure_wrong.measure() — distribution-agnostic rollout loop."""

from __future__ import annotations

import numpy as np

from apprentice.eval.measure_wrong import measure


class _ScriptedEnv:
    """Terminates each episode after a scripted number of steps and reports a
    fixed wrong_count / success. No DB, no real Sudoku logic."""

    def __init__(self, n_actions, episodes):
        # episodes: list of {"steps": int, "wrong": int, "success": bool}
        self.n_actions = n_actions
        self._episodes = episodes
        self._ep_idx = -1
        self._step = 0

    def reset(self, *, seed=None, options=None):
        self._ep_idx += 1
        self._step = 0
        return np.zeros(1, dtype=np.float32), {}

    def action_masks(self):
        m = np.zeros(self.n_actions, dtype=bool)
        m[0] = True
        return m

    def step(self, action):
        self._step += 1
        ep = self._episodes[self._ep_idx]
        terminated = self._step >= ep["steps"]
        info = {
            "is_success": ep["success"] if terminated else False,
            "wrong_count": ep["wrong"],
            "steps": self._step,
        }
        return np.zeros(1, dtype=np.float32), 0.0, terminated, False, info


class _DummyPolicy:
    def predict(self, obs, action_masks=None, deterministic=True):
        valid = np.flatnonzero(action_masks[0])
        return np.array([int(valid[0])]), None


def test_measure_aggregates_correctly():
    episodes = [
        {"steps": 5, "wrong": 2, "success": True},
        {"steps": 3, "wrong": 0, "success": True},
        {"steps": 4, "wrong": 10, "success": False},
    ]
    env = _ScriptedEnv(n_actions=10, episodes=episodes)
    stats = measure(_DummyPolicy(), env, n_episodes=3)

    assert stats["n_episodes"] == 3
    assert stats["success_rate"] == 2 / 3
    assert stats["mean_wrong"] == (2 + 0 + 10) / 3
    assert stats["max_wrong"] == 10
    assert stats["mean_steps"] == (5 + 3 + 4) / 3
