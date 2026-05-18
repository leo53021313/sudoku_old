# html-ppt P0 動畫整合 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 html-ppt skill 的 4 個 P0 動畫特效（neural-net / path-draw / counter-up / stagger-list）依使用者「米色印刷 + 硬陰影 + overshoot 彈跳」風格客製後整合進 [demo/presentation/](../../../demo/presentation/) 的 ch9 s3、ch7 s5、ch8 s4 三張投影片，並建立可複用的 `.anim-stagger-list` CSS utility。

**Architecture:** 每個特效都作為 [src/motifs/](../../../demo/presentation/src/motifs/) 的新 React 元件（NeuralNet、SudokuBoardLive、CounterUp），用 framer-motion 配 SVG 實作；stagger-list 是純 CSS utility 寫在 [src/index.css](../../../demo/presentation/src/index.css)。所有元件遵守既有 motif 慣例：受控的 `active` prop、無外部副作用、有對應 `*.test.jsx` smoke test。風格決策（顏色、字級、陰影）已凍結在每個 Task 開頭的「Style Lock」段，不要在 implementation 階段再變更。

**Tech Stack:** React 18 + Vite + framer-motion 12 + vitest + @testing-library/react；無新增依賴。

---

## File Structure

新檔：

- `demo/presentation/src/motifs/NeuralNet.jsx` — 4-6-6-3 前饋網路 SVG，紅黃脈衝
- `demo/presentation/src/motifs/NeuralNet.test.jsx` — smoke + active prop 行為
- `demo/presentation/src/motifs/SudokuBoardLive.jsx` — 9×9 SVG 含 81-cell stagger 進場（替換 placeholder `SudokuBoard.jsx`，新名避免 import 衝突）
- `demo/presentation/src/motifs/SudokuBoardLive.test.jsx` — smoke + cells prop
- `demo/presentation/src/motifs/CounterUp.jsx` — 0→target 動畫數字 + 完成 callback
- `demo/presentation/src/motifs/CounterUp.test.jsx` — smoke + onComplete callback

改檔：

- `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx` — 右側「AI 訓練 RL」面板的 `<img neural-network.png>` 換成 `<NeuralNet />`
- `demo/presentation/src/chapters/ch7-reasoner/Ch7Step5.jsx` — `<SudokuBoard />` placeholder 換成 `<SudokuBoardLive cells={CH7_S5_BOARD} highlights={CH7_S5_HIGHLIGHTS} />`
- `demo/presentation/src/chapters/ch8-apprentice/Ch8Step4.jsx` — 整個 3D 翻牌區塊換成 `<CounterUp from={20} to={50} />` + `<RedStamp>+50</RedStamp>` + climax B trigger
- `demo/presentation/src/index.css` — 新增 `.anim-stagger-list` keyframes + nth-child delays
- `demo/presentation/src/pages/Sandbox.jsx` — 新增三個 motif 的 demo 入口（在現有 "Motif shells (placeholders)" section）

**注意：** [src/motifs/SudokuBoard.jsx](../../../demo/presentation/src/motifs/SudokuBoard.jsx) (placeholder) 保留不動 — 仍被 [Sandbox.jsx](../../../demo/presentation/src/pages/Sandbox.jsx) 引用作為 design-doc 比對基準。Ch7Step5 只切換 import 到 `SudokuBoardLive`。

**Out of scope:**

- ch7 s3 ThirteenStairs：[Ch7Step3.jsx](../../../demo/presentation/src/chapters/ch7-reasoner/Ch7Step3.jsx) 已有正式內聯實作，不需新 motif；ThirteenStairs placeholder 維持原狀供 Sandbox 用。
- ch8 s2-3 SudokuBoard：[Ch8Step2.jsx](../../../demo/presentation/src/chapters/ch8-apprentice/Ch8Step2.jsx) / [Ch8Step3.jsx](../../../demo/presentation/src/chapters/ch8-apprentice/Ch8Step3.jsx) 已有正式內聯 9×9 grid。
- 全簡報 bullet list 大規模 migration：只交付 `.anim-stagger-list` CSS utility + Sandbox 內 1 個 demo 範例，實際 migration 留給後續觸碰章節時逐步做。

---

## Style Lock（所有 Task 共用）

