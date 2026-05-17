# Phase 0.5 · Presentation Layout System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the layout primitive system specified in [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) and retrofit ch1 / ch2 to use it. Adds a `<Stage>` scaler (1920×1080 fixed canvas → CSS scale to any viewport), `<SafeArea>` content frame (85% of canvas), `<HubSatellite>` declarative layout primitive (hub + 1–8 named-anchor satellites), `<Sticker variant>` table (hub / sat-lg / sat-md / sat-sm / kicker), and repositions `<AmbientShapes>` so decorations only render in the outer 15% ring.

**Architecture:** Stage is a single root scaler that owns the 1920×1080 design canvas and exposes a CSS `transform: scale(N)` driven by a ResizeObserver. SafeArea is a pure layout box (108×144px padding). HubSatellite is a render-prop-free compound component (`HubSatellite.Hub`, `HubSatellite.Satellite`) that absolutely positions named anchors around a flex-centered hub. Sticker centralises the brutalism look so step files never write inline `position: 'absolute'` or hand-tuned padding again. Retrofit of ch1 s1–s8 + ch2 s1–s5 (13 steps total) proves the primitives. ch3–9 plan docs get a one-paragraph prelude requiring future implementers to compose via the primitives.

**Tech Stack:** React 19 · Vitest + @testing-library/react · Tailwind v4 (existing tokens) · Motion 11+ · existing `tokens/spacing.js` + `tokens/chapters.js`.

