# sb3/tests/test_milestone_callback.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

from app.rl.curriculum.milestone_callback import MilestoneCallback, MILESTONES


def test_milestone_definitions_match_spec():
    """MILESTONES must match the spec table exactly."""
    by_step = {m["step"]: m for m in MILESTONES}
    assert 100_000 in by_step
    assert 300_000 in by_step
    assert 500_000 in by_step
    assert 1_000_000 in by_step
    assert 2_000_000 in by_step
    # 100k checks PPO health
    assert "approx_kl_max" in by_step[100_000]
    assert by_step[100_000]["approx_kl_max"] == 0.05
    # 1M is warn-only (does not abort)
    assert by_step[1_000_000].get("warn_only", False) is True
    # 2M is the final-success milestone (abort if not met)
    assert by_step[2_000_000].get("warn_only", False) is False


def test_milestone_callback_aborts_on_failure_at_100k():
    """When approx_kl exceeds threshold at 100k, callback returns False to abort."""
    cb = MilestoneCallback()
    cb._metrics_provider = lambda step: {
        "approx_kl": 0.10,         # > 0.05 threshold
        "entropy_loss": -1.0,
        "success_rate_L1": 0.5,
        "success_rate_L2": 0.0,
        "success_rate_L3": 0.0,
        "success_rate_L4": 0.0,
    }
    should_continue = cb._check_milestone(100_000)
    assert should_continue is False


def test_milestone_callback_continues_when_metrics_pass():
    """When metrics pass thresholds, callback returns True (training continues)."""
    cb = MilestoneCallback()
    cb._metrics_provider = lambda step: {
        "approx_kl": 0.02,
        "entropy_loss": -1.5,
        "success_rate_L1": 0.85,
        "success_rate_L2": 0.65,
        "success_rate_L3": 0.5,
        "success_rate_L4": 0.0,
    }
    assert cb._check_milestone(500_000) is True


def test_milestone_callback_warns_only_at_1m_when_below_target():
    """At 1M, even if below targets, return True but log a warning."""
    cb = MilestoneCallback()
    cb._metrics_provider = lambda step: {
        "approx_kl": 0.02,
        "entropy_loss": -1.5,
        "success_rate_L1": 0.50,   # below 0.80 target
        "success_rate_L2": 0.30,
        "success_rate_L3": 0.20,
        "success_rate_L4": 0.0,
    }
    assert cb._check_milestone(1_000_000) is True
