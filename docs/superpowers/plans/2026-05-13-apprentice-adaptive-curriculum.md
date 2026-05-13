# Apprentice — Reasoner + Adaptive Curriculum Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `apprentice/` as a sibling of frozen `reasoner/`, applying 7 design changes (A3 obs flags, B1 adaptive reverse curriculum, A5 dynamic max_steps, D1 policy hidden layer, E2 dynamic max_wrong, C2 ent_coef, E1 cold-start) per the design spec.

**Architecture:** New `apprentice/` Python package copied from `reasoner/` with import paths rewritten. Env gains `target_empty` attribute driving `fill_back` logic in `reset()`. New `CurriculumController` class manages `target_empty` via sweet-spot formula with stagnation detection. A new SB3 `BaseCallback` syncs controller decisions to all vec_env workers and writes TB metrics.

**Tech Stack:** Python 3.11+, stable-baselines3 (+ sb3-contrib), gymnasium, PyTorch, NumPy, pytest. Project uses POSIX path style in code (cross-platform via `pathlib`). Tests with pytest, run from repo root.

**Spec:** [docs/superpowers/specs/2026-05-13-apprentice-adaptive-curriculum-design.md](../specs/2026-05-13-apprentice-adaptive-curriculum-design.md)

---

## File Structure

```
apprentice/
├── __init__.py                            ← copy from reasoner/__init__.py
├── README.md                              ← NEW (Task 17)
├── configs/
│   └── curriculum.json                    ← NEW (Task 15)
├── data/
│   └── eval_puzzles.json                  ← copy unchanged
├── data_pkg/                              ← copy unchanged (imports rewritten)
│   ├── __init__.py
│   └── pool_db.py
├── env/
│   ├── __init__.py
│   ├── sudoku_gym_env.py                  ← MODIFY (A3, B1, A5, E2)
│   ├── reward_computer.py                 ← copy (import rewrite only)
│   └── obs_helpers.py                     ← NEW (Task 5)
├── eval/
│   ├── __init__.py
│   ├── eval_callback.py                   ← copy (imports + ckpt name pattern)
│   ├── puzzle_set.py                      ← copy (import rewrite only)
│   └── reserved_eval_callback.py          ← copy (import rewrite only)
├── model/
│   ├── __init__.py
│   └── features_extractor.py              ← copy unchanged
├── models/                                ← empty dir for ckpts
├── runs/                                  ← empty dir for TB logs
├── solver/                                ← copy whole tree (import rewrite only)
├── solver_ext/                            ← copy whole tree
├── tests/
│   ├── __init__.py
│   ├── test_candidate_engine.py           ← copy (import rewrite only)
│   ├── test_env_basic.py                  ← copy (import rewrite only)
│   ├── test_human_solver.py               ← copy (import rewrite only)
│   ├── test_imports.py                    ← copy (import rewrite only)
│   ├── test_label_puzzles.py              ← copy (import rewrite only)
│   ├── test_ppo_no_bc.py                  ← copy (import rewrite only)
│   ├── test_reward_computer.py            ← copy (import rewrite only)
│   ├── test_obs_helpers.py                ← NEW (Task 5)
│   ├── test_curriculum_controller.py      ← NEW (Tasks 11, 12, 13)
│   ├── test_curriculum_callback.py        ← NEW (Task 14)
│   └── test_techniques/                   ← copy (import rewrite only)
└── train/
    ├── __init__.py
    ├── ppo.py                             ← copy unchanged
    ├── train.py                           ← MODIFY (D1, C2, E1, integration)
    ├── curriculum_controller.py           ← NEW (Tasks 11-13)
    └── curriculum_callback.py             ← NEW (Task 14)
```

`reasoner/` stays untouched. `data/puzzle_pool.db` at repo root is shared (read-only for training).

---

## Task 1: Bootstrap `apprentice/` Folder

**Files:**
- Create: `apprentice/` directory tree (mirroring `reasoner/`)
- Copy all `.py` files except `__pycache__/`, `models/`, `runs/`
- Rewrite imports `reasoner.*` → `apprentice.*` everywhere
- Update `_CKPT_PATTERN`, `MODEL_NAME`, `TB_LOG_NAME` literals in `train.py`

- [ ] **Step 1: Copy folder structure (excluding caches and runtime dirs)**

Run from repo root `c:/Users/student/Desktop/sudoku_old`:

```bash
# PowerShell (preferred on Windows):
Copy-Item -Recurse -Path reasoner -Destination apprentice
Remove-Item -Recurse -Force apprentice/__pycache__ -ErrorAction SilentlyContinue
Get-ChildItem -Path apprentice -Recurse -Filter __pycache__ -Directory | Remove-Item -Recurse -Force
Remove-Item -Recurse -Force apprentice/models -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force apprentice/runs -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force apprentice/models | Out-Null
New-Item -ItemType Directory -Force apprentice/runs | Out-Null
New-Item -ItemType Directory -Force apprentice/configs | Out-Null
```

Or bash (Git Bash or WSL):

```bash
cp -r reasoner apprentice
find apprentice -name __pycache__ -type d -exec rm -rf {} +
rm -rf apprentice/models apprentice/runs
mkdir -p apprentice/models apprentice/runs apprentice/configs
```

Verify: `ls apprentice` should show `__init__.py data data_pkg env eval model models runs solver solver_ext tests train configs` (no `__pycache__`).

- [ ] **Step 2: Rewrite internal imports `reasoner.*` → `apprentice.*` across all .py files**

Use a sed-style replacement. On Windows PowerShell:

```powershell
Get-ChildItem -Path apprentice -Recurse -Filter *.py | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace 'from reasoner\.', 'from apprentice.' -replace 'import reasoner\.', 'import apprentice.' -replace '\breasoner\.', 'apprentice.' | Set-Content $_.FullName -NoNewline
}
```

Or bash (much simpler):

```bash
find apprentice -name '*.py' -exec sed -i 's/from reasoner\./from apprentice./g; s/import reasoner\./import apprentice./g; s/\breasoner\./apprentice./g' {} +
```

Verify no `reasoner.` strings remain in apprentice/:

```bash
grep -rn "reasoner\." apprentice/ --include='*.py' || echo "OK: no reasoner.* references remain"
```

Expected: prints `OK: no reasoner.* references remain` (the `|| echo` triggers only on no matches).

- [ ] **Step 3: Rewrite `train.py` literals — ckpt pattern, model name, TB log name, path roots**

Open `apprentice/train/train.py`. Find and replace these exact strings:

Replace `reasoner_ckpt_` with `apprentice_ckpt_` (in `_CKPT_PATTERN` regex):
```python
# OLD: _CKPT_PATTERN = re.compile(r"reasoner_ckpt_(\d+)_steps\.zip$")
# NEW: _CKPT_PATTERN = re.compile(r"apprentice_ckpt_(\d+)_steps\.zip$")
```

Replace `"reasoner_latest"` with `"apprentice_latest"` (in `MODEL_NAME`):
```python
# OLD: MODEL_NAME  = "reasoner_latest"
# NEW: MODEL_NAME  = "apprentice_latest"
```

Replace `"reasoner"` with `"apprentice"` in `TB_LOG_NAME`:
```python
# OLD: TB_LOG_NAME = "reasoner"
# NEW: TB_LOG_NAME = "apprentice"
```

Update path roots inside `train.py`:
```python
# OLD: EVAL_PATH = str(_REPO_ROOT / "reasoner" / "data" / "eval_puzzles.json")
# OLD: MODEL_DIR = str(_REPO_ROOT / "reasoner" / "models")
# OLD: LOG_DIR   = str(_REPO_ROOT / "reasoner" / "runs")
# NEW:
EVAL_PATH = str(_REPO_ROOT / "apprentice" / "data" / "eval_puzzles.json")
MODEL_DIR = str(_REPO_ROOT / "apprentice" / "models")
LOG_DIR   = str(_REPO_ROOT / "apprentice" / "runs")
```

Also update the docstring at top of `train.py` to say "apprentice" instead of "reasoner".

Replace the `name_prefix` arg passed to `CheckpointWithSidecars`:
```python
# OLD: name_prefix="reasoner_ckpt",
# NEW: name_prefix="apprentice_ckpt",
```

- [ ] **Step 4: Verify imports resolve**

Run from repo root:

```bash
python -c "from apprentice.env.sudoku_gym_env import SudokuGymEnv; print('OK', SudokuGymEnv.N_CHANNELS)"
```

Expected output: `OK 24`

Run the copied test suite to confirm everything imports:

```bash
python -m pytest apprentice/tests/test_imports.py -v
```

Expected: PASS for all imports.

- [ ] **Step 5: Commit**

```bash
git add apprentice/
git commit -m "feat(apprentice): bootstrap from reasoner/ baseline

Copy reasoner/ → apprentice/ with import paths rewritten
(reasoner.* → apprentice.*). Update train.py constants:
MODEL_NAME, TB_LOG_NAME, ckpt pattern, path roots.

reasoner/ remains frozen as baseline.
No behavioral changes yet."
```

---

## Task 2: Baseline Smoke Test (no changes yet)

**Files:**
- Test: ad-hoc verification only — no test file to write

Confirms the copy is clean: `apprentice` can launch a training loop identical to `reasoner` (cold-start, no curriculum, no obs flags).

- [ ] **Step 1: Run a 2k-step smoke training to verify nothing is broken from the copy**

```bash
python -m apprentice.train.train --timesteps 2000 --n-envs 2 --verbose 1
```

Expected: training runs to completion. TB output goes to `apprentice/runs/apprentice_1/`. A checkpoint `apprentice_latest.zip` is saved.

