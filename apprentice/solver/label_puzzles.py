"""One-shot script: label every puzzle in DB by max technique id needed.

Output: JSON file mapping {str(puzzle_id): int} where int is:
  -1 → v1 solver couldn't solve (Stage 3 bucket)
   1..7 → highest technique needed during solve

Usage:
  python -m apprentice.solver.label_puzzles \\
      --db data/puzzle_pool.db \\
      --out reasoner/data/puzzle_techniques.json --verbose
"""

from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from apprentice.data_pkg.pool_db import PuzzlePoolDB
from apprentice.solver.human_solver import HumanSolver


def label_all_puzzles(db_path: str, out_path: str, verbose: bool = False) -> dict[str, int]:
    db = PuzzlePoolDB(db_path)
    solver = HumanSolver()
    labels: dict[str, int] = {}

    with db.transaction() as conn:
        rows = conn.execute("SELECT id, puzzle FROM puzzles").fetchall()

    if verbose:
        print(f"[label_puzzles] {len(rows)} puzzles to label", flush=True)

    for i, row in enumerate(rows):
        puzzle_id = int(row['id'])
        puzzle_str = row['puzzle']
        board_list = PuzzlePoolDB.string_to_board(puzzle_str)
        board = np.array(board_list, dtype=np.int8)
        _final, max_tech, _solved = solver.solve_to_completion(board)
        labels[str(puzzle_id)] = int(max_tech)
        if verbose and i % 1000 == 0 and i > 0:
            print(f"[label_puzzles] {i}/{len(rows)} done", flush=True)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(labels, f, indent=2)

    if verbose:
        dist = Counter(labels.values())
        print(f"[label_puzzles] Technique distribution:")
        for k in sorted(dist):
            print(f"  max_tech={k}: {dist[k]}", flush=True)

    db.close()
    return labels


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--db', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--verbose', action='store_true')
    args = p.parse_args()
    label_all_puzzles(args.db, args.out, verbose=args.verbose)


if __name__ == '__main__':
    main()
