import json
import os
import tempfile
import numpy as np
from apprentice.data_pkg.pool_db import PuzzlePoolDB
from apprentice.solver.label_puzzles import label_all_puzzles


def _temp_db_path():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    os.remove(path)  # PuzzlePoolDB will create it
    return path


def test_label_all_puzzles_writes_json():
    db_path = _temp_db_path()
    db = PuzzlePoolDB(db_path)
    # Insert one easy puzzle (only one empty cell — naked single)
    easy_solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 0],  # one empty
    ]
    db.upsert_puzzle(easy_solved_board, source='test', level=1)
    db.close()

    out_path = _temp_db_path() + '.json'
    label_all_puzzles(db_path=db_path, out_path=out_path)

    assert os.path.exists(out_path)
    with open(out_path) as f:
        labels = json.load(f)
    assert len(labels) == 1
    # Single naked single → max_tech == 1
    assert next(iter(labels.values())) == 1
    os.remove(db_path)
    os.remove(out_path)


def test_label_all_puzzles_handles_unsolvable():
    db_path = _temp_db_path()
    db = PuzzlePoolDB(db_path)
    # Empty board: solver can't make any move → max_tech = -1
    empty_board = [[0]*9 for _ in range(9)]
    db.upsert_puzzle(empty_board, source='test', level=1)
    db.close()

    out_path = _temp_db_path() + '.json'
    label_all_puzzles(db_path=db_path, out_path=out_path)

    with open(out_path) as f:
        labels = json.load(f)
    assert next(iter(labels.values())) == -1
    os.remove(db_path)
    os.remove(out_path)