The output should print `[apprentice] Policy parameters: ~2,800,000` (close to reasoner's count). The exact number depends on torch/sb3 versions; just sanity check it's in the millions.

- [ ] **Step 2: Verify TB event file exists and shows expected tags**

```bash
ls apprentice/runs/
ls apprentice/runs/apprentice_1/
```

Expected: directory exists with `events.out.tfevents.*` file inside.

- [ ] **Step 3: Run the test suite for sanity**

```bash
python -m pytest apprentice/tests/ -x --tb=short
```

Expected: All tests pass (they're copied from reasoner/, same code, just with renamed imports).

- [ ] **Step 4: Commit (no code changes; this is a checkpoint)**

If everything passed, no commit needed (no source changes since Task 1). Skip to Task 3.

If something failed, fix the copy/import issue, then commit the fix:

```bash
git add apprentice/
git commit -m "fix(apprentice): bootstrap fixup for [issue description]"
```

---

## Task 3: D1 — Policy Hidden Layer in train.py

**Files:**
- Modify: `apprentice/train/train.py` around line 198-203 (the `policy_kwargs` dict in `main()`)

- [ ] **Step 1: Update `policy_kwargs.net_arch`**

Open `apprentice/train/train.py`. Find:

```python
    policy_kwargs = dict(
        features_extractor_class=SudokuFeaturesExtractor,
        features_extractor_kwargs={"features_dim": 192},
        net_arch={"pi": [], "vf": [128]},
    )
```

Replace with:

```python
    policy_kwargs = dict(
        features_extractor_class=SudokuFeaturesExtractor,
        features_extractor_kwargs={"features_dim": 192},
        net_arch={"pi": [128], "vf": [128, 128]},
    )
```

- [ ] **Step 2: Smoke-test that the new policy arch loads**

```bash
python -m apprentice.train.train --timesteps 1000 --n-envs 2 --verbose 1
```

Expected: completes without error. Policy parameter count should INCREASE by ~370K relative to Task 2's count (an extra Linear(1650, 128) for policy + Linear(128, 128) for value).

- [ ] **Step 3: Commit**

```bash
git add apprentice/train/train.py
git commit -m "feat(apprentice): D1 — add policy hidden layer

net_arch from {pi: [], vf: [128]} to {pi: [128], vf: [128, 128]}.
Policy now has explicit 128-unit hidden layer (was direct features → 1458 logits).
Adds ~370K parameters, ~10% of total."
```

---

## Task 4: C2 — Entropy Coefficient

**Files:**
- Modify: `apprentice/train/train.py` around line 220 (the `SudokuMaskablePPO(...)` constructor)

- [ ] **Step 1: Update `ent_coef`**

Open `apprentice/train/train.py`. Find:

```python
            ent_coef=0.02,
```

Replace with:

```python
            ent_coef=0.05,
```

- [ ] **Step 2: Smoke test**

```bash
python -m apprentice.train.train --timesteps 1000 --n-envs 2 --verbose 1
```

Expected: completes without error. TB `train/entropy_loss` should be slightly more negative (more entropy reward).

- [ ] **Step 3: Commit**

```bash
git add apprentice/train/train.py
git commit -m "feat(apprentice): C2 — entropy coefficient 0.02 → 0.05

Increase exploration heat for sparse-reward curriculum training.
0.02 was too cold for curriculum stage transitions where policy
needs to remain flexible."
```

---

## Task 5: A3 Part 1 — `obs_helpers.py` (hidden-single grid computation)

**Files:**
- Create: `apprentice/env/obs_helpers.py`
- Test: `apprentice/tests/test_obs_helpers.py`

- [ ] **Step 1: Write the failing test**

Create `apprentice/tests/test_obs_helpers.py`:

```python
"""Tests for env/obs_helpers.py."""

import numpy as np
import pytest

from apprentice.env.obs_helpers import (
    compute_naked_single_grid,
    compute_hidden_single_grid,
)


def _empty_candidates():
    """9x9 list of sets — initial: every empty cell has {1..9}."""
    return [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]


def _empty_board():
    return np.zeros((9, 9), dtype=np.int8)


def test_compute_naked_single_grid_no_naked():
    board = _empty_board()
    candidates = _empty_candidates()
    grid = compute_naked_single_grid(board, candidates)
    assert grid.shape == (9, 9)
    assert grid.dtype == np.float32
    assert grid.sum() == 0.0


def test_compute_naked_single_grid_one_naked():
    board = _empty_board()
    candidates = _empty_candidates()
    # Cell (3,4) has only {7} as candidate → naked single
    candidates[3][4] = {7}
    grid = compute_naked_single_grid(board, candidates)
    assert grid[3, 4] == 1.0
    # All other cells: 0.0
    assert grid.sum() == 1.0


def test_compute_naked_single_grid_filled_cell_not_marked():
    board = _empty_board()
    candidates = _empty_candidates()
    # Board cell (1,1) is filled with 5
    board[1, 1] = 5
    candidates[1][1] = set()  # filled cells have empty candidate set
    grid = compute_naked_single_grid(board, candidates)
    # Should not mark a filled cell even though its candidate count is "1"
    assert grid[1, 1] == 0.0


def test_compute_hidden_single_grid_row():
    board = _empty_board()
    candidates = _empty_candidates()
    # Make digit 5 only possible in cell (0, 3) within row 0:
    # Remove 5 from candidates of all other cells in row 0
    for c in range(9):
        if c != 3:
            candidates[0][c].discard(5)
    grid = compute_hidden_single_grid(board, candidates)
    assert grid.shape == (9, 9)
    assert grid.dtype == np.float32
    assert grid[0, 3] == 1.0


def test_compute_hidden_single_grid_col():
    board = _empty_board()
    candidates = _empty_candidates()
    # Make digit 7 only possible in cell (5, 8) within col 8:
    for r in range(9):
        if r != 5:
            candidates[r][8].discard(7)
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[5, 8] == 1.0


def test_compute_hidden_single_grid_box():
    board = _empty_board()
    candidates = _empty_candidates()
    # Box (0,0) to (2,2) — make 3 only possible in (1,1)
    for r in range(3):
        for c in range(3):
            if not (r == 1 and c == 1):
                candidates[r][c].discard(3)
    # ALSO remove 3 from row 1 elsewhere and col 1 elsewhere so it's hidden
    # *only* by the box constraint... but the function should still flag it.
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[1, 1] == 1.0


def test_compute_hidden_single_grid_empty_no_hidden():
    board = _empty_board()
    candidates = _empty_candidates()  # every cell has {1..9}, no hidden singles
    grid = compute_hidden_single_grid(board, candidates)
    assert grid.sum() == 0.0


def test_compute_hidden_single_grid_filled_cells_not_marked():
    board = _empty_board()
    candidates = _empty_candidates()
    board[2, 2] = 9
    candidates[2][2] = set()
    # Even if the algorithm theoretically thinks (2,2) is hidden-single
    # for some digit (shouldn't, since it's empty candidates), it must not mark filled cells
    grid = compute_hidden_single_grid(board, candidates)
    assert grid[2, 2] == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest apprentice/tests/test_obs_helpers.py -v
```

Expected: `ModuleNotFoundError: No module named 'apprentice.env.obs_helpers'`

- [ ] **Step 3: Implement `obs_helpers.py`**

Create `apprentice/env/obs_helpers.py`:

```python
"""Helpers for computing obs flag channels (naked-single, hidden-single).

These channels are added to the observation tensor in apprentice's
SudokuGymEnv (A3 change vs reasoner's 24-channel obs).
"""

from __future__ import annotations

import numpy as np


def compute_naked_single_grid(
    board: np.ndarray,
    candidates: list[list[set[int]]],
) -> np.ndarray:
    """Return a (9,9) float32 grid where cell (r,c) is 1.0 iff:
      - board[r,c] == 0 (cell is empty), AND
      - len(candidates[r][c]) == 1 (only one possible value).
    """
    grid = np.zeros((9, 9), dtype=np.float32)
    for r in range(9):
        for c in range(9):
            if board[r, c] != 0:
                continue
            if len(candidates[r][c]) == 1:
                grid[r, c] = 1.0
    return grid


def compute_hidden_single_grid(
    board: np.ndarray,
    candidates: list[list[set[int]]],
) -> np.ndarray:
    """Return a (9,9) float32 grid where cell (r,c) is 1.0 iff:
      - board[r,c] == 0, AND
      - there exists some digit v in candidates[r][c] such that within at
        least one unit (the row r, the column c, or the box containing (r,c)),
        no OTHER empty cell has v as a candidate.

    Cost: O(9 * 27) = O(243) lookups per call. Sub-millisecond.
    """
    grid = np.zeros((9, 9), dtype=np.float32)

    # Build a fast view: for each (unit_type, unit_idx, digit) → list of cells
    # We'll mark cells lazily as we discover hidden singles.
    marked = np.zeros((9, 9), dtype=bool)

    # Rows
    for r in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for c in range(9)
                if board[r, c] == 0 and d in candidates[r][c]
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                marked[rr, cc] = True

    # Columns
    for c in range(9):
        for d in range(1, 10):
            cells_with_d = [
                (r, c) for r in range(9)
                if board[r, c] == 0 and d in candidates[r][c]
            ]
            if len(cells_with_d) == 1:
                rr, cc = cells_with_d[0]
                marked[rr, cc] = True

    # Boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            for d in range(1, 10):
                cells_with_d = [
                    (r, c)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                    if board[r, c] == 0 and d in candidates[r][c]
                ]
                if len(cells_with_d) == 1:
                    rr, cc = cells_with_d[0]
                    marked[rr, cc] = True

    grid[marked] = 1.0
    return grid
```

- [ ] **Step 4: Run test to verify all pass**

```bash
python -m pytest apprentice/tests/test_obs_helpers.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/env/obs_helpers.py apprentice/tests/test_obs_helpers.py
git commit -m "feat(apprentice): A3 part 1 — obs_helpers.compute_*_grid

Add compute_naked_single_grid and compute_hidden_single_grid.
Each returns (9,9) float32 grid where empty cells satisfying the
technique are marked 1.0. Filled cells are never marked.

Hidden-single scans all 27 units (9 row + 9 col + 9 box) × 9 digits.
Sub-millisecond cost per call."
```

---

## Task 6: A3 Part 2 — Env Adds 2 Obs Channels (24 → 26)

**Files:**
- Modify: `apprentice/env/sudoku_gym_env.py`
- Test: `apprentice/tests/test_env_basic.py` (extend with channel-count assertions)

- [ ] **Step 1: Write the failing test (extension to test_env_basic.py)**

Open `apprentice/tests/test_env_basic.py`. Add at the end of the file:

```python
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
```

Make sure these imports are at the top of `test_env_basic.py` (they should be from the copy):

```python
import numpy as np
from pathlib import Path
from apprentice.env.sudoku_gym_env import SudokuGymEnv

_REPO_DB = Path(__file__).resolve().parents[2] / "data" / "puzzle_pool.db"
```

If `_REPO_DB` is not already defined in the test file (it may be defined differently in the copied test), use the existing pattern from the copy.

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_env_basic.py::test_obs_shape_26_channels -v
```

Expected: FAIL (obs is still (24, 9, 9))

- [ ] **Step 3: Update env to produce 26-channel obs**

Open `apprentice/env/sudoku_gym_env.py`. Make the following changes:

(a) Add the import at the top (after existing imports):

```python
from apprentice.env.obs_helpers import (
    compute_naked_single_grid,
    compute_hidden_single_grid,
)
```

(b) Change `N_CHANNELS`:

```python
# OLD: N_CHANNELS = 24  # removed naked-single / hidden-single shortcut flags
# NEW:
N_CHANNELS = 26  # 24 base + naked-single flag (ch 24) + hidden-single flag (ch 25)
```

(c) Replace the end of `_obs()` method. Find the existing comment:

```python
        # ch 24, 25 REMOVED — no naked-single / hidden-single flags

        return obs
```

Replace with:

```python
        # ch 24: naked-single flag (1.0 where empty cell has exactly 1 candidate)
        obs[24] = compute_naked_single_grid(self.board, self.candidates_cache)

        # ch 25: hidden-single flag
        obs[25] = compute_hidden_single_grid(self.board, self.candidates_cache)

        return obs
```

- [ ] **Step 4: Run obs tests to verify they pass**

```bash
python -m pytest apprentice/tests/test_env_basic.py -v
```

Expected: All new tests (test_obs_shape_26_channels, test_obs_ch24_naked_single_flag, test_obs_ch25_hidden_single_flag) PASS. Existing tests also PASS.

- [ ] **Step 5: Smoke-test full training launch with new obs**

```bash
python -m apprentice.train.train --timesteps 1000 --n-envs 2 --verbose 1
```

Expected: training completes. Policy now has `Linear(in_channels=26, 128)` in the first layer of features extractor.

- [ ] **Step 6: Commit**

```bash
git add apprentice/env/sudoku_gym_env.py apprentice/tests/test_env_basic.py
git commit -m "feat(apprentice): A3 part 2 — obs gains naked/hidden single flags

N_CHANNELS 24 → 26.
Ch 24: 1.0 where empty cell has exactly 1 candidate (naked single).
Ch 25: 1.0 where empty cell is hidden single in row/col/box.

Features extractor first Linear adapts automatically from observation_space.shape[0].
Tests cover shape, ch 24 correctness, ch 25 correctness."
```

---

## Task 7: B1 Part 1 — Env `target_empty` Attribute + `set_target_empty()`

**Files:**
- Modify: `apprentice/env/sudoku_gym_env.py`
- Test: `apprentice/tests/test_env_basic.py`

- [ ] **Step 1: Write the failing test**

Append to `apprentice/tests/test_env_basic.py`:

```python
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
```

Also add to the imports if missing: `import pytest`

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest apprentice/tests/test_env_basic.py::test_target_empty_default_is_none apprentice/tests/test_env_basic.py::test_set_target_empty apprentice/tests/test_env_basic.py::test_set_target_empty_rejects_invalid -v
```

Expected: FAIL with `AttributeError: 'SudokuGymEnv' object has no attribute 'target_empty'`

- [ ] **Step 3: Add attribute and setter**

Open `apprentice/env/sudoku_gym_env.py`.

Inside `__init__()`, after the existing `self.wrong_count = 0` etc., add:

```python
        # Curriculum control: when set, reset() will fill back cells from
        # solution until only `target_empty` cells remain. None = use puzzle as-is.
        self.target_empty: int | None = None
```

Add a new method after `set_difficulty_distribution()`:

```python
    def set_target_empty(self, target: int | None) -> None:
        """Set curriculum difficulty: only `target` empty cells will remain.

        None = disable curriculum (use puzzle's natural empty count).
        Must be positive integer if not None.
        """
        if target is not None:
            if not isinstance(target, (int, np.integer)) or target <= 0:
                raise ValueError(f"target_empty must be positive int or None, got {target!r}")
        self.target_empty = None if target is None else int(target)
```

- [ ] **Step 4: Run test to verify pass**

```bash
python -m pytest apprentice/tests/test_env_basic.py::test_target_empty_default_is_none apprentice/tests/test_env_basic.py::test_set_target_empty apprentice/tests/test_env_basic.py::test_set_target_empty_rejects_invalid -v
```

Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/env/sudoku_gym_env.py apprentice/tests/test_env_basic.py
git commit -m "feat(apprentice): B1 part 1 — env target_empty attribute + setter

Adds target_empty attribute and set_target_empty() method.
target_empty=None preserves baseline behavior.
set_target_empty rejects invalid (non-positive) values."
```

---

## Task 8: B1 Part 2 — Env `reset()` fill_back Logic

**Files:**
- Modify: `apprentice/env/sudoku_gym_env.py`
- Test: `apprentice/tests/test_env_basic.py`

- [ ] **Step 1: Write the failing test**

Append to `apprentice/tests/test_env_basic.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_env_basic.py::test_reset_with_target_empty_3 -v
```

Expected: FAIL (target_empty has no effect on reset yet)

- [ ] **Step 3: Implement fill_back in `reset()`**

Open `apprentice/env/sudoku_gym_env.py`. Find this block in `reset()` (the DB branch — after `self.solution = sol`):

```python
        sol = solve(board)
        if sol is None:
            if _retries >= 10:
                raise RuntimeError("Too many unsolvable puzzles in DB")
            return self.reset(seed=seed, options=options, _retries=_retries + 1)
        self.solution = sol

        return self._obs(), {}
```

Replace with:

```python
        sol = solve(board)
        if sol is None:
            if _retries >= 10:
                raise RuntimeError("Too many unsolvable puzzles in DB")
            return self.reset(seed=seed, options=options, _retries=_retries + 1)
        self.solution = sol

        # B1: optional fill_back from solution to enforce target_empty
        if self.target_empty is not None:
            self._apply_fill_back(self.target_empty)

        return self._obs(), {}
```

Then add the new method `_apply_fill_back` (place near other private methods, e.g. before `_rebuild_candidates`):

```python
    def _apply_fill_back(self, target_empty: int) -> None:
        """Fill cells from self.solution until only target_empty cells remain empty.

        Uses self.np_random (gymnasium PRNG, seed-controllable via reset(seed=)).
        """
        empty_cells = [
            (r, c) for r in range(9) for c in range(9) if self.board[r, c] == 0
        ]
        n_current_empty = len(empty_cells)
        fill_back = max(0, n_current_empty - target_empty)
        if fill_back == 0:
            return

        # Shuffle the empty cells with gymnasium PRNG, take the first fill_back
        # (np_random.permutation gives same result for same seed)
        order = self.np_random.permutation(n_current_empty)
        to_fill = [empty_cells[i] for i in order[:fill_back]]

        for r, c in to_fill:
            v = int(self.solution[r, c])
            self.board[r, c] = v
            # `fixed` mask not updated — fill_back cells are considered "given"
            # by the env but we don't mark them as `fixed` since they're not
            # part of the original puzzle. This is fine for obs ch 18.

        # Rebuild candidate cache after the fill_backs change the constraint graph.
        self._rebuild_candidates()
```

Also update `reset()`'s `options` branch (for direct-board callers) to honor target_empty if set: NO, on second thought, the options branch is used for eval callbacks which pass an exact board; they should NOT be modified by target_empty. Leave that branch untouched.

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_env_basic.py -v
```

Expected: All tests PASS (including the 5 new fill_back tests).

- [ ] **Step 5: Smoke-test that a stage-0 training (target_empty=3) actually runs**

Add a quick manual check:

```bash
python -c "
from apprentice.env.sudoku_gym_env import SudokuGymEnv
env = SudokuGymEnv(db_path='data/puzzle_pool.db', difficulty=1)
env.set_target_empty(3)
obs, _ = env.reset(seed=0)
import numpy as np
print('empty cells:', np.count_nonzero(env.board == 0))
print('obs shape:', obs.shape)
"
```

Expected:
```
empty cells: 3
obs shape: (26, 9, 9)
```

- [ ] **Step 6: Commit**

```bash
git add apprentice/env/sudoku_gym_env.py apprentice/tests/test_env_basic.py
git commit -m "feat(apprentice): B1 part 2 — env reset fill_back from solution

When target_empty is set, reset() fills cells from solution to leave
exactly target_empty empty cells. Uses self.np_random for reproducibility.

The options-branch reset (with explicit board) is untouched — that path
is for eval callbacks which need exact boards."
```

---

## Task 9: A5 + E2 — Dynamic `max_steps` and `max_wrong`

**Files:**
- Modify: `apprentice/env/sudoku_gym_env.py`
- Test: `apprentice/tests/test_env_basic.py`

- [ ] **Step 1: Write the failing test**

Append to `apprentice/tests/test_env_basic.py`:

```python
def test_max_steps_dynamic_when_target_empty_set():
    """A5: max_steps = max(60, target_empty * 8)."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(3)
    env.reset(seed=42)
    assert env.max_steps == 60   # max(60, 24)

    env.set_target_empty(12)
    env.reset(seed=42)
    assert env.max_steps == 96   # max(60, 96)

    env.set_target_empty(50)
    env.reset(seed=42)
    assert env.max_steps == 400   # max(60, 400)


def test_max_wrong_dynamic_when_target_empty_set():
    """E2: max_wrong = max(20, target_empty * 1.2)."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1)
    env.set_target_empty(3)
    env.reset(seed=42)
    assert env.max_wrong_fills == 20  # max(20, 3.6)

    env.set_target_empty(18)
    env.reset(seed=42)
    assert env.max_wrong_fills == 22  # max(20, 21.6) → 22 after int

    env.set_target_empty(50)
    env.reset(seed=42)
    assert env.max_wrong_fills == 60  # max(20, 60)


def test_max_steps_static_when_target_empty_none():
    """When target_empty is None, max_steps stays as constructor default."""
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1, max_steps=222)
    env.set_target_empty(None)
    env.reset(seed=42)
    assert env.max_steps == 222


def test_max_wrong_static_when_target_empty_none():
    env = SudokuGymEnv(db_path=str(_REPO_DB), difficulty=1, max_wrong_fills=33)
    env.set_target_empty(None)
    env.reset(seed=42)
    assert env.max_wrong_fills == 33
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_env_basic.py::test_max_steps_dynamic_when_target_empty_set -v
```

Expected: FAIL (max_steps stays at constructor default regardless of target_empty)

- [ ] **Step 3: Implement dynamic max_steps and max_wrong**

Open `apprentice/env/sudoku_gym_env.py`. In `__init__`, save the constructor defaults so we can restore them when target_empty is None:

After `self.max_wrong_fills = max_wrong_fills` and `self.max_steps = max_steps`, add:

```python
        # Save constructor defaults for "target_empty=None" mode
        self._max_steps_static = max_steps
        self._max_wrong_static = max_wrong_fills
```

Now find the `reset()` `_apply_fill_back` call site (just before `return self._obs(), {}` in the DB branch). Replace the curriculum block:

```python
        # B1: optional fill_back from solution to enforce target_empty
        if self.target_empty is not None:
            self._apply_fill_back(self.target_empty)
```

with:

```python
        # B1: optional fill_back from solution to enforce target_empty
        if self.target_empty is not None:
            self._apply_fill_back(self.target_empty)

        # A5 + E2: dynamic max_steps / max_wrong driven by target_empty (if set)
        self._update_dynamic_limits()
```

Add the new method (place near `_apply_fill_back`):

```python
    def _update_dynamic_limits(self) -> None:
        """A5+E2: set max_steps and max_wrong_fills based on target_empty.

        If target_empty is None, restore constructor defaults.
        Formula:
          max_steps = max(60, target_empty * 8)
          max_wrong = max(20, int(target_empty * 1.2))
        """
        if self.target_empty is None:
            self.max_steps = self._max_steps_static
            self.max_wrong_fills = self._max_wrong_static
            return

        self.max_steps = max(60, int(self.target_empty * 8))
        self.max_wrong_fills = max(20, int(self.target_empty * 1.2))
```

Also call `_update_dynamic_limits()` from the `options` branch of `reset()` (so eval-with-explicit-board respects the current limits too). After:

```python
        if options is not None and "board" in options:
            ...
            self._rebuild_candidates()
            return self._obs(), {}
```

modify to:

```python
        if options is not None and "board" in options:
            ...
            self._rebuild_candidates()
            self._update_dynamic_limits()
            return self._obs(), {}
```

(Replace `...` with the existing code in that branch — don't actually delete it.)

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_env_basic.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/env/sudoku_gym_env.py apprentice/tests/test_env_basic.py
git commit -m "feat(apprentice): A5+E2 — dynamic max_steps and max_wrong_fills

Formulas (when target_empty is set):
  max_steps  = max(60, target_empty * 8)
  max_wrong  = max(20, int(target_empty * 1.2))

When target_empty is None, falls back to constructor defaults.
Both DB-branch reset and options-branch reset call _update_dynamic_limits."
```

---

## Task 10: B1 Part 3 — `CurriculumController` Class (sweet-spot update logic)

**Files:**
- Create: `apprentice/train/curriculum_controller.py`
- Test: `apprentice/tests/test_curriculum_controller.py`

- [ ] **Step 1: Write the failing test**

Create `apprentice/tests/test_curriculum_controller.py`:

```python
"""Tests for CurriculumController — sweet-spot adaptive update logic."""

import pytest
from apprentice.train.curriculum_controller import CurriculumController


def _default_config():
    return {
        "initial_target_empty": 3,
        "min_target_empty": 3,
        "max_target_empty": 55,
        "target_rate": 0.70,
        "tolerance_band": [0.55, 0.85],
        "step_size": 10.0,
        "window_size": 200,
        "min_episodes_before_update": 100,
        "min_steps_between_updates": 50000,
        "stagnation_threshold_steps": 500000,
        "stagnation_probe_step": 1,
        "stagnation_rollback_threshold": 0.40,
        "stagnation_rollback_window_steps": 200000,
    }


def test_initial_state():
    ctrl = CurriculumController(_default_config())
    assert ctrl.target_empty_rounded == 3
    assert ctrl.last_advance_step == 0


def test_insufficient_window_no_update():
    """Update before reaching min_episodes_before_update is a no-op."""
    ctrl = CurriculumController(_default_config())
    for i in range(50):  # less than min_episodes_before_update=100
        ctrl.record_episode_outcome(success=True)
    ctrl.update(current_step=100_000)
    assert ctrl.target_empty_rounded == 3  # unchanged


def test_in_band_no_change():
    """sr in [0.55, 0.85] → target_empty stays."""
    ctrl = CurriculumController(_default_config())
    for _ in range(200):
        ctrl.record_episode_outcome(success=(0.70 > 0.30))  # ~70% success
    # Fill window with 70% success exactly
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))  # 0.70 success rate
    ctrl.update(current_step=100_000)
    assert ctrl.target_empty_rounded == 3


def test_too_easy_advance():
    """sr > 0.85 → target_empty increases."""
    ctrl = CurriculumController(_default_config())
    # Fill window with 95% success
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95
    ctrl.update(current_step=100_000)
    # adjustment = (0.95 - 0.85) * 10 = 1.0 → +1 round to 4
    assert ctrl.target_empty_rounded == 4
    assert ctrl.last_advance_step == 100_000


def test_too_hard_retreat():
    """sr < 0.55 → target_empty decreases."""
    cfg = _default_config()
    cfg["initial_target_empty"] = 10
    ctrl = CurriculumController(cfg)
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 3))  # 0.30 sr
    ctrl.update(current_step=100_000)
    # adjustment = (0.55 - 0.30) * 10 = 2.5 → 10 - 2.5 = 7.5 → 8
    assert ctrl.target_empty_rounded == 8


