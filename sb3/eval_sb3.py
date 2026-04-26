# eval_sb3.py
"""
Evaluate a trained SudokuMaskablePPO checkpoint against Sudoku puzzles.

Usage:
    python eval_sb3.py --model models/sudoku_sb3_latest.zip
    python eval_sb3.py --model models/foo.zip --eval-set reserved --n-puzzles 50
    python eval_sb3.py --model models/foo.zip --debug-n 3
    python eval_sb3.py --model models/foo.zip --difficulty 1,2
"""

from __future__ import annotations

import argparse
import os

import numpy as np

from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.envs.sudoku_solver import solve
from app.rl.models.sudoku_ppo import SudokuMaskablePPO
from app.rl.eval.puzzle_set import EvalPuzzleSet
from app.data.pool_db import PuzzlePoolDB

DB_PATH       = "../data/puzzle_pool.db"
RESERVED_PATH = "data/eval_puzzles.json"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sudoku SB3 Model Evaluation")
    p.add_argument("--model",         required=True,  help="Path to .zip checkpoint")
    p.add_argument("--vecnorm",       default=None,   help="Path to _vecnorm.pkl (optional, currently unused)")
    p.add_argument("--eval-set",      default="random", choices=["random", "reserved"])
    p.add_argument("--n-puzzles",     type=int, default=20, help="Puzzles per difficulty")
    p.add_argument("--difficulty",    default="1,2,3,4",   help="Comma-separated levels")
    p.add_argument("--debug-n",       type=int, default=0, help="ASCII viz for first N failures")
    p.add_argument("--db-path",       default=DB_PATH)
    p.add_argument("--reserved-path", default=RESERVED_PATH)
    p.add_argument("--device",        default="cpu")
    return p.parse_args()


# ── Puzzle loading ──────────────────────────────────────────────────────────

def _get_random_puzzles(
    db_path: str, difficulty: int, n: int
) -> list[tuple[np.ndarray, np.ndarray]]:
    db = PuzzlePoolDB(db_path)
    rows = db.fetch_random_puzzles(level=difficulty, n=n)
    result = []
    for row in rows:
        board = np.array(PuzzlePoolDB.string_to_board(row["puzzle"]), dtype=np.int8)
        sol = solve(board)
        if sol is not None:
            result.append((board, sol))
    return result


# ── Eval loop ───────────────────────────────────────────────────────────────

def _run_episode(
    model: SudokuMaskablePPO,
    env: SudokuGymEnv,
    board: np.ndarray,
    solution: np.ndarray,
    difficulty: int,
) -> dict:
    initial_board = board.copy()
    obs, _ = env.reset(options={
        "board": board,
        "solution": solution,
        "difficulty": difficulty,
    })
    total_reward = 0.0
    steps = 0
    done = False

    while not done:
        masks = env.action_masks()[np.newaxis]          # (1, 729)
        action, _ = model.predict(
            obs[np.newaxis],                            # (1, 9, 9, 9)
            action_masks=masks,
            deterministic=True,
        )
        obs, reward, terminated, truncated, info = env.step(int(action[0]))
        total_reward += reward
        steps += 1
        done = terminated or truncated

    return {
        "success":       info["is_success"],
        "steps":         steps,
        "reward":        total_reward,
        "wrong":         info["wrong_count"],
        "initial_board": initial_board,
        "final_board":   env.board.copy(),
    }


# ── ASCII visualization ─────────────────────────────────────────────────────

def _board_row_str(board: np.ndarray, r: int) -> str:
    parts = []
    for c in range(9):
        v = board[r, c]
        parts.append(f" {'.' if v == 0 else v} ")
        if c in (2, 5):
            parts.append("│")
    return "".join(parts)


def _print_debug(i: int, difficulty: int, result: dict) -> None:
    sep = "─────────┼─────────┼─────────"
    print(
        f"\n── Debug: L{difficulty} failure #{i+1} "
        f"({result['steps']} steps, {result['wrong']} wrong fills) ──"
    )
    print("Initial board:               Final board:")
    for r in range(9):
        init_str  = _board_row_str(result["initial_board"], r)
        final_str = _board_row_str(result["final_board"],   r)
        print(f"{init_str}   {final_str}")
        if r in (2, 5):
            print(f"{sep}  {sep}")
    correct = result["steps"] - result["wrong"]
    print(f"Wrong fills: {result['wrong']}  |  Correct: {correct}/{result['steps']}")


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    difficulties = [int(d) for d in args.difficulty.split(",")]

    print(f"\n=== Sudoku Eval — {args.model} ===")
    print(
        f"Eval set: {args.eval_set}  |  "
        f"{args.n_puzzles} puzzles/difficulty  |  "
        f"Difficulties: {' '.join(f'L{d}' for d in difficulties)}\n"
    )

    model = SudokuMaskablePPO.load(args.model, device=args.device)
    env   = SudokuGymEnv(db_path=args.db_path)

    eval_set = (
        EvalPuzzleSet(args.reserved_path, args.db_path, args.n_puzzles)
        if args.eval_set == "reserved"
        else None
    )

    results_per_diff: dict[int, list[dict]] = {}
    debug_failures: list[tuple[int, dict]] = []

    for difficulty in difficulties:
        if eval_set is not None:
            puzzles = eval_set.get_puzzles(difficulty)
        else:
            puzzles = _get_random_puzzles(args.db_path, difficulty, args.n_puzzles)

        diff_results = []
        for board, solution in puzzles:
            result = _run_episode(model, env, board, solution, difficulty)
            diff_results.append(result)
            if not result["success"] and len(debug_failures) < args.debug_n:
                debug_failures.append((difficulty, result))
        results_per_diff[difficulty] = diff_results

    # ── Stats table ──────────────────────────────────────────────────────────
    col = f"{'Difficulty':<12} {'Success':<14} {'Avg Steps':<12} {'Avg Reward'}"
    sep = "─" * len(col)
    print(col)
    print(sep)

    total_success = total_puzzles = 0
    sum_steps = sum_reward = 0.0

    for d in difficulties:
        res = results_per_diff[d]
        n   = len(res)
        s   = sum(r["success"] for r in res)
        avg_steps  = sum(r["steps"]  for r in res) / max(n, 1)
        avg_reward = sum(r["reward"] for r in res) / max(n, 1)
        pct = 100 * s // max(n, 1)
        print(
            f"L{d:<11} {s}/{n}  {pct:>3}%   "
            f"{avg_steps:>8.1f}   {avg_reward:>10.1f}"
        )
        total_success += s
        total_puzzles += n
        sum_steps  += avg_steps
        sum_reward += avg_reward

    print(sep)
    n_diffs = len(difficulties)
    overall_pct = 100 * total_success // max(total_puzzles, 1)
    print(
        f"{'Overall':<12} {total_success}/{total_puzzles}  {overall_pct:>3}%   "
        f"{sum_steps/n_diffs:>8.1f}   {sum_reward/n_diffs:>10.1f}"
    )

    # ── Debug boards ─────────────────────────────────────────────────────────
    for i, (diff, result) in enumerate(debug_failures):
        _print_debug(i, diff, result)


if __name__ == "__main__":
    main()
