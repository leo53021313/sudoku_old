# Image-slide 1080p responsive fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** [docs/superpowers/specs/2026-05-21-img-slide-1080p-responsive-design.md](../specs/2026-05-21-img-slide-1080p-responsive-design.md)

**Goal:** Fix two `<img>`-bearing slides (Ch4Step3, Ch9Step3) so they render correctly on both 1080p (1920×1080) and 2K (2560×1440) viewports.

**Architecture:** Surgical per-slide edits. The image's container becomes a flex-shrinkable box (`flex: 1, minHeight: 0`), and the image scales down via `aspect-ratio` + `maxWidth: 100%, maxHeight: 100%` while preserving aspect ratio. No global scaffolding, no shared CSS changes.

**Tech Stack:** React 19 inline styles, motion/react animations, Vite dev server, manual visual verification via Chrome DevTools device emulation.

**Deviation from spec:** The spec says to apply a "symmetric fix" to both Ch9Step3 cards. On closer inspection only the **left (brain) card** overflows on 1080p — the right (neural net) card is already safe because its inner wrapper is `height: 260` (fixed small value). The neural-net card still receives `minHeight: 0` as defense-in-depth, but its internal layout is not restructured. This preserves the original 2K visual on the right side.

**No automated tests.** Verification is manual visual inspection in Chrome DevTools at two viewport sizes (1920×1080 and 2560×1440). This is consistent with the existing demo — no visual regression suite exists.

---

## File Structure

**Modified files:**
- `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step3.jsx` — fix hero/sticker overlap, make image stage shrinkable
- `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx` — fix brain image overflowing card border; defensive `minHeight: 0` on the right card

**Untouched:**
- `Ch1Step8.jsx` — already responsive via `objectFit: 'cover'`
- All non-image slides
- Global CSS, viewport setup, motion definitions

---

## Task 0: Pre-flight — dev server + baseline

**Purpose:** Confirm the dev server runs and capture a baseline of the current (broken) behavior. This anchors visual comparison after each edit.

- [ ] **Step 0.1: Install deps if not already**

Run from `demo/presentation/`:
```bash
cd demo/presentation
npm install
```
Expected: deps install cleanly (or "already up to date").

- [ ] **Step 0.2: Start the dev server in background**

```bash
npm run dev
```
Expected: Vite logs `Local: http://localhost:5173/` (or similar). Leave running.

- [ ] **Step 0.3: Open in Chrome and confirm presentation loads**

Open `http://localhost:5173` in Chrome. Click through to verify the app boots. Use the right-arrow key (or click) to advance beats. The app should render without console errors.

- [ ] **Step 0.4: Set DevTools to 1920×1080 emulation**

Open DevTools → toolbar device-mode icon → "Responsive" preset → enter `1920 × 1080`, DPR `1.0`. This emulates the report screen.

- [ ] **Step 0.5: Reproduce the two bugs as baseline**

Navigate to **ch4 step 3**. Advance to beat 1, 2, 3. Confirm the `websudoku.com` sticker visually overlaps "終極目標：去每個數獨網站霸榜". Screenshot if helpful.

Navigate to **ch9 step 3**. Confirm the brain image overflows the top and bottom of the left (cream) card by a few pixels.

Both bugs must reproduce at 1920×1080 before moving on. If they don't reproduce, **stop and investigate** — the issue might be DPR or viewport rather than CSS, and the plan's diagnosis would be wrong.

---

## Task 1: Fix Ch4Step3 — hero/sticker overlap

**Files:**
- Modify: `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step3.jsx` (3 distinct edits)

**Strategy:**
1. Add `paddingTop: 180` to `<main>` so the centered flex stack starts below the absolute-positioned hero text (hero stays at `top: 80`).
2. Make the victim stage shrinkable: `flex: '1 1 0', minHeight: 0, maxHeight: 600`, replace fixed `width: 1080` with `width: '100%', maxWidth: 1080`.
3. Make the image scale down: replace `width: 1000` with `width: 1000, maxWidth: '100%', height: 'auto', aspectRatio: '2558 / 1269', maxHeight: '100%'`. The `aspect-ratio` property lets the browser shrink width to satisfy `maxHeight`.

- [ ] **Step 1.1: Read the file**

```bash
# Open in your editor:
demo/presentation/src/chapters/ch4-data-hunt/Ch4Step3.jsx
```
Locate the three target spots: `<main>` style (line 22-28), victim stage div (line 69-73), and `<img>` (line 86-93).

- [ ] **Step 1.2: Edit 1/3 — add `paddingTop` to `<main>`**

In the `<main>` style object, change:
```jsx
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
```

To:
```jsx
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, paddingTop: 180,
    }}>
```

The `paddingTop: 180` reserves vertical space at the top so the flex stack (sticker + stage) starts below the hero text (which is `position: absolute, top: 80, fontSize: '2.5rem'` ≈ 80 + ~50 = ~130px tall — 180 gives a comfortable buffer).

- [ ] **Step 1.3: Edit 2/3 — make victim stage shrinkable**

