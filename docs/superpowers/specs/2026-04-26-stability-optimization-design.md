# Stability & Optimization Design — sb3 + crawler

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all 19 identified stability, resource, and performance issues across the sb3 training system and the standalone crawler, organized into three independently shippable waves.

**Architecture:** Three-wave approach — Wave 1 eliminates crash-inducing bugs, Wave 2 fixes resource leaks and race conditions, Wave 3 adds minor hardening and polish. Each wave can be reviewed and merged independently.

**Tech Stack:** Python 3.12, PyTorch, Stable-Baselines3, PyQt6, SQLite (WAL mode)

---

## Affected Files

| File | Wave | Change type |
|------|------|-------------|
| `sb3/app/rl/envs/sudoku_gym_env.py` | 1, 3 | Guard + obs copy |
| `sb3/app/rl/models/sudoku_ppo.py` | 1, 3 | NaN guards |
| `sb3/app/rl/curriculum/eval_callback.py` | 1 | Exception handling |
| `sb3/app/rl/models/features_extractor.py` | 2 | Tensor reshape |
| `sb3/app/rl/curriculum/callback.py` | 2 | Threading lock |
| `sb3/app/data/pool_db.py` | 2, 3 | Close + idempotent migration + lock log |
| `crawler/app/core/worker.py` | 1, 2, 3 | Traceback log + stats cache + direct-connect warn |
| `crawler/app/gui/main_window.py` | 1 | Force-terminate stragglers |
| `crawler/app/gui/db_panel.py` | 2 | Exception handling |
| `crawler/app/web/proxy_manager.py` | 2, 3 | shutdown wait + timeout alignment |
| `crawler/app/db/pool_db.py` | 3 | Retry backoff + idempotent migration + lock log |

---

## Wave 1 — Critical Stability (5 items)

### W1-1: `sb3/app/rl/envs/sudoku_gym_env.py` — Recursion depth limit in `reset()`

**Problem:** `reset()` calls itself when `solve(board)` returns `None`. No depth limit means stack overflow if DB contains unsolvable puzzles.

**Fix:** Accept `_retries: int = 0` as a private kwarg. Increment on each recursive call. If `_retries >= 10`, raise `RuntimeError("Too many unsolvable puzzles in DB — check puzzle_pool.db integrity")`.

```python
def reset(self, seed=None, options=None, _retries: int = 0):
    ...
    sol = solve(board)
    if sol is None:
        if _retries >= 10:
            raise RuntimeError("Too many unsolvable puzzles in DB — check puzzle_pool.db integrity")
        return self.reset(seed=seed, options=options, _retries=_retries + 1)
```

### W1-2: `sb3/app/rl/models/sudoku_ppo.py` — BC loss NaN guard

**Problem:** `_bc_pass()` computes `-(log_probs * tq).sum() / tq.sum()`. If all teacher samples have quality ≈ 0 (teacher abstains), denominator → 0 → NaN poisons optimizer.

**Fix:** Early return when teacher has effectively abstained:

```python
def _bc_pass(self, ...):
    ...
    if tq.sum() < 1e-8:
        return
    bc_loss = -(log_probs * tq).sum() / tq.sum()
```

### W1-3: `sb3/app/rl/curriculum/eval_callback.py` — Exception safety in eval loop

**Problem:** `model.predict()` with bad action masks or device mismatch raises unhandled exception, silently disabling all future evals.

**Fix:** Wrap the per-difficulty eval loop in `try-except Exception`:

```python
try:
    for difficulty in self.difficulties:
        ...
except Exception as e:
    if self.verbose >= 1:
        print(f"[SudokuEvalCallback] eval failed: {e}")
    return True
```

### W1-4: `crawler/app/core/worker.py` — Full traceback on exception

**Problem:** `except Exception as exc` emits only `str(exc)[:120]`. Worker stops silently; user sees no stack trace.

**Fix:** Import `traceback` and emit full traceback in the error signal:

```python
import traceback as _traceback

except Exception as exc:
    tb = _traceback.format_exc()
    self.event_signal.emit({
        "type": "error",
        "msg": f"{exc}\n{tb}",
        ...
    })
```

### W1-5: `crawler/app/gui/main_window.py` — Force-terminate straggler threads

**Problem:** After `w.wait(5_000)`, threads still running are dereferenced but not stopped. Repeated start/stop cycles accumulate live threads.

**Fix:** Call `w.terminate()` followed by `w.wait(1_000)` for any thread still running after the 5-second wait:

```python
stragglers = [w for w in self._workers if w.isRunning()]
for w in stragglers:
    w.terminate()
    w.wait(1_000)
if stragglers:
    self.log_widget.add_message(f"⚠ {len(stragglers)} 個執行緒強制終止。", "yellow")
self._workers.clear()
```

---

## Wave 2 — Moderate Resource & Race Fixes (6 items)

