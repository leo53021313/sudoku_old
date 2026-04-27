# HISTORY.md — 重大變更紀錄

---

## [v12] 穩定性強化 Wave 3：8 項 Minor Hardening（2026-04-27）

### Fixed (Wave 3 — Minor Hardening)

- **`sb3/app/rl/envs/sudoku_gym_env.py` `_obs()` 持有 live `self.board` reference**（Defensive）
  - 原因：obs 在當前實作下因 `(self.board == v).astype(np.float32)` 隱式 copy 而安全，但若未來改用 `SharedMemoryVecEnv` 或 view-returning op 即會 alias
  - 修正：`_obs()` 開頭加 `board = self.board.copy()`，函式內所有 `self.board` 改為 `board`
  - 為防禦性修正，加入 regression test 鎖定 contract

- **`sb3/app/rl/models/sudoku_ppo.py` BC loss `-inf * 0 = NaN` 風險**（Defensive）
  - 原因：PyTorch `MaskableCategoricalDistribution` 對 masked action 給 log_prob，IEEE 754 下 `-inf * 0 = NaN`（非 0）
  - 注意：當前 sb3-contrib 版本實際給 `-1e8` 而非 `-inf`，並有 `teacher_mask > 0` 預過濾，本次失敗模式在現行程式碼路徑下不可達
  - 修正：`evaluate_actions()` 後加 `log_probs = log_probs.clamp(min=-1e9)`，防護未來 SB3 改動

- **`crawler/app/web/proxy_manager.py` `validate_all()` 預設 timeout 與 config 不一致**（Consistency）
  - 原因：`validate_all()` 預設 `timeout=8`，但 `start_background_validation()` 用 `config.proxy_validate_timeout`（預設 3）
  - 修正：`validate_all()` 預設改為 `timeout=3`

- **`crawler/app/core/worker.py` 直連模式無 UI 提示**（UX）
  - 原因：proxy 池為空時 worker 靜默使用直連，使用者只看到「0 proxies valid」誤以為爬蟲已停
  - 修正：`__init__` 加 `_warned_direct` flag；首次進入直連時發送一次性 `warn` event；`main_window._on_worker_event` 新增 `warn` 分支顯示為黃色

- **`crawler/app/db/pool_db.py` 高並發下 `database is locked` 直接拋例外**（Resilience）
  - 原因：10 worker 並發 INSERT，`busy_timeout` 觸發後直接 `OperationalError`
  - 修正：新增 `_retry_transaction(fn)` helper，最多 3 次重試，延遲 `(0.1, 0.3, 1.0)` 秒；`upsert_puzzle()` 改用 helper

- **`sb3/app/data/pool_db.py` 同樣的鎖等待風險**（Resilience）
  - 對稱於 W3-5：相同 `_retry_transaction()` 實作，套用至 `fetch_one_puzzle_for_training()`（sb3 hot path 是 read 而非 write）
  - 兩個 pool_db.py 的 helper 邏輯為 byte-identical（同 delays、同錯誤判斷、同 log 格式）

- **兩個 `pool_db.py` `ALTER TABLE ADD COLUMN` 用 try/except 遮蔽錯誤**（Maintainability）
  - 原因：`except OperationalError: pass` 會吞掉非「duplicate column」的真實 schema 錯誤
  - 修正：新增模組級 `_EXTRA_COLUMNS = {"level": "INTEGER NOT NULL DEFAULT 1"}` 和 `_migrate(self, conn)` 方法，使用 `PRAGMA table_info(puzzles)` 檢查欄位存在後再 ALTER；`_init_db()` 呼叫 `self._migrate(conn)`
  - 加入新欄位現在只需在 `_EXTRA_COLUMNS` dict 加一行

- **`crawler/app/gui/stats_panel.py` `_insert_times` 無鎖看似可疑**（Documentation）
  - 原因：deque 看起來像 race-prone state，未來工程師可能誤加鎖
  - 修正：加一行註解說明 PyQt6 signal slots 在 main thread serialize，無需鎖

### Tests Added

- `sb3/tests/test_gym_env_stability.py` — `test_obs_uses_board_copy_not_reference`（W3-1 regression）
- `sb3/tests/test_bc_guards.py` — `test_bc_pass_masked_actions_no_nan`（W3-2 clamp 行為）
- `crawler/tests/test_worker_stability.py` — `test_worker_warns_on_direct_connect`（W3-4 一次性語義）
- `crawler/tests/test_pool_db.py`（新增）— `test_upsert_retries_on_locked_db` + `test_migration_idempotent_with_pre_existing_schema`
- `sb3/tests/test_pool_db_close.py` — `test_fetch_retries_on_locked_db` + `test_migration_idempotent_with_pre_existing_schema`

### Cleanup

- **`crawler/app/gui/db_panel.py` 移除 dead `_refresh_error_shown` flag**：v11 polish commit 將 refresh 改為「永遠更新 label」後，此 flag 仍寫入但永不讀取——pure dead state，刪除

