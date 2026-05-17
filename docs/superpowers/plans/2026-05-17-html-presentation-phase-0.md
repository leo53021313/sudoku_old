# HTML Presentation · Phase 0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundation for a click-driven Neo-brutalism HTML presentation at `demo/presentation/`. Phase 0 delivers: Vite + React + Tailwind v4 + Motion stack, design tokens, beat state machine, shared UI shell, complete Climax FX orchestration, 8 full motifs + 5 shells, and a `/sandbox` page to verify style + animation correctness before any chapter implementation begins.

**Architecture:** Single-page React app with global state owning ch/step/beat advance. Tailwind v4 CSS-first config exposes Neo-brutalism tokens (cream `#FFFDF5`, ink `#000`, accent `#FF6B6B`, secondary `#FFD93D`, muted `#C4B5FD`). State changes propagate via React context. URL syncs via `URLSearchParams`. Visual layers (grain / halftone / tint / ambient shapes) are absolute-positioned siblings managed by `<App>`. Motifs are pure visual components with `active`/`play` props; `useClimax` hook orchestrates A/B/C/E/G FX simultaneously using Motion's `useAnimate`.

**Tech Stack:** Vite 5 · React 18 · Tailwind v4 (CSS-first) · Motion 11 (Framer Motion) · lucide-react · Vitest + @testing-library/react for state hooks · vanilla JS (no TypeScript)

**Source spec:** [docs/superpowers/specs/2026-05-17-html-presentation-build-flow-design.md](../specs/2026-05-17-html-presentation-build-flow-design.md)
**Visual reference:** [demo/outline-visual.md](../../../demo/outline-visual.md) · [demo/web_style.md](../../../demo/web_style.md)

---

## File Structure

```
demo/presentation/
├── index.html                         # entry, Google Font load
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx                       # ReactDOM render
│   ├── App.jsx                        # router + global layers + contextmenu disable
│   ├── index.css                      # @import tailwindcss + @theme tokens
│   ├── test-setup.js                  # vitest setup
│   │
│   ├── tokens/
│   │   ├── colors.js                  # color palette
│   │   ├── typography.js              # text-mega/hero/h1/kicker/body/label/caption
│   │   ├── spacing.js                 # 4/8/16/24/32/48/64/96px
│   │   ├── zindex.js                  # 0/1/10/20/30/40/50/60/90/100
│   │   └── chapters.js                # per-chapter palette + ambient shapes config
│   │
│   ├── data/
│   │   └── beat-manifest.js           # 9 chapters · 57 steps · 88 beats data
│   │
│   ├── state/
│   │   ├── PresentationContext.jsx    # context provider
│   │   ├── usePresentation.js         # hook + advance/retreat/jumpTo
│   │   ├── usePresentation.test.js
│   │   ├── useUrlSync.js              # state ↔ URL sync
│   │   ├── useUrlSync.test.js
│   │   └── useKeyMouseControls.js     # mouse + keyboard event listeners
│   │
│   ├── layers/
│   │   ├── GlobalGrain.jsx            # SVG noise overlay
│   │   ├── HalftoneBg.jsx             # halftone dots drift animation
│   │   ├── ChapterTint.jsx            # per-chapter background gradient
│   │   ├── AmbientShapes.jsx          # 4-6 floating decorative shapes
│   │   └── FadeBridge.jsx             # chapter transition
│   │
│   ├── components/
│   │   ├── ProgressBar.jsx            # hover-bottom progress
│   │   ├── ChapterNav.jsx             # hover-top-right chapter switcher
│   │   ├── BeatIndicator.jsx          # 88 squares
│   │   ├── PresenterPanel.jsx         # ?presenter=1 overlay
│   │   ├── Sticker.jsx                # sticker primitive
│   │   ├── Hero.jsx                   # hero primitive
│   │   └── AssetPlaceholder.jsx       # TODO-flagged placeholder
│   │
│   ├── motifs/
│   │   ├── BoomDoubleRing.jsx         # FULL
│   │   ├── CrashLine.jsx              # FULL
│   │   ├── RedStamp.jsx               # FULL
│   │   ├── YellowHighlight.jsx        # FULL
│   │   ├── SpotlightVignette.jsx      # FULL (climax G)
│   │   ├── HalftoneBurst.jsx          # FULL (climax B)
│   │   ├── InkSplatter.jsx            # FULL (climax E)
│   │   ├── ScreenShake.jsx            # FULL (climax A)
│   │   ├── GirlNew.jsx                # SHELL
│   │   ├── GirlVeteran.jsx            # SHELL
│   │   ├── ThirteenStairs.jsx         # SHELL
│   │   ├── FlipTwentyToFifty.jsx      # SHELL
│   │   └── SudokuBoard.jsx            # SHELL
│   │
│   ├── climax/
│   │   ├── useClimax.js               # orchestrator hook + test
│   │   ├── useClimax.test.js
│   │   └── animations.js              # pure animation functions (A shake / C overshoot)
│   │
│   └── pages/
│       └── Sandbox.jsx                # verification page
│
└── TODO.md                            # placeholder tracking
```

---

## Module A · Project Init

### Task 1: Scaffold Vite + React project

**Files:**
- Create: `demo/presentation/` (whole directory via Vite scaffold)

- [ ] **Step 1: Create project via Vite scaffold**

From repo root:
```bash
npm create vite@latest demo/presentation -- --template react
```

When prompted, accept defaults.

- [ ] **Step 2: Verify dev server boots**

```bash
cd demo/presentation
npm install
npm run dev
```

Expected: dev server on `http://localhost:5173/`, default Vite + React welcome page renders.

- [ ] **Step 3: Stop dev server (Ctrl+C) and commit**

```bash
git add demo/presentation/
git commit -m "feat(demo): scaffold Vite + React presentation project"
```

---

### Task 2: Install runtime dependencies

**Files:**
- Modify: `demo/presentation/package.json`

- [ ] **Step 1: Install Motion + lucide-react**

```bash
cd demo/presentation
npm install motion lucide-react
```

- [ ] **Step 2: Verify installations**

```bash
npm ls motion lucide-react
```

Expected: both shown at non-empty versions.

- [ ] **Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "feat(demo): add motion + lucide-react"
```

---

### Task 3: Install + configure Tailwind v4 (CSS-first)

**Files:**
- Modify: `demo/presentation/vite.config.js`
- Create: `demo/presentation/src/index.css` (replace default)
- Modify: `demo/presentation/src/main.jsx`

- [ ] **Step 1: Install Tailwind v4**

```bash
cd demo/presentation
npm install tailwindcss @tailwindcss/vite
```

- [ ] **Step 2: Add Tailwind plugin to Vite config**

Replace `vite.config.js`:

```js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

- [ ] **Step 3: Replace `src/index.css` with Neo-brutalism CSS-first config**

Overwrite `src/index.css` (delete default Vite styles):

```css
@import "tailwindcss";

@theme {
  /* Neo-brutalism color tokens — see demo/web_style.md */
  --color-neo-bg: #FFFDF5;
  --color-neo-ink: #000000;
  --color-neo-accent: #FF6B6B;
  --color-neo-secondary: #FFD93D;
  --color-neo-muted: #C4B5FD;

  /* Font families */
  --font-grotesk: "Space Grotesk", "Noto Sans SC", sans-serif;

  /* Hard shadows (offset, zero blur) */
  --shadow-neo-sm: 4px 4px 0 0 #000;
  --shadow-neo: 8px 8px 0 0 #000;
  --shadow-neo-lg: 12px 12px 0 0 #000;
  --shadow-neo-massive: 16px 16px 0 0 #000;
  --shadow-neo-burst: 20px 20px 0 0 #000;
}

/* Global resets */
html, body, #root {
  margin: 0;
  padding: 0;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-neo-bg);
  font-family: var(--font-grotesk);
  color: var(--color-neo-ink);
}
```

- [ ] **Step 4: Confirm `src/main.jsx` imports the CSS**

Ensure first import in `src/main.jsx` is:

```js
import './index.css';
```

- [ ] **Step 5: Verify with quick test in `App.jsx`**

Temporarily edit `src/App.jsx` to render:

```jsx
function App() {
  return (
    <div className="p-8">
      <div className="inline-block bg-neo-accent border-4 border-black p-6 shadow-neo-lg font-grotesk font-black text-4xl -rotate-2">
        心 虛
      </div>
    </div>
  );
}
export default App;
```

Run `npm run dev` — expected: red `心 虛` sticker with thick black border + hard offset shadow + slight rotation, on cream background.

- [ ] **Step 6: Commit**

```bash
git add vite.config.js src/index.css src/App.jsx
git commit -m "feat(demo): configure Tailwind v4 with Neo-brutalism tokens"
```

---

### Task 4: Load Google Fonts + install Vitest

**Files:**
- Modify: `demo/presentation/index.html`
- Create: `demo/presentation/src/test-setup.js`
- Modify: `demo/presentation/vite.config.js`
- Modify: `demo/presentation/package.json` (via npm install)

- [ ] **Step 1: Add font link in `index.html`**

Inside `<head>`, before any `<style>`/`<script>`, add:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;900&family=Noto+Sans+SC:wght@500;700;900&display=block" rel="stylesheet">
```

Change `<title>` to `演講 — 訓練 AI 解數獨`.

- [ ] **Step 2: Install Vitest + testing-library**

```bash
cd demo/presentation
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

- [ ] **Step 3: Create `src/test-setup.js`**

```js
import '@testing-library/jest-dom';
```

- [ ] **Step 4: Extend `vite.config.js` with test config**

Replace `vite.config.js`:

```js
/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test-setup.js',
  },
});
```

- [ ] **Step 5: Add test scripts to `package.json`**

In the `"scripts"` object, add:

```json
"test": "vitest",
"test:run": "vitest run"
```

- [ ] **Step 6: Smoke-test Vitest works**

Create `src/sanity.test.js`:

```js
import { describe, it, expect } from 'vitest';

describe('sanity', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2);
  });
});
```

Run: `npm run test:run`
Expected: 1 test passed.

Delete `src/sanity.test.js`.

- [ ] **Step 7: Commit**

```bash
git add index.html src/test-setup.js vite.config.js package.json package-lock.json
git commit -m "feat(demo): load Space Grotesk + Noto Sans SC, install Vitest"
```

---

## Module B · Design Tokens

### Task 5: Design token JS files (colors / typography / spacing / zindex)

**Files:**
- Create: `demo/presentation/src/tokens/colors.js`
- Create: `demo/presentation/src/tokens/typography.js`
- Create: `demo/presentation/src/tokens/spacing.js`
- Create: `demo/presentation/src/tokens/zindex.js`

- [ ] **Step 1: Create `src/tokens/colors.js`**

```js
// Neo-brutalism palette — mirror of demo/outline-visual.md §12.1
export const colors = {
  bg:        '#FFFDF5',
  ink:       '#000000',
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  white:     '#FFFFFF',
};
```

- [ ] **Step 2: Create `src/tokens/typography.js`**

```js
// Typography scale — mirror of demo/outline-visual.md §1.5
export const typography = {
  heroMega: { fontSize: '8rem', fontWeight: 900, lineHeight: 1 },
  hero:     { fontSize: '6rem', fontWeight: 900, lineHeight: 1.05 },
  h1:       { fontSize: '3.75rem', fontWeight: 900, lineHeight: 1.1 },
  h2:       { fontSize: '3rem', fontWeight: 900, lineHeight: 1.1 },
  h3:       { fontSize: '2.25rem', fontWeight: 700, lineHeight: 1.15 },
  bodyLg:   { fontSize: '1.875rem', fontWeight: 700, lineHeight: 1.3 },
  body:     { fontSize: '1.5rem', fontWeight: 700, lineHeight: 1.4 },
  kicker:   { fontSize: '1.25rem', fontWeight: 700, lineHeight: 1.4 },
  label:    { fontSize: '1rem', fontWeight: 700, lineHeight: 1.4 },
  caption:  { fontSize: '0.75rem', fontWeight: 700, lineHeight: 1.4 },
};
```

- [ ] **Step 3: Create `src/tokens/spacing.js`**

```js
// 8px base grid — mirror of demo/outline-visual.md §1.5
export const spacing = {
  1:  4,
  2:  8,
  3:  12,
  4:  16,
  6:  24,
  8:  32,
  12: 48,
  16: 64,
  24: 96,
};
```

