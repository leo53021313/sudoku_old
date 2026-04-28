"""SudokuEvalCallback — random-sample eval (observational)."""

from __future__ import annotations
import json
import os
from pathlib import Path

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

from reasoner.data_pkg.pool_db import PuzzlePoolDB
from reasoner.env.sudoku_gym_env import SudokuGymEnv
from reasoner.solver_ext.backtracking import solve


def _log_failure_record(path: str, record: dict) -> None:
    def _default(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(f"Not JSON serialisable: {type(o)}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=_default))
        f.write("\n")


class SudokuEvalCallback(BaseCallback):
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
        self._failures_path: str | None = None

    def _init_callback(self) -> None:
        self._eval_env = SudokuGymEnv(db_path=self._db_path)

    def _on_training_end(self) -> None:
        self._eval_env.close()

    def _resolve_failures_path(self) -> str:
        if self._failures_path is not None:
            return self._failures_path
        log_dir = getattr(self.logger, "dir", None) or "."
        self._failures_path = os.path.join(log_dir, "eval_failures.jsonl")
        return self._failures_path

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_eval < self._eval_freq:
            return True
        self._last_eval = self.num_timesteps

        try:
            db = PuzzlePoolDB(self._db_path)
            total_s, total_n = 0, 0
            level_rates: dict[int, float] = {}

            for diff in self._difficulties:
                puzzles = db.fetch_random_puzzles(level=diff, n=self._n_episodes)
                successes: list[bool] = []
                for row in puzzles:
                    board = np.array(
                        PuzzlePoolDB.string_to_board(row["puzzle"]), dtype=np.int8
                    )
                    sol = solve(board)
                    if sol is None:
                        continue
                    obs, _ = self._eval_env.reset(options={
                        "board": board.tolist(),
                        "solution": sol.tolist(),
                        "difficulty": diff,
                    })
                    done = False
                    info: dict = {}
                    while not done:
                        masks = self._eval_env.action_masks()[np.newaxis]
                        action, _ = self.model.predict(
                            obs[np.newaxis], action_masks=masks, deterministic=True
                        )
                        obs, _, terminated, truncated, info = self._eval_env.step(int(action[0]))
                        done = terminated or truncated
                    successes.append(bool(info.get("is_success", False)))

                rate = float(np.mean(successes)) if successes else 0.0
                level_rates[diff] = rate
                total_s += sum(successes)
                total_n += len(successes)

            for diff in self._difficulties:
                self.logger.record(f"eval/success_rate_L{diff}", level_rates[diff])
            overall = total_s / max(total_n, 1)
            self.logger.record("eval/success_rate_overall", overall)

            if self.verbose >= 1:
                parts = ", ".join(f"L{d}={level_rates[d]:.0%}" for d in self._difficulties)
                print(
                    f"[Eval] Step {self.num_timesteps:,}: overall={overall:.2%} "
                    f"({total_s}/{total_n})  [{parts}]"
                )
        except Exception as e:
            if self.verbose >= 1:
                print(f"[SudokuEvalCallback] eval failed at step {self.num_timesteps}: {e}")

        return True
