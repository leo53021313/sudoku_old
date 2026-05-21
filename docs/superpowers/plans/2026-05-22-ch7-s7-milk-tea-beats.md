# ch7 s7 奶茶 7-beats Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把簡報 ch7 step 7「老油條 ★★★」從 6 beats 擴成 7 beats，把整段主角改為奶茶（左右對峙：奶茶 vs 老油條女生），新增開場「看攻略」與結尾「人都傻了」freeze 特效，沿用既有 climax/FX 機制。

**Architecture:** beat 數真相源 `src/data/beat-manifest.js`；章節元件讀 `usePresentationContext().beatIndex`。`Ch7Step7.jsx` 既有的 climax（`useClimax`）/ spotlight / aftermath / anticipation 機制全部保留，beat 閾值整體 +1，移除原 auto-advance，加入奶茶（翻轉面向右 + grayscale freeze + 浮動 ❓）與「戀愛攻略」[D] sticker。

**Tech Stack:** React 19、motion（`motion/react`）、Vitest。無新 AI 素材（`milk-tea.png` / `girl-veteran.png` 已就位）。

**設計來源：** [docs/superpowers/specs/2026-05-22-ch7-s7-milk-tea-beats-design.md](../specs/2026-05-22-ch7-s7-milk-tea-beats-design.md)

> **執行前先開分支**（目前在 `main`）：`git checkout -b feat/ch7-s7-milk-tea-beats`
> **語言：** 程式註解、commit message 用繁體中文。
> 指令在 `demo/presentation/` 下執行。

---

## 檔案結構

| 檔案 | 動作 | 責任 |
|---|---|---|
| `src/data/beat-manifest.js` | 修改 | ch7 s7 → 7 beats；totalBeats 98→99 |
| `src/state/usePresentation.test.js` | 修改 | totalBeats 斷言 98→99；新增 ch7 s7 7-beats 測試 |
| `src/chapters/ch7-reasoner/Ch7Step7.jsx` | 整檔覆寫 | 左右對峙 7-beat + 奶茶 freeze |

---

## Task 1: beat-manifest ch7 s7 擴成 7 beats

**Files:**
- Modify: `demo/presentation/src/data/beat-manifest.js`
- Test: `demo/presentation/src/state/usePresentation.test.js`

- [ ] **Step 1: 更新測試（先讓它失敗）**

把 `usePresentation.test.js` 的 `reports totalBeats = 98` 測試改成 99：

```js
  it('reports totalBeats = 99', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(99);
  });
```

並在它前面新增：

```js
  it('ch7 step7 has 7 beats then crosses to step 8', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 7, stepId: 7 }));
    expect(result.current.beatIndex).toBe(0);
    for (let i = 1; i <= 6; i++) {
      act(() => result.current.advance());
      expect(result.current.stepId).toBe(7);
      expect(result.current.beatIndex).toBe(i);
    }
    act(() => result.current.advance());      // 第 7 個 beat 後跨到 step 8
    expect(result.current.stepId).toBe(8);
    expect(result.current.beatIndex).toBe(0);
  });
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `npm run test:run -- src/state/usePresentation.test.js`
Expected: FAIL — totalBeats 仍 98、ch7 s7 仍 6 beats（第 7 次 advance 前就跨到 step 8）。

- [ ] **Step 3: 改 manifest — ch7 step7 的 beats 陣列**

在 `beat-manifest.js` 找到 ch7（`id: 7`）的 step 7 整段（由 `{ id: 7, title: '老油條 ★★★', ...` 到對應的 `},`），整段替換為：

```js
        { id: 7, title: '老油條 ★★★',  duration: 30, punchline: true, starLevel: 3, motifs: ['milk-tea', 'girl-veteran', 'yellow-highlight'], climax: ['A', 'G', 'B'],
          beats: [
            { id: 'milk-tea-study',  type: 'click', cue: '奶茶為了雪恥、看了一堆與女生聊天的攻略、以為這次能更進一步', wait: '0.5s', scriptLines: 'L296' },
            { id: 'girl-traps',      type: 'click', cue: '結果女生直接出陷阱題給他', wait: '0.5s', scriptLines: 'L298' },
            { id: 'trap-1',          type: 'click', cue: '例如——和你媽一起掉進水裡你會先救誰？', wait: '2s 觀眾笑', scriptLines: 'L298' },
            { id: 'trap-2-question', type: 'click', cue: '又例如『你覺得我該不該去運動？』', wait: '1s', scriptLines: 'L300' },
            { id: 'answer-a-fill',   type: 'click', cue: '你答該去運動——那就是嫌那個女生胖', wait: '2s 笑點', climax: ['A', 'G'], scriptLines: 'L302' },
            { id: 'answer-b-fill',   type: 'click', cue: '你答不用——那就是不關心女生的身體健康', wait: '2s 笑點', climax: ['A', 'G'], scriptLines: 'L304' },
            { id: 'milk-tea-freeze', type: 'click', cue: '奶茶一看人都傻了、網路上也沒有正確解答', wait: '2-3s', climax: ['B'], scriptLines: 'L306' },
          ],
        },
