# ch9 s5 視覺重設計（思考泡泡 + 奶茶反應）

> **狀態**：已對齊（2026-05-22）
> **章節定位**：ch9 callback / step 5「戀愛 a callback」
> **腳本對應**：[demo/script_new.md](../../../demo/script_new.md) ch9 s5（L313-317）
> **manifest 對應**：[demo/presentation/src/data/beat-manifest.js:175-182](../../../demo/presentation/src/data/beat-manifest.js#L175-L182)
> **現有實作**：[demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx](../../../demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx)

---

## 1. 背景與問題

ch9 s5 的腳本核心是「**AI 加減分的過程其實跟奶茶的腦袋在做的事是一樣的**」——把 AI training 的 reward signal 比喻為奶茶（人類）在追求對象時、大腦對「回訊息 / 已讀不回」做出的加減分反應，最後 climax 揭曉「跟 AI 訓練一模一樣」。

**現況問題**（驗收實機畫面）：

1. 奶茶 sticker 與 brain-reward sticker 被放成兩個並排的獨立卡片，看起來像兩張無關照片，無法傳達「那顆大腦是奶茶的」
2. 背景的 ghost 女生 opacity 太低，幾乎看不到
3. +/− 粒子分別在左右兩側飄、跟中央的奶茶 / 大腦無視覺連線、看不出是「訊息造成的反應」
4. 奶茶在 beat 1 / 2 / 3 完全沒反應，僅靠粒子位置變化敘事
5. punchline 與奶茶 / 大腦疊在同一個垂直區域、視覺擁擠

## 2. 設計目標

- **明確的擁有關係**：一眼看出「大腦 = 奶茶的腦」
- **明確的因果鏈**：訊息 (回訊息 / 已讀不回) → +/− 粒子 → 進入大腦 → 奶茶情緒外顯
- **情緒對比**：beat 1-2 上揚（happy）vs beat 4 崩潰（crashed），對比 climax
- **保留既有 climax 機制**：punchline、`useClimax(['A','C'])`、`triggerShake()` 不重發明

## 3. 構圖（Composition）

採用「思考泡泡 / Thought Bubble」版面（brainstorm 階段選擇 Option A）：

```
┌──────────────────────────────────────────┐
│ [回訊息]                       [已讀不回] │
│   ↓                                ↓     │
│                ┌────────┐                 │
│                │ 🧠 brain│  ← 思考泡泡    │
│                │  +-+-+  │                │
│                └────╮╭───┘                │
│                     ○                     │
│                      ○                    │
│                   ┌────┐                  │
│                   │奶茶│                  │
│                   └────┘                  │
│                                           │
│       [跟 AI 訓練一模一樣]                 │
└──────────────────────────────────────────┘
```

| 元素 | 位置 | 尺寸 | 備註 |
|---|---|---|---|
| 奶茶 sticker | 中央偏下 | 200px wide | 三個變體在不同 beat 切換 |
| 思考泡泡 | 奶茶頭頂偏右 | 圓形邊框、`border-radius: 50%` | CSS 純樣式、不用圖片 |
| 大腦（brain-reward.png） | 泡泡內部 | 180px wide | 沿用既有資產 `public/images/ai/ch9/brain-reward.png` |
| 泡泡尾巴 | 泡泡左下 → 奶茶頭右上 | 兩個圓 (14px, 8px) | 經典漫畫思考泡泡語彙 |
| 「回訊息」label | 左上 (`top: 12px, left: 12px`) | 既有樣式 | 綠 #10B981 |
| 「已讀不回」label | 右上 (`top: 12px, right: 12px`) | 既有樣式 | 紅 #FF6B6B |
| punchline「跟 AI 訓練一模一樣」 | 底中央 | 既有樣式 | 紅 sticker + climax |
| **女生（GirlNew ghost）** | **移除** | — | 拿掉，畫面更聚焦 |

## 4. Beat 結構

beat 數從 **4 拍 → 5 拍**，在原本 beat 1 (`left-positive`) 與 beat 2 (`right-negative`) 之間插入「奶茶 happy 反應」beat。

| Beat | id | cue | type | wait | scriptLines | climax |
|---|---|---|---|---|---|---|
| 0 | `bg-callback` | 追一個人的時候—— | click | null | L313 | — |
| 1 | `left-positive` | 對方回訊息你就被加分 | click | 1s | L313 | — |
| 2 | **`milktea-happy`** ← 新增 | null (無 cue) | click | 0.8s | L315 | — |
| 3 | `right-negative` | 已讀不回你就被扣分 | click | 1.5s | L315 | — |
| 4 | `punchline-hero` | 你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練 | click | 2s | L317 | ['A','C'] |

**奶茶狀態切換**：

- beat 0-1：`milk-tea.png` (neutral)
- beat 2-3：`milk-tea-happy.png` (excited / 心動)
  - beat 3 時雖然 − 粒子進入，奶茶**仍保持 happy**——「他還在笑就已經死了」的喜劇 timing
- beat 4：`milk-tea-crashed.png` (defeated / 崩潰) + grayscale

## 5. 動畫細節

### 5.1 粒子（+ / −）

- **發射源**：
  - `+` 從綠「回訊息」label 中心點下方 spawn
  - `−` 從紅「已讀不回」label 中心點下方 spawn
- **路徑**：用 framer-motion / motion 的 `animate={{ x, y }}` 從 label 下方走貝茲曲線到大腦泡泡中心（從外緣斜向內）
- **頻率**：每 300ms 一顆、beat 啟動後最多 10 顆 buffer（沿用既有 `setInterval` 寫法）
- **持續期**：每顆 `duration: 1.2s, ease: 'easeOut'`
- **抵達 callback**：用 `onAnimationComplete` 觸發 brain flash
- **生命週期**：beat 1 啟動 + 發射，beat 3 啟動 − 發射；兩種粒子可同框存在 (beat 3 時 + 已停止 spawn 但仍可能有殘留在飛)

### 5.2 大腦 flash

每顆粒子抵達泡泡時：
- `+` 抵達 → brain 短綠閃 (`box-shadow: 0 0 0 8px rgba(16,185,129,0.4)` 200ms 漸出)
- `−` 抵達 → brain 短紅閃 + 微抖 (`box-shadow` 紅 + `x` shake [-4, 4, -2, 0] 200ms)

實作上可用一個 `flashCount` state、每次 callback 觸發時 increment，brain 內部聽 state 觸發 motion animate prop。

### 5.3 奶茶反應

- **beat 2 → happy**：
  - `MilkTea` variant prop 切到 `happy`
  - 整個奶茶 motion.div 略前傾：`rotate: -3 → 2`、`y: 0 → -8`、`scale: 1 → 1.05`
  - 頭旁 absolute 飄 ✨ 兩顆 (CSS 4 角星 + 黃色 #FFD93D)
  - 動畫 `duration: 0.5s, ease: OVERSHOOT`
- **beat 4 → crashed**：
  - `MilkTea` variant prop 切到 `crashed`
  - `filter: grayscale(0.7)` 微灰階
  - `y: -8 → 16`、`rotate: 2 → -5`、`scale: 1.05 → 0.95` (整個下沉)
  - 頭頂烏雲視 PNG 內已畫即可（prompt 已要求）
  - 同時觸發 `triggerShake()` + `climax.play()`

### 5.4 思考泡泡

- 純 CSS：`border: 4px solid #000` + `border-radius: 50%` + `box-shadow: 6px 6px 0 0 #000`
- 兩個尾巴小圓：`position: absolute` + `border-radius: 50%`，從泡泡左下出發到奶茶頭右上
- beat 0 進場：`scale: 0 → 1` + `opacity: 0 → 1`、`ease: OVERSHOOT`
- beat 4 climax：`filter: grayscale(1)`，整個泡泡 + 內部大腦同時褪色

### 5.5 punchline

沿用既有結構：beat 4 才出現、紅 sticker、`aftermath` state 控制 box-shadow 收緊（既有 climax 規範）。

## 6. 資產需求

### 6.1 新增 (img2img 生成、prompt 已寫好)

| 檔名 | prompt 來源 | 用途 |
|---|---|---|
| `demo/presentation/public/images/ai/ch6/milk-tea-happy.png` | [asset-production-ai-prompts.md §6.2 #14](../../../demo/asset-production-ai-prompts.md) | beat 2-3 happy 變體 |
| `demo/presentation/public/images/ai/ch6/milk-tea-crashed.png` | [asset-production-ai-prompts.md §6.2 #15](../../../demo/asset-production-ai-prompts.md) | beat 4 crashed 變體 |

**驗收紅線**：三張並排 (`milk-tea.png` / `milk-tea-happy.png` / `milk-tea-crashed.png`) 必須能讀為「同一個奶茶的三個情緒狀態」。若辨識度斷裂 (像不同人) 須 retry。

### 6.2 沿用（已存在）

- `demo/presentation/public/images/ai/ch6/milk-tea.png`
- `demo/presentation/public/images/ai/ch6/milk-tea-question.png`（v1 困惑變體；本次不使用，但保留）
- `demo/presentation/public/images/ai/ch9/brain-reward.png`

### 6.3 元件變更

**[demo/presentation/src/motifs/MilkTea.jsx](../../../demo/presentation/src/motifs/MilkTea.jsx)**：擴充 `VARIANT_SRC`：

```js
const VARIANT_SRC = {
  normal: '/images/ai/ch6/milk-tea.png',
  question: '/images/ai/ch6/milk-tea-question.png',
  happy: '/images/ai/ch6/milk-tea-happy.png',     // 新增
  crashed: '/images/ai/ch6/milk-tea-crashed.png', // 新增
};
```

`AssetPlaceholder` fallback 的 `todo` slug 也對應四個 variant。

## 7. manifest 變更

[demo/presentation/src/data/beat-manifest.js:175-182](../../../demo/presentation/src/data/beat-manifest.js#L175-L182)：

```js
{ id: 5, title: '戀愛 a callback', duration: 22, punchline: true, motifs: [], climax: ['A', 'C'],
  beats: [
    { id: 'bg-callback',     type: 'click', cue: '追一個人的時候——', wait: null, scriptLines: 'L313' },
    { id: 'left-positive',   type: 'click', cue: '對方回訊息你就被加分', wait: '1s', scriptLines: 'L313' },
    { id: 'milktea-happy',   type: 'click', cue: null, wait: '0.8s 觀眾消化反應', scriptLines: 'L315' },
    { id: 'right-negative',  type: 'click', cue: '已讀不回你就被扣分', wait: '1.5s', scriptLines: 'L315' },
    { id: 'punchline-hero',  type: 'click', cue: '你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練', wait: '2s', climax: ['A', 'C'], scriptLines: 'L317' },
  ],
},
```

- `motifs: ['girl-new']` → `motifs: []`（拿掉 girl-new motif）
- `duration: 18 → 22`（多一拍 + 多消化時間）
- `totalBeats: 99 → 100`：
  - `manifest.totalBeats` 物件欄位手動改為 100（純宣告用、source of truth 是 `flattenBeats().length`）
  - `usePresentation.js` 的 `TOTAL` 自動從 `flattenBeats()` 算出，無需動
  - `ProgressBar.jsx` 自動跟著 `totalBeats` 算百分比、無需動
  - **`demo/presentation/src/state/usePresentation.test.js:102`** 寫死 `expect(result.current.totalBeats).toBe(99)`、需同步改為 `100`

### 7.1 `motifs: []` 是否安全

`grep` 確認 `step.motifs` 在 `src/` 目前**沒有任何讀取點**（純標註用），把 `'girl-new'` 拿掉不影響任何邏輯。

## 8. 實作範圍與順序

1. **MilkTea.jsx** — 加 happy / crashed variant 註冊
2. **beat-manifest.js** — 4 → 5 拍 + 拿掉 motifs + `totalBeats: 99 → 100`
3. **usePresentation.test.js** — `expect(...toBe(99))` → `100`
4. **Ch9Step5.jsx** — 重寫構圖
   - 拿掉 `GirlNew` import 與 ghost 區塊
   - 拿掉舊的左右兩欄粒子 layout
   - 新增思考泡泡 div + 內部 brain
   - 新增 +/− 粒子的 label-to-bubble 路徑 motion
   - 新增 brain flash state + animation
   - 新增 beat 2 / 4 的 milk-tea variant 切換 + 反應動畫
   - 沿用既有 climax / triggerShake / punchline

5. **commit + 推（人手）** — 三個圖未生成前 fallback 走 AssetPlaceholder、可先合並、之後補圖

## 9. 不在本次範圍

- 其他章節對 girl-new motif 的依賴 (ch6 s3) 不動
- `milk-tea-question.png` 在 ch7 s7 的用法不動
- 不新增音效 / 額外 climax 視覺
- 不調整 `usePresentation` 或 beat 推進邏輯
- punchline 文案不改、climax fx slot (['A','C']) 不改

## 10. 驗收

- [ ] 點擊 5 次完成 5 拍、節奏與 cue 對齊腳本
- [ ] 三個奶茶 variant 切換時辨識度連續（看得出是同一人）
- [ ] + 粒子明顯從綠 label 飛入大腦泡泡、抵達時 brain 綠閃
- [ ] − 粒子對稱、抵達時 brain 紅閃 + 微抖
- [ ] beat 4 punchline 進場、screen shake、brain grayscale 同時發生
- [ ] 拿掉女生後畫面不空（聚焦於奶茶 + 大腦）
- [ ] 與既有 ch6 s3 / ch7 s7 / ch9 s6 視覺風格一致（同 sticker 風、同色票）
- [ ] 三個圖未生成時 fallback 到 AssetPlaceholder、不破圖
