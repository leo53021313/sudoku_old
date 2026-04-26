# app/rl/curriculum/eval_callback.py
# -*- coding: utf-8 -*-
"""
SudokuEvalCallback — fixed held-out eval using action-masked prediction.

Runs N deterministic episodes per difficulty level every eval_freq steps.
Logs eval/success_rate_L{d} and eval/success_rate_overall to TensorBoard.
Does NOT use EvalCallback from SB3 because that doesn't pass action masks.
"""

from __future__ import annotations

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

from app.rl.envs.sudoku_gym_env import SudokuGymEnv


class SudokuEvalCallback(BaseCallback):
    """
    Parameters
    ----------
    db_path : str
        Path to puzzle DB (same as training).
    eval_freq : int
        Run eval every this many timesteps (default 50_000).
    n_episodes : int
        Episodes per difficulty level per eval (default 20).
    difficulties : tuple[int, ...]
        Difficulty levels to evaluate (default (1, 2, 3, 4)).
    verbose : int
        Verbosity (1 = print summary per eval, 0 = silent).
    """

    def __init__(
        self,
        db_path: str,
        eval_freq: int = 50_000,
        n_episodes: int = 20,
        difficulties: tuple[int, ...] = (1, 2, 3, 4),
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self._db_path      = db_path
        self._eval_freq    = eval_freq
        self._n_episodes   = n_episodes
        self._difficulties = difficulties
        self._last_eval    = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_eval < self._eval_freq:
            return True
        self._last_eval = self.num_timesteps

        env = SudokuGymEnv(db_path=self._db_path)
        total_s, total_n = 0, 0

        for diff in self._difficulties:
            env.set_difficulty_distribution({diff: 1.0})
            successes = []
            for _ in range(self._n_episodes):
                obs, _ = env.reset()
                done = False
                while not done:
                    masks = env.action_masks()[np.newaxis]          # (1, 729)
                    action, _ = self.model.predict(
                        obs[np.newaxis],                             # (1, C, 9, 9)
                        action_masks=masks,
                        deterministic=True,
                    )
                    obs, _, terminated, truncated, info = env.step(int(action[0]))
                    done = terminated or truncated
                successes.append(info["is_success"])

            rate = float(np.mean(successes))
            self.logger.record(f"eval/success_rate_L{diff}", rate)
            total_s += sum(successes)
            total_n += len(successes)

        overall = total_s / max(total_n, 1)
        self.logger.record("eval/success_rate_overall", overall)

        if self.verbose >= 1:
            parts = ", ".join(
                f"L{d}={self._n_episodes}" for d in self._difficulties
            )
            print(
                f"[Eval] Step {self.num_timesteps:,}: "
                f"overall={overall:.2%}  ({total_s}/{total_n})  [{parts}]"
            )

        return True
