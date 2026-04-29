"""Reasoner — pure RL training entry.

Usage:
    cd c:/Users/student/Desktop/sudoku_old
    python -m reasoner.train.train                                    # fresh run
    python -m reasoner.train.train --load-model auto                  # resume latest
    python -m reasoner.train.train --timesteps 100000000 --load-model auto

Resume semantics:
- `--load-model auto`     find newest reasoner_ckpt_*_steps.zip in MODEL_DIR
- `--load-model latest`   alias for `auto`
- `--load-model <path>`   load specific checkpoint
- model.zip side-cars (loaded automatically when present):
    <ckpt>_vecnorm.pkl     VecNormalize running stats
    <ckpt>_curriculum.json Curriculum stage state
- num_timesteps + LR schedule + optimizer state are restored from the .zip
  by SB3 itself; we only need to preserve VecNormalize and curriculum.
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
TB_LOG_NAME = "reasoner"  # consistent across resumes; SB3 will create reasoner_1, reasoner_2, ...
                          # all visible together when TB points at LOG_DIR.

_CKPT_PATTERN = re.compile(r"reasoner_ckpt_(\d+)_steps\.zip$")


def _find_latest_checkpoint(model_dir: str) -> str | None:
    """Find newest reasoner_ckpt_<N>_steps.zip in model_dir, or None."""
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
    """Periodic save of (model, VecNormalize, curriculum-state) trio.

    Replaces SB3's CheckpointCallback to ensure all training state is saved
    together so that --load-model auto can fully resume.
    """

    def __init__(
        self,
        save_freq: int,
        save_path: str,
        name_prefix: str,
        curriculum: TechniqueCurriculumCallback,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix
        self._curriculum = curriculum
        self._last_save: int | None = None  # set on _init_callback to num_timesteps
        os.makedirs(save_path, exist_ok=True)

    def _init_callback(self) -> None:
        # Anchor save schedule to current num_timesteps so resume doesn't
        # spuriously fire a save in the first step.
        self._last_save = int(self.num_timesteps)

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_save < self.save_freq:
            return True
        self._last_save = self.num_timesteps

        base = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps")
        # 1. Model
        self.model.save(base + ".zip")
        # 2. VecNormalize sidecar (if wrapped)
        vec_env = self.model.get_vec_normalize_env()
        if isinstance(vec_env, VecNormalize):
            vec_env.save(base + "_vecnorm.pkl")
        # 3. Curriculum state sidecar
        curr_state = {
            "stage_idx":         self._curriculum._stage_idx,
            "consec_pass":       self._curriculum._consec_pass,
            "stage_entry_step":  self._curriculum._stage_entry_step,
            "stage_entry_rate":  self._curriculum._stage_entry_rate,
        }
        with open(base + "_curriculum.json", "w", encoding="utf-8") as f:
            json.dump(curr_state, f, indent=2)

        if self.verbose >= 1:
            print(f"[Checkpoint] step={self.num_timesteps:,} -> {base}.zip (+vecnorm + curriculum)")
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

    if not os.path.exists(LABELS_PATH):
        sys.exit(
            f"[train] FATAL: puzzle_techniques.json not found at {LABELS_PATH}.\n"
            f"Run: python -m reasoner.solver.label_puzzles --db {DB_PATH} --out {LABELS_PATH} --verbose"
        )
    with open(LABELS_PATH, encoding="utf-8") as f:
        puzzle_labels = json.load(f)

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
        net_arch={"pi": [], "vf": [128]},
    )

    # Model — pure PPO, no BC
    if load_path is not None:
        print(f"[train] Resuming from: {load_path}")
        model = SudokuMaskablePPO.load(
            load_path, env=vec_env, device=args.device,
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
        print(f"[train] num_timesteps at start: {model.num_timesteps:,}")
        print(f"[train] target num_timesteps:   {args.timesteps:,}")
        if load_path and model.num_timesteps >= args.timesteps:
            print(f"[train] WARN: model already past --timesteps target; will exit immediately. "
                  "Increase --timesteps to keep training.")

    # Callbacks
    curriculum = TechniqueCurriculumCallback(
        puzzle_labels=puzzle_labels,
        eval_threshold=0.80,
        consec_pass_required=3,
        verbose=args.verbose,
    )

    # Restore curriculum state if sidecar exists
    if load_path is not None:
        curr_path = load_path.replace(".zip", "_curriculum.json")
        if os.path.exists(curr_path):
            with open(curr_path, encoding="utf-8") as f:
                state = json.load(f)
            curriculum._stage_idx        = int(state.get("stage_idx", 0))
            curriculum._consec_pass      = int(state.get("consec_pass", 0))
            curriculum._stage_entry_step = int(state.get("stage_entry_step", 0))
            curriculum._stage_entry_rate = float(state.get("stage_entry_rate", 0.0))
            if args.verbose >= 1:
                print(f"[train] Curriculum restored: stage={curriculum.current_stage} "
                      f"consec_pass={curriculum._consec_pass}")

    checkpoint = CheckpointWithSidecars(
        save_freq=50_000,
        save_path=MODEL_DIR,
        name_prefix="reasoner_ckpt",
        curriculum=curriculum,
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

    try:
        model.learn(
            total_timesteps=args.timesteps,
            callback=[curriculum, checkpoint, eval_cb, reserved_eval],
            reset_num_timesteps=(load_path is None),
            tb_log_name=TB_LOG_NAME,
        )
    finally:
        # Always save on exit (Ctrl-C, exception, normal completion)
        save_path = os.path.join(MODEL_DIR, MODEL_NAME)
        model.save(save_path)
        sidecars = []
        if isinstance(vec_env, VecNormalize):
            vec_env.save(save_path + "_vecnorm.pkl")
            sidecars.append("vecnorm")
        # Curriculum sidecar (always save)
        curr_state = {
            "stage_idx":         curriculum._stage_idx,
            "consec_pass":       curriculum._consec_pass,
            "stage_entry_step":  curriculum._stage_entry_step,
            "stage_entry_rate":  curriculum._stage_entry_rate,
        }
        with open(save_path + "_curriculum.json", "w", encoding="utf-8") as f:
            json.dump(curr_state, f, indent=2)
        sidecars.append("curriculum")
        sidecar_str = " + ".join(sidecars) if sidecars else "no sidecars"
        print(f"[train] Saved -> {save_path}.zip ({sidecar_str})")


if __name__ == "__main__":
    main()
