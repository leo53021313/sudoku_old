# Final Presentation Polish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 demo 給同學看之前，建立 root `README.md` + `demo.bat`，並做兩個小型 git index 清理；完全不動訓練／crawler 邏輯。

**Architecture:** 5 個獨立 task，每個產生 1 個 commit。Task 1~2 建立檔案（不 commit），Task 3~4 處理已存在的 git 狀態，Task 5 把 Task 1~2 的成果一起 commit（因為 `README.md` 引用 `demo.bat`，邏輯上應為同一個 commit）。

**Tech Stack:** Markdown / Windows batch (`.bat`) / git CLI

**Spec:** [docs/superpowers/specs/2026-04-27-final-presentation-polish-design.md](../specs/2026-04-27-final-presentation-polish-design.md)

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `README.md` | Create (root) | GitHub 訪客一頁式入口 |
| `demo.bat` | Create (root) | Windows 一鍵 demo 啟動腳本 |
| `docs/presentation/2026-04-27-sudoku-journey.md` | Track（檔案已存在但 untracked） | 課堂簡報原始檔 |
| `sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0` | Untrack（檔案已不存在但仍在 git index） | 清掉 stale tfevents 紀錄 |

**沒有 `.py` / 訓練邏輯 / crawler 邏輯改動。**

---

## Task 1: 建立 root `README.md`

**Files:**
- Create: `README.md` (repo root)

**Note:** 本 task 只建立檔案，不 commit；commit 集中在 Task 5（`README.md` 與 `demo.bat` 邏輯耦合，同 commit）。

- [ ] **Step 1: 在 repo root 建立 `README.md`**

完整內容：

````markdown
# Sudoku RL — 一個學期的 RL 工程實踐

> 用強化學習（MaskablePPO）訓練 AI 解數獨。
> 重點不在 AI 演算法本身，而在「把 RL 從研究 notebook 推到生產品質」的工程旅程。

## TL;DR

- **兩代訓練系統**：`legacy/`（自寫 PyTorch PPO + PyQt6 GUI）→ `sb3/`（Stable-Baselines3 MaskablePPO，主力）
- **自帶資料管線**：`crawler/` HTTP 爬蟲 + Proxy 池 + PyQt6 GUI 抓題目
- **19 個生產化 Bug 修復**：完整紀錄見 [HISTORY.md](HISTORY.md)
- **設計決策**：每個「為什麼這樣寫」的答案在 [CLAUDE.md](CLAUDE.md)

## 專案結構

```
sudoku_old/
├── crawler/      # HTTP 爬蟲 + Proxy 池 + PyQt6 監控 GUI
├── data/         # 共用 puzzle_pool.db（兩代訓練系統共享）
├── docs/         # 簡報原始檔 + 設計規格
├── legacy/       # v1：自寫 PyTorch PPO + PyQt6 訓練 GUI（封存）
├── models/       # legacy 訓練產出
└── sb3/          # v2：MaskablePPO（主力，活躍開發）
```

## 快速試跑（Demo）

### 1. 看訓練曲線

```bash
tensorboard --logdir sb3/runs
```

### 2. 用訓練好的 Model 解題

```bash
cd sb3
python eval_sb3.py --model models/sudoku_sb3_ckpt_400000_steps.zip \
                   --difficulty 1,2 --n-puzzles 3 --debug-n 3
```

### 3. 一鍵啟動兩者（Windows）

```bash
demo.bat
```

## 訓練重點技術

- **26-channel observation**：9 ch one-hot board + 9 ch per-digit candidates + 8 ch aux features
- **729-action space + Action Mask**：禁止 agent 在違規動作上浪費學習
- **27 個 Constraint Heads**：9 列 + 9 行 + 9 宮，把規則織進網路結構
- **TeacherEngine + BC Loss**：4-level quality pyramid 提供先驗指導
- **4-stage Curriculum**：L1 → L1+L2 → L1+L2+L3 → 全難度，依成功率自動推進

## Tech Stack

Python 3.11 · PyTorch · Stable-Baselines3 · sb3-contrib · PyQt6 · SQLite (WAL) · requests + SOCKS proxy pool

## 課堂簡報

[2026-04-27 課堂簡報原始檔（Marp）](docs/presentation/2026-04-27-sudoku-journey.md)
````

- [ ] **Step 2: 驗證檔案存在且結構正確**

Run:
```bash
ls -la README.md && head -3 README.md
```

Expected:
```
-rw-r--r-- ... README.md
# Sudoku RL — 一個學期的 RL 工程實踐

> 用強化學習（MaskablePPO）訓練 AI 解數獨。
```

- [ ] **Step 3: 驗證連結指向真實檔案**

Run（一條一條驗證 README 內提到的相對路徑都存在）:
```bash
ls HISTORY.md CLAUDE.md sb3/eval_sb3.py sb3/models/sudoku_sb3_ckpt_400000_steps.zip docs/presentation/2026-04-27-sudoku-journey.md
```

Expected: 所有 5 個檔案都列出來，無 "No such file"。

如果有任何一個不存在 → STOP，回報給 user 確認後再繼續（README 不能連到不存在的檔案）。