def test_clamp_to_min():
    cfg = _default_config()
    cfg["initial_target_empty"] = 4
    ctrl = CurriculumController(cfg)
    for _ in range(200):
        ctrl.record_episode_outcome(success=False)
    ctrl.update(current_step=100_000)
    # adjustment = (0.55 - 0.0) * 10 = 5.5 → 4 - 5.5 = -1.5 → clamped to 3
    assert ctrl.target_empty_rounded == 3


def test_clamp_to_max():
    cfg = _default_config()
    cfg["initial_target_empty"] = 54
    ctrl = CurriculumController(cfg)
    for _ in range(200):
        ctrl.record_episode_outcome(success=True)
    ctrl.update(current_step=100_000)
    # adjustment = (1.0 - 0.85) * 10 = 1.5 → 54 + 1.5 = 55.5 → clamped to 55
    assert ctrl.target_empty_rounded == 55


def test_min_steps_between_updates():
    """Cannot update twice within min_steps_between_updates."""
    ctrl = CurriculumController(_default_config())
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95
    ctrl.update(current_step=100_000)
    advanced_to = ctrl.target_empty_rounded
    # second update within min_steps_between_updates
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))
    ctrl.update(current_step=100_000 + 1000)  # only 1k later
    assert ctrl.target_empty_rounded == advanced_to  # no change


