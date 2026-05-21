# ch3 step1 — Scanline + Inhale 背景動畫 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 ch3 step1 的背景加兩層動畫（一條紫色斜向掃描帶 + 偶發的詞被吸入 LLM hero），讓「LLM 讀資料」的敘事更鮮明。

**Architecture:** 兩個獨立疊加層（CSS-only scanline + motion 粒子 inhale），不動現有 grid。把 inhale 的時序/座標邏輯抽成可單測的 hook + 純函式，UI 元件本身保持薄。

**Tech Stack:** React 19, `motion` v12 (framer-motion successor), vitest + @testing-library/react，CSS `@keyframes` 寫在 `demo/presentation/src/index.css`（沿用既有專案慣例）。

**Spec:** [docs/superpowers/specs/2026-05-21-ch3-s1-scanline-inhale-design.md](../specs/2026-05-21-ch3-s1-scanline-inhale-design.md)

---

## File Structure

新建：
- `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.jsx` — 純 CSS 動畫元件（薄，~30 行）
- `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx` — 結構性測試
- `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx` — 粒子層元件 + `pickStart` helper + `useInhaleSpawn` hook（co-located as named exports for unit testing）
- `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx` — `pickStart` / `useInhaleSpawn` 行為測試 + 元件結構測試

修改：
- `demo/presentation/src/index.css` — 加 `@keyframes ch3s1-scanline`
- `demo/presentation/src/chapters/ch3-llm-vs-rl/Ch3Step1.jsx` — 在既有 grid 容器內 mount 兩個新元件，把 `TERMS` 傳給 `InhaleLayer`

**為何 `InhaleLayer` 三件事都放同一檔**：feature 小、互相只在這個元件用、測試直接 import 即可。一個檔 < 100 行，不會難讀。如果未來變大再拆。

---

## Task 1: ScanlineOverlay — keyframes + 元件 + 測試

**Files:**
- Create: `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.jsx`
- Create: `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx`
- Modify: `demo/presentation/src/index.css` (append `@keyframes ch3s1-scanline`)

- [ ] **Step 1.1: 加 keyframes 到 index.css**

打開 `demo/presentation/src/index.css`，找到既有 `@keyframes stagger-list-rise` block 之後（約 line 63），新增：

```css
@keyframes ch3s1-scanline {
  0%   { transform: rotate(-20deg) translateX(-100%); }
  100% { transform: rotate(-20deg) translateX(100%); }
}
```

**注意**：keyframe 0% 和 100% 都必須完整寫 `rotate(-20deg)`，不能省 — 否則旋轉會被 `translateX` 覆寫，掃描帶會變水平。

- [ ] **Step 1.2: 寫 ScanlineOverlay 的 failing test**

建立 `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx`：

```jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import ScanlineOverlay from './ScanlineOverlay.jsx';

describe('ScanlineOverlay', () => {
  it('renders a non-interactive overlay container with zero z-index', () => {
    const { container } = render(<ScanlineOverlay />);
    const outer = container.firstChild;
    expect(outer.getAttribute('aria-hidden')).toBe('true');
    expect(outer).toHaveStyle({
      position: 'absolute',
      pointerEvents: 'none',
      overflow: 'hidden',
      zIndex: '0',
    });
  });

  it('renders an inner bar with the scanline animation and purple gradient', () => {
    const { container } = render(<ScanlineOverlay />);
    const bar = container.firstChild.firstChild;
    const style = bar.getAttribute('style') || '';
    expect(style).toContain('animation');
    expect(style).toContain('ch3s1-scanline');
    expect(style).toContain('196'); // R of #C4B5FD = 196
  });
});
```

- [ ] **Step 1.3: 跑測試確認失敗**

```bash
cd demo/presentation
npx vitest run src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx
```

Expected: FAIL with "Cannot find module './ScanlineOverlay.jsx'"。

- [ ] **Step 1.4: 寫 ScanlineOverlay 最小實作**

建立 `demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.jsx`：

```jsx
export default function ScanlineOverlay() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute', inset: 0, overflow: 'hidden',
        pointerEvents: 'none', zIndex: 0,
      }}
    >
      <div
        style={{
          position: 'absolute', top: '-50%', left: 0,
          width: '200%', height: '200%',
          background: 'linear-gradient(90deg, rgba(196,181,253,0) 0%, rgba(196,181,253,0) 45%, rgba(196,181,253,0.18) 50%, rgba(196,181,253,0) 55%, rgba(196,181,253,0) 100%)',
          animation: 'ch3s1-scanline 7s linear 1.8s infinite',
          transform: 'rotate(-20deg)',
        }}
      />
    </div>
  );
}
```

