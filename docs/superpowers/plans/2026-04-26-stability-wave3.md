# Stability Wave 3 — Minor Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eight minor fixes: observation board copy, BC log_probs clamp, proxy timeout alignment, direct-connect UI warning, retry backoff in both pool_db files, idempotent migration in both pool_db files, and a safety comment in stats_panel.

**Architecture:** Eight small targeted edits across six files. Two pairs of symmetric fixes (retry backoff + idempotent migration apply to both pool_db files). Tests extend existing test files where possible. Requires Waves 1 and 2 to be merged first.

**Tech Stack:** Python 3.12, PyTorch, SQLite, PyQt6, pytest

---

## Files Modified

| File | Change |
|------|--------|
| `sb3/app/rl/envs/sudoku_gym_env.py` | `board = self.board.copy()` in `_obs()` |
| `sb3/app/rl/models/sudoku_ppo.py` | `log_probs.clamp(min=-1e9)` before BC loss |
| `crawler/app/web/proxy_manager.py` | Align `validate_all()` default timeout to `proxy_validate_timeout` default |
| `crawler/app/core/worker.py` | Emit one-time warn when entering direct-connect mode |
| `crawler/app/db/pool_db.py` | Add `_retry_transaction()` helper; add idempotent `_migrate()` |
| `sb3/app/data/pool_db.py` | Add `_retry_transaction()` helper; add idempotent `_migrate()` |
| `crawler/app/gui/stats_panel.py` | Add safety comment on `_insert_times` |
| `sb3/tests/test_gym_env_stability.py` | Extend with obs copy test |
| `sb3/tests/test_bc_guards.py` | Extend with clamp test |
| `crawler/tests/test_worker_stability.py` | Extend with direct-connect warn test |
| `crawler/tests/test_pool_db.py` | Extend with retry + idempotent migration tests |
| `sb3/tests/test_pool_db_close.py` | Extend with retry + idempotent migration tests |

---

## Task 1: Copy board before building observation

**Files:**
- Modify: `sb3/app/rl/envs/sudoku_gym_env.py:214-252`
- Test: `sb3/tests/test_gym_env_stability.py` (extend)

- [ ] **Step 1: Write the test**

Add to `sb3/tests/test_gym_env_stability.py`:

```python
def test_obs_uses_board_copy_not_reference(tmp_path):
    """_obs() must not hold a live reference to self.board after returning."""
    db_path = _make_db(tmp_path)
    env = SudokuGymEnv(db_path=db_path, difficulty=1)

    # Manually set a non-zero board state
    env.board = np.zeros((9, 9), dtype=np.int8)
    env.board[0, 0] = 5
    env.fixed = np.zeros((9, 9), dtype=bool)
    env.solution = np.zeros((9, 9), dtype=np.int8)
    env.candidates_cache = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
    env.candidate_count_grid = np.full((9, 9), 9, dtype=np.int8)
    env.single_candidate_grid = np.zeros((9, 9), dtype=np.float32)

    obs = env._obs()

    # Mutate board AFTER obs is built
    env.board[0, 0] = 9

    # Channel 4 (digit 5, index 4) should still be 1 at (0,0) in obs
    assert obs[4, 0, 0] == 1.0, \
        "obs was affected by post-obs board mutation — _obs() is not using a copy"
```

- [ ] **Step 2: Run test to confirm it PASSES already (baseline check)**

```
cd sb3 && python -m pytest tests/test_gym_env_stability.py::test_obs_uses_board_copy_not_reference -v
```

Expected: PASS already — `_obs()` reads `self.board` but the obs array is built from comparisons (`self.board == v`), which copies values into the float array. This test is a regression guard, not a failing case.

- [ ] **Step 3: Add explicit board copy in `_obs()`**

In `sb3/app/rl/envs/sudoku_gym_env.py`, replace the first line of `_obs()` (line 214-215):

```python
    def _obs(self) -> np.ndarray:
        obs = np.zeros((self.N_CHANNELS, 9, 9), dtype=np.float32)
```

