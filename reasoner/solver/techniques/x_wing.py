"""Technique 10: X-Wing elimination.

Rows variant:
  For some digit d, if exactly two rows each have d as a candidate in
  exactly the same two columns (c1, c2), then d must be placed in one of
  those two rows at c1 and the other at c2 (or vice-versa).  Either way,
  no OTHER row can contain d at column c1 or c2.  Eliminate d from all
  (r, c1) and (r, c2) where r is not one of the two base rows.

Cols variant (symmetric):
  For some digit d, if exactly two columns each have d as a candidate in
  exactly the same two rows (r1, r2), eliminate d from all other cells in
  rows r1 and r2.

Returns the FIRST effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


def find_x_wing_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    # --- Rows variant ---
    for d in range(1, 10):
        # Collect rows where d appears as a candidate in exactly 2 cells
        rows_with_pair: list[tuple[int, tuple[int, int]]] = []
        for r in range(9):
            cols = tuple(
                c for c in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            )
            if len(cols) == 2:
                rows_with_pair.append((r, cols))

        # Find two rows sharing the same column pair
        n = len(rows_with_pair)
        for i in range(n):
            r1, cols1 = rows_with_pair[i]
            for j in range(i + 1, n):
                r2, cols2 = rows_with_pair[j]
                if cols1 != cols2:
                    continue
                c1, c2 = cols1
                # Eliminate d from all other rows in columns c1 and c2
                for r in range(9):
                    if r in (r1, r2):
                        continue
                    for c in (c1, c2):
                        if engine.is_empty(r, c) and d in engine.get_candidates(r, c):
                            return ('eliminate', r, c, d)

    # --- Cols variant ---
    for d in range(1, 10):
        # Collect cols where d appears as a candidate in exactly 2 cells
        cols_with_pair: list[tuple[int, tuple[int, int]]] = []
        for c in range(9):
            rows = tuple(
                r for r in range(9)
                if engine.is_empty(r, c) and d in engine.get_candidates(r, c)
            )
            if len(rows) == 2:
                cols_with_pair.append((c, rows))

        # Find two cols sharing the same row pair
        n = len(cols_with_pair)
        for i in range(n):
            c1, rows1 = cols_with_pair[i]
            for j in range(i + 1, n):
                c2, rows2 = cols_with_pair[j]
                if rows1 != rows2:
                    continue
                r1, r2 = rows1
                # Eliminate d from all other cols in rows r1 and r2
                for c in range(9):
                    if c in (c1, c2):
                        continue
                    for r in (r1, r2):
                        if engine.is_empty(r, c) and d in engine.get_candidates(r, c):
                            return ('eliminate', r, c, d)

    return None
