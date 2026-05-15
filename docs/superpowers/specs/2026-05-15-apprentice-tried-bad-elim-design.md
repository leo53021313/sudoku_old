# Per-Episode Tried-Bad-Eliminate Mask (Apprentice Env)

**Date:** 2026-05-15
**Scope:** `apprentice/` only (`reasoner/`, `legacy/`, `sb3/` untouched)
**Status:** Draft — pending implementation plan
**Predecessor spec:** [2026-05-15-apprentice-wrong-action-non-destructive-design.md](2026-05-15-apprentice-wrong-action-non-destructive-design.md) (commit `5b88758` + implementation in `35e94af5`, `a4ddbbee`, `6ed1b010`, `3f291c32`)

## 1. Problem

The non-destructive-wrong-actions change (predecessor spec) introduced a known risk (§4.3 of the predecessor): wrong eliminate makes **no state change at all**, so when the policy is in a state where it picks `eliminate(r, c, v)` with `v == solution[r,c]`, the next step's state is identical to this step's state, and the policy will pick the same action again. The episode loops on that single bad action until `wrong_count == MAX_WRONG (20)`.

Empirically observed after deploying the predecessor change: training episodes that previously failed via state cascade now fail via deterministic action loop on a single `(r, c, v)` wrong eliminate. The "stuck at fail 20" symptom regressed — even though the underlying mechanism changed.

The wrong-fill path does **not** have this problem because its local `candidates_cache[r][c].discard(v)` propagates to `action_masks()`, which blocks both `fill(r, c, v)` and `eliminate(r, c, v)` from being re-selected at that exact triple.

## 2. Goals

- Block repeated `eliminate(r, c, v)` after a single wrong eliminate at that triple, within the same episode.
- Keep wrong eliminate's "no candidate removal" property — `(r, c)` must stay solvable, so `v` remains in `candidates_cache[r][c]`.
- Preserve checkpoint compatibility: observation shape and action space stay identical.
- Don't change wrong-fill handling, MAX_WRONG, reward magnitudes, curriculum, or any reward-shaping value.

## 3. Non-Goals

- No `tried-and-failed` observation channel. The predecessor spec §4.3 listed this as the recommended follow-up; the mask-based approach in this spec is a deliberate alternative that does not change `N_CHANNELS` (so existing checkpoints load unchanged).
- No cross-episode persistence of the tried-bad set. The set is per-instance, per-episode, and is cleared on `reset()`.
- No change to `_compute_fill` (wrong or correct branches).
- No change to `_compute_eliminate`'s correct-eliminate branch.
- `reasoner/`, `legacy/`, `sb3/` are out of scope.

## 4. Design

### 4.1 New env state

In [apprentice/env/sudoku_gym_env.py](apprentice/env/sudoku_gym_env.py), `SudokuGymEnv`:

```python
self._tried_bad_elim: set[tuple[int, int, int]] = set()
```

- Initialized empty in `__init__` (alongside the other instance fields around lines 70-87).
- Cleared at the start of `reset()`, **before** either reset branch sets the board, so both the `options["board"]` path and the DB-fetch path get a fresh empty set.

### 4.2 Recording wrong eliminates

In [apprentice/env/reward_computer.py](apprentice/env/reward_computer.py), `_compute_eliminate` wrong branch (currently lines 117-122 post-Task-1):

```python
if is_bad:
    # Penalty only — do NOT remove the solution candidate, otherwise
    # (r,c) becomes unsolvable for the rest of the episode.
    env.wrong_count += 1
    env._tried_bad_elim.add((r, c, v))   # ← new
    terminated = env.wrong_count >= MAX_WRONG
    return -1.0, terminated
```

One added line. No other change to the body. The `env._tried_bad_elim` access is duck-typed (consistent with `env.wrong_count`, `env.candidates_cache`, etc., already accessed via duck typing).

### 4.3 Mask exclusion

In `action_masks()` (currently lines 165-184), after the candidate-based legality loop:

```python
def action_masks(self) -> np.ndarray:
    mask = np.zeros(self.N_ACTIONS, dtype=bool)
    for r in range(9):
        for c in range(9):
            if self.board[r, c] != 0:
                continue
            for v in self.candidates_cache[r][c]:
                base = r * 81 + c * 9 + (v - 1)
                mask[base] = True                       # fill
                mask[self._ELIM_OFFSET + base] = True   # eliminate
    # ← new: forbid eliminates that already failed this episode
    for (r, c, v) in self._tried_bad_elim:
        base = r * 81 + c * 9 + (v - 1)
        mask[self._ELIM_OFFSET + base] = False
    return mask
```

