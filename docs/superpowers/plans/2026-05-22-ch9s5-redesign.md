# ch9 s5 視覺重設計 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ch9 s5「戀愛 a callback」從現有「兩張並排卡 + ghost 女生」改寫成「奶茶 + 大腦在思考泡泡內」的新構圖，beat 從 4 → 5（多一拍奶茶 happy 反應），導入兩個新奶茶 variant（`happy` / `crashed`）。

**Architecture:** 三個小 commit：(1) `MilkTea.jsx` 註冊 happy / crashed variant + 新 PNG 進 git；(2) `beat-manifest.js` 4→5 拍 + `totalBeats: 99→100` + `usePresentation.test.js` 同步；(3) `Ch9Step5.jsx` 構圖整檔重寫。所有單元測試走既有的 vitest + @testing-library/react，動畫 / 構圖部分採人眼驗收（沿用 ch6 / ch7 既有的「無自動測試」慣例）。

**Tech Stack:** React 19、motion 12、vitest 4、@testing-library/react 16、Vite 8。設計依據：[docs/superpowers/specs/2026-05-22-ch9s5-redesign-design.md](../specs/2026-05-22-ch9s5-redesign-design.md)。

---

## File Structure

**Modify:**
- [demo/presentation/src/motifs/MilkTea.jsx](../../demo/presentation/src/motifs/MilkTea.jsx) — `VARIANT_SRC` + `AssetPlaceholder` fallback slug 各加兩個 key
- [demo/presentation/src/motifs/MilkTea.test.jsx](../../demo/presentation/src/motifs/MilkTea.test.jsx) — 為 happy / crashed 各新增一個 render assertion
- [demo/presentation/src/data/beat-manifest.js](../../demo/presentation/src/data/beat-manifest.js) — ch9 step 5 從 4 拍 → 5 拍 + `totalBeats: 99 → 100` + `motifs: []`
- [demo/presentation/src/state/usePresentation.test.js](../../demo/presentation/src/state/usePresentation.test.js) — `totalBeats === 99` → `100`
- [demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx](../../demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx) — 整檔重寫

**Add to git (PNGs 已在磁碟、但 untracked):**
- `demo/presentation/public/images/ai/ch6/milk-tea-happy.png`
- `demo/presentation/public/images/ai/ch6/milk-tea-crashed.png`
- `demo/presentation/public/images/ai/ch6/milk-tea-question.png`（前次 session 移過去、也尚未 commit）

---

## Task 1: MilkTea — 加 happy / crashed variant + commit PNGs

**Files:**
- Modify: `demo/presentation/src/motifs/MilkTea.jsx`
- Modify: `demo/presentation/src/motifs/MilkTea.test.jsx`
- Add: `demo/presentation/public/images/ai/ch6/milk-tea-happy.png`
- Add: `demo/presentation/public/images/ai/ch6/milk-tea-crashed.png`
- Add: `demo/presentation/public/images/ai/ch6/milk-tea-question.png`

- [ ] **Step 1: 寫 happy / crashed 的 render 測試（會失敗）**

把以下兩個 `it` block 加到 `demo/presentation/src/motifs/MilkTea.test.jsx` 最後一個 `it` 後面：

```jsx
  it('variant="happy" 渲染 happy PNG', () => {
    render(<MilkTea variant="happy" />);
    const img = screen.getByAltText('奶茶');
    expect(img.getAttribute('src')).toBe('/images/ai/ch6/milk-tea-happy.png');
  });

  it('variant="crashed" 渲染 crashed PNG', () => {
    render(<MilkTea variant="crashed" />);
    const img = screen.getByAltText('奶茶');
    expect(img.getAttribute('src')).toBe('/images/ai/ch6/milk-tea-crashed.png');
  });

  it('variant="happy" 圖片失敗時 fallback 帶 happy slug', () => {
    render(<MilkTea variant="happy" />);
    fireEvent.error(screen.getByAltText('奶茶'));
    expect(screen.getByLabelText('TODO: ch6-milk-tea-happy')).toBeInTheDocument();
  });

  it('variant="crashed" 圖片失敗時 fallback 帶 crashed slug', () => {
    render(<MilkTea variant="crashed" />);
    fireEvent.error(screen.getByAltText('奶茶'));
    expect(screen.getByLabelText('TODO: ch6-milk-tea-crashed')).toBeInTheDocument();
  });
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd demo/presentation && npx vitest run src/motifs/MilkTea.test.jsx
```