### W2-1: `sb3/app/rl/models/features_extractor.py` — Remove O(N²) nested list

**Problem:** `box_cell_outputs` is a 9×9 Python list. Each box head result is scattered back into individual cell slots (81 assignments), then assembled via two nested `torch.stack` calls — 81 Python tensor indexing ops per forward pass.

**Fix:** Collect the 9 box outputs as a list, stack once, then reshape+permute into board layout:

```python
# Box heads — scatter-free version
box_results = []
for b in range(9):
    br, bc = (b // 3) * 3, (b % 3) * 3
    box_cells = emb_[:, br:br+3, bc:bc+3, :].reshape(B, 9, self.cell_dim)
    box_results.append(self.box_heads[b](box_cells).reshape(B, 3, 3, self.head_dim))

# (B, 9, 3, 3, head_dim) → (B, 3, 3, 3, 3, head_dim)
# permute (0,1,3,2,4,5) → (B, box_row, local_row, box_col, local_col, head_dim)
# reshape → (B, 9, 9, head_dim) with correct spatial layout
box_out = (
    torch.stack(box_results, dim=1)
    .reshape(B, 3, 3, 3, 3, self.head_dim)
    .permute(0, 1, 3, 2, 4, 5)
    .reshape(B, 9, 9, self.head_dim)
)
```

Eliminates 81 Python-level tensor assignments and 2 nested `torch.stack` loops. Output shape `(B, 9, 9, head_dim)` is identical to the current code — downstream `.reshape(B, 81, self.head_dim)` is unchanged.

### W2-2: `sb3/app/rl/curriculum/callback.py` — Lock `_success_buf` access

**Problem:** `_success_buf` (deque) and `_diff_success` (dict) are read/written from callbacks that can fire from multiple SubprocVecEnv workers concurrently.

**Fix:** Add `self._buf_lock = threading.Lock()` in `__init__`. Wrap all reads and writes to `_success_buf` and `_diff_success` with `with self._buf_lock:`.

```python
import threading

class CurriculumCallback:
    def __init__(self, ...):
        ...
        self._buf_lock = threading.Lock()

    def _on_step(self) -> bool:
        with self._buf_lock:
            self._success_buf.append(...)
            self._diff_success[d].append(...)
```

### W2-3: `sb3/app/data/pool_db.py` — Close DB connection on cleanup

**Problem:** `_get_db()` caches connection in `self._db` with no destructor. Each SubprocVecEnv subprocess leaks a file descriptor for the training session lifetime.

**Fix:** Add `close()` and `__del__`:

```python
def close(self) -> None:
    if self._db is not None:
        self._db.close()
        self._db = None

def __del__(self) -> None:
    self.close()
```

### W2-4: `crawler/app/gui/db_panel.py` — Exception safety in `refresh()`

**Problem:** If `get_pool_stats()` raises (DB locked, connection lost), the exception propagates into Qt's event loop, which may silently stop the timer.

**Fix:** Wrap the refresh body in try-except; display a one-time warning in the panel:

```python
def refresh(self) -> None:
    try:
        ...
    except Exception as e:
        if not self._refresh_error_shown:
            self._refresh_error_shown = True
            # update label to show error state
            self._total_label.setText(f"DB 錯誤: {e}")
```

Add `self._refresh_error_shown = False` in `__init__`, reset it on next successful refresh.

### W2-5: `crawler/app/web/proxy_manager.py` — Wait for executor shutdown

**Problem:** `executor.shutdown(wait=False)` returns while threads are still holding sockets, causing resource leaks on stop.

