"""Tests for CurriculumCallback — bridges CurriculumController to SB3."""

from unittest.mock import MagicMock, patch
import pytest

from apprentice.train.curriculum_callback import CurriculumCallback
from apprentice.train.curriculum_controller import CurriculumController


def _default_config():
    return {
        "initial_target_empty": 3,
        "min_target_empty": 3,
        "max_target_empty": 55,
        "target_rate": 0.70,
        "tolerance_band": [0.55, 0.85],
        "step_size": 10.0,
        "window_size": 200,
        "min_episodes_before_update": 100,
        "min_steps_between_updates": 50000,
        "stagnation_threshold_steps": 500000,
        "stagnation_probe_step": 1,
        "stagnation_rollback_threshold": 0.40,
        "stagnation_rollback_window_steps": 200000,
    }


def _mock_vec_env():
    """Mock VecEnv-like object with set_attr / env_method support."""
    venv = MagicMock()
    venv.num_envs = 4
    # Track env_method calls
    venv._env_method_calls = []
    def _env_method(name, *args, **kwargs):
        venv._env_method_calls.append((name, args, kwargs))
        return [None] * venv.num_envs
    venv.env_method.side_effect = _env_method
    return venv


def test_callback_initializes_controller_from_config():
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=50_000, verbose=0)
    # Just instantiate; no asserts on internal state beyond controller link
    assert cb.controller is ctrl


def test_callback_record_outcome_from_info_dict():
    """When env emits is_success=True info dict on episode end, callback records it."""
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=50_000, verbose=0)

    # Simulate _on_step with locals_ containing dones + infos
    cb.model = MagicMock()
    cb.model.num_timesteps = 100
    cb.locals = {
        "dones": [True, False, True, False],
        "infos": [
            {"is_success": True},
            {"is_success": False},
            {"is_success": False},
            {"is_success": False},
        ],
    }
    cb._on_step()

    # 2 episodes finished, 1 success, 1 failure
    assert list(ctrl._success_window) == [1, 0]


def test_callback_pushes_target_empty_at_update_interval():
    """At update_interval_steps boundary, callback applies target_empty to all envs."""
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=10_000, verbose=0)

    venv = _mock_vec_env()
    cb.model = MagicMock()
    cb.model.get_env.return_value = venv

    # Pre-fill controller window with high success
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95

    cb.model.num_timesteps = 10_000
    cb.locals = {"dones": [False] * 4, "infos": [{}] * 4}
    cb._last_update_step = 0
    cb._on_step()

    # Controller should have advanced; callback should have pushed target to envs
    calls = venv._env_method_calls
    set_target_calls = [c for c in calls if c[0] == "set_target_empty"]
    assert len(set_target_calls) >= 1
    pushed = set_target_calls[-1][1][0]
    assert pushed == ctrl.target_empty_rounded


def test_callback_does_not_update_before_interval():
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=10_000, verbose=0)
    venv = _mock_vec_env()
    cb.model = MagicMock()
    cb.model.get_env.return_value = venv
    cb._last_update_step = 0
    cb.model.num_timesteps = 5_000  # halfway to interval
    cb.locals = {"dones": [False] * 4, "infos": [{}] * 4}
    cb._on_step()

    # No update happened yet
    set_target_calls = [c for c in venv._env_method_calls if c[0] == "set_target_empty"]
    assert len(set_target_calls) == 0
