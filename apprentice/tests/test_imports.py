"""Smoke test: every reusable module imports cleanly under reasoner/."""

def test_pool_db_imports():
    from apprentice.data_pkg.pool_db import PuzzlePoolDB
    assert PuzzlePoolDB is not None

def test_backtracking_imports():
    from apprentice.solver_ext.backtracking import solve
    assert solve is not None

def test_features_extractor_imports():
    from apprentice.model.features_extractor import SudokuFeaturesExtractor
    assert SudokuFeaturesExtractor is not None

def test_puzzle_set_imports():
    from apprentice.eval.puzzle_set import EvalPuzzleSet
    assert EvalPuzzleSet is not None