| Token | 值 | 來源 |
|-------|----|------|
| 米色底 | `#FFFDF5` | tokens/colors |
| 純黑邊 | `#000000` | tokens/colors |
| 紅 (reward−) | `#FF6B6B` | tokens/colors |
| 黃 (reward+) | `#FFD93D` | tokens/colors |
| 紫 (柔點綴) | `#C4B5FD` | tokens/colors |
| Overshoot ease | `[0.34, 1.56, 0.64, 1]` | 全簡報慣例 |
| 硬陰影 (0 模糊) | `4px 4px 0 0 #000` ~ `20px 20px 0 0 #000` | 全簡報慣例 |
| 字體 | `Space Grotesk` 900 | tokens/typography |
| 不可用 | glow / blur shadow / 玻璃擬態 / 漸層柔焦 | Part C 風格鎖 |

---

## Task 1：NeuralNet motif（ch9 s3 RL 對等 — 右側「AI 訓練」面板）

**Files:**
- Create: `demo/presentation/src/motifs/NeuralNet.jsx`
- Create: `demo/presentation/src/motifs/NeuralNet.test.jsx`
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx:64-68`（換掉 `<img src="/images/ai/ch9/neural-network.png" />`）
- Modify: `demo/presentation/src/pages/Sandbox.jsx`（新增 demo 入口）

**Style Lock (NeuralNet):**
- 拓撲：4-6-6-3 前饋（input/hidden1/hidden2/output 共 19 節點、4 層 18+18+18=54 條邊上限，但只連完整 bipartite）
- 節點：實心 `#000` 圓 `r=10`，外加 `4px solid #000` 環不要光暈
- 邊：`stroke="#000"` `stroke-width="2"` `opacity="0.35"`（**不要** glow）
- 脈衝：沿邊行進的小圓 `r=6`，**紅 `#FF6B6B` 與黃 `#FFD93D` 交替**（呼應 ch9 ± reward token 主題）
- 脈衝間隔：500ms（比 html-ppt 原版的 250ms 慢一倍，配合彈跳 ease）
- 脈衝動畫：framer-motion `motion.circle` 用 `cx/cy` keyframes 沿固定路徑插值，duration 800ms linear
- Container：`viewBox="0 0 320 200"` `preserveAspectRatio="xMidYMid meet"` `width="100%"` `height="100%"`
- 受 `active` prop 控制：`active=false` 時節點靜態、不發脈衝；`active=true` 時開始發脈衝

**Props:**
```jsx
<NeuralNet active={true} pulseInterval={500} colors={{ pulsePos: '#FFD93D', pulseNeg: '#FF6B6B' }} />
```

**全部都有預設值，呼叫端最簡寫法 `<NeuralNet active />`。**

- [ ] **Step 1.1：寫失敗測試 NeuralNet.test.jsx**

```jsx
// demo/presentation/src/motifs/NeuralNet.test.jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { NeuralNet } from './NeuralNet.jsx';

describe('NeuralNet', () => {
  it('renders an SVG with 19 nodes (4+6+6+3)', () => {
    const { container } = render(<NeuralNet active={false} />);
    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    const nodes = container.querySelectorAll('circle[data-role="node"]');
    expect(nodes.length).toBe(19);
  });

  it('renders 4+6+6+3 layer-edge bipartite = 24+36+18 = 78 edges', () => {
    const { container } = render(<NeuralNet active={false} />);
    const edges = container.querySelectorAll('line[data-role="edge"]');
    expect(edges.length).toBe(4 * 6 + 6 * 6 + 6 * 3);
  });

  it('does not render any pulse circles when inactive', () => {
    const { container } = render(<NeuralNet active={false} />);
    const pulses = container.querySelectorAll('circle[data-role="pulse"]');
    expect(pulses.length).toBe(0);
  });

  it('renders pulse circles when active', () => {
    const { container } = render(<NeuralNet active={true} />);
    const pulses = container.querySelectorAll('circle[data-role="pulse"]');
    expect(pulses.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 1.2：跑測試確認失敗**

Run: `cd demo/presentation && npm test -- NeuralNet --run`
Expected: FAIL with "Cannot find module './NeuralNet.jsx'"

- [ ] **Step 1.3：實作最小可通過版本**

```jsx
// demo/presentation/src/motifs/NeuralNet.jsx
import { motion } from 'motion/react';

const LAYERS = [4, 6, 6, 3];
const VB_W = 320;
const VB_H = 200;
const COLS = LAYERS.length;

function nodeXY(layerIdx, nodeIdx, layerSize) {
  const x = ((layerIdx + 0.5) / COLS) * VB_W;
  const y = ((nodeIdx + 0.5) / layerSize) * VB_H;
  return { x, y };
}

function buildEdges() {
  const edges = [];
  for (let l = 0; l < LAYERS.length - 1; l++) {
    for (let a = 0; a < LAYERS[l]; a++) {
      for (let b = 0; b < LAYERS[l + 1]; b++) {
        const p1 = nodeXY(l, a, LAYERS[l]);
        const p2 = nodeXY(l + 1, b, LAYERS[l + 1]);
        edges.push({ p1, p2, key: `${l}-${a}-${b}` });
      }
    }
  }
  return edges;
}

