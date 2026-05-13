"""Apprentice — pure RL training entry.

Usage:
    cd c:/Users/student/Desktop/sudoku_old
    python -m apprentice.train.train                                    # fresh run
    python -m apprentice.train.train --load-model auto                  # resume latest
    python -m apprentice.train.train --timesteps 100000000 --load-model auto

Resume semantics:
- `--load-model auto`     find newest apprentice_ckpt_*_steps.zip in MODEL_DIR
- `--load-model latest`   alias for `auto`
- `--load-model <path>`   load specific checkpoint
- VecNormalize running stats are saved alongside each checkpoint as
  <ckpt>_vecnorm.pkl and reloaded automatically.
- num_timesteps + LR schedule + optimizer state are restored from the .zip
  by SB3 itself.

The DB sampling does NOT use a stage curriculum; the env samples uniformly
from all puzzles at the requested websudoku difficulty (level 1-4).
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

# Force UTF-8 output (Windows cp950 fix)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

import torch
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.utils import LinearSchedule

from apprentice.env.sudoku_gym_env import SudokuGymEnv
from apprentice.model.features_extractor import SudokuFeaturesExtractor
from apprentice.train.ppo import SudokuMaskablePPO
from apprentice.train.curriculum_controller import CurriculumController
from apprentice.train.curriculum_callback import CurriculumCallback
from apprentice.eval.eval_callback import SudokuEvalCallback
from apprentice.eval.reserved_eval_callback import ReservedEvalCallback


_REPO_ROOT  = Path(__file__).resolve().parents[2]
DB_PATH     = str(_REPO_ROOT / "data" / "puzzle_pool.db")
EVAL_PATH   = str(_REPO_ROOT / "apprentice" / "data" / "eval_puzzles.json")
MODEL_DIR   = str(_REPO_ROOT / "apprentice" / "models")
LOG_DIR     = str(_REPO_ROOT / "apprentice" / "runs")
MODEL_NAME  = "apprentice_latest"
TB_LOG_NAME = "apprentice"  # consistent across resumes; SB3 will create apprentice_1, apprentice_2, ...
                            # all visible together when TB points at LOG_DIR.
CURRICULUM_CONFIG = str(_REPO_ROOT / "apprentice" / "configs" / "curriculum.json")

_CKPT_PATTERN = re.compile(r"apprentice_ckpt_(\d+)_steps\.zip$")


def _find_latest_checkpoint(model_dir: str) -> str | None:
    """Find newest apprentice_ckpt_<N>_steps.zip in model_dir, or None."""
    candidates: list[tuple[int, str]] = []
    if not os.path.isdir(model_dir):
        return None
    for fn in os.listdir(model_dir):
        m = _CKPT_PATTERN.match(fn)
        if m:
            candidates.append((int(m.group(1)), os.path.join(model_dir, fn)))
    if not candidates:
        return None
    candidates.sort()
    return candidates[-1][1]


class CheckpointWithSidecars(BaseCallback):
    """Periodic save of (model, VecNormalize) pair.

    Replaces SB3's CheckpointCallback so that --load-model auto can fully
    resume — VecNormalize stats need to be saved alongside the model zip
    or reward normalization restarts from identity on each resume.
    """

    def __init__(
        self,
        save_freq: int,
        save_path: str,
        name_prefix: str,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix
        self._last_save: int | None = None
        self._associated_curriculum_cbs: list = []
        os.makedirs(save_path, exist_ok=True)

    def add_curriculum_callback(self, cb) -> None:
        self._associated_curriculum_cbs.append(cb)

    def _init_callback(self) -> None:
        # Anchor save schedule to current num_timesteps so resume doesn't
        # spuriously fire a save in the first step.
        self._last_save = int(self.num_timesteps)

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_save < self.save_freq:
            return True
        self._last_save = self.num_timesteps

        base = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps")
        self.model.save(base + ".zip")
        sidecar_tags: list[str] = []
        vec_env = self.model.get_vec_normalize_env()
        if isinstance(vec_env, VecNormalize):
            vec_env.save(base + "_vecnorm.pkl")
            sidecar_tags.append("vecnorm")

        # Also save curriculum state alongside ckpt — look up CurriculumCallback in self.callbacks
        for cb in getattr(self, "_associated_curriculum_cbs", []):
            if cb is not None and cb.controller is not None:
                cb.controller.save(base + "_curriculum.json")
                sidecar_tags.append("curriculum")
                break

        tag = ("+" + " +".join(sidecar_tags)) if sidecar_tags else ""
        if self.verbose >= 1:
            print(f"[Checkpoint] step={self.num_timesteps:,} -> {base}.zip {tag}")
        return True


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--timesteps", type=int, default=2_000_000,
                   help="Final num_timesteps target (not 'add this many'). On resume, "
                        "training stops when num_timesteps reaches this value.")
    p.add_argument("--n-envs",    type=int, default=8)
    p.add_argument("--device",    type=str, default="auto")
    p.add_argument("--load-model", type=str, default=None,
                   help="'auto'/'latest' to auto-find newest ckpt, or explicit path, or omit for fresh run.")
    p.add_argument("--max-wrong",  type=int, default=20)
    p.add_argument("--no-vecnorm", action="store_true")
    p.add_argument("--verbose",    type=int, default=1)
    p.add_argument("--curriculum-config", type=str, default=CURRICULUM_CONFIG,
                   help="Path to curriculum config JSON")
    p.add_argument("--no-curriculum", action="store_true",
                   help="Disable adaptive curriculum entirely (env runs with no target_empty)")
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


def _resolve_load_path(load_arg: str | None) -> str | None:
    """Resolve --load-model arg into an actual path, or None for fresh run."""
    if load_arg is None:
        return None
    if load_arg in ("auto", "latest"):
        path = _find_latest_checkpoint(MODEL_DIR)
        if path is None:
            print(f"[train] --load-model {load_arg}: no checkpoints in {MODEL_DIR}, starting fresh")
            return None
        print(f"[train] --load-model {load_arg} -> {path}")
        return path
    if not os.path.exists(load_arg):
        sys.exit(f"[train] FATAL: --load-model path not found: {load_arg}")
    return load_arg


def main():
    args = parse_args()

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    load_path = _resolve_load_path(args.load_model)

    # Vec envs
    vec_env = make_vec_env(
        make_env_fn(DB_PATH, args.max_wrong),
        n_envs=args.n_envs,
        vec_env_cls=SubprocVecEnv,
    )
    if not args.no_vecnorm:
        # If resuming AND a VecNormalize sidecar exists, load it.
        vecnorm_path = None
        if load_path is not None:
            cand = load_path.replace(".zip", "_vecnorm.pkl")
            if os.path.exists(cand):
                vecnorm_path = cand

        if vecnorm_path is not None:
            vec_env = VecNormalize.load(vecnorm_path, vec_env)
            # Set training=True so stats keep updating (load defaults to inference mode otherwise).
            vec_env.training = True
            vec_env.norm_reward = True
            print(f"[train] Loaded VecNormalize from {vecnorm_path}")
        else:
            vec_env = VecNormalize(
                vec_env, norm_obs=False, norm_reward=True, clip_reward=50.0,
            )
            if load_path is not None:
                print(f"[train] WARN: --load-model {load_path} has no VecNormalize sidecar; "
                      "starting reward stats fresh (this causes the TB jump artefact)")

    # Policy: ConstraintHead
    policy_kwargs = dict(
        features_extractor_class=SudokuFeaturesExtractor,
        features_extractor_kwargs={"features_dim": 192},
        net_arch={"pi": [128], "vf": [128, 128]},
    )

    # Model — pure PPO, no BC
    if load_path is not None:
        print(f"[apprentice] Resuming from: {load_path}")
        try:
            model = SudokuMaskablePPO.load(
                load_path, env=vec_env, device=args.device,
            )
        except RuntimeError as e:
            if "size mismatch" in str(e).lower():
                sys.exit(
                    f"[apprentice] FATAL: ckpt obs shape doesn't match current env "
                    f"observation_space={vec_env.observation_space.shape}. "
                    f"obs shape may have changed between training runs; must cold-start "
                    f"(omit --load-model). Underlying error: {e}"
                )
            raise
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
            ent_coef=0.05,
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
        print(f"[train] num_timesteps at start: {model.num_timesteps:,}")
        print(f"[train] target num_timesteps:   {args.timesteps:,}")
        if load_path and model.num_timesteps >= args.timesteps:
            print(f"[train] WARN: model already past --timesteps target; will exit immediately. "
                  "Increase --timesteps to keep training.")

    # Callbacks
    checkpoint = CheckpointWithSidecars(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="apprentice_ckpt",
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

    # Curriculum controller + callback
    if not args.no_curriculum:
        with open(args.curriculum_config, "r", encoding="utf-8") as f:
            curr_cfg = json.load(f)
        curriculum = CurriculumController(curr_cfg)

        # If resuming and a curriculum sidecar exists alongside the ckpt, load it
        if load_path is not None:
            curr_sidecar = load_path.replace(".zip", "_curriculum.json")
            if os.path.exists(curr_sidecar):
                curriculum.load(curr_sidecar)
                print(f"[apprentice] Loaded curriculum state from {curr_sidecar}")

        # Persistent sidecar: write next to MODEL_NAME on every save
        curriculum_sidecar = os.path.join(MODEL_DIR, MODEL_NAME + "_curriculum.json")
        curriculum_cb = CurriculumCallback(
            controller=curriculum,
            update_interval_steps=50_000,
            save_path=curriculum_sidecar,
            save_freq_steps=50_000,
            verbose=args.verbose,
        )
    else:
        curriculum_cb = None

    if curriculum_cb is not None:
        checkpoint.add_curriculum_callback(curriculum_cb)

    try:
        callbacks = [checkpoint, eval_cb, reserved_eval]
        if curriculum_cb is not None:
            callbacks.append(curriculum_cb)
        model.learn(
            total_timesteps=args.timesteps,
            callback=callbacks,
            reset_num_timesteps=(load_path is None),
            tb_log_name=TB_LOG_NAME,
        )
    finally:
        save_path = os.path.join(MODEL_DIR, MODEL_NAME)
        model.save(save_path)
        sidecars: list[str] = []
        if isinstance(vec_env, VecNormalize):
            vec_env.save(save_path + "_vecnorm.pkl")
            sidecars.append("vecnorm")
        if curriculum_cb is not None:
            curriculum_cb.controller.save(save_path + "_curriculum.json")
            sidecars.append("curriculum")
        sidecar_str = " + ".join(sidecars) if sidecars else "no sidecars"
        print(f"[apprentice] Saved -> {save_path}.zip ({sidecar_str})")


if __name__ == "__main__":
    main()
