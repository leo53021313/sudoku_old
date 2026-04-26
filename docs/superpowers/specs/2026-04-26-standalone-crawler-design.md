# Standalone Sudoku Crawler — Design Spec
Date: 2026-04-26

## Overview

Extract the puzzle-crawling subsystem from `legacy/` into a fully independent `crawler/` program.
The crawler scrapes Sudoku puzzles from `east.websudoku.com` via rotating proxies and inserts them
into the shared `data/puzzle_pool.db`. It includes a PyQt6 GUI with real-time status display.

The crawler has **no dependency on `legacy/`** — it copies the required modules and strips out
all training-system logic.

---

## File Structure

```
sudoku_old/
└── crawler/
    ├── crawler.py                  ← entry point; run as: cd crawler && python crawler.py
    ├── requirements.txt            ← PyQt6, requests, PySocks
    ├── data/
    │   └── config.json             ← persisted user settings (auto-created on first run)
    └── app/
        ├── web/
        │   ├── reader.py           ← fetch_puzzle_via_requests(), BlockedError, get_level_url()
        │   └── proxy_manager.py    ← ProxyManager: download, validate, round-robin rotation
        ├── db/
        │   └── pool_db.py          ← PuzzlePoolDB (crawler-only subset: upsert_puzzle, get_pool_stats)
        ├── core/
        │   └── worker.py           ← CrawlerWorker(QThread): fetch → insert → sleep loop
        └── gui/
            ├── main_window.py      ← MainWindow (QMainWindow): assembles all widgets + toolbar
            ├── stats_panel.py      ← top row: per-difficulty counts + rate/proxy/workers/uptime
            ├── db_panel.py         ← DB status table (level × status) + progress bar
            ├── log_widget.py       ← scrolling QTextEdit log
            └── settings_dialog.py  ← ⚙ settings dialog
```

---

## Database

- **Path**: `../data/puzzle_pool.db` (relative to cwd; always run from `crawler/`)
- **Access**: thread-local SQLite connections, WAL mode, `busy_timeout=5000`
- **Schema**: unchanged from legacy — `puzzles` + `solutions` tables
- **Crawler-only methods** retained in `pool_db.py`:
  - `upsert_puzzle(board, source, level)` → inserts if not duplicate
  - `get_pool_stats(level=None)` → counts by status per level (for GUI table)
  - `board_to_string()` / `string_to_board()` helpers
- **Removed** from crawler's copy: `fetch_one_puzzle_for_training`, `mark_puzzle_attempt`,
  `save_solution`, `count_unsolved` — these are training-system concerns only

---

## Threading Model

```
Qt main thread (GUI)
│
├── ProxyManager
│   └── background validation: ThreadPoolExecutor(max_workers=validate_workers)
│       each thread: _test_one_proxy() → if valid, add to pool
│
└── N × CrawlerWorker(QThread)  [configurable, default 10]
    loop:
      1. proxy = proxy_manager.get_proxy()        round-robin, atomic
      2. level  = weighted_random(level_weights)  per config
      3. url    = get_level_url(level)
      4. board, fixed = fetch_puzzle_via_requests(url, proxy, timeout)
         ├── BlockedError → blacklist proxy, continue (retry next iteration)
         └── success      → db.upsert_puzzle(board, 'websudoku', level)
                            emit signal → GUI updates count
      5. sleep(uniform(min_delay, max_delay))
      6. if db_total >= max_pool_size: wait until db_total < resume_threshold
```

**GUI ↔ Worker communication**: workers emit `pyqtSignal(dict)` — main thread receives and
updates widgets. No direct widget access from worker threads.

**DB stats refresh**: `QTimer` fires every 5 seconds → query `get_pool_stats()` → update
`db_panel` table and progress bar.

---

## GUI Layout

