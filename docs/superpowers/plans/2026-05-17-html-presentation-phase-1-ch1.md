# HTML Presentation · Phase 1 — Chapter 1 (coldopen) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first narrative chapter "coldopen" — 8 steps spanning the opening 心虛 sticker, psychology-major reveal, sudoku-AI subject reveal, MRT-scene daydream sequence (4 steps), and the BOOM punchline with light A+C climax.

**Architecture:** Switch App.jsx from the Phase 0 Sandbox to a chapter router that selects on `chapterId`. Each chapter has its own folder under `src/chapters/`. ScreenShake moves from inside Sandbox to a top-level wrapper in App.jsx so shake works across all chapters; `triggerShake()` is exposed via `PresentationContext` so any step can call it. Each step is one self-contained `.jsx` component that reads `stepId` / `beatIndex` from context and renders accordingly. Re-mount on `stepId` change (via React `key`) so initial animations fire fresh on each step entry.

**Tech Stack:** React 19 / Vite 8 / Tailwind v4 / Motion 11+ (animations + AnimatePresence) — already installed in Phase 0.

**Source spec:** [docs/superpowers/specs/2026-05-17-html-presentation-build-flow-design.md](../specs/2026-05-17-html-presentation-build-flow-design.md)
**Narrative source:** [demo/outline.md](../../../demo/outline.md) §1 coldopen (8 steps)
**Visual source:** [demo/outline-visual.md](../../../demo/outline-visual.md) §6 (ch1 palette) · §7 motif library · §8 climax
**口播 source of truth:** [demo/script.md](../../../demo/script.md) L1, L5, L9, L15, L19, L21, L25, L29-L37 (do NOT modify)

---

## File Structure

```
demo/presentation/
├── src/
│   ├── App.jsx                                # MODIFY: replace Sandbox route with ChapterRouter
│   ├── state/
│   │   └── PresentationContext.jsx             # MODIFY: add shakeRef + triggerShake to context
│   └── chapters/
│       ├── index.jsx                           # CREATE: ChapterRouter dispatches on chapterId
│       └── ch1-coldopen/
│           ├── Ch1.jsx                          # CREATE: ch1 entry, selects step component on stepId
│           ├── Ch1Step1.jsx                     # CREATE: 心虛開場
│           ├── Ch1Step2.jsx                     # CREATE: 心理學系畢業 + 敬請期待
│           ├── Ch1Step3.jsx                     # CREATE: 主題揭曉「訓 練 AI 解 數 獨」
│           ├── Ch1Step4.jsx                     # CREATE: 捷運上正大光明看正妹
│           ├── Ch1Step5.jsx                     # CREATE: Code Bullet flappy bird 靈感
│           ├── Ch1Step6.jsx                     # CREATE: 繼續發呆（喜劇延續拍）
│           ├── Ch1Step7.jsx                     # CREATE: 當兵沒手機解數獨
│           └── Ch1Step8.jsx                     # CREATE: BOOM ★ punchline (3-beat)
```

**Phase 0 components used (do NOT modify):**
- `src/state/usePresentation.js` — beat advance/retreat hook
- `src/components/Sticker.jsx` — sticker primitive
- `src/components/Hero.jsx` — hero primitive
- `src/components/AssetPlaceholder.jsx` — placeholder for missing [E] SVGs
- `src/motifs/BoomDoubleRing.jsx` — used in ch1 s8 (first use)
- `src/motifs/YellowHighlight.jsx` — used in ch1 s8 punchline (first use)
- `src/motifs/ScreenShake.jsx` — wraps app for climax A
- `src/climax/useClimax.js` — climax orchestrator (ch1 s8 uses A+C light)
- `src/layers/GlobalGrain.jsx`, `HalftoneBg.jsx`, `ChapterTint.jsx`, `AmbientShapes.jsx`, `FadeBridge.jsx` — global layers, mounted at App level

---

## Module A · Chapter Router + Shake Context

### Task 1: Wire ChapterRouter + ScreenShake-at-app-level + shakeRef context

**Files:**
- Modify: `demo/presentation/src/state/PresentationContext.jsx`
- Modify: `demo/presentation/src/App.jsx`
- Create: `demo/presentation/src/chapters/index.jsx`
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx`

This task switches the app from "always show Sandbox" to "render a chapter component based on chapterId". It also moves `<ScreenShake>` from Sandbox to App.jsx so all chapters can trigger screen shake via a context-provided `triggerShake()` function.

- [ ] **Step 1: Add shakeRef + triggerShake to `PresentationContext.jsx`**

Read the existing file first, then replace its content with:

```jsx
import { createContext, useContext, useRef, useState } from 'react';
import { usePresentation } from './usePresentation.js';
import { useUrlSync, parseUrl } from './useUrlSync.js';
import { useKeyMouseControls } from './useKeyMouseControls.js';

const Ctx = createContext(null);

export function PresentationProvider({ children }) {
  const initial = parseUrl(window.location.href);
  const pres = usePresentation(initial);
  const [presenter, setPresenter] = useState(initial.presenter);
  const [progressVisible, setProgressVisible] = useState(false);

  // Shared shake controller — ScreenShake (mounted in App.jsx) attaches its imperative
  // handle to this ref. Any chapter step can call triggerShake() via context.
  const shakeRef = useRef(null);
  const triggerShake = () => shakeRef.current?.play();

  useUrlSync(pres, presenter);
  useKeyMouseControls({
    advance: pres.advance,
    retreat: pres.retreat,
    toggleProgress: () => setProgressVisible(v => !v),
  });

  return (
    <Ctx.Provider value={{
      ...pres,
      presenter, setPresenter,
      progressVisible, setProgressVisible,
      shakeRef,
      triggerShake,
    }}>
      {children}
    </Ctx.Provider>
  );
}

