# Phase 9 · Chapter 9 (callback) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>` (parent provides), `<HubSatellite>` (hub + named-anchor satellites) and `<Sticker variant="hub-md|hub-lg|hub-mega|sat-lg|sat-md|sat-sm|kicker">` from `src/components/`. Inline `position: 'absolute'` + hard-coded `%` offsets are PROHIBITED in step files (motif components are exempt — `HalftoneBurst`, `InkSplatter`, `SpotlightVignette`, etc. continue to use viewport-relative positioning). JSX snippets in this plan that follow the hub+satellite or sticker pattern have been pre-translated; snippets for other layouts (split-screen, charts, etc.) are illustrative — translate them to primitive calls when executing. See [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) for tokens, variant table, and acceptance criteria.

**Goal:** Build ch9 callback — final chapter, longest, 13 steps, ~204s. Mostly motif callbacks (girl-new, girl-veteran, 13-stairs, flip-20-to-50, crash-line, boom-double-ring) plus tensorboard real screenshots. 3 punchlines: s5 (戀愛 a callback light A+C), **s11 ★★ 警語**「人生第一次的外向 · 換來一輩子的內向」(A+C+G), **s13 ★★★ 電費小偷 final** (A+B+C+E+G + boom-ring 首尾呼應 ch1 s8).

**Source spec:** [outline.md §9](../../../demo/outline.md) · script.md L303-L375

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch9
└── ch9-callback/
    ├── Ch9.jsx
    ├── Ch9Step1.jsx                        # tensorboard + 磨合期 (real images TODO)
    ├── Ch9Step2.jsx                        # 核心金句 hero-mega
    ├── Ch9Step3.jsx                        # RL 對等
    ├── Ch9Step4.jsx                        # 飛機 + 鳥
    ├── Ch9Step5.jsx                        # 戀愛 a callback ★ 4-beat
    ├── Ch9Step6.jsx                        # 戀愛 b 4 考題
    ├── Ch9Step7.jsx                        # plasticity 引出
    ├── Ch9Step8.jsx                        # plasticity 三欄
    ├── Ch9Step9.jsx                        # plasticity 機制
    ├── Ch9Step10.jsx                       # MBTI + 業務工作（複合兩拍）
    ├── Ch9Step11.jsx                       # 警語 ★★ 4-beat A+C+G
    ├── Ch9Step12.jsx                       # 職場祝福
    └── Ch9Step13.jsx                       # 電費小偷 ★★★ 4-beat + boom-ring callback
```

---

## Task 1: Register Ch9 + Steps 1-4 batched (tensorboard, 核心金句, RL 對等, 飛機+鳥)

- [ ] Update `src/chapters/index.jsx` — `9: Ch9`

- [ ] Create `Ch9.jsx` with empty STEPS (filled in batches):

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';

const STEPS = {};

export function Ch9() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 9 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

### Ch9Step1 — tensorboard + 磨合期 (real PNG screenshots TODO)

Per asset-production.md ch9: tensorboard screenshots should be exported to `demo/presentation/public/images/tensorboard/`. **TODO entry in TODO.md** required (image files not yet available). Use `<AssetPlaceholder>` for now.

```jsx
import { motion } from 'motion/react';
import { AssetPlaceholder } from '../../components/AssetPlaceholder.jsx';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step1() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        AI 還在訓練中⋯⋯<span style={{ color: '#000', fontWeight: 900 }}>我跟對方還在磨合期</span>
      </motion.div>

      <HubSatellite>
        <HubSatellite.Hub>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1.0 }}
              style={{ fontWeight: 700, fontSize: '1.25rem' }}
            >
              但你可以看到 ·{' '}
              <Sticker variant="kicker" bg="#FFD93D">AI 是有在進步的</Sticker>
            </motion.div>

            <motion.div
              initial={{ scale: 0.85, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.9, delay: 1.4, ease: [0.34, 1.56, 0.64, 1] }}
            >
              <Sticker variant="hub-lg" bg="#000" color="#FFFDF5">
                最後我想跟大家講一件事
              </Sticker>
            </motion.div>
          </div>
        </HubSatellite.Hub>

        <HubSatellite.Satellite position="l">
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            style={{ border: '6px solid #000', boxShadow: '12px 12px 0 0 #000', padding: 4, background: '#FFF' }}
          >
            <AssetPlaceholder type="[✓]" width={420} height={260} todo="success_rate 曲線截圖 (export from tensorboard, save to public/images/tensorboard/success-rate.png)" />
          </motion.div>
        </HubSatellite.Satellite>
        <HubSatellite.Satellite position="r">
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            style={{ border: '6px solid #000', boxShadow: '12px 12px 0 0 #000', padding: 4, background: '#FFF' }}
          >
            <AssetPlaceholder type="[✓]" width={420} height={260} todo="curriculum target_empty 截圖 (save to public/images/tensorboard/curriculum-target-empty.png)" />
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

