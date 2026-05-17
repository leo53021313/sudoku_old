# Phase 4 · Chapter 4 (data-hunt) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Build ch4 data-hunt — Kaggle → supervised 拒絕 → websudoku 受害者 punchline → 封 IP + proxy 池. 4 steps, ~50s, 1 punchline (s3 receives A+C+E light). First use of `motif/red-stamp` (s2 stamp) and `motif/ink-splatter` (s2 polish + s3 punchline).

**Source spec:** [outline.md §4](../../../demo/outline.md) · script.md L99-L133

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch4
└── ch4-data-hunt/
    ├── Ch4.jsx
    ├── Ch4Step1.jsx                        # Kaggle 介紹
    ├── Ch4Step2.jsx                        # supervised 拒絕 (polish ink-splatter)
    ├── Ch4Step3.jsx                        # 受害者 punchline 4-beat (A+C+E)
    └── Ch4Step4.jsx                        # 封 IP + proxy 池
```

---

## Task 1: Register Ch4 + Step1 + Step2 (batched)

**Files:**
- Create: `Ch4.jsx`, `Ch4Step1.jsx`, `Ch4Step2.jsx`
- Modify: `src/chapters/index.jsx`

- [ ] **Step 1: Update `src/chapters/index.jsx`** — add `4: Ch4`

- [ ] **Step 2: Create `Ch4.jsx`**

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch4Step1 from './Ch4Step1.jsx';
import Ch4Step2 from './Ch4Step2.jsx';

const STEPS = { 1: Ch4Step1, 2: Ch4Step2 };

export function Ch4() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 4 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Create `Ch4Step1.jsx`** (Kaggle + 紅叉叉 burst)

```jsx
import { motion } from 'motion/react';

export default function Ch4Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <motion.div
        initial={{ scale: 0, opacity: 0, rotate: 0 }}
        animate={{ scale: 1, opacity: 1, rotate: 2 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '24px 56px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '4rem',
        }}
      >
        Kaggle
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{
          marginTop: 32, fontWeight: 700, fontSize: '1.75rem',
          textAlign: 'center', maxWidth: 800,
        }}
      >
        題目+完整答案 整理好的資料集
      </motion.div>

      {/* 3 data cards stagger */}
      <div style={{ marginTop: 48, display: 'flex', gap: 16 }}>
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            initial={{ y: 30, scale: 0.8, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.9 + i * 0.1, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              width: 140, height: 100, background: '#FFFFFF',
              border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
              padding: 16, fontWeight: 700, fontSize: 14,
              transform: `rotate(${[-3, 1, 4][i]}deg)`,
            }}
          >
            dataset #{i + 1}
            <div style={{ marginTop: 12, color: '#999' }}>n=10k</div>
          </motion.div>
        ))}
      </div>

      {/* 但問題來了 — 紅叉叉 burst climax */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1.2, 1], opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          pointerEvents: 'none',
        }}
      >
        <div style={{
          fontWeight: 900, fontSize: '8rem', color: '#FF6B6B',
          WebkitTextStroke: '4px black', textShadow: '12px 12px 0 #000',
          rotate: -5,
        }}>
          ✗ 但問題來了
        </div>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 4: Create `Ch4Step2.jsx`** (supervised 拒絕 — first use of red-stamp, polish ink-splatter)

```jsx
import { motion } from 'motion/react';
import { RedStamp } from '../../motifs/RedStamp.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch4Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Red stamp from above with bounce + ink splatter light variant on impact */}
      <div style={{ position: 'relative' }}>
        <RedStamp active rotation={-5} size="large">supervised 路線 · 拒絕</RedStamp>
        {/* Light ink-splatter on stamp impact, 4 dots, radius 50 */}
        <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          <InkSplatter active count={4} radius={60} centerX="50%" centerY="50%" />
        </div>
      </div>

      {/* Right comparison */}
      <motion.div
        initial={{ x: 60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          background: '#FFD93D', color: '#000',
          padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: 32, rotate: 3,
        }}
      >
        我要 AI · 自己摸出規則
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 5: Build + commit**: `feat(demo): ch4 register + s1 Kaggle + s2 supervised 拒絕 (first red-stamp + ink-splatter polish)`

---

## Task 2: Ch4Step3 — 受害者 ★ punchline (4 beat, A+C+E)

**Files:**
- Create: `Ch4Step3.jsx`
- Modify: `Ch4.jsx`

Beat structure:
- beatIndex 0: kicker - 終極目標霸榜
- beatIndex 1: URL websudoku.com sticker slide-in
- beatIndex 2: 「受害者」紅 stamp 填入 placeholder + climax A+C+E
- beatIndex 3 (auto, 200ms): 副標「簡簡單單被我攻破」fade-up

- [ ] **Step 1: Create `Ch4Step3.jsx`**

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { RedStamp } from '../../motifs/RedStamp.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch4Step3() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C', 'E']);
  const firedRef = useRef(false);

  // Auto-advance from beat 2 (victim-stamp) → beat 3 (subtitle) after 200ms
  useEffect(() => {
    if (beatIndex === 3) {
      // beat 3 is auto-only no action; or could auto-advance happens at beat 2 end
    }
  }, [beatIndex]);

  // After beat 2 click → auto schedule beat 3 (200ms)
  useEffect(() => {
    if (beatIndex === 2) {
      const t = setTimeout(() => advance(), 200);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  // Beat 2 climax fire-once
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
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Beat 0+ kicker hero */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -40, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80, left: 0, right: 0, textAlign: 'center',
          fontWeight: 900, fontSize: '2.5rem',
        }}
      >
        終極目標：去每個數獨網站霸榜
      </motion.div>

      {/* Beat 1+ URL sticker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { x: 0, opacity: 1 } : { x: -200, opacity: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '16px 32px', border: '4px solid #000',
          fontFamily: 'monospace', fontWeight: 700, fontSize: 28,
          display: 'flex', alignItems: 'center', gap: 8,
        }}
      >
        websudoku.com
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
          style={{ color: '#FF6B6B' }}
        >_</motion.span>
      </motion.div>

      {/* Beat 2+ Victim stamp + ink-splatter A+C+E climax */}
      <div style={{ marginTop: 48, position: 'relative' }}>
        {beatIndex >= 2 && (
          <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
            <InkSplatter active count={8} radius={100} centerX="50%" centerY="50%" />
          </div>
        )}
        <RedStamp active={beatIndex >= 2} rotation={4} size="medium">這個受害者</RedStamp>
      </div>

      {/* Beat 3+ subtitle */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.4 }}
        style={{
          marginTop: 32, fontWeight: 700, fontSize: '1.5rem', color: '#666',
        }}
      >
        簡簡單單被我攻破
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch4.jsx STEPS to add `3: Ch4Step3`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch4 s3 受害者 punchline (A+C+E)`

