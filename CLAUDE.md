# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **重大變更紀錄**：查看 [HISTORY.md](HISTORY.md) 了解各版本的設計決策與 Bug Fix 背景。
> 若不確定某段邏輯為何這樣寫，HISTORY.md 是第一個查詢點。

## Overview

A reinforcement learning (PPO) agent that learns to solve Sudoku puzzles. Puzzles are fetched from websudoku.com via `requests` (no browser), stored in SQLite, and the agent trains using a three-phase curriculum that mixes deterministic MRV teacher demonstrations with learned policy rollouts.

## Running

```bash
# Start training (fetches puzzles from websudoku.com + runs PPO loop)
python main_train.py

# Runtime hotkeys during training
# F8 = pause/resume, F9 = stop (also stops proxy validation thread), F10 = force model save
```

Dependencies listed in `requirements.txt`. Core: `torch` (CUDA), `requests`, `numpy`, `PyQt6`, `keyboard`.
Optional: `PySocks` for SOCKS proxy support. `playwright` retained for fallback only.

## Architecture

**Data flow:**
1. 20 producer threads fetch puzzles from `east.websudoku.com` via `requests` → `app/data/pool_db.py` (SQLite, WAL mode)
2. Main loop fetches puzzles from DB (all difficulties, natural curriculum) → creates `SudokuEnv` → runs episodes with agent
3. Agent collects 512-step rollouts → PPO update every rollout
4. Validated solutions written back to DB; model saved every N episodes

**Key files:**
- [main_train.py](main_train.py) — training loop, hotkey controller, producer threads; all hyperparameters live in `app/config/schema.py`
- [app/config/schema.py](app/config/schema.py) — `CONFIG_SCHEMA` dict with all settings (label, type, default, reload_required, etc.)
- [app/config/manager.py](app/config/manager.py) — `ConfigManager`: thread-safe get/set, JSON persistence (`data/user_config.json`), hot-reload callbacks
- [app/gui/training_gui.py](app/gui/training_gui.py) — `TrainingWindow` (QMainWindow), QSystemTrayIcon for hide/show, ⚙ 設定 button
- [app/gui/settings_dialog.py](app/gui/settings_dialog.py) — schema-driven settings dialog (dynamic widget generation per type)
- [app/gui/board_widget.py](app/gui/board_widget.py) — `SudokuBoardWidget`: custom QPainter 9×9 board with two-row title (status + difficulty stars)
- [app/gui/board_grid_panel.py](app/gui/board_grid_panel.py) — responsive multi-board grid; slot 0 = active, slots 1..N = history
- [app/sudoku/env.py](app/sudoku/env.py) — `SudokuEnv`: 9×9 board, 8-channel observation, 729-action space (row×col×num), shaped reward system
- [app/sudoku/torch_agent.py](app/sudoku/torch_agent.py) — `SudokuPPONet` (cell embedding + ConstraintHead per row/col/box), `RolloutBuffer`, PPO+GAE update, quality-weighted BC loss, adaptive entropy, PolicyDemoStore integration
- [app/sudoku/phase_manager.py](app/sudoku/phase_manager.py) — `PhaseManager`: three-phase curriculum with piecewise cosine MRV decay and dual-trigger transitions
- [app/sudoku/teacher_engine.py](app/sudoku/teacher_engine.py) — `TeacherEngine`: deterministic 4-level quality pyramid MRV teacher
- [app/sudoku/policy_demo_store.py](app/sudoku/policy_demo_store.py) — `PolicyDemoStore`: Phase 3 self-improvement ring buffer
- [app/sudoku/agents.py](app/sudoku/agents.py) — `MRVAgent` (minimum remaining values heuristic, used as BC expert), `RandomAgent`
- [app/sudoku/validator.py](app/sudoku/validator.py) — validates completed boards against Sudoku rules
- [app/data/pool_db.py](app/data/pool_db.py) — thread-safe SQLite pool: puzzle locking, attempt tracking, solution storage
- [app/web/reader.py](app/web/reader.py) — `fetch_puzzle_via_requests()` (primary scraper), `WebSudokuReader` (Playwright fallback)
- [app/web/proxy_manager.py](app/web/proxy_manager.py) — downloads proxy lists, background validation with graceful stop via `stop_validation()`

**Observation space** (`env.py`): 8-channel 9×9 tensor — fixed cells, empty cells, row/col/box fill ratio, candidate counts, naked-single flags.

