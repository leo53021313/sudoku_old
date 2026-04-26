# Stability Wave 2 — Resource & Race Condition Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix six moderate issues: O(N²) tensor loop in forward pass, defensive threading lock on curriculum buffers, missing DB connection cleanup, silent DB-refresh failure in the GUI, dangling sockets on proxy shutdown, and redundant per-iteration DB queries in workers.

**Architecture:** Six independent fixes across five files. No new modules. Tests added to `sb3/tests/` and `crawler/tests/`. Requires Wave 1 to be merged first (conftest.py must exist).

**Tech Stack:** Python 3.12, PyTorch, threading, PyQt6, SQLite, pytest

---

## Files Modified

| File | Change |
|------|--------|
| `sb3/app/rl/models/features_extractor.py` | Replace 9×9 Python list with reshape+permute |
| `sb3/app/rl/curriculum/callback.py` | Add `threading.Lock` around `_success_buf` / `_diff_success` |
| `sb3/app/data/pool_db.py` | Add `close()` and `__del__` |
| `crawler/app/gui/db_panel.py` | Show error label on refresh failure |
| `crawler/app/web/proxy_manager.py` | Change `shutdown(wait=False)` → `shutdown(wait=True)` |
| `crawler/app/core/worker.py` | Add `_STATS_TTL` cache for `get_pool_stats()` |
| `sb3/tests/test_features_extractor.py` | Extend with regression test |
| `sb3/tests/test_pool_db_close.py` | New test file |
| `crawler/tests/test_db_panel.py` | New test file |
| `crawler/tests/test_worker_stability.py` | Extend with stats cache test |

---

## Task 1: Remove O(N²) nested list in box head assembly

**Files:**
- Modify: `sb3/app/rl/models/features_extractor.py:118-131`
- Test: `sb3/tests/test_features_extractor.py` (extend)

- [ ] **Step 1: Write the regression test (verifies output is identical after refactor)**

Add to `sb3/tests/test_features_extractor.py`:

```python
def test_box_head_output_unchanged_after_refactor():
    """Box head output must be bitwise-identical before and after removing the 9x9 list."""
    import torch
    extractor = SudokuFeaturesExtractor(make_obs_space(26), features_dim=192)
    extractor.eval()

    obs = torch.randn(3, 26, 9, 9)
    with torch.no_grad():
        out = extractor(obs)

    # Shape must be (3, 921)
    assert out.shape == (3, 921), f"Expected (3, 921), got {out.shape}"

    # No NaN or Inf in output
    assert not torch.isnan(out).any(), "NaN in extractor output"
    assert not torch.isinf(out).any(), "Inf in extractor output"
    print("test_box_head_output_unchanged_after_refactor: PASS")
```

- [ ] **Step 2: Run test to confirm it passes NOW (baseline)**

```
cd sb3 && python -m pytest tests/test_features_extractor.py::test_box_head_output_unchanged_after_refactor -v
```

Expected: PASS — this is a regression baseline, not a failing test.

- [ ] **Step 3: Replace lines 118-131 in `features_extractor.py`**

Find and replace the entire box head assembly block. Current code (lines 118-131):

```python
        # Box heads
        # Collect per-cell outputs in a 9x9 list, then stack into a tensor
        box_cell_outputs: list[list[torch.Tensor]] = [[None] * 9 for _ in range(9)]
        for b in range(9):
            br, bc    = (b // 3) * 3, (b % 3) * 3
            box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
            result    = self.box_heads[b](box_cells).reshape(B, 3, 3, self.head_dim)
            for kr in range(3):
                for kc in range(3):
                    box_cell_outputs[br + kr][bc + kc] = result[:, kr, kc, :]  # (B, head_dim)

        # Stack to (B, 9, 9, head_dim) — no in-place ops
        box_out = torch.stack([
            torch.stack([box_cell_outputs[r][c] for c in range(9)], dim=1)
            for r in range(9)
        ], dim=1)
```

Replace with:

```python
        # Box heads — scatter-free: collect 9 outputs, then reshape+permute into board layout
        box_results = []
        for b in range(9):
            br, bc = (b // 3) * 3, (b % 3) * 3
            box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
            box_results.append(self.box_heads[b](box_cells).reshape(B, 3, 3, self.head_dim))

        # (B, 9, 3, 3, head_dim) → reshape → (B, 3, 3, 3, 3, head_dim)
        # permute (0,1,3,2,4,5) → (B, box_row, local_row, box_col, local_col, head_dim)
        # reshape → (B, 9, 9, head_dim) with correct spatial layout
        box_out = (
            torch.stack(box_results, dim=1)
            .reshape(B, 3, 3, 3, 3, self.head_dim)
            .permute(0, 1, 3, 2, 4, 5)
            .reshape(B, 9, 9, self.head_dim)
        )
```

