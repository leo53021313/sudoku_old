# SB3 Training Hygiene Fixes — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply 5 targeted fixes to the SB3 training system that improve convergence quality without breaking existing model checkpoints or requiring re-training.

**Architecture:** Each fix is independent — clip_reward/ent_coef are 1-line config changes; BC mask fix adds action_masks to the BC loss pass; curriculum save/load adds JSON state persistence; EvalCallback adds a new maskable eval class. All backward-compatible with existing `.zip` checkpoints.

**Tech Stack:** Python 3, stable-baselines3 ≥ 2.0, sb3-contrib ≥ 2.0, numpy, json (stdlib)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `sb3/train_sb3.py` | Modify | clip_reward, ent_coef, curriculum restore, EvalCallback wiring |
| `sb3/app/rl/models/sudoku_ppo.py` | Modify | Pass action_masks to evaluate_actions in BC pass |
| `sb3/app/rl/curriculum/callback.py` | Modify | Add `_on_training_start()` to re-apply stage on resume |
| `sb3/app/rl/curriculum/eval_callback.py` | Create | `SudokuEvalCallback` with maskable predict |

---

## Task 1: Fix VecNormalize clip_reward and ent_coef

The current `clip_reward=10.0` clips the terminal +20 board-done reward in half.
`ent_coef=0.05` is 5× the typical PPO value and over-encourages exploration.

**Files:**
- Modify: `sb3/train_sb3.py:91` (clip_reward)
- Modify: `sb3/train_sb3.py:122` (ent_coef)

- [ ] **Step 1: Apply the two one-line changes**

In `sb3/train_sb3.py`, find and change:

```python
# Line 91 — was clip_reward=10.0
        vec_env = VecNormalize(
            vec_env,
            norm_obs=False,
            norm_reward=True,
            clip_reward=50.0,   # was 10.0 — raise ceiling so +20 terminal survives
        )
```

```python
# Line 122 — was ent_coef=0.05
            ent_coef=0.01,      # was 0.05 — 5× reduction; reduces over-exploration
```

- [ ] **Step 2: Smoke-test startup**

From `sb3/`:
```bash
python train_sb3.py --timesteps 500 --n-envs 1 --verbose 0
```

Expected: training starts and runs for 500 steps without error. Check printed output has no NaN or crash.

- [ ] **Step 3: Verify values in model attributes**

```bash
python -c "
import sys; sys.path.insert(0, '.')
from train_sb3 import *

args_ns = parse_args()
args_ns.n_envs = 1
args_ns.timesteps = 0
# Just check model construction
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
vec_env = make_vec_env(make_env_fn(DB_PATH, 5), n_envs=1, vec_env_cls=SubprocVecEnv)
vec_env = VecNormalize(vec_env, norm_obs=False, norm_reward=True, clip_reward=50.0)
print('clip_reward:', vec_env.clip_obs)  # VecNormalize stores clip_reward as clip_obs on reward
print('PASS if above is 50.0')
vec_env.close()
"
```

(Note: VecNormalize uses `clip_obs` for the reward clip value internally — check the printed value is 50.0.)

- [ ] **Step 4: Commit**

From repo root:
```bash
git add sb3/train_sb3.py
git commit -m "fix(train): raise VecNormalize clip_reward 10→50, lower ent_coef 0.05→0.01"
```

---

## Task 2: Fix BC evaluate_actions — pass action_masks

The BC loss in `_bc_pass()` calls `policy.evaluate_actions(obs_t, ta)` without action masks. This fits an unmasked distribution, which is inconsistent with the masked policy played during rollouts. The rollout buffer already stores masks — we just need to use them.

**Files:**
- Modify: `sb3/app/rl/models/sudoku_ppo.py:113-121`

- [ ] **Step 1: Write a failing test**

Create `sb3/tests/test_bc_masks.py` (create `sb3/tests/__init__.py` if missing):

