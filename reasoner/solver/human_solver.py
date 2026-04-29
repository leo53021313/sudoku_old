"""Human-style solver: priority-loop over Tier-A techniques (1, 2, 4-13, 17).

API:
  HumanSolver().suggest(board) → (action, max_technique_id)
    action: ('fill', r, c, v) | ('eliminate', r, c, v) | None
    max_technique_id: int 1-17 if a technique fired; -1 otherwise.

  HumanSolver().solve_to_completion(board) → (final_board, max_technique_used, solved)
    Repeatedly applies suggestions until solved or stuck.

Priority order (cheapest → most expensive):
  1 naked_single (fill)
  2 hidden_single (fill)
  4 naked_pair (eliminate)
  5 hidden_pair (eliminate)
  6 pointing_pair (eliminate)
  7 box_line (eliminate)
  8 naked_triple (eliminate)
  9 naked_quad (eliminate)
  10 x_wing (eliminate)
  11 swordfish (eliminate)
  12 xy_wing (eliminate)
  13 xyz_wing (eliminate)
  17 trial_error (eliminate; backtracking-based, slow last resort)

Technique 3 (basic elimination) is implicit in CandidateEngine and not a
separately-callable detector. Techniques 14 (Chains), 15 (Coloring), 16
(AIC) are deferred to Tier B.
"""

from __future__ import annotations
import numpy as np

from reasoner.solver.candidate_engine import CandidateEngine
from reasoner.solver.techniques.naked_single import find_naked_single
from reasoner.solver.techniques.hidden_single import find_hidden_single
from reasoner.solver.techniques.naked_pair import find_naked_pair_elimination
from reasoner.solver.techniques.hidden_pair import find_hidden_pair_elimination
from reasoner.solver.techniques.pointing_pair import find_pointing_pair_elimination
from reasoner.solver.techniques.box_line import find_box_line_elimination
from reasoner.solver.techniques.naked_triple import find_naked_triple_elimination
from reasoner.solver.techniques.naked_quad import find_naked_quad_elimination
from reasoner.solver.techniques.x_wing import find_x_wing_elimination
from reasoner.solver.techniques.swordfish import find_swordfish_elimination
from reasoner.solver.techniques.xy_wing import find_xy_wing_elimination
from reasoner.solver.techniques.xyz_wing import find_xyz_wing_elimination
from reasoner.solver.techniques.trial_error import find_trial_error_elimination


_TECHNIQUES: list[tuple[int, str, callable]] = [
    (1,  'naked_single',   find_naked_single),
    (2,  'hidden_single',  find_hidden_single),
    (4,  'naked_pair',     find_naked_pair_elimination),
    (5,  'hidden_pair',    find_hidden_pair_elimination),
    (6,  'pointing_pair',  find_pointing_pair_elimination),
    (7,  'box_line',       find_box_line_elimination),
    (8,  'naked_triple',   find_naked_triple_elimination),
    (9,  'naked_quad',     find_naked_quad_elimination),
    (10, 'x_wing',         find_x_wing_elimination),
    (11, 'swordfish',      find_swordfish_elimination),
    (12, 'xy_wing',        find_xy_wing_elimination),
    (13, 'xyz_wing',       find_xyz_wing_elimination),
    (17, 'trial_error',    find_trial_error_elimination),
]


class HumanSolver:
    """Stateless coordinator: builds a CandidateEngine on each call."""

    def suggest(self, board: np.ndarray) -> tuple[tuple[str, int, int, int] | None, int]:
        engine = CandidateEngine(board)
        for tech_id, _name, fn in _TECHNIQUES:
            result = fn(engine)
            if result is not None:
                return result, tech_id
        return None, -1

    def solve_to_completion(self, board: np.ndarray) -> tuple[np.ndarray, int, bool]:
        """Repeatedly apply suggestions until solved or stuck.

        Returns (final_board, max_technique_used, solved).
        """
        engine = CandidateEngine(board)
        max_tech = -1
        while True:
            applied = False
            for tech_id, _name, fn in _TECHNIQUES:
                result = fn(engine)
                if result is None:
                    continue
                op, r, c, v = result
                if op == 'fill':
                    engine.apply_fill(r, c, v)
                else:
                    engine.apply_eliminate(r, c, v)
                if tech_id > max_tech:
                    max_tech = tech_id
                applied = True
                break  # restart priority loop from technique 1
            if not applied:
                break  # stuck

        solved = bool(np.all(engine.board != 0))
        return engine.board, max_tech, solved
