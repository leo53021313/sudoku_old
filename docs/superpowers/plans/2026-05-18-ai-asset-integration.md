# AI 素材整合進 demo/presentation/ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 10 張 AI 生成的 Neo-brutalism 插畫整合進 demo/presentation/、取代 4 個 step 的 `<AssetPlaceholder>` + 4 種 emoji + 5 個 text sticker。

**Architecture:** 新增 2 個 React component（`AiBackdrop` cinema 背景 + `AiSticker` 包框人物 / 物件）、PNG 放 `public/images/ai/ch<N>/<name>.png`、修改 10 個 step + 1 個 chapter file（Ch1.jsx 升級 MRT 跨 step 共用避免重 mount）。

**Tech Stack:** React 19 + Vite 8 + Motion v12 + Tailwind v4 + Vitest（jsdom + testing-library）+ Playwright（視覺驗收）

**Spec:** [docs/superpowers/specs/2026-05-18-ai-asset-integration-design.md](../specs/2026-05-18-ai-asset-integration-design.md)

---

## File Structure Overview

### 新增（2 component + 10 PNG + 2 test）
```
demo/presentation/
├── src/components/
│   ├── AiBackdrop.jsx           ← Task 2
│   ├── AiBackdrop.test.jsx      ← Task 2
│   ├── AiSticker.jsx            ← Task 3
│   └── AiSticker.test.jsx       ← Task 3
└── public/images/ai/             ← Task 1
    ├── ch1/{mrt-window,girl-daydream,codebullet-flappy,soldier-sudoku}.png
    ├── ch2/{teacher-notes,folding-clothes,dog-handshake}.png
    └── ch9/{airplane-bird,brain-reward,neural-network}.png
```

### 修改（10 step + 1 chapter）
```
demo/presentation/src/chapters/
├── ch1-coldopen/
│   ├── Ch1.jsx                  ← Task 4 (lift MRT backdrop)
│   ├── Ch1Step4.jsx             ← Task 5
│   ├── Ch1Step5.jsx             ← Task 6
│   ├── Ch1Step6.jsx             ← Task 7
│   └── Ch1Step7.jsx             ← Task 8
├── ch2-ml-map/
│   ├── Ch2Step1.jsx             ← Task 9
│   ├── Ch2Step2.jsx             ← Task 10
│   └── Ch2Step3.jsx             ← Task 11
└── ch9-callback/
    ├── Ch9Step3.jsx             ← Task 12
    ├── Ch9Step4.jsx             ← Task 13
    └── Ch9Step5.jsx             ← Task 14
```

---

## Task 1: 搬移 10 張 PNG 到 public/

**Files:**
- Create: `demo/presentation/public/images/ai/ch1/{mrt-window,girl-daydream,codebullet-flappy,soldier-sudoku}.png`
- Create: `demo/presentation/public/images/ai/ch2/{teacher-notes,folding-clothes,dog-handshake}.png`
- Create: `demo/presentation/public/images/ai/ch9/{airplane-bird,brain-reward,neural-network}.png`
- Source: `demo/asset-experiments/*.png`（複製、不搬走）

- [ ] **Step 1.1:** 建立 3 個目標目錄

```powershell
New-Item -ItemType Directory -Force -Path `
  'demo/presentation/public/images/ai/ch1', `
  'demo/presentation/public/images/ai/ch2', `
  'demo/presentation/public/images/ai/ch9' | Out-Null