- [ ] **Step 4: Create `src/tokens/zindex.js`**

```js
// Layering — mirror of demo/outline-visual.md §1.5
export const zindex = {
  ambientShapes:   0,
  globalGrain:     1,
  halftoneBg:      5,
  chapterBg:       10,
  hero:            20,
  sticker:         30,
  climaxOverlay:   40,
  spotlight:       50,
  finalStamp:      60,
  progressBar:     90,
  presenterPanel:  100,
};
```

- [ ] **Step 5: Commit**

```bash
git add src/tokens/
git commit -m "feat(demo): add design token JS files"
```

---

### Task 6: Chapter palette + ambient shapes config

**Files:**
- Create: `demo/presentation/src/tokens/chapters.js`

- [ ] **Step 1: Create `src/tokens/chapters.js`** with all 9 chapter palette entries

Mirror data from [outline-visual.md §6 章節色票統一表](../../../demo/outline-visual.md). Each entry: `id`, `name`, `mood`, `tint`, `density`, `ambientShapes` array (4-6 shapes with `position`/`shape`/`color`/`rotation`).

```js
// Per-chapter palette + ambient shapes config — mirror of outline-visual.md §6
export const chapters = [
  {
    id: 1,
    name: 'coldopen',
    mood: '探索/好奇/白日夢',
    primary: 'cream+紫',
    secondary: '黃',
    climaxAmbient: '紅',
    tint: 'rgba(196,181,253,0.08)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'star',     color: 'secondary', rotation: 15 },
      { position: 'tr', shape: 'square',   color: 'muted',     rotation: -8 },
      { position: 'bl', shape: 'circle',   color: 'accent',    rotation: 0 },
      { position: 'br', shape: 'outline-question', color: 'ink', rotation: 12 },
      { position: 'mr', shape: 'circle',   color: 'secondary', rotation: -3 },
    ],
  },
  {
    id: 2,
    name: 'ml-map',
    mood: '教學/理性',
    primary: 'cream+黑',
    secondary: '灰線',
    climaxAmbient: '紅',
    tint: 'rgba(0,0,0,0.04)',
    density: 'low',
    ambientShapes: [
      { position: 'tl', shape: 'star',   color: 'ink',     rotation: -10, outline: true },
      { position: 'tr', shape: 'square', color: '#888',    rotation: 5 },
      { position: 'bl', shape: 'pill',   color: 'ink',     rotation: 0 },
      { position: 'br', shape: 'circle', color: 'accent',  rotation: -8 },
    ],
  },
  {
    id: 3,
    name: 'llm-vs-rl',
    mood: '對比/分歧',
    primary: 'cream',
    secondary: '紫+黃',
    climaxAmbient: '紅',
    tint: 'rgba(196,181,253,0.06)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'square',   color: 'muted',     rotation: -5 },
      { position: 'tr', shape: 'circle',   color: 'secondary', rotation: 10 },
      { position: 'bl', shape: 'triangle', color: 'muted',     rotation: 3 },
      { position: 'br', shape: 'square',   color: 'secondary', rotation: 38 },
      { position: 'mc', shape: 'outline-question', color: 'accent', rotation: 8 },
    ],
  },
  {
    id: 4,
    name: 'data-hunt',
    mood: '戰鬥/受害',
    primary: 'cream+黑mono',
    secondary: '黃',
    climaxAmbient: '紅',
    tint: 'rgba(255,217,61,0.06)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'square', color: 'ink',       rotation: 5 },
      { position: 'tr', shape: 'star',   color: 'secondary', rotation: -10 },
      { position: 'bl', shape: 'circle', color: 'accent',    rotation: 12 },
      { position: 'br', shape: 'pill',   color: 'ink',       rotation: -3, outline: true },
    ],
  },
  {
    id: 5,
    name: 'legacy',
    mood: '崩盤#1',
    primary: 'cream+紅邊',
    secondary: '紅叉叉',
    climaxAmbient: '紅 flash',
    tint: 'rgba(255,107,107,0.07)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'square', color: 'accent', rotation: 60 },
      { position: 'tr', shape: 'circle', color: 'accent', rotation: -5 },
      { position: 'bl', shape: 'square', color: 'accent', rotation: 8, outline: true },
      { position: 'br', shape: 'pill',   color: 'accent', rotation: -3 },
    ],
  },
  {
    id: 6,
    name: 'sb3',
    mood: '戀愛錯覺→崩盤#2',
    primary: '粉紅',
    secondary: '紅',
    climaxAmbient: '灰→紅stamp',
    tint: 'rgba(255,182,193,0.10)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'circle', color: '#FFB6C1', rotation: 10 },
      { position: 'tr', shape: 'circle', color: 'accent',  rotation: -6 },
      { position: 'bl', shape: 'square', color: '#FFB6C1', rotation: 3 },
      { position: 'br', shape: 'pill',   color: 'accent',  rotation: -10 },
      { position: 'ml', shape: 'circle', color: '#999',    rotation: 5 },
    ],
  },
  {
    id: 7,
    name: 'reasoner',
    mood: '嚴肅/死結',
    primary: 'cream+黑',
    secondary: '多色',
    climaxAmbient: '紅底+黃0',
    tint: 'rgba(0,0,0,0.05)',
    density: 'high',
    ambientShapes: [
      { position: 'tl', shape: 'square',   color: 'accent',    rotation: -8 },
      { position: 'tr', shape: 'star',     color: 'muted',     rotation: 12 },
      { position: 'bl', shape: 'square',   color: 'secondary', rotation: 50 },
      { position: 'br', shape: 'outline-question', color: 'ink', rotation: -10 },
      { position: 'mr', shape: 'circle',   color: 'muted',     rotation: 3 },
      { position: 'ml', shape: 'triangle', color: 'accent',    rotation: -5 },
    ],
  },
  {
    id: 8,
    name: 'apprentice',
    mood: '突破/光明',
    primary: 'cream+金黃',
    secondary: '紫',
    climaxAmbient: '黃 +50',
    tint: 'rgba(255,217,61,0.10)',
    density: 'mid',
    ambientShapes: [
      { position: 'tl', shape: 'star',   color: 'secondary', rotation: 10 },
      { position: 'tr', shape: 'square', color: 'muted',     rotation: -8 },
      { position: 'bl', shape: 'circle', color: 'secondary', rotation: 3 },
      { position: 'br', shape: 'star',   color: 'secondary', rotation: -12 },
    ],
  },
  {
    id: 9,
    name: 'callback',
    mood: '收斂/哲思/收尾',
    primary: 'cream',
    secondary: '紫',
    climaxAmbient: '紅 (電費小偷)',
    tint: 'rgba(196,181,253,0.07)',
    density: 'high',
    ambientShapes: [
      { position: 'tl', shape: 'circle', color: 'muted',     rotation: 5 },
      { position: 'tr', shape: 'star',   color: 'accent',    rotation: -10 },
      { position: 'bl', shape: 'square', color: 'muted',     rotation: 8, outline: true },
      { position: 'br', shape: 'outline-question', color: '#888', rotation: -3 },
    ],
  },
];

export function getChapter(id) {
  return chapters.find(c => c.id === id) ?? chapters[0];
}
```

- [ ] **Step 2: Commit**

```bash
git add src/tokens/chapters.js
git commit -m "feat(demo): per-chapter palette + ambient shapes config"
```

---

## Module C · Beat State + Routing

### Task 7: Beat manifest data

**Files:**
- Create: `demo/presentation/src/data/beat-manifest.js`

- [ ] **Step 1: Create `src/data/beat-manifest.js`**

Encodes all 57 steps and their beats from [outline.md §5 Step Manifest](../../../demo/outline.md). Each beat: `id`, `type` (`'click'` or `'auto'`), `autoDelayMs` (if auto), `cue` (string or null), `wait` (string or null), `motifs` (array), `climax` (array of A/B/C/E/G codes), `scriptLines` (string).

