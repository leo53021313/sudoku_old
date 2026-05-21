# ch6 s3 奶茶 4-beats Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `demo/presentation/` 的 ch6 s3 從 1 beat 擴成 4 個 click beat（奶茶登場 → 名牌 → 女生並肩 → 字幕+`+`），並新增可優雅 fallback 的 `MilkTea` img2img 角色 motif。

**Architecture:** beat 數的唯一真相源是 `src/data/beat-manifest.js`；章節元件讀 `usePresentationContext().beatIndex` 做漸進揭示。新增 `MilkTea.jsx` 鏡像 `GirlNew.jsx`，但多一層 `onError` fallback 到 `AssetPlaceholder`（因為 PNG 尚未生成）。圖生圖 prompt 寫進 `demo/asset-production-ai-prompts.md` §6。

**Tech Stack:** React 19、motion（`motion/react`）、Vitest + @testing-library/react。

**設計來源：** [docs/superpowers/specs/2026-05-22-ch6-s3-milk-tea-beats-design.md](../specs/2026-05-22-ch6-s3-milk-tea-beats-design.md)

> **執行前先開分支**（目前在 `main`）：`git checkout -b feat/ch6-s3-milk-tea-beats`
> **語言：** 所有程式註解、commit message 用繁體中文（依使用者偏好）。
> **PNG 不在本計畫範圍**：使用者會自行生圖並放到 `public/images/ai/ch6/milk-tea.png`。

---

## 檔案結構

| 檔案 | 動作 | 責任 |
|---|---|---|
| `demo/presentation/src/data/beat-manifest.js` | 修改 | ch6 s3 → 4 beats；totalBeats 95→98 |
| `demo/presentation/src/state/usePresentation.test.js` | 修改 | totalBeats 斷言 95→98；新增 ch6 s3 4-beats 測試 |
| `demo/presentation/src/components/AiSticker.jsx` | 修改 | 新增 `onError` prop 轉接到 `<img>`（加法、不破壞既有） |
| `demo/presentation/src/motifs/MilkTea.jsx` | 新增 | 包 AiSticker，img 載入失敗 fallback 到 AssetPlaceholder |
| `demo/presentation/src/motifs/MilkTea.test.jsx` | 新增 | 預設渲染 sticker + error 時 fallback |
| `demo/presentation/src/chapters/ch6-sb3/Ch6Step3.jsx` | 改寫 | 讀 beatIndex 漸進揭示並肩相遇 |
| `demo/asset-production-ai-prompts.md` | 修改 | §6 新增 #13 `ch6-milk-tea` img2img prompt |

> 所有指令在 `demo/presentation/` 目錄下執行（除非另註）。

---

## Task 1: beat-manifest ch6 s3 擴成 4 beats

**Files:**
- Modify: `demo/presentation/src/data/beat-manifest.js`
- Test: `demo/presentation/src/state/usePresentation.test.js`

- [ ] **Step 1: 更新既有測試的 totalBeats 斷言（先讓它失敗）**

把 `usePresentation.test.js` 結尾這個測試由 95 改成 98：

```js
  it('reports totalBeats = 98', () => {
    const { result } = renderHook(() => usePresentation());
    expect(result.current.totalBeats).toBe(98);
  });
```

並在它前面新增一個 ch6 s3 的 beat 數測試：

```js
  it('ch6 step3 has 4 beats then crosses to step 4', () => {
    const { result } = renderHook(() => usePresentation({ chapterId: 6, stepId: 3 }));
    expect(result.current.beatIndex).toBe(0);            // milk-tea-enter
    act(() => result.current.advance());
    expect(result.current.stepId).toBe(3);
    expect(result.current.beatIndex).toBe(1);            // name-tag
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(2);            // girl-enter
    act(() => result.current.advance());
    expect(result.current.beatIndex).toBe(3);            // reply-plus
    act(() => result.current.advance());
    expect(result.current.stepId).toBe(4);               // 第 4 個 beat 後跨到 step 4
    expect(result.current.beatIndex).toBe(0);
  });
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `npm run test:run -- src/state/usePresentation.test.js`
Expected: FAIL — `totalBeats` 仍是 95、ch6 s3 仍只有 1 beat（advance 直接跨到 step 4）。

- [ ] **Step 3: 改 manifest — ch6 step3 的 beats 陣列**

在 `beat-manifest.js` 找到 ch6（`id: 6`）的 `steps` 裡這一行：

```js
        { id: 3, title: '新女生加分',   duration: 12, motifs: ['girl-new'], beats: [{ id: 'enter', type: 'click', cue: null, wait: null, scriptLines: 'L181-185' }] },