Also append to `TODO.md`:
```markdown
- ch9 s1 — [✓] tensorboard 真截圖 — 待匯出至 demo/presentation/public/images/tensorboard/{success-rate,curriculum-target-empty}.png
```

### Ch9Step2 — 核心金句

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step2() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 16,
    }}>
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0, letterSpacing: '0.05em' }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1, letterSpacing: '0em' }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', textAlign: 'center', lineHeight: 1.3,
          color: '#FF6B6B',
        }}
      >
        這兩個月
        <br/>
        我不只在訓練 AI
      </motion.div>

      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.4, ease: [0.34, 1.56, 0.64, 1] }}
      >
        <Sticker variant="hub-mega" bg="#FF6B6B" color="#FFFDF5" rotation={-2}>
          AI · 也在訓練我
        </Sticker>
      </motion.div>
    </main>
  );
}
```

### Ch9Step3 — RL 對等

```jsx
import { motion } from 'motion/react';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step3() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      fontFamily: 'Space Grotesk', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
    }}>
      <HubSatellite>
        <HubSatellite.Hub>
          {/* "=" yellow circle stamp */}
          <motion.div
            initial={{ scale: 0, rotate: 0 }}
            animate={{ scale: 1, rotate: -10 }}
            transition={{ duration: 0.5, delay: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
            style={{
              background: '#FFD93D', color: '#000',
              width: 120, height: 120, borderRadius: '50%',
              border: '8px solid #000', boxShadow: '12px 12px 0 0 #000',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 900, fontSize: 64,
            }}
          >
            =
          </motion.div>
        </HubSatellite.Hub>

        <HubSatellite.Satellite position="l">
          {/* brain (RL 腦科學) */}
          <motion.div
            initial={{ clipPath: 'inset(0 100% 0 0)' }}
            animate={{ clipPath: 'inset(0 0 0 0)' }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            <Sticker variant="hub-lg" bg="#000" color="#FFFDF5">
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                <div style={{ fontSize: 96 }}>🧠</div>
                <div style={{ fontWeight: 900, fontSize: '2rem' }}>腦科學 RL</div>
              </div>
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>

        <HubSatellite.Satellite position="r">
          {/* neural net (AI 訓練) */}
          <motion.div
            initial={{ clipPath: 'inset(0 0 0 100%)' }}
            animate={{ clipPath: 'inset(0 0 0 0)' }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          >
            <Sticker variant="hub-lg" bg="#FFFDF5">
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
                <div style={{ fontSize: 96 }}>🕸️</div>
                <div style={{ fontWeight: 900, fontSize: '2rem' }}>AI 訓練 RL</div>
              </div>
            </Sticker>
          </motion.div>
        </HubSatellite.Satellite>

        <HubSatellite.Satellite position="b">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.0 }}
            style={{ fontWeight: 900, fontSize: '2.5rem', textAlign: 'center' }}
          >
            其實是 <Sticker variant="kicker" bg="#FFD93D">同一件事</Sticker>
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>
    </div>
  );
}
```

### Ch9Step4 — 飛機 + 鳥

```jsx
import { motion } from 'motion/react';
import { HubSatellite } from '../../components/HubSatellite.jsx';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step4() {
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
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center', marginBottom: 32 }}
      >
        AI 在<Sticker variant="kicker" bg="#FFD93D">模仿</Sticker>人類
      </motion.div>

      <HubSatellite>
        <HubSatellite.Hub>
          {/* arrow ← in the middle */}
          <motion.svg
            width="120" height="40" viewBox="0 0 120 40"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            style={{ overflow: 'visible' }}
          >
            <motion.path
              d="M 10 20 L 20 10 L 10 20 L 110 20 L 100 30 L 110 20 L 100 10"
              fill="none" stroke="#000" strokeWidth="6" strokeLinecap="square"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.6, delay: 0.7 }}
            />
          </motion.svg>
        </HubSatellite.Hub>

        <HubSatellite.Satellite position="l">
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            style={{ fontSize: 200 }}
          >
            ✈️
          </motion.div>
        </HubSatellite.Satellite>

        <HubSatellite.Satellite position="r">
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1, y: [0, -6, 0] }}
            transition={{
              x: { duration: 0.5, delay: 0.4 },
              opacity: { duration: 0.5, delay: 0.4 },
              y: { duration: 1.2, repeat: Infinity, ease: 'easeInOut', delay: 1 },
            }}
            style={{ fontSize: 200 }}
          >
            🐦
          </motion.div>
        </HubSatellite.Satellite>
      </HubSatellite>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.2 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666', textAlign: 'center', marginTop: 32 }}
      >
        就像飛機 · 是人類模仿鳥類才造出來
      </motion.div>
    </div>
  );
}
```

- [ ] Update Ch9.jsx STEPS to add `1: Ch9Step1, 2: Ch9Step2, 3: Ch9Step3, 4: Ch9Step4`
- [ ] Build + commit: `feat(demo): ch9 s1-s4 tensorboard / 金句 / RL = / 飛機鳥`

---

## Task 2: Ch9Step5 — 戀愛 a callback ★ 4-beat (girl-new callback)

Beat structure:
- beatIndex 0: girl-new motif from ch6 fades into background (grayscale, opacity 0.3) + brain icon stamp center
- beatIndex 1: 左欄「回訊息」green + + + spawn
- beatIndex 2: 右欄「已讀不回」red - - - spawn
- beatIndex 3: 紅底 hero「跟 AI 訓練一模一樣」mask-reveal + climax A+C

```jsx
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';

