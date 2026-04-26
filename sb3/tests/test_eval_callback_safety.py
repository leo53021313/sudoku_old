# sb3/tests/test_eval_callback_safety.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
import numpy as np


def test_eval_callback_continues_on_predict_error():
    """_on_step must return True (training continues) even if model.predict raises."""
    from app.rl.curriculum.eval_callback import SudokuEvalCallback

    cb = SudokuEvalCallback(
        db_path='../data/puzzle_pool.db',
        eval_freq=1,
        n_episodes=2,
        difficulties=(1,),
        verbose=0,
    )

    # Set up minimal callback state
    cb.num_timesteps = 100
    cb._last_eval = 0
    # Mock logger directly in __dict__ to bypass the property descriptor
    cb.__dict__['logger'] = MagicMock()

    # Mock eval env and model
    mock_env = MagicMock()
    mock_env.reset.return_value = (np.zeros((26, 9, 9), dtype=np.float32), {})
    mock_env.action_masks.return_value = np.ones(729, dtype=bool)

    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("device mismatch")

    cb._eval_env = mock_env
    cb.model = mock_model

    # Before fix: RuntimeError propagates out of _on_step, crashing training
    # After fix: _on_step catches the error, prints warning, returns True
    result = cb._on_step()
    assert result is True, "_on_step must return True even when eval fails"
