# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **重大變更紀錄**：查看 [HISTORY.md](HISTORY.md) 了解各版本的設計決策與 Bug Fix 背景。
> 若不確定某段邏輯為何這樣寫，HISTORY.md 是第一個查詢點。

## Project Structure

This repo contains **four independent training systems** in separate subfolders:

```
sudoku_old/
├── data/puzzle_pool.db        ← shared puzzle database (all versions)
├── legacy/                    ← archived PyTorch PPO + PyQt6 GUI version
├── sb3/                       ← frozen SB3 MaskablePPO baseline (PPO_8 HPs)
├── reasoner/                  ← frozen reference: route-II reasoner (fill+eliminate, justification reward)
└── apprentice/                ← ACTIVE: reasoner + adaptive curriculum + cold-start (26-ch obs)
```

**Shared database**: `data/puzzle_pool.db` at repo root. `legacy/` and `sb3/` reference it as `"../data/puzzle_pool.db"` (run from inside their subfolder). `reasoner/` runs from repo root and resolves the path as `_REPO_ROOT / "data" / "puzzle_pool.db"`.

## Running

```bash
# Active version (apprentice — reasoner + adaptive curriculum); run from REPO ROOT
python -m apprentice.train.train
python -m apprentice.train.train --load-model auto                # resume newest ckpt
python -m apprentice.train.train --curriculum-config apprentice/configs/curriculum_aggressive.json
python -m apprentice.train.train --no-curriculum                  # debug: disable adaptive curriculum

# Frozen reference (reasoner — route II); run from REPO ROOT, not from inside reasoner/
python -m reasoner.train.train
python -m reasoner.train.train --load-model auto                  # resume newest ckpt
python -m reasoner.train.train --timesteps 100000000 --load-model auto

# Frozen baseline (SB3 MaskablePPO — PPO_8)
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

## sb3/ — Frozen SB3 Baseline (reference)

**Data flow:**
1. `SudokuGymEnv.reset()` fetches puzzle from DB → solves with backtracking solver → builds 26-channel observation
2. `SudokuMaskablePPO` collects 512-step rollouts across 8 SubprocVecEnv workers (4,096 steps/update)
3. `TeacherEngine` runs inside each subprocess → returns `(teacher_action, teacher_quality)` via info dict
4. PPO update + separate BC loss pass; `CurriculumCallback` escalates difficulty in 4 stages

**Key files (`sb3/`):**
- [sb3/train_sb3.py](sb3/train_sb3.py) — entry point; argparse for timesteps, n-envs, device, load-model, no-teacher
- [sb3/app/rl/envs/sudoku_gym_env.py](sb3/app/rl/envs/sudoku_gym_env.py) — `SudokuGymEnv`: Gymnasium env, `action_masks()`, `set_difficulty_distribution()`
- [sb3/app/rl/envs/sudoku_solver.py](sb3/app/rl/envs/sudoku_solver.py) — backtracking solver with MRV heuristic; pre-solves puzzle at `reset()`
- [sb3/app/rl/envs/reward_computer.py](sb3/app/rl/envs/reward_computer.py) — `RewardComputer`: naked single +3, hidden single +2, cascade +0.5, unit +5, done +20, wrong −3
- [sb3/app/rl/models/features_extractor.py](sb3/app/rl/models/features_extractor.py) — `SudokuFeaturesExtractor` (BaseFeaturesExtractor): 27 ConstraintHeads → per-cell logits (B,729) + global ctx (B,192) → **(batch, 921)**; net_arch `{"pi": [], "vf": [128]}`
- [sb3/app/rl/models/sudoku_ppo.py](sb3/app/rl/models/sudoku_ppo.py) — `SudokuMaskablePPO`: BC loss as separate optimizer pass; teacher data via callback monkey-patch
- [sb3/app/rl/curriculum/callback.py](sb3/app/rl/curriculum/callback.py) — `CurriculumCallback`: 4-stage dist escalation, backstop/threshold-based advance, entropy warning
- [sb3/app/rl/curriculum/eval_callback.py](sb3/app/rl/curriculum/eval_callback.py) — `SudokuEvalCallback`: per-difficulty eval every 50k steps; `model.predict(obs[np.newaxis], action_masks=masks[np.newaxis], deterministic=True)`

**Observation space** (26 channels, shape `(26,9,9)` channels-first): ch 0-8 one-hot board planes (digit→index 0-8), ch 9-17 per-digit candidate planes (v legal at (r,c)), ch 18-25 aux (fixed, empty, row/col/box fill ratio, cand_count/9, naked-single, hidden-single).

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

## reasoner/ — Active Reasoner Training (route II)

**Differences vs sb3/:** Discrete(1458) action space (fill 0-728 + eliminate 729-1457), 24-ch obs (no naked/hidden-single shortcut flags), technique-justification reward, NO curriculum (removed in `e870443` as inert), pure PPO (no BC pass).

**Run from repo root** (not from inside `reasoner/`): `python -m reasoner.train.train`.

**Key files (`reasoner/`):**
- [reasoner/train/train.py](reasoner/train/train.py) — entry; `--load-model auto` finds newest `reasoner_ckpt_*_steps.zip` in `reasoner/models/`. VecNormalize stats saved as `<ckpt>_vecnorm.pkl` alongside each checkpoint.
- [reasoner/train/ppo.py](reasoner/train/ppo.py) — `SudokuMaskablePPO` (pure PPO, no BC)
- [reasoner/env/sudoku_gym_env.py](reasoner/env/sudoku_gym_env.py) — fill+eliminate env; `max_wrong_fills=20`, `max_steps=300`
- [reasoner/env/reward_computer.py](reasoner/env/reward_computer.py) — action-justification reward (see below)
- [reasoner/solver/human_solver.py](reasoner/solver/human_solver.py) — drives `justifies_<tech>()` lookups across `techniques/`
- [reasoner/solver/techniques/](reasoner/solver/techniques/) — 13 cookbook techniques (naked/hidden single, naked/hidden pair, pointing pair, box-line, naked triple/quad, X-Wing, Swordfish, XY/XYZ-Wing, Trial & Error)
- [reasoner/eval/eval_callback.py](reasoner/eval/eval_callback.py) — random-sample eval; [reasoner/eval/reserved_eval_callback.py](reasoner/eval/reserved_eval_callback.py) — held-out set

**Reward model (`reward_computer.py`):** For every action (fill or eliminate), ask the human solver "what is the *simplest* cookbook technique whose reasoning would produce this exact action?" → reward = `1.0 + TECH_BONUS[tech_id]`. Bonuses scale 0.0 (naked single) → 3.0 (XYZ-Wing, T&E). Wrong action (bad fill OR eliminating the solution value) → `-1`, `wrong_count++`, terminate at `>= MAX_WRONG (20)`. Board-complete → `+20`. Legal-but-unjustified action: `+0.3` (fill) / `+0.1` (eliminate) — small signal to discourage spam without blocking exploration.

**Why action-justification replaced "match `solver.suggest()`":** under the old model only the highest-priority technique's bonus was reachable, so X-Wing / XY-Wing / T&E bonuses never fired when an easier technique was also applicable somewhere else on the board. See commit `0a93dd4`.

---

## apprentice/ — Active Reasoner + Adaptive Curriculum

**Differences vs reasoner/:** 26-ch obs (+ naked-single & hidden-single flags), `CurriculumController` adaptive on `target_empty` (sweet-spot formula, NOT stage-based), dynamic `max_steps`/`max_wrong` scaled by `target_empty`, `net_arch={"pi":[128],"vf":[128,128]}`, `ent_coef=0.05`. **Cold-start required**: obs shape change vs reasoner means ckpts are NOT interchangeable.

**Run from repo root**: `python -m apprentice.train.train [--load-model auto] [--curriculum-config <path>] [--no-curriculum]`. Checkpoints: `apprentice/models/apprentice_ckpt_<N>_steps.zip` with sidecars `<ckpt>_vecnorm.pkl` + `<ckpt>_curriculum.json` (both auto-loaded on `--load-model auto`).

**Key files (`apprentice/`):**
- [apprentice/README.md](apprentice/README.md) — design summary (7 changes A3/B1/A5/D1/E2/C2/E1), TB metrics, sidecar layout
- [apprentice/train/train.py](apprentice/train/train.py) — entry; checkpoint pattern `apprentice_ckpt_<N>_steps.zip`
- [apprentice/train/curriculum_controller.py](apprentice/train/curriculum_controller.py) — adaptive controller (default `target_rate=0.70`, `tolerance_band=[0.55,0.85]`, `step_size=10.0`)
- [apprentice/train/curriculum_callback.py](apprentice/train/curriculum_callback.py) — SB3 integration
- [apprentice/configs/curriculum.json](apprentice/configs/curriculum.json) — controller hyperparams; edit between runs (NO hot reload)
- [apprentice/env/obs_helpers.py](apprentice/env/obs_helpers.py) — naked/hidden-single grids for the 2 new obs channels
- [apprentice/solver/](apprentice/solver/) — same 13-technique cookbook as reasoner/, mirrored by hand (NOT auto-synced)

**Key design decisions (apprentice/):**
- **Sibling, not fork**: `apprentice/solver/techniques/` mirrors `reasoner/solver/techniques/` by hand. A technique fix in one is NOT applied to the other — decide explicitly whether to cross-apply.
- **Curriculum is active here** (unlike the inert one removed from reasoner/ in `e870443`): the adaptive `target_empty` controller is doing meaningful work — don't short-circuit it. `target_empty` is continuous; rounded int is what envs see.
- **Cold-start required when migrating from a reasoner ckpt**: +2 obs channels make `features_extractor` weights non-interchangeable. `--load-model auto` filters by `apprentice_ckpt_*_steps.zip` for this reason — preserve the filter.
- **Wrong-action behavior mirrors reasoner**: non-destructive (penalty + local candidate discard only). Spec: `docs/superpowers/specs/2026-05-15-apprentice-wrong-action-non-destructive-design.md`; reasoner-side reference commits `1e778b2` / `d21629a`. `MAX_WRONG=20` (same reasoning as reasoner — lowering chokes early exploration).
- **Specs & plans live under `docs/superpowers/`**: design specs at `docs/superpowers/specs/<date>-*.md`, execution plans at `docs/superpowers/plans/<date>-*.md`. Check there before reverse-engineering recent behavior changes.

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

## Key Design Decisions (legacy/)

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

## Testing

Reasoner and apprentice both have active test suites. Run from repo root:

```bash
python -m pytest reasoner/tests/                     # full suite
python -m pytest reasoner/tests/test_techniques/     # technique tests only
python -m pytest reasoner/tests/test_techniques/test_x_wing.py -v

