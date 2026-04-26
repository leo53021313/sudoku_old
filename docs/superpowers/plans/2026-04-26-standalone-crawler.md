# Standalone Sudoku Crawler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone `crawler/` program that scrapes Sudoku puzzles from east.websudoku.com via rotating proxies and stores them in `data/puzzle_pool.db`, with a PyQt6 GUI showing real-time status.

**Architecture:** Independent `crawler/` folder at repo root; copies and trims three modules from `legacy/` (reader, proxy_manager, pool_db) removing all training-system logic; N worker QThreads emit `pyqtSignal(dict)` events to the GUI main thread; DB stats table refreshed every 5 s via QTimer; settings persisted to `crawler/data/config.json`.

**Tech Stack:** Python 3.10+, PyQt6, requests, PySocks, SQLite (WAL mode)

---

## File Map

| File | Responsibility |
|------|----------------|
| `crawler/crawler.py` | Entry point: init deps, show window, kick off proxy download |
| `crawler/requirements.txt` | PyQt6, requests, PySocks |
| `crawler/config.py` | `CrawlerConfig` dataclass + JSON save/load |
| `crawler/app/db/pool_db.py` | Trimmed `PuzzlePoolDB`: upsert + stats only |
| `crawler/app/web/reader.py` | Trimmed reader: requests-only, no Playwright |
| `crawler/app/web/proxy_manager.py` | Verbatim copy + `get_requests_proxy()` method |
| `crawler/app/core/worker.py` | `CrawlerWorker(QThread)`: fetch → insert → sleep loop |
| `crawler/app/gui/log_widget.py` | Scrolling coloured log (QTextEdit) |
| `crawler/app/gui/stats_panel.py` | Session counts + rate/proxy/workers/uptime |
| `crawler/app/gui/db_panel.py` | DB status table (level × status) + progress bar |
| `crawler/app/gui/settings_dialog.py` | ⚙ settings form |
| `crawler/app/gui/main_window.py` | `MainWindow`: assembles all widgets + toolbar |
| `crawler/tests/test_pool_db.py` | Tests for upsert + stats |
| `crawler/tests/test_reader_parser.py` | Tests for HTML parser + helpers |
| `crawler/tests/test_config.py` | Tests for config save/load |

---

## Task 1: Scaffold directory structure + requirements.txt

**Files:**
- Create: `crawler/requirements.txt`
- Create: `crawler/app/__init__.py` (empty)
- Create: `crawler/app/web/__init__.py` (empty)
- Create: `crawler/app/db/__init__.py` (empty)
- Create: `crawler/app/core/__init__.py` (empty)
- Create: `crawler/app/gui/__init__.py` (empty)
- Create: `crawler/tests/__init__.py` (empty)
- Create: `crawler/data/.gitkeep` (empty)

- [ ] **Step 1: Create all directories (run from repo root)**

```bash
mkdir -p crawler/app/web crawler/app/db crawler/app/core crawler/app/gui crawler/data crawler/tests
```

- [ ] **Step 2: Create empty `__init__.py` files**

Create these five files, all empty:
- `crawler/app/__init__.py`
- `crawler/app/web/__init__.py`
- `crawler/app/db/__init__.py`
- `crawler/app/core/__init__.py`
- `crawler/app/gui/__init__.py`
- `crawler/tests/__init__.py`

- [ ] **Step 3: Create `crawler/data/.gitkeep`**

Empty file so git tracks the `data/` directory.

- [ ] **Step 4: Create `crawler/requirements.txt`**

```
PyQt6>=6.6.0
requests>=2.31.0
PySocks>=1.7.1
```

- [ ] **Step 5: Commit**

```bash
git add crawler/
git commit -m "feat(crawler): scaffold directory structure"
```

---

## Task 2: Trim and copy pool_db.py

**Files:**
- Create: `crawler/app/db/pool_db.py`
- Create: `crawler/tests/test_pool_db.py`

Copy `legacy/app/data/pool_db.py` and **remove** all methods after `get_pool_stats`:
`count_unsolved`, `fetch_one_puzzle_for_training`, `mark_puzzle_attempt`,
`mark_puzzle_skipped`, `save_solution`, `list_recent_puzzles`, `list_recent_solutions`.

- [ ] **Step 1: Write failing tests**

