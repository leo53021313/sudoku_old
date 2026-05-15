# Non-Destructive Wrong Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop the reasoner env from committing wrong-fill values to the board and from removing the solution candidate on wrong eliminates, so the agent can recover from mistakes within an episode instead of cascading into a forced `wrong_count == 20` termination.

**Architecture:** Two surgical edits in `reasoner/env/reward_computer.py` — the wrong-fill branch in `_compute_fill` and the wrong-eliminate branch in `_compute_eliminate`. Wrong fill keeps `board[r,c]=0` and does a local `discard(v)` only (so the same wrong fill is masked out at that cell but related cells are unaffected). Wrong eliminate leaves candidates untouched. Penalty (`-1`), termination (`wrong_count >= MAX_WRONG`), and all correct-action paths are unchanged. No observation, action-space, or checkpoint format changes — existing models load and continue training.

**Tech Stack:** Python, numpy, pytest. Run from repo root: `python -m pytest reasoner/tests/`.

**Spec:** [docs/superpowers/specs/2026-05-15-wrong-action-non-destructive-design.md](docs/superpowers/specs/2026-05-15-wrong-action-non-destructive-design.md)

---

## File Inventory

- Modify: [reasoner/env/reward_computer.py](reasoner/env/reward_computer.py) — `_compute_fill` wrong branch (~5 lines), `_compute_eliminate` wrong branch (~3 lines).
- Modify: [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py) — flip one existing test's assertion, add three new tests.

No other files. No new files.

---

## Task 1: Non-Destructive Wrong Eliminate

**Files:**
- Modify: [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py) — rename + flip `test_bad_eliminate_removes_solution_value_gets_minus_one`
- Modify: [reasoner/env/reward_computer.py:108-116](reasoner/env/reward_computer.py#L108-L116) — `_compute_eliminate` wrong branch

- [ ] **Step 1: Flip the existing test's assertion to the new expected behavior**

Open [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py). Find this block (around line 193-206):

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

Replace it with:

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

- [ ] **Step 2: Run the modified test, confirm it fails on the assertion**

Run: `python -m pytest reasoner/tests/test_reward_computer.py::test_bad_eliminate_preserves_solution_candidate -v`

Expected: FAIL with `AssertionError: assert 4 in set()` (or similar — the current code discards 4 so the candidate set excludes it).

- [ ] **Step 3: Modify `_compute_eliminate` wrong branch to not discard**

Open [reasoner/env/reward_computer.py](reasoner/env/reward_computer.py). Find this block at lines 108-116:

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

Replace with (remove the `_discard_candidate` line, update the comment):

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

- [ ] **Step 4: Re-run the test, confirm it passes**

Run: `python -m pytest reasoner/tests/test_reward_computer.py::test_bad_eliminate_preserves_solution_candidate -v`

Expected: PASS.

- [ ] **Step 5: Run the full reward_computer test file to confirm no regressions**

Run: `python -m pytest reasoner/tests/test_reward_computer.py -v`

Expected: all tests PASS. Pay particular attention to `test_bad_eliminate_terminates_at_max_wrong` (still passes — termination logic unchanged), `test_valid_eliminate_not_matching_solver_gets_small_positive` (still passes — correct-elim branch unchanged), `test_eliminate_leaves_board_value_unchanged` (still passes — neither branch touches board).

- [ ] **Step 6: Run the full reasoner test suite to confirm no broader regressions**

Run: `python -m pytest reasoner/tests/`

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add reasoner/env/reward_computer.py reasoner/tests/test_reward_computer.py
git commit -m "feat(reasoner): non-destructive wrong eliminate

A wrong eliminate (v == solution[r,c]) used to discard the solution
candidate, making (r,c) unsolvable for the rest of the episode and
forcing the agent to burn wrong-action budget on cells with no valid
moves. Penalty + wrong_count++ remain; the candidate stays.

Spec: docs/superpowers/specs/2026-05-15-wrong-action-non-destructive-design.md"
```

---

## Task 2: Non-Destructive Wrong Fill

**Files:**
- Modify: [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py) — add three new tests
- Modify: [reasoner/env/reward_computer.py:81-89](reasoner/env/reward_computer.py#L81-L89) — `_compute_fill` wrong branch

- [ ] **Step 1: Add three new failing tests for non-destructive wrong fill**

Open [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py). After the existing `test_wrong_fill_terminates_at_max_wrong` (around line 90), add three new test functions:

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

- [ ] **Step 2: Run the new tests, confirm all three fail**

Run:
```
python -m pytest reasoner/tests/test_reward_computer.py::test_wrong_fill_does_not_commit_board reasoner/tests/test_reward_computer.py::test_wrong_fill_locally_removes_value_from_candidates reasoner/tests/test_reward_computer.py::test_wrong_fill_does_not_damage_related_cells -v
```

Expected: all three FAIL. Failure modes (under current code):
- `test_wrong_fill_does_not_commit_board`: `assert env.board[8, 8] == 0` fails — current `_commit_fill` writes `5` there.
- `test_wrong_fill_locally_removes_value_from_candidates`: `assert 9 in env.candidates_cache[8][8]` fails — current `_commit_fill` clears the whole set.
- `test_wrong_fill_does_not_damage_related_cells`: one of the `assert 7 in env.candidates_cache[…]` fails — current `_commit_fill` removes 7 from all related cells.

- [ ] **Step 3: Modify `_compute_fill` wrong branch to be non-destructive**

Open [reasoner/env/reward_computer.py](reasoner/env/reward_computer.py). Find this block at lines 81-89:

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

Replace with:

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

Do NOT modify `_commit_fill` itself — the correct-fill path still uses it (line 95 in the unmodified file).

- [ ] **Step 4: Re-run the three new tests, confirm they pass**

Run:
```
python -m pytest reasoner/tests/test_reward_computer.py::test_wrong_fill_does_not_commit_board reasoner/tests/test_reward_computer.py::test_wrong_fill_locally_removes_value_from_candidates reasoner/tests/test_reward_computer.py::test_wrong_fill_does_not_damage_related_cells -v
```

Expected: all three PASS.

- [ ] **Step 5: Run the full reward_computer test file to confirm no regressions**

Run: `python -m pytest reasoner/tests/test_reward_computer.py -v`

Expected: all tests PASS. Verify in particular:
- `test_wrong_fill_gets_minus_one_and_continues` — reward, wrong_count, terminated unchanged.
- `test_wrong_fill_terminates_at_max_wrong` — `wrong_count` goes 19 → 20, terminated=True.
- `test_correct_fill_completes_board_gives_plus_20` — correct-fill path unaffected.
- `test_naked_single_fill_at_either_target_gets_tech1_bonus` — correct-fill path unaffected.
- `test_correct_hidden_single_gets_tech2_bonus` — correct-fill path unaffected.
- `test_bad_eliminate_preserves_solution_candidate` (from Task 1) — still passes.

- [ ] **Step 6: Run the full reasoner test suite to catch any cross-test regressions**

Run: `python -m pytest reasoner/tests/`

Expected: all tests PASS. The env basic tests (`test_env_basic.py`), candidate engine tests, technique tests, human_solver tests, label_puzzles tests, ppo_no_bc test, and imports test should all be unaffected — none of them depend on wrong-fill commit semantics.

- [ ] **Step 7: Commit**

```bash
git add reasoner/env/reward_computer.py reasoner/tests/test_reward_computer.py
git commit -m "feat(reasoner): non-destructive wrong fill

A wrong fill used to (a) write the wrong value into board[r,c], locking
the cell, and (b) remove v from every related cell's candidate set, so
any cell whose correct solution was v became unsolvable. Result: a
single mistake cascaded into forced wrong_count=20 termination.

New behavior: penalty + wrong_count++, plus a local discard(v) from
(r,c)'s own candidate set (which is informationally honest — the
solution is unique). board[r,c] stays 0 so the agent can try other
values. Related cells are not touched.

