# Image-slide responsive layout fix (1080p + 2K)

**Date:** 2026-05-21
**Scope:** `demo/presentation/` — image-bearing slides only

## Problem

Demo slides were authored on a 2K (2560×1440) screen but the presentation will be delivered on 1080p (1920×1080). On 1080p, two slides break:

1. **Ch4Step3** — the `websudoku.com` URL sticker overlaps the "終極目標：去每個數獨網站霸榜" hero text during beats 1–3. The hero is `position: absolute, top: 80` (outside flex flow), while the centered flex stack (sticker + 600 px stage) gets pushed upward as viewport height shrinks.
2. **Ch9Step3** — the 1254×1254 brain-reward.png image (`width: 70%, height: auto` of a `flex: 0 0 40%, height: 60vh` card) overflows the card's top and bottom borders on 1080p (~17 px each side). The "腦科學 RL" sticker sits at the bottom and also breaks through the lower border.

The pattern: every other slide uses `vh / flex / %` for sizing and is naturally responsive. Image-bearing slides have **fixed pixel container dimensions** picked to match each image's intrinsic aspect ratio — those numbers work on the author's 2K screen but not on the smaller 1080p delivery screen.

## Root cause

| Slide | What's hard-coded | Consequence on 1080p (~900–1000 px usable height) |
|---|---|---|
| `Ch4Step3.jsx:69-73` | victim stage `width: 1080, height: 600` (fixed px); hero text `position: absolute, top: 80` outside flex flow | flex container vertically centers (60 px sticker + 16 gap + 600 stage = 676) → top of sticker lands at ~112 px → beat 2 `y: -32` → ~80 px → overlaps hero text bottom edge (~130 px) |
| `Ch9Step3.jsx:15-34, 53-74` | card `height: 60vh` (648 px on 1080p); image `width: 70%, height: auto` of `flex: 0 0 40%` (768 px wide) → 538×538 image; plus padding 32+32 + gap 16 + sticker ~64 = 682 px total | content overflows card by ~34 px → image visually crosses both top and bottom card borders; sticker pushes through bottom border |
| `Ch1Step8.jsx` | uses `objectFit: 'cover'` already; AiSticker widths 280 px fixed but no overlap reported | **not in scope** — leave as-is |

The fundamental fix pattern: an image's container should be a **shrinkable flex item** (`flex: 1, minHeight: 0`), and the image itself should use `object-fit: contain` with `maxWidth: 100%, maxHeight: 100%` so the browser shrinks it to fit when space is tight, while preserving aspect ratio.

## Approach

**Surgical per-slide fix.** Only two slides are modified. Layout intent is preserved (image stays roughly where the author placed it on 2K); the change is that on 1080p the image shrinks down to fit instead of overflowing or pushing other elements.

**Out of scope:** `Ch1Step8.jsx` (already responsive via `objectFit: 'cover'`), all non-image slides, global scale-to-fit transform (rejected: would soften text rendering at all non-2K resolutions, and we'd need to convert every `100vh` reference).

## Design

### Ch4Step3 — fix hero/sticker overlap

Two coupled changes:

1. **Stage becomes a shrinkable flex child.** Change the victim stage container from fixed `width: 1080, height: 600` to a flex-shrinkable box that respects viewport height:
   - `width: '100%', maxWidth: 1080`
   - `flex: '1 1 0', minHeight: 0` so it shrinks within the column flex flow
   - `maxHeight: 600` so on 2K it never grows past the original design size

2. **Image scales inside the stage.** Replace explicit `width: 1000` on the `<img>` with:
   - `maxWidth: '100%', maxHeight: '100%', width: 'auto', height: 'auto', objectFit: 'contain'`

3. **Hero stays absolute, but reserve space.** The hero text remains `position: absolute, top: 80` (unchanged — preserves the "kicker pinned to top" visual). Add `paddingTop: 180` (or equivalent) to the `<main>` so the flex stack (sticker + stage) starts below the hero, regardless of viewport height. Tune the value so that on 2K the layout looks identical to today.

This keeps every visual choice — sticker pop-up from below, beat 2 `y: -32` shift, stamp overhang — but eliminates the collision.

### Ch9Step3 — fix image overflow on both cards

Symmetric fix on the cream (brain) card and the cream (neural net) card:

1. **Card allows children to shrink.** Add `minHeight: 0` to both card divs. (Required because flex children default to `min-height: auto`, which prevents shrinking below content size.)
2. **Image wrapper is a shrinkable flex middle child.** Wrap the image in a flex item with `flex: '1 1 auto', minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center'`. Same for the NeuralNet div on the right card (it's already `width: 70%, height: 260` — the `height: 260` becomes `flex: 1, minHeight: 0`).
3. **Image fits inside the wrapper.** Change brain image from `width: '70%', height: 'auto'` to `maxWidth: '70%', maxHeight: '100%', width: 'auto', height: 'auto', objectFit: 'contain'`.

The "=" yellow circle and bottom hero text are unaffected (already vh/% based).

## Verification

For each fixed slide, manually verify in browser at two viewports:

- **2K** (≥2560×1440 — emulate via DevTools): screenshot must match current production look pixel-for-pixel (or within visual tolerance — the only difference allowed is that the image might be very slightly smaller because of `maxHeight` constraints).
- **1080p** (1920×1080 — emulate via DevTools): no overlap of hero with URL sticker (Ch4Step3); no image breaking through card borders (Ch9Step3).

Also verify intermediate (1440×900, 1366×768) to confirm graceful degradation.

No automated tests are added — this is a visual regression class of problem and the demo has no existing visual regression suite.

## Risks and rollback

- **Risk:** Subtle visual shift on 2K because we introduce `maxHeight: 600` / `maxHeight: '100%'` constraints that were previously implicit. Mitigation: tune `paddingTop` on Ch4Step3 `<main>` until 2K screenshot matches.
- **Risk:** The Ch4Step3 stamp overhang (`bottom: -44, right: -36` on `RedStamp`) is relative to the inner `transform: rotate(-2deg)` wrapper, not the stage. Shrinking the stage shrinks the image but the stamp offset is fixed px — on a much smaller image, the stamp could overhang too far. Acceptable in 1080p–2K range; document the assumption.
- **Rollback:** revert the two file edits. No data migrations, no config changes.

## Files touched

- `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step3.jsx` (~10 lines)
- `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx` (~15 lines)

No new files, no shared CSS changes, no global scaffolding.