---

## [v11] 穩定性強化 Wave 1+2：11 項 Critical/Resource 修復（2026-04-26）

### Fixed (Wave 1 — Critical Stability)

- **`sb3/app/rl/envs/sudoku_gym_env.py` reset() 遞迴深度無限制**（Critical）
  - 原因：`solve(board)` 回傳 `None` 時無限遞迴自呼叫，DB 含無解題目即 stack overflow
  - 修正：加入 `_retries: int = 0` 參數；`_retries >= 10` 時拋出 `RuntimeError`
  - 為什麼 10 次：合理上限，正常 DB 不應出現連續無解題目

- **`sb3/app/rl/models/sudoku_ppo.py` BC loss NaN 毒化優化器**（Critical）
  - 原因：`-(log_probs * tq).sum() / tq.sum()`，teacher 全部棄權時 `tq.sum() ≈ 0` → NaN
  - 修正：`if tq.sum() < 1e-8: return`；合法最低品質為 0.15，接近 0 代表 teacher 棄權
  - 隱患：`-inf * 0 = NaN`（masked action log_prob = `-inf`），同時在 W3-2 用 `.clamp(min=-1e9)` 防禦（Wave 3 待實作）

- **`sb3/app/rl/curriculum/eval_callback.py` 例外靜默停用後續 eval**（Critical）
  - 原因：`model.predict()` 因 device mismatch 或 mask 問題拋出例外，傳播到 SB3 callback loop 後被靜默吞掉，後續所有 eval 不再觸發
  - 修正：整個難度迴圈包在 `try-except Exception`；`logger.record()` 全部移至迴圈外（原子提交，避免部分寫入 TensorBoard）
  - 關鍵細節：`self._last_eval = self.num_timesteps` 必須在 try 外先設，避免例外後立即重試

- **`crawler/app/core/worker.py` 例外只顯示截斷訊息**（Critical）
  - 原因：`except Exception as exc: emit(str(exc)[:120])` — 使用者看不到 stack trace，無法診斷 worker 停止原因
  - 修正：`import traceback as _traceback`；error signal 的 `msg` 改為 `_traceback.format_exc()`

- **`crawler/app/gui/main_window.py` straggler thread 累積不終止**（Critical）
  - 原因：`w.wait(5_000)` 後仍在跑的 thread 直接解除引用，反覆 start/stop 累積 live thread
  - 修正：收集 `[w for w in self._workers if w.isRunning()]`，逐一 `w.terminate(); w.wait(1_000)`，並在 log 顯示數量

### Fixed (Wave 2 — Resource Leaks & Race Conditions)

- **`sb3/app/rl/models/features_extractor.py` box head O(N²) Python 指定**（Performance）
  - 原因：9×9 list，81 次 Python-level tensor 賦值 + 兩層 nested `torch.stack`，forward pass 效率差
  - 修正：`torch.stack(box_results, dim=1).reshape(B,3,3,3,3,H).permute(0,1,3,2,4,5).reshape(B,9,9,H)`
  - 關鍵：`permute(0,1,3,2,4,5)` 將 `(B,box_row,box_col,local_row,local_col,H)` 轉為正確空間排列 `(B,box_row,local_row,box_col,local_col,H)`，輸出與原始 scatter 版完全一致（以 `torch.allclose` 驗證）

- **`sb3/app/rl/curriculum/callback.py` `_success_buf` 無鎖並發寫入**（Race Condition）
  - 原因：`_success_buf` deque 和 `_diff_success` dict 從多個 SubprocVecEnv worker callback 並發讀寫
  - 修正：`self._buf_lock = threading.Lock()`；所有讀寫包在 `with self._buf_lock:` 內
  - TOCTOU 修正：`_maybe_advance()` 先在鎖內 snapshot `stage_idx`，計算完再以 `if self._stage_idx == stage_idx:` 重新驗證後才寫入，避免雙重 stage advance
  - `_on_rollout_end()` 的 `logger.record()` 移至鎖外（snapshot 後計算），避免長時間持鎖

- **`sb3/app/data/pool_db.py` thread-local DB connection 不釋放**（Resource Leak）
  - 原因：`_get_conn()` 以 `self._local` 快取連線，SubprocVecEnv subprocess 整個訓練週期都不關閉
  - 修正：新增 `close()` 方法（`getattr(self._local, "conn", None)` 安全取值）和 `__del__` 呼叫它
  - 為何用 `getattr`：`threading.local` 的屬性只在設定過的 thread 上存在，直接存取會 `AttributeError`

- **`crawler/app/gui/db_panel.py` refresh() 例外傳播到 Qt event loop**（Stability）
  - 原因：`get_pool_stats()` 因 DB locked 等問題拋出例外，Qt timer callback 靜默停止
  - 修正：`refresh()` 包 `try-except`；每次例外都更新 label 顯示 `DB 錯誤: {e}`（非僅第一次）；成功時重置狀態