```js
// Beat manifest — encodes all 88 beats across 9 chapters / 57 steps.
// Source of truth: demo/outline.md per-step descriptions.

export const manifest = {
  totalChapters: 9,
  totalSteps: 57,
  totalBeats: 88,
  chapters: [
    {
      id: 1, name: 'coldopen', narrative: '心虛→心理學系→主題→捷運→Code Bullet→繼續發呆→當兵→BOOM',
      steps: [
        { id: 1, title: '心虛開場', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L1' }] },
        { id: 2, title: '心理學系畢業', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L5' }] },
        { id: 3, title: '主題揭曉', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L9' }] },
        { id: 4, title: '捷運看正妹', duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L15' }] },
        { id: 5, title: 'Code Bullet flappy bird', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L19' }] },
        { id: 6, title: '繼續發呆', duration: 6, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L21' }] },
        { id: 7, title: '當兵沒手機解數獨', duration: 8, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L25' }] },
        { id: 8, title: 'BOOM', duration: 12, punchline: true, motifs: ['boom-double-ring', 'yellow-highlight'], climax: ['A', 'C'],
          beats: [
            { id: 'boom-burst',       type: 'click',              cue: 'Boom——', wait: null,         scriptLines: 'L29' },
            { id: 'boom-card',        type: 'auto', autoDelayMs: 400, cue: null,    wait: null,         scriptLines: 'L29' },
            { id: 'punchline-reveal', type: 'click',              cue: '靈感就是這麼', wait: '1-2s 觀眾消化', climax: ['A', 'C'], scriptLines: 'L35-37' },
          ],
        },
      ],
    },
    {
      id: 2, name: 'ml-map', narrative: 'supervised→unsupervised→RL+AlphaGo→cliffhanger',
      steps: [
        { id: 1, title: 'supervised',   duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L49-55' }] },
        { id: 2, title: 'unsupervised', duration: 13, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L57-61' }] },
        { id: 3, title: 'RL+AlphaGo',   duration: 15, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L63-67' }] },
        { id: 4, title: 'cliffhanger',  duration: 8,  polish: true, motifs: ['yellow-highlight'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L71' }] },
      ],
    },
    {
      id: 3, name: 'llm-vs-rl', narrative: 'LLM→VS→OK純RL',
      steps: [
        { id: 1, title: 'LLM 路線',     duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L75-77' }] },
        { id: 2, title: 'VS 對比',      duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L81-89' }] },
        { id: 3, title: 'OK 純 RL',     duration: 7,  polish: true, motifs: ['halftone-burst'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L93-95' }] },
      ],
    },
    {
      id: 4, name: 'data-hunt', narrative: 'Kaggle→拒絕→受害者→封IP+proxy',
      steps: [
        { id: 1, title: 'Kaggle',                duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L99-103' }] },
        { id: 2, title: 'supervised 拒絕',       duration: 11, polish: true, motifs: ['red-stamp', 'ink-splatter'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L105-107' }] },
        { id: 3, title: '受害者', duration: 14, punchline: true, motifs: ['red-stamp'], climax: ['A', 'C', 'E'],
          beats: [
            { id: 'kicker',       type: 'click', cue: '我的終極目標是把我訓練好的 AI 拿去每個數獨網站...', wait: null, scriptLines: 'L111-115' },
            { id: 'url-sticker',  type: 'click', cue: '於是我找到了 websudoku.com...', wait: null, scriptLines: 'L117' },
            { id: 'victim-stamp', type: 'click', cue: '...（直接念出「這個受害者」當下點）', wait: '1-2s 笑點', climax: ['A', 'C', 'E'], scriptLines: 'L119-121' },
            { id: 'subtitle',     type: 'auto', autoDelayMs: 200, cue: null, wait: null, scriptLines: 'L121' },
          ],
        },
        { id: 4, title: '封 IP + proxy', duration: 13, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L125-133' }] },
      ],
    },
    {
      id: 5, name: 'legacy', narrative: '天真→prompt→我錯了→838行→debug→第一件學到',
      steps: [
        { id: 1, title: '結果我錯了', duration: 14, punchline: true, motifs: ['crash-line'], climax: ['A', 'C'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '我那時候還很天真、覺得——', wait: null,    scriptLines: 'L141' },
            { id: 'prompt-box',        type: 'click', cue: '不如我丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude？', wait: null, scriptLines: 'L143' },
            { id: 'placeholder-frame', type: 'click', cue: '⋯⋯', wait: '1s 留白', scriptLines: 'L145' },
            { id: 'crash-fill',        type: 'click', cue: '結果我錯了', wait: '2s 觀眾消化', climax: ['A', 'C'], scriptLines: 'L145-147' },
          ],
        },
        { id: 2, title: '838 行單檔',     duration: 8,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L151' }] },
        { id: 3, title: 'debug 爆炸',     duration: 7,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L153' }] },
        { id: 4, title: '第一件學到',     duration: 15, polish: true, motifs: ['ink-splatter'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L157-163' }] },
      ],
    },
    {
      id: 6, name: 'sb3', narrative: '我又錯了→套皮仔→新女生→曲線→卡平段→備胎★★★→偷吃步',
      steps: [
        { id: 1, title: '我又錯了', duration: 11, punchline: true, motifs: ['crash-line'], climax: ['A', 'C'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '正當我以為成了套皮仔...', wait: null, scriptLines: 'L171' },
            { id: 'placeholder-frame', type: 'click', cue: '⋯⋯', wait: '0.8s', scriptLines: 'L173' },
            { id: 'crash-fill',        type: 'click', cue: '我又錯了', wait: '1-2s', climax: ['A', 'C'], scriptLines: 'L173' },
          ],
        },
        { id: 2, title: '套皮仔策略',   duration: 9,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L167-177' }] },
        { id: 3, title: '新女生加分',   duration: 12, motifs: ['girl-new'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L181-185' }] },
        { id: 4, title: '曲線爬升',     duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L181' }] },
        { id: 5, title: '卡平段',       duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L187' }] },
        { id: 6, title: '備胎 ★★★',     duration: 12, punchline: true, starLevel: 3, motifs: ['red-stamp'], climax: ['A', 'B', 'C', 'E', 'G'],
          beats: [
            { id: 'flash',                   type: 'click', cue: '結果後面開始遇到瓶頸——AI 只拿那些必拿的固定分數就不思進取了...', wait: '0.5s', scriptLines: 'L189' },
            { id: 'subtitle-and-placeholder', type: 'click', cue: '換句話說、這個女生只把你當——', wait: '1-2s 留懸念', scriptLines: 'L189' },
            { id: 'bei-tai-fill',            type: 'click', cue: '備胎', wait: '3-4s 笑聲', climax: ['A', 'B', 'C', 'E', 'G'], scriptLines: 'L189' },
          ],
        },
        { id: 7, title: '偷吃步',       duration: 7, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L195-199' }] },
      ],
    },
    {
      id: 7, name: 'reasoner', narrative: '重寫→顛倒→13招→舊vs新→Action擴增→機率0→老油條★★★→死結',
      steps: [
        { id: 1, title: '重寫宣告',    duration: 11, polish: true, motifs: ['screen-shake'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L201-205' }] },
        { id: 2, title: '顛倒驗證',    duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L201-205' }] },
        { id: 3, title: '13 招階梯',   duration: 19, motifs: ['13-stairs'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L209-211' }] },
        { id: 4, title: '舊 vs 新',    duration: 17, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L215-225' }] },
        { id: 5, title: 'Action 擴增', duration: 13, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L229-233' }] },
        { id: 6, title: '機率 0',      duration: 16, punchline: true, motifs: ['red-stamp'], climax: ['A', 'B', 'C', 'E'],
          beats: [
            { id: 'count-up',            type: 'click', cue: '結果呢——練了兩千多萬次...', wait: '0.5s', scriptLines: 'L237' },
            { id: 'subtitle-placeholder', type: 'click', cue: '完整解出一道題的機率還是——', wait: '1-2s 留懸念', scriptLines: 'L237' },
            { id: 'zero-drop',           type: 'click', cue: '零', wait: '2-3s 嘆息/笑聲', climax: ['A', 'B', 'C', 'E'], scriptLines: 'L237' },
          ],
        },
        { id: 7, title: '老油條 ★★★',  duration: 26, punchline: true, starLevel: 3, motifs: ['girl-veteran', 'yellow-highlight'], climax: ['A', 'E', 'G', 'B'],
          beats: [
            { id: 'hero',             type: 'click', cue: '這個感覺就是、你剛開始學習如何跟女生互動...', wait: '0.5s', scriptLines: 'L241' },
            { id: 'trap-1',           type: 'click', cue: '但是那些女生都是老油條...例如——和你媽一起掉進水裡你會先救誰？', wait: '2s 觀眾笑', scriptLines: 'L243-247' },
            { id: 'trap-2-question',  type: 'click', cue: '每道都是陷阱題。舉個例子，『你覺得我該不該去運動？』', wait: '1s', scriptLines: 'L249-251' },
            { id: 'answer-a-fill',    type: 'click', cue: '你回答要去運動——那就是你嫌那個女生胖', wait: '2s 笑點', climax: ['A', 'E', 'G'], scriptLines: 'L253-255' },
            { id: 'answer-b-fill',    type: 'click', cue: '你回答不用去運動——那就是你不關心那個女生的身體健康', wait: '2s 笑點', climax: ['A', 'E', 'G'], scriptLines: 'L255-257' },
            { id: 'both-flash',       type: 'auto', autoDelayMs: 400, cue: null, wait: null, climax: ['B', 'B'], scriptLines: 'L257' },
          ],
        },
        { id: 8, title: '死結',        duration: 20, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L265-269' }] },
      ],
    },
    {
      id: 8, name: 'apprentice', narrative: '反向思考→3格空→3→10動畫→+20→+50→光講不夠看→visualizer按鈕',
      steps: [
        { id: 1, title: '反向思考',          duration: 10, polish: true, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L273-275' }] },
        { id: 2, title: '3 格空',            duration: 12, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L277-279' }] },
        { id: 3, title: '反向課程動畫',      duration: 12, motifs: ['sudoku-board'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L281-285' }] },
        { id: 4, title: '+20 → +50 翻牌',    duration: 10, motifs: ['flip-20-to-50'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L287-291' }] },
        { id: 5, title: '光講不夠看',        duration: 9,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L297-299' }] },
        { id: 6, title: 'visualizer 按鈕',  duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L299' }] },
      ],
    },
    {
      id: 9, name: 'callback', narrative: 'tensorboard→金句→RL=→飛機鳥→戀愛a→4考題→plasticity→三欄→機制→MBTI→警語★★→祝福→電費小偷★★★',
      steps: [
        { id: 1, title: 'tensorboard + 磨合期', duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L303-307' }] },
        { id: 2, title: '核心金句',             duration: 14, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L309' }] },
        { id: 3, title: 'RL 對等',              duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L313-317' }] },
        { id: 4, title: '飛機 + 鳥',            duration: 10, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L319' }] },
        { id: 5, title: '戀愛 a callback', duration: 18, punchline: true, motifs: ['girl-new'], climax: ['A', 'C'],
          beats: [
            { id: 'bg-callback',    type: 'click', cue: '追一個人的時候——', wait: null, scriptLines: 'L323' },
            { id: 'left-positive',  type: 'click', cue: '對方回訊息你就被加分', wait: '1s', scriptLines: 'L325' },
            { id: 'right-negative', type: 'click', cue: '已讀不回你就被扣分', wait: '1.5s', scriptLines: 'L325' },
            { id: 'punchline-hero', type: 'click', cue: '你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練', wait: '2s', climax: ['A', 'C'], scriptLines: 'L327-329' },
          ],
        },
        { id: 6, title: '戀愛 b 4 考題',        duration: 18, motifs: ['girl-veteran'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L333-343' }] },
        { id: 7, title: 'plasticity 引出',      duration: 8,  beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L347-349' }] },
        { id: 8, title: 'plasticity 三欄',      duration: 12, motifs: ['13-stairs'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L351' }] },
        { id: 9, title: 'plasticity 機制',      duration: 12, motifs: ['flip-20-to-50', 'yellow-highlight'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L353-355' }] },
        { id: 10, title: 'MBTI + 業務工作',     duration: 22, composite: true, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L359-365' }] },
        { id: 11, title: '警語 ★★', duration: 18, punchline: true, starLevel: 2, motifs: ['crash-line'], climax: ['A', 'C', 'G'],
          beats: [
            { id: 'kicker-and-frame', type: 'click', cue: '所以遇到不會回答的魔王陷阱題沒有關係...', wait: '1s', scriptLines: 'L367' },
            { id: 'subtitle',         type: 'click', cue: '但是不要停滯不前——', wait: '1s', scriptLines: 'L369' },
            { id: 'warn-line-a-fill', type: 'click', cue: '跟一個女生聊天、結果——人生第一次的外向', wait: '1-1.5s', scriptLines: 'L369' },
            { id: 'warn-line-b-fill', type: 'click', cue: '換來一輩子的內向', wait: '3-4s', climax: ['A', 'C', 'G'], scriptLines: 'L369' },
          ],
        },
        { id: 12, title: '職場祝福',            duration: 12, beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L371-373' }] },
        { id: 13, title: '電費小偷 ★★★', duration: 28, punchline: true, starLevel: 3, motifs: ['boom-double-ring', 'red-stamp', 'yellow-highlight'], climax: ['A', 'B', 'C', 'E', 'G'],
          beats: [
            { id: 'kicker',            type: 'click', cue: '最後再補個笑話——', wait: '1s', scriptLines: 'L375' },
            { id: 'salary-thief',      type: 'click', cue: '想必大家未來出職場後都是薪水小偷...', wait: '1.5-2s', scriptLines: 'L375' },
            { id: 'power-thief-fill',  type: 'click', cue: '但我不一樣、我是——電費小偷', wait: '5-7s 大笑', climax: ['A', 'B', 'C', 'E', 'G'], scriptLines: 'L375' },
            { id: 'footer-and-end',    type: 'click', cue: '我這兩個月一直用班上的電腦瘋狂訓練我的 AI', wait: '5s+', scriptLines: 'L375' },
          ],
        },
      ],
    },
  ],
};

// Flatten beats for indexed advance/retreat
export function flattenBeats(manifestRoot = manifest) {
  const flat = [];
  for (const ch of manifestRoot.chapters) {
    for (const step of ch.steps) {
      for (const beat of step.beats) {
        flat.push({ chapterId: ch.id, stepId: step.id, beatId: beat.id, beat, step, chapter: ch });
      }
    }
  }
  return flat;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/data/beat-manifest.js
git commit -m "feat(demo): encode all 88 beats from outline.md"
```

---

### Task 8: usePresentation hook (TDD)

**Files:**
- Create: `demo/presentation/src/state/usePresentation.test.js`
- Create: `demo/presentation/src/state/usePresentation.js`

- [ ] **Step 1: Write failing test**

Create `src/state/usePresentation.test.js`:

```js
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePresentation } from './usePresentation.js';

describe('usePresentation', () => {
  it('starts at chapter 1 step 1 beat 0', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.chapterId).toBe(1);
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('advances to next beat within a multi-beat step', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8 })); // BOOM 3 beats
    expect(result.current.beatIndex).toBe(0);
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(1);
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(2);
  });

  it('advances across step boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 1 }));
    act(() => result.current.advance()); // step 1 only has 1 beat → move to step 2
    expect(result.current.stepId).toBe(2);
    expect(result.current.beatIndex).toBe(0);
  });

  it('advances across chapter boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8, beatIndex: 2 }));
    act(() => result.current.advance());
    expect(result.current.chapterId).toBe(2);
    expect(result.current.stepId).toBe(1);
  });

  it('retreats to previous beat', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 8, beatIndex: 2 }));
    act(() => result.current.retreat());
    expect(result.current.beatIndex).toBe(1);
  });

  it('retreats across step boundary', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 1, stepId: 2 }));
    act(() => result.current.retreat());
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('jumpTo sets state directly', () => {
    const { result } = renderHook(() => usePresentation());
    act(() => result.current.jumpTo({ chapterId: 6, stepId: 6, beatIndex: 0 }));
    expect(result.current.chapterId).toBe(6);
    expect(result.current.stepId).toBe(6);
  });

  it('does not advance past the last beat', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 9, stepId: 13, beatIndex: 3 }));
    act(() => result.current.advance());
    expect(result.current.chapterId).toBe(9);
    expect(result.current.stepId).toBe(13);
    expect(result.current.beatIndex).toBe(3);
  });

  it('does not retreat past the first beat', () => {
    const { result } = renderHook(() => usePresentation());
    act(() => result.current.retreat());
    expect(result.current.chapterId).toBe(1);
    expect(result.current.stepId).toBe(1);
    expect(result.current.beatIndex).toBe(0);
  });

  it('reports totalBeats = 88', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(88);
  });
});
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
npm run test:run
```

