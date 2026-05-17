# Phase 7 · Chapter 7 (reasoner) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Build ch7 reasoner — 重寫宣告 → 顛倒驗證 → 13 招階梯 → 舊 vs 新 → Action 擴增 → 機率 0 → **老油條陷阱 ★★★** → 死結. 8 steps, ~138s, 2 punchlines (s6 light A+B+C+E + s7 ★★★ 6-beat A+E+G×2 + B×2). First use of `motif/13-stairs` (s3), `motif/sudoku-board` (s5), `motif/girl-veteran` (s7).

**Source spec:** [outline.md §7](../../../demo/outline.md) · script.md L201-L269

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch7
└── ch7-reasoner/
    ├── Ch7.jsx
    ├── Ch7Step1.jsx                        # 重寫宣告 + screen-shake polish
    ├── Ch7Step2.jsx                        # 顛倒驗證宣告
    ├── Ch7Step3.jsx                        # 13 招階梯 (first 13-stairs motif)
    ├── Ch7Step4.jsx                        # 舊 vs 新對比
    ├── Ch7Step5.jsx                        # Action 擴增 (first sudoku-board for ch7)
    ├── Ch7Step6.jsx                        # 機率 0 ★ punchline (A+B+C+E)
    ├── Ch7Step7.jsx                        # 老油條 ★★★ 6-beat (first girl-veteran)
    └── Ch7Step8.jsx                        # 死結
```

---

## Task 1: Register Ch7 + Step1 (screen-shake polish) + Step2

- [ ] **Step 1: Update `src/chapters/index.jsx`** — `7: Ch7`

- [ ] **Step 2: Create `Ch7.jsx`** (with steps populated):

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch7Step1 from './Ch7Step1.jsx';
import Ch7Step2 from './Ch7Step2.jsx';

const STEPS = { 1: Ch7Step1, 2: Ch7Step2 };

export function Ch7() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 7 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Create `Ch7Step1.jsx`** (重寫宣告 + light screen-shake polish on 重寫 yellow highlight)

```jsx
import { useEffect } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';

