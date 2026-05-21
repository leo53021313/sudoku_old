# ch4 step2 — tier-list sticker 動畫節奏 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `Ch4Step2.jsx` 的動畫節奏 — sticker showcase 大尺寸出場 → 縮小 dock 進 tier-list 對應 row，tier list 在 showcase beat 隱藏或虛化，跟 spec 對齊。

**Architecture:** 三個 motion.div (tier-table、supervised、RL) 各自的 `animate` prop 是 `beatIndex` 的純函式回傳值。Showcase = big centered (scale 1.8)；dock = scale 1、左邊緣對齊 slot 左側 + 16 px inset (用 `transformOrigin: 'left center'` + `x: 0`)；dim 透過 `opacity` + CSS `filter: blur()` 對 table 和 parked sticker 各自套用 (不靠 CSS 繼承)。

**Tech Stack:** React 19, Framer Motion (`motion@12`).

**Spec reference:** [docs/superpowers/specs/2026-05-21-ch4-step2-tier-list-animation-design.md](../specs/2026-05-21-ch4-step2-tier-list-animation-design.md)

---

## File Structure

- **Modify:** `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx` (full rewrite of the component body — helpers + JSX)

No new files. No new tests:
- Deck 慣例只對 motif 原件加 vitest (e.g. `CounterUp.test.jsx`, `SudokuBoardLive.test.jsx`)，不對 step-level 元件加。新增 step-level 測試屬於 scope expansion，不在本 plan 內。
- 驗證閘 = `vite build` clean + `npm run test:run` (現有 `usePresentation.test.js totalBeats=93` 等) 全綠 + 人工 / Playwright 視覺 smoke。

Beat manifest (`demo/presentation/src/data/beat-manifest.js`) 已是 4 beats，本 plan 不動。

---

## Task 1: 重寫 Ch4Step2.jsx 為新動畫節奏

把現有檔案改成：tier-table、supervised、RL 各自由 beatIndex 純函式驅動 motion props。

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx` (整檔重寫)

- [ ] **Step 1: 用 Write tool 整檔覆寫**

新檔案內容如下 (完整可貼)：

```jsx
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

// 夯爆了 / 拉完了 tier-list meme — 把 supervised vs RL 兩條路線丟進排行榜。
// 5 rows top→bottom: 夯 顶级 人上人 NPC 拉完了 (簡體中文以還原迷因原版)
const TIERS = [
  { key: '夯',     bg: '#E84545' },
  { key: '顶级',   bg: '#F2A93B' },
  { key: '人上人', bg: '#FFEB3B' },
  { key: 'NPC',    bg: '#FCEED9' },
  { key: '拉完了', bg: '#FFFFFF' },
];

const ROW_H = 124;
const DIVIDER = 3;       // borderTop on rows 1..4 (content-box → adds to total height)
const LABEL_W = 240;
const SLOT_W = 880;
const TABLE_W = LABEL_W + SLOT_W;
const TABLE_H = ROW_H * TIERS.length + DIVIDER * (TIERS.length - 1);

const ROW_HANG = 0;   // 夯  (頂 — RL 的 dock)
const ROW_TRASH = 4;  // 拉完了 (底 — supervised 的 dock)

const OVERSHOOT = [0.34, 1.56, 0.64, 1];
const STICKER_TR = { duration: 0.6, ease: OVERSHOOT };
const TABLE_TR   = { duration: 0.4, ease: 'easeOut' };

const SHOWCASE_SCALE = 1.8;
const DOCK_INSET = 16;   // sticker 視覺左緣 相對 slot 左緣 的 px

const STICKER_BASE = {
  position: 'absolute',
  background: '#FFD93D',
  color: '#000',
  padding: '12px 26px',
  border: '5px solid #000',
  boxShadow: '6px 6px 0 0 #000',
  fontWeight: 900,
  fontSize: 30,
  whiteSpace: 'nowrap',
  transformOrigin: 'left center', // dock 時 left 座標 = 視覺左緣
};

// row i 的 slot 垂直中軸 (相對 table 左上角)
const rowCenterY = (rowIdx) => rowIdx * (ROW_H + DIVIDER) + ROW_H / 2;