export function usePresentationContext() {
  const c = useContext(Ctx);
  if (!c) throw new Error('usePresentationContext must be used inside PresentationProvider');
  return c;
}
```

- [ ] **Step 2: Create `src/chapters/ch1-coldopen/Ch1.jsx`** (placeholder dispatcher — step files come in later tasks)

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';

// Step component lookup — each step file exports default component.
// Placeholder mapping; real Ch1StepN files added in Tasks 2-9.
const STEPS = {
  // Filled in by later tasks
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
      </main>
    );
  }
  // Re-mount on step change so entrance animations fire fresh.
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Create `src/chapters/index.jsx`** (ChapterRouter)

```jsx
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { Ch1 } from './ch1-coldopen/Ch1.jsx';

const CHAPTERS = {
  1: Ch1,
  // 2-9 added in later phases
};

export function ChapterRouter() {
  const { chapterId } = usePresentationContext();
  const Chapter = CHAPTERS[chapterId];
  if (!Chapter) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch {chapterId} (not implemented)</div>
        <div style={{ marginTop: 16, color: '#666' }}>Phase 1 implements ch 1 only. Use the chapter nav (hover top-right) to jump back to ch 1.</div>
      </main>
    );
  }
  return <Chapter />;
}
```

- [ ] **Step 4: Update `src/App.jsx`** — replace Sandbox with ChapterRouter; move ScreenShake to App level

Replace `src/App.jsx`:

```jsx
import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';
import { ChapterRouter } from './chapters/index.jsx';
import { ProgressBar } from './components/ProgressBar.jsx';
import { ChapterNav } from './components/ChapterNav.jsx';
import { BeatIndicator } from './components/BeatIndicator.jsx';
import { PresenterPanel } from './components/PresenterPanel.jsx';
import { FadeBridge } from './layers/FadeBridge.jsx';
import { GlobalGrain } from './layers/GlobalGrain.jsx';
import { HalftoneBg } from './layers/HalftoneBg.jsx';
import { ChapterTint } from './layers/ChapterTint.jsx';
import { AmbientShapes } from './layers/AmbientShapes.jsx';
import { ScreenShake } from './motifs/ScreenShake.jsx';

function Frame() {
  const { chapterId, shakeRef } = usePresentationContext();
  return (
    <ScreenShake ref={shakeRef}>
      <AmbientShapes chapterId={chapterId} />
      <GlobalGrain />
      <HalftoneBg />
      <ChapterTint chapterId={chapterId} />
      <ChapterRouter />
      <FadeBridge chapterId={chapterId} />
      <BeatIndicator />
      <ProgressBar />
      <ChapterNav />
      <PresenterPanel />
    </ScreenShake>
  );
}

export default function App() {
  return (
    <PresentationProvider>
      <Frame />
    </PresentationProvider>
  );
}
```

Note: the Sandbox page is still in `src/pages/Sandbox.jsx` and can be re-mounted later for development — not deleted, just not routed by default.

- [ ] **Step 5: Build verification**

```bash
cd demo/presentation
npm run build
```

Expected: success. Build output should still be ~358 kB JS (no large additions; Sandbox.jsx is still in source but no longer in the import graph for the main entry).

- [ ] **Step 6: Test suite still passes**

```bash
npm run test:run
```

Expected: 19/19 tests passing (no behavior changed in tested modules).

- [ ] **Step 7: Visual smoke test**

`npm run dev`, open `http://localhost:5173/?ch=1&step=1`. Should see "ch 1 · step 1 · (component not yet implemented)". Click left mouse to advance — should see step 2 placeholder, etc.

- [ ] **Step 8: Commit**

```bash
git add demo/presentation/src/state/PresentationContext.jsx demo/presentation/src/App.jsx demo/presentation/src/chapters/index.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): chapter router + ScreenShake at app level + shake context"
```

---

## Module B · 7 single-beat narrative steps

### Task 2: Ch1Step1 — 心虛開場

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step1.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx` (register Step1 in STEPS map)
- Modify: `demo/presentation/src/index.css` (add 心虛 sticker float keyframe)

This step opens the show: full-screen 「心 虛」 sticker, period-report badge, apologetic caption.

Per [outline.md ch1 s1](../../../demo/outline.md):
- 顯示內容: 全屏「心 虛」巨字 sticker（紅底、6px 黑邊、16px hard shadow、微旋轉 -3°）+ 角標「期中報告」黃 sticker + 字幕「報告太不正經、請各位同學和老師多包涵」
- 進場: 黑屏 → cream 紙質淡入(400ms) → 心虛 sticker scale 0.7→1 + rotate -3° (overshoot) → 字幕從左 mask-reveal
- 持續微動: 心虛 sticker ±4px 4s ease-in-out infinite
- 口播對應: script.md L1

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step1.jsx`**

