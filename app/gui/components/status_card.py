# app/gui/components/status_card.py
# -*- coding: utf-8 -*-
import time
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from ..themes import COLORS


class StatusCard(QFrame):
    """
    AI 狀態卡片：
    - 大圓點 + 中文狀態文字（訓練中 / 已暫停 / 已停止）
    - 回合計數 Ep X / ∞
    - 已訓練時間 HH:MM:SS
    """

    _STATE_MAP = {
        "running": ("訓練中", COLORS["success"]),
        "paused":  ("已暫停", COLORS["warning"]),
        "stopped": ("已停止", COLORS["danger"]),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._start_time = time.monotonic()
        self._elapsed_offset = 0.0
        self._paused_at: float | None = None

        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)

        # 第一行：圓點 + 狀態文字
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        self._dot = QLabel("●")
        self._dot.setStyleSheet(
            f"color: {COLORS['success']}; font-size: 14pt;"
            " border: none; background: transparent;"
        )

        self._state_lbl = QLabel("訓練中")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._state_lbl.setFont(font)
        self._state_lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; border: none; background: transparent;"
        )

        row1.addWidget(self._dot)
        row1.addWidget(self._state_lbl)
        row1.addStretch()
        layout.addLayout(row1)

        # 第二行：回合數
        self._ep_lbl = QLabel("Ep 0 / ∞")
        self._ep_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 9pt;"
            " border: none; background: transparent;"
        )
        layout.addWidget(self._ep_lbl)

        # 第三行：計時器
        self._time_lbl = QLabel("00:00:00")
        self._time_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 9pt;"
            " border: none; background: transparent;"
        )
        layout.addWidget(self._time_lbl)

        # 每秒更新計時器
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick_time)
        self._clock.start()

    def set_state(self, state: str) -> None:
        label, color = self._STATE_MAP.get(state, ("訓練中", COLORS["success"]))
        self._dot.setStyleSheet(
            f"color: {color}; font-size: 14pt; border: none; background: transparent;"
        )
        self._state_lbl.setText(label)

        if state == "paused" and self._paused_at is None:
            self._paused_at = time.monotonic()
        elif state == "running" and self._paused_at is not None:
            self._elapsed_offset += time.monotonic() - self._paused_at
            self._paused_at = None
        elif state == "stopped":
            self._clock.stop()

    def set_episode(self, ep: int, total: int) -> None:
        total_str = f"/{total:,}" if total > 0 else "/∞"
        self._ep_lbl.setText(f"Ep {ep:,}{total_str}")

    def _tick_time(self) -> None:
        now = time.monotonic()
        if self._paused_at is not None:
            raw = self._paused_at - self._start_time - self._elapsed_offset
        else:
            raw = now - self._start_time - self._elapsed_offset
        elapsed = max(0.0, raw)
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        s = int(elapsed % 60)
        self._time_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")
