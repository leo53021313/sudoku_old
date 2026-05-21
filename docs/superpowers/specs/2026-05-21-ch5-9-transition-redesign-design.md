# ch5–9 章節轉場重設計（對齊 ch1–4 流暢幾何 DNA）

> 日期：2026-05-21
> 範圍：`demo/presentation/src/layers/FadeBridge.jsx` 內 ch5–9 的 `ChapterEntryGesture`

## 背景與問題

所有章節進場轉場集中在單一檔案 [FadeBridge.jsx](../../../demo/presentation/src/layers/FadeBridge.jsx)，由 `ChapterEntryGesture(chapterId)` 依進入章節 dispatch。

- **ch1–4（保留，使用者喜歡）**：抽象幾何 primitive 全螢幕 wipe/draw/slice。動態是主角，且各自抽象呼應章節概念。
  - ch1 `Ch1PaperUnfold`：cream 雙半開合 unfold
  - ch2 `Ch2GridDrawIn`：SVG 格線用 `pathLength` 一筆筆描入（= ML 地圖）
  - ch3 `Ch3SplitScreen`：雙半合攏 → 黑線劈下 → 紅 flash → 彈開（= LLM vs RL 對決）
  - ch4 `Ch4TierSnap`：黑橫條 + 黃 accent 掃過（= tier-list 盤點）
- **ch5–9（重設計目標，使用者不喜歡）**：改用「貼上有文字標籤的 sticker prop 群組」，以 `cubic-bezier(0.34,1.56,0.64,1)` 彈跳 pop-in。文字標籤（`+1`/`錯`/`AI`/`+50` 等）與 stamp 手勢讓它們讀起來像「主題貼紙拼貼」而非流暢轉場。
  - ch5 `Ch5CrashCard`、ch6 `Ch6PinkStampCascade`、ch7 `Ch7StairsAscend`、ch8 `Ch8BoardMaterialize`、ch9 `Ch9GhostCollage`

## 目標

把 ch5–9 重建成 ch1–4 同款的**抽象幾何 wipe 轉場**，且每章仍**抽象呼應該章概念**（保留概念隱喻原則）。

## 共同 DNA 準則（所有 ch5–9 轉場必守）

1. 保留全螢幕 cream `#FFFDF5` 底層 `opacity: [0,1,1,0]` fade-in / hold / out（與 ch1–4 一致）。
2. 只用**抽象幾何**：面 / 線 / 條 / 切口 / 格。**零文字、零 sticker prop、零 emoji 或標籤字串**。
3. 純黑 4–6px hard border + hard offset shadow（zero blur）；accent 顏色只用該章主色（見下表）。
4. 動態語彙限定 ch1–4 那套：hard-edge `translate` / `scale` snap / SVG `pathLength` 描線 / 面切開。
   **移除 sticker 式 `0.34,1.56,0.64,1` 群組彈跳 pop-in。**（單一硬 snap 可保留，如 ch3 黑刃、ch4 黑條。）
5. 維持既有時長機制：`BIG_TRANSITIONS = {'1-2','4-5','8-9'}` → 1500ms，其餘 1000ms。不更動此集合。
6. 維持 `aria-hidden`、`position: fixed`、`zIndex: 80`、`pointerEvents: 'none'` 容器規格。
7. 全部 `duration` 由 prop 傳入（`const d = duration / 1000`），不寫死秒數。

## 章節色票對照（取自 outline-visual.md §6）

| ch | 主題情緒 | 主色 | accent |
| --- | --- | --- | --- |
| 5 legacy | 崩盤 #1 | cream + 紅邊 | 紅 `#FF6B6B` |
| 6 sb3 | 戀愛錯覺 → 崩盤 #2 | 粉紅 `#FFB6C1` | 紅 `#FF6B6B` |
| 7 reasoner | 嚴肅 / 死結 | cream + 黑 | 紅 `#FF6B6B` → 黃 `#FFD93D` |
| 8 apprentice | 突破 / 光明 | cream + 金黃 `#FFD93D` | 紫盤 `#C4B5FD` |
| 9 callback | 收斂 / 哲思 / 收尾 | cream（純） | 紫 `#C4B5FD` |

## 各章設計（採用主推方案）

### ch5 — 紅色斷層撕裂（Fault-Line Shear）

概念隱喻：崩盤 / 碎裂。

