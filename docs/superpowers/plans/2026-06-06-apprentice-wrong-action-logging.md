# Apprentice Wrong-Action Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `rollout/ep_wrong_mean` to TensorBoard and ship a one-off script that measures the current checkpoint's per-episode error rate without retraining.

**Architecture:** Reuse SB3's own `ep_info_buffer` (Approach A): wire `wrong_count` through Monitor's `info_keywords` so it shares the exact rolling window as `ep_rew_mean`, and a tiny `_on_rollout_end` callback records the mean. The measurement script reuses the checkpoint-load pattern from `apprentice/demo/visualize.py` and runs deterministic rollouts on two distributions.

**Tech Stack:** Python, stable-baselines3 / sb3-contrib (`MaskablePPO`), Gymnasium, NumPy, pytest.

**Spec:** `docs/superpowers/specs/2026-06-06-apprentice-wrong-action-logging-design.md`

**Branch:** `feat/wrong-action-logging` (already created; spec committed as `a0adb77`).

**No cold-start:** observation/action/reward unchanged — `apprentice_ckpt_55000192_steps.zip` resumes normally.

---

## File Structure

- **Create** `apprentice/train/wrong_action_callback.py` — `WrongActionLogCallback`: records `rollout/ep_wrong_mean` from `model.ep_info_buffer` at each rollout end. One responsibility.
- **Create** `apprentice/tests/test_wrong_action_callback.py` — unit tests for the callback + a Monitor `info_keywords` propagation test.
- **Modify** `apprentice/train/train.py` — add `monitor_kwargs={"info_keywords": ("wrong_count",)}` to `make_vec_env`; import and append `WrongActionLogCallback()` to the callback list.
- **Create** `apprentice/eval/measure_wrong.py` — testable `measure(model, env, n_episodes)` + a CLI that measures two distributions and prints a table.
- **Create** `apprentice/tests/test_measure_wrong.py` — tests `measure()` aggregation with a scripted fake env + dummy policy (no DB, no model).

---

## Task 1: WrongActionLogCallback

**Files:**
- Create: `apprentice/train/wrong_action_callback.py`
- Test: `apprentice/tests/test_wrong_action_callback.py`

- [ ] **Step 1: Write the failing tests**

Create `apprentice/tests/test_wrong_action_callback.py`:

```python
"""Tests for WrongActionLogCallback (rollout/ep_wrong_mean)."""

from __future__ import annotations

from collections import deque
from types import SimpleNamespace

import numpy as np
import gymnasium as gym
from stable_baselines3.common.monitor import Monitor

from apprentice.train.wrong_action_callback import WrongActionLogCallback


class _FakeLogger:
    def __init__(self) -> None:
        self.records: dict[str, float] = {}

    def record(self, key, value):
        self.records[key] = value


def _make_cb(ep_info_buffer) -> WrongActionLogCallback:
    cb = WrongActionLogCallback()
    # BaseCallback.logger is a property returning self.model.logger, so the
    # fake model must expose both ep_info_buffer and logger.
    cb.model = SimpleNamespace(ep_info_buffer=ep_info_buffer, logger=_FakeLogger())
    return cb


def test_logs_mean_wrong_count():
    buf = deque([
        {"r": 1.0, "l": 10, "wrong_count": 2},
        {"r": 1.0, "l": 10, "wrong_count": 4},
    ])
    cb = _make_cb(buf)
    cb._on_rollout_end()
    assert cb.model.logger.records["rollout/ep_wrong_mean"] == 3.0


def test_no_record_when_buffer_empty():
    cb = _make_cb(deque())
    cb._on_rollout_end()
    assert "rollout/ep_wrong_mean" not in cb.model.logger.records


def test_no_record_when_key_missing():
    cb = _make_cb(deque([{"r": 1.0, "l": 10}]))
    cb._on_rollout_end()
    assert "rollout/ep_wrong_mean" not in cb.model.logger.records


class _TinyEnv(gym.Env):
    """Minimal env that always reports wrong_count on its terminal step."""

    def __init__(self) -> None:
        self.observation_space = gym.spaces.Box(0.0, 1.0, shape=(1,), dtype=np.float32)
        self.action_space = gym.spaces.Discrete(2)
        self._n = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._n = 0
        return np.zeros(1, dtype=np.float32), {}

    def step(self, action):
        self._n += 1
        terminated = self._n >= 3
        info = {"wrong_count": 7, "is_success": True, "steps": self._n}
        return np.zeros(1, dtype=np.float32), 1.0, terminated, False, info


def test_monitor_propagates_wrong_count_into_episode_info():
    env = Monitor(_TinyEnv(), info_keywords=("wrong_count",))
    env.reset()
    info: dict = {}
    done = False
    while not done:
        _obs, _r, term, trunc, info = env.step(0)
        done = term or trunc
    assert "episode" in info
    assert info["episode"]["wrong_count"] == 7
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest apprentice/tests/test_wrong_action_callback.py -v`
Expected: import error / FAIL — `apprentice.train.wrong_action_callback` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `apprentice/train/wrong_action_callback.py`:

