# 設計文件：Sudoku 專案最終收尾（簡報展演 + Repo 門面）

**日期：** 2026-04-27
**類型：** 文件 / 工具腳本（無訓練邏輯變動）
**狀態：** 設計完成，待 user review 後進入 writing-plans

---

## 1. 背景與目標

### 1.1 背景
Sudoku 專案經過三波 hardening（v10/v11/v12），程式品質已收斂。本次更動是「展示給同學看」前的**最後一次更動**，定位為展演收尾，不是功能擴充。

### 1.2 目標
- **A：簡報展演順利。** 提供低風險的 live demo 路徑，避免現場翻車。
- **B：Repo 門面整齊。** 讓同學會後到 GitHub 看 repo 時有體面的入口。

### 1.3 非目標（明確排除）
- ❌ 任何訓練邏輯變動（envs / models / curriculum / teacher 全部不動）
- ❌ 任何 crawler 行為變動
- ❌ 任何 bug fix（除非實作過程意外發現阻擋本次工作）
- ❌ 截圖、GIF、影片等視覺資產的製作
- ❌ `.gitignore` 整理 / config 模板化（user 已明確取消）
- ❌ Cross-platform demo 腳本（user 環境 = Windows）

---

## 2. Live Demo 策略

### 2.1 安全名單（現場跑）

| Demo | 指令 | 視覺重點 |
|---|---|---|
| **TensorBoard** | `tensorboard --logdir sb3/runs` | 訓練曲線 4 個 run 對照 |
| **eval_sb3.py** | `python eval_sb3.py --model models/sudoku_sb3_ckpt_400000_steps.zip --difficulty 1,2 --n-puzzles 3 --debug-n 3` | ASCII initial vs final board + wrong fills 統計 |

選擇理由：兩者皆**純本地讀檔、無網路依賴、deterministic、啟動 < 5 秒**。

### 2.2 預錄/截圖名單

**全砍。** 簡報靠口述帶過 crawler / legacy GUI 的存在（slide 第 199~213 行已提及）。

理由：GUI 截圖 / GIF 需要 user 親自操作螢幕擷取，而 user 選擇純 live + 口述。

### 2.3 已排除的 demo 候選

| 候選 | 排除原因 |
|---|---|
| Crawler GUI live | 網路 + proxy 池 + 目標站不確定性高 |
| Legacy PyQt6 GUI training | 啟動慢、`mrv_mix_prob=0` 純 RL 模式無法當天看到進步 |
| `train_sb3.py` 跑 30 秒 | log 滾很快但 curriculum 階段變化看不出來，視覺報酬低 |

---

## 3. Repo 工項

### 3.1 R1：root `README.md`

**目的：** 給 GitHub 訪客一個一頁的入口；不重複 CLAUDE.md / HISTORY.md 內容。

**結構（5 section + 3 連結）：**

1. **標題 + tagline** — 「用強化學習訓練 AI 解數獨；重點在工程旅程不在 AI」
2. **TL;DR** — 4 個 bullet：兩代訓練系統、自帶 crawler、19 個 bug 修復、設計決策連結
3. **專案結構** — ASCII 樹狀圖（`legacy/ sb3/ crawler/ data/ docs/`）
4. **快速試跑（Demo）** — 3 段指令：
   - `tensorboard --logdir sb3/runs`
   - `cd sb3 && python eval_sb3.py --model ... --difficulty 1,2 --n-puzzles 3 --debug-n 3`
   - `demo.bat`（一鍵）
5. **訓練重點技術** — 5 個 bullet：26-ch obs、729 action mask、27 constraint heads、TeacherEngine、4-stage curriculum
6. **Tech Stack** — 一行帶過
7. **簡報連結** — 連到 `docs/presentation/2026-04-27-sudoku-journey.md`

**明確排除：**
- ❌ shields.io badges（這不是 OSS 套件）
- ❌ License / Contributing section（個人作業）
- ❌ 大量截圖 / 架構圖（避免 R7 工作量回流）
- ❌ Bug 故事（HISTORY.md 已有，連過去就好）
- ❌ 設計決策說明（CLAUDE.md 已有）

