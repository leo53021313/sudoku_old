# HTML 簡報分階段建置流程

> **產出**: `demo/presentation/` 一個 click-driven 全屏 HTML 簡報、9 章 57 step ~88 beat、配對 `demo/script.md` 個人化口播稿
> **規格來源**: [outline.md](../../../demo/outline.md) (敘事 + beat) · [outline-visual.md](../../../demo/outline-visual.md) (DNA + motif + climax) · [asset-production.md](../../../demo/asset-production.md) (素材路線) · [web_style.md](../../../demo/web_style.md) (Neo-brutalism)
> **不可動**: `demo/script.md`（口播 source of truth）

---

## 1. 目標與約束

### 1.1 目標
- 演講當天用瀏覽器全屏播放、演講者只靠左/右鍵推進
- 視覺風格嚴守 Neo-brutalism (cream + 黑邊 + hard shadow + Space Grotesk 700/900)
- 10 個 punchline + 3 大 ★★★ climax 節奏完美控制（不破梗）
- 整片時長 ~12.5 min 口播 + visualizer 30~60s ≤ 15 min

### 1.2 約束
- **技術鎖**: Vite + React + Tailwind v4 + Motion (Framer Motion) + lucide-react（全免費）
- **明確剔除**: GSAP / Howler / Slidev / Reveal / Three.js / TypeScript（可選）
- **單人開發**: 一人完成、無多人協作
- **單機演講**: 演講者用自己的筆電、Windows / Chrome 為主要 target

---

## 2. 分階段架構

```
Phase 0 · 專案基礎          [1 個 checkpoint · 預估 2-3 hr 工作量]
   ↓
Phase 1-9 · 各章節          [每章 1 個 checkpoint · 每章 ~1-3 hr]
   ↓
Phase 10 · 整片整合         [1 個 checkpoint · 預估 1-2 hr]
```

**人工 checkpoint 規則**: 每階段完成後、使用者親自開瀏覽器走一遍、確認後才進入下階段。

---

## 3. Phase 0 · 專案基礎（重 Phase 0）

### 3.1 範圍

| 區塊 | 內容 | 對應規格 |
|---|---|---|
| 專案 init | `demo/presentation/` 跑 `npm create vite@latest`、選 React + JS（非 TS）；安裝 Tailwind v4 / Motion / lucide-react；配 `vite.config.js` + `tailwind.config.js` | visual.md 開頭技術堆疊 |
| Design tokens | `src/tokens/{colors,typography,spacing,zindex}.js` 五檔 | visual.md §1, §1.5, §12 |
| Global state | `src/state/presentation.js`：當前 ch / step / beat、推進 / 後退 / 跳章；`useEffect` 監聽 mousedown / keydown | outline.md §0-§1 |
| URL routing | `?ch=N&step=M&beat=X` 同步 state；`?presenter=1` 開 Speaker Mode | outline.md §4 + visual.md §5.6 |
| Shared 元件 | `ProgressBar` (hover 浮現)、`ChapterNav` (右上角)、`BeatIndicator` (88 方塊)、`PresenterPanel` (`?presenter=1`)、`AmbientShapes` (per-chapter config) | visual.md §5, §5.6, §9.5, §9.6 |
| 全域 layer | `GlobalGrain` (SVG noise) · `HalftoneBg` (drift 動畫) · `ChapterTint` (背景漸層) · `FadeBridge` (章節間 transition) | visual.md §9.1-§9.4, §10 |
| Motif Library 13 個 | `src/motifs/<Name>.jsx`：完整實作 `BoomDoubleRing` / `CrashLine` / `RedStamp` / `YellowHighlight` / `GirlNew` / `GirlVeteran` / `ThirteenStairs` (殼)/ `FlipTwentyToFifty` / `SudokuBoard` (殼) / `SpotlightVignette` / `HalftoneBurst` / `InkSplatter` / `ScreenShake` | visual.md §7 |
| Climax FX Library 5 個 | `src/climax/{A,B,C,E,G}*.jsx`：完整實作所有 5 個 FX + Motion `useAnimate` orchestrator | visual.md §8.1 |
| Sandbox 頁面 | `/sandbox` route：顯示一個示範 sticker + 觸發 climax A+C 按鈕 + Motif Library 全 13 個小縮圖 + Climax FX 5 個試播按鈕 | 驗證用 |