Expected: All tests FAIL with "usePresentation not defined" or similar.

- [ ] **Step 3: Implement `src/state/usePresentation.js`**

```js
import { useState, useCallback } from 'react';
import { manifest, flattenBeats } from '../data/beat-manifest.js';

const FLAT = flattenBeats();
const TOTAL = FLAT.length;

function findIndex(chapterId, stepId, beatIndex) {
  for (let i = 0; i < FLAT.length; i++) {
    const f = FLAT[i];
    if (f.chapterId === chapterId && f.stepId === stepId) {
      return i + beatIndex;
    }
  }
  return 0;
}

export function usePresentation(initial = {}) {
  const startIdx = findIndex(
    initial.chapterId ?? 1,
    initial.stepId ?? 1,
    initial.beatIndex ?? 0,
  );
  const [globalBeatIdx, setGlobalBeatIdx] = useState(startIdx);

  const current = FLAT[globalBeatIdx];

  const advance = useCallback(() => {
    setGlobalBeatIdx(idx => Math.min(idx + 1, TOTAL - 1));
  }, []);

  const retreat = useCallback(() => {
    setGlobalBeatIdx(idx => Math.max(idx - 1, 0));
  }, []);

  const jumpTo = useCallback(({ chapterId, stepId, beatIndex = 0 }) => {
    setGlobalBeatIdx(findIndex(chapterId, stepId, beatIndex));
  }, []);

  // Compute beatIndex within current step
  let beatIndex = 0;
  for (let i = globalBeatIdx; i >= 0; i--) {
    if (FLAT[i].chapterId === current.chapterId && FLAT[i].stepId === current.stepId) {
      beatIndex = globalBeatIdx - i;
      break;
    }
  }

  return {
    chapterId: current.chapterId,
    stepId: current.stepId,
    beatIndex,
    beat: current.beat,
    step: current.step,
    chapter: current.chapter,
    globalBeatIdx,
    totalBeats: TOTAL,
    advance,
    retreat,
    jumpTo,
  };
}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
npm run test:run
```

Expected: All 10 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/state/usePresentation.js src/state/usePresentation.test.js
git commit -m "feat(demo): usePresentation hook with advance/retreat/jumpTo"
```

---

### Task 9: useUrlSync hook (TDD)

**Files:**
- Create: `demo/presentation/src/state/useUrlSync.test.js`
- Create: `demo/presentation/src/state/useUrlSync.js`

- [ ] **Step 1: Write failing test**

```js
// src/state/useUrlSync.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import { parseUrl, buildUrl } from './useUrlSync.js';

describe('useUrlSync helpers', () => {
  it('parseUrl returns default when no params', () => {
    expect(parseUrl('http://localhost/')).toEqual({ chapterId: 1, stepId: 1, beatIndex: 0, presenter: false });
  });

  it('parseUrl reads ?ch=6&step=6&beat=2', () => {
    expect(parseUrl('http://localhost/?ch=6&step=6&beat=2')).toEqual({
      chapterId: 6, stepId: 6, beatIndex: 2, presenter: false,
    });
  });

  it('parseUrl reads ?presenter=1', () => {
    expect(parseUrl('http://localhost/?presenter=1').presenter).toBe(true);
  });

  it('buildUrl serializes state', () => {
    expect(buildUrl({ chapterId: 6, stepId: 6, beatIndex: 2 })).toBe('?ch=6&step=6&beat=2');
  });

  it('buildUrl preserves presenter flag', () => {
    expect(buildUrl({ chapterId: 1, stepId: 1, beatIndex: 0, presenter: true })).toBe('?ch=1&step=1&beat=0&presenter=1');
  });

  it('parseUrl ignores invalid values', () => {
    const r = parseUrl('http://localhost/?ch=foo&step=-1&beat=abc');
    expect(r.chapterId).toBe(1);
    expect(r.stepId).toBe(1);
    expect(r.beatIndex).toBe(0);
  });
});
```

- [ ] **Step 2: Run test, verify it fails**

```bash
npm run test:run -- useUrlSync
```

Expected: All tests FAIL ("not defined").

- [ ] **Step 3: Implement `src/state/useUrlSync.js`**

```js
import { useEffect } from 'react';

const intOr = (s, d) => {
  const n = parseInt(s, 10);
  return Number.isFinite(n) && n > 0 ? n : d;
};

export function parseUrl(href) {
  const u = new URL(href);
  return {
    chapterId: intOr(u.searchParams.get('ch'), 1),
    stepId:    intOr(u.searchParams.get('step'), 1),
    beatIndex: Math.max(0, parseInt(u.searchParams.get('beat'), 10) || 0),
    presenter: u.searchParams.get('presenter') === '1',
  };
}

export function buildUrl({ chapterId, stepId, beatIndex, presenter }) {
  const p = new URLSearchParams();
  p.set('ch', String(chapterId));
  p.set('step', String(stepId));
  p.set('beat', String(beatIndex));
  if (presenter) p.set('presenter', '1');
  return '?' + p.toString();
}

export function useUrlSync({ chapterId, stepId, beatIndex }, presenter) {
  useEffect(() => {
    const next = buildUrl({ chapterId, stepId, beatIndex, presenter });
    if (window.location.search !== next) {
      window.history.replaceState(null, '', next);
    }
  }, [chapterId, stepId, beatIndex, presenter]);
}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
npm run test:run -- useUrlSync
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/state/useUrlSync.js src/state/useUrlSync.test.js
git commit -m "feat(demo): useUrlSync hook for state ↔ URL persistence"
```

---

### Task 10: useKeyMouseControls hook

**Files:**
- Create: `demo/presentation/src/state/useKeyMouseControls.js`

- [ ] **Step 1: Implement `src/state/useKeyMouseControls.js`**

```js
import { useEffect } from 'react';

export function useKeyMouseControls({ advance, retreat, toggleProgress }) {
  useEffect(() => {
    const onMouseDown = (e) => {
      if (e.button === 0) advance();        // left
      else if (e.button === 2) retreat();   // right
    };
    const onContextMenu = (e) => e.preventDefault();
    const onKey = (e) => {
      if (e.key === ' ' || e.key === 'ArrowRight') {
        e.preventDefault();
        advance();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        retreat();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        toggleProgress?.();
      }
    };
    document.addEventListener('mousedown', onMouseDown);
    document.addEventListener('contextmenu', onContextMenu);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onMouseDown);
      document.removeEventListener('contextmenu', onContextMenu);
      document.removeEventListener('keydown', onKey);
    };
  }, [advance, retreat, toggleProgress]);
}
```

- [ ] **Step 2: Commit**

```bash
git add src/state/useKeyMouseControls.js
git commit -m "feat(demo): useKeyMouseControls — left/right/SPACE/arrows/Esc"
```

---

### Task 11: PresentationContext provider + scaffold App.jsx

**Files:**
- Create: `demo/presentation/src/state/PresentationContext.jsx`
- Modify: `demo/presentation/src/App.jsx`

- [ ] **Step 1: Create `src/state/PresentationContext.jsx`**

```jsx
import { createContext, useContext, useState, useEffect } from 'react';
import { usePresentation } from './usePresentation.js';
import { useUrlSync, parseUrl } from './useUrlSync.js';
import { useKeyMouseControls } from './useKeyMouseControls.js';

const Ctx = createContext(null);

export function PresentationProvider({ children }) {
  const initial = parseUrl(window.location.href);
  const pres = usePresentation(initial);
  const [presenter, setPresenter] = useState(initial.presenter);
  const [progressVisible, setProgressVisible] = useState(false);

  useUrlSync(pres, presenter);
  useKeyMouseControls({
    advance: pres.advance,
    retreat: pres.retreat,
    toggleProgress: () => setProgressVisible(v => !v),
  });

  return (
    <Ctx.Provider value={{ ...pres, presenter, setPresenter, progressVisible, setProgressVisible }}>
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

- [ ] **Step 2: Scaffold `src/App.jsx`**

```jsx
import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';

function CurrentBeat() {
  const { chapterId, stepId, beatIndex, beat, totalBeats, globalBeatIdx } = usePresentationContext();
  return (
    <div className="p-8 font-grotesk">
      <div className="text-sm">beat {globalBeatIdx + 1} / {totalBeats}</div>
      <div className="text-3xl font-black mt-4">ch {chapterId} · step {stepId} · beat {beatIndex} ({beat.id})</div>
      <div className="mt-2 text-base">cue: {beat.cue ?? '—'}</div>
      <div className="text-base">wait: {beat.wait ?? '—'}</div>
      <div className="mt-4 text-sm text-gray-600">Left-click / Space / → advance · Right-click / ← retreat · Esc progress</div>
    </div>
  );
}

export default function App() {
  return (
    <PresentationProvider>
      <CurrentBeat />
    </PresentationProvider>
  );
}
```

- [ ] **Step 3: Visual verification**

Run `npm run dev`, open `http://localhost:5173`, then:
- left-click → beat advances (1/88 → 2/88)
- right-click → beat retreats (no browser context menu)
- arrow keys / space → also work
- URL updates to `?ch=N&step=M&beat=X`
- reload page → state restores from URL

- [ ] **Step 4: Commit**

```bash
git add src/state/PresentationContext.jsx src/App.jsx
git commit -m "feat(demo): wire PresentationProvider + beat advance/retreat in App"
```

---

## Module D · Global Visual Layers

### Task 12: GlobalGrain — SVG noise overlay

**Files:**
- Create: `demo/presentation/src/layers/GlobalGrain.jsx`

- [ ] **Step 1: Implement**

```jsx
// SVG noise overlay — fixed full-viewport, multiply blend, opacity 0.5
// Per outline-visual.md §9.2
export function GlobalGrain() {
  const svgUrl = `data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.15 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E`;
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 1, pointerEvents: 'none',
        backgroundImage: `url("${svgUrl}")`,
        mixBlendMode: 'multiply',
        opacity: 0.5,
      }}
    />
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/layers/GlobalGrain.jsx
git commit -m "feat(demo): GlobalGrain SVG noise overlay"
```

---

### Task 13: HalftoneBg — drift animation

**Files:**
- Create: `demo/presentation/src/layers/HalftoneBg.jsx`

- [ ] **Step 1: Implement**

```jsx
// Halftone dots with 60s drift loop — per outline-visual.md §9.4
export function HalftoneBg() {
  return (
    <div
      aria-hidden="true"
      className="halftone-bg"
      style={{
        position: 'fixed', inset: 0, zIndex: 5, pointerEvents: 'none',
        backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
        backgroundSize: '20px 20px',
        opacity: 0.15,
        animation: 'halftone-drift 60s linear infinite',
      }}
    />
  );
}
```

- [ ] **Step 2: Add keyframe to `src/index.css`** (append to existing file)

```css
@keyframes halftone-drift {
  from { background-position: 0 0; }
  to   { background-position: 0 -20px; }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/layers/HalftoneBg.jsx src/index.css
git commit -m "feat(demo): HalftoneBg with 60s drift loop"
```

---

### Task 14: ChapterTint — per-chapter gradient

**Files:**
- Create: `demo/presentation/src/layers/ChapterTint.jsx`

- [ ] **Step 1: Implement**

```jsx
// Per-chapter diagonal background gradient — per outline-visual.md §9.1
import { getChapter } from '../tokens/chapters.js';

export function ChapterTint({ chapterId }) {
  const ch = getChapter(chapterId);
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 10, pointerEvents: 'none',
        background: `linear-gradient(135deg, #FFFDF5 0%, ${ch.tint} 100%)`,
        transition: 'background 500ms ease-out',
      }}
    />
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/layers/ChapterTint.jsx
git commit -m "feat(demo): ChapterTint per-chapter background gradient"
```

---

### Task 15: AmbientShapes — floating decorative shapes

**Files:**
- Create: `demo/presentation/src/layers/AmbientShapes.jsx`

- [ ] **Step 1: Implement**

```jsx
// 4-6 floating shapes per chapter — per outline-visual.md §9.6
import { getChapter } from '../tokens/chapters.js';

const POSITION_STYLE = {
  tl: { top: '5%',  left: '5%'  },
  tr: { top: '5%',  right: '5%' },
  bl: { bottom: '8%', left: '5%' },
  br: { bottom: '8%', right: '5%' },
  ml: { top: '50%', left: '3%',  transform: 'translateY(-50%)' },
  mr: { top: '50%', right: '3%', transform: 'translateY(-50%)' },
  mc: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
};

const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  ink:       '#000000',
};

