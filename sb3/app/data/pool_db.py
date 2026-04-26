# app/data/pool_db.py
# -*- coding: utf-8 -*-
"""
SQLite 題庫管理：
  puzzles   - 題目池（含難度等級 level）
  solutions - 解答池
"""

from __future__ import annotations

import os
import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PuzzlePoolDB:

    def __init__(self, db_path="data/puzzle_pool.db"):
        self.db_path = db_path
        self._local = threading.local()

        folder = os.path.dirname(db_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        self._init_db()

    # ── Connection ──────────────────────────────────────────────────────────

    def _get_conn(self):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
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
                level       INTEGER NOT NULL DEFAULT 1,
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

            # 舊資料庫遷移：必須在建立 level 索引之前確保欄位存在
            try:
                conn.execute(
                    "ALTER TABLE puzzles"
                    " ADD COLUMN level INTEGER NOT NULL DEFAULT 1"
                )
            except sqlite3.OperationalError:
                pass  # 欄位已存在（新建 DB 或已遷移過），略過

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
                FOREIGN KEY (puzzle_id) REFERENCES puzzles(id)
                    ON DELETE CASCADE
            );
            """)

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_puzzles_status"
                " ON puzzles(status);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_puzzles_status_tries"
                " ON puzzles(status, tries, best_empty, id);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_puzzles_level"
                " ON puzzles(level, status);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_puzzles_created_at"
                " ON puzzles(created_at);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_solutions_verified"
                " ON solutions(verified_local);"
            )

    # ── Static helpers ──────────────────────────────────────────────────────

    @staticmethod
    def board_to_string(board):
        return "".join(
            str(int(board[r][c])) for r in range(9) for c in range(9)
        )

    @staticmethod
    def string_to_board(s):
        if s is None or len(s) != 81:
            raise ValueError(
                f"board string 長度錯誤：{len(s) if s else 'None'}"
            )
        return [[int(s[r * 9 + c]) for c in range(9)] for r in range(9)]

    @staticmethod
    def steps_to_json(steps):
        return json.dumps(steps, ensure_ascii=False)

    @staticmethod
    def json_to_steps(s):
        return json.loads(s) if s else []

    # ── Puzzle management ───────────────────────────────────────────────────

    def upsert_puzzle(self, board: List[List[int]], source: str = "websudoku", level: int = 1) -> Dict[str, Any]:
        """
        插入新題目；若已存在（puzzle_key 相同）則略過。
        level：難度等級，1=easy, 2=medium, 3=hard, 4=evil。
        """
        puzzle = self.board_to_string(board)
        givens = sum(1 for ch in puzzle if ch != "0")
        puzzle_key = puzzle
        now = now_str()

        with self.transaction() as conn:
            row = conn.execute(
                "SELECT id FROM puzzles WHERE puzzle_key = ?", (puzzle_key,)
            ).fetchone()

            if row:
                return {
                    "inserted":   False,
                    "puzzle_id":  int(row["id"]),
                    "puzzle_key": puzzle_key,
                }

            init_empty = 81 - givens
            cur = conn.execute("""
                INSERT INTO puzzles
                    (puzzle_key, puzzle, givens, level, source, status,
                     tries, best_empty, best_reward, last_reward, last_empty,
                     locked_by, locked_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'new', 0, ?, 0, 0, ?,
                        NULL, NULL, ?, ?)
            """, (puzzle_key, puzzle, givens, int(level), source,
                  init_empty, init_empty, now, now))

            return {
                "inserted":   True,
                "puzzle_id":  int(cur.lastrowid),
                "puzzle_key": puzzle_key,
            }

    def get_pool_stats(self, level=None):
        """
        回傳題庫統計。
        level：若指定則只統計該難度；None 表示全部難度合計。
        """
        with self.transaction() as conn:
            def count(q, *a):
                return int(conn.execute(q, a).fetchone()[0])

            if level is None:
                return {
                    "total":          count("SELECT COUNT(*) FROM puzzles"),
                    "new":            count(
                        "SELECT COUNT(*) FROM puzzles WHERE status='new'"
                    ),
                    "training":       count(
                        "SELECT COUNT(*) FROM puzzles WHERE status='training'"
                    ),
                    "solved_local":   count(
                        "SELECT COUNT(*) FROM puzzles"
                        " WHERE status='solved_local'"
                    ),
                    "skipped":        count(
                        "SELECT COUNT(*) FROM puzzles WHERE status='skipped'"
                    ),
                    "verified_local": count(
                        "SELECT COUNT(*) FROM solutions WHERE verified_local=1"
                    ),
                }
            else:
                return {
                    "total":        count(
                        "SELECT COUNT(*) FROM puzzles WHERE level=?", level
                    ),
                    "new":          count(
                        "SELECT COUNT(*) FROM puzzles"
                        " WHERE status='new' AND level=?", level
                    ),
                    "training":     count(
                        "SELECT COUNT(*) FROM puzzles"
                        " WHERE status='training' AND level=?", level
                    ),
                    "solved_local": count(
                        "SELECT COUNT(*) FROM puzzles"
                        " WHERE status='solved_local' AND level=?", level
                    ),
                    "skipped":      count(
                        "SELECT COUNT(*) FROM puzzles"
                        " WHERE status='skipped' AND level=?", level
                    ),
                }

    def count_unsolved(self, max_tries=None, level=None):
        """
        回傳可供訓練的未解題數（status 為 'new' 或 'training'）。
        level：若指定則只計算該難度。
        """
        with self.transaction() as conn:
            level_clause = "AND level=?" if level is not None else ""
            tries_clause = "AND tries < ?" if max_tries is not None else ""

            args = []
            if level is not None:
                args.append(int(level))
            if max_tries is not None:
                args.append(int(max_tries))

            row = conn.execute(
                f"SELECT COUNT(*) FROM puzzles"
                f" WHERE status IN ('new','training')"
                f" {level_clause} {tries_clause}",
                args,
            ).fetchone()
            return int(row[0])

    def fetch_one_puzzle_for_training(
        self,
        worker_name: str = "trainer",
        max_tries: Optional[int] = None,
        level: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        取出一道可訓練題目並鎖定（status → 'training'）。
        level：若指定則只取該難度的題目（擴充介面）。
        """
        now = now_str()

        level_clause = "AND level=?" if level is not None else ""
        tries_clause = "AND tries < ?" if max_tries is not None else ""

        args = []
        if level is not None:
            args.append(int(level))
        if max_tries is not None:
            args.append(int(max_tries))

        with self.transaction() as conn:
            row = conn.execute(
                f"SELECT * FROM puzzles"
                f" WHERE status IN ('new','training')"
                f" {level_clause} {tries_clause}"
                f" ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END,"
                f"          tries ASC, best_empty ASC, id ASC"
                f" LIMIT 1",
                args,
            ).fetchone()

            if row is None:
                return None

            conn.execute("""
                UPDATE puzzles
                SET status='training', locked_by=?, locked_at=?, updated_at=?
                WHERE id=?
            """, (worker_name, now, now, row["id"]))

            return dict(
                conn.execute(
                    "SELECT * FROM puzzles WHERE id=?", (row["id"],)
                ).fetchone()
            )

    def fetch_random_puzzles(
        self,
        level: int,
        n: int,
    ) -> list[dict]:
        """Read-only random sample of N puzzles for eval (no status locking)."""
        with self.transaction() as conn:
            rows = conn.execute(
                "SELECT puzzle FROM puzzles"
                " WHERE level=?"
                " ORDER BY RANDOM()"
                " LIMIT ?",
                (int(level), int(n)),
            ).fetchall()
        return [dict(r) for r in rows]

    def mark_puzzle_attempt(
        self,
        puzzle_id: int,
        total_reward: float,
        empty_cells: int,
        success: bool = False,
    ) -> None:
        now = now_str()
        with self.transaction() as conn:
            row = conn.execute(
                "SELECT * FROM puzzles WHERE id=?", (puzzle_id,)
            ).fetchone()
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
                    locked_by   = NULL,
                    locked_at   = NULL,
                    updated_at  = ?
                WHERE id = ?
            """, (
                int(empty_cells), float(total_reward),
                float(total_reward), int(empty_cells),
                "solved_local" if success else "training",
                now, puzzle_id,
            ))

    def mark_puzzle_skipped(self, puzzle_id: int) -> None:
        with self.transaction() as conn:
            conn.execute(
                "UPDATE puzzles SET status='skipped', updated_at=? WHERE id=?",
                (now_str(), int(puzzle_id)),
            )

    def save_solution(
        self, puzzle_id, solved_board, solution_steps=None,
        verified_local=False, verify_status=None
    ):
        solution_str = self.board_to_string(solved_board)
        steps_json = self.steps_to_json(solution_steps or [])
        now = now_str()

        with self.transaction() as conn:
            conn.execute("""
                INSERT INTO solutions
                    (puzzle_id, solution, solution_steps_json,
                     verified_local, verify_status, created_at, verified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(puzzle_id) DO UPDATE SET
                    solution            = excluded.solution,
                    solution_steps_json = excluded.solution_steps_json,
                    verified_local      = excluded.verified_local,
                    verify_status       = excluded.verify_status,
                    created_at          = excluded.created_at,
                    verified_at         = excluded.verified_at
            """, (
                puzzle_id, solution_str, steps_json,
                1 if verified_local else 0, verify_status,
                now, now if verified_local else None,
            ))

            conn.execute("""
                UPDATE puzzles SET status=?, updated_at=? WHERE id=?
            """, (
                "solved_local" if verified_local else "training",
                now, puzzle_id,
            ))

    def list_recent_puzzles(self, limit=20):
        with self.transaction() as conn:
            rows = conn.execute(
                "SELECT * FROM puzzles ORDER BY id DESC LIMIT ?", (int(limit),)
            ).fetchall()
            return [dict(r) for r in rows]

    def list_recent_solutions(self, limit=20):
        with self.transaction() as conn:
            rows = conn.execute("""
                SELECT s.*, p.puzzle, p.givens, p.status, p.level
                FROM solutions s JOIN puzzles p ON p.id = s.puzzle_id
                ORDER BY s.id DESC LIMIT ?
            """, (int(limit),)).fetchall()
            return [dict(r) for r in rows]
