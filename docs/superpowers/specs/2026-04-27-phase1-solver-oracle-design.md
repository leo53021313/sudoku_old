# 設計文件：Phase 1 — Solver-as-Oracle + 訓練穩定性修正

**日期：** 2026-04-27
**類型：** RL 訓練系統重構
**狀態：** 設計完成，待 user review 後進入 writing-plans
**所屬計畫：** 「成功訓練出能解 4 種難度數獨的 AI」**第 1 期**（共 2 期，第 2 期 = inference-time search，待 Phase 1 訓練完成後再 brainstorm）

---

## 1. 背景與目標

### 1.1 背景

1.37M 步訓練後，model 出現嚴重偏科：

| 難度 | rollout success | eval success | 解讀 |
|---|---|---|---|
| L1 | 0 ~ 0.03 | 0% | 完全遺忘 |
| L2 | 0.92 ~ 0.97 | **0%** | 訓練 / eval 嚴重落差，疑似 overfit MRV teacher |
| L3 | 0.11 ~ 0.96 | 100% | 大幅震盪，但 eval 集上有解 |
| L4 | 0 | 0% | 從未解出 |

PPO 指標也不健康：`approx_kl = 0.05~0.12`（目標 <0.02）、`clip_fraction = 0.28~0.36`（目標 <0.20）、`entropy_loss = -1.0~-1.3`（持續下滑）。

### 1.2 病因分析

1. **Teacher 訊號弱**：`TeacherEngine` 在 Level 3-4 只用 MRV 啟發式（候選最少的格子），**不給正解**——L4 evil 完全沒有有意義的 BC signal
2. **L2 overfit MRV 模式**：rollout 看到的 puzzle 都被 MRV teacher 「指過路」，model 學到的是 teacher 的軌跡而非通用解法
3. **L1 catastrophic forgetting**：Stage 4 中 L1 只佔 10%，每 rollout ~19 個 episode，不足以維持
4. **PPO 不穩**：`n_epochs=10` × 64 minibatches = 640 梯度步/rollout，policy 飄離 rollout policy 太遠 → 高 KL、高 clip_fraction
5. **Entropy collapse**：`ent_coef=0.01` 太低，配上 stage 4 的高 reward 變異，探索性快速死亡

### 1.3 目標（Phase 1 結束後 model 應達到）

| 難度 | 目標成功率 |
|---|---|
| L1 | ≥ 80% |
| L2 | ≥ 80% |
| L3 | ≥ 60% |
| L4 | ≥ 30% |

PPO 指標健康：`approx_kl < 0.03`、`clip_fraction < 0.20`、`entropy_loss > -1.5` 不持續下滑。

L4 ≥ 80% 是 Phase 2 的目標（inference-time search 拉上去）。

### 1.4 非目標（明確排除）

- ❌ 任何 inference-time search（MCTS、beam search）—— Phase 2 範圍
- ❌ 修改 network 架構（27 ConstraintHeads + 192-dim features 不動）
- ❌ 改 action space（保留 729 + mask）
- ❌ 改觀察空間（26 channels 不動）
- ❌ 改 reward 結構（naked +3, hidden +2, cascade +0.5, unit +5, done +20, wrong −3 不動）
- ❌ 動 crawler、legacy/、demo.bat、README.md、簡報

---

## 2. New TeacherEngine 設計

### 2.1 核心改動

**目前** `sb3/app/sudoku/teacher_engine.py`：4 級 quality pyramid，**Level 3-4 用 MRV + min(candidates) 當 value**（不是正解）。

**新版**：所有 level 的 `value` 都來自 `solution[cell]`（reset 時 backtracking solver 已經算好的正解）。Cell 選擇用「分層技巧偵測」：

```python
def get_action_and_quality(state):
    # 1. 嘗試 naked single
    cell = find_naked_single(state)
    if cell:
        return (cell, solution[cell]), 1.00

    # 2. 嘗試 hidden single（環境已有 _is_hidden_single helper）
    cell = find_hidden_single(state)
    if cell:
        return (cell, solution[cell]), 0.75

    # 3. 嘗試 pointing pair / box-line reduction
    #    (兩者實作邏輯接近，本 spec 把它們合併成單一函式 find_pointing_pair_target；
    #     第一版 MVP 只實作 pointing pair，box-line reduction 留 TODO 但 quality 仍給 0.50)
    cell = find_pointing_pair_target(state)
    if cell:
        return (cell, solution[cell]), 0.50

    # 4. MRV fallback（候選最少的格子）
    cell = mrv_pick(state)
    return (cell, solution[cell]), 0.30
```

### 2.2 為何分層

讓 model 學到「**先解容易的、再解難的**」這個排序。對 L4 evil 也有效——大部分 evil 仍從 naked/hidden single 開始解，只有少數中段需要 pointing pair。