Expected: 兩個 src assertion 失敗（VARIANT_SRC 沒這兩個 key、`?? VARIANT_SRC.normal` 退到 normal）；兩個 fallback assertion 也失敗（`todo` slug 邏輯沒考慮新 variant）。

- [ ] **Step 3: 改 `MilkTea.jsx` — 擴充 VARIANT_SRC + fallback slug**

整個 `demo/presentation/src/motifs/MilkTea.jsx` 內容替換為：

```jsx
import { useState } from 'react';
import { AiSticker } from '../components/AiSticker.jsx';
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';

// 奶茶 — img2img 角色（奶茶髮色 + 韓式鍋蓋頭）。
// 四個情緒 variant：normal（中性）/ happy（心動）/ crashed（崩潰）/ question（困惑、ch7 s7 用）。
// PNG 尚未生成時，img onError → 改顯示 AssetPlaceholder，避免破圖。
const VARIANT_SRC = {
  normal: '/images/ai/ch6/milk-tea.png',
  happy: '/images/ai/ch6/milk-tea-happy.png',
  crashed: '/images/ai/ch6/milk-tea-crashed.png',
  question: '/images/ai/ch6/milk-tea-question.png',
};

const VARIANT_TODO = {
  normal: 'ch6-milk-tea',
  happy: 'ch6-milk-tea-happy',
  crashed: 'ch6-milk-tea-crashed',
  question: 'ch6-milk-tea-question',
};

export function MilkTea({ width = 300, rotation = -3, shadow = 12, variant = 'normal', ...rest }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return <AssetPlaceholder type="[AI]" width={width} height={width} todo={VARIANT_TODO[variant] ?? VARIANT_TODO.normal} />;
  }

  return (
    <AiSticker
      src={VARIANT_SRC[variant] ?? VARIANT_SRC.normal}
      alt="奶茶"
      width={width}
      rotation={rotation}
      shadow={shadow}
      onError={() => setErrored(true)}
      {...rest}
    />
  );
}
```

- [ ] **Step 4: 跑測試確認通過**

```bash
cd demo/presentation && npx vitest run src/motifs/MilkTea.test.jsx
```

Expected: 6 個 it block 全 PASS（既有 2 個 + 新加 4 個）。

- [ ] **Step 5: 跑 lint**

```bash
cd demo/presentation && npm run lint
```

Expected: 沒新警告。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/motifs/MilkTea.jsx \
        demo/presentation/src/motifs/MilkTea.test.jsx \
        demo/presentation/public/images/ai/ch6/milk-tea-happy.png \
        demo/presentation/public/images/ai/ch6/milk-tea-crashed.png \
        demo/presentation/public/images/ai/ch6/milk-tea-question.png
git commit -m "feat(motifs): add MilkTea happy/crashed variants + commit PNG assets"
```

---

## Task 2: beat-manifest — 4 → 5 拍 + totalBeats 同步

**Files:**
- Modify: `demo/presentation/src/data/beat-manifest.js`（top-level + ch9 step 5）
- Modify: `demo/presentation/src/state/usePresentation.test.js`（line 100-103）

- [ ] **Step 1: 先改 usePresentation 測試期待值（會讓既有測試失敗）**

把 `demo/presentation/src/state/usePresentation.test.js` 第 100-103 行：

```js
  it('reports totalBeats = 99', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(99);
  });
```

改成：

```js
  it('reports totalBeats = 100', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(100);
  });
```

- [ ] **Step 2: 跑測試確認失敗**

```bash
cd demo/presentation && npx vitest run src/state/usePresentation.test.js
```

Expected: `reports totalBeats = 100` 失敗（拿到 99）。其他既有 test 都 PASS。

- [ ] **Step 3: 改 beat-manifest — top-level totalBeats + ch9 step 5**

a. `demo/presentation/src/data/beat-manifest.js` 第 7 行：

```js
  totalBeats: 99,
