# app/gui/board_grid_panel.py
# -*- coding: utf-8 -*-
"""
多盤面響應式排列面板。
- 單一訓練執行緒：slot 0 = 即時盤面，slot 1..N = 最近完成的歷史
- 多執行緒（未來擴充）：每個 thread_id 擁有獨立 slot
- 視窗縮放時自動重排 grid 欄數
"""

from PyQt6.QtWidgets import QFrame, QGridLayout, QSizePolicy
from PyQt6.QtCore import QSize

from .board_widget import SudokuBoardWidget


def _grid_cols(n: int) -> int:
    if n <= 1:  return 1
    if n <= 2:  return 2
    if n <= 4:  return 2
    if n <= 6:  return 3
    return 3


class BoardGridPanel(QFrame):
    """
    固定 max_boards 個 SudokuBoardWidget，以 QGridLayout 排列。
    slot 0 永遠是當前進行中的 episode，其餘為歷史（最近完成）。
    """

    def __init__(self, max_boards: int = 4, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        self._max = max_boards
        self._gl = QGridLayout(self)
        self._gl.setSpacing(6)
        self._gl.setContentsMargins(6, 6, 6, 6)

        self._widgets: list[SudokuBoardWidget] = [
            SudokuBoardWidget(self) for _ in range(max_boards)
        ]
        self._rearrange()

    # ── 公開 API（由 training_gui QTimer callback 呼叫）──────────────────

    def on_episode_start(
        self, board: list, fixed: list, episode: int, level: int = 0
    ) -> None:
        """新 episode 開始：把所有歷史向右推一格，slot 0 顯示新盤面。"""
        for i in range(self._max - 1, 0, -1):
            src = self._widgets[i - 1]
            self._widgets[i].update_state(
                [row[:] for row in src._board],
                [row[:] for row in src._fixed],
                None,
                src._status if src._episode > 0 else "idle",
                src._episode,
                src._level,
            )
        self._widgets[0].update_state(board, fixed, None, "active", episode, level)

    def on_board_update(
        self, board: list, fixed: list, highlight, episode: int
    ) -> None:
        """即時步驟更新（只更新 slot 0，保留原有 level）。"""
        w = self._widgets[0]
        w.update_state(board, fixed, highlight, "active", episode, w._level)

    def on_episode_end(
        self, board: list, fixed: list, success: bool, episode: int
    ) -> None:
        """Episode 結束：更新 slot 0 的最終狀態標記。"""
        status = "success" if success else "failed"
        self._widgets[0].update_state(board, fixed, None, status, episode)

    def reset_all(self) -> None:
        for w in self._widgets:
            w.reset_idle()

    # ── 版面重排 ────────────────────────────────────────────────────────

    def _rearrange(self) -> None:
        while self._gl.count():
            item = self._gl.takeAt(0)
            if item and item.widget():
                item.widget().setParent(self)

        cols = _grid_cols(self._max)
        for i, w in enumerate(self._widgets):
            r, c = divmod(i, cols)
            self._gl.addWidget(w, r, c)

    def sizeHint(self) -> QSize:
        return QSize(600, 500)
