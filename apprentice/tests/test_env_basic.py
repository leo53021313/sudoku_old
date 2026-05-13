import numpy as np
import pytest
from pathlib import Path
from apprentice.env.sudoku_gym_env import SudokuGymEnv

_REPO_DB = Path(__file__).resolve().parents[2] / "data" / "puzzle_pool.db"


@pytest.fixture
def db_path():
    return "data/puzzle_pool.db"


def test_action_space_is_1458(db_path):
    """Route II: 729 fill + 729 eliminate."""
    env = SudokuGymEnv(db_path=db_path)
    assert env.action_space.n == 1458


def test_max_wrong_fills_default_is_20(db_path):
    env = SudokuGymEnv(db_path=db_path)
    assert env.max_wrong_fills == 20


def test_no_teacher_info_in_step_info(db_path):
    env = SudokuGymEnv(db_path=db_path)
    obs, _ = env.reset()
    masks = env.action_masks()
    legal = np.where(masks)[0]
    if len(legal) == 0:
        pytest.skip("no legal actions")
    obs2, r, term, trunc, info = env.step(int(legal[0]))
    assert "teacher_action" not in info
    assert "teacher_quality" not in info


def test_step_info_has_action_mode(db_path):
    env = SudokuGymEnv(db_path=db_path)
    obs, _ = env.reset()
    masks = env.action_masks()
    legal = np.where(masks)[0]
    if len(legal) == 0:
        pytest.skip("no legal actions")
    obs2, r, term, trunc, info = env.step(int(legal[0]))
    assert info.get("action_mode") in ("fill", "eliminate")


def test_decode_fill_action():
    mode, r, c, v = SudokuGymEnv._decode(0)
    assert mode == "fill"
    assert (r, c, v) == (0, 0, 1)
    mode, r, c, v = SudokuGymEnv._decode(728)
    assert mode == "fill"
    assert (r, c, v) == (8, 8, 9)


def test_decode_eliminate_action():
    mode, r, c, v = SudokuGymEnv._decode(729)
    assert mode == "eliminate"
    assert (r, c, v) == (0, 0, 1)
    mode, r, c, v = SudokuGymEnv._decode(1457)
    assert mode == "eliminate"
    assert (r, c, v) == (8, 8, 9)


def test_encode_decode_roundtrip():
    for r in range(9):
        for c in range(9):
            for v in range(1, 10):
                for mode in ("fill", "eliminate"):
                    a = SudokuGymEnv.encode(mode, r, c, v)
                    m2, r2, c2, v2 = SudokuGymEnv._decode(a)
                    assert (m2, r2, c2, v2) == (mode, r, c, v)


def test_action_mask_shape_is_1458(db_path):
    env = SudokuGymEnv(db_path=db_path)
    env.reset()
    mask = env.action_masks()
    assert mask.shape == (1458,)


def test_action_mask_fill_and_eliminate_have_same_legal_set(db_path):
    """Both halves should mask the same (r,c,v) set: empty cell + v in candidates."""
    env = SudokuGymEnv(db_path=db_path)
    env.reset()
    mask = env.action_masks()
    fill_half = mask[:729]
    elim_half = mask[729:]
    np.testing.assert_array_equal(fill_half, elim_half)


def test_obs_shape_26_channels():
    """A3: obs should be (26, 9, 9) — 24 base channels + naked-single + hidden-single."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    obs, _ = env.reset(seed=42)
    assert obs.shape == (26, 9, 9), f"expected (26,9,9), got {obs.shape}"
    assert env.observation_space.shape == (26, 9, 9)


def test_obs_ch24_naked_single_flag():
    """Ch 24 marks cells with exactly 1 candidate."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    obs, _ = env.reset(seed=42)
    # For every empty cell with candidate_count == 1, ch 24 must be 1
    for r in range(9):
        for c in range(9):
            if env.board[r, c] == 0 and len(env.candidates_cache[r][c]) == 1:
                assert obs[24, r, c] == 1.0
            else:
                assert obs[24, r, c] == 0.0


def test_obs_ch25_hidden_single_flag():
    """Ch 25 marks cells that are hidden singles in some unit."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    obs, _ = env.reset(seed=42)
    # Sanity: ch 25 is float32, all in {0.0, 1.0}
    assert obs[25].dtype == np.float32
    vals = set(np.unique(obs[25]).tolist())
    assert vals.issubset({0.0, 1.0})


def test_target_empty_default_is_none():
    """When target_empty is None, env behaves like the reasoner baseline."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    assert env.target_empty is None


def test_set_target_empty():
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(8)
    assert env.target_empty == 8

    env.set_target_empty(None)
    assert env.target_empty is None


def test_set_target_empty_rejects_invalid():
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    with pytest.raises(ValueError):
        env.set_target_empty(-1)
    with pytest.raises(ValueError):
        env.set_target_empty(0)


def test_reset_with_target_empty_3():
    """With target_empty=3, only 3 cells should remain empty after reset."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(3)
    obs, _ = env.reset(seed=42)
    n_empty = int(np.count_nonzero(env.board == 0))
    assert n_empty == 3, f"expected 3 empty cells, got {n_empty}"


def test_reset_with_target_empty_5():
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(5)
    obs, _ = env.reset(seed=42)
    n_empty = int(np.count_nonzero(env.board == 0))
    assert n_empty == 5


def test_reset_target_empty_larger_than_puzzle_keeps_puzzle():
    """If target_empty >= puzzle's natural empty count, fill nothing back."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(80)  # larger than any L1 puzzle's empty count
    obs, _ = env.reset(seed=42)
    n_empty = int(np.count_nonzero(env.board == 0))
    # L1 puzzles have ~45-55 empty; with target=80 we should keep all of them
    assert n_empty < 80
    assert n_empty > 30  # sanity: puzzle is not heavily pre-filled


def test_reset_fill_back_cells_match_solution():
    """Cells filled back during fill_back must match the solver's solution."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(5)
    obs, _ = env.reset(seed=42)
    # board cells that were not originally empty OR were filled back from solution
    # should match solution
    for r in range(9):
        for c in range(9):
            if env.board[r, c] != 0:
                assert env.board[r, c] == env.solution[r, c], \
                    f"cell ({r},{c}) board={env.board[r,c]} != solution={env.solution[r,c]}"


def test_reset_no_target_empty_unchanged_behavior():
    """With target_empty=None, reset() behaves like reasoner baseline."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(None)
    obs, _ = env.reset(seed=42)
    n_empty_natural = int(np.count_nonzero(env.board == 0))

    # Re-reset with same seed should give same puzzle
    env.set_target_empty(None)
    obs2, _ = env.reset(seed=42)
    n_empty_natural2 = int(np.count_nonzero(env.board == 0))
    assert n_empty_natural == n_empty_natural2
    assert n_empty_natural > 30  # natural L1 puzzle is reasonably empty


def test_reset_with_target_empty_reproducible():
    """Same seed + same target_empty → same fill_back."""
    env1 = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env1.set_target_empty(5)
    env1.reset(seed=123)
    board1 = env1.board.copy()

    env2 = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env2.set_target_empty(5)
    env2.reset(seed=123)
    board2 = env2.board.copy()

    assert np.array_equal(board1, board2)
