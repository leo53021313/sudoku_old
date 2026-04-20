# app/gui/stats_panel.py
# -*- coding: utf-8 -*-
"""
左側統計面板：訓練指標 + 進度條 + 爬蟲狀態。
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QProgressBar,
    QGridLayout, QWidget, QSizePolicy,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QSize


def _bold_label(text: str, size: int = 8) -> QLabel:
    lbl = QLabel(text)
    f = QFont("Arial", size, QFont.Weight.Bold)
    lbl.setFont(f)
    return lbl


def _val_label(text: str = "—") -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Arial", 8))
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return lbl


def _section_title(text: str) -> QLabel:
    lbl = QLabel(f"── {text} ──")
    lbl.setFont(QFont("Arial", 8, QFont.Weight.Bold))
    lbl.setStyleSheet("color: #555; margin-top: 6px;")
    return lbl


class StatsPanel(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(230)

        root = QVBoxLayout(self)
        root.setSpacing(2)
        root.setContentsMargins(8, 8, 8, 8)

        # ── 狀態指示 ──────────────────────────────────────────────────
        self._status_lbl = QLabel("● Stopped")
        self._status_lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self._status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_status_style("stopped")
        root.addWidget(self._status_lbl)

        # ── 訓練統計 ──────────────────────────────────────────────────
        root.addWidget(_section_title("訓練統計"))
        grid = QGridLayout()
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setVerticalSpacing(2)

        self._ep_val      = _val_label()
        self._sr_val      = _val_label()
        self._rw_val      = _val_label()
        self._sp_val      = _val_label()
        self._upd_val     = _val_label()
        self._mrv_val     = _val_label()
        self._ent_val     = _val_label()
        self._loss_val    = _val_label()

        rows = [
            ("Episodes",    self._ep_val),
            ("成功率",       self._sr_val),
            ("Avg Reward",  self._rw_val),
            ("速度",         self._sp_val),
            ("PPO 更新",    self._upd_val),
            ("MRV Mix",     self._mrv_val),
            ("Entropy",     self._ent_val),
            ("Loss",        self._loss_val),
        ]
        for i, (name, val) in enumerate(rows):
            grid.addWidget(_bold_label(name), i, 0)
            grid.addWidget(val, i, 1)

        root.addLayout(grid)

        # ── Rollout Buffer 進度條 ─────────────────────────────────────
        root.addWidget(_section_title("Rollout Buffer"))
        self._buf_bar = QProgressBar()
        self._buf_bar.setRange(0, 100)
        self._buf_bar.setValue(0)
        self._buf_bar.setFormat("%v / 512")
        self._buf_bar.setFixedHeight(16)
        root.addWidget(self._buf_bar)

        # ── 爬蟲 / 資料庫 ─────────────────────────────────────────────
        root.addWidget(_section_title("爬蟲狀態"))
        grid2 = QGridLayout()
        grid2.setColumnStretch(0, 1)
        grid2.setColumnStretch(1, 1)
        grid2.setVerticalSpacing(2)

        self._pool_total  = _val_label()
        self._pool_unsol  = _val_label()
        self._proxy_val   = _val_label()
        self._prod_ok_val = _val_label()
        self._prod_fail_v = _val_label()
        self._prod_blk_v  = _val_label()

        rows2 = [
            ("題庫總數",     self._pool_total),
            ("未解題數",     self._pool_unsol),
            ("Proxy 有效",   self._proxy_val),
            ("爬蟲成功",     self._prod_ok_val),
            ("爬蟲失敗",     self._prod_fail_v),
            ("IP 封鎖",      self._prod_blk_v),
        ]
        for i, (name, val) in enumerate(rows2):
            grid2.addWidget(_bold_label(name), i, 0)
            grid2.addWidget(val, i, 1)

        root.addLayout(grid2)
        root.addStretch()

    # ── 更新方法（Qt 主執行緒呼叫）────────────────────────────────────

    def set_training_state(self, state: str) -> None:
        """state: 'running' | 'paused' | 'stopped'"""
        text = {"running": "● Running", "paused": "⏸ Paused", "stopped": "■ Stopped"}
        self._status_lbl.setText(text.get(state, state))
        self._set_status_style(state)

    def update_training(
        self,
        episode: int = 0,
        total: int = 0,
        success_rate: float = 0.0,
        avg_reward: float = 0.0,
        speed: float = 0.0,
        update_count: int = 0,
        mrv_prob: float = 0.0,
        entropy: float = 0.0,
        loss: float = 0.0,
        rollout_size: int = 0,
        rollout_cap: int = 512,
    ) -> None:
        tot_str = f"/{total}" if total else "/∞"
        self._ep_val.setText(f"{episode:,}{tot_str}")
        self._sr_val.setText(f"{success_rate:.1%}")
        self._rw_val.setText(f"{avg_reward:.2f}")
        self._sp_val.setText(f"{speed:.2f} ep/s")
        self._upd_val.setText(f"{update_count:,}")
        self._mrv_val.setText(f"{mrv_prob:.1%}")
        self._ent_val.setText(f"{entropy:.4f}")
        self._loss_val.setText(f"{loss:.4f}")

        pct = int(rollout_size / max(rollout_cap, 1) * 100)
        self._buf_bar.setRange(0, rollout_cap)
        self._buf_bar.setValue(rollout_size)
        self._buf_bar.setFormat(f"{rollout_size} / {rollout_cap}")

    def update_pool(
        self,
        total: int = 0,
        unsolved: int = 0,
        proxy_valid: int = 0,
        proxy_total: int = 0,
        prod_ok: int = 0,
        prod_fail: int = 0,
        prod_blocked: int = 0,
    ) -> None:
        self._pool_total.setText(f"{total:,}")
        self._pool_unsol.setText(f"{unsolved:,}")
        self._proxy_val.setText(f"{proxy_valid} / {proxy_total}")
        self._prod_ok_val.setText(f"{prod_ok:,}")
        self._prod_fail_v.setText(f"{prod_fail:,}")
        self._prod_blk_v.setText(f"{prod_blocked:,}")

    # ── 私有輔助 ──────────────────────────────────────────────────────

    def _set_status_style(self, state: str) -> None:
        color = {
            "running": "#1a8a2a",
            "paused":  "#b87000",
            "stopped": "#aa2222",
        }.get(state, "#555555")
        self._status_lbl.setStyleSheet(f"color: {color};")
