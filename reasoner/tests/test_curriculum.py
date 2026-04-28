from reasoner.curriculum.callback import (
    TechniqueCurriculumCallback,
    STAGE_MAX_TECH,
)


def test_stage_definitions_match_spec():
    assert STAGE_MAX_TECH[1] == 3
    assert STAGE_MAX_TECH[2] == 7
    assert STAGE_MAX_TECH[3] is None  # None means "everything"


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
    assert cb._stage_idx == 1


def test_record_eval_resets_streak_on_failure():
    cb = TechniqueCurriculumCallback(puzzle_labels={}, eval_threshold=0.80)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.50)
    cb.record_eval(stage=1, success_rate=0.85)
    cb.record_eval(stage=1, success_rate=0.85)
    assert cb._stage_idx == 0


def test_filter_puzzles_for_stage_1():
    labels = {
        "1": 1,  # tech 1 → stage 1
        "2": 2,  # tech 2 → stage 1
        "3": 3,  # tech 3 → stage 1
        "4": 4,  # tech 4 → stage 2
        "5": 7,  # tech 7 → stage 2
        "6": -1, # unsolvable → stage 3
    }
    cb = TechniqueCurriculumCallback(puzzle_labels=labels, eval_threshold=0.80)
    stage_1_ids = cb.puzzle_ids_for_stage(1)
    assert sorted(stage_1_ids) == [1, 2, 3]
    stage_2_ids = cb.puzzle_ids_for_stage(2)
    assert sorted(stage_2_ids) == [4, 5]
    stage_3_ids = cb.puzzle_ids_for_stage(3)
    assert sorted(stage_3_ids) == [6]