- **`crawler/app/web/proxy_manager.py` executor 關閉後 socket 仍懸空**（Resource Leak）
  - 原因：`executor.shutdown(wait=False)` 立即返回，驗證 socket 仍持有連線
  - 修正：`executor.shutdown(wait=True, cancel_futures=True)` — 取消 pending future 並等待 in-flight probe 完成

- **`crawler/app/core/worker.py` get_pool_stats() 高頻 DB 讀取**（Performance）
  - 原因：10 個 worker 每次迭代都呼叫 `db.get_pool_stats()`，≈20 reads/sec 純粹浪費
  - 修正：`_STATS_TTL = 2.0`；`_get_stats()` 以 `time.monotonic()` 實作 2 秒 TTL 快取
  - 兩個 `db.get_pool_stats()` 呼叫點都改為 `self._get_stats()`

### Tests Added

**Wave 1:**
- `sb3/tests/test_gym_env_stability.py` — reset() 遞迴深度限制
- `sb3/tests/test_bc_guards.py` — BC loss NaN guard（quality=1e-9 測試邊界）
- `sb3/tests/test_eval_callback_safety.py` — eval exception safety + atomic logger
- `crawler/tests/test_worker_stability.py` — traceback format + straggler terminate

**Wave 2:**
- `sb3/tests/test_features_extractor.py` — box head 空間映射正確性（`torch.allclose` vs old scatter）
- `sb3/tests/test_curriculum_lock.py` — curriculum lock concurrent access
- `sb3/tests/test_pool_db_close.py` — `close()` / `__del__` 不拋出例外
- `crawler/tests/test_db_panel.py` — refresh() exception safety
- `crawler/tests/test_worker_stability.py` — TTL cache（2s 內不重複呼叫 DB）

---

## [v10] 架構強化：26-channel Obs + Per-cell Action Head + 訓練基礎設施（2026-04-26）

### Changed

- **`sb3/app/rl/envs/sudoku_gym_env.py`** — 觀察空間 9 → 26 channels
  - Ch 0-8：one-hot board planes（digit 1..9 → index 0..8），取代原本 board/9.0 ordinal encoding
  - Ch 9-17：per-digit candidate planes（v is legal at (r,c)），取代單一 candidate_count channel
  - Ch 18-25：auxiliary（fixed, empty, row/col/box fill ratio, cand_count/9, naked-single, hidden-single）

- **`sb3/app/rl/models/features_extractor.py`** — 架構改為 per-cell action head
  - 原本：27 ConstraintHeads → mean-pool → (batch, 192)
  - 現在：27 ConstraintHeads → `cell_proj`(B,81,9)→(B,729) + `global_proj`(mean-pool)→(B,192)
  - 輸出：(batch, 921) = 729 per-cell logits + 192 global context
  - `net_arch` 對應改為 `{"pi": [], "vf": [128]}`：policy head 直接 Linear(921→729)，value head 有 128-unit MLP

- **`sb3/app/rl/models/sudoku_ppo.py`** — `_bc_pass()` 修正
  - `evaluate_actions()` 現在傳入 `action_masks=masks_t`，BC 分布與 rollout 時的 masked policy 一致
  - 修正 dtype 注釋：`rollout_buffer.action_masks` 為 float32，cast 至 bool 在下一行發生

- **`sb3/app/rl/curriculum/callback.py`** — resume 支援強化
  - 新增 `_on_training_start()`：從 checkpoint 恢復時自動 re-apply 當前 stage 的 difficulty distribution
  - 新增 `stage_idx` bounds-check，防止 JSON 與 curriculum stage 數不符時的 IndexError
  - `stage_eps` 納入 JSON 持久化，確保 backstop timer 不因 resume 重置

- **`sb3/train_sb3.py`** — curriculum state save/load；`ent_coef` 0.05→0.01；VecNormalize `clip_reward` 10→50
  - 新增 curriculum state JSON save（`{stage_idx, total_eps, stage_eps, mrv_prob}`）隨 `model.save()` 一起寫出
  - 新增 curriculum state restore 區塊（`--load-model` 時讀取 JSON 並還原所有欄位）
  - `getattr(model, "mrv_prob_init", 0.80)` 容錯舊 checkpoint（無此屬性）

### Added

- **`sb3/app/rl/curriculum/eval_callback.py`**（新增）— `SudokuEvalCallback`
  - 每 50k steps 對各難度分別評估 20 局，記錄 `eval/success_rate_L{d}` 和 `eval/success_rate_overall`
  - 使用 maskable predict：`model.predict(obs[np.newaxis], action_masks=masks[np.newaxis], deterministic=True)`
  - Eval env 在 `_init_callback()` 建立一次，`_on_training_end()` 關閉，避免每次觸發重新建立