In the stage `<div>` (currently line 69-73), change:
```jsx
      <div style={{
        position: 'relative', marginTop: 16,
        width: 1080, height: 600,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
```

To:
```jsx
      <div style={{
        position: 'relative', marginTop: 16,
        width: '100%', maxWidth: 1080,
        flex: '1 1 0', minHeight: 0, maxHeight: 600,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
```

This makes the stage:
- Fill available column width up to 1080 px (matches the original).
- Take available flex space, but shrink (`flex: '1 1 0'`) and never grow beyond 600 px (preserves 2K look).
- Allow content to overflow safely (`minHeight: 0` disables the default `min-height: auto` that would prevent shrinking below content size).

- [ ] **Step 1.4: Edit 3/3 — make image scale with aspect-ratio**

In the `<img>` (currently line 86-93), change:
```jsx
            <img
              src="/images/ch4/websudoku.png"
              alt="websudoku.com 網站截圖"
              style={{
                display: 'block', width: 1000,
                border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
              }}
            />
```

To:
```jsx
            <img
              src="/images/ch4/websudoku.png"
              alt="websudoku.com 網站截圖"
              style={{
                display: 'block',
                width: 1000, maxWidth: '100%',
                height: 'auto', maxHeight: '100%',
                aspectRatio: '2558 / 1269',
                border: '6px solid #000', boxShadow: '16px 16px 0 0 #000',
              }}
            />
```

The image is intrinsically 2558×1269 (aspect ratio ~2.016:1). Setting `aspectRatio: '2558 / 1269'` tells the browser to preserve that ratio when reducing width to satisfy `maxHeight: '100%'`. The rotated wrapper around it (`transform: rotate(-2deg)`) is left untouched — it sizes to the image, and the stamp at `bottom: -44, right: -36` remains pinned to the image's bottom-right.

- [ ] **Step 1.5: Visual verify at 1920×1080**

In Chrome at 1920×1080: navigate to ch4 step 3. Advance beats 0→1→2→3.

Expected:
- Beat 0: hero "終極目標：去每個數獨網站霸榜" visible centered near top.
- Beat 1: URL sticker slides in below hero (with clear gap, no overlap).
- Beat 2: URL sticker moves up 32 px; stage screenshot fades in below; **hero text still fully visible above the sticker, no overlap.**
- Beat 3: stage fades to "簡簡單單被我攻破" text; hero remains visible.

If hero is still overlapped, increase `paddingTop` (try 200, then 220). If hero is now too far from the rest, decrease `paddingTop`.

- [ ] **Step 1.6: Visual verify at 2560×1440**

Switch DevTools viewport to 2560×1440. Walk the same beats.

Expected: layout looks **nearly identical to pre-edit** (same image size, same vertical positions). The only allowed delta: image may render at 1080×~535 instead of original 1000×497 if the stage is now wider — but the spec accepted this within the "preserve original look" tolerance. If it's noticeably different, tighten the image's `width: 1000` (don't go above 1000 — that's the original design value).

- [ ] **Step 1.7: Commit**

```bash
git add demo/presentation/src/chapters/ch4-data-hunt/Ch4Step3.jsx
git commit -m "fix(demo): ch4 s3 hero/sticker overlap on 1080p (responsive stage + image)"
```

---

