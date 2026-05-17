# Phase 3 · Chapter 3 (llm-vs-rl) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

**Goal:** Build ch3 llm-vs-rl — 「LLM = 模仿」vs「我這套 = 自己摸出規則」對比 → cliffhanger「OK 純 RL、第一步找資料」. 3 steps, ~35s, polish FX on s3 (halftone-burst 微縮).

**Architecture:** Standard chapter pattern. First use of `motif/halftone-burst` (polish-tier micro version, radius 60px).

**Source spec:** [outline.md §3](../../../demo/outline.md) · script.md L75-L95

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch3
└── ch3-llm-vs-rl/
    ├── Ch3.jsx
    ├── Ch3Step1.jsx                        # LLM 路線
    ├── Ch3Step2.jsx                        # VS 對比
    └── Ch3Step3.jsx                        # OK 純 RL + halftone-burst polish
```

---

## Task 1: Register Ch3 + Step1 LLM 路線

**Files:**
- Create: `src/chapters/ch3-llm-vs-rl/Ch3.jsx`, `Ch3Step1.jsx`
- Modify: `src/chapters/index.jsx`

- [ ] **Step 1: Create `Ch3.jsx`**

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch3Step1 from './Ch3Step1.jsx';

const STEPS = { 1: Ch3Step1 };

export function Ch3() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 3 · step {stepId}</div></main>;
  }
  return <Step key={stepId} />;
}
```

- [ ] **Step 2: Update `src/chapters/index.jsx`** — add Ch3 import + CHAPTERS entry `3: Ch3`

- [ ] **Step 3: Create `Ch3Step1.jsx`** (LLM 路線 — 左欄 60%)

```jsx
import { motion } from 'motion/react';

export default function Ch3Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', overflow: 'hidden',
    }}>
      {/* Left column wipe-in from left, 60% width */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 0, bottom: 0, left: 0, width: '60%',
          background: 'transparent', padding: 64,
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
        }}
      >
        {/* Background scrolling text grid (subtle low-density) */}
        <div
          aria-hidden="true"
          style={{
            position: 'absolute', inset: 0, overflow: 'hidden',
            opacity: 0.08, fontSize: 14, fontFamily: 'monospace',
            lineHeight: 1.6, padding: 12, color: '#000',
          }}
        >
          {Array.from({ length: 50 }).map((_, i) => (
            <div key={i}>The quick brown fox jumps over the lazy dog 一二三四 ABC </div>
          ))}
        </div>

        {/* "LLM" hero with overshoot stamp */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            fontWeight: 900, fontSize: '10rem', lineHeight: 1, color: '#000',
            position: 'relative', zIndex: 1,
          }}
        >
          LLM
        </motion.div>

        {/* Purple sub-label */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 1.0 }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '8px 20px', alignSelf: 'flex-start',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            fontWeight: 900, fontSize: 22, marginTop: 16, rotate: -2,
            position: 'relative', zIndex: 1,
          }}
        >
          supervised + RLHF
        </motion.div>

        {/* Tagline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.4 }}
          style={{
            marginTop: 32, fontWeight: 700, fontSize: '1.5rem', maxWidth: 600,
            position: 'relative', zIndex: 1,
          }}
        >
          把整個人類網路寫過的東西全部讀一遍
        </motion.div>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 4: Build + commit**

```bash
cd demo/presentation && npm run build
git add demo/presentation/src/chapters/index.jsx demo/presentation/src/chapters/ch3-llm-vs-rl/
git commit -m "feat(demo): ch3 register + s1 LLM 路線"
```

---

## Task 2: Ch3Step2 — VS 對比 (split-screen)

**Files:**
- Create: `Ch3Step2.jsx`
- Modify: `Ch3.jsx`

- [ ] **Step 1: Create `Ch3Step2.jsx`**

```jsx
import { motion } from 'motion/react';