def test_record_episode_outcome_bounded_window():
    """Episode window must not grow beyond window_size."""
    cfg = _default_config()
    cfg["window_size"] = 50
    ctrl = CurriculumController(cfg)
    for _ in range(100):
        ctrl.record_episode_outcome(success=True)
    assert len(ctrl._success_window) == 50
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py -v
```

Expected: `ModuleNotFoundError: No module named 'apprentice.train.curriculum_controller'`

- [ ] **Step 3: Implement `CurriculumController`**

Create `apprentice/train/curriculum_controller.py`:

```python
"""Adaptive curriculum controller for apprentice training.

Tracks per-episode success rate over a sliding window and adjusts
target_empty using a sweet-spot formula:

  sr > tolerance_band[1] → too easy, increase difficulty
  sr < tolerance_band[0] → too hard, decrease difficulty
  else                   → in sweet spot, no change

Plus a stagnation detector (see _check_stagnation) that probes upward
when target_empty hasn't moved for stagnation_threshold_steps, and
auto-rolls-back if the probe fails.

State (target_empty, success_window, etc.) is persistable to JSON for
training resume — see save() / load() in Task 12.
"""

from __future__ import annotations

from collections import deque
from typing import Any


class CurriculumController:
    """See module docstring."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self.target_empty: float = float(config["initial_target_empty"])
        self._min_te: int = int(config["min_target_empty"])
        self._max_te: int = int(config["max_target_empty"])

        self._target_rate: float = float(config["target_rate"])
        self._lo: float = float(config["tolerance_band"][0])
        self._hi: float = float(config["tolerance_band"][1])
        self._step_size: float = float(config["step_size"])

        self._window_size: int = int(config["window_size"])
        self._min_eps: int = int(config["min_episodes_before_update"])
        self._min_steps_between: int = int(config["min_steps_between_updates"])

        self._stagn_threshold: int = int(config["stagnation_threshold_steps"])
        self._stagn_probe_step: int = int(config["stagnation_probe_step"])
        self._stagn_rollback_thresh: float = float(config["stagnation_rollback_threshold"])
        self._stagn_rollback_window: int = int(config["stagnation_rollback_window_steps"])

        self._success_window: deque[int] = deque(maxlen=self._window_size)
        self.last_advance_step: int = 0
        self.last_advance_direction: int = 0      # -1, 0, +1
        self.last_adjustment: float = 0.0
        self._probe_target: float | None = None    # set when probing
        self._probe_started_at: int = 0

    # ── Public API ────────────────────────────────────────────────────────

    @property
    def target_empty_rounded(self) -> int:
        return int(round(self.target_empty))

    def record_episode_outcome(self, success: bool) -> None:
        self._success_window.append(1 if success else 0)

    def success_rate(self) -> float:
        """0.0 if window is empty."""
        if not self._success_window:
            return 0.0
        return sum(self._success_window) / len(self._success_window)

    def update(self, current_step: int) -> None:
        """Possibly adjust target_empty based on recent success rate."""
        # Reset last_adjustment by default
        self.last_adjustment = 0.0

        # Phase 1: regular sweet-spot update
        self._regular_update(current_step)

        # Phase 2: stagnation detection / probe / rollback (implemented in Task 11)
        # (no-op for now; Task 11 fills this in)

    def in_sweet_spot(self) -> bool:
        sr = self.success_rate()
        return self._lo <= sr <= self._hi

    # ── Internals ─────────────────────────────────────────────────────────

    def _regular_update(self, current_step: int) -> None:
        if len(self._success_window) < self._min_eps:
            return

        if (current_step - self.last_advance_step) < self._min_steps_between and self.last_advance_step > 0:
            return

        sr = self.success_rate()

        if sr > self._hi:
            adj = (sr - self._hi) * self._step_size
            new_te = min(self._max_te, self.target_empty + adj)
            if int(round(new_te)) != int(round(self.target_empty)):
                self.target_empty = new_te
                self.last_advance_direction = +1
                self.last_advance_step = current_step
                self.last_adjustment = adj
            else:
                # Adj rounded to 0; treat as no-op
                self.last_advance_direction = 0

        elif sr < self._lo:
            adj = (self._lo - sr) * self._step_size
            new_te = max(self._min_te, self.target_empty - adj)
            if int(round(new_te)) != int(round(self.target_empty)):
                self.target_empty = new_te
                self.last_advance_direction = -1
                self.last_advance_step = current_step
                self.last_adjustment = -adj
            else:
                self.last_advance_direction = 0

        else:
            # In sweet spot
            self.last_advance_direction = 0
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py -v
```

Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/curriculum_controller.py apprentice/tests/test_curriculum_controller.py
git commit -m "feat(apprentice): B1 part 3 — CurriculumController sweet-spot logic

Implements the core adaptive curriculum update:
  sr > 0.85 → increase target_empty
  sr < 0.55 → decrease target_empty
  else      → stay

Adjustment magnitude = |sr - band_edge| × step_size.
Respects min/max bounds and min_steps_between_updates.
Stagnation detection deferred to Task 11."
```

---

## Task 11: B1 Part 4 — Stagnation Detector + Probe + Rollback

**Files:**
- Modify: `apprentice/train/curriculum_controller.py`
- Test: `apprentice/tests/test_curriculum_controller.py`

- [ ] **Step 1: Write the failing test**

Append to `apprentice/tests/test_curriculum_controller.py`:

```python
def test_stagnation_probe_after_threshold_steps():
    """If target_empty hasn't moved for stagnation_threshold_steps, probe +1."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    ctrl = CurriculumController(cfg)

    # Stay perfectly in sweet spot (sr=0.70) for a while
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))

    # First update at step 50k → no change (in band)
    ctrl.update(current_step=50_000)
    assert ctrl.target_empty_rounded == 5

    # At step 150k (> threshold from last_advance_step=0)
    # → should probe +1
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 6
    assert ctrl._probe_target == 6.0