- [ ] **Step 1.5: 跑測試確認通過**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx
```

Expected: PASS（兩個 it 都過）。

- [ ] **Step 1.6: Commit**

```bash
git add demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.jsx \
        demo/presentation/src/chapters/ch3-llm-vs-rl/ScanlineOverlay.test.jsx \
        demo/presentation/src/index.css
git commit -m "feat(ch3-s1): add ScanlineOverlay component with diagonal CSS sweep"
```

---

## Task 2: pickStart — 純函式 rejection sampling

**Files:**
- Create: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx` (only `pickStart` named export at this point)
- Create: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx`

- [ ] **Step 2.1: 寫 pickStart 的 failing test**

建立 `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx`：

```jsx
import { describe, it, expect } from 'vitest';
import { pickStart } from './InhaleLayer.jsx';

describe('pickStart', () => {
  it('returns a coordinate within the viewport bounds', () => {
    const { startX, startY } = pickStart(1920, 1080);
    expect(startX).toBeGreaterThanOrEqual(0);
    expect(startX).toBeLessThanOrEqual(1920);
    expect(startY).toBeGreaterThanOrEqual(0);
    expect(startY).toBeLessThanOrEqual(1080);
  });

  it('avoids the central 320x240 forbidden box across 200 samples', () => {
    const w = 1920, h = 1080;
    const fx0 = w / 2 - 160, fx1 = w / 2 + 160;
    const fy0 = h / 2 - 120, fy1 = h / 2 + 120;
    let insideCount = 0;
    for (let i = 0; i < 200; i++) {
      const { startX, startY } = pickStart(w, h);
      const inX = startX >= fx0 && startX <= fx1;
      const inY = startY >= fy0 && startY <= fy1;
      if (inX && inY) insideCount++;
    }
    // 5 retries + final fallback means worst case ~ (forbidden_area / total_area)^6 chance of falling inside.
    // For 320x240 / (1920x1080) ≈ 0.037, probability after 6 tries ≈ 2.6e-9 — virtually never.
    // Allow up to 1 outlier across 200 samples for safety.
    expect(insideCount).toBeLessThanOrEqual(1);
  });
});
```

- [ ] **Step 2.2: 跑測試確認失敗**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: FAIL with "Cannot find module './InhaleLayer.jsx'" 或 "pickStart is not a function"。

- [ ] **Step 2.3: 寫 pickStart 實作**

建立 `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx`：

```jsx
// 中央禁區大小（避免起點剛好在 LLM hero 上）
const FORBIDDEN_HALF_W = 160;
const FORBIDDEN_HALF_H = 120;

export function pickStart(viewportW, viewportH) {
  const fx0 = viewportW / 2 - FORBIDDEN_HALF_W;
  const fx1 = viewportW / 2 + FORBIDDEN_HALF_W;
  const fy0 = viewportH / 2 - FORBIDDEN_HALF_H;
  const fy1 = viewportH / 2 + FORBIDDEN_HALF_H;
  let startX = 0, startY = 0;
  for (let i = 0; i < 6; i++) {
    startX = Math.random() * viewportW;
    startY = Math.random() * viewportH;
    const inX = startX >= fx0 && startX <= fx1;
    const inY = startY >= fy0 && startY <= fy1;
    if (!(inX && inY)) return { startX, startY };
  }
  return { startX, startY }; // 5 次都中禁區（機率 ~10^-9）就放行
}
```

- [ ] **Step 2.4: 跑測試確認通過**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: PASS。

- [ ] **Step 2.5: Commit**

```bash
git add demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx \
        demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
git commit -m "feat(ch3-s1): add pickStart helper with rejection-sampling for inhale spawn"
```

---

## Task 3: useInhaleSpawn hook — 時序 + state 生命週期

**Files:**
- Modify: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx` (add `useInhaleSpawn` export)
- Modify: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx` (add hook tests)

- [ ] **Step 3.1: 加 useInhaleSpawn 的 failing tests**

在 `InhaleLayer.test.jsx` 末尾加（新 `describe` block）：

```jsx
import { renderHook, act } from '@testing-library/react';
import { vi } from 'vitest';
import { useInhaleSpawn } from './InhaleLayer.jsx';