**Source spec:** [`2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md)

---

## File Structure

```
demo/presentation/src/
├── tokens/
│   ├── spacing.js              # MODIFY: add 32/40/48 large-scale entries
│   └── stage.js                # CREATE: canvas + safe area + cluster tokens
├── components/
│   ├── Stage.jsx               # CREATE: 1920×1080 canvas + ResizeObserver scale
│   ├── Stage.test.jsx          # CREATE
│   ├── SafeArea.jsx            # CREATE: inner 85% padding frame
│   ├── SafeArea.test.jsx       # CREATE
│   ├── HubSatellite.jsx        # CREATE: compound component (Hub + Satellite)
│   ├── HubSatellite.test.jsx   # CREATE
│   ├── Sticker.jsx             # MODIFY: add variant system (hub / sat-lg / sat-md / sat-sm / kicker)
│   └── Sticker.test.jsx        # CREATE (no existing test)
├── layers/
│   └── AmbientShapes.jsx       # MODIFY: anchors snap to outer 15% ring only
├── App.jsx                     # MODIFY: wrap <ChapterRouter> in <Stage><SafeArea>
└── chapters/
    ├── ch1-coldopen/Ch1Step{1..8}.jsx   # MODIFY: compose via primitives, drop inline absolutes
    └── ch2-ml-map/Ch2Step{1..5}.jsx     # MODIFY: same

docs/superpowers/plans/
└── 2026-05-17-html-presentation-phase-{3..9}-ch*.md   # MODIFY: add 1-paragraph prelude
```

---

## Task 1: Stage tokens + Stage primitive

**Files:**
- Create: `demo/presentation/src/tokens/stage.js`
- Modify: `demo/presentation/src/tokens/spacing.js`
- Create: `demo/presentation/src/components/Stage.jsx`
- Create: `demo/presentation/src/components/Stage.test.jsx`

- [ ] **Step 1: Extend `tokens/spacing.js`** — add the three large-scale entries from the spec

Replace the file contents with:

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
  32: 128,   // hub-satellite gap (large) / inter-cluster padding
  40: 160,   // section padding (large)
  48: 192,   // hero-to-cluster vertical gap when both present
};
```

- [ ] **Step 2: Create `tokens/stage.js`**

```js
// Stage / SafeArea / Cluster tokens — mirror of
// docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md §Tokens
export const stage = {
  width: 1920,
  height: 1080,
  aspectRatio: 16 / 9,
  safePadding: { x: 144, y: 108 },   // 7.5% each side → safe area 1632 × 918
  cluster: {
    // Cluster auto-fits the hub child; these are upper bounds, not target sizes.
    // Step author is responsible for sizing the hub so the cluster (hub + satellite
    // extents) fits inside SafeArea.
    maxWidth: 1632,                  // safe area inner width — hub cap
    maxHeight: 918,                  // safe area inner height — hub cap
    hubToSatelliteGap: 48,           // <HubSatellite gap={48}> default
  },
  ambient: {
    outerBandPct: 15,                // outer 15% reserved for AmbientShapes
  },
};

// Pure function — extracted for unit testing.
// Returns the uniform scale factor that fits 1920×1080 inside the viewport
// while preserving aspect ratio (letterbox on mismatched ratios).
export function computeStageScale(viewportWidth, viewportHeight) {
  return Math.min(viewportWidth / stage.width, viewportHeight / stage.height);
}
```

- [ ] **Step 3: Write failing test `components/Stage.test.jsx`**

```jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { computeStageScale, stage } from '../tokens/stage.js';
import { Stage } from './Stage.jsx';

describe('computeStageScale', () => {
  it('returns 1.0 at native 1080p', () => {
    expect(computeStageScale(1920, 1080)).toBe(1);
  });

  it('returns ~1.333 at 2K (2560×1440)', () => {
    expect(computeStageScale(2560, 1440)).toBeCloseTo(1.333, 2);
  });

  it('returns 2.0 at 4K (3840×2160)', () => {
    expect(computeStageScale(3840, 2160)).toBe(2);
  });

  it('letterboxes on 4:3 by picking the smaller dimension', () => {
    // 1600×1200 (4:3): width-fit = 0.833, height-fit = 1.111 → pick 0.833
    expect(computeStageScale(1600, 1200)).toBeCloseTo(0.833, 2);
  });
});

describe('<Stage>', () => {
  it('renders children inside a 1920×1080 inner canvas', () => {
    const { container } = render(<Stage><div data-testid="child" /></Stage>);
    const canvas = container.querySelector('[data-stage-canvas]');
    expect(canvas).not.toBeNull();
    expect(canvas.style.width).toBe(`${stage.width}px`);
    expect(canvas.style.height).toBe(`${stage.height}px`);
    expect(canvas.querySelector('[data-testid="child"]')).not.toBeNull();
  });
});
```

- [ ] **Step 4: Run test, verify it fails**

```bash
cd demo/presentation && npx vitest run src/components/Stage.test.jsx
```

Expected: FAIL with `Cannot find module './Stage.jsx'`.

- [ ] **Step 5: Implement `components/Stage.jsx`**

```jsx
import { useEffect, useRef, useState } from 'react';
import { stage, computeStageScale } from '../tokens/stage.js';

export function Stage({ children }) {
  const [scale, setScale] = useState(() =>
    typeof window === 'undefined'
      ? 1
      : computeStageScale(window.innerWidth, window.innerHeight)
  );
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handle = () => setScale(computeStageScale(window.innerWidth, window.innerHeight));
    handle();
    window.addEventListener('resize', handle);
    return () => window.removeEventListener('resize', handle);
  }, []);

  return (
    <div
      ref={wrapperRef}
      style={{
        position: 'fixed', inset: 0,
        overflow: 'hidden',
        background: '#FFFDF5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}
    >
      <div
        data-stage-canvas
        style={{
          width: stage.width,
          height: stage.height,
          transform: `scale(${scale})`,
          transformOrigin: 'center center',
          position: 'relative',
          flex: 'none',
        }}
      >
        {children}
      </div>
    </div>
  );
}
```

- [ ] **Step 6: Run tests, verify they pass**

```bash
npx vitest run src/components/Stage.test.jsx
```

Expected: 5 passed.

- [ ] **Step 7: Commit**

```bash
git add demo/presentation/src/tokens/stage.js demo/presentation/src/tokens/spacing.js \
        demo/presentation/src/components/Stage.jsx demo/presentation/src/components/Stage.test.jsx
git commit -m "feat(demo): Stage primitive + stage/spacing tokens (Phase 0.5)"
```

---

## Task 2: SafeArea primitive

**Files:**
- Create: `demo/presentation/src/components/SafeArea.jsx`
- Create: `demo/presentation/src/components/SafeArea.test.jsx`

- [ ] **Step 1: Write failing test `components/SafeArea.test.jsx`**

```jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { stage } from '../tokens/stage.js';
import { SafeArea } from './SafeArea.jsx';

describe('<SafeArea>', () => {
  it('applies the safe padding from tokens', () => {
    const { container } = render(<SafeArea><div data-testid="x" /></SafeArea>);
    const root = container.firstChild;
    expect(root.style.padding).toBe(`${stage.safePadding.y}px ${stage.safePadding.x}px`);
  });

  it('fills the parent (absolute inset 0)', () => {
    const { container } = render(<SafeArea><div /></SafeArea>);
    const root = container.firstChild;
    expect(root.style.position).toBe('absolute');
    expect(root.style.inset).toBe('0px');
  });

  it('renders children', () => {
    const { getByTestId } = render(<SafeArea><div data-testid="x" /></SafeArea>);
    expect(getByTestId('x')).not.toBeNull();
  });
});
```

- [ ] **Step 2: Run test, verify fail**

```bash
npx vitest run src/components/SafeArea.test.jsx
```

Expected: FAIL with module not found.

- [ ] **Step 3: Implement `components/SafeArea.jsx`**

```jsx
import { stage } from '../tokens/stage.js';

export function SafeArea({ children, style = {} }) {
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        padding: `${stage.safePadding.y}px ${stage.safePadding.x}px`,
        boxSizing: 'border-box',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
npx vitest run src/components/SafeArea.test.jsx
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/components/SafeArea.jsx demo/presentation/src/components/SafeArea.test.jsx
git commit -m "feat(demo): SafeArea primitive (108×144 padding)"
```

---

## Task 3: HubSatellite primitive (compound component)

**Files:**
- Create: `demo/presentation/src/components/HubSatellite.jsx`
- Create: `demo/presentation/src/components/HubSatellite.test.jsx`

API contract:

```jsx
<HubSatellite gap={48}>
  <HubSatellite.Hub>{hubContent}</HubSatellite.Hub>
  <HubSatellite.Satellite position="tl">{satContent}</HubSatellite.Satellite>
  <HubSatellite.Satellite position="tr">...</HubSatellite.Satellite>
  ...
</HubSatellite>
```

- `position` accepts 8 anchors: `tl t tr l r bl b br`
- **Container auto-fits the hub child** (`display: inline-flex`, sized to hub's natural dimensions, capped at `stage.cluster.maxWidth/maxHeight`)
- Satellites are absolutely positioned **outside** the hub box, offset by `gap` from the hub edge — implemented via edge anchors (`bottom: 100%` etc.) plus margin
- Container is centered horizontally in its parent (`margin: '0 auto'`) — parent (SafeArea) provides the centring context
- Step author must size hub so cluster (hub + satellite extents) stays inside SafeArea

- [ ] **Step 1: Write failing test `components/HubSatellite.test.jsx`**

```jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { HubSatellite } from './HubSatellite.jsx';

describe('<HubSatellite>', () => {
  it('renders the hub child and each satellite at named anchors', () => {
    const { getByTestId } = render(
      <HubSatellite gap={48}>
        <HubSatellite.Hub><div data-testid="hub" style={{ width: 200, height: 100 }}>H</div></HubSatellite.Hub>
        <HubSatellite.Satellite position="tl"><div data-testid="tl">tl</div></HubSatellite.Satellite>
        <HubSatellite.Satellite position="br"><div data-testid="br">br</div></HubSatellite.Satellite>
      </HubSatellite>
    );

    expect(getByTestId('hub')).not.toBeNull();
    // satellite wrapper sits outside the hub box at the correct anchor
    const tl = getByTestId('tl').parentElement;
    expect(tl.style.position).toBe('absolute');
    expect(tl.style.bottom).toBe('100%');   // sits ABOVE the hub container
    expect(tl.style.right).toBe('100%');    // sits LEFT of the hub container
    expect(tl.style.marginBottom).toBe('48px');
    expect(tl.style.marginRight).toBe('48px');

    const br = getByTestId('br').parentElement;
    expect(br.style.top).toBe('100%');
    expect(br.style.left).toBe('100%');
    expect(br.style.marginTop).toBe('48px');
    expect(br.style.marginLeft).toBe('48px');
  });

  it('caps the cluster container at safe-area dimensions', () => {
    const { container } = render(
      <HubSatellite>
        <HubSatellite.Hub><div /></HubSatellite.Hub>
      </HubSatellite>
    );
    const root = container.firstChild;
    expect(root.style.maxWidth).toBe('1632px');
    expect(root.style.maxHeight).toBe('918px');
  });

  it('rejects unknown position values', () => {
    expect(() =>
      render(
        <HubSatellite>
          <HubSatellite.Hub><div /></HubSatellite.Hub>
          <HubSatellite.Satellite position="xx"><div /></HubSatellite.Satellite>
        </HubSatellite>
      )
    ).toThrow(/unknown position/i);
  });

  it('throws if no Hub child is provided', () => {
    expect(() =>
      render(
        <HubSatellite>
          <HubSatellite.Satellite position="tl"><div /></HubSatellite.Satellite>
        </HubSatellite>
      )
    ).toThrow(/requires a Hub/i);
  });
});
```

- [ ] **Step 2: Run, verify fail**

```bash
npx vitest run src/components/HubSatellite.test.jsx
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement `components/HubSatellite.jsx`**

```jsx
import { Children, isValidElement } from 'react';
import { stage } from '../tokens/stage.js';

// Each satellite wrapper anchors to a HUB EDGE and sits OUTSIDE the hub
// container, offset by `gap`. Uses `bottom: 100%` / `top: 100%` etc. so the
// satellite's edge meets the hub's edge with no overlap; margins push it
// further by `gap`.
function getAnchorStyle(position, gap) {
  switch (position) {
    case 'tl': return { bottom: '100%', right: '100%', marginBottom: gap, marginRight: gap };
    case 't':  return { bottom: '100%', left: '50%',   marginBottom: gap, transform: 'translateX(-50%)' };
    case 'tr': return { bottom: '100%', left: '100%',  marginBottom: gap, marginLeft: gap };
    case 'l':  return { top: '50%',     right: '100%', marginRight: gap,  transform: 'translateY(-50%)' };
    case 'r':  return { top: '50%',     left: '100%',  marginLeft: gap,   transform: 'translateY(-50%)' };
    case 'bl': return { top: '100%',    right: '100%', marginTop: gap,    marginRight: gap };
    case 'b':  return { top: '100%',    left: '50%',   marginTop: gap,    transform: 'translateX(-50%)' };
    case 'br': return { top: '100%',    left: '100%',  marginTop: gap,    marginLeft: gap };
    default:   return null;
  }
}

const KNOWN_POSITIONS = ['tl', 't', 'tr', 'l', 'r', 'bl', 'b', 'br'];

function Hub({ children }) {
  return children;
}
Hub.displayName = 'HubSatellite.Hub';

function Satellite({ children }) {
  return children;
}
Satellite.displayName = 'HubSatellite.Satellite';

export function HubSatellite({ children, gap = stage.cluster.hubToSatelliteGap, style = {} }) {
  let hub = null;
  const satellites = [];

  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    if (child.type === Hub) {
      hub = child;
    } else if (child.type === Satellite) {
      const pos = child.props.position;
      if (!KNOWN_POSITIONS.includes(pos)) {
        throw new Error(`HubSatellite: unknown position "${pos}". Allowed: ${KNOWN_POSITIONS.join(', ')}`);
      }
      satellites.push(child);
    }
  });

  if (!hub) {
    throw new Error('HubSatellite: requires a <HubSatellite.Hub> child');
  }

  return (
    <div
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        maxWidth: stage.cluster.maxWidth,
        maxHeight: stage.cluster.maxHeight,
        margin: '0 auto',
        ...style,
      }}
    >
      {hub.props.children}
      {satellites.map((sat, i) => {
        const anchor = getAnchorStyle(sat.props.position, gap);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              ...anchor,
              pointerEvents: 'auto',
            }}
          >
            {sat.props.children}
          </div>
        );
      })}
    </div>
  );
}