export default function Ch7Step1() {
  const { triggerShake } = usePresentationContext();

  // Trigger light shake when 重寫 highlight slides in (~700ms after mount)
  useEffect(() => {
    const t = setTimeout(() => triggerShake(), 700);
    return () => clearTimeout(t);
  }, [triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', marginBottom: 24 }}
      >
        核心想法只有一個
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.3, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        我只好整個計分獎勵系統
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
          transition={{ duration: 0.4, delay: 0.7, ease: 'easeOut' }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '4px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            display: 'inline-block',
            fontSize: '5rem', rotate: -2, marginTop: 16,
          }}
        >
          重寫
        </motion.span>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 4: Create `Ch7Step2.jsx`** (顛倒驗證 — 反過來 + 驗證 雙 highlight)

```jsx
import { motion } from 'motion/react';

export default function Ch7Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3.5rem', textAlign: 'center', lineHeight: 1.4,
          maxWidth: 1300,
        }}
      >
        用人類玩數獨的解題技巧
        <br/>
        <motion.span
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
          transition={{ duration: 0.4, delay: 1.3 }}
          style={{
            background: '#FF6B6B', color: '#FFF',
            padding: '2px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            display: 'inline-block', rotate: -2,
          }}
        >
          反過來
        </motion.span>
        {' '}
        <motion.span
          initial={{ clipPath: 'inset(0 100% 0 0)' }}
          animate={{ clipPath: 'inset(0 0 0 0)' }}
          transition={{ duration: 0.4, delay: 1.6 }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '2px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            display: 'inline-block', rotate: 2,
          }}
        >
          驗證
        </motion.span>
        {' '}
        AI 的每一步
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 5: Build + commit**: `feat(demo): ch7 register + s1 重寫宣告 + s2 顛倒驗證`

---

## Task 2: Ch7Step3 — 13 招大階梯 (first use of `motif/13-stairs` motif)

**Files:**
- Create: `Ch7Step3.jsx`
- Modify: `Ch7.jsx`

13 techniques staggered into a stair pattern. Real names from `reasoner/solver/techniques/`:

```js
const TECHS = [
  { name: 'Naked Single', level: 1, color: 'FFD93D' },
  { name: 'Hidden Single', level: 1, color: 'FFD93D' },
  { name: 'Box-Line Reduction', level: 2, color: 'FFD93D' },
  { name: 'Pointing Pair', level: 2, color: 'FFD93D' },
  { name: 'Naked Pair', level: 3, color: 'C4B5FD' },
  { name: 'Naked Triple', level: 3, color: 'C4B5FD' },
  { name: 'Hidden Pair', level: 4, color: 'C4B5FD' },
  { name: 'Hidden Triple', level: 4, color: 'C4B5FD' },
  { name: 'XY-Wing', level: 5, color: 'FF6B6B' },
  { name: 'XYZ-Wing', level: 5, color: 'FF6B6B' },
  { name: 'Swordfish', level: 6, color: 'FF6B6B' },
  { name: 'X-Wing', level: 7, color: 'FF6B6B' },        // 大且華麗
  { name: 'XYZ-Wing+', level: 7, color: 'FF6B6B' },     // 大且華麗
];
```

- [ ] **Step 1: Create `Ch7Step3.jsx`** (13 stair sticker stagger + hover tooltip)

```jsx
import { useState } from 'react';
import { motion } from 'motion/react';

const TECHS = [
  { name: 'Naked Single', size: 'sm', color: '#FFD93D', tip: '一格只能填一個數' },
  { name: 'Hidden Single', size: 'sm', color: '#FFD93D', tip: '一個數字在一行/列/區只有一處能填' },
  { name: 'Box-Line', size: 'sm', color: '#FFD93D', tip: '區內某數限制於某行/列' },
  { name: 'Pointing Pair', size: 'sm', color: '#FFD93D', tip: '兩格限定一行/列' },
  { name: 'Naked Pair', size: 'md', color: '#C4B5FD', tip: '兩格共用兩個候選數' },
  { name: 'Naked Triple', size: 'md', color: '#C4B5FD', tip: '三格共用三個候選數' },
  { name: 'Hidden Pair', size: 'md', color: '#C4B5FD', tip: '兩個數只能在兩格中之一' },
  { name: 'Hidden Triple', size: 'md', color: '#C4B5FD', tip: '三個數只能在三格中' },
  { name: 'XY-Wing', size: 'lg', color: '#FF6B6B', tip: 'Y-shaped 三格鏈消除' },
  { name: 'XYZ-Wing', size: 'lg', color: '#FF6B6B', tip: 'XYZ 變體三格鏈' },
  { name: 'Swordfish', size: 'lg', color: '#FF6B6B', tip: '三行三列交叉消除' },
  { name: 'X-Wing', size: 'xl', color: '#FF6B6B', tip: '兩行兩列交叉、最強招之一' },
  { name: 'T&E (試錯)', size: 'xl', color: '#FF6B6B', tip: 'Trial and Error 暴力試' },
];

const SIZE_MAP = {
  sm: { padding: '8px 16px', fontSize: 14, shadow: '4px 4px 0 0 #000' },
  md: { padding: '12px 20px', fontSize: 16, shadow: '6px 6px 0 0 #000' },
  lg: { padding: '16px 28px', fontSize: 20, shadow: '8px 8px 0 0 #000' },
  xl: { padding: '20px 36px', fontSize: 26, shadow: '12px 12px 0 0 #000' },
};

export default function Ch7Step3() {
  const [hoverIdx, setHoverIdx] = useState(-1);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px', fontWeight: 900, fontSize: 18,
          marginBottom: 16,
        }}
      >
        13 招 · 真實技巧名
      </motion.div>

      {/* Stairs: each tech is a step, ascending diagonal */}
      <div style={{
        position: 'relative', width: 1000, height: 540,
      }}>
        {TECHS.map((t, i) => {
          const sz = SIZE_MAP[t.size];
          const x = (i / TECHS.length) * 90;
          const y = 95 - (i / TECHS.length) * 85;
          const isHovered = i === hoverIdx;
          return (
            <motion.div
              key={i}
              initial={{ y: 30, scale: 0.8, opacity: 0 }}
              animate={{ y: 0, scale: isHovered ? 1.15 : 1, opacity: 1 }}
              transition={{
                opacity: { duration: 0.3, delay: 0.4 + i * 0.08 },
                y: { duration: 0.3, delay: 0.4 + i * 0.08 },
                scale: { duration: 0.2 },
              }}
              onMouseEnter={() => setHoverIdx(i)}
              onMouseLeave={() => setHoverIdx(-1)}
              style={{
                position: 'absolute', left: `${x}%`, bottom: `${y}%`,
                background: t.color, color: '#000',
                ...sz,
                border: '4px solid #000', boxShadow: sz.shadow, fontWeight: 900,
                transform: `rotate(${(i % 2 === 0 ? -1 : 1) * (3 + i % 4)}deg)`,
                opacity: hoverIdx === -1 ? 1 : isHovered ? 1 : 0.4,
                cursor: 'pointer', whiteSpace: 'nowrap',
                transition: 'opacity 0.2s',
                zIndex: isHovered ? 20 : 1,
              }}
            >
              {t.name}
              {isHovered && (
                <div style={{
                  position: 'absolute', top: '110%', left: 0,
                  background: '#000', color: '#FFFDF5',
                  padding: '8px 12px', fontSize: 12,
                  whiteSpace: 'nowrap', fontWeight: 700,
                }}>
                  {t.tip}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      <div style={{ marginTop: 16, fontWeight: 700, color: '#666', fontSize: 16 }}>
        低階 → → → 高階
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch7.jsx STEPS to add `3: Ch7Step3`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch7 s3 13 招階梯 (first 13-stairs motif)`

---

## Task 3: Ch7Step4 + Ch7Step5 (batched)

### Ch7Step4 — 舊 vs 新對比

```jsx
import { motion } from 'motion/react';

export default function Ch7Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', display: 'flex',
    }}>
      <div style={{ flex: '0 0 60%', padding: 64, borderRight: '6px solid #000' }}>
        <motion.div
          initial={{ x: -100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ fontWeight: 900, fontSize: '2.5rem', marginBottom: 32 }}
        >
          舊：<span style={{ background: '#999', color: '#FFF', padding: '4px 16px' }}>填對給分</span>
        </motion.div>
        {/* one tech glow + single +1 */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.4, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#FFD93D', color: '#000',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 28, display: 'inline-block', rotate: -3,
          }}
        >
          Naked Single
        </motion.div>
        <motion.div
          initial={{ y: 0, opacity: 0 }}
          animate={{ y: -60, opacity: [0, 1, 0] }}
          transition={{ duration: 1.2, delay: 1.0 }}
          style={{ fontWeight: 900, fontSize: 36, color: '#10B981', marginLeft: 200 }}
        >
          +1
        </motion.div>
      </div>

      <div style={{ flex: '0 0 40%', padding: 64, position: 'relative' }}>
        <motion.div
          initial={{ x: 100, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ fontWeight: 900, fontSize: '2rem', marginBottom: 24 }}
        >
          新：<span style={{ background: '#FFD93D', padding: '4px 12px', border: '4px solid #000', fontSize: '1.5rem' }}>哪一招解釋？</span>
        </motion.div>
        {[
          { name: 'Naked Single', score: '+1', y: 0, delay: 0.6, color: '#FFD93D' },
          { name: 'Naked Pair', score: '+2', y: 80, delay: 0.8, color: '#C4B5FD' },
          { name: 'X-Wing', score: '+3', y: 160, delay: 1.0, color: '#FF6B6B' },
          { name: 'XYZ-Wing', score: '+3', y: 240, delay: 1.2, color: '#FF6B6B' },
        ].map((t, i) => (
          <motion.div
            key={i}
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: t.delay }}
            style={{
              position: 'absolute', top: 160 + t.y, left: 64,
              display: 'flex', alignItems: 'center', gap: 16,
            }}
          >
            <span style={{
              background: t.color, color: '#000',
              padding: '8px 16px', border: '4px solid #000', boxShadow: '4px 4px 0 0 #000',
              fontWeight: 900, fontSize: 18,
            }}>{t.name}</span>
            <span style={{ fontWeight: 900, fontSize: 28, color: '#10B981' }}>{t.score}</span>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
```

### Ch7Step5 — Action 擴增 (first use of `motif/sudoku-board` for ch7)

```jsx
import { motion } from 'motion/react';
import { SudokuBoard } from '../../motifs/SudokuBoard.jsx';

export default function Ch7Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        多了一倍可以做的事
      </motion.div>

      {/* Sudoku board placeholder (shell motif, [E] real SVG to be built later) */}
      <SudokuBoard />

      <div style={{ display: 'flex', gap: 32, fontWeight: 900, fontSize: 20 }}>
        <span style={{
          background: '#10B981', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>填一個數字</span>
        <span style={{
          background: '#FF6B6B', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>劃掉這格不可能是這個數 ✗</span>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', marginTop: 8 }}
      >
        消去類技巧才能展示出來
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch7.jsx STEPS to add `4: Ch7Step4, 5: Ch7Step5`

- [ ] Build + commit: `feat(demo): ch7 s4 舊vs新 + s5 Action 擴增`

---

## Task 4: Ch7Step6 ★ punchline 機率 0 (A+B+C+E)

3-beat: count-up 兩千多萬次 → subtitle + caret placeholder → 0 drop-in + climax

- [ ] **Step 1: Create `Ch7Step6.jsx`**

```jsx
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch7Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'E']);
  const firedRef = useRef(false);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (beatIndex === 0) {
      let raf, start;
      const animate = (t) => {
        if (!start) start = t;
        const elapsed = t - start;
        const pct = Math.min(elapsed / 2000, 1);
        setCount(Math.floor(pct * 23456789));
        if (pct < 1) raf = requestAnimationFrame(animate);
      };
      raf = requestAnimationFrame(animate);
      return () => cancelAnimationFrame(raf);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
    }
  }, [beatIndex, climax, triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
      background: beatIndex >= 0 ? 'rgba(255,107,107,0.15)' : 'transparent',
      transition: 'background 0.3s',
    }}>
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="50%" />
      <InkSplatter active={climax.activeFX.E} count={8} radius={160} centerX="50%" centerY="50%" />

      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { opacity: 1 } : { opacity: 0 }}
        style={{
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        練了
        <span style={{
          background: '#FF6B6B', color: '#FFF', padding: '4px 24px', margin: '0 12px',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          fontSize: '3rem', fontFamily: 'monospace',
        }}>
          {count.toLocaleString()}
        </span>
        次
      </motion.div>

      {/* Beat 1+ subtitle with caret placeholder */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { opacity: 1 } : { opacity: 0 }}
        style={{
          fontWeight: 700, fontSize: '2rem', textAlign: 'center',
        }}
      >
        完整解出一道題的機率還是
        {beatIndex < 2 && (
          <motion.span
            animate={{ opacity: [1, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
            style={{ marginLeft: 16, color: '#FF6B6B' }}
          >_</motion.span>
        )}
      </motion.div>

      {/* Beat 2 punchline: "0" drop-in */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0, 1.4, 1.0, 0.95, 1.0], y: [0, 0, 0, 0, 0], opacity: 1 }
          : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '32px 96px', border: '8px solid #000', boxShadow: '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '12rem', lineHeight: 1, rotate: -3,
          position: 'relative', zIndex: 50,
        }}
      >
        0
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch7.jsx STEPS to add `6: Ch7Step6`

- [ ] Build + commit: `feat(demo): ch7 s6 機率 0 punchline (A+B+C+E)`

---

## Task 5: Ch7Step7 ★★★ 老油條陷阱題 (6-beat, first girl-veteran)

Beat structure (6 beats — the most complex punchline in the whole show):
- beatIndex 0: hero「老油條女生陷阱題」mask-reveal
- beatIndex 1: 左 sticker「掉進水裡你會先救誰？」紅底 swing-in
- beatIndex 2: 右 sticker「該不該去運動？」紫底 swing-in + 兩答案箭頭「???」placeholder
- beatIndex 3: 左答案 placeholder → 「❌嫌那個女生胖」+ climax A+E+G
- beatIndex 4: 右答案 placeholder → 「❌你不關心健康」+ climax A+E+G
- beatIndex 5 (auto): 雙 ❌ 同步 flash + 雙 halftone-burst (B×2)

- [ ] **Step 1: Create `Ch7Step7.jsx`**

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch7Step7() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climaxA = useClimax(['A', 'E', 'G']);  // beat 3
  const climaxB = useClimax(['A', 'E', 'G']);  // beat 4
  const climaxBoth = useClimax(['B']);         // beat 5 (double burst)
  const firedA = useRef(false);
  const firedB = useRef(false);
  const firedBoth = useRef(false);

  // Auto-advance from beat 4 → beat 5 after 400ms
  useEffect(() => {
    if (beatIndex === 4) {
      const t = setTimeout(() => advance(), 400);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  useEffect(() => {
    if (beatIndex === 3 && !firedA.current) {
      firedA.current = true;
      climaxA.play();
      triggerShake();
    }
    if (beatIndex === 4 && !firedB.current) {
      firedB.current = true;
      climaxB.play();
      triggerShake();
    }
    if (beatIndex === 5 && !firedBoth.current) {
      firedBoth.current = true;
      climaxBoth.play();
    }
  }, [beatIndex, climaxA, climaxB, climaxBoth, triggerShake]);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <SpotlightVignette active={climaxA.activeFX.G || climaxB.activeFX.G} />
      <InkSplatter active={climaxA.activeFX.E} count={8} radius={140} centerX="30%" centerY="60%" />
      <InkSplatter active={climaxB.activeFX.E} count={8} radius={140} centerX="70%" centerY="60%" />
      <HalftoneBurst active={climaxBoth.activeFX.B} centerX="30%" centerY="65%" size={400} />
      <HalftoneBurst active={climaxBoth.activeFX.B} centerX="70%" centerY="65%" size={400} />

      {/* Beat 0: hero */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { clipPath: 'inset(0 0 0 0)', opacity: 1 } : { clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        transition={{ duration: 0.8 }}
        style={{
          fontWeight: 900, fontSize: '3rem',
        }}
      >
        <span style={{ background: '#FFD93D', padding: '4px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000' }}>
          老油條女生陷阱題
        </span>
      </motion.div>

      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        {/* Beat 1: trap 1 left */}
        <motion.div
          initial={false}
          animate={beatIndex >= 1 ? { rotate: -3, x: 0, opacity: 1 } : { rotate: -30, x: -200, opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#FF6B6B', color: '#FFF',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          和你媽一起<br/>掉進水裡<br/>你會先救誰？
        </motion.div>

        {/* Beat 2: trap 2 right */}
        <motion.div
          initial={false}
          animate={beatIndex >= 2 ? { rotate: 4, x: 0, opacity: 1 } : { rotate: 30, x: 200, opacity: 0 }}
          transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          你覺得我<br/>該不該去<br/>運動？
        </motion.div>
      </div>

      {/* Answer arrows + placeholders */}
      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        <div style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}>
          說要 →
          <motion.span
            initial={false}
            animate={beatIndex >= 3
              ? { scale: [0.9, 1.2, 1], opacity: 1 }
              : { scale: 0.9, opacity: beatIndex >= 2 ? 0.4 : 0 }}
            transition={{ duration: 0.4 }}
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px', border: '4px solid #000',
              display: 'inline-block',
            }}
          >
            {beatIndex >= 3 ? '❌ 嫌那個女生胖' : '❌ ???'}
          </motion.span>
        </div>
        <div style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}>
          說不用 →
          <motion.span
            initial={false}
            animate={beatIndex >= 4
              ? { scale: [0.9, 1.2, 1], opacity: 1 }
              : { scale: 0.9, opacity: beatIndex >= 2 ? 0.4 : 0 }}
            transition={{ duration: 0.4 }}
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px', border: '4px solid #000',
              display: 'inline-block',
            }}
          >
            {beatIndex >= 4 ? '❌ 你不關心健康' : '❌ ???'}
          </motion.span>
        </div>
      </div>

      {beatIndex >= 5 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          style={{
            marginTop: 32, fontWeight: 900, fontSize: 24,
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}
        >
          兩面不討好
        </motion.div>
      )}
    </main>
  );
}
```

- [ ] Update Ch7.jsx STEPS to add `7: Ch7Step7`

- [ ] Build + commit: `feat(demo): ch7 s7 老油條陷阱題 ★★★ 6-beat punchline (first girl-veteran motif)`

---

## Task 6: Ch7Step8 + checkpoint

### Ch7Step8 — 死結

```jsx
import { motion } from 'motion/react';

export default function Ch7Step8() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <motion.div
        initial={{ background: '#FFFDF5' }}
        animate={{ background: '#000' }}
        transition={{ duration: 0.8 }}
        style={{
          position: 'fixed', inset: 0, zIndex: 9, pointerEvents: 'none',
        }}
      />

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.5, delay: 0.6, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3.5rem', color: '#FFFDF5', textAlign: 'center', lineHeight: 1.4,
          maxWidth: 1200, zIndex: 10, position: 'relative',
        }}
      >
        AI 永遠拿不到
        <br/>
        <span style={{ background: '#FF6B6B', padding: '4px 24px', border: '6px solid #FFF', display: 'inline-block', marginTop: 16 }}>
          「整題解完」那個大獎
        </span>
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 2.0 }}
        style={{
          fontWeight: 700, fontSize: '1.5rem', color: '#FFFDF5', zIndex: 10, position: 'relative',
        }}
      >
        就跟我不知道陷阱題的正確解答一樣
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 3.0 }}
        style={{
          position: 'absolute', bottom: 64,
          fontWeight: 700, fontSize: 18, color: '#999', zIndex: 10,
        }}
      >
        反向思考⋯
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch7.jsx STEPS to add `8: Ch7Step8`

- [ ] Build + commit: `feat(demo): ch7 s8 死結 + 反向思考鋪墊`

- [ ] `git tag phase-7-ch7-complete`

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 重寫宣告**: kicker「核心想法只有一個」+ hero「整個計分獎勵系統 / 重寫 (黃底大字 mask-reveal)」+ 700ms 後輕震一下
- [ ] **s2 顛倒驗證**: hero「用人類玩數獨的解題技巧 / 反過來(紅) 驗證(黃) AI 的每一步」雙 highlight stagger
- [ ] **s3 13 招大階梯**: 13 個 sticker 由低到高 stagger stamp-in、X-Wing/XYZ-Wing 最大（紅色 + 12px shadow）、低階小且樸素（黃色 + 4px shadow）、hover 任一 sticker 放大其他 dim、tooltip 顯示
- [ ] **s4 舊 vs 新**: split 60/40、左舊「Naked Single +1」單一招、右新「多招 + 不同分數 stagger」(Naked Single +1、Naked Pair +2、X-Wing +3、XYZ-Wing +3)
- [ ] **s5 Action 擴增**: hero「多了一倍可以做的事」+ SudokuBoard placeholder + 綠/紅雙動作說明
- [ ] **s6 機率 0 ★ punchline** 3-beat:
  - beat 0: 底色紅、count-up「練了 0 → 23,456,789 次」(2s 動畫)
  - beat 1: 副標「完整解出一道題的機率還是 _」閃爍游標
  - beat 2: 「0」黃底超大字砸下 + 紅底 flash + 螢幕震 + halftone burst + ink splatter
- [ ] **s7 老油條 ★★★ punchline** 6-beat:
  - beat 0: 「老油條女生陷阱題」hero + 黃底
  - beat 1: 左紅 sticker「掉進水裡你會先救誰？」swing-in
  - beat 2: 右紫 sticker「該不該去運動？」swing-in + 下方「???」placeholder
  - beat 3 (click): 左答案揭曉「❌ 嫌那個女生胖」+ 該區 spotlight + ink splatter
  - beat 4 (click): 右答案揭曉「❌ 你不關心健康」+ 該區 spotlight + ink splatter
  - beat 5 (auto 400ms): **雙 halftone burst 同步從兩 ❌ 放射** + 「兩面不討好」黃 badge 出現
- [ ] **s8 死結**: 底色轉黑、「AI 永遠拿不到『整題解完』那個大獎」cream 字 mask-reveal、「就跟我不知道陷阱題的正確解答一樣」副標、底「反向思考⋯」鋪墊下章

## 想問你的回饋的點

1. **s3 13 招階梯排列**: 沿對角線從左下→右上 stagger、每個 sticker 大小 + 顏色按等級分（4 黃小 / 4 紫中 / 5 紅大）。視覺辨識度 OK 嗎？技巧名翻譯要中文還是維持英文？
2. **s3 tooltip 中文簡介** (e.g. "一格只能填一個數")：簡單敘述、是否足夠專業？要不要更口語？
3. **s5 SudokuBoard placeholder** 用 Phase 0 的 shell 元件（紅虛線框 + ⚠️ TODO）— 對 ch7 演示來說會不會太空？要不要先用簡單的 9×9 CSS grid 模擬?
4. **s6 「0」字級 12rem + 黃底超大** — 夠衝擊嗎？太大了嗎？
5. **s7 ★★★ 6-beat 流程**: 兩段笑點（beat 3、4）各有 climax、beat 5 是 auto 雙爆。每個 beat 之間 wait（per outline.md）是 2s — 用 setTimeout 自動延遲還是手動點 click 推進？(目前是手動 click 推進、僅 beat 5 auto)
6. **s8 死結轉黑底**: 從 cream 過渡到黑、字也轉成 cream。會不會跟「Neo-brutalism cream 主畫布」原則衝突？(outline 註：原版就是 cinematic 黑底 hero、是刻意的氣質轉換)

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
