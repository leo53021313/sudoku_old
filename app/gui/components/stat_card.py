# app/gui/components/stat_card.py
# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QProgressBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..themes import COLORS


class StatCard(QFrame):
    """
    通用指標卡片：標籤（小字灰色）+ 數值（大字粗體）+ 可選進度條。
    """

    def __init__(
        self,
        label: str,
        unit: str = "",
        show_bar: bool = False,
        color: str = COLORS["info"],
        parent=None,
    ):
        super().__init__(parent)
        self._unit = unit
        self._color = color

        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        self._label_lbl = QLabel(label)
        self._label_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 9pt;"
            " border: none; background: transparent;"
        )
        self._label_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._label_lbl)

        self._value_lbl = QLabel("—")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self._value_lbl.setFont(font)
        self._value_lbl.setStyleSheet(
            f"color: {color}; border: none; background: transparent;"
        )
        self._value_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._value_lbl)

        if show_bar:
            self._bar = QProgressBar()
            self._bar.setFixedHeight(4)
            self._bar.setTextVisible(False)
            self._bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {COLORS['border']};
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background: {color};
                    border-radius: 2px;
                }}
            """)
            layout.addWidget(self._bar)
        else:
            self._bar = None

    def set_value(self, value: str) -> None:
        v = str(value)
        text = f"{v}{self._unit}" if self._unit and not v.endswith(self._unit) else v
        self._value_lbl.setText(text)

    def set_bar(self, current: int, total: int) -> None:
        if self._bar is not None:
            self._bar.setMaximum(max(total, 1))
            self._bar.setValue(max(0, min(current, total)))
