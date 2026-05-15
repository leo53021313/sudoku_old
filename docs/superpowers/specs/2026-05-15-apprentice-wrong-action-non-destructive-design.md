# Non-Destructive Wrong Actions (Apprentice Env)

**Date:** 2026-05-15
**Scope:** `apprentice/` only (`reasoner/`, `legacy/`, `sb3/` untouched)
**Status:** Draft — pending implementation plan
**Sibling spec:** [docs/superpowers/specs/2026-05-15-wrong-action-non-destructive-design.md](2026-05-15-wrong-action-non-destructive-design.md) (same change, already landed in `reasoner/`)

## 1. Problem

The apprentice env currently treats wrong actions as permanent state mutations. This creates two distinct failure modes during training and one observable symptom that turns out to be the downstream effect of the first two.

### 1.1 Wrong fill locks the cell and damages related cells

In [apprentice/env/reward_computer.py:85-89](apprentice/env/reward_computer.py#L85-L89), a wrong fill `(r, c, v)` where `v != solution[r,c]`:

1. Sets `board[r, c] = v` (the wrong value, via `_commit_fill`)
2. Clears `(r, c)`'s candidate set
3. Removes `v` from the candidate set of **every cell in the same row, column, and box** ([apprentice/env/reward_computer.py:137-141](apprentice/env/reward_computer.py#L137-L141))

After this, `action_masks()` ([apprentice/env/sudoku_gym_env.py:178](apprentice/env/sudoku_gym_env.py#L178)) skips occupied cells, so the agent cannot rewrite `(r, c)`. More critically, any cell in the same row/col/box whose correct solution was `v` has lost `v` from its candidates and can never be solved.

### 1.2 Wrong eliminate destroys the solution

In [apprentice/env/reward_computer.py:112-116](apprentice/env/reward_computer.py#L112-L116), a wrong eliminate `(r, c, v)` where `v == solution[r, c]` calls `_discard_candidate(r, c, v)`, removing the correct answer from `(r, c)`'s candidate set. `(r, c)` is then unsolvable for the rest of the episode.

### 1.3 Downstream effect: "stuck at fail 20"

Once 1.1 or 1.2 has fired, downstream cells have no valid candidates. Every subsequent fill attempt at those cells is wrong → `-1` → `wrong_count++`. The agent burns through the remaining wrong-action budget without choice, terminating the episode at `wrong_count >= MAX_WRONG (20)` even though the board still has empty cells.

This is not policy failure — it is environment-induced dead-end propagation.

### 1.4 Note on "elim has no memory" intuition

Elim actions already have within-episode memory: `_discard_candidate` writes to `candidates_cache[r][c]`, which persists for the rest of the episode, drives the action mask (so a discarded `v` cannot be re-eliminated), and is exposed to the policy via observation channels 9-17 ([apprentice/env/sudoku_gym_env.py:208-213](apprentice/env/sudoku_gym_env.py#L208-L213)). What is missing is memory of **failed** eliminates (see §4.3); that is recorded here as a follow-up, not solved by this spec.

## 2. Goals

- Make wrong actions **penalty-only**: still cost `-1` and count toward `wrong_count`, but never break the env's state in a way that prevents recovery.
- Preserve "the agent now knows v doesn't belong at (r, c)" as informational memory **only where it is strictly true** (wrong-fill case).
- Keep all other reward, termination, and observation semantics identical.
- Do not change observation shape, action space, or checkpoint format.

## 3. Non-Goals

- No new observation channel (e.g., "tried-and-failed" mask for repeated wrong eliminates). Tracked as a follow-up if 4.3 turns out to be a real problem.
- No `undo` action.
- No change to `MAX_WRONG`, `max_steps`, `+0.3 / +0.1` unjustified-action rewards, the board-complete reward (currently `+50` in apprentice — see §6), or the `TECH_BONUS` table.
- No curriculum changes — `CurriculumController` / `CurriculumCallback` and `apprentice/configs/curriculum.json` are untouched. The `target_empty` mechanism and `_apply_fill_back` continue working as before.
- `reasoner/`, `legacy/`, `sb3/` are out of scope.

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
- Local `discard(v)` records "v is known wrong at (r, c)" — informationally honest because the solution is unique, so `v != solution[r,c]` proves v cannot be placed here.
- Related-cell candidates are **not** touched. "v is wrong at (r, c)" does not imply anything about v's placement in the rest of the row/col/box.
- The mask now allows `(r, c, v')` for any other candidate v', and disallows both `fill(r, c, v)` and `eliminate(r, c, v)` (since the action mask is gated on `v in candidates_cache[r][c]`). The agent cannot repeat the same wrong fill.

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

This is an information-loss situation: under the current observation, the policy cannot distinguish "I have not tried eliminating v at (r, c)" from "I have tried it 5 times and it was wrong every time." If empirical training shows the policy loops on this pattern, the follow-up is to add a `tried-and-failed` channel to the observation (one boolean plane per `(r, c, v)`, shape `(9, 9, 9)`; the simplest exposure is to collapse to a single per-cell count plane or expand `N_CHANNELS` by 9). That work is out of scope for this spec.

### 4.4 Behavioral table

| Action | Predicate | Old behavior | New behavior |
|---|---|---|---|
| Fill | `v == solution[r,c]` | Commit, reward = `1.0 + TECH_BONUS[t]` or `0.3` / `50.0` (board complete) | **Unchanged** |
| Fill | `v != solution[r,c]` | Commit wrong v + propagate candidate removal to row/col/box; `-1`; `wrong_count++` | Local `discard(v)` only; `-1`; `wrong_count++` |
| Eliminate | `v != solution[r,c]` | Remove v from candidates; reward = `1.0 + TECH_BONUS[t]` or `0.1` | **Unchanged** |
| Eliminate | `v == solution[r,c]` | Remove v from candidates (destroys solution); `-1`; `wrong_count++` | No state change; `-1`; `wrong_count++` |
| Board complete | All cells filled correctly | `+50`, terminate | **Unchanged** |
| `wrong_count >= MAX_WRONG` | Any wrong action | Terminate | **Unchanged** |
| `_step_count >= max_steps` | Truncation | Truncate | **Unchanged** |

## 5. Implementation Surface

### 5.1 Production code

- **File:** [apprentice/env/reward_computer.py](apprentice/env/reward_computer.py)
  - `_compute_fill` wrong branch (replace `self._commit_fill(r, c, v)` with local discard — ~3 lines net change).
  - `_compute_eliminate` wrong branch (drop `self._discard_candidate(r, c, v)` — 1 line removed).
  - No new helpers required. `_commit_fill` and `_discard_candidate` remain in use by the correct-action branches.

### 5.2 Tests

File: [apprentice/tests/test_reward_computer.py](apprentice/tests/test_reward_computer.py)

**Modified tests:**
- `test_bad_eliminate_removes_solution_value_gets_minus_one` ([apprentice/tests/test_reward_computer.py:193](apprentice/tests/test_reward_computer.py#L193)) — rename to `test_bad_eliminate_preserves_solution_candidate`; flip the assertion from `assert 4 not in env.candidates_cache[5][5]` to `assert 4 in env.candidates_cache[5][5]`. Reward and `wrong_count` assertions stay the same.

**New tests:**
- `test_wrong_fill_does_not_commit_board` — after wrong fill at `(r, c)`, assert `env.board[r, c] == 0`.
- `test_wrong_fill_locally_removes_value_from_candidates` — after wrong fill of v at `(r, c)`, assert `v not in env.candidates_cache[r][c]` and `env.candidate_count_grid[r, c]` decremented by 1.
- `test_wrong_fill_does_not_damage_related_cells` — capture candidate sets of all cells in the same row, column, and box of `(r, c)` before the wrong fill, then assert they are unchanged after.

**Unchanged tests (must still pass):**
- `test_wrong_fill_gets_minus_one_and_continues`
- `test_wrong_fill_terminates_at_max_wrong`
- `test_bad_eliminate_terminates_at_max_wrong`
- All correct-action, naked-single, hidden-single, eliminate-correct tests in this file.

### 5.3 Other apprentice tests

- `test_env_basic.py`, `test_candidate_engine.py`, `test_human_solver.py`, `test_obs_helpers.py`, `test_techniques/*`, `test_curriculum_controller.py`, `test_curriculum_callback.py`, `test_ppo_no_bc.py`, `test_imports.py`, `test_label_puzzles.py` — must continue passing without modification. None of these depend on wrong-action commit semantics.

## 6. Compatibility

- **Observation:** unchanged (26 channels — 24 base + naked-single ch 24 + hidden-single ch 25, shape `(26, 9, 9)`).
- **Action space:** unchanged (`Discrete(1458)`).
- **Network architecture:** unchanged.
- **Checkpoints:** existing `apprentice/models/apprentice_ckpt_*_steps.zip` and `*_vecnorm.pkl` / `*_curriculum.json` sidecar files load and run on the new env without modification. `--load-model auto` continues to work.
- **TensorBoard:** scalars stay in the same scale; expect mean episode reward to rise and mean episode length to grow once the env stops force-terminating via cascade.
- **Note on the uncommitted `+20 → +50` board-complete change:** the working tree of `apprentice/env/reward_computer.py` already raises the board-complete reward from 20 to 50 and lowers `ent_coef` from 0.05 to 0.01 (uncommitted). This spec leaves both alone — the wrong-action edit and the reward-magnitude edit are orthogonal and can be committed together or separately; coordinating that is an implementation-plan concern, not a design concern.

## 7. Expected Training Impact

Quantitative predictions (to be verified post-deploy):

- **Mean episode length:** ↑ (the cascade was a major cause of premature termination).
- **Mean episode reward:** ↑ (replacing chains of forced `-1` actions with continued exploration that earns positive rewards).
- **`wrong_count` at termination:** distribution shifts. Previously bimodal at 1-2 wrong actions (single mistake that did not cascade) and 20 (cascade). New distribution should concentrate lower with a thinner tail near 20.
- **Board-completion rate:** ↑, especially on Level 1 and 2 puzzles and on low-`target_empty` curriculum stages.
- **Curriculum advancement:** likely faster early-stage advance because the success-rate signal feeding `CurriculumController` (target rate 0.70 with band [0.50, 0.85]) gets less noise from cascade-induced failures.
- **Discontinuity warning:** the first few hundred steps after switching env will show a sudden upward jump in mean reward. This is the env, not policy improvement. Do not interpret as a learning signal. The curriculum's `stagnation_probe_step` / rollback logic uses windowed averages, so a one-time jump won't trip it spuriously.

## 8. Rollout Plan

1. Land code + tests as a single change.
2. Run full apprentice test suite from repo root: `python -m pytest apprentice/tests/`.
3. Resume training from newest checkpoint: `python -m apprentice.train.train --load-model auto`.
4. Watch TensorBoard for 10-20k steps to confirm episode length / reward shift matches §7 predictions.
5. If `wrong_count` distribution stays clustered near 20 after 100k steps of new training, escalate to follow-up: add `tried-and-failed` observation channel.

## 9. Out-of-Scope Follow-Ups (Recorded for Later)

- `tried-and-failed` observation channel for repeated wrong eliminates (§4.3).
- Adjusting `MAX_WRONG` downward once the cascade is gone (the original 20 was sized partly to absorb cascade pain).
- Reward shaping for the unjustified-action `+0.1 / +0.3` paths.
- Adding an explicit `undo` action.
- Mirroring this change into `legacy/` if that env is ever reactivated.