- **Tests**（5 個新測試檔案）
  - `tests/test_obs_encoding.py` — 9 tests：shape、one-hot ch 0-8、candidate planes ch 9-17、aux ch 18-24 語義正確性
  - `tests/test_features_extractor.py` — 4 tests：output shape (4, 921)、backward pass through all 27 heads
  - `tests/test_bc_masks.py` — BC evaluate_actions with action_masks 產生正確 log_prob
  - `tests/test_curriculum_save_load.py` — curriculum JSON round-trip save/restore
  - `tests/test_eval_callback.py` — SudokuEvalCallback 在 total_timesteps budget 內正確觸發

### Fixed (Critical)

- **`sb3/app/rl/models/features_extractor.py` col/box heads 梯度靜默消失**（Critical）
  - 原因：`torch.zeros(...)` + in-place slice `col_out[:, :, c, :] = head(...)` — autograd 無法追蹤 in-place 寫入無梯度 tensor
  - 影響：9 col_heads + 9 box_heads（共 18/27 個 ConstraintHead）完全無梯度更新
  - 修正：`torch.stack([self.col_heads[c](...) for c in range(9)], dim=2)` 和 nested list + `torch.stack` 拼合 box_out
  - 驗證：修正後 col_grad norm ≈ 70.05、box_grad norm ≈ 105.30、row_grad norm ≈ 91.79

- **`sb3/app/rl/models/sudoku_ppo.py` BC loss 在 unmasked distribution 計算**（Critical）
  - 原因：`evaluate_actions(obs_t, ta)` 未傳 `action_masks`
  - 影響：BC log_prob 在不同於 rollout 的 distribution 上計算，梯度方向有偏差
  - 修正：從 `rollout_buffer.action_masks[teacher_mask]` 取 masks（float32）轉 bool 後傳入

### Architecture (sb3/ updated)

| Component | Before (v9) | After (v10) |
|-----------|-------------|-------------|
| Obs channels | 9 (ordinal board + 7 aux) | 26 (9 one-hot + 9 candidate planes + 8 aux) |
| Extractor output | (B, 192) | (B, 921) = 729 per-cell + 192 global |
| net_arch | default | `{"pi": [], "vf": [128]}` |
| BC masks | not passed | `action_masks=masks_t` in evaluate_actions |
| Eval | none | SudokuEvalCallback every 50k steps |
| Resume | partial | full curriculum JSON save/load |

---

## [v9] 專案拆分：legacy/ + sb3/ + SB3 MaskablePPO 訓練系統（2026-04-25）

### Added

- **`sb3/`**（新增）— 主力 SB3 訓練系統，完全獨立於 legacy/ 版本
  - `sb3/train_sb3.py` — 新入口；argparse 支援 `--timesteps`、`--n-envs`、`--device`、`--load-model`、`--no-teacher`、`--no-vecnorm`
  - `sb3/app/rl/envs/sudoku_gym_env.py` — `SudokuGymEnv`：Gymnasium env，`action_masks()`，`set_difficulty_distribution()`，9-channel obs（新增 hidden-single channel）
  - `sb3/app/rl/envs/sudoku_solver.py` — backtracking solver with MRV heuristic；`reset()` 時預先解出唯一解
  - `sb3/app/rl/envs/reward_computer.py` — `RewardComputer`：dense solution-guided reward（naked single +3, hidden single +2, cascade +0.5, unit +5, done +20, wrong −3）
  - `sb3/app/rl/models/features_extractor.py` — `SudokuFeaturesExtractor`（BaseFeaturesExtractor）：27 ConstraintHeads → mean pool → (batch, 192)；ported from torch_agent.py
  - `sb3/app/rl/models/sudoku_ppo.py` — `SudokuMaskablePPO`：BC loss 作為獨立 optimizer pass；teacher data 透過 `collect_rollouts()` monkey-patch 從 info dict 取得
  - `sb3/app/rl/curriculum/callback.py` — `CurriculumCallback`：4-stage 難度遞增，threshold 或 backstop 觸發 stage advance，entropy < 0.3 nats 警告
  - `sb3/requirements.txt` — 獨立依賴（torch, stable-baselines3, sb3-contrib, gymnasium, tensorboard, pytest）

- **`.gitignore`**（新增）— 排除 `__pycache__/`、`*.pyc`、`runs/`、`*.pt.old`、`*.db.old`

### Changed

- **專案根目錄重組**：所有程式碼移入子資料夾
  - `legacy/` — 封存舊版 `main_train.py` + PyQt6 GUI 系統（完全不修改）
  - `sb3/` — 主力 SB3 版本（持續開發）
  - `data/puzzle_pool.db` — 保留於根目錄，兩版本共用

- **DB 路徑修正**（專案拆分後的關鍵 bug fix）：
  - `sb3/train_sb3.py`：`DB_PATH = "../data/puzzle_pool.db"`
  - `legacy/app/config/schema.py`：`db.path` default → `"../data/puzzle_pool.db"`
  - `legacy/data/user_config.json`：`"db.path"` → `"../data/puzzle_pool.db"`（**最重要**：user_config 的明確值會覆蓋 schema default，兩者都必須改）