### 2.3 Quality 數值意義

`quality` 進 BC loss：`bc_loss = -Σ(log_probs[teacher_action] × quality)`。高 quality 樣本對 BC 貢獻大；低 quality 仍提供基底訊號（不像舊的 MRV value 是錯誤訊號）。

### 2.4 修改檔案

- `sb3/app/sudoku/teacher_engine.py`：核心改動 ~250 行（含 4 個技巧偵測函式）
- `sb3/app/rl/envs/sudoku_gym_env.py`：可能小幅調整 teacher 介面（傳入 `solution`）
- `sb3/tests/`：新增 `test_oracle_teacher.py`，驗證每個 level 的偵測正確性 + value 永遠匹配 solution

---

## 3. PPO / Training HP 改動

| HP | 目前 | 新值 | 理由 |
|---|---|---|---|
| `n_epochs` | 10 | **4** | KL 高的主因 |
| `clip_range` | 0.2 | **0.1** | 直接降 clip_fraction |
| `ent_coef` | 0.01 | **0.02** | 拖慢 entropy collapse |
| `bc_coef` schedule | 與 `mrv_prob` 耦合，衰到 0.0625 | **獨立 `LinearSchedule(1.0, 0.3, end_fraction=1.0)`** | Oracle 永遠正確，BC 全程都該有影響力 |
| `learning_rate` | `LinearSchedule(3e-4, 1e-5)` | 不變 | 健康 |
| `gamma`, `gae_lambda`, `vf_coef`, `max_grad_norm` | 0.99, 0.95, 0.5, 0.5 | 不變 | 標準值 |

### 3.1 BC 解耦的程式碼影響

`sb3/app/rl/models/sudoku_ppo.py` 目前 `bc_coef_eff = bc_coef × (mrv_prob / mrv_mix_prob)^β` —— 改成：

- 在 `__init__` 建立 `self._bc_schedule = LinearSchedule(1.0, 0.3, end_fraction=1.0)`
- 在 `_bc_pass()` 每次呼叫 `bc_coef_eff = self._bc_schedule(self._current_progress_remaining)` （SB3 在 `learn()` 期間維護此 attr）
- 移除原本與 `mrv_prob` 的耦合公式

`mrv_prob` 仍保留給 SudokuGymEnv 用（控制 rollout 中 teacher 直接介入的比例），但**不再控制 BC loss**。

### 3.2 修改檔案

- `sb3/train_sb3.py`：HP 數值更新
- `sb3/app/rl/models/sudoku_ppo.py`：解耦 bc_coef_eff，改用獨立 schedule

---

## 4. Curriculum 改動

| 變動 | 目前 | 新 | 理由 |
|---|---|---|---|
| Stage 4 分布 | `L1:10 L2:20 L3:35 L4:35` | **`L1:25 L2:25 L3:25 L4:25`** | 防 L1 forgetting；oracle 強了 L4 不需 35% |
| `window` | 100 | **200** | 推進判斷更穩 |
| 推進門檻 (75 / 65 / 55) | 不變 | 不變 | Oracle 加持下會更快達到 |

### 4.1 修改檔案

- `sb3/app/rl/curriculum/callback.py`：`CURRICULUM_STAGES` 第 4 階段分布、`window` 預設值

---

## 5. Warm Start 策略：從零訓練

**選擇 A：完全從零，丟棄 1.37M 與 400k 兩個 checkpoint。**

理由：
1. 新 TeacherEngine 給的 BC 訊號跟舊的根本上不同——舊權重會跟新老師打架
2. 1.37M 已偏科（L2 overfit MRV pattern）
3. 400k 雖較均衡但仍是舊老師產物
4. 機器 fps=212、2M 步 ≈ 6.5 小時，可承受

**操作：** 訓練命令使用 **無 `--load-model` 參數**，從 SB3 預設初始化開始。
舊 checkpoint 保留在 `models/` 目錄不刪——將來作為「Phase 1 vs 舊版」對照組可能有用。

---

## 6. 驗證里程碑（Abort Criteria）

訓練 6 小時不能盲跑——加 `MilestoneCallback`，到下列步數做斷言檢查，**不過直接 raise 中止訓練**：

| 步數 | 檢查指標 | 不過時行為 |
|---|---|---|
| **100k** | `approx_kl < 0.05` AND `entropy_loss > -2.0` | Abort + 印出當下指標 |
| **300k** | `success_rate_L1 (last 200 ep) ≥ 0.75` | Abort + 提示「Stage 1 應已過」 |
| **500k** | `success_rate_L1 ≥ 0.70` AND `L2 ≥ 0.50` | Abort |
| **1M** | `L1 ≥ 0.80` AND `L2 ≥ 0.70` AND `L3 ≥ 0.50` | 警告（不 abort，繼續觀察） |
| **2M（最終）** | `L1, L2, L3 ≥ 0.80` AND `L4 ≥ 0.30` | 算 Phase 1 成功 |

