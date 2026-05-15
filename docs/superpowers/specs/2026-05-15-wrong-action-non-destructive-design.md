# Non-Destructive Wrong Actions (Reasoner Env)

**Date:** 2026-05-15
**Scope:** `reasoner/` only (`legacy/` and `sb3/` untouched)
**Status:** Draft — pending implementation plan

## 1. Problem

The reasoner env currently treats wrong actions as permanent state mutations. This creates two distinct failure modes during training:

### 1.1 Wrong fill locks the cell and damages related cells

In [reasoner/env/reward_computer.py:81-89](reasoner/env/reward_computer.py#L81-L89), a wrong fill `(r, c, v)` where `v != solution[r,c]`:

1. Sets `board[r, c] = v` (the wrong value, via `_commit_fill`)
2. Clears `(r, c)`'s candidate set
3. Removes `v` from the candidate set of **every cell in the same row, column, and box** ([reasoner/env/reward_computer.py:137-141](reasoner/env/reward_computer.py#L137-L141))

After this, `action_masks()` ([reasoner/env/sudoku_gym_env.py:158-159](reasoner/env/sudoku_gym_env.py#L158-L159)) skips occupied cells, so the agent cannot rewrite `(r, c)`. More critically, any cell in the same row/col/box whose correct solution was `v` has lost `v` from its candidates and can never be solved.

### 1.2 Wrong eliminate destroys the solution

In [reasoner/env/reward_computer.py:108-116](reasoner/env/reward_computer.py#L108-L116), a wrong eliminate `(r, c, v)` where `v == solution[r, c]` calls `_discard_candidate(r, c, v)`, removing the correct answer from `(r, c)`'s candidate set. `(r, c)` is then unsolvable for the rest of the episode.

### 1.3 Downstream effect: "stuck at fail 20"

Once 1.1 or 1.2 has fired, downstream cells have no valid candidates. Every subsequent fill attempt at those cells is wrong → -1 → `wrong_count++`. The agent burns through the remaining wrong-action budget without choice, terminating the episode at `wrong_count >= MAX_WRONG (20)` even though the board still has empty cells.

This is not policy failure — it is environment-induced dead-end propagation.

## 2. Goals

- Make wrong actions **penalty-only**: still cost `-1` and count toward `wrong_count`, but never break the env's state in a way that prevents recovery.
- Preserve "the agent now knows v doesn't belong at (r, c)" as informational memory **only where it is strictly true**.
- Keep all other reward, termination, and observation semantics identical.
- Do not change observation shape, action space, or checkpoint format.

## 3. Non-Goals

- No new observation channel (e.g., "tried-and-failed" mask). Tracked as a possible follow-up if 4.3 turns out to be a real problem.
- No `undo` action.
- No change to `MAX_WRONG`, `max_steps`, `+0.3 / +0.1` unjustified-action rewards, `+20` board-complete reward, or `TECH_BONUS` table.
- No curriculum reintroduction.
- `legacy/` and `sb3/` are out of scope.

## 4. Design

### 4.1 Wrong fill — new behavior

```python
if not is_correct:
    env.wrong_count += 1
    env.candidates_cache[r][c].discard(v)
    env.candidate_count_grid[r, c] = len(env.candidates_cache[r][c])
    terminated = env.wrong_count >= MAX_WRONG
    return -1.0, terminated
```

- `board[r, c]` stays `0` (cell remains writable in future steps).
- Local `discard(v)` records "v is known wrong at (r, c)" — informationally honest because solution is unique, so `v != solution[r,c]` proves v cannot be placed here.
- Related-cell candidates are **not** touched. "v is wrong at (r, c)" does not imply anything about v's placement in the rest of the row/col/box.
- The mask now allows `(r, c, v')` for any other candidate v', and disallows `(r, c, v)` for both `fill` and `eliminate`. The agent cannot repeat the same wrong fill.

### 4.2 Wrong eliminate — new behavior

```python
if is_bad:
    env.wrong_count += 1
    terminated = env.wrong_count >= MAX_WRONG
    return -1.0, terminated
```

- `candidates_cache` is not modified. The solution candidate stays available, so `(r, c)` remains solvable.
- The mask still permits `(r, c, v)` as an eliminate target in future steps. See risk 4.3.

### 4.3 Risk: repeated wrong eliminate

Because the candidate is preserved, the policy *could* fire the same wrong eliminate again. Each repeat costs `-1` and increments `wrong_count`, so worst case the episode terminates at `wrong_count == MAX_WRONG`. The reward signal (`-1` per repeat) is the deterrent.

This is an information-loss situation: under the current observation, the policy cannot distinguish "I have not tried eliminating v at (r, c)" from "I have tried it 5 times and it was wrong every time." If empirical training shows the policy loops on this pattern, the follow-up is to add a `tried-and-failed` channel to the observation (shape `(9, 9, 9)` collapsed into one boolean plane per `(r, c, v)`). That work is out of scope for this spec.

### 4.4 Behavioral table

| Action | Predicate | Old behavior | New behavior |
|---|---|---|---|
| Fill | `v == solution[r,c]` | Commit, reward = `1.0 + TECH_BONUS[t]` or `0.3` / `20.0` | **Unchanged** |
| Fill | `v != solution[r,c]` | Commit wrong v + propagate candidate removal to row/col/box; `-1`; `wrong_count++` | Local `discard(v)` only; `-1`; `wrong_count++` |
| Eliminate | `v != solution[r,c]` | Remove v from candidates; reward = `1.0 + TECH_BONUS[t]` or `0.1` | **Unchanged** |
| Eliminate | `v == solution[r,c]` | Remove v from candidates (destroys solution); `-1`; `wrong_count++` | No state change; `-1`; `wrong_count++` |
| Board complete | All cells filled correctly | `+20`, terminate | **Unchanged** |
| `wrong_count >= MAX_WRONG` | Any wrong action | Terminate | **Unchanged** |
| `_step_count >= max_steps` | Truncation | Truncate | **Unchanged** |

## 5. Implementation Surface

### 5.1 Production code

- **File:** [reasoner/env/reward_computer.py](reasoner/env/reward_computer.py)
  - `_compute_fill` wrong branch (5 lines).
  - `_compute_eliminate` wrong branch (3 lines).
  - No new helpers required. `_commit_fill` and `_discard_candidate` remain in use by the correct-action branches.

### 5.2 Tests

File: [reasoner/tests/test_reward_computer.py](reasoner/tests/test_reward_computer.py)

**Modified tests:**
- `test_bad_eliminate_removes_solution_value_gets_minus_one` — rename to `test_bad_eliminate_preserves_solution_candidate`; flip the assertion from `assert 4 not in env.candidates_cache[5][5]` to `assert 4 in env.candidates_cache[5][5]`. Reward and `wrong_count` assertions stay the same.

**New tests:**
- `test_wrong_fill_does_not_commit_board` — after wrong fill at `(r, c)`, assert `env.board[r, c] == 0`.
- `test_wrong_fill_locally_removes_value_from_candidates` — after wrong fill of v at `(r, c)`, assert `v not in env.candidates_cache[r][c]`.
- `test_wrong_fill_does_not_damage_related_cells` — capture candidate sets of all cells in the same row, column, and box of `(r, c)` before the wrong fill, then assert they are unchanged after.

**Unchanged tests (must still pass):**
- `test_wrong_fill_gets_minus_one_and_continues`
- `test_wrong_fill_terminates_at_max_wrong`
- `test_bad_eliminate_terminates_at_max_wrong`
- All correct-action, naked-single, hidden-single, eliminate-correct tests.

### 5.3 Other reasoner tests

- `test_env_basic.py`, `test_candidate_engine.py`, `test_human_solver.py`, `test_techniques/*` — must continue passing without modification. None of these depend on wrong-action commit semantics.

## 6. Compatibility

- **Observation:** unchanged (24 channels, `(24, 9, 9)`).
- **Action space:** unchanged (`Discrete(1458)`).
- **Network architecture:** unchanged.
- **Checkpoints:** existing `reasoner/models/reasoner_ckpt_*_steps.zip` and `*_vecnorm.pkl` files load and run on the new env without modification. `--load-model auto` continues to work.
- **TensorBoard:** scalars stay in the same scale; expect mean episode reward to rise and mean episode length to grow once the env stops force-terminating via cascade.

## 7. Expected Training Impact

Quantitative predictions (to be verified post-deploy):

- **Mean episode length:** ↑ (the cascade was a major cause of premature termination).
- **Mean episode reward:** ↑ (replacing chains of forced `-1` actions with continued exploration that earns positive rewards).
- **`wrong_count` at termination:** distribution shifts. Previously bimodal at 1-2 wrong actions (single mistake that did not cascade) and 20 (cascade). New distribution should concentrate lower with a thinner tail near 20.
- **Board-completion rate:** ↑, especially on Level 1 and 2 puzzles.
- **Discontinuity warning:** the first few hundred steps after switching env will show a sudden upward jump in mean reward. This is the env, not policy improvement. Do not interpret as a learning signal.

## 8. Rollout Plan

1. Land code + tests as a single change.
2. Run full test suite from repo root: `python -m pytest reasoner/tests/`.
3. Resume training from newest checkpoint: `python -m reasoner.train.train --load-model auto`.
4. Watch TensorBoard for 10-20k steps to confirm episode length / reward shift matches §7 predictions.
5. If `wrong_count` distribution stays clustered near 20 after 100k steps of new training, escalate to follow-up: add `tried-and-failed` observation channel.

## 9. Out-of-Scope Follow-Ups (Recorded for Later)

- `tried-and-failed` observation channel for repeated wrong eliminates (4.3).
- Adjusting `MAX_WRONG` downward once the cascade is gone.
- Reward shaping for the unjustified-action `+0.1 / +0.3` paths.
- Adding an explicit `undo` action.