---

## Task 2: 建立 root `demo.bat`

**Files:**
- Create: `demo.bat` (repo root)

**Note:** 本 task 只建立檔案 + smoke test，不 commit。

- [ ] **Step 1: 在 repo root 建立 `demo.bat`**

完整內容：

```batch
@echo off
REM 一鍵啟動 Sudoku Demo：TensorBoard + eval_sb3.py
REM 用法：直接雙擊或在 cmd 執行 demo.bat

echo [Demo] 啟動 TensorBoard（背景視窗）...
start "TensorBoard" cmd /k "tensorboard --logdir sb3\runs --port 6006"

echo [Demo] 等 TensorBoard 啟動 5 秒...
timeout /t 5 /nobreak > nul

echo [Demo] 開瀏覽器到 TensorBoard...
start http://localhost:6006

echo [Demo] 跑 eval_sb3 解 L1 + L2 各 3 題...
cd sb3
python eval_sb3.py --model models\sudoku_sb3_ckpt_400000_steps.zip ^
    --difficulty 1,2 --n-puzzles 3 --debug-n 3

echo.
echo [Demo] eval 結束。TensorBoard 視窗請手動關閉。
pause
```

注意：
- `start "TensorBoard" cmd /k "..."` 把 TensorBoard 開在獨立 cmd 視窗，不阻擋當前流程。
- `^` 是 Windows batch 的 line continuation（相當於 bash `\`）。
- `cd sb3` 後的指令使用反斜線 `\`（Windows 路徑）。
- `pause` 讓 cmd 視窗保留輸出，避免結果一閃而過。

- [ ] **Step 2: 驗證檔案存在**

Run:
```bash
ls -la demo.bat && head -3 demo.bat
```

Expected:
```
-rw-r--r-- ... demo.bat
@echo off
REM 一鍵啟動 Sudoku Demo：TensorBoard + eval_sb3.py
```

- [ ] **Step 3: Smoke test（**需 user 親自執行**）**

⚠️ 此 step 由 user 在自己的 Windows cmd 雙擊或執行 `demo.bat`。

驗收條件：
1. 跳出新 cmd 視窗執行 TensorBoard，視窗標題寫 "TensorBoard"
2. 約 5 秒後瀏覽器自動開啟 `http://localhost:6006`，看到 TensorBoard UI 並列出 4 個 run（MaskablePPO_1~4）
3. 主 cmd 視窗印出 ASCII initial vs final board，最後顯示 wrong fills 統計
4. 主 cmd 顯示 `Press any key to continue . . .` 並等待

如有任一條件失敗 → STOP，回報失敗症狀，不要進入 Task 3。

---

## Task 3: 把 `docs/presentation/` 加入 git tracking

**Files:**
- Track: `docs/presentation/2026-04-27-sudoku-journey.md`

**Why:** 簡報原始檔目前是 untracked。此 task 把它加進 git。

- [ ] **Step 1: 確認檔案目前是 untracked 狀態**

Run:
```bash
git status docs/presentation/
```

Expected:
```
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        docs/presentation/
```

如果已被追蹤（顯示 modified 或無輸出），跳過此 Task 進入 Task 4。

- [ ] **Step 2: 加入 git index**

Run:
```bash
git add docs/presentation/
```

Expected: 無輸出。

- [ ] **Step 3: Commit**

Run:
```bash
git commit -m "$(cat <<'EOF'
docs: add classroom presentation source (Marp)

Adds the Marp slide source used for the 2026-04-27 classroom demo.
Lives in docs/presentation/ alongside other docs.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected:
```
[main <hash>] docs: add classroom presentation source (Marp)
 1 file changed, ... insertions(+)
 create mode 100644 docs/presentation/2026-04-27-sudoku-journey.md
```

- [ ] **Step 4: 驗證**

Run:
```bash
git log -1 --stat && git status docs/presentation/
```

Expected:
- `git log -1 --stat` 顯示剛剛的 commit 包含 `docs/presentation/2026-04-27-sudoku-journey.md`
- `git status docs/presentation/` 無輸出（代表已乾淨）

---

## Task 4: 從 git index 移除 stale tfevents

**Files:**
- Untrack: `sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0`

**Why:** 該檔案實體已不存在於 disk，但 git index 仍然追蹤，導致 `git status` 一直顯示 `D` 狀態。`.gitignore` 已涵蓋 `runs/`，故只需 `--cached` 從 index 移除即可，不會試圖刪除 disk 上的檔案。

- [ ] **Step 1: 確認當前狀態**

Run:
```bash
git status sb3/runs/
```

Expected: 應顯示
```
        deleted:    sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0
```

如果沒看到這個 `deleted:` 行，跳過此 Task 進入 Task 5。

- [ ] **Step 2: 從 index 移除**

Run:
```bash
git rm --cached "sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0"
```

Expected:
```
rm 'sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0'
```

⚠️ 注意：必須加 `--cached`。少了它 git 會試圖刪 disk 檔（雖然這裡 disk 檔已不存在所以也沒差，但養成習慣）。

- [ ] **Step 3: Commit**

Run:
```bash
git commit -m "$(cat <<'EOF'
chore: untrack stale tfevents file