```jsx
import { motion } from 'motion/react';

export default function Ch1Step1() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Black → cream fade overlay (one-shot when this step mounts) */}
      <motion.div
        aria-hidden="true"
        initial={{ opacity: 1 }}
        animate={{ opacity: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          position: 'fixed', inset: 0, zIndex: 70,
          background: '#000', pointerEvents: 'none',
        }}
      />

      {/* 期中報告 badge top-left */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 48, left: 48,
          background: '#FFD93D', color: '#000',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          padding: '12px 24px', rotate: -3,
          fontWeight: 900, fontSize: 18,
        }}
      >
        期中報告
      </motion.div>

      {/* 心虛 hero sticker — outer wrapper handles entrance scale/opacity,
          inner does infinite float micro-motion. Nested so the two compose. */}
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ display: 'inline-block', rotate: -3 }}
      >
        <motion.div
          animate={{ y: [0, -4, 0, 4, 0] }}
          transition={{ duration: 4, ease: 'easeInOut', repeat: Infinity, delay: 1 }}
          style={{
            background: '#FF6B6B', color: '#FFFDF5',
            border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
            padding: '64px 96px',
            fontWeight: 900, fontSize: '8rem', letterSpacing: '0.1em',
          }}
        >
          心 虛
        </motion.div>
      </motion.div>

      {/* Caption — mask-reveal from left */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.2, ease: 'easeOut' }}
        style={{
          marginTop: 48,
          fontSize: 24, fontWeight: 700, color: '#000',
          maxWidth: 720, textAlign: 'center', lineHeight: 1.4,
        }}
      >
        報告太不正經、請各位同學和老師多包涵
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step1 in `src/chapters/ch1-coldopen/Ch1.jsx`**

Update the `STEPS` map:

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch1Step1 from './Ch1Step1.jsx';

const STEPS = {
  1: Ch1Step1,
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Build verification**

```bash
cd demo/presentation && npm run build
```

Expected: build succeeds.

- [ ] **Step 4: Visual verification**

`npm run dev`, open `http://localhost:5173/?ch=1&step=1`. Expected:
- Black screen briefly (~0.4s), fades to cream
- Big red 「心 虛」 sticker scales in from 0.7 with overshoot bounce
- Yellow 「期中報告」 badge stamps in top-left
- 「報告太不正經、請各位同學和老師多包涵」 caption masks in left-to-right
- After settling, 心虛 sticker gently floats up/down (±4px loop)

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step1.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s1 心虛開場"
```

---

### Task 3: Ch1Step2 — 心理學系畢業 + 敬請期待

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step2.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx` (register Step2)

Per [outline.md ch1 s2](../../../demo/outline.md):
- 顯示內容: 「心 理 學 系 · 畢業」card hero（白底、6px 黑邊、12px shadow、微旋轉 -2°）+ 紅色箭頭 + 黃色高亮「敬請期待」sticker（伏筆 RL/腦科學/plasticity）
- 進場: 主 card 從右下 translateY + rotate (overshoot) → 箭頭從卡片左側 stroke-draw → 「敬請期待」黃 sticker 從右側 scale 0→1 stamp
- 口播對應: script.md L5

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step2.jsx`**

```jsx
import { motion } from 'motion/react';

export default function Ch1Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 32, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Psychology degree card — slide in from bottom-right with overshoot */}
      <motion.div
        initial={{ x: 200, y: 80, scale: 0.8, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFFFF', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '48px 64px', rotate: -2,
          fontWeight: 900, fontSize: '3.75rem', lineHeight: 1.1,
          textAlign: 'center',
        }}
      >
        心 理 學 系
        <div style={{ fontSize: '1.875rem', marginTop: 12, color: '#000' }}>· 畢業</div>
      </motion.div>

      {/* Red arrow drawn by stroke-dasharray animation */}
      <motion.svg
        width="120" height="40" viewBox="0 0 120 40"
        style={{ overflow: 'visible' }}
      >
        <motion.path
          d="M 10 20 L 100 20 M 90 10 L 100 20 L 90 30"
          fill="none" stroke="#FF6B6B" strokeWidth="6" strokeLinecap="square" strokeLinejoin="miter"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.6, ease: 'easeOut' }}
        />
      </motion.svg>

      {/* 敬請期待 yellow stamp — scales in from 0 */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 1.1, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '32px 48px', rotate: 3,
          fontWeight: 900, fontSize: '2.25rem',
        }}
      >
        敬請期待
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step2 in `Ch1.jsx`**

Add to `STEPS` map (full updated file):

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch1Step1 from './Ch1Step1.jsx';
import Ch1Step2 from './Ch1Step2.jsx';

const STEPS = {
  1: Ch1Step1,
  2: Ch1Step2,
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) {
    return (
      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
        <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
      </main>
    );
  }
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Build + visual check**

```bash
npm run build
```

`?ch=1&step=2` should show: white 心理學系 card stamping in from right-bottom with rotation, red arrow drawing in, yellow 敬請期待 stamp scaling in last.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step2.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s2 心理學系畢業 + 敬請期待"
```

---

### Task 4: Ch1Step3 — 主題揭曉「訓 練 AI 解 數 獨」

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step3.jsx`
- Modify: `Ch1.jsx`

Per [outline.md ch1 s3](../../../demo/outline.md):
- 顯示內容: 上方 kicker「期中主題」黑底 cream 字 + 中央 cinematic hero「訓 練 AI 解 數 獨」（AI 紅底、解數獨黃底兩塊強調 box、text-stroke 描邊樣式）+ 四個漂浮裝飾形狀（紫方塊 / 黃星旋轉 / 紅圓 hard shadow / 描邊問號）
- 進場: kicker 從左 slide-in → hero scale 0.85 + letter-spacing 0.1em → scale 1 + letter-spacing -0.04em (overshoot 720ms) → 4 裝飾物 stagger 從各角飛入
- 持續微動: 黃星 spin-slow 12s、紫方塊 float ±16px 4s
- 口播對應: script.md L9

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step3.jsx`**

```jsx
import { motion } from 'motion/react';

