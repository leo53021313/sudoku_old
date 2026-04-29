from reasoner.curriculum.callback import (
    TechniqueCurriculumCallback,
    STAGE_MAX_TECH,
)


def test_stage_definitions_match_spec():
    """5-stage curriculum aligned with technique tiers."""
    assert STAGE_MAX_TECH[1] == 3   # basic: naked/hidden single
    assert STAGE_MAX_TECH[2] == 7   # pair / pointing / box-line
    assert STAGE_MAX_TECH[3] == 9   # naked triple/quad
    assert STAGE_MAX_TECH[4] == 13  # X-Wing / Swordfish / XY-Wing / XYZ-Wing
    assert STAGE_MAX_TECH[5] is None  # chains / coloring / AIC / T&E + catchall


def test_callback_initial_stage_is_1():
    cb = TechniqueCurriculumCallback(puzzle_labels={}, eval_threshold=0.80)
    assert cb._stage_idx == 0  # 0-indexed → stage 1


def test_record_eval_advances_after_three_consecutive_passes():
    cb = TechniqueCurriculumCallback(puzzle_labels={}, eval_threshold=0.80)
    cb.record_eval(stage=1, success_rate=0.85)
    assert cb._stage_idx == 0
    cb.record_eval(stage=1, success_rate=0.85)
    assert cb._stage_idx == 0
    cb.record_eval(stage=1, success_rate=0.85)
    assert cb._stage_idx == 1  # advanced to stage 2


def test_record_eval_resets_streak_on_failure():
    cb = TechniqueCurriculumCallback(puzzle_labels={}, eval_threshold=0.80)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.50)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.85)
    assert cb._stage_idx == 0


def test_filter_puzzles_for_each_stage():
    labels = {
        "1":  1,   # tech 1 → stage 1
        "2":  2,   # tech 2 → stage 1
        "3":  3,   # tech 3 → stage 1
        "4":  4,   # tech 4 → stage 2
        "5":  7,   # tech 7 → stage 2
        "6":  8,   # tech 8 → stage 3
        "7":  9,   # tech 9 → stage 3
        "8": 10,   # tech 10 → stage 4
        "9": 13,   # tech 13 → stage 4
        "10": 17,  # tech 17 → stage 5
        "11": -1,  # solver failed → stage 5
    }
    cb = TechniqueCurriculumCallback(puzzle_labels=labels, eval_threshold=0.80)
    assert sorted(cb.puzzle_ids_for_stage(1)) == [1, 2, 3]
    assert sorted(cb.puzzle_ids_for_stage(2)) == [4, 5]
    assert sorted(cb.puzzle_ids_for_stage(3)) == [6, 7]
    assert sorted(cb.puzzle_ids_for_stage(4)) == [8, 9]
    assert sorted(cb.puzzle_ids_for_stage(5)) == [10, 11]