### 3.2 R6：root `demo.bat`

**目的：** 一個指令同時開 TensorBoard + eval，當天現場按一下就好。

**行為流程：**
1. `start` 開新 cmd 視窗跑 `tensorboard --logdir sb3\runs --port 6006`
2. `timeout 5` 等 TensorBoard 起來
3. `start http://localhost:6006` 自動開瀏覽器
4. `cd sb3` 切目錄
5. `python eval_sb3.py ...` 在當前 cmd 跑，印 ASCII 結果
6. `pause` 結尾保留輸出在畫面

**設計取捨：**
- 只做 Windows `.bat`（user 環境）
- TensorBoard 視窗手動關閉（不嘗試管理 background process lifecycle）
- eval 跑在前景 cmd，方便觀眾直接看 ASCII board
- 不做錯誤處理（demo 失敗就現場切回手動指令）

### 3.3 R4：`docs/presentation/` 進 git

**操作：**
- `git add docs/presentation/`
- Commit: `docs: add classroom presentation source (Marp)`

簡報原始檔本來就該進 repo，目前是 untracked。

### 3.4 R5：清掉已刪除的 tfevents

**操作：**
- `git rm --cached "sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0"`
- Commit: `chore: untrack tfevents file (already in .gitignore)`

該檔案實體已不存在但 git index 仍追蹤，導致 `git status` 一直顯示 `D` 狀態。`.gitignore` 已有 `runs/` 規則，`--cached` 即可。

### 3.5 已排除的 Repo 工項

| 工項 | 排除原因 |
|---|---|
| R2：`.gitignore` 補 `*.db-shm` `*.db-wal` 等 | User 取消（接受 git status 殘留 4 個 untracked） |
| R3：config.example.json 模板化 | User 取消（無實際痛點） |
| R7：crawler GUI GIF / legacy 截圖 | User 選 C：全砍 |
| R8：把資產嵌進簡報 | R7 砍掉後失去依賴 |
| R9：requirements.txt 統合 | 未在最終 scope |

---

## 4. 執行順序

5 步，按順序執行；每步可獨立 commit：

1. **建立 `README.md`**（§3.1）
2. **建立 `demo.bat`**（§3.2）
3. **`git add docs/presentation/`** + commit（§3.3）
4. **`git rm --cached` tfevents** + commit（§3.4）
5. **`git add README.md demo.bat`** + commit (`docs: add README and demo.bat for classroom presentation`)

---

## 5. 驗收條件

- [ ] `git status` 比現在乾淨（消除：`docs/presentation/` 未追蹤、tfevents `D` 狀態）
- [ ] `README.md` 在 GitHub 網頁上預覽正常（連結都跳得到正確檔案）
- [ ] `demo.bat` 在 user 機器上雙擊可成功啟動 TensorBoard + 跑完 eval（end-to-end smoke test）
- [ ] 簡報原始檔（Marp）在 git 中可被追蹤
- [ ] **無任何 `.py` 檔案被改動**（除非實作過程發現必要，且回報 user 確認）

---

## 6. 風險與後備

| 風險 | 機率 | 後備 |
|---|---|---|
| `demo.bat` 在簡報用機環境失敗 | 低 | 直接退回手打兩條指令（README 已寫好） |
| TensorBoard 6006 port 衝突 | 極低 | 改 port 重跑 |
| `eval_sb3.py` 載 model 失敗 | 極低 | model 已存在於 disk，且 user 多次跑過；現場改 `--difficulty 1` 縮小範圍 |
| README 連結到的 HISTORY.md 段落漂移 | 極低 | 只連檔案不連 anchor |

---

## 7. 後續工作（**不在本次 scope**）

- 簡報實際演練（user 自行）
- 任何資產錄製（user 自行）
- 同學會後 feedback 整理（簡報結束後另外處理）
