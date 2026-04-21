# app/gui/components/info_bar.py
# -*- coding: utf-8 -*-
"""底部控制列（取代 control_panel.py）：按鈕 + 即時 log。"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..themes import COLORS


def _btn_style(bg: str = COLORS["bg_card"]) -> str:
    return f"""
        QPushButton {{
            background: {bg};
            color: {COLORS['text_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            font-size: 9pt;
        }}
        QPushButton:hover {{
            background: {COLORS['border']};
        }}
        QPushButton:disabled {{
            color: {COLORS['text_muted']};
            background: {COLORS['bg_dark']};
            border-color: {COLORS['bg_dark']};
        }}
    """


class InfoBar(QFrame):
    """底部列：控制按鈕（暫停／繼續／停止／儲存）+ 即時 log 訊息。"""

    def __init__(self, hotkey=None, parent=None):
        super().__init__(parent)
        self._hotkey = hotkey

        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_sidebar']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(6)

        self._btn_pause  = self._make_btn("⏸ 暫停",  90)
        self._btn_resume = self._make_btn("▶ 繼續",  90)
        self._btn_stop   = self._make_btn("■ 停止",  90)
        self._btn_save   = self._make_btn("💾 儲存", 90)

        self._btn_resume.setEnabled(False)

        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_resume.clicked.connect(self._on_resume)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_save.clicked.connect(self._on_save)

        for btn in (
            self._btn_pause, self._btn_resume,
            self._btn_stop,  self._btn_save,
        ):
            layout.addWidget(btn)

        sep = QLabel("|")
        sep.setStyleSheet(
            f"color: {COLORS['border']}; border: none; background: transparent;"
        )
        layout.addWidget(sep)

        self._log_lbl = QLabel("")
        self._log_lbl.setFont(QFont("Consolas", 8))
        self._log_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; border: none; background: transparent;"
        )
        self._log_lbl.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._log_lbl, stretch=1)

    def _make_btn(self, text: str, width: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(32)
        btn.setFixedWidth(width)
        btn.setStyleSheet(_btn_style())
        return btn

    # ── 公開 API ─────────────────────────────────────────────────────

    def set_log(self, msg: str) -> None:
        self._log_lbl.setText(msg)

    def set_state(self, state: str) -> None:
        running = (state == "running")
        paused  = (state == "paused")
        stopped = (state == "stopped")
        self._btn_pause.setEnabled(running)
        self._btn_resume.setEnabled(paused)
        self._btn_stop.setEnabled(not stopped)
        self._btn_save.setEnabled(not stopped)

    # ── 按鈕 callbacks ───────────────────────────────────────────────

    def _on_pause(self) -> None:
        if self._hotkey and not self._hotkey.pause_requested:
            self._hotkey.toggle_pause()

    def _on_resume(self) -> None:
        if self._hotkey and self._hotkey.pause_requested:
            self._hotkey.toggle_pause()

    def _on_stop(self) -> None:
        if self._hotkey:
            self._hotkey.request_stop()

    def _on_save(self) -> None:
        if self._hotkey:
            self._hotkey.request_save()
