# Presentation Layout System · Design Spec

**Date:** 2026-05-17
**Status:** Approved (brainstorm done, plan pending)
**Scope:** Establish a uniform spatial layout system for the `demo/presentation/` slide deck so all 9 chapters (58 steps) follow the same rules — cards breathe, ambient space is intentional, presentation looks identical on 1080p and 2K monitors.

## Problem

The deck (Phase 0–2 implemented, Phase 3–9 planned) currently builds every step with hand-tuned inline `position: absolute` + percentage offsets. Two failure modes have shown up:

1. **Cards too close + canvas too empty.** When stickers are pulled toward the central hub (e.g. ch1 s4–s7 after recent tightening) they cluster in the middle and leave 30%+ of the 16:9 canvas as dead space. On 2K screens this gets worse because `rem`-based typography doesn't scale with the viewport.
2. **No reuse across chapters.** Plan docs for ch3–ch9 already prescribe inline-style JSX patterns. Without a primitive, every chapter would repeat the same layout mistakes and the deck would drift visually as it grows.

## Decisions (from brainstorming session)

| Dimension | Choice | Rationale |
|---|---|---|
| Multi-element distribution | **Hub & Satellite** | Familiar, matches the talk's "central topic + 3–4 supporting beats per step" rhythm |
| Cluster scale | **70% safe area** + enlarged satellite stickers (≥1.5rem font) | Leaves 15% breathing ring for ambient layer; satellites large enough to read from back of room |
| Viewport scaling | **Fixed 1920×1080 canvas + CSS `transform: scale`** | Keynote-style WYSIWYG; 1080p → 1.0×, 2K → 1.333×, 4K → 2.0×; QA-friendly |
| Outer 15% ambient zone | **Pure ambient shapes** (strengthen existing `AmbientShapes` layer) | Keeps Neo-brutalism aesthetic; no meta chrome competing with content |

## Architecture

```
<Stage>                              ← 1920×1080 fixed canvas, ResizeObserver → transform:scale(N)
  ├── <AmbientShapes chapterId/>     ← Outer 15% ring, per-chapter decorations (existing, repositioned)
  ├── <SafeArea>                     ← Inner 1632×918 (85%), all step content lives here
  │     └── {step content}           ← Composed from HubSatellite / Sticker / Hero primitives
  ├── <ProgressBar/>                 ← Existing chrome, unchanged
  ├── <ChapterNav/>                  ← Existing chrome, unchanged
  ├── <BeatIndicator/>               ← Existing chrome, unchanged
  └── <PresenterPanel/>              ← Existing chrome, unchanged
```

### Component responsibilities

- **`<Stage>`** (new) — root that owns the 1920×1080 canvas. ResizeObserver on `window` recomputes `scale = min(vw/1920, vh/1080)` on resize; applies `transform: scale(N)` + `transform-origin: top left` to the canvas wrapper. Non-16:9 viewports get letterboxed (top/bottom or left/right cream bands), which the ambient layer naturally fills.
- **`<SafeArea>`** (new) — inner content frame with `padding: 108px 144px` (7.5% each side at 1920×1080). All step content is rendered inside.
- **`<HubSatellite>`** (new) — layout primitive for the dominant pattern: one central hub + 1–8 satellites at named anchor positions (`tl`/`t`/`tr`/`l`/`r`/`bl`/`b`/`br`). Maintains a `gap` (default 48px) between hub edge and nearest satellite edge. Satellites cannot enter the hub's bounding box + gap.
- **`<Sticker variant="...">`** (extended) — single source of truth for the brutalism sticker style. Variants: `hub`, `sat-lg`, `sat-md`, `sat-sm`, `kicker`. Each variant locks font-size, padding, border, and shadow to design tokens.
- **`<AmbientShapes>`** (existing, repositioned) — render shapes outside the SafeArea inner box (in the outer 15% ring). Density and shapes already configured per-chapter in `tokens/chapters.js`; this spec only changes where they render (outer ring, not anywhere on canvas).

