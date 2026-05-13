# Apprentice — Reasoner + Adaptive Curriculum (Design)

**Date:** 2026-05-13
**Status:** Brainstormed, awaiting implementation plan
**Replaces:** Active development on `reasoner/` (which is being frozen)

---

## 1. Background

`reasoner/` 訓練至 **20.3M steps** 後仍卡在 0% solve rate，從 TensorBoard 多個 run 的事件檔合併分析確認：

| 指標 | step 50k | step 10M | step 20.3M | 結論 |
|---|---|---|---|---|
| `rollout/success_rate` | 0.000 | 0.000 | **0.000** | 整段訓練從未解出一道題 |
| `eval/success_rate_L1` ~ L4 | 0.000 | 0.000 | **0.000** | held-out eval 也是 0% |
| `rollout/ep_rew_mean` | 27.7 | 85.7 | 85.7 | step 10M 後完全平穩 |
| `rollout/ep_len_mean` | 40.7 | 53.6 | 53.7 | episode 長度卡住 |
| `train/explained_variance` | -0.12 | 0.78 | 0.86 | value head 學得很好 |
| `train/entropy_loss` | -4.25 | -2.89 | -2.65 | policy 趨穩、但 entropy 還相當高 |

### 1.1 Diagnostic

由 `ep_len=53、max_wrong=20、success=0%` 推導：

- agent 每 episode **正確 33 步 + 錯誤 20 步**，錯誤率 ~38%
- episode 終止於 `wrong_count >= 20`，不是解出也不是 `max_steps`
- agent **有在做半策略性決策**（正確 step 平均拿 ~3 reward），但**錯誤率過高 → 在解完之前就被 max_wrong 截斷**

### 1.2 根本原因

1. **稀疏終局獎勵 (+20) 從未觸發**：解 easy 題需要 ~40-50 個正確連續動作。Action space 1458 下，隨機 policy 連續對 50 步機率近似 0。+20 永遠不出現 → policy gradient 沒有「往解題」的拉力。
2. **Wrong penalty (-1) 太溫和**：38% 錯誤率還能拿正獎勵，agent 學會「猜很多次也沒關係」。
3. **沒有 BC、沒有 curriculum、沒有 obs shortcut**：純 PPO 從零探索 1458-action 空間 + 24-channel obs，學習負擔超出 PPO 能力。
4. **不是「進步慢」、是「卡在 local optimum」**：agent 找到「不解題、刷部分獎勵」的策略並陷得很深。

詳見 conversation 紀錄（`docs/superpowers/specs/` 同目錄下日期相鄰的 brainstorm 對話）。

---

## 2. Goals

**Primary**：在 1 週內讓 `apprentice/` 訓練的 policy 至少能達 stage 5（target_empty=25）75% 解題率以上、且 TB 看得到 success rate 持續上升趨勢。

**Concrete metrics**：

- Day 4 結束：本機 smoke test 跑通、`curriculum/target_empty` 從 3 至少升到 8
- Day 7 結束：
  - `curriculum/target_empty >= 18` 且該 target 下 success_rate ≥ 0.70
  - `eval/success_rate_L1` 不再是常數 0、看得到非零數值
  - 整體訓練 TB 健康（value_loss 收斂、entropy 不崩）

**最低及格線**：Day 7 仍卡在 target_empty < 8 → 設計仍有 blocker、回頭討論。

**Stretch**：`apprentice` policy 能解完整 easy 題（target_empty = 50, L1 reserved success ≥ 30%）。

---

## 3. Non-Goals

明確排除以下選項（brainstorm 期間都討論過）：

- ❌ AlphaZero / MCTS 重寫——時間上 1 週做不完，留下次 phase
- ❌ Behavior Cloning warm-start——`B2` 已捨棄，選擇純自學派 (B1)
- ❌ Self-Imitation Learning (SIL) ——可選 add-on、本 spec 不包含
- ❌ Action space 分解——`D2` 不在這版範圍
- ❌ 自動傳播 naked single (`A1`)——user 想保留 agent 自己學 naked single 的能力
- ❌ 拿掉 `norm_reward` (`B5`)——保留 VecNormalize 的穩定性，user 已決定
- ❌ Reward 量級重設 (`B4`)——本版不動 reward 數值
- ❌ Reward hack 防護 (`A4` mask unjust eliminate)——這版不做
- ❌ 修改 `reasoner/`——`reasoner/` 凍結作為對照基線
- ❌ PPO hyperparameter 大改（clip_range, gamma, n_steps, batch）——僅動 `ent_coef`