describe('useInhaleSpawn', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    // 固定 viewport 尺寸給 hook 用
    Object.defineProperty(window, 'innerWidth', { writable: true, value: 1920 });
    Object.defineProperty(window, 'innerHeight', { writable: true, value: 1080 });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts with empty particles', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI', 'LLM']));
    expect(result.current.particles).toEqual([]);
  });

  it('spawns first particle after 3000ms', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI', 'LLM']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    expect(['AI', 'LLM']).toContain(result.current.particles[0].text);
    expect(result.current.particles[0].endX).toBe(960);
    expect(result.current.particles[0].endY).toBe(540);
  });

  it('spawns subsequent particles every ~6000ms (allow 4500-7500ms window)', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    act(() => { vi.advanceTimersByTime(7500); }); // worst-case next window
    expect(result.current.particles.length).toBe(2);
  });

  it('removeParticle drops the matching id', () => {
    const { result } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    const id = result.current.particles[0].id;
    act(() => { result.current.removeParticle(id); });
    expect(result.current.particles).toEqual([]);
  });

  it('cleans up timer on unmount', () => {
    const { result, unmount } = renderHook(() => useInhaleSpawn(['AI']));
    act(() => { vi.advanceTimersByTime(3000); });
    expect(result.current.particles.length).toBe(1);
    unmount();
    act(() => { vi.advanceTimersByTime(10000); });
    // 不會再 spawn，也不會崩
    expect(result.current.particles.length).toBe(1); // unmount 後 ref 凍結
  });
});
```

**注意**：最後一個測試的斷言其實是「unmount 之後不會崩潰」，因為 `result.current` 在 unmount 後不會再更新。重點在 `vi.advanceTimersByTime` 不會丟錯。

- [ ] **Step 3.2: 跑測試確認失敗**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: FAIL — `useInhaleSpawn` 還沒寫。

- [ ] **Step 3.3: 寫 useInhaleSpawn 實作**

在 `InhaleLayer.jsx` 末尾加（在 `pickStart` 之後）：

```jsx
import { useEffect, useRef, useState } from 'react';

// Inhale 排程參數
const FIRST_DELAY_MS = 3000;
const INTERVAL_BASE_MS = 6000;
const INTERVAL_JITTER_MS = 1500;

export function useInhaleSpawn(terms) {
  const [particles, setParticles] = useState([]);
  const counterRef = useRef(0);

  useEffect(() => {
    let alive = true;
    let timeoutId;

    const spawn = () => {
      if (!alive) return;
      const id = counterRef.current++;
      const { startX, startY } = pickStart(window.innerWidth, window.innerHeight);
      const endX = window.innerWidth / 2;
      const endY = window.innerHeight / 2;
      const text = terms[(Math.random() * terms.length) | 0];
      setParticles(p => [...p, { id, text, startX, startY, endX, endY }]);
      const nextDelay = INTERVAL_BASE_MS + (Math.random() * 2 - 1) * INTERVAL_JITTER_MS;
      timeoutId = setTimeout(spawn, nextDelay);
    };

    timeoutId = setTimeout(spawn, FIRST_DELAY_MS);
    return () => { alive = false; clearTimeout(timeoutId); };
  }, [terms]);

  const removeParticle = (id) => {
    setParticles(p => p.filter(q => q.id !== id));
  };

  return { particles, removeParticle };
}
```

- [ ] **Step 3.4: 跑測試確認通過**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: PASS。

- [ ] **Step 3.5: Commit**

```bash
git add demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx \
        demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
git commit -m "feat(ch3-s1): add useInhaleSpawn hook for particle lifecycle"
```

---

## Task 4: InhaleLayer component — 把 hook 接上 motion 渲染

**Files:**
- Modify: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx` (add default export — the component)
- Modify: `demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx` (add structural tests)

- [ ] **Step 4.1: 加 InhaleLayer 結構性 failing test**

在 `InhaleLayer.test.jsx` 末尾加（新 `describe`）：

```jsx
import InhaleLayer from './InhaleLayer.jsx';

describe('InhaleLayer (component)', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    Object.defineProperty(window, 'innerWidth', { writable: true, value: 1920 });
    Object.defineProperty(window, 'innerHeight', { writable: true, value: 1080 });
  });
  afterEach(() => { vi.useRealTimers(); });

  it('renders a non-interactive container with zero z-index and no particles initially', () => {
    const { container } = render(<InhaleLayer terms={['AI']} />);
    const outer = container.firstChild;
    expect(outer.getAttribute('aria-hidden')).toBe('true');
    expect(outer).toHaveStyle({
      position: 'absolute',
      pointerEvents: 'none',
      zIndex: '0',
    });
    expect(outer.children.length).toBe(0);
  });

  it('renders one particle div after the first spawn delay', () => {
    const { container } = render(<InhaleLayer terms={['AI']} />);
    act(() => { vi.advanceTimersByTime(3000); });
    const outer = container.firstChild;
    expect(outer.children.length).toBe(1);
    expect(outer.firstChild.textContent).toBe('AI');
  });
});
```

