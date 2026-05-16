# outline.md 重對齊 script.md 設計規格

> **日期**：2026-05-16
> **狀態**：Brainstorming approved → 待使用者 review → 進入 writing-plans
> **作者**：Claude Opus 4.7 + user
> **觸發**：使用者在 Phase 1.5 把 `demo/script.md` 個人化重寫後，原本 Phase 1.2 產出的 `demo/outline.md` 結構已失準。需重對齊以保證最終 HTML 對標 script.md。

---

## 1. 背景與目標

### 1.1 既有狀態

- `demo/script.md`（375 行）：使用者個人化重寫完成、已順暢化、本次重對齊的**唯一基石**
- `demo/outline.md`（333 行）：Phase 1.2 從 content.md + prompt.md 機械產出、未經 script.md 重寫後同步、**結構失準**
- `demo/content.md`、`demo/prompt.md`、`demo/web_style.md`：源頭參考資料、**本次不動**（保留歷史脈絡）

### 1.2 目標

讓 `demo/outline.md` 完全對齊 `demo/script.md`，使後續 HTML scaffold（按 outline.md 開章節資料夾 + step 數 + 信息池 + 素材清單）產出的內容與 script.md 口播一致。

### 1.3 主要結構性差異（script.md vs 舊 outline.md）

| 差異點 | 舊 outline | script.md |
|---|---|---|
| Hook | 電費小偷 + 四個月後伏筆 | 心虛 + 心理學系背景 |
| 雙主線編織 (情緒色 + 教訓編號) | ch5-8 章末合併句 | 拿掉、無編號副旋律 |
| 戀愛 hook 進場 | ch5 章末伏筆 | ch6 sb3 (新女生加分) |
| 結尾長度 | ch9 6 step ~80s | ~14 step ~190s |
| 結尾 punchline | 「電費沒白繳」 | 電費小偷笑話 (line 375) |
| 時間 anchor | 四個月 | 兩個月 |
| Visualizer 位置 | ch8 末 step 12 | ch8 末 step 7 |

---

## 2. 範圍

### 2.1 In scope
- 重寫 `demo/outline.md` 全部 9 章的：頂部 metadata block / 信息池 / 開發計畫 (step list) / 口播節選 / 末尾素材清單

### 2.2 Out of scope
- `demo/content.md`、`demo/prompt.md`、`demo/web_style.md` 不動
- 主題 (`monochrome-print` Neo-brutalism) 不重新走 Checkpoint Plan、維持不變
- `demo/script.md` 不動（基石）

---

## 3. 章節對應表

保留 9 章、id 不變、scaffold folder 名稱不需重命名。

| # | id | 動作 | 舊 step | 新 step | script.md 行 | 重點變更 |
|---|---|---|---|---|---|---|
| 1 | coldopen | REWRITE | 8 | 6 | L1-37 | hook 變心虛+心理學系；移除電費小偷/四個月後；保留正妹/flappy bird/當兵/Boom/punchline |
| 2 | ml-map | TRIM | 5 | 4 | L41-69 | 移除 hero 過渡 step；直接 supervised/unsupervised/RL+AlphaGo/cliffhanger |
| 3 | llm-vs-rl | KEEP | 4 | 3 | L71-91 | 內容大致符合、合併原 step 1+2 為單 step (LLM 路線 + 對比) |
| 4 | data-hunt | TRIM | 4 | 4 | L93-135 | 移除「終極武器」戲劇話術；proxy 簡化為「類似 VPN」一句 |
| 5 | legacy | TRIM | 6 | 4 | L137-161 | 移除教訓編號 / 838 行 dump / 難度 1-4 sticker；只留「800 多行單檔 → 第一件事 → 套皮仔過渡」 |
| 6 | sb3 | REORG | 10 | 7 | L163-199 | 加入**戀愛 hook a (新女生加分→備胎)**；移除 95%/0%/14 次/8ch→26ch/8 沙盒等 script 沒提的數字 |
| 7 | reasoner | REORG | 11 | 8 | L201-269 | 加入**戀愛 hook b (老油條陷阱題)**；移除 729→1458 翻牌/24ch/賤招 33+20/2000萬 step 數字；保留 13 招大階梯 |
| 8 | apprentice | TRIM | 13 | 7 (含 viz) | L273-301 | 移除 bug fix #1/#2 / MAX_WRONG / 階乘類比 / 死結 50 步地圖；保留反向課程 + 翻牌 + tensorboard 截圖 + visualizer |
| 9 | callback | GREATLY EXPAND | 6 | 14 | L303-375 | 結尾大擴張：磨合過渡 → AI 訓練我 → RL 對等 + 飛機鳥 → 戀愛 a → 戀愛 b → plasticity 三項 → **MBTI INFJ** → **業務變 E** → 不被擊敗 → 職場祝福 → **電費小偷笑話 (verbatim)** |
| **總計** | — | — | **67** | **57 (含 viz step)** | — | — |