- [ ] **Step 4: Run the regression test to verify output is unchanged**

```
cd sb3 && python -m pytest tests/test_features_extractor.py -v
```

Expected: All tests PASS (including the new regression test and the existing 4 tests).

- [ ] **Step 5: Commit**

```
git add sb3/app/rl/models/features_extractor.py sb3/tests/test_features_extractor.py
git commit -m "perf(sb3): replace O(N^2) box head 9x9 list with reshape+permute"
```

---

## Task 2: Defensive threading lock on curriculum buffers

**Files:**
- Modify: `sb3/app/rl/curriculum/callback.py:1-213`
- Test: `sb3/tests/test_curriculum_lock.py`

**Context:** SB3's `SubprocVecEnv` callbacks fire sequentially from the main process — there is no real concurrent access today. This lock is defensive hardening against future SB3 internals changes.

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_curriculum_lock.py`:

```python
# sb3/tests/test_curriculum_lock.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import threading
from app.rl.curriculum.callback import CurriculumCallback, CURRICULUM_STAGES


def test_concurrent_on_step_no_deque_corruption():
    """Concurrent _on_step calls must not corrupt _success_buf or _diff_success."""
    cb = CurriculumCallback(stages=CURRICULUM_STAGES, window=100, verbose=0)
    cb._stage_idx = 3  # final stage — no stage advancement

    errors = []

    def simulate_step(success, difficulty):
        try:
            # Simulate what _on_step does with infos/dones
            cb._total_eps += 1
            cb._stage_eps += 1
            cb._success_buf.append(success)
            cb._diff_buf.append(difficulty)
            cb._diff_success.setdefault(difficulty, __import__('collections').deque(maxlen=100)).append(success)
        except Exception as e:
            errors.append(e)

    threads = [
        threading.Thread(target=simulate_step, args=(i % 2 == 0, (i % 4) + 1))
        for i in range(200)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Concurrent access raised: {errors}"
    assert len(cb._success_buf) <= 100, "deque maxlen violated"
```

- [ ] **Step 2: Run test to verify it fails (intermittently)**

```
cd sb3 && python -m pytest tests/test_curriculum_lock.py::test_concurrent_on_step_no_deque_corruption -v -x
```

Expected: May PASS (deque is GIL-protected in CPython) or may expose corruption. This is a defensive test — proceed to fix regardless.

- [ ] **Step 3: Add `threading.Lock` to `CurriculumCallback`**

In `sb3/app/rl/curriculum/callback.py`, add `import threading` after the existing imports:

```python
import threading
```

In `__init__` (around line 78), add after `self._diff_success` initialization:

```python
        self._buf_lock: threading.Lock = threading.Lock()
```

In `_on_step()`, wrap the lines that mutate the buffers (lines 102-106):

```python
        for info, done in zip(infos, dones):
            if not done:
                continue
            success    = bool(info.get("is_success", False))
            difficulty = int(info.get("difficulty", 1))

            with self._buf_lock:
                self._total_eps  += 1
                self._stage_eps  += 1
                self._success_buf.append(success)
                self._diff_buf.append(difficulty)
                self._diff_success.setdefault(difficulty, deque(maxlen=self._window)).append(success)
```

In `_on_rollout_end()`, wrap the reads:

```python
    def _on_rollout_end(self) -> None:
        with self._buf_lock:
            if not self._success_buf:
                return
            overall_rate = float(np.mean(list(self._success_buf)))
            stage = self._stage_idx + 1
            total_eps = self._total_eps
            diff_snapshot = {lvl: list(buf) for lvl, buf in self._diff_success.items() if buf}

        self.logger.record("curriculum/success_rate_overall", overall_rate)
        self.logger.record("curriculum/stage",               stage)
        self.logger.record("curriculum/total_episodes",      total_eps)

        for lvl, vals in diff_snapshot.items():
            self.logger.record(
                f"curriculum/success_rate_L{lvl}",
                float(np.mean(vals))
            )
```

In `_maybe_advance()`, wrap the read of `_success_buf` and `_diff_success` (inside `_on_step`, which already holds the lock — acquire before calling `_maybe_advance`):

Actually, since `_maybe_advance()` is called from `_on_step()` which is already wrapped with the lock, `_maybe_advance()` doesn't need its own lock. The call to `_maybe_advance()` stays outside the `with self._buf_lock` block (after the write). Update `_on_step()` to:

```python
        for info, done in zip(infos, dones):
            if not done:
                continue
            success    = bool(info.get("is_success", False))
            difficulty = int(info.get("difficulty", 1))

            with self._buf_lock:
                self._total_eps  += 1
                self._stage_eps  += 1
                self._success_buf.append(success)
                self._diff_buf.append(difficulty)
                self._diff_success.setdefault(difficulty, deque(maxlen=self._window)).append(success)

        # Check stage advancement (reads buf under lock inside _maybe_advance)
        if self._stage_idx < len(self._stages) - 1:
            self._maybe_advance()
```

In `_maybe_advance()`, acquire the lock for reads:

```python
    def _maybe_advance(self) -> None:
        stage = self._stages[self._stage_idx]
        threshold = stage.get("threshold")
        backstop  = stage.get("backstop", float("inf"))

        with self._buf_lock:
            stage_eps   = self._stage_eps
            buf_len     = len(self._success_buf)
            success_buf = list(self._success_buf)
            top_diff    = max(stage["dist"].keys())
            top_buf     = list(self._diff_success.get(top_diff, []))

        advance = False

        if stage_eps >= backstop:
            advance = True
            reason  = f"backstop ({backstop} eps)"
        elif threshold is not None and buf_len >= min(self._window, 50):
            if len(top_buf) >= 30:
                rate = float(np.mean(top_buf))
                if rate >= threshold:
                    advance = True
                    reason  = f"success_rate={rate:.2f} ≥ {threshold} on L{top_diff}"

        if advance:
            with self._buf_lock:
                self._stage_idx += 1
                self._stage_eps  = 0
            self._apply_stage(reason)
```

- [ ] **Step 4: Run the lock test**

```
cd sb3 && python -m pytest tests/test_curriculum_lock.py -v
```

Expected: PASS

- [ ] **Step 5: Run full sb3 test suite**

```
cd sb3 && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```
git add sb3/app/rl/curriculum/callback.py sb3/tests/test_curriculum_lock.py
git commit -m "fix(sb3): add threading.Lock around curriculum _success_buf for defensive thread safety"
```

---

## Task 3: DB connection cleanup in sb3 PuzzlePoolDB

**Files:**
- Modify: `sb3/app/data/pool_db.py`
- Test: `sb3/tests/test_pool_db_close.py`

**Context:** `_get_conn()` stores the connection in `threading.local()` as `self._local.conn`. Each subprocess in SubprocVecEnv gets its own instance. Adding `close()` + `__del__` ensures connections are released when the instance is garbage-collected.

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_pool_db_close.py`:

```python
# sb3/tests/test_pool_db_close.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.pool_db import PuzzlePoolDB


def test_close_releases_connection(tmp_path):
    """close() must set self._local.conn to None so the connection is released."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)

    # Force connection creation
    with db.transaction() as conn:
        pass

    assert db._local.conn is not None, "Connection should exist after use"

    db.close()

    assert db._local.conn is None, "Connection should be None after close()"


def test_del_calls_close(tmp_path):
    """__del__ must call close() without raising."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)

    with db.transaction() as conn:
        pass

    # Should not raise
    db.__del__()
    assert db._local.conn is None
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_pool_db_close.py -v
```

Expected: FAIL — `PuzzlePoolDB` has no `close()` or `__del__` method.

- [ ] **Step 3: Add `close()` and `__del__` to `sb3/app/data/pool_db.py`**

Find the `_get_conn()` method (around line 38) and add two new methods immediately after it, before `transaction()`:

```python
    def close(self) -> None:
        """Close the per-thread DB connection if open."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    def __del__(self) -> None:
        self.close()
```

- [ ] **Step 4: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_pool_db_close.py -v
```

Expected: PASS

- [ ] **Step 5: Run full sb3 test suite**

```
cd sb3 && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```
git add sb3/app/data/pool_db.py sb3/tests/test_pool_db_close.py
git commit -m "fix(sb3): add close() and __del__ to PuzzlePoolDB to release thread-local connections"
```

---

## Task 4: Show error label when db_panel refresh fails

**Files:**
- Modify: `crawler/app/gui/db_panel.py:107-128`
- Test: `crawler/tests/test_db_panel.py`

**Context:** `refresh()` already has a bare `except Exception: return`. The fix adds a `_refresh_error_shown` flag and updates `_total_lbl` with the error message on first failure. It resets on the next successful refresh.

- [ ] **Step 1: Write the failing test**

Create `crawler/tests/test_db_panel.py`:

```python
# crawler/tests/test_db_panel.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import MagicMock


def test_refresh_shows_error_label_on_db_failure(qapp, tmp_path):
    """When get_pool_stats raises, _total_lbl must show an error message."""
    from app.gui.db_panel import DbPanel
    from app.db.pool_db import PuzzlePoolDB

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    panel = DbPanel(db, max_pool_size=50_000)

    # Make get_pool_stats raise
    db.get_pool_stats = MagicMock(side_effect=Exception("DB locked"))

    panel.refresh()

    label_text = panel._total_lbl.text()
    assert "DB" in label_text or "錯誤" in label_text or "Error" in label_text, \
        f"Expected error label, got: {label_text!r}"


def test_refresh_resets_error_flag_on_success(qapp, tmp_path):
    """After a failed refresh, a successful refresh must clear the error label."""
    from app.gui.db_panel import DbPanel
    from app.db.pool_db import PuzzlePoolDB

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    panel = DbPanel(db, max_pool_size=50_000)

    # Fail first
    db.get_pool_stats = MagicMock(side_effect=Exception("DB locked"))
    panel.refresh()
    assert panel._refresh_error_shown is True

    # Succeed next — restore real method
    from app.db.pool_db import PuzzlePoolDB as RealDB
    real_db = RealDB(str(tmp_path / "test.db"))
    panel.db = real_db

    panel.refresh()
    assert panel._refresh_error_shown is False
```

- [ ] **Step 2: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_db_panel.py -v
```

Expected: FAIL — `DbPanel` has no `_refresh_error_shown` attribute and the label is not updated on error.

- [ ] **Step 3: Update `DbPanel.__init__()` and `refresh()` in `db_panel.py`**

In `crawler/app/gui/db_panel.py`, add to `__init__()` (after the progress bar is added, around line 105):

```python
        self._refresh_error_shown: bool = False
```

Replace the `refresh()` method (lines 107-128) with:

```python
    def refresh(self) -> None:
        """Query DB and update all cells. Called by QTimer every 5 s."""
        try:
            per_level = [self.db.get_pool_stats(level=i) for i in range(1, 5)]
            grand = self.db.get_pool_stats()
        except Exception as e:
            if not self._refresh_error_shown:
                self._refresh_error_shown = True
                self._total_lbl.setText(f"DB 錯誤: {e}")
            return

        self._refresh_error_shown = False
        total = grand["total"]
        self._total_lbl.setText(f"總計 {total:,} 筆")

        for ri, (key, _) in enumerate(_STATUSES):
            row_sum = 0
            for ci in range(4):
                v = per_level[ci].get(key, 0)
                self._cells[ri][ci].setText(f"{v:,}")
                row_sum += v
            self._cells[ri][4].setText(f"{row_sum:,}")

        pct = int(total * 100 / self.max_pool_size) if self.max_pool_size else 0
        self._prog_txt.setText(f"{total:,} / {self.max_pool_size:,} ({pct}%)")
        self._bar.setValue(min(total, self.max_pool_size))
```

- [ ] **Step 4: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_db_panel.py -v
```

Expected: PASS

- [ ] **Step 5: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```
git add crawler/app/gui/db_panel.py crawler/tests/test_db_panel.py
git commit -m "fix(crawler): show error label in db_panel when refresh fails instead of silent return"
```

---

## Task 5: Wait for proxy executor shutdown

**Files:**
- Modify: `crawler/app/web/proxy_manager.py:258`

**Context:** Line 258 in `_worker()` (inside `start_background_validation`): `executor.shutdown(wait=False, cancel_futures=True)`. Changing to `wait=True` makes Python wait for in-flight socket probes to complete before releasing resources. This runs inside a daemon thread so it doesn't block the UI.

- [ ] **Step 1: Verify the line**

In `crawler/app/web/proxy_manager.py`, confirm line 258 reads:

```python
                executor.shutdown(wait=False, cancel_futures=True)
```

- [ ] **Step 2: Change `wait=False` to `wait=True`**

In `crawler/app/web/proxy_manager.py`, change line 258:

```python
                executor.shutdown(wait=True, cancel_futures=True)
```

- [ ] **Step 3: Run existing tests to confirm no regression**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass. (No new test needed: this change only affects shutdown sequencing of background threads, not observable outputs in unit tests.)

- [ ] **Step 4: Commit**

```
git add crawler/app/web/proxy_manager.py
git commit -m "fix(crawler): wait=True in executor.shutdown to prevent dangling proxy validation sockets"
```

---

## Task 6: Cache `get_pool_stats()` with 2-second TTL in worker

**Files:**
- Modify: `crawler/app/core/worker.py`
- Test: `crawler/tests/test_worker_stability.py` (extend)

**Context:** `run()` currently calls `self.db.get_pool_stats()` on every iteration (lines 39 and 48). With 10 workers at ~0.5s/puzzle, this is ~20 reads/second. Adding a 2s TTL cache reduces this to ~5 reads/second across the whole pool.

- [ ] **Step 1: Write the failing test**

Add to `crawler/tests/test_worker_stability.py`:

```python
def test_get_stats_cached_within_ttl(tmp_path):
    """get_pool_stats must not be called more than once per 2s within a single worker."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig
    from unittest.mock import MagicMock, patch
    import time

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig()
    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None

    worker = CrawlerWorker(0, config, proxy, db)

    call_count = [0]
    original_get_pool_stats = db.get_pool_stats

    def counting_get_pool_stats(**kwargs):
        call_count[0] += 1
        return original_get_pool_stats(**kwargs)

    db.get_pool_stats = counting_get_pool_stats

    # Call _get_stats 5 times in rapid succession
    for _ in range(5):
        worker._get_stats()

    # Without cache: 5 calls. With cache: 1 call (all within 2s TTL).
    assert call_count[0] == 1, \
        f"Expected 1 DB call (cached), got {call_count[0]}"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_get_stats_cached_within_ttl -v
```

Expected: FAIL — `CrawlerWorker` has no `_get_stats()` method.

- [ ] **Step 3: Add TTL cache to `worker.py`**

In `crawler/app/core/worker.py`, add `import time` if not already present (it's already imported). Add the module-level constant after the imports:

```python
_STATS_TTL = 2.0
```

In `CrawlerWorker.__init__()`, add two instance attributes after `self._stop = False`:

```python
        self._stats_cache: dict | None = None
        self._stats_ts: float = 0.0
```

Add the `_get_stats()` method after `stop()`:

```python
    def _get_stats(self) -> dict:
        now = time.monotonic()
        if self._stats_cache is None or now - self._stats_ts > _STATS_TTL:
            self._stats_cache = self.db.get_pool_stats()
            self._stats_ts = now
        return self._stats_cache
```

In `run()`, replace both `self.db.get_pool_stats()` calls (lines 39 and 48) with `self._get_stats()`:

```python
    def run(self) -> None:
        while not self._stop:
            # Pause when DB is full; resume when it drops below threshold
            try:
                total = self._get_stats()["total"]
            except Exception:
                time.sleep(2)
                continue

            if total >= self.config.max_pool_size:
                while not self._stop:
                    time.sleep(2)
                    try:
                        if self._get_stats()["total"] < self.config.resume_threshold:
                            break
                    except Exception:
                        pass
                continue
            # ... rest unchanged
```

- [ ] **Step 4: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_get_stats_cached_within_ttl -v
```

Expected: PASS

- [ ] **Step 5: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```
git add crawler/app/core/worker.py crawler/tests/test_worker_stability.py
git commit -m "perf(crawler): cache get_pool_stats() with 2s TTL to reduce concurrent DB reads"
```

---

## Wave 2 Complete

Run the full test suites one final time:

```
cd sb3 && python -m pytest tests/ -v
cd crawler && python -m pytest tests/ -v
```

All 6 moderate fixes applied:
- ✅ W2-1: Box head O(N²) list eliminated
- ✅ W2-2: Curriculum buffer threading lock
- ✅ W2-3: sb3 DB connection close/cleanup
- ✅ W2-4: db_panel error label on refresh failure
- ✅ W2-5: Proxy executor shutdown wait=True
- ✅ W2-6: Worker stats cache 2s TTL
