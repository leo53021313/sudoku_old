# sb3/tests/test_pool_db_close.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.pool_db import PuzzlePoolDB


def test_close_releases_connection(tmp_path):
    """close() must set self._local.conn to None so the connection is released."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)

    # Force connection creation
    with db.transaction() as conn:
        pass

    assert db._local.conn is not None, "Connection should exist after use"

    db.close()

    assert db._local.conn is None, "Connection should be None after close()"


def test_del_calls_close(tmp_path):
    """__del__ must call close() without raising."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)

    with db.transaction() as conn:
        pass

    # Should not raise
    db.__del__()
    assert db._local.conn is None