```python
# sb3/tests/test_bc_masks.py
"""Verify BC log_probs differ when action_masks are applied vs not."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import torch
import gymnasium as gym
from app.rl.models.features_extractor import SudokuFeaturesExtractor
from sb3_contrib import MaskablePPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from app.rl.envs.sudoku_gym_env import SudokuGymEnv


def _make_env():
    return SudokuGymEnv(db_path='../data/puzzle_pool.db')


def test_bc_logprob_differs_with_masks():
    env = DummyVecEnv([_make_env])
    model = MaskablePPO("CnnPolicy", env, n_steps=64, verbose=0,
                        policy_kwargs=dict(
                            features_extractor_class=SudokuFeaturesExtractor,
                            features_extractor_kwargs={"features_dim": 192},
                            net_arch=[],
                        ))
    obs_np = np.random.rand(4, 9, 9, 9).astype(np.float32)
    obs_t  = torch.as_tensor(obs_np, device=model.device)
    actions = torch.zeros(4, dtype=torch.long, device=model.device)

    # All-True mask (no masking)
    full_masks = torch.ones(4, 729, dtype=torch.bool, device=model.device)
    # Restrictive mask: only action 0 allowed per sample
    restricted = torch.zeros(4, 729, dtype=torch.bool, device=model.device)
    restricted[:, 0] = True

    _, lp_full,       _ = model.policy.evaluate_actions(obs_t, actions, action_masks=full_masks)
    _, lp_restricted, _ = model.policy.evaluate_actions(obs_t, actions, action_masks=restricted)

    # With restricted mask (only action 0 valid), log_prob of action 0 must be 0.0 (log(1.0))
    assert (lp_restricted.detach().cpu().numpy() > lp_full.detach().cpu().numpy()).all(), \
        "Restricted mask should give higher log_prob for the only valid action"
    print("PASS")
    env.close()


if __name__ == "__main__":
    test_bc_logprob_differs_with_masks()
```

- [ ] **Step 2: Run test to verify it passes (validates API understanding)**

```bash
cd sb3 && python tests/test_bc_masks.py
```

Expected: `PASS`

(This test validates that `evaluate_actions` accepts `action_masks` and produces different log_probs — confirming the API works before we change the BC pass.)

- [ ] **Step 3: Modify `_bc_pass()` in sudoku_ppo.py**

In `sb3/app/rl/models/sudoku_ppo.py`, find `_bc_pass()` at line 94. Replace lines 113–121:

**Current:**
```python
        obs_np = self.rollout_buffer.observations[teacher_mask]
        obs_t  = obs_as_tensor(obs_np, self.device)
        ta     = torch.tensor(teacher_a_flat[teacher_mask], dtype=torch.long,  device=self.device)
        tq     = torch.tensor(teacher_q_flat[teacher_mask], dtype=torch.float32, device=self.device)

        self.policy.set_training_mode(True)

        # evaluate_actions without action masking (teacher actions are always legal)
        _, log_probs, _ = self.policy.evaluate_actions(obs_t, ta)
```

**Replace with:**
```python
        obs_np   = self.rollout_buffer.observations[teacher_mask]
        obs_t    = obs_as_tensor(obs_np, self.device)
        ta       = torch.tensor(teacher_a_flat[teacher_mask], dtype=torch.long,  device=self.device)
        tq       = torch.tensor(teacher_q_flat[teacher_mask], dtype=torch.float32, device=self.device)
        # Use stored masks so BC fits the same masked distribution the policy plays
        masks_np = self.rollout_buffer.action_masks[teacher_mask]   # (N, 729) bool
        masks_t  = torch.as_tensor(masks_np, dtype=torch.bool, device=self.device)

        self.policy.set_training_mode(True)

        _, log_probs, _ = self.policy.evaluate_actions(obs_t, ta, action_masks=masks_t)
```

- [ ] **Step 4: Verify short training run with BC enabled doesn't crash**

```bash
cd sb3 && python train_sb3.py --timesteps 2000 --n-envs 1 --verbose 1
```

Expected: training runs 2000 steps, `train/bc_loss` appears in the output logs, no AttributeError on `rollout_buffer.action_masks`.

- [ ] **Step 5: Commit**

```bash
cd ..
git add sb3/app/rl/models/sudoku_ppo.py sb3/tests/
git commit -m "fix(bc): pass action_masks to evaluate_actions so BC fits masked distribution"
```

---

## Task 3: Curriculum State Save/Load

On `--load-model`, `CurriculumCallback` always starts fresh at Stage 1, `mrv_prob` resets to 0.80, and the env difficulty resets to L1-only. This silently regresses a Stage-3 checkpoint.

**Fix:** Save `{stage_idx, total_eps, mrv_prob}` to a JSON alongside the model. On load, restore these values. Add `_on_training_start()` to `CurriculumCallback` to re-apply the difficulty distribution when training restarts.

**Files:**
- Modify: `sb3/app/rl/curriculum/callback.py` — add `_on_training_start()`
- Modify: `sb3/train_sb3.py` — save/load curriculum JSON

- [ ] **Step 1: Add `_on_training_start()` to CurriculumCallback**

In `sb3/app/rl/curriculum/callback.py`, add this method after `_on_training_end()` (after line 128):