function Shape({ shape, color, outline }) {
  const fill = COLOR_MAP[color] ?? color;
  const border = outline ? `4px solid ${fill}` : 'none';
  const bg = outline ? 'transparent' : fill;
  if (shape === 'star') {
    return <svg width="48" height="48" viewBox="0 0 48 48" style={{ overflow: 'visible' }}>
      <polygon points="24,2 30,18 47,18 33,28 38,46 24,36 10,46 15,28 1,18 18,18"
        fill={outline ? 'transparent' : fill} stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
    </svg>;
  }
  if (shape === 'triangle') {
    return <svg width="48" height="48" viewBox="0 0 48 48">
      <polygon points="24,4 44,44 4,44" fill={outline ? 'transparent' : fill} stroke="#000" strokeWidth="3" strokeLinejoin="miter" />
    </svg>;
  }
  if (shape === 'circle') {
    return <div style={{ width: 48, height: 48, borderRadius: '50%', background: bg, border: outline ? border : '3px solid #000' }} />;
  }
  if (shape === 'pill') {
    return <div style={{ width: 72, height: 28, borderRadius: 9999, background: bg, border: outline ? border : '3px solid #000' }} />;
  }
  if (shape === 'outline-question') {
    return <div style={{
      width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center',
      border: '3px solid #000', background: 'transparent', fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: 32,
    }}>?</div>;
  }
  // default: square
  return <div style={{ width: 48, height: 48, background: bg, border: outline ? border : '3px solid #000' }} />;
}

export function AmbientShapes({ chapterId }) {
  const ch = getChapter(chapterId);
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
      {ch.ambientShapes.map((s, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            ...POSITION_STYLE[s.position],
            transform: `${POSITION_STYLE[s.position]?.transform ?? ''} rotate(${s.rotation}deg)`,
            animation: `ambient-float ${4 + (i % 4)}s ease-in-out infinite`,
            animationDelay: `${i * 0.3}s`,
          }}
        >
          <Shape shape={s.shape} color={s.color} outline={s.outline} />
        </div>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Add keyframe to `src/index.css`**

```css
@keyframes ambient-float {
  0%, 100% { translate: 0 0; }
  50%      { translate: 4px -8px; }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/layers/AmbientShapes.jsx src/index.css
git commit -m "feat(demo): AmbientShapes 4-6 floating per-chapter decorative shapes"
```

---

### Task 16: FadeBridge — chapter transition

**Files:**
- Create: `demo/presentation/src/layers/FadeBridge.jsx`

- [ ] **Step 1: Implement**

```jsx
// 0.8-1.2s auto fade-bridge between chapters — per outline-visual.md §10
import { useEffect, useState } from 'react';

const BIG_TRANSITIONS = new Set(['1-2', '4-5', '8-9']);

export function FadeBridge({ chapterId }) {
  const [active, setActive] = useState(false);
  const [prevChapter, setPrevChapter] = useState(chapterId);

  useEffect(() => {
    if (chapterId !== prevChapter) {
      const key = `${prevChapter}-${chapterId}`;
      const duration = BIG_TRANSITIONS.has(key) ? 1500 : 1000;
      setActive(true);
      const t = setTimeout(() => {
        setActive(false);
        setPrevChapter(chapterId);
      }, duration);
      return () => clearTimeout(t);
    }
  }, [chapterId, prevChapter]);

  if (!active) return null;
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'fixed', inset: 0, zIndex: 80, pointerEvents: 'none',
        background: '#FFFDF5',
        animation: 'fade-bridge 1000ms ease-out forwards',
      }}
    />
  );
}
```

- [ ] **Step 2: Add keyframe to `src/index.css`**

```css
@keyframes fade-bridge {
  0%   { opacity: 0; }
  30%  { opacity: 1; }
  70%  { opacity: 1; }
  100% { opacity: 0; }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/layers/FadeBridge.jsx src/index.css
git commit -m "feat(demo): FadeBridge chapter transition"
```

---

## Module E · Shared UI Components

### Task 17: ProgressBar — hover-bottom

**Files:**
- Create: `demo/presentation/src/components/ProgressBar.jsx`

- [ ] **Step 1: Implement**

```jsx
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';

export function ProgressBar() {
  const { globalBeatIdx, totalBeats, progressVisible } = usePresentationContext();
  const [hover, setHover] = useState(false);
  const visible = hover || progressVisible;
  const pct = ((globalBeatIdx + 1) / totalBeats) * 100;

  useEffect(() => {
    const onMove = (e) => setHover(e.clientY > window.innerHeight - 32);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <div
      style={{
        position: 'fixed', left: 0, right: 0, bottom: 0,
        height: 24, zIndex: 90,
        opacity: visible ? 0.8 : 0,
        transition: visible ? 'opacity 0.6s' : 'opacity 1s',
        background: 'rgba(255,253,245,0.6)',
        borderTop: '2px solid #000',
        display: 'flex', alignItems: 'center', padding: '0 16px',
        fontFamily: 'Space Grotesk', fontWeight: 700, fontSize: 11,
      }}
    >
      <div style={{ flex: 1, height: 6, background: '#fff', border: '1px solid #000', position: 'relative' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: `${pct}%`, background: '#FF6B6B' }} />
      </div>
      <div style={{ marginLeft: 12 }}>{globalBeatIdx + 1} / {totalBeats}</div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ProgressBar.jsx
git commit -m "feat(demo): ProgressBar hover-bottom hidden indicator"
```

---

### Task 18: ChapterNav — hover-top-right

**Files:**
- Create: `demo/presentation/src/components/ChapterNav.jsx`

- [ ] **Step 1: Implement**

```jsx
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { chapters } from '../tokens/chapters.js';

export function ChapterNav() {
  const { chapterId, jumpTo } = usePresentationContext();
  const [hover, setHover] = useState(false);

  useEffect(() => {
    const onMove = (e) => setHover(e.clientX > window.innerWidth - 200 && e.clientY < 60);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <nav
      style={{
        position: 'fixed', top: 8, right: 8, zIndex: 90,
        opacity: hover ? 0.95 : 0,
        transition: hover ? 'opacity 0.4s' : 'opacity 0.8s',
        pointerEvents: hover ? 'auto' : 'none',
        background: '#FFFDF5', border: '4px solid #000', padding: 8,
        display: 'flex', gap: 4, fontFamily: 'Space Grotesk', fontWeight: 900,
      }}
    >
      {chapters.map(c => (
        <button
          key={c.id}
          onClick={() => jumpTo({ chapterId: c.id, stepId: 1, beatIndex: 0 })}
          style={{
            width: 28, height: 28,
            background: c.id === chapterId ? '#FF6B6B' : '#fff',
            color: '#000', border: '2px solid #000', cursor: 'pointer',
            fontFamily: 'inherit', fontWeight: 'inherit', fontSize: 14,
          }}
        >{c.id}</button>
      ))}
    </nav>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ChapterNav.jsx
git commit -m "feat(demo): ChapterNav hover-top-right chapter switcher"
```

---

### Task 19: BeatIndicator — 88 squares

**Files:**
- Create: `demo/presentation/src/components/BeatIndicator.jsx`

- [ ] **Step 1: Implement**

```jsx
// 88 squares + chapter boundary yellow gaps — per outline-visual.md §9.5
import { useState, useEffect, useMemo } from 'react';
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { flattenBeats } from '../data/beat-manifest.js';

export function BeatIndicator() {
  const { globalBeatIdx, totalBeats, chapterId, stepId, beatIndex } = usePresentationContext();
  const [hover, setHover] = useState(false);
  const flat = useMemo(() => flattenBeats(), []);

  useEffect(() => {
    const onMove = (e) => setHover(e.clientY > window.innerHeight - 32);
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <div
      style={{
        position: 'fixed', bottom: 26, left: 16, right: 16, zIndex: 88,
        height: 8, display: 'flex', alignItems: 'center', gap: 1,
        opacity: hover ? 0.7 : 0,
        transition: hover ? 'opacity 0.6s' : 'opacity 1s',
        pointerEvents: 'none',
      }}
    >
      {flat.map((f, i) => {
        const isChapterStart = i > 0 && f.chapterId !== flat[i - 1].chapterId;
        const isCurrent = i === globalBeatIdx;
        const isPast = i < globalBeatIdx;
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center' }}>
            {isChapterStart && <div style={{ width: 4, height: 6, background: '#FFD93D', marginRight: 2 }} />}
            <div style={{
              width: 8, height: 5,
              background: isCurrent ? '#FF6B6B' : isPast ? '#000' : 'transparent',
              border: isCurrent || isPast ? 'none' : '1px solid #000',
              transform: isCurrent ? 'scaleY(1.5)' : 'none',
            }} />
          </div>
        );
      })}
      <div style={{
        marginLeft: 'auto', fontSize: 11, fontFamily: 'Space Grotesk', fontWeight: 700, color: '#666',
      }}>
        step {flat.findIndex(f => f.chapterId === chapterId && f.stepId === stepId) + 1} / 57 · beat {beatIndex + 1} · ch {chapterId}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/BeatIndicator.jsx
git commit -m "feat(demo): BeatIndicator 88-square hover-bottom strip"
```

---

### Task 20: PresenterPanel — ?presenter=1 overlay

**Files:**
- Create: `demo/presentation/src/components/PresenterPanel.jsx`

- [ ] **Step 1: Implement**

```jsx
// Speaker mode overlay — per outline-visual.md §5.6
import { usePresentationContext } from '../state/PresentationContext.jsx';
import { flattenBeats } from '../data/beat-manifest.js';
import { useMemo } from 'react';

export function PresenterPanel() {
  const { presenter, globalBeatIdx, beat, chapter, step, beatIndex } = usePresentationContext();
  const flat = useMemo(() => flattenBeats(), []);
  if (!presenter) return null;

  const next = flat[globalBeatIdx + 1];

  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 100, pointerEvents: 'none',
        display: 'flex', flexDirection: 'column',
        background: 'rgba(255,253,245,0.96)', padding: 24,
        fontFamily: 'Space Grotesk', color: '#000',
      }}
    >
      <div style={{ borderBottom: '4px solid #000', paddingBottom: 12, fontSize: 16, fontWeight: 700 }}>
        ch {chapter.id} / 9 · step {step.id} · beat {beatIndex + 1} / {step.beats.length}
        {step.starLevel === 3 && <span style={{ marginLeft: 12, color: '#FF6B6B' }}>★★★</span>}
        {step.starLevel === 2 && <span style={{ marginLeft: 12, color: '#FF6B6B' }}>★★</span>}
      </div>

      <div style={{ marginTop: 24, fontSize: 14, fontWeight: 700, color: '#666' }}>▣ Cue (該說):</div>
      <div style={{ marginTop: 8, fontSize: 24, fontWeight: 900, lineHeight: 1.4 }}>
        {beat.cue ?? <em style={{ color: '#999' }}>（無 cue）</em>}
      </div>

      <div style={{ marginTop: 24, fontSize: 14, fontWeight: 700, color: '#666' }}>▣ Wait:</div>
      <div style={{ marginTop: 8, fontSize: 18, fontWeight: 700 }}>
        {beat.wait ?? <em style={{ color: '#999' }}>—</em>}
      </div>

      {next && (
        <div style={{ marginTop: 'auto', borderTop: '4px solid #000', paddingTop: 12, fontSize: 14, fontWeight: 700 }}>
          下一 beat: ch{next.chapterId} step{next.stepId} · {next.beat.id}
          <div style={{ fontSize: 14, color: '#666', marginTop: 4 }}>cue: {next.beat.cue ?? '—'}</div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/PresenterPanel.jsx
git commit -m "feat(demo): PresenterPanel ?presenter=1 overlay"
```

---

### Task 21: Sticker primitive

**Files:**
- Create: `demo/presentation/src/components/Sticker.jsx`

- [ ] **Step 1: Implement**

```jsx
// Sticker primitive — 4-6px black border + hard shadow + optional rotation
const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  cream:     '#FFFDF5',
  ink:       '#000000',
};
const SHADOW_MAP = {
  sm:      '4px 4px 0 0 #000',
  md:      '8px 8px 0 0 #000',
  lg:      '12px 12px 0 0 #000',
  massive: '16px 16px 0 0 #000',
  burst:   '20px 20px 0 0 #000',
};

export function Sticker({
  bg = 'accent', textColor, border = 4, shadow = 'md',
  rotation = 0, padding = 16, children, className = '', style = {},
}) {
  return (
    <div
      className={className}
      style={{
        display: 'inline-block',
        background: COLOR_MAP[bg] ?? bg,
        color: textColor ? (COLOR_MAP[textColor] ?? textColor) : '#000',
        border: `${border}px solid #000`,
        boxShadow: SHADOW_MAP[shadow] ?? shadow,
        padding,
        transform: `rotate(${rotation}deg)`,
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        ...style,
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/Sticker.jsx
git commit -m "feat(demo): Sticker primitive (border + hard shadow + rotation)"
```

---

### Task 22: Hero primitive

**Files:**
- Create: `demo/presentation/src/components/Hero.jsx`

- [ ] **Step 1: Implement**

```jsx
// Hero primitive — full-bleed centered with sized typography
const SIZE_MAP = {
  mega: '8rem',
  hero: '6rem',
  h1:   '3.75rem',
  h2:   '3rem',
};

export function Hero({ size = 'hero', children, color, stroke = false, className = '', style = {} }) {
  return (
    <div
      className={className}
      style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        fontSize: SIZE_MAP[size] ?? size,
        lineHeight: 1.05,
        textAlign: 'center',
        color: stroke ? 'transparent' : (color ?? '#000'),
        WebkitTextStroke: stroke ? '2px black' : 'initial',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/Hero.jsx
git commit -m "feat(demo): Hero primitive (mega/hero/h1/h2 sizes + text-stroke option)"
```

---

### Task 23: AssetPlaceholder — TODO flag

**Files:**
- Create: `demo/presentation/src/components/AssetPlaceholder.jsx`
- Create: `demo/presentation/TODO.md`

- [ ] **Step 1: Implement component**

```jsx
// Placeholder with cream + 4px red dashed border + ⚠️ TODO label
export function AssetPlaceholder({ type = '[E]', width = 600, height = 360, todo = 'asset TODO' }) {
  return (
    <div
      role="img"
      aria-label={`TODO: ${todo}`}
      style={{
        width, height,
        background: '#FFFDF5',
        border: '4px dashed #FF6B6B',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column', padding: 16, textAlign: 'center',
        fontFamily: 'Space Grotesk', fontWeight: 700, color: '#FF6B6B',
      }}
    >
      <div style={{ fontSize: 14, marginBottom: 8 }}>{type}</div>
      <div style={{ fontSize: 18 }}>⚠️ TODO</div>
      <div style={{ fontSize: 14, marginTop: 8, color: '#000' }}>{todo}</div>
    </div>
  );
}
```

- [ ] **Step 2: Initialize `TODO.md`**

```markdown
# Asset TODO

> Placeholders rendered via `<AssetPlaceholder>`. Each line: `ch<N> s<M> — type — description`.
> Updated as each chapter's plan completes.

(none yet — populated during Phase 1-9)
```

- [ ] **Step 3: Commit**

```bash
git add src/components/AssetPlaceholder.jsx TODO.md
git commit -m "feat(demo): AssetPlaceholder component + TODO.md tracker"
```

---

## Module F · Motif Library (8 full + 5 shells)

### Task 24: BoomDoubleRing motif

**Files:**
- Create: `demo/presentation/src/motifs/BoomDoubleRing.jsx`

- [ ] **Step 1: Implement**

```jsx
// Yellow outer ring + red inner ring stamp — per outline-visual.md §7
import { motion } from 'motion/react';

export function BoomDoubleRing({ active = false, size = 320, style = {} }) {
  const animate = active ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 };
  return (
    <div style={{ position: 'relative', width: size, height: size, ...style }}>
      <motion.div
        initial={false}
        animate={animate}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1], delay: 0.08 }}
        style={{
          position: 'absolute', inset: 0,
          border: '8px solid #FFD93D',
          borderRadius: '50%',
          boxShadow: '8px 8px 0 0 #000',
        }}
      />
      <motion.div
        initial={false}
        animate={animate}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1], delay: 0.12 }}
        style={{
          position: 'absolute', inset: '20%',
          border: '8px solid #FF6B6B',
          borderRadius: '50%',
          boxShadow: '6px 6px 0 0 #000',
        }}
      />
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/BoomDoubleRing.jsx
git commit -m "feat(demo): motif BoomDoubleRing"
```

---

### Task 25: CrashLine motif

**Files:**
- Create: `demo/presentation/src/motifs/CrashLine.jsx`

- [ ] **Step 1: Implement**

```jsx
// Cream big-text box + 6px red border + flash + blinking caret placeholder
import { useState, useEffect } from 'react';
import { motion } from 'motion/react';