---

## 4. Architecture Overview

新建 `apprentice/` 子目錄、從 `reasoner/` 複製代碼後應用 7 項改動。`reasoner/` 不再修改、保留為 baseline。

### 4.1 三層 sibling 結構

```
sudoku_old/
├── data/puzzle_pool.db        ← 共享 DB（不動）
├── legacy/                    ← 封存（不動）
├── sb3/                       ← 封存（不動）
├── reasoner/                  ← 凍結！從現在起不再修改
└── apprentice/                ← 新建：reasoner + 7 項改動
```

`apprentice/` 完全獨立、有自己的 `models/`、`runs/`、入口（`python -m apprentice.train.train`）。`reasoner/` 的 20.3M checkpoint 保留在原處作為對照、不遷移。

### 4.2 七項改動總覽

| ID | 改動 | 影響範圍 |
|---|---|---|
| **A3** | obs +2 channel（naked-single flag + hidden-single flag），shape (24→26) | env, features extractor |
| **E1** | Cold-start（無 ckpt resume）；A3 obs shape 改變強制要求 | train entry |
| **B1** | Adaptive curriculum：`target_empty` 用 sweet-spot 公式自動調整 | env reset, new callback, new config |
| **A5** | `max_steps = max(60, target_empty × 8)` 動態公式 | env |
| **D1** | `net_arch={"pi": [128], "vf": [128, 128]}` | train entry |
| **E2** | `max_wrong = max(20, target_empty × 1.2)` 動態公式 | env |
| **C2** | `ent_coef = 0.05`（從 0.02 提高） | train entry |

---

## 5. Detailed Design — Per Change

### 5.1 A3：Observation Flag Channels

**目的**：給 agent 視覺先驗、把「最簡單兩種人類技巧」直接放在 obs 上、減少從零學習負擔。

**Channel 新增**：

- **ch 24 — naked_single_flag**：對每個空格 `(r,c)`、若 `len(candidates[r][c]) == 1` 則 `1.0`，否則 `0.0`
- **ch 25 — hidden_single_flag**：對每個空格 `(r,c)`、若存在數字 `v` 滿足「`v` 在 `(r,c)` 所在 row 或 col 或 box 中只有這一格能放」則 `1.0`，否則 `0.0`

**實作位置**：`apprentice/env/sudoku_gym_env.py` 的 `_get_observation()`。

**Hidden-single 計算 helper**：新增 `apprentice/env/obs_helpers.py`，包一個 `compute_hidden_single_grid(candidates) -> np.ndarray[9,9]` 函式、avoid 重新跑技巧 detector。注意計算成本：每 env step 需掃所有 27 個 unit（9 row + 9 col + 9 box）× 9 digits，~243 個 lookup；應該維持在 sub-ms 量級、Day 4 smoke test 量化確認。

**obs space 變動**：

```python
N_CHANNELS = 26   # was 24
observation_space = spaces.Box(low=0.0, high=1.0, shape=(26, 9, 9), dtype=np.float32)
```

**features_extractor 自動相容**：`SudokuFeaturesExtractor` 從 `observation_space.shape[0]` 讀 in_channels、無需修改。

**研究宗旨保留**：reasoner 哲學「reward 來自人類技巧的 justifier」不受影響、agent 還是要面對 1458 action space、reward 還是透過 `find_simplest_justifier` 計算。A3 只是「視覺先驗」、不是「答案外洩」。

### 5.2 B1：Adaptive Reverse Curriculum

**目的**：解開「agent 從未看過 +20 終局獎勵」的死結。把訓練起點壓低（少量空格）讓 agent 真的解出來、再依表現自動加難。

#### 5.2.1 Env-side：受控的「填回正解」

`SudokuGymEnv.reset()` 增加 `target_empty` 屬性、流程改為：

