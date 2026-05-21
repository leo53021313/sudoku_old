# ch4 step2 — caption beats + impact 動畫強化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在現有 ch4 step2 排行榜 step 插入兩個 caption beat（❌ / ✓），並追加三組動畫強化（A impact landing、B caption stamp polish、C showcase idle wobble），讓視覺節奏更有衝擊力。

**Architecture:** 在既有 motion-driven state machine 上加碼：(1) manifest 4→6 beats、(2) Ch4Step2.jsx state 函式 boundary 重新調整、(3) 新增 caption motion blocks、(4) 借用既有 motif `ImpactDust` / `StarburstShards` 透過 wrapper 定位到 dock 落點、(5) `triggerShake()` 在 dock + ❌ caption 進場時觸發、(6) `showcaseAnim` 的 `rotate` 改成 keyframe array 配 per-property `transition` 跑無限 mirror loop。

**Tech Stack:** React 19, Framer Motion (`motion@12`).

**Spec reference:** [docs/superpowers/specs/2026-05-21-ch4-step2-caption-and-impact-design.md](../specs/2026-05-21-ch4-step2-caption-and-impact-design.md)

---

## File Structure

- **Modify:** `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx` (主要)
- **Modify:** `demo/presentation/src/data/beat-manifest.js` (ch4 step2 beats、totalBeats)
- **Modify:** `demo/presentation/src/state/usePresentation.test.js` (totalBeats assertion)

No new files. No new motif primitives. Tests follow deck convention (step-level component 無單元測試)；驗證 = `vite build` clean + `npm run test:run` (39+ tests pass) + 手動 / Playwright 視覺 smoke。

---

## Task 1: Beat semantics expansion (4 → 6 beats)

擴 manifest、test、Ch4Step2 state 函式邊界。此 task 結束時新 beats 1/4 還沒有 caption（畫面上只是 showcase 多延一拍），dock/dim 已對齊新 boundary。

**Files:**
- Modify: `demo/presentation/src/data/beat-manifest.js` (ch4 step2 beats 陣列、totalBeats)
- Modify: `demo/presentation/src/state/usePresentation.test.js` (totalBeats assertion)
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx` (tableState、supervisedState、rlState)

- [ ] **Step 1: 改 manifest**

於 `demo/presentation/src/data/beat-manifest.js`，把 ch4 step2 的整段 step 物件取代為以下（duration 16→24、beats 從 4 個變 6 個）：

```js
        { id: 2, title: 'supervised vs RL tier list', duration: 24, motifs: ['tier-list'],
          beats: [
            { id: 'supervised-enter', type: 'click', cue: 'supervised 路線 ——',                       wait: null,           scriptLines: 'L105-107' },
            { id: 'supervised-cross', type: 'click', cue: '❌ 我不想要 AI 背答案',                      wait: '1-2s',         scriptLines: 'L105-107' },
            { id: 'supervised-trash', type: 'click', cue: '拉完了',                                     wait: '1-1.5s 笑點',  scriptLines: 'L105-107' },
            { id: 'rl-enter',         type: 'click', cue: '再看看我這套 RL 增強式訓練 ——',                 wait: null,           scriptLines: 'L105-107' },
            { id: 'rl-check',         type: 'click', cue: '✓ 讓 AI 從零自己學習規則',                     wait: '1-2s',         scriptLines: 'L105-107' },
            { id: 'rl-hang',          type: 'click', cue: '夯',                                         wait: '1-2s 笑點',    scriptLines: 'L105-107' },
          ],
        },
```

同檔案頂部 `totalBeats: 93` 改成 `totalBeats: 95`。

- [ ] **Step 2: 改 usePresentation 測試**

`demo/presentation/src/state/usePresentation.test.js`：

```js
  it('reports totalBeats = 95', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(95);
  });
