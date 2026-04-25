# tests/unit/test_phase_manager.py
import math
import pytest

from app.sudoku.phase_manager import PhaseManager, PhaseConfig


def make_pm(**kwargs):
    cfg = PhaseConfig(**kwargs)
    return PhaseManager(cfg)


def test_initial_phase_is_1():
    pm = make_pm()
    assert pm.phase == PhaseManager.PHASE_1


def test_phase1_mrv_starts_at_init():
    pm = make_pm(mrv_init=0.90, phase1_steps=1000)
    assert abs(pm.mrv_prob(0) - 0.90) < 1e-6


def test_phase1_mrv_ends_at_040():
    pm = make_pm(mrv_init=0.90, phase1_steps=1000)
    assert abs(pm.mrv_prob(1000) - 0.40) < 1e-4


def test_phase2_mrv_starts_at_040():
    pm = make_pm(mrv_init=0.90, phase1_steps=100, phase2_steps=1000)
    # Force advance to phase 2 via time backstop
    for _ in range(101):
        pm.record_episode(success=False, mrv_step=101)
    assert pm.phase == PhaseManager.PHASE_2
    assert abs(pm.mrv_prob(100) - 0.40) < 0.01


def test_phase3_mrv_fixed_at_floor():
    pm = make_pm(mrv_init=0.90, phase1_steps=1, phase2_steps=2, mrv_floor=0.05)
    pm.record_episode(success=True, mrv_step=2)
    pm.record_episode(success=True, mrv_step=2)
    # Should be in phase 3
    if pm.phase == PhaseManager.PHASE_3:
        assert abs(pm.mrv_prob(999999) - 0.05) < 1e-6


def test_performance_based_phase1_transition():
    pm = make_pm(tau1=0.50, phase1_steps=100000)
    # Feed 100 successes → rolling_success = 1.0 ≥ 0.50
    for _ in range(100):
        pm.record_episode(success=True, mrv_step=0)
    assert pm.phase >= PhaseManager.PHASE_2


def test_time_backstop_phase1_transition():
    pm = make_pm(tau1=0.99, phase1_steps=5)
    # Feed failures so success_rate never reaches tau1
    for _ in range(10):
        pm.record_episode(success=False, mrv_step=6)
    assert pm.phase >= PhaseManager.PHASE_2


def test_bc_exponent_per_phase():
    pm = make_pm(tau1=0.99, tau2=0.99, phase1_steps=1, phase2_steps=2)
    assert pm.bc_exponent() == 0.5  # phase 1
    pm.record_episode(success=False, mrv_step=2)
    if pm.phase == PhaseManager.PHASE_2:
        assert pm.bc_exponent() == 1.0


def test_state_dict_roundtrip():
    pm = make_pm()
    pm.record_episode(success=True, mrv_step=0)
    sd = pm.state_dict()
    pm2 = make_pm()
    pm2.load_state_dict(sd)
    assert pm2.phase == pm.phase
    assert pm2.rolling_success() == pm.rolling_success()


def test_rolling_success_empty_window_returns_zero():
    pm = make_pm()
    assert pm.rolling_success() == 0.0