---

## Task 3: Ch4Step4 — 封 IP + proxy 池

**Files:**
- Create: `Ch4Step4.jsx`
- Modify: `Ch4.jsx`

- [ ] **Step 1: Create `Ch4Step4.jsx`** (proxy grid + IP rotation animation)

```jsx
import { motion } from 'motion/react';
import { useState, useEffect } from 'react';

export default function Ch4Step4() {
  const [highlightIdx, setHighlightIdx] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setHighlightIdx(i => (i + 1) % 30), 200);
    return () => clearInterval(id);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 紅警示 hero phase 1 */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '3rem', rotate: -3, marginBottom: 32,
        }}
      >
        才爬 20 題就被封 IP
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{ fontWeight: 900, fontSize: '1.5rem', marginBottom: 24 }}
      >
        proxy 池 · 類似 VPN · 好幾萬個 IP
      </motion.div>

      {/* IP grid */}
      <motion.div
        initial="hidden"
        animate="visible"
        variants={{
          hidden: { opacity: 0 },
          visible: { opacity: 1, transition: { staggerChildren: 0.03 } },
        }}
        style={{
          display: 'grid', gridTemplateColumns: 'repeat(10, 1fr)', gap: 8,
          maxWidth: 800,
        }}
      >
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            variants={{
              hidden: { scale: 0, opacity: 0 },
              visible: { scale: 1, opacity: i === highlightIdx ? 1 : 0.4 },
            }}
            transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              background: i === highlightIdx ? '#FFD93D' : '#FFFDF5',
              border: '3px solid #000',
              boxShadow: i === highlightIdx ? '4px 4px 0 0 #000' : '2px 2px 0 0 #000',
              padding: '8px 4px',
              fontFamily: 'monospace', fontWeight: 700, fontSize: 12,
              textAlign: 'center', transform: `rotate(${(i * 7) % 5 - 2}deg)`,
              transition: 'background 0.15s, opacity 0.15s',
            }}
          >
            {`${(i * 17 + 23) % 256}.${(i * 31) % 256}`}
          </motion.div>
        ))}
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch4.jsx STEPS to add `4: Ch4Step4`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch4 s4 封 IP + proxy 池`

---

## Task 4: ch4 Checkpoint

```bash
npm run build && npm run test:run
git tag phase-4-ch4-complete
```

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 Kaggle**: 黃 Kaggle sticker stamp、3 張資料 card stagger、紅「✗ 但問題來了」大字 burst 覆蓋
- [ ] **s2 supervised 拒絕**: 紅 stamp「supervised 路線 · 拒絕」從天上砸下 + 周圍 4 個小黑點 ink splatter (polish 輕量)、右側黃「我要 AI · 自己摸出規則」
- [ ] **s3 受害者 ★ punchline** 4-beat:
  - beat 0: 「終極目標：去每個數獨網站霸榜」hero 從上 fade-in
  - beat 1: `websudoku.com` 黑底白字 mono 從左 slide-in（cursor 閃爍）
  - beat 2 (click): 「這個受害者」紅 stamp 砸下 + 8 個墨點散開 + 螢幕震 + 紅 stamp overshoot
  - beat 3 (auto 200ms): 副標「簡簡單單被我攻破」fade-up
- [ ] **s4 封 IP + proxy 池**: 紅警示「才爬 20 題就被封 IP」、proxy 池說明、30 張 IP 卡 grid 浮現 + 每 200ms 隨機一張高亮黃色

## 想問你的回饋的點

1. **s1「✗ 但問題來了」**用 8rem 紅字 + 4px text-stroke + 黑陰影、佔據整片 70%。視覺夠衝擊嗎？還是該用紅 stamp motif？
2. **s2 紅 stamp 旁的 ink splatter 4 個墨點**（半徑 60）— 看得到嗎？或被 stamp 蓋住了需要放大半徑？
3. **s3 punchline 受害者**: cue 講「這個受害者」當下才點 → 視覺同步爆。節奏要不要再延遲一點?
4. **s4 IP grid 30 張**: 排成 10×3、每 200ms 跳一張高亮。卡密度合適嗎？需要再多 (60 張) 還是太少？
5. **proxy IP 數字**：用 `(i * 17 + 23) % 256` 計算假造、避免真實 IP。需要顯示更像真 IP（4 個 octet）嗎？

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