```

(把 `= 93` 換成 `= 95`、字串跟數字都改。)

- [ ] **Step 3: 改 Ch4Step2 state 函式邊界**

`demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`，找到三個函式 `tableState`、`supervisedState`、`rlState`，替換為以下版本（新增 caption beat 視為「showcase 延長」、dock 跟 dim 的 boundary 後推一位）：

```js
function tableState(beatIndex) {
  if (beatIndex <= 1) return { opacity: 0,    filter: 'blur(0px)' };
  if (beatIndex === 3 || beatIndex === 4) return { opacity: 0.35, filter: 'blur(3px)' };
  return { opacity: 1, filter: 'blur(0px)' };
}

function supervisedState(beatIndex) {
  if (beatIndex < 2) return showcaseAnim(0);
  // beat ≥ 2: dock 拉完了；dim 在 RL showcase 區段 (beat 3-4)
  return dockAnim(ROW_TRASH, -3, beatIndex === 3 || beatIndex === 4);
}

function rlState(beatIndex) {
  if (beatIndex < 3) return hiddenAnim();
  if (beatIndex < 5) return showcaseAnim(0);
  // beat ≥ 5: dock 夯
  return dockAnim(ROW_HANG, 3, false);
}
```

- [ ] **Step 4: 驗證 build + test**

```bash
cd demo/presentation && npm run build
```
Expected: `✓ built in <time>`、無 warning。

```bash
cd demo/presentation && npm run test:run
```
Expected: 全綠（含新的 `totalBeats = 95`）。

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx demo/presentation/src/data/beat-manifest.js demo/presentation/src/state/usePresentation.test.js
git commit -m "feat(ch4-step2): expand to 6 beats with caption beat slots"
```

---

## Task 2: Caption components (❌ / ✓ stamp-in below showcase)

新增兩塊 caption motion block，beat 1 顯示 ❌「我不想要 AI 背答案」、beat 4 顯示 ✓「讓 AI 從零自己學習規則」。dock beat（2 / 5）時 caption 自動 fade out。

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`

- [ ] **Step 1: 新增 caption 動畫常數**

在 `STICKER_TR` 跟 `TABLE_TR` 下方加：

```js
const CAPTION_TR = { duration: 0.45, ease: OVERSHOOT };          // 整塊 caption 進出
const CAPTION_TEXT_TR = { duration: 0.35, ease: 'easeOut' };     // 下方文字 fade-up

