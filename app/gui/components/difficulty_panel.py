# app/gui/components/difficulty_panel.py
# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..themes import COLORS


_LEVEL_INFO: dict[int, tuple[str, str, str]] = {
    1: ("Easy",  "★☆☆☆", COLORS["easy"]),
    2: ("Med",   "★★☆☆", COLORS["med"]),
    3: ("Hard",  "★★★☆", COLORS["hard"]),
    4: ("Evil",  "★★★★", COLORS["evil"]),
}


class DifficultyPanel(QFrame):
    """難度分解面板：4 張 DifficultyCard 橫排。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self._cards: dict[int, DifficultyCard] = {}
        for level, (name, stars, color) in _LEVEL_INFO.items():
            card = DifficultyCard(name, stars, color)
            self._cards[level] = card
            layout.addWidget(card, stretch=1)

    def update_level(self, level: int, success: int, total: int) -> None:
        if level in self._cards:
            self._cards[level].set_stats(success, total)


class DifficultyCard(QFrame):
    """單一難度的統計卡片。"""

    def __init__(self, name: str, stars: str, color: str, parent=None):
        super().__init__(parent)
        self._color = color

        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_dark']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)

        # 難度名稱 + 星等
        header = QHBoxLayout()
        header.setSpacing(4)

        name_lbl = QLabel(name)
        nf = QFont()
        nf.setPointSize(9)
        nf.setBold(True)
        name_lbl.setFont(nf)
        name_lbl.setStyleSheet(
            f"color: {color}; border: none; background: transparent;"
        )

        stars_lbl = QLabel(stars)
        stars_lbl.setStyleSheet(
            f"color: {color}; font-size: 8pt; border: none; background: transparent;"
        )

        header.addWidget(name_lbl)
        header.addStretch()
        header.addWidget(stars_lbl)
        layout.addLayout(header)

        # N / M
        self._count_lbl = QLabel("0 / 0")
        self._count_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 9pt;"
            " border: none; background: transparent;"
        )
        layout.addWidget(self._count_lbl)

        # 成功率 %
        self._rate_lbl = QLabel("—")
        rf = QFont()
        rf.setPointSize(14)
        rf.setBold(True)
        self._rate_lbl.setFont(rf)
        self._rate_lbl.setStyleSheet(
            f"color: {color}; border: none; background: transparent;"
        )
        layout.addWidget(self._rate_lbl)

        # 進度條
        self._bar = QProgressBar()
        self._bar.setFixedHeight(4)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
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

    def set_stats(self, success: int, total: int) -> None:
        if total == 0:
            self._count_lbl.setText("0 / 0")
            self._rate_lbl.setText("—")
            self._bar.setValue(0)
        else:
            rate = success / total
            self._count_lbl.setText(f"{success} / {total}")
            self._rate_lbl.setText(f"{rate:.1%}")
            self._bar.setValue(int(rate * 100))