```python
"""WrongActionLogCallback — log per-episode wrong_count to TensorBoard.

Reads SB3's own episode-info buffer (`model.ep_info_buffer`) — the same rolling
window used for `rollout/ep_rew_mean` / `rollout/ep_len_mean` — so the new
`rollout/ep_wrong_mean` metric lines up apples-to-apples with them.

Relies on each episode's info carrying "wrong_count". That is wired in
train.py via make_vec_env(..., monitor_kwargs={"info_keywords": ("wrong_count",)}),
which makes Monitor copy the terminal-step wrong_count into ep_info_buffer.
"""

from __future__ import annotations

from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.utils import safe_mean


class WrongActionLogCallback(BaseCallback):
    """Record rollout/ep_wrong_mean from ep_info_buffer at each rollout end."""

    def _on_step(self) -> bool:  # required abstract method; no per-step work
        return True

    def _on_rollout_end(self) -> None:
        buf = self.model.ep_info_buffer
        if not buf:
            return
        wrongs = [ep["wrong_count"] for ep in buf if "wrong_count" in ep]
        if not wrongs:
            return
        self.logger.record("rollout/ep_wrong_mean", safe_mean(wrongs))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest apprentice/tests/test_wrong_action_callback.py -v`
Expected: PASS (4 tests).

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/wrong_action_callback.py apprentice/tests/test_wrong_action_callback.py
git commit -m "feat(apprentice): WrongActionLogCallback for rollout/ep_wrong_mean"
```

---

## Task 2: Wire logging into the training entry point

**Files:**
- Modify: `apprentice/train/train.py` (imports near line 45; `make_vec_env` near line 190; callbacks list near line 322)

- [ ] **Step 1: Add the import**

In `apprentice/train/train.py`, alongside the other callback imports (after the
`from apprentice.eval.reserved_eval_callback import ReservedEvalCallback` line), add:

```python
from apprentice.train.wrong_action_callback import WrongActionLogCallback
```

- [ ] **Step 2: Add monitor_kwargs to make_vec_env**

Replace the existing `make_vec_env(...)` call:

```python
    vec_env = make_vec_env(
        make_env_fn(DB_PATH, args.max_wrong),
        n_envs=args.n_envs,
        vec_env_cls=SubprocVecEnv,
    )
```

with:

```python
    vec_env = make_vec_env(
        make_env_fn(DB_PATH, args.max_wrong),
        n_envs=args.n_envs,
        vec_env_cls=SubprocVecEnv,
        monitor_kwargs={"info_keywords": ("wrong_count",)},
    )
```

- [ ] **Step 3: Register the callback (always on)**

Replace:

```python
        callbacks = [checkpoint, eval_cb, reserved_eval]
        if curriculum_cb is not None:
            callbacks.append(curriculum_cb)
```

with:

```python
        callbacks = [checkpoint, eval_cb, reserved_eval, WrongActionLogCallback()]
        if curriculum_cb is not None:
            callbacks.append(curriculum_cb)
```

- [ ] **Step 4: Verify import + full suite still green**

Run: `python -c "import apprentice.train.train"`
Expected: no error (module imports cleanly).

Run: `python -m pytest apprentice/tests/ -q`
Expected: all pass (previous green count + 4 new from Task 1).

- [ ] **Step 5: Commit**

```bash
git add apprentice/train/train.py
git commit -m "feat(apprentice): wire wrong_count through Monitor + log ep_wrong_mean"
```

---

## Task 3: measure() core function

**Files:**
- Create: `apprentice/eval/measure_wrong.py`
- Test: `apprentice/tests/test_measure_wrong.py`

- [ ] **Step 1: Write the failing test**

Create `apprentice/tests/test_measure_wrong.py`:

```python
"""Tests for measure_wrong.measure() — distribution-agnostic rollout loop."""

from __future__ import annotations

import numpy as np

from apprentice.eval.measure_wrong import measure


