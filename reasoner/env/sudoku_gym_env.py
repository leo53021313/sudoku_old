# reasoner/env/sudoku_gym_env.py
# -*- coding: utf-8 -*-
"""SudokuGymEnv — 24-ch obs, fill+eliminate action space, solver-aware reward.

Action space: Discrete(1458)
  action 0..728     -> ('fill',      r, c, v)
  action 729..1457  -> ('eliminate', r, c, v)
  in both halves: r=idx//81, c=(idx%81)//9, v=(idx%9)+1
                  where idx = action (fill) or action - 729 (eliminate)

Routes I and II divergence: this env supports route II — the agent can
either fill a cell with a value, OR eliminate a candidate from a cell.
Eliminate actions let the agent directly demonstrate techniques 4-7
(naked/hidden pair, pointing pair, box-line) that act on candidates.

Wrong actions (whether wrong fill or eliminating the solution value) both
increment wrong_count; episode terminates when wrong_count >= max_wrong_fills.
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from reasoner.solver_ext.backtracking import solve
from reasoner.env.reward_computer import RewardComputer
from reasoner.data_pkg.pool_db import PuzzlePoolDB


class SudokuGymEnv(gym.Env):
    metadata = {"render_modes": []}

    N_CHANNELS = 24  # removed naked-single / hidden-single shortcut flags
    N_ACTIONS  = 1458  # 729 fill + 729 eliminate
    _ELIM_OFFSET = 729

    def __init__(
        self,
        db_path: str = "data/puzzle_pool.db",
        difficulty: int = 1,
        max_wrong_fills: int = 20,  # was 5
        max_steps: int = 300,
    ) -> None:
        super().__init__()

        self.db_path        = db_path
        self.max_wrong_fills = max_wrong_fills
        self.max_steps       = max_steps

        self._difficulty_dist: dict[int, float] = {difficulty: 1.0}

        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self.N_CHANNELS, 9, 9),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(self.N_ACTIONS)

        self._db: PuzzlePoolDB | None = None

        self.board: np.ndarray = np.zeros((9, 9), dtype=np.int8)
        self.fixed: np.ndarray = np.zeros((9, 9), dtype=bool)
        self.solution: np.ndarray = np.zeros((9, 9), dtype=np.int8)
        self.candidates_cache: list[list[set[int]]] = [
            [set() for _ in range(9)] for _ in range(9)
        ]
        self.candidate_count_grid: np.ndarray = np.zeros((9, 9), dtype=np.int8)

        self.wrong_count = 0
        self._step_count = 0
        self._current_difficulty = difficulty
        self._episode_reward = 0.0

        self._reward_computer = RewardComputer(self)

    def reset(self, *, seed=None, options=None, _retries=0):
        super().reset(seed=seed)

        if options is not None and "board" in options:
            self.board    = np.array(options["board"], dtype=np.int8).copy()
            raw_sol = options.get("solution")
            if raw_sol is None:
                raw_sol = solve(self.board)
            if raw_sol is None:
                raise ValueError("Board has no unique solution and no solution was provided.")
            self.solution = np.array(raw_sol, dtype=np.int8).copy()
            self.fixed    = (self.board != 0)
            self._current_difficulty = int(options.get("difficulty", 1))
            self.wrong_count    = 0
            self._step_count    = 0
            self._episode_reward = 0.0
            self._rebuild_candidates()
            return self._obs(), {}

        difficulties = list(self._difficulty_dist.keys())
        probs        = list(self._difficulty_dist.values())
        difficulty   = int(self.np_random.choice(difficulties, p=probs))
        self._current_difficulty = difficulty

        row = self._get_db().fetch_one_puzzle_for_training(level=difficulty)
        if row is None:
            row = self._get_db().fetch_one_puzzle_for_training()
        if row is None:
            raise RuntimeError("No puzzles available in DB for training")

        puzzle_str = row["puzzle"]
        board_list = PuzzlePoolDB.string_to_board(puzzle_str)
        board = np.array(board_list, dtype=np.int8)

        self.board = board.copy()
        self.fixed = (board != 0)
        self.wrong_count   = 0
        self._step_count   = 0
        self._episode_reward = 0.0

        self._rebuild_candidates()

        sol = solve(board)
        if sol is None:
            if _retries >= 10:
                raise RuntimeError("Too many unsolvable puzzles in DB")
            return self.reset(seed=seed, options=options, _retries=_retries + 1)
        self.solution = sol

        return self._obs(), {}

    def step(self, action):
        mode, r, c, v = self._decode(int(action))
        reward, terminated = self._reward_computer.compute(mode, r, c, v)
        self._step_count += 1
        self._episode_reward += reward
        truncated = (not terminated) and (self._step_count >= self.max_steps)

        info = {
            "is_success":  terminated and bool(np.all(self.board != 0)),
            "difficulty":  self._current_difficulty,
            "wrong_count": self.wrong_count,
            "steps":       self._step_count,
            "action_mode": mode,
            "episode_reward": self._episode_reward,
        }
        return self._obs(), float(reward), terminated, truncated, info

    def action_masks(self) -> np.ndarray:
        """Legality mask over the 1458-action space.

        Both fill and eliminate operate on (r, c, v) where v is currently
        a candidate at empty cell (r, c). Filling a non-empty cell is illegal;
        eliminating a digit that's not in candidates is a no-op so we mask it
        out too. The CORRECTNESS of the action (whether v matches solution)
        is NOT checked here — that would leak the solution; correctness is
        evaluated by RewardComputer and contributes to wrong_count instead.
        """
        mask = np.zeros(self.N_ACTIONS, dtype=bool)
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    continue
                for v in self.candidates_cache[r][c]:
                    base = r * 81 + c * 9 + (v - 1)
                    mask[base] = True                       # fill
                    mask[self._ELIM_OFFSET + base] = True   # eliminate
        return mask

    def set_difficulty_distribution(self, dist: dict[int, float]) -> None:
        self._difficulty_dist = {int(k): float(p) for k, p in dist.items()}

    def _obs(self) -> np.ndarray:
        board = self.board.copy()
        obs = np.zeros((self.N_CHANNELS, 9, 9), dtype=np.float32)

        # ch 0-8: digit one-hot
        for v in range(1, 10):
            obs[v - 1] = (board == v).astype(np.float32)

        # ch 9-17: per-digit candidate planes
        for r in range(9):
            for c in range(9):
                if board[r, c] == 0:
                    for v in self.candidates_cache[r][c]:
                        obs[9 + v - 1, r, c] = 1.0

        # ch 18: fixed
        obs[18] = self.fixed.astype(np.float32)
        # ch 19: empty
        obs[19] = (board == 0).astype(np.float32)

        # ch 20: row fill ratio
        for r in range(9):
            obs[20, r, :] = float(np.count_nonzero(board[r, :] != 0)) / 9.0
        # ch 21: col fill ratio
        for c in range(9):
            obs[21, :, c] = float(np.count_nonzero(board[:, c] != 0)) / 9.0
        # ch 22: box fill ratio
        for br in range(3):
            for bc in range(3):
                box = board[br*3:(br+1)*3, bc*3:(bc+1)*3]
                obs[22, br*3:(br+1)*3, bc*3:(bc+1)*3] = float(np.count_nonzero(box != 0)) / 9.0

        # ch 23: candidate count / 9.0
        obs[23] = self.candidate_count_grid.astype(np.float32) / 9.0

        # ch 24, 25 REMOVED — no naked-single / hidden-single flags

        return obs

    def _rebuild_candidates(self):
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    self.candidates_cache[r][c] = set()
                    self.candidate_count_grid[r, c] = 0
                else:
                    cands = self._compute_candidates(r, c)
                    self.candidates_cache[r][c] = cands
                    self.candidate_count_grid[r, c] = len(cands)

    def _compute_candidates(self, r, c):
        used: set[int] = set()
        used.update(int(v) for v in self.board[r, :] if v != 0)
        used.update(int(v) for v in self.board[:, c] if v != 0)
        br, bc = (r // 3) * 3, (c // 3) * 3
        used.update(
            int(self.board[rr, cc])
            for rr in range(br, br + 3)
            for cc in range(bc, bc + 3)
            if self.board[rr, cc] != 0
        )
        return {n for n in range(1, 10) if n not in used}

    @staticmethod
    def _decode(action: int) -> tuple[str, int, int, int]:
        """Decode a 0..1457 action into (mode, r, c, v)."""
        if action < SudokuGymEnv._ELIM_OFFSET:
            mode = "fill"
            idx = action
        else:
            mode = "eliminate"
            idx = action - SudokuGymEnv._ELIM_OFFSET
        r = idx // 81
        c = (idx % 81) // 9
        v = (idx % 9) + 1
        return mode, r, c, v

    @staticmethod
    def encode(mode: str, r: int, c: int, v: int) -> int:
        """Encode (mode, r, c, v) into a 0..1457 action.

        mode: 'fill' or 'eliminate'.
        """
        base = r * 81 + c * 9 + (v - 1)
        if mode == "fill":
            return base
        if mode == "eliminate":
            return SudokuGymEnv._ELIM_OFFSET + base
        raise ValueError(f"Unknown action mode: {mode!r}")

    def _get_db(self):
        if self._db is None:
            self._db = PuzzlePoolDB(self.db_path)
        return self._db