HubSatellite.Hub = Hub;
HubSatellite.Satellite = Satellite;
```

Design notes:
- `display: inline-flex` sizes the container to the hub child's natural box (the hub is the only direct flex child rendered without absolute positioning).
- Each satellite wrapper uses `position: absolute` and an anchor pair that pins the wrapper's appropriate edge to the hub container's opposite edge (`bottom: 100%` → satellite's bottom sits at container's top, putting satellite above).
- Margins inject the `gap` clearance.
- `margin: '0 auto'` on the container relies on the parent (SafeArea) being block-level to centre horizontally.

- [ ] **Step 4: Run tests, verify pass**

```bash
npx vitest run src/components/HubSatellite.test.jsx
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/components/HubSatellite.jsx demo/presentation/src/components/HubSatellite.test.jsx
git commit -m "feat(demo): HubSatellite primitive (8 named anchors + cluster box)"
```

---

## Task 4: Sticker variant system

**Files:**
- Modify: `demo/presentation/src/components/Sticker.jsx`
- Create: `demo/presentation/src/components/Sticker.test.jsx`

Adds a `variant` prop driving font-size / padding / border / shadow / min-width per the spec's variant table. Existing props (bg, textColor, rotation, etc.) preserved for backwards compatibility.

- [ ] **Step 1: Write failing test `components/Sticker.test.jsx`**

```jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Sticker, STICKER_VARIANTS } from './Sticker.jsx';

describe('<Sticker variant>', () => {
  it('exports a variant table with hub-md/hub-lg/hub-mega/sat-lg/sat-md/sat-sm/kicker keys', () => {
    expect(Object.keys(STICKER_VARIANTS).sort()).toEqual(
      ['hub-lg', 'hub-md', 'hub-mega', 'kicker', 'sat-lg', 'sat-md', 'sat-sm'].sort()
    );
  });

  it('hub-md / hub-lg / hub-mega use 4 / 6 / 8 rem font-size', () => {
    expect(STICKER_VARIANTS['hub-md'].fontSize).toBe('4rem');
    expect(STICKER_VARIANTS['hub-lg'].fontSize).toBe('6rem');
    expect(STICKER_VARIANTS['hub-mega'].fontSize).toBe('8rem');
  });

  it('sat-lg uses font-size 1.75rem and padding 20×32', () => {
    const v = STICKER_VARIANTS['sat-lg'];
    expect(v.fontSize).toBe('1.75rem');
    expect(v.padding).toBe('20px 32px');
  });

  it('renders sat-lg by default and applies variant styles', () => {
    const { container } = render(<Sticker>hello</Sticker>);
    const el = container.firstChild;
    expect(el.style.fontSize).toBe('1.75rem');
    expect(el.style.padding).toBe('20px 32px');
  });

  it('honors an explicit variant override', () => {
    const { container } = render(<Sticker variant="kicker">kicker</Sticker>);
    expect(container.firstChild.style.fontSize).toBe('1.25rem');
  });

  it('throws on unknown variant', () => {
    expect(() => render(<Sticker variant="bogus">x</Sticker>)).toThrow(/unknown variant/i);
  });

  it('still supports legacy bg/rotation props', () => {
    const { container } = render(
      <Sticker variant="sat-md" bg="secondary" rotation={-3}>x</Sticker>
    );
    const el = container.firstChild;
    expect(el.style.background).toBe('rgb(255, 217, 61)');   // #FFD93D
    expect(el.style.transform).toBe('rotate(-3deg)');
  });
});
```

- [ ] **Step 2: Run, verify fail**

```bash
npx vitest run src/components/Sticker.test.jsx
```

Expected: FAIL — `STICKER_VARIANTS` not exported.

- [ ] **Step 3: Replace `components/Sticker.jsx` contents**

```jsx
const COLOR_MAP = {
  accent:    '#FF6B6B',
  secondary: '#FFD93D',
  muted:     '#C4B5FD',
  cream:     '#FFFDF5',
  ink:       '#000000',
};

export const STICKER_VARIANTS = {
  'hub-md': {
    fontSize: '4rem',
    padding: '48px 64px',
    border: 6,
    shadow: 'massive',
    minWidth: undefined,
  },
  'hub-lg': {
    fontSize: '6rem',
    padding: '56px 72px',
    border: 6,
    shadow: 'massive',
    minWidth: undefined,
  },
  'hub-mega': {
    fontSize: '8rem',
    padding: '64px 96px',
    border: 8,
    shadow: 'burst',
    minWidth: undefined,
  },
  'sat-lg': {
    fontSize: '1.75rem',
    padding: '20px 32px',
    border: 4,
    shadow: 'lg',
    minWidth: 160,
  },
  'sat-md': {
    fontSize: '1.5rem',
    padding: '16px 24px',
    border: 4,
    shadow: 'md',
    minWidth: 140,
  },
  'sat-sm': {
    fontSize: '1.25rem',
    padding: '12px 20px',
    border: 3,
    shadow: 'md',
    minWidth: 80,
  },
  kicker: {
    fontSize: '1.25rem',
    padding: '12px 28px',
    border: 3,
    shadow: 'sm',
    minWidth: undefined,
  },
};

