# Reasoner — Pure RL with Technique-Based Curriculum (Design)

**Date:** 2026-04-28
**Status:** Brainstormed, awaiting plan
**Replaces:** Active development on `sb3/` (which is being frozen)

---

## 1. Background

`sb3/` 經歷 14+ 個訓練 run 全部在真正 held-out reserved set 上拿 0%。RESULTS.md 記錄了 PPO_8 雖然 in-training eval 95%+，但 reserved set 0%——training pipeline 跑通不等於 generalize。問題是結構性的，不是 hyperparameter 細節：

- Reward shape 給「naked single +3、hidden single +2、unit complete +5」這類 shortcut bonus，model 學會 pattern match 局部 cue 而非整盤推理
- Observation channel 24（naked single flag）和 25（hidden single flag）直接告訴 model 答案位置，model 高度依賴這些 shortcut → eval 時資料分佈一變就崩
- Teacher 用 `env.solution[r,c]` 即 backtracking solver 的全局答案；BC 鼓勵記憶而非推理
- Curriculum 用 backstop 強制升級（5k/15k/30k episodes），即使 success_rate 仍 0 也照升，使 model 在 Stage 4 還沒學會 Stage 1
- 訓練池取題函式 `fetch_one_puzzle_for_training` 對「剩餘空格少的題」優先（best_empty ASC），訓練分佈和 reserved 分佈差異大

## 2. Goals

**Primary**：在 reserved eval set（`data/eval_puzzles.json`）上達到「**穩定的非零 success rate**」並隨訓練步數**單調上升**——比起追求特定百分比，先確認 framework 真的能 generalize。

**Concrete metrics**：
- 200k 步內 `eval/reserved_L1 > 0`（任何非零都比 sb3/ 強）
- 500k 步 `eval/reserved_L1` 穩定爬升（至少看到 0 → 5% → 10% 的軌跡）
- 1M 步 `eval/reserved_L1` reach 30%+
- Stage 1 puzzle（只需技巧 1-3）的 reserved success ≥ 80% 才升 Stage 2

**最低及格線**：500k 步 `eval/reserved_L1` 仍 0 → framework 仍有結構問題，回頭討論。

## 3. Non-Goals

- ❌ Transformer / decoder-only / autoregressive chain-of-thought（已在 brainstorm 拒絕）
- ❌ DSL token 序列輸出
- ❌ Natural language reasoning trace
- ❌ Behavior Cloning / teacher-driven distillation
- ❌ 修改 sb3/——sb3/ 凍結，新系統獨立目錄
- ❌ Port HoDoKu 全部 15 技巧——v1 只做 1-7，足以分組大部分題目

## 4. Architecture Overview

**仍是 MaskablePPO + ConstraintHead network**——這個架構本身對 sudoku 結構是合理的，問題在 reward / obs / teacher / curriculum，不在 model。

**核心改動**：
- 純 RL（移除 BC pass）
- Reward 結構徹底改：對齊 human-style solver
- Observation 移除 shortcut channels
- Curriculum 改技巧分層（不再用 websudoku 難度）
- Teacher 從「全局解答」換成「human-style 推理結果」

```
┌──────────────────────────────────────────────────────────────┐
│  PuzzlePoolDB (data/puzzle_pool.db)                          │
│   ↳ 一次性標注：每題 max_technique_id ∈ {1..15}              │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────┐
        │  CurriculumCallback             │
        │  Stage 1: max_tech ≤ 3          │
        │  Stage 2: max_tech ≤ 7          │
        │  Stage 3: max_tech ≤ 10  (TBD)  │
        │  Stage 4: max_tech ≤ 13  (TBD)  │
        │  Stage 5: max_tech > 13  (TBD)  │
        │  升級條件：reserved 80%+        │
        │  降級條件：50k 步無進展         │
        └─────────────────────────────────┘
                          │
                          ▼
       ┌──────────────────────────────────┐
       │  SudokuGymEnv (24 channels)      │
       │   - reset(): 從 Stage 對應池抽題 │
       │   - step():                      │
       │     ・solver.suggest(board) →    │
       │        (action★, technique★)    │
       │     ・compute reward by比對       │
       │   - obs：移除 ch 24, 25          │
       └──────────────────────────────────┘
                          │
                          ▼
              MaskablePPO + ConstraintHead
              (28-action 合法掩碼，729 logits)
```

## 5. Directory Layout