---

## 4. 信息池規則（更新）

### 4.1 新規則
1. **主要 anchor 必須在 script.md 找得到**（script 是基石）
2. **補充 anchor 可從 content.md / prompt.md / 真實程式碼取**——僅在加強 script 已提到的內容時
3. **不挂 script 沒提的數字**（避免畫面資訊密度超過口播）
4. **真實程式碼 anchor 只在 script 對應內容存在時保留**（e.g., legacy 838 行：script 提「800 多行」、所以 838 留作畫面 anchor、口播照 script 走）

### 4.2 移除清單（script 沒提、舊 outline 有的數字）
- sb3：14+ runs / 訓練 95% / held-out 0% / obs 8→26ch / 8× SubprocVecEnv
- reasoner：729→1458 Action / 24ch / ~20.3M steps / 33+20 賤招 / MAX_WRONG=20
- apprentice：MAX_WRONG=20 / `target_empty=3` 配置數字 / 死結 50 步×1500 選擇階乘類比 / bug fix #1 + #2 工程描述

### 4.3 保留清單（真實程式碼 anchor 對 script 有支撐）
- legacy 838 行 `legacy/app/sudoku/torch_agent.py`（口播 800 多行、畫面 838 為實值）
- reasoner 13 招技巧名（naked single / hidden single / X-Wing / Swordfish / XY-Wing 等、script L209 列出）
- apprentice 反向課程 (3→4→5→7→10) + 破關獎 +20→+50（script L287、L293 提）
- apprentice visualizer `apprentice/demo/visualize.py`（script L297-299 提）
- apprentice tensorboard 截圖（使用者表示有素材可挂）

---

## 5. 素材清單調整

| 章 | 移除 | 新增 | 保留 |
|---|---|---|---|
| 1 coldopen | 「電費小偷」sticker · 「四個月後⋯⋯」標尺 | 「心虛」表情 sticker · 心理學系背景 sticker | 正妹 / Code Bullet flappy bird / 當兵數獨 / 訓練 AI 解數獨 4 sticker |
| 2 ml-map | hero 過渡 step | — | 三欄 supervised/unsupervised/RL + AlphaGo 標籤 |
| 3 llm-vs-rl | — | — | LLM vs 我的 AI 對比 + 房間 sticker |
| 4 data-hunt | 「終極武器」戲劇大字 · proxy 池細節 | — | Kaggle 標籤 · websudoku URL sticker · 多 worker fanout |
| 5 legacy | 838 行 dump 動畫 · 難度 1-4 sticker · 教訓編號紅底大字 | 「800 多行單一檔案」簡單視覺 sticker | 「⋯我錯了」獨立崩盤句 |
| 6 sb3 | obs 8→26ch 對照 · 訓練曲線 95%→0% · 8 沙盒 · 14+ runs 標籤 · 「AI 在背小抄」紅 stamp | **「新女生加分」sticker · 「備胎」stamp sticker** · 計分表「填對給分」· 「找漏洞作弊」紅 stamp | — |
| 7 reasoner | 729→1458 翻牌 · 24ch · 訓練曲線 0 success · 賤招 33+20 動畫 · 冷戰期 callback | **「老油條女陷阱題」sticker · 「跟你媽掉水裡」考題 · 「該不該運動」考題 · 兩個答案都錯的陷阱箭頭** | 13 招大階梯 (X-Wing / XYZ-Wing 最大) · 舊 vs 新作法對比 |
| 8 apprentice | bug fix #1/#2 對照動畫 · MAX_WRONG=20 · 階乘類比 · 死結 50 步地圖 | — | 反向課程盤面動畫 (3→4→5→7→10) · +20→+50 翻牌 · **tensorboard 真實截圖** · visualizer 大按鈕 |
| 9 callback | 雙 hook 四線合流 · 「電費沒白繳」(原 punchline) | **MBTI INFJ sticker · 業務工作 sticker · 「不是天生會講話/相處」三欄 · 「不被擊敗」標語 · 「人生第一次外向→一輩子內向」警語 · 電費小偷 final 笑話大字** | 戀愛 a 加分扣分雙欄 · 戀愛 b 考題 sticker · plasticity 三欄 · 飛機模仿鳥 sticker |

