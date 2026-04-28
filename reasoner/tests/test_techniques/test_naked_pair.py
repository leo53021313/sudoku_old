import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.naked_pair import find_naked_pair_elimination


def _eng(board=None):
    if board is None:
        board = np.zeros((9, 9), dtype=np.int8)
    return CandidateEngine(board)


def test_no_pair_on_empty_board():
    assert find_naked_pair_elimination(_eng()) is None


def test_naked_pair_with_no_targets_returns_none():
    # Construct: (0,0) and (0,1) have candidates {2,7}, other cells in row 0 are filled
    # → the pair exists in row 0, but row 0 has no third empty cell to eliminate from
    # The function will skip row 0 (no targets there) and continue to columns/boxes.
    # Since no naked pair exists in columns or boxes, it returns None.
    board = np.zeros((9, 9), dtype=np.int8)
    # Fill row 0 except (0,0) and (0,1)
    board[0, 2] = 1; board[0, 3] = 3; board[0, 4] = 4
    board[0, 5] = 5; board[0, 6] = 6; board[0, 7] = 8; board[0, 8] = 9
    # Fill columns 0 and 1 to ensure no pairs exist in those columns
    # (just place values such that no two cells share identical 2-element candidate sets)
    board[1, 0] = 2; board[1, 1] = 2
    board[2, 0] = 3; board[2, 1] = 4
    board[3, 0] = 5; board[3, 1] = 6
    board[4, 0] = 7; board[4, 1] = 8
    board[5, 0] = 9; board[5, 1] = 1
    board[6, 0] = 1; board[6, 1] = 3
    board[7, 0] = 4; board[7, 1] = 5
    board[8, 0] = 6; board[8, 1] = 7
    eng = CandidateEngine(board)
    # Verify that no naked pair exists (no two empty cells in any unit have identical 2-element candidate sets)
    assert find_naked_pair_elimination(eng) is None


def test_naked_pair_eliminates_from_third_cell():
    # Make (0,0) and (0,1) be a naked pair {2,7}, with (0,2)..(0,8) empty so the
    # pair can eliminate. Use col placements to constrain (0,0) and (0,1) candidates.
    # Setup (verified by hand or by ad-hoc trial): place values to drive (0,0) → {2,7} and (0,1) → {2,7}
    # while leaving most of row 0 empty.
    board = np.zeros((9, 9), dtype=np.int8)
    # Eliminate {1,3,4,5,6,8,9} from (0,0) via col 0 (using rows 1-8 to avoid cluttering row 0)
    board[1, 0] = 1; board[2, 0] = 3; board[3, 0] = 4
    board[4, 0] = 5; board[5, 0] = 6; board[6, 0] = 8; board[7, 0] = 9
    # Same for (0,1) via col 1, using different digit→row mapping than col 0 to avoid box conflicts
    # Box (0,0) covers rows 0-2, cols 0-2. Avoid duplicate digits in box.
    board[3, 1] = 1; board[4, 1] = 3; board[5, 1] = 4
    board[6, 1] = 5; board[7, 1] = 6; board[8, 1] = 8
    # (0,1) col missing 9: need 9 also eliminated from (0,1)
    # Use box (0,0) row 1 or 2: (1,2) = 9 → (0,1) is in box (0,0); 9 eliminated from (0,1)
    board[1, 2] = 9
    eng = CandidateEngine(board)
    # Sanity check: (0,0) and (0,1) should both be {2,7}
    cands_00 = eng.get_candidates(0, 0)
    cands_01 = eng.get_candidates(0, 1)
    assert cands_00 == {2, 7}, f"expected (0,0)={{2,7}}, got {cands_00}"
    assert cands_01 == {2, 7}, f"expected (0,1)={{2,7}}, got {cands_01}"
    # (0,3) should be empty + have 2 or 7 as candidate (depending on cols/box)
    assert eng.is_empty(0, 3)
    cands_03 = eng.get_candidates(0, 3)
    # The naked pair should propose eliminating 2 or 7 from some empty cell in row 0
    # other than (0,0) and (0,1)
    result = find_naked_pair_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v in (2, 7)
    assert r == 0
    assert c not in (0, 1)
