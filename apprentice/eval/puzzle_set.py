from __future__ import annotations

import json
import os
import threading
from datetime import date

import numpy as np

from apprentice.data_pkg.pool_db import PuzzlePoolDB
from apprentice.solver_ext.backtracking import solve


class EvalPuzzleSet:
    """
    Manages a fixed set of eval puzzles stored in a JSON file.

    Parameters
    ----------
    json_path : str
        Path to the JSON file (auto-created if missing).
    db_path : str
        SQLite database path (only used if JSON must be populated).
    n_per_difficulty : int
        Number of puzzles per difficulty to sample when populating.
    """

    def __init__(
        self,
        json_path: str = "data/eval_puzzles.json",
        db_path: str = "../data/puzzle_pool.db",
        n_per_difficulty: int = 50,
    ) -> None:
        self._json_path = json_path
        self._db_path = db_path
        self._n = n_per_difficulty
        self._data: dict | None = None
        self._lock = threading.Lock()

    def get_puzzles(self, difficulty: int) -> list[tuple[np.ndarray, np.ndarray]]:
        """Return list of (board 9x9, solution 9x9) for the given difficulty."""
        data = self._load_or_create()
        entries = data["puzzles"].get(str(difficulty), [])
        result = []
        for entry in entries:
            board = np.array(
                PuzzlePoolDB.string_to_board(entry["puzzle"]), dtype=np.int8
            )
            sol = solve(board)
            if sol is not None:
                result.append((board, sol))
        return result

    def _load_or_create(self) -> dict:
        with self._lock:
            if self._data is not None:
                return self._data
            if os.path.exists(self._json_path):
                try:
                    with open(self._json_path, encoding="utf-8") as f:
                        self._data = json.load(f)
                    total = sum(len(v) for v in self._data["puzzles"].values())
                    print(f"[EvalPuzzleSet] Loaded {total} reserved puzzles from {self._json_path}")
                except (json.JSONDecodeError, KeyError):
                    print(f"[EvalPuzzleSet] Warning: {self._json_path} is malformed, regenerating.")
                    self._populate()
            else:
                self._populate()
        return self._data

    def _populate(self) -> None:
        db = PuzzlePoolDB(self._db_path)
        puzzles: dict[str, list] = {}
        for level in [1, 2, 3, 4]:
            rows = db.fetch_random_puzzles(level=level, n=self._n)
            puzzles[str(level)] = [{"puzzle": r["puzzle"]} for r in rows]

        self._data = {
            "created": str(date.today()),
            "n_per_difficulty": self._n,
            "puzzles": puzzles,
        }

        os.makedirs(os.path.dirname(self._json_path) or ".", exist_ok=True)
        with open(self._json_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

        total = sum(len(v) for v in puzzles.values())
        print(f"[EvalPuzzleSet] Reserved set created: {total} puzzles -> {self._json_path}")