export default function Ch1Step3() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Kicker: 期中主題 */}
      <motion.div
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '12px 28px',
          fontWeight: 900, fontSize: 20, letterSpacing: '0.1em',
          marginBottom: 48,
        }}
      >
        期中主題
      </motion.div>

      {/* Hero: 訓 練 [AI] 解 數 獨, with red & yellow emphasis boxes */}
      <motion.div
        initial={{ scale: 0.85, letterSpacing: '0.1em', opacity: 0 }}
        animate={{ scale: 1, letterSpacing: '-0.04em', opacity: 1 }}
        transition={{ duration: 0.72, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          fontWeight: 900, fontSize: '6rem', lineHeight: 1.05,
          display: 'flex', alignItems: 'center', gap: 16,
          textAlign: 'center',
        }}
      >
        <span style={{ WebkitTextStroke: '2px black', color: 'transparent' }}>訓 練</span>
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', rotate: -2,
        }}>AI</span>
        <span style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', rotate: 2,
        }}>解 數 獨</span>
      </motion.div>

      {/* 4 floating decoratives — 角落動 */}
      <motion.div
        initial={{ x: -120, y: -120, opacity: 0, scale: 0 }}
        animate={{ x: 0, y: 0, opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: '12%', left: '8%',
          width: 64, height: 64, background: '#C4B5FD',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          rotate: 8,
        }}
      />
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 12, ease: 'linear', repeat: Infinity }}
        style={{
          position: 'absolute', top: '14%', right: '10%',
          width: 64, height: 64,
        }}
      >
        <motion.svg
          width="64" height="64" viewBox="0 0 64 64"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.1, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <polygon points="32,4 38,24 60,24 42,36 50,58 32,46 14,58 22,36 4,24 26,24"
            fill="#FFD93D" stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
        </motion.svg>
      </motion.div>
      <motion.div
        initial={{ scale: 0, opacity: 0, x: -120, y: 120 }}
        animate={{ scale: 1, opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 0.5, delay: 1.2, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '10%',
          width: 64, height: 64, borderRadius: '50%', background: '#FF6B6B',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}
      />
      <motion.div
        initial={{ scale: 0, opacity: 0, x: 120, y: 120 }}
        animate={{ scale: 1, opacity: 1, x: 0, y: 0 }}
        transition={{ duration: 0.5, delay: 1.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '12%', right: '8%',
          width: 64, height: 64,
          border: '4px solid #000',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 36, rotate: -8,
          background: 'transparent', color: '#000',
        }}
      >
        ?
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step3 in `Ch1.jsx`**

Update STEPS:

```jsx
import Ch1Step3 from './Ch1Step3.jsx';
// ... existing imports

const STEPS = {
  1: Ch1Step1,
  2: Ch1Step2,
  3: Ch1Step3,
};
```

- [ ] **Step 3: Build + visual**

`npm run build`, then `?ch=1&step=3`. Expected: "期中主題" black tag from left, then big "訓 練 AI 解 數 獨" hero with red AI box + yellow 解數獨 box + text-stroke 訓練, then 4 decoratives flying into corners. Yellow star spins slowly forever; other 3 stay put.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step3.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s3 主題揭曉 訓練 AI 解數獨"
```

---

### Task 5: Ch1Step4 — 捷運上正大光明看正妹

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx`
- Modify: `Ch1.jsx`
- Modify: `demo/presentation/TODO.md` (add MRT window TODO entry)

Per [outline.md ch1 s4](../../../demo/outline.md):
- 顯示內容: 過場字幕「靈感哪來呢？某天捷運上⋯」+ 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop）+ 第一張 sticker「正妹發呆中」黃底 cloud 樣式（左下、微旋轉 -4°）
- 進場: 捷運背景 fade-in(300ms) → 字幕從上 fade-down → 窗景 stamp-in → 正妹 sticker 從左下 stamp-in (stagger 240ms)
- 口播對應: script.md L15

The MRT window SVG is a `[E]` asset that's not built yet — use `<AssetPlaceholder>` per Phase 0 placeholder strategy.

- [ ] **Step 1: Append MRT placeholder to `demo/presentation/TODO.md`**

Read the existing TODO.md and append:

```markdown
- ch1 s4-s7 — [E] 捷運窗景 SVG — 紫底窗 + 黑邊、車廂線條 backdrop (used in MRT scene steps 4-7)
```

- [ ] **Step 2: Create `src/chapters/ch1-coldopen/Ch1Step4.jsx`**

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Caption from top */}
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 64, left: 0, right: 0,
          textAlign: 'center',
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        靈感哪來呢？某天捷運上⋯
      </motion.div>

      {/* MRT window centered (placeholder for [E] SVG) */}
      <motion.div
        initial={{ scale: 0.85, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <AssetPlaceholder
          type="[E]"
          width={720}
          height={400}
          todo="ch1 s4-s7 捷運窗景 SVG (紫底窗 + 黑邊 + 車廂線條 backdrop)"
        />
      </motion.div>

      {/* 正妹 sticker bottom-left cloud-style */}
      <motion.div
        initial={{ x: -200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '8%',
          background: '#FFD93D', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', rotate: -4,
          fontWeight: 900, fontSize: 24,
          borderRadius: 24,  // cloud style: pill-y corners (still hard-edged via border style)
        }}
      >
        正妹發呆中
      </motion.div>
    </main>
  );
}
```

Note: `borderRadius: 24` is intentional cloud-bubble feel — the rest of the Neo-brutalism aesthetic is preserved (4px border, hard shadow, no soft drop-shadow). The web_style.md "rounded-md forbidden" rule applies to standard cards/buttons; this is a one-off cloud sticker for narrative effect.

- [ ] **Step 3: Register Step4 in `Ch1.jsx`** (add to STEPS)

```jsx
import Ch1Step4 from './Ch1Step4.jsx';
// ...
const STEPS = { 1: Ch1Step1, 2: Ch1Step2, 3: Ch1Step3, 4: Ch1Step4 };
```

- [ ] **Step 4: Build + visual**

`npm run build`, then `?ch=1&step=4`. Expected: "靈感哪來呢" caption from top, MRT placeholder (red dashed border with ⚠️ TODO) stamping in center, yellow 正妹發呆中 sticker bouncing in from bottom-left.

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx demo/presentation/TODO.md
git commit -m "feat(demo): ch1 s4 捷運看正妹 + MRT window TODO"
```