def test_probe_success_clears_probe_state():
    """If sr stays acceptable after probe, probe state clears."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    cfg["stagnation_rollback_window_steps"] = 50_000
    ctrl = CurriculumController(cfg)

    # Trigger probe
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl._probe_target == 6.0

    # Now agent does OK at new target — sr stays at 0.70
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    # After rollback window, probe should be cleared
    ctrl.update(current_step=210_000)  # 60k after probe started, > rollback_window
    assert ctrl._probe_target is None


def test_probe_failure_triggers_rollback():
    """If sr drops below rollback threshold after probe, target_empty rolls back."""
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 5
    cfg["stagnation_rollback_window_steps"] = 50_000
    cfg["stagnation_rollback_threshold"] = 0.40
    ctrl = CurriculumController(cfg)

    # Trigger probe to 6
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 6

    # Now agent struggles at 6 — sr drops to 0.20
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 2))  # 0.20

    # Wait until rollback_window has passed
    ctrl.update(current_step=210_000)  # 60k after probe started
    # Probe failed; rollback to 5
    assert ctrl.target_empty_rounded == 5
    assert ctrl._probe_target is None


def test_probe_rollback_clamps_to_min():
    cfg = _default_config()
    cfg["stagnation_threshold_steps"] = 100_000
    cfg["initial_target_empty"] = 3
    cfg["stagnation_rollback_window_steps"] = 50_000
    cfg["min_target_empty"] = 3
    ctrl = CurriculumController(cfg)

    # Trigger probe — even though we're at min, probe just adds 1
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 10 < 7))
    ctrl.update(current_step=150_000)
    assert ctrl.target_empty_rounded == 4  # 3 + 1

    # Fail probe
    ctrl._success_window.clear()
    for i in range(200):
        ctrl.record_episode_outcome(success=False)
    ctrl.update(current_step=210_000)
    # Rollback would be 4 - 1 = 3, which is min, so clamps to 3.
    assert ctrl.target_empty_rounded == 3
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py::test_stagnation_probe_after_threshold_steps -v
```

Expected: FAIL (no stagnation logic yet)

- [ ] **Step 3: Implement stagnation/probe/rollback**

Open `apprentice/train/curriculum_controller.py`. Replace the `update()` method:

```python
    def update(self, current_step: int) -> None:
        """Possibly adjust target_empty based on recent success rate."""
        self.last_adjustment = 0.0

        # Phase 0: handle in-flight probe (must come BEFORE regular update,
        # otherwise regular update might shadow probe rollback)
        if self._probe_target is not None:
            self._handle_active_probe(current_step)
            if self._probe_target is None:
                return  # probe just resolved; skip regular update this cycle

        # Phase 1: regular sweet-spot update
        self._regular_update(current_step)
        if self.last_advance_direction != 0:
            return  # regular update happened; no stagnation check needed this cycle

        # Phase 2: stagnation detection (only if regular update did nothing)
        self._maybe_probe_stagnation(current_step)
```

Add the new methods (place after `_regular_update`):

```python
    def _maybe_probe_stagnation(self, current_step: int) -> None:
        """If target_empty hasn't advanced for stagnation_threshold_steps, probe +1."""
        if self._probe_target is not None:
            return  # already probing

        if len(self._success_window) < self._min_eps:
            return  # not enough data yet

        idle_steps = current_step - self.last_advance_step
        if idle_steps < self._stagn_threshold:
            return

        new_te = min(self._max_te, self.target_empty + self._stagn_probe_step)
        if int(round(new_te)) == int(round(self.target_empty)):
            # No-op probe (already at max)
            return

        self._probe_target = new_te
        self._probe_started_at = current_step
        # Snapshot the pre-probe target for rollback target tracking
        # (we already have it implicitly via probe_target - probe_step)

        # Apply the probe
        self.target_empty = new_te
        self.last_advance_step = current_step
        self.last_advance_direction = +1
        self.last_adjustment = float(self._stagn_probe_step)

    def _handle_active_probe(self, current_step: int) -> None:
        """If a probe is in flight, decide whether to roll back or clear it."""
        elapsed = current_step - self._probe_started_at
        if elapsed < self._stagn_rollback_window:
            return  # give the probe more time to evaluate

        sr = self.success_rate()
        if sr < self._stagn_rollback_thresh:
            # Probe failed — roll back to one step below probe_target
            rollback_te = max(self._min_te, self._probe_target - 1)
            self.target_empty = float(rollback_te)
            self.last_advance_step = current_step
            self.last_advance_direction = -1
            self.last_adjustment = -1.0
            self._probe_target = None
        elif sr >= self._lo:
            # Probe succeeded or at least not catastrophic — clear probe
            self._probe_target = None
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py -v
```

Expected: All tests PASS (13 total now).

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/curriculum_controller.py apprentice/tests/test_curriculum_controller.py
git commit -m "feat(apprentice): B1 part 4 — stagnation detector + probe + rollback

If target_empty hasn't advanced for stagnation_threshold_steps (default 500k),
controller probes target_empty + 1. After rollback_window (200k step) it
evaluates the probe:
  sr < rollback_threshold (0.40)  → roll back to probe_target - 1
  sr >= tolerance_band lo (0.55)  → clear probe state

Rollback clamps to min_target_empty."
```

---

## Task 12: B1 Part 5 — `CurriculumController` Save/Load JSON

**Files:**
- Modify: `apprentice/train/curriculum_controller.py`
- Test: `apprentice/tests/test_curriculum_controller.py`

- [ ] **Step 1: Write the failing test**

Append to `apprentice/tests/test_curriculum_controller.py`:

```python
def test_save_load_round_trip(tmp_path):
    """save() then load() should restore exactly the same state."""
    cfg = _default_config()
    ctrl1 = CurriculumController(cfg)
    # Mutate some state
    for i in range(200):
        ctrl1.record_episode_outcome(success=(i % 20 < 19))  # 0.95
    ctrl1.update(current_step=100_000)
    assert ctrl1.target_empty_rounded == 4

    path = tmp_path / "curriculum.json"
    ctrl1.save(str(path))
    assert path.exists()

    ctrl2 = CurriculumController(cfg)
    ctrl2.load(str(path))

    assert ctrl2.target_empty == ctrl1.target_empty
    assert ctrl2.last_advance_step == ctrl1.last_advance_step
    assert ctrl2.last_advance_direction == ctrl1.last_advance_direction
    assert list(ctrl2._success_window) == list(ctrl1._success_window)
    assert ctrl2._probe_target == ctrl1._probe_target
    assert ctrl2._probe_started_at == ctrl1._probe_started_at


def test_load_missing_file_keeps_init(tmp_path):
    """load() of a non-existent file leaves controller at initial state (no crash)."""
    cfg = _default_config()
    ctrl = CurriculumController(cfg)
    ctrl.load(str(tmp_path / "does_not_exist.json"))
    assert ctrl.target_empty == float(cfg["initial_target_empty"])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py::test_save_load_round_trip -v
```