```
1. 從 DB 取題目 puzzle (原始有 N_empty_original 個空格、通常 45-55)
2. 用 backtracking solver 算正解 solution
3. 計算需要填回的格子數：fill_back = max(0, N_empty_original - target_empty)
4. 用 self.np_random（gymnasium 標準 PRNG、reset(seed=) 可重現）
   從目前空格中選 fill_back 個、填入 solution 對應值
5. _rebuild_candidates()
6. 結果：盤面上恰好剩 target_empty 個空格
```

**Edge case 處理**：

- 若 `target_empty >= N_empty_original`：不填回任何格子（題目本身就比 target 簡單）
- 若 `target_empty <= 0`：直接 raise（call site 應避免，min 是 3）
- 必須在 fill_back 後**重新算 candidates**、obs 才會正確顯示新盤面

**`target_empty` 設定機制**：由 `CurriculumController` 透過 `vec_env.env_method("set_target_empty", new_val)` 對所有 worker 同步更新（SubprocVecEnv-safe）。

#### 5.2.2 Adaptive controller（核心邏輯）

新檔：`apprentice/train/curriculum_controller.py`

**狀態**：

```python
class CurriculumController:
    target_empty: float          # 當前難度（連續變數、round 後傳給 env）
    success_window: deque        # 最近 N=200 episode 是否解出（1/0）
    last_advance_step: int       # 上次調整 target 的 step
    last_advance_direction: int  # +1 / -1 / 0
    stagnation_since: int        # 上次「離開停滯」的 step
```

**Hyperparameters**（放 `apprentice/configs/curriculum.json`）：

```json
{
  "initial_target_empty": 3,
  "min_target_empty": 3,
  "max_target_empty": 55,
  "target_rate": 0.70,
  "tolerance_band": [0.55, 0.85],
  "step_size": 10.0,
  "window_size": 200,
  "min_episodes_before_update": 100,
  "min_steps_between_updates": 50000,
  "stagnation_threshold_steps": 500000,
  "stagnation_probe_step": 1,
  "stagnation_rollback_threshold": 0.40,
  "stagnation_rollback_window_steps": 200000
}
```

**Update rule（每 N=50000 step 觸發 1 次）**：

```python
def update(self, current_step):
    if len(success_window) < min_episodes_before_update:
        return  # 還沒蒐集到足夠數據
    
    if current_step - last_advance_step < min_steps_between_updates:
        return  # 上次調整後還沒給夠訓練時間
    
    sr = mean(success_window)
    
    if sr > tolerance_band[1]:                     # > 0.85 太簡單
        adj = (sr - tolerance_band[1]) * step_size
        target_empty = min(max_target_empty, target_empty + adj)
        last_advance_direction = +1
        last_advance_step = current_step
    
    elif sr < tolerance_band[0]:                   # < 0.55 太難
        adj = (tolerance_band[0] - sr) * step_size
        target_empty = max(min_target_empty, target_empty - adj)
        last_advance_direction = -1
        last_advance_step = current_step
    
    # else: in band, no change
    
    self._check_stagnation(current_step)
```

#### 5.2.3 振盪防護（風險 1）

兩層防護：

1. **Sliding window 平滑**：`success_window` 用 200 episode、不是 1 episode 一次。瞬時雜訊被吸收。
2. **Update interval**：每 50k step 才更新 1 次（不是每 batch 都更新）、避免高頻震盪。
3. **保守 step_size**：值 10、實務上每次調整 < 2 格、不會跳太大。

#### 5.2.4 Stagnation detector（風險 2）

兩種停滯情況：

**情況 A：sr 落在 sweet spot、target_empty 永不動**

```python
def _check_stagnation(self, current_step):
    if last_advance_step == 0:
        stagnation_since = current_step
        return
    
    if current_step - last_advance_step > stagnation_threshold_steps:  # 500k step
        # 強制 probe +1
        target_empty += stagnation_probe_step  # +1
        last_advance_step = current_step
        last_advance_direction = +1
        self._probe_target = target_empty       # 紀錄這次是 probe
        self._probe_started_at = current_step
```

**情況 B：probe 後勝率暴跌 → 自動退回**

