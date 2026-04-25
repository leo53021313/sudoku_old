# app/gui/components/sidebar_panel.py
# -*- coding: utf-8 -*-
"""
可收合的側欄設定面板（取代 modal SettingsDialog）。
4 個 tab：一般設定 / AI 訓練 / 爬蟲 / 除錯
頂部篩選：一般 / 進階 / 除錯
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QTabWidget,
    QScrollArea, QWidget, QLabel, QPushButton,
    QCheckBox, QSpinBox, QDoubleSpinBox,
    QLineEdit, QComboBox, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal

from ..themes import COLORS
from app.config import config
from app.config.schema import CONFIG_SCHEMA


# ── Tab 分組定義 ───────────────────────────────────────────────────────────

_TAB_GROUPS: dict[str, tuple[str, list[str]]] = {
    "general": ("一般設定", [
        "gui.enabled", "gui.max_boards", "gui.board_fps",
        "run.mode", "run.infinite_training", "run.train_episodes",
        "run.max_steps_per_episode", "run.eval_episodes",
        "model.path", "model.auto_load", "model.dir",
        "model.reset_optimizer_on_load", "model.reset_counters_on_load",
        "training.save_every_episodes", "training.device", "training.use_fp16",
    ]),
    "ai": ("AI 訓練", [
        "training.lr", "training.rollout_steps", "training.mrv_mix_prob",
        "training.phase1_tau", "training.phase2_tau", "training.level_dist",
        "training.success_bonus",
        "training.gamma", "training.gae_lambda", "training.ppo_clip",
        "training.ppo_epochs", "training.ppo_minibatch",
        "training.mrv_decay_steps", "training.mrv_min_prob",
        "training.phase1_steps", "training.phase2_steps",
        "training.adaptive_entropy", "training.target_entropy",
        "training.bc_coef", "training.dead_end_penalty",
        "training.agent_type", "training.train_policy_mode",
        "training.eval_policy_mode",
        "training.normalize_returns", "training.value_coef",
        "training.grad_clip", "training.cell_dim", "training.head_dim",
        "training.teacher_max_cand", "training.entropy_init",
        "training.entropy_lr", "training.min_entropy_coef",
        "training.max_entropy_coef",
        "training.policy_demo_capacity", "training.policy_demo_weight",
    ]),
    "crawler": ("爬蟲", [
        "crawler.producer_workers",
        "crawler.max_pool_size", "crawler.min_pool_size",
        "proxy.enabled",
        "crawler.min_delay", "crawler.max_delay",
        "crawler.page_timeout_ms", "crawler.max_tries_per_puzzle",
        "proxy.validate", "proxy.validate_workers",
        "proxy.validate_timeout", "db.path",
        "crawler.min_expected_givens", "crawler.max_expected_givens",
        "proxy.validate_count", "db.worker_name",
    ]),
    "debug": ("除錯", [
        "logging.print_episode_result", "logging.print_every_episodes",
        "logging.print_rolling_stats", "logging.rolling_stats_window",
        "logging.print_agent_update_log", "logging.print_run_config",
        "logging.print_web_retry", "logging.print_pool",
        "logging.print_producer_success", "logging.producer_debug",
    ]),
}

# Visibility 等級對應數字（數字越小越核心）
_VIS_ORDER = {"core": 0, "advanced": 1, "debug": 2}


# ── 主元件 ──────────────────────────────────────────────────────────────────

class SidebarPanel(QFrame):
    """可收合的側欄設定面板。"""

    applied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._widgets: dict[str, QWidget] = {}
        self._row_widgets: dict[str, QWidget] = {}
        self._vis_level = "core"

        self.setFixedWidth(240)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_sidebar']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 顯示等級選擇器 ────────────────────────────────────────────
        level_bar = QWidget()
        level_bar.setStyleSheet(
            f"background: {COLORS['bg_dark']};"
            f"border-bottom: 1px solid {COLORS['border']};"
        )
        lb = QHBoxLayout(level_bar)
        lb.setContentsMargins(6, 4, 6, 4)
        lb.setSpacing(4)

        lbl = QLabel("顯示：")
        lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 8pt;"
            " border: none; background: transparent;"
        )
        lb.addWidget(lbl)

        self._level_combo = QComboBox()
        self._level_combo.addItems(["一般", "進階", "除錯"])
        self._level_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        self._level_combo.currentIndexChanged.connect(self._on_level_changed)
        lb.addWidget(self._level_combo, stretch=1)
        root.addWidget(level_bar)

        # ── Tab 區域 ──────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {COLORS['bg_sidebar']};
                border: none;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_dark']};
                color: {COLORS['text_muted']};
                padding: 4px 5px;
                font-size: 8pt;
                border: 1px solid {COLORS['border']};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['bg_sidebar']};
                color: {COLORS['text_primary']};
            }}
        """)

        for group_key, (tab_name, keys) in _TAB_GROUPS.items():
            self._tabs.addTab(self._build_tab(keys), tab_name)

        root.addWidget(self._tabs, stretch=1)

        # ── 底部：題庫狀態 + 套用按鈕 ────────────────────────────────
        bottom = QWidget()
        bottom.setStyleSheet(
            f"background: {COLORS['bg_dark']};"
            f"border-top: 1px solid {COLORS['border']};"
        )
        bl = QVBoxLayout(bottom)
        bl.setContentsMargins(8, 6, 8, 6)
        bl.setSpacing(4)

        self._pool_lbl = QLabel("題庫: — | 未解: —")
        self._pool_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; font-size: 8pt;"
            " border: none; background: transparent;"
        )
        bl.addWidget(self._pool_lbl)

        apply_btn = QPushButton("套用設定")
        apply_btn.setFixedHeight(30)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['info']};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #2980b9; }}
        """)
        apply_btn.clicked.connect(self._on_apply)
        bl.addWidget(apply_btn)
        root.addWidget(bottom)

        # 初始化可見度
        self._apply_visibility()

    # ── Tab 建構 ─────────────────────────────────────────────────────

    def _build_tab(self, keys: list[str]) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {COLORS['bg_sidebar']}; }}
            QScrollBar:vertical {{
                background: {COLORS['bg_dark']}; width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['border']}; border-radius: 2px;
            }}
        """)

        container = QWidget()
        container.setStyleSheet(f"background: {COLORS['bg_sidebar']};")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(8, 6, 8, 6)
        vbox.setSpacing(4)

        for key in keys:
            schema = CONFIG_SCHEMA.get(key)
            if schema is None:
                continue
            row = self._build_row(key, schema)
            self._row_widgets[key] = row
            vbox.addWidget(row)

        vbox.addStretch()
        scroll.setWidget(container)
        return scroll

    def _build_row(self, key: str, schema: dict) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(row)
        lay.setContentsMargins(0, 2, 0, 2)
        lay.setSpacing(2)

        # 標籤 + ⚠ 重啟提示
        top = QHBoxLayout()
        top.setSpacing(3)

        lbl = QLabel(schema.get("label", key))
        lbl.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 8pt;"
            " background: transparent; border: none;"
        )
        lbl.setWordWrap(True)

        tooltip = schema.get("tooltip_zh") or schema.get("description", "")
        if tooltip:
            lbl.setToolTip(tooltip)

        top.addWidget(lbl, stretch=1)

        if schema.get("reload_required", True):
            warn = QLabel("⚠")
            warn.setStyleSheet(
                f"color: {COLORS['warning']}; font-size: 8pt;"
                " background: transparent; border: none;"
            )
            warn.setToolTip("需要重新啟動訓練才能生效")
            top.addWidget(warn)

        lay.addLayout(top)

        # 輸入 widget
        widget = self._make_input(key, schema)
        if tooltip:
            widget.setToolTip(tooltip)
        self._widgets[key] = widget
        lay.addWidget(widget)

        return row

    def _make_input(self, key: str, schema: dict) -> QWidget:
        typ     = schema.get("type", "str")
        default = config.get(key)
        base    = (
            f"background: {COLORS['bg_card']};"
            f"color: {COLORS['text_primary']};"
            f"border: 1px solid {COLORS['border']};"
            "border-radius: 3px; padding: 2px 4px; font-size: 8pt;"
        )

        if typ == "bool":
            w = QCheckBox()
            w.setChecked(bool(default))
            w.setStyleSheet(
                f"color: {COLORS['text_primary']};"
                " background: transparent; border: none;"
            )
            return w

        if typ == "int":
            w = QSpinBox()
            w.setMinimum(int(schema.get("min", -2147483648)))
            w.setMaximum(int(schema.get("max",  2147483647)))
            w.setValue(int(default) if default is not None else 0)
            w.setFixedHeight(24)
            w.setStyleSheet(f"QSpinBox {{ {base} }}")
            return w

        if typ == "float":
            w = QDoubleSpinBox()
            w.setMinimum(float(schema.get("min", 0.0)))
            w.setMaximum(float(schema.get("max", 1.0)))
            w.setValue(float(default) if default is not None else 0.0)
            w.setDecimals(6)
            w.setSingleStep(1e-4)
            w.setFixedHeight(24)
            w.setStyleSheet(f"QDoubleSpinBox {{ {base} }}")
            return w

        if typ == "str" and schema.get("options"):
            w = QComboBox()
            for opt in schema["options"]:
                w.addItem(str(opt))
            idx = w.findText(str(default) if default is not None else "")
            if idx >= 0:
                w.setCurrentIndex(idx)
            w.setFixedHeight(24)
            w.setStyleSheet(f"""
                QComboBox {{ {base} }}
                QComboBox::drop-down {{ border: none; }}
                QComboBox QAbstractItemView {{
                    background: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                    border: 1px solid {COLORS['border']};
                }}
            """)
            return w

        # str (free text)
        w = QLineEdit(str(default) if default is not None else "")
        w.setFixedHeight(24)
        w.setStyleSheet(f"QLineEdit {{ {base} }}")
        return w

    # ── 可見度控制 ────────────────────────────────────────────────────

    def _on_level_changed(self, idx: int) -> None:
        self._vis_level = ["core", "advanced", "debug"][idx]
        self._apply_visibility()

    def _apply_visibility(self) -> None:
        current_order = _VIS_ORDER.get(self._vis_level, 0)
        for key, row in self._row_widgets.items():
            schema = CONFIG_SCHEMA.get(key, {})
            key_vis = schema.get("visibility", "core")
            key_order = _VIS_ORDER.get(key_vis, 0)
            row.setVisible(key_order <= current_order)

    # ── 套用設定 ─────────────────────────────────────────────────────

    def _on_apply(self) -> None:
        needs_restart = False
        for key, widget in self._widgets.items():
            schema = CONFIG_SCHEMA.get(key)
            if schema is None:
                continue
            typ = schema.get("type", "str")
            if typ == "bool":
                value = widget.isChecked()
            elif typ == "int":
                value = widget.value()
            elif typ == "float":
                value = widget.value()
            elif typ == "str" and schema.get("options"):
                value = widget.currentText()
            else:
                value = widget.text()

            if value != config.get(key):
                config.set(key, value)
                if schema.get("reload_required", True):
                    needs_restart = True

        self.applied.emit()
        if needs_restart:
            msg = QMessageBox(self)
            msg.setWindowTitle("設定已儲存")
            msg.setText(
                "部分設定需要重新啟動訓練才能生效（標有 ⚠ 的設定）。"
            )
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()

    # ── 題庫狀態更新（供 DashboardWindow 呼叫）────────────────────────

    def update_pool_status(
        self,
        total: int,
        unsolved: int,
        proxy_valid: int,
        proxy_total: int,
    ) -> None:
        self._pool_lbl.setText(
            f"題庫: {total:,} | 未解: {unsolved:,} | "
            f"Proxy: {proxy_valid}/{proxy_total}"
        )
