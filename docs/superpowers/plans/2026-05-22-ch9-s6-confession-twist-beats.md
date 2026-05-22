# ch9 s6 「告白成功 → 殊不知更多關卡」3-beat 重構 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 [Ch9Step6.jsx](../../../demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx) 從單一 auto-play 動畫重構成 3-click-beat 結構（告白成功 → pivot → 4 卡雨），呼應 [demo/script_new.md](../../../demo/script_new.md) L359 的「喜 → 預感 → 傻眼」mini-arc。

**Architecture:** 先用 TDD 改 `beat-manifest.js`（state 端唯一可自動驗證的層）；然後重寫 `Ch9Step6.jsx`，先把骨架 gate by `beatIndex` 讓既有元素（老油條 / 標題 / 4 卡）延後出現，再依序加入新內容（奶茶 + sticker + 💗 → sticker dim/grayscale → 奶茶 question variant + ❓ + climax B）。每個 beat 的視覺內容用 dev server 人工驗證。

**Tech Stack:** Vite + React + motion/react + vitest（測試）。沒有新增 npm 依賴，沒有新增 AI 素材。

**Spec reference:** [docs/superpowers/specs/2026-05-22-ch9-s6-confession-twist-beats-design.md](../specs/2026-05-22-ch9-s6-confession-twist-beats-design.md)

---

## Task 1: Beat manifest 3-beat 化 + state-level tests (TDD)

**Files:**
- Modify: `demo/presentation/src/state/usePresentation.test.js`（更新 `totalBeats` 斷言、新增 ch9 s6 traversal 測試）
- Modify: `demo/presentation/src/data/beat-manifest.js:7`（`totalBeats: 99 → 101`）
- Modify: `demo/presentation/src/data/beat-manifest.js:183`（ch9 step 6 entry 改寫）

### Step 1.1: 寫失敗測試 — `totalBeats=101` + ch9 s6 3 beats traversal

- [ ] 修改 `demo/presentation/src/state/usePresentation.test.js`：把現有 `'reports totalBeats = 99'` 測試的 `99` 改成 `101`，並在它前面新增一個 ch9 s6 traversal 測試。

把 `usePresentation.test.js` line 100-103 的測試：

```js
  it('reports totalBeats = 99', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(99);
  });
```

替換為：

```js
  it('ch9 step 6 has 3 beats then crosses to step 7', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 9, stepId: 6 }));
    expect(result.current.beatIndex).toBe(0);
    for (let i = 1; i <= 2; i++) {
      act(() => result.current.advance());
      expect(result.current.stepId).toBe(6);
      expect(result.current.beatIndex).toBe(i);
    }
    act(() => result.current.advance());      // 第 3 個 beat 後跨到 step 7
    expect(result.current.chapterId).toBe(9);
    expect(result.current.stepId).toBe(7);
    expect(result.current.beatIndex).toBe(0);
  });

  it('reports totalBeats = 101', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(101);
  });
```

### Step 1.2: 跑測試確認失敗

執行：
```
npm --prefix demo/presentation run test:run -- usePresentation.test
```

預期：
- `ch9 step 6 has 3 beats then crosses to step 7` FAIL（目前只有 1 beat，第 1 次 advance 就跨到 step 7）
- `reports totalBeats = 101` FAIL（目前 99）

### Step 1.3: 更新 beat-manifest.js — `totalBeats` 與 ch9 step 6 entries

- [ ] 修改 `demo/presentation/src/data/beat-manifest.js` line 7：把 `totalBeats: 99` 改成 `totalBeats: 101`。
- [ ] 修改 `demo/presentation/src/data/beat-manifest.js` line 183（ch9 / step 6 那一筆），把：

```js
        { id: 6, title: '戀愛 b 4 考題',        duration: 18, motifs: ['girl-veteran'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L333-343' }] },
```

替換為：