```python
def _check_probe(self, current_step, sr):
    if self._probe_target is None:
        return
    
    if current_step - self._probe_started_at < stagnation_rollback_window_steps:  # 200k
        return  # 還沒給 probe 足夠時間
    
    if sr < stagnation_rollback_threshold:  # < 0.40
        # probe 失敗、退回去（同樣 clamp 到 min_target_empty）
        target_empty = max(min_target_empty, self._probe_target - 1)
        self._probe_target = None
    elif sr >= tolerance_band[0]:
        # probe 成功
        self._probe_target = None
```

#### 5.2.5 Resume 兼容性

`CurriculumController` 狀態存到 `<ckpt_path>_curriculum.json` sidecar（跟 `_vecnorm.pkl` 同機制）：

```json
{
  "target_empty": 12.4,
  "last_advance_step": 850000,
  "last_advance_direction": 1,
  "stagnation_since": 0,
  "probe_target": null,
  "probe_started_at": 0,
  "success_window": [1, 0, 1, 1, 0, ...]
}
```

Resume 流程：

1. 找最新 ckpt：`apprentice_ckpt_<N>_steps.zip`
2. 載入 model.zip + vecnorm.pkl + curriculum.json
3. 把 controller state 還原、用 `set_target_empty()` 重新校準 env

### 5.3 A5：Dynamic `max_steps`

**公式**：

```python
max_steps = max(60, int(target_empty * 8))
```

**理由**：沒有 A1 的情況下、agent 要自己手動填每個 naked single 鏈、episode 自然較長。係數 8 = 每空格 agent 平均要做 ~6-8 個動作（含試錯）。下限 60 防止 target_empty=3 時 max_steps 過小、agent 完全沒空間。

**實作**：env reset 時根據 `self.target_empty` 算出當前 episode 的 `max_steps`、覆寫 `self.max_steps`。

對應表（reference）：

| target_empty | max_steps |
|---|---|
| 3 | 60 |
| 5 | 60 |
| 8 | 64 |
| 12 | 96 |
| 18 | 144 |
| 25 | 200 |
| 35 | 280 |
| 50 | 400 |
| 55 | 440 |

### 5.4 D1：Policy Network Hidden Layer

**改動**：[apprentice/train/train.py](apprentice/train/train.py) 內 `policy_kwargs`：

```python
policy_kwargs = dict(
    features_extractor_class=SudokuFeaturesExtractor,
    features_extractor_kwargs={"features_dim": 192},
    net_arch={"pi": [128], "vf": [128, 128]},   # was {"pi": [], "vf": [128]}
)
```

**影響**：

- Policy head：features (1650) → Linear(1650, 128) → ReLU → Linear(128, 1458) logits
- Value head：features → Linear(1650, 128) → ReLU → Linear(128, 128) → ReLU → Linear(128, 1)

**多出參數量**：~370K（policy 多 ~210K、value 多 ~16K + 偏置）、不到模型總大小 10%。

### 5.5 E2：Dynamic `max_wrong`

**公式**：

```python
max_wrong = max(20, int(target_empty * 1.2))
```

**理由**：early stage（target=3-5）給 agent 寬容、容錯 5-6 次；中後期 stage（target=25-50）容錯比例隨難度上升、但下限 20 防止過嚴。

對應表：

| target_empty | max_wrong |
|---|---|
| 3 | 20 |
| 5 | 20 |
| 8 | 20 |
| 12 | 20 |
| 18 | 22 |
| 25 | 30 |
| 35 | 42 |
| 50 | 60 |

**實作**：同 A5、env reset 時根據 `self.target_empty` 算出當前 `max_wrong_fills`。

### 5.6 C2：Entropy Coefficient

**改動**：[apprentice/train/train.py](apprentice/train/train.py) `SudokuMaskablePPO(...)`：

```python
ent_coef=0.05,   # was 0.02
```

**理由**：稀疏終局獎勵 + curriculum 跳階段都需要 policy 保持探索熱度。0.02 太冷、policy 過早收斂到 local optimum；0.05 是中等熱度、Graves 2017 等 paper 常見值。

**不上 schedule**：保持固定常數。如果訓練後期看到 entropy 還是太高（policy 不收斂）、可以加 LinearSchedule 0.05 → 0.02、但本 spec 不預先做。

