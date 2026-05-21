# ch5–9 章節轉場重設計 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ch5–9 的章節進場轉場從「有文字標籤的 sticker prop 群組彈跳」重建成 ch1–4 那種抽象幾何 wipe/draw/slice，且各自仍抽象呼應章節概念。

**Architecture:** 所有轉場集中在單一檔案 `demo/presentation/src/layers/FadeBridge.jsx`，由 `ChapterEntryGesture(chapterId)` 的 `switch` 依進入章節 dispatch 到各 gesture 函式。本計畫只替換 ch5–9 五個 gesture 函式與其 `switch` 分派名稱，並移除僅供舊 ch8 使用的 `CH8_YELLOW_CELLS` 常數。ch1–4、`FadeBridge` 主邏輯、`BIG_TRANSITIONS`、`DefaultCreamFade` 完全不動。

**Tech Stack:** React + `motion/react`（`motion.div` / `motion.svg` / `motion.line` / `motion.rect` / `motion.path`，含 `pathLength`、keyframe `times`、`ease` 陣列、`clipPath`）。Vite dev server 做視覺驗收。

**驗收方式說明：** 轉場為純視覺、無邏輯分支，無自動化測試。每章以 `npm run dev` + `?ch=N` 直接載入觸發進場 gesture（`FadeBridge` 的 `prevChapter` 初值為 `null`，首次 mount 即播放一次該章轉場）肉眼驗收。最後跑既有 `npm run test:run` 確認沒有破壞既有套件。

**參考檔：** spec 在 `docs/superpowers/specs/2026-05-21-ch5-9-transition-redesign-design.md`。

---

## File Structure

- Modify: `demo/presentation/src/layers/FadeBridge.jsx`
  - 改 `ChapterEntryGesture` 的 `switch`：case 5–9 改指向新函式名。
  - 替換五個函式：`Ch5CrashCard`→`Ch5FaultLineShear`、`Ch6PinkStampCascade`→`Ch6PinkRedSweep`、`Ch7StairsAscend`→`Ch7LatticeLock`、`Ch8BoardMaterialize`→`Ch8GoldWedge`、`Ch9GhostCollage`→`Ch9ConvergeLines`。
  - 刪除 `CH8_YELLOW_CELLS` 常數（僅舊 ch8 用）。
- 不新增檔案、不改 import（既有 `import { motion } from 'motion/react'` 已足夠）。

---

### Task 0: 啟動 dev server（驗收用，整個計畫期間保持執行）

**Files:** 無（僅啟動服務）

- [ ] **Step 1: 啟動 Vite dev server（背景）**

Run: `cd demo/presentation && npm run dev`
Expected: 終端顯示 `Local: http://localhost:5173/`。整個實作期間保持此服務執行；每完成一章就在瀏覽器開對應 `?ch=N` 重新整理檢視。

---

### Task 1: ch5 — 紅色斷層撕裂（Ch5FaultLineShear）

概念：崩盤／碎裂。cream 沿反對角線剪成兩三角，鋸齒黑裂縫 `pathLength` 描入 + 紅光 flash，兩半沿對角 shear 滑出。時長 1500ms（ch4→5 屬 BIG_TRANSITIONS）。

**Files:**
- Modify: `demo/presentation/src/layers/FadeBridge.jsx`（`switch` case 5；替換 `Ch5CrashCard` 函式）

- [ ] **Step 1: 改 switch case 5**

把：
```jsx
    case 5: return <Ch5CrashCard duration={duration} />;
```
改成：
```jsx
    case 5: return <Ch5FaultLineShear duration={duration} />;
```

- [ ] **Step 2: 替換函式**