```
sudoku_old/
├── data/puzzle_pool.db               # 共用，不動
├── sb3/                              # 凍結
└── reasoner/                         # 新系統
    ├── data/
    │   ├── eval_puzzles.json         # 從 sb3/data/ 複製
    │   └── puzzle_techniques.json    # 一次性標注產物：{puzzle_id: max_tech}
    ├── solver/
    │   ├── candidate_engine.py       # 從 sb3 移植 + 改裝
    │   ├── techniques/
    │   │   ├── naked_single.py
    │   │   ├── hidden_single.py
    │   │   ├── basic_elimination.py
    │   │   ├── naked_pair.py
    │   │   ├── hidden_pair.py
    │   │   ├── pointing_pair.py
    │   │   └── box_line.py
    │   ├── human_solver.py           # 主入口
    │   └── label_puzzles.py          # 一次性標注 script
    ├── env/
    │   └── sudoku_gym_env.py         # 從 sb3 改裝（24-ch obs、新 reward）
    ├── model/
    │   └── features_extractor.py     # 從 sb3 直接複製
    ├── train/
    │   ├── train.py                  # MaskablePPO，移除所有 BC
    │   └── ppo.py                    # MaskablePPO subclass（移除 BC pass）
    ├── curriculum/
    │   ├── callback.py               # 技巧分層 + 嚴格升級 + 降級
    │   ├── eval_callback.py          # SudokuEvalCallback
    │   └── reserved_eval_callback.py # 從 sb3 直接複製
    ├── eval/
    │   ├── eval.py
    │   └── puzzle_set.py             # 從 sb3 直接複製
    └── tests/
        ├── test_techniques/
        │   ├── test_naked_single.py
        │   ├── test_hidden_single.py
        │   └── ...                   # 每技巧正例+負例
        ├── test_human_solver.py
        ├── test_reward.py
        ├── test_curriculum.py
        └── test_obs.py
```

## 6. Component Spec

### 6.1 Human-Style Solver（v1：技巧 1-7）

**目的**：給定 board state，回傳 `(suggested_action, max_technique_used)`。

```python
class HumanSolver:
    """按優先序套用技巧 1-7。失敗時回 (None, -1)，外部視為「v1 解不了」。"""

    TECHNIQUE_ORDER = [
        ('naked_single', 1),       # 最簡單，最先試
        ('hidden_single', 2),
        ('basic_elimination', 3),  # 候選集自動更新（其實是 candidate_engine 的常駐動作）
        ('naked_pair', 4),
        ('hidden_pair', 5),
        ('pointing_pair', 6),
        ('box_line', 7),
    ]

    def suggest(self, board, candidates):
        """
        Returns: (action_or_None, max_technique_id)
            action: ('fill', r, c, v) | ('eliminate', r, c, v) | None
            max_technique_id: 用了哪個技巧解出此 action
        """
        for name, tech_id in self.TECHNIQUE_ORDER:
            result = self._try(name, board, candidates)
            if result is not None:
                return result, tech_id
        return None, -1  # v1 解不了
```

**消去類技巧**（4-7）回 `('eliminate', r, c, v)`，由 candidate_engine 套用後再次跑 priority loop——可能觸發 naked single 等填格動作。最終一定回填格動作；若一輪 priority loop 都沒進展才 return None。

**LOC 估算**：
- candidate_engine: ~250
- naked_single: ~80
- hidden_single: ~150
- basic_elimination: 內建在 candidate_engine
- naked_pair: ~150
- hidden_pair: ~200
- pointing_pair: ~150
- box_line: ~100
- human_solver coordination: ~150
- **小計：~1,230 LOC + 測試 ~500**

### 6.2 Reward Redesign

**Reward function**（在 `RewardComputer.compute(r,c,v)` 內）：

```python
MAX_WRONG = 20

def compute(self, r, c, v):
    # 1. 求 solver 的建議（在 commit 之前的 state 上）
    solver_action, tech_id = self.solver.suggest(board, candidates)

    # 2. 判斷 agent 動作正確性（對 ORIGINAL solution，非 poisoned state）
    is_correct = (v == self.env.solution[r, c])

    if not is_correct:
        self.env.wrong_count += 1
        commit_fill(r, c, v)  # 仍寫入 board，candidates 同步更新
        terminated = (self.env.wrong_count >= MAX_WRONG)
        return -1.0, terminated

    # 3. 正確填，board complete 給 +20
    commit_fill(r, c, v)
    if board_complete():
        return 20.0, True

    # 4. 否則根據是否對應 solver 的建議給 bonus
    if solver_action is None:
        # solver 也解不了（v1：≥技巧 8 才解得出）→ 算亂猜對
        return 0.3, False
    elif solver_action == ('fill', r, c, v):
        # 完全對應 solver 建議
        return 1.0 + TECH_BONUS[tech_id], False
    else:
        # 正確但繞遠路（solver 認為該做 simpler 的事）
        return 0.3, False
```

