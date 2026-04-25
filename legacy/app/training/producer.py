# app/training/producer.py
# -*- coding: utf-8 -*-
# Background puzzle-fetching threads (requests-based, no browser).

import json
import random
import threading
import traceback

from app.config import config
from app.web.reader import BlockedError, fetch_puzzle_via_requests, get_level_url
from app.training.hotkey_controller import HOTKEY


# ── Shared producer stats (read by GUI every ~30s) ─────────────────────────

_lock  = threading.Lock()
_stats = {"ok": 0, "fail": 0, "blocked": 0}


def stats_inc(key: str) -> None:
    with _lock:
        _stats[key] += 1


def stats_snapshot_and_reset() -> dict:
    with _lock:
        snap = dict(_stats)
        _stats.update({"ok": 0, "fail": 0, "blocked": 0})
    return snap


# ── Level selection ────────────────────────────────────────────────────────

def pick_level() -> int:
    raw = config.get("training.level_dist")
    if isinstance(raw, str):
        dist = {int(k): v for k, v in json.loads(raw).items()}
    else:
        dist = raw
    levels  = list(dist.keys())
    weights = [dist[lv] for lv in levels]
    return random.choices(levels, weights=weights, k=1)[0]


# ── Logging helpers ────────────────────────────────────────────────────────

def _log_pool(msg: str) -> None:
    if config.get("logging.print_pool"):
        print(msg)


def _log_web(msg: str) -> None:
    if config.get("logging.print_web_retry"):
        print(msg)


def _log_producer_success(msg: str) -> None:
    if config.get("logging.print_producer_success"):
        print(msg)


def count_givens(board) -> int:
    return sum(1 for row in board for v in row if v != 0)


# ── Puzzle validation ──────────────────────────────────────────────────────

def validate_loaded_puzzle(board, fixed) -> bool:
    import numpy as np
    b = np.asarray(board, dtype=np.int8)
    f = np.asarray(fixed, dtype=bool)
    if b.shape != (9, 9):
        raise RuntimeError(f"board shape 錯誤：{b.shape}")
    if f.shape != (9, 9):
        raise RuntimeError(f"fixed shape 錯誤：{f.shape}")
    givens = int(np.count_nonzero(b != 0))
    fc     = int(np.count_nonzero(f))
    if givens < config.get("crawler.min_expected_givens"):
        raise RuntimeError(f"givens 過少：{givens}")
    if givens > config.get("crawler.max_expected_givens"):
        raise RuntimeError(f"givens 過多：{givens}")
    if fc <= 0:
        raise RuntimeError("fixed_count=0，讀盤失敗")
    if fc != givens:
        raise RuntimeError(f"givens={givens} vs fixed={fc} 不一致")
    return True


# ── Producer thread entry point ────────────────────────────────────────────

def run_producer(db, proxy_manager, stop_event) -> None:
    """Background scraper: fetches puzzles via requests (no browser)."""
    name = threading.current_thread().name
    _log_pool(f"[{name}] 執行緒啟動（requests 模式）")

    while not stop_event.is_set() and not HOTKEY.stop_requested:
        try:
            if db.count_unsolved() >= config.get("crawler.max_pool_size"):
                stop_event.wait(timeout=30.0)
                continue

            level     = pick_level()
            fetch_url = get_level_url(level)

            proxy_dict = None
            server_url = None
            if proxy_manager:
                pw = proxy_manager.get_playwright_proxy()
                if pw:
                    server_url = pw["server"]
                    proxy_dict = {"http": server_url, "https": server_url}

            try:
                board, fixed = fetch_puzzle_via_requests(
                    fetch_url,
                    proxy_dict=proxy_dict,
                    timeout=config.get("crawler.page_timeout_ms") // 1000,
                    debug=config.get("logging.producer_debug"),
                )
                validate_loaded_puzzle(board, fixed)

            except BlockedError:
                _log_pool(f"[{name}] IP 封鎖，切換 Proxy")
                stats_inc("blocked")
                stop_event.wait(timeout=2.0)
                continue

            except ValueError as e:
                if proxy_manager and server_url:
                    proxy_manager.blacklist_server(server_url)
                _log_web(f"[{name}] 解析失敗，已移除代理：{e}")
                stats_inc("fail")
                stop_event.wait(timeout=0.5)
                continue

            except Exception as e:
                _log_web(
                    f"[{name}] 抓取失敗（{type(e).__name__}: {e}）"
                    + (f"\n{traceback.format_exc().strip()}"
                       if config.get("logging.producer_debug") else "")
                )
                stats_inc("fail")
                stop_event.wait(timeout=1.0)
                continue

            res = db.upsert_puzzle(board, source="websudoku", level=level)
            if res["inserted"]:
                stats_inc("ok")
                _log_producer_success(
                    f"[{name}] 新題 id={res['puzzle_id']}"
                    f" L{level} givens={count_givens(board)}"
                )

            stop_event.wait(
                timeout=random.uniform(
                    config.get("crawler.min_delay"),
                    config.get("crawler.max_delay"),
                )
            )

        except Exception as e:
            _log_pool(f"[{name}] 未預期例外：{type(e).__name__}: {e}")
            stop_event.wait(timeout=5.0)

    _log_pool(f"[{name}] 執行緒結束")