const EDGES = buildEdges();

export function NeuralNet({
  active = false,
  pulseInterval = 500,
  colors = { pulsePos: '#FFD93D', pulseNeg: '#FF6B6B' },
}) {
  const nodes = LAYERS.flatMap((sz, l) =>
    Array.from({ length: sz }, (_, n) => ({ ...nodeXY(l, n, sz), key: `n${l}-${n}` }))
  );

  return (
    <svg viewBox={`0 0 ${VB_W} ${VB_H}`} preserveAspectRatio="xMidYMid meet" width="100%" height="100%">
      {EDGES.map(e => (
        <line
          key={e.key}
          data-role="edge"
          x1={e.p1.x} y1={e.p1.y} x2={e.p2.x} y2={e.p2.y}
          stroke="#000" strokeWidth={2} opacity={0.35}
        />
      ))}
      {nodes.map(n => (
        <circle
          key={n.key}
          data-role="node"
          cx={n.x} cy={n.y} r={8}
          fill="#000" stroke="#000" strokeWidth={2}
        />
      ))}
      {active && EDGES.map((e, i) => (
        <motion.circle
          key={`p-${e.key}`}
          data-role="pulse"
          r={5}
          fill={i % 2 === 0 ? colors.pulsePos : colors.pulseNeg}
          initial={{ cx: e.p1.x, cy: e.p1.y, opacity: 0 }}
          animate={{ cx: [e.p1.x, e.p2.x], cy: [e.p1.y, e.p2.y], opacity: [0, 1, 0] }}
          transition={{
            duration: 0.8,
            ease: 'linear',
            repeat: Infinity,
            repeatDelay: pulseInterval / 1000 + (i * 0.05),
            delay: (i * 0.05) % 1.5,
          }}
        />
      ))}
    </svg>
  );
}
```

- [ ] **Step 1.4：跑測試確認通過**

Run: `cd demo/presentation && npm test -- NeuralNet --run`
Expected: PASS (4/4)

- [ ] **Step 1.5：整合進 Ch9Step3.jsx**

替換 [Ch9Step3.jsx:64-68](../../../demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx#L64) 的 `<img src="/images/ai/ch9/neural-network.png" />` 為：

```jsx
// 在頂部 import 加上
import { NeuralNet } from '../../motifs/NeuralNet.jsx';

// 替換 line 64-68
<div style={{ width: '70%', height: 260, display: 'block' }}>
  <NeuralNet active />
</div>
```

`<img>` 連同 `alt` 整個刪除。其他 line 51-75 區塊（外框 `motion.div`、下方「AI 訓練 RL」黑色標籤）保持不變。

- [ ] **Step 1.6：在 Sandbox 加入 demo 入口**

修改 [Sandbox.jsx](../../../demo/presentation/src/pages/Sandbox.jsx) 的 "Motif shells (placeholders)" section（line 121-131），新增一段顯示 NeuralNet 並讓使用者切換 active：

```jsx
// 在頂部 import 加上
import { NeuralNet } from '../motifs/NeuralNet.jsx';

// 加入新 state（在現有 useState 區塊）
const [neuralActive, setNeuralActive] = useState(true);

// 在 "Motif shells (placeholders)" section 後加新 section
<section style={{ marginTop: 32 }}>
  <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>NeuralNet (live)</h2>
  <div style={{ width: 480, height: 240, border: '4px solid #000', background: '#FFFDF5' }}>
    <NeuralNet active={neuralActive} />
  </div>
  <button onClick={() => setNeuralActive(v => !v)} style={btn}>NeuralNet toggle</button>
</section>
```

- [ ] **Step 1.7：跑全測試 + build 驗證沒破壞既有**

Run: `cd demo/presentation && npm test -- --run && npm run build`
Expected: 30+ tests pass; build success in <300ms

- [ ] **Step 1.8：Commit**

```bash
git add demo/presentation/src/motifs/NeuralNet.jsx \
        demo/presentation/src/motifs/NeuralNet.test.jsx \
        demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx \
        demo/presentation/src/pages/Sandbox.jsx
