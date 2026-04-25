# app/gui/components/phase_widget.py
# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..themes import COLORS


class PhaseWidget(QFrame):
    """
    三階段課程進度可視化。
    當前 Phase 全彩高亮，其他 Phase 灰色。
    """

    # (phase_num, 英文名, 中文名, 門檻說明, 顏色)
    _PHASE_INFO = [
        (1, "Phase 1", "觀察學習", "成功率 ≥ 30%", COLORS["phase1"]),
        (2, "Phase 2", "逐步獨立", "成功率 ≥ 65%", COLORS["phase2"]),
        (3, "Phase 3", "自主解題", "AI 完全自主",  COLORS["phase3"]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_phase = 1
        self._mrv_prob = 0.9

        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(0)

        self._segments: list[_PhaseSegment] = []
        for i, (phase, name, zh, threshold, color) in enumerate(self._PHASE_INFO):
            seg = _PhaseSegment(phase, name, zh, threshold, color)
            self._segments.append(seg)
            layout.addWidget(seg, stretch=1)

            if i < len(self._PHASE_INFO) - 1:
                arrow = QLabel("▶")
                arrow.setStyleSheet(
                    f"color: {COLORS['text_muted']}; background: transparent;"
                    " border: none; font-size: 10pt;"
                )
                arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
                arrow.setFixedWidth(18)
                layout.addWidget(arrow)

        self._refresh()

    def set_phase(self, phase: int, mrv_prob: float = 0.0) -> None:
        self._current_phase = max(1, min(3, phase))
        self._mrv_prob = mrv_prob
        self._refresh()

    def _refresh(self) -> None:
        for seg in self._segments:
            active = (seg.phase == self._current_phase)
            seg.set_active(active, self._mrv_prob if active else 0.0)


class _PhaseSegment(QFrame):

    def __init__(
        self,
        phase: int,
        name: str,
        zh_name: str,
        threshold: str,
        color: str,
        parent=None,
    ):
        super().__init__(parent)
        self.phase = phase
        self._color = color
        self._threshold = threshold

        self.setStyleSheet("background: transparent; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(0)

        self._name_lbl = QLabel(name)
        nf = QFont()
        nf.setPointSize(8)
        self._name_lbl.setFont(nf)
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setStyleSheet("border: none; background: transparent;")

        self._zh_lbl = QLabel(zh_name)
        zf = QFont()
        zf.setPointSize(10)
        zf.setBold(True)
        self._zh_lbl.setFont(zf)
        self._zh_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zh_lbl.setStyleSheet("border: none; background: transparent;")

        self._sub_lbl = QLabel(threshold)
        sf = QFont()
        sf.setPointSize(7)
        self._sub_lbl.setFont(sf)
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setStyleSheet("border: none; background: transparent;")

        layout.addWidget(self._name_lbl)
        layout.addWidget(self._zh_lbl)
        layout.addWidget(self._sub_lbl)

        self.set_active(False)

    def set_active(self, active: bool, mrv_prob: float = 0.0) -> None:
        if active:
            tc = self._color
            bg = self._color + "22"
            border = f"1px solid {self._color}"
            sub_text = (
                f"MRV: {mrv_prob:.0%}" if mrv_prob > 0 else self._threshold
            )
            sub_color = self._color + "bb"
        else:
            tc = COLORS["text_muted"]
            bg = "transparent"
            border = "none"
            sub_text = self._threshold
            sub_color = COLORS["text_muted"]

        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: {border};
                border-radius: 4px;
            }}
        """)
        for lbl, color in (
            (self._name_lbl, tc),
            (self._zh_lbl,   tc),
            (self._sub_lbl,  sub_color),
        ):
            lbl.setStyleSheet(
                f"color: {color}; border: none; background: transparent;"
            )
        self._sub_lbl.setText(sub_text)
