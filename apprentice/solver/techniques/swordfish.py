"""Technique 11: Swordfish elimination.

Rows variant:
  For some digit d, find three distinct rows r1, r2, r3 such that:
  - Each row has d as a candidate in 2 or 3 cells.
  - The union of those column positions across the three rows has exactly
    3 distinct columns {c1, c2, c3}.

  Because d must be placed in each of those three columns exactly once
  (across the three rows), no OTHER row can contain d at c1, c2, or c3.
  Eliminate d from (r, ck) for r ∉ {r1, r2, r3}, k ∈ {1, 2, 3}.

Cols variant (symmetric):
  Three columns whose d-candidate row positions union to exactly 3 rows.
  Eliminate d from cells (rk, c) for c ∉ {c1, c2, c3}, k ∈ {1, 2, 3}.

Returns the FIRST effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from itertools import combinations
from apprentice.solver.candidate_engine import CandidateEngine


def find_swordfish_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    # --- Rows variant ---
    for d in range(1, 10):
        # Collect rows where d appears in 2 or 3 cells
        rows_with_few: list[tuple[int, set[int]]] = []
        for r in range(9):
            cols = {
                c for c in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            }
            if 2 <= len(cols) <= 3:
                rows_with_few.append((r, cols))

        # Try all combinations of 3 qualifying rows
        for (r1, s1), (r2, s2), (r3, s3) in combinations(rows_with_few, 3):
            union = s1 | s2 | s3
            if len(union) != 3:
                continue
            target_cols = list(union)
            # Eliminate d from other rows in the target columns
            for r in range(9):
                if r in (r1, r2, r3):
                    continue
                for c in target_cols:
                    if engine.is_empty(r, c) and d in engine.get_candidates(r, c):
                        return ('eliminate', r, c, d)

    # --- Cols variant ---
    for d in range(1, 10):
        # Collect cols where d appears in 2 or 3 cells
        cols_with_few: list[tuple[int, set[int]]] = []
        for c in range(9):
            rows = {
                r for r in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            }
            if 2 <= len(rows) <= 3:
                cols_with_few.append((c, rows))

        # Try all combinations of 3 qualifying cols
        for (c1, s1), (c2, s2), (c3, s3) in combinations(cols_with_few, 3):
            union = s1 | s2 | s3
            if len(union) != 3:
                continue
            target_rows = list(union)
            # Eliminate d from other cols in the target rows
            for c in range(9):
                if c in (c1, c2, c3):
                    continue
                for r in target_rows:
                    if engine.is_empty(r, c) and d in engine.get_candidates(r, c):
                        return ('eliminate', r, c, d)

    return None


def justifies_swordfish(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does swordfish reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and either:
    - Rows variant: 3 rows each have v's candidates in 2-3 cells whose union
      of columns is exactly 3 cols {c1,c2,c3}; r ∉ those rows, c ∈ {c1,c2,c3}
    - Cols variant: symmetric.
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    # Rows variant
    rows_with_few: list[tuple[int, set[int]]] = []
    for row in range(9):
        cols = {
            cc for cc in range(9)
            if engine.is_empty(row, cc) and v in engine.get_candidates(row, cc)
        }
        if 2 <= len(cols) <= 3:
            rows_with_few.append((row, cols))

    for (r1, s1), (r2, s2), (r3, s3) in combinations(rows_with_few, 3):
        union = s1 | s2 | s3
        if len(union) != 3:
            continue
        if r not in (r1, r2, r3) and c in union:
            return True

    # Cols variant
    cols_with_few: list[tuple[int, set[int]]] = []
    for col in range(9):
        rows = {
            rr for rr in range(9)
            if engine.is_empty(rr, col) and v in engine.get_candidates(rr, col)
        }
        if 2 <= len(rows) <= 3:
            cols_with_few.append((col, rows))

    for (c1, s1), (c2, s2), (c3, s3) in combinations(cols_with_few, 3):
        union = s1 | s2 | s3
        if len(union) != 3:
            continue
        if c not in (c1, c2, c3) and r in union:
            return True

    return False
