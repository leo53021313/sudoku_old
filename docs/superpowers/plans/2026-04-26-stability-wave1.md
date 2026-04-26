# Stability Wave 1 — Critical Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate five crash-inducing bugs: infinite recursion in env reset, NaN-poisoned BC optimizer, unhandled eval crash, silent worker death, and accumulating straggler threads.

**Architecture:** Five independent one-file fixes. Each fix adds a guard to an existing code path. No new modules. Tests added to `sb3/tests/` and `crawler/tests/`.

**Tech Stack:** Python 3.12, PyTorch, SB3 MaskablePPO, PyQt6, pytest

---

## Files Modified

| File | Change |
|------|--------|
| `sb3/app/rl/envs/sudoku_gym_env.py` | Add `_retries` depth guard to `reset()` |
| `sb3/app/rl/models/sudoku_ppo.py` | Add `tq.sum() < 1e-8` early return in `_bc_pass()` |
| `sb3/app/rl/curriculum/eval_callback.py` | Wrap eval loop in `try-except` |
| `crawler/app/core/worker.py` | Import `traceback`, emit full stack in error signal |
| `crawler/app/gui/main_window.py` | Call `w.terminate(); w.wait(1_000)` on stragglers |
| `sb3/tests/test_gym_env_stability.py` | New test file |
| `sb3/tests/test_bc_guards.py` | New test file |
| `sb3/tests/test_eval_callback_safety.py` | New test file |
| `crawler/tests/test_worker_stability.py` | New test file |
| `crawler/tests/conftest.py` | New: session-scoped QApplication fixture |

---

## Task 1: Reset recursion depth guard

**Files:**
- Modify: `sb3/app/rl/envs/sudoku_gym_env.py:87-144`
- Test: `sb3/tests/test_gym_env_stability.py`

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_gym_env_stability.py`:

```python
# sb3/tests/test_gym_env_stability.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
import app.rl.envs.sudoku_gym_env as env_mod
from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.data.pool_db import PuzzlePoolDB