git commit -m "feat(demo): NeuralNet motif replaces static PNG in ch9 s3 (P0 #1)"
```

---

## Task 2：SudokuBoardLive motif（ch7 s5 — Action 擴增）

**Files:**
- Create: `demo/presentation/src/motifs/SudokuBoardLive.jsx`
- Create: `demo/presentation/src/motifs/SudokuBoardLive.test.jsx`
- Modify: `demo/presentation/src/chapters/ch7-reasoner/Ch7Step5.jsx`（切換 import + 加 puzzle data）
- Modify: `demo/presentation/src/pages/Sandbox.jsx`（新增 demo 入口）

**Style Lock (SudokuBoardLive):**
- 9×9 SVG，外框 6px `#000`，每 3×3 box 邊 4px `#000`，普通格線 1px `#000`
- 格子米色 `#FFFDF5`，已填字黑色 Space Grotesk 900 字級 24
- 進場：每條格線 80ms stagger 用 `stroke-dasharray` path-draw 動畫畫進來（10 條垂直 + 10 條水平 = 20 條，總 1.6s）
- 然後數字 stagger pop-in 每格 30ms（共 81 × 30ms = 2.4s 上限），用 overshoot ease，但只 pop 有值的格
- highlight 格：黑紅閃爍呼吸 `boxShadow inset 0 0 0 4px #FF6B6B` 1.2s infinite（同 Ch8Step2 既有 pattern）
- 寬度 `width=540 height=540`（同 Ch8Step2/3）

**Props:**
```jsx
<SudokuBoardLive cells={9x9_array_of_int_or_0} highlights={[[r,c],...]} active={true} />
```
- `cells`: `number[9][9]`，0 表示空格
- `highlights`: `Array<[r:number, c:number]>`，被框紅閃爍的格
- `active`: 控制是否觸發進場動畫；false 時直接 render 終態（給 Storybook/snapshot 用）

- [ ] **Step 2.1：寫失敗測試 SudokuBoardLive.test.jsx**

```jsx
// demo/presentation/src/motifs/SudokuBoardLive.test.jsx
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { SudokuBoardLive } from './SudokuBoardLive.jsx';

const SOLVED = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,2, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];

describe('SudokuBoardLive', () => {
  it('renders 81 cells', () => {
    const { container } = render(<SudokuBoardLive cells={SOLVED} active={false} />);
    const cells = container.querySelectorAll('[data-role="cell"]');
    expect(cells.length).toBe(81);
  });

  it('renders 20 grid lines (10 vertical + 10 horizontal)', () => {
    const { container } = render(<SudokuBoardLive cells={SOLVED} active={false} />);
    const lines = container.querySelectorAll('[data-role="grid-line"]');
    expect(lines.length).toBe(20);
  });

  it('cells with value 0 render empty', () => {
    const empty = Array.from({ length: 9 }, () => Array(9).fill(0));
    const { container } = render(<SudokuBoardLive cells={empty} active={false} />);
    const cells = container.querySelectorAll('[data-role="cell"]');
    cells.forEach(c => expect(c.textContent).toBe(''));
  });

  it('marks highlighted cells with data-highlight="true"', () => {
    const { container } = render(
      <SudokuBoardLive cells={SOLVED} highlights={[[0,0],[4,4]]} active={false} />
    );
    const highlighted = container.querySelectorAll('[data-role="cell"][data-highlight="true"]');
    expect(highlighted.length).toBe(2);
  });
});
```

- [ ] **Step 2.2：跑測試確認失敗**

Run: `cd demo/presentation && npm test -- SudokuBoardLive --run`
Expected: FAIL with module not found

- [ ] **Step 2.3：實作 SudokuBoardLive.jsx**