刪除整個 `Ch5CrashCard`（含其上方註解，從 `// ch5 · CrashLine 卡片放大版...` 到該函式結尾 `}`），改成：
```jsx
// ch5 · 斷層撕裂 —— cream 沿反對角剪兩半、鋸齒黑裂縫 pathLength 描入 + 紅光、兩半 shear 滑出
function Ch5FaultLineShear({ duration }) {
  const d = duration / 1000;
  const crack = 'M2000,0 L1500,360 L1180,200 L760,560 L420,360 L0,1200';
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {/* 左上三角 cream，hold 後往左上 shear 出 */}
      <motion.div
        animate={{ x: ['0%', '0%', '0%', '-60%'], y: ['0%', '0%', '0%', '-60%'], opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.12, 0.62, 1], ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5', clipPath: 'polygon(0 0, 100% 0, 0 100%)' }}
      />
      {/* 右下三角 cream，往右下 shear 出 */}
      <motion.div
        animate={{ x: ['0%', '0%', '0%', '60%'], y: ['0%', '0%', '0%', '60%'], opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.12, 0.62, 1], ease: ['easeOut', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5', clipPath: 'polygon(100% 0, 100% 100%, 0 100%)' }}
      />
      <svg viewBox="0 0 2000 1200" preserveAspectRatio="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}>
        {/* 鋸齒黑裂縫 —— pathLength 0→1 描入 */}
        <motion.path
          d={crack} fill="none" stroke="#000" strokeWidth={10}
          initial={{ pathLength: 0 }}
          animate={{ pathLength: [0, 1, 1, 1], opacity: [1, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.42, 0.62, 1], ease: ['easeIn', 'linear', 'easeOut'] }}
        />
        {/* 紅光 flash 沿裂縫 */}
        <motion.path
          d={crack} fill="none" stroke="#FF6B6B" strokeWidth={22}
          animate={{ opacity: [0, 0, 0.85, 0, 0] }}
          transition={{ duration: d, times: [0, 0.42, 0.5, 0.62, 1], ease: 'linear' }}
        />
      </svg>
    </div>
  );
}
```

- [ ] **Step 3: 視覺驗收**

瀏覽器開 `http://localhost:5173/?ch=5` 重新整理。
Expected: 畫面快速覆上 cream → 一道鋸齒黑線從右上往左下描出、線上閃一下紅光 → cream 沿該對角剪成兩塊、分別往左上與右下滑出，露出 ch5 內容。全程無文字、無貼紙彈跳。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/layers/FadeBridge.jsx
git commit -m "feat(demo): ch5 transition → fault-line shear (geometric DNA)"
```

---

### Task 2: ch6 — 粉轉紅切裂（Ch6PinkRedSweep）

概念：粉紅錯覺 → 第二次崩盤。粉紅面溫柔掃入並 hold（有希望）→ 紅 streak 橫掃（崩盤）→ 粉面滑出露出下一章。時長 1000ms。

**Files:**
- Modify: `demo/presentation/src/layers/FadeBridge.jsx`（`switch` case 6；替換 `Ch6PinkStampCascade` 函式）

- [ ] **Step 1: 改 switch case 6**

把：
```jsx
    case 6: return <Ch6PinkStampCascade duration={duration} />;
```
改成：
```jsx
    case 6: return <Ch6PinkRedSweep duration={duration} />;
```

- [ ] **Step 2: 替換函式**

刪除整個 `Ch6PinkStampCascade`（含其上方兩行註解 `// ch6 · 4 張粉紅 sticker cascade...` 與 `// 粉紅底 / 6px...`），改成：
```jsx
// ch6 · 粉轉紅 —— 粉紅面溫柔掃入 hold、紅 streak 橫掃（崩盤）、粉面滑出
function Ch6PinkRedSweep({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {/* 粉紅面：左→右掃入、hold、再往右掃出 */}
      <motion.div
        initial={{ x: '-100%' }}
        animate={{ x: ['-100%', '0%', '0%', '0%', '100%'] }}
        transition={{ duration: d, times: [0, 0.38, 0.5, 0.7, 1], ease: ['easeOut', 'linear', 'linear', [0.7, 0, 0.84, 0]] }}
        style={{ position: 'absolute', inset: 0, background: '#FFB6C1', borderRight: '6px solid #000' }}
      />
      {/* 紅 streak：橫向快速掃過粉面 */}
      <motion.div
        initial={{ x: '-120%' }}
        animate={{ x: ['-120%', '-120%', '120%'] }}
        transition={{ duration: d, times: [0, 0.5, 0.72], ease: ['linear', 'easeIn'] }}
        style={{ position: 'absolute', top: 0, bottom: 0, left: 0, width: '45%', background: '#FF6B6B', boxShadow: '12px 0 0 0 #000' }}
      />
    </div>
  );
}
```

- [ ] **Step 3: 視覺驗收**

