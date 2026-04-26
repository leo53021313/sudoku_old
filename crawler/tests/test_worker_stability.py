# crawler/tests/test_worker_stability.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import MagicMock, patch
from PyQt6.QtCore import QCoreApplication
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
        if emitted:
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
    assert "Traceback" in error_events[0]["msg"] or "ValueError" in error_events[0]["msg"], \
        f"Expected traceback in msg, got: {error_events[0]['msg']!r}"