## Task 2: Fix Ch9Step3 — brain card overflow

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx` (2 edits to the left card, 1 defensive edit to the right card)

**Strategy:**
1. Add `minHeight: 0` to both cards' style objects (allows flex children to shrink below content).
2. On the left (brain) card: wrap the `<img>` in a flex-shrinkable middle slot (`flex: 1 1 auto, minHeight: 0`), and change the `<img>` from `width: '70%', height: 'auto'` to `maxWidth: '70%', maxHeight: '100%', width: 'auto', height: 'auto'` so the browser shrinks it to fit.
3. On the right (neural net) card: just add `minHeight: 0` for defense — the existing `width: 70%, height: 260` wrapper doesn't overflow at 1080p, so no structural change.

- [ ] **Step 2.1: Read the file**

```bash
# Open in your editor:
demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx
```

The file has two `<motion.div>` cards (left brain, right neural net) plus a yellow "=" circle in the middle and a hero text at the bottom. Both card styles use `flex: '0 0 40%', height: '60vh'`.

- [ ] **Step 2.2: Edit 1/3 — left card: add minHeight, wrap image, restructure**

Find the left card (currently line 11-34). Change:
```jsx
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
```

To:
```jsx
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)' }}
        animate={{ clipPath: 'inset(0 0 0 0)' }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh', minHeight: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
      >
        <div style={{
          flex: '1 1 auto', minHeight: 0,
          width: '100%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <img
            src="/images/ai/ch9/brain-reward.png"
            alt="大腦與獎懲 token"
            style={{
              display: 'block',
              maxWidth: '70%', maxHeight: '100%',
              width: 'auto', height: 'auto',
            }}
          />
        </div>
        <div style={{
          flex: '0 0 auto',
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '8px 20px',
          border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          fontWeight: 900, fontSize: '2rem',
        }}>腦科學 RL</div>
      </motion.div>
```

Changes:
- Card gets `minHeight: 0` (enables shrink).
- New `<div>` wrapper around `<img>`: `flex: 1 1 auto, minHeight: 0` (takes available card height, shrinks if needed); inner flex centering preserves the image's centered look.
- `<img>`: `maxWidth: 70%, maxHeight: 100%, width: auto, height: auto` — browser computes natural size, then caps it. On 2K the image renders at 70% of card width (538-ish px wide, ≤ 100% wrapper height). On 1080p the `maxHeight: 100%` caps it so the image shrinks to fit the wrapper.
- Sticker gets `flex: 0 0 auto` to lock its size (don't let it grow into the freed-up space).

- [ ] **Step 2.3: Edit 2/3 — right card: defensive `minHeight: 0`**

Find the right card (currently line 53-74). Change only the `height: '60vh'` line:
```jsx
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
```

To:
```jsx
        style={{
          flex: '0 0 40%', background: '#FFFDF5', color: '#000',
          height: '60vh', minHeight: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 32, gap: 16,
          border: '6px solid #000',
        }}
```

That's it. The `<NeuralNet>` wrapper (`width: 70%, height: 260`) stays unchanged — it doesn't overflow because 260 + 16 + ~64 + 64 padding = 404 < 648 (60vh on 1080p).

- [ ] **Step 2.4: (Skipped — defensive change only, no third edit needed)**

This step exists in the plan structure to mark that we considered changing the NeuralNet wrapper but explicitly chose not to (see "Deviation from spec" note at the top of this plan). Mark complete and move on.

- [ ] **Step 2.5: Visual verify at 1920×1080**

In Chrome at 1920×1080: navigate to ch9 step 3.

Expected:
- Left card: brain image fully inside the card's border (no overflow on top or bottom). Image is slightly smaller than the 2K version (acceptable). "腦科學 RL" sticker sits below the image, inside the border.
- Right card: visually unchanged from before (neural net + "AI 訓練 RL" sticker, same positions).
- "=" yellow circle in middle: unchanged.
- Bottom hero "其實是 同一件事": unchanged.

If brain image is still overflowing, double-check that `minHeight: 0` was added to the card and the wrapper div has `flex: 1 1 auto, minHeight: 0`. Both are required.

- [ ] **Step 2.6: Visual verify at 2560×1440**

Switch DevTools viewport to 2560×1440. Confirm ch9 step 3 looks **nearly identical to pre-edit**. The brain image may render at exactly 70% of card width (~717 px) and be centered vertically in the available flex space — slight vertical-centering shift is acceptable. If the visual is meaningfully different, log what changed and decide whether to tighten the constraints.

- [ ] **Step 2.7: Commit**

```bash
git add demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx
git commit -m "fix(demo): ch9 s3 brain image overflow on 1080p (flex-shrinkable image slot)"
```

---

## Task 3: Cross-resolution sanity check

**Purpose:** Walk the relevant slides at one intermediate viewport size to catch off-by-some-pixels at common laptop resolutions.

- [ ] **Step 3.1: Test at 1366×768 (small laptop)**

Set Chrome DevTools to 1366×768. Walk ch4 step 3 (all beats) and ch9 step 3.

Expected:
- Ch4 s3: hero and sticker both visible, no overlap. Stage image may be much smaller. Stamp may overhang the visible area slightly (acceptable per spec — out of 1080p–2K range).
- Ch9 s3: brain image fits inside left card. Both cards may look short but content is bounded.

If something breaks at 1366×768, log it but don't fix in this plan — the spec's verification window is 1080p–2K.

- [ ] **Step 3.2: Test at 1440×900 (MacBook Air)**

Same walk-through. Expected: clean layout at both slides.

- [ ] **Step 3.3: Stop the dev server**

```bash
# In the terminal running `npm run dev`, press Ctrl+C
```

- [ ] **Step 3.4: Final review**

Confirm:
1. Two commits in `git log`:
   - `fix(demo): ch4 s3 hero/sticker overlap on 1080p (responsive stage + image)`
   - `fix(demo): ch9 s3 brain image overflow on 1080p (flex-shrinkable image slot)`
2. No untracked changes to other slides.
3. `git diff main..HEAD --stat` shows exactly 2 files modified.

If everything matches, the plan is done.

---

## Self-Review Notes (already applied)

- **Spec coverage:** every spec requirement maps to a task (Ch4Step3 → Task 1, Ch9Step3 brain card → Task 2, Ch9Step3 neural-net card → Task 2 Step 2.3 defensive-only). The deviation from "symmetric restructure" is called out in the header.
- **Placeholder scan:** all code blocks are concrete; no "TBD" or "implement later".
- **Type consistency:** property names (`flex`, `minHeight`, `maxHeight`, `aspectRatio`) are used consistently across tasks.
- **Unknown:** Whether `paddingTop: 180` on Ch4Step3 is exactly right is a tunable. The plan calls this out at Step 1.5 with guidance to adjust ±20px if needed.