export default function Ch9Step5() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);
  const [pluses, setPluses] = useState([]);
  const [minuses, setMinuses] = useState([]);

  useEffect(() => {
    if (beatIndex >= 1) {
      let id = 0;
      const t = setInterval(() => {
        setPluses(p => [...p, { id: id++, x: Math.random() * 40 + 10 }].slice(-10));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex >= 2) {
      let id = 0;
      const t = setInterval(() => {
        setMinuses(m => [...m, { id: id++, x: Math.random() * 40 + 50 }].slice(-10));
      }, 350);
      return () => clearInterval(t);
    }
  }, [beatIndex]);

  useEffect(() => {
    if (beatIndex === 3 && !firedRef.current) {
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
      {/* Beat 0+ background girl-new callback (grayscale ghost) */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { opacity: 0.3 } : { opacity: 0 }}
        transition={{ duration: 0.6 }}
        style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          filter: 'grayscale(1)',
          pointerEvents: 'none',
        }}
      >
        <div style={{
          background: '#FFB6C1', color: '#000',
          padding: '32px 56px', border: '6px solid #000', boxShadow: '14px 14px 0 0 #000',
          fontWeight: 900, fontSize: '2.5rem', transform: 'rotate(-4deg)', lineHeight: 1.3,
          textAlign: 'center',
        }}>剛認識的<br/>新女生 ✨</div>
      </motion.div>

      {/* Beat 0+ brain center */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{ fontSize: 160, zIndex: 10 }}
      >
        🧠
      </motion.div>

      {/* Beat 1+ left positives */}
      {beatIndex >= 1 && (
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '5%', width: '40%' }}>
          <div style={{
            position: 'absolute', top: 80,
            fontWeight: 900, fontSize: 20, background: '#10B981', color: '#FFF',
            padding: '8px 20px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}>回訊息</div>
          {pluses.map(p => (
            <motion.div
              key={p.id}
              initial={{ y: 0, opacity: 1 }}
              animate={{ y: -400, opacity: 0 }}
              transition={{ duration: 2.5, ease: 'easeOut' }}
              style={{
                position: 'absolute', bottom: 0, left: `${p.x}%`,
                fontSize: 40, fontWeight: 900, color: '#10B981',
                WebkitTextStroke: '2px black',
              }}
            >+</motion.div>
          ))}
        </div>
      )}

      {/* Beat 2+ right negatives */}
      {beatIndex >= 2 && (
        <div style={{ position: 'absolute', top: 0, bottom: 0, right: '5%', width: '40%' }}>
          <div style={{
            position: 'absolute', top: 80, right: 0,
            fontWeight: 900, fontSize: 20, background: '#FF6B6B', color: '#FFF',
            padding: '8px 20px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}>已讀不回</div>
          {minuses.map(m => (
            <motion.div
              key={m.id}
              initial={{ y: -300, opacity: 1 }}
              animate={{ y: 400, opacity: 0 }}
              transition={{ duration: 2.5, ease: 'easeIn' }}
              style={{
                position: 'absolute', top: 0, right: `${m.x}%`,
                fontSize: 40, fontWeight: 900, color: '#FF6B6B',
                WebkitTextStroke: '2px black',
              }}
            >–</motion.div>
          ))}
        </div>
      )}

      {/* Beat 3 punchline */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3
          ? { scale: 1, opacity: 1, y: 0 }
          : { scale: 0.85, opacity: 0, y: 100 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: 64, left: 0, right: 0, textAlign: 'center',
          zIndex: 20,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
          fontWeight: 900, fontSize: '3.5rem', display: 'inline-block', rotate: -2,
        }}>
          跟 AI 訓練一模一樣
        </span>
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch9.jsx STEPS to add `5: Ch9Step5`
- [ ] Build + commit: `feat(demo): ch9 s5 戀愛 a callback ★ punchline (girl-new callback)`

---

## Task 3: Ch9Step6 ~ Ch9Step10 batched (4 考題 / plasticity 3 steps / MBTI)

### Ch9Step6 — 戀愛 b 4 考題 grid (girl-veteran callback)

```jsx
import { motion } from 'motion/react';

const QUESTIONS = [
  { text: '前女友跟我比 · 誰比較好？', bg: '#FFD93D', color: '#000', rotate: -2 },
  { text: '你心中的女神是誰？', bg: '#C4B5FD', color: '#000', rotate: 3 },
  { text: '你喜歡我哪裡？', bg: '#FF6B6B', color: '#FFFDF5', rotate: -3 },
  { text: '猜猜看 · 今天我哪裡不一樣？', bg: '#FFFDF5', color: '#000', rotate: 2 },
];

export default function Ch9Step6() {
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
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        以為穩了 · <span style={{ background: '#FF6B6B', color: '#FFF', padding: '4px 16px' }}>結果魔王關卡</span>
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 32 }}>
        {QUESTIONS.map((q, i) => (
          <motion.div
            key={i}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.4 + i * 0.15, ease: [0.34, 1.56, 0.64, 1] }}
            whileHover={{ scale: 1.1, boxShadow: '16px 16px 0 0 #000' }}
            style={{
              background: q.bg, color: q.color,
              padding: '28px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', maxWidth: 360,
              transform: `rotate(${q.rotate}deg)`, cursor: 'pointer',
              transition: 'box-shadow 0.2s, transform 0.2s',
            }}
          >
            {q.text}
          </motion.div>
        ))}
      </div>
    </main>
  );
}
```

### Ch9Step7 — plasticity 引出

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step7() {
  return (
    <div style={{
      position: 'relative', zIndex: 20, height: '100%',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', gap: 16,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        最後再跟大家分享
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '5rem', textAlign: 'center', lineHeight: 1.3,
        }}
      >
        大腦可塑性
        <br/>
        <motion.span
          initial={{ letterSpacing: '0.3em', opacity: 0 }}
          animate={{ letterSpacing: '0.05em', opacity: 1 }}
          transition={{ duration: 1, delay: 1.2 }}
          style={{ display: 'inline-block', marginTop: 16 }}
        >
          <Sticker variant="hub-lg" bg="#C4B5FD">plasticity</Sticker>
        </motion.span>
      </motion.div>
    </div>
  );
}
```

### Ch9Step8 — plasticity 三欄 (13-stairs callback in background, grayscale)

```jsx
import { motion } from 'motion/react';

export default function Ch9Step8() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      {/* Background callback: faint 13-stairs grid (mini tile pattern) */}
      <div
        aria-hidden="true"
        style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          opacity: 0.08, filter: 'grayscale(1)',
          backgroundImage: 'radial-gradient(#000 2px, transparent 2.5px)',
          backgroundSize: '20px 20px',
        }}
      />

      <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start', marginBottom: 32 }}>
        {[
          { label: '解數獨', sub: 'AI 沒天生會 ·', color: '#FF6B6B', textColor: '#FFF' },
          { label: '講話', sub: '你 出生不會 ·', color: '#FFD93D', textColor: '#000' },
          { label: '跟人相處', sub: '你 不是天生會 ·', color: '#C4B5FD', textColor: '#000' },
        ].map((col, i) => (
          <motion.div
            key={i}
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.2 }}
            style={{
              background: col.color, color: col.textColor,
              padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
              fontWeight: 900, fontSize: 24, textAlign: 'center', minWidth: 200,
            }}
          >
            <div style={{ fontSize: 18, marginBottom: 8 }}>{col.sub}</div>
            <div style={{ fontSize: 32 }}>{col.label}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          fontWeight: 900, fontSize: '8rem',
          background: '#FFFDF5', color: '#000',
          padding: '24px 64px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
          rotate: -2,
        }}
      >
        一樣
      </motion.div>
    </main>
  );
}
```

### Ch9Step9 — plasticity 機制 (flip-20-to-50 background loop, grayscale)

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step9() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      {/* Background: flipping +20/+50 callback at opacity 0.06 */}
      <motion.div
        aria-hidden="true"
        animate={{ rotateY: [0, 360] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        style={{
          position: 'absolute', inset: 0, opacity: 0.06,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          filter: 'grayscale(1)', pointerEvents: 'none',
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '20rem' }}>+50</div>
      </motion.div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontWeight: 700, fontSize: '1.5rem', color: '#666' }}>
        {['每改一次 reward function', '每談一場戀愛', '每學一個新東西'].map((line, i) => (
          <motion.div
            key={i}
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.4, delay: 0.3 + i * 0.24 }}
          >
            · {line}
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 1.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        每次都把我們
        <br/>
        <div style={{ display: 'inline-block', marginTop: 16 }}>
          <Sticker variant="hub-md" bg="#FFD93D">重新塑造一次</Sticker>
        </div>
      </motion.div>
    </main>
  );
}
```