Expected: FAIL `AttributeError: 'CurriculumController' object has no attribute 'save'`

- [ ] **Step 3: Implement save/load**

Add to `apprentice/train/curriculum_controller.py` (inside the class):

```python
    def save(self, path: str) -> None:
        """Serialize state to a JSON file at `path`."""
        import json
        from pathlib import Path

        state = {
            "target_empty": self.target_empty,
            "last_advance_step": self.last_advance_step,
            "last_advance_direction": self.last_advance_direction,
            "last_adjustment": self.last_adjustment,
            "probe_target": self._probe_target,
            "probe_started_at": self._probe_started_at,
            "success_window": list(self._success_window),
        }
        Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")

    def load(self, path: str) -> None:
        """Restore state from a JSON file. No-op if the file does not exist."""
        import json
        from pathlib import Path

        p = Path(path)
        if not p.exists():
            return  # leave controller at init state

        state = json.loads(p.read_text(encoding="utf-8"))
        self.target_empty = float(state["target_empty"])
        self.last_advance_step = int(state["last_advance_step"])
        self.last_advance_direction = int(state["last_advance_direction"])
        self.last_adjustment = float(state["last_adjustment"])
        self._probe_target = (
            float(state["probe_target"]) if state["probe_target"] is not None else None
        )
        self._probe_started_at = int(state["probe_started_at"])

        # Restore success window (preserve maxlen)
        self._success_window.clear()
        for v in state["success_window"]:
            self._success_window.append(int(v))
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_curriculum_controller.py -v
```

Expected: All tests PASS (15 total).

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/curriculum_controller.py apprentice/tests/test_curriculum_controller.py
git commit -m "feat(apprentice): B1 part 5 — CurriculumController save/load JSON

Allows resuming curriculum state from a sidecar JSON file alongside
the checkpoint. load() on a missing file leaves controller at init
state (no crash) — supports first-run case."
```

---

## Task 13: B1 Part 6 — `CurriculumCallback` (SB3 Integration)

**Files:**
- Create: `apprentice/train/curriculum_callback.py`
- Test: `apprentice/tests/test_curriculum_callback.py`

- [ ] **Step 1: Write the failing test**

Create `apprentice/tests/test_curriculum_callback.py`:

```python
"""Tests for CurriculumCallback — bridges CurriculumController to SB3."""

from unittest.mock import MagicMock, patch
import pytest

from apprentice.train.curriculum_callback import CurriculumCallback
from apprentice.train.curriculum_controller import CurriculumController


def _default_config():
    return {
        "initial_target_empty": 3,
        "min_target_empty": 3,
        "max_target_empty": 55,
        "target_rate": 0.70,
        "tolerance_band": [0.55, 0.85],
        "step_size": 10.0,
        "window_size": 200,
        "min_episodes_before_update": 100,
        "min_steps_between_updates": 50000,
        "stagnation_threshold_steps": 500000,
        "stagnation_probe_step": 1,
        "stagnation_rollback_threshold": 0.40,
        "stagnation_rollback_window_steps": 200000,
    }


def _mock_vec_env():
    """Mock VecEnv-like object with set_attr / env_method support."""
    venv = MagicMock()
    venv.num_envs = 4
    # Track env_method calls
    venv._env_method_calls = []
    def _env_method(name, *args, **kwargs):
        venv._env_method_calls.append((name, args, kwargs))
        return [None] * venv.num_envs
    venv.env_method.side_effect = _env_method
    return venv


def test_callback_initializes_controller_from_config():
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=50_000, verbose=0)
    # Just instantiate; no asserts on internal state beyond controller link
    assert cb.controller is ctrl


def test_callback_record_outcome_from_info_dict():
    """When env emits is_success=True info dict on episode end, callback records it."""
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=50_000, verbose=0)

    # Simulate _on_step with locals_ containing dones + infos
    cb.model = MagicMock()
    cb.model.num_timesteps = 100
    cb.locals = {
        "dones": [True, False, True, False],
        "infos": [
            {"is_success": True},
            {"is_success": False},
            {"is_success": False},
            {"is_success": False},
        ],
    }
    cb._on_step()

    # 2 episodes finished, 1 success, 1 failure
    assert list(ctrl._success_window) == [1, 0]


def test_callback_pushes_target_empty_at_update_interval():
    """At update_interval_steps boundary, callback applies target_empty to all envs."""
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=10_000, verbose=0)

    cb.model = MagicMock()
    cb.training_env = _mock_vec_env()

    # Pre-fill controller window with high success
    for i in range(200):
        ctrl.record_episode_outcome(success=(i % 20 < 19))  # 0.95

    cb.model.num_timesteps = 10_000
    cb.locals = {"dones": [False] * 4, "infos": [{}] * 4}
    cb._last_update_step = 0
    cb._on_step()

    # Controller should have advanced; callback should have pushed target to envs
    calls = cb.training_env._env_method_calls
    set_target_calls = [c for c in calls if c[0] == "set_target_empty"]
    assert len(set_target_calls) >= 1
    pushed = set_target_calls[-1][1][0]
    assert pushed == ctrl.target_empty_rounded


def test_callback_does_not_update_before_interval():
    ctrl = CurriculumController(_default_config())
    cb = CurriculumCallback(controller=ctrl, update_interval_steps=10_000, verbose=0)
    cb.model = MagicMock()
    cb.training_env = _mock_vec_env()
    cb._last_update_step = 0
    cb.model.num_timesteps = 5_000  # halfway to interval
    cb.locals = {"dones": [False] * 4, "infos": [{}] * 4}
    cb._on_step()

    # No update happened yet
    set_target_calls = [c for c in cb.training_env._env_method_calls if c[0] == "set_target_empty"]
    assert len(set_target_calls) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest apprentice/tests/test_curriculum_callback.py -v
```

Expected: `ModuleNotFoundError: No module named 'apprentice.train.curriculum_callback'`

- [ ] **Step 3: Implement `CurriculumCallback`**

Create `apprentice/train/curriculum_callback.py`:

```python
"""CurriculumCallback — SB3 callback wiring CurriculumController to training.

Responsibilities:
  1. After each env step, read `infos` for ended episodes and forward
     `is_success` to the controller.
  2. At every `update_interval_steps` steps, ask controller to update; if
     target_empty changed, push the new value to every vec_env worker.
  3. Write TB metrics (curriculum/target_empty, etc.) at update boundaries.
  4. Save / restore controller state via sidecar JSON.
"""

from __future__ import annotations

import os
from typing import Any

from stable_baselines3.common.callbacks import BaseCallback

from apprentice.train.curriculum_controller import CurriculumController


