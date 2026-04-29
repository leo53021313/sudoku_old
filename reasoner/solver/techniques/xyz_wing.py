"""Technique 13: XYZ-Wing elimination.

Like XY-Wing but the pivot has THREE candidates {x, y, z}, and the two wings
are bivalue cells {x, z} and {y, z}, both peers of the pivot.  Because the
pivot itself can be z, a target cell must see ALL THREE cells (pivot, wing1,
wing2) — not just the two wings — for z to be eliminated.

Why it works: one of {pivot, wing1, wing2} must be z.
  - If pivot ≠ x → wing1 = z  (wing1 can only be x or z)
  - If pivot ≠ y → wing2 = z  (wing2 can only be y or z)
  - If pivot = z → pivot is z
So in every case z is "used" somewhere in the triple.  A cell seeing all
three cannot be z.

Returns the first effective ('eliminate', r, c, v) action, or None.
"""

from __future__ import annotations
from reasoner.solver.candidate_engine import CandidateEngine


def _are_peers(r1: int, c1: int, r2: int, c2: int) -> bool:
    """True iff two distinct cells share a row, column, or 3×3 box."""
    if (r1, c1) == (r2, c2):
        return False
    if r1 == r2 or c1 == c2:
        return True
    return (r1 // 3 == r2 // 3) and (c1 // 3 == c2 // 3)


def justifies_xyz_wing(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does XYZ-Wing reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and there exist P={x,y,z} (trivalue), W1={x,z}, W2={y,z}
    (bivalue) with v==z, W1 and W2 peers of P, and (r,c) a peer of P, W1, W2.
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    trivalues: list[tuple[int, int, set[int]]] = []
    bivalues: list[tuple[int, int, set[int]]] = []
    for rr in range(9):
        for cc in range(9):
            if engine.is_empty(rr, cc):
                cands = engine.get_candidates(rr, cc)
                if len(cands) == 3:
                    trivalues.append((rr, cc, cands))
                elif len(cands) == 2:
                    bivalues.append((rr, cc, cands))

    for (pr, pc, pcands) in trivalues:
        for z in pcands:
            if z != v:
                continue
            xy = pcands - {z}
            x, y = sorted(xy)
            for (w1r, w1c, w1cands) in bivalues:
                if (w1r, w1c) == (pr, pc):
                    continue
                if not _are_peers(pr, pc, w1r, w1c):
                    continue
                if w1cands != {x, z}:
                    continue
                for (w2r, w2c, w2cands) in bivalues:
                    if (w2r, w2c) in [(pr, pc), (w1r, w1c)]:
                        continue
                    if not _are_peers(pr, pc, w2r, w2c):
                        continue
                    if w2cands != {y, z}:
                        continue
                    # (r, c) must see ALL THREE, not be any of them
                    if (r, c) in [(pr, pc), (w1r, w1c), (w2r, w2c)]:
                        continue
                    if (_are_peers(r, c, pr, pc) and
                            _are_peers(r, c, w1r, w1c) and
                            _are_peers(r, c, w2r, w2c)):
                        return True
    return False


def find_xyz_wing_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    trivalues: list[tuple[int, int, set[int]]] = []
    bivalues: list[tuple[int, int, set[int]]] = []
    for r in range(9):
        for c in range(9):
            if engine.is_empty(r, c):
                cands = engine.get_candidates(r, c)
                if len(cands) == 3:
                    trivalues.append((r, c, cands))
                elif len(cands) == 2:
                    bivalues.append((r, c, cands))

    for (pr, pc, pcands) in trivalues:
        # Try each digit z as the shared elimination digit
        for z in pcands:
            xy = pcands - {z}
            x, y = sorted(xy)
            # Wing1: bivalue {x, z}, peer of pivot
            for (w1r, w1c, w1cands) in bivalues:
                if (w1r, w1c) == (pr, pc):
                    continue
                if not _are_peers(pr, pc, w1r, w1c):
                    continue
                if w1cands != {x, z}:
                    continue
                # Wing2: bivalue {y, z}, peer of pivot, distinct from wing1
                for (w2r, w2c, w2cands) in bivalues:
                    if (w2r, w2c) in [(pr, pc), (w1r, w1c)]:
                        continue
                    if not _are_peers(pr, pc, w2r, w2c):
                        continue
                    if w2cands != {y, z}:
                        continue
                    # Found XYZ-Wing — eliminate z from cells seeing ALL THREE
                    for r in range(9):
                        for c in range(9):
                            if (r, c) in [(pr, pc), (w1r, w1c), (w2r, w2c)]:
                                continue
                            if not engine.is_empty(r, c):
                                continue
                            if z not in engine.get_candidates(r, c):
                                continue
                            if (_are_peers(r, c, pr, pc) and
                                    _are_peers(r, c, w1r, w1c) and
                                    _are_peers(r, c, w2r, w2c)):
                                return ('eliminate', r, c, z)
    return None