### Ch9Step10 — MBTI + 業務工作（複合兩拍）

Auto-trigger phase 2 after 9s (via setTimeout).

```jsx
import { motion } from 'motion/react';
import { useEffect, useState } from 'react';

export default function Ch9Step10() {
  const [phase, setPhase] = useState(1);

  useEffect(() => {
    const t = setTimeout(() => setPhase(2), 9000);
    return () => clearTimeout(t);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 900, fontSize: '2rem' }}
      >
        我真的是一個 <span style={{ background: '#C4B5FD', padding: '0 16px', border: '4px solid #000' }}>極度的 I 人</span>
      </motion.div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 48, marginTop: 24 }}>
        {/* MBTI Pie chart — phase 1 full 100% I, phase 2 shrinks to side */}
        <motion.svg
          animate={{ width: phase === 1 ? 240 : 120, height: phase === 1 ? 240 : 120 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          viewBox="0 0 100 100"
          style={{ flex: '0 0 auto' }}
        >
          <circle cx="50" cy="50" r="45" fill="#FFFDF5" stroke="#000" strokeWidth="6" />
          {phase === 1 ? (
            <motion.circle
              cx="50" cy="50" r="45" fill="#C4B5FD" stroke="#000" strokeWidth="6"
              initial={{ strokeDasharray: '0 283', strokeDashoffset: 0 }}
              animate={{ strokeDasharray: '283 0', strokeDashoffset: 0 }}
              transition={{ duration: 1.5 }}
              style={{ transformOrigin: 'center', transform: 'rotate(-90deg)' }}
            />
          ) : (
            // Phase 2: 30% I (purple), 70% E? — represent as partial pie
            <path d="M 50 5 A 45 45 0 0 1 90 65 L 50 50 Z" fill="#C4B5FD" stroke="#000" strokeWidth="6" />
          )}
          <text x="50" y="55" textAnchor="middle" fontWeight="900" fontSize="24" fontFamily="Space Grotesk">
            I {phase === 1 ? '100%' : '30%'}
          </text>
        </motion.svg>

        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.6, ease: [0.34, 1.56, 0.64, 1] }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '24px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: 28, rotate: -3,
          }}
        >
          極度 I 人
        </motion.div>

        {/* Phase 2 only: 業務工作 sticker + I→E bar */}
        {phase === 2 && (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
              style={{
                background: '#FFD93D', color: '#000',
                padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
                fontWeight: 900, fontSize: 28, rotate: 2,
              }}
            >
              業務工作
            </motion.div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ position: 'relative', width: 280, height: 40, background: '#FFFDF5', border: '4px solid #000' }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '30%', background: '#C4B5FD' }} />
                <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: '40%', background: '#FF6B6B' }} />
                <motion.div
                  initial={{ left: '0%' }}
                  animate={{ left: '60%' }}
                  transition={{ duration: 4, ease: 'easeInOut' }}
                  style={{
                    position: 'absolute', top: -4, width: 12, height: 48,
                    background: '#000', border: '2px solid #FFFDF5',
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: 14 }}>
                <span>I 0%</span><span>E 100%</span>
              </div>
            </div>
          </>
        )}
      </div>

      {phase === 1 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 2.0 }}
          style={{ fontWeight: 700, fontSize: '1.5rem' }}
        >
          <span style={{ background: '#FFD93D', padding: '2px 12px', border: '4px solid #000' }}>明明我很 E</span>
        </motion.div>
      )}

      {phase === 2 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', textAlign: 'center', marginTop: 16 }}
        >
          天天逼自己跟陌生人講話 · 才慢慢變得比較 E
        </motion.div>
      )}
    </main>
  );
}
```