def _make_db(tmp_path):
    """Create a minimal DB with one puzzle for testing."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    db.upsert_puzzle(board, level=1)
    return db_path


def test_reset_recursion_guard(tmp_path, monkeypatch):
    """reset() must raise RuntimeError after 10 failed solve attempts, not recurse forever."""
    db_path = _make_db(tmp_path)
    monkeypatch.setattr(env_mod, "solve", lambda b: None)
    env = SudokuGymEnv(db_path=db_path, difficulty=1)
    with pytest.raises(RuntimeError, match="Too many unsolvable"):
        env.reset()
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_gym_env_stability.py::test_reset_recursion_guard -v
```

Expected: FAIL — either `RecursionError` (hits Python's recursion limit) or the test hangs. Neither matches `RuntimeError("Too many unsolvable...")`.

- [ ] **Step 3: Add `_retries` parameter to `reset()`**

In `sb3/app/rl/envs/sudoku_gym_env.py`, change line 88 (the `reset` signature) and lines 138-142 (the `sol is None` branch):

```python
def reset(
    self,
    *,
    seed: int | None = None,
    options: dict | None = None,
    _retries: int = 0,
) -> tuple[np.ndarray, dict]:
```

And change lines 138-142:

```python
        # Pre-compute unique solution
        sol = solve(board)
        if sol is None:
            if _retries >= 10:
                raise RuntimeError(
                    "Too many unsolvable puzzles in DB — check puzzle_pool.db integrity"
                )
            return self.reset(seed=seed, options=options, _retries=_retries + 1)
        self.solution = sol
```

- [ ] **Step 4: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_gym_env_stability.py::test_reset_recursion_guard -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```
git add sb3/app/rl/envs/sudoku_gym_env.py sb3/tests/test_gym_env_stability.py
git commit -m "fix(sb3): add recursion depth limit to reset() when solver returns None"
```

---

## Task 2: BC loss NaN guard

**Files:**
- Modify: `sb3/app/rl/models/sudoku_ppo.py:94-134`
- Test: `sb3/tests/test_bc_guards.py`

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_bc_guards.py`:

```python
# sb3/tests/test_bc_guards.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import torch
import gymnasium as gym
from unittest.mock import MagicMock, patch


def _make_ppo():
    from app.rl.models.sudoku_ppo import SudokuMaskablePPO
    from app.rl.models.features_extractor import SudokuFeaturesExtractor
    from stable_baselines3.common.vec_env import DummyVecEnv
    from app.rl.envs.sudoku_gym_env import SudokuGymEnv
    env = DummyVecEnv([lambda: SudokuGymEnv(db_path='../data/puzzle_pool.db')])
    model = SudokuMaskablePPO(
        "CnnPolicy", env, n_steps=64, verbose=0, bc_coef=1.0, mrv_prob_init=0.8,
        policy_kwargs=dict(
            features_extractor_class=SudokuFeaturesExtractor,
            features_extractor_kwargs={"features_dim": 192},
            net_arch={"pi": [], "vf": [128]},
        ),
    )
    env.close()
    return model


def test_bc_pass_tiny_quality_no_optimizer_step():
    """_bc_pass must early-return (no optimizer step) when tq.sum() < 1e-8."""
    model = _make_ppo()
    # quality = 1e-9: positive so passes teacher_mask (> 0), but sum = 1e-9 < 1e-8
    n = 1
    model._teacher_actions = np.array([[0]], dtype=np.int64)
    model._teacher_quality = np.array([[1e-9]], dtype=np.float32)

    model.rollout_buffer = MagicMock()
    model.rollout_buffer.observations = np.zeros((n, *model.observation_space.shape), dtype=np.float32)
    model.rollout_buffer.action_masks  = np.ones((n, 729), dtype=np.float32)

    step_count = [0]
    original_step = model.policy.optimizer.step

    def counting_step():
        step_count[0] += 1
        return original_step()

    model.policy.optimizer.step = counting_step

    # Before fix: no tq.sum() guard → optimizer steps with tiny noisy gradient
    # After fix: tq.sum() = 1e-9 < 1e-8 → early return, no optimizer step
    model._bc_pass()

    assert step_count[0] == 0, \
        f"Optimizer stepped {step_count[0]} times — tq.sum() < 1e-8 guard not working"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_bc_guards.py::test_bc_pass_all_zero_quality_no_nan -v
```

Expected: FAIL — NaN propagates to policy parameters (or AssertionError on the `isnan` check).

- [ ] **Step 3: Add the early-return guard in `_bc_pass()`**

In `sb3/app/rl/models/sudoku_ppo.py`, find line 125:

```python
        bc_loss = -(log_probs * tq).sum() / tq.sum()
```

Add the guard immediately before it (after the `tq` tensor is constructed, around line 116):

```python
        tq       = torch.tensor(teacher_q_flat[teacher_mask], dtype=torch.float32, device=self.device)
        if tq.sum() < 1e-8:
            return
        # Use stored masks so BC fits the same masked distribution the policy plays
```

- [ ] **Step 4: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_bc_guards.py::test_bc_pass_all_zero_quality_no_nan -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```
git add sb3/app/rl/models/sudoku_ppo.py sb3/tests/test_bc_guards.py
git commit -m "fix(sb3): guard _bc_pass() against NaN when all teacher quality is zero"
```

---

## Task 3: Eval callback exception safety

**Files:**
- Modify: `sb3/app/rl/curriculum/eval_callback.py:56-97`
- Test: `sb3/tests/test_eval_callback_safety.py`

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_eval_callback_safety.py`:

```python
# sb3/tests/test_eval_callback_safety.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
import numpy as np


def test_eval_callback_continues_on_predict_error():
    """_on_step must return True (training continues) even if model.predict raises."""
    from app.rl.curriculum.eval_callback import SudokuEvalCallback

    cb = SudokuEvalCallback(
        db_path='../data/puzzle_pool.db',
        eval_freq=1,
        n_episodes=2,
        difficulties=(1,),
        verbose=0,
    )

    # Set up minimal callback state
    cb.num_timesteps = 100
    cb._last_eval = 0
    cb.logger = MagicMock()

    # Mock eval env and model
    mock_env = MagicMock()
    mock_env.reset.return_value = (np.zeros((26, 9, 9), dtype=np.float32), {})
    mock_env.action_masks.return_value = np.ones(729, dtype=bool)

    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("device mismatch")

    cb._eval_env = mock_env
    cb.model = mock_model

    # Before fix: RuntimeError propagates out of _on_step, crashing training
    # After fix: _on_step catches the error, prints warning, returns True
    result = cb._on_step()
    assert result is True, "_on_step must return True even when eval fails"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_eval_callback_safety.py::test_eval_callback_continues_on_predict_error -v
```

Expected: FAIL — `RuntimeError: device mismatch` propagates out of `_on_step`.

- [ ] **Step 3: Wrap the eval loop in `try-except` in `_on_step()`**

In `sb3/app/rl/curriculum/eval_callback.py`, replace lines 61-96 (the entire block after `self._last_eval = self.num_timesteps`) with a try-except:

```python
    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_eval < self._eval_freq:
            return True
        self._last_eval = self.num_timesteps

        try:
            total_s, total_n = 0, 0
            level_rates: dict[int, float] = {}

            for diff in self._difficulties:
                self._eval_env.set_difficulty_distribution({diff: 1.0})
                successes = []
                for _ in range(self._n_episodes):
                    obs, _ = self._eval_env.reset()
                    done = False
                    while not done:
                        masks = self._eval_env.action_masks()[np.newaxis]          # (1, 729)
                        action, _ = self.model.predict(
                            obs[np.newaxis],                             # (1, C, 9, 9)
                            action_masks=masks,
                            deterministic=True,
                        )
                        obs, _, terminated, truncated, info = self._eval_env.step(int(action[0]))
                        done = terminated or truncated
                    successes.append(info["is_success"])

                rate = float(np.mean(successes))
                level_rates[diff] = rate
                self.logger.record(f"eval/success_rate_L{diff}", rate)
                total_s += sum(successes)
                total_n += len(successes)

            overall = total_s / max(total_n, 1)
            self.logger.record("eval/success_rate_overall", overall)

            if self.verbose >= 1:
                parts = ", ".join(f"L{d}={level_rates[d]:.0%}" for d in self._difficulties)
                print(
                    f"[Eval] Step {self.num_timesteps:,}: "
                    f"overall={overall:.2%}  ({total_s}/{total_n})  [{parts}]"
                )

        except Exception as e:
            if self.verbose >= 1:
                print(f"[SudokuEvalCallback] eval failed at step {self.num_timesteps}: {e}")

        return True
```

- [ ] **Step 4: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_eval_callback_safety.py::test_eval_callback_continues_on_predict_error -v
```

Expected: PASS

- [ ] **Step 5: Run full sb3 test suite to check for regressions**

```
cd sb3 && python -m pytest tests/ -v
```

Expected: All previously passing tests still pass.

- [ ] **Step 6: Commit**

```
git add sb3/app/rl/curriculum/eval_callback.py sb3/tests/test_eval_callback_safety.py
git commit -m "fix(sb3): wrap eval loop in try-except so training continues if eval fails"
```

---

## Task 4: Worker full traceback in error signal

**Files:**
- Modify: `crawler/app/core/worker.py:1-92`
- Test: `crawler/tests/test_worker_stability.py`
- Create: `crawler/tests/conftest.py`

- [ ] **Step 1: Create the Qt session fixture**

Create `crawler/tests/conftest.py`:

```python
# crawler/tests/conftest.py
import sys
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
```

- [ ] **Step 2: Write the failing test**

Create `crawler/tests/test_worker_stability.py`:

```python
# crawler/tests/test_worker_stability.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QCoreApplication
import pytest


@pytest.fixture
def worker(tmp_path):
    """Create a CrawlerWorker with a real DB and mocked proxy/config."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1, max_pool_size=100)
    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None
    return CrawlerWorker(0, config, proxy, db)