```js
        { id: 6, title: '戀愛 b 4 考題',        duration: 18, motifs: ['girl-veteran', 'milk-tea'],
          beats: [
            { id: 'confess-success', type: 'click', cue: '最後奶茶終於成功跟對方告白成功——', wait: '0.8-1.2s 慶祝感', scriptLines: 'L359' },
            { id: 'twist-veteran',   type: 'click', cue: '結果殊不知——',                       wait: '1-1.5s 留懸念',  scriptLines: 'L359' },
            { id: 'traps-rain',      type: 'click', cue: '前面還有更多關卡等著奶茶',           wait: '2-3s 觀眾消化',  climax: ['B'], scriptLines: 'L359' },
          ],
        },
```

### Step 1.4: 跑測試確認通過

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全部測試綠（含新的 ch9 s6 3-beats traversal + `totalBeats=101`）。

### Step 1.5: Commit

```
git add demo/presentation/src/data/beat-manifest.js demo/presentation/src/state/usePresentation.test.js
git commit -m "feat(ch9-s6): expand manifest to 3 beats (confess-success / twist-veteran / traps-rain)"
```

---

## Task 2: Ch9Step6 骨架重構 — 既有元素 gate by `beatIndex`

**目的：** 在加新內容之前，先把現有 4 卡 + 老油條 + 標題用 `beatIndex` gating 起來，這樣 beat 0 / beat 1 點擊時畫面差異可以肉眼看到。新內容（奶茶 / sticker / 💗 / ❓ / climax B）留到後面 task 處理。

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`（整檔改寫）

### Step 2.1: 整檔改寫 Ch9Step6.jsx（骨架版）

- [ ] 將 `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx` 整檔替換為：

```jsx
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { GirlVeteran } from '../../motifs/GirlVeteran.jsx';

const QUESTIONS = [
  { text: '前女友跟我比 · 誰比較好？', bg: '#FFD93D', color: '#000', rotate: -2 },
  { text: '你心中的女神是誰？', bg: '#C4B5FD', color: '#000', rotate: 3 },
  { text: '你喜歡我哪裡？', bg: '#FF6B6B', color: '#FFFDF5', rotate: -3 },
  { text: '猜猜看 · 今天我哪裡不一樣？', bg: '#FFFDF5', color: '#000', rotate: 2 },
];

const OVERSHOOT = [0.34, 1.56, 0.64, 1];

export default function Ch9Step6() {
  const { beatIndex } = usePresentationContext();

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      {/* 標題 — beat>=1 clip-path 從左刷出 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { clipPath: 'inset(-24px)', opacity: 1 }
          : { clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        transition={{ duration: 0.8 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        以為穩了 · <span style={{ background: '#FF6B6B', color: '#FFF', padding: '4px 16px' }}>結果更多關卡等著奶茶</span>
      </motion.div>

      {/* 老油條 — beat>=1 從右上 spring-in */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { scale: 1, opacity: 1, rotate: 4 }
          : { scale: 0, opacity: 0, rotate: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: OVERSHOOT }}
        style={{ position: 'absolute', top: 48, right: 48, zIndex: 15 }}
      >
        <GirlVeteran width={200} rotation={0} shadow={10} />
      </motion.div>

      {/* 4 張陷阱題卡 — beat>=2 cascade */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 32 }}>
        {QUESTIONS.map((q, i) => (
          <motion.div
            key={i}
            initial={false}
            animate={beatIndex >= 2
              ? { scale: 1, opacity: 1, rotate: q.rotate, transition: { duration: 0.4, delay: 0.05 + i * 0.15, ease: OVERSHOOT } }
              : { scale: 0, opacity: 0, rotate: q.rotate }}
            whileHover={{
              scale: 1.1,
              rotate: q.rotate,
              boxShadow: '16px 16px 0 0 #000',
              transition: { duration: 0.2, ease: 'easeOut' },
            }}
            style={{
              background: q.bg, color: q.color,
              padding: '28px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', maxWidth: 360,
              cursor: 'pointer',
            }}
          >
            {q.text}
          </motion.div>
        ))}
      </div>
    </main>
  );
}
```

### Step 2.2: 跑全部測試確認沒回歸

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠（task 1 加的測試 + 既有 92 個測試）。

### Step 2.3: dev server 人工驗證（骨架）

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0` →
- 預期 beat 0：**空白**（畫面只有背景，老油條/標題/4 卡都未現）
- 按一次空白鍵或滑鼠點擊 → beat 1：老油條從右上滑入、標題從左刷出
- 再按一次 → beat 2：4 張陷阱題卡 cascade 落定
- 倒退（左方向鍵）可逆