export function CrashLine({ active = false, filled = false, text = '⋯⋯結果我錯了', width = 720 }) {
  const [flashCount, setFlashCount] = useState(0);

  useEffect(() => {
    if (filled) {
      setFlashCount(2);
      const t1 = setTimeout(() => setFlashCount(1), 200);
      const t2 = setTimeout(() => setFlashCount(0), 400);
      return () => { clearTimeout(t1); clearTimeout(t2); };
    }
  }, [filled]);

  return (
    <motion.div
      initial={false}
      animate={active ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3 }}
      style={{
        width,
        background: '#FFFDF5',
        border: `6px solid ${flashCount > 0 ? '#FF6B6B' : '#FF6B6B'}`,
        boxShadow: filled ? '16px 16px 0 0 #000' : '8px 8px 0 0 #000',
        padding: '32px 48px',
        fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: '3rem',
        textAlign: 'center',
        transform: 'rotate(1deg)',
        transition: 'box-shadow 200ms',
        outline: flashCount === 2 ? '4px solid #FF6B6B' : 'none',
        outlineOffset: 4,
      }}
    >
      {filled ? text : <BlinkingCaret />}
    </motion.div>
  );
}

function BlinkingCaret() {
  return <span style={{ animation: 'caret-blink 1s steps(2) infinite', color: '#FF6B6B' }}>_</span>;
}
```

- [ ] **Step 2: Add caret keyframe to `src/index.css`**

```css
@keyframes caret-blink {
  50% { opacity: 0; }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/motifs/CrashLine.jsx src/index.css
git commit -m "feat(demo): motif CrashLine with placeholder caret + flash"
```

---

### Task 26: RedStamp motif

**Files:**
- Create: `demo/presentation/src/motifs/RedStamp.jsx`

- [ ] **Step 1: Implement**

```jsx
// Red stamp drops from above with overshoot bounce + shadow burst
import { motion } from 'motion/react';

export function RedStamp({ active = false, children, rotation = -3, size = 'large', shadow = '16px 16px 0 0 #000' }) {
  const fontSize = size === 'large' ? '5rem' : size === 'medium' ? '3rem' : '2rem';
  return (
    <motion.div
      initial={false}
      animate={active ? { y: 0, scale: 1, opacity: 1 } : { y: -200, scale: 0, opacity: 0 }}
      transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      style={{
        display: 'inline-block',
        background: '#FF6B6B',
        color: '#FFFDF5',
        border: '6px solid #000',
        boxShadow: shadow,
        padding: '24px 48px',
        transform: `rotate(${rotation}deg)`,
        fontFamily: 'Space Grotesk', fontWeight: 900, fontSize,
      }}
    >
      {children}
    </motion.div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/RedStamp.jsx
git commit -m "feat(demo): motif RedStamp with overshoot bounce"
```

---

### Task 27: YellowHighlight motif

**Files:**
- Create: `demo/presentation/src/motifs/YellowHighlight.jsx`

- [ ] **Step 1: Implement**

```jsx
// Yellow highlight box for keyword emphasis — supports mask-reveal animation
import { motion } from 'motion/react';

export function YellowHighlight({ active = false, children, padding = '4px 12px', className = '', style = {} }) {
  return (
    <motion.span
      initial={false}
      animate={active ? { clipPath: 'inset(0 0 0 0)' } : { clipPath: 'inset(0 100% 0 0)' }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={className}
      style={{
        display: 'inline-block',
        background: '#FFD93D',
        border: '3px solid #000',
        boxShadow: '4px 4px 0 0 #000',
        padding,
        fontFamily: 'Space Grotesk', fontWeight: 900,
        ...style,
      }}
    >
      {children}
    </motion.span>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/YellowHighlight.jsx
git commit -m "feat(demo): motif YellowHighlight with mask-reveal"
```

---

### Task 28: SpotlightVignette motif (also climax G)

**Files:**
- Create: `demo/presentation/src/motifs/SpotlightVignette.jsx`

- [ ] **Step 1: Implement**

```jsx
// Radial gradient overlay with multiply blend — per outline-visual.md §7 / §8 climax G
import { motion } from 'motion/react';

export function SpotlightVignette({ active = false, centerX = '50%', centerY = '50%' }) {
  return (
    <motion.div
      aria-hidden="true"
      initial={false}
      animate={{ opacity: active ? 1 : 0 }}
      transition={{ duration: 0.5 }}
      style={{
        position: 'fixed', inset: 0, zIndex: 50, pointerEvents: 'none',
        background: `radial-gradient(circle at ${centerX} ${centerY}, transparent 25%, rgba(0,0,0,0.6) 100%)`,
        mixBlendMode: 'multiply',
      }}
    />
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/SpotlightVignette.jsx
git commit -m "feat(demo): motif SpotlightVignette (climax G)"
```

---

### Task 29: HalftoneBurst motif (also climax B)

**Files:**
- Create: `demo/presentation/src/motifs/HalftoneBurst.jsx`

- [ ] **Step 1: Implement**

```jsx
// Halftone dots burst from center — per outline-visual.md §7 / §8 climax B
import { motion } from 'motion/react';

export function HalftoneBurst({ active = false, size = 600, centerX = '50%', centerY = '50%' }) {
  return (
    <motion.div
      aria-hidden="true"
      initial={false}
      animate={{
        scale: active ? 3 : 0,
        opacity: active ? [1, 1, 0] : 0,
      }}
      transition={{ duration: 0.5, ease: 'easeOut', times: active ? [0, 0.2, 1] : [0, 1] }}
      style={{
        position: 'absolute', left: centerX, top: centerY,
        width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2,
        zIndex: 40, pointerEvents: 'none',
        backgroundImage: 'radial-gradient(#000 2px, transparent 2.5px)',
        backgroundSize: '30px 30px',
        mask: 'radial-gradient(circle, #000 0%, #000 70%, transparent 100%)',
        WebkitMask: 'radial-gradient(circle, #000 0%, #000 70%, transparent 100%)',
      }}
    />
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/HalftoneBurst.jsx
git commit -m "feat(demo): motif HalftoneBurst (climax B)"
```

---

### Task 30: InkSplatter motif (also climax E)

**Files:**
- Create: `demo/presentation/src/motifs/InkSplatter.jsx`

- [ ] **Step 1: Implement**

```jsx
// 4 or 8 inkblot paths radiating with stagger — per outline-visual.md §7 / §8 climax E
import { motion } from 'motion/react';

// Pseudo-random inkblot SVG paths (small, stylized irregular shapes)
const BLOBS = [
  'M0,0 C8,-12 22,-8 28,4 C32,12 18,24 6,18 Z',
  'M0,0 C-10,-6 -4,-22 8,-16 C18,-10 14,8 4,12 Z',
  'M0,0 C12,-4 24,12 14,18 C2,22 -8,8 -2,-2 Z',
  'M0,0 C-14,-8 -4,18 6,14 C18,8 8,-12 0,-6 Z',
  'M0,0 C10,8 0,22 -10,16 C-18,12 -10,-4 0,-4 Z',
  'M0,0 C-8,6 -22,-2 -16,-14 C-8,-22 6,-12 4,-2 Z',
  'M0,0 C8,12 -10,20 -16,10 C-22,0 -8,-12 0,-6 Z',
  'M0,0 C16,4 18,-12 6,-18 C-4,-22 -10,-8 -2,-2 Z',
];

export function InkSplatter({ active = false, count = 8, radius = 140, centerX = '50%', centerY = '50%' }) {
  const blobs = BLOBS.slice(0, count);
  return (
    <div aria-hidden="true" style={{
      position: 'absolute', left: centerX, top: centerY,
      width: 0, height: 0, zIndex: 40, pointerEvents: 'none',
    }}>
      {blobs.map((path, i) => {
        const angle = (i / count) * Math.PI * 2;
        const r = radius * (0.6 + 0.4 * ((i * 7) % 5) / 5);
        const x = Math.cos(angle) * r;
        const y = Math.sin(angle) * r;
        return (
          <motion.svg
            key={i}
            initial={false}
            animate={{ scale: active ? 1 : 0, opacity: active ? 1 : 0 }}
            transition={{ duration: 0.3, delay: active ? 0.08 * i : 0, ease: [0.34, 1.56, 0.64, 1] }}
            width="40" height="40" viewBox="-20 -20 40 40"
            style={{ position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(${i * 47}deg)` }}
          >
            <path d={path} fill="#000" />
          </motion.svg>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/InkSplatter.jsx
git commit -m "feat(demo): motif InkSplatter (climax E)"
```

---

### Task 31: ScreenShake motif (also climax A)

**Files:**
- Create: `demo/presentation/src/motifs/ScreenShake.jsx`

- [ ] **Step 1: Implement**

```jsx
// Wraps children and applies a random shake to the wrapper — per outline-visual.md §7 / §8 climax A
import { useAnimate } from 'motion/react';
import { useEffect, forwardRef, useImperativeHandle, useRef } from 'react';

export const ScreenShake = forwardRef(function ScreenShake({ children, light = false }, ref) {
  const [scope, animate] = useAnimate();
  const internalRef = useRef(null);

  useImperativeHandle(ref, () => ({
    play: async () => {
      const intensity = light ? 2 : 5;
      const cycles = light ? 1 : 3;
      const keyframes = [];
      for (let i = 0; i < cycles; i++) {
        keyframes.push({ x: (Math.random() - 0.5) * intensity * 2, y: (Math.random() - 0.5) * intensity * 2 });
      }
      keyframes.push({ x: 0, y: 0 });
      await animate(scope.current, keyframes, { duration: light ? 0.08 : 0.15 });
    },
  }), [animate, scope, light]);

  return <div ref={scope} style={{ display: 'contents' }}>{children}</div>;
});
```

- [ ] **Step 2: Commit**

```bash
git add src/motifs/ScreenShake.jsx
git commit -m "feat(demo): motif ScreenShake (climax A) via imperative ref"
```

---

### Task 32: 5 motif shells (GirlNew / GirlVeteran / ThirteenStairs / FlipTwentyToFifty / SudokuBoard)

**Files:**
- Create: `demo/presentation/src/motifs/GirlNew.jsx`
- Create: `demo/presentation/src/motifs/GirlVeteran.jsx`
- Create: `demo/presentation/src/motifs/ThirteenStairs.jsx`
- Create: `demo/presentation/src/motifs/FlipTwentyToFifty.jsx`
- Create: `demo/presentation/src/motifs/SudokuBoard.jsx`

Each shell renders an `<AssetPlaceholder>` with appropriate TODO message.

- [ ] **Step 1: GirlNew shell**

```jsx
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';
export function GirlNew(props) {
  return <AssetPlaceholder type="motif/girl-new" width={280} height={200} todo="ch 6 s3 粉紅新女生 sticker + +/+/+ 浮動" {...props} />;
}
```

- [ ] **Step 2: GirlVeteran shell**

```jsx
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';
export function GirlVeteran(props) {
  return <AssetPlaceholder type="motif/girl-veteran" width={320} height={220} todo="ch 7 s7 老油條陷阱題 sticker + ❌ 箭頭" {...props} />;
}
```

- [ ] **Step 3: ThirteenStairs shell**

```jsx
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';
export function ThirteenStairs(props) {
  return <AssetPlaceholder type="motif/13-stairs" width={800} height={500} todo="ch 7 s3 13 招技巧階梯 SVG (X-Wing/XYZ-Wing 最大)" {...props} />;
}
```

- [ ] **Step 4: FlipTwentyToFifty shell**

```jsx
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';
export function FlipTwentyToFifty(props) {
  return <AssetPlaceholder type="motif/flip-20-to-50" width={400} height={240} todo="ch 8 s4 +20 → +50 3D flip 翻牌" {...props} />;
}
```

- [ ] **Step 5: SudokuBoard shell**

```jsx
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';
export function SudokuBoard(props) {
  return <AssetPlaceholder type="motif/sudoku-board" width={400} height={400} todo="ch 7 s5 / ch 8 s2-3 9×9 盤面 SVG" {...props} />;
}
```

- [ ] **Step 6: Append to `TODO.md`**

```markdown
## Phase 0 reserved motif shells

- ch6 s3 — motif/girl-new — 粉紅新女生 sticker + +/+/+ 浮動
- ch7 s7 — motif/girl-veteran — 老油條陷阱題 sticker + ❌ 箭頭
- ch7 s3 — motif/13-stairs — 13 招階梯 SVG
- ch7 s5 / ch8 s2-s3 — motif/sudoku-board — 9×9 盤面 SVG
- ch8 s4 — motif/flip-20-to-50 — 3D flip 翻牌
```

- [ ] **Step 7: Commit**

```bash
git add src/motifs/GirlNew.jsx src/motifs/GirlVeteran.jsx src/motifs/ThirteenStairs.jsx src/motifs/FlipTwentyToFifty.jsx src/motifs/SudokuBoard.jsx TODO.md
git commit -m "feat(demo): 5 motif shells + TODO.md updated"
```

---

## Module G · Climax FX

### Task 33: useClimax orchestrator hook (TDD)

**Files:**
- Create: `demo/presentation/src/climax/useClimax.test.js`
- Create: `demo/presentation/src/climax/useClimax.js`
- Create: `demo/presentation/src/climax/animations.js`

- [ ] **Step 1: Write failing test**

```js
// src/climax/useClimax.test.js
import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useClimax } from './useClimax.js';

describe('useClimax', () => {
  it('returns an object with play/active/setActive', () => {
    const { result } = renderHook(() => useClimax(['A', 'C']));
    expect(typeof result.current.play).toBe('function');
    expect(result.current.activeFX).toEqual({ A: false, B: false, C: false, E: false, G: false });
  });

  it('activates fx codes on play()', async () => {
    const { result } = renderHook(() => useClimax(['A', 'B', 'G']));
    await act(async () => { await result.current.play(); });
    expect(result.current.activeFX.A).toBe(true);
    expect(result.current.activeFX.B).toBe(true);
    expect(result.current.activeFX.G).toBe(true);
    expect(result.current.activeFX.C).toBe(false);
    expect(result.current.activeFX.E).toBe(false);
  });

  it('reset() clears all activeFX', async () => {
    const { result } = renderHook(() => useClimax(['A', 'B']));
    await act(async () => { await result.current.play(); });
    expect(result.current.activeFX.A).toBe(true);
    act(() => result.current.reset());
    expect(result.current.activeFX.A).toBe(false);
    expect(result.current.activeFX.B).toBe(false);
  });
});
```

- [ ] **Step 2: Run, verify fail**

```bash
npm run test:run -- useClimax
```

Expected: All tests FAIL.

- [ ] **Step 3: Implement `src/climax/animations.js`**

```js
// Pure animation values for A (shake) and C (overshoot) — used by hooks
export const SHAKE_KEYFRAMES = {
  light: { x: [0, 2, -2, 0], y: [0, 1, -1, 0], duration: 0.08 },
  full:  { x: [0, 5, -5, 3, -3, 0], y: [0, 3, -3, 2, -2, 0], duration: 0.15 },
};

export const OVERSHOOT_KEYFRAMES = {
  scale: [0, 1.4, 1.0, 0.95, 1.0],
  duration: 0.6,
  ease: [0.34, 1.56, 0.64, 1],
};
```

- [ ] **Step 4: Implement `src/climax/useClimax.js`**

```js
import { useState, useCallback } from 'react';

const ALL_FX = ['A', 'B', 'C', 'E', 'G'];

export function useClimax(variants = []) {
  const [activeFX, setActiveFX] = useState(
    Object.fromEntries(ALL_FX.map(k => [k, false]))
  );

  const play = useCallback(async () => {
    const next = Object.fromEntries(ALL_FX.map(k => [k, variants.includes(k)]));
    setActiveFX(next);
    // Hold for ~600ms then return; consumer can call reset() to hide overlays
    await new Promise(r => setTimeout(r, 600));
  }, [variants]);

  const reset = useCallback(() => {
    setActiveFX(Object.fromEntries(ALL_FX.map(k => [k, false])));
  }, []);

  return { activeFX, play, reset };
}
```

- [ ] **Step 5: Run tests, verify pass**

```bash
npm run test:run -- useClimax
```

Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/climax/useClimax.js src/climax/useClimax.test.js src/climax/animations.js
git commit -m "feat(demo): useClimax hook orchestrating A/B/C/E/G FX"
```

---

## Module H · Sandbox Verification Page

### Task 34: Sandbox page scaffold + integrate global layers

**Files:**
- Create: `demo/presentation/src/pages/Sandbox.jsx`
- Modify: `demo/presentation/src/App.jsx`

- [ ] **Step 1: Create `src/pages/Sandbox.jsx`**

```jsx
import { useRef, useState } from 'react';
import { GlobalGrain } from '../layers/GlobalGrain.jsx';
import { HalftoneBg } from '../layers/HalftoneBg.jsx';
import { ChapterTint } from '../layers/ChapterTint.jsx';
import { AmbientShapes } from '../layers/AmbientShapes.jsx';
import { Sticker } from '../components/Sticker.jsx';
import { Hero } from '../components/Hero.jsx';
import { BoomDoubleRing } from '../motifs/BoomDoubleRing.jsx';
import { CrashLine } from '../motifs/CrashLine.jsx';
import { RedStamp } from '../motifs/RedStamp.jsx';
import { YellowHighlight } from '../motifs/YellowHighlight.jsx';
import { SpotlightVignette } from '../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../motifs/InkSplatter.jsx';
import { ScreenShake } from '../motifs/ScreenShake.jsx';
import { GirlNew } from '../motifs/GirlNew.jsx';
import { GirlVeteran } from '../motifs/GirlVeteran.jsx';
import { ThirteenStairs } from '../motifs/ThirteenStairs.jsx';
import { FlipTwentyToFifty } from '../motifs/FlipTwentyToFifty.jsx';
import { SudokuBoard } from '../motifs/SudokuBoard.jsx';
import { useClimax } from '../climax/useClimax.js';

export function Sandbox() {
  const [chapterId, setChapterId] = useState(1);
  const [boomActive, setBoomActive] = useState(false);
  const [crashFilled, setCrashFilled] = useState(false);
  const [stampActive, setStampActive] = useState(false);
  const [highlightActive, setHighlightActive] = useState(false);
  const shakeRef = useRef(null);

  const climaxAC = useClimax(['A', 'C']);
  const climaxFull = useClimax(['A', 'B', 'C', 'E', 'G']);

  const triggerShake = () => shakeRef.current?.play();

  return (
    <ScreenShake ref={shakeRef}>
      <AmbientShapes chapterId={chapterId} />
      <GlobalGrain />
      <HalftoneBg />
      <ChapterTint chapterId={chapterId} />

      <SpotlightVignette active={climaxFull.activeFX.G || climaxAC.activeFX.G} />
      <HalftoneBurst active={climaxFull.activeFX.B || climaxAC.activeFX.B} />
      <InkSplatter active={climaxFull.activeFX.E || climaxAC.activeFX.E} />

      <main style={{ position: 'relative', zIndex: 20, padding: 32, fontFamily: 'Space Grotesk' }}>
        <h1 style={{ fontSize: '3rem', fontWeight: 900, margin: 0 }}>Sandbox · 風格驗證</h1>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Chapter palette (切換看 tint + ambient shapes)</h2>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            {[1,2,3,4,5,6,7,8,9].map(i => (
              <button key={i} onClick={() => setChapterId(i)}
                style={{ width: 40, height: 40, border: '3px solid #000',
                  background: chapterId === i ? '#FF6B6B' : '#fff', fontWeight: 900, fontFamily: 'inherit', cursor: 'pointer' }}>
                {i}
              </button>
            ))}
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Sticker primitive</h2>
          <div style={{ display: 'flex', gap: 32, marginTop: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <Sticker bg="accent" rotation={-3} shadow="lg" padding={24}>心 虛</Sticker>
            <Sticker bg="secondary" rotation={2}>期中報告</Sticker>
            <Sticker bg="muted" rotation={-5}>敬請期待</Sticker>
            <Sticker bg="cream" rotation={1} shadow="md">cream sticker</Sticker>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Motif Library — 4 full visual</h2>
          <div style={{ display: 'flex', gap: 24, marginTop: 16, alignItems: 'center' }}>
            <div>
              <BoomDoubleRing active={boomActive} size={120} />
              <button onClick={() => setBoomActive(v => !v)} style={btn}>BoomRing toggle</button>
            </div>
            <div>
              <CrashLine active filled={crashFilled} width={360} />
              <button onClick={() => setCrashFilled(v => !v)} style={btn}>CrashLine fill toggle</button>
            </div>
            <div>
              <RedStamp active={stampActive} rotation={-3} size="medium">受害者</RedStamp>
              <button onClick={() => setStampActive(v => !v)} style={btn}>RedStamp toggle</button>
            </div>
            <div>
              重新塑造 <YellowHighlight active={highlightActive}>關鍵字</YellowHighlight>
              <button onClick={() => setHighlightActive(v => !v)} style={btn}>YellowHighlight toggle</button>
            </div>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Climax FX (overlays + screen shake)</h2>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
            <button onClick={() => { climaxAC.play(); triggerShake(); }} style={btn}>輕量 A+C (shake + overshoot)</button>
            <button onClick={() => { climaxFull.play(); triggerShake(); }} style={btn}>★★★ 全套 A+B+C+E+G</button>
            <button onClick={() => { climaxAC.reset(); climaxFull.reset(); }} style={btn}>reset overlays</button>
          </div>
        </section>

        <section style={{ marginTop: 32 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Motif shells (placeholders)</h2>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
            <GirlNew />
            <GirlVeteran />
            <FlipTwentyToFifty />
          </div>
          <div style={{ display: 'flex', gap: 16, marginTop: 16, flexWrap: 'wrap' }}>
            <ThirteenStairs />
            <SudokuBoard />
          </div>
        </section>

        <section style={{ marginTop: 48 }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>Hero primitive</h2>
          <div style={{ position: 'relative', height: 240, marginTop: 16, border: '4px solid #000', background: '#FFFDF5' }}>
            <Hero size="hero" stroke>訓 練 AI 解 數 獨</Hero>
          </div>
        </section>
      </main>
    </ScreenShake>
  );
}

const btn = {
  marginTop: 8, padding: '8px 16px', border: '3px solid #000', background: '#fff',
  fontFamily: 'Space Grotesk', fontWeight: 900, cursor: 'pointer',
};
```

- [ ] **Step 2: Update `src/App.jsx` to route to Sandbox**

Replace `src/App.jsx`:

```jsx
import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';
import { Sandbox } from './pages/Sandbox.jsx';
import { ProgressBar } from './components/ProgressBar.jsx';
import { ChapterNav } from './components/ChapterNav.jsx';
import { BeatIndicator } from './components/BeatIndicator.jsx';
import { PresenterPanel } from './components/PresenterPanel.jsx';
import { FadeBridge } from './layers/FadeBridge.jsx';
import { usePresentationContext as useCtx } from './state/PresentationContext.jsx';

function Frame() {
  const { chapterId } = useCtx();
  // Phase 0: route always shows Sandbox. Phase 1+ will switch on chapterId/stepId.
  return (
    <>
      <Sandbox />
      <FadeBridge chapterId={chapterId} />
      <BeatIndicator />
      <ProgressBar />
      <ChapterNav />
      <PresenterPanel />
    </>
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

- [ ] **Step 3: Run dev server + verify**

```bash
npm run dev
```

Open `http://localhost:5173/`. Expected:

- cream `#FFFDF5` background with subtle noise grain + slow halftone drift
- 5 floating ambient shapes near corners (slow `ambient-float` animation)
- "Sandbox · 風格驗證" big heading
- Chapter 1-9 buttons that switch tint + ambient shapes
- 4 sticker primitives rendered with rotation/shadow
- 4 motif buttons that toggle visual state (BoomDoubleRing animates in, CrashLine flashes red border, RedStamp drops in, YellowHighlight masks reveal)
- 2 climax buttons that trigger overlay FX (spotlight darkens, halftone burst expands, ink splatter dots stagger, screen shakes)
- 5 motif shell placeholders (red dashed borders with `⚠️ TODO` labels)
- Hero rendering "訓 練 AI 解 數 獨" with text-stroke
- Beat indicator strip appears hovering bottom 32px
- Progress bar appears hovering bottom 32px
- Chapter nav appears hovering top-right
- `?presenter=1` URL shows PresenterPanel overlay covering the screen

- [ ] **Step 4: Commit**

```bash
git add src/pages/Sandbox.jsx src/App.jsx
git commit -m "feat(demo): Sandbox verification page integrating all Phase 0 pieces"
```

---

## Module I · Phase 0 Checkpoint

### Task 35: Phase 0 final verification + checkpoint commit

**Files:**
- Modify: `demo/presentation/README.md` (or create)

- [ ] **Step 1: Create `demo/presentation/README.md`**

```markdown
# Presentation · HTML 演講簡報

Click-driven Neo-brutalism presentation. See:
- [demo/outline.md](../outline.md) — narrative + beat structure
- [demo/outline-visual.md](../outline-visual.md) — visual DNA + motif + climax library
- [demo/asset-production.md](../asset-production.md) — asset routes
- [demo/script.md](../script.md) — 口播 source of truth

## Dev

```bash
cd demo/presentation
npm install
npm run dev
```

Open <http://localhost:5173/>. Currently shows the **Sandbox** page (Phase 0). Chapter pages arrive in Phase 1+.

## Test

```bash
npm run test:run
```

## URL params

- `?ch=N&step=M&beat=X` — jump to specific position
- `?presenter=1` — toggle Speaker Mode (cue + wait overlay)

## Controls

- Left-click / SPACE / → : advance one beat
- Right-click / ← : retreat one beat
- Esc : toggle progress bar

## Phase 0 scope (complete)

- Vite + React + Tailwind v4 + Motion stack
- Design tokens (colors / typography / spacing / zindex / chapters)
- Beat state machine (88 beats from outline.md, advance / retreat / URL sync)
- Global visual layers (grain / halftone-drift / chapter-tint / ambient-shapes / fade-bridge)
- Shared components (progress / chapter-nav / beat-indicator / presenter-panel / sticker / hero / asset-placeholder)
- Motif Library: 8 full + 5 shells = 13 total
- Climax FX (A/B/C/E/G) via useClimax hook
- /sandbox verification page

## Phase 1+ scope (next)

Per-chapter steps will be added under `src/chapters/ch<N>-<name>/`. See [Phase 0 plan](../../docs/superpowers/plans/2026-05-17-html-presentation-phase-0.md) for the foundation, and subsequent plans per chapter.
```

- [ ] **Step 2: Run full test suite**

```bash
npm run test:run
```

Expected: All tests PASS (usePresentation 10 + useUrlSync 6 + useClimax 3 = 19 tests).

- [ ] **Step 3: Run dev server + complete Phase 0 visual checklist**

```bash
npm run dev
```

Open `http://localhost:5173/` and verify each item:

- [ ] cream `#FFFDF5` background with subtle multi-layer texture (noise + halftone)
- [ ] halftone dots drift slowly (60s loop)
- [ ] 5 ambient shapes float gently in corners (ch1 default)
- [ ] Chapter 1-9 buttons change tint color smoothly
- [ ] Sticker primitives show 4-6px black border + 8-16px hard shadow + rotation
- [ ] BoomDoubleRing animates in with overshoot
- [ ] CrashLine shows red border + caret blink, fills with text on toggle
- [ ] RedStamp drops from above with bounce
- [ ] YellowHighlight mask-reveals from left
- [ ] 輕量 A+C button: screen shakes + visual elements scale-bounce
- [ ] ★★★ 全套 button: spotlight darkens edges + halftone burst + ink splatter dots + screen shake + scale overshoot
- [ ] Hero text "訓 練 AI 解 數 獨" renders with text-stroke (hollow letters)
- [ ] Open <http://localhost:5173/?presenter=1> — Speaker Mode overlay appears
- [ ] Hover bottom 32px → progress bar + beat indicator (88 squares) appear
- [ ] Hover top-right 32px → chapter nav appears
- [ ] Left-click anywhere → advances beat
- [ ] Right-click → retreats beat (no browser context menu)
- [ ] Reload URL with `?ch=6&step=6&beat=2` → state restores

- [ ] **Step 4: Commit checkpoint marker**

```bash
git add README.md
git commit -m "chore(demo): Phase 0 complete — foundation ready for ch1"
git tag phase-0-complete
```

- [ ] **Step 5: Report to user**

> Phase 0 complete. `/sandbox` should now demonstrate Neo-brutalism style + full Climax FX + Motif library. Test suite: 19 tests passing. Ready for human checkpoint review — please open the dev server and walk through the verification checklist above. Once approved, we'll start Phase 1 (ch1 coldopen).

---

## Self-Review

**Spec coverage** — checked against [build-flow spec §3.1 (Phase 0 範圍)](../specs/2026-05-17-html-presentation-build-flow-design.md):
- ✅ 專案 init → Tasks 1-4
- ✅ Design tokens → Tasks 5-6
- ✅ Global state → Tasks 7-11
- ✅ URL routing → Task 9 (helpers) + Task 11 (provider integration)
- ✅ Shared 元件 (ProgressBar / ChapterNav / BeatIndicator / PresenterPanel / AmbientShapes) → Tasks 15, 17-20
- ✅ 全域 layer (GlobalGrain / HalftoneBg / ChapterTint / FadeBridge) → Tasks 12-14, 16
- ✅ Motif Library 13 個 → Tasks 24-32 (8 full + 5 shells)
- ✅ Climax FX Library 5 個 → Task 33 (orchestrator) + motifs that double as FX (Tasks 28-31)
- ✅ Sandbox page → Task 34
- ✅ Phase 0 Checkpoint → Task 35

**Placeholder scan**: No "TBD" / "implement later" / "add validation" / "similar to Task N" patterns. Each step contains executable content. ✓

**Type consistency**: `usePresentation()` returns `chapterId/stepId/beatIndex/beat/step/chapter/advance/retreat/jumpTo/totalBeats/globalBeatIdx` — same shape consumed by Context provider (Task 11), ProgressBar (Task 17), ChapterNav (Task 18), BeatIndicator (Task 19), PresenterPanel (Task 20). ✓

`useClimax(variants)` returns `{ activeFX, play, reset }` — same shape consumed by Sandbox (Task 34). ✓

Motif components all accept `active` prop (BoomDoubleRing, CrashLine, RedStamp, YellowHighlight, SpotlightVignette, HalftoneBurst, InkSplatter) — consistent. ScreenShake uses imperative `ref.play()` because it needs to capture random keyframes per-trigger. ✓

`<AssetPlaceholder type todo width height>` props consistent across all 5 shells. ✓

No spec gaps found. Plan complete.

---

## Execution Handoff

Plan complete and saved to [`docs/superpowers/plans/2026-05-17-html-presentation-phase-0.md`](2026-05-17-html-presentation-phase-0.md). Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best when total task count is high (this plan = 35 tasks) and tasks are independent enough to delegate.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for human review.

Which approach?
