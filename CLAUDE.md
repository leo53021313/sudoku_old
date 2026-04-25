# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **重大變更紀錄**：查看 [HISTORY.md](HISTORY.md) 了解各版本的設計決策與 Bug Fix 背景。
> 若不確定某段邏輯為何這樣寫，HISTORY.md 是第一個查詢點。

## Project Structure

This repo contains **two independent training systems** in separate subfolders:

```
sudoku_old/
├── data/puzzle_pool.db        ← shared puzzle database (both versions)
├── legacy/                    ← archived PyTorch PPO + PyQt6 GUI version
└── sb3/                       ← active SB3 MaskablePPO version (main development)
```

**Shared database**: `data/puzzle_pool.db` at repo root. Both versions reference it as `"../data/puzzle_pool.db"` (run from inside their subfolder). This value is set in `legacy/data/user_config.json` (`db.path`) and `sb3/train_sb3.py` (`DB_PATH`).

## Running

```bash
# Active version (SB3 MaskablePPO)
cd sb3
python train_sb3.py
python train_sb3.py --timesteps 2000000 --n-envs 8
python train_sb3.py --load-model models/sudoku_sb3_ckpt_XXXXX_steps.zip   # resume

# Legacy version (archived PyTorch PPO + GUI)
cd legacy
python main_train.py
# F8 = pause/resume, F9 = stop, F10 = force model save
```

---

## sb3/ — Active SB3 Training System

**Data flow:**
1. `SudokuGymEnv.reset()` fetches puzzle from DB → solves with backtracking solver → builds 9-channel observation
2. `SudokuMaskablePPO` collects 512-step rollouts across 8 SubprocVecEnv workers (4,096 steps/update)
3. `TeacherEngine` runs inside each subprocess → returns `(teacher_action, teacher_quality)` via info dict
4. PPO update + separate BC loss pass; `CurriculumCallback` escalates difficulty in 4 stages

**Key files (`sb3/`):**
- [sb3/train_sb3.py](sb3/train_sb3.py) — entry point; argparse for timesteps, n-envs, device, load-model, no-teacher
- [sb3/app/rl/envs/sudoku_gym_env.py](sb3/app/rl/envs/sudoku_gym_env.py) — `SudokuGymEnv`: Gymnasium env, `action_masks()`, `set_difficulty_distribution()`
- [sb3/app/rl/envs/sudoku_solver.py](sb3/app/rl/envs/sudoku_solver.py) — backtracking solver with MRV heuristic; pre-solves puzzle at `reset()`
- [sb3/app/rl/envs/reward_computer.py](sb3/app/rl/envs/reward_computer.py) — `RewardComputer`: naked single +3, hidden single +2, cascade +0.5, unit +5, done +20, wrong −3
- [sb3/app/rl/models/features_extractor.py](sb3/app/rl/models/features_extractor.py) — `SudokuFeaturesExtractor` (BaseFeaturesExtractor): 27 ConstraintHeads → mean pool → (batch, 192)
- [sb3/app/rl/models/sudoku_ppo.py](sb3/app/rl/models/sudoku_ppo.py) — `SudokuMaskablePPO`: BC loss as separate optimizer pass; teacher data via callback monkey-patch
- [sb3/app/rl/curriculum/callback.py](sb3/app/rl/curriculum/callback.py) — `CurriculumCallback`: 4-stage dist escalation, backstop/threshold-based advance, entropy warning

**Observation space** (9 channels, shape `(9,9,9)` channels-first): board/9, fixed, empty, row/col/box fill ratio, candidate count/9, naked-single flag, hidden-single flag.

**Action space**: `Discrete(729)` = `row*81 + col*9 + (val-1)`. `action_masks()` masks illegal fills.

**4-stage curriculum** (`CurriculumCallback`):

| Stage | Mix | MRV prob | Advance when |
|-------|-----|----------|--------------|
| 1 | L1: 100% | 0.80 | L1 success ≥ 75% or 5k eps |
| 2 | L1:60% L2:40% | 0.40 | L2 success ≥ 65% or 15k eps |
| 3 | L1:20% L2:40% L3:40% | 0.20 | L3 success ≥ 55% or 30k eps |
| 4 | L1:10% L2:20% L3:35% L4:35% | 0.05 | final stage |

