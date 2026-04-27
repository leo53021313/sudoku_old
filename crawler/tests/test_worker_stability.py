# crawler/tests/test_worker_stability.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def worker(tmp_path):
    """Create a CrawlerWorker with a real DB and mocked proxy/config."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1, max_pool_size=100)
    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None
    return CrawlerWorker(0, config, proxy, db)


def test_error_signal_contains_traceback(qapp, worker, monkeypatch):
    """When fetch raises, the error signal must include the full traceback."""
    import app.core.worker as worker_mod

    emitted = []

    # Connect to the signal to capture emissions
    def on_event(d):
        emitted.append(d)
        # Stop the worker after first event to prevent infinite loop
        worker._stop = True

    worker.event_signal.connect(on_event)

    # Make fetch raise a specific error
    monkeypatch.setattr(
        worker_mod, "fetch_puzzle_via_requests",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("connection reset")),
    )

    # Patch db to return non-full stats so it reaches the fetch path
    worker.db.get_pool_stats = lambda: {"total": 0}

    # Patch random.uniform to return 0 delay to speed up test
    monkeypatch.setattr("random.uniform", lambda a, b: 0.0)

    worker._stop = False
    worker.run()

    error_events = [e for e in emitted if e.get("type") == "error"]
    assert error_events, "No error event emitted"
    assert "Traceback (most recent call last)" in error_events[0]["msg"], \
        f"Expected traceback in msg, got: {error_events[0]['msg']!r}"
    assert "connection reset" in error_events[0]["msg"], \
        f"Expected 'connection reset' in msg, got: {error_events[0]['msg']!r}"


def test_proxy_error_emits_short_net_error_not_traceback(qapp, worker, monkeypatch):
    """Routine requests.exceptions.RequestException must produce a short net_error, not a full traceback."""
    import app.core.worker as worker_mod
    import requests

    emitted = []

    def on_event(d):
        emitted.append(d)
        worker._stop = True

    worker.event_signal.connect(on_event)

    monkeypatch.setattr(
        worker_mod, "fetch_puzzle_via_requests",
        lambda *a, **kw: (_ for _ in ()).throw(
            requests.exceptions.ProxyError("Unable to connect to proxy")
        ),
    )
    worker.db.get_pool_stats = lambda: {"total": 0}
    monkeypatch.setattr("random.uniform", lambda a, b: 0.0)

    worker._stop = False
    worker.run()

    net_events = [e for e in emitted if e.get("type") == "net_error"]
    assert net_events, "No net_error event emitted for ProxyError"
    msg = net_events[0]["msg"]
    assert "Traceback" not in msg, \
        f"net_error msg must not contain traceback, got: {msg!r}"
    assert "ProxyError" in msg, \
        f"Expected exception class name in msg, got: {msg!r}"

    # Also confirm no `error` (red) events leaked through
    error_events = [e for e in emitted if e.get("type") == "error"]
    assert not error_events, \
        f"Routine ProxyError should not produce error events, got: {error_events}"


def test_get_stats_cached_within_ttl(tmp_path):
    """get_pool_stats must not be called more than once per 2s within a single worker."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig
    from unittest.mock import MagicMock

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig()
    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None

    worker = CrawlerWorker(0, config, proxy, db)

    call_count = [0]
    original_get_pool_stats = db.get_pool_stats

    def counting_get_pool_stats(**kwargs):
        call_count[0] += 1
        return original_get_pool_stats(**kwargs)

    db.get_pool_stats = counting_get_pool_stats

    # Call _get_stats 5 times in rapid succession
    for _ in range(5):
        worker._get_stats()

    # Without cache: 5 calls. With cache: 1 call (all within 2s TTL).
    assert call_count[0] == 1, \
        f"Expected 1 DB call (cached), got {call_count[0]}"


def test_worker_warns_on_direct_connect(qapp, tmp_path, monkeypatch):
    """Worker must emit one 'warn' event when proxy pool is empty (direct connect)."""
    from app.core.worker import CrawlerWorker
    from app.db.pool_db import PuzzlePoolDB
    from config import CrawlerConfig
    import app.core.worker as worker_mod
    from unittest.mock import MagicMock

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1, max_pool_size=100)

    proxy = MagicMock()
    proxy.get_requests_proxy.return_value = None  # empty proxy pool

    worker = CrawlerWorker(0, config, proxy, db)

    emitted = []
    worker.event_signal.connect(lambda d: emitted.append(d))
    worker._stop = False

    # Patch fetch to succeed and stop the worker after first iteration
    monkeypatch.setattr(
        worker_mod, "fetch_puzzle_via_requests",
        lambda *a, **kw: ([[0]*9]*9, [[False]*9]*9),
    )
    call_count = [0]

    def patched_upsert(board, source, level):
        call_count[0] += 1
        worker._stop = True
        return {"inserted": True, "puzzle_id": 1}

    db.upsert_puzzle = patched_upsert
    monkeypatch.setattr("random.uniform", lambda a, b: 0.0)

    worker.run()

    warn_events = [e for e in emitted if e.get("type") == "warn"]
    assert warn_events, "No warn event emitted when proxy pool is empty"
    assert "直連" in warn_events[0]["msg"] or "direct" in warn_events[0]["msg"].lower(), \
        f"Expected direct-connect warning, got: {warn_events[0]['msg']!r}"

    # Second run on the same worker: warning should NOT repeat
    emitted.clear()
    worker._stop = False
    db.upsert_puzzle = patched_upsert  # re-attach (still stops after first iter)

    worker.run()

    warn_events2 = [e for e in emitted if e.get("type") == "warn"]
    assert not warn_events2, "Warn should only be emitted once per worker, not on every iteration"


def test_straggler_threads_are_terminated(qapp, tmp_path, monkeypatch):
    """Threads that don't stop within 5s must have terminate() called on them."""
    from app.gui.main_window import MainWindow
    from app.web.proxy_manager import ProxyManager
    from app.db.pool_db import PuzzlePoolDB
    from app.core.worker import CrawlerWorker
    from config import CrawlerConfig
    from unittest.mock import call, MagicMock

    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    config = CrawlerConfig(num_workers=1)
    proxy = ProxyManager()

    win = MainWindow(config, proxy, db)

    # Create a mock worker that never stops
    mock_worker = MagicMock(spec=CrawlerWorker)
    mock_worker.isRunning.return_value = True  # always appears running

    win._workers = [mock_worker]

    win._on_stop()

    # terminate() must be called on the straggler
    mock_worker.terminate.assert_called_once()
    # The last wait() call must be wait(1_000) — the post-terminate cleanup wait
    assert mock_worker.wait.call_args_list[-1] == call(1_000)
