# sb3/tests/test_pool_db_fetcher.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from collections import Counter
from app.data.pool_db import PuzzlePoolDB


def _seed_db(tmp_path, n_per_level=20):
    """Build a tiny test DB with N puzzles per difficulty in 'training' status,
    each with a distinct best_empty value to expose biased ordering."""
    db = PuzzlePoolDB(str(tmp_path / "test.db"))
    # Direct insert: vary best_empty so OLD ORDER BY would always pick the same one
    with db.transaction() as conn:
        counter = 0
        for level in (1, 2, 3, 4):
            for i in range(n_per_level):
                # Create a unique puzzle for each puzzle.
                # Use counter to ensure global uniqueness.
                puzzle_str = str(counter % 10) * 80 + str(counter // 10 % 10)
                counter += 1
                # puzzle_key is just the puzzle string
                conn.execute(
                    "INSERT INTO puzzles (puzzle_key, puzzle, givens, level, status, tries, best_empty, created_at, updated_at)"
                    " VALUES (?, ?, 45, ?, 'training', 0, ?, datetime('now'), datetime('now'))",
                    (puzzle_str, puzzle_str, level, i),
                )
    return db


def test_fetcher_returns_diverse_puzzles_within_status_group(tmp_path):
    """100 fetches of L1 'training' puzzles should hit diverse rows, not the
    same lowest-best_empty row every time. Verifies ORDER BY RANDOM() is used."""
    db = _seed_db(tmp_path, n_per_level=20)
    seen_ids = []
    for _ in range(100):
        # Fetch and undo the lock so subsequent fetches see same rows
        row = db.fetch_one_puzzle_for_training(level=1)
        assert row is not None, "DB has 20 L1 puzzles, fetch should never return None"
        seen_ids.append(row["id"])
        with db.transaction() as conn:
            conn.execute(
                "UPDATE puzzles SET status='training' WHERE id=?",
                (row["id"],),
            )

    counts = Counter(seen_ids)
    # With true RANDOM() and 20 puzzles, no single id should dominate
    most_common_id, most_common_n = counts.most_common(1)[0]
    assert most_common_n < 30, (
        f"Expected diverse fetches, got id={most_common_id} {most_common_n}/100 "
        f"times -- ORDER BY RANDOM() not in effect"
    )
    # Should have hit at least half the puzzles
    assert len(counts) >= 10, (
        f"Only {len(counts)} unique puzzles fetched in 100 attempts -- "
        f"sampling not diverse enough"
    )


def test_fetcher_still_prefers_new_status(tmp_path):
    """'new' status puzzles should be exhausted before 'training' ones."""
    db = PuzzlePoolDB(str(tmp_path / "test2.db"))
    with db.transaction() as conn:
        # 5 'new' L1 puzzles + 5 'training' L1 puzzles (each puzzle unique)
        for i in range(5):
            puzzle = "1" * 80 + str(i)  # Unique: ends with 0-4
            conn.execute(
                "INSERT INTO puzzles (puzzle_key, puzzle, givens, level, status, tries, best_empty, created_at, updated_at)"
                " VALUES (?, ?, 45, 1, 'new', 0, 0, datetime('now'), datetime('now'))",
                (puzzle, puzzle),
            )
        for i in range(5):
            puzzle = "2" * 80 + str(i)  # Unique: ends with 0-4
            conn.execute(
                "INSERT INTO puzzles (puzzle_key, puzzle, givens, level, status, tries, best_empty, created_at, updated_at)"
                " VALUES (?, ?, 45, 1, 'training', 0, 0, datetime('now'), datetime('now'))",
                (puzzle, puzzle),
            )

    # First 5 fetches should all start as 'new' (and be marked 'training' afterward)
    new_count = 0
    for _ in range(5):
        row = db.fetch_one_puzzle_for_training(level=1)
        assert row is not None
        # The first character of puzzle indicates which group: '1' = was 'new', '2' = was 'training'
        if row["puzzle"][0] == "1":
            new_count += 1
    assert new_count == 5, (
        f"Expected first 5 fetches to drain the 'new' pool first, got {new_count}/5"
    )
