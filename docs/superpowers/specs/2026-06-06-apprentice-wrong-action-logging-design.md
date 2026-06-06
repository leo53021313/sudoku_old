# Apprentice — Per-Episode Wrong-Action Logging + One-Off Measurement

**Date:** 2026-06-06
**Status:** Design approved, pending spec review.
**Scope:** Observability only. No change to obs / action space / reward / curriculum / hyperparameters → **no cold-start required**.

---

## 1. Motivation — why now

The user observed that `curriculum/target_empty` keeps creeping up (51.77 → 53.77) while
`rollout/ep_rew_mean` (~300) and `rollout/ep_len_mean` (~143) have plateaued, and wants to
(1) log per-episode error count and (2) optimize the model toward fewer errors.

Parsing the latest TB event file (`apprentice/runs/apprentice_2`) reframes the situation:

| Metric | Value | Meaning |
|---|---|---|
| `curriculum/success_rate_window` | **1.000** | training boards solved 100% |
| `eval/success_rate_L1..L4` | **all 1.000** | real full puzzles (all 4 difficulties) solved 100% |
| `eval/reserved_overall` | **1.000** | held-out puzzles solved 100% |
| `curriculum/target_empty` | 51.77 → 53.77 | curriculum keeps raising difficulty *because* success is 100% |
| `env/max_wrong` | ~64 | wrong-action budget dynamically inflated |

**The plateau is success saturation, not a stuck model.** The +50 board-complete reward
dominates `ep_rew_mean`; once success is 100% everywhere, the reward cannot climb further.

**The hidden gap:** because `max_wrong` is now ~64, the agent can make dozens of wrong
actions and still complete the board (= "success"). Per-episode `env.wrong_count` is tracked
and exposed in `info` (`sudoku_gym_env.py:166`) but is **never written to TensorBoard**. So we
cannot currently tell whether the 100% success is *clean reasoning* or *messy guessing*.
Logging the error count is the prerequisite for any error-reduction work.

---

## 2. Goals / Non-goals

**Goals**
- Add `rollout/ep_wrong_mean` to TensorBoard, on the same rolling window as `ep_rew_mean`.
- Provide a one-off measurement script to read the current checkpoint's error rate
  immediately, without retraining.

**Non-goals (YAGNI — explicitly out of scope)**
- No split of wrong-fills vs wrong-eliminates (user chose minimal change) → **env and
  `reward_computer.py` are untouched**.
- No error-rate-per-step metric, no reward change, no curriculum change, no `max_wrong` change.
- The actual error-reduction *optimization* is deferred to a separate brainstorm once the
  measured baseline is in hand.

---

## 3. Part 1 — Training-time logging (Approach A)

`wrong_count` is already in every step's `info`. The chosen approach reuses SB3's own
episode-info buffer so the new metric shares the exact window and cadence as `ep_rew_mean`.

### 3.1 New file — `apprentice/train/wrong_action_callback.py`

`WrongActionLogCallback(BaseCallback)`:
- `_on_step` → returns `True` (no per-step work).
- `_on_rollout_end` → reads `self.model.ep_info_buffer`; if non-empty and the entries carry
  `"wrong_count"`, record `rollout/ep_wrong_mean = safe_mean([ep["wrong_count"] for ep in buf])`.
- Guards: empty buffer or missing key → record nothing (no crash, no zero-pollution).

`_on_rollout_end` runs at the end of `collect_rollouts`, before SB3's `_dump_logs`, so the
value lands in the same dump as `ep_rew_mean` / `ep_len_mean`.

### 3.2 Edit — `apprentice/train/train.py`

1. `make_vec_env(..., monitor_kwargs={"info_keywords": ("wrong_count",)})` — Monitor copies
   the terminal-step `wrong_count` into each episode's info, which feeds `ep_info_buffer`.
2. Append `WrongActionLogCallback()` to the callback list, **always** (independent of
   `--no-curriculum`).

### 3.3 Data flow

`env.step()` → `info["wrong_count"]` → Monitor → `model.ep_info_buffer` →
`WrongActionLogCallback._on_rollout_end` → `logger.record("rollout/ep_wrong_mean", mean)` →
SB3 `_dump_logs` → TensorBoard, sitting beside `ep_rew_mean` / `ep_len_mean`.

### 3.4 Resume compatibility

Pure logging change. `apprentice_ckpt_55000192_steps.zip` resumes via `--load-model auto`
unchanged; VecNormalize and curriculum sidecars load normally; no obs/size mismatch. The new
curve simply starts plotting from the resume point forward (logging cannot backfill history).

---

## 4. Part 2 — One-off measurement script

### 4.1 New file — `apprentice/eval/measure_wrong.py`

Reuses the load pattern from `apprentice/demo/visualize.py`
(`SudokuMaskablePPO.load(ckpt, device="cpu")`, raw obs fed directly — obs is **not**
normalized at train time, `norm_obs=False`, so no VecNormalize needed for inference).

- Core, testable function `measure(model, env, n_episodes) -> dict` returning
  `{success_rate, mean_wrong, max_wrong, mean_steps}`, using `deterministic=True` greedy
  rollouts with `env.action_masks()`.
- Thin CLI wrapper that:
  - auto-finds the newest `apprentice_ckpt_*_steps.zip`,
  - measures **two distributions**:
    1. **Real full puzzles** L1–L4, ~20 episodes each (`target_empty=None`; mirrors `eval/*`).
    2. **Current curriculum difficulty** (`target_empty` read from the ckpt's
       `_curriculum.json` sidecar, ≈54), ~80 episodes (mirrors `rollout/*`).
  - prints a table: distribution → `success_rate / mean_wrong / max_wrong / mean_steps`.

### 4.2 Interpretation caveat (must be stated in script output / report)

The script uses `deterministic=True` (greedy) → measures error count under the policy's
*actual competence*. Training's `rollout/ep_wrong_mean` is from **stochastic sampling**
(exploration) and will typically read **higher**. The deterministic number is a lower bound;
the two must not be compared 1:1.

---

## 5. Testing (TDD)

- **`apprentice/tests/test_wrong_action_callback.py`** — feed a fake `ep_info_buffer`
  containing `wrong_count` values; call `_on_rollout_end`; assert
  `logger.record("rollout/ep_wrong_mean", <correct mean>)` is called. Separate case: empty
  buffer / missing key → `record` not called for the metric.
- **`apprentice/tests/test_measure_wrong.py`** — run `measure()` with a dummy/random policy on
  a small env; assert the returned dict has the expected keys and values in sane ranges
  (`0 ≤ success_rate ≤ 1`, `mean_wrong ≥ 0`, etc.).

Full apprentice suite must stay green (`python -m pytest apprentice/tests/`).

---

## 6. Execution order

1. Implement + test Part 1 and Part 2 (TDD).
2. Run `measure_wrong.py` on the latest checkpoint → **immediate** baseline error numbers
   (zero training).
3. On the next resumed training run, `rollout/ep_wrong_mean` begins plotting.
4. With the baseline in hand, open a separate brainstorm for the actual error-reduction
   optimization (candidate levers, for reference, not part of this spec: higher wrong-action
   penalty, smaller `max_wrong` for a fine-tuning phase, removing the +0.3/+0.1
   unjustified-action rewards, or justified-action masking).
