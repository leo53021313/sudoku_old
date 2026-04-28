import numpy as np
from reasoner.solver.human_solver import HumanSolver


def test_naked_single_takes_priority_1():
    """A board with both naked single AND naked pair available — naked single must win."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Make (0,8) a naked single for 9 (fill rest of row 0 with 1..8)
    for c in range(8):
        board[0, c] = c + 1
    solver = HumanSolver()
    action, tech_id = solver.suggest(board)
    assert action == ('fill', 0, 8, 9)
    assert tech_id == 1


def test_returns_none_when_no_technique_applies():
    """Empty board: no technique fires."""
    board = np.zeros((9, 9), dtype=np.int8)
    solver = HumanSolver()
    action, tech_id = solver.suggest(board)
    assert action is None
    assert tech_id == -1


def test_max_technique_id_reflects_used_technique():
    """Hidden-single-only setup → tech_id == 2."""
    board = np.zeros((9, 9), dtype=np.int8)
    # Same setup as test_hidden_single_in_row from test_hidden_single.py — places 7 in 8 cols outside (1,4)
    board[0, 0] = 7
    board[2, 1] = 7
    board[3, 2] = 7
    board[4, 3] = 7
    board[5, 5] = 7
    board[6, 6] = 7
    board[7, 7] = 7
    board[8, 8] = 7
    solver = HumanSolver()
    action, tech_id = solver.suggest(board)
    assert action is not None
    op, r, c, v = action
    assert op == 'fill'
    assert tech_id == 2


def test_solve_to_completion_simple_board():
    """Cascading naked singles solve a near-complete board."""
    board = np.array([
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 0],  # only (8,8) empty — naked single for 9
    ], dtype=np.int8)
    solver = HumanSolver()
    final_board, max_tech, solved = solver.solve_to_completion(board)
    assert solved
    assert final_board[8, 8] == 9
    assert max_tech == 1


def test_solve_to_completion_unsolvable_with_v1_techniques():
    """Empty board: no technique fires → stuck immediately."""
    board = np.zeros((9, 9), dtype=np.int8)
    solver = HumanSolver()
    final_board, max_tech, solved = solver.solve_to_completion(board)
    assert not solved
    assert max_tech == -1