With:

```python
    def _obs(self) -> np.ndarray:
        board = self.board.copy()  # isolate obs snapshot from live board state
        obs = np.zeros((self.N_CHANNELS, 9, 9), dtype=np.float32)
```

Then replace all `self.board` references inside `_obs()` with `board`:
- Line 219: `obs[v - 1] = (board == v).astype(np.float32)`
- Line 222-226: replace `if self.board[r, c] == 0` with `if board[r, c] == 0`
- Lines 234-243: replace `self.board[r, :]`, `self.board[:, c]`, `self.board[br*3:...]` with `board[...]`

Full updated `_obs()`:

```python
    def _obs(self) -> np.ndarray:
        board = self.board.copy()  # isolate obs snapshot from live board state
        obs = np.zeros((self.N_CHANNELS, 9, 9), dtype=np.float32)

        # Channels 0-8: one-hot board planes (digit 1..9 → index 0..8)
        for v in range(1, 10):
            obs[v - 1] = (board == v).astype(np.float32)

        # Channels 9-17: per-digit candidate planes (v is still legal at (r,c))
        for r in range(9):
            for c in range(9):
                if board[r, c] == 0:
                    for v in self.candidates_cache[r][c]:
                        obs[9 + v - 1, r, c] = 1.0

        # Channel 18: fixed (given) cells
        obs[18] = self.fixed.astype(np.float32)
        # Channel 19: empty cells
        obs[19] = (board == 0).astype(np.float32)

        # Channel 20: row fill ratio
        for r in range(9):
            obs[20, r, :] = float(np.count_nonzero(board[r, :] != 0)) / 9.0
        # Channel 21: col fill ratio
        for c in range(9):
            obs[21, :, c] = float(np.count_nonzero(board[:, c] != 0)) / 9.0
        # Channel 22: box fill ratio
        for br in range(3):
            for bc in range(3):
                box = board[br*3:(br+1)*3, bc*3:(bc+1)*3]
                obs[22, br*3:(br+1)*3, bc*3:(bc+1)*3] = float(np.count_nonzero(box != 0)) / 9.0

        # Channel 23: candidate count / 9.0
        obs[23] = self.candidate_count_grid.astype(np.float32) / 9.0
        # Channel 24: naked-single flag
        obs[24] = self.single_candidate_grid
        # Channel 25: hidden-single flag
        obs[25] = self._reward_computer.compute_hidden_single_grid()

        return obs
```

- [ ] **Step 4: Run all gym_env tests**

```
cd sb3 && python -m pytest tests/test_gym_env_stability.py tests/test_obs_encoding.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```
git add sb3/app/rl/envs/sudoku_gym_env.py sb3/tests/test_gym_env_stability.py
git commit -m "fix(sb3): copy board before building obs in _obs() to isolate snapshot from live state"
```

---

## Task 2: Clamp log_probs before BC loss to prevent -inf×0=NaN

**Files:**
- Modify: `sb3/app/rl/models/sudoku_ppo.py:123`
- Test: `sb3/tests/test_bc_guards.py` (extend)

- [ ] **Step 1: Write the failing test**

Add to `sb3/tests/test_bc_guards.py`:

```python
def test_bc_pass_masked_actions_no_nan():
    """BC pass must not produce NaN when some log_probs are -inf (masked actions)."""
    import torch
    from unittest.mock import MagicMock

    model = _make_ppo()

    # Create a scenario: one teacher action is a MASKED cell (log_prob = -inf)
    n = 16
    model._teacher_actions = np.zeros((n, 1), dtype=np.int64)
    model._teacher_quality = np.ones((n, 1), dtype=np.float32) * 0.5

    # Inject rollout buffer: action_masks has the teacher action masked out (=0)
    obs_np = np.zeros((n, *model.observation_space.shape), dtype=np.float32)
    masks_np = np.ones((n, 729), dtype=np.float32)
    masks_np[:, 0] = 0.0  # mask out action 0 — teacher action 0 is masked

    model.rollout_buffer = MagicMock()
    model.rollout_buffer.observations = obs_np
    model.rollout_buffer.action_masks  = masks_np

    # Run BC pass — should not produce NaN in params
    model._bc_pass()

    for p in model.policy.parameters():
        assert not torch.isnan(p).any(), "NaN found in parameter after masked-action BC pass"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_bc_guards.py::test_bc_pass_masked_actions_no_nan -v
