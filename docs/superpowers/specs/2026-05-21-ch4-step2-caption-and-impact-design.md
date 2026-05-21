# ch4 step2 — caption beats + impact 動畫強化設計

**日期:** 2026-05-21
**範圍:** `demo/presentation/src/chapters/ch4-data-hunt/Ch4Step2.jsx`、`demo/presentation/src/data/beat-manifest.js`、`demo/presentation/src/state/usePresentation.test.js`
**前置 spec:** `docs/superpowers/specs/2026-05-21-ch4-step2-tier-list-animation-design.md`（showcase / dock / dim 基礎節奏已落地）

## 目標

在現有 4-beat 排行榜 step 中插入兩個 caption beat（每張 sticker showcase 後加一拍 ❌ / ✓ 字幕），並追加三組視覺強化動畫（A 著陸衝擊、B caption stamp 打擊感、C showcase idle wobble）。

## 改動 1 — 從 4 beats 擴成 6 beats

| 新 beat | 內容 | 對應舊 beat |
|---------|------|-------------|
| 0 | supervised showcase（table 隱形、無 caption） | 0（同） |
| **1（新）** | supervised 維持 showcase、❌「我不想要 AI 背答案」caption 從 sticker 下方 stamp-in | — |
| 2 | supervised dock → 拉完了、caption fade out 同步消失、table 實化 | 舊 1 |
| 3 | RL showcase（table 虛化、無 caption） | 舊 2 |
| **4（新）** | RL 維持 showcase、✓「讓 AI 從零自己學習規則」caption 從 sticker 下方 stamp-in | — |
| 5 | RL dock → 夯、caption fade out 同步消失、table 實化 | 舊 3 |

連動：
- `beat-manifest.js`：ch4 step2 的 `beats` 陣列從 4 個擴成 6 個；`duration` 從 16s 提到 24s（每個 caption beat 加 ~4s）；`totalBeats` 從 93 → 95。
- `usePresentation.test.js`：`reports totalBeats = 93` 改 `= 95`。

新 beat 物件：
```js
{ id: 'supervised-cross', type: 'click', cue: '❌ 我不想要 AI 背答案', wait: '1-2s', scriptLines: 'L105-107' },
{ id: 'rl-check',         type: 'click', cue: '✓ 讓 AI 從零自己學習規則', wait: '1-2s', scriptLines: 'L105-107' },
```

## Caption 元件設計

兩個 caption 都是 `<motion.div>`、絕對定位在 table 容器內。

**位置：** showcase sticker 正下方、垂直距離約 80 px（避開 sticker 的 hard shadow），水平置中於 table（`left: TABLE_W / 2, x: '-50%'`）。

**結構：**
```
[ 大符號 ❌ 或 ✓ ]       ← 64-80 px、粗描邊、有色（紅 / 綠）
[ 文字 caption       ]    ← 32 px 黑底白字 sticker 樣式或反白
```

兩塊（符號＋文字）共組一個 caption block，整塊有自己的 motion state。

**Caption visibility 邏輯：**

```
captionState(beatIndex):
  supervised caption (❌):
    beat 1 → visible (stamp-in)
    其它   → hidden (opacity 0, scale 0.2)
  RL caption (✓):
    beat 4 → visible (stamp-in)
    其它   → hidden
```

特別注意：caption 在 beat 2/5（sticker 縮小 dock 時）一定要 fade out，不能停留。

## 改動 2 — 動畫強化 A：Impact landing

**supervised dock 到拉完了（beat 2）：**
- 觸發 `ImpactDust active`：黑色碎塊從拉完了 row 的 dock 位置向外飛散
- 觸發 `triggerShake()`：全螢幕短促晃動
- 兩者都用 `useEffect` 在 `beatIndex === 2 && previousBeatIndex !== 2` 時 fire（避免重複觸發）

**RL dock 到夯（beat 5）：**
- 觸發 `StarburstShards active`：星形碎片從夯 row 的 dock 位置向外彈出
- 觸發 `triggerShake()`：全螢幕晃動
- RL sticker 額外做 scale bounce：`scale: [1, 1.15, 1]` 在 dock 落定時播放（同 0.6s 主動畫一拍）