```

- [ ] **Step 1.2:** 複製 10 個檔案到對應路徑

```powershell
$mapping = @{
  'ch1-mrt-window.png'         = 'ch1/mrt-window.png'
  'ch1-girl-daydream.png'      = 'ch1/girl-daydream.png'
  'ch1-codebullet-flappy.png'  = 'ch1/codebullet-flappy.png'
  'ch1-soldier-sudoku.png'     = 'ch1/soldier-sudoku.png'
  'ch2-teacher-notes.png'      = 'ch2/teacher-notes.png'
  'ch2-folding-clothes.png'    = 'ch2/folding-clothes.png'
  'ch2-dog-handshake.png'      = 'ch2/dog-handshake.png'
  'ch9-airplane-bird.png'      = 'ch9/airplane-bird.png'
  'ch9-brain-reward.png'       = 'ch9/brain-reward.png'
  'ch9-neural-network.png'     = 'ch9/neural-network.png'
}
$mapping.GetEnumerator() | ForEach-Object {
  Copy-Item "demo/asset-experiments/$($_.Key)" `
            "demo/presentation/public/images/ai/$($_.Value)" -Force
}
```

- [ ] **Step 1.3:** 驗證 10 個檔案都在

```powershell
Get-ChildItem -Recurse demo/presentation/public/images/ai -File | Measure-Object
# 預期: Count: 10
```

- [ ] **Step 1.4:** Commit

```bash
git add demo/presentation/public/images/ai/
git commit -m "feat(presentation): add 10 AI-generated Neo-brutalism illustrations

ch1: mrt-window, girl-daydream, codebullet-flappy, soldier-sudoku
ch2: teacher-notes, folding-clothes, dog-handshake
ch9: airplane-bird, brain-reward, neural-network"
```

---

## Task 2: AiBackdrop 元件 + 測試

**Files:**
- Create: `demo/presentation/src/components/AiBackdrop.jsx`
- Create: `demo/presentation/src/components/AiBackdrop.test.jsx`

- [ ] **Step 2.1:** 寫失敗測試

Create `demo/presentation/src/components/AiBackdrop.test.jsx`:

```jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AiBackdrop } from './AiBackdrop.jsx';

describe('AiBackdrop', () => {
  it('renders an img with src and alt', () => {
    render(<AiBackdrop src="/images/ai/ch1/mrt-window.png" alt="MRT" />);
    const img = screen.getByAltText('MRT');
    expect(img.tagName).toBe('IMG');
    expect(img.getAttribute('src')).toBe('/images/ai/ch1/mrt-window.png');
  });

  it('applies full-bleed positioning style with z-index 5', () => {
    render(<AiBackdrop src="/x.png" alt="x" />);
    const img = screen.getByAltText('x');
    expect(img).toHaveStyle({
      position: 'absolute',
      width: '100vw',
      height: '100vh',
      zIndex: '5',
      objectFit: 'cover',
    });
  });

  it('defaults alt to empty string when not provided', () => {
    const { container } = render(<AiBackdrop src="/x.png" />);
    const img = container.querySelector('img');
    expect(img.getAttribute('alt')).toBe('');
  });
});
```

- [ ] **Step 2.2:** Run test、確認失敗

```bash
cd demo/presentation && npm run test:run -- src/components/AiBackdrop.test.jsx
```

Expected: FAIL（`Cannot find module './AiBackdrop.jsx'`）

- [ ] **Step 2.3:** 實作 AiBackdrop.jsx

Create `demo/presentation/src/components/AiBackdrop.jsx`:

```jsx
export function AiBackdrop({ src, alt = '' }) {
  return (
    <img
      src={src}
      alt={alt}
      loading="eager"
      style={{
        position: 'absolute',
        inset: 0,
        width: '100vw',
        height: '100vh',
        objectFit: 'cover',
        objectPosition: 'center',
        zIndex: 5,
        pointerEvents: 'none',
      }}
    />
  );
}
```

- [ ] **Step 2.4:** Run test、確認 PASS

```bash
cd demo/presentation && npm run test:run -- src/components/AiBackdrop.test.jsx
```

Expected: PASS（3 tests）

- [ ] **Step 2.5:** Commit

```bash
git add demo/presentation/src/components/AiBackdrop.jsx demo/presentation/src/components/AiBackdrop.test.jsx
git commit -m "feat(presentation): add AiBackdrop component for cinema-mode backgrounds

Full-bleed 100vw x 100vh img, z-index 5 (above ambient/tint, below main).
Used by ch1 s4-s7 MRT scene."
```

---

## Task 3: AiSticker 元件 + 測試

**Files:**
- Create: `demo/presentation/src/components/AiSticker.jsx`
- Create: `demo/presentation/src/components/AiSticker.test.jsx`

- [ ] **Step 3.1:** 寫失敗測試

Create `demo/presentation/src/components/AiSticker.test.jsx`:

```jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AiSticker } from './AiSticker.jsx';

describe('AiSticker', () => {
  it('renders an img wrapped in bordered div', () => {
    render(<AiSticker src="/images/ai/ch2/teacher-notes.png" alt="Teacher" />);
    const img = screen.getByAltText('Teacher');
    expect(img.tagName).toBe('IMG');
    expect(img.parentElement.tagName).toBe('DIV');
    expect(img.parentElement).toHaveStyle({
      border: '4px solid #000',
    });
  });

  it('applies default rotation -3deg and 8px hard shadow', () => {
    render(<AiSticker src="/x.png" alt="x" />);
    const wrapper = screen.getByAltText('x').parentElement;
    expect(wrapper).toHaveStyle({
      transform: 'rotate(-3deg)',
      boxShadow: '8px 8px 0 0 #000',
    });
  });

  it('respects custom rotation, width, shadow props', () => {
    render(<AiSticker src="/x.png" alt="x" rotation={2} width={420} shadow={12} />);
    const img = screen.getByAltText('x');
    const wrapper = img.parentElement;
    expect(wrapper).toHaveStyle({
      transform: 'rotate(2deg)',
      boxShadow: '12px 12px 0 0 #000',
    });
    expect(img).toHaveStyle({ width: '420px' });
  });

  it('defaults alt to empty string when not provided', () => {
    const { container } = render(<AiSticker src="/x.png" />);
    const img = container.querySelector('img');
    expect(img.getAttribute('alt')).toBe('');
  });
});
```

- [ ] **Step 3.2:** Run test、確認失敗

```bash
cd demo/presentation && npm run test:run -- src/components/AiSticker.test.jsx
```

Expected: FAIL（`Cannot find module './AiSticker.jsx'`）

- [ ] **Step 3.3:** 實作 AiSticker.jsx

Create `demo/presentation/src/components/AiSticker.jsx`:

```jsx
export function AiSticker({ src, alt = '', width = 280, rotation = -3, shadow = 8 }) {
  return (
    <div style={{
      display: 'inline-block',
      border: '4px solid #000',
      boxShadow: `${shadow}px ${shadow}px 0 0 #000`,
      transform: `rotate(${rotation}deg)`,
      background: '#FFFDF5',
      lineHeight: 0,
    }}>
      <img
        src={src}
        alt={alt}
        loading="lazy"
        style={{ display: 'block', width, height: 'auto' }}
      />
    </div>
  );
}
```

- [ ] **Step 3.4:** Run test、確認 PASS

```bash
cd demo/presentation && npm run test:run -- src/components/AiSticker.test.jsx
```

Expected: PASS（4 tests）

- [ ] **Step 3.5:** 跑整套測試確認沒打壞既有功能

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS（既有 useClimax / usePresentation / useUrlSync test + 新增 2 個元件 test）

- [ ] **Step 3.6:** Commit

```bash
git add demo/presentation/src/components/AiSticker.jsx demo/presentation/src/components/AiSticker.test.jsx
git commit -m "feat(presentation): add AiSticker component for AI illustration wrapping