- [ ] Update Ch9.jsx STEPS to add `6: Ch9Step6, 7: Ch9Step7, 8: Ch9Step8, 9: Ch9Step9, 10: Ch9Step10`
- [ ] Build + commit: `feat(demo): ch9 s6-s10 4 考題 / plasticity 引出/三欄/機制 / MBTI 複合`

---

## Task 4: Ch9Step11 ★★ 警語 4-beat (crash-line 放大版 + A+C+G)

Beat structure:
- beat 0: kicker「從挫敗中學習就行了」+ halftone 加密 + crash-line 空框 (cream + 6px 紅邊 + 閃爍游標)
- beat 1: 副標「但是不要停滯不前」
- beat 2: warn-line-a 填上半「人生第一次的外向」（red 大字 mask-reveal）+ 紅邊 flash 1×
- beat 3: warn-line-b 填下半「· 換來一輩子的內向」+ A+C+G climax (spotlight 警語性質)

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';

export default function Ch9Step11() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C', 'G']);
  const firedRef = useRef(false);

  useEffect(() => {
    if (beatIndex === 3 && !firedRef.current) {
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
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <SpotlightVignette active={climax.activeFX.G} />

      {/* Beat 0+ kicker + halftone densify */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '1.75rem', color: '#000',
        }}
      >
        從挫敗中學習就行了
      </motion.div>
      {beatIndex >= 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.3 }}
          transition={{ duration: 0.4 }}
          style={{
            position: 'fixed', inset: 0, zIndex: 6, pointerEvents: 'none',
            backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
            backgroundSize: '12px 12px',
          }}
        />
      )}

      {/* Beat 0+ crash-line frame (bigger version: 6px red border + scale 1.3 on beat 3) */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0
          ? { scale: beatIndex === 3 ? [1, 1.3, 1] : 1, opacity: 1 }
          : { scale: 0.9, opacity: 0 }}
        transition={{ duration: beatIndex === 3 ? 0.6 : 0.3, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFDF5', color: '#FF6B6B',
          border: '6px solid #FF6B6B',
          boxShadow: beatIndex === 3 ? '20px 20px 0 0 #000' : '12px 12px 0 0 #000',
          padding: '48px 80px', minWidth: 800, minHeight: 240,
          textAlign: 'center', rotate: -2,
          position: 'relative', zIndex: 30,
        }}
      >
        <div style={{ fontWeight: 900, fontSize: '3.5rem', lineHeight: 1.3 }}>
          {/* Beat 2+ first line */}
          {beatIndex >= 2 ? (
            <motion.span
              initial={{ clipPath: 'inset(0 100% 0 0)' }}
              animate={{ clipPath: 'inset(0 0 0 0)' }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              人生第一次的外向
            </motion.span>
          ) : (
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, ease: 'steps(2)' }}
            >_</motion.span>
          )}
          <br/>
          {/* Beat 3+ second line */}
          {beatIndex >= 3 && (
            <motion.span
              initial={{ clipPath: 'inset(0 100% 0 0)' }}
              animate={{ clipPath: 'inset(0 0 0 0)' }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
            >
              · 換來一輩子的內向
            </motion.span>
          )}
        </div>
      </motion.div>

      {/* Beat 1+ subtitle */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', bottom: 80,
          fontWeight: 900, fontSize: '1.5rem',
        }}
      >
        但是<span style={{ background: '#FF6B6B', color: '#FFF', padding: '2px 12px', border: '4px solid #000' }}>不要停滯不前</span>
      </motion.div>
    </main>
  );
}
```

- [ ] Update Ch9.jsx STEPS to add `11: Ch9Step11`
- [ ] Build + commit: `feat(demo): ch9 s11 ★★ 警語 (crash-line 放大版 + A+C+G)`

---

## Task 5: Ch9Step12 + Ch9Step13 (職場祝福 + 電費小偷 ★★★ final)

### Ch9Step12 — 職場祝福

```jsx
import { motion } from 'motion/react';
import { Sticker } from '../../components/Sticker.jsx';

