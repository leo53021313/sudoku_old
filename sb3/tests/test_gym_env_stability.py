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


def test_obs_uses_board_copy_not_reference(tmp_path):
    """_obs() must snapshot self.board so later mutations don't alter the returned obs.

    Regression guard for shared-memory VecEnv compatibility (e.g. SharedMemoryVecEnv).
    If _obs() ever aliases self.board (rather than copying), a post-_obs() mutation
    of env.board would silently corrupt the previously-returned observation.
    """
    db_path = _make_db(tmp_path)
    env = SudokuGymEnv(db_path=db_path, difficulty=1)

    # Build a minimal valid state without going through reset() (avoids solve()).
    env.board = np.zeros((9, 9), dtype=np.int8)
    env.board[0, 0] = 5
    env.fixed = (env.board != 0)
    env.solution = np.zeros((9, 9), dtype=np.int8)
    env._rebuild_candidates()

    # Build observation snapshot.
    obs = env._obs()

    # Sanity: digit 5 at (0,0) → channel 4 (v=5 → index v-1=4).
    assert obs[4, 0, 0] == 1.0

    # Mutate live board AFTER obs is built. A correctly-snapshotted obs must
    # remain unaffected; an aliased obs would silently flip channel planes.
    env.board[0, 0] = 9

    # Channel 4 (digit 5) at (0,0) should still be 1.0 — proof obs holds an
    # independent snapshot, not a live view of self.board.
    assert obs[4, 0, 0] == 1.0
    # And channel 8 (digit 9) at (0,0) should still be 0.0 — the post-mutation
    # value must NOT have leaked into the returned obs.
    assert obs[8, 0, 0] == 0.0
