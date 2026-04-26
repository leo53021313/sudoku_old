# app/gui/settings_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QPushButton, QGroupBox, QMessageBox,
)
from config import CrawlerConfig


class SettingsDialog(QDialog):
    def __init__(self, config: CrawlerConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ 爬蟲設定")
        self.setMinimumWidth(420)
        self._config = config

        layout = QVBoxLayout(self)

        # ── Crawling ──────────────────────────────────────────────────────────
        crawl_grp = QGroupBox("爬蟲設定")
        crawl_form = QFormLayout(crawl_grp)

        self._num_workers = QSpinBox()
        self._num_workers.setRange(1, 200)
        self._num_workers.setValue(config.num_workers)
        crawl_form.addRow("爬蟲執行緒數（重啟後生效）:", self._num_workers)

        self._max_pool = QSpinBox()
        self._max_pool.setRange(1_000, 10_000_000)
        self._max_pool.setSingleStep(1_000)
        self._max_pool.setValue(config.max_pool_size)
        crawl_form.addRow("目標收錄上限（達到後暫停）:", self._max_pool)

        self._resume = QSpinBox()
        self._resume.setRange(0, 10_000_000)
        self._resume.setSingleStep(1_000)
        self._resume.setValue(config.resume_threshold)
        crawl_form.addRow("恢復爬取門檻（低於此數重新開始）:", self._resume)

        self._min_delay = QDoubleSpinBox()
        self._min_delay.setRange(0.0, 60.0)
        self._min_delay.setSingleStep(0.1)
        self._min_delay.setDecimals(2)
        self._min_delay.setValue(config.min_delay)
        crawl_form.addRow("最短請求間隔（秒）:", self._min_delay)

        self._max_delay = QDoubleSpinBox()
        self._max_delay.setRange(0.0, 60.0)
        self._max_delay.setSingleStep(0.1)
        self._max_delay.setDecimals(2)
        self._max_delay.setValue(config.max_delay)
        crawl_form.addRow("最長請求間隔（秒）:", self._max_delay)

        self._timeout = QSpinBox()
        self._timeout.setRange(1, 60)
        self._timeout.setValue(config.request_timeout)
        crawl_form.addRow("請求逾時（秒）:", self._timeout)

        layout.addWidget(crawl_grp)

        # ── Level weights ─────────────────────────────────────────────────────
        level_grp = QGroupBox("各難度爬取比例（填入相對比重，程式自動正規化）")
        level_form = QFormLayout(level_grp)
        level_names = ["L1 Easy", "L2 Medium", "L3 Hard", "L4 Evil"]
        self._weights: list[QSpinBox] = []
        weights = config.level_weights
        for i, name in enumerate(level_names):
            sb = QSpinBox()
            sb.setRange(0, 100)
            sb.setValue(weights[i] if i < len(weights) else 25)
            level_form.addRow(f"{name}:", sb)
            self._weights.append(sb)
        layout.addWidget(level_grp)

        # ── Proxy ─────────────────────────────────────────────────────────────
        proxy_grp = QGroupBox("Proxy 設定（下次啟動時生效）")
        proxy_form = QFormLayout(proxy_grp)

        self._proxy_workers = QSpinBox()
        self._proxy_workers.setRange(1, 500)
        self._proxy_workers.setValue(config.proxy_validate_workers)
        proxy_form.addRow("Proxy 驗證執行緒數:", self._proxy_workers)

        self._proxy_timeout = QSpinBox()
        self._proxy_timeout.setRange(1, 30)
        self._proxy_timeout.setValue(config.proxy_validate_timeout)
        proxy_form.addRow("Proxy 驗證逾時（秒）:", self._proxy_timeout)

        layout.addWidget(proxy_grp)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("套用並關閉")
        ok_btn.clicked.connect(self._apply)
        ok_btn.setDefault(True)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _apply(self) -> None:
        if self._resume.value() >= self._max_pool.value():
            QMessageBox.warning(
                self, "設定錯誤",
                "恢復爬取門檻必須小於目標收錄上限。",
            )
            return
        if self._min_delay.value() > self._max_delay.value():
            QMessageBox.warning(
                self, "設定錯誤",
                "最短請求間隔不可大於最長請求間隔。",
            )
            return
        self._config.num_workers          = self._num_workers.value()
        self._config.max_pool_size        = self._max_pool.value()
        self._config.resume_threshold     = self._resume.value()
        self._config.min_delay            = self._min_delay.value()
        self._config.max_delay            = self._max_delay.value()
        self._config.request_timeout      = self._timeout.value()
        self._config.level_weights        = [sb.value() for sb in self._weights]
        self._config.proxy_validate_workers = self._proxy_workers.value()
        self._config.proxy_validate_timeout = self._proxy_timeout.value()
        self._config.save()
        self.accept()
