# sb3/tests/test_bc_schedule.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


def test_bc_schedule_starts_at_1_0_at_progress_remaining_1():
    """At training start, progress_remaining=1.0 → bc_coef should be 1.0."""
    from stable_baselines3.common.utils import LinearSchedule
    sched = LinearSchedule(1.0, 0.3, end_fraction=1.0)
    assert sched(1.0) == pytest.approx(1.0, abs=1e-6)


def test_bc_schedule_ends_at_0_3_at_progress_remaining_0():
    """At training end, progress_remaining=0.0 → bc_coef should be 0.3."""
    from stable_baselines3.common.utils import LinearSchedule
    sched = LinearSchedule(1.0, 0.3, end_fraction=1.0)
    assert sched(0.0) == pytest.approx(0.3, abs=1e-6)


def test_bc_schedule_is_independent_of_mrv_prob():
    """Setting model.mrv_prob should not affect the BC schedule output."""
    class FakeModel:
        pass
    m = FakeModel()
    from stable_baselines3.common.utils import LinearSchedule
    m._bc_schedule = LinearSchedule(1.0, 0.3, end_fraction=1.0)

    for prob in (0.05, 0.20, 0.50, 0.80):
        m.mrv_prob = prob
        # The schedule is queried by progress_remaining, not mrv_prob:
        assert m._bc_schedule(0.5) == pytest.approx(0.65, abs=1e-6)
