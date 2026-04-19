# app/data/pool_db.py
# -*- coding: utf-8 -*-
"""
SQLite 題庫管理：
  puzzles   - 題目池
  solutions - 解答池
"""

import os
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PuzzlePoolDB:

    def __init__(self, db_path="data/puzzle_pool.db"):
        self.db_path = db_path
        self._local  = threading.local()

        folder = os.path.dirname(db_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        self._init_db()

    # ---------------------------------------------------------------
    # Connection
    # ---------------------------------------------------------------
    def _get_conn(self):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = conn
        return conn

    @contextmanager
    def transaction(self):
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _init_db(self):
        with self.transaction() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS puzzles (
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

            conn.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                puzzle_id            INTEGER NOT NULL UNIQUE,
                solution             TEXT    NOT NULL,
                solution_steps_json  TEXT    DEFAULT NULL,
                verified_local       INTEGER NOT NULL DEFAULT 0,
                verify_status        TEXT    DEFAULT NULL,
                created_at           TEXT    NOT NULL,
                verified_at          TEXT    DEFAULT NULL,
                FOREIGN KEY (puzzle_id) REFERENCES puzzles(id) ON DELETE CASCADE
            );
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_puzzles_status ON puzzles(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_puzzles_status_tries ON puzzles(status, tries, best_empty, id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_puzzles_created_at ON puzzles(created_at);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_solutions_verified ON solutions(verified_local);")

    # ---------------------------------------------------------------
    # Static helpers
    # ---------------------------------------------------------------
    @staticmethod
    def board_to_string(board):
        return "".join(str(int(board[r][c])) for r in range(9) for c in range(9))

    @staticmethod
    def string_to_board(s):
        if s is None or len(s) != 81:
            raise ValueError(f"board string 長度錯誤：{len(s) if s else 'None'}")
        return [[int(s[r*9+c]) for c in range(9)] for r in range(9)]

    @staticmethod
    def steps_to_json(steps):
        return json.dumps(steps, ensure_ascii=False)

    @staticmethod
    def json_to_steps(s):
        return json.loads(s) if s else []

    # ---------------------------------------------------------------
    # Puzzle management
    # ---------------------------------------------------------------
    def upsert_puzzle(self, board, source="websudoku"):
        puzzle     = self.board_to_string(board)
        givens     = sum(1 for ch in puzzle if ch != "0")
        puzzle_key = puzzle
        now        = now_str()

        with self.transaction() as conn:
            row = conn.execute(
                "SELECT id FROM puzzles WHERE puzzle_key = ?", (puzzle_key,)
            ).fetchone()

            if row:
                return {"inserted": False, "puzzle_id": int(row["id"]), "puzzle_key": puzzle_key}

            cur = conn.execute("""
                INSERT INTO puzzles
                    (puzzle_key, puzzle, givens, source, status,
                     tries, best_empty, best_reward, last_reward, last_empty,
                     locked_by, locked_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'new', 0, 81, 0, 0, 81, NULL, NULL, ?, ?)
            """, (puzzle_key, puzzle, givens, source, now, now))

            return {"inserted": True, "puzzle_id": int(cur.lastrowid), "puzzle_key": puzzle_key}

    def get_pool_stats(self):
        with self.transaction() as conn:
            def count(q, *a):
                return int(conn.execute(q, a).fetchone()[0])

            return {
                "total":          count("SELECT COUNT(*) FROM puzzles"),
                "new":            count("SELECT COUNT(*) FROM puzzles WHERE status='new'"),
                "training":       count("SELECT COUNT(*) FROM puzzles WHERE status='training'"),
                "solved_local":   count("SELECT COUNT(*) FROM puzzles WHERE status='solved_local'"),
                "skipped":        count("SELECT COUNT(*) FROM puzzles WHERE status='skipped'"),
                "verified_local": count("SELECT COUNT(*) FROM solutions WHERE verified_local=1"),
            }

    def count_unsolved(self, max_tries=None):
        with self.transaction() as conn:
            if max_tries is None:
                row = conn.execute("""
                    SELECT COUNT(*) FROM puzzles WHERE status IN ('new','training')
                """).fetchone()
            else:
                row = conn.execute("""
                    SELECT COUNT(*) FROM puzzles
                    WHERE status IN ('new','training') AND tries < ?
                """, (int(max_tries),)).fetchone()
            return int(row[0])

    def fetch_one_puzzle_for_training(self, worker_name="trainer", max_tries=None):
        now = now_str()
        with self.transaction() as conn:
            if max_tries is None:
                row = conn.execute("""
                    SELECT * FROM puzzles
                    WHERE status IN ('new','training')
                    ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END,
                             tries ASC, best_empty ASC, id ASC
                    LIMIT 1
                """).fetchone()
            else:
                row = conn.execute("""
                    SELECT * FROM puzzles
                    WHERE status IN ('new','training') AND tries < ?
                    ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END,
                             tries ASC, best_empty ASC, id ASC
                    LIMIT 1
                """, (int(max_tries),)).fetchone()

            if row is None:
                return None

            conn.execute("""
                UPDATE puzzles SET status='training', locked_by=?, locked_at=?, updated_at=?
                WHERE id=?
            """, (worker_name, now, now, row["id"]))

            return dict(conn.execute("SELECT * FROM puzzles WHERE id=?", (row["id"],)).fetchone())

    def mark_puzzle_attempt(self, puzzle_id, total_reward, empty_cells, success=False):
        now = now_str()
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM puzzles WHERE id=?", (puzzle_id,)).fetchone()
            if row is None:
                raise ValueError(f"找不到 puzzle_id={puzzle_id}")

            conn.execute("""
                UPDATE puzzles
                SET tries       = tries + 1,
                    best_empty  = MIN(best_empty, ?),
                    best_reward = MAX(best_reward, ?),
                    last_reward = ?,
                    last_empty  = ?,
                    status      = ?,
                    updated_at  = ?
                WHERE id = ?
            """, (
                int(empty_cells), float(total_reward),
                float(total_reward), int(empty_cells),
                "solved_local" if success else "training",
                now, puzzle_id,
            ))

    def mark_puzzle_skipped(self, puzzle_id):
        with self.transaction() as conn:
            conn.execute(
                "UPDATE puzzles SET status='skipped', updated_at=? WHERE id=?",
                (now_str(), int(puzzle_id)),
            )

    def save_solution(self, puzzle_id, solved_board, solution_steps=None,
                      verified_local=False, verify_status=None):
        solution_str = self.board_to_string(solved_board)
        steps_json   = self.steps_to_json(solution_steps or [])
        now          = now_str()

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO solutions
                    (puzzle_id, solution, solution_steps_json,
                     verified_local, verify_status, created_at, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(puzzle_id) DO UPDATE SET
                    solution             = excluded.solution,
                    solution_steps_json  = excluded.solution_steps_json,
                    verified_local       = excluded.verified_local,
                    verify_status        = excluded.verify_status,
                    created_at           = excluded.created_at,
                    verified_at          = excluded.verified_at
            """, (
                puzzle_id, solution_str, steps_json,
                1 if verified_local else 0, verify_status,
                now, now if verified_local else None,
            ))

            conn.execute("""
                UPDATE puzzles SET status=?, updated_at=? WHERE id=?
            """, ("solved_local" if verified_local else "training", now, puzzle_id))

    def list_recent_puzzles(self, limit=20):
        with self.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM puzzles ORDER BY id DESC LIMIT ?", (int(limit),)
            ).fetchall()
            return [dict(r) for r in rows]

    def list_recent_solutions(self, limit=20):
        with self.transaction() as conn:
            rows = conn.execute("""
                SELECT s.*, p.puzzle, p.givens, p.status
                FROM solutions s JOIN puzzles p ON p.id = s.puzzle_id
                ORDER BY s.id DESC LIMIT ?
            """, (int(limit),)).fetchall()
            return [dict(r) for r in rows]
