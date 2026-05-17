# Phase 6 · Chapter 6 (sb3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>` (parent provides), `<HubSatellite>` (hub + named-anchor satellites) and `<Sticker variant="hub-md|hub-lg|hub-mega|sat-lg|sat-md|sat-sm|kicker">` from `src/components/`. Inline `position: 'absolute'` + hard-coded `%` offsets are PROHIBITED in step files (motif components are exempt — `HalftoneBurst`, `InkSplatter`, `SpotlightVignette`, etc. continue to use viewport-relative positioning). JSX snippets in this plan that follow the hub+satellite or sticker pattern have been pre-translated; snippets for other layouts (split-screen, charts, etc.) are illustrative — translate them to primitive calls when executing. See [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) for tokens, variant table, and acceptance criteria.

**Goal:** Build ch6 sb3 — 套皮仔 → 「我又錯了」#2 崩盤 → 新女生加分 → 曲線爬升 → 卡平段 → **備胎 ★★★** → 偷吃步揭穿. 7 steps, ~73s, 2 punchlines (s1 light A+C + s6 ★★★ full A+B+C+E+G). First use of `motif/girl-new` (s3) and all 4 climax-FX motifs being used as primary (spotlight-vignette / halftone-burst / ink-splatter / screen-shake all converge in s6 ★★★).

**Source spec:** [outline.md §6](../../../demo/outline.md) · script.md L167-L199

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch6
└── ch6-sb3/
    ├── Ch6.jsx
    ├── Ch6Step1.jsx                        # 我又錯了 ★ (3-beat, crash-line rhyme)
    ├── Ch6Step2.jsx                        # 套皮仔策略 + 填對給分
    ├── Ch6Step3.jsx                        # 新女生加分 (first girl-new motif)
    ├── Ch6Step4.jsx                        # AI 得分曲線爬升
    ├── Ch6Step5.jsx                        # 卡平段 · 不思進取
    ├── Ch6Step6.jsx                        # 備胎 ★★★ full A+B+C+E+G
    └── Ch6Step7.jsx                        # 偷吃步 · 找漏洞作弊
```

---

## Task 1: Register Ch6 + Step1 ★ punchline (crash-line rhyme)

**Files:**
- Create: `Ch6.jsx`, `Ch6Step1.jsx`
- Modify: `src/chapters/index.jsx`

Beat structure (3-beat, similar to ch5 s1):
- beatIndex 0: kicker「正當我以為成了套皮仔⋯⋯」fade-down
- beatIndex 1: CrashLine placeholder (empty frame + blinking caret) — note: `wait: 0.8s` shorter than ch5 s1 because audience knows the motif now
- beatIndex 2: CrashLine fill「⋯⋯我又錯了」+ A+C climax (rhyme)

- [ ] **Step 1: Update `src/chapters/index.jsx`** — register `6: Ch6`

- [ ] **Step 2: Create `Ch6.jsx`**

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch6Step1 from './Ch6Step1.jsx';

const STEPS = { 1: Ch6Step1 };

export function Ch6() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 6 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Create `Ch6Step1.jsx`** (mirrors ch5 s1 — motif rhyme, slightly shorter wait)

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { CrashLine } from '../../motifs/CrashLine.jsx';

export default function Ch6Step1() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);

  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
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
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -30, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '2rem',
        }}
      >
        正當我以為成了套皮仔⋯⋯
      </motion.div>

      <CrashLine
        active={beatIndex >= 1}
        filled={beatIndex >= 2}
        text="⋯⋯我又錯了"
        width={720}
      />
    </main>
  );
}
```

- [ ] **Step 4: Build + commit**: `feat(demo): ch6 register + s1 我又錯了 punchline (crash-line rhyme)`

---

## Task 2: Ch6Step2/Step3/Step4/Step5 batched (4 narrative steps)

**Files:**
- Create: `Ch6Step2.jsx`, `Ch6Step3.jsx`, `Ch6Step4.jsx`, `Ch6Step5.jsx`
- Modify: `Ch6.jsx`

### Ch6Step2 — 套皮仔策略 + 填對給分