---

### Task 6: Ch1Step5 — Code Bullet flappy bird 靈感

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step5.jsx`
- Modify: `Ch1.jsx`

Per [outline.md ch1 s5](../../../demo/outline.md):
- 顯示內容: 捷運背景延續 + 第一張 sticker（正妹左下）+ 第二張 sticker「Code Bullet · flappy bird」紫底（右上、微旋轉 3°）+ 思考氣球線從正妹 → flappy bird 虛線連接
- 進場: 左鍵觸發 → 第二張 sticker 從右上 stamp-in(240ms) + 思考線 stroke-draw(600ms)
- 口播對應: script.md L19

Reuse MRT window + 正妹 sticker (use `initial={false}` so they appear instantly without re-animating). Add the new flappy-bird sticker + dashed thought line connecting the two stickers.

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step5.jsx`**

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* MRT window (persisted, no entrance animation) */}
      <div style={{ opacity: 1 }}>
        <AssetPlaceholder
          type="[E]"
          width={720}
          height={400}
          todo="ch1 s4-s7 捷運窗景 SVG"
        />
      </div>

      {/* 正妹 sticker persisted */}
      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
        background: '#FFD93D', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(-4deg)',
        fontWeight: 900, fontSize: 24,
        borderRadius: 24,
      }}>
        正妹發呆中
      </div>

      {/* NEW: Code Bullet · flappy bird sticker top-right, scales in */}
      <motion.div
        initial={{ x: 200, y: -100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: '14%', right: '8%',
          background: '#C4B5FD', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', rotate: 3,
          fontWeight: 900, fontSize: 22,
          lineHeight: 1.2,
        }}
      >
        Code Bullet
        <div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div>
      </motion.div>

      {/* Thought-bubble dashed line from bottom-left to top-right */}
      <svg
        style={{
          position: 'absolute', inset: 0, width: '100%', height: '100%',
          pointerEvents: 'none', zIndex: 25,
        }}
      >
        <motion.path
          d="M 15% 78% Q 50% 35%, 88% 22%"
          fill="none" stroke="#000" strokeWidth="3"
          strokeDasharray="8 8"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
        />
      </svg>
    </main>
  );
}
```

Note: SVG `d` with `%` coordinates is non-standard; the SVG renders inside viewBox-less mode, so % is interpreted as user units which won't be correct. Use absolute pixel coords instead by computing from `100% × 100%` element dimensions. For now use the simplest workaround: render with viewBox and pixel coords.

Actually let me fix that — SVG paths don't accept `%`. Replace the path with viewBox-based coords:

Replace the entire `<svg>` block above with:

```jsx
      {/* Thought-bubble dashed line — using viewBox so % becomes parameterized */}
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{
          position: 'absolute', inset: 0, width: '100%', height: '100%',
          pointerEvents: 'none', zIndex: 25,
        }}
      >
        <motion.path
          d="M 15 78 Q 50 35, 88 22"
          fill="none" stroke="#000" strokeWidth="0.6"
          strokeDasharray="1.5 1.5"
          vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
        />
      </svg>
```

The viewBox `0 0 100 100` with `preserveAspectRatio="none"` lets us use percentages-as-coords (15 ≈ 15% of width). `vectorEffect="non-scaling-stroke"` keeps stroke width 3px regardless of element size; we set strokeWidth=0.6 because the viewBox transform would otherwise scale it.

Wait — with `vectorEffect="non-scaling-stroke"` set, the strokeWidth ignores the viewBox scale and uses user-space units (pixels). So `strokeWidth="3"` would be 3px. Let me use that:

Final SVG block (use this, not the two earlier versions):

```jsx
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{
          position: 'absolute', inset: 0, width: '100%', height: '100%',
          pointerEvents: 'none', zIndex: 25,
        }}
      >
        <motion.path
          d="M 15 78 Q 50 35, 88 22"
          fill="none" stroke="#000"
          strokeWidth="3" strokeDasharray="8 8"
          vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
        />
      </svg>
```

- [ ] **Step 2: Register Step5 in `Ch1.jsx`**

```jsx
import Ch1Step5 from './Ch1Step5.jsx';
// ...
const STEPS = { 1: Ch1Step1, 2: Ch1Step2, 3: Ch1Step3, 4: Ch1Step4, 5: Ch1Step5 };
```

- [ ] **Step 3: Build + visual**

`npm run build`, then `?ch=1&step=5`. Expected: same MRT background + 正妹 sticker (no re-animation), plus new purple Code Bullet sticker stamping in from top-right, plus dashed black line drawing from bottom-left to top-right.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step5.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s5 Code Bullet flappy bird + 思考線"
```

---