## Tokens

### `tokens/spacing.js` — additions

```js
export const spacing = {
  1: 4, 2: 8, 3: 12, 4: 16, 6: 24, 8: 32, 12: 48, 16: 64, 24: 96,
  // new (post-spec):
  32: 128,   // hub-satellite gap (large), inter-cluster padding
  40: 160,   // section padding (large)
  48: 192,   // hero-to-cluster gap (vertical, when both present)
};
```

### `tokens/stage.js` — new file

```js
export const stage = {
  width: 1920,
  height: 1080,
  aspectRatio: 16 / 9,
  safePadding: { x: 144, y: 108 },   // 7.5% each side → safe area 85% (1632×918)
  cluster: {
    maxWidth: 1344,                  // 70% of 1920
    maxHeight: 756,                  // 70% of 1080
    hubToSatelliteGap: 48,           // default <HubSatellite gap={48}>
  },
  ambient: {
    outerBandPct: 15,                // outer 15% of canvas reserved for AmbientShapes
  },
};
```

### Sticker variant table (drives `<Sticker variant>`)

| variant | use case | font-size | padding | border | shadow | min-size |
|---|---|---|---|---|---|---|
| `hub` | Central window / hero card | 4–8rem | 56–96px | 6px | 12–20px | — (content-driven) |
| `sat-lg` | Primary satellite (default) | **1.75rem** | **20×32px** | **4px** | **10×10px** | min-width 160px |
| `sat-md` | Secondary satellite | 1.5rem | 16×24px | 4px | 8×8px | min-width 140px |
| `sat-sm` | Accent (`⋯⋯` bubble) | 1.25rem | 12×20px | 3px | 6×6px | min-width 80px |
| `kicker` | Top/bottom caption | 1–1.25rem | 12×28px | 3px | 6×6px | — |

**Hard rules:** all satellites must use `sat-lg` / `sat-md` / `sat-sm`. Custom inline `style={{ fontSize, padding }}` for sticker-like elements is **forbidden** post-refactor. New ESLint rule (optional) can flag inline `position: 'absolute'` outside `<HubSatellite>`.

## API examples

### Replace current ch1 s7 pattern

**Before** (current, hand-tuned negative offsets):
```jsx
<div style={{ position: 'relative' }}>
  <AssetPlaceholder width={640} height={360} ... />
  <div style={{ position: 'absolute', bottom: -32, left: -48,
    background: '#FFD93D', padding: '12px 20px', ... }}>正妹發呆中</div>
  <motion.div style={{ position: 'absolute', top: -32, right: -48, ... }}>
    Code Bullet</motion.div>
  {/* + 2 more identical blobs */}
</div>
```

**After** (declarative primitive):
```jsx
<HubSatellite gap={48}>
  <HubSatellite.Hub>
    <AssetPlaceholder width={960} height={540} todo="MRT 窗景 SVG" />
  </HubSatellite.Hub>
  <HubSatellite.Satellite position="tl" variant="sat-sm" color="cream">⋯⋯</HubSatellite.Satellite>
  <HubSatellite.Satellite position="tr" variant="sat-lg" color="purple">
    Code Bullet<div>· flappy bird</div>
  </HubSatellite.Satellite>
  <HubSatellite.Satellite position="bl" variant="sat-lg" color="yellow">正妹發呆中</HubSatellite.Satellite>
  <HubSatellite.Satellite position="br" variant="sat-lg" color="red">沒手機·解數獨</HubSatellite.Satellite>
</HubSatellite>
```

- `position` enum: `tl t tr l r bl b br` — 8 anchors around the hub
- `color` enum: matches Neo palette (`cream cream-bg yellow purple red ink`)
- `variant` default `sat-lg`; override per-satellite when needed
- Motion entrance animation: `<HubSatellite>` adds a default stagger (overshoot `[0.34, 1.56, 0.64, 1]`, 0.5s, 120ms stagger between satellites). Per-satellite `delay` / `transition` overrides allowed.