```

整行替換為：

```js
        { id: 3, title: '新女生加分',   duration: 16, motifs: ['girl-new', 'milk-tea'],
          beats: [
            { id: 'milk-tea-enter', type: 'click', cue: '今天有一個男生、頭髮奶茶色',           wait: null, scriptLines: 'L181-185' },
            { id: 'name-tag',       type: 'click', cue: '所以我們叫他奶茶',                       wait: null, scriptLines: 'L181-185' },
            { id: 'girl-enter',     type: 'click', cue: '奶茶遇見了一個女生、很想追',             wait: null, scriptLines: 'L181-185' },
            { id: 'reply-plus',     type: 'click', cue: '每次對方持續回訊息就覺得對方也喜歡他',   wait: null, scriptLines: 'L181-185' },
          ],
        },
```

- [ ] **Step 4: 改 manifest 頂部 totals**

把第 4-7 行的 totals 與註解由：

```js
// Beat manifest — encodes all 95 beats across 9 chapters / 58 steps.
// Source of truth: demo/outline.md per-step descriptions.

export const manifest = {
  totalChapters: 9,
  totalSteps: 58,
  totalBeats: 95,
```

改為：

```js
// Beat manifest — encodes all 98 beats across 9 chapters / 58 steps.
// Source of truth: demo/outline.md per-step descriptions.

export const manifest = {
  totalChapters: 9,
  totalSteps: 58,
  totalBeats: 98,
```

- [ ] **Step 5: 跑測試確認通過**

Run: `npm run test:run -- src/state/usePresentation.test.js`
Expected: PASS（全部綠）。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/data/beat-manifest.js demo/presentation/src/state/usePresentation.test.js
git commit -m "feat(demo): ch6 s3 擴成 4 beats（奶茶/名牌/女生/字幕）"
```

---

## Task 2: AiSticker onError + MilkTea motif（含 fallback）

**Files:**
- Modify: `demo/presentation/src/components/AiSticker.jsx`
- Create: `demo/presentation/src/motifs/MilkTea.jsx`
- Test: `demo/presentation/src/motifs/MilkTea.test.jsx`

- [ ] **Step 1: 寫失敗測試 MilkTea.test.jsx**

新檔 `demo/presentation/src/motifs/MilkTea.test.jsx`：

```jsx
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MilkTea } from './MilkTea.jsx';

describe('MilkTea', () => {
  it('預設渲染奶茶 AI sticker', () => {
    render(<MilkTea />);
    const img = screen.getByAltText('奶茶');
    expect(img.tagName).toBe('IMG');
    expect(img.getAttribute('src')).toBe('/images/ai/ch6/milk-tea.png');
  });

  it('圖片載入失敗時 fallback 到 AssetPlaceholder', () => {
    render(<MilkTea />);
    fireEvent.error(screen.getByAltText('奶茶'));
    expect(screen.getByLabelText('TODO: ch6-milk-tea')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: 跑測試確認失敗**

Run: `npm run test:run -- src/motifs/MilkTea.test.jsx`
Expected: FAIL — `MilkTea.jsx` 不存在（解析錯誤）。

- [ ] **Step 3: AiSticker 加 onError prop**

`demo/presentation/src/components/AiSticker.jsx` 第 1 行簽名與 `<img>` 改成：

```jsx
export function AiSticker({ src, alt = '', width = 280, rotation = -3, shadow = 8, onError }) {
  return (
    <div style={{
      display: 'inline-block',
      border: '4px solid #000',
      boxShadow: `${shadow}px ${shadow}px 0 0 #000`,
      transform: `rotate(${rotation}deg)`,
      background: '#FFFDF5',
      lineHeight: 0,
    }}>
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onError={onError}
        style={{ display: 'block', width, height: 'auto' }}
      />
    </div>
  );
}
```

- [ ] **Step 4: 建立 MilkTea.jsx**

新檔 `demo/presentation/src/motifs/MilkTea.jsx`：

```jsx
import { useState } from 'react';
import { AiSticker } from '../components/AiSticker.jsx';
import { AssetPlaceholder } from '../components/AssetPlaceholder.jsx';

// 奶茶 — img2img 角色（奶茶髮色 + 韓式鍋蓋頭）。
// PNG 尚未生成時，img onError → 改顯示 AssetPlaceholder，避免破圖；
// 使用者把檔案放到 public/images/ai/ch6/milk-tea.png 後自動顯示真圖。
export function MilkTea({ width = 300, rotation = -3, shadow = 12, ...rest }) {
  const [errored, setErrored] = useState(false);

  if (errored) {
    return <AssetPlaceholder type="[AI]" width={width} height={width} todo="ch6-milk-tea" />;
  }

  return (
    <AiSticker
      src="/images/ai/ch6/milk-tea.png"
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

- [ ] **Step 5: 跑測試確認通過（含 AiSticker 既有測試未被破壞）**

Run: `npm run test:run -- src/motifs/MilkTea.test.jsx src/components/AiSticker.test.jsx`
Expected: PASS（兩檔全綠）。

- [ ] **Step 6: Commit**

```bash
git add demo/presentation/src/components/AiSticker.jsx demo/presentation/src/motifs/MilkTea.jsx demo/presentation/src/motifs/MilkTea.test.jsx
git commit -m "feat(demo): 新增 MilkTea 角色 motif（img 失敗 fallback placeholder）+ AiSticker onError"
```

---

## Task 3: Ch6Step3 改寫成 4-beat 並肩相遇

**Files:**
- Modify (整檔覆寫): `demo/presentation/src/chapters/ch6-sb3/Ch6Step3.jsx`

> 章節視覺元件不做單元測試（與專案既有慣例一致——其他 ChNStepN 皆無測試）。驗收靠 `tsc`/lint + dev server 手動點測。

- [ ] **Step 1: 整檔覆寫 Ch6Step3.jsx**

把 `demo/presentation/src/chapters/ch6-sb3/Ch6Step3.jsx` 全部內容換成：

```jsx
import { motion } from 'motion/react';
import { useState, useEffect } from 'react';
import { usePresentationContext } from '../../state/PresentationContext.jsx';
import { GirlNew } from '../../motifs/GirlNew.jsx';
import { MilkTea } from '../../motifs/MilkTea.jsx';

// 沿用全片 sticker overshoot ease
const OVERSHOOT = [0.34, 1.56, 0.64, 1];

// 並肩 stage 尺寸（絕對定位，避免女生佔位導致奶茶 beat0 偏離置中）
const STAGE_W = 820;
const STAGE_H = 460;
const MILKTEA_W = 300;
const GIRL_W = 300;

export default function Ch6Step3() {
  const { beatIndex } = usePresentationContext();
  const [plusses, setPlusses] = useState([]);

  // + 浮動只在 beat 3 啟動
  useEffect(() => {
    if (beatIndex < 3) {
      setPlusses([]);
      return;
    }
    let id = 0;
    const t = setInterval(() => {
      setPlusses(prev => [
        ...prev,
        { id: id++, x: Math.random() * 80 + 10 },
      ].slice(-15));
    }, 400);
    return () => clearInterval(t);
  }, [beatIndex]);

  // 奶茶 beat0-1 置中、beat>=2 左移讓位給女生
  const milkTeaX = beatIndex >= 2 ? -200 : 0;

  return (
    <main style={{
      position: 'relative', zIndex: 20, height: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Space Grotesk', padding: 32,
    }}>
      {/* 並肩 stage */}
      <div style={{ position: 'relative', width: STAGE_W, height: STAGE_H }}>
        {/* 奶茶 + 名牌（置中基準 left，beat>=2 動畫左移） */}
        <motion.div
          initial={false}
          animate={{ x: milkTeaX }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{
            position: 'absolute', top: 0,
            left: (STAGE_W - MILKTEA_W) / 2,
            width: MILKTEA_W,
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16,
          }}
        >
          {/* 奶茶登場 beat0 */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5, ease: OVERSHOOT }}
          >
            <MilkTea width={MILKTEA_W} rotation={-3} shadow={12} />
          </motion.div>

          {/* 名牌「奶茶」 beat>=1 */}
          <motion.div
            initial={false}
            animate={beatIndex >= 1
              ? { scale: 1, opacity: 1 }
              : { scale: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: OVERSHOOT }}
            style={{
              background: '#FFD93D', color: '#000',
              padding: '8px 24px', border: '4px solid #000',
              boxShadow: '5px 5px 0 0 #000',
              fontWeight: 900, fontSize: 28, whiteSpace: 'nowrap',
            }}
          >
            奶茶
          </motion.div>
        </motion.div>

        {/* 女生 beat>=2 從右側滑入 */}
        <motion.div
          initial={false}
          animate={beatIndex >= 2
            ? { x: 0, opacity: 1 }
            : { x: 80, opacity: 0 }}
          transition={{ duration: 0.5, ease: OVERSHOOT }}
          style={{
            position: 'absolute', top: 20,
            left: STAGE_W - GIRL_W - 30,
            width: GIRL_W,
            pointerEvents: 'none',
          }}
        >
          <GirlNew width={GIRL_W} rotation={4} shadow={12} />
        </motion.div>
      </div>

      {/* + 浮動 beat3 */}
      {plusses.map(p => (
        <motion.div
          key={p.id}
          initial={{ y: 0, opacity: 1 }}
          animate={{ y: -300, opacity: 0 }}
          transition={{ duration: 2, ease: 'easeOut' }}
          style={{
            position: 'absolute', left: `${p.x}%`, bottom: '20%',
            fontSize: 48, fontWeight: 900, color: '#10B981',
            WebkitTextStroke: '2px black', pointerEvents: 'none',
          }}
        >
          +
        </motion.div>
      ))}

      {/* beat3 字幕 */}
      <motion.div
        initial={false}
        animate={beatIndex >= 3 ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          marginTop: 48, fontWeight: 700, fontSize: '1.5rem', color: '#000',
          textAlign: 'center', maxWidth: 900,
        }}
      >
        奶茶只要看到對方持續回覆訊息，就會覺得對方也喜歡他。
      </motion.div>
    </main>
  );
}
```

- [ ] **Step 2: 型別 / lint 檢查**

Run: `npx tsc --noEmit` （若無 tsconfig 則改跑 `npm run lint`）
Expected: 無錯誤。

- [ ] **Step 3: dev server 手動點測並微調位移**

Run: `npm run dev`，瀏覽器開 `localhost:5173/?chapter=6&step=3`（或用方向鍵移到 ch6 s3）。
逐項確認：
- beat0：只有奶茶 sticker、置中、overshoot scale-in。PNG 未就位時顯示 `[AI] ch6-milk-tea` placeholder、不破圖。
- beat1：奶茶下方彈出黃底名牌「奶茶」。
- beat2：奶茶左移、女生從右滑入並肩、兩人不重疊。**若重疊或偏移**，調整 `milkTeaX`（-200）、女生 `left`（`STAGE_W - GIRL_W - 30`）或 `STAGE_W`。
- beat3：字幕淡入 + 綠色 `+` 由下往上浮。
- 倒退鍵（←）逐 beat 可逆，回到 beat0 時 `+` 停止、女生與名牌消失。

- [ ] **Step 4: Commit**

```bash
git add demo/presentation/src/chapters/ch6-sb3/Ch6Step3.jsx
git commit -m "feat(demo): ch6 s3 並肩相遇 4-beat 漸進揭示（奶茶+名牌+女生+字幕）"
```

---

## Task 4: §6 新增 #13 ch6-milk-tea img2img prompt

**Files:**
- Modify: `demo/asset-production-ai-prompts.md`

> 純文件，無自動測試；驗收靠 read/grep。

- [ ] **Step 1: 在 §6.1 候選素材總表後、§6.2 個別 prompt 區塊新增 #13**

在 `demo/asset-production-ai-prompts.md` 的 §6.2 內，`#### 12. \`ch7-girl-veteran\`` 那一整段之後，加入：

````markdown
---

#### 13. `ch6-milk-tea` 奶茶（img2img 真人轉繪）

**用途**：[ch6 s3](outline.md) beat 0-1，奶茶角色登場 + 名牌「奶茶」；與 `ch6-girl-new` 並肩相遇
**原路線**：無（新角色）
**生成方式**：**img2img 編輯**——使用者連同一張真人照片一起貼給 Nano Banana 2 / GPT Image，要求保留本人臉部辨識度
**比例**：1:1 sticker（800×800）
**重點**：
- 保留照片本人五官辨識度（同臉型、同特徵），讓觀眾認得出是同一個人
- 奶茶髮色是這角色的名字哏 → **色票破例**：髮色用一個平塗的奶茶／淺棕色（刻意的一次性延伸），其餘維持五色票
- 韓式鍋蓋頭（圓蘑菇蓋）髮型要畫清楚
- 表情：友善、帶點期待（剛遇到喜歡的人）
- 紫上衣（與 girl-new 紅上衣形成並肩對比）
- **隱私**：prompt 與任何文件一律不寫真名，只用 "the person in the attached photo" 與暱稱「奶茶」

**Prompt (English, img2img — 連同照片一起貼)**:
```
[Paste shared style prefix from §3 above]

EDIT THE ATTACHED PHOTO: Redraw the real person in the photo in the flat
illustration style described above, while PRESERVING their facial likeness and
identity (same face shape, same features) so they stay recognizable. Keep their
milk-tea / light-brown hair COLOR — render it as a single FLAT milk-tea tan fill
(a deliberate one-off palette extension; this hair color is the character's whole
joke), bold black outline, no gradient. Keep the Korean bowl-cut / round
mushroom-cap hairstyle clearly readable. Redraw as bold black ink outline + flat
color fill only, NO photo texture, NO gradient, NO blur, NO 3D.
Pose: 3/4 front-facing, head and upper torso, a friendly slightly-hopeful
expression (a guy who just met someone he likes). Plain top in soft violet
#C4B5FD. Cream #FFFDF5 plain background. Character takes ~75% of canvas height,
centered, clean sticker cutout. NO text.
Aspect ratio: 1:1 square.
```

**驗收**：
- 一眼看出奶茶髮色 + 鍋蓋頭、且保留本人辨識度
- 線條粗細一致黑邊、平塗無漸層
- 除髮色奶茶棕外不出現五色票以外雜色、無文字
- 可乾淨剪成 sticker（透明 / cream 底）
- 落地路徑：`demo/presentation/public/images/ai/ch6/milk-tea.png`
````

- [ ] **Step 2: 驗收文件**

Run: `npx rg "ch6-milk-tea" demo/asset-production-ai-prompts.md`
Expected: 命中 `#### 13. \`ch6-milk-tea\`` 與落地路徑等行。

- [ ] **Step 3: Commit**

```bash
git add demo/asset-production-ai-prompts.md
git commit -m "docs(demo): asset-prompts §6 新增 #13 ch6-milk-tea img2img prompt"
```

---

## 完工檢查

- [ ] `npm run test:run`（全專案）綠燈。
- [ ] `npx tsc --noEmit` / `npm run lint` 無錯。
- [ ] dev server ch6 s3 連點 4 下依序揭示、倒退可逆。
- [ ] PNG 未就位顯示 placeholder、就位後自動顯示真圖（使用者放檔後驗）。
- [ ] 全片 `totalBeats` = 98、游標前進後退無錯位。