瀏覽器開 `http://localhost:5173/?ch=6` 重新整理。
Expected: 粉紅整面從左滑入覆蓋、停一下 → 一條紅色寬條（右側帶黑硬陰影）由左快速掃過 → 粉面往右滑出，露出 ch6 內容。顏色序列粉→紅自己說完故事，無文字、無貼紙。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/layers/FadeBridge.jsx
git commit -m "feat(demo): ch6 transition → pink-to-red sweep (geometric DNA)"
```

---

### Task 3: ch7 — 約束格鎖死（Ch7LatticeLock）

概念：嚴肅／推理／死結／「0」。3×3 sudoku 粗框用 `pathLength` 描入、整體 scale snap 咬合，中央格閃紅轉黃（不寫字）。時長 1000ms。

**Files:**
- Modify: `demo/presentation/src/layers/FadeBridge.jsx`（`switch` case 7；替換 `Ch7StairsAscend` 函式）

- [ ] **Step 1: 改 switch case 7**

把：
```jsx
    case 7: return <Ch7StairsAscend duration={duration} />;
```
改成：
```jsx
    case 7: return <Ch7LatticeLock duration={duration} />;
```

- [ ] **Step 2: 替換函式**

刪除整個 `Ch7StairsAscend`（含上方註解 `// ch7 · 13-stairs ascend...`），改成：
```jsx
// ch7 · 約束格鎖死 —— 3×3 sudoku 粗框 pathLength 描入 + scale snap 咬合、中央格閃紅轉黃
function Ch7LatticeLock({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      <motion.div
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ duration: d, times: [0, 0.15, 0.82, 1], ease: 'linear' }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
        <motion.svg
          viewBox="0 0 90 90"
          style={{ width: '62vh', height: '62vh', overflow: 'visible' }}
          animate={{ scale: [0.92, 0.92, 1.04, 1, 1], opacity: [0, 1, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.2, 0.6, 0.82, 1], ease: ['linear', 'easeOut', 'easeOut', 'easeOut'] }}
        >
          {/* 外框 */}
          <motion.rect
            x="0" y="0" width="90" height="90" fill="none" stroke="#000" strokeWidth={3}
            initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
            transition={{ duration: d * 0.4, delay: d * 0.18, ease: 'easeOut' }}
          />
          {/* 直粗線 */}
          {[30, 60].map((x) => (
            <motion.line
              key={`v-${x}`} x1={x} y1={0} x2={x} y2={90} stroke="#000" strokeWidth={3}
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
              transition={{ duration: d * 0.35, delay: d * 0.25, ease: 'easeOut' }}
            />
          ))}
          {/* 橫粗線 */}
          {[30, 60].map((y) => (
            <motion.line
              key={`h-${y}`} x1={0} y1={y} x2={90} y2={y} stroke="#000" strokeWidth={3}
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
              transition={{ duration: d * 0.35, delay: d * 0.25, ease: 'easeOut' }}
            />
          ))}
          {/* 中央格閃紅轉黃 */}
          <motion.rect
            x="40" y="40" width="10" height="10" stroke="#000" strokeWidth={1.5}
            animate={{ fill: ['#FF6B6B', '#FF6B6B', '#FFD93D', '#FFD93D'], opacity: [0, 0, 1, 1] }}
            transition={{ duration: d, times: [0, 0.6, 0.66, 1], ease: 'linear' }}
          />
        </motion.svg>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: 視覺驗收**

瀏覽器開 `http://localhost:5173/?ch=7` 重新整理。
Expected: cream 覆上 → 一個置中的 3×3 粗框（外框 + 2 直 2 橫粗線）一筆筆描出、整體輕微放大後 snap 定位 → 正中央那格先閃紅再變黃 → cream 淡出露出 ch7。完全無數字文字。與 ch2 的滿版均勻細格明顯不同。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/layers/FadeBridge.jsx
git commit -m "feat(demo): ch7 transition → constraint lattice lock (geometric DNA)"
```

---

### Task 4: ch8 — 金光楔形破曉（Ch8GoldWedge）+ 刪除 CH8_YELLOW_CELLS

概念：突破／光明。金黃斜帶硬邊掃過全螢幕 + 紫窄帶 depth。時長 1500ms（ch8→9 屬 BIG_TRANSITIONS）。

**Files:**
- Modify: `demo/presentation/src/layers/FadeBridge.jsx`（`switch` case 8；替換 `Ch8BoardMaterialize` 函式；刪 `CH8_YELLOW_CELLS` 常數）

- [ ] **Step 1: 改 switch case 8**

把：
```jsx
    case 8: return <Ch8BoardMaterialize duration={duration} />;
