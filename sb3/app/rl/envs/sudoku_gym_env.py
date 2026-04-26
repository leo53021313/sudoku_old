# app/rl/envs/sudoku_gym_env.py
# -*- coding: utf-8 -*-
"""
SudokuGymEnv — Gymnasium-compatible environment for Sudoku RL.

Key features:
- action_masks() for sb3-contrib MaskablePPO
- Solution pre-computed by backtracking solver at reset()
- Dense solution-guided reward via RewardComputer
- TeacherEngine runs inside subprocess (pure numpy) and returns
  teacher_action + teacher_quality via info dict
- set_difficulty_distribution() for CurriculumCallback

Observation: (9, 9, 9) float32 — 9 channels, channels-first
Action:      Discrete(729)  — r*81 + c*9 + (v-1)
"""

from __future__ import annotations

import os
import sys
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from app.rl.envs.sudoku_solver import solve
from app.rl.envs.reward_computer import RewardComputer
from app.data.pool_db import PuzzlePoolDB
from app.sudoku.teacher_engine import TeacherEngine


class SudokuGymEnv(gym.Env):
    metadata = {"render_modes": []}

    N_CHANNELS = 9  # 8 original + 1 hidden-single

    def __init__(
        self,
        db_path: str = "data/puzzle_pool.db",
        difficulty: int = 1,
        max_wrong_fills: int = 5,
        max_steps: int = 300,
        teacher_max_cand: int = 4,
    ) -> None:
        super().__init__()

        self.db_path        = db_path
        self.max_wrong_fills = max_wrong_fills
        self.max_steps       = max_steps

        # Difficulty distribution: {level: probability}. Mutated by CurriculumCallback.
        self._difficulty_dist: dict[int, float] = {difficulty: 1.0}

        # Gymnasium spaces
        self.observation_space = spaces.Box(
            low=0.0, high=1.0,
            shape=(self.N_CHANNELS, 9, 9),
            dtype=np.float32,
        )
        self.action_space = spaces.Discrete(729)

        # Lazy DB connection (each subprocess gets its own)
        self._db: PuzzlePoolDB | None = None

        # Teacher (pure numpy — safe in subprocess)
        self._teacher = TeacherEngine(max_candidates=teacher_max_cand)

        # Board state (populated by reset)
        self.board: np.ndarray = np.zeros((9, 9), dtype=np.int8)
        self.fixed: np.ndarray = np.zeros((9, 9), dtype=bool)
        self.solution: np.ndarray = np.zeros((9, 9), dtype=np.int8)
        self.candidates_cache: list[list[set[int]]] = [
            [set() for _ in range(9)] for _ in range(9)
        ]
        self.candidate_count_grid: np.ndarray = np.zeros((9, 9), dtype=np.int8)
        self.single_candidate_grid: np.ndarray = np.zeros((9, 9), dtype=np.float32)

        self.wrong_count = 0
        self._step_count = 0
        self._current_difficulty = difficulty
        self._episode_reward = 0.0

        self._reward_computer = RewardComputer(self)

    # ── Gymnasium API ─────────────────────────────────────────────────────────

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict | None = None,
    ) -> tuple[np.ndarray, dict]:
        super().reset(seed=seed)

        if options is not None and "board" in options:
            self.board    = np.array(options["board"], dtype=np.int8).copy()
            self.solution = np.array(options["solution"], dtype=np.int8).copy()
            self.fixed    = (self.board != 0)
            self._current_difficulty = int(options.get("difficulty", 1))
            self.wrong_count    = 0
            self._step_count    = 0
            self._episode_reward = 0.0
            self._rebuild_candidates()
            return self._obs(), {}

        # Sample difficulty from distribution
        difficulties = list(self._difficulty_dist.keys())
        probs        = list(self._difficulty_dist.values())
        difficulty   = int(self.np_random.choice(difficulties, p=probs))
        self._current_difficulty = difficulty

        # Fetch puzzle from DB
        row = self._get_db().fetch_one_puzzle_for_training(level=difficulty)
        if row is None:
            # Fallback: any difficulty if chosen level has no puzzles
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

        # Pre-compute unique solution
        sol = solve(board)
        if sol is None:
            # Should not happen with well-formed DB puzzles; reset again
            return self.reset(seed=seed, options=options)
        self.solution = sol

        return self._obs(), {}

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        r, c, v = self._decode(int(action))

        # Teacher recommendation on CURRENT state (before agent's action is committed)
        teacher_result = self._teacher(self)
        if teacher_result[0] is not None:
            tr, tc, tv = teacher_result[0]
            teacher_action  = int(tr * 81 + tc * 9 + (tv - 1))
            teacher_quality = float(teacher_result[1])
        else:
            teacher_action  = -1
            teacher_quality = 0.0

        # Compute reward + commit fill
        reward, terminated = self._reward_computer.compute(r, c, v)
        self._step_count += 1
        self._episode_reward += reward
        truncated = (not terminated) and (self._step_count >= self.max_steps)

        info = {
            "teacher_action":  teacher_action,
            "teacher_quality": teacher_quality,
            "is_success":      terminated and bool(np.all(self.board != 0)),
            "difficulty":      self._current_difficulty,
            "wrong_count":     self.wrong_count,
            "steps":           self._step_count,
            "episode_reward":  self._episode_reward,
        }
        return self._obs(), float(reward), terminated, truncated, info

    def action_masks(self) -> np.ndarray:
        """Required by sb3-contrib MaskablePPO."""
        mask = np.zeros(729, dtype=bool)
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    continue
                for v in self.candidates_cache[r][c]:
                    mask[r * 81 + c * 9 + (v - 1)] = True
        return mask

    # ── Curriculum interface ──────────────────────────────────────────────────

    def set_difficulty_distribution(self, dist: dict[int, float]) -> None:
        """Called by CurriculumCallback via env_method()."""
        self._difficulty_dist = {int(k): float(p) for k, p in dist.items()}

    # ── TeacherEngine compatibility (board / candidates / hidden-single) ──────

    def _is_hidden_single(self, r: int, c: int, num: int) -> bool:
        """Mirrors SudokuEnv._is_hidden_single for TeacherEngine compatibility."""
        def only_place(cells):
            for rr, cc in cells:
                if rr == r and cc == c:
                    continue
                if self.board[rr, cc] == 0 and num in self.candidates_cache[rr][cc]:
                    return False
            return True

        if only_place([(r, cc) for cc in range(9)]):
            return True
        if only_place([(rr, c) for rr in range(9)]):
            return True
        br, bc = (r // 3) * 3, (c // 3) * 3
        return only_place([(br + dr, bc + dc) for dr in range(3) for dc in range(3)])

    # ── Observation builder ───────────────────────────────────────────────────

    def _obs(self) -> np.ndarray:
        obs = np.zeros((self.N_CHANNELS, 9, 9), dtype=np.float32)

        obs[0] = self.board / 9.0
        obs[1] = self.fixed.astype(np.float32)
        obs[2] = (self.board == 0).astype(np.float32)

        for r in range(9):
            filled_r = float(np.count_nonzero(self.board[r, :] != 0))
            obs[3, r, :] = filled_r / 9.0
        for c in range(9):
            filled_c = float(np.count_nonzero(self.board[:, c] != 0))
            obs[4, :, c] = filled_c / 9.0
        for br in range(3):
            for bc in range(3):
                box = self.board[br*3:(br+1)*3, bc*3:(bc+1)*3]
                filled_b = float(np.count_nonzero(box != 0))
                obs[5, br*3:(br+1)*3, bc*3:(bc+1)*3] = filled_b / 9.0

        obs[6] = self.candidate_count_grid.astype(np.float32) / 9.0
        obs[7] = self.single_candidate_grid  # naked-single flag
        obs[8] = self._reward_computer.compute_hidden_single_grid()  # hidden-single flag

        return obs

    # ── Candidate management ──────────────────────────────────────────────────

    def _rebuild_candidates(self) -> None:
        for r in range(9):
            for c in range(9):
                if self.board[r, c] != 0:
                    self.candidates_cache[r][c] = set()
                    self.candidate_count_grid[r, c] = 0
                    self.single_candidate_grid[r, c] = 0.0
                else:
                    cands = self._compute_candidates(r, c)
                    self.candidates_cache[r][c] = cands
                    cnt = len(cands)
                    self.candidate_count_grid[r, c] = cnt
                    self.single_candidate_grid[r, c] = 1.0 if cnt == 1 else 0.0

    def _compute_candidates(self, r: int, c: int) -> set[int]:
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

    # ── Action encoding ───────────────────────────────────────────────────────

    @staticmethod
    def _decode(action: int) -> tuple[int, int, int]:
        r = action // 81
        c = (action % 81) // 9
        v = (action % 9) + 1
        return r, c, v

    @staticmethod
    def encode(r: int, c: int, v: int) -> int:
        return r * 81 + c * 9 + (v - 1)

    # ── DB (lazy per-process) ─────────────────────────────────────────────────

    def _get_db(self) -> PuzzlePoolDB:
        if self._db is None:
            self._db = PuzzlePoolDB(self.db_path)
        return self._db