```

（注意：原本最後一個 beat `both-flash` 是 `type: 'auto'`，新版改為 7 個 `click` beat，無 auto。）

- [ ] **Step 4: 改 manifest 頂部 totals**

把檔案最上方的 totals 與註解由 `98` 改 `99`：

```js
// Beat manifest — encodes all 99 beats across 9 chapters / 58 steps.
// Source of truth: demo/outline.md per-step descriptions.

export const manifest = {
  totalChapters: 9,
  totalSteps: 58,
  totalBeats: 99,
```

- [ ] **Step 5: 跑測試確認通過**

Run: `npm run test:run -- src/state/usePresentation.test.js`
Expected: PASS（全綠）。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/data/beat-manifest.js demo/presentation/src/state/usePresentation.test.js
git commit -m "feat(demo): ch7 s7 擴成 7 beats（奶茶看攻略→陷阱題→傻了）"
```

---

## Task 2: Ch7Step7 改寫成左右對峙 7-beat + 奶茶 freeze

**Files:**
- Modify（整檔覆寫）: `demo/presentation/src/chapters/ch7-reasoner/Ch7Step7.jsx`

> 章節視覺元件不寫單元測試（與專案慣例一致）。驗收靠 lint/build + dev server 點測。

- [ ] **Step 1: 整檔覆寫 Ch7Step7.jsx 為下列內容**

```jsx
import { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { useClimax } from '../../climax/useClimax.js';
import { SpotlightVignette } from '../../motifs/SpotlightVignette.jsx';
import { GirlVeteran } from '../../motifs/GirlVeteran.jsx';
import { MilkTea } from '../../motifs/MilkTea.jsx';

const OVERSHOOT = [0.34, 1.56, 0.64, 1];

export default function Ch7Step7() {
  const { beatIndex, triggerShake } = usePresentationContext();
  const climaxA = useClimax(['A', 'G']);   // beat 4
  const climaxB = useClimax(['A', 'G']);   // beat 5
  const climaxBoth = useClimax(['B']);     // beat 6（雙爆）
  const firedA = useRef(false);
  const firedB = useRef(false);
  const firedBoth = useRef(false);
  const [aftermathA, setAftermathA] = useState(false);
  const [aftermathB, setAftermathB] = useState(false);

  useEffect(() => {
    if (beatIndex === 4 && !firedA.current) {
      firedA.current = true;
      climaxA.play();
      triggerShake();
      const t = setTimeout(() => setAftermathA(true), 700);
      return () => clearTimeout(t);
    }
    if (beatIndex === 5 && !firedB.current) {
      firedB.current = true;
      climaxB.play();
      triggerShake();
      const t = setTimeout(() => setAftermathB(true), 700);
      return () => clearTimeout(t);
    }
    if (beatIndex === 6 && !firedBoth.current) {
      firedBoth.current = true;
      climaxBoth.play();
      triggerShake();
    }
  }, [beatIndex, climaxA, climaxB, climaxBoth, triggerShake]);

  const anticipationActive = beatIndex === 3;
  const frozen = beatIndex >= 6;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32, gap: 24,
    }}>
      <SpotlightVignette active={climaxA.activeFX.G || climaxB.activeFX.G} />

      {/* 奶茶 — 左、翻轉面向右；beat6 灰階 freeze + 浮動 ❓ */}
      <motion.div
        initial={false}
        animate={beatIndex >= 0 ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: OVERSHOOT }}
        style={{
          position: 'absolute', left: 60, bottom: 100, zIndex: 15,
          filter: frozen ? 'grayscale(1)' : 'none',
          transition: 'filter 0.4s ease',
        }}
      >
        {/* 翻轉讓奶茶面向右側女生 */}
        <div style={{ transform: 'scaleX(-1)' }}>
          <MilkTea width={220} rotation={-3} shadow={10} />
        </div>

        {/* 戀愛攻略 [D] sticker */}
        <motion.div
          initial={false}
          animate={beatIndex >= 0 ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.4, delay: 0.5 }}
          style={{
            position: 'absolute', right: -36, bottom: 8,
            background: '#FFD93D', color: '#000',
            padding: '6px 14px', border: '4px solid #000', boxShadow: '4px 4px 0 0 #000',
            fontWeight: 900, fontSize: 16, whiteSpace: 'nowrap',
            transform: 'rotate(-8deg)',
          }}
        >
          戀愛攻略
        </motion.div>

        {/* freeze 浮動 ❓❓❓ */}
        {frozen && [0, 1, 2].map(i => (
          <motion.div
            key={i}
            initial={{ y: 0, opacity: 0, scale: 0.5 }}
            animate={{ y: -70, opacity: [0, 1, 1, 0], scale: 1 }}
            transition={{ duration: 1.6, repeat: Infinity, delay: i * 0.3, ease: 'easeOut' }}
            style={{
              position: 'absolute', top: -20, left: 40 + i * 34,
              fontSize: 40, fontWeight: 900, color: '#FF3B30',
              WebkitTextStroke: '2px #000', pointerEvents: 'none', zIndex: 16,
            }}
          >
            ?
          </motion.div>
        ))}
      </motion.div>

      {/* 老油條女生 — 右、beat>=1 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1
          ? { scale: 1, opacity: 1, rotate: 4 }
          : { scale: 0, opacity: 0, rotate: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: OVERSHOOT }}
        style={{ position: 'absolute', top: 60, right: 60, zIndex: 15 }}
      >
        <GirlVeteran width={220} rotation={0} shadow={10} />
      </motion.div>

      {/* Beat 1: 標題 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 1 ? { clipPath: 'inset(-24px)', opacity: 1 } : { clipPath: 'inset(0px 100% 0px 0px)', opacity: 0 }}
        transition={{ duration: 0.8 }}
        style={{ fontWeight: 900, fontSize: '3rem' }}
      >
        <span style={{ background: '#FFD93D', padding: '4px 24px', border: '6px solid #000', boxShadow: '8px 8px 0 0 #000' }}>
          女生陷阱題
        </span>
      </motion.div>

      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        {/* Beat 2: 陷阱題 1（左） */}
        <motion.div
          initial={false}
          animate={beatIndex >= 2 ? { rotate: -3, x: 0, opacity: 1 } : { rotate: -30, x: -200, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{
            background: '#FF6B6B', color: '#FFF',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          和你媽一起<br/>掉進水裡<br/>你會先救誰？
        </motion.div>

        {/* Beat 3: 陷阱題 2（右） */}
        <motion.div
          initial={false}
          animate={beatIndex >= 3 ? { rotate: 4, x: 0, opacity: 1 } : { rotate: 30, x: 200, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{
            background: '#C4B5FD', color: '#000',
            padding: '24px 32px', border: '6px solid #000', boxShadow: '12px 12px 0 0 #000',
            fontWeight: 900, fontSize: '1.5rem', maxWidth: 320, lineHeight: 1.3, textAlign: 'center',
          }}
        >
          你覺得我<br/>該不該去<br/>運動？
        </motion.div>
      </div>

      {/* 答案箭頭 + 填空 — beat>=3 顯示，beat>=4/5 填入 */}
      <div style={{ display: 'flex', gap: 48, marginTop: 32 }}>
        <motion.div
          initial={false}
          animate={{ opacity: beatIndex >= 3 ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}
        >
          說要 →
          <motion.span
            initial={false}
            animate={
              beatIndex >= 4
                ? aftermathA
                  ? { scale: 1, rotate: 1, opacity: 1 }
                  : { scale: [0.9, 1.2, 1], rotate: 0, opacity: 1 }
                : anticipationActive
                  ? { scale: [0.9, 0.915, 0.885, 0.9], rotate: [0, 0.6, -0.4, 0], opacity: 0.4 }
                  : { scale: 0.9, rotate: 0, opacity: beatIndex >= 3 ? 0.4 : 0 }
            }
            transition={
              beatIndex >= 4
                ? aftermathA
                  ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
                  : { duration: 0.4 }
                : anticipationActive
                  ? { duration: 1.4, repeat: Infinity, ease: 'linear' }
                  : { duration: 0.4 }
            }
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px',
              border: '4px solid #000',
              boxShadow: aftermathA ? '2px 2px 0 0 #000' : '4px 4px 0 0 #000',
              display: 'inline-block',
              transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
            }}
          >
            {beatIndex >= 4 ? '❌ 嫌那個女生胖' : '❌ ???'}
          </motion.span>
        </motion.div>
        <motion.div
          initial={false}
          animate={{ opacity: beatIndex >= 3 ? 1 : 0 }}
          transition={{ duration: 0.4 }}
          style={{ minWidth: 340, textAlign: 'center', fontWeight: 700, fontSize: 18 }}
        >
          說不用 →
          <motion.span
            initial={false}
            animate={
              beatIndex >= 5
                ? aftermathB
                  ? { scale: 1, rotate: 1, opacity: 1 }
                  : { scale: [0.9, 1.2, 1], rotate: 0, opacity: 1 }
                : anticipationActive
                  ? { scale: [0.9, 0.915, 0.885, 0.9], rotate: [0, -0.6, 0.4, 0], opacity: 0.4 }
                  : { scale: 0.9, rotate: 0, opacity: beatIndex >= 3 ? 0.4 : 0 }
            }
            transition={
              beatIndex >= 5
                ? aftermathB
                  ? { duration: 0.35, ease: [0.22, 1, 0.36, 1] }
                  : { duration: 0.4 }
                : anticipationActive
                  ? { duration: 1.4, repeat: Infinity, ease: 'linear' }
                  : { duration: 0.4 }
            }
            style={{
              marginLeft: 8,
              background: '#FF6B6B', color: '#FFF',
              padding: '4px 12px',
              border: '4px solid #000',
              boxShadow: aftermathB ? '2px 2px 0 0 #000' : '4px 4px 0 0 #000',
              display: 'inline-block',
              transition: 'box-shadow 0.35s cubic-bezier(0.22, 1, 0.36, 1)',
            }}
          >
            {beatIndex >= 5 ? '❌ 你不關心健康' : '❌ ???'}
          </motion.span>
        </motion.div>
      </div>

      {/* Beat 6: 兩面不討好 punchline */}
      {beatIndex >= 6 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          style={{
            marginTop: 32, fontWeight: 900, fontSize: 24,
            background: '#FFD93D', color: '#000',
            padding: '12px 28px', border: '4px solid #000', boxShadow: '6px 6px 0 0 #000',
          }}
        >
          兩面不討好
        </motion.div>
      )}
    </main>
  );
}
```

- [ ] **Step 2: lint 檢查**

Run: `npm run lint`
Expected: 不新增任何 error（與覆寫前相比，Ch7Step7 不應有新 lint 問題；若 `react-hooks/set-state-in-effect` 之類觸發，比照 ch6 做法用 `setTimeout(fn, 0)` 包裹並加 cleanup）。回報實際結果。

- [ ] **Step 3: build 驗證可編譯**

Run: `npm run build`
Expected: 成功 build、無錯誤。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch7-reasoner/Ch7Step7.jsx
git commit -m "feat(demo): ch7 s7 左右對峙 7-beat（奶茶看攻略→陷阱題→灰階傻了）"
```

---

## 完工檢查

- [ ] `npm run test:run`（全專案）綠燈。
- [ ] `npm run build` / `npm run lint` 無新錯。
- [ ] dev server ch7 s7 連點 7 下依序揭示、倒退可逆；beat6 奶茶灰階 + ❓ + 兩面不討好 + 雙爆。
- [ ] 全片 `totalBeats=99`，游標前進後退無錯位。
