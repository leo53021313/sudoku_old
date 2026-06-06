"""Tests for WrongActionLogCallback (rollout/ep_wrong_mean)."""

from __future__ import annotations

from collections import deque
from types import SimpleNamespace

import numpy as np
import gymnasium as gym
from stable_baselines3.common.monitor import Monitor

from apprentice.train.wrong_action_callback import WrongActionLogCallback


class _FakeLogger:
    def __init__(self) -> None:
        self.records: dict[str, float] = {}

    def record(self, key, value):
        self.records[key] = value


def _make_cb(ep_info_buffer) -> WrongActionLogCallback:
    cb = WrongActionLogCallback()
    # BaseCallback.logger is a property returning self.model.logger, so the
    # fake model must expose both ep_info_buffer and logger.
    cb.model = SimpleNamespace(ep_info_buffer=ep_info_buffer, logger=_FakeLogger())
    return cb


def test_logs_mean_wrong_count():
    buf = deque([
        {"r": 1.0, "l": 10, "wrong_count": 2},
        {"r": 1.0, "l": 10, "wrong_count": 4},
    ])
    cb = _make_cb(buf)
    cb._on_rollout_end()
    assert cb.model.logger.records["rollout/ep_wrong_mean"] == 3.0


def test_no_record_when_buffer_empty():
    cb = _make_cb(deque())
    cb._on_rollout_end()
    assert "rollout/ep_wrong_mean" not in cb.model.logger.records


def test_no_record_when_key_missing():
    cb = _make_cb(deque([{"r": 1.0, "l": 10}]))
    cb._on_rollout_end()
    assert "rollout/ep_wrong_mean" not in cb.model.logger.records


class _TinyEnv(gym.Env):
    """Minimal env that always reports wrong_count on its terminal step."""

    def __init__(self) -> None:
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(1,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(2)
        self._n = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._n = 0
        return np.zeros(1, dtype=np.float32), {}

    def step(self, action):
        self._n += 1
        terminated = self._n >= 3
        info = {"wrong_count": 7, "is_success": True, "steps": self._n}
        return np.zeros(1, dtype=np.float32), 1.0, terminated, False, info


def test_partial_key_presence_uses_only_episodes_with_key():
    buf = deque([
        {"r": 1.0, "l": 10, "wrong_count": 6},
        {"r": 1.0, "l": 10},               # no wrong_count — should be ignored
        {"r": 1.0, "l": 10, "wrong_count": 2},
    ])
    cb = _make_cb(buf)
    cb._on_rollout_end()
    assert cb.model.logger.records["rollout/ep_wrong_mean"] == 4.0  # mean of 6 and 2 only


def test_monitor_propagates_wrong_count_into_episode_info():
    env = Monitor(_TinyEnv(), info_keywords=("wrong_count",))
    env.reset()
    info: dict = {}
    done = False
    while not done:
        _obs, _r, term, trunc, info = env.step(0)
        done = term or trunc
    assert "episode" in info
    assert info["episode"]["wrong_count"] == 7