`crawler/tests/test_pool_db.py`:
```python
import pytest
from app.db.pool_db import PuzzlePoolDB


def _board(givens: dict) -> list:
    b = [[0] * 9 for _ in range(9)]
    for (r, c), v in givens.items():
        b[r][c] = v
    return b


@pytest.fixture
def db(tmp_path):
    return PuzzlePoolDB(str(tmp_path / "test.db"))


def test_upsert_inserts_new_puzzle(db):
    result = db.upsert_puzzle(_board({(0, 0): 5, (1, 1): 3}), "websudoku", level=1)
    assert result["inserted"] is True
    assert isinstance(result["puzzle_id"], int)
    assert len(result["puzzle_key"]) == 81


def test_upsert_skips_duplicate(db):
    board = _board({(0, 0): 5, (1, 1): 3})
    r1 = db.upsert_puzzle(board, "websudoku", level=1)
    r2 = db.upsert_puzzle(board, "websudoku", level=1)
    assert r1["inserted"] is True
    assert r2["inserted"] is False
    assert r1["puzzle_id"] == r2["puzzle_id"]


def test_get_pool_stats_counts_by_level(db):
    db.upsert_puzzle(_board({(0, 0): 1}), "websudoku", level=1)
    db.upsert_puzzle(_board({(0, 0): 2}), "websudoku", level=2)
    assert db.get_pool_stats(level=1)["total"] == 1
    assert db.get_pool_stats(level=1)["new"] == 1
    assert db.get_pool_stats()["total"] == 2


def test_board_string_roundtrip():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[8][8] = 9
    s = PuzzlePoolDB.board_to_string(board)
    assert len(s) == 81 and s[0] == "5" and s[80] == "9"
    back = PuzzlePoolDB.string_to_board(s)
    assert back[0][0] == 5 and back[8][8] == 9
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd crawler && pytest tests/test_pool_db.py -v
```
Expected: `ImportError` (module not yet created)

- [ ] **Step 3: Create `crawler/app/db/pool_db.py`**

Copy `legacy/app/data/pool_db.py` in full, then delete from line 246 to end of file
(everything from `def count_unsolved` onwards). Update the module comment at the top:

```python
# app/db/pool_db.py  (crawler-only subset: upsert + stats)
```

The kept methods are:
`__init__`, `_get_conn`, `transaction`, `_init_db`, `board_to_string`, `string_to_board`,
`steps_to_json`, `json_to_steps`, `upsert_puzzle`, `get_pool_stats`.

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd crawler && pytest tests/test_pool_db.py -v
```
Expected: 4 PASSes

- [ ] **Step 5: Commit**

```bash
git add crawler/app/db/pool_db.py crawler/tests/test_pool_db.py
git commit -m "feat(crawler): add trimmed pool_db (upsert + stats only)"
```

---

## Task 3: Trim and copy reader.py

**Files:**
- Create: `crawler/app/web/reader.py`
- Create: `crawler/tests/test_reader_parser.py`

Copy `legacy/app/web/reader.py` and **remove**:
- `_READ_BOARD_JS` constant (lines 26–36)
- `check_page_blocked` function (lines 75–84)
- `WebSudokuReader` class (lines 242–299)

- [ ] **Step 1: Write failing tests**

`crawler/tests/test_reader_parser.py`:
```python
import pytest
from app.web.reader import _PuzzleHTMLParser, get_level_url, BlockedError, SUDOKU_LEVELS


def _make_html(values: dict) -> str:
    """Build minimal websudoku-style HTML. values: {(col, row): digit_str}"""
    parts = []
    for row in range(9):
        for col in range(9):
            val = values.get((col, row), "")
            readonly = " readonly" if val else ""
            parts.append(f'<input id="f{col}{row}" value="{val}"{readonly}>')
    return "".join(parts)


def test_parser_reads_81_cells():
    html = _make_html({(0, 0): "5", (8, 8): "9"})
    p = _PuzzleHTMLParser()
    p.feed(html)
    assert p.cell_count == 81
    assert p.board[0][0] == 5
    assert p.board[8][8] == 9


def test_parser_fixed_flags():
    html = _make_html({(1, 2): "7"})  # col=1, row=2 → board[row][col] = board[2][1]
    p = _PuzzleHTMLParser()
    p.feed(html)
    assert p.fixed[2][1] is True
    assert p.fixed[0][0] is False


def test_get_level_url_all_levels():
    for lvl in [1, 2, 3, 4]:
        url = get_level_url(lvl)
        assert f"level={lvl}" in url
        assert "east.websudoku.com" in url


def test_get_level_url_invalid_raises():
    with pytest.raises(ValueError):
        get_level_url(5)


def test_blocked_error_is_runtime_error():
    assert issubclass(BlockedError, RuntimeError)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd crawler && pytest tests/test_reader_parser.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Create `crawler/app/web/reader.py`**

Copy `legacy/app/web/reader.py`, then delete:
- Lines 26–36 (`_READ_BOARD_JS = """..."""`)
- Lines 75–84 (`def check_page_blocked(page):`)
- Lines 242–299 (`class WebSudokuReader:`)

Update module comment at top:
```python
# app/web/reader.py  (requests-only; Playwright fallback removed)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd crawler && pytest tests/test_reader_parser.py -v
```
Expected: 5 PASSes

