# Apprentice Non-Destructive Wrong Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make wrong fill and wrong eliminate in `apprentice/env/reward_computer.py` penalty-only — they no longer mutate `board` or destroy related-cell candidate sets, so single mistakes can no longer cascade into forced `wrong_count == 20` terminations.

**Architecture:** Mirror the change already shipped in `reasoner/` (commits `1e778b2` wrong-eliminate, `d21629a` wrong-fill). Wrong fill keeps `board[r,c] = 0` and only discards `v` from `(r,c)`'s own candidate set; wrong eliminate makes no state change at all. Observation shape, action space, network architecture, checkpoint format, `MAX_WRONG`, and all reward magnitudes are unchanged. Curriculum (`CurriculumController` / `CurriculumCallback` / `curriculum.json`) is untouched.

**Tech Stack:** Python 3, NumPy, pytest, Stable-Baselines3, sb3-contrib MaskablePPO. Run from repo root.

**Spec:** [docs/superpowers/specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md](../specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md) (committed `5b88758`).

**Reference implementation:** `reasoner/env/reward_computer.py` after commits `1e778b2` and `d21629a`. The apprentice edit is identical except for the module path.

---

## File Structure

**Modified files (production code):**
- `apprentice/env/reward_computer.py` — two wrong-branch edits in `_compute_fill` (~5 lines) and `_compute_eliminate` (1 line removal). Reasoner-side reference: [reasoner/env/reward_computer.py:85-92](../../../reasoner/env/reward_computer.py#L85-L92), [reasoner/env/reward_computer.py:115-119](../../../reasoner/env/reward_computer.py#L115-L119).

**Modified files (tests):**
- `apprentice/tests/test_reward_computer.py` — rename `test_bad_eliminate_removes_solution_value_gets_minus_one` → `test_bad_eliminate_preserves_solution_candidate` and flip the candidate-set assertion; add three new wrong-fill tests (`test_wrong_fill_does_not_commit_board`, `test_wrong_fill_locally_removes_value_from_candidates`, `test_wrong_fill_does_not_damage_related_cells`); also fix the stale `test_correct_fill_completes_board_gives_plus_20` assertion (currently asserts `20.0` but working-tree code returns `50.0`).

**Untouched files (out of scope):**
- `apprentice/env/sudoku_gym_env.py` (observation, action mask, `max_wrong_fills` default of 20 all stay)
- `apprentice/train/train.py` (wrong-action behavior is env-side; PPO config stays)
- `apprentice/configs/curriculum.json`
- `reasoner/`, `legacy/`, `sb3/`

**Working-tree note:** the repo's working tree currently has three unrelated uncommitted changes alongside this work — `apprentice/env/reward_computer.py` raises board-complete reward from `+20` to `+50`, `apprentice/train/train.py` lowers `ent_coef` from `0.05` to `0.01`, and `apprentice/configs/curriculum.json` widens `tolerance_band` from `[0.55, 0.85]` to `[0.50, 0.85]`. Task 0 captures these in a separate prep commit so the wrong-action commits stay focused on the spec.

---

## Task 0: Prep — isolate unrelated working-tree changes

The current working tree of `apprentice/env/reward_computer.py` has a `+20 → +50` change at the board-complete branch (line ~98). The test `test_correct_fill_completes_board_gives_plus_20` still asserts `20.0`, so it is currently failing. Before any wrong-action work, commit those orthogonal tweaks (+ fix the stale test assertion) as a separate commit so the wrong-action diff in Tasks 1 and 2 is minimal and reviewable.

**Files:**
- Modify: `apprentice/tests/test_reward_computer.py:52-62`
- Already-modified (working tree, will be staged): `apprentice/env/reward_computer.py`, `apprentice/train/train.py`, `apprentice/configs/curriculum.json`

- [ ] **Step 0.1: Confirm the three working-tree edits are exactly what the spec describes**

Run:
```
git -C "c:/Users/student/Desktop/sudoku_old" diff -- apprentice/env/reward_computer.py apprentice/train/train.py apprentice/configs/curriculum.json
```

Expected output (the three edits, in order):
- `apprentice/env/reward_computer.py`: `-return 20.0, True` / `+return 50.0, True` in `_compute_fill`'s board-complete branch.
- `apprentice/train/train.py`: `-ent_coef=0.05,` / `+ent_coef=0.01,` inside the fresh-model `SudokuMaskablePPO(...)` block.
- `apprentice/configs/curriculum.json`: `tolerance_band` array changes from `[0.55, 0.85]` to `[0.50, 0.85]`.

If any other apprentice-tree edit shows up here, STOP and ask before proceeding — Task 0 only commits these three.

- [ ] **Step 0.2: Fix the stale assertion in the board-complete test**

In `apprentice/tests/test_reward_computer.py`, change the assertion at line 62:

Before:
```python
def test_correct_fill_completes_board_gives_plus_20():
    sol = _solved_grid()
    board = sol.copy()
    board[8, 8] = 0  # one empty cell
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    # solution[8,8] == 9
    reward, terminated = rc.compute("fill", 8, 8, 9)
    assert terminated
    assert reward == pytest.approx(20.0)
```

After:
```python
def test_correct_fill_completes_board_gives_plus_50():
    sol = _solved_grid()
    board = sol.copy()
    board[8, 8] = 0  # one empty cell
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    # solution[8,8] == 9
    reward, terminated = rc.compute("fill", 8, 8, 9)
    assert terminated
    assert reward == pytest.approx(50.0)
```

(Function rename mirrors the new constant. Only this one test changes in Step 0.2; everything else is preserved.)

- [ ] **Step 0.3: Run the renamed test to confirm it now passes against the working-tree code**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_correct_fill_completes_board_gives_plus_50 -v
```

Expected: PASS (1 passed). If FAIL, check that `apprentice/env/reward_computer.py` still returns `50.0` in its board-complete branch.

- [ ] **Step 0.4: Stage and commit the three prep edits**

Stage explicitly — do NOT use `git add -A` or `git add .`:
```
git -C "c:/Users/student/Desktop/sudoku_old" add apprentice/env/reward_computer.py apprentice/train/train.py apprentice/configs/curriculum.json apprentice/tests/test_reward_computer.py
```

Verify the staged change is only the four files above:
```
git -C "c:/Users/student/Desktop/sudoku_old" status
git -C "c:/Users/student/Desktop/sudoku_old" diff --cached --stat
```

Expected staged files:
- `apprentice/configs/curriculum.json`
- `apprentice/env/reward_computer.py`
- `apprentice/tests/test_reward_computer.py`
- `apprentice/train/train.py`

Commit:
```
git -C "c:/Users/student/Desktop/sudoku_old" commit -m "$(cat <<'EOF'
feat(apprentice): bump board-complete reward to +50, lower ent_coef to 0.01

Three small tuning tweaks that have been sitting in the working tree:
- reward_computer: board-complete reward 20 -> 50 (sharpens terminal signal).
- train.py: ent_coef 0.05 -> 0.01 (less exploration noise after curriculum stabilised).
- curriculum.json: tolerance_band 0.55 -> 0.50 on lower bound (slightly more lenient sweet-spot).

Also renames the corresponding unit test to keep its name consistent with the new constant.

Isolated from the upcoming non-destructive wrong-action change so each
diff stays focused.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 0.5: Verify clean tree for the wrong-action files**

Run:
```
git -C "c:/Users/student/Desktop/sudoku_old" status --porcelain apprentice/env/reward_computer.py apprentice/tests/test_reward_computer.py
```

Expected: empty output. (Other files such as `data/puzzle_pool.db*` and `apprentice/demo/` may still show — they are unrelated to this plan and stay untouched.)

---

## Task 1: TDD wrong eliminate — preserve solution candidate

Mirror commit `1e778b2` from `reasoner/`. Wrong eliminate (where `v == solution[r,c]`) must NOT call `_discard_candidate(r, c, v)`; otherwise the cell becomes unsolvable for the rest of the episode.

**Files:**
- Modify test: `apprentice/tests/test_reward_computer.py:193-206` (rename + flip assertion)
- Modify prod: `apprentice/env/reward_computer.py:112-116` (drop one line)

- [ ] **Step 1.1: Rename and flip the existing wrong-eliminate test**

In `apprentice/tests/test_reward_computer.py`, replace the function at line 193:

Before:
```python
def test_bad_eliminate_removes_solution_value_gets_minus_one():
    """Eliminating v == solution[r,c] is wrong; -1 + wrong_count++."""
    sol = _solved_grid()
    board = sol.copy()
    board[5, 5] = 0  # solution[5,5] = 4
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    reward, terminated = rc.compute("eliminate", 5, 5, 4)
    assert reward == -1.0
    assert env.wrong_count == 1
    assert not terminated
    # The candidate IS removed (agent lives with the bad eliminate)
    assert 4 not in env.candidates_cache[5][5]
```

After:
```python
def test_bad_eliminate_preserves_solution_candidate():
    """Eliminating v == solution[r,c] is wrong; -1 + wrong_count++, but the
    solution candidate is NOT removed — otherwise (r,c) becomes unsolvable
    for the rest of the episode (see spec §1.2)."""
    sol = _solved_grid()
    board = sol.copy()
    board[5, 5] = 0  # solution[5,5] = 4
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    reward, terminated = rc.compute("eliminate", 5, 5, 4)
    assert reward == -1.0
    assert env.wrong_count == 1
    assert not terminated
    # The solution candidate IS preserved — cell remains solvable.
    assert 4 in env.candidates_cache[5][5]
```

- [ ] **Step 1.2: Run the renamed test to verify it FAILS against current code**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_bad_eliminate_preserves_solution_candidate -v
```

Expected: FAIL on `assert 4 in env.candidates_cache[5][5]` — current `_compute_eliminate` calls `_discard_candidate(r, c, v)` which removes `4` from the set. The error message should contain `AssertionError` near the final assertion.

- [ ] **Step 1.3: Edit the wrong-eliminate branch in `_compute_eliminate`**

In `apprentice/env/reward_computer.py`, replace lines 108-116 (the `if is_bad:` block):

Before:
```python
    def _compute_eliminate(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_bad = (int(v) == int(env.solution[r, c]))

        if is_bad:
            env.wrong_count += 1
            self._discard_candidate(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated
```

After:
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

The diff is a single removed line (`self._discard_candidate(r, c, v)`) plus a two-line comment explaining why.

- [ ] **Step 1.4: Run the test to verify it PASSES**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_bad_eliminate_preserves_solution_candidate -v
```

Expected: PASS (1 passed).

- [ ] **Step 1.5: Run the related wrong-eliminate tests to confirm no regression**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_bad_eliminate_terminates_at_max_wrong apprentice/tests/test_reward_computer.py::test_valid_eliminate_not_matching_solver_gets_small_positive apprentice/tests/test_reward_computer.py::test_eliminate_leaves_board_value_unchanged -v
```

Expected: 3 passed. (`test_bad_eliminate_terminates_at_max_wrong` doesn't assert on the candidate set, only `wrong_count` and `terminated`, so the new behavior keeps it passing.)

- [ ] **Step 1.6: Commit**

Stage exactly the two files:
```
git -C "c:/Users/student/Desktop/sudoku_old" add apprentice/env/reward_computer.py apprentice/tests/test_reward_computer.py
git -C "c:/Users/student/Desktop/sudoku_old" diff --cached --stat
```

Expected: 2 files changed (1 line removed + 2 comment lines in reward_computer.py; 4 lines around the renamed test in test_reward_computer.py).

Commit:
```
git -C "c:/Users/student/Desktop/sudoku_old" commit -m "$(cat <<'EOF'
feat(apprentice): non-destructive wrong eliminate

A wrong eliminate (v == solution[r,c]) used to discard the solution
candidate, making (r,c) unsolvable for the rest of the episode and
forcing the agent to burn wrong-action budget on cells with no valid
moves. Penalty + wrong_count++ remain; the candidate stays.

Spec: docs/superpowers/specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md
Mirrors reasoner-side commit 1e778b2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: TDD wrong fill — keep board empty, only local discard

Mirror commit `d21629a` from `reasoner/`. Wrong fill must NOT write the bad value into `board[r,c]` and must NOT propagate `discard(v)` to row/col/box neighbors. It only discards `v` locally from `(r,c)`'s own candidate set.

**Files:**
- Modify test: `apprentice/tests/test_reward_computer.py` — insert three new tests immediately after `test_wrong_fill_terminates_at_max_wrong` (currently ends at line 90).
- Modify prod: `apprentice/env/reward_computer.py:81-89` (replace `_commit_fill(r, c, v)` with local discard).

- [ ] **Step 2.1: Add three new wrong-fill tests**

In `apprentice/tests/test_reward_computer.py`, insert the following three test functions immediately after `test_wrong_fill_terminates_at_max_wrong` (and before `test_naked_single_fill_at_either_target_gets_tech1_bonus`):

```python
def test_wrong_fill_does_not_commit_board():
    """Wrong fill must not write v into board[r,c] — the cell stays empty so
    the agent can try other values in subsequent steps (see spec §1.1)."""
    sol = _solved_grid()
    board = sol.copy()
    board[8, 8] = 0  # solution[8,8] = 9
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    rc = RewardComputer(env)
    # Wrong: agent fills 5 when solution is 9.
    rc.compute("fill", 8, 8, 5)
    assert env.board[8, 8] == 0


def test_wrong_fill_locally_removes_value_from_candidates():
    """After a wrong fill of v at (r,c), v is discarded from (r,c)'s candidate
    set so the action mask blocks repeating the same wrong fill at that cell.
    Other candidates at (r,c) remain available."""
    sol = _solved_grid()
    board = sol.copy()
    board[8, 8] = 0  # solution[8,8] = 9
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    # Force 5 to be in (8,8)'s candidates so we can verify removal.
    env.candidates_cache[8][8] = {5, 9}
    env.candidate_count_grid[8, 8] = 2
    rc = RewardComputer(env)
    rc.compute("fill", 8, 8, 5)  # wrong (solution is 9)
    assert 5 not in env.candidates_cache[8][8]
    assert 9 in env.candidates_cache[8][8]  # solution still available
    assert env.candidate_count_grid[8, 8] == 1


def test_wrong_fill_does_not_damage_related_cells():
    """Wrong fill of v at (r,c) must NOT remove v from any related cell's
    candidates (same row, column, or box). Under the old behavior _commit_fill
    propagated v removal to all related empty cells, destroying their
    solvability when v was actually their correct solution somewhere."""
    sol = _solved_grid()
    board = sol.copy()
    board[0, 0] = 0  # solution[0,0] = 5
    board[0, 1] = 0  # same row as (0,0)
    board[1, 0] = 0  # same column as (0,0)
    board[2, 2] = 0  # same box as (0,0)
    cands = _candidates_from_board(board)
    env = _StubEnv(board, sol, cands)
    # Force 7 into (0,0)'s candidates so the wrong fill is over a real candidate.
    # Also force 7 into each related cell's candidates so we can detect
    # propagation (if any).
    for (r, c) in [(0, 0), (0, 1), (1, 0), (2, 2)]:
        env.candidates_cache[r][c].add(7)
        env.candidate_count_grid[r, c] = len(env.candidates_cache[r][c])
    rc = RewardComputer(env)
    rc.compute("fill", 0, 0, 7)  # wrong: solution[0,0] = 5
    # Local removal at (0,0) is allowed.
    assert 7 not in env.candidates_cache[0][0]
    # Related cells must STILL contain 7 — no propagation.
    assert 7 in env.candidates_cache[0][1], "row neighbor lost candidate"
    assert 7 in env.candidates_cache[1][0], "col neighbor lost candidate"
    assert 7 in env.candidates_cache[2][2], "box neighbor lost candidate"
```

- [ ] **Step 2.2: Run the three new tests to verify they FAIL against current code**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_wrong_fill_does_not_commit_board apprentice/tests/test_reward_computer.py::test_wrong_fill_locally_removes_value_from_candidates apprentice/tests/test_reward_computer.py::test_wrong_fill_does_not_damage_related_cells -v
```

Expected failure pattern (one assertion failure per test):
- `test_wrong_fill_does_not_commit_board`: FAIL at `assert env.board[8, 8] == 0` — current code commits `5` to `(8,8)`.
- `test_wrong_fill_locally_removes_value_from_candidates`: FAIL at `assert 9 in env.candidates_cache[8][8]` or at `assert env.candidate_count_grid[8, 8] == 1` — current `_commit_fill` clears the entire candidate set for the filled cell.
- `test_wrong_fill_does_not_damage_related_cells`: FAIL at one of the `assert 7 in env.candidates_cache[...]` lines — current `_commit_fill` propagates `discard(v)` to row/col/box.

Output should show "3 failed" with the assertion lines above. Do NOT proceed if the failures look different — investigate first.

- [ ] **Step 2.3: Edit the wrong-fill branch in `_compute_fill`**

In `apprentice/env/reward_computer.py`, replace lines 81-89 (the `if not is_correct:` block inside `_compute_fill`):

Before:
```python
    def _compute_fill(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_correct = (int(v) == int(env.solution[r, c]))

        if not is_correct:
            env.wrong_count += 1
            self._commit_fill(r, c, v)
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated
```

After:
```python
    def _compute_fill(self, r: int, c: int, v: int) -> tuple[float, bool]:
        env = self._env
        is_correct = (int(v) == int(env.solution[r, c]))

        if not is_correct:
            # Penalty only — do NOT commit the wrong value to the board, and do
            # NOT propagate candidate removal to related cells. The solution is
            # unique, so v is known wrong at (r,c) — local discard is honest and
            # blocks the same wrong fill via the action mask next step.
            env.wrong_count += 1
            env.candidates_cache[r][c].discard(v)
            env.candidate_count_grid[r, c] = len(env.candidates_cache[r][c])
            terminated = env.wrong_count >= MAX_WRONG
            return -1.0, terminated
```

Net change: `self._commit_fill(r, c, v)` line removed; two lines added (`discard(v)` and `candidate_count_grid` resync); four-line explanatory comment added.

- [ ] **Step 2.4: Run the three new tests to verify they PASS**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_wrong_fill_does_not_commit_board apprentice/tests/test_reward_computer.py::test_wrong_fill_locally_removes_value_from_candidates apprentice/tests/test_reward_computer.py::test_wrong_fill_does_not_damage_related_cells -v
```

Expected: 3 passed.

- [ ] **Step 2.5: Run the related wrong-fill tests to confirm no regression**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py::test_wrong_fill_gets_minus_one_and_continues apprentice/tests/test_reward_computer.py::test_wrong_fill_terminates_at_max_wrong -v
```

Expected: 2 passed. These tests only assert on `reward`, `wrong_count`, and `terminated` — they don't touch `env.board` or `env.candidates_cache`, so the new behavior keeps them passing.

- [ ] **Step 2.6: Commit**

Stage exactly the two files:
```
git -C "c:/Users/student/Desktop/sudoku_old" add apprentice/env/reward_computer.py apprentice/tests/test_reward_computer.py
git -C "c:/Users/student/Desktop/sudoku_old" diff --cached --stat
```

Expected: 2 files changed. Production diff: 1 line removed, ~6 lines added (2 logic + 4 comment) in `reward_computer.py`. Test diff: 3 new tests, ~60 lines added.

Commit:
```
git -C "c:/Users/student/Desktop/sudoku_old" commit -m "$(cat <<'EOF'
feat(apprentice): non-destructive wrong fill

A wrong fill used to (a) write the wrong value into board[r,c], locking
the cell, and (b) remove v from every related cell's candidate set, so
any cell whose correct solution was v became unsolvable. Result: a
single mistake cascaded into forced wrong_count=20 termination.

New behavior: penalty + wrong_count++, plus a local discard(v) from
(r,c)'s own candidate set (which is informationally honest — the
solution is unique). board[r,c] stays 0 so the agent can try other
values. Related cells are not touched.

Spec: docs/superpowers/specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md
Mirrors reasoner-side commit d21629a.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Full apprentice regression

Confirm the wider apprentice suite still passes — none of these tests are supposed to depend on wrong-action commit semantics, but TDD doesn't help if a non-obvious dependency exists.

**Files:** none modified in this task.

- [ ] **Step 3.1: Run the full `apprentice/tests/test_reward_computer.py` file**

Run:
```
python -m pytest apprentice/tests/test_reward_computer.py -v
```

Expected: all tests pass. Total count is 14 (11 original tests, of which two are renamed but still count once, plus 3 new tests from Task 2). Confirm `14 passed` and that none are skipped or xfailed.

- [ ] **Step 3.2: Run the rest of the apprentice test suite**

Run:
```
python -m pytest apprentice/tests/ -v
```

Expected: every test in `apprentice/tests/test_env_basic.py`, `test_candidate_engine.py`, `test_human_solver.py`, `test_obs_helpers.py`, `test_techniques/*`, `test_curriculum_controller.py`, `test_curriculum_callback.py`, `test_ppo_no_bc.py`, `test_imports.py`, `test_label_puzzles.py` passes. If any unexpected failure appears, STOP and report it — it likely means there is a non-obvious dependency on the old wrong-action behavior that the spec missed.

- [ ] **Step 3.3: (Optional) Short training smoke test**

Confirm the env still loads and rolls out without crashing. The simplest invocation: list the latest checkpoint, add ~one PPO rollout (4096 timesteps = `n_envs(8) × n_steps(512)`) to its step count, and pass that number as `--timesteps`.

Run, in order:
```
ls apprentice/models/apprentice_ckpt_*_steps.zip
```

Pick the highest `_N_steps.zip` from the listing — call that `N`. Then compute `N + 4096` (the next-rollout target) and run:
```
python -m apprentice.train.train --load-model auto --timesteps <N + 4096>
```

Example: if the highest checkpoint is `apprentice_ckpt_300000_steps.zip`, run `--timesteps 304096`.

Expected behavior:
- `[apprentice] Resuming from: ...apprentice_ckpt_<N>_steps.zip` prints.
- `[train] Loaded VecNormalize from ...` prints (assuming the sidecar exists).
- At least one `rollout/ep_rew_mean` line is logged to stdout/TensorBoard.
- Process exits cleanly via `[apprentice] Saved -> ...apprentice_latest.zip (vecnorm + curriculum)`.
- No `RuntimeError`, no Python traceback, no `size mismatch` error.

If this step is skipped (e.g. no GPU at hand, or no checkpoint exists yet), the next normal training run will exercise the env end-to-end and any breakage will surface there. Task 3 is considered complete after Step 3.2.

---

## Self-Review Summary

- **Spec coverage:** §1.1 covered by Task 2 (wrong fill non-destructive); §1.2 covered by Task 1 (wrong eliminate non-destructive); §1.3 (downstream cascade) is the consequence both fixes prevent; §1.4 (elim memory note) is observational, no task needed; §4.4 behavioral table aligns with Task 1 + Task 2 outcomes; §5.1 implementation surface → Task 1.3 + Task 2.3; §5.2 test plan → Task 1.1 (rename+flip) + Task 2.1 (three new tests); §5.3 untouched-tests guarantee → Task 3.2; §6 compatibility note about uncommitted `+20→+50` and `ent_coef` → Task 0.
- **Placeholder scan:** every code block contains the actual code; every command shows the actual invocation; every "Expected" line says what the engineer should see; no "similar to above" references.
- **Type consistency:** function/method names match between tasks (`_compute_fill`, `_compute_eliminate`, `_commit_fill`, `_discard_candidate`, `candidates_cache`, `candidate_count_grid`, `wrong_count`, `MAX_WRONG` all consistent with [apprentice/env/reward_computer.py](../../../apprentice/env/reward_computer.py)).
- **Frequent commits:** four commits total — one for prep (Task 0), one per behavior change (Task 1, Task 2), and Task 3 introduces no commits (verification only).