```
改成：
```jsx
    case 8: return <Ch8GoldWedge duration={duration} />;
```

- [ ] **Step 2: 替換函式並刪常數**

刪除整段：上方註解 `// ch8 · 9×9 sudoku 盤面...`、`const CH8_YELLOW_CELLS = new Set([20, 44, 66]);  // ...` 那一行、以及整個 `Ch8BoardMaterialize` 函式，改成：
```jsx
// ch8 · 金光楔形破曉 —— 金黃斜帶硬邊掃過全螢幕 + 紫窄帶 depth
function Ch8GoldWedge({ duration }) {
  const d = duration / 1000;
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {/* 主金黃斜帶 */}
      <motion.div
        initial={{ x: '-160%', rotate: -18 }}
        animate={{ x: ['-160%', '0%', '0%', '160%'], rotate: [-18, -18, -18, -18] }}
        transition={{ duration: d, times: [0, 0.42, 0.6, 1], ease: ['easeOut', 'linear', 'easeIn'] }}
        style={{ position: 'absolute', top: '-80%', left: '-50%', width: '200%', height: '260%', background: '#FFD93D' }}
      />
      {/* 紫窄帶 trailing depth */}
      <motion.div
        initial={{ x: '-160%', rotate: -18 }}
        animate={{ x: ['-160%', '-32%', '-32%', '170%'], rotate: [-18, -18, -18, -18] }}
        transition={{ duration: d, times: [0, 0.5, 0.66, 1], ease: ['easeOut', 'linear', 'easeIn'] }}
        style={{ position: 'absolute', top: '-80%', left: '-50%', width: '22%', height: '260%', background: '#C4B5FD', borderRight: '6px solid #000' }}
      />
    </div>
  );
}
```

- [ ] **Step 3: 視覺驗收**

瀏覽器開 `http://localhost:5173/?ch=8` 重新整理。
Expected: 一道大面積金黃斜帶（約 -18°）從左下硬邊掃入覆蓋整個畫面、停一下、再往右上掃出；一條較窄的紫色硬邊帶緊跟其後做 depth → 露出 ch8。無柔光、無漸層、無數字盤面。

- [ ] **Step 4: 確認沒有殘留 CH8_YELLOW_CELLS 參照**

Run: `cd demo/presentation && npx grep -r CH8_YELLOW_CELLS src 2>/dev/null || rg CH8_YELLOW_CELLS src`
Expected: 無輸出（常數已完全移除、無其他檔參照）。

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/layers/FadeBridge.jsx
git commit -m "feat(demo): ch8 transition → gold wedge wipe (geometric DNA)"
```

---

### Task 5: ch9 — 線條收斂（Ch9ConvergeLines）

概念：收斂／收尾／哲思。黑/紫線從四邊向中心收斂成十字，cream 由中心 iris 展開覆蓋。時長 1500ms。

**Files:**
- Modify: `demo/presentation/src/layers/FadeBridge.jsx`（`switch` case 9；替換 `Ch9GhostCollage` 函式）

- [ ] **Step 1: 改 switch case 9**

把：
```jsx
    case 9: return <Ch9GhostCollage duration={duration} />;
```
改成：
```jsx
    case 9: return <Ch9ConvergeLines duration={duration} />;
