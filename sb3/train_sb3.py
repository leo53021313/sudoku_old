# train_sb3.py
# -*- coding: utf-8 -*-
"""
Entry point for the SB3-based Sudoku RL training system.

Usage:
    python train_sb3.py
    python train_sb3.py --timesteps 2000000 --n-envs 8
    python train_sb3.py --load-model models/sudoku_sb3_latest.zip
    python train_sb3.py --no-teacher --n-envs 4

Key design:
  - 8 parallel SubprocVecEnv environments for 8× sample throughput
  - MaskablePPO with action masking (no illegal fills)
  - Dense solution-guided reward (technique detection + correctness at every fill)
  - 4-stage curriculum: L1-only → mixed L1-L4
  - Constraint-head network reused from SudokuPPONet via SudokuFeaturesExtractor
  - BC teacher loss (optional, enabled by default)
"""

from __future__ import annotations

import argparse
import os
import sys

import torch
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.utils import LinearSchedule

from app.rl.envs.sudoku_gym_env import SudokuGymEnv
from app.rl.models.features_extractor import SudokuFeaturesExtractor
from app.rl.models.sudoku_ppo import SudokuMaskablePPO
from app.rl.curriculum.callback import CurriculumCallback, CURRICULUM_STAGES


DB_PATH    = "../data/puzzle_pool.db"
MODEL_DIR  = "models"
MODEL_NAME = "sudoku_sb3_latest"
LOG_DIR    = "./runs/sudoku_sb3"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sudoku SB3 PPO Training")
    p.add_argument("--timesteps",    type=int,   default=2_000_000)
    p.add_argument("--n-envs",       type=int,   default=8)
    p.add_argument("--device",       type=str,   default="auto")
    p.add_argument("--load-model",   type=str,   default=None,
                   help="Path to .zip checkpoint to resume from")
    p.add_argument("--no-teacher",   action="store_true",
                   help="Disable BC teacher loss")
    p.add_argument("--max-wrong",    type=int,   default=5,
                   help="Max wrong fills before episode terminates")
    p.add_argument("--no-vecnorm",   action="store_true",
                   help="Disable VecNormalize reward normalization")
    p.add_argument("--verbose",      type=int,   default=1)
    return p.parse_args()


def make_env_fn(db_path: str, max_wrong: int):
    def _init():
        return SudokuGymEnv(
            db_path=db_path,
            difficulty=1,         # overridden by CurriculumCallback
            max_wrong_fills=max_wrong,
            max_steps=300,
        )
    return _init


def main() -> None:
    args = parse_args()

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR,   exist_ok=True)

    # ── Vectorized envs ───────────────────────────────────────────────────────
    vec_env = make_vec_env(
        make_env_fn(DB_PATH, args.max_wrong),
        n_envs=args.n_envs,
        vec_env_cls=SubprocVecEnv,
    )

    if not args.no_vecnorm:
        vec_env = VecNormalize(
            vec_env,
            norm_obs=False,
            norm_reward=True,
            clip_reward=50.0,
        )

    # ── Policy kwargs: constraint-head network ────────────────────────────────
    policy_kwargs = dict(
        features_extractor_class=SudokuFeaturesExtractor,
        features_extractor_kwargs={"features_dim": 192},
        net_arch=[],   # features extractor handles all; no additional MLP layers
    )

    # ── Model ─────────────────────────────────────────────────────────────────
    bc_coef = 0.0 if args.no_teacher else 1.0

    if args.load_model:
        print(f"[train_sb3] Resuming from: {args.load_model}")
        model = SudokuMaskablePPO.load(
            args.load_model,
            env=vec_env,
            device=args.device,
            bc_coef=bc_coef,
        )
    else:
        model = SudokuMaskablePPO(
            policy="CnnPolicy",
            env=vec_env,
            n_steps=512,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            learning_rate=LinearSchedule(3e-4, 1e-5, end_fraction=1.0),
            policy_kwargs=policy_kwargs,
            tensorboard_log=LOG_DIR,
            device=args.device,
            verbose=args.verbose,
            bc_coef=bc_coef,
            mrv_prob_init=0.80,
        )

    if args.verbose >= 1:
        total_params = sum(p.numel() for p in model.policy.parameters())
        print(f"[train_sb3] Policy parameters: {total_params:,}")
        print(f"[train_sb3] Device: {model.device}")
        print(f"[train_sb3] Envs: {args.n_envs}  Steps/update: {args.n_envs * 512}")
        print(f"[train_sb3] BC teacher: {'disabled' if args.no_teacher else 'enabled'}")
        print(f"[train_sb3] Timesteps: {args.timesteps:,}")

    # ── Callbacks ─────────────────────────────────────────────────────────────
    curriculum = CurriculumCallback(
        stages=CURRICULUM_STAGES,
        window=100,
        verbose=args.verbose,
    )
    checkpoint = CheckpointCallback(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="sudoku_sb3_ckpt",
        verbose=args.verbose,
    )

    # ── Training ──────────────────────────────────────────────────────────────
    model.learn(
        total_timesteps=args.timesteps,
        callback=[curriculum, checkpoint],
        reset_num_timesteps=args.load_model is None,
    )

    save_path = os.path.join(MODEL_DIR, MODEL_NAME)
    model.save(save_path)
    if not args.no_vecnorm and isinstance(vec_env, VecNormalize):
        vec_env.save(save_path + "_vecnorm.pkl")
    print(f"[train_sb3] Saved → {save_path}.zip")


if __name__ == "__main__":
    main()