### 6.1 修改檔案

- 新增 `sb3/app/rl/curriculum/milestone_callback.py`（~80 行）
- `sb3/train_sb3.py`：加進 `callback=[curriculum, checkpoint, eval_cb, milestones]`

---

## 7. Eval Diagnostics

當 `SudokuEvalCallback` 中某個 puzzle fail 時，append 一筆 JSONL 到 `sb3/runs/sudoku_sb3/MaskablePPO_X/eval_failures.jsonl`：

```json
{
  "step": 1350000,
  "difficulty": 2,
  "puzzle_id": 12345,
  "first_wrong_step": 7,                  // env.step() 序號，從 0 起算
  "model_picked_cell": [3, 5],
  "model_picked_value": 9,
  "correct_cell_at_that_step": [3, 5],
  "correct_value": 4,
  "teacher_quality_at_that_step": 0.75,
  "candidates_at_cell": [4, 9]
}
```

分析後可區分：
- 選對格子、填錯值（value error）
- 選錯格子（selection error）
- Teacher 在該步本就無 signal（quality < 0.30）

### 7.1 修改檔案

- `sb3/app/rl/curriculum/eval_callback.py`：新增 `_log_failure()` helper

---

## 8. 執行順序

每個 task 獨立、可單獨驗證、可單獨 commit：

| Task | 內容 | 修改/新增檔案數 | 預估時間 |
|---|---|---|---|
| **T1** | 重寫 `teacher_engine.py`（含 4 級偵測 + 單元測試） | 1 修 + 1 新 | 4-6 小時 |
| **T2** | 解耦 BC schedule（`sudoku_ppo.py`） | 1 修 | 1-2 小時 |
| **T3** | 更新 PPO HP（`train_sb3.py`） | 1 修 | 30 分 |
| **T4** | 修 curriculum stage 4（`callback.py`） | 1 修 | 30 分 |
| **T5** | 新增 `MilestoneCallback` | 1 新 + 1 修（train_sb3） | 1-2 小時 |
| **T6** | Eval failures JSONL（`eval_callback.py`） | 1 修 | 30-60 分 |
| **T7** | **跑 2M 步從零訓練** | 0（純執行） | ~6.5 小時 |
| **T8** | 用 `eval_sb3.py` 跑 4 難度 × 各 50 puzzle 終評 | 0（純執行） | 30 分 |
| **T9** | 寫一頁 RESULTS.md（Phase 1 結果摘要） | 1 新 | 30 分 |

**工程時間：** ~10-12 小時（不含訓練）
**訓練時間：** ~6.5 小時（背景跑）
**總 wall-clock：** 約 1.5-2 工作天

---

## 9. 驗收條件（Phase 1 成功）

- [ ] T1-T6 程式碼修改 + 對應單元測試全綠
- [ ] T7 訓練成功跑完 2M 步（未被 milestone abort）
- [ ] T8 最終 eval 達標：L1 ≥ 80%, L2 ≥ 80%, L3 ≥ 60%, L4 ≥ 30%
- [ ] PPO 指標健康：`approx_kl < 0.03`, `clip_fraction < 0.20`
- [ ] L2 rollout/eval 成功率落差 < 15%（解掉 overfit 之謎）
- [ ] T9 RESULTS.md 完成，含與舊 400k checkpoint 的對照數據

---

## 10. 風險與後備

| 風險 | 機率 | 後備 |
|---|---|---|
| 100k milestone fail（PPO 仍不穩） | 中 | 進一步降 `n_epochs` 到 3、`clip_range` 到 0.05；或加 KL target |
| 500k milestone fail（L1/L2 學不起來） | 低 | Oracle teacher 太強，model 變成 BC 模仿器；降 `bc_coef` 上限到 0.5 |
| 2M 完成但 L4 < 30% | 中（forward inference 上限） | 接受、進 Phase 2（inference search）；L4 ≥ 30% 算合理 |
| 訓練中斷（電源、OS 死機） | 低 | 已有 `CheckpointCallback` 每 50k 儲存；可 `--load-model` 續跑 |
| Oracle teacher 跟 RL reward 衝突（BC 拉一邊、PPO 拉另一邊） | 低 | bc_coef 已從 1.0 衰到 0.3，後期 PPO 主導；如果衝突嚴重，提早 milestone 會發現 |

---

## 11. 後續工作（**不在 Phase 1 範圍**）

- **Phase 2**：Inference-time search（beam search 或 MCTS 包住 trained model）→ 把 L4 推到 80%+
- **可能 Phase 3**：架構優化（更深的 ConstraintHead、更大 features_dim）若 Phase 1+2 仍 < 80%
- 整理 RL 訓練心得寫入 HISTORY.md（v13 條目）
