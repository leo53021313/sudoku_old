import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.hidden_pair import find_hidden_pair_elimination


def test_no_hidden_pair_on_empty_board():
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    assert find_hidden_pair_elimination(eng) is None


def test_hidden_pair_eliminates_extras_via_internal_mutation():
    """Hidden pair {1,2} at (0,3) and (0,5); both have extra candidates.
    The technique should eliminate the extras (5 from (0,3), 7 from (0,5))."""
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    # Force a known candidate state via internal mutation:
    # In row 0, only (0,3) and (0,5) contain digits 1 or 2 in candidates.
    # Other cells in row 0 must NOT have 1 or 2 in their candidate sets.
    for c in range(9):
        if c == 3:
            eng._cands[0][c] = {1, 2, 5}      # extra digit 5
        elif c == 5:
            eng._cands[0][c] = {1, 2, 7}      # extra digit 7
        else:
            eng._cands[0][c] = {3, 4, 6, 8, 9}  # no 1 or 2

    result = find_hidden_pair_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert (r, c) in [(0, 3), (0, 5)]
    # v must be the EXTRA digit (5 if cell=(0,3), 7 if cell=(0,5)), not 1 or 2 (the pair)
    assert v not in (1, 2)
    if (r, c) == (0, 3):
        assert v == 5
    else:
        assert v == 7


def test_no_hidden_pair_returns_none_when_pair_already_clean():
    """If the pair cells already only contain {1,2}, no extras to eliminate → None"""
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    for c in range(9):
        if c == 3:
            eng._cands[0][c] = {1, 2}        # no extras
        elif c == 5:
            eng._cands[0][c] = {1, 2}        # no extras
        else:
            eng._cands[0][c] = {3, 4, 6, 8, 9}
    # The hidden pair exists but has no extras to eliminate → None
    result = find_hidden_pair_elimination(eng)
    assert result is None