export default function Ch9Step12() {
  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', color: '#666' }}
      >
        繼續嘗試跟其他女生聊天
      </motion.div>

      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.0, delay: 0.4, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.4,
        }}
      >
        祝大家未來在職場上
        <br/>
        <div style={{ display: 'inline-block', marginTop: 16 }}>
          <Sticker variant="hub-md" bg="#FF6B6B" color="#FFFDF5" rotation={-2}>
            不被挫敗給擊敗
          </Sticker>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.6 }}
        style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', marginTop: 16 }}
      >
        不是每個女生都那麼老油條
      </motion.div>
    </main>
  );
}
```

### Ch9Step13 ★★★ 電費小偷 final (full A+B+C+E+G + boom-ring callback)

Beat structure (4-beat — peak climax of entire show):
- beat 0: kicker「最後再補個笑話」
- beat 1: 中央上「想必大家未來出職場後都是 · 薪水小偷」黑底 sticker + 中央下「我不一樣 → ?」cream 泡泡 placeholder
- beat 2: 「我不一樣 → ?」泡泡 morph → 「但我不一樣 · 我是 電費小偷」紅底 FINAL stamp + 全套 A+B+C+E+G + **motif/boom-double-ring 縮小化雙圈圍邊** (首尾呼應 ch1 s8)
- beat 3: 底部 footer「我這兩個月一直用班上的電腦瘋狂訓練我的 AI」字逐字打字 + 右下「— END —」

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { BoomDoubleRing } from '../../motifs/BoomDoubleRing.jsx';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

const FOOTER_TEXT = '我這兩個月一直用班上的電腦 · 瘋狂訓練我的 AI';

export default function Ch9Step13() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'B', 'C', 'E', 'G']);
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
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <SpotlightVignette active={climax.activeFX.G} />
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="55%" size={800} />
      <InkSplatter active={climax.activeFX.E} count={8} radius={200} centerX="50%" centerY="55%" />

      {/* Beat 0+ kicker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: -20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 64,
          fontWeight: 700, fontSize: '1.5rem', color: '#666',
        }}
      >
        最後再補個笑話 ⋯
      </motion.div>

      {/* Beat 1+ salary-thief sticker */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { scale: 1, opacity: 1 } : { scale: 0.85, opacity: 0 }}
        transition={{ duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#000', color: '#FFFDF5',
          padding: '20px 36px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '1.75rem', rotate: 2,
        }}
      >
        想必大家未來出職場後都是 · 薪水小偷
      </motion.div>

      {/* Beat 2+: morph from placeholder "我不一樣 → ?" → FINAL "電費小偷" stamp */}
      <div style={{ position: 'relative', zIndex: 30 }}>
        {/* boom-ring callback wrap when beat >= 2 — small size for visual rhyme with ch1 s8 */}
        {beatIndex >= 2 && (
          <div style={{
            position: 'absolute', left: '50%', top: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: -1,
          }}>
            <BoomDoubleRing active size={520} />
          </div>
        )}

        <motion.div
          animate={beatIndex === 2
            ? { scale: [0.85, 1.5, 1.0, 0.95, 1.0] }
            : { scale: beatIndex >= 1 ? 1 : 0 }}
          transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <div style={{
            background: beatIndex >= 2 ? '#FF6B6B' : '#FFFDF5',
            color: beatIndex >= 2 ? '#FFFDF5' : '#000',
            padding: '40px 72px', border: '8px solid #000', boxShadow: '20px 20px 0 0 #000',
            fontWeight: 900, fontSize: beatIndex >= 2 ? '5rem' : '2.25rem', rotate: -3, lineHeight: 1.2,
            textAlign: 'center', minWidth: 480,
            transition: 'background 0.3s, color 0.3s, font-size 0.3s',
          }}>
            {beatIndex >= 2 ? (
              <>
                但我不一樣 · 我是
                <br/>
                電費小偷
              </>
            ) : (
              <>我不一樣 → <span style={{ color: '#FF6B6B' }}>?</span></>
            )}
          </div>
        </motion.div>
      </div>

      {/* Beat 3+ footer type-in + END */}
      {beatIndex >= 3 && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            style={{
              position: 'absolute', bottom: 96,
              fontWeight: 700, fontSize: '1.25rem', color: '#000',
              textAlign: 'center', maxWidth: 800,
            }}
          >
            <TypeIn text={FOOTER_TEXT} duration={1.5} />
          </motion.div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 2.0 }}
            style={{
              position: 'absolute', bottom: 32, right: 32,
              fontWeight: 900, fontSize: 20, color: '#000', letterSpacing: '0.2em',
            }}
          >
            — END —
          </motion.div>
        </>
      )}
    </main>
  );
}

function TypeIn({ text, duration = 1.5 }) {
  // Render characters with stagger via clipPath
  return (
    <motion.span
      initial={{ clipPath: 'inset(0 100% 0 0)' }}
      animate={{ clipPath: 'inset(0 0 0 0)' }}
      transition={{ duration, ease: 'linear' }}
      style={{ display: 'inline-block' }}
    >
      {text}
    </motion.span>
  );
}
```