**Fix:** Switch to `shutdown(wait=True, cancel_futures=True)`. This cancels all pending validation futures immediately and waits for any in-flight socket probes to finish before returning — no dangling sockets. Call this from a short-lived thread if blocking the UI is a concern (it isn't here since stop is already async).

```python
executor.shutdown(wait=True, cancel_futures=True)
```

### W2-6: `crawler/app/core/worker.py` — Cache `get_pool_stats()` with 2s TTL

**Problem:** Every worker calls `db.get_pool_stats()` every iteration. With 10 workers and ~0.5s per puzzle, this is ~20 DB reads/second just for stats.

**Fix:** Cache the result with a 2-second TTL:

```python
_STATS_TTL = 2.0

class CrawlerWorker(QThread):
    def __init__(self, ...):
        ...
        self._stats_cache: dict | None = None
        self._stats_ts: float = 0.0

    def _get_stats(self) -> dict:
        now = time.monotonic()
        if self._stats_cache is None or now - self._stats_ts > _STATS_TTL:
            self._stats_cache = self.db.get_pool_stats()
            self._stats_ts = now
        return self._stats_cache
```

Replace all `db.get_pool_stats()` calls in the run loop with `self._get_stats()`.

---

## Wave 3 — Minor Hardening (8 items)

### W3-1: `sb3/app/rl/envs/sudoku_gym_env.py` — Copy board before building obs

**Problem:** `_obs()` references `self.board` directly. Safe today, but fragile if env ever runs in shared-memory mode.

**Fix:** One line at the start of `_obs()`:

```python
def _obs(self) -> np.ndarray:
    board = self.board.copy()
    # use `board` instead of `self.board` throughout
```

### W3-2: `sb3/app/rl/models/sudoku_ppo.py` — Clamp log_probs before BC loss

**Problem:** Masked actions have log_prob = `-inf`. `-inf * 0` = `NaN` in PyTorch, even when the weight is zero.

**Fix:** Before the loss computation:

```python
log_probs = log_probs.clamp(min=-1e9)
bc_loss = -(log_probs * tq).sum() / tq.sum()
```

### W3-3: `crawler/app/web/proxy_manager.py` — Confirm validation timeout reads from config

**Problem:** Proxy validation timeout is hardcoded to `8` in some call sites instead of reading `config.proxy_validate_timeout`.

**Fix:** Audit all `timeout=` arguments in `proxy_manager.py`; replace hardcoded values with `self._config.proxy_validate_timeout` (or pass config in).

### W3-4: `crawler/app/core/worker.py` — Warn UI when entering direct-connect mode

**Problem:** When proxy pool is empty, worker silently uses direct connection. User sees "0 proxies valid" but doesn't know crawling still works.

**Fix:** Emit a one-time warning signal when first entering direct-connect mode:

```python
if proxy is None and not self._warned_direct:
    self._warned_direct = True
    self.event_signal.emit({"type": "warn", "msg": "⚠ Proxy 池為空，使用直連模式"})
```

### W3-5: `crawler/app/db/pool_db.py` — Retry backoff on `OperationalError: database is locked`

**Problem:** Under high concurrency (10 workers), SQLite busy_timeout triggers, then raises `OperationalError`. Currently this crashes the worker.

**Fix:** Wrap `transaction()` with up to 3 retries using exponential backoff:

```python
import time

_RETRY_DELAYS = (0.1, 0.3, 1.0)

def transaction(self, fn):
    for attempt, delay in enumerate(_RETRY_DELAYS, 1):
        try:
            with self._conn:
                return fn(self._conn)
        except sqlite3.OperationalError as e:
            if "locked" not in str(e) or attempt == len(_RETRY_DELAYS):
                raise
            print(f"[pool_db] DB busy, retry {attempt}/{len(_RETRY_DELAYS)} in {delay}s", flush=True)
            time.sleep(delay)
```

### W3-6: `sb3/app/data/pool_db.py` — Same retry backoff

Same pattern as W3-5, applied to the sb3-side `pool_db.py`. Log to stderr. Max 3 retries.

### W3-7: Both `pool_db.py` files — Idempotent migration via PRAGMA

**Problem:** `ALTER TABLE ADD COLUMN` is wrapped in a bare `except OperationalError`, masking unrelated schema errors.

**Fix:** Use `PRAGMA table_info(puzzles)` to check column existence before ALTER:

```python
def _migrate(self, conn) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(puzzles)")}
    for col, definition in _EXTRA_COLUMNS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE puzzles ADD COLUMN {col} {definition}")
```

Where `_EXTRA_COLUMNS` is a dict of `{column_name: sql_type_and_default}`.

### W3-8: `crawler/app/gui/stats_panel.py` — Safety comment

`_insert_times` deque is only ever accessed from PyQt signal slots, which are serialized on the main thread. No code change needed — add a one-line comment:

```python
# _insert_times is only accessed from signal slots (main thread) — no lock needed
```

---

## Testing Strategy

**Wave 1:** Each fix is independently testable:
- W1-1: Insert an unsolvable puzzle into test DB; verify `RuntimeError` raised (not infinite hang)
- W1-2: Mock `_bc_pass` with all-zero quality array; verify returns without NaN
- W1-3: Mock `model.predict` to raise; verify callback returns `True` (training continues)
- W1-4: Mock worker with raising fetch function; verify traceback appears in emitted signal
- W1-5: Mock QThread that never stops; verify `terminate()` called

**Wave 2:** Integration tests:
- W2-1: Run forward pass; verify output shape matches pre-change (same (B, 921) features)
- W2-2: Concurrent `_on_step` calls from threads; verify no deque corruption
- W2-3: Create `PuzzlePoolDB`; verify `__del__` calls `close()` without error
- W2-4: Mock DB to raise; verify panel shows error label, not unhandled exception
- W2-5: Not easily testable in unit test — verify no `ResourceWarning` in integration run
- W2-6: Verify `get_pool_stats()` not called more than once per 2 seconds under rapid iteration

**Wave 3:** Mostly regression tests — verify existing behavior unchanged after each fix.