```

- [ ] **Step 2: 替換函式**

刪除整個 `Ch9GhostCollage`（含上方註解 `// ch9 · ghost-collage...`），改成：
```jsx
// ch9 · 線條收斂 —— 黑/紫線從四邊向中心收斂成十字、cream 由中心 iris 展開
function Ch9ConvergeLines({ duration }) {
  const d = duration / 1000;
  const hLines = [
    { start: '-46vh', color: '#000' },
    { start: '-24vh', color: '#C4B5FD' },
    { start: '24vh',  color: '#C4B5FD' },
    { start: '46vh',  color: '#000' },
  ];
  const vLines = [
    { start: '-46vw', color: '#C4B5FD' },
    { start: '-24vw', color: '#000' },
    { start: '24vw',  color: '#000' },
    { start: '46vw',  color: '#C4B5FD' },
  ];
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none' }}>
      {hLines.map((l, i) => (
        <motion.div
          key={`h-${i}`}
          initial={{ y: l.start, opacity: 0 }}
          animate={{ y: [l.start, '0vh', '0vh', '0vh'], opacity: [0, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.5, 0.7, 1], ease: ['easeIn', 'linear', 'linear'] }}
          style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: 4, marginTop: -2, background: l.color }}
        />
      ))}
      {vLines.map((l, i) => (
        <motion.div
          key={`v-${i}`}
          initial={{ x: l.start, opacity: 0 }}
          animate={{ x: [l.start, '0vw', '0vw', '0vw'], opacity: [0, 1, 1, 0] }}
          transition={{ duration: d, times: [0, 0.5, 0.7, 1], ease: ['easeIn', 'linear', 'linear'] }}
          style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 4, marginLeft: -2, background: l.color }}
        />
      ))}
      {/* cream 由中心 iris 展開覆蓋 */}
      <motion.div
        animate={{ clipPath: ['circle(0% at 50% 50%)', 'circle(0% at 50% 50%)', 'circle(150% at 50% 50%)'] }}
        transition={{ duration: d, times: [0, 0.6, 1], ease: ['linear', 'easeIn'] }}
        style={{ position: 'absolute', inset: 0, background: '#FFFDF5' }}
      />
    </div>
  );
}
```

- [ ] **Step 3: 視覺驗收**

瀏覽器開 `http://localhost:5173/?ch=9` 重新整理。
Expected: 多條黑/紫細線從上下左右朝中心加速收斂、交會成一個十字 → 一個 cream 圓從正中央向外擴張覆蓋全螢幕 → 露出 ch9。乾淨克制，紫色 accent，無文字、無 8 張回憶貼紙。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/layers/FadeBridge.jsx
git commit -m "feat(demo): ch9 transition → converging lines iris (geometric DNA)"
```

---

### Task 6: 全章串看 + 既有測試 + 收尾

**Files:** 無（驗收與回歸）

- [ ] **Step 1: 串看 ch4→5→6→7→8→9 連續轉場**

從 `http://localhost:5173/?ch=4` 開始，用點擊/方向鍵推進直到自然進入 ch5、ch6…ch9，確認每章轉場自動播放且與 ch1–4 同語系（抽象幾何、流暢、無文字 sticker）。
Expected: ch5–9 風格與 ch1–4 一致；無 console 報錯。

- [ ] **Step 2: 跑既有測試套件確認沒破壞**

Run: `cd demo/presentation && npm run test:run`
Expected: 既有測試全數通過（本次未改動任何被測元件邏輯）。

- [ ] **Step 3: reduced-motion 抽查（選做）**

在瀏覽器 DevTools 開啟 `prefers-reduced-motion: reduce`，重整 `?ch=5`～`?ch=9`。
Expected: 沿用既有全域規範，轉場不應造成卡死或報錯（本檔未特別處理 reduced-motion，行為與 ch1–4 一致）。

- [ ] **Step 4: 確認分支狀態乾淨**

Run: `git status`
Expected: working tree clean；ch5–9 五個 commit 都在 `feat/ch5-9-transition-redesign` 分支上。

---

## Self-Review

**Spec coverage:**
- 共同 DNA 準則 1–7 → 每個函式都用 cream 底/抽象幾何/hard edge/該章 accent/`duration` prop/`zIndex:80` 容器；BIG_TRANSITIONS 未更動（Task 未碰）。✓
- ch5 斷層撕裂 / ch6 粉轉紅 / ch7 約束格鎖死 / ch8 金光楔形 / ch9 線條收斂 → Task 1–5 各一。✓
- 「唯一改動 FadeBridge.jsx、不動 ch1–4」→ File Structure + 各 Task 明列。✓
- 刪除舊 ch8 專用 `CH8_YELLOW_CELLS` → Task 4 Step 2/4。✓
- 驗收（dev server `?ch=N` + `npm run test:run`）→ Task 0、Task 6。✓

**Placeholder scan:** 每個 code step 都有完整可貼上的函式碼，無 TBD/TODO/「類似上面」。✓

**Type/naming consistency:** 五個新函式名（`Ch5FaultLineShear` / `Ch6PinkRedSweep` / `Ch7LatticeLock` / `Ch8GoldWedge` / `Ch9ConvergeLines`）在「改 switch」與「替換函式」兩處逐一對應一致。✓