- [ ] Update Ch9.jsx STEPS to add `12: Ch9Step12, 13: Ch9Step13`
- [ ] Build + commit: `feat(demo): ch9 s12 職場祝福 + s13 ★★★ 電費小偷 final (full climax + boom-ring callback)`
- [ ] `git tag phase-9-ch9-complete`

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 tensorboard + 磨合期**: 字幕「磨合期」、左右 tensorboard 截圖 placeholder（待匯出）、副標「但你可以看到 · AI 是有在進步的」、中央黑「最後我想跟大家講一件事」hero
- [ ] **s2 核心金句**: 「這兩個月 / 我不只在訓練 AI」mask-reveal、底下紅「AI · 也在訓練我」超大 hero stamp
- [ ] **s3 RL 對等**: 左黑面板「腦科學 RL 🧠」/ 中央黃「=」圓 stamp / 右白面板「AI 訓練 RL 🕸️」、底「其實是同一件事」
- [ ] **s4 飛機+鳥**: ✈️ ← 🐦、副標「就像飛機 · 是人類模仿鳥類才造出來」、鳥輕微振翅
- [ ] **s5 戀愛 a callback ★** 4-beat:
  - beat 0: 背景 girl-new sticker 灰階退入 + 中央 🧠 stamp
  - beat 1: 左欄「回訊息」 + 綠色 + + + 持續往上飄
  - beat 2: 右欄「已讀不回」 + 紅色 - - - 持續往下沉
  - beat 3 (click): 底部紅「跟 AI 訓練一模一樣」hero punchline + 螢幕震 + overshoot
