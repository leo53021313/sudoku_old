# app/gui/training_gui.py
# -*- coding: utf-8 -*-
"""
主視窗：組合 StatsPanel + BoardGridPanel + ControlPanel。
QTimer 每 33ms 從 EventBus 抽取事件並分發到各 panel。
訓練邏輯跑在另一個執行緒，GUI 全程只碰 Qt widget（主執行緒）。
"""

import sys
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QSplitter, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCloseEvent

from .event_bus import bus as gui_bus
from .board_grid_panel import BoardGridPanel
from .stats_panel import StatsPanel
from .control_panel import ControlPanel


class TrainingWindow(QMainWindow):

    def __init__(self, hotkey=None, max_boards: int = 4):
        super().__init__()
        self._hotkey = hotkey
        self._state  = "running"

        # ── 統計追蹤（GUI 端累積，不需和訓練端共享 memory）──────────
        self._episode     = 0
        self._success_cnt = 0
        self._reward_sum  = 0.0
        self._ep_times: list[float] = []
        self._t_last_ep   = time.monotonic()
        self._prod_ok     = 0
        self._prod_fail   = 0
        self._prod_blocked= 0
        self._proxy_valid = 0
        self._proxy_total = 0

        self._build_ui(max_boards, hotkey)

        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    # ── UI 建構 ──────────────────────────────────────────────────────

    def _build_ui(self, max_boards: int, hotkey) -> None:
        self.setWindowTitle("Sudoku AI 訓練視覺化")
        self.resize(900, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 頂部工具列 ────────────────────────────────────────────────
        toolbar = QWidget()
        toolbar.setFixedHeight(30)
        toolbar.setStyleSheet("background: #f0f0f0; border-bottom: 1px solid #ccc;")
        tbl = QHBoxLayout(toolbar)
        tbl.setContentsMargins(8, 2, 8, 2)

        title_lbl = QPushButton("Sudoku AI 訓練視覺化")
        title_lbl.setFlat(True)
        title_lbl.setStyleSheet(
            "font-weight: bold; font-size: 10pt; background: transparent;"
        )
        tbl.addWidget(title_lbl)
        tbl.addStretch()

        self._hide_btn = QPushButton("隱藏 GUI")
        self._hide_btn.setFixedWidth(70)
        self._hide_btn.clicked.connect(self.hide)
        tbl.addWidget(self._hide_btn)

        root_layout.addWidget(toolbar)

        # ── 主體 Splitter ─────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(4)

        self._stats  = StatsPanel()
        self._boards = BoardGridPanel(max_boards=max_boards)

        splitter.addWidget(self._stats)
        splitter.addWidget(self._boards)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter, stretch=1)

        # ── 底部控制列 ────────────────────────────────────────────────
        self._ctrl = ControlPanel(hotkey=hotkey)
        root_layout.addWidget(self._ctrl)

        self._stats.set_training_state("running")
        self._ctrl.set_state("running")

    # ── QTimer tick：抽取並分發事件 ──────────────────────────────────

    def _tick(self) -> None:
        for ev in gui_bus.drain(max_n=100):
            self._dispatch(ev)

        # 若 hotkey 已停止，同步 GUI 狀態
        if self._hotkey and self._hotkey.stop_requested and self._state != "stopped":
            self._apply_state("stopped")

    def _dispatch(self, ev) -> None:
        t = ev.type
        d = ev.data

        if t == "episode_start":
            self._on_episode_start(d)
        elif t == "board_update":
            self._on_board_update(d)
        elif t == "episode_end":
            self._on_episode_end(d)
        elif t == "stats_update":
            self._on_stats_update(d)
        elif t == "pool_update":
            self._on_pool_update(d)
        elif t == "proxy_update":
            self._proxy_valid = d.get("valid", self._proxy_valid)
            self._proxy_total = d.get("total", self._proxy_total)
            self._refresh_pool_ui()
        elif t == "producer_update":
            self._prod_ok      += d.get("success_delta", 0)
            self._prod_fail    += d.get("fail_delta", 0)
            self._prod_blocked += d.get("blocked_delta", 0)
            self._refresh_pool_ui()
        elif t == "state_change":
            self._apply_state(d.get("state", "running"))
        elif t == "model_saved":
            path = d.get("path", "")
            ep   = d.get("episode_idx", 0)
            self._ctrl.set_log(f"[已儲存] Ep {ep} → {path}")
        elif t == "log":
            self._ctrl.set_log(d.get("msg", ""))

    # ── 事件處理 ─────────────────────────────────────────────────────

    def _on_episode_start(self, d: dict) -> None:
        board   = d.get("board", [[0]*9]*9)
        fixed   = d.get("fixed", [[False]*9]*9)
        episode = d.get("episode_idx", 0)
        self._episode = episode
        self._boards.on_episode_start(board, fixed, episode)

    def _on_board_update(self, d: dict) -> None:
        board   = d.get("board", [[0]*9]*9)
        fixed   = d.get("fixed", [[False]*9]*9)
        hl      = d.get("highlight")
        episode = d.get("episode_idx", self._episode)
        self._boards.on_board_update(board, fixed, hl, episode)

    def _on_episode_end(self, d: dict) -> None:
        board   = d.get("board", [[0]*9]*9)
        fixed   = d.get("fixed", [[False]*9]*9)
        success = d.get("success", False)
        episode = d.get("episode_idx", self._episode)
        reward  = d.get("total_reward", 0.0)

        self._boards.on_episode_end(board, fixed, success, episode)

        if success:
            self._success_cnt += 1
        self._reward_sum += reward

        now = time.monotonic()
        self._ep_times.append(now)
        if len(self._ep_times) > 50:
            self._ep_times.pop(0)
        self._t_last_ep = now

        tag = "✓" if success else "✗"
        self._ctrl.set_log(
            f"Ep {episode}  {tag}  reward={reward:.2f}"
        )

    def _on_stats_update(self, d: dict) -> None:
        ep    = d.get("episode_idx", self._episode)
        n     = max(ep, 1)
        sr    = self._success_cnt / n

        # 計算速度：最近 N 個 episode 的時間差
        speed = 0.0
        if len(self._ep_times) >= 2:
            dt = self._ep_times[-1] - self._ep_times[0]
            if dt > 0:
                speed = (len(self._ep_times) - 1) / dt

        self._stats.update_training(
            episode=ep,
            total=d.get("total_episodes", 0),
            success_rate=sr,
            avg_reward=self._reward_sum / n,
            speed=speed,
            update_count=d.get("update_count", 0),
            mrv_prob=d.get("mrv_prob", 0.0),
            entropy=d.get("entropy", 0.0),
            loss=d.get("loss", 0.0),
            rollout_size=d.get("rollout_size", 0),
            rollout_cap=d.get("rollout_cap", 512),
        )

    def _on_pool_update(self, d: dict) -> None:
        self._stats.update_pool(
            total=d.get("total", 0),
            unsolved=d.get("unsolved", 0),
            proxy_valid=self._proxy_valid,
            proxy_total=self._proxy_total,
            prod_ok=self._prod_ok,
            prod_fail=self._prod_fail,
            prod_blocked=self._prod_blocked,
        )

    def _refresh_pool_ui(self) -> None:
        self._stats.update_pool(
            proxy_valid=self._proxy_valid,
            proxy_total=self._proxy_total,
            prod_ok=self._prod_ok,
            prod_fail=self._prod_fail,
            prod_blocked=self._prod_blocked,
        )

    def _apply_state(self, state: str) -> None:
        self._state = state
        self._stats.set_training_state(state)
        self._ctrl.set_state(state)
        if state == "stopped":
            self._timer.stop()

    # ── 視窗關閉：通知訓練停止 ───────────────────────────────────────

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._hotkey and not self._hotkey.stop_requested:
            self._hotkey.request_stop()
        self._timer.stop()
        event.accept()


# ── 進入點 ─────────────────────────────────────────────────────────────────

def launch_gui(hotkey=None, max_boards: int = 4) -> None:
    """
    建立 QApplication + TrainingWindow，阻塞直到視窗關閉。
    必須在主執行緒呼叫；訓練迴圈應在另一個執行緒執行。
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    win = TrainingWindow(hotkey=hotkey, max_boards=max_boards)
    win.show()
    app.exec()