```jsx
// demo/presentation/src/motifs/SudokuBoardLive.jsx
import { motion } from 'motion/react';

const SIZE = 540;
const STROKE_OUTER = 6;
const STROKE_BOX = 4;
const STROKE_THIN = 1;

export function SudokuBoardLive({ cells, highlights = [], active = true }) {
  const cellSize = (SIZE - STROKE_OUTER * 2) / 9;
  const highlightSet = new Set(highlights.map(([r, c]) => `${r}-${c}`));

  const lines = [];
  for (let i = 1; i <= 9; i++) {
    const x = STROKE_OUTER + i * cellSize;
    const sw = (i % 3 === 0 && i !== 9) ? STROKE_BOX : i === 9 ? STROKE_OUTER : STROKE_THIN;
    lines.push({ key: `v${i}`, x1: x, y1: 0, x2: x, y2: SIZE, sw });
    lines.push({ key: `h${i}`, x1: 0, y1: STROKE_OUTER + i * cellSize, x2: SIZE, y2: STROKE_OUTER + i * cellSize, sw });
  }

  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}
         style={{ background: '#FFFDF5', boxShadow: '12px 12px 0 0 #000', border: `${STROKE_OUTER}px solid #000` }}>
      {lines.map((ln, i) => (
        <motion.line
          key={ln.key}
          data-role="grid-line"
          x1={ln.x1} y1={ln.y1} x2={ln.x2} y2={ln.y2}
          stroke="#000" strokeWidth={ln.sw}
          initial={active ? { pathLength: 0 } : { pathLength: 1 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 0.3, delay: active ? i * 0.08 : 0 }}
        />
      ))}
      {cells.flatMap((row, r) => row.map((val, c) => {
        const isHl = highlightSet.has(`${r}-${c}`);
        const cx = STROKE_OUTER + c * cellSize + cellSize / 2;
        const cy = STROKE_OUTER + r * cellSize + cellSize / 2;
        return (
          <g key={`${r}-${c}`} data-role="cell" data-highlight={isHl ? 'true' : 'false'}>
            {isHl && (
              <motion.rect
                x={STROKE_OUTER + c * cellSize + 2}
                y={STROKE_OUTER + r * cellSize + 2}
                width={cellSize - 4} height={cellSize - 4}
                fill="none" stroke="#FF6B6B" strokeWidth={4}
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
              />
            )}
            {val !== 0 && (
              <motion.text
                x={cx} y={cy}
                textAnchor="middle" dominantBaseline="central"
                fontFamily="Space Grotesk" fontWeight={900} fontSize={28} fill="#000"
                initial={active ? { scale: 0, opacity: 0 } : { scale: 1, opacity: 1 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  duration: 0.4,
                  delay: active ? 1.8 + (r * 9 + c) * 0.015 : 0,
                  ease: [0.34, 1.56, 0.64, 1],
                }}
              >{val}</motion.text>
            )}
          </g>
        );
      }))}
    </svg>
  );
}
```

- [ ] **Step 2.4：跑測試確認通過**

Run: `cd demo/presentation && npm test -- SudokuBoardLive --run`
Expected: PASS (4/4)

- [ ] **Step 2.5：整合進 Ch7Step5.jsx**

替換 [Ch7Step5.jsx](../../../demo/presentation/src/chapters/ch7-reasoner/Ch7Step5.jsx) 完整檔案：

```jsx
import { motion } from 'motion/react';
import { SudokuBoardLive } from '../../motifs/SudokuBoardLive.jsx';

const BOARD = [
  [5,3,4, 6,7,8, 9,1,2],
  [6,7,0, 1,9,5, 3,4,8],
  [1,9,8, 3,4,2, 5,6,7],
  [8,5,9, 7,6,1, 4,2,3],
  [4,2,6, 8,5,3, 7,9,1],
  [7,1,3, 9,2,4, 8,5,6],
  [9,6,1, 5,3,7, 2,8,4],
  [2,8,7, 4,1,9, 6,3,5],
  [3,4,5, 2,8,6, 1,7,9],
];
const HIGHLIGHTS = [[1, 2]];