### Root Cause Fixed

- **Legacy 爬蟲存取錯誤**：`legacy/data/user_config.json` 有明確的 `"db.path": "data/puzzle_pool.db"`，覆蓋了 schema default，導致爬蟲試圖讀取 `legacy/data/puzzle_pool.db`（不存在）。修正：同時更新 schema default 和 user_config 的值。

### Architecture

| | legacy/ | sb3/ |
|--|---------|------|
| RL framework | 自製 PPO (torch) | SB3 MaskablePPO |
| Env | SudokuEnv (gym-like) | SudokuGymEnv (gymnasium) |
| Curriculum | 3-phase cosine decay | 4-stage dist escalation |
| Reward | sparse + shaping | dense solution-guided |
| BC | quality-weighted, inline | quality-weighted, separate pass |
| Parallelism | single env | 8× SubprocVecEnv |
| GUI | PyQt6 | 無（TensorBoard） |

---

## [v8] 學習框架重設計 + 全專案 Critical Review（2026-04-21）

### Added

- **`app/sudoku/phase_manager.py`**（新增）
  - `PhaseConfig`：Phase 轉換閾值容器（T1/T2/tau1/tau2/mrv_init/mrv_floor）
  - `PhaseManager`：三階段課程管理（Phase 1 Bootstrap → Phase 2 Transfer → Phase 3 RL-only）
  - 分段餘弦 MRV 衰減曲線：Phase 1 = 0.90→0.40，Phase 2 = 0.40→0.10，Phase 3 = mrv_floor (0.05)
  - 雙觸發轉換：`success_rate >= tau`（performance-based）優先，`mrv_step >= T`（time backstop）作保底
  - 支援 `state_dict()` / `load_state_dict()` 用於 checkpoint

- **`app/sudoku/teacher_engine.py`**（新增）
  - `TeacherEngine`：確定性四層品質金字塔 MRV Teacher
  - Level 1 naked single (quality=1.00) → Level 2 hidden single (0.75) → Level 3 min≤2 (0.40) → Level 4 min≤4 (0.15) → Level 5 abstain (0.0)
  - 完全確定性：`min(candidates)` 替代 `random.choice`，同一狀態永遠給相同 label，BC 梯度方向一致
  - 取代舊版 `_mrv_action()` 方法

- **`app/sudoku/policy_demo_store.py`**（新增）
  - `PolicyDemoStore`：Phase 3 自我改善飛輪的 thread-safe ring buffer
  - 儲存 policy 主導（≥50% steps）的成功 episode
  - `try_add_episode()`：`min_ratio` 門檻防止低品質示範污染
  - 支援 `state_dict()` / `load_state_dict()` 用於 checkpoint

- **`app/config/schema.py`** — 新增 7 個訓練 Phase 相關設定
  - `training.phase1_steps` (30000)、`training.phase2_steps` (90000)
  - `training.phase1_tau` (0.30)、`training.phase2_tau` (0.65)
  - `training.teacher_max_cand` (4)
  - `training.policy_demo_capacity` (2048)、`training.policy_demo_weight` (0.30)

### Changed

- **`app/sudoku/torch_agent.py`** — 全面重構學習語義
  - `RolloutBuffer.push()` 新增 `quality: float` 參數；新增 `quality_weights` tensor
  - `get_tensors()` 回傳 6-tuple（含 `is_mrvs`、`quality_weights`）
  - `TorchAgent.__init__` 建立 `PhaseManager`、`TeacherEngine`、`PolicyDemoStore`；新增 `_pending_quality`、`_demo_states`、`_demo_actions`、`_demo_total_steps` 追蹤
  - `select_action()` 改用 `TeacherEngine(env)` 取得 `(action, quality)`；quality=0.0 的 fallback 不標記為 MRV
  - `_ppo_update()` BC loss 改為 quality-weighted：`bc_raw = -(log_prob * w).sum() / (w.sum() + 1e-8)`
  - `_ppo_update()` 加入耦合衰減：`eff_bc = bc_coef × (mrv_prob/mrv_init)^β`，β 依 Phase 不同（0.5/1.0/999）
  - `_ppo_update()` Phase 3 加入 PolicyDemoStore soft BC loss
  - `_ppo_update()` 回傳 dict 新增 `mrv_ratio`、`bc_loss`、`bc_ppo_ratio`、`eff_bc`、`phase`
  - `finish_episode()` 觸發 Phase 轉換偵測 + Phase 3 demo 存入
  - `save_model()` / `load_model()` 新增 `phase_manager`、`policy_demo_store` checkpoint 支援
  - `last_loss_value`、`last_entropy_value`、`last_advantage_mean` 初始化從 `None` 改為 `0.0`

