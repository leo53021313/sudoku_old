#!/usr/bin/env python3
# crawler.py
"""
Standalone Sudoku puzzle crawler.

Usage:
    cd crawler
    python crawler.py
"""
import sys
import threading
from pathlib import Path

# Force UTF-8 on stdout/stderr so logs with → ⚠ 池等字元 don't crash on
# Windows cp950/cp936 consoles.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from PyQt6.QtWidgets import QApplication

from config import CrawlerConfig
from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from app.gui.main_window import MainWindow

DB_PATH = str(Path(__file__).parent.parent / "data" / "puzzle_pool.db")


def _init_proxy(proxy_manager: ProxyManager, config: CrawlerConfig) -> None:
    proxy_manager.download_all()
    proxy_manager.start_background_validation(
        max_workers=config.proxy_validate_workers,
        timeout=config.proxy_validate_timeout,
    )


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    config = CrawlerConfig.load()
    db = PuzzlePoolDB(DB_PATH)
    proxy_manager = ProxyManager()

    window = MainWindow(config, proxy_manager, db)
    window.show()

    window.log_widget.add_message("正在下載 Proxy 清單，請稍候...", "blue")
    threading.Thread(
        target=_init_proxy, args=(proxy_manager, config), daemon=True
    ).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
