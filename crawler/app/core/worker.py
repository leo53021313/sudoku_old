# app/core/worker.py
from __future__ import annotations

import random
import time

from PyQt6.QtCore import QThread, pyqtSignal

from app.web.reader import fetch_puzzle_via_requests, get_level_url, BlockedError
from app.web.proxy_manager import ProxyManager
from app.db.pool_db import PuzzlePoolDB
from config import CrawlerConfig


class CrawlerWorker(QThread):
    event_signal = pyqtSignal(dict)

    def __init__(
        self,
        worker_id: int,
        config: CrawlerConfig,
        proxy_manager: ProxyManager,
        db: PuzzlePoolDB,
    ) -> None:
        super().__init__()
        self.worker_id = worker_id
        self.config = config
        self.proxy_manager = proxy_manager
        self.db = db
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        while not self._stop:
            # Pause when DB is full; resume when it drops below threshold
            try:
                total = self.db.get_pool_stats()["total"]
            except Exception:
                time.sleep(2)
                continue

            if total >= self.config.max_pool_size:
                while not self._stop:
                    time.sleep(2)
                    try:
                        if self.db.get_pool_stats()["total"] < self.config.resume_threshold:
                            break
                    except Exception:
                        pass
                continue

            # Choose proxy (None = direct connection)
            proxy_dict = self.proxy_manager.get_requests_proxy()
            server_url: str | None = proxy_dict.get("http") if proxy_dict else None

            # Weighted random difficulty level
            level = random.choices([1, 2, 3, 4], weights=self.config.level_weights, k=1)[0]
            url = get_level_url(level)

            try:
                board, _fixed = fetch_puzzle_via_requests(
                    url, proxy_dict, timeout=self.config.request_timeout
                )
                result = self.db.upsert_puzzle(board, "websudoku", level)
                self.event_signal.emit({
                    "type": "inserted" if result["inserted"] else "duplicate",
                    "level": level,
                    "puzzle_id": result["puzzle_id"],
                    "worker_id": self.worker_id,
                })
            except BlockedError:
                if server_url:
                    self.proxy_manager.blacklist_server(server_url)
                self.event_signal.emit({
                    "type": "blocked",
                    "proxy": server_url or "direct",
                    "worker_id": self.worker_id,
                })
                continue
            except Exception as exc:
                self.event_signal.emit({
                    "type": "error",
                    "msg": str(exc)[:120],
                    "worker_id": self.worker_id,
                })

            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            if delay > 0:
                time.sleep(delay)