- **`app/config/schema.py`**
  - `training.mrv_min_prob` 預設值 0.0 → 0.05，description 更新為「Phase 3 Floor」
  - `training.mrv_decay_steps` 預設值 60000 → 90000，description 更新為「Phase 2 endpoint」
  - 移除過時的 `proxy.max_rotations`、`crawler.puzzle_ready_timeout_ms`、`crawler.puzzle_ready_poll_ms`（schema 中無對應邏輯）
  - 新增 `training.bc_coef` (default 1.0)

- **`main_train.py`**
  - `create_agent()` 傳入 7 個新 Phase/Teacher/Demo config 參數
  - `bc_coef` 從硬編碼 1.0 改為 `config.get("training.bc_coef")`
  - `all_results` 增加 running accumulators (`_n_results`, `_run_steps` 等)，避免長期訓練時 numpy array 累積耗盡記憶體
  - `all_results` 以 rolling window (`logging.rolling_stats_window`) 限制大小

- **`app/config/manager.py`**
  - `set()` 改為鎖外 I/O：取 snapshot 後釋放鎖，再做 JSON 寫入，避免 20 個 producer 執行緒造成串行等待

### Fixed

- **`app/sudoku/phase_manager.py` MRV 曲線邊界計算錯誤**（Critical）
  - 原始公式：`mrv_floor + (mrv_init - 0.40) * cos_w`，在 step=0 時回傳 0.55 而非 0.90
  - 原因：以 `mrv_floor` 作為 cosine 基底，應以各 Phase 的終點值（0.40 / 0.10）作基底
  - 修正：Phase 1 → `0.40 + (mrv_init - 0.40) * cos_w`；Phase 2 → `0.10 + (0.40 - 0.10) * cos_w`

- **`app/sudoku/torch_agent.py` 初始值 None 導致 GUI TypeError**（Critical）
  - `last_entropy_value`、`last_loss_value`、`last_advantage_mean` 初始化為 `None`
  - `getattr(agent, "last_entropy_value", 0.0)` 無法攔截（屬性存在但值為 None）
  - GUI `stats_panel.py` 收到 None 後 `f"{entropy:.4f}"` 拋出 `TypeError`
  - 修正：初始化改為 `0.0`

- **`app/gui/board_grid_panel.py:74` `on_episode_end()` 丟失 level**（Critical）
  - Episode 結束時未傳 `level`，`_level` 被重設為 0，難度徽章和星等消失
  - 修正：`w.update_state(..., w._level)` 保留現有 level（同 `on_board_update` 的修法）

- **`main_train.py` GUI `stats_update` 被 `print_rolling_stats` 旗標控制**（Critical）
  - `gui_bus.put("stats_update", ...)` 包在 `if config.get("logging.print_rolling_stats"):` 內
  - 使用者關閉文字統計時 GUI 面板同時凍結
  - 修正：將 print 條件與 GUI 更新分離，GUI 只依 `print_every_episodes` 間隔觸發

- **`main_train.py` 跳過題目不回退 `episode_idx`**（Warning）
  - `tries >= max_tries` 時 `continue` 但 `episode_idx` 已加 1，進度計數器偏高
  - 修正：`episode_idx -= 1` 後再 `continue`

- **`app/config/manager.py` `reset_to_default()` 在鎖內做 I/O**（Warning）
  - 與 `set()` 的修正模式不一致
  - 修正：先取 snapshot 再釋放鎖，鎖外呼叫 `_save(snapshot)`

### Refactored

- **`app/sudoku/torch_agent.py`** — Phase 3 PolicyDemoStore soft BC 移除巢狀 `autocast`
  - 原本在已進入的外層 `autocast` 中再開一層，多餘
  - 移除內層 `with autocast(...)` 包裝

- **`app/sudoku/validator.py`** — `_is_group_valid()` 改用 set 比較
  - `sorted(...) == [1,2,3,4,5,6,7,8,9]` 每次呼叫建立新 list（共 27 次/驗證）
  - 改為 `{int(x) for x in nums} == _VALID_GROUP`，`_VALID_GROUP` 為模組級 frozenset

- **`app/gui/stats_panel.py`** — 移除死變數 `pct`
  - `pct = int(rollout_size / max(rollout_cap, 1) * 100)` 計算但從未使用

---

## [v7] GUI 視覺化強化 + 設定系統重構（2026-04-20）

### Added

- **難度徽章（Difficulty Badge）**（`app/gui/board_widget.py`）
  - 每個盤面標題列右側顯示彩色徽章：Easy=綠 / Med=橘 / Hard=紅 / Evil=紫
  - `_LEVEL_INFO` dict 統一管理顏色、縮寫、星等字串
- **難度星等第二列**（`app/gui/board_widget.py`）
  - 標題列擴為兩行（`_TITLE_ROW1=20px` + `_TITLE_ROW2=18px`，`TITLE_H=38px`）
  - 第二行以難度色背景顯示 ★☆☆☆ 等星等
- **系統托盤（QSystemTrayIcon）**（`app/gui/training_gui.py`）
  - 隱藏視窗後可透過托盤雙擊或右鍵「顯示 GUI」恢復
  - `closeEvent`：訓練中→隱藏（ignore），已停止→正常退出