**Reward shaping** (tuned values in `env.py`): naked single +3.0, hidden single +1.5, unit complete +5.0, board done +15.0, dead-end −30.0, invalid −3.0.

**Three-phase curriculum** (`phase_manager.py`):
- **Phase 1 (Bootstrap)**: MRV 0.90→0.40 cosine decay over `phase1_steps`; BC exponent β=0.5 (BC decays slower than MRV)
- **Phase 2 (Transfer)**: MRV 0.40→0.10 cosine decay over `phase2_steps`; BC exponent β=1.0 (BC and MRV co-decay)
- **Phase 3 (RL-only)**: MRV fixed at `mrv_min_prob` floor (0.05); BC exponent β=999 (effectively zero); `PolicyDemoStore` self-improvement flywheel activates
- Transition trigger: `success_rate >= tau` (performance, rolling 100 episodes) **OR** `mrv_step >= T` (time backstop), whichever comes first
- Effective BC: `eff_bc = bc_coef × (mrv_prob / mrv_init)^β` — coupled to MRV decay, never jumps abruptly

Difficulty distribution configurable via `training.level_dist` (JSON string, default L1=60%, L2=30%, L3=10%).

**Model**: `models/sudoku_policy_latest.pt` (PyTorch checkpoint). Puzzles: `data/puzzle_pool.db` (SQLite).

## Config System

All hardcoded constants have been moved to `app/config/schema.py` (v7). Access via `config.get("key")`. User overrides persist in `data/user_config.json` (auto-created). Settings UI: ⚙ 設定 button in the toolbar.

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

## Config Overrides (data/user_config.json vs schema defaults)

The following keys in `data/user_config.json` intentionally deviate from the schema defaults. This is a "pure RL" training configuration — minimal teacher guidance, aggressive phase thresholds:

| Key | Schema Default | Runtime Value | Reason |
|-----|---------------|---------------|--------|
| `training.mrv_mix_prob` | 0.9 | 0.0 | Pure RL mode — no teacher demonstrations |
| `training.mrv_min_prob` | 0.05 | 0.0 | No teacher floor in Phase 3 |
| `training.phase1_tau` | 0.30 | 0.65 | Aggressive phase advance threshold |
| `training.phase2_tau` | 0.65 | 0.90 | Aggressive phase advance threshold |
| `training.level_dist` | `{"1":0.6,"2":0.3,"3":0.1}` | `{"1":0.25,"2":0.25,"3":0.25,"4":0.25}` | Uniform across all 4 difficulties |
| `crawler.producer_workers` | 20 | 1 | Single-worker crawl (low-network environment) |
| `training.dead_end_penalty` | 0.0 | -5.0 | Explicit dead-end penalty enabled |

## SB3 Training System (train_sb3.py)

A second training entry point alongside `main_train.py`:
- **`train_sb3.py`** — SB3 MaskablePPO entry point (8× SubprocVecEnv, 4-stage curriculum, dense reward)
- **`app/rl/`** — SB3-specific modules:
  - `envs/sudoku_gym_env.py` — Gymnasium env with `action_masks()`, TeacherEngine runs inside subprocess
  - `envs/sudoku_solver.py` — Backtracking solver with MRV heuristic (pre-solves puzzle at `reset()`)
  - `envs/reward_computer.py` — Dense reward: naked single +3, hidden single +2, cascade +0.5, unit +5, done +20, wrong −3
  - `models/features_extractor.py` — `SudokuFeaturesExtractor` (BaseFeaturesExtractor), ports constraint-head from `torch_agent.py`
  - `models/sudoku_ppo.py` — `SudokuMaskablePPO`: BC loss as separate optimizer pass after PPO; teacher data captured via callback monkey-patch in `collect_rollouts()`
  - `curriculum/callback.py` — `CurriculumCallback`: 4-stage difficulty escalation; backstop or per-difficulty success-rate threshold triggers stage advance
- **SB3 API**: `linear_schedule` removed in SB3 2.8 → use `LinearSchedule(start, end, end_fraction=1.0)` from `stable_baselines3.common.utils`
- **TensorBoard**: must be installed separately (`pip install tensorboard`); not bundled with SB3
- **Resume**: `python train_sb3.py --load-model models/sudoku_sb3_ckpt_XXXXX_steps.zip`