python -m pytest apprentice/tests/                   # full apprentice suite
python -m pytest apprentice/tests/test_techniques/   # technique tests only
python -m pytest apprentice/tests/test_reward_computer.py -v
```

Each `reasoner/solver/techniques/<tech>.py` has a paired `reasoner/tests/test_techniques/test_<tech>.py`. When adding a new technique, add the matching test alongside the bonus entry in `TECH_BONUS`. Apprentice mirrors this structure — when cross-applying a fix between reasoner/ and apprentice/, mirror both code and tests.

`legacy/` and `sb3/` have no automated test suites.

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
- **`torch.zeros` + in-place slice assignment drops gradients**: `col_out[:, :, c, :] = head(...)` breaks autograd — 18/27 constraint heads received zero gradients. Always use `torch.stack([head(...) for c in range(9)], dim=2)` instead.
- **BC `evaluate_actions` must pass `action_masks`**: `evaluate_actions(obs, actions, action_masks=masks_t)` — omitting masks trains BC on unmasked distribution, biasing gradients. `rollout_buffer.action_masks` is `float32`; cast to bool before passing.
- **Curriculum JSON state**: `{stage_idx, total_eps, stage_eps, mrv_prob}` saved alongside model; `_on_training_start()` re-applies difficulty distribution on resume. `stage_eps` must be included or backstop resets every resume.
- **Old checkpoint compatibility**: Use `getattr(model, "mrv_prob_init", 0.80)` when loading — old checkpoints may lack this attribute.
- **`db.path` in user_config.json overrides schema default**: if `legacy/data/user_config.json` has an explicit `db.path` key, the schema default is ignored. Both must be `"../data/puzzle_pool.db"` after the project split.
- **`reset()` recursion guard — `_retries` kwarg**: If `solve(board)` returns `None`, `reset()` calls itself with `_retries+1`. At `_retries >= 10` it raises `RuntimeError` instead of stack-overflowing. Legitimate puzzles never hit this; it fires only when the DB has corrupted/unsolvable rows.
- **`_bc_pass()` early-return when `tq.sum() < 1e-8`**: Minimum legitimate teacher quality is 0.15; near-zero sum means teacher abstained on every sample. `-(log_probs * tq).sum() / tq.sum()` would produce NaN that poisons the optimizer. Return early instead. Separately, masked-action log_probs are `-inf`; `-inf * 0 = NaN` in PyTorch even when weight is zero — clamp log_probs to `min=-1e9` before BC loss.
- **`SudokuEvalCallback` — set `_last_eval` before try-except**: The eval body is wrapped in `try-except Exception` to keep training alive if `model.predict()` raises. `self._last_eval = self.num_timesteps` must be assigned *before* the try-block, not inside it — otherwise a failed eval immediately retries next step, causing a busy-loop. `logger.record()` calls must be outside the per-difficulty loop (atomic) to avoid partial TensorBoard writes.
- **Box head reshape order — `permute(0,1,3,2,4,5)`**: After `torch.stack(box_results, dim=1)` the box index dimension encodes `(box_row*3 + box_col)`. Reshape to `(B,3,3,3,3,H)` gives axes `(B, box_row, box_col, local_row, local_col, H)`. The required board layout has row=`box_row*3+local_row`, col=`box_col*3+local_col`, so swap axes 2↔3 with `permute(0,1,3,2,4,5)` before the final `reshape(B,9,9,H)`. Getting this wrong produces a silently incorrect spatial mapping — test with `torch.allclose` against the original scatter logic.
- **`CurriculumCallback._maybe_advance()` TOCTOU fix**: Read `self._stage_idx` into a local under `_buf_lock`, compute advance logic outside the lock, then re-acquire and check `if self._stage_idx == stage_idx:` before writing. Skipping the re-check allows two concurrent callbacks both to advance the stage index, jumping two stages at once.
- **`PuzzlePoolDB.close()` uses `getattr(self._local, "conn", None)`**: `threading.local` attributes only exist on threads that have set them. Direct attribute access (`self._local.conn`) raises `AttributeError` on any thread that never opened a connection. Always use `getattr` with a default of `None`.
- **`CrawlerWorker._get_stats()` — 2 s TTL cache**: `get_pool_stats()` is a DB read. With 10 concurrent workers at ~0.5 s/puzzle this is ~20 reads/sec for a value that barely changes. Cache with `time.monotonic()` TTL; invalidate when `_stats_cache is None or now - _stats_ts > _STATS_TTL`.
- **`executor.shutdown(wait=True, cancel_futures=True)` in proxy_manager**: `wait=False` returns while validation threads still hold sockets, causing resource leaks on stop. `wait=True` blocks until all in-flight probes finish; `cancel_futures=True` skips any not yet started. This is safe because stop is already called from a background context.
- **`_obs()` snapshots board with `.copy()` even though current code path is safe**: `(self.board == v).astype(np.float32)` already materialises a fresh array, so the obs is *de facto* snapshot-safe. The explicit `board = self.board.copy()` is a defensive guard for any future refactor that swaps in a view-returning op or shared-memory backend (`SharedMemoryVecEnv`). Don't strip it as dead code.
- **`log_probs.clamp(min=-1e9)` in `_bc_pass()` is defensive against `-inf * 0 = NaN`**: PyTorch IEEE 754 says `-inf * 0 = NaN` even when the BC weight is 0. Current sb3-contrib uses `-1e8` (not `-inf`) for masked actions and `teacher_mask > 0` pre-filters zero-quality, so the failure mode is unreachable today. The clamp is a no-op for `-1e8` and protects against future SB3 changes — keep it.
- **`_LOCK_RETRY_DELAYS = (0.1, 0.3, 1.0)` and `_EXTRA_COLUMNS` duplicated in both pool_db files**: deliberate two-package separation (legacy/sb3 split). Both files MUST stay in sync — same delays, same retry condition (`"locked" in str(e).lower()`), same migration columns dict. If you add a column to one, add it to the other.
- **`_retry_transaction(self, fn)` initialises `conn = None` BEFORE `_get_conn()`**: this lets the helper handle the case where `_get_conn()` itself raises `OperationalError: database is locked` (rare but possible under heavy connection pressure). The rollback branch uses `if conn is not None` — without the sentinel, an UnboundLocalError fires before retry can happen.
- **`_migrate(conn)` runs inside `_init_db()` after `CREATE TABLE IF NOT EXISTS`**: `PRAGMA table_info(puzzles)` reflects the freshly-created schema correctly. To add a new column, just add a line to `_EXTRA_COLUMNS = {"level": "INTEGER NOT NULL DEFAULT 1", ...}` — no method changes needed.
- **`_warned_direct` is a one-shot per-worker flag, not per-session**: each worker independently emits one direct-connect warning when its first `proxy_dict is None` happens. Restart of a worker (new instance) re-arms the flag. Don't accidentally make it class-level — that would suppress the warning across all workers after the first one fires.

## Key Design Decisions (reasoner/)

- **`TECH_BONUS` keys are 1-13 and 17 only** — `tech_id` 3 ("basic_elim") is engine-internal and never appears as a justifier. IDs 14-16 are reserved (unimplemented Tier B). Adding a new technique = file under `solver/techniques/`, register in `human_solver.py`, add a bonus to `TECH_BONUS` in `reward_computer.py`.
- **No curriculum**: env samples uniformly from all puzzles at the configured websudoku difficulty (1-4). The old stage-curriculum infrastructure was removed in `e870443` — do NOT reintroduce without explicit ask; it was inert (never triggered meaningful escalation under the justification reward).
- **TB log name is constant (`"reasoner"`)**: SB3 auto-suffixes (`reasoner_1`, `reasoner_2`, ...) across resumes so all runs are visible together in a single TensorBoard view pointed at `reasoner/runs/`.
- **Action mask permits any `(r,c,v)` where v is currently a candidate at empty `(r,c)`**: solution-correctness is checked in the reward computer, NOT in the mask, to avoid leaking the answer into the policy's input distribution.
- **`max_wrong_fills=20` (was 5)**: raised because the eliminate action half makes accidental "destroy the solution" events more frequent (any eliminate of the true solution value counts as a wrong action). Lowering this back to 5 chokes early exploration.
