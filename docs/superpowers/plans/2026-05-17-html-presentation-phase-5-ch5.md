# Phase 5 · Chapter 5 (legacy) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development.

> **Layout primitives (mandatory):** all step JSX must compose via `<Stage>` (already present in `App.jsx`), `<SafeArea>` (parent provides), `<HubSatellite>` (hub + named-anchor satellites) and `<Sticker variant="hub-md|hub-lg|hub-mega|sat-lg|sat-md|sat-sm|kicker">` from `src/components/`. Inline `position: 'absolute'` + hard-coded `%` offsets are PROHIBITED in step files (motif components are exempt — `HalftoneBurst`, `InkSplatter`, `SpotlightVignette`, etc. continue to use viewport-relative positioning). JSX snippets in this plan that follow the hub+satellite or sticker pattern have been pre-translated; snippets for other layouts (split-screen, charts, etc.) are illustrative — translate them to primitive calls when executing. See [`docs/superpowers/specs/2026-05-17-presentation-layout-system-design.md`](../specs/2026-05-17-presentation-layout-system-design.md) for tokens, variant table, and acceptance criteria.

**Goal:** Build ch5 legacy — 天真期 → 丟 prompt 給 Claude → 「結果我錯了」#1 崩盤 → 838 行單檔 → debug 爆炸 → 第一件學到. 4 steps, ~51s, 1 punchline (s1 receives A+C light). **First use of `motif/crash-line`** (s1, will be reused in ch6 s1 and ch9 s11). Polish ink-splatter on s4.

**Source spec:** [outline.md §5](../../../demo/outline.md) · script.md L141-L163

---

## File Structure

```
src/chapters/
├── index.jsx                              # MODIFY: register Ch5
└── ch5-legacy/
    ├── Ch5.jsx
    ├── Ch5Step1.jsx                        # 結果我錯了 ★ punchline 4-beat
    ├── Ch5Step2.jsx                        # 838 行單檔
    ├── Ch5Step3.jsx                        # debug 爆炸 (chaotic 紅叉叉)
    └── Ch5Step4.jsx                        # 第一件學到 + ink-splatter polish 微縮
```

---

## Task 1: Register Ch5 + Step1 ★ punchline (most complex, first crash-line motif)

**Files:**
- Create: `Ch5.jsx`, `Ch5Step1.jsx`
- Modify: `src/chapters/index.jsx`