```python
TECH_BONUS = {
    1: 0.0,   # naked single（最基本，無 bonus）
    2: 0.5,   # hidden single
    3: 0.0,   # basic elim（不直接填）
    4: 1.0,   # naked pair（消去後通常觸發更簡單填法，但鏈本身值錢）
    5: 1.0,
    6: 1.0,
    7: 1.0,
    # 8-15 在 v1 不存在
}
```

**Episode termination**：
- ✅ Board complete（success） → +20 reward + terminated=True
- ✅ Step 上限（300）→ truncated=True
- ❌ **移除** `max_wrong=5` 終止——改成 `max_wrong=20`，讓 agent 有更多機會嘗試和學習

理由：sb3/ 的 ep_len_mean ≈ 9 步，agent 平均才填 9 格 episode 就死，根本沒機會學「整題流程」。放寬 wrong limit 讓 episode 長一些。

**移除的 reward 元素**（從 sb3/）：
- ❌ `+3 naked single bonus`、`+2 hidden single bonus`（被 TECH_BONUS 取代）
- ❌ `+0.5 cascade per new naked single`（不再追蹤；rewardable signal 來自 solver match）
- ❌ `+5 unit complete`（純 shortcut，移除）

### 6.3 Observation Changes

**從 26 channel 砍到 24 channel**：

| Channel | 原用途 | v2 狀態 |
|---|---|---|
| 0-8 | board one-hot（每數字一面） | ✅ 保留 |
| 9-17 | per-digit candidate planes | ✅ 保留 |
| 18 | fixed cells（題目給定） | ✅ 保留 |
| 19 | empty cells | ✅ 保留 |
| 20-22 | row/col/box fill ratio | ✅ 保留 |
| 23 | candidate count / 9.0 | ✅ 保留 |
| **24** | **naked single flag** | **❌ 移除** |
| **25** | **hidden single flag** | **❌ 移除** |

**理由**：24/25 直接把答案位置告訴 model，不可能 generalize 到沒這兩個 channel 的情境（雖然 eval 時環境也提供，但這仍是 model 學「直接看 ch24=1 就填」的捷徑）。移除後 model 必須從 candidate planes (9-17) 自己推導 naked / hidden single。

### 6.4 No BC, Pure RL

**移除以下 sb3/ 程式**：
- `_bc_pass()` 整個 method
- `collect_rollouts()` 對 `info["teacher_action"]` / `info["teacher_quality"]` 的 monkey-patch
- `SudokuGymEnv.step()` 不再回 teacher_action / teacher_quality
- TeacherEngine 整個 class 移除（或保留為「solver 內部使用」但不回傳給 model）

**結果**：`SudokuMaskablePPO` 變成純 `MaskablePPO`，`train()` 只跑 `super().train()` 一次，沒有額外 BC pass。

### 6.5 Curriculum: Technique-Based Tiered

**Pre-training labelling**（一次性 script `solver/label_puzzles.py`）：

```python
def label_all_puzzles():
    db = PuzzlePoolDB('../data/puzzle_pool.db')
    solver = HumanSolver()
    labels = {}
    for puzzle in db.iter_all_puzzles():
        max_tech = run_solver_track_max_technique(solver, puzzle.board)
        labels[puzzle.id] = max_tech  # -1 if v1 solver fails
    json.dump(labels, open('reasoner/data/puzzle_techniques.json', 'w'))
```

執行一次（估約 1-2 小時跑完整個 DB），結果存 `reasoner/data/puzzle_techniques.json`。

**Stage 定義**：

| Stage | 條件 | 描述 |
|---|---|---|
| 1 | max_tech ∈ {1, 2, 3} | 純粹 naked / hidden single |
| 2 | max_tech ∈ {1..7} | 加入 pair / pointing / box-line |
| 3 | max_tech ∈ {1..10} | （v1 不可達——標 -1 的全部丟這） |
| 4 | max_tech ∈ {1..13} | （TBD） |
| 5 | max_tech ∈ {14, 15} | （TBD） |

v1 只做 Stage 1, 2, 3。Stage 3 是 v1 solver 解不了的混合桶，當「壓力測試」用。

**升級條件**（嚴格，無 backstop）：
- `reserved_eval` 在當前 stage 對應 puzzle 集合上 `success_rate ≥ 0.80`
- 連續 3 次 eval 都過 0.80（避免噪音誤判）
- 達標就升