Ctrl+C 關 dev server。

### Step 2.4: Commit

```
git add demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx
git commit -m "refactor(ch9-s6): gate existing elements behind beatIndex (skeleton for 3-beat structure)"
```

---

## Task 3: Beat 0 — 奶茶 + 「告白成功 ✓」brutalist sticker

**目的：** 把 beat 0 從「空白」改成「奶茶 + 黃色告白成功貼紙」的完整慶祝畫面。

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`

### Step 3.1: 加入 MilkTea import

- [ ] 在 `Ch9Step6.jsx` 頂部 import 區塊加入：

```jsx
import { MilkTea } from '../../motifs/MilkTea.jsx';
```

### Step 3.2: 加入奶茶元件（中下方 spring-in，beat>=0 入場）

**重要：** motion/react 的 `animate.scale/opacity` 會編譯成 `transform` 並覆蓋 `style.transform`。所以絕對置中要用**外層 wrapper div** 處理 `translateX(-50%)`，內層 motion.div 只負責 scale/opacity 動畫。

- [ ] 在 `<main>` 內、**標題 motion.div 之前**插入：

```jsx
      {/* 奶茶 — beat>=0 入場，beat>=2 切到 question variant + 浮動 ❓（後續 task 補） */}
      {/* Wrapper handles absolute centering — motion's transform animation would clobber translateX(-50%) */}
      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', zIndex: 15 }}>
        <motion.div
          initial={false}
          animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{ position: 'relative' }}
        >
          <MilkTea width={200} rotation={-3} shadow={10} variant="normal" />
        </motion.div>
      </div>
```

### Step 3.3: 加入「告白成功 ✓」brutalist sticker（奶茶頭上方）

- [ ] 在剛才插入的奶茶 wrapper div **下方**緊接著插入：

```jsx
      {/* 告白成功 ✓ sticker — beat>=0 入場，beat>=1 變灰淡出（下一個 task 補） */}
      {/* Wrapper handles centering; motion controls scale/opacity/rotate */}
      <div style={{ position: 'absolute', left: '50%', bottom: 280, transform: 'translateX(-50%)', zIndex: 14 }}>
        <motion.div
          initial={false}
          animate={beatIndex >= 0
            ? { scale: 1, opacity: 1, rotate: -8 }
            : { scale: 0, opacity: 0, rotate: 0 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            fontWeight: 900, fontSize: 28,
            whiteSpace: 'nowrap',
          }}
        >
          告白成功 ✓
        </motion.div>
      </div>
```

### Step 3.4: dev server 人工驗證

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0` →
- 預期 beat 0：奶茶從下方 spring-in、黃色「告白成功 ✓」貼紙在他頭上方
- 按一次 → beat 1：老油條 + 標題出現，奶茶與貼紙仍在原位（**注意：此 task 還沒把貼紙變灰，那是 Task 5**）
- 按一次 → beat 2：4 卡雨

Ctrl+C 關 dev server。

### Step 3.5: 跑測試確認沒回歸

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠。

### Step 3.6: Commit

```
git add demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx
git commit -m "feat(ch9-s6): add 奶茶 + 「告白成功 ✓」brutalist sticker on beat 0"
```

---

## Task 4: Beat 0 — 💗 hearts 粒子系統

