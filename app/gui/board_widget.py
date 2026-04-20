# app/gui/board_widget.py
# -*- coding: utf-8 -*-
"""
單一 Sudoku 9x9 盤面 Widget。
以 QPainter 繪製，所有狀態更新必須在 Qt 主執行緒呼叫。
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QRect, QSize


# ── 色彩配置 ───────────────────────────────────────────────────────────────
_C = {
    "fixed_bg":     QColor(55,  55,  55),
    "fixed_fg":     QColor(255, 255, 255),
    "ai_bg":        QColor(210, 230, 255),
    "ai_fg":        QColor(20,  60,  160),
    "hl_bg":        QColor(255, 210, 60),
    "hl_fg":        QColor(0,   0,   0),
    "empty_bg":     QColor(255, 255, 255),
    "success_ov":   QColor(80,  200, 120, 70),
    "fail_ov":      QColor(220, 60,  60,  60),
    "box_line":     QColor(20,  20,  20),
    "cell_line":    QColor(170, 170, 170),
    "title_active": QColor(48,  130, 240),
    "title_succ":   QColor(40,  170, 80),
    "title_fail":   QColor(210, 50,  50),
    "title_idle":   QColor(130, 130, 130),
    "title_fg":     QColor(255, 255, 255),
}

TITLE_H = 22


class SudokuBoardWidget(QWidget):
    """
    顯示單一 Sudoku 盤面。
    狀態: "active" | "success" | "failed" | "idle"
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._board: list = [[0] * 9 for _ in range(9)]
        self._fixed: list = [[False] * 9 for _ in range(9)]
        self._highlight = None   # (row, col) or None
        self._status: str = "idle"
        self._episode: int = 0

        sp = QSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )
        sp.setHeightForWidth(True)
        self.setSizePolicy(sp)
        self.setMinimumSize(QSize(126, 126 + TITLE_H))

    # ── 公開 API ──────────────────────────────────────────────────────────

    def update_state(
        self,
        board: list,
        fixed: list,
        highlight=None,
        status: str = "active",
        episode: int = 0,
    ) -> None:
        self._board = board
        self._fixed = fixed
        self._highlight = highlight
        self._status = status
        self._episode = episode
        self.update()

    def reset_idle(self) -> None:
        self._board = [[0] * 9 for _ in range(9)]
        self._fixed = [[False] * 9 for _ in range(9)]
        self._highlight = None
        self._status = "idle"
        self._episode = 0
        self.update()

    # ── Qt overrides ───────────────────────────────────────────────────────

    def heightForWidth(self, w: int) -> int:
        return w + TITLE_H

    def sizeHint(self) -> QSize:
        return QSize(180, 180 + TITLE_H)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        W = self.width()
        H = self.height()
        board_px = min(W, H - TITLE_H)
        ox = (W - board_px) // 2
        oy = TITLE_H
        cell = board_px / 9

        self._draw_title(p, W)
        self._draw_cells(p, ox, oy, cell)
        self._draw_grid(p, ox, oy, board_px, cell)
        self._draw_overlay(p, ox, oy, board_px)

        p.end()

    # ── 私有繪製方法 ────────────────────────────────────────────────────────

    def _draw_title(self, p: QPainter, W: int) -> None:
        color = {
            "active":  _C["title_active"],
            "success": _C["title_succ"],
            "failed":  _C["title_fail"],
        }.get(self._status, _C["title_idle"])

        p.fillRect(0, 0, W, TITLE_H, color)

        status_text = {
            "active":  "解題中",
            "success": "✓ 成功",
            "failed":  "✗ 失敗",
        }.get(self._status, "---")

        if self._episode > 0:
            label = f"Ep {self._episode}  [{status_text}]"
        else:
            label = f"[{status_text}]"

        font = QFont("Arial", 8, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(_C["title_fg"])
        p.drawText(
            QRect(0, 0, W, TITLE_H),
            Qt.AlignmentFlag.AlignCenter,
            label,
        )

    def _draw_cells(self, p: QPainter, ox: int, oy: int, cell: float) -> None:
        font_sz = max(7, int(cell * 0.52))
        font = QFont("Arial", font_sz)
        p.setFont(font)

        for r in range(9):
            for c in range(9):
                x = int(ox + c * cell)
                y = int(oy + r * cell)
                cw = int(ox + (c + 1) * cell) - x
                ch = int(oy + (r + 1) * cell) - y

                val = self._board[r][c]
                is_fixed = self._fixed[r][c]
                is_hl = (self._highlight == (r, c))

                if is_hl:
                    bg, fg = _C["hl_bg"], _C["hl_fg"]
                elif is_fixed:
                    bg, fg = _C["fixed_bg"], _C["fixed_fg"]
                elif val != 0:
                    bg, fg = _C["ai_bg"], _C["ai_fg"]
                else:
                    bg, fg = _C["empty_bg"], _C["ai_fg"]

                p.fillRect(x, y, cw, ch, bg)

                if val != 0:
                    p.setPen(fg)
                    p.drawText(
                        QRect(x, y, cw, ch),
                        Qt.AlignmentFlag.AlignCenter,
                        str(val),
                    )

    def _draw_grid(
        self, p: QPainter, ox: int, oy: int, board_px: int, cell: float
    ) -> None:
        pen_cell = QPen(_C["cell_line"], 1)
        pen_box  = QPen(_C["box_line"], 2)

        for i in range(10):
            p.setPen(pen_box if i % 3 == 0 else pen_cell)
            xi = int(ox + i * cell)
            yi = int(oy + i * cell)
            p.drawLine(xi, oy, xi, oy + board_px)
            p.drawLine(ox, yi, ox + board_px, yi)

    def _draw_overlay(
        self, p: QPainter, ox: int, oy: int, board_px: int
    ) -> None:
        if self._status == "success":
            p.fillRect(ox, oy, board_px, board_px, _C["success_ov"])
        elif self._status == "failed":
            p.fillRect(ox, oy, board_px, board_px, _C["fail_ov"])