Neo-brutalism wrapper: 4px black border, hard offset shadow, slight rotation.
Default rotation -3deg, shadow 8px, width 280px. All customizable via props."
```

---

## Task 4: Ch1.jsx — MRT backdrop 升到 chapter 層

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx`

**理由**：MRT 在 step 4-7 共用、放在 step 層每切 step 就 unmount/remount `<img>` 會重新解碼 + 閃爍。升到 chapter 層 + 條件 render 確保 React 不重 mount。

- [ ] **Step 4.1:** 改 Ch1.jsx

Replace entire `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx` content with:

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { AiBackdrop } from '../../components/AiBackdrop.jsx';
import Ch1Step1 from './Ch1Step1.jsx';
import Ch1Step2 from './Ch1Step2.jsx';
import Ch1Step3 from './Ch1Step3.jsx';
import Ch1Step4 from './Ch1Step4.jsx';
import Ch1Step5 from './Ch1Step5.jsx';
import Ch1Step6 from './Ch1Step6.jsx';
import Ch1Step7 from './Ch1Step7.jsx';
import Ch1Step8 from './Ch1Step8.jsx';

const STEPS = {
  1: Ch1Step1,
  2: Ch1Step2,
  3: Ch1Step3,
  4: Ch1Step4,
  5: Ch1Step5,
  6: Ch1Step6,
  7: Ch1Step7,
  8: Ch1Step8,
};

