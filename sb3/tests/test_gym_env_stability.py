# sb3/tests/test_gym_env_stability.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
import app.rl.envs.sudoku_gym_env as env_mod
from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.data.pool_db import PuzzlePoolDB


def _make_db(tmp_path):
    """Create a minimal DB with one puzzle for testing."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    db.upsert_puzzle(board, level=1)
    return db_path


def test_reset_recursion_guard(tmp_path, monkeypatch):
    """reset() must raise RuntimeError after 10 failed solve attempts, not recurse forever."""
    db_path = _make_db(tmp_path)
    monkeypatch.setattr(env_mod, "solve", lambda b: None)
    env = SudokuGymEnv(db_path=db_path, difficulty=1)
    with pytest.raises(RuntimeError, match="Too many unsolvable"):
        env.reset()
