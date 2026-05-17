# Phase 8 · Chapter 8 (apprentice) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>` (parent provides), `<HubSatellite>` (hub + named-anchor satellites) and `<Sticker variant="hub-md|hub-lg|hub-mega|sat-lg|sat-md|sat-sm|kicker">` from `src/components/`. Inline `position: 'absolute'` + hard-coded `%` offsets are PROHIBITED in step files (motif components are exempt — `HalftoneBurst`, `InkSplatter`, `SpotlightVignette`, etc. continue to use viewport-relative positioning). JSX snippets in this plan that follow the hub+satellite or sticker pattern have been pre-translated; snippets for other layouts (split-screen, charts, etc.) are illustrative — translate them to primitive calls when executing. See [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) for tokens, variant table, and acceptance criteria.

**Goal:** Build ch8 apprentice — 反向思考 → 3 格空 → 反向課程動畫 3→10 → +20→+50 翻牌 → 光講不夠看 → visualizer 大按鈕. 6 steps, ~66s + visualizer 30~60s. First use of `motif/flip-20-to-50` (s4). No punchlines but ch8 is breakthrough chapter, ends with visualizer launch button using Windows custom URL scheme.

**Source spec:** [outline.md §8](../../../demo/outline.md) · script.md L273-L299

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch8
└── ch8-apprentice/
    ├── Ch8.jsx
    ├── Ch8Step1.jsx                        # 反向思考過渡
    ├── Ch8Step2.jsx                        # 3 格空盤面
    ├── Ch8Step3.jsx                        # 反向課程動畫 3→10
    ├── Ch8Step4.jsx                        # +20 → +50 翻牌 (first flip-20-to-50)
    ├── Ch8Step5.jsx                        # 光講不夠看
    └── Ch8Step6.jsx                        # visualizer 大按鈕
```

---

## Task 1: Register Ch8 + Step1 (反向思考過渡)

- [ ] Update `src/chapters/index.jsx` — `8: Ch8`

- [ ] Create `Ch8.jsx`:

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch8Step1 from './Ch8Step1.jsx';

const STEPS = { 1: Ch8Step1 };

export function Ch8() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 8 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

- [ ] Create `Ch8Step1.jsx` (black → cream fade-in + hero):

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch8Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', gap: 24,
    }}>
      {/* Fade-out black overlay (one-shot, mirrors ch7 s8's black → cream transition) */}
      <motion.div
        initial={{ opacity: 1 }}
        animate={{ opacity: 0 }}
        transition={{ duration: 1.2, ease: [0.4, 0.0, 0.2, 1] }}
        style={{
          position: 'fixed', inset: 0, zIndex: 60, background: '#000', pointerEvents: 'none',
        }}
      />

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.9, delay: 0.6, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        <Sticker variant="kicker" bg="#FF6B6B" color="#FFF">反向思考</Sticker>
        <br/>
        先解簡單的陷阱題答案
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        之後從容面對老油條
      </motion.div>

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.8 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 700, fontSize: 18, color: '#666',
        }}
      >
        AI 也是、我把題目反過來給他 →
      </motion.div>
    </div>
  );
}
```

- [ ] Build + commit: `feat(demo): ch8 register + s1 反向思考`

---

## Task 2: Ch8Step2 + Ch8Step3 (sudoku board + reverse curriculum animation)

### Ch8Step2 — 3 格空

```jsx
import { motion } from 'motion/react';

// 90% filled board, 3 empty cells highlighted
const BOARD = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,2, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];
const EMPTY_CELLS = [[1,3],[4,7],[7,2]];  // row, col positions to blank out

export default function Ch8Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '1.5rem', color: '#666' }}
      >
        他一定解得出來
      </motion.div>

      {/* 9x9 board */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)',
          gap: 0, width: 540, height: 540,
          border: '6px solid #000', background: '#000',
          boxShadow: '12px 12px 0 0 #000',
        }}
      >
        {BOARD.flatMap((row, r) =>
          row.map((val, c) => {
            const isEmpty = EMPTY_CELLS.some(([er, ec]) => er === r && ec === c);
            const borderRight = (c + 1) % 3 === 0 && c < 8 ? '4px solid #000' : '1px solid #000';
            const borderBottom = (r + 1) % 3 === 0 && r < 8 ? '4px solid #000' : '1px solid #000';
            return (
              <motion.div
                key={`${r}-${c}`}
                animate={isEmpty ? { boxShadow: ['inset 0 0 0 0 #FF6B6B', 'inset 0 0 0 4px #FF6B6B', 'inset 0 0 0 0 #FF6B6B'] } : {}}
                transition={isEmpty ? { duration: 1.2, repeat: Infinity, ease: 'easeInOut' } : {}}
                style={{
                  background: '#FFFDF5', color: '#000',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 24, fontFamily: 'Space Grotesk',
                  borderRight, borderBottom,
                }}
              >
                {isEmpty ? '' : val}
              </motion.div>
            );
          })
        )}
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.9 }}
        style={{ fontWeight: 900, fontSize: '2rem' }}
      >
        只有 <span style={{ background: '#FF6B6B', color: '#FFF', padding: '0 16px', border: '4px solid #000' }}>3 格空</span>
      </motion.div>
    </main>
  );
}
```

