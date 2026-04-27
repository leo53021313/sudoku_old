# app/gui/main_window.py
from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QTimer

from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from app.core.worker import CrawlerWorker
from app.gui.stats_panel import StatsPanel
from app.gui.db_panel import DbPanel
from app.gui.log_widget import LogWidget
from app.gui.settings_dialog import SettingsDialog
from config import CrawlerConfig


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: CrawlerConfig,
        proxy_manager: ProxyManager,
        db: PuzzlePoolDB,
    ) -> None:
        super().__init__()
        self.config = config
        self.proxy_manager = proxy_manager
        self.db = db
        self._workers: list[CrawlerWorker] = []

        self.setWindowTitle("🕷 Sudoku Crawler")
        self.setMinimumWidth(500)
        self.setStyleSheet("QMainWindow,QWidget{background:#1a1a2e;color:#e0e0e0;}")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = QWidget()
        toolbar.setStyleSheet("QWidget{background:#16213e;border-radius:5px;}")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(10, 7, 10, 7)

        title = QLabel("🕷 Sudoku Crawler")
        title.setStyleSheet(
            "color:#a29bfe;font-size:13px;font-weight:bold;background:transparent;"
        )
        tb.addWidget(title)
        tb.addStretch()

        self._start_btn = QPushButton("▶ 開始")
        self._start_btn.setStyleSheet(
            "QPushButton{background:#00b894;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#00cec9;}"
            "QPushButton:disabled{background:#444;color:#888;}"
        )
        self._stop_btn = QPushButton("■ 停止")
        self._stop_btn.setStyleSheet(
            "QPushButton{background:#636e72;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#b2bec3;}"
            "QPushButton:disabled{background:#444;color:#888;}"
        )
        self._stop_btn.setEnabled(False)
        settings_btn = QPushButton("⚙ 設定")
        settings_btn.setStyleSheet(
            "QPushButton{background:#0984e3;color:#fff;border:none;"
            "border-radius:4px;padding:3px 10px;font-size:10px;}"
            "QPushButton:hover{background:#74b9ff;}"
        )

        self._start_btn.clicked.connect(self._on_start)
        self._stop_btn.clicked.connect(self._on_stop)
        settings_btn.clicked.connect(self._on_settings)

        for btn in (self._start_btn, self._stop_btn, settings_btn):
            tb.addWidget(btn)
        root.addWidget(toolbar)

        # ── Panels ────────────────────────────────────────────────────────────
        self.stats_panel = StatsPanel()
        root.addWidget(self.stats_panel)

        self.db_panel = DbPanel(db, max_pool_size=config.max_pool_size)
        root.addWidget(self.db_panel)

        self.log_widget = LogWidget()
        self.log_widget.setMinimumHeight(110)
        root.addWidget(self.log_widget)

        # ── Timers ────────────────────────────────────────────────────────────
        self._db_timer = QTimer(self)
        self._db_timer.timeout.connect(self._refresh_db)
        self._db_timer.start(5_000)

        self._uptime_timer = QTimer(self)
        self._uptime_timer.timeout.connect(self.stats_panel.refresh_uptime)
        self._uptime_timer.start(1_000)

        self._refresh_db()
        self.log_widget.add_message("就緒。點擊「開始」啟動爬蟲。", "grey")

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_start(self) -> None:
        if self._workers:
            return
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self.stats_panel.start_session(self.config.num_workers)
        self.log_widget.add_message(
            f"啟動 {self.config.num_workers} 個爬蟲執行緒...", "blue"
        )
        for i in range(self.config.num_workers):
            w = CrawlerWorker(i, self.config, self.proxy_manager, self.db)
            w.event_signal.connect(self._on_worker_event)
            w.start()
            self._workers.append(w)

    def _on_stop(self) -> None:
        if not self._workers:
            return
        self._stop_btn.setEnabled(False)
        self.log_widget.add_message("正在停止爬蟲...", "yellow")
        for w in self._workers:
            w.stop()
        for w in self._workers:
            w.wait(5_000)
        stragglers = [w for w in self._workers if w.isRunning()]
        for w in stragglers:
            w.terminate()
            w.wait(1_000)
        if stragglers:
            self.log_widget.add_message(
                f"⚠ {len(stragglers)} 個執行緒強制終止。", "yellow"
            )
        self._workers.clear()
        self.stats_panel.stop_session()
        self._start_btn.setEnabled(True)
        self.log_widget.add_message("爬蟲已停止。", "grey")

    def _on_settings(self) -> None:
        dlg = SettingsDialog(self.config, parent=self)
        if dlg.exec():
            self.db_panel.update_max(self.config.max_pool_size)
            self.log_widget.add_message("設定已儲存。", "grey")

    def _on_worker_event(self, event: dict) -> None:
        t = event["type"]
        if t == "inserted":
            self.stats_panel.increment_level(event["level"])
            self.log_widget.add_message(
                f"✓ L{event['level']} puzzle inserted (id={event['puzzle_id']})", "green"
            )
        elif t == "blocked":
            self.log_widget.add_message(
                f"⚠ BlockedError → blacklist {event['proxy']}", "yellow"
            )
        elif t == "warn":
            self.log_widget.add_message(event["msg"], "yellow")
        elif t == "net_error":
            self.log_widget.add_message(f"✗ {event['msg']}", "grey")
        elif t == "parse_error":
            self.log_widget.add_message(f"✗ {event['msg']}", "grey")
        elif t == "error":
            self.log_widget.add_message(f"✗ {event['msg']}", "red")

    def _refresh_db(self) -> None:
        self.db_panel.refresh()
        stats = self.proxy_manager.get_stats()
        self.stats_panel.refresh_proxy(stats["valid"], stats["total"])

    def closeEvent(self, event) -> None:
        self._on_stop()
        self.proxy_manager.stop_validation()
        event.accept()
