import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
import pytest
from app.db.pool_db import PuzzlePoolDB


def _board(givens: dict) -> list:
    b = [[0] * 9 for _ in range(9)]
    for (r, c), v in givens.items():
        b[r][c] = v
    return b


@pytest.fixture
def db(tmp_path):
    return PuzzlePoolDB(str(tmp_path / "test.db"))


def test_upsert_inserts_new_puzzle(db):
    result = db.upsert_puzzle(_board({(0, 0): 5, (1, 1): 3}), "websudoku", level=1)
    assert result["inserted"] is True
    assert isinstance(result["puzzle_id"], int)
    assert len(result["puzzle_key"]) == 81


def test_upsert_skips_duplicate(db):
    board = _board({(0, 0): 5, (1, 1): 3})
    r1 = db.upsert_puzzle(board, "websudoku", level=1)
    r2 = db.upsert_puzzle(board, "websudoku", level=1)
    assert r1["inserted"] is True
    assert r2["inserted"] is False
    assert r1["puzzle_id"] == r2["puzzle_id"]


def test_get_pool_stats_counts_by_level(db):
    db.upsert_puzzle(_board({(0, 0): 1}), "websudoku", level=1)
    db.upsert_puzzle(_board({(0, 0): 2}), "websudoku", level=2)
    assert db.get_pool_stats(level=1)["total"] == 1
    assert db.get_pool_stats(level=1)["new"] == 1
    assert db.get_pool_stats()["total"] == 2


def test_board_string_roundtrip():
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 5
    board[8][8] = 9
    s = PuzzlePoolDB.board_to_string(board)
    assert len(s) == 81 and s[0] == "5" and s[80] == "9"
    back = PuzzlePoolDB.string_to_board(s)
    assert back[0][0] == 5 and back[8][8] == 9


def test_upsert_retries_on_locked_db(tmp_path, monkeypatch):
    """upsert_puzzle must retry up to 3 times on OperationalError: database is locked."""
    db_path = str(tmp_path / "test.db")
    db = PuzzlePoolDB(db_path)
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1

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

    result = db.upsert_puzzle(board, level=1)
    assert result["inserted"] is True
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