**SB3 API note**: `linear_schedule` removed in SB3 2.8 → use `LinearSchedule(start, end, end_fraction=1.0)` from `stable_baselines3.common.utils`. TensorBoard must be installed separately (`pip install tensorboard`).

---

## legacy/ — Archived PPO Training System

**Data flow:**
1. 20 producer threads fetch puzzles from `east.websudoku.com` via `requests` → SQLite (WAL mode)
2. Main loop fetches puzzles from DB → creates `SudokuEnv` → runs episodes with agent
3. Agent collects 512-step rollouts → PPO update every rollout
4. Validated solutions written back to DB; model saved every N episodes

**Key files (`legacy/`):**
- [legacy/main_train.py](legacy/main_train.py) — entry point (thin wrapper); training logic in `app/training/`
- [legacy/app/config/schema.py](legacy/app/config/schema.py) — `CONFIG_SCHEMA` dict with all settings
- [legacy/app/config/manager.py](legacy/app/config/manager.py) — `ConfigManager`: thread-safe get/set, JSON persistence, hot-reload callbacks
- [legacy/app/gui/training_gui.py](legacy/app/gui/training_gui.py) — `TrainingWindow` (QMainWindow), QSystemTrayIcon
- [legacy/app/sudoku/env.py](legacy/app/sudoku/env.py) — `SudokuEnv`: 8-channel obs, 729-action space, shaped reward
- [legacy/app/sudoku/torch_agent.py](legacy/app/sudoku/torch_agent.py) — `SudokuPPONet`, `RolloutBuffer`, PPO+GAE, quality-weighted BC loss
- [legacy/app/sudoku/phase_manager.py](legacy/app/sudoku/phase_manager.py) — `PhaseManager`: 3-phase cosine MRV decay, dual-trigger transitions
- [legacy/app/sudoku/teacher_engine.py](legacy/app/sudoku/teacher_engine.py) — `TeacherEngine`: deterministic 4-level quality pyramid
- [legacy/app/data/pool_db.py](legacy/app/data/pool_db.py) — thread-safe SQLite pool
- [legacy/app/web/reader.py](legacy/app/web/reader.py) — `fetch_puzzle_via_requests()` (primary scraper)

**Model**: `legacy/models/sudoku_policy_latest.pt`. Config: `legacy/data/user_config.json`. Puzzles: `../data/puzzle_pool.db`.

## Config System (legacy/ only)

All hardcoded constants in `legacy/app/config/schema.py`. Access via `config.get("key")`. User overrides persist in `legacy/data/user_config.json`. Settings UI: ⚙ 設定 button in the toolbar.

- `reload_required: False` → hot-reload (callback triggered immediately on Apply)
- `reload_required: True` → requires training restart; settings are saved but take effect next run

## Key Design Decisions