### Task 7: Ch1Step6 — 繼續發呆（喜劇延續拍）

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step6.jsx`
- Modify: `Ch1.jsx`

Per [outline.md ch1 s6](../../../demo/outline.md):
- 顯示內容: 捷運背景與兩 sticker 維持不動 + 中央正妹 sticker 上方「⋯⋯」省略號氣球（cream 底、黑邊框、輕微浮動）+ 角標小字「然後我繼續發呆⋯」
- 類型: cinematic + interactive
- 進場: 「⋯⋯」氣球 stamp-in(300ms) + 緩慢 pulse(1s ease-in-out infinite)
- 氣質: 喜劇半拍、給觀眾笑點 + 演講者口語停頓
- 口播對應: script.md L21

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step6.jsx`**

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step6() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div>
        <AssetPlaceholder type="[E]" width={720} height={400} todo="ch1 s4-s7 捷運窗景 SVG" />
      </div>

      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
        background: '#FFD93D', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(-4deg)',
        fontWeight: 900, fontSize: 24,
        borderRadius: 24,
      }}>
        正妹發呆中
      </div>

      <div style={{
        position: 'absolute', top: '14%', right: '8%',
        background: '#C4B5FD', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(3deg)',
        fontWeight: 900, fontSize: 22,
        lineHeight: 1.2,
      }}>
        Code Bullet
        <div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div>
      </div>

      {/* NEW: ⋯⋯ ellipsis bubble above 正妹 — stamp-in + pulse */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1, 1], opacity: 1 }}
        transition={{
          scale: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
          opacity: { duration: 0.3 },
        }}
        style={{
          position: 'absolute', bottom: '34%', left: '12%',
        }}
      >
        <motion.div
          animate={{ scale: [1, 1.08, 1] }}
          transition={{ duration: 1, ease: 'easeInOut', repeat: Infinity }}
          style={{
            background: '#FFFDF5', color: '#000',
            border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
            padding: '12px 24px', borderRadius: 32,
            fontWeight: 900, fontSize: 32, letterSpacing: '0.2em',
          }}
        >
          ⋯⋯
        </motion.div>
      </motion.div>

      {/* Bottom-right small caption */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{
          position: 'absolute', bottom: 32, right: 32,
          fontSize: 18, fontWeight: 700, color: '#666',
        }}
      >
        然後我繼續發呆⋯
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step6 in `Ch1.jsx`**

```jsx
import Ch1Step6 from './Ch1Step6.jsx';
// ...
const STEPS = { 1: Ch1Step1, 2: Ch1Step2, 3: Ch1Step3, 4: Ch1Step4, 5: Ch1Step5, 6: Ch1Step6 };
```

- [ ] **Step 3: Build + visual**

`?ch=1&step=6`. Expected: same scene as step 5, with new "⋯⋯" cream bubble above 正妹 sticker that pulses slowly, plus "然後我繼續發呆⋯" small text at bottom-right.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step6.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s6 繼續發呆 喜劇延續拍"
```

---

### Task 8: Ch1Step7 — 當兵沒手機解數獨

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step7.jsx`
- Modify: `Ch1.jsx`

Per [outline.md ch1 s7](../../../demo/outline.md):
- 顯示內容: 捷運背景延續 + 三張 sticker（正妹左下 + flappy bird 右上 + 紅底白字「沒手機·解數獨」右下、微旋轉 2°）
- 進場: 第三張 sticker 從右下 stamp-in(240ms)、其他不重畫
- 口播對應: script.md L25

The ⋯⋯ bubble from step 6 is gone (back to "scene with 3 stickers").

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step7.jsx`**

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step7() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      <div>
        <AssetPlaceholder type="[E]" width={720} height={400} todo="ch1 s4-s7 捷運窗景 SVG" />
      </div>

      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
        background: '#FFD93D', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(-4deg)',
        fontWeight: 900, fontSize: 24,
        borderRadius: 24,
      }}>
        正妹發呆中
      </div>

      <div style={{
        position: 'absolute', top: '14%', right: '8%',
        background: '#C4B5FD', color: '#000',
        border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
        padding: '16px 28px', transform: 'rotate(3deg)',
        fontWeight: 900, fontSize: 22,
        lineHeight: 1.2,
      }}>
        Code Bullet
        <div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div>
      </div>

      {/* NEW: 沒手機·解數獨 sticker bottom-right */}
      <motion.div
        initial={{ x: 200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', right: '8%',
          background: '#FF6B6B', color: '#FFFDF5',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', rotate: 2,
          fontWeight: 900, fontSize: 24,
        }}
      >
        沒手機·解數獨
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step7 in `Ch1.jsx`**

```jsx
import Ch1Step7 from './Ch1Step7.jsx';
// ...
const STEPS = { 1: Ch1Step1, 2: Ch1Step2, 3: Ch1Step3, 4: Ch1Step4, 5: Ch1Step5, 6: Ch1Step6, 7: Ch1Step7 };
```

- [ ] **Step 3: Build + visual**

`?ch=1&step=7`. Expected: same MRT background + 正妹 + Code Bullet, plus new red "沒手機·解數獨" sticker stamping in from bottom-right. ⋯⋯ bubble is gone.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step7.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s7 當兵沒手機解數獨"
```

---

## Module C · Multi-beat BOOM punchline

### Task 9: Ch1Step8 — BOOM ★ punchline (3-beat with light A+C climax)

**Files:**
- Create: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step8.jsx`
- Modify: `Ch1.jsx`

Per [outline.md ch1 s8](../../../demo/outline.md):
- 顯示內容: 三 sticker 抖動 → 雙圈爆破 → 中央 cream boom card「訓 練 AI 解 數 獨」→ 下方 punchline 黃底高亮「靈感就是這麼莫名其妙地蹦出來」
- placeholder: 下方黃底高亮 box 預留位、內容 hold 到 beat 3 (= beatIndex 2)
- Motif: motif/boom-double-ring (首發) · motif/yellow-highlight (首發)
- Climax 火力 輕量: A+C (screen shake + overshoot on punchline box)

Beat structure (from beat-manifest.js):
- beatIndex 0 — `boom-burst` [click]: 三 sticker 背景抖動 + 雙圈爆破覆蓋
- beatIndex 1 — `boom-card` [auto, 400ms]: 中央 cream boom card scale 0.8→1 overshoot
- beatIndex 2 — `punchline-reveal` [click]: 黃底空 box 填入「靈感就是這麼 *莫名其妙* 地蹦出來」+ A+C climax

Auto-advance: when component is at beatIndex 0, schedule a setTimeout 400ms to call `advance()`. This satisfies the `type: 'auto', autoDelayMs: 400` spec for beat 1.

- [ ] **Step 1: Create `src/chapters/ch1-coldopen/Ch1Step8.jsx`**

```jsx
import { useEffect, useRef } from 'react';
import { motion, useAnimate } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { BoomDoubleRing } from '../../motifs/BoomDoubleRing.jsx';
import { YellowHighlight } from '../../motifs/YellowHighlight.jsx';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';

