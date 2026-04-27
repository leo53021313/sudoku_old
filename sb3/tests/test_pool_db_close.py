# sb3/tests/test_pool_db_close.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
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


def test_fetch_retries_on_locked_db(tmp_path, monkeypatch):
    """fetch_one_puzzle_for_training must retry up to 3 times on
    OperationalError: database is locked."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)

    # Pre-populate the DB BEFORE patching _get_conn so the row exists for
    # the fetch to find.
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1
    db.upsert_puzzle(board, level=1)

    call_count = [0]
    original_get_conn = db._get_conn

    def flaky_get_conn():
        if call_count[0] < 2:
            call_count[0] += 1
            raise sqlite3.OperationalError("database is locked")
        return original_get_conn()

    monkeypatch.setattr(db, "_get_conn", flaky_get_conn)
    # Speed up retries
    monkeypatch.setattr("time.sleep", lambda s: None)

    result = db.fetch_one_puzzle_for_training(level=1)
    assert result is not None
    assert call_count[0] == 2  # 2 failures then success


def test_migration_idempotent_with_pre_existing_schema(tmp_path):
    """_migrate must be idempotent: running PuzzlePoolDB(path) twice over a
    pre-existing schema (no level column) must not raise and must add the column."""
    db_path = str(tmp_path / "legacy.db")

    # Create a pre-existing schema WITHOUT level column
    raw = sqlite3.connect(db_path)
    raw.execute("""
        CREATE TABLE puzzles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_key  TEXT    NOT NULL UNIQUE,
            puzzle      TEXT    NOT NULL,
            givens      INTEGER NOT NULL,
            source      TEXT    NOT NULL DEFAULT 'websudoku',
            status      TEXT    NOT NULL DEFAULT 'new',
            tries       INTEGER NOT NULL DEFAULT 0,
            best_empty  INTEGER NOT NULL DEFAULT 81,
            best_reward REAL    NOT NULL DEFAULT 0,
            last_reward REAL    NOT NULL DEFAULT 0,
            last_empty  INTEGER NOT NULL DEFAULT 81,
            locked_by   TEXT    DEFAULT NULL,
            locked_at   TEXT    DEFAULT NULL,
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        );
    """)
    raw.commit()
    raw.close()

    # First open: should ALTER TABLE to add the level column
    db1 = PuzzlePoolDB(db_path)
    cols = {row[1] for row in
            db1._get_conn().execute("PRAGMA table_info(puzzles)")}
    assert "level" in cols

    # Second open: must NOT raise (PRAGMA-based check should see the column
    # already exists and skip the ALTER TABLE)
    db2 = PuzzlePoolDB(db_path)
    cols2 = {row[1] for row in
             db2._get_conn().execute("PRAGMA table_info(puzzles)")}
    assert "level" in cols2