### 5.7 E1：Cold-Start

**為什麼必要**：A3 把 obs shape 從 (24,9,9) 改為 (26,9,9) → features_extractor 第一層 `cell_embed` 的 `Linear(in_channels=24, 128)` 不能 load 進 `Linear(in_channels=26, 128)` 的新模型。

**實作**：

1. `apprentice/` 從一個全新的目錄開始、沒有任何 ckpt
2. `train.py` `--load-model` 預設 `None`（不是 `auto`）
3. 加 ckpt-shape assertion：載入時若 obs shape 不符立刻 fail-fast、顯示明確錯誤訊息

```python
if load_path is not None:
    try:
        loaded_obs_shape = ...  # 從 ckpt 推導
    except Exception:
        sys.exit(f"[apprentice] FATAL: cannot inspect obs shape in ckpt {load_path}")
    
    if loaded_obs_shape != env.observation_space.shape:
        sys.exit(
            f"[apprentice] FATAL: ckpt obs shape {loaded_obs_shape} != env "
            f"{env.observation_space.shape}. obs shape changed between training "
            "runs; must cold-start (omit --load-model)."
        )
```

**`reasoner/` ckpt 處理**：保留原處、視為對照組。不複製到 `apprentice/models/`、也不嘗試 load。

---

## 6. New / Modified Files

### 6.1 從 `reasoner/` 複製不變的檔案（直接 cp）

```
reasoner/__init__.py                        → apprentice/__init__.py
reasoner/data_pkg/                          → apprentice/data_pkg/     (整個目錄)
reasoner/solver/                            → apprentice/solver/        (整個目錄)
reasoner/solver_ext/                        → apprentice/solver_ext/    (整個目錄)
reasoner/data/eval_puzzles.json             → apprentice/data/eval_puzzles.json
reasoner/model/features_extractor.py        → apprentice/model/features_extractor.py  (in_channels 自動 adapt)
reasoner/env/reward_computer.py             → apprentice/env/reward_computer.py        (不動)
reasoner/eval/eval_callback.py              → apprentice/eval/eval_callback.py
reasoner/eval/reserved_eval_callback.py     → apprentice/eval/reserved_eval_callback.py
reasoner/train/ppo.py                       → apprentice/train/ppo.py
reasoner/tests/                             → apprentice/tests/         (測試需要重 import path)
```

### 6.2 從 `reasoner/` 複製後修改的檔案

```
reasoner/env/sudoku_gym_env.py              → apprentice/env/sudoku_gym_env.py
    - N_CHANNELS = 24 → 26
    - _get_observation(): 新增 ch 24, 25
    - __init__: 加 target_empty 屬性
    - reset(): 加 fill_back 邏輯
    - reset(): 動態算 self.max_steps, self.max_wrong_fills
    - set_target_empty(): 新方法、給 controller 呼叫
    - 新增 compute_hidden_single_grid() helper（或拆到 obs_helpers.py）

reasoner/train/train.py                     → apprentice/train/train.py
    - 所有路徑 reasoner/* → apprentice/*
    - MODEL_NAME → "apprentice_latest"
    - TB_LOG_NAME → "apprentice"
    - _CKPT_PATTERN → r"apprentice_ckpt_(\d+)_steps\.zip$"
    - policy_kwargs.net_arch → {"pi": [128], "vf": [128, 128]}
    - ent_coef → 0.05
    - 拿掉 --load-model auto 的預設行為（cold-start required）
    - 加 obs-shape 一致性檢查
    - 新增 CurriculumCallback 到 callbacks list
```

### 6.3 新增檔案

```
apprentice/configs/curriculum.json          ← Adaptive 三個 hyperparam + bounds
apprentice/env/obs_helpers.py               ← compute_hidden_single_grid() 等
apprentice/train/curriculum_controller.py   ← CurriculumController class
apprentice/train/curriculum_callback.py     ← SB3 callback 介接 controller
apprentice/README.md                        ← 簡述 apprentice 跟 reasoner 差別
```

### 6.4 不複製的目錄

```
reasoner/models/    ← 不複製、apprentice 從零訓練
reasoner/runs/      ← 不複製、apprentice 自己的 TB log
reasoner/__pycache__/
```

