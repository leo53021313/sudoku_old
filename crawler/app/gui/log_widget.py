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