const CAPTION_TOP_OFFSET = 170;  // sticker 下方 ~170 px (避開 hard shadow + scale 1.8 邊緣)
```

- [ ] **Step 2: 新增 caption 區塊 JSX**

在 RL motion.div（zIndex 11 的那個）關閉 tag `</motion.div>` 之後、外層 `<div>` 容器關閉之前，插入：

```jsx
        {/* supervised ❌ caption — beat 1 stamp-in、beat 其它 hidden */}
        <motion.div
          initial={false}
          animate={{
            opacity: beatIndex === 1 ? 1 : 0,
            top: TABLE_H / 2 + CAPTION_TOP_OFFSET,
            left: TABLE_W / 2,
            x: '-50%',
          }}
          transition={CAPTION_TR}
          style={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 14,
            pointerEvents: 'none',
            zIndex: 12,
          }}
        >
          <motion.div
            initial={false}
            animate={beatIndex === 1
              ? { scale: [0, 1.4, 1], rotate: [-8, 2, 0], opacity: 1 }
              : { scale: 0, rotate: 0, opacity: 0 }}
            transition={CAPTION_TR}
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: '#FF3B30',
              textShadow: '4px 4px 0 #000',
              lineHeight: 1,
            }}
          >
            ✕
          </motion.div>
          <motion.div
            initial={false}
            animate={beatIndex === 1 ? { y: 0, opacity: 1 } : { y: 12, opacity: 0 }}
            transition={{ ...CAPTION_TEXT_TR, delay: beatIndex === 1 ? 0.2 : 0 }}
            style={{
              background: '#000',
              color: '#FFFDF5',
              padding: '12px 28px',
              border: '4px solid #000',
              boxShadow: '6px 6px 0 0 #000',
              fontWeight: 900,
              fontSize: 30,
              whiteSpace: 'nowrap',
            }}
          >
            我不想要 AI 背答案
          </motion.div>
        </motion.div>

        {/* RL ✓ caption — beat 4 stamp-in、beat 其它 hidden */}
        <motion.div
          initial={false}
          animate={{
            opacity: beatIndex === 4 ? 1 : 0,
            top: TABLE_H / 2 + CAPTION_TOP_OFFSET,
            left: TABLE_W / 2,
            x: '-50%',
          }}
          transition={CAPTION_TR}
          style={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 14,
            pointerEvents: 'none',
            zIndex: 12,
          }}
        >
          <motion.div
            initial={false}
            animate={beatIndex === 4
              ? { scale: [0, 1.4, 1], rotate: [-8, 2, 0], opacity: 1 }
              : { scale: 0, rotate: 0, opacity: 0 }}
            transition={CAPTION_TR}
            style={{
              fontSize: 96,
              fontWeight: 900,
              color: '#06B26F',
              textShadow: '4px 4px 0 #000',
              lineHeight: 1,
            }}
          >
            ✓
          </motion.div>
          <motion.div
            initial={false}
            animate={beatIndex === 4 ? { y: 0, opacity: 1 } : { y: 12, opacity: 0 }}
            transition={{ ...CAPTION_TEXT_TR, delay: beatIndex === 4 ? 0.2 : 0 }}
            style={{
              background: '#000',
              color: '#FFFDF5',
              padding: '12px 28px',
              border: '4px solid #000',
              boxShadow: '6px 6px 0 0 #000',
              fontWeight: 900,
              fontSize: 30,
              whiteSpace: 'nowrap',
            }}
          >
            讓 AI 從零自己學習規則
          </motion.div>
        </motion.div>
```

注意：❌ 用 `✕` U+2715（重劃 X），跟瀏覽器內建 emoji 比較不會被 OS theming 干擾。也可直接用 `❌`，但有些字型會 render 成 emoji 樣式失去尖銳感 — 此 plan 用 `✕`。✓ 用 U+2713。

- [ ] **Step 3: 驗證 build + test**

```bash
cd demo/presentation && npm run build && npm run test:run
```
Expected: 全綠。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx
git commit -m "feat(ch4-step2): caption beats (cross / check) stamp-in below sticker"
```

---

## Task 3: Impact landing motifs (A — ImpactDust / StarburstShards / shake)

dock 著陸時觸發既有 motif + 全域 screen shake。supervised → 拉完了 觸發 `ImpactDust`，RL → 夯 觸發 `StarburstShards`，兩者都觸發 `triggerShake()`。

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`

- [ ] **Step 1: 新增 imports**

檔頂 import 區改成：

```js
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { ImpactDust } from '../../motifs/ImpactDust.jsx';
import { StarburstShards } from '../../motifs/StarburstShards.jsx';
```

- [ ] **Step 2: 在 Ch4Step2 元件內取得 triggerShake、加 firedRef**

`export default function Ch4Step2()` 第一行 `const { beatIndex } = usePresentationContext();` 改為：

```js
  const { beatIndex, triggerShake } = usePresentationContext();

  // 著陸 shake 只在進入 dock beat 的「上升緣」觸發一次，避免來回切 beat 重打。
  const shakeFiredRef = useRef({ supervised: false, rl: false });

  useEffect(() => {
    if (beatIndex === 2 && !shakeFiredRef.current.supervised) {
      shakeFiredRef.current.supervised = true;
      triggerShake();
    } else if (beatIndex !== 2) {
      shakeFiredRef.current.supervised = false;
    }
    if (beatIndex === 5 && !shakeFiredRef.current.rl) {
      shakeFiredRef.current.rl = true;
      triggerShake();
    } else if (beatIndex !== 5) {
      shakeFiredRef.current.rl = false;
    }
  }, [beatIndex, triggerShake]);
