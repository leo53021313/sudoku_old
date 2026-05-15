# Apprentice Per-Episode Tried-Bad-Eliminate Mask Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a per-episode `_tried_bad_elim` set to `SudokuGymEnv` and wire it through `RewardComputer._compute_eliminate` (writer) and `action_masks()` (reader) so the policy cannot deterministically loop on the same wrong `eliminate(r, c, v)` action after a single failure.

**Architecture:** Two-task split: Task 1 lands the env-side plumbing (field init + reset clearing) with paired tests. After Task 1, no behavioral change yet (set is dead state). Task 2 wires up the writer in the reward computer's wrong-eliminate branch and the reader in `action_masks()`. This is when the loop fix becomes active. Task 3 runs the full apprentice regression to confirm no other tests break.

**Tech Stack:** Python 3, NumPy, pytest, Stable-Baselines3 / sb3-contrib MaskablePPO. All commands run from repo root `c:\Users\student\Desktop\sudoku_old`.

**Spec:** [docs/superpowers/specs/2026-05-15-apprentice-tried-bad-elim-design.md](../specs/2026-05-15-apprentice-tried-bad-elim-design.md) (committed `7e11f54`).

**Predecessor:** [docs/superpowers/specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md](../specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md). This change addresses the predecessor spec's §4.3 risk now that it's been observed in training.

---

## File Structure

**Modified files (production code):**
- `apprentice/env/sudoku_gym_env.py` — 3 edit sites:
  - `__init__` (around line 86, before `self._reward_computer = RewardComputer(self)`): initialize `self._tried_bad_elim`.
  - `reset()` (start of the function, after `super().reset(seed=seed)` on line 90): clear `self._tried_bad_elim`. Placement before either of the two reset branches (`options["board"]` path or DB-fetch path) ensures both paths get a fresh empty set.
  - `action_masks()` (lines 165-184): append a mask-exclusion loop after the candidate-based legality loop, before `return mask`.
- `apprentice/env/reward_computer.py` — 1 edit site:
  - `_compute_eliminate` wrong branch (around lines 117-122 post-Task-1 of the predecessor work): add `env._tried_bad_elim.add((r, c, v))` next to the existing `env.wrong_count += 1`.

**Modified files (tests):**
- `apprentice/tests/test_reward_computer.py` — 2 edit sites:
  - `_StubEnv.__init__` (line 7-17): add `self._tried_bad_elim: set[tuple[int, int, int]] = set()` so all existing tests continue to work after the wrong-branch starts writing to it.
  - Append one new test (`test_bad_eliminate_records_triple_in_tried_bad_elim`) after `test_bad_eliminate_terminates_at_max_wrong` (line 209).
- `apprentice/tests/test_env_basic.py` — append 4 new tests at end of file.

**Untouched files (out of scope):**
- `apprentice/train/train.py`, `apprentice/configs/curriculum.json` (the fix is env-side; PPO config and curriculum stay).
- `apprentice/env/obs_helpers.py` (observation channels unchanged).
- `apprentice/eval/*`, `apprentice/model/*`, `apprentice/solver/*`.
- `reasoner/`, `legacy/`, `sb3/`.

---

## Task 1: Env-side plumbing — add `_tried_bad_elim` field and reset clearing

This task adds the state and its lifecycle. After this commit, the field exists but nothing reads or writes to it during normal training — it is dead state. Production behavior is identical to pre-Task-1.

**Files:**
- Modify: `apprentice/env/sudoku_gym_env.py:42-90` (two sites: `__init__` and start of `reset()`)
- Test: `apprentice/tests/test_env_basic.py` (append at end)

- [ ] **Step 1.1: Write failing test `test_tried_bad_elim_initially_empty`**

Append to `apprentice/tests/test_env_basic.py`:

```python
def test_tried_bad_elim_initially_empty(db_path):
    """A fresh SudokuGymEnv has an empty _tried_bad_elim set (per-episode state)."""
    env = SudokuGymEnv(db_path=db_path)
    assert env._tried_bad_elim == set()
```