- [ ] **Step 5: Commit**

```bash
git add crawler/app/web/reader.py crawler/tests/test_reader_parser.py
git commit -m "feat(crawler): add trimmed reader (requests-only, no Playwright)"
```

---

## Task 4: Copy proxy_manager.py + add get_requests_proxy()

**Files:**
- Create: `crawler/app/web/proxy_manager.py`

Copy `legacy/app/web/proxy_manager.py` verbatim, then add one method to `ProxyManager`
that converts the Playwright-format proxy to a `requests`-compatible dict.

- [ ] **Step 1: Create `crawler/app/web/proxy_manager.py`**

Copy `legacy/app/web/proxy_manager.py` in full, then add the following method
to the `ProxyManager` class (after `get_playwright_proxy`, before `rotate`):

```python
def get_requests_proxy(self):
    """
    Returns a requests-compatible proxy dict {"http": ..., "https": ...},
    or None if no proxies are available (direct connection).
    """
    info = self.get_playwright_proxy()
    if info is None:
        return None
    server = info["server"]
    return {"http": server, "https": server}
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.web.proxy_manager import ProxyManager; pm = ProxyManager(); print('OK size:', pm.size())"
```
Expected: `OK size: 0`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/web/proxy_manager.py
git commit -m "feat(crawler): add proxy_manager (verbatim + get_requests_proxy)"
```

---

## Task 5: Implement config.py

**Files:**
- Create: `crawler/config.py`
- Create: `crawler/tests/test_config.py`

- [ ] **Step 1: Write failing tests**

`crawler/tests/test_config.py`:
```python
import pytest


def test_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig()
    assert cfg.num_workers == 10
    assert cfg.max_pool_size == 50_000
    assert cfg.resume_threshold == 30_000
    assert cfg.level_weights == [25, 25, 25, 25]
    assert cfg.min_delay == 0.0
    assert cfg.max_delay == 0.3
    assert cfg.request_timeout == 8
    assert cfg.proxy_validate_workers == 50
    assert cfg.proxy_validate_timeout == 3