class _ScriptedEnv:
    """Terminates each episode after a scripted number of steps and reports a
    fixed wrong_count / success. No DB, no real Sudoku logic."""

    def __init__(self, n_actions, episodes):
        # episodes: list of {"steps": int, "wrong": int, "success": bool}
        self.n_actions = n_actions
        self._episodes = episodes
        self._ep_idx = -1
        self._step = 0

    def reset(self, *, seed=None, options=None):
        self._ep_idx += 1
        self._step = 0
        return np.zeros(1, dtype=np.float32), {}

    def action_masks(self):
        m = np.zeros(self.n_actions, dtype=bool)
        m[0] = True
        return m

    def step(self, action):
        self._step += 1
        ep = self._episodes[self._ep_idx]
        terminated = self._step >= ep["steps"]
        info = {
            "is_success": ep["success"] if terminated else False,
            "wrong_count": ep["wrong"],
            "steps": self._step,
        }
        return np.zeros(1, dtype=np.float32), 0.0, terminated, False, info


class _DummyPolicy:
    def predict(self, obs, action_masks=None, deterministic=True):
        valid = np.flatnonzero(action_masks[0])
        return np.array([int(valid[0])]), None


def test_measure_aggregates_correctly():
    episodes = [
        {"steps": 5, "wrong": 2, "success": True},
        {"steps": 3, "wrong": 0, "success": True},
        {"steps": 4, "wrong": 10, "success": False},
    ]
    env = _ScriptedEnv(n_actions=10, episodes=episodes)
    stats = measure(_DummyPolicy(), env, n_episodes=3)

    assert stats["n_episodes"] == 3
    assert stats["success_rate"] == 2 / 3
    assert stats["mean_wrong"] == (2 + 0 + 10) / 3
    assert stats["max_wrong"] == 10
    assert stats["mean_steps"] == (5 + 3 + 4) / 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest apprentice/tests/test_measure_wrong.py -v`
Expected: import error / FAIL — `apprentice.eval.measure_wrong` does not exist.

- [ ] **Step 3: Write minimal implementation (measure only)**

Create `apprentice/eval/measure_wrong.py` with the core function (CLI added in Task 4):

```python
"""measure_wrong — one-off per-episode error-rate measurement for a checkpoint.

Loads a trained apprentice checkpoint and runs deterministic (greedy) rollouts,
reporting per-episode wrong_count alongside success rate. Used to baseline the
current model before any error-reduction optimization.

NOTE: deterministic=True measures the policy's actual competence. Training's
rollout/ep_wrong_mean is from stochastic sampling (exploration) and will read
higher; the two are not directly comparable.
"""

from __future__ import annotations

import numpy as np


