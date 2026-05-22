# ch9 s6「告白成功 → 殊不知更多關卡」3-beat 重構 — 設計

> 日期：2026-05-22
> 範圍：`demo/presentation/` 單章節編輯（ch9 step 6）。無新 AI 素材（沿用既有 `milk-tea.png` / `milk-tea-question.png` / `girl-veteran.png`）。
> 關聯：延續 [2026-05-22-ch6-s3-milk-tea-beats-design.md](2026-05-22-ch6-s3-milk-tea-beats-design.md) 與 [2026-05-22-ch7-s7-milk-tea-beats-design.md](2026-05-22-ch7-s7-milk-tea-beats-design.md) 的奶茶角色弧線。

## 1. 目標

把 ch9 s6 從 1 beat（單一 auto 播）→ **3 beats**，對齊 `demo/script_new.md` ch9 s6（L359）：

> 最後奶茶終於成功跟對方告白成功，結果殊不知前面還有更多關卡等著奶茶

目前 [Ch9Step6.jsx](../../../demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx) 直接跳到 4 張陷阱題雨 + 紅底反白標題，把稿子裡明確存在的「告白成功」情緒峰完全略過。新版用 3 個 click beat 還原稿子的「喜 → 預感 → 傻眼」mini-arc，並把奶茶 mood 從 normal 順移到 question variant，呼應 [Ch7Step7](../../../demo/presentation/src/chapters/ch7-reasoner/Ch7Step7.jsx) beat 6 的「奶茶傻了」收尾。

## 2. Beat 結構（1 → 3）

| beat | id | type | 口播 cue | 畫面 | climax | wait |
|---|---|---|---|---|---|---|
| 0 | `confess-success` | click | 最後奶茶終於成功跟對方告白成功—— | 奶茶（normal）從中央升起 + 黃色「告白成功 ✓」brutalist 貼紙（rotate -8°、box-shadow）。2-3 顆 💗 emoji 從奶茶旁邊浮起淡出（`setInterval` 350ms 生成、最多保留 3 顆、translateY -180px + opacity 0 動畫）。背景乾淨。 | — | 0.8-1.2s 慶祝感 |
| 1 | `twist-veteran` | click | 結果殊不知—— | 老油條 GirlVeteran 從右上 spring-in（沿用現有 motion 設定）。標題 clip-path 從左刷出：「以為穩了 · **結果更多關卡等著奶茶**」（紅底反白只在後半段、與現有設計一致）。「告白成功 ✓」貼紙降到 opacity 0.4 + `filter: grayscale(1)`；💗 停止生成（既存的淡出完成後自然消失）。 | — | 1-1.5s 留懸念 |
| 2 | `traps-rain` | click | 前面還有更多關卡等著奶茶 | 4 張陷阱題卡延用現有 cascade（rotate spring + boxShadow，每張 0.15s stagger、overshoot ease `[0.34, 1.56, 0.64, 1]`）。奶茶切到 `variant="question"`（困惑版）+ 頭頂 1-2 顆浮動 ❓（沿用 Ch7Step7 beat 6 的 `?` 浮動寫法）。觸發 `triggerShake()` 一次（climax B）。 | `['B']` | 2-3s 觀眾消化、接 s7 |

## 3. 機制改動（相對現有 `Ch9Step6.jsx`）

