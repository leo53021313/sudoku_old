"""Tests for CurriculumController — sweet-spot adaptive update logic."""

import pytest
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


def test_initial_state():
    ctrl = CurriculumController(_default_config())
    assert ctrl.target_empty_rounded == 3
    assert ctrl.last_advance_step == 0


def test_insufficient_window_no_update():
    """Update before reaching min_episodes_before_update is a no-op."""
    ctrl = CurriculumController(_default_config())
    for i in range(50):  # less than min_episodes_before_update=100
        ctrl.record_episode_outcome(success=True)
    ctrl.update(current_step=100_000)
    assert ctrl.target_empty_rounded == 3  # unchanged


def test_in_band_no_change():
    """sr in [0.55, 0.85] → target_empty stays."""
    ctrl = CurriculumController(_default_config())
    for _ in range(200):
        ctrl.record_episode_outcome(success=(0.70 > 0.30))  # ~70% success
    # Fill window with 70% success exactly
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))  # 0.70 success rate
    ctrl.update(current_step=100_000)
    assert ctrl.target_empty_rounded == 3


def test_too_easy_advance():
    """sr > 0.85 → target_empty increases."""
    ctrl = CurriculumController(_default_config())
    # Fill window with 95% success
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95
    ctrl.update(current_step=100_000)
    # adjustment = (0.95 - 0.85) * 10 = 1.0 → +1 round to 4
    assert ctrl.target_empty_rounded == 4
    assert ctrl.last_advance_step == 100_000


def test_too_hard_retreat():
    """sr < 0.55 → target_empty decreases."""
    cfg = _default_config()
    cfg["initial_target_empty"] = 10
    ctrl = CurriculumController(cfg)
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 3))  # 0.30 sr
    ctrl.update(current_step=100_000)
    # adjustment = (0.55 - 0.30) * 10 = 2.5 → 10 - 2.5 = 7.5 → 8
    assert ctrl.target_empty_rounded == 8


def test_clamp_to_min():
    cfg = _default_config()
    cfg["initial_target_empty"] = 4
    ctrl = CurriculumController(cfg)
    for _ in range(200):
        ctrl.record_episode_outcome(success=False)
    ctrl.update(current_step=100_000)
    # adjustment = (0.55 - 0.0) * 10 = 5.5 → 4 - 5.5 = -1.5 → clamped to 3
    assert ctrl.target_empty_rounded == 3


def test_clamp_to_max():
    cfg = _default_config()
    cfg["initial_target_empty"] = 54
    ctrl = CurriculumController(cfg)
    for _ in range(200):
        ctrl.record_episode_outcome(success=True)
    ctrl.update(current_step=100_000)
    # adjustment = (1.0 - 0.85) * 10 = 1.5 → 54 + 1.5 = 55.5 → clamped to 55
    assert ctrl.target_empty_rounded == 55


def test_min_steps_between_updates():
    """Cannot update twice within min_steps_between_updates."""
    ctrl = CurriculumController(_default_config())
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95
    ctrl.update(current_step=100_000)
    advanced_to = ctrl.target_empty_rounded
    # second update within min_steps_between_updates
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))
    ctrl.update(current_step=100_000 + 1000)  # only 1k later
    assert ctrl.target_empty_rounded == advanced_to  # no change


def test_record_episode_outcome_bounded_window():
    """Episode window must not grow beyond window_size."""
    cfg = _default_config()
    cfg["window_size"] = 50
    ctrl = CurriculumController(cfg)
    for _ in range(100):
        ctrl.record_episode_outcome(success=True)
    assert len(ctrl._success_window) == 50


def test_stagnation_probe_after_threshold_steps():
    """If target_empty hasn't moved for stagnation_threshold_steps, probe +1."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    ctrl = CurriculumController(cfg)

    # Stay perfectly in sweet spot (sr=0.70) for a while
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))

    # First update at step 50k → no change (in band)
    ctrl.update(current_step=50_000)
    assert ctrl.target_empty_rounded == 5

    # At step 150k (> threshold from last_advance_step=0)
    # → should probe +1
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 6
    assert ctrl._probe_target == 6.0


def test_probe_success_clears_probe_state():
    """If sr stays acceptable after probe, probe state clears."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    cfg["stagnation_rollback_window_steps"] = 50_000
    ctrl = CurriculumController(cfg)

    # Trigger probe
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl._probe_target == 6.0

    # Now agent does OK at new target — sr stays at 0.70
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    # After rollback window, probe should be cleared
    ctrl.update(current_step=210_000)  # 60k after probe started, > rollback_window
    assert ctrl._probe_target is None


def test_probe_failure_triggers_rollback():
    """If sr drops below rollback threshold after probe, target_empty rolls back."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    cfg["stagnation_rollback_window_steps"] = 50_000
    cfg["stagnation_rollback_threshold"] = 0.40
    ctrl = CurriculumController(cfg)

    # Trigger probe to 6
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 6

    # Now agent struggles at 6 — sr drops to 0.20
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 2))  # 0.20

    # Wait until rollback_window has passed
    ctrl.update(current_step=210_000)  # 60k after probe started
    # Probe failed; rollback to 5
    assert ctrl.target_empty_rounded == 5
    assert ctrl._probe_target is None


def test_probe_rollback_clamps_to_min():
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 3
    cfg["stagnation_rollback_window_steps"] = 50_000
    cfg["min_target_empty"] = 3
    ctrl = CurriculumController(cfg)

    # Trigger probe — even though we're at min, probe just adds 1
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 4  # 3 + 1

    # Fail probe
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=False)
    ctrl.update(current_step=210_000)
    # Rollback would be 4 - 1 = 3, which is min, so clamps to 3.
    assert ctrl.target_empty_rounded == 3
