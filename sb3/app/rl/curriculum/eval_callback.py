# app/rl/curriculum/eval_callback.py
# -*- coding: utf-8 -*-
"""
SudokuEvalCallback — fixed held-out eval using action-masked prediction.

Runs N deterministic episodes per difficulty level every eval_freq steps.
Logs eval/success_rate_L{d} and eval/success_rate_overall to TensorBoard.
Does NOT use EvalCallback from SB3 because that doesn't pass action masks.

Phase 1 addition: each failure appends one JSON line to <log_dir>/eval_failures.jsonl
so the rollout/eval success-rate divergence can be diagnosed offline.

Phase 1.5 fix: pulls puzzles via fetch_random_puzzles (read-only) instead of
env.reset() / fetch_one_puzzle_for_training (which is biased toward
"easy-for-this-model" puzzles via best_empty ASC ordering).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

from app.data.pool_db import PuzzlePoolDB
from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.envs.sudoku_solver import solve


def _log_failure_record(path: str, record: dict) -> None:
    """Append one JSONL record. Coerces numpy scalars/arrays via json default."""
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
        self._failures_path: str | None = None  # set on first eval

    def _init_callback(self) -> None:
        self._eval_env = SudokuGymEnv(db_path=self._db_path)

    def _on_training_end(self) -> None:
        self._eval_env.close()

    def _resolve_failures_path(self) -> str:
        """Locate failures.jsonl relative to the active TB run directory."""
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
                rows = db.fetch_random_puzzles(level=diff, n=self._n_episodes)
                successes = []

                for row in rows:
                    board = np.array(
                        PuzzlePoolDB.string_to_board(row["puzzle"]),
                        dtype=np.int8,
                    )
                    sol = solve(board)
                    if sol is None:
                        continue  # skip unsolvable rows defensively
                    obs, _ = self._eval_env.reset(options={
                        "board": board,
                        "solution": sol,
                        "difficulty": diff,
                    })
                    history: list[tuple[int, int, int, int, float]] = []
                    done = False
                    while not done:
                        masks = self._eval_env.action_masks()[np.newaxis]
                        action, _ = self.model.predict(
                            obs[np.newaxis],
                            action_masks=masks,
                            deterministic=True,
                        )
                        a_int = int(action[0])
                        r, c, v = self._eval_env._decode(a_int)
                        correct_v = int(sol[r, c])
                        obs, _, terminated, truncated, info = self._eval_env.step(a_int)
                        teacher_q = float(info.get("teacher_quality", 0.0))
                        history.append((r, c, correct_v, v, teacher_q))
                        done = terminated or truncated
                    is_success = info["is_success"]
                    successes.append(is_success)

                    if not is_success:
                        first_wrong = next(
                            (i for i, (_, _, cv, pv, _) in enumerate(history) if cv != pv),
                            len(history) - 1,
                        )
                        r, c, cv, pv, tq = history[first_wrong]
                        _log_failure_record(self._resolve_failures_path(), {
                            "step": int(self.num_timesteps),
                            "difficulty": int(diff),
                            "first_wrong_step": int(first_wrong),
                            "model_picked_cell": [int(r), int(c)],
                            "model_picked_value": int(pv),
                            "correct_value": int(cv),
                            "teacher_quality_at_that_step": float(tq),
                        })

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
                    f"[Eval] Step {self.num_timesteps:,}: "
                    f"overall={overall:.2%}  ({total_s}/{total_n})  [{parts}]"
                )

        except Exception as e:
            if self.verbose >= 1:
                print(f"[SudokuEvalCallback] eval failed at step {self.num_timesteps}: {e}")

        return True
