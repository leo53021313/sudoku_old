"""measure_wrong — one-off per-episode error-rate measurement for a checkpoint.

Loads a trained apprentice checkpoint and runs deterministic (greedy) rollouts,
reporting per-episode wrong_count alongside success rate. Used to baseline the
current model before any error-reduction optimization.

NOTE: deterministic=True measures the policy's actual competence. Training's
rollout/ep_wrong_mean is from stochastic sampling (exploration) and will read
higher; the two are not directly comparable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

from apprentice.env.sudoku_gym_env import SudokuGymEnv
from apprentice.train.ppo import SudokuMaskablePPO
from apprentice.train.train import _find_latest_checkpoint, MODEL_DIR, DB_PATH


def measure(model, env, n_episodes: int, seed: int | None = None) -> dict:
    """Run n_episodes deterministic rollouts; return aggregate error stats.

    env must expose reset(seed=)/step(action)/action_masks() and put
    is_success / wrong_count / steps into the step info dict.
    All fields are 0 when n_episodes == 0.
    """
    successes: list[bool] = []
    wrongs: list[int] = []
    steps: list[int] = []

    for i in range(n_episodes):
        ep_seed = None if seed is None else seed + i
        obs, _ = env.reset(seed=ep_seed)
        done = False
        info: dict = {}
        while not done:
            masks = env.action_masks()[np.newaxis]
            action, _ = model.predict(
                obs[np.newaxis], action_masks=masks, deterministic=True
            )
            obs, _reward, terminated, truncated, info = env.step(int(action[0]))
            done = terminated or truncated
        successes.append(bool(info.get("is_success", False)))
        wrongs.append(int(info.get("wrong_count", 0)))
        steps.append(int(info.get("steps", 0)))

    return {
        "n_episodes": len(successes),
        "success_rate": sum(successes) / len(successes) if successes else 0.0,
        "mean_wrong": float(np.mean(wrongs)) if wrongs else 0.0,
        "max_wrong": int(max(wrongs)) if wrongs else 0,
        "mean_steps": float(np.mean(steps)) if steps else 0.0,
    }


def _read_curriculum_target(ckpt_path: str) -> int | None:
    """Read rounded target_empty from the ckpt's _curriculum.json sidecar."""
    side = ckpt_path.replace(".zip", "_curriculum.json")
    if not os.path.exists(side):
        return None
    with open(side, encoding="utf-8") as f:
        data = json.load(f)
    te = data.get("target_empty")
    return int(round(te)) if te is not None else None


def _print_row(label: str, stats: dict) -> None:
    print(
        f"{label:<16} "
        f"success={stats['success_rate']:6.1%}  "
        f"mean_wrong={stats['mean_wrong']:6.2f}  "
        f"max_wrong={stats['max_wrong']:3d}  "
        f"mean_steps={stats['mean_steps']:6.1f}  "
        f"(n={stats['n_episodes']})"
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Measure per-episode wrong-action rate of a checkpoint.")
    p.add_argument("--ckpt", type=str, default=None, help="Checkpoint path; default = newest in MODEL_DIR.")
    p.add_argument("--n-real", type=int, default=20, help="Episodes per real-puzzle difficulty (L1-L4).")
    p.add_argument("--n-curr", type=int, default=80, help="Episodes at the curriculum target_empty.")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def main() -> None:
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    ckpt = args.ckpt or _find_latest_checkpoint(MODEL_DIR)
    if ckpt is None:
        sys.exit(f"[measure] No checkpoint found in {MODEL_DIR}")
    print(f"[measure] Loading: {ckpt}")
    model = SudokuMaskablePPO.load(ckpt, device="cpu")

    print("\n=== Distribution 1: real full puzzles (target_empty=None) ===")
    for diff in (1, 2, 3, 4):
        # constructor already sets _difficulty_dist={diff:1.0} and target_empty=None
        env = SudokuGymEnv(db_path=DB_PATH, difficulty=diff)
        stats = measure(model, env, args.n_real, seed=args.seed)
        _print_row(f"REAL L{diff}", stats)

    print("\n=== Distribution 2: curriculum difficulty (difficulty=1, fill-back) ===")
    curr_target = _read_curriculum_target(ckpt)
    if curr_target is None:
        print("[measure] no curriculum sidecar; skipping curriculum-matched measurement")
    else:
        env = SudokuGymEnv(db_path=DB_PATH, difficulty=1)
        env.set_target_empty(curr_target)  # fill-back to the curriculum's target_empty
        stats = measure(model, env, args.n_curr, seed=args.seed)
        _print_row(f"CURR te={curr_target}", stats)


if __name__ == "__main__":
    main()