Beat structure (from beat-manifest.js):
- beatIndex 0: kicker「我那時候很天真」 fade-up + halftone dots 加密
- beatIndex 1: prompt box「幫我寫一個訓練 AI 解數獨的程式」stamp-in
- beatIndex 2: 崩盤句空框 (CrashLine placeholder mode — empty frame with blinking caret)
- beatIndex 3: CrashLine fill「⋯⋯結果我錯了」+ A+C climax (light, plus crash-line motif's built-in 紅邊 flash)

- [ ] **Step 1: Update `src/chapters/index.jsx`** — register `5: Ch5`

- [ ] **Step 2: Create `Ch5.jsx`**

```jsx
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import Ch5Step1 from './Ch5Step1.jsx';

const STEPS = { 1: Ch5Step1 };

export function Ch5() {
  const { stepId } = usePresentationContext();
  const Step = STEPS[stepId];
  if (!Step) return <main style={{ padding: 32, fontFamily: 'Space Grotesk' }}><div style={{ fontSize: 24, fontWeight: 900 }}>ch 5 · step {stepId}</div></main>;
  return <Step key={stepId} />;
}
```

- [ ] **Step 3: Create `Ch5Step1.jsx`**

```jsx
import { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { CrashLine } from '../../motifs/CrashLine.jsx';

export default function Ch5Step1() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
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
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Beat 0+ kicker top + halftone densify */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { y: 0, opacity: 1 } : { y: 30, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          position: 'absolute', top: 80,
          fontWeight: 900, fontSize: '2rem', color: '#000',
        }}
      >
        我那時候很天真
      </motion.div>

      {/* Halftone dots overlay density 1.5x when beat >= 0 */}
      {beatIndex >= 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.25 }}
          transition={{ duration: 0.4 }}
          style={{
            position: 'fixed', inset: 0, zIndex: 6, pointerEvents: 'none',
            backgroundImage: 'radial-gradient(#000 1.5px, transparent 1.5px)',
            backgroundSize: '14px 14px',
          }}
        />
      )}

      {/* Beat 1+ prompt chat box */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          background: '#FFFDF5', color: '#000',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: '24px 36px', maxWidth: 700,
          fontWeight: 700, fontSize: '1.5rem', lineHeight: 1.4,
          fontFamily: 'monospace',
          marginBottom: 56,
        }}
      >
        &gt; 幫我寫一個訓練 AI 解數獨的程式
      </motion.div>

      {/* Beat 2+ crash-line placeholder/fill */}
      <CrashLine
        active={beatIndex >= 2}
        filled={beatIndex >= 3}
        text="⋯⋯結果我錯了"
        width={720}
      />
    </main>
  );
}
```

- [ ] **Step 4: Build + commit**: `feat(demo): ch5 register + s1 結果我錯了 punchline (first crash-line motif)`

---

## Task 2: Ch5Step2 — 838 行單檔 + Ch5Step3 — debug 爆炸 (batched)

**Files:**
- Create: `Ch5Step2.jsx`, `Ch5Step3.jsx`
- Modify: `Ch5.jsx`

- [ ] **Step 1: Create `Ch5Step2.jsx`** (code block sticker + count-up)

```jsx
import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

const CODE_SNIPPET = `
class SudokuPPONet(nn.Module):
    def __init__(self, board_size=9, action_dim=729):
        super().__init__()
        self.board_size = board_size
        self.action_dim = action_dim
        self.encoder = nn.Sequential(...)
        self.policy_head = nn.Linear(...)
        self.value_head = nn.Linear(...)
    
    def forward(self, obs):
        ...

class RolloutBuffer:
    def __init__(self, n_steps=512):
        ...

def compute_gae(rewards, values, ...):
    ...

class TeacherEngine:
    def __init__(self, level=5):
        ...
    
    def naked_single(self, board):
        ...
    
    def hidden_single(self, board):
        ...

# 800+ more lines below
# everything stuffed into one file
`.trim();

export default function Ch5Step2() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let raf, start;
    const animate = (t) => {
      if (!start) start = t;
      const elapsed = t - start;
      const pct = Math.min(elapsed / 600, 1);
      setCount(Math.floor(pct * 838));
      if (pct < 1) raf = requestAnimationFrame(animate);
    };
    raf = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* Code wall slide up from below */}
      <motion.pre
        initial={{ y: 600, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        style={{
          width: '70%', maxHeight: '70vh', overflow: 'hidden',
          background: '#FFFDF5', color: '#222',
          border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          padding: 24, fontFamily: 'monospace', fontSize: 13, lineHeight: 1.5,
          marginTop: 80,
        }}
      >
        {CODE_SNIPPET}
      </motion.pre>

      {/* Top-right count-up badge */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', top: 32, right: 32,
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '8px 8px 0 0 #000',
          fontFamily: 'monospace', fontWeight: 900, fontSize: 24, rotate: 3,
        }}
      >
        torch_agent.py · {count} lines
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{
          marginTop: 16, fontWeight: 700, fontSize: '1.5rem', color: '#000',
        }}
      >
        什麼都塞在裡面
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: Create `Ch5Step3.jsx`** (chaos red X spawn)

```jsx
import { useEffect, useState } from 'react';
import { motion } from 'motion/react';

export default function Ch5Step3() {
  const [xs, setXs] = useState([]);
  useEffect(() => {
    let id = 0;
    const spawn = setInterval(() => {
      setXs(prev => [
        ...prev,
        {
          id: id++,
          x: Math.random() * 90 + 5,
          y: Math.random() * 60 + 20,
          rotate: Math.random() * 60 - 30,
          size: Math.random() * 40 + 60,
        },
      ].slice(-12));  // keep last 12
    }, 200);
    return () => clearInterval(spawn);
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, overflow: 'hidden',
    }}>
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        style={{
          fontWeight: 900, fontSize: '4rem', textAlign: 'center', zIndex: 2, position: 'relative',
        }}
      >
        每改一個地方都東倒西歪
      </motion.div>

      {/* Chaotic X spawning */}
      {xs.map(x => (
        <motion.div
          key={x.id}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 0 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${x.x}%`, top: `${x.y}%`,
            fontWeight: 900, fontSize: x.size, color: '#FF6B6B',
            WebkitTextStroke: '3px black',
            transform: `rotate(${x.rotate}deg)`,
            pointerEvents: 'none', zIndex: 1,
          }}
        >
          ✗
        </motion.div>
      ))}

      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{
          marginTop: 32,
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '20px 40px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
          fontWeight: 900, fontSize: '2.5rem', rotate: -2, zIndex: 2, position: 'relative',
        }}
      >
        debug 成本爆炸
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 3: Update Ch5.jsx STEPS to add `2: Ch5Step2, 3: Ch5Step3`**

- [ ] **Step 4: Build + commit**: `feat(demo): ch5 s2 838 行 + s3 debug 爆炸`

---

## Task 3: Ch5Step4 — 第一件學到 (with ink-splatter polish 微縮)

**Files:**
- Create: `Ch5Step4.jsx`
- Modify: `Ch5.jsx`

- [ ] **Step 1: Create `Ch5Step4.jsx`** (4 keyword highlights with ink-splatter micro per keyword)

```jsx
import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { YellowHighlight } from '../../motifs/YellowHighlight.jsx';
import { InkSplatter } from '../../motifs/InkSplatter.jsx';

const KEYWORDS = ['架構', '演算法', '自己', '分工'];

export default function Ch5Step4() {
  const [activeKw, setActiveKw] = useState(-1);

  // Stagger keyword reveal every 250ms after initial mask
  useEffect(() => {
    KEYWORDS.forEach((_, i) => {
      setTimeout(() => setActiveKw(i), 1200 + i * 250);
    });
  }, []);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      {/* Hero — mask-reveal */}
      <motion.div
        initial={{ clipPath: 'inset(0 100% 0 0)', opacity: 0 }}
        animate={{ clipPath: 'inset(0 0 0 0)', opacity: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        style={{
          fontWeight: 900, fontSize: '3rem', textAlign: 'center', lineHeight: 1.5,
          maxWidth: 1200,
        }}
      >
        <KeywordSpan idx={0} active={activeKw >= 0} text="架構" />、
        <KeywordSpan idx={1} active={activeKw >= 1} text="演算法" />都得
        <KeywordSpan idx={2} active={activeKw >= 2} text="自己" />先想清楚
        <br />
        再請 AI 來
        <KeywordSpan idx={3} active={activeKw >= 3} text="分工" />
      </motion.div>

      {/* Footer transition hint */}
      <motion.div
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 2.4 }}
        style={{
          position: 'absolute', bottom: 64,
          fontWeight: 700, fontSize: '1.25rem', color: '#666',
        }}
      >
        轉而當個套皮仔 →
      </motion.div>
    </main>
  );
}

function KeywordSpan({ idx, active, text }) {
  return (
    <span style={{ position: 'relative', display: 'inline-block' }}>
      <YellowHighlight active={active} padding="2px 12px">{text}</YellowHighlight>
      {active && (
        <div style={{
          position: 'absolute', left: '50%', top: '120%',
          width: 0, height: 0, pointerEvents: 'none',
        }}>
          <InkSplatter active count={1} radius={30} centerX="50%" centerY="50%" />
        </div>
      )}
    </span>
  );
}
```

- [ ] **Step 2: Update Ch5.jsx STEPS to add `4: Ch5Step4`**

- [ ] **Step 3: Build + commit**: `feat(demo): ch5 s4 第一件學到 + ink-splatter polish micro`

---

## Task 4: ch5 Checkpoint

```bash
npm run build && npm run test:run
git tag phase-5-ch5-complete
```

---

## 人工 Checkpoint 視覺驗證清單

- [ ] **s1 結果我錯了 ★ punchline** 4-beat:
  - beat 0: 上方「我那時候很天真」+ halftone dots 加密
  - beat 1: prompt 對話框「&gt; 幫我寫一個訓練 AI 解數獨的程式」stamp
  - beat 2: cream 大字框 + 6px 紅邊 + 閃爍游標 `_` 出現（CrashLine placeholder）
  - beat 3 (click): mask-reveal「⋯⋯結果我錯了」+ 紅邊 flash 2× + 螢幕震 + overshoot
- [ ] **s2 838 行**: 程式碼 sticker 從下方 slide-up（70% 高、可見 PPONet/RolloutBuffer 等）、右上「torch_agent.py · 838 lines」count-up（0→838）
- [ ] **s3 debug 爆炸**: 「每改一個地方都東倒西歪」hero、紅色 ✗ 持續隨機 spawn （每 200ms 一個、最多 12 個同時）、底下「debug 成本爆炸」紅 stamp
- [ ] **s4 第一件學到**: 主標 mask-reveal、4 個關鍵字「架構」「演算法」「自己」「分工」依序 stagger 黃底高亮、每個高亮下方有 1 小黑墨點、底部「轉而當個套皮仔 →」footer

## 想問你的回饋的點

1. **s1 prompt box** 用 monospace 字體 + `&gt;` 前綴模擬 chat input — 夠像 Claude 對話框嗎？要不要加 user/assistant avatar?
2. **s2 程式碼內容**: 我寫了假的 SudokuPPONet/RolloutBuffer 片段（30 行示意、字尾「800+ more lines below」）— 要不要改成直接讀 repo 真檔 `legacy/app/sudoku/torch_agent.py` 的前 30 行？(per asset-production.md ch5 用 [✓] 真檔)
3. **s3 紅叉 chaotic spawn 200ms 間隔**: 太快還是太慢？視覺亂度足夠嗎?
4. **s4 4 個關鍵字 stagger 250ms 間隔**: 動畫節奏 OK 嗎？每個關鍵字下方的單一墨點是否看得到？
5. **CrashLine motif 首發** (s1)：cream 大字框 + 6px 紅邊 + 閃爍游標 — 這個視覺語言將在 ch6 s1（「我又錯了」rhyme）和 ch9 s11（警語放大版）復用、現在的視覺強度滿意嗎？

## Execution Handoff

Plan saved. Execute via subagent-driven-development.
