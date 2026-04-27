# sb3/tests/test_curriculum_stage4.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.rl.curriculum.callback import CURRICULUM_STAGES, CurriculumCallback


def test_stage4_distribution_is_uniform_to_prevent_l1_forgetting():
    """Stage 4 must give L1 ≥ 25% to prevent catastrophic forgetting."""
    stage4 = CURRICULUM_STAGES[3]
    dist = stage4["dist"]
    assert dist == {1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}, \
        f"Stage 4 should be uniform 25/25/25/25, got {dist}"
    assert dist[1] >= 0.25, "L1 must be ≥ 25% in stage 4"


def test_stage4_mrv_prob_unchanged_at_0_05():
    """Stage 4 mrv_prob is still 0.05 — it controls env teacher rate, not BC."""
    stage4 = CURRICULUM_STAGES[3]
    assert stage4["mrv"] == 0.05


def test_curriculum_default_window_is_200_for_stable_advancement():
    """Default rolling window for advancement decisions widened to 200 episodes."""
    cb = CurriculumCallback()
    assert cb._window == 200