class CurriculumCallback(BaseCallback):
    """See module docstring."""

    def __init__(
        self,
        controller: CurriculumController,
        update_interval_steps: int = 50_000,
        save_path: str | None = None,
        save_freq_steps: int = 50_000,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self.controller = controller
        self.update_interval_steps = update_interval_steps
        self.save_path = save_path
        self.save_freq_steps = save_freq_steps
        self._last_update_step: int = 0
        self._last_save_step: int = 0
        self._last_pushed_target: int | None = None

    def _on_training_start(self) -> None:
        """Push initial target_empty to all envs."""
        self._push_target_to_envs()

    def _on_step(self) -> bool:
        # 1. Record episode outcomes from infos
        dones = self.locals.get("dones", [])
        infos = self.locals.get("infos", [])
        for done, info in zip(dones, infos):
            if not done:
                continue
            success = bool(info.get("is_success", False))
            self.controller.record_episode_outcome(success=success)

        step = int(self.model.num_timesteps)

        # 2. Maybe update controller
        if step - self._last_update_step >= self.update_interval_steps:
            self.controller.update(current_step=step)
            self._last_update_step = step
            new_target = self.controller.target_empty_rounded
            if new_target != self._last_pushed_target:
                self._push_target_to_envs()
            self._log_tb_metrics()

        # 3. Periodic save
        if self.save_path and step - self._last_save_step >= self.save_freq_steps:
            self.controller.save(self.save_path)
            self._last_save_step = step

        return True

    def _push_target_to_envs(self) -> None:
        target = self.controller.target_empty_rounded
        if self.training_env is None:
            return
        # SubprocVecEnv supports env_method; this calls set_target_empty(target) on every worker
        self.training_env.env_method("set_target_empty", target)
        self._last_pushed_target = target
        if self.verbose >= 1:
            print(f"[Curriculum] pushed target_empty={target} at step={self.model.num_timesteps if self.model else 0}")

    def _log_tb_metrics(self) -> None:
        if self.logger is None:
            return
        self.logger.record("curriculum/target_empty", float(self.controller.target_empty))
        self.logger.record("curriculum/target_empty_rounded", float(self.controller.target_empty_rounded))
        self.logger.record("curriculum/success_rate_window", float(self.controller.success_rate()))
        self.logger.record("curriculum/in_sweet_spot", 1.0 if self.controller.in_sweet_spot() else 0.0)
        self.logger.record("curriculum/adjustment_per_update", float(self.controller.last_adjustment))
        steps_since = int(self.model.num_timesteps) - int(self.controller.last_advance_step)
        self.logger.record("curriculum/steps_since_last_advance", float(steps_since))
        self.logger.record("curriculum/is_probing", 1.0 if self.controller._probe_target is not None else 0.0)
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest apprentice/tests/test_curriculum_callback.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/curriculum_callback.py apprentice/tests/test_curriculum_callback.py
git commit -m "feat(apprentice): B1 part 6 — CurriculumCallback (SB3 integration)

Bridges CurriculumController to SB3 training:
- Records episode outcomes from info['is_success']
- Calls controller.update() every update_interval_steps
- Pushes new target_empty to all vec_env workers via env_method
- Writes 7 TB metrics (curriculum/target_empty, etc.)
- Periodic save of controller state to sidecar JSON
- Pushes initial target_empty in _on_training_start"
```

---

## Task 14: Curriculum Config JSON

**Files:**
- Create: `apprentice/configs/curriculum.json`

- [ ] **Step 1: Create the config file**

Create `apprentice/configs/curriculum.json` with the exact content:

```json
{
  "initial_target_empty": 3,
  "min_target_empty": 3,
  "max_target_empty": 55,

  "target_rate": 0.70,
  "tolerance_band": [0.55, 0.85],
  "step_size": 10.0,

  "window_size": 200,
  "min_episodes_before_update": 100,
  "min_steps_between_updates": 50000,

  "stagnation_threshold_steps": 500000,
  "stagnation_probe_step": 1,
  "stagnation_rollback_threshold": 0.40,
  "stagnation_rollback_window_steps": 200000
}
```

- [ ] **Step 2: Verify it parses**

```bash
python -c "import json; print(json.load(open('apprentice/configs/curriculum.json')))"
```

Expected: prints the parsed dict.

- [ ] **Step 3: Commit**

```bash
git add apprentice/configs/curriculum.json
git commit -m "feat(apprentice): B1 part 7 — default curriculum config

Default hyperparameters for adaptive curriculum:
- target_rate 0.70
- tolerance_band [0.55, 0.85]
- step_size 10
- stagnation_threshold 500k steps
- rollback_threshold 0.40

Editable between training runs; takes effect on next launch."
```

---

## Task 15: E1 + Wire Everything in `train.py`

**Files:**
- Modify: `apprentice/train/train.py`

This task pulls together everything: load curriculum config, instantiate controller + callback, enforce obs-shape safety on resume, set callback into model.learn() callbacks list.

- [ ] **Step 1: Add imports and helpers**

Open `apprentice/train/train.py`. Near the existing imports, add:

```python
import json
from apprentice.train.curriculum_controller import CurriculumController
from apprentice.train.curriculum_callback import CurriculumCallback
```

- [ ] **Step 2: Add curriculum config path constant**

Below the existing path constants (`MODEL_DIR`, `LOG_DIR`, etc.):

```python
CURRICULUM_CONFIG = str(_REPO_ROOT / "apprentice" / "configs" / "curriculum.json")
```

- [ ] **Step 3: Add `--curriculum-config` CLI flag**

In `parse_args()`, add:

```python
    p.add_argument("--curriculum-config", type=str, default=CURRICULUM_CONFIG,
                   help="Path to curriculum config JSON")
    p.add_argument("--no-curriculum", action="store_true",
                   help="Disable adaptive curriculum entirely (env runs with no target_empty)")
```

- [ ] **Step 4: Add obs-shape safety check on resume**

Find the existing model-loading block:

```python
    if load_path is not None:
        print(f"[train] Resuming from: {load_path}")
        model = SudokuMaskablePPO.load(
            load_path, env=vec_env, device=args.device,
        )
```

Replace with:

```python
    if load_path is not None:
        print(f"[apprentice] Resuming from: {load_path}")
        try:
            model = SudokuMaskablePPO.load(
                load_path, env=vec_env, device=args.device,
            )
        except RuntimeError as e:
            if "size mismatch" in str(e).lower():
                sys.exit(
                    f"[apprentice] FATAL: ckpt obs shape doesn't match current env "
                    f"observation_space={vec_env.observation_space.shape}. "
                    f"obs shape may have changed between training runs; must cold-start "
                    f"(omit --load-model). Underlying error: {e}"
                )
            raise
```

- [ ] **Step 5: Wire CurriculumController and CurriculumCallback into the callback list**

Find the existing callback creation block (around line 240-260):

```python
    checkpoint = CheckpointWithSidecars(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="apprentice_ckpt",
        verbose=args.verbose,
    )
    eval_cb = SudokuEvalCallback(
        ...
    )
    reserved_eval = ReservedEvalCallback(
        ...
    )
```

After these, add:

```python
    # Curriculum controller + callback
    if not args.no_curriculum:
        with open(args.curriculum_config, "r", encoding="utf-8") as f:
            curr_cfg = json.load(f)
        curriculum = CurriculumController(curr_cfg)

        # If resuming and a curriculum sidecar exists alongside the ckpt, load it
        if load_path is not None:
            curr_sidecar = load_path.replace(".zip", "_curriculum.json")
            if os.path.exists(curr_sidecar):
                curriculum.load(curr_sidecar)
                print(f"[apprentice] Loaded curriculum state from {curr_sidecar}")

        # Persistent sidecar: write next to MODEL_NAME on every save
        curriculum_sidecar = os.path.join(MODEL_DIR, MODEL_NAME + "_curriculum.json")
        curriculum_cb = CurriculumCallback(
            controller=curriculum,
            update_interval_steps=50_000,
            save_path=curriculum_sidecar,
            save_freq_steps=50_000,
            verbose=args.verbose,
        )
    else:
        curriculum_cb = None
```

- [ ] **Step 6: Update the `model.learn(...)` callbacks list**

Find:

```python
        model.learn(
            total_timesteps=args.timesteps,
            callback=[checkpoint, eval_cb, reserved_eval],
            reset_num_timesteps=(load_path is None),
            tb_log_name=TB_LOG_NAME,
        )
```

Replace with:

```python
        callbacks = [checkpoint, eval_cb, reserved_eval]
        if curriculum_cb is not None:
            callbacks.append(curriculum_cb)
        model.learn(
            total_timesteps=args.timesteps,
            callback=callbacks,
            reset_num_timesteps=(load_path is None),
            tb_log_name=TB_LOG_NAME,
        )
```

- [ ] **Step 7: Make CheckpointWithSidecars also save curriculum state**

Open `apprentice/train/train.py`. Find `CheckpointWithSidecars._on_step` method. Locate:

```python
        base = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps")
        self.model.save(base + ".zip")
        vec_env = self.model.get_vec_normalize_env()
        if isinstance(vec_env, VecNormalize):
            vec_env.save(base + "_vecnorm.pkl")
            tag = "+vecnorm"
        else:
            tag = ""
```

Modify the sidecar save logic to also write curriculum.json. Replace with:

```python
        base = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps")
        self.model.save(base + ".zip")
        sidecar_tags: list[str] = []
        vec_env = self.model.get_vec_normalize_env()
        if isinstance(vec_env, VecNormalize):
            vec_env.save(base + "_vecnorm.pkl")
            sidecar_tags.append("vecnorm")

        # Also save curriculum state alongside ckpt — look up CurriculumCallback in self.callbacks
        for cb in getattr(self, "_associated_curriculum_cbs", []):
            if cb is not None and cb.controller is not None:
                cb.controller.save(base + "_curriculum.json")
                sidecar_tags.append("curriculum")
                break

        tag = ("+" + " +".join(sidecar_tags)) if sidecar_tags else ""
```

For the associated callbacks list, add this near the constructor of `CheckpointWithSidecars`:

```python
    def __init__(
        self,
        save_freq: int,
        save_path: str,
        name_prefix: str,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix
        self._last_save: int | None = None
        self._associated_curriculum_cbs: list = []
        os.makedirs(save_path, exist_ok=True)

    def add_curriculum_callback(self, cb) -> None:
        self._associated_curriculum_cbs.append(cb)
```

Then after creating both `checkpoint` and `curriculum_cb` in `main()`:

```python
    if curriculum_cb is not None:
        checkpoint.add_curriculum_callback(curriculum_cb)
```

- [ ] **Step 8: Update the `finally` block to save curriculum.json on exit**

Find the `finally` block at the end of `main()`:

```python
    finally:
        # Always save on exit (Ctrl-C, exception, normal completion)
        save_path = os.path.join(MODEL_DIR, MODEL_NAME)
        model.save(save_path)
        sidecars: list[str] = []
        if isinstance(vec_env, VecNormalize):
            vec_env.save(save_path + "_vecnorm.pkl")
            sidecars.append("vecnorm")
        sidecar_str = " + ".join(sidecars) if sidecars else "no sidecars"
        print(f"[train] Saved -> {save_path}.zip ({sidecar_str})")
```

Modify to also save curriculum:

```python
    finally:
        save_path = os.path.join(MODEL_DIR, MODEL_NAME)
        model.save(save_path)
        sidecars: list[str] = []
        if isinstance(vec_env, VecNormalize):
            vec_env.save(save_path + "_vecnorm.pkl")
            sidecars.append("vecnorm")
        if curriculum_cb is not None:
            curriculum_cb.controller.save(save_path + "_curriculum.json")
            sidecars.append("curriculum")
        sidecar_str = " + ".join(sidecars) if sidecars else "no sidecars"
        print(f"[apprentice] Saved -> {save_path}.zip ({sidecar_str})")
```

- [ ] **Step 9: Smoke-test the integrated training**

```bash
python -m apprentice.train.train --timesteps 2000 --n-envs 2 --verbose 1
```

Expected:
- Training runs to completion
- Console prints `[Curriculum] pushed target_empty=3 at step=...`
- `apprentice_latest.zip` + `apprentice_latest_vecnorm.pkl` + `apprentice_latest_curriculum.json` are created in `apprentice/models/`
- `apprentice/runs/apprentice_1/events.out.tfevents.*` exists

- [ ] **Step 10: Verify TB has curriculum metrics**

```bash
python -c "
from pathlib import Path
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
runs = Path('apprentice/runs/')
files = sorted(runs.rglob('events.out.tfevents.*'), key=lambda p: p.stat().st_mtime)
ea = EventAccumulator(str(files[-1]), size_guidance={'scalars': 0})
ea.Reload()
tags = sorted(ea.Tags().get('scalars', []))
print('Curriculum metrics found:')
for t in tags:
    if t.startswith('curriculum/'):
        print('  ', t)
"
```

Expected: Prints at least the 7 curriculum metrics from the callback.

- [ ] **Step 11: Commit**

```bash
git add apprentice/train/train.py
git commit -m "feat(apprentice): E1 + integration — wire curriculum into train.py

- Load curriculum.json config (--curriculum-config flag, default to apprentice/configs/)
- Instantiate CurriculumController and CurriculumCallback
- Resume curriculum state from <ckpt>_curriculum.json sidecar if present
- CheckpointWithSidecars now also saves curriculum sidecar alongside vecnorm
- finally-block save also writes curriculum sidecar
- E1: obs-shape mismatch on resume now fails fast with clear error message
- New flags: --no-curriculum (debug), --curriculum-config (custom path)"
```

---

## Task 16: `apprentice/README.md`

**Files:**
- Create: `apprentice/README.md`

- [ ] **Step 1: Create README**

Create `apprentice/README.md`:

```markdown
# apprentice/ — Reasoner + Adaptive Curriculum

Sibling of `reasoner/` (frozen baseline). Applies 7 design changes:

| ID | Change |
|---|---|
| A3 | obs +2 channels (naked-single flag + hidden-single flag) — 26 ch total |
| B1 | Adaptive reverse curriculum (sweet-spot formula on `target_empty`) |
| A5 | Dynamic `max_steps = max(60, target_empty × 8)` |
| D1 | Policy hidden layer: `net_arch={"pi": [128], "vf": [128, 128]}` |
| E2 | Dynamic `max_wrong = max(20, target_empty × 1.2)` |
| C2 | `ent_coef = 0.05` (was 0.02) |
| E1 | Cold-start required (obs shape change vs reasoner) |

See [docs/superpowers/specs/2026-05-13-apprentice-adaptive-curriculum-design.md](../docs/superpowers/specs/2026-05-13-apprentice-adaptive-curriculum-design.md).

## Run from repo root

```bash
# Fresh training
python -m apprentice.train.train

# Resume latest ckpt
python -m apprentice.train.train --load-model auto

# Custom curriculum config
python -m apprentice.train.train --curriculum-config apprentice/configs/curriculum_aggressive.json

# Disable curriculum (debug)
python -m apprentice.train.train --no-curriculum
```

## Tests

```bash
python -m pytest apprentice/tests/ -v
```

## Curriculum config

Edit [configs/curriculum.json](configs/curriculum.json) between training sessions. Hot-reload during a single run is not supported.

Three core hyperparameters:
- `target_rate`: desired success rate the curriculum aims for (default 0.70)
- `tolerance_band`: do-nothing zone around target rate (default [0.55, 0.85])
- `step_size`: difficulty adjustment per 10% deviation outside band (default 10.0)

## What's different vs reasoner/

- `env/sudoku_gym_env.py`: 26-channel obs; `target_empty` attribute drives fill_back, dynamic max_steps, dynamic max_wrong
- `env/obs_helpers.py`: new — compute naked/hidden single grids
- `train/curriculum_controller.py`: new — adaptive controller
- `train/curriculum_callback.py`: new — SB3 integration
- `train/train.py`: D1 policy hidden, C2 ent_coef, E1 cold-start assertion, curriculum wiring
- `configs/curriculum.json`: new — controller hyperparameters

`reasoner/` itself is untouched.
```

- [ ] **Step 2: Commit**

```bash
git add apprentice/README.md
git commit -m "docs(apprentice): add README

Describes the 7 design changes, how to run training, tests,
curriculum config, and diff vs reasoner/."
```

---

## Task 17: End-to-End Smoke Test (10k step run)

**Files:**
- No file changes — just verification

- [ ] **Step 1: Cold-start training run for 10k steps**

```bash
python -m apprentice.train.train --timesteps 10000 --n-envs 4 --verbose 1
```

Expected (in order on console):
- `[apprentice] Policy parameters: ~3,200,000`
- `[apprentice] num_timesteps at start: 0`
- `[apprentice] target num_timesteps:   10,000`
- `[Curriculum] pushed target_empty=3 at step=0` (initial push from _on_training_start)
- Per-update TB scalar lines (every 50k step — but at 10k we won't see any updates)

The run completes without exception. `apprentice_latest.zip` + `_vecnorm.pkl` + `_curriculum.json` are saved.

- [ ] **Step 2: Verify TB scalars look correct**

```bash
python -c "
from pathlib import Path
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
runs = Path('apprentice/runs/')
files = sorted(runs.rglob('events.out.tfevents.*'), key=lambda p: p.stat().st_mtime)
ea = EventAccumulator(str(files[-1]), size_guidance={'scalars': 0})
ea.Reload()
tags = sorted(ea.Tags().get('scalars', []))
print(f'Total scalar tags: {len(tags)}')
required = [
    'curriculum/target_empty',
    'curriculum/target_empty_rounded',
    'curriculum/success_rate_window',
    'curriculum/in_sweet_spot',
    'curriculum/adjustment_per_update',
    'curriculum/steps_since_last_advance',
    'curriculum/is_probing',
    'rollout/ep_rew_mean',
    'rollout/ep_len_mean',
    'train/entropy_loss',
    'train/value_loss',
]
missing = [t for t in required if t not in tags]
if missing:
    print('MISSING tags:', missing)
else:
    print('All required tags present')
"
```

Expected: `All required tags present`.

- [ ] **Step 3: Run full unit test suite**

```bash
python -m pytest apprentice/tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 4: Verify reasoner/ untouched**

```bash
git diff --stat HEAD~17 -- reasoner/
```

Expected: empty output (no changes to reasoner/).

- [ ] **Step 5: Verify resume works correctly**

```bash
# Resume from latest ckpt with another 2k steps
python -m apprentice.train.train --timesteps 12000 --load-model auto --n-envs 4 --verbose 1
```

Expected:
- `[apprentice] Resuming from: apprentice/models/apprentice_ckpt_..._steps.zip` (or `apprentice_latest.zip`)
- `[apprentice] Loaded curriculum state from ..._curriculum.json` (if a ckpt-sidecar exists; otherwise prints a warning is OK on first resume because the sidecar lives next to apprentice_latest)
- Training continues from `num_timesteps ≈ 10000`

- [ ] **Step 6: Final commit**

If everything passes and no code changes happened in this task, no commit is needed. Otherwise commit any fixes.

If you want a marker commit:

```bash
git commit --allow-empty -m "chore(apprentice): end-to-end smoke test verified

10k step cold-start completed:
- All 7 curriculum metrics present in TB
- All unit tests pass
- reasoner/ untouched
- Resume from ckpt with curriculum sidecar restoration works"
```

---

## Self-Review

### Spec coverage

| Spec § | Plan task(s) |
|---|---|
| §1 Background | (informational; embedded in Plan header + Spec link) |
| §2 Goals (concrete metrics) | Day 1-7 results from Task 17 + later Colab training |
| §3 Non-goals | Plan respects all exclusions (no A1, A2, A4, B2, B3, B4, B5, D2; no AlphaZero) |
| §4.1 Three-sibling structure | Task 1 bootstraps; Task 17 verifies reasoner/ untouched |
| §4.2 Seven-change overview | Tasks 3 (D1), 4 (C2), 5-6 (A3), 7-9 (B1+A5+E2 env-side), 10-13 (B1 controller+callback), 15 (E1) |
| §5.1 A3 obs flag | Tasks 5-6 |
| §5.2.1 fill_back env logic | Task 8 |
| §5.2.2 Adaptive controller | Tasks 10-11 |
| §5.2.3 Oscillation defense | window_size=200, min_steps_between_updates — built into Task 10 |
| §5.2.4 Stagnation detector | Task 11 |
| §5.2.5 Resume compatibility | Tasks 12 (save/load) + 15 (wiring in train.py) |
| §5.3 A5 max_steps formula | Task 9 |
| §5.4 D1 net_arch | Task 3 |
| §5.5 E2 max_wrong formula | Task 9 |
| §5.6 C2 ent_coef | Task 4 |
| §5.7 E1 cold-start | Task 15 step 4 (obs-shape assertion) |
| §6.1-6.4 File copy structure | Task 1 |
| §7 Config schema | Task 14 |
| §8 TB metrics | Task 13 _log_tb_metrics; Task 17 step 2 verifies |
| §9 Day 1-7 schedule | Tasks order matches Day 1-4 (Day 5-7 = Colab, not in this plan) |
| §10 Acceptance criteria | Task 17 covers code-level criteria; training-level Day 7 criteria are runtime-only |
| §11 Colab placeholder | Out of scope (deferred) |
| §12 Risk register | Mitigations are built into Tasks 10-11 |
| §13 Open questions | obs_helpers.py is separate file ✓; probe_step=1 ✓; eval callback curriculum-aware = NO (deferred); partial weight transfer = NO (clean cold-start) |

All spec items covered or explicitly deferred (Colab in spec §11; eval-callback curriculum-aware in spec §13.3).

### Placeholder scan

Searched for: `TBD`, `TODO`, `implement later`, `add error handling`, `similar to`, `etc.` — none found in plan tasks. Code blocks complete.

### Type consistency

- `target_empty` is `int | None` in env, `float` internally in controller (with `.target_empty_rounded` accessor as int). Consistent.
- `success_window` is `deque[int]` (0 or 1). Consistent across record/save/load.
- `CurriculumCallback._push_target_to_envs` passes `target_empty_rounded` (int) to env's `set_target_empty()` which accepts `int | None`. Consistent.
- `is_success` info-dict key — env emits `bool` (from `terminated and np.all(board != 0)`), controller stores as int 0/1. Compatible.
- Sidecar file naming: `<ckpt>_curriculum.json` consistent across save (Task 15), load (Task 15), `_associated_curriculum_cbs` mechanism (Task 15).

All consistent.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-13-apprentice-adaptive-curriculum.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