```

Expected: FAIL — when all teacher actions are masked, `log_probs` contains `-inf`, and `-inf * 0.5` may produce NaN.

- [ ] **Step 3: Add `clamp` before the BC loss computation**

In `sb3/app/rl/models/sudoku_ppo.py`, find line 123 (after `evaluate_actions`):

```python
        _, log_probs, _ = self.policy.evaluate_actions(obs_t, ta, action_masks=masks_t)

        bc_loss = -(log_probs * tq).sum() / tq.sum()
```

Add the clamp between them:

```python
        _, log_probs, _ = self.policy.evaluate_actions(obs_t, ta, action_masks=masks_t)
        log_probs = log_probs.clamp(min=-1e9)  # prevent -inf * 0 = NaN for masked actions

        bc_loss = -(log_probs * tq).sum() / tq.sum()
```

- [ ] **Step 4: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_bc_guards.py -v
```

Expected: Both BC guard tests PASS.

- [ ] **Step 5: Commit**

```
git add sb3/app/rl/models/sudoku_ppo.py sb3/tests/test_bc_guards.py
git commit -m "fix(sb3): clamp log_probs in _bc_pass() to prevent -inf*0=NaN from masked actions"
```

---

## Task 3: Align `validate_all()` default timeout to config default

**Files:**
- Modify: `crawler/app/web/proxy_manager.py:129`

**Context:** `validate_all()` has `timeout=8` as its default parameter, while `start_background_validation()` (which the crawler actually uses) takes `timeout` from `config.proxy_validate_timeout` (default 3s). The standalone `validate_all()` default is inconsistent. Change it to 3 to match the config default.

- [ ] **Step 1: Locate the default in `validate_all()`**

In `crawler/app/web/proxy_manager.py`, find line 129:

```python
    def validate_all(
        self,
        max_validate=None,
        max_workers=100,
        timeout=8,
        verbose=True,
    ):
```

- [ ] **Step 2: Change the default to 3**

```python
    def validate_all(
        self,
        max_validate=None,
        max_workers=100,
        timeout=3,
        verbose=True,
    ):
```

- [ ] **Step 3: Run crawler tests**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass. (No new test needed — this is a default-value alignment that only affects callers who omit the argument.)

- [ ] **Step 4: Commit**

```
git add crawler/app/web/proxy_manager.py
git commit -m "fix(crawler): align validate_all() default timeout=3 with proxy_validate_timeout config default"
```

---

## Task 4: Emit one-time warning when worker enters direct-connect mode

**Files:**
- Modify: `crawler/app/core/worker.py`
- Test: `crawler/tests/test_worker_stability.py` (extend)

- [ ] **Step 1: Write the failing test**

Add to `crawler/tests/test_worker_stability.py`:

```python
def test_worker_warns_on_direct_connect(qapp, tmp_path, monkeypatch):
    """Worker must emit one 'warn' event when proxy pool is empty (direct connect)."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig
    import app.core.worker as worker_mod

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1, max_pool_size=100)

    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None  # empty proxy pool

    worker = CrawlerWorker(0, config, proxy, db)

    emitted = []
    worker.event_signal.emit = lambda d: emitted.append(d)
    worker._stop = False

    # Patch fetch to succeed so we get past the try block
    monkeypatch.setattr(
        worker_mod, "fetch_puzzle_via_requests",
        lambda *a, **kw: ([[0]*9]*9, [[False]*9]*9),
    )
    # Patch upsert to succeed and stop after first insert
    original_upsert = db.upsert_puzzle
    call_count = [0]

    def patched_upsert(board, source, level):
        call_count[0] += 1
        worker._stop = True
        return {"inserted": True, "puzzle_id": 1}

    db.upsert_puzzle = patched_upsert

    worker.run()

    warn_events = [e for e in emitted if e.get("type") == "warn"]
    assert warn_events, "No warn event emitted when proxy pool is empty"
    assert "直連" in warn_events[0]["msg"] or "direct" in warn_events[0]["msg"].lower(), \
        f"Expected direct-connect warning, got: {warn_events[0]['msg']!r}"

    # Second run: warning should NOT be emitted again (one-time only)
    emitted.clear()
    worker._stop = False
    call_count[0] = 0

    def patched_upsert2(board, source, level):
        call_count[0] += 1
        worker._stop = True
        return {"inserted": True, "puzzle_id": 2}

    db.upsert_puzzle = patched_upsert2
    worker.run()

    warn_events2 = [e for e in emitted if e.get("type") == "warn"]
    assert not warn_events2, "Warn should only be emitted once, not on every iteration"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_worker_warns_on_direct_connect -v
```

Expected: FAIL — no `warn` event is emitted when proxy is None.

- [ ] **Step 3: Add `_warned_direct` flag and warning emit to `worker.py`**

In `CrawlerWorker.__init__()`, add after `self._stats_cache`:

```python
        self._warned_direct: bool = False
```

In `run()`, find the proxy section (around line 54-56):

```python
            # Choose proxy (None = direct connection)
            proxy_dict = self.proxy_manager.get_requests_proxy()
            server_url: str | None = proxy_dict.get("http") if proxy_dict else None
```

Add the warning immediately after:

```python
            # Choose proxy (None = direct connection)
            proxy_dict = self.proxy_manager.get_requests_proxy()
            server_url: str | None = proxy_dict.get("http") if proxy_dict else None

            if proxy_dict is None and not self._warned_direct:
                self._warned_direct = True
                self.event_signal.emit({
                    "type": "warn",
                    "msg": "⚠ Proxy 池為空，使用直連模式",
                    "worker_id": self.worker_id,
                })
```

- [ ] **Step 4: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_worker_stability.py::test_worker_warns_on_direct_connect -v
```

Expected: PASS

- [ ] **Step 5: Update `_on_worker_event` in `main_window.py` to handle the new `warn` type**

In `crawler/app/gui/main_window.py`, extend `_on_worker_event()` to handle `warn`:

```python
    def _on_worker_event(self, event: dict) -> None:
        t = event["type"]
        if t == "inserted":
            self.stats_panel.increment_level(event["level"])
            self.log_widget.add_message(
                f"✓ L{event['level']} puzzle inserted (id={event['puzzle_id']})", "green"
            )
        elif t == "blocked":
            self.log_widget.add_message(
                f"⚠ BlockedError → blacklist {event['proxy']}", "yellow"
            )
        elif t == "warn":
            self.log_widget.add_message(event["msg"], "yellow")
        elif t == "error":
            self.log_widget.add_message(f"✗ {event['msg']}", "red")
