# app/gui/db_panel.py
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt

from app.db.pool_db import PuzzlePoolDB

_LEVEL_COLORS = ["#74b9ff", "#55efc4", "#fdcb6e", "#fd79a8"]
_STATUSES = [
    ("new",          "new"),
    ("training",     "訓練中"),
    ("solved_local", "solved"),
]


class DbPanel(QWidget):
    def __init__(self, db: PuzzlePoolDB, max_pool_size: int = 50_000, parent=None):
        super().__init__(parent)
        self.db = db
        self.max_pool_size = max_pool_size
        self._refresh_error_shown: bool = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("📦 DB 現況 (puzzle_pool.db)")
        title.setStyleSheet(
            "color:#a29bfe;font-size:10px;font-weight:bold;background:transparent;"
        )
        self._total_lbl = QLabel("總計 0 筆")
        self._total_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._total_lbl.setStyleSheet("color:#636e72;font-size:9px;background:transparent;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self._total_lbl)
        outer.addLayout(hdr)

        # Table inside a dark frame
        table_frame = QFrame()
        table_frame.setStyleSheet("QFrame{background:#0f1f3a;border-radius:5px;}")
        grid = QGridLayout(table_frame)
        grid.setContentsMargins(8, 6, 8, 6)
        grid.setSpacing(4)

        # Column headers: L1 L2 L3 L4 合計
        for ci, (color, txt) in enumerate(
            zip(_LEVEL_COLORS + ["#aaaaaa"], ["L1", "L2", "L3", "L4", "合計"])
        ):
            h = QLabel(txt)
            h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            h.setStyleSheet(f"color:{color};font-size:9px;background:transparent;")
            grid.addWidget(h, 0, ci + 1)

        # Data rows
        self._cells: list[list[QLabel]] = []
        for ri, (_, display) in enumerate(_STATUSES):
            row_lbl = QLabel(display)
            row_lbl.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
            grid.addWidget(row_lbl, ri + 1, 0)
            row: list[QLabel] = []
            for ci in range(5):
                cell = QLabel("0")
                cell.setAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                cell.setStyleSheet("color:#e0e0e0;font-size:9px;background:transparent;")
                grid.addWidget(cell, ri + 1, ci + 1)
                row.append(cell)
            self._cells.append(row)

        outer.addWidget(table_frame)

        # Progress bar
        prog_hdr = QHBoxLayout()
        prog_lbl = QLabel("收錄進度")
        prog_lbl.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
        self._prog_txt = QLabel(f"0 / {max_pool_size:,} (0%)")
        self._prog_txt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._prog_txt.setStyleSheet("color:#aaaaaa;font-size:9px;background:transparent;")
        prog_hdr.addWidget(prog_lbl)
        prog_hdr.addStretch()
        prog_hdr.addWidget(self._prog_txt)
        outer.addLayout(prog_hdr)

        self._bar = QProgressBar()
        self._bar.setRange(0, max_pool_size)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(8)
        self._bar.setStyleSheet(
            "QProgressBar{background:#2d2d4e;border-radius:4px;border:none;}"
            "QProgressBar::chunk{"
            "background:qlineargradient("
            "x1:0,y1:0,x2:1,y2:0,stop:0 #6c5ce7,stop:1 #a29bfe);"
            "border-radius:4px;}"
        )
        outer.addWidget(self._bar)

    def refresh(self) -> None:
        """Query DB and update all cells. Called by QTimer every 5 s."""
        try:
            per_level = [self.db.get_pool_stats(level=i) for i in range(1, 5)]
            grand = self.db.get_pool_stats()
        except Exception as e:
            if not self._refresh_error_shown:
                self._refresh_error_shown = True
                self._total_lbl.setText(f"DB 錯誤: {e}")
            return

        self._refresh_error_shown = False
        total = grand["total"]
        self._total_lbl.setText(f"總計 {total:,} 筆")

        for ri, (key, _) in enumerate(_STATUSES):
            row_sum = 0
            for ci in range(4):
                v = per_level[ci].get(key, 0)
                self._cells[ri][ci].setText(f"{v:,}")
                row_sum += v
            self._cells[ri][4].setText(f"{row_sum:,}")

        pct = int(total * 100 / self.max_pool_size) if self.max_pool_size else 0
        self._prog_txt.setText(f"{total:,} / {self.max_pool_size:,} ({pct}%)")
        self._bar.setValue(min(total, self.max_pool_size))

    def update_max(self, new_max: int) -> None:
        self.max_pool_size = new_max
        self._bar.setRange(0, new_max)