**降級條件**（卡住保護）：
- 進入新 stage 後 50k 步內 `reserved_eval` 沒任何進步（≤ 上 stage 結束時的水準）
- 自動降回上一個 stage，續訓 50k 步後再嘗試升

### 6.6 Removed from sb3/

| sb3/ 元件 | 為何移除 |
|---|---|
| `teacher_engine.py` | 純 RL 不需要 |
| BC 相關（`sudoku_ppo._bc_pass`, monkey-patch） | 純 RL |
| `MilestoneCallback` | 太多 hard abort，新系統用「降級」處理 |
| `reward_computer.py` 的 cascade / unit-complete bonus | 已在 6.2 詳述 |
| `CurriculumCallback` 4-stage 難度分布 | 換成技巧分層 |
| Channel 24, 25 | shortcut |

## 7. Data Flow（end-to-end）

**Training step**：

```
1. CurriculumCallback 決定當前 stage（初始 1）
2. SudokuGymEnv.reset()：
   - 從 puzzle_techniques.json 找符合 stage 的 puzzle ids
   - DB.fetch by id
   - 預先解出 ground-truth solution（用 backtracking solver）
   - 跑 candidate_engine 初始化
   - 回傳 24-ch obs

3. for each step:
   a. agent.predict(obs, masks) → action (729 dim)
   b. env.step(action):
      - decode action → (r, c, v)
      - solver.suggest(board, candidates) → (solver_action, tech_id)
      - reward = reward_computer.compute(r, c, v, solver_action, tech_id)
      - update board, candidates_cache
      - obs' = build_obs(board, candidates) (24 ch)
      - return obs', reward, terminated, truncated, info{tech_id, ...}
   c. PPO collect into rollout buffer

4. After 4096 steps (8 envs × 512), PPO update:
   - super().train() 純 PPO 更新
   - 沒有 BC pass

5. Periodic：
   - eval_callback.py 每 50k 步 evaluate（reserved set）
   - curriculum 檢查升級條件
```

**Eval step**：與 training step 相同但：
- `env.reset()` 用 reserved set
- model 用 `deterministic=True`
- 不寫回 DB 任何 status

## 8. Success Criteria

**早期信號**（200k 步內必須出現）：
- `train/entropy_loss` 從 ~-4.5 緩慢升到 ~-3.5（policy 開始 commit）
- `rollout/ep_rew_mean` 從負爬到 0+
- `eval/reserved_L1` 出現任何非零數字

**進展信號**（500k 步內看到）：
- `eval/reserved_L1` 穩定 > 5%
- `curriculum/stage` 嘗試升級（若還在 Stage 1 也行，但要看 success rate 在爬）

**Mature 信號**（1M+ 步看到）：
- Stage 1 reserved 80%+ 達成，升 Stage 2
- Stage 2 開始有 progress（≥ 5%）

**失敗信號（早停討論）**：
- 500k 步 reserved_L1 仍 0 → framework 結構問題，重新檢視
- success_rate 短期上升後跌回 0 → reward overfit / spurious correlation

## 9. Engineering Plan & LOC

| 階段 | 工作 | LOC | 時間估 |
|---|---|---|---|
| Phase 0 | reasoner/ scaffold + 從 sb3/ 複製可重用檔 | ~50（多 import 改 path） | 0.5 day |
| Phase 1 | candidate_engine + 技巧 1-3（naked/hidden/elim） | ~480 | 2 days |
| Phase 2 | 技巧 4-7（pair/pointing/box-line） | ~600 | 3 days |
| Phase 3 | human_solver 整合 + label_puzzles.py + 一次性跑 DB | ~200 | 1 day |
| Phase 4 | 重寫 reward_computer + obs 改 + env step 改 | ~350 | 2 days |
| Phase 5 | curriculum 改寫 + eval callback 接通 | ~250 | 1 day |
| Phase 6 | 移除 BC 相關（sudoku_ppo subclass 變單純 PPO） | -150 LOC | 0.5 day |
| Phase 7 | 整合測試 + 跑第一次 1M-step training | - | 1-2 days |
| **合計** | | **~2,600** | **10-13 天** |

## 10. Open Questions / Risks

### 10.1 Solver 寫對是 critical path

如果 solver 偵測 hidden single / naked pair 有 bug，整個 reward signal 全錯，模型學到的東西也全錯。**緩解**：每技巧寫 ≥ 10 個 hand-crafted unit test（正例 + 負例）；solver 對整個 DB 跑一遍，回報「解到底有多少 % puzzle」當 sanity check。

