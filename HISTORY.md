# HISTORY.md — 重大變更紀錄

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