```

改成：

```js
  totalBeats: 100,
```

b. 同檔第 175-182 行（ch9 step 5）：

```js
        { id: 5, title: '戀愛 a callback', duration: 18, punchline: true, motifs: ['girl-new'], climax: ['A', 'C'],
          beats: [
            { id: 'bg-callback',    type: 'click', cue: '追一個人的時候——', wait: null, scriptLines: 'L323' },
            { id: 'left-positive',  type: 'click', cue: '對方回訊息你就被加分', wait: '1s', scriptLines: 'L325' },
            { id: 'right-negative', type: 'click', cue: '已讀不回你就被扣分', wait: '1.5s', scriptLines: 'L325' },
            { id: 'punchline-hero', type: 'click', cue: '你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練', wait: '2s', climax: ['A', 'C'], scriptLines: 'L327-329' },
          ],
        },
```

改成：

```js
        { id: 5, title: '戀愛 a callback', duration: 22, punchline: true, motifs: [], climax: ['A', 'C'],
          beats: [
            { id: 'bg-callback',     type: 'click', cue: '追一個人的時候——', wait: null, scriptLines: 'L323' },
            { id: 'left-positive',   type: 'click', cue: '對方回訊息你就被加分', wait: '1s', scriptLines: 'L325' },
            { id: 'milktea-happy',   type: 'click', cue: null, wait: '0.8s 觀眾消化反應', scriptLines: 'L325' },
            { id: 'right-negative',  type: 'click', cue: '已讀不回你就被扣分', wait: '1.5s', scriptLines: 'L325' },
            { id: 'punchline-hero',  type: 'click', cue: '你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練', wait: '2s', climax: ['A', 'C'], scriptLines: 'L327-329' },
          ],
        },
```

**注意**：duration 從 18 → 22、motifs 從 `['girl-new']` → `[]`、第 3 個位置（index 2）新增 `milktea-happy` beat。

- [ ] **Step 4: 跑測試確認通過**

```bash
cd demo/presentation && npx vitest run src/state/usePresentation.test.js
```

Expected: 全 PASS（包含 `reports totalBeats = 100`）。

- [ ] **Step 5: 順手跑全部測試確認沒打到別人**

```bash
cd demo/presentation && npm run test:run
```

Expected: 全 PASS。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/data/beat-manifest.js \
        demo/presentation/src/state/usePresentation.test.js
git commit -m "feat(beats): ch9 s5 4→5 beats with milktea-happy reaction beat"
```

---

## Task 3: Ch9Step5.jsx — 構圖整檔重寫

**Files:**
- Modify: `demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx`