const SHADOW_MAP = {
  sm:      '4px 4px 0 0 #000',
  md:      '8px 8px 0 0 #000',
  lg:      '12px 12px 0 0 #000',
  massive: '16px 16px 0 0 #000',
  burst:   '20px 20px 0 0 #000',
};

export function Sticker({
  variant = 'sat-lg',
  bg = 'cream',
  textColor,
  rotation = 0,
  children,
  className = '',
  style = {},
  // legacy overrides — kept for incremental migration
  border, padding, shadow,
}) {
  const v = STICKER_VARIANTS[variant];
  if (!v) {
    throw new Error(`Sticker: unknown variant "${variant}". Allowed: ${Object.keys(STICKER_VARIANTS).join(', ')}`);
  }
  const effBorder = border ?? v.border;
  const effPadding = padding ?? v.padding;
  const effShadow = shadow ?? v.shadow;

  return (
    <div
      className={className}
      style={{
        display: 'inline-block',
        background: COLOR_MAP[bg] ?? bg,
        color: textColor ? (COLOR_MAP[textColor] ?? textColor) : '#000',
        border: `${effBorder}px solid #000`,
        boxShadow: SHADOW_MAP[effShadow] ?? effShadow,
        padding: effPadding,
        fontSize: v.fontSize,
        minWidth: v.minWidth,
        transform: `rotate(${rotation}deg)`,
        fontFamily: 'Space Grotesk',
        fontWeight: 900,
        lineHeight: 1.2,
        textAlign: 'center',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 4: Run tests, verify pass**

```bash
npx vitest run src/components/Sticker.test.jsx
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/components/Sticker.jsx demo/presentation/src/components/Sticker.test.jsx
git commit -m "feat(demo): Sticker variant system (hub/sat-lg/sat-md/sat-sm/kicker)"
```

---

## Task 5: Reposition AmbientShapes to outer 15% ring

**Files:**
- Modify: `demo/presentation/src/layers/AmbientShapes.jsx`

Goal: shapes render only outside the SafeArea inner box (the outer 15% ring). Existing anchor positions (`tl/tr/bl/br/ml/mr/mc`) keep their semantic meaning but get pushed further toward the edge so they never collide with content placed inside SafeArea.

Current values: `tl/tr` at 5% from top/side, `bl/br` at 8% bottom. Spec band is 15% — but the *visual centre* of a shape should sit roughly in the middle of that band (~7.5%). Move all corner anchors to fixed pixel offsets that anchor inside the outer band of the 1920×1080 canvas.

- [ ] **Step 1: Replace `POSITION_STYLE` in `layers/AmbientShapes.jsx`** to anchor inside the outer 15% ring of the 1920×1080 canvas (≤108 px from top/bottom; ≤144 px from left/right — same as SafeArea padding)

Replace the `POSITION_STYLE` block (lines 4–12) with:

```js
// Anchor coords pin shape centre into the outer 15% ambient band.
// Values are pixel offsets in the 1920×1080 design canvas.
const POSITION_STYLE = {
  tl: { top: 40,    left: 56  },
  tr: { top: 40,    right: 56 },
  bl: { bottom: 40, left: 56  },
  br: { bottom: 40, right: 56 },
  ml: { top: '50%', left: 24,  transform: 'translateY(-50%)' },
  mr: { top: '50%', right: 24, transform: 'translateY(-50%)' },
  mc: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },  // keep mc usable for special steps
};
```

- [ ] **Step 2: Also change the wrapper container so it scales with the Stage canvas, not the viewport**

Replace the wrapper `<div>` opening (around line 55) from:

```jsx
<div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
```

to:

```jsx
<div aria-hidden="true" style={{ position: 'absolute', inset: 0, zIndex: 0, pointerEvents: 'none' }}>
```

(`position: fixed` was tied to the viewport — but Stage owns a scaled canvas now, so `absolute inset:0` anchors the layer to the canvas instead.)

- [ ] **Step 3: Verify presentation still builds**

```bash
cd demo/presentation && npm run build
```

Expected: build succeeds, no errors. (No unit test for AmbientShapes; visual check happens in Task 13.)

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/layers/AmbientShapes.jsx
git commit -m "refactor(demo): AmbientShapes anchors snap to outer 15% ring inside Stage"
```

---

## Task 6: Wrap `App.jsx` in `<Stage>` + `<SafeArea>`

**Files:**
- Modify: `demo/presentation/src/App.jsx`

- [ ] **Step 1: Replace `Frame()` in `App.jsx`** to wrap `<ChapterRouter />` in `<Stage><SafeArea>`

```jsx
import { PresentationProvider, usePresentationContext } from './state/PresentationContext.jsx';
import { ChapterRouter } from './chapters/index.jsx';
import { ProgressBar } from './components/ProgressBar.jsx';
import { ChapterNav } from './components/ChapterNav.jsx';
import { BeatIndicator } from './components/BeatIndicator.jsx';
import { PresenterPanel } from './components/PresenterPanel.jsx';
import { Stage } from './components/Stage.jsx';
import { SafeArea } from './components/SafeArea.jsx';
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
      <Stage>
        <GlobalGrain />
        <HalftoneBg />
        <ChapterTint chapterId={chapterId} />
        <AmbientShapes chapterId={chapterId} />
        <SafeArea>
          <ChapterRouter />
        </SafeArea>
        <FadeBridge chapterId={chapterId} />
      </Stage>
      {/* Chrome stays outside the scaled canvas — pinned to viewport corners */}
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

- [ ] **Step 2: Verify build + existing tests still green**

```bash
cd demo/presentation && npm run build && npm run test:run
```

Expected: build OK, all existing tests pass (this change wraps but does not alter chapter render output yet; ch1 / ch2 steps still use their old absolute positioning — they're inside SafeArea but render unchanged because they each set `position: relative` + their own internal layout).

- [ ] **Step 3: Manual visual smoke test**

Open [http://localhost:5173/?ch=1&step=1](http://localhost:5173/?ch=1&step=1) and [http://localhost:5173/?ch=2&step=1](http://localhost:5173/?ch=2&step=1). Confirm: page still renders, no console errors, ambient shapes now appear at fixed pixel offsets (40px / 56px) — not 5% of viewport.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/App.jsx
git commit -m "feat(demo): wrap ChapterRouter in Stage/SafeArea (Phase 0.5)"
```

---

## Task 7: Retrofit Ch1 s1–s3 (text-only steps)

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step1.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step2.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step3.jsx`

These three steps have **no hub-satellite cluster** — they are vertically-centered text columns. They become `<SafeArea>` (already provided by App.jsx) + flex column with `<Sticker variant="kicker">` for badges / kickers and inline JSX for the hero text.

- [ ] **Step 1: Replace `Ch1Step1.jsx`** — keep visuals identical, drop the redundant `<main>` wrapper and use Sticker variants

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
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

      {/* 資展會 badge top-left (absolute inside SafeArea is allowed for fixed-corner chrome) */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <Sticker variant="kicker" bg="secondary" rotation={-3}>資展會 2026</Sticker>
      </motion.div>

      {/* 期中報告 hero */}
      <motion.div
        initial={{ scale: 0.7, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ display: 'inline-block', transform: 'rotate(-2deg)' }}
      >
        <Sticker variant="hub-mega" bg="accent" textColor="cream" style={{ fontSize: '7rem', padding: '56px 96px', letterSpacing: '0.08em', lineHeight: 1 }}>
          期中報告
        </Sticker>
      </motion.div>

      {/* presented by 王文杰 — mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 1.2, ease: 'easeOut' }}
        style={{
          marginTop: 48,
          fontSize: 28, fontWeight: 700, color: '#000',
          textAlign: 'center', letterSpacing: '0.05em',
        }}
      >
        presented by{' '}
        <span style={{
          background: '#000', color: '#FFFDF5',
          padding: '4px 20px', marginLeft: 8,
          fontWeight: 900,
        }}>
          王文杰
        </span>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Replace `Ch1Step2.jsx`** — same pattern (kicker top + hub center + caption)

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step2() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      gap: 32, fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">先簡單自我介紹</Sticker>
      </motion.div>

      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <Sticker variant="hub-md" bg="cream" rotation={-2}>
          心 理 學 系
          <div style={{ fontSize: '1.75rem', marginTop: 16, letterSpacing: '0.1em' }}>· 畢 業 ·</div>
        </Sticker>
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.7, delay: 1.1, ease: 'easeOut' }}
        style={{ marginTop: 16, fontSize: 22, fontWeight: 700, textAlign: 'center', lineHeight: 1.5, maxWidth: 760 }}
      >
        跨領域來資展會學 AI ·{' '}
        <span style={{
          background: '#FFD93D', padding: '2px 12px',
          border: '3px solid #000', boxShadow: '4px 4px 0 0 #000',
          marginLeft: 4,
        }}>非本科生</span>
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 3: Replace `Ch1Step3.jsx`** — same pattern + kicker + 3-span hero

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step3() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ x: -200, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ marginBottom: 48 }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">期中主題</Sticker>
      </motion.div>

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
        <span style={{ color: '#000', fontWeight: 900 }}>訓 練</span>
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', transform: 'rotate(-2deg)', display: 'inline-block',
        }}>AI</span>
        <span style={{
          background: '#FFD93D', color: '#000',
          border: '6px solid #000', boxShadow: '8px 8px 0 0 #000',
          padding: '0 24px', transform: 'rotate(2deg)', display: 'inline-block',
        }}>解 數 獨</span>
      </motion.div>
    </div>
  );
}
```

Note: Ch1Step3 previously had **4 corner decorative shapes**. They are removed here — that decoration role is now owned by the AmbientShapes layer (ch1 already has 5 ambient shapes registered in `tokens/chapters.js` covering tl/tr/bl/br/mr).

- [ ] **Step 4: Build + smoke test**

```bash
cd demo/presentation && npm run build
```

Open [http://localhost:5173/?ch=1&step=1](http://localhost:5173/?ch=1&step=1) → walk through s1/s2/s3. Confirm visuals match intent.

- [ ] **Step 5: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step{1,2,3}.jsx
git commit -m "refactor(demo): ch1 s1-s3 use Sticker variants + drop inline absolute decor"
```

---

## Task 8: Retrofit Ch1 s4–s7 (MRT window + satellites — HubSatellite)

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step5.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step6.jsx`
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step7.jsx`

These four steps form the central use case for `<HubSatellite>`: MRT window hub + 1–4 satellite stickers. Window size scaled up to **960×540** (was 640×360) per the spec's A2 "Cluster 70%" target — the previous 640px window was the root cause of the "too small in centre" complaint.

- [ ] **Step 1: Replace `Ch1Step4.jsx`** (caption + MRT window + 1 satellite)

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step4() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3, ease: 'easeOut' }}
        style={{
          position: 'absolute', top: 0, left: 0, right: 0,
          textAlign: 'center',
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        靈感哪來呢？某天捷運上⋯
      </motion.div>

      <HubSatellite>
        <HubSatellite.Hub>
          <motion.div
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.7, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
          </motion.div>
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <motion.div
            initial={{ x: -40, y: 40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
              正妹發呆中
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

- [ ] **Step 2: Replace `Ch1Step5.jsx`** (window + 正妹 persisted + Code Bullet new)

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step5() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
            正妹發呆中
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tr">
          <motion.div
            initial={{ x: 40, y: -40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="muted" rotation={3}>
              Code Bullet
              <div style={{ fontSize: 16, marginTop: 4, fontWeight: 700 }}>· flappy bird</div>
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>

      {/* Thought-bubble dashed arc (decoration overlay — full SafeArea) */}
      <svg
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        style={{
          position: 'absolute', inset: 0,
          width: '100%', height: '100%',
          pointerEvents: 'none', zIndex: 4,
        }}
      >
        <motion.path
          d="M 18 78 Q 50 30, 82 18"
          fill="none" stroke="#000"
          strokeWidth="2" strokeDasharray="6 6"
          vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.6, delay: 0.5, ease: 'easeOut' }}
        />
      </svg>
    </div>
  );
}
```

- [ ] **Step 3: Replace `Ch1Step6.jsx`** (3 satellites: 正妹 + Code Bullet + ⋯⋯)

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step6() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
            正妹發呆中
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tr">
          <Sticker variant="sat-lg" bg="muted" rotation={3}>
            Code Bullet
            <div style={{ fontSize: 16, marginTop: 4, fontWeight: 700 }}>· flappy bird</div>
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tl">
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [0, 1, 1], opacity: 1 }}
            transition={{
              scale: { duration: 0.3, ease: [0.34, 1.56, 0.64, 1] },
              opacity: { duration: 0.3 },
            }}
          >
            <motion.div
              animate={{ scale: [1, 1.08, 1] }}
              transition={{ duration: 1, ease: 'easeInOut', repeat: Infinity }}
            >
              <Sticker variant="sat-sm" bg="cream" style={{ borderRadius: 28, letterSpacing: '0.2em' }}>
                ⋯⋯
              </Sticker>
            </motion.div>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{
          position: 'absolute', bottom: 0, right: 0,
          fontSize: 18, fontWeight: 700, color: '#666',
        }}
      >
        然後我繼續發呆⋯
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 4: Replace `Ch1Step7.jsx`** (all 4 satellites)

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch1Step7() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          <AssetPlaceholder type="[E]" width={960} height={540} todo="ch1 s4-s7 捷運窗景 SVG" />
        </HubSatellite.Hub>
        <HubSatellite.Satellite position="bl">
          <Sticker variant="sat-lg" bg="secondary" rotation={-4} style={{ borderRadius: 20 }}>
            正妹發呆中
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tr">
          <Sticker variant="sat-lg" bg="muted" rotation={3}>
            Code Bullet
            <div style={{ fontSize: 16, marginTop: 4, fontWeight: 700 }}>· flappy bird</div>
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="tl">
          <Sticker variant="sat-sm" bg="cream" style={{ borderRadius: 28, letterSpacing: '0.2em' }}>
            ⋯⋯
          </Sticker>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="br">
          <motion.div
            initial={{ x: 40, y: 40, scale: 0.7, opacity: 0 }}
            animate={{ x: 0, y: 0, scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="sat-lg" bg="accent" textColor="cream" rotation={2}>
              沒手機·解數獨
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

- [ ] **Step 5: Build + smoke walk**

```bash
cd demo/presentation && npm run build
```

Open [http://localhost:5173/?ch=1&step=4](http://localhost:5173/?ch=1&step=4) → click through s4 / s5 / s6 / s7. Confirm:
- MRT window centred and visibly larger than before (960×540)
- Each satellite sits at the cluster corner with ≥48 px clear gap to the window edge
- Ambient shapes still visible in outer 15% ring, not overlapping satellites

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step{4,5,6,7}.jsx
git commit -m "refactor(demo): ch1 s4-s7 compose via HubSatellite + Sticker variants"
```

---

## Task 9: Retrofit Ch1 s8 (BOOM punchline)

**Files:**
- Modify: `demo/presentation/src/chapters/ch1-coldopen/Ch1Step8.jsx`

Ch1Step8 is the BOOM punchline (motif-heavy). It doesn't fit the HubSatellite pattern — the BOOM hero is centred + motif overlays cover the screen. Just swap any sticker-shaped inline blocks to `<Sticker>` and remove the redundant `<main>` height/100vh wrapper.

- [ ] **Step 1: Read the current `Ch1Step8.jsx`** to identify sticker-shaped inline blocks

```bash
cat demo/presentation/src/chapters/ch1-coldopen/Ch1Step8.jsx
```

- [ ] **Step 2: Apply two mechanical changes:**

  a. Replace the outer `<main style={{ ..., height: '100vh', padding: 32, ... }}>` with `<div style={{ ..., height: '100%', ... }}>` (drop `padding: 32` — SafeArea owns padding now; drop `height: 100vh` — SafeArea fills Stage)
  b. For any element with `background + border: '6px solid #000' + boxShadow + padding + fontWeight: 900`, wrap content in `<Sticker variant="hub-mega|hub-lg|hub-md|sat-lg|sat-md">` (pick the variant whose font-size most closely matches the original inline `fontSize`). Remove those inline styles. Leave motion props and positioning wrappers untouched. The BOOM hero specifically (8rem) → `hub-mega`.

  Do NOT touch the `<BoomDoubleRing>`, `<YellowHighlight>`, `<HalftoneBurst>`, `<InkSplatter>` motif components — they keep their existing positioning (motifs are exempt from layout rules).

- [ ] **Step 3: Build + walk s8**

```bash
cd demo/presentation && npm run build
```

Open [http://localhost:5173/?ch=1&step=8](http://localhost:5173/?ch=1&step=8) → click through the 3 beats. Confirm BOOM hero overshoot still fires, motifs still render, no console errors.

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch1-coldopen/Ch1Step8.jsx
git commit -m "refactor(demo): ch1 s8 use Sticker variant for BOOM hero (motifs unchanged)"
```

---

## Task 10: Retrofit Ch2 s1 + s4 (kicker-driven steps)

**Files:**
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step1.jsx`
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step4.jsx`

Ch2Step1 (ML overview) and Ch2Step4 (RL + AlphaGo) are similar shape: top kicker + hero + 3 stickers stagger. Replace inline `background/border/boxShadow/padding/fontWeight` blocks with `<Sticker>`.

- [ ] **Step 1: Replace `Ch2Step1.jsx`** — use Sticker for kicker / branch tiles, keep tree-connector SVG

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

const BRANCHES = [
  { id: 1, label: 'supervised',   sub: '看著答案抄筆記', bg: 'secondary', rotation: -3 },
  { id: 2, label: 'unsupervised', sub: '自己分類整理',   bg: 'muted',     rotation: 2 },
  { id: 3, label: 'RL',           sub: '試錯加獎懲',     bg: 'accent', textColor: 'cream', rotation: -2 },
];

export default function Ch2Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', gap: 32,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
      >
        <Sticker variant="kicker" bg="ink" textColor="cream">在開始之前 · 先講個背景</Sticker>
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4, ease: 'easeOut' }}
        style={{ fontWeight: 900, fontSize: '6rem', lineHeight: 1.05, letterSpacing: '0.05em' }}
      >
        機器學習
      </motion.div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.5rem' }}
      >
        底下總共分成{' '}
        <span style={{
          background: '#FFD93D', padding: '2px 14px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900,
        }}>三大分支</span>
      </motion.div>

      <motion.svg
        width="640" height="60" viewBox="0 0 640 60"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 1.4 }}
        style={{ overflow: 'visible' }}
      >
        <motion.path
          d="M 320 0 L 320 20 M 110 50 L 110 30 L 530 30 L 530 50 M 320 30 L 320 50"
          fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.5, delay: 1.4, ease: 'easeOut' }}
        />
      </motion.svg>

      <div style={{ display: 'flex', gap: 64, alignItems: 'flex-start' }}>
        {BRANCHES.map((b, i) => (
          <motion.div
            key={b.id}
            initial={{ y: -30, scale: 0.8, opacity: 0 }}
            animate={{ y: 0, scale: 1, opacity: 1 }}
            transition={{
              duration: 0.4, delay: 1.7 + i * 0.18,
              ease: [0.34, 1.56, 0.64, 1],
            }}
          >
            <Sticker variant="sat-lg" bg={b.bg} textColor={b.textColor} rotation={b.rotation}>
              <div style={{ fontSize: 14, letterSpacing: '0.1em', opacity: 0.7 }}>{`(${i + 1})`}</div>
              <div style={{ marginTop: 4, fontSize: 28 }}>{b.label}</div>
              <div style={{ fontSize: 16, marginTop: 8, fontWeight: 700 }}>{b.sub}</div>
            </Sticker>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 2.6 }}
        style={{ position: 'absolute', bottom: 0, fontWeight: 700, fontSize: 18, color: '#666' }}
      >
        一個一個來看 →
      </motion.div>
    </div>
  );
}
```

- [ ] **Step 2: Open `Ch2Step4.jsx`** and apply the same Sticker substitution

```bash
cat demo/presentation/src/chapters/ch2-ml-map/Ch2Step4.jsx
```

Replace any inline `background + border: '...solid #000' + boxShadow + padding + fontWeight: 900` block with `<Sticker variant=...>` (use `kicker` for the top tag, `hub` for the big "RL · reinforcement learning" composite, `sat-lg` for the 白話 label, and keep the AlphaGo stamp inline since it has bespoke `rotate -2` + `y: -200` choreography that doesn't fit `<Sticker>` cleanly — but you can still wrap the inner content of the stamp in `<Sticker variant="sat-lg" bg="accent" textColor="cream">`).

Also drop the outer `<main height: 100vh padding: 32>` wrapper → use `<div height: 100%>`.

- [ ] **Step 3: Build + walk**

```bash
cd demo/presentation && npm run build
```

Open [http://localhost:5173/?ch=2&step=1](http://localhost:5173/?ch=2&step=1) and [http://localhost:5173/?ch=2&step=4](http://localhost:5173/?ch=2&step=4). Confirm sticker sizing matches sat-lg (≥1.5rem, ≥16px padding).

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step{1,4}.jsx
git commit -m "refactor(demo): ch2 s1+s4 use Sticker variants (kicker/hub/sat-lg)"
```

---

## Task 11: Retrofit Ch2 s2 + s3 + s5 (supervised / unsupervised / cliffhanger)

**Files:**
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step2.jsx`
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step3.jsx`
- Modify: `demo/presentation/src/chapters/ch2-ml-map/Ch2Step5.jsx`

Same pattern as Task 10 — these are kicker + hero + label + right-side illustration steps. The right-side illustration cluster (老師/題目/學生 in s2; 衣服分類 in s3; ? sticker in s5) can stay as inline JSX or be modelled as `<HubSatellite>` with the hero text as Hub and the illustration as a satellite — implementer's choice based on visual outcome.

- [ ] **Step 1: For each of Ch2Step2 / Ch2Step3 / Ch2Step5, apply the same mechanical conversion:**

  a. Drop `<main height: 100vh padding: 32>` → `<div height: 100%>`
  b. Top kicker (`機器學習 · ①/3` etc.) → `<Sticker variant="kicker" bg="ink" textColor="cream">`
  c. Right-side sticker blocks (老師 / 題目 / 學生 in s2; 一堆 / 紅黃紫 in s3; ? sticker in s5) → `<Sticker variant="sat-md" bg=...>` (use `sat-md` because they're decorative, not primary satellites; `sat-lg` only for elements that need to read from the back of the room)
  d. The "白話：" yellow / purple highlight box → `<Sticker variant="sat-md">` inline
  e. KEEP all motion props and big mask-reveal hero (`supervised` / `unsupervised` / 問號 720° rotation) untouched — they're already the dominant focal element

- [ ] **Step 2: Build + walk all 5 ch2 steps**

```bash
cd demo/presentation && npm run build
```

Open [http://localhost:5173/?ch=2&step=1](http://localhost:5173/?ch=2&step=1), walk s1→s5. Confirm: no element below 1.5 rem font; no element with `<16 px` padding; ambient shapes visible.

- [ ] **Step 3: Commit**

```bash
git add demo/presentation/src/chapters/ch2-ml-map/Ch2Step{2,3,5}.jsx
git commit -m "refactor(demo): ch2 s2/s3/s5 use Sticker variants"
```

---

## Task 12: Add layout-system prelude + selective JSX rewrite for ch3–ch9 plan docs

**Files:**
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-3-ch3.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-4-ch4.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-5-ch5.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-6-ch6.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-7-ch7.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-8-ch8.md`
- Modify: `docs/superpowers/plans/2026-05-17-html-presentation-phase-9-ch9.md`

Two passes per file:
- **Pass A** (mandatory): insert the layout-primitives prelude after the existing `> **For agentic workers:**` blockquote.
- **Pass B** (selective): scan each task's JSX snippet — if the snippet's original layout is the hub + satellite or sticker stack pattern, rewrite it to use `<HubSatellite>` / `<Sticker variant=...>`. If the original layout is something else (split-screen, full-page chart, motif-heavy beat sequence, code wall, etc.), **leave the snippet untouched** and the implementer will translate it at execution time.

- [ ] **Step 1: Pass A** — for each of the 7 files, find the existing `> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.` line and insert immediately after it:

```markdown

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>` (parent provides), `<HubSatellite>` (hub + named-anchor satellites) and `<Sticker variant="hub-md|hub-lg|hub-mega|sat-lg|sat-md|sat-sm|kicker">` from `src/components/`. Inline `position: 'absolute'` + hard-coded `%` offsets are PROHIBITED in step files (motif components are exempt — `HalftoneBurst`, `InkSplatter`, `SpotlightVignette`, etc. continue to use viewport-relative positioning). JSX snippets in this plan that follow the hub+satellite or sticker pattern have been pre-translated; snippets for other layouts (split-screen, charts, etc.) are illustrative — translate them to primitive calls when executing. See [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) for tokens, variant table, and acceptance criteria.

```

- [ ] **Step 2: Pass B classification — walk each plan file and tag each step's snippet as one of:**

  - **HS** (hub+satellite): central element + 1–8 stickers around it → rewrite to `<HubSatellite>`
  - **S** (sticker-only stack): vertically/horizontally arranged sticker blocks, no central hub → rewrite each block to `<Sticker variant=...>` inside a flex container
  - **N** (not-applicable): split-screen, full-page charts, code walls, motif-driven punchlines, sudoku boards, IP grids, complex composite animations → leave snippet unchanged

  Reference classification (from a read of each plan):

  | Plan | Step | Pattern | Pass B action |
  |---|---|---|---|
  | ch3 | s1 LLM 路線 | N (left-column wipe + bg text grid) | leave |
  | ch3 | s2 VS 對比 | N (split-screen 60/40) | leave |
  | ch3 | s3 OK 純 RL | S (sticker stack + halftone motif) | rewrite Sticker blocks |
  | ch4 | s1 Kaggle | HS (Kaggle hub + 3 dataset card satellites + burst overlay) | rewrite to HubSatellite |
  | ch4 | s2 supervised 拒絕 | HS (red stamp hub + yellow satellite + ink splatter) | rewrite |
  | ch4 | s3 受害者 punchline | N (4-beat composite with red stamp motif) | leave |
  | ch4 | s4 封 IP | N (proxy grid + IP rotation) | leave |
  | ch5 | s1 結果我錯了 | N (4-beat crash-line motif) | leave |
  | ch5 | s2 838 行 | N (code wall + count-up badge) | leave |
  | ch5 | s3 debug 爆炸 | N (chaotic X spawn motif) | leave |
  | ch5 | s4 第一件學到 | S (4 keyword highlight stack) | rewrite Sticker blocks |
  | ch6 | s1 我又錯了 | N (crash-line punchline) | leave |
  | ch6 | s2 套皮仔策略 | HS (purple toolbox hub + yellow scoring satellite — or 2-block S) | rewrite |
  | ch6 | s3 新女生加分 | S (sticker + floating + symbols) | rewrite sticker |
  | ch6 | s4 曲線爬升 | N (SVG chart + sticker label) | leave |
  | ch6 | s5 卡平段 | N (chart with overlay) | leave |
  | ch6 | s6 備胎 ★★★ | N (motif-heavy 3-beat punchline) | leave |
  | ch6 | s7 偷吃步 | S (red stamp + 2 highlight blocks) | rewrite Sticker blocks |
  | ch7 | s1 重寫宣告 | S (kicker + hero + yellow highlight) | rewrite Sticker blocks |
  | ch7 | s2 顛倒驗證 | S (hero + 2 highlight blocks) | rewrite |
  | ch7 | s3 13 招階梯 | N (13 sticker custom stair grid + hover) | leave |
  | ch7 | s4 舊 vs 新 | N (split-screen 60/40) | leave |
  | ch7 | s5 Action 擴增 | HS (SudokuBoard hub + 2 action satellites) | rewrite |
  | ch7 | s6 機率 0 | N (3-beat punchline + count-up) | leave |
  | ch7 | s7 老油條 ★★★ | N (6-beat composite) | leave |
  | ch7 | s8 死結 | N (cinematic black-bg hero) | leave |
  | ch8 | s1 反向思考 | S (kicker + hero + footer hint) | rewrite Sticker blocks |
  | ch8 | s2 3 格空 | N (9×9 sudoku board centerpiece) | leave |
  | ch8 | s3 反向課程動畫 | N (board animation) | leave |
  | ch8 | s4 +20 → +50 | N (flip card motif) | leave |
  | ch8 | s5 光講不夠看 | S (hero + caption + arrow) | rewrite Sticker blocks |
  | ch8 | s6 visualizer 按鈕 | S (big button hero) | rewrite Sticker block |
  | ch9 | s1 tensorboard | HS (text hub + 2 image satellites + final hero) | rewrite |
  | ch9 | s2 核心金句 | S (hero stack 2-line) | rewrite Sticker blocks |
  | ch9 | s3 RL 對等 | HS (= sign hub + 2 panel satellites) | rewrite |
  | ch9 | s4 飛機+鳥 | HS (arrow hub + 2 emoji satellites) | rewrite |
  | ch9 | s5 戀愛 a | N (4-beat motif callback) | leave |
  | ch9 | s6 4 考題 | N (2×2 grid with hover) | leave |
  | ch9 | s7 plasticity 引出 | S (hero stack) | rewrite |
  | ch9 | s8 plasticity 三欄 | N (3-column + center stamp) | leave |
  | ch9 | s9 plasticity 機制 | S (3-item list + hero) | rewrite Sticker blocks |
  | ch9 | s10 MBTI | N (composite phase 1+2 with chart) | leave |
  | ch9 | s11 警語 ★★ | N (4-beat crash-line motif) | leave |
  | ch9 | s12 職場祝福 | S (hero stack) | rewrite Sticker blocks |
  | ch9 | s13 電費小偷 ★★★ | N (4-beat boom-ring motif callback) | leave |

  **Rewrite rule for HS-tagged steps:** replace the outermost `<main>...children with inline absolute positioning...</main>` with:
  ```jsx
  <div style={{ position: 'relative', zIndex: 20, height: '100%', display: 'flex',
                flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                fontFamily: 'Space Grotesk' }}>
    <HubSatellite>
      <HubSatellite.Hub>{the hub element}</HubSatellite.Hub>
      <HubSatellite.Satellite position="...">{satellite element}</HubSatellite.Satellite>
      ...
    </HubSatellite>
  </div>
  ```
  And replace each satellite's inline `background + border + boxShadow + padding + fontWeight: 900` with `<Sticker variant="sat-lg" bg=... rotation=...>`.

  **Rewrite rule for S-tagged steps:** replace sticker-shaped inline blocks with `<Sticker variant=...>` and preserve the existing flex / gap layout.

- [ ] **Step 3: For each HS or S step in the table above, apply the rewrite in the corresponding plan file.** This is mechanical but file-by-file — do not batch-edit with sed; each snippet has its own surrounding motion props and structure to preserve.

- [ ] **Step 4: Verify all 7 files now contain the prelude**

```bash
grep -l "Layout primitives (mandatory)" docs/superpowers/plans/2026-05-17-html-presentation-phase-*.md | wc -l
```

Expected: `7`.

- [ ] **Step 5: Verify N-tagged snippets remain untouched** — spot-check 3 random N steps from the table by reading their JSX snippet in the corresponding plan and confirming no `<HubSatellite>` or `<Sticker variant=`  was inserted.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/2026-05-17-html-presentation-phase-{3,4,5,6,7,8,9}-*.md
git commit -m "docs(plans): ch3-9 prelude + selective HS/S snippet rewrite (N-tagged leave alone)"
```

---

## Task 13: Final acceptance checkpoint

**Files:** none modified (verification only)

- [ ] **Step 1: Full build + test pass**

```bash
cd demo/presentation && npm run build && npm run test:run
```

Expected: build succeeds; all tests pass (existing 3 test files + 4 new ones from Tasks 1-4 = at least 7 test files green).

- [ ] **Step 2: Verify acceptance criteria from spec**

Open the running dev server and walk through. For each criterion, tick:

- [ ] `<Stage>` resizes: shrink dev tools to 960×540 (sub-1080p) → cluster scales proportionally; expand to 2560×1440 → cluster scales 1.333× larger; layout proportions identical at both sizes.
- [ ] All 13 retrofitted steps (ch1 s1–s8 + ch2 s1–s5) walk through without console errors.
- [ ] Grep step files for forbidden patterns:
  ```bash
  grep -nE "position: 'absolute'" demo/presentation/src/chapters/ch{1,2}-*/Ch*.jsx
  ```
  Expected output: only matches inside fixed-corner kicker / footer wrappers (top/bottom captions) or motion overlay wrappers — no hub+satellite cluster element should have raw `position: 'absolute'` outside `<HubSatellite>`.
- [ ] Grep for sticker-shape inline styles still in step files:
  ```bash
  grep -nE "border: '[46]px solid #000'" demo/presentation/src/chapters/ch{1,2}-*/Ch*.jsx
  ```
  Expected: a handful of remaining matches are OK if they belong to bespoke highlight `<span>`s inside hero text (e.g. ch1 s3 `AI` / `解 數 獨` inline highlights). Confirm none are full sticker blocks that should have used `<Sticker>`.
- [ ] AmbientShapes render in outer 15% ring on every step (never over content).
- [ ] Smallest satellite text rendered ≥1.5rem (zoom in browser dev tools to verify computed font-size).

- [ ] **Step 3: Tag**

```bash
git tag phase-0.5-layout-system-complete
```

- [ ] **Step 4: Update `demo/presentation/TODO.md`** if any acceptance criterion failed → record the gap and decide whether to fix-and-retag or defer.

---

## Resolved decisions (from brainstorm — 2026-05-17)

| Open question | Decision |
|---|---|
| HubSatellite cluster sizing | **Auto-fit hub + gap**, capped at safe area (1632×918) — see Task 1 / Task 3 |
| Ambient shape pixel offsets | 40 px top/bottom + 56 px left/right (centred in outer ~7.5% band) — Task 5 |
| Sticker `hub` variant granularity | **Three variants**: `hub-md` (4rem) / `hub-lg` (6rem) / `hub-mega` (8rem) — Task 4 |
| `<Sticker>` rotation + style transform composition | Out of scope for Phase 0.5; defer until a real step needs to compose both |
| ch3-9 JSX retrofit scope | **Prelude + selective rewrite**: only HS / S-tagged steps get JSX rewrites; N-tagged (split-screen / motif-heavy / charts) left untouched — Task 12 |

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-17-html-presentation-phase-0.5-layout-system.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