### 3.2 殼 vs 完整實作

- **完整實作** (Phase 0): Climax FX 5 個全部 + 跨章節通用 motif (BoomDoubleRing, CrashLine, RedStamp, YellowHighlight, SpotlightVignette, HalftoneBurst, InkSplatter, ScreenShake)
- **殼 + TODO** (Phase 0 預留、各章用到時填): ThirteenStairs (ch7 s3 才需要)、SudokuBoard (ch7-8 才需要)、GirlNew/GirlVeteran/FlipTwentyToFifty (各章首發時填)

### 3.3 Phase 0 Checkpoint 驗證

打開 `localhost:5173/sandbox` 應看到：

1. cream `#FFFDF5` 底 + 隱約 noise grain + halftone dots（呼吸感）
2. 一個示範紅底 sticker（6px 黑邊、12px hard shadow、微旋轉 -3°）
3. 5 個按鈕分別觸發 climax A / B / C / E / G、視覺正確
4. 13 個 motif 小縮圖（含殼）顯示在頁面下方
5. 按 `?presenter=1` → 第二螢幕 layout 出現
6. 字體確認: Space Grotesk 700/900 已載入

✅ 過關 = 風格、tokens、climax 系統、state 機制全部對齊 → 開 Phase 1

---

## 4. Phase 1-9 · 各章節工作流

### 4.1 每章標準工作流

```
1. [讀 spec] outline.md §<N> 整章 + 引用的 visual.md §7/§8 / asset-production.md §5.1
2. [建檔] src/chapters/ch<N>-<name>/Ch<N>Step<M>.jsx 每 step 一檔
3. [實作首發 motif] 該章「首發」motif 從殼填到完整（per visual.md §7）
4. [步進邏輯] 每 step 標 `beats=[{id, type:'click|auto', ...}]` 給 global state 用
5. [Speaker cue 資料] 每 beat 內聯 `cue` / `wait` 字串、給 PresenterPanel 讀
6. [動畫] 進場 / 持續微動 / climax / placeholder 模式 per outline.md
7. [素材] 缺的 [E] SVG / [✓] 截圖用 placeholder 元件 + ⚠️ TODO 標記
8. [章節 transition] 章末 fade-bridge per visual.md §10
9. [視覺檢查] 開 `localhost:5173/?ch=<N>&step=1` 自己走完所有 beat
10. ⏸ 人工 checkpoint → 過關進下一章
```

### 4.2 章節順序（線性）

| Phase | 章節 | step 數 | beat 數 | 大致工作量 | 重點 motif 首發 |
|---|---|---|---|---|---|
| 1 | ch1 coldopen | 8 | 10 | ~2-3 hr | boom-double-ring · yellow-highlight |
| 2 | ch2 ml-map | 4 | 4 | ~1.5 hr | (none) |
| 3 | ch3 llm-vs-rl | 3 | 3 | ~1.5 hr | (none) |
| 4 | ch4 data-hunt | 4 | 7 | ~2 hr | red-stamp · ink-splatter |
| 5 | ch5 legacy | 4 | 7 | ~2 hr | crash-line |
| 6 | ch6 sb3 ★★★ | 7 | 12 | ~3 hr | girl-new · screen-shake · halftone-burst · spotlight-vignette |
| 7 | ch7 reasoner ★★★ | 8 | 17 | **~4 hr** | 13-stairs · sudoku-board · girl-veteran |
| 8 | ch8 apprentice | 6 | 6 | ~2-3 hr (含 visualizer button) | flip-20-to-50 |
| 9 | ch9 callback ★★★ | 13 | 24 | **~4 hr** | (全 motif callback) |

**總預估**: ~22-26 hr (建置) + Phase 0 (2-3 hr) + Phase 10 (1-2 hr) = **25-30 hr**

### 4.3 每章 Checkpoint 驗證標準

**視覺檢查 + 你親自走 beat 一遍**：