---

## 6. 全片 anchor 統一變更

- 時間：「四個月」全部改「兩個月」（script L375 verbatim「這兩個月」是錨點）
- 自我標籤：「電費小偷」只在 ch9 結尾笑話出現一次（line 375）、ch1-8 不再 thread 出現
- 雙主線編織片頭備註整段刪除（outline.md 頂部）

---

## 7. 視覺主題

`monochrome-print` Neo-brutalism 維持不變：
- 色票：cream / black / hot-red / yellow / violet（per `demo/web_style.md`）
- Sticker：黑邊 border-4 / hard shadow / 旋轉 -3°~4°
- 字體：mono cue + 大字 hero
- 不需重走 Checkpoint Plan 主題選擇

---

## 8. 總時長預算

| 章 | step | 估時 |
|---|---|---|
| 1 coldopen | 6 | ~60s |
| 2 ml-map | 4 | ~50s |
| 3 llm-vs-rl | 3 | ~35s |

| 4 data-hunt | 4 | ~50s |
| 5 legacy | 4 | ~50s |
| 6 sb3 | 7 | ~70s |
| 7 reasoner | 8 | ~130s |
| 8 apprentice | 7 (含 viz) | ~75s + viz 30-60s |
| 9 callback | 14 | ~190s |
| **總計** | **57 (含 viz step)** | **~12 min + viz 30-60s = 12.5-13 min** |

- 估算速率：~3.5 字/秒（口語停頓 + 戲劇拉長 → 比 OUTLINE-FORMAT 預設 4 字/秒 慢）
- 在 15 min 之內

---

## 9. 執行步驟

1. 頂部 metadata block 改：總時長 ~12 min + viz / 章節數 9 / 67→57 step + 移除雙主線編織備註
2. 章節 1-9 逐章 in-place edit (Edit tool、不整檔 Write)，每章順序：信息池 → 開發計畫 → 口播節選
3. 末尾「素材清單」整段重寫對應新章節
4. 全片 grep「四個月」→「兩個月」、移除 ch5-8 「電費小偷」threading callback
5. 67→57 step 變更會影響的 metadata：頂部「9 章 / 57 步」+ 雙主線編織 4 行 callout 整段刪除

---

## 10. 自檢清單（按 OUTLINE-FORMAT.md §自檢）

寫完後執行：
- [ ] 每個 step 都是單一句屏幕內容描述、沒有動畫/手段行
- [ ] 沒有 step 寫具體毫秒/秒數（除 `(~Ts)` 口播估時）
- [ ] 每章首段有「信息池」block、至少 3 條 anchor、**每條必帶來源標注**（`—— 來源 script.md Lxx` 或 content.md / 真實程式碼）
- [ ] 所有 step `(~Ts)` 累加 ≈ 頂部總時長（誤差 < 10%）
- [ ] 章節切分符合「每章 3~8 步 / 30~60s 一聚焦主題」經驗（ch9 例外因結尾長章）
- [ ] 末尾「素材清單」分章節列出、✓ / ⚠️ / 📦 標註清楚

---

## 11. 風險與緩解

| 風險 | 緩解 |
|---|---|
| outline 變更失準時 chapter agent 寫 HTML 時跟 script.md 對不上 | 信息池每條都標注 `—— 來源 script.md Lxx`、chapter agent 必回 script 對照 |
| 結尾 ch9 14 step 超過 OUTLINE-FORMAT 建議 8 step | 在 outline 章末標明「結尾長章例外」+ 章內用 micro-step 切分（chapter agent 自行決定動畫節拍） |
| 時長 ~12 min 估算誤差 | 實作時以 narrations.ts 為準（雙源原則），audio 合成時回 script.md 字數重算 |
| outline 變更未 git commit 導致回滾困難 | spec 通過後 + outline.md 修改完 → git commit（不 push） |
