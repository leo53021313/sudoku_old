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
        # _insert_times is only accessed from signal slots (main thread) — no lock needed
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