```

- [ ] **Step 6: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```
git add crawler/app/core/worker.py crawler/app/gui/main_window.py crawler/tests/test_worker_stability.py
git commit -m "fix(crawler): emit one-time warn when worker enters direct-connect mode (empty proxy pool)"
```

---

## Task 5: Retry backoff in crawler `pool_db.py`

**Files:**
- Modify: `crawler/app/db/pool_db.py`
- Test: `crawler/tests/test_pool_db.py` (extend)

**Context:** `transaction()` is a context manager — it can't be retried with a loop. Instead, add a `_retry_transaction(fn)` helper that runs a callable with retry, and update `upsert_puzzle()` to use it since that's the high-concurrency write path.

- [ ] **Step 1: Write the failing test**

Add to `crawler/tests/test_pool_db.py`:

```python
def test_upsert_retries_on_locked_db(tmp_path, monkeypatch):
    """upsert_puzzle must retry up to 3 times on OperationalError: database is locked."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    import sqlite3
    from app.db.pool_db import PuzzlePoolDB

    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)
    board = [[0]*9 for _ in range(9)]
    board[0][0] = 1

    call_count = [0]
    original_get_conn = db._get_conn

    def flaky_get_conn():
        conn = original_get_conn()
        if call_count[0] < 2:
            call_count[0] += 1
            raise sqlite3.OperationalError("database is locked")
        return conn

    monkeypatch.setattr(db, "_get_conn", flaky_get_conn)

    # Before fix: raises on first failure
    # After fix: retries and succeeds on 3rd attempt
    result = db.upsert_puzzle(board, level=1)
    assert result["inserted"] is True
```

- [ ] **Step 2: Run test to verify it fails**

```
cd crawler && python -m pytest tests/test_pool_db.py::test_upsert_retries_on_locked_db -v
```

Expected: FAIL — `OperationalError: database is locked` propagates immediately.

- [ ] **Step 3: Add `import time`, `_LOCK_RETRY_DELAYS`, and `_retry_transaction()` to `crawler/app/db/pool_db.py`**

Add `import time` after the existing imports (around line 10).

Add the module-level constant after the `now_str()` function:

```python
_LOCK_RETRY_DELAYS = (0.1, 0.3, 1.0)
```

Add the `_retry_transaction()` method to `PuzzlePoolDB`, after the `transaction()` context manager:

```python
    def _retry_transaction(self, fn):
        """Run fn(conn) with automatic retry on 'database is locked' errors."""
        for attempt, delay in enumerate(_LOCK_RETRY_DELAYS, 1):
            conn = self._get_conn()
            try:
                result = fn(conn)
                conn.commit()
                return result
            except sqlite3.OperationalError as e:
                conn.rollback()
                if "locked" not in str(e).lower() or attempt == len(_LOCK_RETRY_DELAYS):
                    raise
                print(
                    f"[pool_db] DB busy, retry {attempt}/{len(_LOCK_RETRY_DELAYS)} in {delay}s",
                    flush=True,
                )
                time.sleep(delay)
```

- [ ] **Step 4: Update `upsert_puzzle()` to use `_retry_transaction()`**

In `crawler/app/db/pool_db.py`, replace the `with self.transaction() as conn:` block inside `upsert_puzzle()`:

```python
    def upsert_puzzle(self, board: List[List[int]], source: str = "websudoku", level: int = 1) -> Dict[str, Any]:
        puzzle = self.board_to_string(board)
        givens = sum(1 for ch in puzzle if ch != "0")
        puzzle_key = puzzle
        now = now_str()

        def _do(conn):
            row = conn.execute(
                "SELECT id FROM puzzles WHERE puzzle_key = ?", (puzzle_key,)
            ).fetchone()

            if row:
                return {
                    "inserted":   False,
                    "puzzle_id":  int(row["id"]),
                    "puzzle_key": puzzle_key,
                }

            init_empty = 81 - givens
            cur = conn.execute("""
                INSERT INTO puzzles
                    (puzzle_key, puzzle, givens, level, source, status,
                     tries, best_empty, best_reward, last_reward, last_empty,
                     locked_by, locked_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'new', 0, ?, 0, 0, ?,
                        NULL, NULL, ?, ?)
            """, (puzzle_key, puzzle, givens, int(level), source,
                  init_empty, init_empty, now, now))

            return {
                "inserted":   True,
                "puzzle_id":  int(cur.lastrowid),
                "puzzle_key": puzzle_key,
            }

        return self._retry_transaction(_do)
```

- [ ] **Step 5: Run test to verify it passes**

```
cd crawler && python -m pytest tests/test_pool_db.py::test_upsert_retries_on_locked_db -v
```

Expected: PASS

- [ ] **Step 6: Run full crawler test suite**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```
git add crawler/app/db/pool_db.py crawler/tests/test_pool_db.py
git commit -m "fix(crawler): add _retry_transaction() with 3-attempt backoff for DB lock contention"
```

---

## Task 6: Retry backoff in sb3 `pool_db.py`

**Files:**
- Modify: `sb3/app/data/pool_db.py`
- Test: `sb3/tests/test_pool_db_close.py` (extend)

**Context:** Symmetric fix to Task 5, applied to the sb3-side `pool_db.py`. Same `_retry_transaction()` pattern; logs to stderr.

- [ ] **Step 1: Write the failing test**

Add to `sb3/tests/test_pool_db_close.py`:

```python
def test_fetch_retries_on_locked_db(tmp_path, monkeypatch):
    """fetch_one_puzzle_for_training must retry up to 3 times on locked DB."""
    import sqlite3
    from app.data.pool_db import PuzzlePoolDB

    db_path = str(tmp_path / "test_retry.db")
    db = PuzzlePoolDB(db_path)

    board = [[0]*9 for _ in range(9)]
    board[0][0] = 1
    db.upsert_puzzle(board, level=1)

    call_count = [0]
    original_get_conn = db._get_conn

    def flaky_get_conn():
        conn = original_get_conn()
        if call_count[0] < 2:
            call_count[0] += 1
            raise sqlite3.OperationalError("database is locked")
        return conn

    monkeypatch.setattr(db, "_get_conn", flaky_get_conn)

    result = db.fetch_one_puzzle_for_training(level=1)
    assert result is not None, "Expected puzzle row, got None"
```

- [ ] **Step 2: Run test to verify it fails**

```
cd sb3 && python -m pytest tests/test_pool_db_close.py::test_fetch_retries_on_locked_db -v
```

Expected: FAIL — `OperationalError` propagates immediately.

- [ ] **Step 3: Add `import time`, `_LOCK_RETRY_DELAYS`, and `_retry_transaction()` to `sb3/app/data/pool_db.py`**

Add `import time` after the existing imports (around line 10).

Add after the `now_str()` function:

```python
_LOCK_RETRY_DELAYS = (0.1, 0.3, 1.0)
```

Add `_retry_transaction()` after the `transaction()` context manager:

```python
    def _retry_transaction(self, fn):
        """Run fn(conn) with automatic retry on 'database is locked' errors."""
        for attempt, delay in enumerate(_LOCK_RETRY_DELAYS, 1):
            conn = self._get_conn()
            try:
                result = fn(conn)
                conn.commit()
                return result
            except sqlite3.OperationalError as e:
                conn.rollback()
                if "locked" not in str(e).lower() or attempt == len(_LOCK_RETRY_DELAYS):
                    raise
                print(
                    f"[pool_db] DB busy, retry {attempt}/{len(_LOCK_RETRY_DELAYS)} in {delay}s",
                    flush=True,
                )
                time.sleep(delay)
```

- [ ] **Step 4: Update `fetch_one_puzzle_for_training()` to use `_retry_transaction()`**

In `sb3/app/data/pool_db.py`, replace the `with self.transaction() as conn:` block inside `fetch_one_puzzle_for_training()`:

```python
    def fetch_one_puzzle_for_training(
        self,
        worker_name: str = "trainer",
        max_tries: Optional[int] = None,
        level: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        now = now_str()
        level_clause = "AND level=?" if level is not None else ""
        tries_clause = "AND tries < ?" if max_tries is not None else ""

        args = []
        if level is not None:
            args.append(int(level))
        if max_tries is not None:
            args.append(int(max_tries))

        def _do(conn):
            row = conn.execute(
                f"SELECT * FROM puzzles"
                f" WHERE status IN ('new','training')"
                f" {level_clause} {tries_clause}"
                f" ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END,"
                f"          tries ASC, best_empty ASC, id ASC"
                f" LIMIT 1",
                args,
            ).fetchone()

            if row is None:
                return None

            conn.execute("""
                UPDATE puzzles
                SET status='training', locked_by=?, locked_at=?, updated_at=?
                WHERE id=?
            """, (worker_name, now, now, row["id"]))

            return dict(
                conn.execute(
                    "SELECT * FROM puzzles WHERE id=?", (row["id"],)
                ).fetchone()
            )

        return self._retry_transaction(_do)
```

- [ ] **Step 5: Run test to verify it passes**

```
cd sb3 && python -m pytest tests/test_pool_db_close.py::test_fetch_retries_on_locked_db -v
```

Expected: PASS

- [ ] **Step 6: Run full sb3 test suite**

```
cd sb3 && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 7: Commit**

```
git add sb3/app/data/pool_db.py sb3/tests/test_pool_db_close.py
git commit -m "fix(sb3): add _retry_transaction() with 3-attempt backoff for DB lock contention"
```

---

## Task 7: Idempotent migration via `PRAGMA table_info` in both `pool_db.py` files

**Files:**
- Modify: `crawler/app/db/pool_db.py:61-91`
- Modify: `sb3/app/data/pool_db.py:61-91`
- Test: both test files (extend)

**Context:** Both files have the same migration pattern — `ALTER TABLE ADD COLUMN level` wrapped in `try/except OperationalError`. The fix adds `_EXTRA_COLUMNS` dict and extracts a `_migrate(conn)` method that checks column existence via `PRAGMA table_info` before altering.

- [ ] **Step 1: Write the failing tests**

Add to `crawler/tests/test_pool_db.py`:

```python
def test_migration_idempotent(tmp_path):
    """Opening the DB twice must not raise — migration must be idempotent."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from app.db.pool_db import PuzzlePoolDB
    import sqlite3

    db_path = str(tmp_path / "migrate_test.db")

    # Create a minimal DB without 'level' column
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_key TEXT NOT NULL UNIQUE,
            puzzle TEXT NOT NULL,
            givens INTEGER NOT NULL,
            source TEXT NOT NULL DEFAULT 'websudoku',
            status TEXT NOT NULL DEFAULT 'new',
            tries INTEGER NOT NULL DEFAULT 0,
            best_empty INTEGER NOT NULL DEFAULT 81,
            best_reward REAL NOT NULL DEFAULT 0,
            last_reward REAL NOT NULL DEFAULT 0,
            last_empty INTEGER NOT NULL DEFAULT 81,
            locked_by TEXT DEFAULT NULL,
            locked_at TEXT DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

    # First open — should add 'level' column
    db1 = PuzzlePoolDB(db_path)

    # Second open — must NOT fail (idempotent)
    db2 = PuzzlePoolDB(db_path)

    # Verify 'level' column exists
    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(puzzles)")}
    conn.close()
    assert "level" in cols, "'level' column missing after migration"