- [ ] **Step 1.2: Run test, verify it FAILS**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_tried_bad_elim_initially_empty -v
```

Expected: FAIL with `AttributeError: 'SudokuGymEnv' object has no attribute '_tried_bad_elim'`.

- [ ] **Step 1.3: Add `_tried_bad_elim` field to `__init__`**

In `apprentice/env/sudoku_gym_env.py`, locate the block in `__init__` at lines 78-87:

Before:
```python
        self.wrong_count = 0
        self._step_count = 0
        self._current_difficulty = difficulty
        self._episode_reward = 0.0

        # Curriculum control: when set, reset() will fill back cells from
        # solution until only `target_empty` cells remain. None = use puzzle as-is.
        self.target_empty: int | None = None

        self._reward_computer = RewardComputer(self)
```

After (insert one new line + brief comment immediately before `self._reward_computer = ...`):
```python
        self.wrong_count = 0
        self._step_count = 0
        self._current_difficulty = difficulty
        self._episode_reward = 0.0

        # Curriculum control: when set, reset() will fill back cells from
        # solution until only `target_empty` cells remain. None = use puzzle as-is.
        self.target_empty: int | None = None

        # Per-episode set of (r, c, v) triples whose eliminate turned out to be
        # the solution. action_masks() forbids these from being re-tried.
        self._tried_bad_elim: set[tuple[int, int, int]] = set()

        self._reward_computer = RewardComputer(self)
```

- [ ] **Step 1.4: Run test, verify it PASSES**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_tried_bad_elim_initially_empty -v
```

Expected: PASS (1 passed).

- [ ] **Step 1.5: Write failing test `test_reset_clears_tried_bad_elim`**

Append to `apprentice/tests/test_env_basic.py`:

```python
def test_reset_clears_tried_bad_elim(db_path):
    """reset() clears the per-episode tried-bad-elim set so episodes don't
    inherit stale wrong-elim records from prior episodes."""
    env = SudokuGymEnv(db_path=db_path)
    env._tried_bad_elim.add((0, 0, 1))
    env._tried_bad_elim.add((5, 5, 4))
    assert len(env._tried_bad_elim) == 2
    env.reset(seed=42)
    assert env._tried_bad_elim == set()
```

- [ ] **Step 1.6: Run test, verify it FAILS**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_reset_clears_tried_bad_elim -v
```

Expected: FAIL at `assert env._tried_bad_elim == set()` — the set is still `{(0, 0, 1), (5, 5, 4)}` because `reset()` does not yet clear it.

- [ ] **Step 1.7: Add reset clearing**

In `apprentice/env/sudoku_gym_env.py`, locate the start of `reset()` at line 89:

Before:
```python
    def reset(self, *, seed=None, options=None, _retries=0):
        super().reset(seed=seed)

        if options is not None and "board" in options:
```

After (insert one new line + brief comment immediately after `super().reset(seed=seed)`, before the `if options is not None` branch):
```python
    def reset(self, *, seed=None, options=None, _retries=0):
        super().reset(seed=seed)

        # Per-episode state: clear before either reset branch decides the board.
        self._tried_bad_elim = set()

        if options is not None and "board" in options:
```

(Using rebind `= set()` instead of `.clear()` makes the field robust even if a future code path replaces the set with another object; both work but rebind is one fewer mutation type to reason about.)

- [ ] **Step 1.8: Run test, verify it PASSES**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_reset_clears_tried_bad_elim -v
```

Expected: PASS (1 passed).

- [ ] **Step 1.9: Run both new tests + the rest of test_env_basic.py to confirm no regression**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py -v
```

Expected: all tests pass, including the two new ones. (Original count was 25 tests; should now be 27.)

- [ ] **Step 1.10: Commit**

Stage exactly the two files:
```
git -C "c:/Users/student/Desktop/sudoku_old" add apprentice/env/sudoku_gym_env.py apprentice/tests/test_env_basic.py
git -C "c:/Users/student/Desktop/sudoku_old" diff --cached --stat
```

Expected: 2 files changed.

Commit:
```
git -C "c:/Users/student/Desktop/sudoku_old" commit -m "$(cat <<'EOF'
feat(apprentice): env plumbing for per-episode tried-bad-elim set