- **HTTP proxy priority**: Validated by actual page fetch (`puzzle_grid` check); SOCKS only TCP connect — HTTP proxies are more reliable and sorted first (`_PROTO_PRIORITY`).
- **Proxy stop on F9**: `run()` finally calls `proxy_manager.stop_validation()` before `_stop_event.set()`, ensuring the background validator exits within one iteration.
- **`logging.print_producer_success = False`**: 20 producers inserting puzzles generates too much noise; toggle in settings to debug scraper issues.
- **`locked_by`/`locked_at`**: Informational only; `fetch_one_puzzle_for_training` selects by status, not lock state.
- **Board title is two rows** (`TITLE_H = _TITLE_ROW1 + _TITLE_ROW2 = 38px`): top row = episode/status + difficulty badge; bottom row = star rating (★★☆☆). Do NOT add a bare `TITLE_H = 22` after the `_C` color dict — that was a bug that overwrote the correct value.
- **`on_board_update` AND `on_episode_end` both pass `w._level`**: Both intermediate updates and the final episode-end call must preserve difficulty level. Missing `w._level` in either one silently resets the badge to 0. Pattern: `w = self._widgets[0]; w.update_state(..., w._level)`.
- **`proxy.validate_count = -1`**: sentinel for "validate all"; converted to `None` in `run()` before passing to `start_background_validation()`.
- **`training.level_dist` is a JSON string**: stored as `'{"1": 0.6, "2": 0.3, "3": 0.1}'` (JSON only supports string keys); parse with `{int(k): v for k, v in json.loads(raw).items()}`.
- **TeacherEngine is fully deterministic**: uses `min(candidates)` not `random.choice`. Same state always gives the same label, keeping BC gradient direction consistent. Level 5 (quality=0.0) means teacher abstains — no BC loss generated, action falls through to policy.
- **PhaseManager cosine bases are NOT `mrv_floor`**: Phase 1 formula is `0.40 + (mrv_init - 0.40) * cos_w`; Phase 2 is `0.10 + 0.30 * cos_w`. Using `mrv_floor` as the cosine base caused a critical bug (Phase 1 started at 0.55 instead of 0.90). The floor is only used as the Phase 3 fixed value.
- **`_mrv_ratio` denominator is always `self.mrv_mix_prob` (initial value)**: `eff_bc = bc_coef × (mrv_prob / mrv_mix_prob)^β`. The decay is intentionally anchored to the original init — do not change the denominator to a phase-relative value.
- **`last_entropy_value` / `last_loss_value` must be initialized to `0.0` not `None`**: `getattr(agent, attr, 0.0)` silently returns `None` when the attribute exists with value `None`. The GUI format string `f"{entropy:.4f}"` TypeError-crashes on None. Always initialize numeric fields to a number.
- **`stats_update` GUI event must NOT be gated by `logging.print_rolling_stats`**: User logging flags control terminal output only. GUI refresh depends solely on the `print_every_episodes` interval. Mixing these two conditions freezes the GUI panel when text logging is disabled.
- **Skipped puzzles (`tries >= max_tries`) must decrement `episode_idx` before `continue`**: They never run an actual episode so must not consume an episode slot in the counter.
- **`ConfigManager._save()` is always called outside `_lock`**: Take a `snapshot = dict(self._user)` inside the lock, release, then call `_save(snapshot)`. This applies to both `set()` and `reset_to_default()`. Doing file I/O inside the lock causes unnecessary hold time when 20 producer threads call concurrently.
- **`PolicyDemoStore.try_add_episode()` requires policy ratio ≥ `min_ratio` (0.50)**: Episodes dominated by the MRV teacher are rejected — they don't represent policy capability and would pollute the Phase 3 self-improvement signal.
- **Phase transitions only happen at episode boundaries**: `phase_manager.record_episode()` is called only in `finish_episode()`. Within a single episode the phase never changes, so `_demo_states` / `_demo_total_steps` are always consistent with the phase they were collected under.

## Config Overrides (legacy/data/user_config.json vs schema defaults)

The following keys in `legacy/data/user_config.json` intentionally deviate from the schema defaults. This is a "pure RL" training configuration — minimal teacher guidance, aggressive phase thresholds:

| Key | Schema Default | Runtime Value | Reason |
|-----|---------------|---------------|--------|
| `training.mrv_mix_prob` | 0.9 | 0.0 | Pure RL mode — no teacher demonstrations |
| `training.mrv_min_prob` | 0.05 | 0.0 | No teacher floor in Phase 3 |
| `training.phase1_tau` | 0.30 | 0.65 | Aggressive phase advance threshold |
| `training.phase2_tau` | 0.65 | 0.90 | Aggressive phase advance threshold |
| `training.level_dist` | `{"1":0.6,"2":0.3,"3":0.1}` | `{"1":0.25,"2":0.25,"3":0.25,"4":0.25}` | Uniform across all 4 difficulties |
| `crawler.producer_workers` | 20 | 1 | Single-worker crawl (low-network environment) |
| `training.dead_end_penalty` | 0.0 | -5.0 | Explicit dead-end penalty enabled |

## Key Design Decisions (sb3/)

- **TeacherEngine in subprocess**: pure numpy → safe inside SubprocVecEnv. Results passed via `info` dict from `step()`, read by `collect_rollouts()` monkey-patch.
- **BC buffer alignment**: after `super().train()`, `rollout_buffer.observations` is `swap_and_flatten`ed to `(n_envs * n_steps, *obs_shape)`. Teacher arrays `(n_steps, n_envs)` must use `.T.flatten()` to align.
- **BC as separate pass**: `_bc_pass()` runs after `super().train()` with its own `optimizer.step()`. Keeps BC gradient separate from PPO to avoid interference.
- **`db.path` in user_config.json overrides schema default**: if `legacy/data/user_config.json` has an explicit `db.path` key, the schema default is ignored. Both must be `"../data/puzzle_pool.db"` after the project split.