## Refactor scope

### Phase A · Immediate (becomes Phase 0.5 implementation plan)

1. Create `<Stage>`, `<SafeArea>`, `<HubSatellite>` primitives under `src/components/`.
2. Extend `<Sticker>` with the 5-variant system.
3. Add `tokens/stage.js`; extend `tokens/spacing.js`.
4. Reposition `<AmbientShapes>` to render only inside the outer 15% ring (not over content).
5. Wrap `<ChapterRouter />` in `<Stage><SafeArea>` inside `App.jsx`.
6. **Retrofit existing steps**: ch1 s1–s8 + ch2 s1–s5 (13 steps total) to use new primitives. Remove hand-tuned absolute positioning.
7. Visual regression check: walk all 13 steps on both 1080p and 2K (or browser dev tools resize), confirm cluster fills 70%, satellites breathe, no overflow into ambient ring.

### Phase B · Forward-applied to ch3–ch9 plans

Each plan doc (`docs/superpowers/plans/2026-05-17-html-presentation-phase-3-ch3.md` through `-phase-9-ch9.md`) gets a **one-paragraph prelude** added at the top:

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>`, `<HubSatellite>` / `<Sticker variant=...>` from `src/components/`. Inline `position: absolute` + hard-coded `%` offsets are prohibited except inside motif components (`HalftoneBurst`, `InkSplatter`, `SpotlightVignette` etc.). See `docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md` for tokens and variant table.

The JSX snippets currently in those plans are illustrative — implementers will translate them to primitive calls when they execute that phase. The plans themselves don't need full JSX rewrites in this Phase B pass; just the prelude + a TODO note next to any step that explicitly used a layout pattern incompatible with `<HubSatellite>` (e.g. split-screen steps in ch3 s2 / ch6 s5).

## Out of scope

- **Motif components** (`HalftoneBurst`, `InkSplatter`, `BoomDoubleRing`, etc.) — these are FX overlays, they get a free pass on absolute positioning and continue to use `position: fixed` + viewport coords.
- **Punchline ★/★★/★★★ stages** — beat-driven composition logic (climax FX, screen shake) is unchanged. Layout primitives only govern static positioning.
- **Background layers** (`HalftoneBg`, `GlobalGrain`, `ChapterTint`, `FadeBridge`) — already render as full-canvas overlays, no change.
- **Real asset production** (SVG illustrations, tensorboard screenshots) — tracked separately in `demo/presentation/TODO.md`.

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Letterbox bands on non-16:9 screens look like a bug | Ambient layer extends into the band naturally; document for presenter |
| `transform: scale` interferes with `position: fixed` motif overlays | Motifs render in a separate sibling layer outside the scaled canvas |
| Retrofit breaks an already-recorded beat sequence | Beat-manifest.js unchanged; only JSX inside step files rewrites — `<HubSatellite>` is purely visual |
| `<HubSatellite>` doesn't fit asymmetric split-screen steps (ch3 s2, ch6 s5, etc.) | Those steps fall back to `<SafeArea>` + manual flex layout; primitive is opt-in, not enforced for non-hub patterns |
| Plan doc preludes get ignored by future implementers | Spec is the source of truth; preludes link back; code review checks for `position: 'absolute'` in step files |

## Acceptance criteria

After Phase A is implemented:

- [ ] `<Stage>` resizes correctly: 1920×1080 viewport → scale 1.0; 2560×1440 → scale 1.333; 3840×2160 → scale 2.0
- [ ] Same step file renders **identical relative layout** (sticker positions vs hub) on 1080p and 2K
- [ ] All 13 retrofitted steps use `<HubSatellite>` or `<SafeArea>` + flex — no `position: 'absolute'` remains in step JSX
- [ ] Satellite stickers ≥ 1.5rem font, ≥ 16px padding everywhere
- [ ] Ambient shapes render only in the outer 15% ring, never over a sticker
- [ ] All existing tests pass; visual walk-through of all 13 steps passes manual review