```
┌─────────────────────────────────────────────────┐
│ 🕷 Sudoku Crawler    [▶ 開始] [■ 停止] [⚙ 設定] │  ← toolbar
├─────────────┬──────────────┬──────────┬──────────┤
│  L1 Easy    │  L2 Medium   │ L3 Hard  │ L4 Evil  │  ← this-session counts (large)
│   241       │    198       │   211    │   187    │
├─────────────┴──────────────┴──────────┴──────────┤
│  速率/min  │  Proxy 可用   │ Workers  │ 執行時間  │  ← runtime stats
│    23      │   47 / 312   │  10/20   │ 00:12:34  │
├───────────────────────────────────────────────────┤
│ 📦 DB 現況 (puzzle_pool.db)        總計 12,847 筆 │
│       L1     L2     L3     L4    合計             │
│ new   2841   2701   2798   2906  11246             │
│ train  280    271    290    300   1141             │
│ solved 120    130    110    100    460             │
│ ████████░░░░░░░░░░░░░  12,847 / 50,000 (26%)      │
├───────────────────────────────────────────────────┤
│ [10:23:01] ✓ L2 puzzle inserted (id=12847)        │  ← scrolling log
│ [10:23:02] ⚠ BlockedError → blacklist 31.14.x.x  │
│ [10:23:03] ✓ L3 puzzle inserted (id=12849)        │
└───────────────────────────────────────────────────┘
```

---

## Settings Dialog (⚙)

All settings persist to `crawler/data/config.json`. Changes apply immediately (no restart needed)
except "爬蟲執行緒數" which takes effect on next Start.

| Setting | Description | Default |
|---------|-------------|---------|
| 爬蟲執行緒數 | 同時爬取的 thread 數，越多越快但容易被封鎖 | 10 |
| 目標收錄上限 | DB 達到此數量後暫停爬取 | 50,000 |
| 恢復爬取門檻 | DB 低於此數時自動重新開始（供訓練系統消耗） | 30,000 |
| 各難度比例 L1/L2/L3/L4 | 爬取時的難度分配比例（自動正規化） | 25/25/25/25 |
| 最短請求間隔（秒） | 每次成功後的最短等待時間 | 0.0 |
| 最長請求間隔（秒） | 每次成功後的最長等待時間（隨機） | 0.3 |
| 請求逾時（秒） | 單次 HTTP 請求的最長等待時間 | 8 |
| Proxy 驗證執行緒數 | 啟動時同時測試幾個 proxy | 50 |
| Proxy 驗證逾時（秒） | 每個 proxy 的測試逾時時間 | 3 |

---

## Proxy System

Copied verbatim from `legacy/app/web/proxy_manager.py` with no logic changes:
- Downloads from 6 GitHub free-proxy sources (HTTP + SOCKS4/5)
- HTTP proxies sorted first (`_PROTO_PRIORITY`)
- Validation: HTTP → actual page fetch + `"puzzle_grid"` marker check; SOCKS → TCP connect
- Round-robin selection, atomic get+rotate under lock
- `blacklist_server(url)` removes permanently failed proxies

On startup: `download_all()` → `start_background_validation()` (daemon thread, incremental).
Proxy count shown live in GUI stats row.

---

## Source Modules: What Changes vs Legacy

| Module | Changes from legacy |
|--------|---------------------|
| `reader.py` | Remove Playwright/`WebSudokuReader` fallback; keep `fetch_puzzle_via_requests` + `BlockedError` + `get_level_url` only |
| `proxy_manager.py` | No logic changes; `stop_validation()` called on app quit |
| `pool_db.py` | Remove training methods (`fetch_one_puzzle_for_training`, `mark_puzzle_attempt`, `save_solution`, `count_unsolved`); keep upsert + stats |

---

## Running

```bash
cd crawler
python crawler.py
```

DB path resolves to `../data/puzzle_pool.db` relative to `crawler/`.
Legacy training and this crawler can run simultaneously — SQLite WAL mode supports concurrent writers.

---

## Out of Scope

- Playwright / browser-based fallback scraping
- Solution verification
- Any training-related DB operations
- Proxy export / import from file