### Ch8Step3 — 反向課程動畫 3→10 (board with growing empty cells)

```jsx
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

const BOARD = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,2, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];
const REMOVAL_SEQ = [
  [1,3],[4,7],[7,2],[0,4],[3,1],[6,7],[2,2],[5,5],[8,1],[4,4],
];

export default function Ch8Step3() {
  const [count, setCount] = useState(3);

  useEffect(() => {
    let cur = 3;
    const id = setInterval(() => {
      cur = cur + 1;
      if (cur > 10) {
        clearInterval(id);
        return;
      }
      setCount(cur);
    }, 500);
    return () => clearInterval(id);
  }, []);

  const blanks = new Set(REMOVAL_SEQ.slice(0, count).map(([r, c]) => `${r}-${c}`));

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '1.5rem' }}
      >
        讓難度跟著他的能力走
      </motion.div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(9, 1fr)',
        width: 540, height: 540,
        border: '6px solid #000', background: '#000',
        boxShadow: '12px 12px 0 0 #000',
      }}>
        {BOARD.flatMap((row, r) =>
          row.map((val, c) => {
            const isEmpty = blanks.has(`${r}-${c}`);
            const borderRight = (c + 1) % 3 === 0 && c < 8 ? '4px solid #000' : '1px solid #000';
            const borderBottom = (r + 1) % 3 === 0 && r < 8 ? '4px solid #000' : '1px solid #000';
            return (
              <motion.div
                key={`${r}-${c}`}
                animate={isEmpty ? { scale: [0.95, 1], background: ['#FFFDF5', '#FFFDF5'] } : {}}
                style={{
                  background: '#FFFDF5', color: '#000',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 24,
                  borderRight, borderBottom,
                }}
              >
                {isEmpty ? '' : val}
              </motion.div>
            );
          })
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontWeight: 900, fontSize: 24 }}>
        空格:
        <span style={{
          background: '#FFD93D', color: '#000',
          padding: '4px 16px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontFamily: 'monospace', fontSize: 32, rotate: -2,
        }}>
          {count}
        </span>
        / 10
      </div>
    </main>
  );
}
```

- [ ] Update Ch8.jsx STEPS to add `2: Ch8Step2, 3: Ch8Step3`

- [ ] Build + commit: `feat(demo): ch8 s2 3-empty + s3 reverse curriculum 3→10 animation`

---

## Task 3: Ch8Step4 — +20 → +50 翻牌 (first use of `motif/flip-20-to-50`)

This step uses 3D flip transform. The shell motif exists but needs real implementation. Let me build it inline for now (flip card with 3D rotateY).

```jsx
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

export default function Ch8Step4() {
  const [flipped, setFlipped] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setFlipped(true), 800);
    return () => clearTimeout(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        破關獎勵調更大
      </motion.div>

      {/* 3D flip card */}
      <div style={{ perspective: 1000, width: 400, height: 240 }}>
        <motion.div
          initial={{ rotateY: 0 }}
          animate={{ rotateY: flipped ? 180 : 0 }}
          transition={{ duration: 0.6, ease: 'easeInOut' }}
          style={{
            position: 'relative', width: '100%', height: '100%',
            transformStyle: 'preserve-3d',
          }}
        >
          {/* Front: +20 (red) */}
          <div style={{
            position: 'absolute', inset: 0,
            backfaceVisibility: 'hidden',
            background: '#FF6B6B', color: '#FFF',
            border: '8px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 900, fontSize: '8rem',
          }}>
            +20
          </div>
          {/* Back: +50 (yellow) */}
          <div style={{
            position: 'absolute', inset: 0,
            backfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
            background: '#FFD93D', color: '#000',
            border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 900, fontSize: '8rem',
          }}>
            +50
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.6 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', textAlign: 'center', color: '#666' }}
      >
        誘惑超過刷部分分數的賤招
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch8.jsx STEPS to add `4: Ch8Step4`

- [ ] Build + commit: `feat(demo): ch8 s4 +20 → +50 3D flip card (first flip-20-to-50)`

---

## Task 4: Ch8Step5 + Ch8Step6 (光講不夠看 + visualizer button)

### Ch8Step5 — 光講不夠看

```jsx
import { motion } from 'motion/react';