### 10.2 Stage 3「未分類」puzzle 比例可能太高

如果 v1 solver 只能解 < 30% 的 DB，那 Stage 3 占 70%，在進 Stage 3 時 agent 真的要面對 8-15 號技巧的題——但無法 reward 對應，純靠 lucky correct (+0.3)。**緩解**：Phase 3 標注完看比例。如果 Stage 3 太大，往後加做技巧 8-10 縮小未分類池。

### 10.3 Pure RL cold-start

第一個 reward 出現時間：估 50k 步內（27 候選中亂選 1 個對的機率 ~3.7%，每 episode 平均 9 步，512×8=4096 steps/iter，所以 ~10 iter 內必有第一個對的 fill）。**緩解**：監看 `rollout/ep_rew_mean` 早期軌跡，5k 步沒看到任何正 reward 就停下來查 reward 計算 bug。

### 10.4 移除 ch 24/25 後 model 學不會 naked/hidden single

ch 9-17 已含完整 candidate info，model 理論上能從這推導 naked single（cell 上候選 plane 只有一個非零）和 hidden single（某 plane 在 row/col/box 內只有一個非零）。但要不要 model 真的能學會？**這是 framework 的根本賭注**，無法事先排除——只能靠跑訓練看。

### 10.5 Curriculum 卡 Stage 1

如果 1M 步 Stage 1 success_rate 還不到 80%，卡死。**緩解**：design 預留「降級」機制；如果進 Stage 1 三次都退出，admit failure，重審 framework。

## 11. Dependencies & Constraints

- **Python 版本**：與 sb3/ 一致（Python 3.12）
- **核心 dep**：stable-baselines3 ≥ 2.8、sb3-contrib（MaskablePPO）、PyTorch、numpy、gymnasium
- **GPU**：consumer-tier 即可（PPO_8 在這跑出來過；新系統參數量幾乎相同）
- **DB**：唯讀，新系統不寫回 puzzle_pool.db；training labels 存 `reasoner/data/puzzle_techniques.json`

## 12. Open Issues to Resolve in Implementation Plan

- HoDoKu 演算法移植細節（哪些 routine 對應哪個 .py）
- candidate_engine 的鎖機制（SubprocVecEnv 多 worker 並發）
- reserved_eval 是否要按 stage 分割（Stage 1 reserved subset / Stage 2 reserved subset）——需要 reserved set 也跑 label
- VecNormalize 是否保留（純 RL + 新 reward scale 變了，可能要重新校）
- 訓練步數預算（3M? 5M? 看 cold-start 後爬升速率決定）

---

## Appendix A — 為什麼這次會比 sb3/ 好？

| sb3/ 問題 | reasoner/ 解法 |
|---|---|
| Reward shortcut bonus 鼓勵局部 pattern | Reward 只在「對齊 solver 的技巧化推理」時給 bonus；亂猜對只 +0.3 |
| ch 24/25 直接洩答案 | 移除，model 必須自己從 candidate plane 推導 |
| Teacher 用全局 backtracking solution | 移除 BC，純靠 reward 探索 |
| Curriculum backstop 強升不管學沒學會 | 嚴格 success-only 升級；卡住自動降級 |
| Websudoku 難度標註與技巧無關 | 用 human-style solver 標每題「最高需要技巧 id」 |
| Eval 池子和 training 池子重疊 | reserved set 從未進 training（已在 sb3/ 達成，繼承） |
| 訓練分佈和 eval 分佈差異大（fetcher bias） | 純 random sample by stage，無 best_empty 排序 |

## Appendix B — 為什麼還是用 (cell, value) action 而非 macro-actions？

Brainstorming 過程考慮過 (B) 「ML agent 學技巧優先序 + assumption」、(C) 「technique macro action」。最終選 (D)「保持 (cell, value) 重設 reward」是因為：

1. (B) 和 (C) 把 ML 用在「技巧優先序」這個其實很簡單的問題上，ROI 低
2. (D) 不需要重訓 model 架構，能最大限度利用既有 stable-baselines3 / sb3-contrib 工具鏈
3. (D) 的限制（4-13 號技巧不能直接 reward）是接受的：accept 這部分技巧的學習必須隱式發生在 model 的 forward pass 裡

如果 (D) 跑通看到泛化進展，那這個 trade-off 是對的。如果 (D) 失敗，下一個 attempt 會考慮 (B)/(C)/(其他典範)。

---

**End of Design Spec**