export default function Ch3Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', overflow: 'hidden', display: 'flex',
    }}>
      {/* Left 60% — LLM */}
      <div style={{
        flex: '0 0 60%', padding: 64, position: 'relative',
        display: 'flex', flexDirection: 'column', justifyContent: 'center',
      }}>
        <div style={{ fontWeight: 900, fontSize: '6rem', color: '#000' }}>LLM</div>
        <motion.div
          initial={{ y: -200, scale: 0, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            marginTop: 24, background: '#FF6B6B', color: '#FFFDF5',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 32, rotate: -3, alignSelf: 'flex-start',
          }}
        >
          LLM = 模仿
        </motion.div>
      </div>

      {/* Center 6px divider + VS sticker */}
      <div style={{
        position: 'absolute', left: '60%', top: 0, bottom: 0, width: 6,
        background: '#000',
      }} />
      <motion.div
        initial={{ scale: 0, rotate: 0 }}
        animate={{ scale: 1, rotate: -10 }}
        transition={{ duration: 0.5, delay: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', left: '60%', top: '50%',
          transform: 'translate(-50%, -50%)',
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          width: 120, height: 120, borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 36, zIndex: 5,
        }}
      >
        VS
      </motion.div>

      {/* Right 40% — 我的 AI */}
      <motion.div
        initial={{ clipPath: 'inset(0 0 0 100%)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', padding: 64, position: 'relative',
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '4rem', color: '#000' }}>我的 AI</div>

        {/* Door icon (drawn as black-bordered rect for now) */}
        <div style={{
          marginTop: 24, alignSelf: 'flex-start',
          width: 100, height: 140, background: '#FFFFFF',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          position: 'relative',
        }}>
          <div style={{
            position: 'absolute', right: 12, top: '50%',
            width: 8, height: 8, background: '#000', borderRadius: '50%',
          }} />
        </div>

        <motion.div
          initial={{ y: -200, scale: 0, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            marginTop: 24, background: '#FFD93D', color: '#000',
            padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 24, rotate: 3, alignSelf: 'flex-start',
          }}
        >
          自己摸出規則
        </motion.div>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch3.jsx STEPS to add `2: Ch3Step2`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch3 s2 VS 對比 split-screen`

---

## Task 3: Ch3Step3 — OK 純 RL (with halftone-burst polish)

**Files:**
- Create: `Ch3Step3.jsx`
- Modify: `Ch3.jsx`

- [ ] **Step 1: Create `Ch3Step3.jsx`** (first use of `motif/halftone-burst` polish-tier micro-radius)

```jsx
import { motion } from 'motion/react';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';

export default function Ch3Step3() {
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
          fontWeight: 900, fontSize: '5rem', lineHeight: 1.2,
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
        }}
      >
        <div style={{ position: 'relative', display: 'inline-block' }}>
          <span style={{
            background: '#FF6B6B', color: '#FFFDF5',
            padding: '0 32px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
            rotate: -2, display: 'inline-block',
          }}>OK</span>
          {/* Halftone burst micro on OK highlight finish */}
          <div style={{ position: 'absolute', inset: 0 }}>
            <HalftoneBurst active size={120} centerX="50%" centerY="50%" />
          </div>
        </div>
        <div>所以我要走 <span style={{
          background: '#FFD93D', color: '#000',
          padding: '0 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          rotate: 2, display: 'inline-block',
        }}>純 RL</span></div>
        <div style={{ fontSize: '3rem', marginTop: 32 }}>第一步是找資料</div>
      </motion.div>
    </main>
  );
}
```

Note: HalftoneBurst is sized 120px instead of 600px for polish-tier micro variant (per outline-visual.md §8.4).

- [ ] **Step 2: Update Ch3.jsx STEPS to add `3: Ch3Step3`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch3 s3 OK 純 RL + halftone-burst polish`

---

## Task 4: ch3 Checkpoint

```bash
npm run build && npm run test:run  # 19/19 expected
git tag phase-3-ch3-complete
```

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 LLM 路線**: 左 60% wipe-in、超大「LLM」字、紫「supervised+RLHF」、底下「整個人類網路」標語、背景低密度文字 grid
- [ ] **s2 VS 對比**: 右 40% wipe-in 出現「我的 AI」+ door icon、中央 VS 黃圓 sticker、左欄「LLM = 模仿」紅 stamp + 右欄「自己摸出規則」黃 stamp
- [ ] **s3 OK 純 RL**: 「OK」紅高亮 + 「純 RL」黃高亮 mask-reveal、OK 出現瞬間有小型 halftone-burst（120px radius）放射 → 暗示「決定下了」

## 想問你的回饋的點

1. **背景滾動文字 grid (s1)**: 用「The quick brown fox...一二三四 ABC」隨機填充、opacity 0.08。要不要換成 LLM 訓練語料風（"the cat sat on the mat..." / 中文常見句）？
2. **Door icon (s2)**: 用 CSS rectangle + 黑色圓點代表門把、視覺粗略。要走 Phosphor `Door` 真 icon 嗎？(現在是文字方塊近似)
3. **VS sticker 旋轉 -10°**: 視覺上偏歪、是否要降到 -5°？
4. **s3 halftone-burst 120px**: 對 polish 級夠醒目嗎？太小看不到的話可放大到 200px

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