Add `_tried_bad_elim: set[tuple[int, int, int]]` to SudokuGymEnv,
initialised empty in __init__ and cleared at the start of reset() (before
either reset branch decides the board, so options-board and DB-fetch
paths both get a fresh empty set).

No consumer yet — this is dead state until the reward computer writes to
it (in the next commit) and action_masks() reads from it. Training
behavior unchanged.

Spec: docs/superpowers/specs/2026-05-15-apprentice-tried-bad-elim-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Writer + reader — wrong-elim records to set, mask excludes

This task wires the writer in `RewardComputer._compute_eliminate`'s wrong branch and the reader in `action_masks()`. After this commit, the loop fix is active.

**Files:**
- Modify: `apprentice/env/reward_computer.py:117-122` (1 added line in wrong branch)
- Modify: `apprentice/env/sudoku_gym_env.py:165-184` (mask exclusion loop)
- Modify: `apprentice/tests/test_reward_computer.py:7-17` (`_StubEnv.__init__` adds the field)
- Modify: `apprentice/tests/test_reward_computer.py` (append 1 new test after `test_bad_eliminate_terminates_at_max_wrong`)
- Modify: `apprentice/tests/test_env_basic.py` (append 2 new tests at end)

- [ ] **Step 2.1: Update `_StubEnv` to mirror the new env field**

In `apprentice/tests/test_reward_computer.py`, replace lines 7-17:

Before:
```python
class _StubEnv:
    """Minimal env-like object the RewardComputer needs."""
    def __init__(self, board, solution, candidates):
        self.board = board.astype(np.int8).copy()
        self.solution = solution.astype(np.int8).copy()
        self.candidates_cache = candidates
        self.candidate_count_grid = np.zeros((9, 9), dtype=np.int8)
        for r in range(9):
            for c in range(9):
                self.candidate_count_grid[r, c] = len(candidates[r][c])
        self.wrong_count = 0
```

After:
```python
class _StubEnv:
    """Minimal env-like object the RewardComputer needs."""
    def __init__(self, board, solution, candidates):
        self.board = board.astype(np.int8).copy()
        self.solution = solution.astype(np.int8).copy()
        self.candidates_cache = candidates
        self.candidate_count_grid = np.zeros((9, 9), dtype=np.int8)
        for r in range(9):
            for c in range(9):
                self.candidate_count_grid[r, c] = len(candidates[r][c])
        self.wrong_count = 0
        self._tried_bad_elim: set[tuple[int, int, int]] = set()
```

- [ ] **Step 2.2: Run all existing test_reward_computer.py tests to confirm `_StubEnv` change is non-breaking**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py -v
```

Expected: 14 passed (the post-predecessor-Task-2 count). The `_StubEnv` addition is field-only; no test logic changes yet.

- [ ] **Step 2.3: Write failing test `test_bad_eliminate_records_triple_in_tried_bad_elim`**

In `apprentice/tests/test_reward_computer.py`, append immediately after the existing `test_bad_eliminate_terminates_at_max_wrong` function (which ends around line 220):

```python
def test_bad_eliminate_records_triple_in_tried_bad_elim():
    """A wrong eliminate (v == solution[r,c]) records the triple in
    env._tried_bad_elim so action_masks() can forbid re-trying it (see spec §4.2)."""
    sol = _solved_grid()
    board = sol.copy()
    board[5, 5] = 0  # solution[5,5] = 4
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    assert env._tried_bad_elim == set()
    rc.compute("eliminate", 5, 5, 4)  # wrong: 4 IS the solution
    assert (5, 5, 4) in env._tried_bad_elim
    assert len(env._tried_bad_elim) == 1
```

- [ ] **Step 2.4: Run test, verify it FAILS**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_bad_eliminate_records_triple_in_tried_bad_elim -v
```

Expected: FAIL at `assert (5, 5, 4) in env._tried_bad_elim` — the production code does not yet write to the set.