**Motif 定位：**
ImpactDust / StarburstShards 既有實作位置是 `position: absolute; left: 50%; top: ...%`。要讓它出現在 dock 落點（拉完了 row dock 位置 ≈ `(LABEL_W + DIVIDER + DOCK_INSET + ~100, rowCenterY(ROW_TRASH))`）。

兩種做法：
- (i) 把 motif 用一個外層 wrapper 移到 dock 位置 → 改 motif 沒事
- (ii) 寫 inline shard / dust（不用既有 motif）

採 **(i)** ─ 用包裝 div 把既有 motif 移到 dock 位置（既有 motif 內部用 `left:50%` 是相對自己的父容器，包裝 div 用絕對定位定到正確錨點即可）。

## 改動 3 — 動畫強化 B：Caption stamp polish

Caption block 進場用 stamp-in 動畫（已在 §改動 1 caption 設計裡），追加：

- **符號 stamp-in：** scale `[0, 1.4, 1]` overshoot、rotate `[-8°, 2°, 0°]`、duration 0.45s
- **下方文字：** stamp-in 後 0.2s delay 才 fade-up（先看到符號、再看到文字）
- **❌ 進場觸發 light ScreenShake**：用 `triggerShake()` 同步觸發
- **✓ 進場觸發黃色閃光**：在 caption 後方鋪一個短促 yellow flash（opacity 0 → 0.5 → 0、duration 0.3s）

Caption fade out（beat 2/5）：opacity 1 → 0、duration 0.3s easeOut、不另觸發效果。

## 改動 4 — 動畫強化 C：Showcase idle wobble

showcase 大尺寸 sticker（beat 0/1 的 supervised、beat 3/4 的 RL）在停留時，做 infinite 微擺：

```js
rotate: [-1.5, 1.5, -1.5]   // 約 ±1.5 度
duration: 3s
ease: 'easeInOut'
repeat: Infinity
repeatType: 'mirror'
```

**怎麼跟 showcase / dock state 整合：**

現有 `showcaseAnim(rotate)` 回傳 `{ rotate: 0, ... }`。需要改成：showcase 時 rotate 是「動畫陣列」而非定值。Framer Motion 支援 animate prop 用陣列做 keyframe，但跟 transition repeat 一起用要小心。

**方案：** showcase 狀態下，把 `rotate` 改成 `[(-1.5), 1.5, -1.5]` 陣列，並在該 motion.div 的 `transition` 加 `rotate: { duration: 3, ease: 'easeInOut', repeat: Infinity, repeatType: 'mirror' }`。

但這跟主 `STICKER_TR` 的 `duration: 0.6` 衝突。解法：transition prop 用物件 per-property 設定：
```js
transition={{
  default: STICKER_TR,
  rotate: beatIndex === 0 || beatIndex === 1 ? { duration: 3, ease: 'easeInOut', repeat: Infinity, repeatType: 'mirror' } : STICKER_TR,
}}
```

只有 showcase + caption beat 才用 wobble transition，dock beat 用一般 transition。

## 不變動

- 排行榜 5 列結構與顏色
- sticker 文案（`supervised` / `RL 增強式訓練`）
- showcase / dock / dim 的核心動畫常數（SHOWCASE_SCALE = 1.8、DOCK_INSET = 16、blur 3px、opacity 0.35）

## 測試

- `vitest run` 全綠（特別注意 `usePresentation.test.js` 改成 95 之後仍 pass）
- `vite build` clean
- 視覺 smoke：逐 beat 0→5 驗證 caption 出現 / 消失、dock 衝擊效果觸發、showcase wobble 不刺眼

## 風險

- **idle wobble 跟 beat 切換時 rotate 衝突：** 從 wobble（陣列）切到 dock 定值，motion 可能會有怪 interpolation。要在實作時 sanity check；若有問題，回退方案是只在 showcase 階段給 wobble、進入 dock 時 transition 改回 `STICKER_TR` 並 reset rotate 到目標值。
- **ScreenShake 全域共用：** 兩次 shake（B 的 ❌ 進場、A 的 dock 衝擊）都靠同一個 `triggerShake()`。若太密集會疊。但 beat 1（❌）跟 beat 2（dock）之間最少 1-2s 用戶點擊間隔，不會疊。
- **既有 motif 定位：** ImpactDust / StarburstShards 內部硬 code `left: 50%`，移到非中央位置要靠外層 wrapper 強制改錨點。確認 wrapper 不被內部 transform 干擾。
