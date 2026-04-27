# sb3/tests/test_eval_callback_random.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock
import numpy as np


def test_eval_callback_uses_fetch_random_puzzles_not_env_reset(tmp_path, monkeypatch):
    """When SudokuEvalCallback runs, it must call PuzzlePoolDB.fetch_random_puzzles
    (read-only) and NOT route through env.reset()/fetch_one_puzzle_for_training."""
    from app.rl.curriculum.eval_callback import SudokuEvalCallback
    from app.rl.envs.sudoku_gym_env import SudokuGymEnv
    from app.data.pool_db import PuzzlePoolDB

    cb = SudokuEvalCallback(
        db_path=str(tmp_path / "fake.db"),
        eval_freq=1,
        n_episodes=2,
        difficulties=(1,),
        verbose=0,
    )

    # Track whether fetch_random_puzzles is called
    rand_calls = []
    one_calls = []

    def stub_random(self, level, n):
        rand_calls.append((level, n))
        # Return a tiny solvable-ish board (all 0 except one cell) — solver will
        # fill the rest. Use a known minimal puzzle string that solves uniquely.
        return [{"puzzle": "530070000600195000098000060800060003400803001700020006060000280000419005000080079"}] * n

    def stub_one(self, *a, **kw):
        one_calls.append((a, kw))
        return None

    monkeypatch.setattr(PuzzlePoolDB, "fetch_random_puzzles", stub_random)
    monkeypatch.setattr(PuzzlePoolDB, "fetch_one_puzzle_for_training", stub_one)

    # Stub model to always pick action 0 (will be masked in env, but we just need
    # the loop to terminate quickly via max_wrong_fills)
    cb.model = MagicMock()
    cb.model.predict = MagicMock(
        return_value=(np.array([0]), None)
    )
    cb.model.logger.dir = str(tmp_path)
    cb.num_timesteps = 1
    cb._eval_env = SudokuGymEnv(db_path=str(tmp_path / "fake.db"))

    # Run one eval cycle
    cb._on_step()

    assert len(rand_calls) >= 1, (
        f"Eval callback must call fetch_random_puzzles; got 0 calls"
    )
    assert len(one_calls) == 0, (
        f"Eval callback must NOT call fetch_one_puzzle_for_training; got {len(one_calls)} calls"
    )

    cb._eval_env.close()