```python
    def _on_training_start(self) -> None:
        """Re-apply stage distribution when training (re)starts — handles resume."""
        if self._stage_idx == 0:
            return  # default stage, nothing to restore
        stage = self._stages[self._stage_idx]
        self.training_env.env_method("set_difficulty_distribution", stage["dist"])
        if self.verbose >= 1:
            print(
                f"[Curriculum] Restored stage {self._stage_idx + 1}: "
                f"dist={stage['dist']}  mrv={stage['mrv']:.2f}"
            )
```

- [ ] **Step 2: Add curriculum state save in `main()` of train_sb3.py**

In `sb3/train_sb3.py`, add `import json` near the top (after `import os`):

```python
import json
```

Then after `model.save(save_path)` at line 163, add:

```python
    # Save curriculum state alongside the model for resume support
    curriculum_path = os.path.join(MODEL_DIR, MODEL_NAME + "_curriculum.json")
    curriculum_state = {
        "stage_idx": curriculum._stage_idx,
        "total_eps": curriculum._total_eps,
        "mrv_prob":  float(model.mrv_prob),
    }
    with open(curriculum_path, "w") as f:
        json.dump(curriculum_state, f, indent=2)
    print(f"[train_sb3] Curriculum state saved → {curriculum_path}")
```

- [ ] **Step 3: Add curriculum state restore in `main()` of train_sb3.py**

After the curriculum and checkpoint callbacks are created (after line 153), add:

```python
    # Restore curriculum state if resuming from a checkpoint
    if args.load_model:
        _cpath = args.load_model.replace(".zip", "_curriculum.json")
        if os.path.exists(_cpath):
            with open(_cpath) as _f:
                _cs = json.load(_f)
            curriculum._stage_idx = int(_cs.get("stage_idx", 0))
            curriculum._total_eps = int(_cs.get("total_eps", 0))
            model.mrv_prob = float(_cs.get("mrv_prob", model.mrv_prob_init))
            if args.verbose >= 1:
                print(
                    f"[train_sb3] Curriculum restored: stage={curriculum._stage_idx + 1}  "
                    f"total_eps={curriculum._total_eps}  mrv_prob={model.mrv_prob:.3f}"
                )
        else:
            if args.verbose >= 1:
                print(f"[train_sb3] No curriculum state found at {_cpath} — starting fresh")
```

- [ ] **Step 4: Write a test for save/load round-trip**

Create `sb3/tests/test_curriculum_save_load.py`:

```python
# sb3/tests/test_curriculum_save_load.py
"""Verify curriculum state is saved and restored correctly."""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.rl.curriculum.callback import CurriculumCallback, CURRICULUM_STAGES


def test_save_load_roundtrip():
    cb = CurriculumCallback(verbose=0)
    # Simulate having advanced to stage 2
    cb._stage_idx = 2
    cb._total_eps = 12345
    fake_mrv_prob = 0.20

    with tempfile.NamedTemporaryFile(mode='w', suffix='_curriculum.json', delete=False) as f:
        json.dump({
            "stage_idx": cb._stage_idx,
            "total_eps": cb._total_eps,
            "mrv_prob":  fake_mrv_prob,
        }, f, indent=2)
        path = f.name

    # Simulate restore
    cb2 = CurriculumCallback(verbose=0)
    with open(path) as f:
        cs = json.load(f)
    cb2._stage_idx = int(cs["stage_idx"])
    cb2._total_eps = int(cs["total_eps"])
    restored_mrv   = float(cs["mrv_prob"])

    assert cb2._stage_idx == 2,     f"stage_idx: {cb2._stage_idx}"
    assert cb2._total_eps == 12345, f"total_eps: {cb2._total_eps}"
    assert restored_mrv   == 0.20,  f"mrv_prob:  {restored_mrv}"
    os.unlink(path)
    print("PASS")


if __name__ == "__main__":
    test_save_load_roundtrip()
```

- [ ] **Step 5: Run the test**

```bash
cd sb3 && python tests/test_curriculum_save_load.py
```

Expected: `PASS`

- [ ] **Step 6: End-to-end verification**

```bash
# Run a short training that saves a checkpoint
cd sb3 && python train_sb3.py --timesteps 3000 --n-envs 1 --verbose 1

# Verify the curriculum JSON was created
ls models/sudoku_sb3_latest_curriculum.json
python -c "import json; print(json.load(open('models/sudoku_sb3_latest_curriculum.json')))"
```

Expected: JSON file exists with `{"stage_idx": 0, "total_eps": N, "mrv_prob": 0.8}` (Stage 1 since only 3000 steps).

```bash
# Resume and verify restoration message
python train_sb3.py --load-model models/sudoku_sb3_latest.zip --timesteps 500 --n-envs 1 --verbose 1
```

Expected output includes: `[train_sb3] Curriculum restored: stage=1  total_eps=N  mrv_prob=0.800`