- **⚙ 設定對話框**（`app/gui/settings_dialog.py` 新增）
  - 動態從 `CONFIG_SCHEMA` 生成 UI（8 個 Tab）
  - `reload_required=False` 設定即時生效，`True` 則顯示 ⚠ 需重啟提示
- **Config 系統**（`app/config/` 新增）
  - `schema.py`：全部 60+ 設定的 schema 定義（type, default, min, max, label, description）
  - `manager.py`：`ConfigManager` — thread-safe get/set，JSON 持久化（`data/user_config.json`），hot-reload callback
  - 分 8 類：`gui`, `training`, `run`, `crawler`, `proxy`, `logging`, `model`, `db`

### Changed

- **`main_train.py`** — 移除全部 110 行硬編碼常數，改為 94 個 `config.get("key")` 呼叫
  - `import json` 移至檔案頂部（原散落在函式內部）
  - 移除冗餘的 `import threading as _threading`，統一用 `threading.Lock()`
- **`app/gui/board_grid_panel.py`** — `on_episode_start` 加入 `level` 參數並傳遞給 widget
- **`app/gui/stats_panel.py`** — 移除未使用的 `QColor` import

### Fixed

- **`board_widget.py` 雙重 `TITLE_H` 定義**（Critical）
  - 舊版在 `_C` 色彩 dict 之後留有 `TITLE_H = 22`，覆蓋了第 14 行的 `TITLE_H = 38`
  - 導致難度星等第二列（y=20–38）幾乎全被盤面（oy=22）蓋住，僅剩 2px 可見
  - 修復：移除多餘的 `TITLE_H = 22`
- **`board_grid_panel.on_board_update` 中途清零 level**（Warning）
  - 中途更新未傳 `level`，導致 `self._level` 被重設為 0，難度徽章在每步後消失
  - 修復：改為 `w.update_state(..., w._level)` 保留現有 level

---

本文件記錄本專案的重大設計決策與架構變更，供未來維護時參考。
若某次改動的動機不明，可在此查找背景說明。

---

## [v6] 多難度 + Proxy 支援 + 背景爬蟲重構

### 混合難度抓題（`main_train.py`）
- 移除全域 `SUDOKU_LEVEL = 1` 與 `URL`，改用 `SUDOKU_LEVEL_DIST = {1: 0.6, 2: 0.3, 3: 0.1}`
- 新增 `_pick_level()` 函式，每次抓題前以加權隨機選取難度
- 訓練迴圈改為 `fetch_one_puzzle_for_training(level=None)`，從全難度池取題（依 `tries ASC, best_empty ASC` 排序形成自然課程）
- 故意不含 level=4（evil），等模型穩定後再加入

### Proxy 管理重構（`app/web/proxy_manager.py`）
- 新增 `_PROTO_PRIORITY = {"http": 0, "socks5": 1, "socks4": 2}`，HTTP 代理優先進入輪換池（因驗證更嚴格：實際抓取頁面確認 `puzzle_grid`，SOCKS 只做 TCP connect）
- `download_all()`：下載後先 shuffle 再穩定排序，確保同協定內保持隨機、跨協定 HTTP 在前
- `start_background_validation()` 完全重寫：
  - 新增 `threading.Event(_stop_validation)` 支援外部中止
  - `_worker()` 每迭代檢查 stop event，收到信號即跳出
  - 使用 `executor.shutdown(wait=False, cancel_futures=True)`（需 Python 3.9+）立即取消未執行任務
  - 改為邊驗證邊 append 至 `self._proxies`（非批量替換），爬蟲可在驗證期間先以直連啟動
- 新增 `stop_validation()` 方法，供主程式 `finally` 區塊呼叫
- `main_train.py` `finally` 區塊：`proxy_manager.stop_validation()` 在 `_stop_event.set()` 之前呼叫，確保按 F9 後背景驗證能乾淨停止

### 爬蟲日誌靜音（`main_train.py`）
- 新增 `PRINT_PRODUCER_SUCCESS_LOG = False`（預設關閉），避免 20 個 worker 的成功插題訊息淹沒 PPO 更新輸出
- 新增 `log_producer_success()` 包裝函式，取代原本的 `log_pool()`
- Proxy 驗證進度間隔從 100 改為 500，減少噪音
- 移除 `rotate()` 的 verbose print

### 驗證全量代理（`main_train.py` + `proxy_manager.py`）
- `PROXY_VALIDATE_COUNT = None`（原為固定數字），對應 `start_background_validation(max_validate=None)` 表示驗證所有下載的代理

---

## [v5] requests 爬蟲取代 Playwright（`app/web/reader.py`）