def test_save_and_load(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig(num_workers=5, max_pool_size=1000)
    cfg.save()
    assert (tmp_path / "data" / "config.json").exists()
    cfg2 = CrawlerConfig.load()
    assert cfg2.num_workers == 5
    assert cfg2.max_pool_size == 1000


def test_load_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    from config import CrawlerConfig
    cfg = CrawlerConfig.load()
    assert cfg.num_workers == 10
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd crawler && pytest tests/test_config.py -v
```
Expected: `ImportError`

- [ ] **Step 3: Create `crawler/config.py`**

```python
# config.py
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path

_CONFIG_PATH = Path("data/config.json")


@dataclass
class CrawlerConfig:
    num_workers: int = 10
    max_pool_size: int = 50_000
    resume_threshold: int = 30_000
    level_weights: list = field(default_factory=lambda: [25, 25, 25, 25])
    min_delay: float = 0.0
    max_delay: float = 0.3
    request_timeout: int = 8
    proxy_validate_workers: int = 50
    proxy_validate_timeout: int = 3

    def save(self) -> None:
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> "CrawlerConfig":
        if not _CONFIG_PATH.exists():
            return cls()
        try:
            data = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        except Exception:
            return cls()
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd crawler && pytest tests/test_config.py -v
```
Expected: 3 PASSes

- [ ] **Step 5: Commit**

```bash
git add crawler/config.py crawler/tests/test_config.py
git commit -m "feat(crawler): add CrawlerConfig dataclass with JSON persistence"
```

---

## Task 6: Implement app/core/worker.py

**Files:**
- Create: `crawler/app/core/worker.py`

`CrawlerWorker` runs the fetch→insert→sleep loop on a QThread and emits one
`event_signal(dict)` per event. Dict `"type"` values: `"inserted"`, `"duplicate"`,
`"blocked"`, `"error"`.

- [ ] **Step 1: Create `crawler/app/core/worker.py`**

```python
# app/core/worker.py
from __future__ import annotations

import random
import time

from PyQt6.QtCore import QThread, pyqtSignal

from app.web.reader import fetch_puzzle_via_requests, get_level_url, BlockedError
from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from config import CrawlerConfig


class CrawlerWorker(QThread):
    event_signal = pyqtSignal(dict)

    def __init__(
        self,
        worker_id: int,
        config: CrawlerConfig,
        proxy_manager: ProxyManager,
        db: PuzzlePoolDB,
    ) -> None:
        super().__init__()
        self.worker_id = worker_id
        self.config = config
        self.proxy_manager = proxy_manager
        self.db = db
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        while not self._stop:
            # Pause when DB is full; resume when it drops below threshold
            try:
                total = self.db.get_pool_stats()["total"]
            except Exception:
                time.sleep(2)
                continue

            if total >= self.config.max_pool_size:
                while not self._stop:
                    time.sleep(2)
                    try:
                        if self.db.get_pool_stats()["total"] < self.config.resume_threshold:
                            break
                    except Exception:
                        pass
                continue

            # Choose proxy (None = direct connection)
            proxy_dict = self.proxy_manager.get_requests_proxy()
            server_url: str | None = proxy_dict.get("http") if proxy_dict else None

            # Weighted random difficulty level
            level = random.choices([1, 2, 3, 4], weights=self.config.level_weights, k=1)[0]
            url = get_level_url(level)

            try:
                board, _fixed = fetch_puzzle_via_requests(
                    url, proxy_dict, timeout=self.config.request_timeout
                )
                result = self.db.upsert_puzzle(board, "websudoku", level)
                self.event_signal.emit({
                    "type": "inserted" if result["inserted"] else "duplicate",
                    "level": level,
                    "puzzle_id": result["puzzle_id"],
                    "worker_id": self.worker_id,
                })
            except BlockedError:
                if server_url:
                    self.proxy_manager.blacklist_server(server_url)
                self.event_signal.emit({
                    "type": "blocked",
                    "proxy": server_url or "direct",
                    "worker_id": self.worker_id,
                })
                continue
            except Exception as exc:
                self.event_signal.emit({
                    "type": "error",
                    "msg": str(exc)[:120],
                    "worker_id": self.worker_id,
                })

            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            if delay > 0:
                time.sleep(delay)
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.core.worker import CrawlerWorker; print('CrawlerWorker OK')"
```
Expected: `CrawlerWorker OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/core/worker.py
git commit -m "feat(crawler): add CrawlerWorker QThread"
```

---

## Task 7: Implement app/gui/log_widget.py

**Files:**
- Create: `crawler/app/gui/log_widget.py`

- [ ] **Step 1: Create `crawler/app/gui/log_widget.py`**

```python
# app/gui/log_widget.py
from datetime import datetime

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextCursor

_MAX_LINES = 2000

_COLORS = {
    "green":  "#55efc4",
    "yellow": "#fdcb6e",
    "red":    "#ff7675",
    "blue":   "#74b9ff",
    "grey":   "#636e72",
    "white":  "#e0e0e0",
}


class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumBlockCount(_MAX_LINES)
        self.setStyleSheet(
            "QTextEdit{"
            "background:#0d0d0d;color:#e0e0e0;"
            "font-family:Consolas,monospace;font-size:11px;"
            "border:none;"
            "}"
        )

    def add_message(self, text: str, color: str = "white") -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        hex_color = _COLORS.get(color, _COLORS["white"])
        self.append(f'<span style="color:{hex_color}">[{ts}] {text}</span>')
        self.moveCursor(QTextCursor.MoveOperation.End)
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.gui.log_widget import LogWidget; print('LogWidget OK')"
```
Expected: `LogWidget OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/gui/log_widget.py
git commit -m "feat(crawler): add LogWidget scrolling log panel"
```

---

## Task 8: Implement app/gui/stats_panel.py

**Files:**
- Create: `crawler/app/gui/stats_panel.py`

Two rows of stat cards:
- Row 1: L1/L2/L3/L4 session insert counts (large numbers, colour-coded)
- Row 2: rate/min, Proxy 可用, Workers, 執行時間

- [ ] **Step 1: Create `crawler/app/gui/stats_panel.py`**

```python
# app/gui/stats_panel.py
from __future__ import annotations

import time
from collections import deque

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

_LEVEL_COLORS = ["#74b9ff", "#55efc4", "#fdcb6e", "#fd79a8"]
_LEVEL_NAMES  = ["L1 Easy", "L2 Medium", "L3 Hard", "L4 Evil"]


def _make_card(
    label_txt: str,
    value_txt: str,
    label_color: str,
    bg: str = "#0f3460",
    val_size: str = "16px",
    val_color: str = "#ffffff",
) -> tuple[QFrame, QLabel]:
    frame = QFrame()
    frame.setStyleSheet(f"QFrame{{background:{bg};border-radius:5px;}}")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(6, 4, 6, 4)
    layout.setSpacing(2)

    lbl = QLabel(label_txt)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"color:{label_color};font-size:9px;background:transparent;")

    val = QLabel(value_txt)
    val.setAlignment(Qt.AlignmentFlag.AlignCenter)
    val.setStyleSheet(
        f"color:{val_color};font-size:{val_size};font-weight:bold;background:transparent;"
    )

    layout.addWidget(lbl)
    layout.addWidget(val)
    return frame, val


class StatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._counts: list[int] = [0, 0, 0, 0]
        self._insert_times: deque[float] = deque()
        self._start_time: float | None = None
        self._num_workers = 0
        self._active_workers = 0

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        # Row 1: per-level count cards
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        self._level_vals: list[QLabel] = []
        for i in range(4):
            f, v = _make_card(_LEVEL_NAMES[i], "0", _LEVEL_COLORS[i])
            row1.addWidget(f)
            self._level_vals.append(v)
        outer.addLayout(row1)

        # Row 2: runtime stat cards
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        f1, self._rate_val    = _make_card("速率/min",   "0",        "#aaaaaa", "#0d0d1a", "13px", "#55efc4")
        f2, self._proxy_val   = _make_card("Proxy 可用", "0 / 0",    "#aaaaaa", "#0d0d1a", "13px", "#fdcb6e")
        f3, self._workers_val = _make_card("Workers",    "0 / 0",    "#aaaaaa", "#0d0d1a", "13px", "#74b9ff")
        f4, self._uptime_val  = _make_card("執行時間",   "00:00:00", "#aaaaaa", "#0d0d1a", "13px", "#e0e0e0")
        for f in (f1, f2, f3, f4):
            row2.addWidget(f)
        outer.addLayout(row2)

    def start_session(self, num_workers: int) -> None:
        self._counts = [0, 0, 0, 0]
        self._insert_times.clear()
        self._start_time = time.time()
        self._num_workers = num_workers
        self._active_workers = num_workers
        for v in self._level_vals:
            v.setText("0")

    def stop_session(self) -> None:
        self._active_workers = 0
        self._workers_val.setText(f"0 / {self._num_workers}")

    def increment_level(self, level: int) -> None:
        idx = level - 1
        self._counts[idx] += 1
        self._level_vals[idx].setText(f"{self._counts[idx]:,}")
        now = time.time()
        self._insert_times.append(now)
        while self._insert_times and now - self._insert_times[0] > 60:
            self._insert_times.popleft()

    def refresh_proxy(self, valid: int, total: int) -> None:
        self._proxy_val.setText(f"{valid} / {total}")

    def refresh_uptime(self) -> None:
        if self._start_time is None:
            return
        elapsed = int(time.time() - self._start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self._uptime_val.setText(f"{h:02d}:{m:02d}:{s:02d}")
        self._rate_val.setText(str(len(self._insert_times)))
        self._workers_val.setText(f"{self._active_workers} / {self._num_workers}")
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.gui.stats_panel import StatsPanel; print('StatsPanel OK')"
```
Expected: `StatsPanel OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/gui/stats_panel.py
git commit -m "feat(crawler): add StatsPanel (session counts + runtime stats)"
```

---

## Task 9: Implement app/gui/db_panel.py

**Files:**
- Create: `crawler/app/gui/db_panel.py`

Grid table: rows = `new / training / solved`, columns = `L1 L2 L3 L4 合計`.
Progress bar: total / max_pool_size.

- [ ] **Step 1: Create `crawler/app/gui/db_panel.py`**

```python
# app/gui/db_panel.py
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt

from app.db.pool_db import PuzzlePoolDB

_LEVEL_COLORS = ["#74b9ff", "#55efc4", "#fdcb6e", "#fd79a8"]
_STATUSES = [
    ("new",          "new"),
    ("training",     "訓練中"),
    ("solved_local", "solved"),
]


class DbPanel(QWidget):
    def __init__(self, db: PuzzlePoolDB, max_pool_size: int = 50_000, parent=None):
        super().__init__(parent)
        self.db = db
        self.max_pool_size = max_pool_size

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("📦 DB 現況 (puzzle_pool.db)")
        title.setStyleSheet(
            "color:#a29bfe;font-size:10px;font-weight:bold;background:transparent;"
        )
        self._total_lbl = QLabel("總計 0 筆")
        self._total_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._total_lbl.setStyleSheet("color:#636e72;font-size:9px;background:transparent;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._total_lbl)
        outer.addLayout(hdr)

        # Table inside a dark frame
        table_frame = QFrame()
        table_frame.setStyleSheet("QFrame{background:#0f1f3a;border-radius:5px;}")
        grid = QGridLayout(table_frame)
        grid.setContentsMargins(8, 6, 8, 6)
        grid.setSpacing(4)

        # Column headers: L1 L2 L3 L4 合計
        for ci, (color, txt) in enumerate(
            zip(_LEVEL_COLORS + ["#aaaaaa"], ["L1", "L2", "L3", "L4", "合計"])
        ):
            h = QLabel(txt)
            h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            h.setStyleSheet(f"color:{color};font-size:9px;background:transparent;")
            grid.addWidget(h, 0, ci + 1)

        # Data rows
        self._cells: list[list[QLabel]] = []
        for ri, (_, display) in enumerate(_STATUSES):
            row_lbl = QLabel(display)
            row_lbl.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
            grid.addWidget(row_lbl, ri + 1, 0)
            row: list[QLabel] = []
            for ci in range(5):
                cell = QLabel("0")
                cell.setAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                cell.setStyleSheet("color:#e0e0e0;font-size:9px;background:transparent;")
                grid.addWidget(cell, ri + 1, ci + 1)
                row.append(cell)
            self._cells.append(row)

        outer.addWidget(table_frame)

        # Progress bar
        prog_hdr = QHBoxLayout()
        prog_lbl = QLabel("收錄進度")
        prog_lbl.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
        self._prog_txt = QLabel(f"0 / {max_pool_size:,} (0%)")
        self._prog_txt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._prog_txt.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
        prog_hdr.addWidget(prog_lbl)
        prog_hdr.addStretch()
        prog_hdr.addWidget(self._prog_txt)
        outer.addLayout(prog_hdr)

        self._bar = QProgressBar()
        self._bar.setRange(0, max_pool_size)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(8)
        self._bar.setStyleSheet(
            "QProgressBar{background:#2d2d4e;border-radius:4px;border:none;}"
            "QProgressBar::chunk{"
            "background:qlineargradient("
            "x1:0,y1:0,x2:1,y2:0,stop:0 #6c5ce7,stop:1 #a29bfe);"
            "border-radius:4px;}"
        )
        outer.addWidget(self._bar)

    def refresh(self) -> None:
        """Query DB and update all cells. Called by QTimer every 5 s."""
        try:
            per_level = [self.db.get_pool_stats(level=i) for i in range(1, 5)]
            grand = self.db.get_pool_stats()
        except Exception:
            return

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

    def update_max(self, new_max: int) -> None:
        self.max_pool_size = new_max
        self._bar.setRange(0, new_max)
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.gui.db_panel import DbPanel; print('DbPanel OK')"
```
Expected: `DbPanel OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/gui/db_panel.py
git commit -m "feat(crawler): add DbPanel (DB stats table + progress bar)"
```

---

## Task 10: Implement app/gui/settings_dialog.py

**Files:**
- Create: `crawler/app/gui/settings_dialog.py`

All settings in a `QDialog` with three `QGroupBox` sections. Writes changes back to
the `CrawlerConfig` instance and calls `config.save()` on Apply.

- [ ] **Step 1: Create `crawler/app/gui/settings_dialog.py`**

```python
# app/gui/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton, QGroupBox,
)
from config import CrawlerConfig


class SettingsDialog(QDialog):
    def __init__(self, config: CrawlerConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ 爬蟲設定")
        self.setMinimumWidth(420)
        self._config = config

        layout = QVBoxLayout(self)

        # ── Crawling ──────────────────────────────────────────────────────────
        crawl_grp = QGroupBox("爬蟲設定")
        crawl_form = QFormLayout(crawl_grp)

        self._num_workers = QSpinBox()
        self._num_workers.setRange(1, 200)
        self._num_workers.setValue(config.num_workers)
        crawl_form.addRow("爬蟲執行緒數（重啟後生效）:", self._num_workers)

        self._max_pool = QSpinBox()
        self._max_pool.setRange(1_000, 10_000_000)
        self._max_pool.setSingleStep(1_000)
        self._max_pool.setValue(config.max_pool_size)
        crawl_form.addRow("目標收錄上限（達到後暫停）:", self._max_pool)

        self._resume = QSpinBox()
        self._resume.setRange(0, 10_000_000)
        self._resume.setSingleStep(1_000)
        self._resume.setValue(config.resume_threshold)
        crawl_form.addRow("恢復爬取門檻（低於此數重新開始）:", self._resume)

        self._min_delay = QDoubleSpinBox()
        self._min_delay.setRange(0.0, 60.0)
        self._min_delay.setSingleStep(0.1)
        self._min_delay.setDecimals(2)
        self._min_delay.setValue(config.min_delay)
        crawl_form.addRow("最短請求間隔（秒）:", self._min_delay)

        self._max_delay = QDoubleSpinBox()
        self._max_delay.setRange(0.0, 60.0)
        self._max_delay.setSingleStep(0.1)
        self._max_delay.setDecimals(2)
        self._max_delay.setValue(config.max_delay)
        crawl_form.addRow("最長請求間隔（秒）:", self._max_delay)

        self._timeout = QSpinBox()
        self._timeout.setRange(1, 60)
        self._timeout.setValue(config.request_timeout)
        crawl_form.addRow("請求逾時（秒）:", self._timeout)

        layout.addWidget(crawl_grp)

        # ── Level weights ─────────────────────────────────────────────────────
        level_grp = QGroupBox("各難度爬取比例（填入相對比重，程式自動正規化）")
        level_form = QFormLayout(level_grp)
        level_names = ["L1 Easy", "L2 Medium", "L3 Hard", "L4 Evil"]
        self._weights: list[QSpinBox] = []
        weights = config.level_weights
        for i, name in enumerate(level_names):
            sb = QSpinBox()
            sb.setRange(0, 100)
            sb.setValue(weights[i] if i < len(weights) else 25)
            level_form.addRow(f"{name}:", sb)
            self._weights.append(sb)
        layout.addWidget(level_grp)

        # ── Proxy ─────────────────────────────────────────────────────────────
        proxy_grp = QGroupBox("Proxy 設定（下次啟動時生效）")
        proxy_form = QFormLayout(proxy_grp)

        self._proxy_workers = QSpinBox()
        self._proxy_workers.setRange(1, 500)
        self._proxy_workers.setValue(config.proxy_validate_workers)
        proxy_form.addRow("Proxy 驗證執行緒數:", self._proxy_workers)

        self._proxy_timeout = QSpinBox()
        self._proxy_timeout.setRange(1, 30)
        self._proxy_timeout.setValue(config.proxy_validate_timeout)
        proxy_form.addRow("Proxy 驗證逾時（秒）:", self._proxy_timeout)

        layout.addWidget(proxy_grp)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("套用並關閉")
        ok_btn.clicked.connect(self._apply)
        ok_btn.setDefault(True)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _apply(self) -> None:
        self._config.num_workers          = self._num_workers.value()
        self._config.max_pool_size        = self._max_pool.value()
        self._config.resume_threshold     = self._resume.value()
        self._config.min_delay            = self._min_delay.value()
        self._config.max_delay            = self._max_delay.value()
        self._config.request_timeout      = self._timeout.value()
        self._config.level_weights        = [sb.value() for sb in self._weights]
        self._config.proxy_validate_workers = self._proxy_workers.value()
        self._config.proxy_validate_timeout = self._proxy_timeout.value()
        self._config.save()
        self.accept()
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.gui.settings_dialog import SettingsDialog; print('SettingsDialog OK')"
```
Expected: `SettingsDialog OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/gui/settings_dialog.py
git commit -m "feat(crawler): add SettingsDialog"
```

---

## Task 11: Implement app/gui/main_window.py

**Files:**
- Create: `crawler/app/gui/main_window.py`

Assembles toolbar + StatsPanel + DbPanel + LogWidget. Manages worker lifecycle.
DB stats refreshed every 5 s; uptime every 1 s.

- [ ] **Step 1: Create `crawler/app/gui/main_window.py`**

```python
# app/gui/main_window.py
from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QTimer

from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from app.core.worker import CrawlerWorker
from app.gui.stats_panel import StatsPanel
from app.gui.db_panel import DbPanel
from app.gui.log_widget import LogWidget
from app.gui.settings_dialog import SettingsDialog
from config import CrawlerConfig


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: CrawlerConfig,
        proxy_manager: ProxyManager,
        db: PuzzlePoolDB,
    ) -> None:
        super().__init__()
        self.config = config
        self.proxy_manager = proxy_manager
        self.db = db
        self._workers: list[CrawlerWorker] = []

        self.setWindowTitle("🕷 Sudoku Crawler")
        self.setMinimumWidth(500)
        self.setStyleSheet("QMainWindow,QWidget{background:#1a1a2e;color:#e0e0e0;}")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet("QWidget{background:#16213e;border-radius:5px;}")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(10, 7, 10, 7)

        title = QLabel("🕷 Sudoku Crawler")
        title.setStyleSheet(
            "color:#a29bfe;font-size:13px;font-weight:bold;background:transparent;"
        )
        tb.addWidget(title)
        tb.addStretch()

        self._start_btn = QPushButton("▶ 開始")
        self._start_btn.setStyleSheet(
            "QPushButton{background:#00b894;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#00cec9;}"
            "QPushButton:disabled{background:#444;color:#888;}"
        )
        self._stop_btn = QPushButton("■ 停止")
        self._stop_btn.setStyleSheet(
            "QPushButton{background:#636e72;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#b2bec3;}"
            "QPushButton:disabled{background:#444;color:#888;}"
        )
        self._stop_btn.setEnabled(False)
        settings_btn = QPushButton("⚙ 設定")
        settings_btn.setStyleSheet(
            "QPushButton{background:#0984e3;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#74b9ff;}"
        )

        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self._on_stop)
        settings_btn.clicked.connect(self._on_settings)

        for btn in (self._start_btn, self._stop_btn, settings_btn):
            tb.addWidget(btn)
        root.addWidget(toolbar)

        # ── Panels ────────────────────────────────────────────────────────────
        self.stats_panel = StatsPanel()
        root.addWidget(self.stats_panel)

        self.db_panel = DbPanel(db, max_pool_size=config.max_pool_size)
        root.addWidget(self.db_panel)

        self.log_widget = LogWidget()
        self.log_widget.setMinimumHeight(110)
        root.addWidget(self.log_widget)

        # ── Timers ────────────────────────────────────────────────────────────
        self._db_timer = QTimer(self)
        self._db_timer.timeout.connect(self._refresh_db)
        self._db_timer.start(5_000)

        self._uptime_timer = QTimer(self)
        self._uptime_timer.timeout.connect(self.stats_panel.refresh_uptime)
        self._uptime_timer.start(1_000)

        self._refresh_db()
        self.log_widget.add_message("就緒。點擊「開始」啟動爬蟲。", "grey")

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_start(self) -> None:
        if self._workers:
            return
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self.stats_panel.start_session(self.config.num_workers)
        self.log_widget.add_message(
            f"啟動 {self.config.num_workers} 個爬蟲執行緒...", "blue"
        )
        for i in range(self.config.num_workers):
            w = CrawlerWorker(i, self.config, self.proxy_manager, self.db)
            w.event_signal.connect(self._on_worker_event)
            w.start()
            self._workers.append(w)

    def _on_stop(self) -> None:
        if not self._workers:
            return
        self._stop_btn.setEnabled(False)
        self.log_widget.add_message("正在停止爬蟲...", "yellow")
        for w in self._workers:
            w.stop()
        for w in self._workers:
            w.wait(5_000)
        self._workers.clear()
        self.stats_panel.stop_session()
        self._start_btn.setEnabled(True)
        self.log_widget.add_message("爬蟲已停止。", "grey")

    def _on_settings(self) -> None:
        dlg = SettingsDialog(self.config, parent=self)
        if dlg.exec():
            self.db_panel.update_max(self.config.max_pool_size)
            self.log_widget.add_message("設定已儲存。", "grey")

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
        elif t == "error":
            self.log_widget.add_message(f"✗ {event['msg']}", "red")

    def _refresh_db(self) -> None:
        self.db_panel.refresh()
        stats = self.proxy_manager.get_stats()
        self.stats_panel.refresh_proxy(stats["valid"], stats["total"])

    def closeEvent(self, event) -> None:
        self._on_stop()
        self.proxy_manager.stop_validation()
        event.accept()
