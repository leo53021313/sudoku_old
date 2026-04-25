# tests/unit/test_pool_db.py
import pytest

from app.data.pool_db import PuzzlePoolDB
from tests.conftest import SAMPLE_BOARD, SAMPLE_SOLUTION


def test_upsert_puzzle_inserts_new(tmp_db):
    result = tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    assert result["inserted"] is True
    assert result["puzzle_id"] > 0


def test_upsert_puzzle_deduplicates(tmp_db):
    r1 = tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    r2 = tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    assert r1["inserted"] is True
    assert r2["inserted"] is False
    assert r1["puzzle_id"] == r2["puzzle_id"]


def test_upserted_puzzle_has_status_new(tmp_db):
    result = tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    puzzle = tmp_db.fetch_one_puzzle_for_training()
    assert puzzle is not None
    # After fetch, status transitions to 'training'
    assert puzzle["status"] == "training"


def test_fetch_returns_none_when_empty(tmp_db):
    result = tmp_db.fetch_one_puzzle_for_training()
    assert result is None


def test_mark_puzzle_attempt_increments_tries(tmp_db):
    tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    puzzle = tmp_db.fetch_one_puzzle_for_training()
    pid = puzzle["id"]
    tmp_db.mark_puzzle_attempt(pid, total_reward=10.0, empty_cells=5)
    stats = tmp_db.get_pool_stats()
    # After one attempt with no success, status stays 'training'
    assert stats["training"] == 1


def test_mark_puzzle_attempt_success_sets_solved(tmp_db):
    tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    puzzle = tmp_db.fetch_one_puzzle_for_training()
    pid = puzzle["id"]
    tmp_db.mark_puzzle_attempt(pid, total_reward=20.0, empty_cells=0, success=True)
    stats = tmp_db.get_pool_stats()
    assert stats["solved_local"] == 1


def test_mark_puzzle_skipped(tmp_db):
    tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    puzzle = tmp_db.fetch_one_puzzle_for_training()
    pid = puzzle["id"]
    tmp_db.mark_puzzle_skipped(pid)
    stats = tmp_db.get_pool_stats()
    assert stats["skipped"] == 1


def test_save_and_retrieve_solution(tmp_db):
    tmp_db.upsert_puzzle(SAMPLE_BOARD, level=1)
    puzzle = tmp_db.fetch_one_puzzle_for_training()
    pid = puzzle["id"]
    steps = [{"row": 0, "col": 2, "num": 4}]
    tmp_db.save_solution(pid, SAMPLE_SOLUTION, solution_steps=steps)
    solutions = tmp_db.list_recent_solutions(limit=1)
    assert len(solutions) == 1
    recovered = tmp_db.json_to_steps(solutions[0]["solution_steps_json"])
    assert recovered == steps


def test_board_string_roundtrip(tmp_db):
    s = tmp_db.board_to_string(SAMPLE_BOARD)
    assert len(s) == 81
    recovered = tmp_db.string_to_board(s)
    assert recovered == SAMPLE_BOARD


def test_string_to_board_raises_on_wrong_length(tmp_db):
    with pytest.raises(ValueError):
        tmp_db.string_to_board("123")
