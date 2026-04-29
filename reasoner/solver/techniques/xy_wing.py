"""Technique 12: XY-Wing elimination.

Find a pivot bivalue cell P={x,y}, two wing bivalue cells W1={x,z} and
W2={y,z} that are both peers of P.  Any empty cell that is a peer of BOTH
W1 and W2 (and is not P, W1, or W2) cannot be z → eliminate z from it.

Why it works: whatever value P takes, one of the wings must hold z.
  - P=x → W1 cannot be x, so W1=z
  - P=y → W2 cannot be y, so W2=z
Hence z is always present in at least one of {W1, W2}, so any cell seeing
both wings is never z.

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


def justifies_xy_wing(
    engine: CandidateEngine,
    action: tuple[str, int, int, int],
) -> bool:
    """Does XY-Wing reasoning justify the given action?

    True iff action is ('eliminate', r, c, v) where (r, c) is empty and v is a
    candidate, and there exist P={x,y}, W1={x,z}, W2={y,z} (all bivalue) with
    v==z, W1 and W2 peers of P, and (r,c) a peer of both W1 and W2.
    """
    op, r, c, v = action
    if op != 'eliminate':
        return False
    if not engine.is_empty(r, c):
        return False
    if v not in engine.get_candidates(r, c):
        return False

    # Collect all bivalue cells
    bivalues: list[tuple[int, int, set[int]]] = []
    for rr in range(9):
        for cc in range(9):
            if engine.is_empty(rr, cc):
                cands = engine.get_candidates(rr, cc)
                if len(cands) == 2:
                    bivalues.append((rr, cc, cands))

    for (pr, pc, pcands) in bivalues:
        x, y = sorted(pcands)
        for (w1r, w1c, w1cands) in bivalues:
            if (w1r, w1c) == (pr, pc):
                continue
            if not _are_peers(pr, pc, w1r, w1c):
                continue
            common = w1cands & pcands
            if len(common) != 1:
                continue
            shared_digit = next(iter(common))
            other_pivot_digit = (pcands - {shared_digit}).pop()
            z = (w1cands - {shared_digit}).pop()
            if z in pcands:
                continue
            if z != v:
                continue
            # Wing2: peer of pivot, candidates {other_pivot_digit, z}
            for (w2r, w2c, w2cands) in bivalues:
                if (w2r, w2c) in [(pr, pc), (w1r, w1c)]:
                    continue
                if not _are_peers(pr, pc, w2r, w2c):
                    continue
                if w2cands != {other_pivot_digit, z}:
                    continue
                # (r, c) must be a peer of both W1 and W2, not P/W1/W2 itself
                if (r, c) in [(pr, pc), (w1r, w1c), (w2r, w2c)]:
                    continue
                if _are_peers(r, c, w1r, w1c) and _are_peers(r, c, w2r, w2c):
                    return True
    return False


def find_xy_wing_elimination(engine: CandidateEngine) -> tuple[str, int, int, int] | None:
    # Collect all bivalue cells
    bivalues: list[tuple[int, int, set[int]]] = []
    for r in range(9):
        for c in range(9):
            if engine.is_empty(r, c):
                cands = engine.get_candidates(r, c)
                if len(cands) == 2:
                    bivalues.append((r, c, cands))

    for (pr, pc, pcands) in bivalues:
        x, y = sorted(pcands)
        # Iterate over wing1 candidates: a peer of pivot sharing exactly one
        # digit with pivot.  The shared digit is x or y; the other digit is z.
        for (w1r, w1c, w1cands) in bivalues:
            if (w1r, w1c) == (pr, pc):
                continue
            if not _are_peers(pr, pc, w1r, w1c):
                continue
            common = w1cands & pcands
            if len(common) != 1:
                continue
            shared_digit = next(iter(common))          # x or y
            other_pivot_digit = (pcands - {shared_digit}).pop()   # the other of {x,y}
            z = (w1cands - {shared_digit}).pop()
            if z in pcands:
                continue  # z must NOT be in pivot's candidates

            # Wing2: peer of pivot, candidates {other_pivot_digit, z}
            for (w2r, w2c, w2cands) in bivalues:
                if (w2r, w2c) in [(pr, pc), (w1r, w1c)]:
                    continue
                if not _are_peers(pr, pc, w2r, w2c):
                    continue
                if w2cands != {other_pivot_digit, z}:
                    continue
                # Found XY-Wing — eliminate z from cells seeing BOTH wings
                for r in range(9):
                    for c in range(9):
                        if (r, c) in [(pr, pc), (w1r, w1c), (w2r, w2c)]:
                            continue
                        if not engine.is_empty(r, c):
                            continue
                        if z not in engine.get_candidates(r, c):
                            continue
                        if _are_peers(r, c, w1r, w1c) and _are_peers(r, c, w2r, w2c):
                            return ('eliminate', r, c, z)
    return None