def test_error_signal_contains_traceback(qapp, worker, monkeypatch):
    """When fetch raises, the error signal must include the full traceback."""
    import app.core.worker as worker_mod

    emitted = []
    worker.event_signal.connect(lambda d: emitted.append(d))

    # Make fetch raise a specific error
    monkeypatch.setattr(
        worker_mod, "fetch_puzzle_via_requests",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("connection reset")),
    )

    # Run one iteration manually
    worker._stop = False

    # Patch db to return non-full stats so it reaches the fetch path
    worker.db.get_pool_stats = lambda: {"total": 0}

    # Run the worker loop for one pass by patching stop after first iteration
    calls = []
    orig_emit = worker.event_signal.emit

    def capture(d):
        emitted.append(d)
        worker._stop = True  # stop after first event

    worker.event_signal.emit = capture
    worker.run()

    error_events = [e for e in emitted if e.get("type") == "error"]
    assert error_events, "No error event emitted"
    assert "Traceback" in error_events[0]["msg"] or "ValueError" in error_events[0]["msg"], \
        f"Expected traceback in msg, got: {error_events[0]['msg']!r}"
```

- [ ] **Step 3: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_error_signal_contains_traceback -v
```

Expected: FAIL — the error `msg` is `str(exc)[:120]`, which does NOT include `"Traceback"`.

