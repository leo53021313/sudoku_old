# Web Presentation Outline · Click-Driven Cinematic Edition

> **基石**：本 outline 對齊 `demo/script.md`（使用者個人化重寫定稿）。
> **形式**：**click-driven step presentation**——每步獨佔整屏、左鍵點擊推進下一 **beat**（多數 step 為單 beat、punchline step 拆 2-6 beat）、右鍵點擊退回上一 beat。**不**是滾動敘事。
> **演講情境**：現場上台、桌面瀏覽器、演講者只需要左右鍵就能順暢推進。
> **主題**：Neo-brutalism + cinematic depth — cream `#FFFDF5` / 純黑 / 熱紅 `#FF6B6B` / 鮮黃 `#FFD93D` / 柔紫 `#C4B5FD`，詳 `demo/web_style.md`。每章鎖定情緒色票（見各章 header）強化敘事弧。
> **總時長**：約 12.5 分鐘口播 + 桌面 visualizer 30~60s（總 ≤ 15 分）。口播 ~3000 字 ÷ ~3.5 字/秒（含口語停頓 / 戲劇拉長 / 笑點停拍）。
> **章節數**：9 章 / 57 step / **~88 beat**（57 個原 step + 10 個破梗 step 拆出的 31 個額外 beat）。
>
> - ch1 從 6 step 加為 8 step（新增「繼續發呆」喜劇延續拍 + 拆解 sticker 累積動畫）
> - ch8 從 7 step 縮為 6 step（tensorboard 截圖挪到 ch9 step1）
> - ch9 從 14 step 縮為 13 step（MBTI + 業務工作合併為複合 step、降低結尾點擊密度）
>
> **v2 升級（2026-05-17）**：
> - 新增 [Sub-step Beat 機制](#sub-step-beat-機制子點擊推進) + [Punchline Placeholder 模式](#punchline-placeholder-模式破梗預防) + [Speaker Cue 規範](#speaker-cue-規範) + [Motif Library](#motif-library視覺母題復用庫) + [章節情緒色票](#章節情緒色票-chapter-palette) + [章節間 Transition](#章節間-transition電影-cut-感)
> - 10 個 punchline step 重寫成 beat 模式、避免破梗（搜尋 `破梗 fix #` 標記）：ch1 s8、ch4 s3、ch5 s1、ch6 s1、ch6 s6 ★★★、ch7 s6、ch7 s7 ★★★、ch9 s5、ch9 s11、ch9 s13 ★★★
> - ch9 callback 步驟（s5/s6/s8/s9/s13）加入 motif 復用引用、視覺勾起 ch5/6/7/8 記憶

---

## 全域設計原則

### 操作機制（演講者唯一要記住的）

- **滑鼠左鍵** → 推進到下一 step（含跨章節）
- **滑鼠右鍵** → 退回上一 step（含跨章節）
- **鍵盤備援** → `SPACE` / `→` 同左鍵；`←` 同右鍵；`Esc` 顯示進度條
- **右鍵實作 note**：必須 `document.addEventListener('contextmenu', e => e.preventDefault())` 禁用瀏覽器原生選單
- **滑鼠 hover** → 進度條 / 章節 nav 從邊角浮現、移開 0.5s 後淡出
- **不可** 用滾輪 / scroll / scrollIntoView 推進——禁滾動敘事

### 視覺 DNA（Neo-brutalism · 每步都遵守）

- **Cream `#FFFDF5` 為主畫布**、halftone dots / 細格線紋理當底
- **純黑 4-6px border + 8-16px hard offset shadow（zero blur）**——所有 card / sticker / hero 元素的識別物件
- **Space Grotesk 700/900** 為唯一拉丁字體（中文回退 Noto Sans SC 700/900）
- **微旋轉 sticker**（-3°~4°）破直角；**禁圓角中段** (`rounded-md`)——要嘛 0 (鋭角) 要嘛 50%（pill）
- **動態效果禁忌**：禁紫粉漸變 / 軟陰影 / blur 大過 4px / ease-in-out 慢動畫
- **動態效果保留**：強 hard-edge translate / scale snap / SVG stroke-dasharray draw / 大字 mask reveal / 多層 depth fade

### 每步節奏 4 拍（每個 step 觸發左鍵後依序執行）

1. **進場 enter (0-400ms)**：左鍵觸發 → 主元素從 mask / blur / scale 0.85 / translateY 進入；底色或裝飾物 stagger 進入（每物件 50-100ms 偏移）
2. **停頓 hold (400ms-結束)**：主元素就定位、留給觀眾 + 演講者口播時間；可有「持續微動」（如 sticker 輕微浮動、icon 慢轉），但**不**搶焦點
3. **重點 climax**（步內顯眼瞬間、可能在 enter 後 1-3s 觸發）：數字翻牌 / sticker 砸下 / 大字 mask 完成 / 互動 hover 高亮
4. **退場 exit**：演講者左鍵 → 主元素 fade-out + scale 0.95 + 底色微暗（200ms），下一 step 進場無縫接

### 互動類型字典（每 step 標一個主類型 + 視需要混合）

| 類型            | 用途                                   | within-step 實作                                       |
| --------------- | -------------------------------------- | ------------------------------------------------------ |
| `cinematic`   | 氛圍 hero / 全螢幕單一強訊息           | full-bleed、blur clear、慢動 mask reveal、留白         |
| `depth`       | 多層深度場景（取代 parallax 的靜態版） | 多 layer translateY + opacity 模擬遠近、無 scroll 依賴 |
| `progressive` | 漸進揭示資訊                           | 元素 stagger 進入（左鍵觸發 enter 後 50-150ms 一個）   |
| `interactive` | 步內 hover / sub-click                 | hover 高亮 / 子卡放大 / 隨機切換、不影響推進           |
| `comparison`  | 二元對比                               | split-screen / 左右雙欄、可加 hover 雙向加重           |
| `timeline`    | 時序事件、依序揭示                     | 步內 horizontal 或 vertical 多卡 stagger、不需 scroll  |
| `data-viz`    | 數字 / 曲線 / 翻牌                     | SVG stroke-dasharray draw、3D flip、CSS count-up       |

### 響應式策略

- **Desktop (≥1280px)**：完整 depth 層、完整 hover 互動、字級照 web_style.md 規範
- **Tablet (≥768px)**：depth 簡化為 2 層、touch tap 替代 hover (hover 行為改成 tap 觸發)、字級降一級
- **mobile (<768px)**：**不在範圍**（演講場合只在桌面/平板播放）

### 全域 UI 規範

- 進度條：默認 `opacity: 0`、滑鼠近底部邊緣 32px 內 → 0.6s 淡入到 0.8、移開 1s 後淡出
- 章節 nav：默認隱藏、滑鼠近右上角 32px 內 → 浮現可跳章
- 無 header / footer / 品牌條 / 頁碼角標（per skill 「舞台無 chrome」原則）
- 演講者模式：URL `?presenter=1` 開 → 顯示 step 編號 + 下一步預覽 + **下一 beat speaker cue**（second screen 友善）

### Sub-step Beat 機制（子點擊推進）

每個 step 可拆成 1-N 個「**beat**」。一次左鍵 = 推進一個 beat（不是推進整 step）。step 跑完最後一 beat 後，下一次左鍵才跳到下一 step。**唯一目的：精準控制 punchline 揭曉時機，避免畫面在演講者開口前就把笑點寫出來。**

- **beat 標註格式**：step 描述內以 `▸ **beat N** [click/auto] <id>: <描述>` 形式列出
  - `[click]` → 等待左鍵推進（給演講者鋪墊／停拍時間）
  - `[auto, Nms]` → 前一 beat 完成後自動觸發、不需點擊（如 BOOM 爆破完自動翻 boom card）
- **預設**：不寫 `beats` 的 step 視為單 beat（1 click = 1 step、與舊行為一致）
- **Punchline 強制規範**：任何 punchline 文字 / stamp / 數字 / 翻牌 **必須**獨立成 `[click]` beat、不可與前置元素同步進場（破梗 = 觀眾不會笑）
- **演講者體驗**：左鍵只有一個鍵、只是粒度從 step 細到 beat。右鍵退一個 beat（可跨 step 回上一 step 最後一 beat）
- **進度條計算**：以 beat 為單位、不以 step。`Esc` 顯示「step M / 9 · beat N / X」

### Punchline Placeholder 模式（破梗預防）

所有 punchline step 強制走兩拍模板：

```
[beat A] 預留視覺佔位（剪影 / 空白 sticker / ??? / 閃爍游標 _ / 半透明剪影）
         ← 演講者「開鋪」期間視覺已就位、給觀眾期待感
[beat B] click → placeholder 被「填入 / morph / stamp 砸下」變真實內容
         ← 演講者「念出 punchline」當下視覺同步揭曉
```

範例：
- 「**備胎**」(ch 6 step 6) → 預先紅底空白 sticker → click 填入「備胎」
- 「**電費小偷**」(ch 9 step 13) → 「薪水小偷」旁先放「**我不一樣 → ?**」空泡泡 → click 填入
- 「**0**」(ch 7 step 6) → 「機率還是」後放閃爍游標 `_` → click 後「0」砸下
- 「**結果我錯了**」(ch 5 step 1) → 預留 cream 大字框 + 6px 紅邊（內容空）→ click 文字 mask-reveal

**不走 placeholder 模式的 punchline = 破梗 = 觀眾不會笑**。outline 撰寫 punchline step 時必須明示 placeholder beat。

### Speaker Cue 規範

punchline 與鋪墊 step 的每個 beat 旁可加：
- `· **cue**: "..."` — 演講者「觸發這個 beat 之前」該說到的句子（短截、verbatim or 接近）
- `· **wait**: ...s` — 觸發後該停多久才推下一 beat（笑點／沉默／停頓）

範例：
```
▸ **beat 2** [click] stamp: 「備胎」紅 stamp 砸下
  · **cue**: "這個女生只把你當——"（停半拍、再點）
  · **wait**: 2-3s 笑聲後再進下一 step
```

`?presenter=1` 模式在第二螢幕即時顯示「下一 beat 的 cue + wait」，演講者單看一眼就抓得到節奏。

### Motif Library（視覺母題復用庫）

定義整片可復用的視覺母題（motif）。**callback 章 (ch 9)** 必須大量引用這些 motif，喚起觀眾前段的視覺記憶 → callback 笑點力道 +30%。

| Motif ID | 首次出現 | 視覺定義 | 復用點 |
|---|---|---|---|
| `motif/boom-double-ring` | ch 1 step 8 | 黃外圈 + 紅內圈、border 8px、stagger stamp、shadow burst | ch 9 step 13「電費小偷」stamp 圍邊（縮小化、暗示「最後的 BOOM」） |
| `motif/crash-line` | ch 5 step 1 | 「⋯⋯結果我錯了」cream 大字 + 6px 紅邊 + 紅 flash | ch 6 step 1「⋯⋯我又錯了」（同款 motif、形成 motif rhyme） |
| `motif/red-stamp` | ch 4 step 2 | 紅 stamp 從天上砸下、overshoot bounce、shadow burst | ch 6 step 6「備胎」 / ch 7 step 6「0」 |
| `motif/yellow-highlight` | ch 1 step 8 | 黃底 box 高亮關鍵詞 | 全片所有 punchline 關鍵字共用 |
| `motif/girl-new` | ch 6 step 3 | 粉紅底 sticker + 微旋轉 + 「+/+/+」浮動 | ch 9 step 5 戀愛 a callback（退到背景、灰階） |
| `motif/girl-veteran` | ch 7 step 7 | 老油條陷阱題 sticker（紅底＋紫底）+ ❌ 答案箭頭 | ch 9 step 6 戀愛 b 4 題（視覺繼承同款 sticker 樣式） |
| `motif/13-stairs` | ch 7 step 3 | 13 招技巧階梯、X-Wing / XYZ-Wing 最大 | ch 9 step 8 plasticity 三欄背景縮小裝飾 |
| `motif/flip-20-to-50` | ch 8 step 4 | +20 → +50 3D flip 翻牌、紅 → 黃 | ch 9 step 9 plasticity 機制「reward 加加減減」背景 loop |
| `motif/sudoku-board` | ch 8 step 2 | 9×9 cream 盤面、黑邊、Space Grotesk 700 數字 | ch 8 step 3 反向課程 / ch 7 step 5 mini 盤面 |
| `motif/spotlight-vignette` | ch 6 step 6 beat 3 | 全屏 radial gradient overlay、transparent (中央 25%) → rgba(0,0,0,0.6)、`mix-blend-mode: multiply`、500ms 淡入、stamp 自身保亮 | ch 7 step 7 beat 4/5、ch 9 step 11 beat 4、ch 9 step 13 beat 3 |
| `motif/halftone-burst` | ch 6 step 6 beat 3 | 從 stamp 中心放射 3 圈 dots、scale 0→3 opacity 1→0、500ms、`mask: radial-gradient` 控形、與 `motif/boom-double-ring` 語彙互補 | ch 7 step 6 beat 3、ch 7 step 7 beat 6（雙 burst）、ch 9 step 13 beat 3、ch 3 step 3 微縮版 |
| `motif/ink-splatter` | ch 4 step 3 beat 3 | SVG 8 個不規則黑墨 path、stagger 80ms scale 0→1 overshoot、半徑 80-180px 隨機（輕量版：4 個點、半徑 40-80px） | ch 4 step 2 輕量、ch 5 step 4 微縮、ch 6 step 6 beat 3、ch 7 step 6 beat 3、ch 7 step 7 beat 4/5、ch 9 step 13 beat 3 |
| `motif/screen-shake` | ch 6 step 6 beat 3 | `<main>` 容器 `translate(±5px,±3px)` 隨機 3 次共 150ms（輕量版：±2px、1 次、80ms） | ch 7 step 1 輕量、ch 7 step 7 beat 4/5、ch 9 step 5 beat 4、ch 9 step 11 beat 4、ch 9 step 13 beat 3 |

**新增 motif 規範**：任何單一視覺元素若打算復用於 ≥ 2 step，必須登錄到本表並指派 `motif/xxx` ID。step 引用時以 `▸ **Motif 復用**: motif/xxx (...形式)` 標註。

**v3 新增 4 個 motif 規範**：詳細 CSS / Motion 實作見 [§全域視覺升級 v3 §7 / §10](#10-motif-library-新增-4-個-motif)、本表已同步列出簡述。

### 章節情緒色票 (Chapter Palette)

每章鎖定主情緒色調、強化敘事弧。觀眾翻章時無意識感受到色調轉變。

| ch | 情緒 | 主色 | 副色 | climax 色 |
|---|---|---|---|---|
| 1 coldopen | 探索／好奇／白日夢 | cream + 紫 | 黃 | 紅 (BOOM) |
| 2 ml-map | 教學／理性 | cream + 黑 | 灰線 | 紅 (AlphaGo) |
| 3 llm-vs-rl | 對比／分歧 | cream | 紫 (LLM 側) + 黃 (我的 AI 側) | 紅 (VS) |
| 4 data-hunt | 戰鬥／受害 | cream + 黑 mono | 黃 (Kaggle) | 紅 (受害者 + 封 IP) |
| 5 legacy | 崩盤 #1（天真 → 失敗） | cream + 紅邊 | 紅叉叉 | 紅 flash |
| 6 sb3 | 戀愛／錯覺 → 崩盤 #2 | 粉紅（新女生） | 紅 | 灰（備胎前夕） → 紅 stamp |
| 7 reasoner | 嚴肅／死結 | cream + 黑 | 多色 sticker（紅／黃／紫） | 紅底 + 黃「0」 |
| 8 apprentice | 突破／光明 | cream + 金黃 | 紫（盤面） | 黃 (+50 翻牌) |
| 9 callback | 收斂／哲思／收尾 | cream（純） | 紫 (plasticity) | 紅（電費小偷 final） |

### 章節間 Transition（電影 cut 感）

每章末強制插入一個 0.8-1.2s 的 **fade-bridge auto-transition**（不算進 step 計數、不需點擊、自動播放）：

1. 上一章主色 fade-out（300ms）
2. cream 純畫面 hold（200-400ms）
3. 下一章主色用 halftone dots 微染滲入（500ms）
4. 下一章 step 1 enter 動畫接上

**例外**：ch 1 → ch 2（白日夢→理性）、ch 4 → ch 5（戰鬥→崩盤）、ch 8 → ch 9（突破→收尾）三個情緒大轉折拉長到 1.5s。

---

## 全域視覺升級 v3 (cinematic polish)

> **基石**：本 section 對齊 [docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md](../docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md)、把 Tier B 加料 6 項 + Climax 加成 5 項 + 4 個新 motif 全域規範化、所有章節必須遵守。
> **不破壞既有設計**：本 section 不修改 §全域設計原則 / §視覺 DNA / §每步節奏 4 拍 / §響應式策略 等既有規範、純粹「在 cream 紙感上多加一層 cinematic 氛圍 + climax 衝擊」、Neo-brutalism DNA 100% 保留。
> **明確不做**：custom cursor、cinematic letterbox bars、聲音設計（Howler.js）、Tier C 破格方案——使用者明確剔除、不要重新提案。

### 技術堆疊 (locked)

`Vite + React + Tailwind v4 + Motion (Framer Motion) + lucide-react` — 全免費、零年費、static folder 部署到 `demo/presentation/dist/`。

**明確剔除**：GSAP（Motion v11 `useAnimate` 夠用）、Howler.js、SplitType（用 React 字串 split 替代）、TypeScript（可選非必要）、Three.js / Lottie / Rive / Slidev / Reveal.js / Lenis / Theatre.js。

### 1. 章節色票背景漸層

每章 cream 底（`#FFFDF5`）外加一層該章副色的對角漸層：

```css
main { background: linear-gradient(135deg, #FFFDF5 0%, var(--chapter-tint) 100%); }
```

`--chapter-tint` 值（沿用 §章節情緒色票 副色、opacity ≤ 0.10）：

| ch | 副色 | --chapter-tint |
|---|---|---|
| 1 | 紫 | `rgba(196,181,253,0.08)` |
| 2 | 黑線 | `rgba(0,0,0,0.04)` |
| 3 | 紫+黃 | `rgba(196,181,253,0.06)` |
| 4 | 黃 | `rgba(255,217,61,0.06)` |
| 5 | 紅叉叉 | `rgba(255,107,107,0.07)` |
| 6 | 粉紅+紅 | `rgba(255,182,193,0.10)` |
| 7 | 多色 | `rgba(0,0,0,0.05)` |
| 8 | 紫+金 | `rgba(255,217,61,0.10)` |
| 9 | 紫 | `rgba(196,181,253,0.07)` |

**章節切換**：tint 過渡走 §3 View Transitions API、500ms cross-fade。

### 2. SVG 紙紋 noise grain

全屏覆蓋層、`pointer-events: none`、`z-index: 1`（在背景漸層上、所有 sticker 下）：

```css
.global-grain {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.15 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  mix-blend-mode: multiply;
  opacity: 0.5;
}
```

**上限**：opacity ≤ 0.6（再高搶 sticker 焦點）、baseFrequency ≥ 0.7（再低看到大斑塊、破紙感）。

### 3. View Transitions API · 章節 cross-fade

章節切換（非 step 切換）走瀏覽器原生 View Transitions：

```js
function navigateToChapter(chId) {
  if (!document.startViewTransition) { setChapter(chId); return; }
  document.startViewTransition(() => setChapter(chId));
}
```

```css
::view-transition-old(root) { animation: fade-out 0.5s ease-out forwards; }
::view-transition-new(root) { animation: fade-in 0.6s ease-out forwards; }
@keyframes fade-out { to { opacity: 0; } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
```

**Fallback**：Safari < 18 / Firefox 全版本 → 純 React state 切換、無動畫但功能不損。
**相容**：仍保留既有 §章節間 Transition fade-bridge auto-transition（0.8-1.2s）、兩者疊加不衝突。

### 4. 動態 halftone 漂移

既有 halftone dots 背景加極緩慢漂移、暗示「畫面在呼吸」：

```css
@keyframes halftone-drift {
  from { background-position: 0 0; }
  to { background-position: 0 -20px; }
}
.halftone-bg {
  background-image: radial-gradient(#000 1.5px, transparent 1.5px);
  background-size: 20px 20px;
  animation: halftone-drift 60s linear infinite;
}
```

**規範**：60s 完成 cycle、`linear` easing（ease-in-out 會被察覺）、垂直向上、`prefers-reduced-motion: reduce` 必須關閉。

### 5. Beat indicator · 隱藏式

底部固定 1.5% 高度區塊、平時 `opacity: 0`、滑鼠進入 bottom 32px 內 0.6s 淡入到 0.7、移開 1s 淡出。

**佈局**：88 個小方塊水平排列（對應全片 88 beat、跨章不分隔）、每個 ~10×4px：

- 已過 beat：`#000` 黑色實心
- 當前 beat：`#FF6B6B` 紅色實心 + scale 1.1
- 未到 beat：透明 + 1.5px 黑邊輪廓
- 章節邊界（9 章 → 8 個邊界）：方塊間 4px 黃色 `#FFD93D` 隔條

**右上角同步文字**：`step M / 57 · beat N / X · ch K`（11px、`color: #666`、Space Grotesk 700）

**作用**：演講者下意識掌握剩餘節奏、觀眾 hover 看到「快結束了」收尾期待感。

### 6. 環境裝飾幾何 · 各章常駐 (ambient shapes)

每章 4-6 個微旋轉幾何 sticker 常駐邊角、CSS 緩慢浮動、`z-index: 0`（在所有 sticker 下、grain 上）。

**形狀限定**：`star` / `square` / `circle` / `triangle` / `outline-question` / `pill` 六種。
**配色取**：章節副色 + climax 色（避主色避免搶焦點）。
**微旋轉**：±3°-8°。
**浮動**：`translateY(±8px) translateX(±4px)` 4-8s `ease-in-out infinite`、每個 sticker 起始 phase 隨機 offset。
**位置**：4 角為主、可有 1-2 個浮在中段邊緣（離主元素 30%+）。
**上限**：6 個/章（超過會與 sticker 搶焦點）。

每章配置由章節 header 的 `**Ambient shapes**：...` 行指定（見各章）。

### 7. 三大 ★★★ Climax 視覺加成（5 效果）

僅套用於三大 ★★★ punchline 拍：**ch6 s6 備胎**、**ch7 s7 老油條**、**ch9 s13 電費小偷**。

| 代號 | 名稱 | 觸發時機 | 規格 |
|---|---|---|---|
| **A** | Screen shake 微震 | stamp 砸下瞬間 | 150ms 內 `<main>` `translate(±5px,±3px)` 隨機 3 次（每次 50ms） |
| **B** | Halftone 同心圓爆破 | A 同步 | 從 stamp 中心向外 3 圈 dots、500ms scale 0→3、opacity 1→0、`mask: radial-gradient` 控形 |
| **C** | Slow-mo overshoot 4 拍 | stamp 進場 | scale 0→1.4 (160ms)→1.0 (200ms)→0.95 (120ms)→1.0 (120ms)、bezier `(0.34, 1.56, 0.64, 1)` |
| **E** | 黑墨噴濺 splatter | A/B 同步 | 周圍 8 個不規則黑墨 SVG inline path、stagger 80ms、scale 0→1 overshoot、半徑 80-180px 隨機 |
| **G** | Spotlight 聚焦暗化 | punchline 揭曉 → climax 全程 hold | 全屏 `radial-gradient(circle at <stamp-center>, transparent 25%, rgba(0,0,0,0.6) 100%)`、`mix-blend-mode: multiply`、500ms 淡入、stamp 自身保亮 |

**Motion `useAnimate` 範例**（給實作 agent 參考）：

```js
const [scope, animate] = useAnimate();
await animate([
  ["#stamp", { scale: [0, 1.4, 1.0, 0.95, 1.0] }, { duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }],
  ["main", { x: [0, 5, -5, 3, -3, 0], y: [0, 3, -3, 2, -2, 0] }, { duration: 0.15, at: 0 }],
  ["#halftone-burst", { scale: [0, 3], opacity: [1, 0] }, { duration: 0.5, at: 0 }],
  ["#splatter [data-dot]", { scale: [0, 1] }, { duration: 0.3, delay: stagger(0.08), at: 0 }],
  ["#spotlight", { opacity: [0, 1] }, { duration: 0.5, at: 0.2 }],
]);
```

### 8. 一般 punchline · Climax 輕量版

剩 7 個 punchline placeholder step 套用 A + C 起跳（去除 B/E/G 重度、避免疲勞）：

| step | beat | 套用 |
|---|---|---|
| ch1 s8 beat 3 `punchline-reveal` | A + C |
| ch4 s3 beat 3 `victim-stamp` | A + C + E (stamp 性質) |
| ch5 s1 beat 4 `crash-fill` | A + C |
| ch6 s1 beat 3 `crash-fill` | A + C |
| ch7 s6 beat 3 `zero-drop` | A + B + C + E (「0」實體 stamp 性質) |
| ch9 s5 beat 4 `punchline-hero` | A + C |
| ch9 s11 beat 4 `warn-line-b-fill` | A + C + G (警語性質、聚焦合理) |

### 9. prefers-reduced-motion 規範

所有動態效果在 `prefers-reduced-motion: reduce` 環境必須降級：

- §4 動態 halftone 漂移 → 關閉動畫、保持靜態
- §7-A screen shake → 改純 scale punch（不晃畫面）
- §7-B halftone burst → 縮短至 200ms、不放射
- §7-C slow-mo overshoot → 縮短至 200ms、直接 scale 0→1
- §7-E splatter → 同時出現、不 stagger
- §7-G spotlight → 改 200ms instant 暗化

### 10. Motif Library 新增 4 個 motif

加進既有 §Motif Library 表（與 9 個既有 motif 並列）：

| Motif ID | 首次出現 | 視覺定義 | 復用點 |
|---|---|---|---|
| `motif/spotlight-vignette` | ch 6 s6 beat 3 | 全屏 radial gradient overlay、transparent → rgba(0,0,0,0.6)、`mix-blend-mode: multiply`、500ms 淡入 | ch 7 s7 beat 4/5、ch 9 s11 beat 4、ch 9 s13 beat 3 |
| `motif/halftone-burst` | ch 6 s6 beat 3 | 從 stamp 中心放射 3 圈 dots、scale 0→3 opacity 1→0、500ms、與 `motif/boom-double-ring` 語彙互補 | ch 7 s6 beat 3、ch 7 s7 beat 6、ch 9 s13 beat 3 |
| `motif/ink-splatter` | ch 4 s3 beat 3 | SVG 8 個不規則黑墨 path、stagger 80ms scale 0→1 overshoot、半徑 80-180px 隨機 | ch 6 s6 beat 3、ch 7 s6 beat 3、ch 7 s7 beat 4/5、ch 9 s13 beat 3 |
| `motif/screen-shake` | ch 6 s6 beat 3 | `<main>` 容器 `translate(±5px,±3px)` 隨機 3 次共 150ms | ch 7 s7 beat 4/5、ch 9 s5 beat 4、ch 9 s11 beat 4、ch 9 s13 beat 3 |

---

## 1. coldopen — 心虛開場 · 心理學系 · 捷運靈感（8 steps · ~72s · step 8 拆 3 beat）

**章節色票**：cream + 紫（白日夢底色）｜副 黃｜climax 紅（BOOM）

**Ambient shapes**：TL 黃星 +15° · TR 紫方塊 -8° · BL 紅圓 0° · BR 描邊? +12° · 中右 黃圓 -3°

**信息池**（chapter agent 按需挂角標 / 副標 / sticker 文字）：

- 自我揭露：「**心虛**」「報告太不正經、請各位同學和老師多包涵」—— 來源 `script.md` L1
- 背景標籤：「**心理學系畢業**」（為後段 RL / 腦科學 / plasticity 鋪墊）—— 來源 `script.md` L5
- 主題揭露：「訓練出一個 AI、讓他自己學會如何解數獨」—— 來源 `script.md` L9
- 場景具象：「搭捷運來上學、正大光明地看著對面的正妹發呆」—— 來源 `script.md` L15
- 影片 anchor：**Code Bullet** flappy bird YouTuber 影片靈感氣泡（注意：是 flappy bird 不是踩地雷）—— 來源 `script.md` L19 + `content.md` §1.1
- 場景具象：「當兵時大家很無聊、沒有手機、唯一能玩的就是解數獨」—— 來源 `script.md` L25
- punchline 金句：「靈感就是這麼莫名其妙地蹦出來」—— 來源 `script.md` L37

**開發計畫**：

- **step 1 (~10s)** — 全螢幕「**心 虛**」巨字 sticker（紅底、6px 黑邊、16px hard shadow、微旋轉 -3°）+ 角標「期中報告」黃 sticker + 字幕「報告太不正經、請各位同學和老師多包涵」
  ▸ **類型** `cinematic` · **進場**: 黑屏 → cream 紙質淡入（400ms）→ 心虛 sticker 從 scale 0.7 + rotate 0° snap 到 scale 1 + rotate -3° (overshoot easing) · **停頓**: 字幕從左 mask-reveal · **持續微動**: 心虛 sticker 輕微浮動（4s ease-in-out infinite ±4px）
- **step 2 (~8s)** — 「**心 理 學 系 · 畢業**」card hero（白底、6px 黑邊、12px hard shadow、微旋轉 -2°）+ 紅色箭頭 + 黃色高亮 sticker「**敬請期待**」（伏筆後段 RL / 腦科學 / plasticity）
  ▸ **類型** `cinematic + depth` · **進場**: 主 card 從右下 translateY+rotate 進入（overshoot）→ 箭頭從卡片左側 stroke-draw → 「敬請期待」黃 sticker 從右側 scale 0 → 1 stamp · **動畫元素 (≤2)**: card 進場 + 箭頭 stroke
- **step 3 (~10s)** — 主題揭曉：上方 kicker「**期中主題**」黑底 cream 字 → 中央 cinematic hero「**訓 練 AI 解 數 獨**」大字（AI 用紅底、解數獨用黃底兩塊強調 box、text-stroke 描邊樣式）+ 四個漂浮裝飾形狀（紫方塊 / 黃星旋轉 / 紅圓 hard shadow / 描邊問號）
  ▸ **類型** `cinematic + depth` · **進場**: kicker 從左 slide-in → hero 從 scale 0.85 + letter-spacing 0.1em → scale 1 + letter-spacing -0.04em (overshoot 720ms) → 四裝飾物 stagger 進場（從各角飛入）· **持續微動**: 黃星 spin-slow 12s、紫方塊 float ±16px 4s
- **step 4 (~10s)** — 過場「**靈感哪來呢？某天捷運上⋯**」+ 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop）+ 第一張 sticker（黃底「正妹發呆中」放左下、微旋轉 -4°、cloud 樣式）
  ▸ **類型** `depth + progressive` · **進場**: 捷運背景 fade-in（300ms）→ 「靈感哪來呢」字幕從上 fade-down → 窗景 stamp-in → 正妹 sticker 從左下角 stamp-in (stagger 240ms) · **depth layers**: 背景線條 0.5 opacity 不動 / 中景窗 1.0 / 前景 sticker 1.2 視覺層次
  ▸ **口播對應**: script.md L15「一如往常搭捷運來上學、正大光明地看著對面的正妹發呆」
- **step 5 (~8s)** — 同捷運背景延續 + 第一張 sticker（正妹、左下）+ **新疊**：第二張 sticker（紫底「Code Bullet · flappy bird」放右上、微旋轉 3°）
  ▸ **類型** `progressive` · **進場**: 左鍵觸發 → 第二張 sticker 從右上角 stamp-in（240ms）+ 思考氣球線從正妹 sticker 連到 flappy bird sticker（虛線、stroke-draw 動畫 600ms）· **動畫元素 (≤2)**: 第二張 stamp-in + 思考線
  ▸ **口播對應**: script.md L19「腦袋突然冒出 Code Bullet 訓練 AI 玩 flappy bird 的影片」
- **step 6 (~6s)** — **繼續發呆**（喜劇延續拍）：捷運背景與兩張 sticker 維持不動 + 中央正妹 sticker 上方浮現「⋯⋯」省略號氣球（cream 底、黑邊框、輕微浮動）+ 角標小字「**然後我繼續發呆⋯**」
  ▸ **類型** `cinematic + interactive` · **進場**: 「⋯⋯」氣球 stamp-in (300ms) + 緩慢 pulse (1s ease-in-out infinite) · **氣質**: 喜劇半拍、給觀眾笑點 + 演講者口語停頓
  ▸ **口播對應**: script.md L21「然後我繼續發呆看著正妹」(獨立一拍、強化反差、給 Boom 鋪墊)
  ▸ **設計來源**: 原 outline 把 L15+L19 跟 L25 合併成 2 step、丟失了 L21 這個喜劇延續拍。新增本 step 拍出「繼續發呆」的回扣節奏
- **step 7 (~8s)** — 同捷運背景延續 + 三張 sticker（正妹左下 + flappy bird 右上 + **新疊** 紅底白字「沒手機·解數獨」放右下、微旋轉 2°）
  ▸ **類型** `progressive` · **進場**: 第三張 sticker 從右下 stamp-in（240ms）· **動畫元素 (≤2)**: 第三張 stamp-in、其他不重畫
  ▸ **口播對應**: script.md L25「當兵的時候大家很無聊、沒有手機、唯一能玩的就是解數獨」
- **step 8 (~12s)** — **BOOM · 兩個想法撞在一起** + 靈感 punchline（**punchline 拆 beat、避免畫面破梗 #1**）
  ▸ **類型** `cinematic + data-viz` · **placeholder 模式**: punchline 黃底高亮預留位但**內容 hold**、等 beat 3 才填字
  ▸ **Climax 加成 (輕量版)**: beat 3 `punchline-reveal` 套 A (screen-shake) + C (slow-mo overshoot) · 引用 [§全域視覺升級 v3 §8 一般 punchline](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `boom-burst`: 三 sticker 背景輕微抖動 (150ms shake) → **雙圈爆破覆蓋** ([motif/boom-double-ring](#motif-libraryml視覺母題復用庫) 首次出現：黃外圈 + 紅內圈、border 8px、scale 0→1 overshoot、stagger 黃 80ms / 紅 120ms)
    · **cue**: "Boom——"（演講者話一出口就點）
  ▸ **beat 2** [auto, 400ms] `boom-card`: 中央 cream「**訓 練 AI 解 數 獨**」boom card stamp 進場（accent red AI 標、6px 黑邊、16px shadow、微旋轉 -2°、scale 0.8 → 1 overshoot）
    · 自動觸發、銜接「兩個想法結合在一起、訓練 AI 解數獨」口播
  ▸ **beat 3** [click] `punchline-reveal`: 下方預留黃底空高亮 box → 填入「**靈感就是這麼 *莫名其妙* 地蹦出來**」mask-reveal（720ms、左到右）
    · **cue**: "很多人問我靈感哪來的、我也不知道怎麼解釋——靈感就是這麼"（最後一字「莫名其妙」前點下、字一邊出演講者一邊念）
    · **wait**: 1-2s 讓觀眾消化
  ▸ **口播對應**: script.md L29「Boom，就這樣在我腦袋裡莫名其妙地把兩個想法結合在一起、訓練 AI 解數獨」+ L37「靈感就是這麼莫名其妙地蹦出來」
  ▸ **破梗 fix #1**: 原版「punchline mask-reveal」與 boom card 同步進場、口播在 BOOM 之前就把笑點寫在屏幕上；現拆為 boom (beat 1) → boom card (beat 2 auto) → punchline (beat 3 click)、punchline 黃底先佔位、文字 hold 到演講者念那句才填入

**口播節選**：

> 「我是心理學系畢業的⋯⋯某天搭捷運看著對面的正妹發呆⋯⋯腦袋冒出 Code Bullet 訓練 AI 玩 flappy bird⋯⋯又想到當兵解數獨⋯⋯Boom，靈感就是這麼莫名其妙地蹦出來。」

---

## 2. ml-map — 機器學習地圖（4 steps · ~50s）

**章節色票**：cream + 黑（教學底色）｜副 灰線｜climax 紅（AlphaGo sticker）

**Ambient shapes**：TL 黑描邊星 -10° · TR 灰方塊 +5° · BL 黑 pill 0° · BR 紅圓 -8°（為 AlphaGo climax 鋪色）

**信息池**：

- 三大塊：**supervised / unsupervised / RL**—— 來源 `script.md` L49-67
- 日常比喻：「看著答案抄筆記」「自己分類整理（折衣服）」「試錯加獎懲（訓練狗握手）」—— 來源 `script.md` L51-65
- 名人事件 anchor：**AlphaGo 打敗世界圍棋王**（給 RL 加重）—— 來源 `script.md` L67
- cliffhanger：「那 ChatGPT 跟 Claude 又是哪一招？」—— 來源 `script.md` L71

**開發計畫**：

- **step 1 (~14s)** — **第一塊揭示**：上方 kicker「**機器學習 · ①/3**」黑底白字 + 中央「supervised」大字 + 副標「白話：**看著答案抄筆記**」+ 右側「老師給題目 + 答案 · 你硬背」插畫（純 SVG · 老師線稿 + 學生 + 紙張）
  ▸ **類型** `cinematic + depth` · **進場**: kicker 從上 slide-in → 「supervised」大字 mask-reveal 從左到右 → 副標 fade-up → 右側插畫 stagger（老師 → 學生 → 紙張）
- **step 2 (~13s)** — **第二塊揭示**：kicker「②/3」+ 「unsupervised」大字 + 副標「**自己分類整理**」+ 右側折衣服插畫（一堆衣服 → 三疊分顏色、純 SVG）
  ▸ **類型** `cinematic + depth` · **進場**: kicker 切換 +1 動畫 → unsupervised 大字 mask-reveal → 衣服堆 stagger 散開（從一堆 → 三疊動畫 1200ms）
- **step 3 (~15s)** — **第三塊揭示**：kicker「③/3」+ 「**RL** · reinforcement learning」大字 + 副標「**試錯加獎懲**」+ 訓練狗握手插畫 + **AlphaGo 標籤 sticker**（accent red 底、黑邊、微旋轉 -2°、stamp-in）
  ▸ **類型** `cinematic + depth + data-viz` · **進場**: kicker 切換 → RL 大字 mask-reveal → 狗握手插畫 → **AlphaGo sticker 砸下 (scale 1.4 → 1 snap, overshoot)**（climax）· **持續微動**: AlphaGo sticker 浮動
- **step 4 (~8s)** — 全螢幕單句 cliffhanger「**那 ChatGPT 跟 Claude · 又是哪一招？**」cream 底 + 黑大字 + 中央問號黃底大字（旋轉 -8°）
  ▸ **類型** `cinematic` · **進場**: cream 底 fade-up → 問句 mask-reveal 左到右（左半 800ms） → 問號 sticker 從天上 drop-in（overshoot bounce）· **氣質**: 換語氣 / 換主題、留 1-2s 給演講者口播 cliffhanger
  ▸ **視覺補強 (v3)**: 問號 sticker 用 `motif/yellow-highlight` 黃底放大 +10%、enter 動畫加入 720° 完整旋轉一次（與 drop-in 同步、暗示「問題在飛轉」）。本 step 平淡感 = ch2 句末、加旋轉問號補張力

**口播節選**：

> 「機器學習主要分三塊。supervised、unsupervised、RL⋯⋯當年 AlphaGo 打敗世界圍棋王、用的就是這招。那 ChatGPT 跟 Claude 又是哪一招？」

---

## 3. llm-vs-rl — ChatGPT 跟 Claude 在哪？（3 steps · ~35s）

**章節色票**：cream｜副 紫（LLM 側）+ 黃（我的 AI 側）｜climax 紅（VS sticker）

**Ambient shapes**：TL 紫方塊 -5° · TR 黃圓 +10° · BL 紫三角 +3° · BR 黃方塊 45° 旋轉 -7° · 中下 紅描邊? +8°

**信息池**：

- LLM 路線：**supervised + RLHF**——「把整個人類網路寫過的東西全部讀一遍 + 人類教他怎麼回」—— 來源 `script.md` L75-77
- 對比 anchor：「**LLM = 模仿**」 vs 「**我這套 = 自己摸出規則**」—— 來源 `script.md` L83-89
- 場景比喻：「把 AI 丟進一個他什麼都不知道的房間」—— 來源 `script.md` L89
- cliffhanger：「OK 所以我要走純 RL。第一步是找資料」—— 來源 `script.md` L93-95

**開發計畫**：

- **step 1 (~14s)** — 左欄「**LLM**」hero（佔 60% 寬）+ 副標「**supervised + RLHF**」紫底標籤 + 底下「把整個人類網路寫過的東西全部讀一遍」標語 + 背景文字流動效果（暗示「網路文字海」、低密度灰色字 grid 微動）
  ▸ **類型** `cinematic + depth` · **進場**: 左欄 wipe-in 從左到右 → 「LLM」大字 stamp（overshoot）→ 副標 + 背景文字 grid stagger fade-in · **持續微動**: 背景文字 grid 緩慢 translateY 上飄
- **step 2 (~14s)** — 同畫面右欄「**我的 AI**」hero（佔 40%）+ 中央粗 6px 黑色分隔線 + 「**VS**」大字旋轉 sticker 在分隔線上 + 強對比 sticker「**LLM = 模仿**」紅 stamp（左欄）vs「**自己摸出規則**」黃 stamp（右欄）+ 右欄底部 房間 / 門 SVG icon（門關著、AI 在房內）
  ▸ **類型** `comparison + interactive` · **進場**: 右欄 wipe-in 從右到左 → VS sticker 從 scale 0 stamp 中央 → 兩 stamp 同時砸下（紅左、黃右）→ 房間 icon fade-in · **互動**: hover 左欄 → 左欄 zoom-in 1.02 + 右欄 dim opacity 0.6（vice versa）· **不影響推進**: hover 純視覺
- **step 3 (~7s)** — 全螢幕單句「**OK · 所以我要走純 RL** / 第一步是找資料」cream 底大字（OK 用紅底高亮、純 RL 用黃底）
  ▸ **類型** `cinematic` · **進場**: split-screen 兩半 collapse → cream 全屏 → 標題 mask-reveal · **氣質**: 短促、cliffhanger
  ▸ **視覺補強 (v3)**: 「OK」紅底高亮切換到位瞬間加 `motif/halftone-burst` 微縮版（半徑限 60px、不放射超出 OK box、500ms scale 0→2 opacity 1→0）暗示「決定下了」的決心感

**口播節選**：

> 「LLM 是模仿——模仿人類寫過的字。我這套不一樣——把 AI 丟進一個他什麼都不知道的房間、讓他自己摸出規則。OK 所以我要走純 RL、第一步是找資料。」

---

## 4. data-hunt — 找資料：從 Kaggle 到爬蟲（4 steps · ~50s · step 3 拆 4 beat）

**章節色票**：cream + 黑 mono（戰鬥底色）｜副 黃 (Kaggle)｜climax 紅（受害者 + 封 IP）

**Ambient shapes**：TL 黑方塊 +5° · TR 黃星 -10° · BL 紅圓 +12° · BR 黑描邊 pill -3°

**信息池**：

- 資料來源 anchor：**Kaggle**（先去）→ **websudoku.com**（後來爬）—— 來源 `script.md` L99 + L117
- 拒絕理由 anchor：「題目+答案 = supervised 路線」與「我要 AI 自己摸出規則」衝突 —— 來源 `script.md` L105-107
- 戰略 anchor：「終極目標霸榜各數獨網站 → 題目來源得從那些網站來」—— 來源 `script.md` L111-115
- 爬蟲 punchline：「**這個受害者**」+ 「沒有現代防爬蟲機制、簡簡單單被攻破」—— 來源 `script.md` L117-121
- 反爬 anchor：被封 IP → **proxy 池**（類似 VPN、一次擁有好幾萬個 IP）—— 來源 `script.md` L125-133

**開發計畫**：

- **step 1 (~12s)** — Kaggle 標籤 sticker（黃底、微旋轉 2°）+ 「題目+完整答案 整理好的資料集」副標 + 兩三個資料 card 浮現 + 角落「**但問題來了**」紅色叉叉動畫覆蓋（從中心 burst-out）
  ▸ **類型** `progressive + cinematic` · **進場**: Kaggle sticker stamp-in → 資料 card stagger（3 張 100ms 間隔）→ **climax**: 紅色叉叉 burst-in (scale 0 → 1.2 → 1 overshoot) 覆蓋 70% 畫面
- **step 2 (~11s)** — 「**supervised 路線 · 拒絕**」紅 stamp full-bleed（旋轉 -5°、stamp-in、shadow 大）+ 右側對比「**我要 AI · 自己摸出規則**」黃底 sticker
  ▸ **類型** `cinematic + comparison` · **進場**: 紅 stamp 從天上 drop（overshoot bounce）→ 右側黃 sticker stamp-in · **climax**: 紅 stamp 砸下瞬間
  ▸ **視覺補強 (v3)**: 紅 stamp 砸下瞬間加 `motif/ink-splatter` 輕量版（4 個黑點而非 8 個、半徑 40-80px 而非 80-180px）。stamp 是「拒絕」性質的砸下、墨噴強化「最終決定」氣勢
- **step 3 (~14s)** — 「**終極目標：去每個數獨網站霸榜**」hero + websudoku URL + **「這個受害者」punchline**（破梗 fix #2）
  ▸ **類型** `cinematic + depth` · **placeholder 模式**: URL sticker 旁預留紅 sticker 空形狀、文字 hold 到 beat 3 才填
  ▸ **Climax 加成 (輕量版)**: beat 3 `victim-stamp` 套 A (screen-shake) + C (slow-mo overshoot) + E (ink-splatter)、stamp 性質適合墨噴 · 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `kicker`: 上方 hero「**終極目標：去每個數獨網站霸榜**」從上 fade-in
    · **cue**: "我的終極目標是把我訓練好的 AI 拿去每個數獨網站..."
  ▸ **beat 2** [click] `url-sticker`: 中央 websudoku URL sticker 從左 slide-in（黑底 cream 字 mono「websudoku.com」+ cursor 閃爍）
    · **cue**: "於是我找到了 websudoku.com..."
  ▸ **beat 3** [click] `victim-stamp`: URL 旁預留的紅 sticker 形狀 → 文字「**這個受害者**」打入 + 紅 stamp 微旋轉斜貼動畫
    · **cue**: "..."（演講者直接念出「這個受害者」當下點，**梗一說就視覺同步**）
    · **wait**: 1-2s 笑點
  ▸ **beat 4** [auto, 200ms] `subtitle`: 副標「簡簡單單被我攻破」fade-up
  ▸ **持續微動**: URL 後 cursor 閃爍
  ▸ **破梗 fix #2**: 原版「URL + 受害者 stamp 同 step 進場」、視覺先把「受害者」這個自嘲梗寫出來；現拆出獨立 beat、預留空紅 sticker 形狀佔位、文字 hold 到演講者念那一刻才填入
- **step 4 (~13s)** — 「**才爬 20 題就被封 IP**」紅警示 hero + IP 封鎖圖示（黑邊框 + 紅色斜線）→ **proxy 池視覺化**：「類似 VPN · 好幾萬個 IP」+ 多個半透明 IP 小卡 grid（30+ 卡）漂浮 + 隨機 IP 切換動畫（每 200ms 一個卡高亮 + 切下個 IP 數字）
  ▸ **類型** `data-viz + cinematic` · **進場**: 紅警示 hero 進來 (800ms hold) → 警示淡化、IP grid 從中央 burst-out (stagger 30 個 30ms 間隔) → IP 切換動畫啟動 · **climax**: IP grid burst 瞬間 · **持續微動**: 隨機卡片高亮輪播

**口播節選**：

> 「Kaggle 是 supervised 路線、拒絕⋯⋯找到 websudoku 這個受害者⋯⋯結果 20 題就被封 IP⋯⋯我請出反反爬蟲工具 proxy。」

---

## 5. legacy — 一句搞定的幻想 → 800 多行單檔（4 steps · ~51s · step 1 拆 4 beat）

**章節色票**：cream + 紅邊（崩盤底色 #1）｜副 紅叉叉｜climax 紅 flash

**Ambient shapes**：TL 紅方塊 45° 旋轉 +15°（叉感）· TR 紅圓 -5° · BL 紅描邊方塊 +8° · BR 紅 pill -3°（章節整體紅意、為崩盤鋪壓力）

**信息池**：

- 戲劇崩盤句：「我以為⋯⋯**結果我錯了**」—— 來源 `script.md` L141-145
- 程式碼 anchor：**`legacy/app/sudoku/torch_agent.py` 一檔 838 行**（畫面值；口播照 script 走「800 多行」）—— 來源 `script.md` L151 + 真實程式碼 `legacy/app/sudoku/torch_agent.py`
- debug 痛點 anchor：「每改一個地方都東倒西歪、我自己都看不懂、debug 成本爆炸」—— 來源 `script.md` L153
- 第一件學到 anchor：「**不能再這樣偷懶全靠 AI 了。架構、演算法都得自己先想清楚、再請 AI 分工**」—— 來源 `script.md` L157-159
- 過渡 anchor：「放棄這個版本、轉而當個套皮仔」—— 來源 `script.md` L163

**開發計畫**：

- **step 1 (~14s)** — **cream + 強紅邊崩盤感** + prompt 對話框 + **「結果我錯了」崩盤 punchline**（破梗 fix #3）
  ▸ **類型** `cinematic` · **placeholder 模式**: 「結果我錯了」位置預留 cream 大字框 + 6px 紅邊（**內容空、僅閃爍游標 `_`**）→ 等 beat 4 才填字
  ▸ **Climax 加成 (輕量版)**: beat 4 `crash-fill` 套 A (screen-shake) + C (slow-mo overshoot)、跟既有紅邊 flash 2× 疊加 · 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **Motif 首發**: `motif/crash-line`（後續 ch 6 step 1「我又錯了」復用同款）
  ▸ **beat 1** [click] `kicker`: 上方字幕「我那時候還很天真」fade-up + halftone dots 加密 1.5×
    · **cue**: "我那時候還很天真、覺得——"
  ▸ **beat 2** [click] `prompt-box`: 中央 prompt 對話框 sticker「**幫我寫一個訓練 AI 解數獨的程式**」stamp-in（cream 底、6px 黑邊、12px shadow、模擬 chat input）
    · **cue**: "不如我丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude？他應該能搞定吧？"
  ▸ **beat 3** [click] `placeholder-frame`: 下方預留崩盤句空框出現（cream 大字框、6px 紅邊、16px shadow、微旋轉 1°、**內部僅閃爍游標 `_`**、無文字）
    · **cue**: "⋯⋯"（演講者拖長尾音、給空框出現的反應時間）
    · **wait**: 1s 留白
  ▸ **beat 4** [click] `crash-fill`: 空框內 mask-reveal 填入「**⋯⋯結果我錯了**」+ 紅邊 flash 2× (200ms 一次、200ms 間隔) + shadow burst 從 8px → 16px
    · **cue**: "結果我錯了"（演講者念出當下視覺同步爆）
    · **wait**: 2s 觀眾消化
  ▸ **破梗 fix #3**: 原版 prompt 對話框與「結果我錯了」同 step stamp、視覺把崩盤點提前曝光；現拆四 beat、崩盤句先以空紅邊框 + 閃爍游標 placeholder 預告「有東西要來」、文字 hold 到 beat 4 才填入
  ▸ **設計來源**: 原版「底色切黑」會脫離 web_style.md cream 主畫布的 visual DNA、改為「cream + 6px 紅邊 + halftone 加密 + 雙重 flash」表達崩盤感（保 brutalism 連續性、不破 visual cohesion）
- **step 2 (~8s)** — **「800 多行的單一檔案」程式碼 sticker** ：cream 上一坨深色文字塊（讀真實 `legacy/app/sudoku/torch_agent.py` 部分內容、syntax 高亮輕量化）+ 角標「`torch_agent.py · 838 lines`」+ 副標「**什麼都塞在裡面**」
  ▸ **類型** `cinematic + data-viz` · **進場**: 程式碼 sticker 從下方快速 slide-up（佔 70% 高、400ms）→ 角標 stamp-in 右上 · **climax**: 角標 838 數字 count-up 動畫 (0 → 838、600ms) · **持續微動**: 程式碼塊內輕微捲動 (背景慢速 translateY、暗示「巨量」)
  ▸ **節奏修正**: 原版 14s 進場過慢、口播只有 script.md L151「他產出了一個 800 多行的單一檔案、什麼都塞在裡面」(~6s)。縮到 8s 避免演講者卡空白
- **step 3 (~7s)** — **debug 痛點**：cream 上「**每改一個地方都東倒西歪**」hero + 紅色叉叉飛來飛去動畫 (chaotic、6-8 個叉叉隨機位置 spawn + scale + fade) + 「**debug 成本爆炸**」hero kicker
  ▸ **類型** `cinematic + data-viz` · **進場**: hero 文字 fade-in (300ms) → 紅叉叉 burst 一波（爆炸感、500ms）→ 持續隨機 spawn 叉叉 · **climax**: 「debug 成本爆炸」punchline mask-reveal · **氣質**: chaotic、視覺亂、暗示痛苦
  ▸ **節奏修正**: 原版 13s、口播 script.md L153 「後面我每改一個地方都東倒西歪、我自己都看不懂、debug 成本爆炸」(~7s)。縮到 7s 對齊
- **step 4 (~15s)** — **第一件學到 hero 標語**：「**架構、演算法都得自己先想清楚、再請 AI 分工**」（cream 底、黑大字、關鍵詞「架構」「演算法」「自己」「分工」黃底高亮 sticker）+ 過渡 footer「轉而當個套皮仔 →」
  ▸ **類型** `cinematic` · **進場**: chaotic 叉叉 fade-out → 底色穩定 → hero 標語慢速 mask-reveal 從左到右 (1200ms) → 4 個關鍵詞 stagger 黃底高亮 (per word 250ms) · **climax**: 4 黃底全亮的瞬間 · **轉場**: footer 從下 slide-up、暗示下章
  ▸ **視覺補強 (v3)**: 4 個關鍵詞 stagger 黃底高亮時、每個關鍵詞下方加 `motif/ink-splatter` 1 個小黑點（半徑 20-40px、隨機位置、與該詞 highlight 同時出）佐證「在白紙上寫字」感、強化金句的物理書寫感
  ▸ **節奏修正**: 原 10s → 15s。把 step 2+3 省下來的 12s 挪一半到此 step、讓金句節奏放慢、給觀眾消化 + 演講者口播 script L157-163「我學到的第一件事」+「自己手刻整套訓練系統就是浪費時間」雙段口播時間

**口播節選**：

> 「丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude⋯⋯結果我錯了。他產出 800 多行的單一檔案⋯⋯架構自己要先想清楚、再請 AI 分工。」

---

## 6. sb3 — 套皮仔 + 戀愛 hook a · 新女生加分到備胎（7 steps · ~73s · step 1 拆 3 beat、step 6 拆 3 beat ★★★）

**章節色票**：粉紅（新女生鋪）｜副 紅｜climax 灰（備胎前夕）→ 紅 stamp（備胎）

**Ambient shapes**：TL 粉圓 +10° · TR 紅圓 -6° · BL 粉方塊 +3° · BR 紅 pill -10° · 中左 灰圓 +5°（中左灰色暗示備胎情緒前夕）

**信息池**：

- 套皮仔 anchor：「社群已經有現成的 Python 工具箱、負責訓練的數學邏輯底層架構」—— 來源 `script.md` L167-169
- 戲劇崩盤句：「正當我以為成了套皮仔、就能成功訓練 AI⋯⋯**我又錯了**」—— 來源 `script.md` L171-173
- 計分策略 anchor：「**只要他填對一格就給分數**」—— 來源 `script.md` L177
- **戀愛 hook a 出場**：「就像剛認識新女生、每次聊天你都覺得對方也喜歡你、一直給你加分」—— 來源 `script.md` L181-183
- 瓶頸 anchor：「AI 只拿那些必拿的固定分數就不思進取、一直沒辦法完整解出一道題」—— 來源 `script.md` L187
- **戀愛 hook a 收**：「這個女生只把你當**備胎**、看似有進展、結果什麼都沒發生」—— 來源 `script.md` L189
- 揭穿 anchor：「AI 學會了**偷吃步**——只拿必拿的分數、就以為這樣行了」+ 「**計分標準寫錯了、AI 就會找漏洞作弊**」—— 來源 `script.md` L195-199

**開發計畫**：

- **step 1 (~11s)** — 過渡：「**⋯⋯我又錯了**」崩盤 punchline #2（破梗 fix #4、與 ch5 step 1 形成 motif rhyme）
  ▸ **類型** `cinematic` · **Motif 復用**: `motif/crash-line`（ch 5 step 1 首發、同款 cream + 6px 紅邊 + flash + 閃爍游標 placeholder）
  ▸ **placeholder 模式**: 「我又錯了」位置先放同款 cream + 6px 紅邊空框、僅閃爍游標 `_`、文字 hold 到 beat 3
  ▸ **Climax 加成 (輕量版)**: beat 3 `crash-fill` 套 A (screen-shake) + C (slow-mo overshoot)、與 ch 5 s1 同款手法（motif rhyme 一致性）· 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `kicker`: 上方字幕「正當我以為成了套皮仔⋯⋯」fade-down
    · **cue**: "正當我以為成了套皮仔、就能成功訓練出解數獨的 AI..."
  ▸ **beat 2** [click] `placeholder-frame`: 中央崩盤句空框出現（同 ch5 step 1 同款 motif、cream 大字框 + 6px 紅邊 + 微旋轉 -1° + 內部閃爍游標 `_`）
    · **cue**: "⋯⋯"（拖長尾音、觀眾此時應該已經認出 motif、預期下一拍會打字）
    · **wait**: 0.8s（比 ch5 step 1 短、因為觀眾已熟悉這 motif）
  ▸ **beat 3** [click] `crash-fill`: 空框內 mask-reveal 填入「**⋯⋯我又錯了**」+ 紅邊 flash + shadow burst
    · **cue**: "我又錯了"
    · **wait**: 1-2s 觀眾笑/嘆息（這次比 ch5 應該更有反應、因為觀眾發現「又」這個 motif rhyme）
  ▸ **氣質**: 重複 ch5 step 1 崩盤感、形成 motif rhyme（「結果我錯了」→「我又錯了」雙拍）
- **step 2 (~9s)** — 套皮仔策略：左側「**社群現成 Python 工具箱**」標籤 sticker（紫底、微旋轉）+ 右側 「**只要他填對一格 · 就給分數**」計分表 hero（卡片化、黑邊 + shadow + 填對 = +1 動畫）
  ▸ **類型** `cinematic + data-viz` · **進場**: 左 label slide-in → 右計分表 card stamp-in → 內部「+1」數字動畫 (count-up 0 → 1)
- **step 3 (~12s)** — **戀愛 hook a 出場**：cream 底 + 中央「**剛認識的新女生**」sticker（粉紅色 + 微旋轉、暗示「新鮮」）+ 「+/+/+」浮動加分動畫（多個綠色 + 符號從下浮起）+ 副標「**聊天都覺得對方也喜歡你**」
  ▸ **類型** `cinematic + progressive` · **進場**: 中央 sticker stamp-in → 「+/+/+」符號連續 spawn from below + float-up + fade (持續動畫) → 副標 fade-up · **持續微動**: 加分符號連續浮動
- **step 4 (~10s)** — 左側保留新女生 sticker + 右側「**AI 得分曲線**」(SVG path、黑線粗、cream 底)、scroll-trigger 概念棄、改 enter 時 path stroke-dasharray 0 → 100% 自動 draw（2s）、爬升曲線 + 標籤「+/+/+」對應點亮
  ▸ **類型** `data-viz` · **進場**: 曲線從左到右 stroke-draw（2s ease-out）+ 對應 +/+/+ 沿曲線標記 stagger · **climax**: 曲線完成的瞬間
- **step 5 (~12s)** — **瓶頸**：曲線進入畫面停留、卡平段 highlighted (紅色背景帶) + 字幕「**拿那些必拿的固定分數 · 就不思進取**」+ 「一直沒辦法完整解出一道題」副標 + 新女生 sticker 慢慢淡化 / 變灰
  ▸ **類型** `data-viz + cinematic` · **進場**: 卡平段紅色 highlight band fade-in → 字幕 mask-reveal → 新女生 sticker grayscale 漸變 (1s) · **氣質**: 從亢奮 → 失落
- **step 6 (~12s)** — **戀愛 hook a 收 · 「備胎」punchline ★★★**（破梗 fix #5、全 ch 6 最重笑點、必須完美控時）
  ▸ **類型** `cinematic` · **Motif 復用**: `motif/red-stamp`（紅 stamp 從天砸下、overshoot bounce、shadow burst）
  ▸ **placeholder 模式**: 「備胎」位置預先放**紅底 cream 邊空白 sticker**（旋轉 -3°、超大、shadow 16px、**內部僅有「  」空白字符位**）→ 等 beat 3 才填字
  ▸ **Climax 加成 ★★★ (全套)**: beat 3 `bei-tai-fill` 套 A (screen-shake) + B (halftone-burst) + C (slow-mo overshoot) + E (ink-splatter) + G (spotlight-vignette)、全片 #1 重要 climax 全火力 · 引用 [§全域視覺升級 v3 §7](#7-三大--climax-視覺加成5-效果) + 新增 motif: [`motif/spotlight-vignette`](#10-motif-library-新增-4-個-motif) / [`motif/halftone-burst`](#10-motif-library-新增-4-個-motif) / [`motif/ink-splatter`](#10-motif-library-新增-4-個-motif) / [`motif/screen-shake`](#10-motif-library-新增-4-個-motif)
  ▸ **beat 1** [click] `flash`: 黑色閃一下 (100ms flash)
    · **cue**: "結果後面開始遇到瓶頸——AI 只拿那些必拿的固定分數就不思進取了..."（鋪語境）
    · **wait**: 0.5s 給觀眾「視覺從錯覺切到現實」的反應時間
  ▸ **beat 2** [click] `subtitle-and-placeholder`: 中央出現紅底空白 sticker（內無字、僅 cream 邊輪廓）+ 下方副標「看似有進展 · 結果什麼都沒發生」fade-up
    · **cue**: "換句話說、這個女生只把你當——"（拉長尾音「當——」、給空 sticker 出現的反應時間、觀眾此時應該開始猜了）
    · **wait**: 1-2s 留懸念（這是全 step 最關鍵的停拍、演講者不要急著點下一 beat）
  ▸ **beat 3** [click] `bei-tai-fill`: 紅底空 sticker 內 mask-reveal 填入「**備胎**」+ scale 1.4 → 1 砸下感 overshoot + 紅邊 flash 2× + shadow burst 8px → 20px
    · **cue**: "備胎"（演講者念出當下視覺同步爆、節奏卡死、是 step 的「climax」）
    · **wait**: 3-4s 笑聲（這是 ch 6 最大笑點、不要急、停夠久再進 step 7）
  ▸ **climax**: beat 3 stamp 砸下瞬間（全 ch 6 最重的一拍）
  ▸ **破梗 fix #5 ★★★**: 原版「黑閃 → 備胎 stamp → 副標」一鍵全動畫進、視覺把「備胎」笑點在演講者開口前曝光；現拆三 beat，預留空 sticker + 副標已就位但「備胎」二字 hold 到演講者念出「當——」拉長尾音的停拍後才填入。**這是全片 #1 重要破梗 fix**
- **step 7 (~7s)** — 揭穿全屏：「**偷吃步**」紅 stamp 左上 + 「**計分標準寫錯了 · AI 就會找漏洞作弊**」hero 中央（cream 底、黑大字、紅底 + 黃底 雙色強調）
  ▸ **類型** `cinematic` · **進場**: 紅 stamp stamp-in → hero 文字 mask-reveal → 雙色強調 box stagger fade-in
  ▸ **D1 修正**: 原版這裡轉場 footer「我只好整個計分獎勵系統重寫」與 ch 7 step 1 主 hero「我只好整個計分獎勵系統重寫」是同一句、口播 (script.md L201) 只念一次但畫面出兩次。改為純做「偷吃步 / 找漏洞作弊」punchline 收尾、轉場留給 ch 7 step 1 開「重寫」hero

**口播節選**：

> 「填對一格就給分數⋯⋯剛開始得分急遽增長⋯⋯結果只把你當備胎⋯⋯計分標準寫錯了、AI 就會找漏洞作弊。」

---

## 7. reasoner — 重寫獎勵 + 13 招 + 戀愛 hook b · 老油條陷阱（8 steps · ~138s · step 6 拆 3 beat、step 7 拆 6 beat ★★★）

**章節色票**：cream + 黑（嚴肅底色）｜副 多色 sticker（紅／黃／紫）｜climax 紅底 + 黃「0」

**Ambient shapes**：TL 紅方塊 -8° · TR 紫星 +12° · BL 黃方塊 45° 旋轉 +5° · BR 黑描邊? -10° · 中右 紫圓 +3° · 中左 紅三角 -5°（章節最 dense ambient、配 13 招複雜感）

**信息池**：

- 重寫宣告 anchor：「**整個計分獎勵系統重寫**」+ 核心想法「**用人類玩數獨的解題技巧、反過來驗證 AI 的每一步**」—— 來源 `script.md` L201-205
- 13 招技巧 anchor：naked single / hidden single / **X-Wing** / Swordfish / **XY-Wing** 等共 **13 招**（真實技巧名、不是亂掰）—— 來源 `script.md` L209-211 + 真實程式碼 `reasoner/solver/techniques/`
- 顛倒驗證 anchor：**舊**「填對一格就給分」 vs **新**「AI 這一步、可以用人類技巧的哪一招解釋？越高階分越高」—— 來源 `script.md` L215-225
- Action 擴增 anchor：「多了**劃掉這格不可能是這個數**、消去類技巧才能展示」—— 來源 `script.md` L229-233
- 慘烈結果 anchor：「練了**兩千多萬次**——完整解出一道題的機率還是 **0**」—— 來源 `script.md` L237
- **戀愛 hook b 出場**：「**老油條女生陷阱題**——和你媽一起掉進水裡你會先救誰」「該不該去運動：說要 → 嫌她胖 / 說不用 → 不關心健康」—— 來源 `script.md` L241-257
- 死結 anchor：「AI 一直卡在永遠拿不到**整題解完**那個大獎」+ 「就跟我不知道陷阱題的正確解答一樣」—— 來源 `script.md` L265-269
- 反思過渡 anchor：「反向思考——先解出簡單的陷阱題答案、之後從容面對老油條」—— 來源 `script.md` L273-275

**開發計畫**：

- **step 1 (~11s)** — 過渡：「**我只好整個計分獎勵系統重寫**」hero（cream 底、黑大字、「重寫」黃底高亮）+ kicker「核心想法只有一個」
  ▸ **類型** `cinematic` · **進場**: hero mask-reveal + 「重寫」黃底 highlight slide-in · **氣質**: 嚴肅、轉折
  ▸ **視覺補強 (v3)**: 「重寫」黃底高亮 slide-in 完成瞬間加 80ms 整屏 `motif/screen-shake` 輕量版（±2px 而非 ±5px、僅 1 次而非 3 次）暗示「決心宣告」的重量感、不到 climax 規模但配嚴肅氣質
- **step 2 (~14s)** — 顛倒驗證宣告 full-screen 標語：「**用人類玩數獨的解題技巧 · 反過來驗證 AI 的每一步**」（超大 typography、關鍵詞「反過來」紅底 + 「驗證」黃底 highlight）
  ▸ **類型** `cinematic` · **進場**: 文字 mask-reveal 慢動 (1200ms) → 關鍵詞 stagger highlight · **climax**: 「反過來」「驗證」雙 highlight 同時亮 · **持續微動**: 主標題輕微 letter-spacing 微動
- **step 3 (~19s)** — **13 招大階梯**：cream 底、13 張小 sticker 從低（naked single / hidden single）排到高（X-Wing / Swordfish / **XY-Wing** / **XYZ-Wing**），階梯式由左下到右上排列、低階小且樸素、高階大且華麗（**X-Wing 跟 XYZ-Wing 最大、最華麗** · accent yellow / accent violet 底、6px 黑邊、微旋轉 -3° / 4°、12px shadow）+ 角標「**13 招 · 真實技巧名**」
  ▸ **類型** `progressive + interactive` · **進場**: 13 張 sticker 從低到高 stagger stamp-in（每張 80ms 間隔、1s 共完成）· **互動**: hover 任一 sticker → 該 sticker scale 1.15 + 其他 dim opacity 0.5 + tooltip 浮出該招中文簡介 · **climax**: 13 張全 stamp 完的瞬間
- **step 4 (~17s)** — **舊 vs 新對比動畫**：split-screen 60/40、左「**舊：填對一格就給分**」（只有一招亮 + 一個分數浮現）vs 右「**新：可以用哪一招解釋？**」（每張技巧都可以亮 + 高招分數更高、+1 +2 +3 浮動）
  ▸ **類型** `comparison + data-viz + interactive` · **進場**: split-screen wipe-in → 左側單一招亮起 + 數字 +1 → 右側多招陸續亮起 + 不同高度分數浮動 stagger · **互動**: hover 左 / 右 → 該側放大 dim 對立側 · **climax**: 右側 X-Wing 亮 + +3 分浮起
- **step 5 (~13s)** — Action 擴增：「**多了一倍可以做的事**」hero + 中央 9×9 mini 盤面動畫，「**填一個數字**」(綠) + 「**劃掉這格不可能是這個數**」(紅斜線) 兩種動作示意動畫 + 副標「消去類技巧才能展示出來」
  ▸ **類型** `data-viz + interactive` · **進場**: hero 上方 fade-in → mini 盤面 stamp-in → 填數字綠動畫 → 劃掉紅斜線動畫 (stagger 600ms) · **持續微動**: 盤面 loop 動畫示意兩動作交替
- **step 6 (~16s)** — **慘烈結果 · 「0」punchline**（破梗 fix #7）
  ▸ **類型** `cinematic + data-viz` · **Motif 復用**: `motif/red-stamp`（「0」用紅 stamp 形式砸下）
  ▸ **placeholder 模式**: 「機率還是」後面預留閃爍游標 `_` 佔位、「0」hold 到 beat 3
  ▸ **Climax 加成 (輕量+)**: beat 3 `zero-drop` 套 A (screen-shake) + B (halftone-burst) + C (slow-mo overshoot) + E (ink-splatter)、「0」實體 stamp 性質配重火力（不放 G spotlight 留給 ch7 s7 climax 之後）· 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `count-up`: 底色閃紅 → 全屏紅底進入 → cream 大字「練了 **兩千多萬次**」count-up 0 → 2,000,000+（2s 動畫）
    · **cue**: "結果呢——練了兩千多萬次..."
    · **wait**: 0.5s 給數字落定
  ▸ **beat 2** [click] `subtitle-placeholder`: 下方副標「完整解出一道題的機率還是」mask-reveal + 句末預留**閃爍游標 `_`** 佔位（無「0」字）
    · **cue**: "完整解出一道題的機率還是——"（拉長尾音「還是——」、停拍給觀眾猜）
    · **wait**: 1-2s 留懸念（觀眾此時應該已經猜到「0」）
  ▸ **beat 3** [click] `zero-drop`: 游標 `_` 消失 → 「**0**」超大字從上 drop-in（overshoot bounce、scale 0 → 1.4 → 1、accent yellow 底）+ 紅底 flash 2× + shadow burst
    · **cue**: "零"（演講者念出當下視覺同步爆）
    · **wait**: 2-3s 嘆息/笑聲（觀眾與演講者的「失敗共感」）
  ▸ **climax**: beat 3 「0」砸下瞬間 + 紅底 flash
  ▸ **破梗 fix #7**: 原版「兩千多萬次 count-up + 0 drop-in 同 step」、視覺把「失敗到底」結論在演講者念出前曝光；現拆三 beat、句末閃爍游標 placeholder 預告「即將揭曉」、數字 hold 到演講者念「零」當下砸下
- **step 7 (~26s)** — **戀愛 hook b 全面展開 · 老油條陷阱題 ★★★**（破梗 fix #6、6 beat 控答案揭示、ch 7 最大笑點群）
  ▸ **類型** `interactive + comparison` · **Motif 首發**: `motif/girl-veteran`（陷阱題 sticker 樣式、後續 ch 9 step 6 復用同款）
  ▸ **placeholder 模式**: 兩個答案箭頭 ❌ 預先佔位但**文字 hold**（先顯示「說要 → ???」「說不用 → ???」、等對應 beat 才填出「嫌她胖／不關心健康」）
  ▸ **Climax 加成 ★★★ (分 beat 套)**: beat 4 `answer-a-fill` + beat 5 `answer-b-fill` 各套 A (screen-shake) + E (ink-splatter) + G (spotlight-vignette)；beat 6 `both-flash` 套 B (halftone-burst) × 2（從兩個 ❌ 同時 burst）· 引用 [§全域視覺升級 v3 §7](#7-三大--climax-視覺加成5-效果)、ch 7 全段最大笑點群
  ▸ **beat 1** [click] `hero`: 上方 hero「**老油條女生陷阱題**」mask-reveal + 黃底高亮（`motif/yellow-highlight` 復用）
    · **cue**: "這個感覺就是、你剛開始學習如何跟女生互動..."
    · **wait**: 0.5s
  ▸ **beat 2** [click] `trap-1`: 左 sticker「**和你媽一起掉進水裡 · 你會先救誰？**」從左 swing-in（紅底 cream 字、微旋轉 -3°、overshoot）
    · **cue**: "但是那些女生都是老油條、他們都會問一些奇奇怪怪的問題。例如——和你媽一起掉進水裡你會先救誰？"
    · **wait**: 2s 觀眾笑（這題本身就是 trigger）
  ▸ **beat 3** [click] `trap-2-question`: 右 sticker「**你覺得我該不該去運動？**」從右 swing-in（紫底 cream 字、微旋轉 4°、overshoot）+ **下方兩個答案箭頭以「???」placeholder 形式同步出現**（先看到「說要 → ???」「說不用 → ???」）
    · **cue**: "每道都是陷阱題。舉個例子，『你覺得我該不該去運動？』這道題——"
    · **wait**: 1s 給觀眾自己心裡想答案
  ▸ **beat 4** [click] `answer-a-fill`: 「說要」箭頭 placeholder「???」mask-reveal 填入「**❌ 嫌那個女生胖**」+ ❌ 紅 flash
    · **cue**: "你回答要去運動——那就是你嫌那個女生胖"（演講者念出當下視覺同步揭曉）
    · **wait**: 2s 笑點
  ▸ **beat 5** [click] `answer-b-fill`: 「說不用」箭頭 placeholder「???」mask-reveal 填入「**❌ 你不關心健康**」+ ❌ 紅 flash
    · **cue**: "你回答不用去運動——那就是你不關心那個女生的身體健康"
    · **wait**: 2s 笑點
  ▸ **beat 6** [auto, 400ms] `both-flash`: 兩個 ❌ 同步雙 flash 強調「兩面不討好」+ 兩 sticker hover 互動啟用
    · **氣質**: 滑稽、共鳴、給觀眾消化雙 ❌ 反差
  ▸ **互動**: 步內 hover 任一 sticker → 該 sticker 放大 + 對應 ❌ 紅 flash（純視覺、不影響推進）
  ▸ **climax**: beat 6 雙 ❌ 同步 flash 瞬間
  ▸ **破梗 fix #6 ★★★**: 原版「兩 sticker + 兩答案 ❌ 全部 stagger 進場」、觀眾在演講者念「你回答要去運動」之前就看到「❌ 嫌她胖」答案、整段笑點直接破。現拆 6 beat：題目先出（觀眾自己想答案）→ 演講者念「你回答 X」→ 才填入對應 ❌。觀眾與演講者同步走完「兩面不討好」邏輯、笑點才會炸
- **step 8 (~20s)** — **死結**：cinematic 黑底 → cream 大字「**AI 永遠拿不到「整題解完」那個大獎**」+ 副標「**就跟我不知道陷阱題的正確解答一樣**」+ 角落「**反向思考⋯**」鋪墊 footer
  ▸ **類型** `cinematic` · **進場**: 底色 cream → 黑 fade (800ms) → 主標 mask-reveal 慢動 (1500ms) → 副標 fade-up → footer 從下 slide-in · **氣質**: 沉重、留白、為下章鋪墊 · **轉場**: 「反向思考⋯」footer 提示下章方向

**口播節選**：

> 「13 招數獨技巧——naked single、X-Wing、XY-Wing⋯⋯練了兩千多萬次、解出整題機率還是 0⋯⋯就跟我不知道老油條陷阱題的正確解答一樣。」

---

## 8. apprentice — 反向課程 + visualizer（6 steps · ~66s + visualizer 30~60s）

**章節色票**：cream + 金黃（突破底色）｜副 紫（盤面）｜climax 黃 (+50 翻牌)

**Ambient shapes**：TL 黃星 +10°（強）· TR 紫方塊 -8° · BL 金圓 +3° · BR 黃星 -12°（章節氣質最開朗、雙黃星呼應「+50」突破）

> 本章為視覺高潮 + 整片唯一可挂真實 tensorboard 截圖（使用者表示有素材可挂）+ 現場 visualizer cue。

**信息池**：

- 反向思考 anchor：「**我把題目反過來給他**——一開始只給 3 格空的盤面、90% 都填好了、他一定解得出來」—— 來源 `script.md` L273-279
- 反向課程 anchor：「能穩定解、我再加一格空、再加一格⋯⋯讓難度跟著他的能力走」—— 來源 `script.md` L281-285
- 破關獎勵翻牌 anchor：「我同時把破關獎勵調更大——從 **+20 拉到 +50**」+ 「讓完成整題的訊號更明確、誘惑超過固定刷取部分分數的招數」—— 來源 `script.md` L287-291 + 真實程式碼 `reasoner/env/reward_computer.py:8 (=20)` + `apprentice/env/reward_computer.py:8 (=50)`
- 突破 anchor：「從 3 個空格慢慢加到 10 個——他**終於開始解出整題**」—— 來源 `script.md` L293
- 真實素材 anchor：**tensorboard 截圖**（勝率曲線 / curriculum step 圖）—— 使用者確認有素材可挂
- visualizer 大按鈕設計：cream 底 + 粗黑邊 + 強陰影 + accent red 字 + sticker 微旋轉、「點我看 AI 即時解數獨 →」—— 來源 `prompt.md` §六 #7

**開發計畫**：

- **step 1 (~10s)** — 過渡：黑底慢慢回 cream + 「**反向思考 · 先解簡單的陷阱題答案**」hero + 副標「之後從容面對老油條」+ 下方 footer「AI 也是、我把題目反過來給他 →」
  ▸ **類型** `cinematic` · **進場**: 底色 fade → hero mask-reveal + 「反向思考」紅底高亮 → footer slide-up · **氣質**: 開朗、解題感
  ▸ **視覺補強 (v3)**: 底色 fade 由純 CSS `background-color` 1.2s `cubic-bezier(0.4, 0.0, 0.2, 1)` 自然減速完成、同步 halftone dots opacity 0 → 1 漸入（dots 「逐漸顯影」配合黑底退去的視覺）。避免色塊硬切、cinematic 氣質保持。注意：本 step 章內轉場、不用 View Transitions API（VT 僅用於章節切換）
- **step 2 (~12s)** — **反向課程登場**：中央 9×9 數獨盤面（黑邊、cream 格子、Space Grotesk 700 數字、90% 已填）+ 副標「**只有 3 格空**」+「他一定解得出來」kicker
  ▸ **類型** `data-viz + cinematic` · **進場**: 盤面從 scale 0.85 stamp-in → 「只有 3 格空」mask-reveal → 3 個空格 highlight 紅色 outline pulse · **climax**: 3 個空格 pulse 同步
- **step 3 (~12s)** — **反向課程動畫**：盤面從 **3 → 4 → 5 → 6 → 7 → 8 → 9 → 10** 空（連續一格一格自動揭示、每次格子被「擦掉」變空、~500ms 一格、scale 0.95 → 1 transition、共約 3.5s）+ 副標「**讓難度跟著他的能力走**」 + 計數器「空格: 3 → 10」count-up
  ▸ **節奏對齊**: 原版用 3→4→5→7→10 跳格（不連續）、口播 script.md L281「他能穩定解、我再加一格空、**再加一格**⋯⋯」是「一格一格」的延續感、所以改為連續 3→4→5→6→7→8→9→10 八步
  ▸ **類型** `data-viz + progressive` · **進場**: 自動進入動畫 (~5s 完成 3→10)、計數器同步 count-up · **持續微動**: 完成後盤面輕微 shake 暗示「難度持續上升」
- **step 4 (~10s)** — **數字翻牌**：cinematic 全屏 → cream 底 + 中央 **「+20 → +50」**大字翻牌動畫 (3D flip rotateY 600ms、shadow 翻面換邊)、20 紅色、50 黃色 + 副標「**破關獎勵調更大**」+ 下方「誘惑超過刷部分分數的賤招」
  ▸ **類型** `data-viz + cinematic` · **進場**: 「+20」stamp-in → hold 500ms → flip 3D → 「+50」snap (overshoot、shadow 加深) → 副標 fade-up · **climax**: flip 完成瞬間
- **step 5 (~9s)** — 過渡：「**光講不夠看**」hero kicker + 「**給大家看一下 AI 即時解數獨的題目**」副標 + 中央向下大箭頭（指向下一 step 的 visualizer 大按鈕）
  ▸ **類型** `cinematic` · **進場**: 「光講不夠看」mask-reveal → 「給大家看」fade-up → 向下大箭頭 stroke-draw + bounce · **持續微動**: 箭頭 bounce 上下
  ▸ ⚠️ **原 step 5「tensorboard 截圖」已挪去 ch 9 step 1**——因 script.md L293→L297→L299 直接從「終於解出整題」跳到「光講不夠看」、中間沒有口播提及訓練曲線、tensorboard 在此步會卡空白。挪到 ch 9 開頭「AI 還在訓練中、但有在進步」當視覺證據
- **step 6 (~10s + visualizer 30~60s)** — **visualizer 大按鈕** 獨佔整屏：cream 底 + **「點我看 AI 即時解數獨 →」**超大按鈕（粗黑邊 6px、強 hard shadow 16px、accent red 文字、微旋轉 -2°、hover 時 scale 1.05 + shadow 變深）。按鈕 `href="sudoku-demo:run"` —— **點擊直接觸發 Windows custom URL scheme**、自動啟動桌面 pygame 視窗、不需要演講者手動 Alt+Tab
  ▸ **類型** `cinematic + interactive` · **進場**: 按鈕從 scale 0.8 stamp-in（overshoot）· **互動**: hover 按鈕 → scale 1.05 + shadow 16px → 20px + 紅底深一階 (mechanical feedback、模仿物理 button) · **氣質**: 全片最強 cinematic moment、留給演講者切換實機
  ▸ **啟動機制**: HTML 端 `<a href="sudoku-demo:run">` → 觸發瀏覽器 custom protocol → 對應到 HKCU registry → 跑 `demo/visualizer-launch/launcher.bat` → `cd <repo root> && python -m apprentice.demo.visualize` → pygame 視窗 0.5-1s 內 pop-up 並自動搶到最上層（pygame 預設行為）→ AI 解數獨 30-60s → 演講者關閉視窗 → 簡報自動回最上層
  ▸ **portable 部署**：所有 .bat 都從 `%~dp0` 自動偵測 `sudoku_old/` 根目錄、不寫死路徑。新機只需跑一次 `demo/visualizer-launch/install.bat`（自動 `pip install -r requirements-demo.txt` + 自動寫 HKCU registry、不需 admin）。詳見 [demo/visualizer-launch/README.md](visualizer-launch/README.md)
  ▸ ⚠️ **此決策 override `prompt.md` 第六節 #7**：原 #7「禁止演講者手動切桌面 pygame」+「主路線 pygbag iframe」已被取代。`apprentice/demo/visualize.py` 用 SB3 MaskablePPO + PyTorch、ONNX 轉換不確定性高（27-ConstraintHead features extractor 可能無法直接 export）、實測工作量 3-7 天。改走 URL scheme 桌面啟動：零 WASM 風險、保留現場 live inference 氣勢、演講者操作從 2 步（點 + Alt+Tab）變 1 步（只點）。`prompt.md` 第六節 #7 待同步修正

**口播節選**：

> 「我把題目反過來給他——一開始只給 3 格空⋯⋯破關獎勵 +20 拉到 +50⋯⋯3 空慢慢加到 10、他終於開始解出整題。光講不夠看、給大家看一下 AI 即時解數獨。」

---

## 9. callback — AI 也在訓練我（13 steps · ~204s · step 5 拆 4 beat、step 11 拆 4 beat、step 13 拆 4 beat ★★★）

**章節色票**：cream（純，收尾底色）｜副 紫 (plasticity)｜climax 紅（電費小偷 final）

**Ambient shapes**：TL 紫圓 +5° · TR 紅星 -10° · BL 紫描邊方塊 +8° · BR 灰描邊? -3°（章節氣質沉思收斂、灰描邊?暗示哲思）

> **結尾長章例外**：超過 OUTLINE-FORMAT 建議的「每章 3~8 步」上限，因 script.md L303-375 結尾為壓軸大段、無法切兩章保持節奏。原 14 step 已合併 MBTI + 業務工作 (step 10+11 → step 10) 縮成 13 step、降低結尾點擊密度。

> **Motif callback 章**：本章必須大量引用 [Motif Library](#motif-library視覺母題復用庫) 母題，喚起觀眾前段視覺記憶 = callback 笑點力道 +30%。各 step 引用以 `▸ **Motif 復用**:` 行標註。

**信息池**：

- 過渡 anchor：「最後因為時間不太夠、我這個 AI 還在訓練中、但是你可以看到 AI 是有在進步的⋯⋯**我跟對方還在磨合期**⋯⋯最後我想跟大家講一件事」—— 來源 `script.md` L303-307
- 核心金句 anchor：「**這兩個月、我不只在訓練 AI、AI 也在訓練我**」—— 來源 `script.md` L309
- RL 對等 anchor：「試錯加獎懲——腦科學裡這叫 reinforcement learning、AI 訓練也叫 RL、其實**是同一件事**」—— 來源 `script.md` L313-317
- 飛機鳥 anchor：「**AI 在模仿人類**——就像當初的飛機、也是人類模仿鳥類才造出來的」—— 來源 `script.md` L319
- 戀愛 a callback：「追一個人——對方回訊息你就被加分、已讀不回你就被扣分、大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷、**跟 AI 訓練一模一樣**」—— 來源 `script.md` L323-329
- 戀愛 b callback：「以為穩了結果魔王關卡——**前女友跟我比、誰比較好** / **你心中的女神是誰** / **你喜歡我哪裡** / **猜猜看今天我哪裡不一樣**」—— 來源 `script.md` L333-343
- plasticity 引出：「最後再跟大家分享一個我最喜歡的心理學底層概念——**大腦可塑性 plasticity**」—— 來源 `script.md` L347-349
- plasticity 三項對等：「AI 沒有天生會解數獨、跟你出生不會講話、跟你不是天生就懂怎麼跟人相處——**一樣**」—— 來源 `script.md` L351
- plasticity 機制：「每改一次 reward function、每談一場戀愛、每學一個新東西——底層都是 reward 加加減減、**每次都把我們重新塑造一次**」—— 來源 `script.md` L353-355
- **MBTI 自我故事 anchor**：「我真的是一個**極度的 I 人**、之前測 MBTI 我有 **100% 的時間都偏向 I 人**、明明我很 E」—— 來源 `script.md` L359-361（注意：script 沒提 INFJ、所以畫面 sticker 改用「極度 I 人」與口播對齊）
- **業務工作變 E anchor**：「我後來逼自己跳脫舒適圈、去做了一份**業務工作**、天天逼自己跟陌生人講話、才慢慢變得比較 E」—— 來源 `script.md` L363
- 不被擊敗 anchor：「遇到不會回答的魔王陷阱題沒有關係、我們只要從**挫敗中學習**就行了。但是不要停滯不前——跟一個女生聊天、結果**人生第一次的外向、換來一輩子的內向**」—— 來源 `script.md` L367-369
- 職場祝福 anchor：「繼續嘗試跟其他女生聊天——不是每個女生都那麼老油條。也祝大家未來在職場上能夠保有同樣的精神——**不被挫敗給擊敗**」—— 來源 `script.md` L371-373
- **電費小偷結尾笑話 anchor (verbatim)**：「最後再補個笑話 - 想必大家未來出職場後都是薪水小偷。但我不一樣，我是**電費小偷**、我這**兩個月**一直用班上的電腦瘋狂訓練我的 AI」—— 來源 `script.md` L375

**開發計畫**：

- **step 1 (~12s)** — 過渡：cream 底 + 上方「AI 還在訓練中⋯⋯**我跟對方還在磨合期**」字幕 + **左右雙圖：真實 tensorboard 截圖**（左 success_rate 曲線、右 curriculum target_empty 圖；6px 黑邊 + 12px shadow 框）+ 下方「**但你可以看到 · AI 是有在進步的**」副標 + 中央「**最後我想跟大家講一件事**」hero（黑大字、stamp-in）
  ▸ **類型** `data-viz + cinematic` · **進場**: 字幕 fade-down → 左圖從左 slide-in → 右圖從右 slide-in (stagger 200ms) → 副標 fade-up → hero mask-reveal 慢動 (900ms) · **氣質**: 過渡、收斂、為金句鋪墊；真實素材給 callback「AI 在進步」具象視覺證據
  ▸ **資料來源**: ⚠️ 待使用者匯出截圖至 `demo/presentation/public/images/tensorboard/` 並提供路徑——對應 script.md L303「AI 還在訓練中、但是你可以看到 AI 是有在進步的」
  ▸ **設計來源**: 本 step 整合原 ch 8 step 5「tensorboard 截圖」素材——挪到這裡因為 script 在此處才有對應口播（「AI 還在訓練中、但是你可以看到 AI 是有在進步的」）
- **step 2 (~14s)** — **核心金句 cinematic full-bleed**：「**這兩個月 · 我不只在訓練 AI / AI · 也在訓練我**」（cream 底、accent red 巨字、6px 黑邊框、letter-spacing 動畫）
  ▸ **類型** `cinematic` · **進場**: 文字 mask-reveal 慢動 1200ms + letter-spacing 0.05em → 0em 收緊 · **climax**: 「AI 也在訓練我」最後三字砸下 (stamp + 紅底 flash) · **氣質**: 全片金句、最重的 hero
- **step 3 (~12s)** — **RL 對等動畫**：split-screen 左「**腦科學 RL**」（黑底 cream 字、大腦 sticker）/ 右「**AI 訓練 RL**」（cream 底黑字、神經網路 sticker）+ 中央「**=**」大字（黃底圓形 sticker、stamp-in）+ 下方「**其實是同一件事**」hero
  ▸ **類型** `comparison + cinematic` · **進場**: 左右 split wipe-in → 中央「=」stamp-in (overshoot) → 下方 hero mask-reveal · **climax**: 「=」砸下瞬間
- **step 4 (~10s)** — **飛機鳥 sticker**：cream 底 + 上方「**AI 在模仿人類**」hero + 中央飛機（純 SVG 線稿、黑線）+ 鳥（純 SVG 線稿、黃色填充）並置、中央「←」箭頭暗示「模仿」+ 副標「就像飛機 · 是人類模仿鳥類才造出來」
  ▸ **類型** `cinematic + depth` · **進場**: hero fade-in → 飛機從左 slide-in → 鳥從右 slide-in → 「←」箭頭 stroke-draw · **持續微動**: 鳥輕微振翅、飛機輕微 yaw
- **step 5 (~18s)** — **戀愛 a callback · 「跟 AI 一模一樣」punchline**（破梗 fix #8）
  ▸ **類型** `comparison + data-viz + cinematic`
  ▸ **Motif 復用**: `motif/girl-new`（ch 6 step 3 粉紅新女生 sticker 退到背景、灰階、暗示「就是那個女生」）
  ▸ **placeholder 模式**: 「跟 AI 訓練一模一樣」紅底 hero 預留位、文字 hold 到 beat 4
  ▸ **Climax 加成 (輕量版)**: beat 4 `punchline-hero` 套 A (screen-shake) + C (slow-mo overshoot) · 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `bg-callback`: 背景退入 `motif/girl-new`（ch 6 粉紅新女生 sticker、灰階、opacity 0.3、退到最底層）+ 中央大腦 sticker（黑線稿 + 內部紫色 reward 漂浮）stamp-in
    · **cue**: "追一個人的時候——"
  ▸ **beat 2** [click] `left-positive`: 左欄「**回訊息**」綠色 +/+/+ 連續 spawn 從下浮起（持續動畫）
    · **cue**: "對方回訊息你就被加分"
    · **wait**: 1s 給觀眾建立左右對照預期
  ▸ **beat 3** [click] `right-negative`: 右欄「**已讀不回**」紅色 -/-/- 連續 spawn 從上沉（持續動畫）
    · **cue**: "已讀不回你就被扣分"
    · **wait**: 1.5s 給觀眾感受加分扣分的拉扯
  ▸ **beat 4** [click] `punchline-hero`: 下方紅底全屏 hero 預留位 mask-reveal 填入「**跟 AI 訓練一模一樣**」+ 紅底 flash 2× + shadow burst + 中央大腦的紫色 reward 與兩側 +/+/- 漂浮同步加速
    · **cue**: "你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練"（最後三字「一模一樣」前點下、字一邊出演講者一邊念）
    · **wait**: 2s 觀眾領悟、回想 ch 6/7 戀愛 hook
  ▸ **持續微動**: +/+/+ 與 -/-/- 連續浮動
  ▸ **climax**: beat 4 紅底 hero 砸下瞬間
  ▸ **破梗 fix #8**: 原版「split wipe-in → +/+/- → 大腦 sticker → 紅底 hero」全 stagger 連續觸發、紅底 hero 「跟 AI 一模一樣」在演講者鋪「對方回訊息你就被加分」前就出現。現拆 4 beat、紅底 hero 預留位、文字 hold 到演講者鋪完上下加扣分鋪墊後才填入
- **step 6 (~18s)** — **戀愛 b callback**：cream 底 + 上方「**以為穩了 · 結果魔王關卡**」hero + 中央 **4 個考題 sticker grid 並排** (2×2、每張不同底色 + 微旋轉)：
  - 「**前女友跟我比 · 誰比較好？**」（黃底）
  - 「**你心中的女神是誰？**」（紫底）
  - 「**你喜歡我哪裡？**」（紅底 cream 字）
  - 「**猜猜看 · 今天我哪裡不一樣？**」（cream 底 + 描邊）

  ▸ **類型** `interactive + cinematic` · **進場**: hero fade → 4 sticker 從 grid 中心 stagger stamp-in (each 150ms 間隔) · **互動**: hover 任一 sticker → scale 1.1 + shadow 加深 + 其他 dim 0.5 + 該題下方浮現「⋯⋯（沒有正解）」副標 · **氣質**: 滑稽、共鳴
  ▸ **Motif 復用**: `motif/girl-veteran`（ch 7 step 7 老油條陷阱題 sticker 樣式繼承——4 個考題 sticker 用同款「斜貼、不同底色、微旋轉」視覺語言、暗示「這就是 ch 7 那個老油條 → 你現在懂了吧」、觀眾自動勾起 ch 7 笑點記憶）
- **step 7 (~8s)** — **plasticity 引出**：cinematic 全屏 cream → 上方「最後再跟大家分享」kicker → 中央「**大腦可塑性 · plasticity**」hero (中文 + 英文並列、英文 letter-spacing 撐開)
  ▸ **類型** `cinematic` · **進場**: kicker fade-down → hero mask-reveal 慢動 (1000ms) + 「plasticity」英文 letter-spacing 0.3em → 0.05em 收緊 · **氣質**: 學術感、慢拍
- **step 8 (~12s)** — **plasticity 三欄對位**：cream 底、三欄並列：
  - 欄 1: 「**AI** 沒天生會 · 解數獨」(紅底 sticker)
  - 欄 2: 「**你** 出生不會 · 講話」(黃底 sticker)
  - 欄 3: 「**你** 不是天生會 · 跟人相處」(紫底 sticker)
  - 中央巨字「**一樣**」(cream 底、黑超大字、stamp-in)

  ▸ **類型** `comparison + cinematic` · **進場**: 三欄 stagger fade-up (each 200ms 間隔) → 中央「一樣」從 scale 0 砸下 (overshoot + 紅邊 flash) · **climax**: 「一樣」砸下瞬間
  ▸ **Motif 復用**: `motif/13-stairs`（背景以**極淡 opacity 0.08**、灰階的 ch 7 13 招階梯縮小化平鋪、暗示「就像那 13 招 AI 也是學出來的」、視覺潛意識勾起 ch 7 學習進階感、不搶前景文字焦點）
- **step 9 (~12s)** — **plasticity 機制**：cinematic + 中央「**每次都把我們重新塑造一次**」hero + 上方副標「每改一次 reward function、每談一場戀愛、每學一個新東西」(三項 stagger reveal)
  ▸ **類型** `cinematic + progressive` · **進場**: 副標三項 stagger fade-up (each 240ms 間隔) → 主 hero mask-reveal 慢動 + 「重新塑造」黃底高亮 · **氣質**: 哲思、慢動
  ▸ **Motif 復用**: `motif/flip-20-to-50`（背景以**極淡 opacity 0.06**、灰階的「+20 → +50」3D flip 翻牌 loop 動畫平鋪、暗示「reward 加加減減」的循環、視覺潛意識勾起 ch 8 突破感、不搶前景 hero 焦點） + `motif/yellow-highlight`（「重新塑造」黃底）
- **step 10 (~22s)** — **MBTI 自我故事 + 業務工作變 E**（合併原 step 10+11）：cream 底 + 上方「我真的是一個 **極度的 I 人**」kicker
  - **第一拍 (0-9s)**：中央 **MBTI 圓餅視覺**（圓餅完整黑邊、I 紫色填滿 100%、E 0%、cream 中心）+ 右側「**極度 I 人**」標籤 sticker（紫底、6px 黑邊、微旋轉 -3°、stamp-in）+ 副標「明明我很 E」（黃底高亮）
  - **第二拍 (9-22s)**：圓餅 sticker 縮到左側 30% 寬、右側 70% 拉出 **「業務工作」標籤 sticker** (黃底、微旋轉 2°、stamp-in) + **I → E 漸變條** (水平條、從紫色 I → 紅色 E、indicator 動畫從 I 0% 移到 60%、4s) + 副標「天天逼自己跟陌生人講話 · 才慢慢變得比較 E」
    ▸ **類型** `data-viz + progressive` · **進場**: kicker fade-down → 圓餅 0% → 100% I 填滿動畫 (1.5s) → 「極度 I 人」sticker 砸下 (overshoot) → 副標 fade-up · **第二拍觸發**: 步內第二拍由 step 內動畫自動觸發（hold 1.5s 後）、不需要演講者額外點擊 → 圓餅縮側 (600ms ease) → 業務 sticker stamp-in → 漸變條 fade-in → indicator 移動 (4s) → 副標 stagger · **climax**: 圓餅 100% I 填滿瞬間 + indicator 抵達 60% 瞬間
    ▸ **合併來源**: 原 step 10 (14s MBTI) + step 11 (14s 業務工作) = 28s。合併為單一複合 step (22s)、保兩段資訊密度但縮一個點擊節點（ch 9 從 14 step → 13 step、降低結尾點擊密度）。對應 script.md L359-365 連續一段、原本就沒有 `---` 分隔
- **step 11 (~18s)** — **不被擊敗 · 警語拆兩段揭示**（破梗 fix #9、整片最重一拍）
  ▸ **類型** `cinematic` · **Motif 復用**: `motif/crash-line`（cream + 6px 紅邊 + flash、與 ch 5/6 崩盤 motif 同源、但放大成「警語」尺度）
  ▸ **placeholder 模式**: 警語 sticker 預先放空 cream + 6px 紅邊大框（內部閃爍游標 `_`、無文字）→ 兩段 punchline 拆兩次 click 填入
  ▸ **Climax 加成 (輕量+ 警語版)**: beat 4 `warn-line-b-fill` 套 A (screen-shake) + C (slow-mo overshoot) + G (spotlight-vignette)、警語性質聚焦合理、shadow burst 8px → 20px 配 spotlight 暗化外圍效果加成 · 引用 [§全域視覺升級 v3 §8](#8-一般-punchline--climax-輕量版)
  ▸ **beat 1** [click] `kicker-and-frame`: 上方「從挫敗中學習就行了」kicker fade-down + halftone dots 加密 (400ms) + 中央警語 sticker 空框出現（cream 底、6px 紅邊、微旋轉 -2°、超大、內部閃爍游標 `_`）
    · **cue**: "所以遇到不會回答的魔王陷阱題沒有關係、我們只要從挫敗中學習就行了..."
    · **wait**: 1s 鋪正面語氣
  ▸ **beat 2** [click] `subtitle`: 下方副標「但是不要停滯不前」fade-up
    · **cue**: "但是不要停滯不前——"（停拍、語氣轉折、觀眾預期反轉）
    · **wait**: 1s
  ▸ **beat 3** [click] `warn-line-a-fill`: 警語空框內**上半行** mask-reveal 填入「**人生第一次的外向**」（accent red 大字）+ 紅邊 flash 1×
    · **cue**: "跟一個女生聊天、結果——人生第一次的外向"
    · **wait**: 1-1.5s 停拍、給觀眾預期下半句反轉
  ▸ **beat 4** [click] `warn-line-b-fill`: 警語空框內**下半行** mask-reveal 填入「**· 換來一輩子的內向**」（accent red 大字）+ scale 1.3 → 1 snap 整 sticker overshoot + 紅邊 flash 2× + shadow burst 從 8px → 20px
    · **cue**: "換來一輩子的內向"（演講者念出當下視覺同步爆）
    · **wait**: 3-4s 停拍（整片最重的一拍、不要急、給觀眾完全消化反轉）
  ▸ **climax**: beat 4 警語全文落定 + shadow burst + 紅邊 flash（全 ch 9 第二重 climax、僅次電費小偷 final）
  ▸ **破梗 fix #9**: 原版整段警語 1 click stamp、觀眾在演講者念「跟一個女生聊天」前就看到完整警語、「外向 → 內向」反轉笑點直接破。現拆 4 beat、警語拆成「人生第一次的外向」+「換來一輩子的內向」兩段揭示、卡在演講者念句子的兩段反轉節奏上
  ▸ **設計來源**: 原版用「黑底紅字」會脫離 web_style.md cream 主畫布的 visual DNA。改為「cream + accent red 大字 + 6px 紅邊 + 20px shadow + halftone 加密」表達警語的重量感（保 brutalism 連續性、力道靠 shadow + flash + halftone 加密、不靠切黑底）
- **step 12 (~12s)** — **職場祝福**：cream 底回歸 + 上方「繼續嘗試跟其他女生聊天」kicker + 中央「**祝大家未來在職場上 · 不被挫敗給擊敗**」hero（黑大字、「不被挫敗給擊敗」紅底高亮、cream 字）+ 下方「不是每個女生都那麼老油條」副標
  ▸ **類型** `cinematic` · **進場**: kicker fade-down → hero mask-reveal + 紅底高亮 slide-in → 副標 fade-up · **氣質**: 正能量、收斂、為最後笑話鋪墊
- **step 13 (~28s)** — **電費小偷結尾笑話 verbatim · final ★★★**（破梗 fix #10、全片最後一個笑點、4 beat 必須完全卡死節奏）
  ▸ **類型** `cinematic`
  ▸ **Motif 復用**: `motif/boom-double-ring` 縮小化（「電費小偷」FINAL sticker 圍邊、暗示「最後的 BOOM」、首尾呼應 ch 1 step 8） + `motif/red-stamp` + `motif/yellow-highlight`
  ▸ **placeholder 模式**: 「薪水小偷」與「電費小偷」配對中、「電費小偷」位置先放「**我不一樣 → ?**」空泡泡（cream 底、6px 黑邊、紅色問號 ?、微旋轉 -3°）→ 等 beat 3 才填字
  ▸ **Climax 加成 ★★★ (全套 + 加碼)**: beat 3 `power-thief-fill` 套 A (screen-shake) + B (halftone-burst) + C (slow-mo overshoot) + E (ink-splatter) + G (spotlight-vignette) + 既有 `motif/boom-double-ring` 縮小化雙圈圍邊 + 整屏 cream 底 micro-shake 150ms — **全片視覺火力最強的一拍**、首尾呼應 ch 1 step 8 BOOM · 引用 [§全域視覺升級 v3 §7](#7-三大--climax-視覺加成5-效果) 全部
  ▸ **beat 1** [click] `kicker`: 上方 kicker「最後再補個笑話」fade-in
    · **cue**: "最後再補個笑話——"
    · **wait**: 1s
  ▸ **beat 2** [click] `salary-thief`: 中央上「想必大家未來出職場後都是 · **薪水小偷**」對位 sticker stamp-in（黑底 cream 字、微旋轉 2°、scale 0.85 → 1 overshoot）+ 中央下「**我不一樣 → ?**」空泡泡同時出現（cream 底、6px 黑邊、紅色 ? 字、微旋轉 -3°）
    · **cue**: "想必大家未來出職場後都是薪水小偷..."
    · **wait**: 1.5-2s 給觀眾笑「薪水小偷」+ 看到空泡泡開始猜「他要說什麼」
  ▸ **beat 3** [click] `power-thief-fill`: 「我不一樣 → ?」空泡泡 → 紅 ? 消失 → 整個泡泡 morph 成 FINAL sticker（accent red 底、cream 大字、6px 黑邊、16px hard shadow、微旋轉 -3°、超大）+ **mask-reveal 填入「但我不一樣 · 我是 電費小偷」** + scale 1.5 → 1 snap overshoot bounce + 紅邊 flash 3× + shadow burst 從 8px → 20px + `motif/boom-double-ring` 縮小化雙圈圍繞 stamp（黃外圈 + 紅內圈、stagger 80ms / 120ms）+ 整屏 cream 底 micro-shake 150ms
    · **cue**: "但我不一樣、我是——電費小偷"（演講者念出「電費小偷」當下視覺同步爆、整片節奏 climax）
    · **wait**: 5-7s 觀眾大笑（全片最後一個笑點、絕對不要急著進 beat 4）
  ▸ **beat 4** [click] `footer-and-end`: 底部 footer「我這兩個月 · 一直用班上的電腦 · 瘋狂訓練我的 AI」progressive type-in（字逐字打字效果 1.5s）+ 整屏右下角浮現「— END —」minimal footer（純黑字、cream 底、無 chrome）
    · **cue**: "我這兩個月一直用班上的電腦瘋狂訓練我的 AI"（演講者跟著字打的節奏念）
    · **wait**: 5s+ 讓 END 字留在畫面、給掌聲時間、可永久 hold（不再有下一 step）
  ▸ **climax**: beat 3 電費小偷 stamp 砸下瞬間 + shadow burst + boom 雙圈 + 整屏 shake（全片最強 reveal、首尾呼應 ch 1 step 8 的 BOOM）
  ▸ **氣質**: punchline 爆破、收尾
  ▸ **破梗 fix #10 ★★★**: 原版「薪水小偷 sticker stamp-in (stagger 600ms) → 電費小偷 FINAL sticker 砸下」自動 600ms 串連、觀眾根本來不及笑「薪水小偷」就被「電費小偷」蓋過、整個對比笑點直接死。**現拆 4 beat、且第 3 beat 用「我不一樣 → ?」空泡泡 placeholder 預告「等下要揭曉答案」、讓觀眾在心裡先猜**（這正是脫口秀「setup → 停 → punchline」的標準節奏）。電費小偷 stamp 用 boom 雙圈圍邊、與 ch 1 step 8 BOOM 首尾呼應、整片最後一拍最強 reveal

**口播節選**：

> 「這兩個月、我不只在訓練 AI、AI 也在訓練我⋯⋯大腦可塑性 plasticity⋯⋯我真的是極度的 I 人、明明我很 E⋯⋯祝大家在職場上不被挫敗給擊敗。我是電費小偷、我這兩個月一直用班上的電腦瘋狂訓練我的 AI。」

---

## 素材清單

> **產製策略**：本片所有素材依「**D / E / A 三路線**」分派產製。新增素材必須按決策樹判斷路線、依各路線 SOP 製作。
> **決策依據**：踩過 v1 火柴人 → v2 道具放大 → v3 背面視角三輪 Route E 迭代後總結——「**多角色互動 + 動態姿態 + 表情**」走 Route E 直接翻車、必須走 Route A。
> **本節結構**：路線分類 → 決策樹 → Route E / A SOP → 每章既有素材清單（每條皆標路線）。

### 產製路線分類

| 路線 | 用法 | 適用情境 | 工時/張 |
|---|---|---|---|
| **[D]** 文字隱喻 | HTML + CSS + Neo-brutalism sticker（純文字 + 色塊 + 黑邊 + hard shadow） | 純概念 / 情緒 / 標語 / hero / 角標 / punchline / kicker 字幕 | 2-5 min |
| **[E]** 自製 SVG | Claude 直接生 SVG、可搭 `frontend-design` skill 輔助 | 單一物件 / 對稱結構 / 幾何形狀 / 結構性圖形（曲線、盤面、圓餅、翻牌、階梯） | 10-30 min |
| **[A]** Icon library | phosphoricons.com / lucide.dev 找 icon + Neo-brutalism wrapper | 多角色互動場景 / 人物動作 / 動物 / 設備識別 | 5-15 min |
| **[✓]** 真實素材 | 引用既有檔案 / 截圖 / Pygame visualizer | 程式碼 sticker、tensorboard 真截圖、visualizer iframe | 路徑可指 |
| **[⛔]** 紅線 | 不可挂的素材（偽造截圖、假 logo、假數據顯擺） | 防破口 | — |

**全片預期混合比例**：D ≈ 80% · E ≈ 12% · A ≈ 8% · ✓ 點綴。**ch 2 全章走 A**（三大塊插畫），**ch 5 全章走 D**（情緒崩盤章），其餘章節混用。

### 新增素材決策樹

新素材必須**逐題**順問下來：

1. 是「**文字 / 標語 / sticker / hero / kicker / 字幕**」？ → **[D]**
2. 是「**單一物件 + 對稱 / 幾何**」（飛機、星、圓餅、盤面、曲線、翻牌、階梯、漂浮幾何裝飾）？ → **[E]**
3. 是「**多角色互動 / 人物動作 / 動物 / 設備識別**」（老師教學、訓練狗、神經網路、IP 封鎖、大腦）？ → **[A]**
4. 是「**真實檔案 / 截圖 / 既存 demo**」？ → **[✓]** + 路徑
5. 都不是 → **停下來、跟使用者確認**、不要硬塞

**陷阱題**：

- 「**人 + 道具**」場景 → 看主體：**人**主體 = [A]；**道具**主體（人很小退到副位）= [E]
- 「**多 sticker 並列**」（4 個考題 grid、3 欄對位）→ 純文字色塊組合 = [D]，即使是 4-N 個
- 「**ch 1 漂浮裝飾物**」（黃星 / 紫方塊 / 描邊問號 / 紅圓）→ 單一幾何 = [E]、不是 [D]
- 「**符號 +/+/+ 浮動**」 → 純 CSS 動畫的符號 = [D] 系（不需要 SVG 結構）

### Route E 製作 SOP

每個 [E] 素材依序執行：

1. **避地雷檢查**：場景含「2+ 角色互動 / 動態姿態 / 臉部表情」之一 → **STOP**、降級到 Route A
2. **構圖分區**：viewBox 切 2-3 個敘事區、共用底線、留呼吸空間
3. **道具優於人物**：放大語意承載物（黑板、紙、盤面、翻牌、曲線）、縮小人形或避免人形
4. **silhouette 分化**：若必須有人形、靠 silhouette + 服裝色 + 姿態剪影分化（不靠臉）；優先考慮**背面視角**避開臉
5. **標籤輔助**：補小型黃黑 sticker 標識身分（「老師 / 學生 / SUPERVISED」）—— Neo-brutalism 本來就鼓勵
6. **故事流向**：箭頭 + 浮動 token + 視線虛線、把因果鏈視覺化
7. **嚴守 web_style.md**：cream `#FFFDF5` 底 / 4px 黑邊 / 8-16px hard offset shadow zero blur / 紅 `#FF6B6B` / 黃 `#FFD93D` / 紫 `#C4B5FD` / Space Grotesk 900
8. **迭代上限**：截圖人工驗收最多 **2-3 輪**、超過仍認不出 → 降級到 Route A 或 D

**Route E 提示詞模板**（給 Claude / frontend-design skill）：

> 「產一張 Neo-brutalism 風格 SVG、viewBox 600×360、場景 = `[描述]`。要素 = `[清單]`。每個要素粗略位置 = `[區塊 e.g. 左 1/3、中央、右下角]`。風格 = cream #FFFDF5 底 / 4px 黑邊 / 8-16px hard offset shadow zero blur / 紅 #FF6B6B / 黃 #FFD93D / 紫 #C4B5FD / Space Grotesk 900。驗收 = 一眼看得出 `[關鍵語意]`。」

### Route A 製作 SOP

每個 [A] 素材依序執行：

1. **找 icon**：去 [phosphoricons.com](https://phosphoricons.com/) 或 [lucide.dev](https://lucide.dev/) 搜關鍵字（中英）、複製 SVG（推薦 Phosphor `regular` weight）
2. **覆寫 stroke**：把 `stroke="currentColor"` 改 `stroke="#000"`、`stroke-width="4"`（Phosphor 預設 16px 在 256 viewBox、scale 後正好 ~4px、與 Neo-brutalism 邊框 token 一致）
3. **加色塊背景**：icon 外層包一個 Neo-brutalism card：4px 黑邊 + 8px hard shadow + 主色填底（紅 / 黃 / 紫 / cream）
4. **多 icon 並列**：用「卡片 + 連接箭頭」結構敘事、每張卡內一個 icon + 一個短文字標籤
5. **標籤旋轉**：sticker 標籤微旋轉 ±3°、配 hard shadow
6. **禁忌**：絕不用 Phosphor `bold` 或 `fill` 風格（線太細 / 太實心、跟 Neo-brutalism 不協調）

**常用 icon 對應**（按本片需求）：

| 素材 | Phosphor / Lucide icon |
|---|---|
| 老師教學 | `Chalkboard` / `ChalkboardSimple` + `User` |
| 學生抄筆記 | `GraduationCap` + `Notebook` + `Pencil` |
| 折衣服 | `Shirt` + `StackSimple` |
| 訓練狗握手 | `Dog`（Phosphor）+ `Handshake`（Lucide） |
| 房間 / 門 | `Door` |
| IP 封鎖 | `Prohibit` / `ShieldSlash` |
| 大腦 | `Brain` |
| 神經網路 | `GraphBranching` / `Tree` |

**注意 ch 9 飛機+鳥走 [E] 不走 [A]**：因為要「飛機線稿 + 鳥線稿並列、風格一致」、Phosphor 的 `Airplane` 跟手繪 SVG 線稿混搭會違和、整 step 自製。

### 既有素材清單（每章每條皆標路線）

> 標註：**[D]** 文字 · **[E]** 自製 SVG · **[A]** icon library · **[✓]** 真實素材 · **[⛔]** 紅線

#### 1. coldopen

- **[D]** 「**心 虛**」巨字 sticker（純 CSS）+ 黃色「期中報告」角標
- **[D]** 「**心理學系**」card + 紅箭頭 + 黃底「敬請期待」高亮
- **[D]+[E]** 「**訓 練 AI 解 數 獨**」hero（[D] text-stroke 樣式 + 紅黃 box）+ **[E]** 4 漂浮裝飾物（紫方塊 / 黃星 / 紅圓 / 描邊問號、單一幾何）
- **[E]** 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop、結構性 SVG）+ 多層 depth
- **[D]** 4 張靈感串聯 sticker（正妹 / Code Bullet flappy bird / 沒手機解數獨 / 訓練 AI 解數獨）—— 純文字 sticker
- **[E]+[D]** BOOM 雙圈爆破動畫（[E] 黃外圈 + 紅內圈幾何）+ **[D]** punchline 黃底高亮 · **+climax/A+C (s8 b3)**
- **[D]+[E]** ambient shapes × 5（黃星 / 紫方塊 / 紅圓 / 描邊? / 黃圓、per [§全域 v3 §6](#6-環境裝飾幾何--各章常駐-ambient-shapes)）
- **[D]+[E]** 章節 tint 背景漸層（紫 `rgba(196,181,253,0.08)`、純 CSS）
- **[E]** **全屏 SVG noise grain**（per [§全域 v3 §2](#2-svg-紙紋-noise-grain)、整片全域、僅此處列一次）
- **[E]** **動態 halftone 漂移**（60s linear infinite、per [§全域 v3 §4](#4-動態-halftone-漂移)、全域）
- **[D]+[E]** **Beat indicator** 隱藏式底部 88 方塊條（per [§全域 v3 §5](#5-beat-indicator--隱藏式)、全域）
- **[D]** **View Transitions API** 章節 cross-fade（per [§全域 v3 §3](#3-view-transitions-api--章節-cross-fade)、全域、零依賴）

#### 2. ml-map（整章走 [A]）

- **[A]** **三大塊插畫**（抄筆記 / 折衣服 / 訓練狗握手）—— 從 Phosphor 取 `Chalkboard + User`、`Shirt + StackSimple`、`Dog`，套 Neo-brutalism wrapper（卡片 + 連接箭頭結構）
- **[D]** AlphaGo 標籤 sticker（**文字 sticker、不挂真實 logo 或圍棋盤照片**）
- **[D]** kicker 切換動畫「①/②/③」
- **[D]** cliffhanger 黃底問號 sticker · **+polish/問號 720° 旋轉 (s4)**
- **[D]+[E]** ambient shapes × 4（黑描邊星 / 灰方塊 / 黑pill / 紅圓）
- **[D]+[E]** 章節 tint 背景漸層（黑線 `rgba(0,0,0,0.04)`）

#### 3. llm-vs-rl

- **[D]** split-screen 60/40 對比版型（純 CSS layout）
- **[D]** 中央 VS 大字 sticker + 紅底/黃底 stamp 對比
- **[A]** 房間 / 門 SVG icon —— Phosphor `Door`
- **[E]** 背景文字流動效果（低密度文字 grid 微動、結構性） · **+polish/halftone-burst 微縮 (s3)**
- **[D]+[E]** ambient shapes × 5（紫方塊 / 黃圓 / 紫三角 / 黃方塊45° / 紅描邊?）
- **[D]+[E]** 章節 tint 背景漸層（紫 `rgba(196,181,253,0.06)`）

#### 4. data-hunt

- **[D]** Kaggle 標籤 sticker（**文字 sticker、不挂 Kaggle 真 logo**）+ 多張資料 card 浮現
- **[D]** 「supervised 路線拒絕」紅 stamp（旋轉、stamp-in） · **+polish/ink-splatter 輕量 4 點 (s2)**
- **[D]** websudoku URL sticker「**這個受害者**」（純文字 mono + 紅標籤 + cursor 閃爍） · **+climax/A+C+E (s3 b3)**
- **[D]+[A]** 「20 題就被封 IP」紅警示（[D] 文字 + [A] Phosphor `Prohibit` 封鎖圖示）
- **[E]** **proxy 池視覺化**：30+ IP 小卡 grid 漂浮 + 隨機切換動畫（結構性陣列）
- **[D]+[E]** ambient shapes × 4（黑方塊 / 黃星 / 紅圓 / 黑描邊 pill）
- **[D]+[E]** 章節 tint 背景漸層（黃 `rgba(255,217,61,0.06)`）

#### 5. legacy（整章走 [D]，除程式碼 sticker 走 [✓]）

- **[✓]** **`legacy/app/sudoku/torch_agent.py` 真實檔案 838 行**——直接讀檔做程式碼 sticker、count-up 角標 838
- **[D]** prompt 對話框「**幫我寫一個訓練 AI 解數獨的程式**」sticker
- **[D]** 「**⋯⋯結果我錯了**」獨立崩盤句 sticker · **+climax/A+C (s1 b4)**
- **[E]** 紅色叉叉 burst 動畫（chaotic spawn、幾何粒子）
- **[D]** 第一件學到 hero + 4 個關鍵詞黃底高亮 stagger · **+polish/ink-splatter 4 詞各 1 點微縮 (s4)**
- **[D]+[E]** ambient shapes × 4（紅方塊45° / 紅圓 / 紅描邊方塊 / 紅 pill；章節整體紅意）
- **[D]+[E]** 章節 tint 背景漸層（紅 `rgba(255,107,107,0.07)`）

#### 6. sb3

- **[D]** 「**社群現成 Python 工具箱**」標籤 + 「**填對一格 · 給分**」計分表 hero
- **[D]+[E]** 「剛認識的新女生」sticker（[D] 粉紅 + 微旋轉文字）+ **[E]** 「+/+/+」加分動畫（符號浮動、純 CSS 也可走 [D]）
- **[E]** SVG 曲線爬升（stroke-dasharray draw）→ 卡平段紅 highlight band
- **[D]** 新女生 sticker grayscale 漸變（CSS filter）
- **[D]** **「備胎」FINAL stamp sticker**（紅、超大、微旋轉、16px shadow） · **+climax/A+B+C+E+G ★★★ (s6 b3)**
- **[D]** 「**偷吃步**」紅 stamp + 「**找漏洞作弊**」hero（紅 + 黃雙色強調）
- **[⛔]** **禁挂偽造 tensorboard 截圖**（曲線一律 SVG 概念示意、`prompt.md` §五紅線）
- **[D]+[E]** ambient shapes × 5（粉圓 / 紅圓 / 粉方塊 / 紅 pill / 中左灰圓；灰圓暗示備胎前夕）
- **[D]+[E]** 章節 tint 背景漸層（粉紅 `rgba(255,182,193,0.10)`、本章最強 tint）

#### 7. reasoner

- **[E]** **13 招大階梯**（13 個技巧 sticker 結構性堆疊、X-Wing 跟 XYZ-Wing 最大；技巧名清單從 `reasoner/solver/techniques/` 取真實檔名）+ hover tooltip
- **[D]+[E]** 「舊作法 vs 新作法」split-screen 對比動畫（[D] 文字 sticker + [E] mini 盤面）+ 多招亮 + 分數浮動
- **[E]** 9×9 mini 盤面 + 填數字綠 + 劃掉紅斜線 loop 動畫（純結構性 SVG）
- **[D]** 「**兩千多萬次**」count-up + 「**0**」紅底超大字 hero · **+climax/A+B+C+E (s6 b3「0」)**
- **[D]** **戀愛 hook b 陷阱題 sticker**：「**和你媽掉進水裡你會先救誰**」「**該不該運動**」（含兩答案都錯 ❌ 箭頭）+ hover 互動 · **+climax/A+E+G ×2 (s7 b4/5) + B×2 (s7 b6) ★★★**
- **[D]** 死結 cinematic 黑底 hero + 反向思考 footer 鋪墊
- **[⛔]** **禁挂 `TECH_BONUS` 整張數值表 / `net_arch` / `SubprocVecEnv` 等字串**（假數據顯擺反例，`prompt.md` §五）
- **[D]** ch 7 step 1 「整個計分系統重寫」hero · **+polish/screen-shake ±2px 80ms (s1)**
- **[D]+[E]** ambient shapes × 6（紅方塊 / 紫星 / 黃方塊45° / 黑描邊? / 紫圓 / 紅三角；章節最 dense、配 13 招複雜感）
- **[D]+[E]** 章節 tint 背景漸層（黑 `rgba(0,0,0,0.05)`）

#### 8. apprentice

- **[D]** 「**反向思考**」hero + 紅底高亮
- **[E]** 9×9 數獨盤面（黑邊 + cream 格子 + Space Grotesk 700 數字、90% 已填、3 空 highlight）
- **[E]** 反向課程動畫：3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 空（連續一格一格擦掉 + 計數器 count-up、對齊 script「再加一格、再加一格」口語）
- **[E]** **「+20 → +50」3D flip 翻牌動畫**（紅 → 黃、shadow 加深）
- **[D]+[E]** 「光講不夠看」hero（[D] 文字 + [E] 向下大箭頭 stroke-draw + bounce）
- **[D]** **visualizer 大按鈕**（cream 底 + 粗黑邊 + 強陰影 + accent red 字、微旋轉、hover scale + shadow 加深 mechanical feedback、`href="sudoku-demo:run"`）
- **[✓]** **`apprentice/demo/visualize.py` 桌面 pygame 視窗**——透過 Windows custom URL scheme `sudoku-demo:` 自動啟動，演講者不需 Alt+Tab
- **[✓]** **`demo/visualizer-launch/` 一鍵啟動套件**（install.bat / uninstall.bat / launcher.bat / requirements-demo.txt / README.md）——所有 .bat 自動偵測 `sudoku_old/` 根目錄、portable 到任何 Windows 機器
- **[⛔→挪 ch 9]** **「tensorboard 截圖」已從 ch 8 移除**——挪去 ch 9 step 1 當「AI 在進步」的視覺證據
- **[D]** ch 8 step 1 「反向思考」過渡 · **+polish/章內 1.2s cubic-bezier 底色 fade + halftone 同步漸入**
- **[D]+[E]** ambient shapes × 4（黃星 / 紫方塊 / 金圓 / 黃星；雙黃星呼應「+50」突破）
- **[D]+[E]** 章節 tint 背景漸層（金黃 `rgba(255,217,61,0.10)`、本章最強 tint 之一）

#### 9. callback

- **[D]** cinematic hero「**AI 也在訓練我**」大字 mask reveal + letter-spacing 收緊 + 紅底 flash
- **[✓]** **tensorboard 真實截圖**（success_rate 曲線 + curriculum target_empty 圖）——使用者匯出至 `demo/presentation/public/images/tensorboard/` 並提供路徑、**整片唯一可挂真截圖的地方**
- **[D]+[A]** 「腦科學 RL = AI RL」split + 「**=**」大字 stamp（[D] split layout + [A] Phosphor `Brain` 大腦 icon + `GraphBranching` 神經網路 icon、黃底圓 sticker `=`）
- **[E]** 飛機 + 鳥 並置 sticker（自製黑線稿 + 黃填充、輕微振翅；**因要風格一致、不用 Phosphor**）
- **[D]+[A]+[E]** 戀愛 a 雙欄：[E] 「+/+/+」「-/-/-」浮動符號 + [A] 中央大腦 sticker（Phosphor `Brain`）+ [D] 紅底「跟 AI 一模一樣」hero · **+climax/A+C (s5 b4)**
- **[D]** 戀愛 b 4 個魔王考題 sticker grid（2×2）+ hover 互動（純文字色塊）
- **[D]** plasticity 三欄對位 sticker（AI 解數獨 / 出生講話 / 跟人相處）→ 中央「**一樣**」snap
- **[D]** plasticity 機制 hero「每次都把我們重新塑造一次」+ 三項 stagger
- **[E]+[D]** **MBTI 圓餅視覺**（[E] 0% → 100% I 填滿幾何）+ **[D]** 「極度 I 人」紫色標籤 sticker（script.md L359 verbatim）
- **[D]+[E]** **業務工作 sticker**（[D] 文字）+ **[E]** I → E 漸變條（水平 indicator 動畫）
- **[D]** **警語 sticker「人生第一次的外向 · 換來一輩子的內向」**（cream 底、accent red 大字、6px 紅邊、20px shadow、微旋轉、超大；per ch 9 step 11 設計、**不再用黑底紅字**） · **+climax/A+C+G (s11 b4)**
- **[D]** 「**不被挫敗給擊敗**」職場祝福 hero（紅底高亮）
- **[D]** 「**薪水小偷**」對位 sticker
- **[D]** **「電費小偷」FINAL 超大字 sticker**（accent red 底、6px 黑邊、16px hard shadow、微旋轉、整片最強 reveal、stamp + shadow burst + `motif/boom-double-ring` 圍邊） · **+climax/A+B+C+E+G ★★★ 全片最強 (s13 b3)**
- **[D]** 「— END —」minimal footer
- **[D]+[E]** ambient shapes × 4（紫圓 / 紅星 / 紫描邊方塊 / 灰描邊?；灰描邊?暗示哲思）
- **[D]+[E]** 章節 tint 背景漸層（紫 `rgba(196,181,253,0.07)`）

---

## 實作參考（不在本 outline 範圍、留給後續實作 agent）

> 以下僅供未來 chapter agent / 實作工程師參考、本 outline 不規定具體技術選型。

- **觸發機制**：`mousedown` 監聽（button 0 = 左鍵 next、button 2 = 右鍵 prev）+ `keydown` 監聽（`Space` / `ArrowRight` = next、`ArrowLeft` = prev、`Escape` = toggle progress bar）
- **右鍵實作**：`document.addEventListener('contextmenu', e => e.preventDefault())` 必須在 mount 時設置、unmount 時 remove
- **動畫庫 (v3 鎖定)**：簡單 transition 用純 CSS（最大宗）；React 元件 reveal + climax timeline 統一用 [Motion (Framer Motion)](https://motion.dev/) `useAnimate` sequence——**禁用 GSAP**（v3 spec 明確剔除付費 SplitText、Motion v11 已足夠）；punchline mask-reveal 用 React `text.split('').map(...)` + Motion stagger children
- **字體**：Space Grotesk 700/900（Latin）+ Noto Sans SC 700/900（中文）
- **無障礙**：`prefers-reduced-motion` 媒體查詢內、所有 stamp / overshoot / parallax 動畫切回 instant；hover 互動需有 focus 版本（鍵盤 tab）
- **效能**：所有動畫用 `transform` + `opacity` 屬性（GPU-friendly）；避免 `width/height` 變動觸發 layout；code wall 視窗化（virtual scroll）避免 838 行全 DOM
- **演講者模式**：URL `?presenter=1` 開啟（第二螢幕顯示「下一 step 預覽 + 口播 cue」）、現場用單螢幕模式

---

## 反向索引 · script.md 行號 → outline step

> **用途**：每次改 `script.md` 一段口播時、查本表可立刻知道要動 outline.md 的哪幾個 step。
> **格式**：script.md 行號區間 → 章節 step + 內容摘要。
> **依 script.md 章節分段順序排列**。

| script.md 行號 | 對應 outline step     | 內容摘要                                                      |
| -------------- | --------------------- | ------------------------------------------------------------- |
| L1             | ch 1 step 1           | 心虛開場、報告太不正經、請各位同學和老師多包涵                |
| L5             | ch 1 step 2           | 心理學系畢業 + 敬請期待伏筆                                   |
| L9             | ch 1 step 3           | 期中主題：訓練 AI 解數獨                                      |
| L13-L17        | ch 1 step 4           | 捷運上正大光明看著正妹發呆                                    |
| L19            | ch 1 step 5           | 腦袋冒出 Code Bullet flappy bird                              |
| L21            | ch 1 step 6           | 繼續發呆看著正妹（喜劇延續拍）                                |
| L25            | ch 1 step 7           | 當兵沒手機解數獨                                              |
| L29            | ch 1 step 8 beat 1-2  | Boom · 兩個想法撞在一起：訓練 AI 解數獨（拆 beat、fix #1）   |
| L35-L37        | ch 1 step 8 beat 3    | 靈感就是這麼莫名其妙地蹦出來（placeholder 模式）· +climax/A+C |
| L41-L45        | ch 2 lead-in          | 機器學習的世界長什麼樣                                        |
| L49-L55        | ch 2 step 1           | supervised：看著答案抄筆記                                    |
| L57-L61        | ch 2 step 2           | unsupervised：折衣服分顏色                                    |
| L63-L67        | ch 2 step 3           | RL：試錯加獎懲、AlphaGo                                       |
| L71            | ch 2 step 4           | cliffhanger：那 ChatGPT 跟 Claude 又是哪一招？ · +polish/問號旋轉 |
| L75-L77        | ch 3 step 1           | LLM = supervised + RLHF                                       |
| L81-L89        | ch 3 step 2           | LLM 模仿 vs 我的 AI 自己摸出規則                              |
| L93-L95        | ch 3 step 3           | OK 純 RL、第一步找資料 · +polish/halftone-burst 微縮 |
| L99-L107       | ch 4 step 1+2         | Kaggle / supervised 路線拒絕 · +polish/ink-splatter 輕量 (s2) |
| L111-L121      | ch 4 step 3 (4 beat)  | 霸榜目標 + websudoku 受害者（拆 beat、fix #2）· +climax/A+C+E |
| L125-L133      | ch 4 step 4           | 20 題被封 IP + proxy 池                                       |
| L141-L147      | ch 5 step 1 (4 beat)  | 我那時候很天真 / 丟一句 prompt / 我錯了（拆 beat、fix #3、motif/crash-line 首發）· +climax/A+C |
| L151           | ch 5 step 2           | 800 多行的單一檔案                                            |
| L153           | ch 5 step 3           | 每改一個地方都東倒西歪 / debug 成本爆炸                       |
| L157-L163      | ch 5 step 4           | 第一件學到 / 架構自己先想清楚 / 套皮仔 · +polish/ink-splatter 4 詞微縮 |
| L167-L173      | ch 6 step 1 (3 beat) + step 2 | 社群工具箱 / 套皮仔 / 我又錯了（step 1 拆 beat、fix #4、motif/crash-line 復用）· +climax/A+C (s1) |
| L177           | ch 6 step 2           | 填對一格就給分數                                              |
| L181-L185      | ch 6 step 3           | 新女生加分（戀愛 hook a 出場）                                |
| L187           | ch 6 step 4+5         | 卡平段 / 不思進取                                             |
| L189           | ch 6 step 6 (3 beat) ★★★ | 備胎（戀愛 hook a 收、拆 beat、fix #5、全 ch 6 最重笑點）· +climax/A+B+C+E+G ★★★ |
| L195-L199      | ch 6 step 7           | 偷吃步 / 計分標準寫錯 / 找漏洞作弊                            |
| L201-L205      | ch 7 step 1+2         | 整個計分系統重寫 / 用人類技巧反過來驗證 · +polish/screen-shake 輕量 (s1) |
| L209-L211      | ch 7 step 3           | 13 招技巧名（naked / hidden / X-Wing / Swordfish / XY-Wing）  |
| L215-L225      | ch 7 step 4           | 舊（填對一格給分）vs 新（用哪一招解釋）對比                   |
| L229-L233      | ch 7 step 5           | Action 擴增：填數字 + 劃掉候選                                |
| L237           | ch 7 step 6 (3 beat)  | 兩千多萬次 · 完整解出機率 0（拆 beat、fix #7）· +climax/A+B+C+E |
| L241-L257      | ch 7 step 7 (6 beat) ★★★ | 老油條陷阱題（戀愛 hook b 展開、拆 beat、fix #6、motif/girl-veteran 首發、ch 7 最大笑點群）· +climax/A+E+G (beat 4/5) + B×2 (beat 6) ★★★ |
| L265-L269      | ch 7 step 8           | 死結：永遠拿不到「整題解完」大獎                              |
| L273-L275      | ch 8 step 1           | 反向思考 · +polish/章內 1.2s 色票 cubic-bezier fade |
| L277-L279      | ch 8 step 2           | 一開始只給 3 格空                                             |
| L281-L285      | ch 8 step 3           | 再加一格、再加一格⋯⋯3→4→5→6→7→8→9→10                 |
| L287-L291      | ch 8 step 4           | 破關獎勵 +20 → +50                                           |
| L293           | ch 8 lead-out         | 3 → 10、他終於開始解出整題                                   |
| L297-L299      | ch 8 step 5+6         | 光講不夠看 / 給大家看 AI 即時解數獨 + visualizer 按鈕         |
| L303-L307      | ch 9 step 1           | AI 還在訓練中 / 磨合期 / 最後一件事（tensorboard 截圖此處挂） |
| L309           | ch 9 step 2           | 核心金句：這兩個月、我不只在訓練 AI、AI 也在訓練我            |
| L313-L317      | ch 9 step 3           | 腦科學 RL = AI RL、其實是同一件事                             |
| L319           | ch 9 step 4           | 飛機 / 鳥：AI 在模仿人類                                      |
| L323-L329      | ch 9 step 5 (4 beat)  | 戀愛 a callback：回訊息加分 / 已讀扣分（拆 beat、fix #8、motif/girl-new 復用）· +climax/A+C |
| L333-L343      | ch 9 step 6           | 戀愛 b callback：4 個魔王考題（motif/girl-veteran 復用）      |
| L347-L349      | ch 9 step 7           | 大腦可塑性 plasticity 引出                                    |
| L351           | ch 9 step 8           | plasticity 三欄對等（motif/13-stairs 背景復用）              |
| L353-L355      | ch 9 step 9           | plasticity 機制：每次都把我們重新塑造一次（motif/flip-20-to-50 背景復用） |
| L359-L361      | ch 9 step 10 第一拍   | 極度 I 人 + MBTI 100% I 圓餅                                  |
| L363-L365      | ch 9 step 10 第二拍   | 業務工作變 E + I→E 漸變條                                    |
| L367-L369      | ch 9 step 11 (4 beat) | 人生第一次的外向 · 換來一輩子的內向（拆 beat、fix #9、motif/crash-line 放大）· +climax/A+C+G |
| L371-L373      | ch 9 step 12          | 職場祝福：不被挫敗給擊敗                                      |
| L375           | ch 9 step 13 (4 beat) ★★★ | 電費小偷 final（拆 beat、fix #10、motif/boom-double-ring 首尾呼應 ch 1 step 8）· +climax/A+B+C+E+G ★★★ 全片最強 |

**注意事項**：

- 同一行可能對應到多個 step（例如 L201 = ch 6 step 7 提示 + ch 7 step 1 主 hero）
- 同一個 step 可能對應多行 script（例如 ch 9 step 10 合併 L359-365）
- 演講者改 script 一段時、本表配合 outline 章節「**口播對應**」欄位（部分 step 已標）反查
- **標 `★★★` 的三個 step**（ch 6 s6 備胎、ch 7 s7 老油條、ch 9 s13 電費小偷）是全片三大笑點 climax、beat 節奏控制必須完美、`?presenter=1` 模式重點檢視
- **標「拆 N beat」**的 step 表示已套用 [Sub-step Beat 機制](#sub-step-beat-機制子點擊推進) + [Punchline Placeholder 模式](#punchline-placeholder-模式破梗預防)，每個 beat 都有對應的 `cue` / `wait` 註記
