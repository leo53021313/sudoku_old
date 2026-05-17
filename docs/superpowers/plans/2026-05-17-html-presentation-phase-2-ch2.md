# Phase 2 · Chapter 2 (ml-map) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Build ch2 ml-map — the educational intro to ML's 3 main types (supervised / unsupervised / RL + AlphaGo) → cliffhanger「ChatGPT/Claude 是哪一招？」. 4 steps, ~50s, no punchlines, polish FX on s4 (problem mark 720° rotation).

**Architecture:** Same as ch1 — each step is a JSX file under `src/chapters/ch2-ml-map/`. Register Ch2 in chapter router. No new motifs needed (yellow-highlight already exists from ch1).

**Tech Stack:** React 19 · Motion 11+ · Tailwind v4 · Phase 0 components/motifs already available.

**Source spec:** [outline.md §2](../../../demo/outline.md) · script.md L49-L71

---

## File Structure

```
demo/presentation/src/chapters/
├── index.jsx                              # MODIFY: register Ch2
└── ch2-ml-map/
    ├── Ch2.jsx                             # CREATE: dispatcher
    ├── Ch2Step1.jsx                        # CREATE: supervised
    ├── Ch2Step2.jsx                        # CREATE: unsupervised
    ├── Ch2Step3.jsx                        # CREATE: RL + AlphaGo
    └── Ch2Step4.jsx                        # CREATE: cliffhanger（問號 720° 旋轉 polish）
```

---

## Task 1: Register Ch2 + scaffold dispatcher + Step1

**Files:**
- Create: `src/chapters/ch2-ml-map/Ch2.jsx`
- Create: `src/chapters/ch2-ml-map/Ch2Step1.jsx`
- Modify: `src/chapters/index.jsx`

- [ ] **Step 1: Create `src/chapters/ch2-ml-map/Ch2.jsx`**

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch2Step1 from './Ch2Step1.jsx';

const STEPS = {
  1: Ch2Step1,
};

export function Ch2() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 2 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
```

- [ ] **Step 2: Update `src/chapters/index.jsx`**

```jsx
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { Ch1 } from './ch1-coldopen/Ch1.jsx';
import { Ch2 } from './ch2-ml-map/Ch2.jsx';

const CHAPTERS = {
  1: Ch1,
  2: Ch2,
};

export function ChapterRouter() {
  const { chapterId } = usePresentationContext();
  const Chapter = CHAPTERS[chapterId];
  if (!Chapter) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch {chapterId} (not implemented)</div>
        <div style={{ marginTop: 16, color: '#666' }}>Implemented: ch 1, ch 2. Other chapters incoming.</div>
      </main>
    );
  }
  return <Chapter />;
}
```

- [ ] **Step 3: Create `src/chapters/ch2-ml-map/Ch2Step1.jsx`** (supervised — 看著答案抄筆記)

```jsx
import { motion } from 'motion/react';

