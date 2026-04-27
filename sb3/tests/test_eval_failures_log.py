# sb3/tests/test_eval_failures_log.py
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from app.rl.curriculum.eval_callback import _log_failure_record


def test_log_failure_record_writes_one_jsonl_line(tmp_path):
    """_log_failure_record appends exactly one valid JSON line per call."""
    log_path = tmp_path / "eval_failures.jsonl"
    record = {
        "step": 100_000,
        "difficulty": 2,
        "first_wrong_step": 7,
        "model_picked_cell": [3, 5],
        "model_picked_value": 9,
        "correct_value": 4,
        "teacher_quality_at_that_step": 0.75,
    }
    _log_failure_record(str(log_path), record)
    _log_failure_record(str(log_path), record)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    parsed = [json.loads(l) for l in lines]
    assert all(p == record for p in parsed)


def test_log_failure_record_handles_numpy_types(tmp_path):
    """Numpy ints/floats must serialise without TypeError (json default fallback)."""
    log_path = tmp_path / "eval_failures.jsonl"
    record = {
        "step": np.int64(200_000),
        "difficulty": np.int32(3),
        "model_picked_cell": [np.int64(1), np.int64(2)],
        "teacher_quality_at_that_step": np.float32(0.5),
    }
    _log_failure_record(str(log_path), record)
    parsed = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert parsed["step"] == 200_000
    assert parsed["difficulty"] == 3
    assert parsed["model_picked_cell"] == [1, 2]
    assert parsed["teacher_quality_at_that_step"] == pytest.approx(0.5)
