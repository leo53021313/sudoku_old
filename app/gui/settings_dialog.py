# app/gui/settings_dialog.py
# -*- coding: utf-8 -*-
"""
設定對話框：根據 CONFIG_SCHEMA 動態生成 UI。
- 按 category 分 Tab
- reload_required=True 的設定旁顯示橘色警告
- 套用後即時生效（hot reload）或提示需重啟
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QComboBox, QDialogButtonBox, QScrollArea, QFrame,
    QFormLayout, QSizePolicy,
)
from PyQt6.QtCore import Qt

from app.config import config
from app.config.schema import CATEGORY_LABELS


class SettingsDialog(QDialog):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumSize(560, 480)
        self.resize(640, 560)
        self._widgets: dict[str, QWidget] = {}
        self._build_ui()

    # ── UI 建構 ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        tabs = QTabWidget()
        schema = config.schema()

        # 按 category 分組
        categories: dict[str, list[str]] = {}
        for key, entry in schema.items():
            cat = entry["category"]
            categories.setdefault(cat, []).append(key)

        cat_order = [
            "gui", "training", "run", "crawler",
            "proxy", "logging", "model", "db",
        ]
        for cat in cat_order:
            if cat not in categories:
                continue
            tab_widget = self._build_tab(categories[cat], schema)
            label = CATEGORY_LABELS.get(cat, cat)
            tabs.addTab(tab_widget, label)

        root.addWidget(tabs)

        # ── 底部按鈕 ─────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Apply).setText("套用")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        btns.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply
        )
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _build_tab(self, keys: list[str], schema: dict) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        form = QFormLayout(container)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)
        form.setContentsMargins(12, 12, 12, 12)

        for key in keys:
            entry = schema[key]
            label_text = entry["label"]
            current = config.get(key)

            widget = self._make_widget(key, entry, current)
            self._widgets[key] = widget

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)
            row_layout.addWidget(widget)

            if entry["reload_required"]:
                warn = QLabel("⚠ 需重啟")
                warn.setStyleSheet("color: #e67e22; font-size: 8pt;")
                warn.setSizePolicy(
                    QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
                )
                row_layout.addWidget(warn)

            row_layout.addStretch()

            lbl = QLabel(label_text)
            if entry.get("description"):
                lbl.setToolTip(entry["description"])
                widget.setToolTip(entry["description"])

            form.addRow(lbl, row_widget)

        scroll.setWidget(container)
        return scroll

    def _make_widget(self, key: str, entry: dict, current) -> QWidget:
        t = entry["type"]

        if t == "bool":
            w = QCheckBox()
            w.setChecked(bool(current))
            return w

        if t == "int":
            _INT32_MAX = 2_147_483_647
            w = QSpinBox()
            w.setMinimum(max(entry.get("min", 0), -_INT32_MAX - 1))
            w.setMaximum(min(entry.get("max", 9_999_999), _INT32_MAX))
            w.setValue(max(-_INT32_MAX - 1, min(int(current), _INT32_MAX)))
            w.setFixedWidth(110)
            return w

        if t == "float":
            w = QDoubleSpinBox()
            w.setMinimum(entry.get("min", 0.0))
            w.setMaximum(entry.get("max", 1e9))
            w.setDecimals(6)
            w.setSingleStep(0.0001)
            w.setValue(float(current))
            w.setFixedWidth(130)
            return w

        if t == "str" and "options" in entry:
            w = QComboBox()
            for opt in entry["options"]:
                w.addItem(str(opt))
            idx = w.findText(str(current))
            if idx >= 0:
                w.setCurrentIndex(idx)
            w.setFixedWidth(130)
            return w

        # str / dict → 純文字輸入
        w = QLineEdit()
        w.setText(str(current))
        w.setFixedWidth(260)
        return w

    # ── 套用設定 ─────────────────────────────────────────────────────

    def _apply(self) -> None:
        needs_restart: list[str] = []
        schema = config.schema()

        for key, widget in self._widgets.items():
            entry = schema[key]
            value = self._read_widget(widget, entry)
            hot = config.set(key, value)
            if not hot:
                needs_restart.append(entry["label"])

        if needs_restart:
            from PyQt6.QtWidgets import QMessageBox
            names = "、".join(needs_restart)
            QMessageBox.information(
                self,
                "部分設定需重啟",
                f"以下設定已儲存，重新啟動訓練後生效：\n\n{names}",
            )

        self.accept()

    def _read_widget(self, widget: QWidget, entry: dict):
        t = entry["type"]
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QDoubleSpinBox):
            return widget.value()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, QLineEdit):
            text = widget.text().strip()
            if t == "float":
                return float(text)
            if t == "int":
                return int(text)
            return text
        return None