export function Ch1() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  const showMrtBackdrop = stepId >= 4 && stepId <= 7;
  return (
    <>
      {showMrtBackdrop && (
        <AiBackdrop src="/images/ai/ch1/mrt-window.png" alt="台北捷運車廂內視" />
      )}
      {Step ? (
        <Step key={stepId} />
      ) : (
        <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
          <div style={{ fontSize: 24, fontWeight: 900 }}>ch 1 · step {stepId}</div>
          <div style={{ marginTop: 16, color: '#666' }}>(component not yet implemented)</div>
        </main>
      )}
    </>
  );
}
```

- [ ] **Step 4.2:** 跑既有測試確認沒打壞

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 4.3:** Commit

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx
git commit -m "feat(presentation): lift MRT backdrop to Ch1 chapter level

Conditional render for step 4-7. Avoids unmount/remount/re-decode flash
when transitioning between MRT scene steps."
```

---

## Task 5: Ch1Step4 — 取代 MRT placeholder + 正妹文字 sticker

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx`

- [ ] **Step 5.1:** 改 Ch1Step4.jsx

Replace entire file content with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

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

      {/* 正妹 AI sticker bottom-left, overshoot in */}
      <motion.div
        initial={{ x: -200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', left: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 5.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 5.3:** Commit

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx
git commit -m "feat(presentation): ch1 s4 use AiSticker for girl-daydream, drop MRT placeholder

MRT backdrop now provided by Ch1.jsx at chapter level.
Yellow text sticker replaced with AI illustration (rotation -4deg)."
```

---

## Task 6: Ch1Step5 — 取代 MRT placeholder + flappy bird 文字 sticker

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step5.jsx`

- [ ] **Step 6.1:** 改 Ch1Step5.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 正妹 sticker persisted (no entrance animation) */}
      <div style={{
        position: 'absolute', bottom: '14%', left: '8%',
      }}>
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </div>

      {/* NEW: Code Bullet flappy bird AI sticker top-right, scales in */}
      <motion.div
        initial={{ x: 200, y: -100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: '14%', right: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/codebullet-flappy.png"
          alt="Code Bullet flappy bird"
          width={280}
          rotation={3}
          shadow={8}
        />
      </motion.div>

      {/* Thought-bubble dashed line between two stickers */}
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
    </main>
  );
}
```

- [ ] **Step 6.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 6.3:** Commit

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step5.jsx
git commit -m "feat(presentation): ch1 s5 use AiSticker for girl + flappy, drop placeholder

Both text stickers replaced with AI illustrations.
Thought-bubble dashed SVG path preserved."
```

---

## Task 7: Ch1Step6 — 拿掉 MRT placeholder（保留 ellipsis bubble）

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step6.jsx`