Only the eliminate half is masked. `mask[base]` (fill) is untouched — `fill(r, c, v)` for the same triple is now the *correct* fill (since `v == solution[r,c]`), and we want the policy to be able to choose it.

### 4.4 Behavioral table (delta vs. predecessor spec)

| Action | Predicate | Predecessor behavior | New behavior |
|---|---|---|---|
| Fill | `v == solution[r,c]` | reward `1.0 + TECH_BONUS[t]` / `0.3` / `50.0` | **Unchanged** |
| Fill | `v != solution[r,c]` | Local `discard(v)`; `-1`; `wrong_count++` | **Unchanged** |
| Eliminate | `v != solution[r,c]` | `_discard_candidate`; `1.0 + TECH_BONUS[t]` / `0.1` | **Unchanged** |
| Eliminate | `v == solution[r,c]` | `-1`; `wrong_count++`; no state change | `-1`; `wrong_count++`; **add `(r,c,v)` to `_tried_bad_elim`** |
| `action_masks()` | `(r,c,v) in _tried_bad_elim` | (set didn't exist) | `mask[ELIM_OFFSET + base] = False` |
| `action_masks()` | `(r,c,v) in _tried_bad_elim`, fill half | (set didn't exist) | `mask[base]` **unchanged** (still True if `v ∈ candidates`) |
| `reset()` | start of episode | (set didn't exist) | `_tried_bad_elim` cleared / re-initialized |
| Board complete | All cells filled correctly | `+50`, terminate | **Unchanged** |
| `wrong_count >= MAX_WRONG` | Any wrong action | Terminate | **Unchanged** |
| `_step_count >= max_steps` | Truncation | Truncate | **Unchanged** |

## 5. Information Leakage

After a wrong eliminate of `v` at `(r, c)`, the mask forbids `eliminate(r, c, v)` but still allows `fill(r, c, v)`. An outside observer could deduce that `v` is the correct solution at `(r, c)`. **The policy has already received `-1` reward for that exact action**, so the information content of the mask is no greater than the information already carried by the reward signal — the mask just enforces avoidance deterministically rather than statistically.

This is structurally the same leakage as wrong fill: after `fill(r, c, v)` with `v != solution`, `candidates_cache[r][c].discard(v)` causes the mask to forbid both `fill(r, c, v)` and `eliminate(r, c, v)` — signaling that `v` is wrong at `(r, c)`. We accept this leakage as inherent to the env design under the action-justification reward model.

## 6. Implementation Surface

### 6.1 Production code

- **`apprentice/env/sudoku_gym_env.py`** (~3 changed regions, ~6 net lines):
  - `__init__`: initialize `self._tried_bad_elim`.
  - `reset()`: clear `self._tried_bad_elim` at the top, before either branch decides on a board.
  - `action_masks()`: append the exclusion loop after the candidate-based legality loop.

- **`apprentice/env/reward_computer.py`** (1 changed line):
  - `_compute_eliminate` wrong branch: add `env._tried_bad_elim.add((r, c, v))`.

### 6.2 Tests

File [apprentice/tests/test_reward_computer.py](apprentice/tests/test_reward_computer.py):

- **Update `_StubEnv`:** add `self._tried_bad_elim: set[tuple[int, int, int]] = set()` to `__init__`. This is required so all existing eliminate-related tests still construct a valid stub. No test logic changes for unrelated tests.
- **New test:** `test_bad_eliminate_records_triple_in_tried_bad_elim` — after a wrong eliminate of `(5, 5, 4)`, assert `(5, 5, 4) in env._tried_bad_elim` and `len(env._tried_bad_elim) == 1`.
- **Unchanged tests:** all currently-passing tests in this file must still pass with no modification beyond the `_StubEnv` update.

File [apprentice/tests/test_env_basic.py](apprentice/tests/test_env_basic.py):

- **New test:** `test_tried_bad_elim_initially_empty` — fresh env construct, assert `env._tried_bad_elim == set()`.
- **New test:** `test_action_masks_excludes_tried_bad_elim_after_wrong_eliminate` — reset env, perform a step that does a wrong eliminate (use solution leakage to construct the action: query `env.solution[r, c]` from the test, then submit `eliminate(r, c, v=solution[r, c])` as the action). After that step, assert `action_masks()[ELIM_OFFSET + r*81 + c*9 + (v-1)] == False`.
- **New test:** `test_action_masks_still_allows_fill_for_tried_bad_elim` — same setup as the above; after the wrong eliminate, assert `action_masks()[r*81 + c*9 + (v-1)] == True` (the correct fill remains available).
- **New test:** `test_reset_clears_tried_bad_elim` — perform a wrong eliminate to populate the set, call `env.reset()`, assert `env._tried_bad_elim == set()`.

### 6.3 Other apprentice tests

- `test_candidate_engine.py`, `test_human_solver.py`, `test_obs_helpers.py`, `test_techniques/*`, `test_curriculum_controller.py`, `test_curriculum_callback.py`, `test_ppo_no_bc.py`, `test_imports.py`, `test_label_puzzles.py` must continue passing without modification. None reference `_tried_bad_elim` (it's new) and none depend on the legacy "no-op wrong eliminate" behavior the spec is changing.

## 7. Compatibility

- **Observation:** unchanged (26 channels, `(26, 9, 9)`).
- **Action space:** unchanged (`Discrete(1458)`). The new mask only flips bits — it does not introduce new actions or remove the action space's overall size.
- **Network architecture:** unchanged.
- **Checkpoints:** existing `apprentice_ckpt_*.zip` and `*_vecnorm.pkl` / `*_curriculum.json` sidecars resume without modification. `_tried_bad_elim` is per-env-instance per-episode state — not policy weights, not VecNormalize stats, not curriculum state. A fresh empty set is created automatically on env construction.
- **Resumed training:** `--load-model auto` continues to work. No new flags, no migration step.
- **Curriculum:** untouched.

## 8. Expected Training Impact

Quantitative predictions (to be verified post-deploy):

- **`wrong_count` at termination:** the loop-to-20 failure mode disappears. Distribution should concentrate further at low values; the right tail at 20 thins to near zero (still possible if the policy makes 20 *different* wrong actions in one episode, but no longer reachable by a single wrong action looping 20 times).
- **Mean episode reward:** ↑ — after each wrong eliminate the policy is forced to find a different action, eventually hitting the correct fill (which now has the highest available value at that mask-thinned (r, c)).
- **Mean episode length:** more stable — bounded loops vanish.
- **Board-completion rate:** ↑ further on Level 1 and Level 2 puzzles; smaller but still positive effect on Level 3/4.
- **Discontinuity warning:** another small upward step in mean reward when the env switches over. Same source as before (env change, not policy improvement). The first ~10k steps after switchover is not a learning signal.

## 9. Rollout Plan

1. Land code + tests as a single change (or two if implementation plan prefers test-first per-file split).
2. Run full apprentice test suite from repo root: `python -m pytest apprentice/tests/`.
3. Resume training from newest checkpoint: `python -m apprentice.train.train --load-model auto`.
4. Watch TensorBoard for 10-20k steps to confirm `wrong_count` distribution shifts as predicted in §8.
5. If `wrong_count` still cluster-fails at 20 after 100k new steps, the failure is no longer the loop pattern — investigate as a separate issue (likely a different bad-action pattern, not addressable by this mask).

## 10. Out-of-Scope Follow-Ups (Recorded for Later)

- Observation channel for `_tried_bad_elim` exposure (so the policy can *learn* to avoid those eliminates rather than just being masked-out from them). Predecessor spec §4.3 also lists this. If the masked-out approach proves brittle (e.g., the policy fails to generalize across episodes), this becomes the next step.
- Reward shaping: should a repeated-but-now-masked-out wrong eliminate still penalize? Currently it can't happen (mask blocks it before reward is computed). If we ever drop the mask, we'd need to think about repeat-penalty curves.
- Trial-and-error technique justifier (T&E, tech_id 17) interaction: T&E performs deeper search. If T&E's reasoning path produces eliminates that this mask blocks, the justifier could fail to attribute correctly. To be checked empirically; not blocking.
- Mirroring this change into `reasoner/` if reasoner-side training also shows the same loop pattern.