---

## 7. Config Schema

**`apprentice/configs/curriculum.json`** 完整 schema：

```json
{
  "initial_target_empty": 3,
  "min_target_empty": 3,
  "max_target_empty": 55,

  "target_rate": 0.70,
  "tolerance_band": [0.55, 0.85],
  "step_size": 10.0,

  "window_size": 200,
  "min_episodes_before_update": 100,
  "min_steps_between_updates": 50000,

  "stagnation_threshold_steps": 500000,
  "stagnation_probe_step": 1,
  "stagnation_rollback_threshold": 0.40,
  "stagnation_rollback_window_steps": 200000
}
```

**Hot-reload？**：本版**不支援訓練中 hot-reload**。要改 hyperparam 需 ctrl+C → 改 config → resume。原因：避免 controller 內部狀態（success_window, last_advance_step）跟 config 不一致。

---

## 8. TensorBoard Metrics（新增）

| Tag | 來源 | 意義 |
|---|---|---|
| `curriculum/target_empty` | controller | 當前 target_empty（連續值） |
| `curriculum/target_empty_rounded` | controller | round 後傳給 env 的整數值 |
| `curriculum/success_rate_window` | controller | 過去 200 ep 滾動勝率 |
| `curriculum/in_sweet_spot` | controller | 1 if sr ∈ [0.55, 0.85] else 0 |
| `curriculum/adjustment_per_update` | controller | 每次 update 改了多少（含 0 不動）|
| `curriculum/steps_since_last_advance` | controller | 距上次 target 變動的步數 |
| `curriculum/is_probing` | controller | 1 if 目前處於 stagnation probe 中 |
| `env/max_steps` | env attribute aggregation | 當前 episode 的 max_steps |
| `env/max_wrong` | env attribute aggregation | 當前 episode 的 max_wrong |

既有 `rollout/`、`train/`、`eval/`、`eval/reserved_*` metrics 保留不動。

---

## 9. Training Schedule (Day 1-7)

| 階段 | 內容 | 預估時間 |
|---|---|---|
| **Day 1** | 建立 `apprentice/` 目錄、複製不變檔案、改 import path、確認 `python -m apprentice.train.train` 能 launch（即使 controller 還沒寫）| 4-8 hr |
| **Day 2** | 實作 A3（obs flag）、E1（cold-start assertion）、D1（net_arch）、C2（ent_coef）。本機跑 ~10k step smoke test、確認 model 不會 crash | 6-8 hr |
| **Day 3** | 實作 B1 + A5 + E2（curriculum_controller, curriculum_callback, env target_empty 邏輯）。本機跑 50k step、確認 target_empty 真的會動 | 8-10 hr |
| **Day 4** | 本機 smoke test 整體 200k step、確認 controller 行為合理、TB metrics 正常、`target_empty` 從 3 至少升到 8 | 4-6 hr 跑 + watch |
| **Day 5** | Colab 部署（單獨章節，見 §11）、上 Colab T4 開始長訓 | 4-6 hr |
| **Day 6** | 訓練中、看 TB 並判斷需不需要調 config（修 step_size, target_rate 等）、必要時重啟 | watch |
| **Day 7** | 收斂評估、Day 7 結束的 ckpt 跑 reserved eval、收集 acceptance criteria 數據 | 2-4 hr |

---

## 10. Acceptance Criteria

### 10.1 程式碼層次（Day 4 結束前）

- [ ] `apprentice/` 目錄完整建立、所有 import path 一致
- [ ] `python -m apprentice.train.train` 從零跑 200k step 不 crash
- [ ] TB 上看得到所有新增 metric（§8 列表）
- [ ] `curriculum/target_empty` 至少升一次（從 3 → 4 以上）
- [ ] `reasoner/` 目錄完全不變（diff 對照確認）

### 10.2 訓練收斂層次（Day 7 結束）

**Pass 條件**（都要達成）：

- [ ] `curriculum/target_empty >= 18` 至少維持 200k step
- [ ] 在 target_empty=18 時、`curriculum/success_rate_window >= 0.55` 維持 100k step
- [ ] `eval/success_rate_L1` 至少**一次**達到非零（任何 > 0 都算 pass）
- [ ] `train/value_loss` 收斂（不發散）、`train/entropy_loss` 不崩到 0