export default function Ch8Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8 }}
        style={{ fontWeight: 900, fontSize: '5rem' }}
      >
        光講不夠看
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{ fontWeight: 700, fontSize: '2rem', color: '#000' }}
      >
        給大家看一下 AI 即時解數獨的題目
      </motion.div>

      {/* Bounce arrow pointing down */}
      <motion.svg
        width="80" height="120" viewBox="0 0 80 120"
        animate={{ y: [0, 16, 0] }}
        transition={{ duration: 1.2, ease: 'easeInOut', repeat: Infinity }}
      >
        <motion.path
          d="M 40 10 L 40 90 M 10 70 L 40 100 L 70 70"
          fill="none" stroke="#000" strokeWidth="8" strokeLinecap="square" strokeLinejoin="miter"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 1.0 }}
        />
      </motion.svg>
    </main>
  );
}
```

### Ch8Step6 — visualizer 大按鈕

```jsx
import { motion } from 'motion/react';
import { useState } from 'react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch8Step6() {
  const [hover, setHover] = useState(false);

  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.a
        href="sudoku-demo:run"
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: hover ? 1.05 : 1, opacity: 1 }}
        transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ textDecoration: 'none', cursor: 'pointer', display: 'inline-block' }}
      >
        <Sticker variant="hub-mega" bg={hover ? '#E25555' : '#FF6B6B'} color="#FFFDF5" rotation={-2}>
          點我看 AI 即時解數獨 →
        </Sticker>
      </motion.a>

      <div style={{
        position: 'absolute', bottom: 64,
        fontWeight: 700, fontSize: 14, color: '#999', textAlign: 'center', maxWidth: 600,
      }}>
        點擊後會自動啟動桌面 pygame 視窗（透過 Windows custom URL scheme），不需手動 Alt+Tab。<br/>
        詳細部署見 demo/visualizer-launch/README.md
      </div>
    </div>
  );
}
```

- [ ] Update Ch8.jsx STEPS to add `5: Ch8Step5, 6: Ch8Step6`

- [ ] Build + commit: `feat(demo): ch8 s5 光講不夠看 + s6 visualizer 大按鈕`

- [ ] `git tag phase-8-ch8-complete`

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 反向思考**: 黑底淡入到 cream、紅高亮「反向思考」hero、副標、底「AI 也是→」footer
- [ ] **s2 3 格空**: 9×9 數獨盤面（90% 已填、3 空格紅色 outline pulse）、副標「只有 3 格空 / 他一定解得出來」
- [ ] **s3 反向課程動畫**: 同盤面、每 500ms 多一格變空（3→4→5→...→10）、計數器同步「空格: 3→10」
- [ ] **s4 +20 → +50 翻牌**: 紅「+20」card 800ms 後翻面變黃「+50」card（3D rotateY 0→180）、副標「誘惑超過刷部分分數的賤招」
- [ ] **s5 光講不夠看**: 「光講不夠看」mask-reveal、「給大家看一下 AI 即時解數獨的題目」、向下大箭頭 bounce 永動
- [ ] **s6 visualizer 大按鈕**: 「點我看 AI 即時解數獨 →」紅色超大按鈕、hover 變暗 + scale 1.05 + shadow 加深、底下說明文字。href 是 `sudoku-demo:run` (Windows custom URL scheme)

## 想問你的回饋的點

1. **s2 / s3 9×9 盤面用 CSS grid 真實渲染**（不是 placeholder）— 我內聯了 81 格、3×3 子格用粗 4px 邊、其他 1px 邊。視覺效果像真數獨嗎？
2. **s3 空格動畫**: 從 3 漸進到 10、每 500ms 多一格。視覺漸進感 OK 嗎？該不該加「擦除」效果（淡出原數字）?
3. **s4 3D flip**: rotateY 0→180、`transformStyle: preserve-3d` + `backfaceVisibility: hidden`。flip 翻得平滑嗎？要不要加 shadow 翻面動畫?
4. **s6 visualizer 按鈕**: `href="sudoku-demo:run"` — 點下去如果 Windows custom URL scheme 沒註冊、會顯示「protocol not handled」錯誤。要不要加 fallback 訊息？（例如點下去後 5s 沒響應、顯示「請執行 demo/visualizer-launch/install.bat」?）
5. **填好的 9×9 數字** 我用一個合法的解答 (Sudoku 9×9 latin square)、3 個 EMPTY_CELLS 寫死座標 — 要不要從真正的 puzzle DB 抓題目?

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
