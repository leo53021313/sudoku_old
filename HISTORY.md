# HISTORY.md — 重大變更紀錄

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

| 日期       | 檔案                   | 問題描述                                                          | 修復方式                                          |
|------------|------------------------|-------------------------------------------------------------------|---------------------------------------------------|
| 2026-04-20 | `main_train.py`        | `"reward" in dir()` 語義錯誤（`dir()` 非 scope 查詢）            | 改為 `"reward" in locals()`                       |
| 2026-04-20 | `app/data/pool_db.py`  | `mark_puzzle_attempt` 未清除 `locked_by`/`locked_at`，殘留鎖定   | UPDATE 時加入 `locked_by=NULL, locked_at=NULL`    |
| 2026-04-20 | `app/data/pool_db.py`  | `upsert_puzzle` 將 `best_empty`/`last_empty` 硬編碼為 81，初始值不準確 | 改為 `81 - givens`（實際初始空格數）              |
| 2026-04-20 | `app/web/proxy_manager.py` | F9 後背景驗證 thread 繼續跑（無停止機制）                    | 新增 `_stop_validation` Event + `stop_validation()` |