- [ ] 開 `?ch=<N>&step=1`、所有 step 依序顯示正確
- [ ] 每個 step 進場動畫合規（type 對、stagger 對、shadow 對）
- [ ] 多 beat step 的 placeholder 模式正確（punchline 不破梗）
- [ ] cue + wait 字串符合 outline.md（演講者可以按節奏念）
- [ ] climax FX 觸發時機對（per visual.md §8.3）
- [ ] motif 視覺與 visual.md §7 一致
- [ ] 章末 fade-bridge transition 自動觸發
- [ ] `?presenter=1` 模式右下 cue 顯示正確

退回修改 = 哪個 step / beat 有問題、回到 step 4-6 重做、再 checkpoint。

---

## 5. 素材 Placeholder 策略

未準備好的 [E] SVG 與 [✓] 真實截圖用統一 placeholder：

```jsx
<AssetPlaceholder
  type="[E]"               // [E] SVG / [✓] 真截圖
  width={600} height={360}
  todo="ch5 s2 程式碼 sticker · 待讀檔 838 行 + virtual scroll"
  fallback={<div className="...">程式碼 placeholder</div>}
/>
```

- 視覺: cream 底 + 4px 紅虛線邊 + 中央「⚠️ TODO: ...」字 + 維持原本 viewBox / 尺寸佔位
- 不阻塞章節 checkpoint：演講者看到有 placeholder、知道未完成、但流程仍可走

**清單 TODO 集中**: `demo/presentation/TODO.md` 列出所有未完素材、各章末更新。

---

## 6. Phase 10 · 整片整合

### 6.1 範圍

1. 章節間 fade-bridge transition 連貫測試（9 章 → 8 個邊界、3 個 1.5s 大轉折）
2. `?presenter=1` 第二螢幕完整測試（接外接螢幕、確認 cue 同步）
3. visualizer 大按鈕 (ch8 s6) + Windows custom URL scheme 串接（`demo/visualizer-launch/`）
4. 完整 12.5 min 走完一遍（從黑屏到 END）
5. 收集所有 placeholder TODO、補實素材

### 6.2 最終 Checkpoint

- [ ] 從黑屏到 — END — 一鏡到底走完
- [ ] 三大 ★★★ 笑點節奏正確（彩排 cue + wait）
- [ ] 演講者模式右下 cue 全程不缺
- [ ] visualizer 按鈕點擊正確啟動 pygame 視窗
- [ ] 所有 placeholder 已替換為實際素材（或明確接受 placeholder）

---

## 7. 風險與緩解

| 風險 | 緩解 |
|---|---|
| ch7 s3 13 招大階梯複雜、SVG 自製可能翻車 | 預留 Route A 降級到 Phosphor icon stack；Phase 7 開始前先決定 |
| ch7 s7 老油條 6 beat、climax FX 分 beat 套（A+E+G ×2 + B ×2）orchestration 複雜 | Phase 0 sandbox 階段就先驗證 climax FX 可以分 beat 觸發 |
| ch9 s13 電費小偷 wait 5-7s + 5s+ 共 ~13s（🚩 紅旗）| Phase 10 彩排驗證、cue 寫死 5s upper bound、提示演講者 |
| Motif 跨章節漂移（同 motif 在不同 step 視覺不一致） | Motif Library 集中元件、所有章節 import；Phase 0 完整實作通用 motif、避免後期改一處漏一處 |
| Phase 0 過大、第一個 checkpoint 看不到實際章節 | sandbox 頁面提供「視覺風格 + climax 試播」、用戶可即時驗證風格 |
| 素材 placeholder 太多、最後沒補 | `TODO.md` 集中追蹤、Phase 10 強制清單清零 |

---

## 8. 不在範圍內

- Mobile (<768px) 響應式
- Tablet 字級降一級規範（per outline-visual.md §4、但演講桌面為主）
- prefers-reduced-motion 降級
- 多人協作 / git branch 流程
- E2E 自動化測試（手動視覺檢查為主）
- 演講後 PDF 匯出

---

## 9. 後續

通過此 spec 後、進入 [writing-plans 階段](../../skills/superpowers/writing-plans) 產出 Phase 0 詳細實作步驟。Phase 1-9 各章在前一章 checkpoint 過關後、單獨產出該章實作步驟（避免一次寫太多 stale）。