> **設計準則**：[spec §3 構圖](../specs/2026-05-22-ch9s5-redesign-design.md#3-構圖composition) + [§4 Beat 結構](../specs/2026-05-22-ch9s5-redesign-design.md#4-beat-結構) + [§5 動畫細節](../specs/2026-05-22-ch9s5-redesign-design.md#5-動畫細節)

- [ ] **Step 1: 整檔替換 Ch9Step5.jsx**

把 `demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx` 整份內容替換為：

```jsx
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { MilkTea } from '../../motifs/MilkTea.jsx';

const OVERSHOOT = [0.34, 1.56, 0.64, 1];

// 粒子發射位置（label 中心點下方）
const PLUS_SPAWN = { left: '15%', top: 70 };
const MINUS_SPAWN = { right: '15%', top: 70 };
// 大腦泡泡中心（粒子飛行目的地）
const BUBBLE_CENTER_X = '50%';
const BUBBLE_CENTER_Y = '35%';

export default function Ch9Step5() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climax = useClimax(['A', 'C']);
  const firedRef = useRef(false);
  const [pluses, setPluses] = useState([]);
  const [minuses, setMinuses] = useState([]);
  const [aftermath, setAftermath] = useState(false);
  const [brainFlash, setBrainFlash] = useState(null); // 'plus' | 'minus' | null

  // beat 1：+ 粒子從綠 label 連發飛向大腦泡泡
  useEffect(() => {
    if (beatIndex < 1) return;
    let id = 0;
    const t = setInterval(() => {
      setPluses(p => [...p, { id: id++ }].slice(-10));
    }, 300);
    return () => clearInterval(t);
  }, [beatIndex]);

  // beat 3：− 粒子從紅 label 連發飛向大腦泡泡
  useEffect(() => {
    if (beatIndex < 3) return;
    let id = 0;
    const t = setInterval(() => {
      setMinuses(m => [...m, { id: id++ }].slice(-10));
    }, 300);
    return () => clearInterval(t);
  }, [beatIndex]);

  // beat 4：climax + shake + aftermath（沿用既有結構）
  useEffect(() => {
    if (beatIndex === 4 && !firedRef.current) {
      firedRef.current = true;
      climax.play();
      triggerShake();
      const t = setTimeout(() => setAftermath(true), 700);
      return () => clearTimeout(t);
    }
  }, [beatIndex, climax, triggerShake]);

  // 奶茶 variant：beat 0-1 normal / beat 2-3 happy / beat 4 crashed
  const milkTeaVariant =
    beatIndex >= 4 ? 'crashed'
    : beatIndex >= 2 ? 'happy'
    : 'normal';

  // 奶茶 motion：beat 2 前傾 / beat 4 下沉
  const milkTeaAnimate =
    beatIndex >= 4 ? { y: 16, rotate: -5, scale: 0.95, filter: 'grayscale(0.7)' }
    : beatIndex >= 2 ? { y: -8, rotate: 2, scale: 1.05, filter: 'grayscale(0)' }
    : { y: 0, rotate: -3, scale: 1, filter: 'grayscale(0)' };

  // 大腦在 climax 時褪色
  const bubbleFilter = beatIndex >= 4 ? 'grayscale(1)' : 'none';

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 「回訊息」綠 label（beat 1+） */}
      {beatIndex >= 1 && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 40, left: '8%',
            fontWeight: 900, fontSize: 32, background: '#10B981', color: '#FFF',
            padding: '14px 32px', border: '6px solid #000', boxShadow: '9px 9px 0 0 #000',
            zIndex: 12,
          }}
        >回訊息</motion.div>
      )}

      {/* 「已讀不回」紅 label（beat 3+） */}
      {beatIndex >= 3 && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.4, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 40, right: '8%',
            fontWeight: 900, fontSize: 32, background: '#FF6B6B', color: '#FFF',
            padding: '14px 32px', border: '6px solid #000', boxShadow: '9px 9px 0 0 #000',
            zIndex: 12,
          }}
        >已讀不回</motion.div>
      )}

      {/* 思考泡泡 + 大腦（beat 0+） */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0
          ? { scale: 1, opacity: 1 }
          : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, ease: OVERSHOOT }}
        style={{
          position: 'absolute', top: '15%', left: '50%',
          transform: 'translateX(-50%)',
          filter: bubbleFilter,
          transition: 'filter 0.6s ease',
          zIndex: 10,
        }}
      >
        {/* 思考泡泡 — 圓邊框 */}
        <div style={{
          width: 240, height: 240,
          background: '#FFFDF5',
          border: '6px solid #000',
          borderRadius: '50%',
          boxShadow: '8px 8px 0 0 #000',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          position: 'relative',
        }}>
          {/* 大腦 sticker（內嵌、無 sticker 邊框，避免框中框） */}
          <motion.img
            src="/images/ai/ch9/brain-reward.png"
            alt="大腦"
            animate={brainFlash === 'plus'
              ? { scale: [1, 1.08, 1], filter: 'drop-shadow(0 0 12px #10B981)' }
              : brainFlash === 'minus'
                ? { scale: 1, x: [-3, 3, -2, 0], filter: 'drop-shadow(0 0 12px #FF6B6B)' }
                : { scale: 1, x: 0, filter: 'drop-shadow(0 0 0px transparent)' }}
            transition={{ duration: 0.25 }}
            style={{ width: 180, height: 'auto' }}
          />
        </div>

        {/* 思考泡泡尾巴 — 兩個小圓朝奶茶頭頂方向 */}
        <div style={{
          position: 'absolute', bottom: -20, left: '30%',
          width: 18, height: 18, borderRadius: '50%',
          background: '#FFFDF5', border: '4px solid #000',
        }} />
        <div style={{
          position: 'absolute', bottom: -42, left: '24%',
          width: 10, height: 10, borderRadius: '50%',
          background: '#FFFDF5', border: '3px solid #000',
        }} />
      </motion.div>

      {/* 奶茶（中央偏下、隨 beat 變 variant + 動作） */}
      <motion.div
        initial={false}
        animate={{ ...milkTeaAnimate, opacity: beatIndex >= 0 ? 1 : 0 }}
        transition={{ duration: 0.5, ease: OVERSHOOT }}
        style={{
          position: 'absolute', bottom: '18%', left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 11,
        }}
      >
        <MilkTea width={200} rotation={0} shadow={10} variant={milkTeaVariant} />

        {/* beat 2 / 3 happy 時頭旁飄 ✨ */}
        {(beatIndex === 2 || beatIndex === 3) && (
          <>
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, y: [0, -8, 0] }}
              transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
              style={{
                position: 'absolute', top: 10, left: -28,
                fontSize: 28, color: '#FFD93D',
                WebkitTextStroke: '2px #000', fontWeight: 900,
              }}
            >✦</motion.div>
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, y: [0, -10, 0] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
              style={{
                position: 'absolute', top: 20, right: -28,
                fontSize: 24, color: '#FFD93D',
                WebkitTextStroke: '2px #000', fontWeight: 900,
              }}
            >✦</motion.div>
          </>
        )}
      </motion.div>

      {/* + 粒子（綠 label → 大腦泡泡） */}
      {pluses.map(p => (
        <motion.div
          key={`plus-${p.id}`}
          initial={{ left: PLUS_SPAWN.left, top: PLUS_SPAWN.top, opacity: 1, scale: 1 }}
          animate={{ left: BUBBLE_CENTER_X, top: BUBBLE_CENTER_Y, opacity: [1, 1, 0], scale: [1, 1, 0.5] }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          onAnimationComplete={() => {
            setBrainFlash('plus');
            setTimeout(() => setBrainFlash(null), 250);
          }}
          style={{
            position: 'absolute',
            fontSize: 42, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '3px black',
            zIndex: 9, pointerEvents: 'none',
          }}
        >+</motion.div>
      ))}

      {/* − 粒子（紅 label → 大腦泡泡） */}
      {minuses.map(m => (
        <motion.div
          key={`minus-${m.id}`}
          initial={{ right: MINUS_SPAWN.right, top: MINUS_SPAWN.top, opacity: 1, scale: 1 }}
          animate={{ right: '50%', top: BUBBLE_CENTER_Y, opacity: [1, 1, 0], scale: [1, 1, 0.5] }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          onAnimationComplete={() => {
            setBrainFlash('minus');
            setTimeout(() => setBrainFlash(null), 250);
          }}
          style={{
            position: 'absolute',
            fontSize: 42, fontWeight: 900, color: '#FF6B6B',
            WebkitTextStroke: '3px black',
            zIndex: 9, pointerEvents: 'none',
          }}
        >−</motion.div>
      ))}

      {/* Beat 4 punchline */}
      <motion.div
        initial={false}
        animate={
          beatIndex >= 4
            ? aftermath
              ? { scale: 1, opacity: 1, y: 0, rotate: 1 }
              : { scale: 1, opacity: 1, y: 0, rotate: 0 }
            : { scale: 0.85, opacity: 0, y: 100, rotate: 0 }
        }
        transition={beatIndex >= 4 && aftermath
          ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
          : { duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        style={{
          position: 'absolute', bottom: 64, left: 0, right: 0, textAlign: 'center',
          zIndex: 20,
        }}
      >
        <span style={{
          background: '#FF6B6B', color: '#FFFDF5',
          padding: '24px 48px', border: '8px solid #000',
          boxShadow: aftermath ? '12px 12px 0 0 #000' : '16px 16px 0 0 #000',
          fontWeight: 900, fontSize: '3.5rem', display: 'inline-block', rotate: '-2deg',
          transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
        }}>
          跟 AI 訓練一模一樣
        </span>
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: 跑 lint 確認沒新警告**

```bash
cd demo/presentation && npm run lint
```

Expected: 沒新 error / warning。如果出現 `react-hooks/exhaustive-deps` 警告，檢查 useEffect 依賴；如果是無關 warning（其他檔已有），忽略。

- [ ] **Step 3: 跑全部測試**

```bash
cd demo/presentation && npm run test:run
```

Expected: 全 PASS（重點看 MilkTea + usePresentation 兩個 test 檔仍綠）。

- [ ] **Step 4: 啟 dev server 人眼驗收**

```bash
cd demo/presentation && npm run dev
```

打開瀏覽器、用 keyboard ←/→ 或 URL 跳到 `ch9 / step 5`，逐拍點擊：

驗收 checklist：
1. **Beat 0**：奶茶（中性表情）置中偏下、思考泡泡 + 大腦從上方淡入。畫面沒有女生 ghost。
2. **Beat 1**：左上彈出綠「回訊息」label、+ 粒子從 label 下方連發 → 飛向大腦泡泡 → 抵達時大腦短綠閃 + 微微脈衝。
3. **Beat 2**：奶茶換成 happy 變體（眼睛發亮 / 嘴角上揚 / 紫腮紅 / hand at chest）、整個 sticker 微前傾 + 向上移、頭旁飄兩顆黃色 ✦。+ 粒子繼續發射。
4. **Beat 3**：右上彈出紅「已讀不回」label、− 粒子從 label 下方連發 → 飛向大腦泡泡 → 抵達時大腦短紅閃 + 微抖。奶茶**仍是 happy 狀態**（保持笑容）。+ 粒子也仍在繼續發。
5. **Beat 4**（climax）：奶茶換成 crashed 變體（駝背 / 烏雲 / 沮喪線）+ 微灰階下沉。大腦 + 泡泡同時灰階。畫面 shake 一下、底部「跟 AI 訓練一模一樣」punchline 從下方彈入。

如果有任何一拍不對：對照 [spec §4](../specs/2026-05-22-ch9s5-redesign-design.md#4-beat-結構) + [§5](../specs/2026-05-22-ch9s5-redesign-design.md#5-動畫細節) 找出差異、修 `Ch9Step5.jsx`、再 Step 2 / 3 / 4 重跑。

- [ ] **Step 5: 截圖 5 拍（可選、做檔案存證）**

如果要存 demo 圖，把 5 張截圖放到 `apprentice/demo/` 下，命名 `_ch9s5_beat0.png` ~ `_ch9s5_beat4.png`（沿用 `_smoke_preview*.png` 既有命名慣例）。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx
git commit -m "feat(ch9 s5): thought bubble + milktea variants + 5-beat reaction flow"
```

如果有跑 Step 5 截圖，也一起加：

```bash
git add apprentice/demo/_ch9s5_beat*.png
git commit -m "docs(ch9 s5): smoke preview screenshots for 5-beat redesign"
```

---

## Final Verification

- [ ] **三個 commit 都在 main 上**：`git log --oneline -n 5` 應該能看到 MilkTea / beat-manifest / Ch9Step5 三個新 commit
- [ ] **`npm run test:run` 全 PASS**
- [ ] **`npm run lint` 無新警告**
- [ ] **`npm run build` 成功**（建議跑一下、確認 vite 沒在 import path 上抱怨）
- [ ] **手動跑完 ch9 s5 5 拍**、5 個驗收 checklist 全綠

---

## Notes

- **無 Ch9Step5 自動測試**：沿用 `chapters/` 其他 Step 元件「無單元測試」慣例。視覺與動畫部分靠人眼。日後若決定整片加 chapter step smoke test，再一起補。
- **`milk-tea-question.png`** 也順手 commit 進來，避免日後 ch7 s7 beat6 在新環境 checkout 時破圖（之前的 session 移過去後沒 commit）。
- **粒子飛行用 `left` / `top` 動畫**：motion 對百分比 + 絕對定位的 left/top 支援 ok，但若實機效能差、考慮改成 transform-only（先在 spawn 處 absolute 定位、用 `x` / `y` 偏移到 bubble）。
- **若 PNG 沒搬到 public/**：MilkTea 的 onError fallback 會顯示 AssetPlaceholder，不會破圖、但會看到 TODO 框框——這是預期行為。