```jsx
import { motion } from 'motion/react';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch6Step2() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          {/* Hub: scoring rule card */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
          >
            <Sticker variant="hub-md" bg="#FFFFFF">
              <div style={{ textAlign: 'center', lineHeight: 1.3, fontSize: '2rem' }}>
                只要他<br/>
                <Sticker variant="kicker" bg="#FFD93D">填對一格</Sticker>
                <br/>就給分數
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.3, delay: 1.0 }}
                  style={{ marginTop: 16, fontSize: '3rem', color: '#FF6B6B' }}
                >+1</motion.div>
              </div>
            </Sticker>
          </motion.div>
        </HubSatellite.Hub>

        <HubSatellite.Satellite position="l">
          {/* Satellite: Python toolbox sticker */}
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          >
            <Sticker variant="sat-lg" bg="#C4B5FD" rotation={-3}>
              社群現成<br/>Python 工具箱
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

### Ch6Step3 — 新女生加分 (first use of `motif/girl-new`)

```jsx
import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch6Step3() {
  const [plusses, setPlusses] = useState([]);
  useEffect(() => {
    let id = 0;
    const t = setInterval(() => {
      setPlusses(prev => [
        ...prev,
        { id: id++, x: Math.random() * 80 + 10, delay: 0 },
      ].slice(-15));
    }, 400);
    return () => clearInterval(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 剛認識的新女生 sticker — pink + rotation */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <Sticker variant="hub-lg" bg="#FFB6C1" rotation={-4}>
          <div style={{ textAlign: 'center', lineHeight: 1.3 }}>
            剛認識的<br/>新女生 ✨
          </div>
        </Sticker>
      </motion.div>

      {/* +/+/+ floating plus symbols */}
      {plusses.map(p => (
        <motion.div
          key={p.id}
          initial={{ y: 0, opacity: 1 }}
          animate={{ y: -300, opacity: 0 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${p.x}%`, bottom: '20%',
            fontSize: 48, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '2px black',
            pointerEvents: 'none',
          }}
        >
          +
        </motion.div>
      ))}

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000',
        }}
      >
        聊天都覺得對方也喜歡你
      </motion.div>
    </main>
  );
}
```

### Ch6Step4 — AI 得分曲線爬升

```jsx
import { motion } from 'motion/react';

export default function Ch6Step4() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Persisted 新女生 sticker on left */}
      <div style={{
        background: '#FFB6C1', color: '#000',
        padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
        fontWeight: 900, fontSize: '1.5rem', transform: 'rotate(-4deg)', lineHeight: 1.3,
        textAlign: 'center',
      }}>
        剛認識的<br/>新女生 ✨
      </div>

      {/* SVG curve climbing */}
      <svg viewBox="0 0 400 240" width="500" height="300" style={{ overflow: 'visible' }}>
        {/* axis */}
        <line x1="20" y1="220" x2="380" y2="220" stroke="#000" strokeWidth="3" />
        <line x1="20" y1="220" x2="20" y2="20" stroke="#000" strokeWidth="3" />

        {/* climbing curve */}
        <motion.path
          d="M 20 200 L 80 180 L 140 140 L 200 90 L 260 50 L 380 40"
          fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, ease: 'easeOut' }}
        />

        {/* +/+/+ markers on curve */}
        {[
          { x: 80, y: 180 }, { x: 140, y: 140 }, { x: 200, y: 90 }, { x: 260, y: 50 },
        ].map((p, i) => (
          <motion.text
            key={i}
            x={p.x} y={p.y - 10}
            fill="#10B981" fontFamily="Space Grotesk" fontSize="24" fontWeight="900"
            stroke="#000" strokeWidth="0.5"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.5 + i * 0.4, ease: [0.34, 1.56, 0.64, 1] }}
          >+</motion.text>
        ))}
      </svg>
    </main>
  );
}
```

### Ch6Step5 — 卡平段 · 不思進取

```jsx
import { motion } from 'motion/react';

export default function Ch6Step5() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      gap: 64, fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 新女生 sticker grayscale fade */}
      <motion.div
        initial={{ filter: 'grayscale(0)' }}
        animate={{ filter: 'grayscale(1)', opacity: 0.5 }}
        transition={{ duration: 1.0 }}
        style={{
          background: '#FFB6C1', color: '#000',
          padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '1.5rem', transform: 'rotate(-4deg)', lineHeight: 1.3,
          textAlign: 'center',
        }}
      >
        剛認識的<br/>新女生 ✨
      </motion.div>

      {/* Curve with red flat-section highlight band */}
      <div style={{ position: 'relative' }}>
        <svg viewBox="0 0 400 240" width="500" height="300" style={{ overflow: 'visible' }}>
          <line x1="20" y1="220" x2="380" y2="220" stroke="#000" strokeWidth="3" />
          <line x1="20" y1="220" x2="20" y2="20" stroke="#000" strokeWidth="3" />

          {/* flat-section red band */}
          <motion.rect
            x="240" y="45" width="140" height="50" fill="#FF6B6B"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.4 }}
            transition={{ duration: 0.5 }}
          />

          <path
            d="M 20 200 L 80 180 L 140 140 L 200 90 L 260 50 L 380 50"
            fill="none" stroke="#000" strokeWidth="4" strokeLinecap="square"
          />
        </svg>

        <motion.div
          initial={{ x: 40, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          style={{
            position: 'absolute', top: '20%', right: -180,
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 200, lineHeight: 1.3,
          }}
        >
          拿固定分數 ·<br/>
          <span style={{ background: '#FF6B6B', color: '#FFF', padding: '2px 12px', border: '3px solid #000' }}>
            不思進取
          </span>
        </motion.div>
      </div>

      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 700, fontSize: '1.25rem', color: '#666',
        }}
      >
        一直沒辦法完整解出一道題
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch6.jsx STEPS to include `2: Ch6Step2, 3: Ch6Step3, 4: Ch6Step4, 5: Ch6Step5`

- [ ] Build + commit: `feat(demo): ch6 s2-s5 套皮仔/新女生/曲線/卡平段 (first girl-new motif)`

---

## Task 3: Ch6Step6 ★★★ 備胎 — full A+B+C+E+G climax (most complex)

**Files:**
- Create: `Ch6Step6.jsx`
- Modify: `Ch6.jsx`

Beat structure (3-beat, full ★★★ climax — first time A+B+C+E+G all fire together):
- beatIndex 0: 黑色 flash 100ms
- beatIndex 1: 紅底空 sticker + 副標「看似有進展 · 結果什麼都沒發生」
- beatIndex 2: 「備胎」mask-reveal 填入 + 整套 A+B+C+E+G + 紅 stamp scale overshoot

- [ ] **Step 1: Create `Ch6Step6.jsx`**

```jsx
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

export default function Ch6Step6() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'E', 'G']);
  const firedRef = useRef(false);
  const [blackFlash, setBlackFlash] = useState(false);

  // Beat 0: black flash 100ms
  useEffect(() => {
    if (beatIndex === 0) {
      setBlackFlash(true);
      const t = setTimeout(() => setBlackFlash(false), 100);
      return () => clearTimeout(t);
    }
  }, [beatIndex]);

  // Beat 2 climax — full A+B+C+E+G
  useEffect(() => {
    if (beatIndex === 2 && !firedRef.current) {
      firedRef.current = true;
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
      {/* Black flash overlay */}
      {blackFlash && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 60, background: '#000', pointerEvents: 'none',
        }} />
      )}

      {/* Climax overlays — only render when beatIndex 2 + climax fires */}
      <SpotlightVignette active={climax.activeFX.G} />
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="50%" />
      <InkSplatter active={climax.activeFX.E} count={8} radius={160} centerX="50%" centerY="50%" />

      {/* Beat 1+ red placeholder + fill on beat 2 */}
      <motion.div
        animate={beatIndex === 2
          ? { scale: [0.85, 1.4, 1.0, 0.95, 1.0] }
          : { scale: beatIndex >= 1 ? 1 : 0 }}
        transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ position: 'relative', zIndex: 50 }}
      >
        <div style={{
          background: '#FF6B6B',
          color: beatIndex >= 2 ? '#FFFDF5' : 'transparent',
          padding: '64px 128px',
          border: '6px solid #FFFDF5',
          boxShadow: '20px 20px 0 0 #000',
          fontWeight: 900, fontSize: '8rem', lineHeight: 1,
          letterSpacing: '0.2em', rotate: -3,
          minWidth: 600, minHeight: 200, textAlign: 'center',
        }}>
          {beatIndex >= 2 ? '備胎' : '  '}
        </div>
      </motion.div>

      {/* Beat 1+ subtitle below */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5, delay: beatIndex === 1 ? 0.2 : 0 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000', zIndex: 50, position: 'relative',
        }}
      >
        看似有進展 · 結果什麼都沒發生
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Update Ch6.jsx STEPS to add `6: Ch6Step6`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch6 s6 備胎 ★★★ punchline (full A+B+C+E+G climax)`

---

## Task 4: Ch6Step7 — 偷吃步 + Checkpoint

**Files:**
- Create: `Ch6Step7.jsx`
- Modify: `Ch6.jsx`

```jsx
import { motion } from 'motion/react';
import { RedStamp } from '../../motifs/RedStamp.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch6Step7() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          <motion.div
            initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
            animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
            style={{
              fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.5, maxWidth: 1200,
            }}
          >
            <Sticker variant="kicker" bg="#FF6B6B" color="#FFF">計分標準寫錯了</Sticker>
            <br/>
            <div style={{ marginTop: 16, display: 'inline-block' }}>
              <Sticker variant="kicker" bg="#FFD93D">AI 就會找漏洞作弊</Sticker>
            </div>
          </motion.div>
        </HubSatellite.Hub>

        <HubSatellite.Satellite position="tl">
          <RedStamp active rotation={-8} size="medium">偷吃步</RedStamp>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

- [ ] Update Ch6.jsx STEPS to add `7: Ch6Step7`

- [ ] Build + commit: `feat(demo): ch6 s7 偷吃步 · 找漏洞作弊`

- [ ] `git tag phase-6-ch6-complete`

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 我又錯了 ★ punchline** 3-beat: 字幕「正當我以為成了套皮仔⋯⋯」+ crash-line placeholder + click 填「⋯⋯我又錯了」+ 紅邊 flash + 螢幕震
- [ ] **s2 套皮仔策略**: 左紫「社群現成 Python 工具箱」+ 右白「填對一格給分」card + +1 浮現
- [ ] **s3 新女生加分**: 粉紅 sticker「剛認識的新女生 ✨」+ 持續綠色 + 符號從下浮起
- [ ] **s4 曲線爬升**: 左持續粉紅 sticker、右 SVG 曲線從 0 爬升 + 沿線 +/+/+ stagger 點亮
- [ ] **s5 卡平段**: 新女生 sticker grayscale 漸變、曲線卡平段紅色帶 highlight、「拿固定分數 · 不思進取」副標
- [ ] **s6 備胎 ★★★ punchline** 3-beat:
  - beat 0: 黑色閃一下
  - beat 1: 中央紅底空白 sticker + 副標「看似有進展 · 結果什麼都沒發生」
  - beat 2: 「備胎」mask-reveal + **同時 fire**: 螢幕震、邊緣 spotlight 暗化、中央 halftone burst、8 個 ink splatter 墨點、紅 stamp overshoot
- [ ] **s7 偷吃步**: 左上紅「偷吃步」stamp + 中央「計分標準寫錯了 → AI 找漏洞作弊」hero

## 想問你的回饋的點

1. **s3 新女生 sticker**：用 ✨ emoji + 粉紅底 + lineHeight 1.3 多行 — 視覺夠「新鮮 / 心動」感嗎？要不要換 SVG 線稿心形 / 笑臉？
2. **s4 曲線**：viewBox 400×240、6 個 anchor points 模擬「快速上升」 — 曲度自然嗎？需要更陡 / 平滑？
3. **s5 grayscale 漸變 1s**：粉紅 sticker 變灰的時機 OK 嗎？太快 / 太慢？
4. **s6 ★★★ 5 個 FX 同時 fire** — 在 sandbox 看了你覺得太雜、但這是 ch6 最大笑點 = 全套合理。實際走完 step 6 看起來如何？是否需要改 staging（per ★★★ 重新設計提案）？
5. **「備胎」字體 8rem + letter-spacing 0.2em** — 夠衝擊嗎？要不要再放大?

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