- [ ] **Step 4.2: 跑測試確認失敗**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: FAIL — `InhaleLayer` 還沒 default export。

- [ ] **Step 4.3: 寫 InhaleLayer 元件**

在 `InhaleLayer.jsx` 檔頂部 import 區加：

```jsx
import { motion } from 'motion/react';
```

並在檔末尾加（注意：保留前面所有 `pickStart`、`useInhaleSpawn`、constants）：

```jsx
export default function InhaleLayer({ terms }) {
  const { particles, removeParticle } = useInhaleSpawn(terms);

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute', inset: 0,
        pointerEvents: 'none', zIndex: 0,
      }}
    >
      {particles.map(p => (
        <motion.div
          key={p.id}
          initial={{ x: p.startX, y: p.startY, scale: 1, opacity: 0.7 }}
          animate={{ x: p.endX, y: p.endY, scale: 0.2, opacity: 0 }}
          transition={{ duration: 1.2, ease: [0.4, 0, 1, 1] }}
          onAnimationComplete={() => removeParticle(p.id)}
          style={{
            position: 'absolute', top: 0, left: 0,
            fontFamily: 'monospace', fontWeight: 700, fontSize: 14,
            color: '#C4B5FD', whiteSpace: 'nowrap',
          }}
        >
          {p.text}
        </motion.div>
      ))}
    </div>
  );
}
```

- [ ] **Step 4.4: 跑測試確認通過（含先前所有測試）**

```bash
npx vitest run src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
```

Expected: 全部 PASS（pickStart 2 個 + useInhaleSpawn 5 個 + InhaleLayer component 2 個 = 9 個）。

- [ ] **Step 4.5: Commit**

```bash
git add demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.jsx \
        demo/presentation/src/chapters/ch3-llm-vs-rl/InhaleLayer.test.jsx
git commit -m "feat(ch3-s1): add InhaleLayer component rendering motion particles"
```

---

## Task 5: 把兩個新元件接進 Ch3Step1

**Files:**
- Modify: `demo/presentation/src/chapters/ch3-llm-vs-rl/Ch3Step1.jsx`

- [ ] **Step 5.1: 修改 Ch3Step1 import 與 mount 兩個新元件**

打開 `demo/presentation/src/chapters/ch3-llm-vs-rl/Ch3Step1.jsx`，做兩處修改：

**(a) 在檔頂 import 區加：**

```jsx
import ScanlineOverlay from './ScanlineOverlay.jsx';
import InhaleLayer from './InhaleLayer.jsx';
```

**(b) 在既有 grid `<div aria-hidden="true">` 的閉合 `</div>` 之後、`{/* "LLM" hero with overshoot stamp */}` 之前插入兩個元件：**

找到這段（約 line 33 附近）：

```jsx
          {lines.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>

        {/* "LLM" hero with overshoot stamp */}
```

改成：

```jsx
          {lines.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </div>

        <ScanlineOverlay />
        <InhaleLayer terms={TERMS} />

        {/* "LLM" hero with overshoot stamp */}
```

注意：`TERMS` 已是 `Ch3Step1.jsx` 內 module-level 的 const（不需新建），直接傳給 `InhaleLayer` 即可。

- [ ] **Step 5.2: 手動驗證 — dev server 起來看畫面**

```bash
cd demo/presentation && npm run dev
```

接著用瀏覽器（或下面 Step 5.3 的 Playwright 流程）開 `http://localhost:5173/?ch=3&step=1&beat=0`。

人工檢查清單：
1. 進入 step1 後，1.8 秒前畫面看起來跟之前一樣（hero、sticker、tagline、grid 進場動畫不變）。
2. 大約 1.8 秒後，可看到一條紫色斜向漸層帶從畫面一側緩慢滑到另一側，每 7 秒一輪、無限循環。
3. 大約 3 秒後，開始有紫色的詞從 grid 邊緣飛向畫面中心、邊飛邊縮小淡出。
4. 詞之間的出現間隔約 6 秒 ± 1.5 秒，肉眼看起來不規律但不稀疏。
5. 按方向鍵右切到 step2 後，背景的兩個動畫都停止（Step1 卸載）。