- [ ] **Step 7.1:** 改 Ch1Step6.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step6() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* girl + flappy stickers persisted */}
      <div style={{ position: 'absolute', bottom: '14%', left: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </div>
      <div style={{ position: 'absolute', top: '14%', right: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/codebullet-flappy.png"
          alt="Code Bullet flappy bird"
          width={280}
          rotation={3}
          shadow={8}
        />
      </div>

      {/* ⋯⋯ ellipsis bubble above girl — stamp-in + pulse (preserved) */}
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

      {/* Bottom-right small caption (preserved) */}
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

- [ ] **Step 7.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 7.3:** Commit

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step6.jsx
git commit -m "feat(presentation): ch1 s6 swap placeholders for AiSticker, keep ellipsis"
```

---

## Task 8: Ch1Step7 — 取代 MRT placeholder + 軍人文字 sticker

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step7.jsx`

- [ ] **Step 8.1:** 改 Ch1Step7.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch1Step7() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* girl + flappy stickers persisted */}
      <div style={{ position: 'absolute', bottom: '14%', left: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/girl-daydream.png"
          alt="正妹發呆中"
          width={280}
          rotation={-4}
          shadow={8}
        />
      </div>
      <div style={{ position: 'absolute', top: '14%', right: '8%' }}>
        <AiSticker
          src="/images/ai/ch1/codebullet-flappy.png"
          alt="Code Bullet flappy bird"
          width={280}
          rotation={3}
          shadow={8}
        />
      </div>

      {/* NEW: 沒手機·解數獨 AI sticker bottom-right, scales in */}
      <motion.div
        initial={{ x: 200, y: 100, scale: 0.7, opacity: 0 }}
        animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: '14%', right: '8%',
        }}
      >
        <AiSticker
          src="/images/ai/ch1/soldier-sudoku.png"
          alt="軍人解數獨"
          width={280}
          rotation={2}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 8.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 8.3:** Commit

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step7.jsx
git commit -m "feat(presentation): ch1 s7 add soldier AiSticker, drop placeholder + text"
```

---

## Task 9: Ch2Step1 — supervised 右側文字 stack → AI 插畫

**Files:**
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step1.jsx`

- [ ] **Step 9.1:** 改 Ch2Step1.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

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

      {/* Right-side AI illustration */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
        }}
      >
        <AiSticker
          src="/images/ai/ch2/teacher-notes.png"
          alt="老師教學、學生抄筆記"
          width={420}
          rotation={-2}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 9.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 9.3:** Commit

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step1.jsx
git commit -m "feat(presentation): ch2 s1 right-side text stack → AI teacher-notes illustration"
```

---

## Task 10: Ch2Step2 — unsupervised 衣堆 layout → AI 插畫

**Files:**
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step2.jsx`

- [ ] **Step 10.1:** 改 Ch2Step2.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

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

      {/* Right-side AI illustration */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        style={{
          position: 'absolute', right: 64, top: '50%', transform: 'translateY(-50%)',
        }}
      >
        <AiSticker
          src="/images/ai/ch2/folding-clothes.png"
          alt="折衣服按顏色分類"
          width={420}
          rotation={3}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 10.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 10.3:** Commit

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step2.jsx
git commit -m "feat(presentation): ch2 s2 emoji clothes pile → AI folding-clothes illustration"
```

---

## Task 11: Ch2Step3 — RL 狗握手 emoji → AI 插畫

**Files:**
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step3.jsx`

- [ ] **Step 11.1:** 改 Ch2Step3.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

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

      {/* AlphaGo red stamp drops in last (climax, preserved) */}
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

      {/* Dog handshake AI illustration (replaces 🐕 ↔ 🤝 emoji) */}
      <motion.div
        initial={{ opacity: 0, x: 60 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{
          position: 'absolute', left: 64, top: '60%',
        }}
      >
        <AiSticker
          src="/images/ai/ch2/dog-handshake.png"
          alt="訓練狗握手"
          width={420}
          rotation={-3}
          shadow={8}
        />
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 11.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 11.3:** Commit

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step3.jsx
git commit -m "feat(presentation): ch2 s3 dog/handshake emoji → AI dog-handshake illustration"
```

---

## Task 12: Ch9Step3 — 腦/網絡 emoji → AI 插畫 + 黑卡改 cream 卡

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx`

**衝突解法**：左卡背景從 `#000` 改成 `#FFFDF5`（與 PNG cream 底協調）、「腦科學 RL」label 改紅底高亮維持左右對比。

- [ ] **Step 12.1:** 改 Ch9Step3.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';

export default function Ch9Step3() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      fontFamily: 'Space Grotesk', display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {/* Left: brain (RL 腦科學) — cream card now, AI brain illustration */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
      >
        <img
          src="/images/ai/ch9/brain-reward.png"
          alt="大腦與獎懲 token"
          style={{ width: '70%', height: 'auto', display: 'block' }}
        />
        <div style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '8px 20px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900, fontSize: '2rem',
        }}>腦科學 RL</div>
      </motion.div>

      {/* Center: "=" yellow circle stamp (preserved) */}
      <motion.div
        initial={{ scale: 0, rotate: 0 }}
        animate={{ scale: 1, rotate: -10 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFD93D', color: '#000',
          width: 120, height: 120, borderRadius: '50%',
          border: '8px solid #000', boxShadow: '12px 12px 0 0 #000',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 900, fontSize: 64, margin: '0 -40px', zIndex: 5,
        }}
      >
        =
      </motion.div>

      {/* Right: neural net (AI 訓練) — AI neural network illustration */}
      <motion.div
        initial={{ clipPath: 'inset(0 0 0 100%)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
      >
        <img
          src="/images/ai/ch9/neural-network.png"
          alt="神經網路"
          style={{ width: '70%', height: 'auto', display: 'block' }}
        />
        <div style={{
          background: '#000', color: '#FFFDF5',
          padding: '8px 20px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900, fontSize: '2rem',
        }}>AI 訓練 RL</div>
      </motion.div>

      {/* Hero below (preserved) */}
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          position: 'absolute', bottom: 80, left: 0, right: 0, textAlign: 'center',
          fontWeight: 900, fontSize: '2.5rem',
        }}
      >
        其實是 <span style={{ background: '#FFD93D', padding: '4px 16px', border: '4px solid #000' }}>同一件事</span>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 12.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 12.3:** Commit

```bash
git add demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx
git commit -m "feat(presentation): ch9 s3 brain/network emoji → AI illustrations

Left card background flipped from #000 to #FFFDF5 to match PNG cream
underlay. Label color contrast preserved via red bg on '腦科學 RL'
sticker and black bg on 'AI 訓練 RL' sticker."
```

---

## Task 13: Ch9Step4 — 飛機/鳥 emoji → AI 整圖（保留中央 SVG 箭頭）

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step4.jsx`

**設計重點**：`airplane-bird.png` 是整張 16:9 含飛機+鳥並置、中央留白；HTML SVG 箭頭疊在中央維持「鳥 ← 飛機」模仿方向視覺。

- [ ] **Step 13.1:** 改 Ch9Step4.jsx

Replace entire file with:

```jsx
import { motion } from 'motion/react';
import { AiSticker } from '../../components/AiSticker.jsx';

export default function Ch9Step4() {
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
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        AI 在<span style={{ background: '#FFD93D', padding: '0 16px', border: '4px solid #000' }}>模仿</span>人類
      </motion.div>

      {/* Airplane + bird AI sticker (single 16:9 illustration) + center SVG arrow overlay */}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 32 }}>
        <motion.div
          initial={{ scale: 0.85, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <AiSticker
            src="/images/ai/ch9/airplane-bird.png"
            alt="飛機與鳥並置"
            width={900}
            rotation={0}
            shadow={12}
          />
        </motion.div>

        {/* Center bidirectional arrow overlay (preserved) */}
        <motion.svg
          width="120" height="40" viewBox="0 0 120 40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.9 }}
          style={{
            position: 'absolute', left: '50%', top: '50%',
            transform: 'translate(-50%, -50%)',
            overflow: 'visible', zIndex: 5,
          }}
        >
          <motion.path
            d="M 10 20 L 20 10 L 10 20 L 110 20 L 100 30 L 110 20 L 100 10"
            fill="none" stroke="#000" strokeWidth="6" strokeLinecap="square"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          />
        </motion.svg>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', textAlign: 'center' }}
      >
        就像飛機 · 是人類模仿鳥類才造出來
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 13.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 13.3:** Commit

```bash
git add demo/presentation/src/chapters/ch9-callback/Ch9Step4.jsx
git commit -m "feat(presentation): ch9 s4 emoji ✈️🐦 → AI airplane-bird single illustration

PNG holds both subjects side-by-side; SVG bidirectional arrow overlays
the center, preserving the '鳥 ← 飛機' biomimicry direction cue."
```

---

## Task 14: Ch9Step5 — 中央腦 emoji → AI 插畫

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx`

- [ ] **Step 14.1:** 改 Ch9Step5.jsx 中的中央腦 emoji 區塊

Find this block in `Ch9Step5.jsx`:

```jsx
      {/* Beat 0+ brain center */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ fontSize: 160, zIndex: 10 }}
      >
        🧠
      </motion.div>
```

Replace with:

```jsx
      {/* Beat 0+ brain center — AI brain-reward sticker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ zIndex: 10 }}
      >
        <AiSticker
          src="/images/ai/ch9/brain-reward.png"
          alt="大腦與獎懲 token"
          width={320}
          rotation={0}
          shadow={12}
        />
      </motion.div>
```

Also add the import to the top of the file (after existing imports):

```jsx
import { AiSticker } from '../../components/AiSticker.jsx';
```

- [ ] **Step 14.2:** 跑測試

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS

- [ ] **Step 14.3:** Commit

```bash
git add demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx
git commit -m "feat(presentation): ch9 s5 center 🧠 emoji → AI brain-reward sticker

Sticker scale animation preserved (was on emoji wrapper; now on
AiSticker wrapper)."
```

---

## Task 15: Playwright 視覺驗收 + 收尾

**Files:**
- 無新增、僅啟動 dev server 截圖驗收

- [ ] **Step 15.1:** 啟動 dev server（背景跑）

```bash
cd demo/presentation && npm run dev
```

Expected: `Local: http://localhost:5173/` 之類訊息

- [ ] **Step 15.2:** 用 playwright 巡 10 個 step 截圖

依序 navigate 並截圖：

```
http://localhost:5173/?ch=1&step=4  → 截圖：MRT full-bleed + girl sticker bottom-left
http://localhost:5173/?ch=1&step=5  → 截圖：MRT + girl + flappy bird top-right
http://localhost:5173/?ch=1&step=6  → 截圖：MRT + girl + flappy + ⋯⋯ 氣球
http://localhost:5173/?ch=1&step=7  → 截圖：MRT + 3 sticker（girl + flappy + soldier）
http://localhost:5173/?ch=2&step=1  → 截圖：supervised 大字 + 右側 teacher-notes 插畫
http://localhost:5173/?ch=2&step=2  → 截圖：unsupervised 大字 + 右側 folding-clothes 插畫
http://localhost:5173/?ch=2&step=3  → 截圖：RL 大字 + 左側 dog-handshake 插畫 + AlphaGo 紅 stamp
http://localhost:5173/?ch=9&step=3  → 截圖：左 cream 卡 brain + 中央黃「=」 + 右 cream 卡 neural net
http://localhost:5173/?ch=9&step=4  → 截圖：飛機+鳥 整圖 + 中央 SVG 箭頭
http://localhost:5173/?ch=9&step=5&beat=0  → 截圖：中央 brain AI sticker
```

對每張截圖人工確認：
- 沒有 emoji 殘留
- 沒有 `<AssetPlaceholder>` 紅虛線框殘留
- 所有 sticker 有 4px 黑邊 + 8px hard shadow + 微旋轉
- ch1 s4→s5→s6→s7 切換時 MRT backdrop 不閃（DevTools Network: mrt-window.png 只 GET 一次）

- [ ] **Step 15.3:** 跑 ch1 step 4-7 連續切換、觀察 MRT 是否重新解碼

在 playwright 中：
```
1. 打開 http://localhost:5173/?ch=1&step=4
2. 開 DevTools → Network → Filter "mrt"
3. Clear Network log
4. 按右鍵或左方向鍵切到 step 5, 6, 7
5. 確認 Network 沒有新的 mrt-window.png 請求（只有 step 4 進入時一次）
```

若有閃爍或重複請求 → Bug 回 Task 4 檢查 Ch1.jsx 條件 render 邏輯。

- [ ] **Step 15.4:** 跑整套測試最後一次

```bash
cd demo/presentation && npm run test:run
```

Expected: ALL PASS（既有 3 個 hook test + 新增 2 個 component test）

- [ ] **Step 15.5:** Lint 檢查

```bash
cd demo/presentation && npm run lint
```

Expected: 無新增 warning / error。若有、修掉。

- [ ] **Step 15.6:** 終止 dev server（從背景終止）

- [ ] **Step 15.7:** 寫驗收紀錄並 commit

Create `demo/presentation/docs/ai-integration-verification-2026-05-18.md`（若 `demo/presentation/docs/` 不存在則先建立）：

```markdown
# AI 素材整合驗收紀錄 · 2026-05-18

## 視覺驗收（playwright 截圖、10 step）

| step | 截圖路徑 | 通過 |
| --- | --- | --- |
| ch1 s4 | (paste path) | ✓/✗ |
| ch1 s5 | (paste path) | ✓/✗ |
| ch1 s6 | (paste path) | ✓/✗ |
| ch1 s7 | (paste path) | ✓/✗ |
| ch2 s1 | (paste path) | ✓/✗ |
| ch2 s2 | (paste path) | ✓/✗ |
| ch2 s3 | (paste path) | ✓/✗ |
| ch9 s3 | (paste path) | ✓/✗ |
| ch9 s4 | (paste path) | ✓/✗ |
| ch9 s5 b0 | (paste path) | ✓/✗ |

## ch1 MRT backdrop 重 mount 檢查

DevTools Network: ch1 s4→s5→s6→s7 切換時 mrt-window.png 請求次數 = ___ (預期 1)

## 紅線通過

- [ ] 10 個 step 中無 emoji 殘留
- [ ] 10 個 step 中無 AssetPlaceholder 殘留
- [ ] 所有 sticker 有黑邊 + hard shadow + 旋轉
- [ ] MRT backdrop 無黑邊框、full-bleed
- [ ] npm run test:run all pass
- [ ] npm run lint clean
```

填入結果後 commit：

```bash
git add demo/presentation/docs/ai-integration-verification-2026-05-18.md
git commit -m "docs(presentation): AI asset integration verification 2026-05-18"
```

---

## Self-Review Checklist

**Spec coverage**:
- §0 四個策略 → 全部落實在 Task 1-14
- §1 兩個 component → Task 2 (AiBackdrop) + Task 3 (AiSticker)
- §2 檔案路徑 → Task 1
- §3 取代清單 10 個 → Task 5-14（10 個 step）
- §4 動畫保留 → 每個 step task 都在註解標 "(preserved)"
- §5 改動範圍 → 全部覆蓋
- §6 驗收 → Task 15
- §7 後續延伸 → 不在範圍（spec 已說明）
- §8 風險 → 衝突解法已在 Task 4 / Task 12 / Task 13 落實

**Type/method consistency**:
- `AiBackdrop({ src, alt })` 在 Task 2 定義、Task 4 使用 ✓
- `AiSticker({ src, alt, width, rotation, shadow })` 在 Task 3 定義、Task 5-14 使用 ✓
- 預設值 `rotation=-3, shadow=8, width=280, alt=''` 一致 ✓

**No placeholders**: 無 TBD / TODO / "fill in details" — 每個 code step 都附完整 code。

**Critical paths verified**:
- Vite serves `public/` at root → `/images/ai/...` URL works without import ✓
- `loading="eager"` on AiBackdrop（首屏 MRT 不可 lazy）/ `loading="lazy"` on AiSticker（章節漸進）✓
- 條件 render `{stepId >= 4 && stepId <= 7 && <AiBackdrop>}` 跨 step 不重 mount（React reconciler 規則：同 type + 同 props 不 unmount）✓

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-18-ai-asset-integration.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — 派 fresh subagent 處理每個 task、task 之間 review、快迭代

**2. Inline Execution** — 在這個 session 內依序 execute、checkpoint review

**Which approach?**