export default function Ch7Step5() {
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
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '3rem', textAlign: 'center' }}
      >
        多了一倍可以做的事
      </motion.div>

      <SudokuBoardLive cells={BOARD} highlights={HIGHLIGHTS} active />

      <div style={{ display: 'flex', gap: 32, fontWeight: 900, fontSize: 20 }}>
        <span style={{
          background: '#10B981', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>填一個數字</span>
        <span style={{
          background: '#FF6B6B', color: '#FFF',
          padding: '12px 24px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        }}>劃掉這格不可能是這個數 ✗</span>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.0 }}
        style={{ fontWeight: 700, fontSize: '1.25rem', color: '#666', marginTop: 8 }}
      >
        消去類技巧才能展示出來
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2.6：在 Sandbox 加入 demo 入口**

修改 [Sandbox.jsx](../../../demo/presentation/src/pages/Sandbox.jsx)：

```jsx
import { SudokuBoardLive } from '../motifs/SudokuBoardLive.jsx';

// 在 "Motif shells" section 後加新 section
<section style={{ marginTop: 32 }}>
  <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>SudokuBoardLive</h2>
  <SudokuBoardLive
    cells={[
      [5,3,4, 6,7,8, 9,1,2],
      [6,7,0, 1,9,5, 3,4,8],
      [1,9,8, 3,4,2, 5,6,7],
      [8,5,9, 7,6,1, 4,2,3],
      [4,2,6, 8,5,3, 7,9,1],
      [7,1,3, 9,2,4, 8,5,6],
      [9,6,1, 5,3,7, 2,8,4],
      [2,8,7, 4,1,9, 6,3,5],
      [3,4,5, 2,8,6, 1,7,9],
    ]}
    highlights={[[1,2]]}
    active
  />
</section>
```

- [ ] **Step 2.7：跑測試 + build**

Run: `cd demo/presentation && npm test -- --run && npm run build`
Expected: all tests pass, build success

- [ ] **Step 2.8：Commit**

```bash
git add demo/presentation/src/motifs/SudokuBoardLive.jsx \
        demo/presentation/src/motifs/SudokuBoardLive.test.jsx \
        demo/presentation/src/chapters/ch7-reasoner/Ch7Step5.jsx \
        demo/presentation/src/pages/Sandbox.jsx
git commit -m "feat(demo): SudokuBoardLive motif for ch7 s5 (P0 #2, path-draw 81-cell stagger)"
```

---

## Task 3：CounterUp motif（ch8 s4 — 取代 3D 翻牌 +20→+50）

**Files:**
- Create: `demo/presentation/src/motifs/CounterUp.jsx`
- Create: `demo/presentation/src/motifs/CounterUp.test.jsx`
- Modify: `demo/presentation/src/chapters/ch8-apprentice/Ch8Step4.jsx`（整段 perspective flip 區塊替換）
- Modify: `demo/presentation/src/pages/Sandbox.jsx`

**Style Lock (CounterUp):**
- 數字字體：Space Grotesk 900，字級 8rem（同既有翻牌的 fontSize）
- 計數動畫：用 `requestAnimationFrame` 從 `from` tick 到 `to`，duration 1200ms，ease-out（用 `1 - (1-t)^2` 立方緩動）
- 完成瞬間觸發 `onComplete` callback（呼叫端用來啟動 climax B）
- 容器：黃色背景 `#FFD93D` + 8px 黑邊 + `16px 16px 0 0 #000` 硬陰影 + `rotate: -3deg`（呼應 Ch7Step6 「0」的視覺律動）
- prefix（如 `+`）、suffix 透過 props 可選

**Props:**
```jsx
<CounterUp from={20} to={50} duration={1200} prefix="+" onComplete={() => {}} />
```

- [ ] **Step 3.1：寫失敗測試 CounterUp.test.jsx**

```jsx
// demo/presentation/src/motifs/CounterUp.test.jsx
import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { CounterUp } from './CounterUp.jsx';

describe('CounterUp', () => {
  it('renders initial value with prefix', () => {
    const { container } = render(<CounterUp from={20} to={50} prefix="+" duration={1200} />);
    expect(container.textContent).toContain('+20');
  });

  it('renders without prefix when not provided', () => {
    const { container } = render(<CounterUp from={0} to={10} duration={500} />);
    expect(container.textContent).toMatch(/^0/);
  });

  it('calls onComplete after animation ends', async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    render(<CounterUp from={0} to={5} duration={100} onComplete={onComplete} />);
    await act(async () => {
      vi.advanceTimersByTime(200);
    });
    expect(onComplete).toHaveBeenCalledTimes(1);
    vi.useRealTimers();
  });
});
```

- [ ] **Step 3.2：跑測試確認失敗**

Run: `cd demo/presentation && npm test -- CounterUp --run`
Expected: FAIL

- [ ] **Step 3.3：實作 CounterUp.jsx**

```jsx
// demo/presentation/src/motifs/CounterUp.jsx
import { useEffect, useState, useRef } from 'react';

export function CounterUp({
  from = 0,
  to,
  duration = 1200,
  prefix = '',
  suffix = '',
  onComplete = () => {},
}) {
  const [value, setValue] = useState(from);
  const completedRef = useRef(false);

  useEffect(() => {
    completedRef.current = false;
    const start = performance.now();
    let raf;
    const tick = (t) => {
      const elapsed = t - start;
      const pct = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - pct, 2);
      setValue(Math.round(from + (to - from) * eased));
      if (pct < 1) {
        raf = requestAnimationFrame(tick);
      } else if (!completedRef.current) {
        completedRef.current = true;
        onComplete();
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [from, to, duration, onComplete]);

  return (
    <div style={{
      background: '#FFD93D', color: '#000',
      padding: '32px 96px', border: '8px solid #000', boxShadow: '16px 16px 0 0 #000',
      fontFamily: 'Space Grotesk', fontWeight: 900, fontSize: '8rem',
      transform: 'rotate(-3deg)',
      display: 'inline-block', lineHeight: 1,
    }}>
      {prefix}{value}{suffix}
    </div>
  );
}
```

- [ ] **Step 3.4：跑測試確認通過**

Run: `cd demo/presentation && npm test -- CounterUp --run`
Expected: PASS (3/3)

- [ ] **Step 3.5：整合進 Ch8Step4.jsx**

替換 [Ch8Step4.jsx](../../../demo/presentation/src/chapters/ch8-apprentice/Ch8Step4.jsx) 全檔：

```jsx
import { useState } from 'react';
import { motion } from 'motion/react';
import { useClimax } from '../../climax/useClimax.js';
import { HalftoneBurst } from '../../motifs/HalftoneBurst.jsx';
import { CounterUp } from '../../motifs/CounterUp.jsx';

export default function Ch8Step4() {
  const climax = useClimax(['B']);
  const [showFinal, setShowFinal] = useState(false);

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 32,
    }}>
      <HalftoneBurst active={climax.activeFX.B} centerX="50%" centerY="50%" />

      <motion.div
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ fontWeight: 900, fontSize: '2.5rem' }}
      >
        破關獎勵調更大
      </motion.div>

      <CounterUp
        from={20}
        to={50}
        prefix="+"
        duration={1200}
        onComplete={() => { climax.play(); setShowFinal(true); }}
      />

      <motion.div
        animate={showFinal ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
        transition={{ duration: 0.5 }}
        style={{ fontWeight: 700, fontSize: '1.5rem', textAlign: 'center', color: '#666' }}
      >
        誘惑超過刷部分分數的賤招
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 3.6：在 Sandbox 加入 demo 入口**

```jsx
import { CounterUp } from '../motifs/CounterUp.jsx';

// 在 Motif shells section 後加
<section style={{ marginTop: 32 }}>
  <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>CounterUp</h2>
  <CounterUp from={20} to={50} prefix="+" duration={1200} />
</section>
```

- [ ] **Step 3.7：跑測試 + build**

Run: `cd demo/presentation && npm test -- --run && npm run build`
Expected: all tests pass, build success

- [ ] **Step 3.8：Commit**

```bash
git add demo/presentation/src/motifs/CounterUp.jsx \
        demo/presentation/src/motifs/CounterUp.test.jsx \
        demo/presentation/src/chapters/ch8-apprentice/Ch8Step4.jsx \
        demo/presentation/src/pages/Sandbox.jsx
git commit -m "feat(demo): CounterUp motif replaces 3D flip in ch8 s4 (P0 #3, +20→+50 + climax B)"
```

---

## Task 4：`.anim-stagger-list` CSS utility

**Files:**
- Modify: `demo/presentation/src/index.css`（新增 keyframes + class）
- Modify: `demo/presentation/src/pages/Sandbox.jsx`（加 demo 區）

**Style Lock (stagger-list):**
- 子元素 `> *` 進場：`opacity 0 → 1` + `translateY(20px) → 0`
- Stagger 增量：120ms（比 html-ppt 原版 50ms 慢，配合 overshoot 節奏）
- 個別子項 duration：500ms，ease 用 overshoot `cubic-bezier(0.34, 1.56, 0.64, 1)`
- 最多支援前 12 個 `nth-child` 延遲；超過 12 個的元素一律用第 12 個的延遲（避免無止盡）

- [ ] **Step 4.1：在 index.css 加 keyframes + class**

把以下加到 [index.css](../../../demo/presentation/src/index.css) **最末端**（避免影響既有 `halftone-drift` / `ambient-float` / `fade-bridge` / `caret-blink`）：

```css
@keyframes stagger-list-rise {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.anim-stagger-list > * {
  opacity: 0;
  animation: stagger-list-rise 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
.anim-stagger-list > *:nth-child(1)  { animation-delay: 0.00s; }
.anim-stagger-list > *:nth-child(2)  { animation-delay: 0.12s; }
.anim-stagger-list > *:nth-child(3)  { animation-delay: 0.24s; }
.anim-stagger-list > *:nth-child(4)  { animation-delay: 0.36s; }
.anim-stagger-list > *:nth-child(5)  { animation-delay: 0.48s; }
.anim-stagger-list > *:nth-child(6)  { animation-delay: 0.60s; }
.anim-stagger-list > *:nth-child(7)  { animation-delay: 0.72s; }
.anim-stagger-list > *:nth-child(8)  { animation-delay: 0.84s; }
.anim-stagger-list > *:nth-child(9)  { animation-delay: 0.96s; }
.anim-stagger-list > *:nth-child(10) { animation-delay: 1.08s; }
.anim-stagger-list > *:nth-child(11) { animation-delay: 1.20s; }
.anim-stagger-list > *:nth-child(n+12) { animation-delay: 1.32s; }
```

- [ ] **Step 4.2：在 Sandbox 加 demo 區（同時當作 smoke verification）**

```jsx
// 在最末段加
<section style={{ marginTop: 32 }}>
  <h2 style={{ fontSize: '1.5rem', fontWeight: 900 }}>.anim-stagger-list (CSS utility)</h2>
  <ul className="anim-stagger-list" style={{ listStyle: 'none', padding: 0, marginTop: 16 }}>
    {['填', '消', '對', '錯', '快', '慢', '深', '淺'].map((t, i) => (
      <li key={i} style={{
        background: '#FFFDF5', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
        padding: '8px 16px', marginBottom: 8, fontWeight: 900, display: 'inline-block', marginRight: 8,
      }}>{t}</li>
    ))}
  </ul>
</section>
```

- [ ] **Step 4.3：跑 build 確認 CSS 編譯 OK**

Run: `cd demo/presentation && npm run build`
Expected: success；`dist/assets/index-*.css` 應該增加 ~400 bytes

開瀏覽器 `npm run dev` 切到 Sandbox 用肉眼確認 8 個 li 依序彈跳出現（不在自動化測試範圍 — CSS 動畫很難可靠 unit 測；用 Sandbox 視覺驗證更實際）。

- [ ] **Step 4.4：在 README 加一行 utility 說明（非必要、跳過如果想速戰）**

[demo/presentation/README.md](../../../demo/presentation/README.md) 適當位置加：

```markdown
- `.anim-stagger-list` — CSS utility, children rise+fade with 120ms stagger (max 12 children before flooring)
```

- [ ] **Step 4.5：Commit**

```bash
git add demo/presentation/src/index.css \
        demo/presentation/src/pages/Sandbox.jsx \
        demo/presentation/README.md
git commit -m "feat(demo): .anim-stagger-list CSS utility (P0 #4, overshoot ease, 120ms stagger)"
```

---

## Final Verification（執行完所有 Task 後）

- [ ] **跑完整測試套件**

Run: `cd demo/presentation && npm test -- --run`
Expected: 26 + 11 (新增 4+4+3) = 37 passing

- [ ] **跑 build**

Run: `cd demo/presentation && npm run build`
Expected: success in <300ms，bundle size 增加 < 5 KB gzip

- [ ] **dev server 視覺驗證**

Run: `cd demo/presentation && npm run dev`

開瀏覽器逐一檢查：
- `/sandbox` — 4 個新 motif 都能 render（NeuralNet、SudokuBoardLive、CounterUp、`.anim-stagger-list`）
- ch9 s3（RL 對等）— 右側不再是靜態 PNG，是動的神經網路 + 紅黃脈衝
- ch7 s5（Action 擴增）— 9×9 grid 線條依序畫進來、數字 stagger pop、紅框格閃爍
- ch8 s4（+20→+50）— 黃色 +20 滾到 +50，halftone burst 同步觸發

- [ ] **檢查 git log 整潔**

Run: `git log --oneline -10`
Expected: 4 個 commit，commit message 都用 `feat(demo):` 開頭

---

## Self-Review Pass（Plan 作者自查）

**1. Spec coverage:**

| Part C P0 項目 | 對應 Task | 備註 |
|----------------|----------|------|
| neural-net (ch9 s1) | Task 1 | 修正目標為 ch9 s3 RL 對等右側面板 |
| path-draw (ThirteenStairs ch7 s3) | — | Out of scope — Ch7Step3 已有正式內聯實作，placeholder 留作 Sandbox 比對 |
| path-draw (SudokuBoard ch7 s5) | Task 2 | 新名 `SudokuBoardLive` 避免與 placeholder 衝突 |
| path-draw (SudokuBoard ch8 s2-3) | — | Out of scope — 已有內聯實作 |
| counter-up (ch8 s4) | Task 3 | 取代 3D 翻牌（非 FlipTwentyToFifty placeholder） |
| stagger-list utility | Task 4 | 純 CSS utility + Sandbox demo；不做全簡報 migration |

**2. Placeholder scan:** 無「TBD」「TODO later」「add appropriate error handling」「Similar to Task N」等模糊指示。每個 code block 完整可貼上。

**3. Type consistency:** 三個新 motif 命名一致 — `NeuralNet` / `SudokuBoardLive` / `CounterUp`，prop 命名都用既有慣例（`active`, `from`/`to`, `cells`/`highlights`）。`data-role` 屬性命名一致（`node` / `edge` / `pulse` / `cell` / `grid-line`）。

---

## Execution Handoff

執行有兩條路（待使用者選）：

1. **Subagent-Driven（推薦，符合使用者 memory 偏好）** — 每個 Task 派一個 fresh subagent，TDD per step，兩段式 review checkpoint。對應 sub-skill：`superpowers:subagent-driven-development`
2. **Inline Execution** — 本對話內 batch 執行，每個 Task 之間 checkpoint 給人類 review。對應 sub-skill：`superpowers:executing-plans`