- cream 底層進場。
- 一道鋸齒黑裂縫（SVG polyline）用 `pathLength: 0→1` 斜向劃過全螢幕（描入）。
- 裂縫描完瞬間，沿裂縫閃一道紅光（短暫 `opacity` flash，`#FF6B6B`）。
- 畫面沿裂縫剪成兩塊，兩塊以 hard-edge `translate` 往反方向滑出（shear），露出下一章。
- 與 ch3 對切的區隔：用「鋸齒裂縫 + 反向 shear」而非「直線對切 + 彈開」。
- 時長 1500ms（ch4→5 屬 BIG_TRANSITIONS）。

### ch6 — 粉轉紅切裂（Pink → Red Sweep & Crack）

概念隱喻：粉紅錯覺 → 第二次崩盤。

- 粉紅 `#FFB6C1` 面從一側溫柔（`easeOut`，較慢）掃入全螢幕。
- 短暫 hold（看似有希望）。
- 一道紅 `#FF6B6B` 刀刃（細長條，`scaleY`/`scaleX` 由 0 snap 到 1）劈過粉紅面。
- cream 收掉，露出下一章。
- 全程零文字；顏色序列 pink → red 自己說完故事。

### ch7 — 約束格鎖死（Constraint Lattice Lock）

概念隱喻：嚴肅 / 推理 / 死結 / 「0」。

- 畫的是 sudoku 的 3×3 粗框格線（非 ch2 的均勻細格），用 `pathLength` 從四周向中心描入。
- 描完做一個緊的硬 `scale` snap（咬合鎖定感）。
- 中央一格先閃紅 `#FF6B6B` 再轉黃 `#FFD93D`（暗示死結與 reward「0」，**不寫任何字**）。
- cream 收掉。
- 與 ch2 區隔：ch2 是滿版均勻 graph-paper 描線；ch7 是 3×3 box 結構鎖死 + 中央格變色。
- 時長 1000ms。

### ch8 — 金光楔形破曉（Gold Wedge Wipe）

概念隱喻：突破 / 光明。

- cream hold。
- 一道金黃 `#FFD93D` 硬邊楔形 / 斜帶從一角以 hard-edge `translate` 掃過全螢幕（brutalist 版「光芒展開」，非柔光、非漸層）。
- 可疊一兩條較窄的同色或紫 `#C4B5FD` 平行硬條做 depth，但不可用 blur / soft shadow。
- 揭開下一章。
- 時長 1500ms（ch8→9 屬 BIG_TRANSITIONS）。

### ch9 — 線條收斂（Converging Lines / Iris）

概念隱喻：收斂 / 收尾 / 哲思。

- 多條細黑 / 紫 `#C4B5FD` 線條從四邊向中心 `translate` 收斂成一點或一條中線（收斂）。
- 短暫 hold。
- 再以 cream 由中心向外展開（iris-out），露出下一章。
- 紫色 accent，乾淨克制。
- 時長 1500ms。

## 實作範圍與不變項

- **唯一改動檔**：`demo/presentation/src/layers/FadeBridge.jsx`。
- 替換 `Ch5CrashCard` / `Ch6PinkStampCascade` / `Ch7StairsAscend` / `Ch8BoardMaterialize` / `Ch9GhostCollage` 五個函式的內容；`ChapterEntryGesture` 的 `switch` 分派與函式名可沿用（或改名後同步更新 `switch`）。
- **不更動**：`FadeBridge` 主元件邏輯、`BIG_TRANSITIONS` 集合、`DefaultCreamFade`、ch1–4 四個函式。
- 既有 `motion/react` import 已足夠；如需 SVG polyline 描線沿用 ch2 的 `motion.line` + `pathLength` 模式。
- 沿用既有 `@keyframes fade-bridge`（僅 default fallback 用，不影響 ch5–9）。

## 測試 / 驗收

- `cd demo/presentation && npm run dev`，用 `?ch=N` 逐章切換觀察進場轉場（或從上一章末自動播放進入）。
- 驗收標準：ch5–9 轉場讀起來與 ch1–4 同一語系（抽象幾何、流暢、無文字 sticker），且各自仍能聯想到該章概念。
- 既有 vitest 套件（`npm run test:run`）不應因此改動失敗；本次不新增測試（轉場為純視覺、無邏輯分支）。
- 確認 `prefers-reduced-motion` 行為未被破壞（沿用既有全域規範，不在本檔特別處理）。

## YAGNI / 範圍外

- 不重做 ch1–4。
- 不改 step 內動畫、motif、climax FX。
- 不調整 `BIG_TRANSITIONS` 時長分類。
- 備案方案（每章的第二選項）本次不實作，僅作為未來微調備查。