- [ ] **Step 2.5: Add `env._tried_bad_elim.add((r, c, v))` to the wrong-eliminate branch**

In `apprentice/env/reward_computer.py`, locate the `_compute_eliminate` function. The wrong branch (after the predecessor's Task 1 commit) looks like:

Before:
```python
    def _compute_eliminate(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_bad = (int(v) == int(env.solution[r, c]))

        if is_bad:
            # Penalty only — do NOT remove the solution candidate, otherwise
            # (r,c) becomes unsolvable for the rest of the episode.
            env.wrong_count += 1
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated
```

After (insert one new line + brief comment immediately after `env.wrong_count += 1`):
```python
    def _compute_eliminate(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_bad = (int(v) == int(env.solution[r, c]))

        if is_bad:
            # Penalty only — do NOT remove the solution candidate, otherwise
            # (r,c) becomes unsolvable for the rest of the episode.
            env.wrong_count += 1
            # Record the triple so action_masks() forbids re-trying it this episode.
            env._tried_bad_elim.add((r, c, v))
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated
```

- [ ] **Step 2.6: Run test, verify it PASSES**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_bad_eliminate_records_triple_in_tried_bad_elim -v
```

Expected: PASS (1 passed).

- [ ] **Step 2.7: Run all test_reward_computer.py tests to confirm no regression**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py -v
```

Expected: 15 passed (14 prior + 1 new).

- [ ] **Step 2.8: Write failing test `test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate`**

Append to `apprentice/tests/test_env_basic.py`:

```python
def test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate(db_path):
    """After a wrong eliminate of (r, c, v) (v == solution[r,c]), action_masks()
    must forbid eliminate(r, c, v) on subsequent steps."""
    env = SudokuGymEnv(db_path=db_path)
    env.reset(seed=42)
    # Find an empty cell.
    target = None
    for r in range(9):
        for c in range(9):
            if env.board[r, c] == 0:
                target = (r, c)
                break
        if target is not None:
            break
    assert target is not None, "no empty cell to test against"
    r, c = target
    v = int(env.solution[r, c])
    # Submit a wrong eliminate at the cell's solution value.
    action = SudokuGymEnv.encode("eliminate", r, c, v)
    env.step(action)
    mask = env.action_masks()
    base = r * 81 + c * 9 + (v - 1)
    assert mask[729 + base] == False, "eliminate(r,c,v) should be masked after one wrong eliminate"
```

- [ ] **Step 2.9: Write failing test `test_action_masks_still_allows_fill_for_tried_bad_elim`**

Append to `apprentice/tests/test_env_basic.py`:

```python
def test_action_masks_still_allows_fill_for_tried_bad_elim(db_path):
    """After a wrong eliminate of (r, c, v), fill(r, c, v) — which is the
    CORRECT fill at that cell — must remain available in the mask."""
    env = SudokuGymEnv(db_path=db_path)
    env.reset(seed=42)
    target = None
    for r in range(9):
        for c in range(9):
            if env.board[r, c] == 0:
                target = (r, c)
                break
        if target is not None:
            break
    assert target is not None, "no empty cell to test against"
    r, c = target
    v = int(env.solution[r, c])
    action = SudokuGymEnv.encode("eliminate", r, c, v)
    env.step(action)
    mask = env.action_masks()
    base = r * 81 + c * 9 + (v - 1)
    assert mask[base] == True, "fill(r,c,v) should remain available — v is the correct solution"
```

- [ ] **Step 2.10: Run both new tests, verify they FAIL**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate apprentice/tests/test_env_basic.py::test_action_masks_still_allows_fill_for_tried_bad_elim -v
```

Expected failure pattern:
- `test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate`: FAIL at `assert mask[729 + base] == False` — `action_masks()` does not yet read from `_tried_bad_elim`, so the mask still says True.
- `test_action_masks_still_allows_fill_for_tried_bad_elim`: this test will likely PASS even before the fix, because the mask was always True for the fill of a candidate `v`. Note: a PASS here is acceptable in Step 2.10 because the test asserts a property that should still hold after the fix is in place — its purpose is to guard against a "naive fix" that masks BOTH fill and eliminate. Document this in the report.

If both tests fail unexpectedly (e.g., `test_action_masks_still_allows_fill...` fails too), investigate before proceeding.

- [ ] **Step 2.11: Add the mask-exclusion loop to `action_masks()`**

In `apprentice/env/sudoku_gym_env.py`, locate `action_masks()` at lines 165-184. Replace the function body:

Before:
```python
    def action_masks(self) -> np.ndarray:
        """Legality mask over the 1458-action space.

        Both fill and eliminate operate on (r, c, v) where v is currently
        a candidate at empty cell (r, c). Filling a non-empty cell is illegal;
        eliminating a digit that's not in candidates is a no-op so we mask it
        out too. The CORRECTNESS of the action (whether v matches solution)
        is NOT checked here — that would leak the solution; correctness is
        evaluated by RewardComputer and contributes to wrong_count instead.
        """
        mask = np.zeros(self.N_ACTIONS, dtype=bool)
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    continue
                for v in self.candidates_cache[r][c]:
                    base = r * 81 + c * 9 + (v - 1)
                    mask[base] = True                       # fill
                    mask[self._ELIM_OFFSET + base] = True   # eliminate
        return mask
```

After (append the exclusion loop just before `return mask`):
```python
    def action_masks(self) -> np.ndarray:
        """Legality mask over the 1458-action space.

        Both fill and eliminate operate on (r, c, v) where v is currently
        a candidate at empty cell (r, c). Filling a non-empty cell is illegal;
        eliminating a digit that's not in candidates is a no-op so we mask it
        out too. The CORRECTNESS of the action (whether v matches solution)
        is NOT checked here — that would leak the solution; correctness is
        evaluated by RewardComputer and contributes to wrong_count instead.

        After the candidate-based legality pass, also forbid any (r, c, v)
        eliminate that has already failed this episode. The fill half for the
        same triple is left True — it's the correct fill at that cell, and
        we want the policy to be able to choose it.
        """
        mask = np.zeros(self.N_ACTIONS, dtype=bool)
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    continue
                for v in self.candidates_cache[r][c]:
                    base = r * 81 + c * 9 + (v - 1)
                    mask[base] = True                       # fill
                    mask[self._ELIM_OFFSET + base] = True   # eliminate
        for (r, c, v) in self._tried_bad_elim:
            base = r * 81 + c * 9 + (v - 1)
            mask[self._ELIM_OFFSET + base] = False          # forbid repeat
        return mask
```

- [ ] **Step 2.12: Run the two new mask tests, verify they PASS**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py::test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate apprentice/tests/test_env_basic.py::test_action_masks_still_allows_fill_for_tried_bad_elim -v
```

Expected: 2 passed.

- [ ] **Step 2.13: Run full test_env_basic.py + test_reward_computer.py to confirm no regression**

Run:
```
python -m pytest apprentice/tests/test_env_basic.py apprentice/tests/test_reward_computer.py -v
```

Expected: all pass. Counts:
- `test_env_basic.py`: 29 (25 original + 2 from Task 1 + 2 from Task 2)
- `test_reward_computer.py`: 15 (14 prior + 1 from Task 2)
- Total: 44

- [ ] **Step 2.14: Commit**

Stage exactly the four files:
```
git -C "c:/Users/student/Desktop/sudoku_old" add apprentice/env/sudoku_gym_env.py apprentice/env/reward_computer.py apprentice/tests/test_reward_computer.py apprentice/tests/test_env_basic.py
git -C "c:/Users/student/Desktop/sudoku_old" diff --cached --stat
```

Expected: 4 files changed.

Commit:
```
git -C "c:/Users/student/Desktop/sudoku_old" commit -m "$(cat <<'EOF'
feat(apprentice): wire tried-bad-elim — wrong-elim records, mask excludes

Wrong eliminate (v == solution[r,c]) now adds (r, c, v) to
env._tried_bad_elim. action_masks() reads the set and forbids
eliminate(r, c, v) on subsequent steps within the same episode. The fill
half for the same triple stays True so the policy can pick the correct
fill (v IS the solution at that cell).

Closes the deterministic-loop failure mode where the policy kept
picking the same wrong eliminate until wrong_count == 20. Obs shape,
action space, network architecture, and checkpoint format unchanged.

Spec: docs/superpowers/specs/2026-05-15-apprentice-tried-bad-elim-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Full apprentice regression

Confirm the full apprentice test suite passes after Task 1 + Task 2. No new code or commits — verification only.

**Files:** none modified.

- [ ] **Step 3.1: Run full apprentice test suite**

Run:
```
python -m pytest apprentice/tests/ -v
```

Expected: every test passes. Count delta vs. pre-Task-1 baseline:
- `test_env_basic.py`: +4 (29 total, was 25)
- `test_reward_computer.py`: +1 (15 total, was 14)
- Other files: unchanged
- Pre-task baseline was `178 passed, 1 skipped`; new total should be `183 passed, 1 skipped`.

The single pre-existing skip is `test_techniques/test_trial_error.py::test_te_returns_none_when_all_candidates_consistent` — not related to this work.

If any unexpected failure appears, STOP and report — likely indicates a hidden dependency on either the pre-fix wrong-elim behavior or on `action_masks()`'s prior mask layout.

- [ ] **Step 3.2: (Optional) Short training smoke test**

You may SKIP this step and still complete Task 3. To run it:

List the latest checkpoint:
```
ls apprentice/models/apprentice_ckpt_*_steps.zip
```

Pick the highest `_N_steps.zip` value as `N`. Compute `N + 4096` and run:
```
python -m apprentice.train.train --load-model auto --timesteps <N + 4096>
```

Example: if highest is `apprentice_ckpt_300000_steps.zip`, run `--timesteps 304096`.

Expected:
- `[apprentice] Resuming from: ...apprentice_ckpt_<N>_steps.zip` prints.
- `[train] Loaded VecNormalize from ...` prints if a sidecar exists.
- At least one `rollout/ep_rew_mean` line is logged.
- Process exits cleanly via `[apprentice] Saved -> ...apprentice_latest.zip (vecnorm + curriculum)`.
- No `RuntimeError`, no traceback, no `size mismatch`.

If the smoke test fails to start within ~2 minutes, interrupt and note as a concern.

---

## Self-Review Summary

- **Spec coverage:** §4.1 (env state) → Task 1 Steps 1.3, 1.7; §4.2 (wrong-elim writes to set) → Task 2 Step 2.5; §4.3 (mask exclusion loop) → Task 2 Step 2.11; §4.4 behavioral table rows all covered by the two-task split; §5 information leakage acknowledgment is in the spec only (no code implication, no task needed); §6.1 implementation surface matches Task 1+2 exactly; §6.2 test plan: `_StubEnv` update → Task 2 Step 2.1, reward_computer test → Step 2.3, env_basic tests → Steps 1.1/1.5/2.8/2.9; §6.3 untouched-tests guarantee → Task 3 Step 3.1; §7 compatibility (no obs/action/checkpoint change) is structural and verified by checkpoint resume in Step 3.2.
- **Placeholder scan:** every code block contains literal code; every command shows the actual invocation; every "Expected" line states observable output. No "similar to above", no "TBD".
- **Type consistency:** `_tried_bad_elim: set[tuple[int, int, int]]` typed identically in `__init__` (Task 1), `_StubEnv` (Task 2), and reset clearing (Task 1). The triple element ordering `(r, c, v)` is consistent across writer (Step 2.5), reader (Step 2.11), and tests (Steps 2.3, 2.8, 2.9). `_ELIM_OFFSET` and the `729 + base` literal in tests both encode the same offset; Step 2.11 uses `self._ELIM_OFFSET` consistent with the surrounding code, Steps 2.8 and 2.9 use the literal `729` consistent with predecessor-spec test patterns.
- **Frequent commits:** two production commits (env plumbing, then writer+reader), one verification task with no commit. Each commit is bisect-friendly: plumbing alone is a no-op behaviorally, so a regression bisects to Task 2.