```

- [ ] **Step 3: 新增 motif wrapper JSX**

在 tier table 的 `</motion.div>` 之後、supervised sticker `<motion.div>` 之前，插入兩個 wrapper：

```jsx
        {/* ImpactDust — 拉完了 dock 著陸；wrapper 把 motif 內建的 (50%, 78%) 錨點移到 dock 中心 */}
        <div style={{
          position: 'absolute',
          left: LABEL_W + DIVIDER + DOCK_INSET + 60,  // sticker 視覺中心 ≈ left edge + 60
          top: rowCenterY(ROW_TRASH) - 78,            // 78% of 100 = 78; offset 使 motif 中心對齊 row 中軸
          width: 200,
          height: 100,
          pointerEvents: 'none',
          zIndex: 5,
        }}>
          <ImpactDust active={beatIndex >= 2} />
        </div>

        {/* StarburstShards — 夯 dock 著陸；wrapper 把 motif 內建的 (50%, 50%) 錨點移到 dock 中心 */}
        <div style={{
          position: 'absolute',
          left: LABEL_W + DIVIDER + DOCK_INSET + 60,
          top: rowCenterY(ROW_HANG) - 50,
          width: 200,
          height: 100,
          pointerEvents: 'none',
          zIndex: 5,
        }}>
          <StarburstShards active={beatIndex >= 5} />
        </div>
```

注意 zIndex 5：星爆 / 塵爆在 sticker（zIndex 10、11）之下，避免遮文字。

- [ ] **Step 4: 驗證 build + test**

```bash
cd demo/presentation && npm run build && npm run test:run
```
Expected: 全綠。

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx
git commit -m "feat(ch4-step2): impact landing motifs (dust / starburst / shake) on dock"
```

---

## Task 4: Caption stamp polish (B — ❌ shake、✓ yellow flash)

❌ caption 進場 (beat 1) 觸發 light shake；✓ caption 進場 (beat 4) 後方鋪短促黃色 flash。

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`

- [ ] **Step 1: 擴 firedRef + useEffect 觸發 caption shake**

把 Task 3 加的 `useEffect` 整段擴成：

```js
  const shakeFiredRef = useRef({ supervised: false, rl: false, cross: false });

  useEffect(() => {
    if (beatIndex === 2 && !shakeFiredRef.current.supervised) {
      shakeFiredRef.current.supervised = true;
      triggerShake();
    } else if (beatIndex !== 2) {
      shakeFiredRef.current.supervised = false;
    }
    if (beatIndex === 5 && !shakeFiredRef.current.rl) {
      shakeFiredRef.current.rl = true;
      triggerShake();
    } else if (beatIndex !== 5) {
      shakeFiredRef.current.rl = false;
    }
    if (beatIndex === 1 && !shakeFiredRef.current.cross) {
      shakeFiredRef.current.cross = true;
      triggerShake();
    } else if (beatIndex !== 1) {
      shakeFiredRef.current.cross = false;
    }
  }, [beatIndex, triggerShake]);