def measure(model, env, n_episodes: int, seed: int | None = None) -> dict:
    """Run n_episodes deterministic rollouts; return aggregate error stats.

    env must expose reset(seed=)/step(action)/action_masks() and put
    is_success / wrong_count / steps into the step info dict.
    """
    successes: list[bool] = []
    wrongs: list[int] = []
    steps: list[int] = []

    for i in range(n_episodes):
        ep_seed = None if seed is None else seed + i
        obs, _ = env.reset(seed=ep_seed)
        done = False
        info: dict = {}
        while not done:
            masks = env.action_masks()[np.newaxis]
            action, _ = model.predict(
                obs[np.newaxis], action_masks=masks, deterministic=True
            )
            obs, _reward, terminated, truncated, info = env.step(int(action[0]))
            done = terminated or truncated
        successes.append(bool(info.get("is_success", False)))
        wrongs.append(int(info.get("wrong_count", 0)))
        steps.append(int(info.get("steps", 0)))

    n = max(len(successes), 1)
    return {
        "n_episodes": len(successes),
        "success_rate": sum(successes) / n,
        "mean_wrong": float(np.mean(wrongs)) if wrongs else 0.0,
        "max_wrong": int(max(wrongs)) if wrongs else 0,
        "mean_steps": float(np.mean(steps)) if steps else 0.0,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest apprentice/tests/test_measure_wrong.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apprentice/eval/measure_wrong.py apprentice/tests/test_measure_wrong.py
git commit -m "feat(apprentice): measure_wrong.measure() deterministic error-rate core"
```

---

## Task 4: measure_wrong CLI + run the baseline

**Files:**
- Modify: `apprentice/eval/measure_wrong.py` (append CLI helpers + `main()`)

- [ ] **Step 1: Append the CLI to `apprentice/eval/measure_wrong.py`**

Add these imports at the top of the file (below the existing `import numpy as np`):

```python
import argparse
import json
import os
import sys

from apprentice.env.sudoku_gym_env import SudokuGymEnv
from apprentice.train.ppo import SudokuMaskablePPO
from apprentice.train.train import _find_latest_checkpoint, MODEL_DIR, DB_PATH
```

Append at the end of the file:

```python
def _read_curriculum_target(ckpt_path: str) -> int | None:
    """Read rounded target_empty from the ckpt's _curriculum.json sidecar."""
    side = ckpt_path.replace(".zip", "_curriculum.json")
    if not os.path.exists(side):
        return None
    data = json.loads(open(side, encoding="utf-8").read())
    te = data.get("target_empty")
    return int(round(te)) if te is not None else None


def _print_row(label: str, stats: dict) -> None:
    print(
        f"{label:<16} "
        f"success={stats['success_rate']:6.1%}  "
        f"mean_wrong={stats['mean_wrong']:6.2f}  "
        f"max_wrong={stats['max_wrong']:3d}  "
        f"mean_steps={stats['mean_steps']:6.1f}  "
        f"(n={stats['n_episodes']})"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Measure per-episode wrong-action rate of a checkpoint.")
    p.add_argument("--ckpt", type=str, default=None, help="Checkpoint path; default = newest in MODEL_DIR.")
    p.add_argument("--n-real", type=int, default=20, help="Episodes per real-puzzle difficulty (L1-L4).")
    p.add_argument("--n-curr", type=int, default=80, help="Episodes at the curriculum target_empty.")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def main() -> None:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    ckpt = args.ckpt or _find_latest_checkpoint(MODEL_DIR)
    if ckpt is None:
        sys.exit(f"[measure] No checkpoint found in {MODEL_DIR}")
    print(f"[measure] Loading: {ckpt}")
    model = SudokuMaskablePPO.load(ckpt, device="cpu")

    print("\n=== Distribution 1: real full puzzles (target_empty=None) ===")
    for diff in (1, 2, 3, 4):
        env = SudokuGymEnv(db_path=DB_PATH, difficulty=diff)
        env.set_difficulty_distribution({diff: 1.0})
        env.set_target_empty(None)
        stats = measure(model, env, args.n_real, seed=args.seed)
        _print_row(f"REAL L{diff}", stats)

    print("\n=== Distribution 2: curriculum difficulty (difficulty=1, fill-back) ===")
    curr_target = _read_curriculum_target(ckpt)
    if curr_target is None:
        print("[measure] no curriculum sidecar; skipping curriculum-matched measurement")
    else:
        env = SudokuGymEnv(db_path=DB_PATH, difficulty=1)
        env.set_difficulty_distribution({1: 1.0})
        env.set_target_empty(curr_target)
        stats = measure(model, env, args.n_curr, seed=args.seed)
        _print_row(f"CURR te={curr_target}", stats)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Re-run the unit test to confirm nothing broke**

Run: `python -m pytest apprentice/tests/test_measure_wrong.py -v`
Expected: PASS (the CLI additions don't change `measure()`).

- [ ] **Step 3: Run the baseline measurement on the latest checkpoint**

Run (from repo root): `python -m apprentice.eval.measure_wrong`
Expected: loads `apprentice_ckpt_55000192_steps.zip`, prints a table like:

```
=== Distribution 1: real full puzzles (target_empty=None) ===
REAL L1          success=...%  mean_wrong=...  max_wrong=...  mean_steps=...  (n=20)
REAL L2          ...
=== Distribution 2: curriculum difficulty (difficulty=1, fill-back) ===
CURR te=54       ...
```

Record the printed numbers — this is the Part 2 deliverable (the error baseline).

- [ ] **Step 4: Commit**

```bash
git add apprentice/eval/measure_wrong.py
git commit -m "feat(apprentice): measure_wrong CLI; baseline error rate over two distributions"
```

---

## Self-Review

**1. Spec coverage**
- §3 training-time logging → Task 1 (callback) + Task 2 (train.py wiring). ✓
- §3.1 guards (empty buffer / missing key) → Task 1 tests `test_no_record_when_buffer_empty` / `test_no_record_when_key_missing`. ✓
- §3.2 `monitor_kwargs` + always-on callback → Task 2 Steps 2–3. ✓
- §4 measurement script, two distributions, deterministic, caveat → Task 3 (core) + Task 4 (CLI, real L1–L4 + curriculum). Caveat documented in `measure_wrong.py` docstring. ✓
- §5 testing → Task 1 + Task 3 tests; full suite green in Task 2 Step 4. ✓
- §2 non-goals (no env/reward change) → no task touches `sudoku_gym_env.py` / `reward_computer.py`. ✓

**2. Placeholder scan** — no TBD/TODO/"handle edge cases"; every code step has complete code. ✓

**3. Type/name consistency** — `measure(model, env, n_episodes, seed)` signature identical in Task 3 impl, Task 3 test, and Task 4 CLI call. Returned dict keys (`n_episodes`, `success_rate`, `mean_wrong`, `max_wrong`, `mean_steps`) match between impl, `_print_row`, and the test asserts. `WrongActionLogCallback` name identical in Task 1 and Task 2. `rollout/ep_wrong_mean` string identical in impl and test. ✓