// 「showcase 大」 — 置中 table 容器、scale 1.8。
// 用 transformOrigin 'left center' 配 x:'-50%' 達成水平居中、y:'-50%' 達成垂直居中。
function showcaseAnim(rotate) {
  return {
    opacity: 1,
    scale: SHOWCASE_SCALE,
    top: TABLE_H / 2,
    left: TABLE_W / 2,
    x: '-50%',
    y: '-50%',
    rotate,
    filter: 'blur(0px)',
  };
}

// 「dock 小」 — sticker 視覺左緣 = LABEL_W + DIVIDER + DOCK_INSET。
// transformOrigin: 'left center' (在 STICKER_BASE) + x:0 → left 座標即視覺左緣。
function dockAnim(rowIdx, rotate, dim) {
  return {
    opacity: dim ? 0.35 : 1,
    scale: 1,
    top: rowCenterY(rowIdx),
    left: LABEL_W + DIVIDER + DOCK_INSET,
    x: 0,
    y: '-50%',
    rotate,
    filter: dim ? 'blur(3px)' : 'blur(0px)',
  };
}

// 「隱藏」 — 縮在 showcase 位置外、opacity 0。給 RL beat<2 用，beat 2 可平順 morph 成 showcase。
function hiddenAnim() {
  return {
    opacity: 0,
    scale: 0.2,
    top: TABLE_H / 2,
    left: TABLE_W / 2,
    x: '-50%',
    y: '-50%',
    rotate: 0,
    filter: 'blur(0px)',
  };
}

// tier-table 容器自己的 dim 狀態 — 跟 parked sticker 的 dim 狀態同步、但這裡單獨算
// 因為 sticker 是 motion 平級兄弟、不靠 CSS 繼承 (避免 filter inheritance 不可預期)。
function tableState(beatIndex) {
  if (beatIndex <= 0) return { opacity: 0,    filter: 'blur(0px)' };
  if (beatIndex === 2) return { opacity: 0.35, filter: 'blur(3px)' };
  return { opacity: 1, filter: 'blur(0px)' };
}

function supervisedState(beatIndex) {
  if (beatIndex === 0) return showcaseAnim(0);
  // beat ≥ 1: dock 在 拉完了；只在 beat 2 dim。
  return dockAnim(ROW_TRASH, -3, beatIndex === 2);
}

function rlState(beatIndex) {
  if (beatIndex < 2)  return hiddenAnim();
  if (beatIndex === 2) return showcaseAnim(0);
  // beat ≥ 3: dock 在 夯；不會 dim (table 此時 crisp)。
  return dockAnim(ROW_HANG, 3, false);
}

export default function Ch4Step2() {
  const { beatIndex } = usePresentationContext();

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div style={{
        position: 'relative',
        width: TABLE_W,
        height: TABLE_H,
      }}>
        {/* Tier table — 用 motion.div 包，opacity + blur 由 tableState 控 */}
        <motion.div
          initial={{ opacity: 0, filter: 'blur(0px)' }}
          animate={tableState(beatIndex)}
          transition={TABLE_TR}
          style={{
            position: 'absolute', inset: 0,
            border: '6px solid #000',
            boxShadow: '14px 14px 0 0 #000',
            background: '#000',
          }}
        >
          {TIERS.map((t, i) => (
            <div key={t.key} style={{
              display: 'flex',
              height: ROW_H,
              borderTop: i === 0 ? 'none' : `${DIVIDER}px solid #000`,
              background: '#D0D0D0',
            }}>
              <div style={{
                width: LABEL_W,
                background: t.bg,
                borderRight: `${DIVIDER}px solid #000`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 900,
                fontSize: t.key === 'NPC' ? 56 : 64,
                color: '#000',
                letterSpacing: t.key === 'NPC' ? 0 : 2,
              }}>
                {t.key}
              </div>
              <div style={{ width: SLOT_W }} />
            </div>
          ))}
        </motion.div>

        {/* supervised — beat 0 showcase、beat 1+ dock 在 拉完了 (beat 2 dim) */}
        <motion.div
          initial={hiddenAnim()}
          animate={supervisedState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 10 }}
        >
          supervised
        </motion.div>

        {/* RL 增強式訓練 — beat<2 hidden、beat 2 showcase、beat 3+ dock 在 夯 */}
        <motion.div
          initial={hiddenAnim()}
          animate={rlState(beatIndex)}
          transition={STICKER_TR}
          style={{ ...STICKER_BASE, zIndex: 11 }}
        >
          RL 增強式訓練
        </motion.div>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: vite build clean check**