```

Add to `sb3/tests/test_pool_db_close.py`:

```python
def test_migration_idempotent_sb3(tmp_path):
    """Opening the sb3 DB twice must not raise — migration must be idempotent."""
    import sqlite3
    from app.data.pool_db import PuzzlePoolDB

    db_path = str(tmp_path / "migrate_sb3.db")

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE puzzles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_key TEXT NOT NULL UNIQUE,
            puzzle TEXT NOT NULL,
            givens INTEGER NOT NULL,
            source TEXT NOT NULL DEFAULT 'websudoku',
            status TEXT NOT NULL DEFAULT 'new',
            tries INTEGER NOT NULL DEFAULT 0,
            best_empty INTEGER NOT NULL DEFAULT 81,
            best_reward REAL NOT NULL DEFAULT 0,
            last_reward REAL NOT NULL DEFAULT 0,
            last_empty INTEGER NOT NULL DEFAULT 81,
            locked_by TEXT DEFAULT NULL,
            locked_at TEXT DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

    db1 = PuzzlePoolDB(db_path)
    db2 = PuzzlePoolDB(db_path)  # must not raise

    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(puzzles)")}
    conn.close()
    assert "level" in cols
```

- [ ] **Step 2: Run tests to verify they pass already (baseline — existing code handles this OK)**

```
cd crawler && python -m pytest tests/test_pool_db.py::test_migration_idempotent -v
cd sb3 && python -m pytest tests/test_pool_db_close.py::test_migration_idempotent_sb3 -v
```

Expected: PASS — the existing `try/except` already handles the idempotent case. These are regression guards.

- [ ] **Step 3: Replace the `try/except` migration with `PRAGMA table_info` in `crawler/app/db/pool_db.py`**

Add a module-level constant after `_LOCK_RETRY_DELAYS`:

```python
_EXTRA_COLUMNS = {
    "level": "INTEGER NOT NULL DEFAULT 1",
}
```

Add a `_migrate()` method to `PuzzlePoolDB` (after `_get_conn`, before `transaction`):

```python
    def _migrate(self, conn) -> None:
        """Add any missing columns to puzzles table. Safe to call multiple times."""
        existing = {row[1] for row in conn.execute("PRAGMA table_info(puzzles)")}
        for col, definition in _EXTRA_COLUMNS.items():
            if col not in existing:
                conn.execute(
                    f"ALTER TABLE puzzles ADD COLUMN {col} {definition}"
                )
