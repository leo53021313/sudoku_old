# app/rl/curriculum/reserved_eval_callback.py
# -*- coding: utf-8 -*-
"""
ReservedEvalCallback — every eval_freq steps, evaluate the policy against the
strict held-out reserved set (data/eval_puzzles.json) and log eval/reserved_L*
+ eval/reserved_overall to TensorBoard.

Unlike SudokuEvalCallback (which samples random puzzles from the training pool
and may overlap with what the model has seen), this callback always uses the
fixed reserved set that was set aside before training started -- a true
generalisation signal.

Never aborts training -- always returns True. Purely observational.
"""

from __future__ import annotations

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.eval.puzzle_set import EvalPuzzleSet


class ReservedEvalCallback(BaseCallback):
    """
    Parameters
    ----------
    json_path : str
        Path to reserved eval JSON file.
    db_path : str
        Fallback DB path (only used by EvalPuzzleSet if JSON is missing).
    eval_freq : int
        Run reserved eval every this many timesteps (default 50_000).
    difficulties : tuple[int, ...]
        Difficulty levels to evaluate.
    verbose : int
    """

    def __init__(
        self,
        json_path: str,
        db_path: str,
        eval_freq: int = 50_000,
        difficulties: tuple[int, ...] = (1, 2, 3, 4),
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self._json_path    = json_path
        self._db_path      = db_path
        self._eval_freq    = eval_freq
        self._difficulties = difficulties
        self._last_eval    = 0
        self._eval_env: SudokuGymEnv | None = None
        self._puzzle_set: EvalPuzzleSet | None = None

    def _init_callback(self) -> None:
        self._eval_env = SudokuGymEnv(db_path=self._db_path)
        self._puzzle_set = EvalPuzzleSet(
            json_path=self._json_path,
            db_path=self._db_path,
        )

    def _on_training_end(self) -> None:
        if self._eval_env is not None:
            self._eval_env.close()

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_eval < self._eval_freq:
            return True
        self._last_eval = self.num_timesteps

        try:
            total_s, total_n = 0, 0
            level_rates: dict[int, float] = {}

            for diff in self._difficulties:
                puzzles = self._puzzle_set.get_puzzles(diff)
                successes: list[bool] = []
                for board, solution in puzzles:
                    obs, _ = self._eval_env.reset(options={
                        "board": board,
                        "solution": solution,
                        "difficulty": diff,
                    })
                    done = False
                    info: dict = {}
                    while not done:
                        masks = self._eval_env.action_masks()[np.newaxis]
                        action, _ = self.model.predict(
                            obs[np.newaxis],
                            action_masks=masks,
                            deterministic=True,
                        )
                        obs, _, terminated, truncated, info = self._eval_env.step(int(action[0]))
                        done = terminated or truncated
                    successes.append(bool(info.get("is_success", False)))

                rate = float(np.mean(successes)) if successes else 0.0
                level_rates[diff] = rate
                total_s += sum(successes)
                total_n += len(successes)

            for diff in self._difficulties:
                self.logger.record(f"eval/reserved_L{diff}", level_rates[diff])
            overall = total_s / max(total_n, 1)
            self.logger.record("eval/reserved_overall", overall)

            if self.verbose >= 1:
                parts = ", ".join(f"L{d}={level_rates[d]:.0%}" for d in self._difficulties)
                print(
                    f"[ReservedEval] Step {self.num_timesteps:,}: "
                    f"overall={overall:.2%}  ({total_s}/{total_n})  [{parts}]"
                )

        except Exception as e:
            if self.verbose >= 1:
                print(f"[ReservedEvalCallback] eval failed at step {self.num_timesteps}: {e}")

        # NEVER abort -- this callback is observational only
        return True