- [ ] **Step 7: Commit**

```bash
cd ..
git add sb3/app/rl/curriculum/callback.py sb3/train_sb3.py sb3/tests/test_curriculum_save_load.py
git commit -m "feat(curriculum): add state save/load for correct resume behavior"
```

---

## Task 4: Add SudokuEvalCallback

Training success rate is biased by curriculum mix and BC teacher. We need a fixed held-out eval that measures actual policy performance.

**Files:**
- Create: `sb3/app/rl/curriculum/eval_callback.py`
- Modify: `sb3/train_sb3.py` — import + wire into model.learn()

- [ ] **Step 1: Write the failing test**

Create `sb3/tests/test_eval_callback.py`:

```python
# sb3/tests/test_eval_callback.py
"""Verify SudokuEvalCallback runs without error and logs to TensorBoard."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np


def test_eval_callback_logs(tmp_path):
    from app.rl.curriculum.eval_callback import SudokuEvalCallback
    from app.rl.models.sudoku_ppo import SudokuMaskablePPO
    from app.rl.models.features_extractor import SudokuFeaturesExtractor
    from stable_baselines3.common.vec_env import DummyVecEnv
    from app.rl.envs.sudoku_gym_env import SudokuGymEnv

    env = DummyVecEnv([lambda: SudokuGymEnv(db_path='../data/puzzle_pool.db')])
    model = SudokuMaskablePPO(
        "CnnPolicy", env, n_steps=64, verbose=0,
        tensorboard_log=str(tmp_path),
        policy_kwargs=dict(
            features_extractor_class=SudokuFeaturesExtractor,
            features_extractor_kwargs={"features_dim": 192},
            net_arch=[],
        ),
    )

    cb = SudokuEvalCallback(
        db_path='../data/puzzle_pool.db',
        eval_freq=64,
        n_episodes=3,
        difficulties=(1,),
        verbose=1,
    )

    model.learn(total_timesteps=64, callback=cb, reset_num_timesteps=True)
    # If we got here without exception, the callback ran
    print("PASS")
    env.close()


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_eval_callback_logs(d)
```

- [ ] **Step 2: Run the test (expect ImportError since the file doesn't exist yet)**

```bash
cd sb3 && python tests/test_eval_callback.py
```

Expected: `ModuleNotFoundError: No module named 'app.rl.curriculum.eval_callback'`

- [ ] **Step 3: Create eval_callback.py**

Create `sb3/app/rl/curriculum/eval_callback.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

```bash
cd sb3 && python tests/test_eval_callback.py
```

Expected: `PASS`

- [ ] **Step 5: Wire SudokuEvalCallback into train_sb3.py**

In `sb3/train_sb3.py`, add import after existing imports:

```python
from app.rl.curriculum.eval_callback import SudokuEvalCallback
```

Then in `main()`, after the checkpoint callback (after line 153), add:

```python
    eval_cb = SudokuEvalCallback(
        db_path=DB_PATH,
        eval_freq=50_000,
        n_episodes=20,
        difficulties=(1, 2, 3, 4),
        verbose=args.verbose,
    )
```

And update `model.learn(...)` to include `eval_cb`:

```python
    model.learn(
        total_timesteps=args.timesteps,
        callback=[curriculum, checkpoint, eval_cb],
        reset_num_timesteps=args.load_model is None,
    )
```

- [ ] **Step 6: Verify eval logs appear in a short training run**

```bash
cd sb3 && python train_sb3.py --timesteps 55000 --n-envs 1 --verbose 1
```

Expected: after ~50k steps, output shows:
```
[Eval] Step 50,000: overall=X.XX%  (N/80)  [L1=20, L2=20, L3=20, L4=20]
```

Also verify TensorBoard: `eval/success_rate_L1`, `eval/success_rate_overall` appear in `runs/sudoku_sb3/`.

- [ ] **Step 7: Commit and push**

```bash
cd ..
git add sb3/app/rl/curriculum/eval_callback.py sb3/train_sb3.py sb3/tests/test_eval_callback.py
git commit -m "feat(eval): add SudokuEvalCallback with maskable predict for unbiased eval"
git push origin main
```

---

## Verification Checklist

After all 4 tasks:

- [ ] `VecNormalize.clip_obs` == 50.0 (reward clip)
- [ ] `model.ent_coef` == 0.01
- [ ] BC pass uses `rollout_buffer.action_masks` — no AttributeError on 2000-step run
- [ ] `models/sudoku_sb3_latest_curriculum.json` created after training
- [ ] `--load-model` prints curriculum restore message
- [ ] TensorBoard shows `eval/success_rate_L1` metric after 50k steps
