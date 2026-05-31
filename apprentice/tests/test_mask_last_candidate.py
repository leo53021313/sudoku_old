"""Mask fix: a cell with one candidate must not allow eliminating it.

Eliminating a cell's sole candidate would empty the cell — illegal in Sudoku
regardless of the solution (solution-agnostic). This removes the dominant
"bad eliminate" wrong-action mode (agent destroying forced answers).
"""

import numpy as np
from apprentice.env.sudoku_gym_env import SudokuGymEnv

DB = "data/puzzle_pool.db"


def test_cannot_eliminate_last_candidate():
    env = SudokuGymEnv(db_path=DB)
    env.reset(seed=42)
    r, c = next((r, c) for r in range(9) for c in range(9) if env.board[r, c] == 0)
    v = next(iter(env.candidates_cache[r][c]))
    # Force a naked single at (r, c).
    env.candidates_cache[r][c] = {v}
    env.candidate_count_grid[r, c] = 1

    mask = env.action_masks()
    base = r * 81 + c * 9 + (v - 1)
    assert mask[base] == True, "fill of the sole candidate must stay legal"
    assert mask[729 + base] == False, "eliminating the cell's only candidate must be masked"


def test_eliminate_allowed_when_multiple_candidates():
    env = SudokuGymEnv(db_path=DB)
    env.reset(seed=42)
    r, c = next((r, c) for r in range(9) for c in range(9)
                if env.board[r, c] == 0 and len(env.candidates_cache[r][c]) >= 2)
    v = next(iter(env.candidates_cache[r][c]))
    mask = env.action_masks()
    base = r * 81 + c * 9 + (v - 1)
    assert mask[729 + base] == True, "eliminate must remain legal when the cell has >1 candidate"