- [ ] **Step 5.3: Playwright 程式化驗證（quick smoke）**

dev server 應該已經在 5173。在 Claude Code 內：

1. 用 `mcp__plugin_playwright_playwright__browser_navigate` 打開 `http://localhost:5173/?ch=3&step=1&beat=0`
2. 用 `mcp__plugin_playwright_playwright__browser_evaluate` 跑：

```js
async () => {
  // 等 4 秒，看 InhaleLayer 內 children 是否曾經 > 0
  await new Promise(r => setTimeout(r, 4000));
  // 找 InhaleLayer 容器（aria-hidden 且 zIndex 0 的 div，子元素是紫色詞）
  const candidates = Array.from(document.querySelectorAll('[aria-hidden="true"]'));
  const inhale = candidates.find(el =>
    el.style && el.style.zIndex === '0' && Array.from(el.children).some(c => (c.style.color || '').includes('196'))
  );
  // 找 Scanline 容器（aria-hidden 且第一個 child 的 style 含 ch3s1-scanline）
  const scan = candidates.find(el =>
    el.firstChild && (el.firstChild.style || {}).animation && el.firstChild.style.animation.includes('ch3s1-scanline')
  );
  return {
    scanlineMounted: !!scan,
    scanlineHasAnimation: scan && scan.firstChild.style.animation.includes('7s'),
    inhaleCurrentCount: inhale ? inhale.children.length : 'no inhale layer',
  };
}
```

預期回傳：`scanlineMounted: true`、`scanlineHasAnimation: true`、`inhaleCurrentCount` 為 0、1 或 2（4 秒內已有第一發 inhale 出現、可能已飛完或還在飛）。

如果 `scanlineMounted: false` → 重看 Step 5.1 是否漏了 `<ScanlineOverlay />`。
如果 `inhaleCurrentCount: 'no inhale layer'` → 重看 `<InhaleLayer />` 是否有掛上。

- [ ] **Step 5.4: 視覺截圖留底（供 commit message 與 PR 對照）**

用 `mcp__plugin_playwright_playwright__browser_take_screenshot`，filename `ch3-s1-scanline-inhale-verify.png`，存到 repo 根。Step 5.5 不會 commit 這張圖。

- [ ] **Step 5.5: Commit**

```bash
git add demo/presentation/src/chapters/ch3-llm-vs-rl/Ch3Step1.jsx
git commit -m "feat(ch3-s1): mount ScanlineOverlay + InhaleLayer in Step1"
```

---

## Self-Review Notes

- **Spec coverage**：
  - Scanline (顏色 #C4B5FD、7s 週期、1.8s delay、-20° rotate) → Task 1 ✓
  - Inhale (起點避開中央禁區、終點 viewport center、紫色 0.7 alpha、1.2s 動畫 ease-in、6s ± 1.5s 間隔、3s 第一發、`onAnimationComplete` 清理) → Tasks 2-4 ✓
  - 編舞時序 (Step1 既有元素不動，新元件 1.8s/3.0s 啟動) → Task 1 keyframe delay + Task 3 hook constants ✓
  - 兩個新元件就近放 `ch3-llm-vs-rl/` 同層 → Task 1, 2 ✓
  - 不修改既有 grid → Task 5 確認只插入新行 ✓
  - YAGNI 項（不追蹤 hero 位置、不監聽 resize、不做粒子互相避讓）→ 沒實作即達標 ✓

- **無 placeholder**：每個程式碼步驟都有完整可貼上去執行的 code。

- **型別/命名一致性**：
  - `pickStart` 簽名：`(viewportW, viewportH) → { startX, startY }` 用於 Task 2 測試與 Task 3 hook ✓
  - particle 物件結構：`{ id, text, startX, startY, endX, endY }` 一致 ✓
  - `useInhaleSpawn` 回傳 `{ particles, removeParticle }` 用於 Task 3 hook tests 與 Task 4 元件 ✓

- **風險點再提醒**：
  - keyframe 內 `transform` 一定要重寫 `rotate(-20deg)`（Task 1 Step 1.1 已標）
  - motion 的 `x`/`y` 必須是純數字像素，不能用 `'25vw'`（Task 4 Step 4.3 的 props 都用數字 ✓）