- **引入 beat 機制**：原檔是純 `motion` 自動播、無 `usePresentationContext`。新版 import `{ usePresentationContext }`，取 `beatIndex` 與 `triggerShake`，所有元件以 `beatIndex >= N` gating。
- **奶茶**：原檔無奶茶，新增為主角。`beatIndex >= 0` 入場（中央偏下、spring scale-in）。`beatIndex >= 2` 切到 `variant="question"`（沿用既有 `MilkTea` 元件的 variant prop）+ 頭頂浮動 ❓（沿用 Ch7Step7 的寫法、`motion.div` 循環上浮 + opacity keyframes、紅字黑描邊）。
- **告白成功貼紙**：純 JSX brutalist sticker（黃底 `#FFD93D`、`6px solid #000` 邊、`8px 8px 0 0 #000` shadow、`rotate(-8deg)`、文字「告白成功 ✓」）。沒有新素材。`beatIndex >= 0` 入場 spring。`beatIndex >= 1` 加上 `opacity: 0.4` + `filter: grayscale(1)` transition（0.4s ease）。
- **💗 粒子**：用 Unicode `💗` 字元（彩色 emoji，跨平台一致）。`useState([])` 存粒子陣列；`beatIndex === 0` 啟動 `setInterval` 350ms 生成（最多保留 3 顆 = `slice(-3)`，類似 [Ch9Step5.jsx](../../../demo/presentation/src/chapters/ch9-callback/Ch9Step5.jsx) 的 `pluses` 寫法但量更少）。粒子定位於奶茶左右兩側 ±40% 隨機水平偏移；`translateY: 0 → -180` + `opacity: 1 → 0`、2.0s ease-out。`beatIndex >= 1` 清掉 interval、舊粒子讓既存動畫自然淡出。
- **老油條 GirlVeteran**：原檔 `beatIndex` 無條件入場（mount 即播）。改成 `beatIndex >= 1` 才入場（同 motion 設定不變）。
- **標題**：原檔 mount 即播。改成 `beatIndex >= 1` 入場（clip-path 從左刷出，沿用 Ch7Step7 標題的 `clipPath: 'inset(...)'` 寫法）。
- **4 張陷阱題卡**：原檔 `delay: 0.4 + i * 0.15` 在 mount 觸發。改成 `beatIndex >= 2` 觸發；`delay` 降到 `0.05 + i * 0.15`（pivot 已在前一個 beat 處理過，這裡直接落定）。卡片內容、顏色、rotate 全部不動。
- **climax B 觸發**：`useClimax(['B'])` + `useRef` 觸發旗標。`useEffect` 在 `beatIndex === 2 && !firedRef.current` 時 `climax.play()` + `triggerShake()` 各一次（同 Ch9Step5 / Ch7Step7 的 fire-once pattern）。

## 4. 受影響檔案

- **`demo/presentation/src/data/beat-manifest.js`**：ch9（id:9）step 6 的 `beats: [{ id: 'enter', ... }]` 改成 3 筆（id/cue/wait 如上）。`duration` 維持 18（總時間預估不變、原本 18s = 一句口播 + 觀眾笑點，現在 3 個 beat 分散同樣時長）。`motifs` 加 `'milk-tea'`（原有 `'girl-veteran'` 保留）。頂部 `totalBeats: 99 → 101`（`totalSteps` 不變）。
- **`demo/presentation/src/state/usePresentation.test.js`**：第 102 行 `totalBeats` 斷言 `99 → 101`；新增「ch9 step 6 has 3 beats then crosses to step 7」測試（模式同既有 ch7 s7 7 beats 測試）。
- **`demo/presentation/src/chapters/ch9-callback/Ch9Step6.jsx`**：整檔改寫（加奶茶 + 告白成功貼紙 + 💗 粒子、beatIndex gating、climax B、老油條與標題與 4 卡延後）。

## 5. 不做（YAGNI）

- 不生新 AI 素材（💗 用 Unicode 字元、貼紙用 JSX brutalist style）。
- 不改 ch9 其他 step、不動 ch6 / ch7 既有奶茶 / 女生使用處。
- 不新增 motif 檔（💗 粒子與貼紙用 inline `motion`）。
- 不為告白成功 beat 新增第二個女生角色（lightweight 路線：只放奶茶 solo + sticker）。
- 不在 beat 0 / beat 1 開額外 climax（保留 climax B 只在 beat 2 落卡時用，避免 ch9 整章 climax 過度耗用）。

## 6. 驗收

- `npm run test:run` 全綠（含新 ch9 s6 3-beats 測試、`totalBeats=101`）。
- `npm run build` 無錯。
- dev server ch9 s6 連點 3 下：奶茶 + 「告白成功 ✓」 + 💗 → 老油條從右上來 + 標題從左刷出 + 貼紙變灰 → 4 卡 cascade 落定 + 奶茶傻眼版 + 螢幕微震；倒退可逆，全片 `totalBeats=101` 游標前進後退無錯位。
- 視覺一致性：💗 不蓋住奶茶臉、貼紙 grayscale 變化不突兀、老油條進場節奏與 Ch7Step7 一致。