```

In `_init_db()`, replace the `try/except OperationalError` block (lines 85-91):

```python
            # 舊資料庫遷移：必須在建立 level 索引之前確保欄位存在
            try:
                conn.execute(
                    "ALTER TABLE puzzles"
                    " ADD COLUMN level INTEGER NOT NULL DEFAULT 1"
                )
            except sqlite3.OperationalError:
                pass  # 欄位已存在（新建 DB 或已遷移過），略過
```

With:

```python
            self._migrate(conn)
```

- [ ] **Step 4: Apply the same change to `sb3/app/data/pool_db.py`**

Same as Step 3, applied to `sb3/app/data/pool_db.py`. Add `_EXTRA_COLUMNS`, add `_migrate()`, replace the `try/except` block in `_init_db()` with `self._migrate(conn)`.

- [ ] **Step 5: Run both test suites**

```
cd crawler && python -m pytest tests/ -v
cd sb3 && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```
git add crawler/app/db/pool_db.py sb3/app/data/pool_db.py crawler/tests/test_pool_db.py sb3/tests/test_pool_db_close.py
git commit -m "fix: replace try/except migration with PRAGMA table_info check in both pool_db files"
```

---

## Task 8: Safety comment in `stats_panel.py`

**Files:**
- Modify: `crawler/app/gui/stats_panel.py:94-97`