**目的：** 在 beat 0 周期性生成 💗 從奶茶兩側浮起，beat>=1 時停止生成（舊粒子讓動畫自然淡出）。

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`

### Step 4.1: 加入 React hooks import

- [ ] 在 `Ch9Step6.jsx` 第一行 `import { motion } from 'motion/react';` **上方**加入：

```jsx
import { useEffect, useState } from 'react';
```

### Step 4.2: 在 component 內加入 hearts state 與 interval effect

- [ ] 在 `export default function Ch9Step6() {` 那行之後、`return (` 之前插入：

```jsx
  const [hearts, setHearts] = useState([]);

  useEffect(() => {
    if (beatIndex === 0) {
      let id = 0;
      const t = setInterval(() => {
        setHearts(h => [...h, { id: id++, x: Math.random() * 80 - 40 }].slice(-3));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);
```

說明：
- 粒子最多保留 3 顆（`slice(-3)`），符合 spec section 3 的「lightweight」路線。
- `x` 是水平偏移 ±40px（相對奶茶中線），給每顆 💗 一點點隨機分散感。
- `beatIndex !== 0` 時 effect cleanup 自動清掉 interval（React 機制），舊粒子留在陣列裡讓既存 motion 動畫自然走完。

### Step 4.3: render 💗 粒子（緊接在 sticker wrapper 之後）

**重要：** 同樣的 motion-transform 衝突問題 — 粒子的 `y` 動畫會編譯成 transform 並覆蓋 `translateX(-50%)`。用 wrapper div 處理水平定位。

- [ ] 在 Task 3 加的「告白成功 ✓」 sticker wrapper div **下方**插入：

```jsx
      {/* 💗 粒子 — beat 0 啟動，beat>=1 停止生成（舊粒子讓動畫自然淡出） */}
      {hearts.map(h => (
        <div
          key={h.id}
          style={{
            position: 'absolute',
            left: `calc(50% + ${h.x}px)`, bottom: 240,
            transform: 'translateX(-50%)',
            pointerEvents: 'none', zIndex: 13,
          }}
        >
          <motion.div
            initial={{ y: 0, opacity: 1 }}
            animate={{ y: -180, opacity: 0 }}
            transition={{ duration: 2.0, ease: 'easeOut' }}
            style={{ fontSize: 36 }}
          >
            💗
          </motion.div>
        </div>
      ))}
```

### Step 4.4: dev server 人工驗證

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0` →
- 預期 beat 0：奶茶 + 貼紙 + 持續有 💗 從奶茶兩側浮起淡出（最多同時 3 顆）
- 按一次 → beat 1：💗 停止生成、最後幾顆走完動畫後消失；老油條 + 標題出現
- 按一次 → beat 2：4 卡雨

Ctrl+C 關 dev server。

### Step 4.5: 跑測試 + commit

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠。

```
git add demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx
git commit -m "feat(ch9-s6): add 💗 hearts particle system on beat 0 (3-cap, 2s float-up)"
```

---

## Task 5: Beat 1 — 「告白成功 ✓」 sticker dim + grayscale 過渡

**目的：** beat>=1 時讓 sticker 變灰 + opacity 0.4（被陰影籠罩的感覺），呼應稿子「殊不知」的 pivot。

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`

### Step 5.1: 改 sticker 的 animate 邏輯 + grayscale filter

- [ ] 找到 Task 3 加的「告白成功 ✓」 sticker（外層 wrapper div 包著 motion.div），把整段 wrapper + motion.div 替換為：

```jsx
      {/* 告白成功 ✓ sticker — beat>=0 入場，beat>=1 變灰 + opacity 0.4 */}
      <div style={{ position: 'absolute', left: '50%', bottom: 280, transform: 'translateX(-50%)', zIndex: 14 }}>
        <motion.div
          initial={false}
          animate={beatIndex >= 0
            ? beatIndex >= 1
              ? { scale: 1, opacity: 0.4, rotate: -8 }
              : { scale: 1, opacity: 1, rotate: -8 }
            : { scale: 0, opacity: 0, rotate: 0 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            fontWeight: 900, fontSize: 28,
            whiteSpace: 'nowrap',
            filter: beatIndex >= 1 ? 'grayscale(1)' : 'none',
            transition: 'filter 0.4s ease',
          }}
        >
          告白成功 ✓
        </motion.div>
      </div>
```

說明：
- `animate.opacity` 由 motion/react 控制（0.4s ease overshoot）
- `style.filter` 的 `grayscale(1)` 用 CSS native transition（0.4s ease）— motion/react 不支援動畫 filter，所以用 CSS transition 補足
- wrapper div 維持 `translateX(-50%)` 不受 motion transform 動畫影響

### Step 5.2: dev server 人工驗證

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0` →
- 預期 beat 0：黃色 sticker 鮮豔
- 按一次 → beat 1：sticker 在 0.4s 內由黃變灰、opacity 從 1 降到 0.4（被陰影感覺）
- 倒退（左方向鍵）→ beat 0：sticker 在 0.4s 內由灰變回黃、opacity 1

Ctrl+C 關 dev server。

### Step 5.3: 跑測試 + commit

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠。

```
git add demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx
git commit -m "feat(ch9-s6): sticker dim + grayscale transition on beat>=1"
```

---

## Task 6: Beat 2 — 奶茶 question variant + 浮動 ❓ + climax B + screen shake

**目的：** beat 2 時奶茶從 normal 切到 question variant（傻眼版）、頭頂浮動 ❓、觸發一次 climax B + triggerShake（同 Ch7Step7 收尾 pattern）。

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`

### Step 6.1: import `useRef` + `useClimax`

- [ ] 把 `import { useEffect, useState } from 'react';` 改成：

```jsx
import { useEffect, useRef, useState } from 'react';
```

- [ ] 在 `import { usePresentationContext } ...` 之後加入：

```jsx
import { useClimax } from '../../climax/useClimax.js';
```

### Step 6.2: 在 component 內加入 climax 與 firedRef hooks

- [ ] 把 `const { beatIndex } = usePresentationContext();` 改成：

```jsx
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['B']);
  const firedRef = useRef(false);
```

### Step 6.3: 加入 beat 2 fire-once effect

- [ ] 在現有 hearts `useEffect` **之後**插入：

```jsx
  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
    }
  }, [beatIndex, climax, triggerShake]);
```

### Step 6.4: 奶茶切到 `variant` dynamic + 加浮動 ❓

- [ ] 找到 Task 3 加的奶茶（外層 wrapper div 包著 motion.div + `<MilkTea ... variant="normal" />`），把整段 wrapper + motion.div 替換為：

```jsx
      {/* 奶茶 — beat>=0 入場，beat>=2 切到 question variant + 浮動 ❓ */}
      <div style={{ position: 'absolute', left: '50%', bottom: 60, transform: 'translateX(-50%)', zIndex: 15 }}>
        <motion.div
          initial={false}
          animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{ position: 'relative' }}
        >
          <MilkTea width={200} rotation={-3} shadow={10} variant={beatIndex >= 2 ? 'question' : 'normal'} />

          {/* 浮動 ❓ — beat>=2，沿用 Ch7Step7 寫法。父層 motion.div 是 position:relative，這裡 absolute 會 anchor 到奶茶圖 */}
          {beatIndex >= 2 && [0, 1].map(i => (
            <motion.div
              key={i}
              initial={false}
              animate={{ y: [0, -70], opacity: [0, 1, 1, 0], scale: [0.5, 1, 1, 1] }}
              transition={{ duration: 1.6, repeat: Infinity, repeatType: 'loop', delay: i * 0.3, ease: 'easeOut' }}
              style={{
                position: 'absolute', top: -20, left: 60 + i * 50,
                fontSize: 40, fontWeight: 900, color: '#FF3B30',
                WebkitTextStroke: '2px #000', pointerEvents: 'none', zIndex: 16,
              }}
            >
              ?
            </motion.div>
          ))}
        </motion.div>
      </div>
```

### Step 6.5: dev server 人工驗證

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0` →
- 預期 beat 0：奶茶 normal + 貼紙 + 💗
- 按一次 → beat 1：sticker 變灰、💗 停、老油條 + 標題出現、奶茶仍是 normal
- 按一次 → beat 2：奶茶**切到傻眼版**（picture 換成 milk-tea-question.png）、頭頂兩個 ? 循環浮起、**螢幕震動一次**（climax B + triggerShake）、4 卡 cascade 落定
- 倒退（左方向鍵）→ beat 1：奶茶切回 normal、? 消失（climax 與 shake 已經放完，不會倒著放，這是設計上接受的）

Ctrl+C 關 dev server。

### Step 6.6: 跑測試 + commit

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠。

```
git add demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx
git commit -m "feat(ch9-s6): beat 2 — 奶茶 question variant + 浮動 ❓ + climax B + screen shake"
```

---

## Task 7: 最終整合驗證

**Files:** 只跑驗證指令，不改檔。

### Step 7.1: 跑全部測試

執行：
```
npm --prefix demo/presentation run test:run
```

預期：全綠（包含 task 1 新增的 ch9 s6 3-beats traversal 測試 + `totalBeats=101`）。

### Step 7.2: 跑 production build

執行：
```
npm --prefix demo/presentation run build
```

預期：build 成功、沒有 React/Vite 警告或錯誤。

### Step 7.3: dev server 完整 e2e 走演

執行：
```
npm --prefix demo/presentation run dev
```

開瀏覽器 `?ch=9&step=6&beat=0`，按照下表 click-walk：

| Step | 動作 | 預期畫面 |
|---|---|---|
| 1 | 進入 beat 0 | 奶茶（normal）+ 「告白成功 ✓」 貼紙（黃、鮮豔）+ 💗 持續從兩側升起淡出（最多 3 顆同時）。背景乾淨，無老油條、無標題、無 4 卡。 |
| 2 | 點擊（→ beat 1）| 老油條從右上 spring-in。標題從左 clip-path 刷出「以為穩了 · 結果更多關卡等著奶茶」（紅底反白只在後半段）。貼紙在 0.4s 內變灰 + opacity 0.4。💗 停止生成（最後幾顆走完淡出後消失）。 |
| 3 | 點擊（→ beat 2）| 4 張陷阱題卡依序 cascade 落定（每張 0.15s stagger，overshoot ease）。奶茶**切到傻眼版**（圖換）、頭頂 2 個 ? 循環浮起。**螢幕震動一次**（climax B + triggerShake，~600ms）。 |
| 4 | 倒退（← 方向鍵） | 回 beat 1：4 卡縮回消失、奶茶切回 normal、? 消失。climax 與 shake 不會倒放（一次性，設計上接受）。 |
| 5 | 倒退（← 方向鍵） | 回 beat 0：老油條縮回、標題收回左邊、貼紙變回鮮豔黃、💗 重新開始生成。 |
| 6 | 倒退 | 跨回 step 5 beat 末（Ch9Step5）。 |
| 7 | 從 step 1 一路點到底 | 全片總共 101 個 beat（task 1 manifest 更新後），游標前進到底不卡、不錯位。 |

Ctrl+C 關 dev server。

### Step 7.4: 完成 — 不做新 commit（task 7 純驗證）

如果 step 7.1-7.3 都過，這個 plan 就完成。如果發現視覺微調需求（例如 💗 位置太靠近 / sticker 位置擋到奶茶臉），開新的小修補 commit。

---

## 自我審閱備註（spec coverage check）

- ✅ Spec section 2 beat 表：Task 1 寫進 manifest、Task 3-6 實作對應視覺
- ✅ Spec section 3 機制改動全部分到 Task 2-6
- ✅ Spec section 4 受影響檔案三個都列在對應 task 的 Files
- ✅ Spec section 6 驗收標準：Task 7 step 7.3 走完全部
- ✅ totalBeats 99→101：Task 1.3 / 1.4
- ✅ 不做（YAGNI）section：plan 沒有偷加新女生 / 新 motif / 新素材 / beat 0/1 climax
