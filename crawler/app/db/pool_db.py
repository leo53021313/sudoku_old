# app/db/pool_db.py  (crawler-only subset: upsert + stats)
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
