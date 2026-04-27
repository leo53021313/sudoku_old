# sb3/tests/test_reserved_eval_callback.py
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock
import numpy as np


def test_reserved_eval_callback_logs_per_difficulty_rates(tmp_path):
    """Callback runs reserved eval and logs eval/reserved_L1..L4 + overall."""
    # Create a tiny reserved JSON
    reserved_json = tmp_path / "reserved.json"
    reserved_json.write_text(json.dumps({
        "created": "2026-04-27",
        "n_per_difficulty": 1,
        "puzzles": {
            "1": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}],
            "2": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}],
            "3": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}],
            "4": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}],
        },
    }), encoding="utf-8")

    from app.rl.curriculum.reserved_eval_callback import ReservedEvalCallback
    cb = ReservedEvalCallback(
        json_path=str(reserved_json),
        db_path=str(tmp_path / "fake.db"),  # only used if json missing
        eval_freq=1,
        difficulties=(1, 2, 3, 4),
        verbose=0,
    )

    # Stub model to always pick action 0 (always wrong, so eval will fail every puzzle)
    cb.model = MagicMock()
    cb.model.predict = MagicMock(return_value=(np.array([0]), None))
    cb.model.logger = MagicMock()
    cb.model.logger.dir = str(tmp_path)
    cb.num_timesteps = 1

    cb._init_callback()
    cb._on_step()

    # Verify per-difficulty rates were recorded
    recorded = {call.args[0]: call.args[1] for call in cb.model.logger.record.call_args_list}
    assert "eval/reserved_L1" in recorded
    assert "eval/reserved_L2" in recorded
    assert "eval/reserved_L3" in recorded
    assert "eval/reserved_L4" in recorded
    assert "eval/reserved_overall" in recorded
    # All should be 0 because the stubbed model is broken
    for k in ("eval/reserved_L1", "eval/reserved_L2", "eval/reserved_L3", "eval/reserved_L4", "eval/reserved_overall"):
        assert recorded[k] == 0.0, f"{k} = {recorded[k]}, expected 0.0"

    cb._on_training_end()


def test_reserved_eval_callback_does_not_abort(tmp_path):
    """Callback never returns False from _on_step (no abort), even if all puzzles fail."""
    reserved_json = tmp_path / "reserved.json"
    reserved_json.write_text(json.dumps({
        "created": "2026-04-27",
        "n_per_difficulty": 1,
        "puzzles": {"1": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}]},
    }), encoding="utf-8")

    from app.rl.curriculum.reserved_eval_callback import ReservedEvalCallback
    cb = ReservedEvalCallback(
        json_path=str(reserved_json),
        db_path=str(tmp_path / "fake.db"),
        eval_freq=1,
        difficulties=(1,),
        verbose=0,
    )
    cb.model = MagicMock()
    cb.model.predict = MagicMock(return_value=(np.array([0]), None))
    cb.model.logger = MagicMock()
    cb.model.logger.dir = str(tmp_path)
    cb.num_timesteps = 1
    cb._init_callback()

    assert cb._on_step() is True, "Reserved callback must not abort training"
    cb._on_training_end()


def test_reserved_eval_callback_respects_eval_freq(tmp_path):
    """When num_timesteps - _last_eval < eval_freq, callback skips evaluation."""
    reserved_json = tmp_path / "reserved.json"
    reserved_json.write_text(json.dumps({
        "puzzles": {"1": [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}]},
    }), encoding="utf-8")

    from app.rl.curriculum.reserved_eval_callback import ReservedEvalCallback
    cb = ReservedEvalCallback(
        json_path=str(reserved_json),
        db_path=str(tmp_path / "fake.db"),
        eval_freq=50_000,
        difficulties=(1,),
        verbose=0,
    )
    cb.model = MagicMock()
    cb.model.predict = MagicMock(return_value=(np.array([0]), None))
    cb.model.logger = MagicMock()
    cb.num_timesteps = 100  # < eval_freq, should skip
    cb._init_callback()
    cb._on_step()
    assert cb.model.logger.record.call_count == 0, "Should skip when below eval_freq"

    cb._on_training_end()