```

(三個獨立 firedRef key，邏輯一致。)

- [ ] **Step 2: 在 ✓ caption 區塊內加 yellow flash 背景**

找到 RL ✓ caption 的最外層 motion.div（zIndex 12 那個），在它的開頭、`<motion.div ... 96px ✓>` 之前，插入：

```jsx
          {/* yellow flash — ✓ 進場時短促閃光，鋪在 caption 後方 */}
          <motion.div
            initial={false}
            animate={beatIndex === 4
              ? { opacity: [0, 0.55, 0], scale: [0.6, 1.4, 1.6] }
              : { opacity: 0, scale: 0.6 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            style={{
              position: 'absolute',
              left: '50%',
              top: 48,           // 對齊 ✓ 符號的視覺中心
              width: 220, height: 220,
              transform: 'translate(-50%, -50%)',
              borderRadius: '50%',
              background: 'radial-gradient(circle, #FFD93D 0%, rgba(255,217,61,0) 70%)',
              pointerEvents: 'none',
              zIndex: -1,
            }}
          />
```

注意 motion 元件 + CSS `transform: translate` 同時使用會被 motion 覆寫 — 改用 motion-style centering：把 `transform` 拿掉，加 `marginLeft: -110, marginTop: -110`（即 -width/2、-height/2）做靜態置中：

```jsx
            style={{
              position: 'absolute',
              left: '50%',
              top: 48,
              width: 220, height: 220,
              marginLeft: -110,
              marginTop: -110,
              borderRadius: '50%',
              background: 'radial-gradient(circle, #FFD93D 0%, rgba(255,217,61,0) 70%)',
              pointerEvents: 'none',
              zIndex: -1,
            }}
```

(用 `marginLeft/Top` negative 達成置中，不跟 motion transform 衝突。)

- [ ] **Step 3: 驗證 build + test**

```bash
cd demo/presentation && npm run build && npm run test:run
```
Expected: 全綠。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx
git commit -m "feat(ch4-step2): caption stamp polish (shake on cross, yellow flash on check)"
```

---

## Task 5: Showcase idle wobble (C)

showcase 大尺寸 sticker 在停留時做 ±1.5° infinite mirror 微擺。透過 `showcaseAnim` 回傳 `rotate` keyframe array + per-property `transition` 達成。

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`

- [ ] **Step 1: 改 showcaseAnim 回傳 rotate keyframe**

把 `showcaseAnim` 整段換成（rotate 改成陣列，但保留 caller 傳入的 baseline rotate）：

```js
// 「showcase 大」 — 置中 table 容器、scale 1.8、rotate 在 baseline ±1.5° 做 infinite mirror wobble。
// 用 transformOrigin: 'center center' 配 x:'-50%', y:'-50%' 達成水平垂直居中。
function showcaseAnim(rotate) {
  return {
    opacity: 1,
    scale: SHOWCASE_SCALE,
    top: TABLE_H / 2,
    left: TABLE_W / 2,
    x: '-50%',
    y: '-50%',
    rotate: [rotate - 1.5, rotate + 1.5, rotate - 1.5],
    filter: 'blur(0px)',
    transformOrigin: 'center center',
  };
}
```

- [ ] **Step 2: 加 per-property transition helper**

在 `STICKER_TR` 下方加：

```js
// showcase 階段 (sticker 是 showcase state) 才把 rotate transition 改成無限 mirror loop。
// dock / hidden state 用標準 STICKER_TR。
const wobbleRotateTR = { duration: 3, ease: 'easeInOut', repeat: Infinity, repeatType: 'mirror' };

function stickerTransition(isShowcase) {
  if (isShowcase) {
    return { ...STICKER_TR, rotate: wobbleRotateTR };
  }
  return STICKER_TR;
}
```

- [ ] **Step 3: 在 sticker motion.div 用新的 transition**

把 supervised 跟 RL sticker `<motion.div>` 的 `transition={STICKER_TR}` 換成下列（用 helper 計算 per-beat transition）：

supervised：
```jsx
          transition={stickerTransition(beatIndex < 2)}
```

RL：
```jsx
          transition={stickerTransition(beatIndex >= 3 && beatIndex < 5)}
```

(showcase boundary：supervised beat 0-1，RL beat 3-4。)

- [ ] **Step 4: 驗證 build + test**

```bash
cd demo/presentation && npm run build && npm run test:run
```
Expected: 全綠。

注意：Framer Motion 對 `rotate: [a, b, a]` keyframe + `repeat: Infinity` 組合是支援的（cf. `IPPool` rotation 在 Ch4Step4 有類似用法）。若視覺上有怪 transition jank（從 wobble keyframe 切到 dock 定值時 rotate 跳一下），fallback 是把 dock state 的 rotate 也設為單一 keyframe `[targetRotate]`，讓 motion 平順收尾。先不預先處理，等視覺 smoke 時再決定。

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx
git commit -m "feat(ch4-step2): showcase idle wobble (±1.5° infinite mirror)"
```

---

## Task 6: 視覺 smoke

純驗證、不寫 code。

**Files:** 無

- [ ] **Step 1: 啟動 dev server (需 user 授權)**

```bash
cd demo/presentation && npm run dev
```

- [ ] **Step 2: 對 6 個 beat 逐拍驗證**

開瀏覽器 `http://localhost:5173/?chapter=4&step=2&beat=0`，按方向鍵逐拍。

| Beat | 預期 |
|------|------|
| 0 | 排行榜隱形；supervised 大尺寸正中、微擺中 |
| 1 | supervised 維持大尺寸 + 下方 ❌ + 「我不想要 AI 背答案」stamp-in；ScreenShake 觸發 |
| 2 | 排行榜淡入實化；supervised 縮小 dock 拉完了；caption 消失；ImpactDust 黑色碎塊飛散；ScreenShake 觸發 |
| 3 | 排行榜虛化 (opacity 0.35 + blur)；supervised 跟著虛化；RL 大尺寸正中、微擺中 |
| 4 | RL 維持大尺寸 + 下方 ✓ + 「讓 AI 從零自己學習規則」stamp-in；後方黃色閃光；無 ScreenShake (✓ 只有 flash) |
| 5 | 排行榜實化；RL 縮小 dock 夯；StarburstShards 星形碎片彈出；ScreenShake 觸發 |

- [ ] **Step 3: 左鍵回放**

從 beat 5 退回 beat 0，確認反向動畫不破。特別注意：rotate keyframe → dock 定值的 transition 銜接、shake firedRef 在退 beat 後正確 reset (再進前 beat 又能重觸發)。

- [ ] **Step 4: (no commit — 純驗證)**

若視覺有偏差，回到對應 task 修正、重 commit。

---

## Self-Review 紀錄

對照 spec 跑過：

1. **Spec coverage:**
   - 改動 1 (4→6 beats、manifest+test 同步) → Task 1。✓
   - 改動 2 (Impact landing A) → Task 3。✓
   - 改動 3 (Caption stamp polish B) → Task 4。✓
   - 改動 4 (Showcase idle wobble C) → Task 5。✓
   - Caption 元件本身 → Task 2。✓
   - 已涵蓋。

2. **Placeholder scan:** 無 TODO/TBD。code block 完整。

3. **Type consistency:**
   - 函式名 `tableState` / `supervisedState` / `rlState` / `showcaseAnim` / `dockAnim` / `hiddenAnim` 跟 v1 一致。
   - 新增的 `stickerTransition(isShowcase)` 跟 `wobbleRotateTR` 命名清楚、Task 5 內部用法一致。
   - `shakeFiredRef.current` 三個 key (`supervised` / `rl` / `cross`) 在 Task 3+4 一致引用。
   - `CAPTION_TR` / `CAPTION_TEXT_TR` / `CAPTION_TOP_OFFSET` 命名一致。

4. **Spec deviation:** spec 提及 RL dock scale bounce (`[1, 1.15, 1]`)。本 plan 未實作 — 原因：keyframe array 從 showcase scale 1.8 切到 dock keyframe `[1, 1.15, 1]` 在 motion 內部 interpolation 行為不確定，且 dock 已有 StarburstShards + ScreenShake 提供衝擊感，bounce 屬於 marginal polish。**YAGNI**。若 Task 6 視覺 smoke 後仍想要 bounce、再開新 task。
