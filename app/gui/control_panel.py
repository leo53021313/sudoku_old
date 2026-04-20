# app/gui/control_panel.py
# -*- coding: utf-8 -*-
"""
底部控制列：Pause / Resume / Stop / Save Model + 最後一行 log。
按鈕直接設定 HotkeyController 的 flag，與鍵盤熱鍵共用同一套機制。
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ControlPanel(QFrame):

    def __init__(self, hotkey=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(44)

        self._hotkey = hotkey

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self._btn_pause  = QPushButton("⏸ Pause")
        self._btn_resume = QPushButton("▶ Resume")
        self._btn_stop   = QPushButton("■ Stop")
        self._btn_save   = QPushButton("💾 Save")

        for btn in (self._btn_pause, self._btn_resume, self._btn_stop, self._btn_save):
            btn.setFixedHeight(30)
            btn.setFixedWidth(80)

        self._btn_resume.setEnabled(False)

        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_resume.clicked.connect(self._on_resume)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_save.clicked.connect(self._on_save)

        layout.addWidget(self._btn_pause)
        layout.addWidget(self._btn_resume)
        layout.addWidget(self._btn_stop)
        layout.addWidget(self._btn_save)

        self._log_lbl = QLabel("")
        self._log_lbl.setFont(QFont("Consolas", 8))
        self._log_lbl.setStyleSheet("color: #444;")
        self._log_lbl.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self._log_lbl, stretch=1)

    # ── 公開 API ──────────────────────────────────────────────────────

    def set_log(self, msg: str) -> None:
        self._log_lbl.setText(msg)

    def set_state(self, state: str) -> None:
        """state: 'running' | 'paused' | 'stopped'"""
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