The file no longer exists on disk but remained in git index,
keeping git status dirty. .gitignore already covers runs/, so
removing it from the index alone is sufficient.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected:
```
[main <hash>] chore: untrack stale tfevents file
 1 file changed, 0 insertions(+), 0 deletions(-)
 delete mode 100644 sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0
```

- [ ] **Step 4: 驗證 git status 不再顯示該檔**

Run:
```bash
git status sb3/runs/
```

Expected: 無輸出，或只顯示其他不相關的檔案，不應再看到那條 `deleted:` 行。

---

## Task 5: Commit `README.md` + `demo.bat`

**Files:**
- Commit: `README.md`、`demo.bat`（兩者皆 Task 1、Task 2 已建立但未 commit）

**Why:** README 內文引用 `demo.bat`（"一鍵啟動兩者"區塊），兩者邏輯耦合，同 commit 較合理。

- [ ] **Step 1: 確認兩個檔案都存在且尚未 commit**

Run:
```bash
git status README.md demo.bat
```

Expected:
```
Untracked files:
        README.md
        demo.bat
```

如果只看到一個 → 回頭檢查 Task 1 / Task 2 是否完成。

- [ ] **Step 2: 加入 git index**

Run:
```bash
git add README.md demo.bat
```

Expected: 無輸出。

- [ ] **Step 3: Commit**

Run:
```bash
git commit -m "$(cat <<'EOF'
docs: add README and demo.bat for classroom presentation

- README.md: GitHub-facing single-page entry; links to HISTORY.md
  / CLAUDE.md / docs/presentation/ for full context.
- demo.bat: one-click launcher for the classroom live demo
  (TensorBoard on sb3/runs + eval_sb3.py on the 400k checkpoint).

No training, crawler, or model logic changed.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected:
```
[main <hash>] docs: add README and demo.bat for classroom presentation
 2 files changed, ... insertions(+)
 create mode 100644 README.md
 create mode 100644 demo.bat
```

- [ ] **Step 4: 驗證**

Run:
```bash
git log --oneline -5 && echo "---" && git status
```

Expected:
- `git log --oneline -5` 顯示最新 3 個 commit 為本次 plan 產出（Task 5 → Task 4 → Task 3）。
- `git status` 應乾淨許多；殘餘的 untracked 應只有 user 已明確選擇不處理的：
  - `crawler/data/config.json`
  - `data/config.json`
  - `data/puzzle_pool.db-shm`
  - `data/puzzle_pool.db-wal`
  - `data/puzzle_pool.db`（modified，puzzle 池增長中）
  - `sb3/models/`（已存在 checkpoint，但 .gitignore 未涵蓋——user 選擇不動）

---

## 驗收條件（全 plan 完成後）

- [ ] `README.md` 存在於 repo root，GitHub 網頁預覽正常
- [ ] `demo.bat` 存在於 repo root，雙擊可成功啟動 TensorBoard + 跑完 eval（end-to-end smoke test）
- [ ] `docs/presentation/2026-04-27-sudoku-journey.md` 已被 git 追蹤
- [ ] `git status` 不再顯示 `deleted: sb3/runs/.../events.out.tfevents.1777102874...`
- [ ] `git log --oneline -5` 顯示新增的 3 個 commit（Task 3 / 4 / 5）
- [ ] **沒有任何 `.py` 檔案被改動**（用 `git diff main~5 -- '*.py'` 確認，新增 commit 不含 `.py`）

---

## Self-Review

**Spec coverage check:**
- ✅ §2.1 Live demo 安全名單 → README §快速試跑 + demo.bat 兩處都包含 TensorBoard 和 eval_sb3 指令
- ✅ §2.2 預錄資產全砍 → 計畫無任何資產製作 task
- ✅ §3.1 R1 README 結構（7 sections）→ Task 1 Step 1 內容包含全部 7 個 section
- ✅ §3.2 R6 demo.bat 行為流程（6 步）→ Task 2 Step 1 batch 內容對應 6 步
- ✅ §3.3 R4 docs/presentation/ → Task 3
- ✅ §3.4 R5 git rm --cached tfevents → Task 4
- ✅ §4 執行順序 5 步 → Task 1~5 對應
- ✅ §5 驗收條件 → 「驗收條件」section 全部覆蓋

**Placeholder scan:** 無 TBD / TODO / "implement later" / "similar to Task N"。所有 code block 都是完整可執行內容。

**File path consistency:** 
- README.md 內 `sudoku_sb3_ckpt_400000_steps.zip` ✓ matches 實際檔名
- demo.bat 內 `sb3\runs` 與 `sb3\models\sudoku_sb3_ckpt_400000_steps.zip` 路徑用 Windows backslash ✓
- Task 4 tfevents 完整路徑 `sb3/runs/sudoku_sb3/MaskablePPO_1/events.out.tfevents.1777102874.DESKTOP-VNDI6BN.24436.0` ✓ matches `git status` 報告
