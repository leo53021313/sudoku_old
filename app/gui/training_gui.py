# app/gui/training_gui.py
# -*- coding: utf-8 -*-
"""
DashboardWindow：作品集等級 AI 訓練儀表板。
Layout：
  - TitleBar（40px）
  - QSplitter：左側 SidebarPanel（240px，可收合）| 右側主內容
  - 右側主內容：
      Row 1（80px）: StatusCard + PhaseWidget
      Row 2（160px）: 6 張 StatCard（3×2 grid）
      Row 3（100px）: DifficultyPanel
      Row 4（flex）: BoardGridPanel
  - InfoBar（44px）底部控制列
"""

import sys
import time

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QSplitter, QPushButton, QLabel,
    QSystemTrayIcon, QMenu, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCloseEvent, QAction, QFont

from .event_bus import bus as gui_bus
from .board_grid_panel import BoardGridPanel
from .themes import COLORS
from .components.status_card import StatusCard
from .components.stat_card import StatCard
from .components.phase_widget import PhaseWidget
from .components.difficulty_panel import DifficultyPanel
from .components.info_bar import InfoBar
from .components.sidebar_panel import SidebarPanel


class DashboardWindow(QMainWindow):

    def __init__(self, hotkey=None, max_boards: int = 4):
        super().__init__()
        self._hotkey  = hotkey
        self._state   = "running"

        # ── 統計追蹤 ─────────────────────────────────────────────────
        self._episode      = 0
        self._success_cnt  = 0
        self._reward_sum   = 0.0
        self._ep_times: list[float] = []
        self._t_last_ep    = time.monotonic()
        self._prod_ok      = 0
        self._prod_fail    = 0
        self._prod_blocked = 0
        self._proxy_valid  = 0
        self._proxy_total  = 0
        self._pool_total   = 0
        self._pool_unsolved= 0

        # 難度分解統計
        self._diff_stats: dict[int, dict[str, int]] = {
            1: {"success": 0, "total": 0},
            2: {"success": 0, "total": 0},
            3: {"success": 0, "total": 0},
            4: {"success": 0, "total": 0},
        }
        # episode_start 記錄的難度，供 episode_end 使用（fallback）
        self._current_level: int = 0

        self._build_ui(max_boards, hotkey)

        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    # ── UI 建構 ──────────────────────────────────────────────────────

    def _build_ui(self, max_boards: int, hotkey) -> None:
        self.setWindowTitle("Sudoku AI 訓練儀表板")
        self.resize(1100, 720)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(
            f"QMainWindow {{ background: {COLORS['bg_dark']}; }}"
        )

        central = QWidget()
        central.setStyleSheet(f"background: {COLORS['bg_dark']};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_title_bar())

        # ── Splitter：側欄 + 主內容 ───────────────────────────────────
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(2)
        self._splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {COLORS['border']}; }}"
        )

        self._sidebar = SidebarPanel()
        self._splitter.addWidget(self._sidebar)
        self._splitter.addWidget(self._build_main_area(max_boards))
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([240, 860])

        root.addWidget(self._splitter, stretch=1)

        # ── 底部控制列 ────────────────────────────────────────────────
        self._info_bar = InfoBar(hotkey=hotkey)
        root.addWidget(self._info_bar)

        # ── 系統托盤 ──────────────────────────────────────────────────
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(
            self.style().standardIcon(
                self.style().StandardPixmap.SP_ComputerIcon
            )
        )
        tray_menu = QMenu()
        show_act = QAction("顯示 GUI", self)
        show_act.triggered.connect(self._show_window)
        tray_menu.addAction(show_act)
        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

        # 初始狀態同步
        self._info_bar.set_state("running")
        self._status_card.set_state("running")

    def _build_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['bg_sidebar']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(8)

        title = QLabel("Sudoku AI 訓練儀表板")
        tf = QFont()
        tf.setPointSize(11)
        tf.setBold(True)
        title.setFont(tf)
        title.setStyleSheet(
            f"color: {COLORS['text_primary']}; background: transparent; border: none;"
        )
        lay.addWidget(title)
        lay.addStretch()

        self._toggle_btn = QPushButton("≡ 收起側欄")
        self._toggle_btn.setFixedHeight(28)
        self._toggle_btn.setFixedWidth(90)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px; font-size: 9pt;
            }}
            QPushButton:hover {{ background: {COLORS['border']}; }}
        """)
        self._toggle_btn.clicked.connect(self._toggle_sidebar)
        lay.addWidget(self._toggle_btn)

        hide_btn = QPushButton("— 隱藏")
        hide_btn.setFixedHeight(28)
        hide_btn.setFixedWidth(60)
        hide_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px; font-size: 9pt;
            }}
            QPushButton:hover {{ background: {COLORS['border']}; }}
        """)
        hide_btn.clicked.connect(self._toggle_window)
        lay.addWidget(hide_btn)

        return bar

    def _build_main_area(self, max_boards: int) -> QWidget:
        area = QWidget()
        area.setStyleSheet(f"background: {COLORS['bg_dark']};")
        lay = QVBoxLayout(area)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # ROW 1: StatusCard + PhaseWidget
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self._status_card = StatusCard()
        self._status_card.setFixedWidth(180)
        self._status_card.setFixedHeight(80)
        row1.addWidget(self._status_card)

        self._phase_widget = PhaseWidget()
        self._phase_widget.setFixedHeight(80)
        row1.addWidget(self._phase_widget, stretch=1)

        lay.addLayout(row1)

        # ROW 2: 6 StatCards（2行×3列）
        grid = QGridLayout()
        grid.setSpacing(8)

        self._card_success = StatCard(
            "成功率", color=COLORS["success"],
        )
        self._card_speed = StatCard(
            "速度 (ep/s)", color=COLORS["info"],
        )
        self._card_reward = StatCard(
            "Avg 獎勵", color=COLORS["info"],
        )
        self._card_ppo = StatCard(
            "PPO 更新", color=COLORS["text_muted"],
        )
        self._card_entropy = StatCard(
            "Entropy", color=COLORS["text_muted"],
        )
        self._card_loss = StatCard(
            "Loss", color=COLORS["text_muted"],
        )

        for card in (
            self._card_success, self._card_speed, self._card_reward,
            self._card_ppo,     self._card_entropy, self._card_loss,
        ):
            card.setFixedHeight(80)

        grid.addWidget(self._card_success, 0, 0)
        grid.addWidget(self._card_speed,   0, 1)
        grid.addWidget(self._card_reward,  0, 2)
        grid.addWidget(self._card_ppo,     1, 0)
        grid.addWidget(self._card_entropy, 1, 1)
        grid.addWidget(self._card_loss,    1, 2)

        row2_w = QWidget()
        row2_w.setLayout(grid)
        row2_w.setStyleSheet("background: transparent;")
        lay.addWidget(row2_w)

        # ROW 3: DifficultyPanel
        self._diff_panel = DifficultyPanel()
        self._diff_panel.setFixedHeight(100)
        lay.addWidget(self._diff_panel)

        # ROW 4: Boards
        self._boards = BoardGridPanel(max_boards=max_boards)
        lay.addWidget(self._boards, stretch=1)

        return area

    # ── QTimer tick ───────────────────────────────────────────────────

    def _tick(self) -> None:
        for ev in gui_bus.drain(max_n=100):
            self._dispatch(ev)
        if (
            self._hotkey
            and self._hotkey.stop_requested
            and self._state != "stopped"
        ):
            self._apply_state("stopped")

    def _dispatch(self, ev) -> None:
        t, d = ev.type, ev.data
        if   t == "episode_start":   self._on_episode_start(d)
        elif t == "board_update":    self._on_board_update(d)
        elif t == "episode_end":     self._on_episode_end(d)
        elif t == "stats_update":    self._on_stats_update(d)
        elif t == "pool_update":     self._on_pool_update(d)
        elif t == "proxy_update":
            self._proxy_valid = d.get("valid", self._proxy_valid)
            self._proxy_total = d.get("total", self._proxy_total)
            self._refresh_pool_ui()
        elif t == "producer_update":
            self._prod_ok      += d.get("success_delta", 0)
            self._prod_fail    += d.get("fail_delta", 0)
            self._prod_blocked += d.get("blocked_delta", 0)
        elif t == "state_change":    self._apply_state(d.get("state", "running"))
        elif t == "model_saved":
            self._info_bar.set_log(
                f"[已儲存] Ep {d.get('episode_idx', 0)} → {d.get('path', '')}"
            )
        elif t == "log":
            self._info_bar.set_log(d.get("msg", ""))

    # ── 事件處理 ─────────────────────────────────────────────────────

    def _on_episode_start(self, d: dict) -> None:
        board   = d.get("board", [[0]*9]*9)
        fixed   = d.get("fixed", [[False]*9]*9)
        episode = d.get("episode_idx", 0)
        level   = d.get("level", 0)
        self._episode = episode
        self._current_level = level
        self._boards.on_episode_start(board, fixed, episode, level)

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
        # level 優先從事件取（main_train.py 已加入），fallback 到 episode_start 記錄
        level   = d.get("level", self._current_level)

        self._boards.on_episode_end(board, fixed, success, episode)

        if success:
            self._success_cnt += 1
        self._reward_sum += reward

        now = time.monotonic()
        self._ep_times.append(now)
        if len(self._ep_times) > 50:
            self._ep_times.pop(0)
        self._t_last_ep = now

        # 難度分解統計
        if level in self._diff_stats:
            self._diff_stats[level]["total"] += 1
            if success:
                self._diff_stats[level]["success"] += 1
            ds = self._diff_stats[level]
            self._diff_panel.update_level(
                level, ds["success"], ds["total"]
            )

        tag = "✓" if success else "✗"
        self._info_bar.set_log(f"Ep {episode}  {tag}  reward={reward:.2f}")

    def _on_stats_update(self, d: dict) -> None:
        ep    = d.get("episode_idx", self._episode)
        n     = max(ep, 1)
        sr    = self._success_cnt / n

        speed = 0.0
        if len(self._ep_times) >= 2:
            dt = self._ep_times[-1] - self._ep_times[0]
            if dt > 0:
                speed = (len(self._ep_times) - 1) / dt

        total = d.get("total_episodes", 0)
        mrv   = d.get("mrv_prob", 0.0)
        phase = d.get("phase", 1)

        self._status_card.set_episode(ep, total)
        self._phase_widget.set_phase(phase, mrv)

        self._card_success.set_value(f"{sr:.1%}")
        self._card_speed.set_value(f"{speed:.1f}")
        self._card_reward.set_value(f"{self._reward_sum / n:.1f}")
        self._card_ppo.set_value(f"{d.get('update_count', 0):,}")
        self._card_entropy.set_value(f"{d.get('entropy', 0.0):.4f}")
        self._card_loss.set_value(f"{d.get('loss', 0.0):.4f}")

    def _on_pool_update(self, d: dict) -> None:
        self._pool_total    = d.get("total",   self._pool_total)
        self._pool_unsolved = d.get("unsolved", self._pool_unsolved)
        self._refresh_pool_ui()

    def _refresh_pool_ui(self) -> None:
        self._sidebar.update_pool_status(
            total=self._pool_total,
            unsolved=self._pool_unsolved,
            proxy_valid=self._proxy_valid,
            proxy_total=self._proxy_total,
        )

    def _apply_state(self, state: str) -> None:
        self._state = state
        self._status_card.set_state(state)
        self._info_bar.set_state(state)
        if state == "stopped":
            self._timer.stop()

    # ── 側欄收合動畫 ─────────────────────────────────────────────────

    def _toggle_sidebar(self) -> None:
        sidebar_open = self._sidebar.maximumWidth() > 10
        if sidebar_open:
            self._anim = QPropertyAnimation(self._sidebar, b"maximumWidth")
            self._anim.setDuration(200)
            self._anim.setStartValue(self._sidebar.width())
            self._anim.setEndValue(0)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.start()
            self._toggle_btn.setText("≡ 展開側欄")
        else:
            self._sidebar.setMaximumWidth(16777215)
            self._anim = QPropertyAnimation(self._sidebar, b"maximumWidth")
            self._anim.setDuration(200)
            self._anim.setStartValue(0)
            self._anim.setEndValue(240)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.start()
            self._toggle_btn.setText("≡ 收起側欄")

    # ── 視窗顯示/隱藏 ────────────────────────────────────────────────

    def _toggle_window(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self._show_window()

    def _show_window(self) -> None:
        self.show()
        self.activateWindow()
        self.raise_()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._state != "stopped":
            event.ignore()
            self.hide()
        else:
            self._tray.hide()
            if self._hotkey and not self._hotkey.stop_requested:
                self._hotkey.request_stop()
            self._timer.stop()
            event.accept()


# 向下相容別名
TrainingWindow = DashboardWindow


# ── 進入點 ────────────────────────────────────────────────────────────────

def launch_gui(hotkey=None, max_boards: int = 4) -> None:
    """
    建立 QApplication + DashboardWindow，阻塞直到視窗關閉。
    必須在主執行緒呼叫；訓練迴圈應在另一個執行緒執行。
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    win = DashboardWindow(hotkey=hotkey, max_boards=max_boards)
    win.show()
    app.exec()