```

- [ ] **Step 2: Smoke-test import**

```bash
cd crawler && python -c "from app.gui.main_window import MainWindow; print('MainWindow OK')"
```
Expected: `MainWindow OK`

- [ ] **Step 3: Commit**

```bash
git add crawler/app/gui/main_window.py
git commit -m "feat(crawler): add MainWindow (toolbar + panels + timers)"
```

---

## Task 12: Implement crawler.py entry point + run end-to-end smoke test

**Files:**
- Create: `crawler/crawler.py`

- [ ] **Step 1: Create `crawler/crawler.py`**

```python
#!/usr/bin/env python3
# crawler.py
"""
Standalone Sudoku puzzle crawler.

Usage:
    cd crawler
    python crawler.py
"""
import sys
import threading

from PyQt6.QtWidgets import QApplication

from config import CrawlerConfig
from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from app.gui.main_window import MainWindow

DB_PATH = "../data/puzzle_pool.db"


def _init_proxy(proxy_manager: ProxyManager, config: CrawlerConfig) -> None:
    proxy_manager.download_all()
    proxy_manager.start_background_validation(
        max_workers=config.proxy_validate_workers,
        timeout=config.proxy_validate_timeout,
    )


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    config = CrawlerConfig.load()
    db = PuzzlePoolDB(DB_PATH)
    proxy_manager = ProxyManager()

    window = MainWindow(config, proxy_manager, db)
    window.show()

    window.log_widget.add_message("正在下載 Proxy 清單，請稍候...", "blue")
    threading.Thread(
        target=_init_proxy, args=(proxy_manager, config), daemon=True
    ).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run all unit tests**

```bash
cd crawler && pytest tests/ -v
```
Expected: all tests PASS (pool_db × 4, reader × 5, config × 3 = 12 total)

- [ ] **Step 3: Smoke-test launch (visual check)**

```bash
cd crawler && python crawler.py
```

Verify:
- Window opens with dark theme
- DB 現況 table shows current counts from `puzzle_pool.db`
- Progress bar reflects current total
- "就緒" message appears in log
- "正在下載 Proxy 清單" message appears after a moment
- Proxy 可用 count gradually increments in the stats row (every 5 s refresh)
- Click ▶ 開始 → workers start, log shows `✓ L? puzzle inserted` entries
- Click ■ 停止 → workers stop cleanly
- Click ⚙ 設定 → dialog opens with all fields populated; Apply saves config.json

- [ ] **Step 4: Commit**

```bash
git add crawler/crawler.py
git commit -m "feat(crawler): add entry point crawler.py — standalone crawler complete"
```
