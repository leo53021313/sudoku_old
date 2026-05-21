# ch4 step2 — 夯/拉完了 tier-list sticker 動畫節奏設計

**日期:** 2026-05-21
**範圍:** `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`
**相關:** `demo/presentation/src/data/beat-manifest.js` (ch4 step2 已是 4 beats，本 spec 不變動 manifest)

## 目標

把目前 ch4 step2 的 tier-list 排行榜 (5 列：夯／顶级／人上人／NPC／拉完了) 動畫從「sticker 直接在 slot 中央 spawn → 滑到目標 row」改成「sticker showcase 大尺寸出場 → 縮小 dock 進 row 左側」的兩段式節奏，並讓排行榜在 showcase 階段隱藏或虛化，凸顯當下講解的 sticker。

## 逐 beat 行為

| Beat | Tier list | supervised | RL 增強式訓練 |
|------|-----------|------------|---------------|
| 0 | 隱藏 (opacity 0) | **大** 在 table 中央 (scale ≈ 1.8) | 不存在 (opacity 0, scale 0.2) |
| 1 | 實化 fade-in (opacity 1, no blur) | 縮小 + 滑進 **拉完了** row、靠左 dock | 不存在 |
| 2 | 虛化 (opacity 0.35, filter blur 3px) | 維持 dock，跟 table 一起 dim (opacity 0.35 + blur) | **大** 在 table 中央 (scale ≈ 1.8) |
| 3 | 實化 (opacity 1, blur 0) | dock 在拉完了，回到 crisp (opacity 1, no blur) | 縮小 + 滑進 **夯** row、靠左 dock |

「showcase 大」與「dock 小」是同一個 motion 元件不同的目標 state，由 Framer Motion 直接 tween；不開兩個 component、不用 `layoutId`。

## Dock 位置定義

Sticker docked 時：
- **視覺左邊緣** = `LABEL_W + DIVIDER + DOCK_INSET`，其中 `DOCK_INSET = 16`px。
- 透過 `transformOrigin: 'left center'` + `x: 0` 達成 — sticker 自己的座標 `left` 即視覺左緣，不再用 `x: '-50%'` 居中。
- 不擋 label 右邊框 (`DIVIDER` 是 borderTop 的 3 px，DOCK_INSET 還預留 16 px gap)。

對應的垂直位置：
- `top: slotCenter(rowIdx).top` (row 中軸)
- `y: '-50%'` 仍保留，視覺垂直居中。

## Showcase 位置定義

Sticker 在「大」狀態時：
- `left: TABLE_W / 2, top: TABLE_H / 2`，即 table 容器的正中。
- `transformOrigin: 'center center'`，`x: '-50%', y: '-50%'` 標準居中。
- `scale: 1.8`。

> 因為 tier table 在 showcase beat 是 `opacity 0` (beat 0) 或 dim (beat 2)，大 sticker 蓋過去也沒視覺衝突。

## Dim 模式

**Tier table 容器：**
- beat 0: `opacity: 0`
- beat 1: `opacity: 1, filter: 'blur(0px)'`
- beat 2: `opacity: 0.35, filter: 'blur(3px)'`
- beat 3: `opacity: 1, filter: 'blur(0px)'`

**Parked sticker (dock 狀態的 sticker)：**
- 同步套 table 的 dim：beat 2 時 `opacity: 0.35, filter: 'blur(3px)'`，其它 beat `opacity: 1, filter: 'blur(0px)'`。
- 用每張 sticker 自己的 motion 屬性 (不靠 CSS 繼承)，因為 sticker 是 motion 元件、跟 table 平級。

**Showcase sticker (大顯示中的 sticker)：**
- 永遠 crisp (`opacity: 1, filter: 'blur(0px)'`)。
- 一個 beat 內，supervised 和 RL 不會同時都是 showcase 狀態 — supervised 只在 beat 0 showcase、RL 只在 beat 2 showcase；其它 beat 它們不是 showcase 就是 docked (或不存在)。

## 兩張 sticker 的 state 推導

```
supervisedState(beatIndex) =
  beat 0 → showcase
  beat ≥ 1 → docked at ROW_TRASH
  其中 beat 2 → docked + dim, 其它 docked beat → docked + crisp

rlState(beatIndex) =
  beat < 2 → hidden (opacity 0, scale 0.2, 中央位置 — 不必畫面看到)
  beat 2 → showcase
  beat ≥ 3 → docked at ROW_HANG, crisp
  (RL 不會經過「docked + dim」狀態，因為 RL 出場後 table 一直 crisp)
```

## Approach 選擇

採 **approach A — 每個元素自己 compute dim 狀態**：

- table 容器、supervised motion、RL motion 三個 motion.div，各自的 `animate` prop 是 `beatIndex` 的純函式。
- 不用 `AnimatePresence` 也不用 `layoutId`；同一個 motion.div 直接 tween 從「showcase 大」到「dock 小」的所有屬性 (top, left, x, y, scale, rotate, opacity, filter)。

否決 approach B (`layoutId` morph)：
- showcase ↔ dock 是同一個 sticker 的兩個 state，不是兩個 component；用 layoutId 等於增加元件數又把 opacity / filter 動畫拆到兩處，反而更亂。

## 動畫參數

- **Sticker 縮放 / 位移 transition:** `duration: 0.6s, ease: [0.34, 1.56, 0.64, 1]` (現有 OVERSHOOT 常數)。
- **Tier list opacity / blur transition:** `duration: 0.4s, ease: 'easeOut'`。
- **Sticker dim transition:** 跟著 sticker 主動畫一起 (0.6s overshoot)；視覺上 sticker 進 / 出 dock 跟 table 的 dim/show 同節拍。
- **Showcase scale:** `1.8`。
- **Docked scale:** `1` (sticker base size：fontSize 30、padding 12/26)。
- **Rotation:**
  - supervised showcase: `0°` (正立、明確展示)
  - supervised docked (拉完了): `-3°`
  - RL showcase: `0°`
  - RL docked (夯): `+3°`

## 不變動

- 5 列 tier 結構 (夯 / 顶级 / 人上人 / NPC / 拉完了)、各 row 的顏色與字級。
- `beat-manifest.js` 已是 4 beat、本 spec 不動。
- Sticker 文案：`supervised` / `RL 增強式訓練` (保留台灣慣用「增強」)。
- 整個 step 用 step-local `beatIndex`，由 `usePresentationContext()` 取得。

## 測試

- `vitest run` 全綠 (主要驗證 manifest 仍對得上 `totalBeats: 93`)。
- `vite build` clean (無 syntax error)。
- 視覺驗證 (browser smoke test) 等 user 啟動 dev server 時手動 / Playwright 驅動逐 beat 截圖。

## 可能風險

- **Showcase 時 sticker scale 1.8 在小視窗會超出 table 容器**：sticker 視覺寬約 250 px × 1.8 = 450 px，在 TABLE_W (1120 px) 中央夠空間，無問題。
- **Filter blur + opacity 同時動可能在某些瀏覽器卡頓**：blur 0→3px 範圍小、僅 0.4s，現代 Chromium / Firefox 都流暢。如有疑慮，可改成兩段 CSS variable 動畫 — 但先不預先優化。
- **Dock 位置依賴 sticker 自身寬度估算 transformOrigin**：用 `transformOrigin: 'left center'` 避開這問題 — left 座標即視覺左緣，跟 sticker 寬度無關。
