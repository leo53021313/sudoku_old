"""Reasoner — pure RL training entry.

Usage:
    cd c:/Users/student/Desktop/sudoku_old
    python -m reasoner.train.train
    python -m reasoner.train.train --timesteps 1000000 --n-envs 8
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

# Force UTF-8 output (Windows cp950 fix)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import torch
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.utils import LinearSchedule

from reasoner.env.sudoku_gym_env import SudokuGymEnv
from reasoner.model.features_extractor import SudokuFeaturesExtractor
from reasoner.train.ppo import SudokuMaskablePPO
from reasoner.curriculum.callback import TechniqueCurriculumCallback
from reasoner.eval.eval_callback import SudokuEvalCallback
from reasoner.eval.reserved_eval_callback import ReservedEvalCallback


_REPO_ROOT  = Path(__file__).resolve().parents[2]
DB_PATH     = str(_REPO_ROOT / "data" / "puzzle_pool.db")
LABELS_PATH = str(_REPO_ROOT / "reasoner" / "data" / "puzzle_techniques.json")
EVAL_PATH   = str(_REPO_ROOT / "reasoner" / "data" / "eval_puzzles.json")
MODEL_DIR   = str(_REPO_ROOT / "reasoner" / "models")
LOG_DIR     = str(_REPO_ROOT / "reasoner" / "runs")
MODEL_NAME  = "reasoner_latest"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--timesteps", type=int, default=2_000_000)
    p.add_argument("--n-envs",    type=int, default=8)
    p.add_argument("--device",    type=str, default="auto")
    p.add_argument("--load-model", type=str, default=None)
    p.add_argument("--max-wrong",  type=int, default=20)
    p.add_argument("--no-vecnorm", action="store_true")
    p.add_argument("--verbose",    type=int, default=1)
    return p.parse_args()


def make_env_fn(db_path: str, max_wrong: int):
    def _init():
        return SudokuGymEnv(
            db_path=db_path,
            difficulty=1,
            max_wrong_fills=max_wrong,
            max_steps=300,
        )
    return _init


def main():
    args = parse_args()

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.exists(LABELS_PATH):
        sys.exit(
            f"[train] FATAL: puzzle_techniques.json not found at {LABELS_PATH}.\n"
            f"Run: python -m reasoner.solver.label_puzzles --db {DB_PATH} --out {LABELS_PATH} --verbose"
        )
    with open(LABELS_PATH, encoding="utf-8") as f:
        puzzle_labels = json.load(f)

    # Vec envs
    vec_env = make_vec_env(
        make_env_fn(DB_PATH, args.max_wrong),
        n_envs=args.n_envs,
        vec_env_cls=SubprocVecEnv,
    )
    if not args.no_vecnorm:
        vec_env = VecNormalize(vec_env, norm_obs=False, norm_reward=True, clip_reward=50.0)

    # Policy: ConstraintHead
    policy_kwargs = dict(
        features_extractor_class=SudokuFeaturesExtractor,
        features_extractor_kwargs={"features_dim": 192},
        net_arch={"pi": [], "vf": [128]},
    )

    # Model — pure PPO, no BC
    if args.load_model:
        print(f"[train] Resuming from: {args.load_model}")
        model = SudokuMaskablePPO.load(
            args.load_model, env=vec_env, device=args.device,
        )
    else:
        model = SudokuMaskablePPO(
            policy="CnnPolicy",
            env=vec_env,
            n_steps=512,
            batch_size=64,
            n_epochs=4,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.1,
            ent_coef=0.02,
            vf_coef=0.5,
            max_grad_norm=0.5,
            learning_rate=LinearSchedule(3e-4, 1e-5, end_fraction=1.0),
            policy_kwargs=policy_kwargs,
            tensorboard_log=LOG_DIR,
            device=args.device,
            verbose=args.verbose,
        )

    if args.verbose >= 1:
        total_params = sum(p.numel() for p in model.policy.parameters())
        print(f"[train] Policy parameters: {total_params:,}")
        print(f"[train] Device: {model.device}")
        print(f"[train] Envs: {args.n_envs}  Steps/update: {args.n_envs * 512}")

    # Callbacks
    curriculum = TechniqueCurriculumCallback(
        puzzle_labels=puzzle_labels,
        eval_threshold=0.80,
        consec_pass_required=3,
        verbose=args.verbose,
    )
    checkpoint = CheckpointCallback(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="reasoner_ckpt",
        verbose=args.verbose,
    )
    eval_cb = SudokuEvalCallback(
        db_path=DB_PATH,
        eval_freq=50_000,
        n_episodes=20,
        difficulties=(1, 2, 3, 4),
        verbose=args.verbose,
    )
    reserved_eval = ReservedEvalCallback(
        json_path=EVAL_PATH,
        db_path=DB_PATH,
        eval_freq=50_000,
        difficulties=(1, 2, 3, 4),
        verbose=args.verbose,
    )

    model.learn(
        total_timesteps=args.timesteps,
        callback=[curriculum, checkpoint, eval_cb, reserved_eval],
        reset_num_timesteps=args.load_model is None,
    )

    save_path = os.path.join(MODEL_DIR, MODEL_NAME)
    model.save(save_path)
    if not args.no_vecnorm and isinstance(vec_env, VecNormalize):
        vec_env.save(save_path + "_vecnorm.pkl")
    print(f"[train] Saved → {save_path}.zip")


if __name__ == "__main__":
    main()