```bash
cd demo/presentation && npm run build
```

Expected: `✓ built in <時間>`、無 warning 也無 error。

- [ ] **Step 3: 跑現有 vitest suite**

```bash
cd demo/presentation && npm run test:run
```

Expected: 全綠。特別注意 `usePresentation.test.js` 的 `reports totalBeats = 93` 仍 pass (本 plan 不改 manifest，這個 assertion 不該動)。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx
git commit -m "refactor(ch4-step2): showcase→dock sticker animation w/ tier list dim"
```

---

## Task 2: 視覺 smoke (人工或 Playwright)

純驗證、不寫 code。

**Files:** 無

- [ ] **Step 1: 啟動 dev server**

```bash
cd demo/presentation && npm run dev
```

(此 step 需要使用者授權 — 若 auto-mode 擋下，請 user 自己跑。)

- [ ] **Step 2: 對每個 beat 截圖驗證**

開瀏覽器到 `http://localhost:5173/?chapter=4&step=2&beat=0`，逐步按方向鍵 / 滑鼠右鍵推進，確認：

| Beat | 預期視覺 |
|------|----------|
| 0 | tier list 不可見 (opacity 0)；supervised sticker 大尺寸 (scale 1.8) 在 table 中軸位置 |
| 1 | tier list 從透明 → 完全實化；supervised 同時縮回 scale 1、滑到 拉完了 row 左側 dock (label 邊框 右側 + 16 px inset)、−3° tilt |
| 2 | tier list dim 到 opacity 0.35 + blur 3px；supervised 也 dim (parked 跟 table 同步)；RL 增強式訓練 大尺寸 (scale 1.8) 在 table 中央 crisp |
| 3 | tier list 回 opacity 1 / blur 0；supervised 回 crisp；RL 縮小滑到 夯 row 左側 dock、+3° tilt |

兩張 sticker dock 後都不擋到 label 右邊框 (因為靠 `LABEL_W + DIVIDER + 16 px` 對齊)。

- [ ] **Step 3: 退回 beat (左鍵) 確認動畫可逆**

從 beat 3 一路退回 beat 0，每個 state 視覺應跟 forward 路徑對稱 — 因為 motion.div 都是純 `animate` prop 跟 beatIndex 對應、不會有 hysteresis。

- [ ] **Step 4: (no commit — 本 task 純驗證)**

若視覺有偏差，回到 Task 1 對應步驟修正、重 commit。

---

## Self-Review 紀錄

寫完後對照 spec 跑過：

1. **Spec coverage:** spec 中每個 row (beat 0/1/2/3 行為、dock 位置定義、showcase 位置定義、dim 模式、approach A 採用) 都對應到 Task 1 的某段 code (tableState / supervisedState / rlState / showcaseAnim / dockAnim / hiddenAnim / STICKER_BASE.transformOrigin)。對齊。
2. **Placeholder scan:** 無 TODO/TBD/placeholder。code 區塊完整。
3. **Type consistency:** function 名 (`tableState` / `supervisedState` / `rlState` / `showcaseAnim` / `dockAnim` / `hiddenAnim` / `rowCenterY`) 全檔一致。常數 (`SHOWCASE_SCALE` / `DOCK_INSET` / `ROW_HANG` / `ROW_TRASH` / `DIVIDER`) 全檔一致。
4. **Risks 確認:** spec 列的三個 risk (showcase 超出容器、filter blur 卡頓、dock 寬度計算) 都在 design 階段已釋疑、不需要在 plan 額外處理。