**Context:** `_insert_times` is a `deque` accessed only from signal slots, which PyQt6 serializes on the main thread. No lock is needed, but the reasoning is non-obvious. Add a one-line comment to prevent future over-engineering.

- [ ] **Step 1: Add the comment**

In `crawler/app/gui/stats_panel.py`, find `increment_level()` (around line 90). Add a comment before the deque access:

```python
    def increment_level(self, level: int) -> None:
        idx = level - 1
        self._counts[idx] += 1
        self._level_vals[idx].setText(f"{self._counts[idx]:,}")
        now = time.time()
        # _insert_times is only accessed from signal slots (main thread) — no lock needed
        self._insert_times.append(now)
        while self._insert_times and now - self._insert_times[0] > 60:
            self._insert_times.popleft()
```

- [ ] **Step 2: Run crawler tests**

```
cd crawler && python -m pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 3: Commit**

```
git add crawler/app/gui/stats_panel.py
git commit -m "docs(crawler): add safety comment on _insert_times deque in stats_panel"
```

---

## Wave 3 Complete

Run the full test suites one final time:

```
cd sb3 && python -m pytest tests/ -v
cd crawler && python -m pytest tests/ -v
```

All 8 minor hardening fixes applied:
- ✅ W3-1: `_obs()` board copy
- ✅ W3-2: `log_probs.clamp` in BC pass
- ✅ W3-3: `validate_all()` timeout alignment
- ✅ W3-4: Direct-connect UI warning
- ✅ W3-5: Crawler `pool_db` retry backoff
- ✅ W3-6: sb3 `pool_db` retry backoff
- ✅ W3-7: Idempotent migration in both `pool_db` files
- ✅ W3-8: `stats_panel` safety comment