**Stretch**（額外加分）：

- [ ] `curriculum/target_empty >= 35` 維持 100k step
- [ ] `eval/success_rate_L1 >= 0.10`
- [ ] `eval/reserved_L1 >= 0.05`

**Fail 條件**（任一達成代表 spec 有結構性問題）：

- [ ] `curriculum/target_empty` 整訓練都 ≤ 5
- [ ] target_empty 振盪幅度 ±5 以上不收斂
- [ ] 訓練全程 `eval/success_rate_L1 = 0`

---

## 11. Colab Deployment (Placeholder)

**Status**：本 spec 不涵蓋 Colab 細節。Day 5 開始時另開設計或在本 spec 加章節。

**待設計的事**：

- notebook 結構（cells: env setup, drive mount, code sync, training launch, TB tunnel）
- Code 同步機制：git clone vs zip 上傳 vs 直接 Drive 上 import
- Checkpoint sync 策略：每 50k step 寫 Drive
- VecNormalize sidecar、curriculum.json sidecar 都要寫 Drive
- Keep-alive：JS snippet vs 沒有（容忍 12h 自然斷線）
- Resume cell：自動偵測 Drive 上最新 ckpt、resume 訓練
- TB hosted：`%load_ext tensorboard` + `%tensorboard --logdir runs/`

**Day 5 之前先用本機訓練**。

---

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| target_empty 振盪不收斂 | 中 | 高 | step_size=10 保守、window_size=200 平滑；若仍振盪、可改 step_size=5 |
| 卡在低 target_empty (e.g., 5) 永不升 | 低-中 | 高 | Stagnation detector @ 500k step、強制 probe +1 |
| stagnation probe 失敗無限循環 | 低 | 中 | rollback_threshold=0.40 寬鬆、不會頻繁觸發；單向計數防止 probe-rollback-probe 無限 |
| Cold-start 後 entropy 暴衝、value head 也跟著爛 | 中 | 中 | C2 ent_coef=0.05 中等熱度、不會極端；vf_coef=0.5 保持 |
| 本機 smoke test 跑通但 Colab 上 vec_env 異常 | 低 | 中 | Day 5 安排專門時間 debug Colab 環境差異 |
| TB log 沒同步到 Drive、訓練結束後丟失 | 中 | 中 | Colab 部署 spec 要強制把 runs/ 寫 Drive |
| A3 obs flag 計算太慢、env step 速度大降 | 低-中 | 中 | hidden_single 用 `compute_hidden_single_grid` 一次性算、cache；smoke test 量化 step/sec |

---

## 13. Open Questions（spec 寫完前留待 plan 階段細化）

1. **`obs_helpers.py` vs inline**：hidden-single 計算放單獨檔案 vs 直接 inline 在 env 裡。傾向獨立檔案、testability 較好。
2. **`stagnation_probe_step` 是否該大於 1**：probe +1 vs probe +2。本 spec 取 +1（最保守），plan 可以討論。
3. **Eval callback 是否要 curriculum-aware**：目前 `SudokuEvalCallback` 用固定 difficulties (1,2,3,4)、跟 curriculum 無關。是否需要新增 `eval_at_current_target_empty` metric？plan 階段決定。
4. **Reasoner ckpt 是否該載入到 apprentice 做 partial weight transfer**：除了 `cell_embed` 第一層、其他 layer 都 compatible、理論上可以 cherry-pick。但 spec 採取乾淨 cold-start（簡單、避免污染）。

---

## 14. References

- Conversation log（brainstorm phase）：相同目錄 2026-05-13 日期、`/superpowers:brainstorming` invocation
- Graves et al. 2017, "Automated Curriculum Learning for Neural Networks"
- Matiisen et al. 2017, "Teacher-Student Curriculum Learning"
- Vygotsky 1978, "Mind in Society"（Zone of Proximal Development 起源）
- 既有 reasoner 設計：`docs/superpowers/specs/2026-04-28-reasoner-pure-rl-redesign-design.md`
- TB diagnostic（20.3M step）：`reasoner/runs/reasoner_1/` 多個 event file