export default function Ch1Step8() {
  const { beatIndex, advance, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const [stickersScope, animateStickers] = useAnimate();
  const firedClimaxRef = useRef(false);

  // Auto-advance from beat 0 → beat 1 after 400ms.
  useEffect(() => {
    if (beatIndex === 0) {
      const t = setTimeout(() => advance(), 400);
      return () => clearTimeout(t);
    }
  }, [beatIndex, advance]);

  // Beat 0 entry: shake the 3 background stickers (150ms).
  useEffect(() => {
    if (beatIndex === 0) {
      animateStickers(stickersScope.current,
        { x: [0, 4, -4, 2, -2, 0], y: [0, 2, -2, 1, -1, 0] },
        { duration: 0.15 }
      );
    }
  }, [beatIndex, animateStickers, stickersScope]);

  // Beat 2 (punchline reveal): trigger A (screen shake) + C (overshoot on punchline box).
  // C is implemented as scale keyframes on the punchline wrapper below.
  useEffect(() => {
    if (beatIndex === 2 && !firedClimaxRef.current) {
      firedClimaxRef.current = true;
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
      {/* 3 background stickers + MRT — wrapped in stickersScope for shake animation */}
      <div ref={stickersScope} style={{
        position: 'absolute', inset: 0, opacity: 0.35,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <AssetPlaceholder type="[E]" width={720} height={400} todo="ch1 s8 捷運背景" />
        <div style={{
          position: 'absolute', bottom: '14%', left: '8%',
          background: '#FFD93D', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', transform: 'rotate(-4deg)',
          fontWeight: 900, fontSize: 24, borderRadius: 24,
        }}>正妹發呆中</div>
        <div style={{
          position: 'absolute', top: '14%', right: '8%',
          background: '#C4B5FD', color: '#000',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', transform: 'rotate(3deg)',
          fontWeight: 900, fontSize: 22, lineHeight: 1.2,
        }}>Code Bullet<div style={{ fontSize: 16, marginTop: 4 }}>· flappy bird</div></div>
        <div style={{
          position: 'absolute', bottom: '14%', right: '8%',
          background: '#FF6B6B', color: '#FFFDF5',
          border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '16px 28px', transform: 'rotate(2deg)',
          fontWeight: 900, fontSize: 24,
        }}>沒手機·解數獨</div>
      </div>

      {/* Beat 0+ : BoomDoubleRing covers center */}
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
        <BoomDoubleRing active={beatIndex >= 0} size={320} />
      </div>

      {/* Beat 1+ : Cream BOOM card with "訓 練 AI 解 數 獨" */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { scale: 1, opacity: 1 }
          : { scale: 0.8, opacity: 0 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'relative', zIndex: 30,
          background: '#FFFDF5', color: '#000',
          border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
          padding: '40px 64px', rotate: -2,
          fontWeight: 900, fontSize: '4rem', lineHeight: 1.1,
          display: 'flex', alignItems: 'center', gap: 12,
        }}
      >
        訓 練
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '0 20px', border: '4px solid #000',
        }}>AI</span>
        解 數 獨
      </motion.div>

      {/* Beat 2 : Punchline yellow highlight box (placeholder before; mask-reveal text on beat 2)
          Wrapper also performs C overshoot (scale keyframes) when beatIndex hits 2. */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] }
          : { scale: 1 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ marginTop: 56, position: 'relative', zIndex: 30 }}
      >
        <YellowHighlight
          active={beatIndex >= 2}
          padding="16px 32px"
          style={{ fontSize: '2.5rem' }}
        >
          靈感就是這麼 <em style={{ fontStyle: 'normal', color: '#FF6B6B' }}>莫名其妙</em> 地蹦出來
        </YellowHighlight>

        {/* Placeholder underlying frame visible before beat 2 — shows users where the text will land. */}
        {beatIndex < 2 && (
          <div style={{
            position: 'absolute', inset: 0,
            border: '4px dashed #FFD93D',
            pointerEvents: 'none',
          }} />
        )}
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Register Step8 in `Ch1.jsx`**

```jsx
import Ch1Step8 from './Ch1Step8.jsx';
// ...
const STEPS = {
  1: Ch1Step1, 2: Ch1Step2, 3: Ch1Step3, 4: Ch1Step4,
  5: Ch1Step5, 6: Ch1Step6, 7: Ch1Step7, 8: Ch1Step8,
};
```

- [ ] **Step 3: Build + visual walk-through**

`npm run build`, then `?ch=1&step=8&beat=0`. Expected behavior:

- **beat 0 (boom-burst)**: 3 dim background stickers shake briefly + BoomDoubleRing (yellow outer + red inner) stamps in with overshoot.
- **beat 1 (auto, ~400ms after beat 0)**: Cream "訓 練 [AI] 解 數 獨" card stamps in over center.
- **beat 2 (after click)**: Yellow highlight box reveals "靈感就是這麼 *莫名其妙* 地蹦出來" text via mask-reveal, screen shakes briefly, yellow box overshoots scale.

Test using keyboard ←/→ or left-click to advance.

- [ ] **Step 4: Test suite still passes**

```bash
npm run test:run
```

Expected: 19/19 tests passing (no behavior changed in tested modules).

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step8.jsx demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(demo): ch1 s8 BOOM punchline (3-beat, A+C climax, first use of boom-double-ring + yellow-highlight)"
```

---

## Module D · Chapter 1 Checkpoint

### Task 10: ch1 visual verification + checkpoint tag

**Files:**
- (no new code files; this task only runs the dev server and walks through all 8 steps)

- [ ] **Step 1: Build verification**

```bash
cd demo/presentation
npm run build
```

Expected: clean build, bundle size grew modestly from Phase 0 baseline (still well under 500 kB JS).

- [ ] **Step 2: Test suite verification**

```bash
npm run test:run
```

Expected: 19/19 tests passing.

- [ ] **Step 3: Dev server + visual walk-through**

```bash
npm run dev
```

Open `http://localhost:5173/?ch=1&step=1&beat=0`, then use left-click / SPACE / → to advance through all 8 steps. Verify each:

- [ ] **s1 心虛開場**: black→cream fade, 「心 虛」 sticker overshoot + float, 期中報告 badge, caption mask-reveal
- [ ] **s2 心理學系**: white card stamps from bottom-right with rotation, red arrow stroke-draws, yellow 敬請期待 stamps in
- [ ] **s3 主題揭曉**: 期中主題 black kicker, "訓 練 AI 解 數 獨" hero (text-stroke 訓練 + red AI + yellow 解數獨), 4 corner decoratives (yellow star spins forever)
- [ ] **s4 捷運看正妹**: caption from top, MRT placeholder, 正妹發呆中 yellow cloud sticker from bottom-left
- [ ] **s5 Code Bullet**: same scene + purple Code Bullet · flappy bird sticker from top-right + dashed thought line
- [ ] **s6 繼續發呆**: same scene + ⋯⋯ cream bubble that pulses + "然後我繼續發呆⋯" small caption
- [ ] **s7 沒手機解數獨**: same scene with 3 stickers (正妹 + Code Bullet + new red 沒手機·解數獨), no ⋯⋯ bubble
- [ ] **s8 BOOM**:
  - beat 0: 3 bg stickers shake, BoomDoubleRing stamps in
  - beat 1: auto, 400ms later boom card appears
  - beat 2: click → yellow box reveals "靈感就是這麼 *莫名其妙* 地蹦出來", screen shakes, box overshoots
- [ ] **Re-walk ch1**: Use `?ch=1&step=1` to restart, verify smooth state reset.
- [ ] **`?presenter=1` mode**: open `?ch=1&step=8&beat=2&presenter=1`, confirm Speaker Panel shows the punchline cue (per beat-manifest.js).

- [ ] **Step 4: Tag the checkpoint**

```bash
git tag phase-1-ch1-complete
```

- [ ] **Step 5: Report back to user**

> Phase 1 ch1 coldopen complete. 8 steps + BOOM punchline. Tag: `phase-1-ch1-complete`. Ready for human checkpoint review — please open `http://localhost:5173/?ch=1&step=1` and walk all 8 steps. After approval, we plan ch 2 (ml-map, 4 steps).

---

## Self-Review

**Spec coverage** — checked against [outline.md ch1](../../../demo/outline.md):

- ✅ s1 心虛開場 (10s · 單 beat) → Task 2
- ✅ s2 心理學系畢業 (8s · 單 beat) → Task 3
- ✅ s3 主題揭曉 (10s · 單 beat) → Task 4
- ✅ s4 捷運看正妹 (10s · 單 beat) → Task 5
- ✅ s5 Code Bullet (8s · 單 beat) → Task 6
- ✅ s6 繼續發呆 (6s · 單 beat) → Task 7
- ✅ s7 沒手機解數獨 (8s · 單 beat) → Task 8
- ✅ s8 BOOM (12s · 3 beat · punchline · placeholder · A+C) → Task 9
- ✅ Motif 首發: boom-double-ring (Task 9) · yellow-highlight (Task 9)
- ✅ Climax 火力 A+C (light) → Task 9 (screen shake via triggerShake + scale overshoot keyframes)
- ✅ Speaker mode cue + wait — already wired in Phase 0 PresenterPanel; beat-manifest.js already has cue strings
- ✅ Ambient shapes, chapter tint, halftone, grain — already wired in Phase 0 (mounted in App.jsx Frame)

**Placeholder scan**: No "TBD" / "implement later" / "similar to Task N" patterns. Every step has full inline JSX. Test commands include exact pass/fail expectations.

**Type consistency**: All step components use `usePresentationContext()` for `stepId` / `beatIndex` / `advance` / `triggerShake` — consistent shape. STEPS map keys are numeric matching `stepId`. BoomDoubleRing accepts `active` + `size`, YellowHighlight accepts `active` + `children` + `padding` + `style` — all match Phase 0 API.

**One ambiguity resolved during writing**: outline.md s4 says "正妹發呆中 黃底 cloud 樣式" — "cloud" implied speech-bubble feel. Implemented as yellow sticker with `borderRadius: 24` (rounded corners, but still 4px black border + hard shadow preserving Neo-brutalism). The web_style.md "rounded-md forbidden" rule was intended for standard cards/buttons; cloud bubbles are a narrative special case. If you prefer strict no-rounded, change `borderRadius: 24` → `0` in Tasks 5, 6, 7, 8.

**One follow-up to track**: TODO.md gets a `[E]` SVG entry for the MRT window. Real SVG implementation deferred until you have time for asset production (not blocking ch2).

---

## Execution Handoff

Plan complete and saved to [`docs/superpowers/plans/2026-05-17-html-presentation-phase-1-ch1.md`](2026-05-17-html-presentation-phase-1-ch1.md). Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for the 10-task scale.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for human review.

Which approach?