Spec: docs/superpowers/specs/2026-05-15-wrong-action-non-destructive-design.md"
```

---

## Post-Implementation: Manual Verification (NOT automated)

After both tasks land, the user (not Claude) should do the rollout per spec §8:

1. Confirm `python -m pytest reasoner/tests/` is fully green (last commit already did this).
2. Resume training: `python -m reasoner.train.train --load-model auto`.
3. Watch TensorBoard for 10-20k steps. Expected (per spec §7):
   - `rollout/ep_len_mean` rises.
   - `rollout/ep_rew_mean` rises (sudden upward jump in the first few hundred steps is the env change, not learning).
   - Termination at `wrong_count==20` becomes rarer.
4. If after ~100k steps the `wrong_count` distribution still clusters near 20, escalate to the spec's §9 follow-up (`tried-and-failed` observation channel). That work is **out of scope for this plan**.

---

## Self-Review Checklist (done — recorded for traceability)

- **Spec §1.1 (wrong fill cascade):** addressed by Task 2 (board not committed + no propagation).
- **Spec §1.2 (wrong elim destroys solution):** addressed by Task 1 (no `_discard_candidate` on wrong elim).
- **Spec §1.3 (stuck at fail 20):** addressed by removing the two root causes above.
- **Spec §4.4 behavioral table:** all "New behavior" rows mapped to test assertions (Task 1 Step 1, Task 2 Step 1).
- **Spec §5.2 test list:** one renamed/flipped test (Task 1) + three new tests (Task 2) = 4 test changes, matches spec exactly.
- **Spec §6 compatibility:** no changes to obs shape, action space, network, or checkpoint format — verified by file inventory.
- **Placeholder scan:** no TBDs, no "implement later", no "similar to Task N", every code block is complete.
- **Type consistency:** function signatures `_compute_fill(r, c, v) -> tuple[float, bool]` and `_compute_eliminate(r, c, v) -> tuple[float, bool]` unchanged; helper names `discard`, `candidates_cache`, `candidate_count_grid`, `wrong_count`, `MAX_WRONG` consistent across all tasks.