export default function Ch2Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Kicker top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 18, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        機器學習 · ①/3
      </motion.div>

      {/* Big "supervised" mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em',
        }}
      >
        supervised
      </motion.div>

      {/* Subtitle: 白話 */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 24,
          fontWeight: 700, fontSize: '2rem', color: '#000',
        }}
      >
        白話：<span style={{
          background: '#FFD93D', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>看著答案抄筆記</span>
      </motion.div>

      {/* Right-side text illustration (no Phosphor for now — text labels) */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
        }}
      >
        <div style={{
          background: '#FFFFFF', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>老師</div>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <div style={{
          background: '#FFD93D', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>題目 + 答案</div>
        <div style={{ fontWeight: 900, fontSize: 20 }}>↓</div>
        <div style={{
          background: '#C4B5FD', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 20px', fontWeight: 900, fontSize: 16,
        }}>學生硬背</div>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 4: Build + test + commit**

```bash
cd demo/presentation && npm run build && npm run test:run
git add demo/presentation/src/chapters/index.jsx demo/presentation/src/chapters/ch2-ml-map/
git commit -m "feat(demo): ch2 register + s1 supervised"
```

---

## Task 2: Ch2Step2 — unsupervised + Ch2Step3 — RL + AlphaGo (batched)

**Files:**
- Create: `src/chapters/ch2-ml-map/Ch2Step2.jsx`
- Create: `src/chapters/ch2-ml-map/Ch2Step3.jsx`
- Modify: `src/chapters/ch2-ml-map/Ch2.jsx` (register Step2, Step3)

- [ ] **Step 1: Create `Ch2Step2.jsx`**

```jsx
import { motion } from 'motion/react';

export default function Ch2Step2() {
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
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 18, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        機器學習 · ②/3
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em',
        }}
      >
        unsupervised
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 24,
          fontWeight: 700, fontSize: '2rem', color: '#000',
        }}
      >
        白話：<span style={{
          background: '#C4B5FD', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>自己分類整理</span>
      </motion.div>

      {/* Clothes piles: one messy → 3 sorted */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
          display: 'flex', alignItems: 'center', gap: 24,
        }}
      >
        <div style={{ fontWeight: 900, fontSize: 18, textAlign: 'center' }}>
          <div style={{
            width: 80, height: 80, background: '#999',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#FFF', marginBottom: 8,
          }}>👕👖👔</div>
          一堆
        </div>
        <div style={{ fontWeight: 900, fontSize: 24 }}>→</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ background: '#FF6B6B', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>紅</div>
          <div style={{ background: '#FFD93D', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>黃</div>
          <div style={{ background: '#C4B5FD', border: '3px solid #000', padding: 4, fontWeight: 900, fontSize: 12, textAlign: 'center' }}>紫</div>
        </div>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Create `Ch2Step3.jsx`** (RL + AlphaGo)

```jsx
import { motion } from 'motion/react';

export default function Ch2Step3() {
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
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 18, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        機器學習 · ③/3
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '7rem', lineHeight: 1.05,
          letterSpacing: '-0.04em', display: 'flex', alignItems: 'baseline', gap: 16,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5', padding: '0 20px',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
        }}>RL</span>
        <span style={{ fontSize: '3rem', color: '#666' }}>· reinforcement learning</span>
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 24,
          fontWeight: 700, fontSize: '2rem', color: '#000',
        }}
      >
        白話：<span style={{
          background: '#FFD93D', padding: '4px 16px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          marginLeft: 8,
        }}>試錯加獎懲</span>
      </motion.div>

      {/* AlphaGo red stamp drops in last (climax) */}
      <motion.div
        initial={{ y: -200, scale: 0, opacity: 0, rotate: -8 }}
        animate={{ y: 0, scale: 1, opacity: 1, rotate: -2 }}
        transition={{ duration: 0.5, delay: 1.8, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '20%', right: 96,
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '20px 36px',
          fontWeight: 900, fontSize: 32,
        }}
      >
        AlphaGo · 打敗世界圍棋王
      </motion.div>

      {/* Dog handshake placeholder text */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', left: 64, top: '60%',
          fontSize: 64, fontWeight: 900,
        }}
      >
        🐕 ↔ 🤝
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 3: Update `Ch2.jsx`** — STEPS map

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch2Step1 from './Ch2Step1.jsx';
import Ch2Step2 from './Ch2Step2.jsx';
import Ch2Step3 from './Ch2Step3.jsx';

const STEPS = {
  1: Ch2Step1, 2: Ch2Step2, 3: Ch2Step3,
};

export function Ch2() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 2 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
```

- [ ] **Step 4: Build + commit**

```bash
npm run build
git add demo/presentation/src/chapters/ch2-ml-map/
git commit -m "feat(demo): ch2 s2 unsupervised + s3 RL+AlphaGo"
```

---

## Task 3: Ch2Step4 — cliffhanger 問號 720° 旋轉

**Files:**
- Create: `src/chapters/ch2-ml-map/Ch2Step4.jsx`
- Modify: `src/chapters/ch2-ml-map/Ch2.jsx`

- [ ] **Step 1: Create `Ch2Step4.jsx`** (polish — yellow ? sticker with 720° rotation)

```jsx
import { motion } from 'motion/react';

export default function Ch2Step4() {
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
        transition={{ duration: 0.8, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.1,
          textAlign: 'center', maxWidth: 1200,
        }}
      >
        那 ChatGPT 跟 Claude · 又是哪一招？
      </motion.div>

      {/* Yellow ? sticker — drops in from top with 720° spin */}
      <motion.div
        initial={{ y: -300, rotate: 0, scale: 0, opacity: 0 }}
        animate={{ y: 0, rotate: 720, scale: 1.1, opacity: 1 }}
        transition={{ duration: 0.9, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          marginTop: 48,
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
          width: 200, height: 200, borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 120,
        }}
      >
        ?
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch2.jsx STEPS to add `4: Ch2Step4`**

- [ ] **Step 3: Build + commit**

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step4.jsx demo/presentation/src/chapters/ch2-ml-map/Ch2.jsx
git commit -m "feat(demo): ch2 s4 cliffhanger 問號 720° 旋轉"
```

---

## Task 4: ch2 Checkpoint

- [ ] Run `npm run build && npm run test:run` — both must pass
- [ ] Tag: `git tag phase-2-ch2-complete`
- [ ] Walk all 4 steps in browser

---

## 人工 Checkpoint 視覺驗證清單

開 [http://localhost:5173/?ch=2&step=1](http://localhost:5173/?ch=2&step=1)、用左鍵走完：

- [ ] **s1 supervised**: 黑「①/3」kicker、「supervised」mask-reveal、黃「看著答案抄筆記」高亮、右側「老師→題目+答案→學生硬背」三層 sticker
- [ ] **s2 unsupervised**: 「②/3」kicker、「unsupervised」、紫「自己分類整理」、右側「一堆 👕👖→紅黃紫三疊」分類示意
- [ ] **s3 RL + AlphaGo**: 「③/3」、「RL · reinforcement learning」(RL 紅 box)、黃「試錯加獎懲」、右下紅 AlphaGo stamp 從天上砸下、左下 🐕 ↔ 🤝 (狗握手 emoji)
- [ ] **s4 cliffhanger**: 「那 ChatGPT 跟 Claude · 又是哪一招？」hero、中央黃色圓「?」從上方旋轉 720° 砸下

## 想問你的回饋的點

1. **emoji 🐕 / 👕** 暫時用 emoji 代替 Phosphor icon (per asset-production.md ch2 走 Route [A] icon library 但 emoji 視覺上夠突出且零配置) — 接受嗎？或要替換成真正的 Phosphor icon?
2. **s1/s2 右側教學插畫**用「文字 sticker 堆」(老師/題目+答案/學生硬背) 表達流程 — 比起 SVG 線稿是否夠清晰？
3. **AlphaGo stamp 砸下時機** 在 delay 1.8s — 視覺上算 climax 還是太晚 / 太早？
4. **s4 問號 720° 旋轉**動畫是否夠戲劇？要不要加 halftone-burst 微縮版?

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
