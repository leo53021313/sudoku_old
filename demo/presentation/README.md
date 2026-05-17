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
- Beat state machine (85 beats from outline.md, advance / retreat / URL sync)
- Global visual layers (grain / halftone-drift / chapter-tint / ambient-shapes / fade-bridge)
- Shared components (progress / chapter-nav / beat-indicator / presenter-panel / sticker / hero / asset-placeholder)
- Motif Library: 8 full + 5 shells = 13 total
- Climax FX (A/B/C/E/G) via useClimax hook
- /sandbox verification page

## Phase 1+ scope (next)

Per-chapter steps will be added under `src/chapters/ch<N>-<name>/`. See [Phase 0 plan](../../docs/superpowers/plans/2026-05-17-html-presentation-phase-0.md) for the foundation.
