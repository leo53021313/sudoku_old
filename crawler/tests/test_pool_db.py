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