- [ ] **s6 戀愛 b 4 考題**: 2×2 grid 4 個問題 sticker (黃/紫/紅/cream) stagger stamp、hover 放大 + shadow 加深
- [ ] **s7 plasticity 引出**: 「最後再跟大家分享」kicker、「大腦可塑性 / plasticity」hero (英文紫底高亮、letter-spacing 收緊)
- [ ] **s8 plasticity 三欄**: 3 個欄 stagger fade-up (AI 解數獨 / 出生會講話 / 跟人相處)、中央「一樣」cream 大字 stamp、背景淡灰色 13-stairs 痕跡
- [ ] **s9 plasticity 機制**: 3 項 stagger reveal（reward function / 戀愛 / 學新東西）、底「每次都把我們 / 重新塑造一次」hero (黃高亮)、背景 +50 灰階旋轉 loop
- [ ] **s10 MBTI + 業務工作** (composite):
  - phase 1 (0-9s): 圓餅 0→100% I 填滿、「極度 I 人」紫 sticker、「明明我很 E」黃高亮
  - phase 2 (9s 後 auto): 圓餅縮側、「業務工作」黃 sticker + I→E 漸變條 indicator 移動到 60%
- [ ] **s11 警語 ★★ punchline** 4-beat:
  - beat 0: 上方「從挫敗中學習就行了」kicker + halftone 加密 + crash-line 空框 (cream + 6px 紅邊 + 閃爍游標)
  - beat 1: 下方副標「但是不要停滯不前」
  - beat 2 (click): 框內上半填「人生第一次的外向」mask-reveal + 紅邊 flash
  - beat 3 (click): 框內下半填「· 換來一輩子的內向」+ 整框 scale 1.3 overshoot + spotlight 暗化 + 螢幕震
- [ ] **s12 職場祝福**: 「祝大家未來在職場上 / 不被挫敗給擊敗 (紅 stamp)」、底「不是每個女生都那麼老油條」副標
- [ ] **s13 電費小偷 ★★★ final** 4-beat:
  - beat 0: 上方「最後再補個笑話 ⋯」kicker
  - beat 1: 中央黑底「想必大家未來出職場後都是 · 薪水小偷」對位 sticker + 中央下「我不一樣 → ?」cream 泡泡 (placeholder)
  - beat 2 (click): 泡泡 morph → 紅底「但我不一樣 · 我是 / 電費小偷」FINAL stamp (5rem 超大) + 整套 A+B+C+E+G FX + **`motif/boom-double-ring` 圍邊 520px (首尾呼應 ch1 s8)** + 整屏震動 + ink splatter 8 點散開
  - beat 3 (click): 底部 footer「我這兩個月一直用班上的電腦 · 瘋狂訓練我的 AI」逐字打字 (1.5s)、右下「— END —」minimal footer

## 想問你的回饋的點

1. **tensorboard 截圖 placeholder (s1)** — 等我匯出真截圖前、用紅虛線 placeholder 看起來會醜嗎？要不要先用一張假的曲線 SVG 替代？
2. **s2 核心金句**: 用 5rem「這兩個月 / 我不只在訓練 AI」+ 6rem「AI · 也在訓練我」紅底 hero。階層感對嗎？要不要兩段都用相同字級？
3. **s3 emoji** 🧠 + 🕸️ + ✈️ + 🐦 全篇靠 emoji — 跟 Neo-brutalism cream + 黑邊風格搭嗎？要不要某些換成 Phosphor `Brain` / `GraphBranching` / `Airplane` icon?
4. **s5 戀愛 a callback** 背景 girl-new sticker 灰階 opacity 0.3 — 觀眾看得到「就是 ch6 的那個女生」嗎？要不要更明顯（opacity 0.5+）?
5. **s10 MBTI 圓餅切兩 phase auto trigger 9s 後**: phase 2 自動發、不用點擊。9s 等待時間 OK 嗎？演講者口播完該段需要 9-13s
6. **s11 ★★ 警語 crash-line 放大版**: 6px 紅邊 + scale 1.3 overshoot + spotlight 暗化。比 ch5 s1 ch6 s1 的 crash-line 版本更狂、能看出「警語級別」嗎？
7. **s13 ★★★ 電費小偷 final** — boom-double-ring 520px 圍邊在 stamp 外、首尾呼應 ch1 s8 BOOM。觀眾會記得 ch1 嗎？視覺呼應效果預計如何？
8. **s13 字級 5rem「電費小偷」** vs ch6 s6「備胎」8rem — final 應該比中段 ★★★ 更大嗎？要不要拉到 7rem?
9. **整片 9 章節走完的節奏**: ch9 13 step + 3 punchlines + 2 個 climax 高峰、是否最後一章太長？要不要剪掉某幾步?

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
