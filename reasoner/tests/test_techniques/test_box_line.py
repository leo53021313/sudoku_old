import numpy as np
from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.box_line import find_box_line_elimination, justifies_box_line


def test_no_box_line_on_empty_board():
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    assert find_box_line_elimination(eng) is None


def test_row_to_box_reduction():
    """Row 0: digit 4 only in cols 0..2 (within box (0,0)) → eliminate from box's other rows.
    Force row 0 (cols 3..8) to lose 4 by placing 4 in cols 3..8 of various other rows
    (choosing rows 3+ to avoid blocking rows 1-2 in cols 0-2)."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Place 4 in cols 3..8 of rows 3+ to eliminate 4 from row 0 cols 3..8
    # without affecting rows 1-2 in cols 0-2
    board[3, 3] = 4
    board[4, 4] = 4
    board[5, 5] = 4
    board[6, 6] = 4
    board[7, 7] = 4
    board[8, 8] = 4
    eng = CandidateEngine(board)
    # In row 0, digit 4 only candidates at (0,0)..(0,2) (cols 3..8 lost via col constraint)
    # → these are all in box (0,0) → eliminate 4 from rest of box ((1,0..2),(2,0..2))
    result = find_box_line_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 4
    assert (r, c) in [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def test_col_to_box_reduction():
    """Col 3: digit 7 only in rows 0..2 (within box (0,1)) → eliminate from box's other cols.
    Ensure col 3 has 7 only in rows 0-2 by placing 7 in rows 3+ other columns.
    Use digit 7 instead of 4 to avoid interference with row-to-box test setup."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Place 7 in rows 3-8 in diagonal positions to block those rows from having 7 elsewhere
    board[3, 0] = 7
    board[4, 1] = 7
    board[5, 2] = 7
    board[6, 5] = 7
    board[7, 6] = 7
    board[8, 7] = 7
    eng = CandidateEngine(board)
    # In col 3, digit 7 only candidates at (0..2, 3) (rows 3..8 lost via row constraint)
    # → all in box_row 0 (box (0,1)) → eliminate from box's other cols (cols 4-5)
    result = find_box_line_elimination(eng)
    assert result is not None
    op, r, c, v = result
    assert op == 'eliminate'
    assert v == 7
    # Should eliminate from rest of box (0,1) excluding col 3
    assert (r, c) in [(0, 4), (0, 5), (1, 4), (1, 5), (2, 4), (2, 5)]


# ---------------------------------------------------------------------------
# justifies_box_line tests
# ---------------------------------------------------------------------------

def test_justifies_box_line_positive():
    """Row 0 has digit 4 only in box (0,0). Eliminate from (1,1) inside box but outside row."""
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    # Row 0 candidates for 4: only in box (0,0) cols 0-2
    eng._board[0, 0] = 0; eng._board[0, 1] = 0
    eng._cands[0][0] = {4, 5}
    eng._cands[0][1] = {4, 6}
    # Target: (1,0) is in box (0,0), outside row 0
    eng._board[1, 0] = 0
    eng._cands[1][0] = {4, 7}
    assert justifies_box_line(eng, ('eliminate', 1, 0, 4)) is True


def test_justifies_box_line_rejects_wrong_mode():
    """justifies_box_line returns False for 'fill' actions."""
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    eng._board[0, 0] = 0; eng._board[0, 1] = 0; eng._board[1, 0] = 0
    eng._cands[0][0] = {4, 5}
    eng._cands[0][1] = {4, 6}
    eng._cands[1][0] = {4, 7}
    assert justifies_box_line(eng, ('fill', 1, 0, 4)) is False


def test_justifies_box_line_rejects_outside_box():
    """Cell (3,0) is NOT in box (0,0) — box-line from row 0/box (0,0) would not eliminate there."""
    eng = CandidateEngine(np.zeros((9, 9), dtype=np.int8))
    for r in range(9):
        for c in range(9):
            eng._cands[r][c] = set()
    eng._board[:] = 1
    eng._board[0, 0] = 0; eng._board[0, 1] = 0
    eng._cands[0][0] = {4, 5}
    eng._cands[0][1] = {4, 6}
    eng._board[3, 0] = 0
    eng._cands[3][0] = {4, 7}
    # (3,0) is NOT in box (0,0) — box-line technique would not eliminate there
    assert justifies_box_line(eng, ('eliminate', 3, 0, 4)) is False