- 新增 `fetch_puzzle_via_requests()`：直接用 `requests` 抓取 `east.websudoku.com` HTML，速度比 Playwright 快 5–10 倍
- 使用 `_PuzzleHTMLParser`（`html.parser`）直接解析 input ID 格式 `f{col}{row}`
- 支援 iframe 追蹤（websudoku 題目有時在 iframe 內）
- 封鎖偵測：`_BLOCK_SIGNATURES` 字串清單，命中即拋出 `BlockedError`
- `BrowserManager` 和 `WebSudokuReader`（Playwright 版）保留備用，不再是主要流程
- URL 改用 `http://`（非 https），避免 SOCKS proxy + HTTPS SSL 憑證驗證問題

---

## [v4] PPO 架構重大修正（`app/sudoku/torch_agent.py`）

- **Value 反歸一化 Bug Fix**：GAE 計算前先將 value 預測反歸一化（`values * std + mean`），否則 advantages 尺度崩壞
- **BC Loss（Behavior Cloning）**：MRV 專家示範動作以 `-log_prob` 損失直接監督 policy，繞過 PPO Clip 限制，加速早期學習
- **Adaptive Entropy（SAC-style）**：以 `_log_alpha` 參數自動調節 entropy coefficient，目標 `H ≈ target_entropy`
- `RolloutBuffer` 新增 `is_mrvs` 布林標記，標記哪些 step 是 MRV 示範動作，供 BC Loss 使用
- `SudokuPPONet`：CNN 改為 cell-level embedding + 三組 ConstraintHead（行/列/宮），比純 CNN 更符合數獨約束結構

---

## [v3] Reward 重設計（`app/sudoku/env.py`）

- **Naked Single** +3.0（候選數唯一的格子，最確定的填法）
- **Hidden Single** +1.5（在行/列/宮中，某數字只有此格可填）
- **Dead End** −30.0（製造死局，大幅加強讓 PPO advantage 對比顯著；舊版 −15）
- `REWARD_BOARD_DONE` 從 30 降至 15（全局驗證獎勵由 `SUCCESS_BONUS` 負責，避免重複計算）
- 新增 `_is_hidden_single()` 邏輯，在 `step()` 填格前判斷 reward 類型

---

## [v2] SQLite 題庫（`app/data/pool_db.py`）

- 新增 `PuzzlePoolDB`：puzzles + solutions 兩張表，WAL 模式，threading.local 連線池
- `level` 欄位：難度等級（1–4），含舊資料庫 migration（`ALTER TABLE ADD COLUMN`）
- `fetch_one_puzzle_for_training()`：原子性鎖定 + `ORDER BY tries ASC, best_empty ASC` 優先訓練進度較好的題目
- `mark_puzzle_attempt()`：追蹤 `best_empty`、`best_reward`、`tries` 等統計欄位

---

## Bug Fixes（各版本累積）

| 日期       | 檔案                         | 問題描述                                                                         | 修復方式                                                       |
|------------|------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------|
| 2026-04-21 | `app/sudoku/phase_manager.py`| Phase 1 step=0 時 mrv_prob 回傳 0.55 而非 0.90（cosine 基底用了 mrv_floor）     | 改用各 Phase 終點值（0.40/0.10）作基底                        |
| 2026-04-21 | `app/sudoku/torch_agent.py`  | `last_entropy_value` 初始 None → GUI `f"{entropy:.4f}"` TypeError               | 初始化改為 `0.0`                                               |
| 2026-04-21 | `app/gui/board_grid_panel.py`| `on_episode_end()` 未傳 level → 難度徽章在 episode 結束時消失                   | `w.update_state(..., w._level)` 保留現有 level                 |
| 2026-04-21 | `main_train.py`              | `stats_update` 事件被 `print_rolling_stats` 旗標誤控，關閉文字統計時 GUI 凍結   | 將 print 條件與 GUI 更新條件分離                               |
| 2026-04-21 | `main_train.py`              | 跳過超試次題目時 `episode_idx` 未回退，進度計數偏高                             | 增加 `episode_idx -= 1` 後再 `continue`                        |
| 2026-04-21 | `app/config/manager.py`      | `reset_to_default()` 在鎖內做 I/O，與 `set()` 修正後的風格不一致                | 取 snapshot 後釋放鎖，鎖外呼叫 `_save(snapshot)`              |
| 2026-04-20 | `main_train.py`              | `"reward" in dir()` 語義錯誤（`dir()` 非 scope 查詢）                           | 改為 `"reward" in locals()`                                    |
| 2026-04-20 | `app/data/pool_db.py`        | `mark_puzzle_attempt` 未清除 `locked_by`/`locked_at`，殘留鎖定                  | UPDATE 時加入 `locked_by=NULL, locked_at=NULL`                 |
| 2026-04-20 | `app/data/pool_db.py`        | `upsert_puzzle` 將 `best_empty`/`last_empty` 硬編碼為 81，初始值不準確          | 改為 `81 - givens`（實際初始空格數）                           |
| 2026-04-20 | `app/web/proxy_manager.py`   | F9 後背景驗證 thread 繼續跑（無停止機制）                                       | 新增 `_stop_validation` Event + `stop_validation()`            |