- [ ] **Step 4: Add traceback import and update error signal in `worker.py`**

In `crawler/app/core/worker.py`, add import at the top (after existing imports):

```python
import traceback as _traceback
```

Then find lines 82-87 (the `except Exception as exc:` block) and replace with:

```python
            except Exception as exc:
                self.event_signal.emit({
                    "type": "error",
                    "msg": f"{exc}\n{_traceback.format_exc()}",
                    "worker_id": self.worker_id,
                })
```

- [ ] **Step 5: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_error_signal_contains_traceback -v
```

Expected: PASS

- [ ] **Step 6: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All previously passing tests still pass.

- [ ] **Step 7: Commit**

```
git add crawler/app/core/worker.py crawler/tests/test_worker_stability.py crawler/tests/conftest.py
git commit -m "fix(crawler): emit full traceback in worker error signal instead of truncated str"
```

---

## Task 5: Force-terminate straggler threads

**Files:**
- Modify: `crawler/app/gui/main_window.py:123-140`
- Test: `crawler/tests/test_worker_stability.py` (extend)

- [ ] **Step 1: Write the failing test**

Add to `crawler/tests/test_worker_stability.py`:

```python
def test_straggler_threads_are_terminated(qapp, tmp_path, monkeypatch):
    """Threads that don't stop within 5s must have terminate() called on them."""
    from app.gui.main_window import MainWindow
    from app.web.proxy_manager import ProxyManager
    from app.db.pool_db import PuzzlePoolDB
    from app.core.worker import CrawlerWorker
    from config import CrawlerConfig
    from unittest.mock import patch, MagicMock

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1)
    proxy = ProxyManager()

    win = MainWindow(config, proxy, db)

    # Create a mock worker that never stops
    mock_worker = MagicMock(spec=CrawlerWorker)
    mock_worker.isRunning.return_value = True  # always appears running

    win._workers = [mock_worker]

    win._on_stop()

    # terminate() must be called on the straggler
    mock_worker.terminate.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_straggler_threads_are_terminated -v
```

Expected: FAIL — `mock_worker.terminate.assert_called_once()` fails because `terminate()` is never called.

- [ ] **Step 3: Update `_on_stop()` in `main_window.py`**

In `crawler/app/gui/main_window.py`, replace lines 123-140 (the entire `_on_stop` method):

```python
    def _on_stop(self) -> None:
        if not self._workers:
            return
        self._stop_btn.setEnabled(False)
        self.log_widget.add_message("正在停止爬蟲...", "yellow")
        for w in self._workers:
            w.stop()
        for w in self._workers:
            w.wait(5_000)
        stragglers = [w for w in self._workers if w.isRunning()]
        for w in stragglers:
            w.terminate()
            w.wait(1_000)
        if stragglers:
            self.log_widget.add_message(
                f"⚠ {len(stragglers)} 個執行緒強制終止。", "yellow"
            )
        self._workers.clear()
        self.stats_panel.stop_session()
        self._start_btn.setEnabled(True)
        self.log_widget.add_message("爬蟲已停止。", "grey")
```

- [ ] **Step 4: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_straggler_threads_are_terminated -v
```

Expected: PASS

- [ ] **Step 5: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All previously passing tests still pass.

- [ ] **Step 6: Commit**

```
git add crawler/app/gui/main_window.py crawler/tests/test_worker_stability.py
git commit -m "fix(crawler): force-terminate straggler threads in _on_stop() instead of silently discarding"
```

---

## Wave 1 Complete

Run the full test suites one final time to confirm everything passes:

```
cd sb3 && python -m pytest tests/ -v
cd crawler && python -m pytest tests/ -v
```

All 5 critical stability fixes applied:
- ✅ W1-1: reset() recursion guard
- ✅ W1-2: BC NaN guard  
- ✅ W1-3: eval callback exception safety
- ✅ W1-4: worker full traceback
- ✅ W1-5: straggler thread force-terminate
