# 視覺系統主檔（DNA · Motif · Climax · 全域 polish）

> **配對檔**: [outline.md](outline.md)（敘事 + beat + speaker cue）· [asset-production.md](asset-production.md)（素材生產路線）
> **詳細 spec**: [docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md](../docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md)
> **Neo-brutalism 設計系統**: [web_style.md](web_style.md)（完整規範、本檔 §12 摘要 mirror）
> **技術堆疊**: `Vite + React + Tailwind v4 + Motion (Framer Motion) + lucide-react`（全免費、零年費、static folder 部署到 `demo/presentation/dist/`）
> **明確剔除（技術）**: GSAP、Howler.js、SplitType（用 React 字串 split 替代）、TypeScript（可選）、Three.js / Lottie / Rive / Slidev / Reveal.js / Lenis / Theatre.js
> **明確剔除（設計）**: custom cursor、cinematic letterbox bars、聲音設計、Tier C 破格方案

---

## §1 Visual DNA（Neo-brutalism · 每步都遵守）

- **Cream `#FFFDF5` 為主畫布**、halftone dots / 細格線紋理當底
- **純黑 4-6px border + 8-16px hard offset shadow（zero blur）**——所有 card / sticker / hero 元素的識別物件
- **Space Grotesk 700/900** 為唯一拉丁字體（中文回退 Noto Sans SC 700/900）
- **微旋轉 sticker** -3°~4° 破直角
- **禁圓角中段** (`rounded-md`)——要嘛 0 (鋭角) 要嘛 50%（pill）
- **動態效果禁忌**: 禁紫粉漸變 / 軟陰影 / blur > 4px / ease-in-out 慢動畫
- **動態效果保留**: 強 hard-edge translate / scale snap / SVG stroke-dasharray draw / 大字 mask reveal / 多層 depth fade

---

## §1.5 Typography / Spacing / z-index Tokens

### Typography Scale（rem-based、desktop ≥1280px 基準）

| token | 字級 | Tailwind class | 字重 | 用途 |
| --- | --- | --- | --- | --- |
| `hero-mega` | 8rem (128px) | `text-9xl` | 900 | 全屏單句金句（ch9 s2「AI 也在訓練我」） |
| `hero` | 6rem (96px) | `text-8xl` | 900 | 章內主標題、BOOM card、punchline FINAL stamp |
| `h1` | 3.75rem (60px) | `text-6xl` | 900 | step 主視覺文字（supervised / LLM / VS） |
| `h2` | 3rem (48px) | `text-5xl` | 900 | 副標題、警語「換來一輩子的內向」 |
| `h3` | 2.25rem (36px) | `text-4xl` | 700 | 章內次標題 |
| `body-lg` | 1.875rem (30px) | `text-3xl` | 700 | step 副標（粗體）、kicker 突出版 |
| `body` | 1.5rem (24px) | `text-2xl` | 700 | 副標、內文 |
| `kicker` | 1.25rem (20px) | `text-xl` | 700 | 上方小標籤、章節編號 |
| `label` | 1rem (16px) | `text-base` | 700 | sticker 內文字、按鈕 |
| `caption` | 0.75rem (12px) | `text-xs` | 700 | 角標、進度條、beat indicator 文字 |

**特殊處理**:
- punchline 關鍵字一律包 `motif/yellow-highlight` 黃底 box（無論字級）
- 「電費小偷」FINAL stamp 用 `hero` (6rem) + scale 1.5 → 1 snap overshoot、視覺等同 `hero-mega`
- text-stroke 描邊（`-webkit-text-stroke: 2px black; color: transparent`）僅用於章主題揭曉的 hero 字

### Spacing Scale（8px base grid）

`4px · 8px · 12px · 16px · 24px · 32px · 48px · 64px · 96px · 128px`

| token | px | 用途 |
| --- | --- | --- |
| `space-1` | 4px | sticker 內極小間距、border 與 shadow 偏移基底 |
| `space-2` | 8px | sticker 內 padding、small shadow 偏移 |
| `space-3` | 12px | card 內 padding、medium shadow 偏移 |
| `space-4` | 16px | 元素間 gap、large shadow 偏移 |
| `space-6` | 24px | sticker 間 gap、massive shadow 偏移 |
| `space-8` | 32px | card 間 gap、section 內小段落分隔 |
| `space-12` | 48px | hero 與副標間距 |
| `space-16` | 64px | step 內主元素 + 副元素分隔 |
| `space-24` | 96px | section 上下 padding |

### z-index 層級表

| z | 用途 |
| --- | --- |
| `0` | ambient shapes（per §9.6） |
| `1` | global noise grain（per §9.2） |
| `5` | halftone dots 背景 |
| `10` | 章節背景、tint 漸層 |
| `20` | hero card、主元素 |
| `30` | sticker、文字、副標 |
| `40` | climax overlay：halftone-burst、ink-splatter（per §8） |
| `50` | spotlight-vignette（`mix-blend-mode: multiply`、per §8） |
| `60` | boom-double-ring、FINAL stamp、★★★ climax 主體 |
| `90` | progress bar、章節 nav |
| `100` | speaker mode（`?presenter=1`）overlay |

---

## §2 每步節奏 4 拍

每個 step 觸發左鍵後依序執行：

1. **進場 enter (0-400ms)**: 左鍵觸發 → 主元素從 mask / blur / scale 0.85 / translateY 進入；底色或裝飾物 stagger 進入（每物件 50-100ms 偏移）
2. **停頓 hold (400ms-結束)**: 主元素就定位、留給觀眾 + 演講者口播時間；可有「持續微動」（如 sticker 輕微浮動、icon 慢轉），但**不**搶焦點
3. **重點 climax**（步內顯眼瞬間、可能在 enter 後 1-3s 觸發）: 數字翻牌 / sticker 砸下 / 大字 mask 完成 / 互動 hover 高亮
4. **退場 exit**: 演講者左鍵 → 主元素 fade-out + scale 0.95 + 底色微暗（200ms），下一 step 進場無縫接

---

## §3 互動類型字典

每 step 標一個主類型 + 視需要混合：

| 類型 | 用途 | within-step 實作 |
| --------------- | -------------------------------------- | ------------------------------------------------------ |
| `cinematic` | 氛圍 hero / 全螢幕單一強訊息 | full-bleed、blur clear、慢動 mask reveal、留白 |
| `depth` | 多層深度場景（取代 parallax 的靜態版） | 多 layer translateY + opacity 模擬遠近、無 scroll 依賴 |
| `progressive` | 漸進揭示資訊 | 元素 stagger 進入（左鍵觸發 enter 後 50-150ms 一個） |
| `interactive` | 步內 hover / sub-click | hover 高亮 / 子卡放大 / 隨機切換、不影響推進 |
| `comparison` | 二元對比 | split-screen / 左右雙欄、可加 hover 雙向加重 |
| `data-viz` | 數字 / 曲線 / 翻牌 | SVG stroke-dasharray draw、3D flip、CSS count-up |

---

## §4 響應式策略

- **Desktop (≥1280px)**: 完整 depth 層、完整 hover 互動、字級照 §1.5 Typography Scale 規範
- **Tablet (≥768px)**: depth 簡化為 2 層、touch tap 替代 hover (hover 行為改成 tap 觸發)、字級降一級（hero-mega 8rem → 6rem、hero 6rem → 4.5rem）
- **mobile (<768px)**: **不在範圍**（演講場合只在桌面/平板播放）

---

## §5 全域 UI 規範

- **進度條**: 默認 `opacity: 0`、滑鼠近底部邊緣 32px 內 → 0.6s 淡入到 0.8、移開 1s 後淡出
- **章節 nav**: 默認隱藏、滑鼠近右上角 32px 內 → 浮現可跳章
- **無 header / footer / 品牌條 / 頁碼角標**（per skill 「舞台無 chrome」原則）

### §5.6 Speaker Mode（`?presenter=1`）

第二螢幕專用、給演講者看的 layout（觀眾螢幕仍走正常模式）。URL `?presenter=1` 開啟。

**Layout（第二螢幕、預設 1920×1080）**:

```
┌─────────────────────────────────────────────────────────────┐
│ 總計: 02:34 / 12:30   章: 01:12 / 01:42   下一 climax: 00:18 │ ← 計時器列
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  目前: ch 6 / 9 · step 6 · beat 2 / 3  ★★★                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [當前 beat 縮圖預覽 · 60% 螢幕寬]                      │   │
│  │ 中央紅底空白 sticker 已就位                            │   │
│  │ 副標「看似有進展 · 結果什麼都沒發生」已出              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ▣ Cue (該說):                                              │
│  「換句話說、這個女生只把你當——」                          │
│  （拉長尾音「當——」、給空 sticker 出現的反應時間）         │
│                                                             │
│  ▣ Wait: 1-2s 留懸念（演講者不要急著點下一 beat）            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  下一 beat: beat 3 [click] bei-tai-fill                     │
│  下一 cue: 「備胎」（念出當下視覺同步爆）                    │
│  下一 wait: 3-4s 笑聲                                       │
└─────────────────────────────────────────────────────────────┘
```

**單螢幕 fallback（無第二螢幕時）**:
- 按 `Q` toggle cue overlay（半透明右下角、不擋觀眾視線）
- 按 `Tab` 一直按住顯示完整 cue + wait
- 按 `Esc` 顯示進度條 + 章節 nav

**Dry-run / 練習模式**: URL `?presenter=1&practice=1`
- 自動推進每 beat（依各 beat 的 wait 預設值計時）
- 無需點擊、可全程練口播節奏
- 右上角顯示「PRACTICE MODE · 自動推進中」紅色標籤

**緊急 fallback**: 按 `Ctrl+Shift+→` 強制跳到下一章 step 1（visualizer 啟動失敗 / 演講者迷路時用）。

**計時器規格**:
- 總計: 演講開始到現在 / 預估總長 12:30
- 章內: 進入當前章節到現在 / 該章預估長度
- 下一 climax: 倒數到下一個 ★★ / ★★★ punchline 的時間

---

## §6 章節色票統一表

每章鎖定主情緒色調、強化敘事弧。觀眾翻章時無意識感受到色調轉變。

| ch | 情緒 | 主色 | 副色 | climax 氛圍色 | tint (對角漸層) | 視覺密度 | Ambient shapes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 coldopen | 探索/好奇/白日夢 | cream + 紫 | 黃 | 紅 (BOOM) | `rgba(196,181,253,0.08)` | 中 | TL 黃星+15° / TR 紫方塊-8° / BL 紅圓 0° / BR 描邊?+12° / 中右 黃圓-3° |
| 2 ml-map | 教學/理性 | cream + 黑 | 灰線 | 紅 (AlphaGo) | `rgba(0,0,0,0.04)` | 低 | TL 黑描邊星-10° / TR 灰方塊+5° / BL 黑 pill 0° / BR 紅圓-8° |
| 3 llm-vs-rl | 對比/分歧 | cream | 紫 (LLM) + 黃 (我的 AI) | 紅 (VS) | `rgba(196,181,253,0.06)` | 中 | TL 紫方塊-5° / TR 黃圓+10° / BL 紫三角+3° / BR 黃方塊45°-7° / 中下 紅描邊?+8° |
| 4 data-hunt | 戰鬥/受害 | cream + 黑 mono | 黃 (Kaggle) | 紅 (受害者 + 封 IP) | `rgba(255,217,61,0.06)` | 中 | TL 黑方塊+5° / TR 黃星-10° / BL 紅圓+12° / BR 黑描邊 pill-3° |
| 5 legacy | 崩盤 #1 | cream + 紅邊 | 紅叉叉 | 紅 flash | `rgba(255,107,107,0.07)` | 中 | TL 紅方塊45°+15° / TR 紅圓-5° / BL 紅描邊方塊+8° / BR 紅 pill-3° |
| 6 sb3 | 戀愛錯覺 → 崩盤 #2 | 粉紅（新女生） | 紅 | 灰（備胎前夕）→ 紅 stamp | `rgba(255,182,193,0.10)` | 中 | TL 粉圓+10° / TR 紅圓-6° / BL 粉方塊+3° / BR 紅 pill-10° / 中左 灰圓+5° |
| 7 reasoner | 嚴肅/死結 | cream + 黑 | 多色 sticker | 紅底 + 黃「0」 | `rgba(0,0,0,0.05)` | **高** | TL 紅方塊-8° / TR 紫星+12° / BL 黃方塊45°+5° / BR 黑描邊?-10° / 中右 紫圓+3° / 中左 紅三角-5° |
| 8 apprentice | 突破/光明 | cream + 金黃 | 紫（盤面） | 黃 (+50 翻牌) | `rgba(255,217,61,0.10)` | 中 | TL 黃星+10° / TR 紫方塊-8° / BL 金圓+3° / BR 黃星-12° |
| 9 callback | 收斂/哲思/收尾 | cream（純） | 紫 (plasticity) | 紅（電費小偷 final） | `rgba(196,181,253,0.07)` | **高** | TL 紫圓+5° / TR 紅星-10° / BL 紫描邊方塊+8° / BR 灰描邊?-3° |

**視覺密度規則**:
- 低 = 4 個 ambient shapes、字級偏大（hero）、留白多
- 中 = 5 個 ambient shapes、混合字級
- 高 = 6 個 ambient shapes、字級偏小（h1/h2）、密集 sticker

**「climax 氛圍色」vs 「climax FX」區分**: 本欄為章節情緒色（紅 / 黃 / 灰），是視覺**氛圍**；§8 Climax FX A-G 是動畫**效果**、兩者非同一概念。

---

## §7 Motif Library（13 motif）

定義整片可復用的視覺母題。**callback 章 (ch 9)** 必須大量引用 → callback 笑點力道 +30%。

| Motif ID | 首發 | 視覺定義 | 復用點 |
| --- | --- | --- | --- |
| `motif/boom-double-ring` | ch 1 s8 | 黃外圈 + 紅內圈、border 8px、stagger stamp、shadow burst | ch 9 s13 電費小偷 stamp 圍邊（縮小、首尾呼應）|
| `motif/crash-line` | ch 5 s1 | cream 大字 + 6px 紅邊 + 紅 flash + 閃爍游標 `_` placeholder | ch 6 s1（rhyme）· ch 9 s11 警語（放大）|
| `motif/red-stamp` | ch 4 s2 | 紅 stamp 從天砸下、overshoot bounce、shadow burst | ch 6 s6 備胎 · ch 7 s6「0」|
| `motif/yellow-highlight` | ch 1 s8 | 黃底 box 高亮關鍵詞 | 全片所有 punchline 關鍵字共用 |
| `motif/girl-new` | ch 6 s3 | 粉紅底 sticker + 微旋轉 + 「+/+/+」浮動 | ch 9 s5 戀愛 a callback（退背景、灰階）|
| `motif/girl-veteran` | ch 7 s7 | 老油條陷阱題 sticker（紅底＋紫底）+ ❌ 答案箭頭 | ch 9 s6 戀愛 b 4 題（同款 sticker 樣式）|
| `motif/13-stairs` | ch 7 s3 | 13 招技巧階梯、X-Wing / XYZ-Wing 最大 | ch 9 s8 plasticity 三欄背景縮小裝飾（opacity 0.08 灰階）|
| `motif/flip-20-to-50` | ch 8 s4 | +20 → +50 3D flip 翻牌、紅 → 黃 | ch 9 s9 plasticity「reward 加加減減」背景 loop（opacity 0.06 灰階）|
| `motif/sudoku-board` | ch 8 s2 | 9×9 cream 盤面、黑邊、Space Grotesk 700 數字 | ch 8 s3 反向課程 · ch 7 s5 mini 盤面 |
| `motif/spotlight-vignette` | ch 6 s6 | 全屏 radial gradient overlay、transparent (中央 25%) → rgba(0,0,0,0.6)、`mix-blend-mode: multiply`、500ms 淡入、stamp 自身保亮 | ch 7 s7 b4/5 · ch 9 s11 b4 · ch 9 s13 b3 |
| `motif/halftone-burst` | ch 6 s6 | 從 stamp 中心放射 3 圈 dots、scale 0→3 opacity 1→0、500ms、`mask: radial-gradient` 控形、與 boom-double-ring 語彙互補 | ch 7 s6 b3 · ch 7 s7 b6（雙 burst）· ch 9 s13 b3 · ch 3 s3 微縮版 |
| `motif/ink-splatter` | ch 4 s3 b3 | SVG 8 個不規則黑墨 path、stagger 80ms scale 0→1 overshoot、半徑 80-180px 隨機（輕量版 4 點、半徑 40-80px）| ch 4 s2 輕量 · ch 5 s4 微縮 · ch 6 s6 b3 · ch 7 s6 b3 · ch 7 s7 b4/5 · ch 9 s13 b3 |
| `motif/screen-shake` | ch 6 s6 b3 | `<main>` 容器 `translate(±5px,±3px)` 隨機 3 次共 150ms（輕量版 ±2px、1 次、80ms）| ch 7 s1 輕量 · ch 7 s7 b4/5 · ch 9 s5 b4 · ch 9 s11 b4 · ch 9 s13 b3 |

**新增 motif 規範**: 任何單一視覺元素若打算復用於 ≥ 2 step、必須登錄到本表並指派 `motif/xxx` ID。`outline.md` 引用以 `Motif: motif/xxx`（首發/復用）標註。

---

## §8 Climax FX Library

### §8.1 Climax FX 代號（5 效果）

| 代號 | 名稱 | 觸發時機 | 規格 |
| --- | --- | --- | --- |
| **A** | Screen shake 微震 | stamp 砸下瞬間 | 150ms 內 `<main>` `translate(±5px,±3px)` 隨機 3 次（每次 50ms） |
| **B** | Halftone 同心圓爆破 | A 同步 | 從 stamp 中心向外 3 圈 dots、500ms scale 0→3、opacity 1→0、`mask: radial-gradient` 控形 |
| **C** | Slow-mo overshoot 4 拍 | stamp 進場 | scale 0→1.4(160ms)→1.0(200ms)→0.95(120ms)→1.0(120ms)、bezier `(0.34, 1.56, 0.64, 1)` |
| **E** | 黑墨噴濺 splatter | A/B 同步 | 周圍 8 個不規則黑墨 SVG inline path、stagger 80ms、scale 0→1 overshoot、半徑 80-180px 隨機 |
| **G** | Spotlight 聚焦暗化 | punchline 揭曉 → climax 全程 hold | 全屏 `radial-gradient(circle at <stamp-center>, transparent 25%, rgba(0,0,0,0.6) 100%)`、`mix-blend-mode: multiply`、500ms 淡入、stamp 自身保亮 |

**Motion `useAnimate` 範例**（給實作 agent 參考、非規範）:

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

### §8.2 三大 ★★★ Climax 全套（A+B+C+E+G）

僅套用於：**ch6 s6 備胎** · **ch7 s7 老油條** · **ch9 s13 電費小偷**。

### §8.3 10 個 punchline 套用一覽

| step | beat | id | 火力 | 等級 | motif |
| --- | --- | --- | --- | --- | --- |
| ch1 s8 | b3 | punchline-reveal | A+C | 輕量 | motif/boom-double-ring（首發）· motif/yellow-highlight |
| ch4 s3 | b3 | victim-stamp | A+C+E（stamp 性質）| 輕量+ | motif/red-stamp |
| ch5 s1 | b4 | crash-fill | A+C 跟紅邊 flash 2× 疊加 | 輕量 | motif/crash-line（首發）|
| ch6 s1 | b3 | crash-fill | A+C（同 ch5 s1 motif rhyme 一致性）| 輕量 | motif/crash-line（復用）|
| ch6 s6 ★★★ | b3 | bei-tai-fill | A+B+C+E+G | 全套（全片 #1 重要）| motif/red-stamp |
| ch7 s6 | b3 | zero-drop | A+B+C+E（「0」實體 stamp 性質）| 輕量+ | motif/red-stamp |
| ch7 s7 ★★★ | b4 / b5 | answer-a/b-fill | 各 A+E+G | 全套（分 beat 套）| motif/girl-veteran（首發）· motif/yellow-highlight |
| ch7 s7 ★★★ | b6 | both-flash | 雙 B（halftone-burst × 2 從兩 ❌ 同時放）| 全套（分 beat 套）| 同上 |
| ch9 s5 | b4 | punchline-hero | A+C | 輕量 | motif/girl-new（callback、灰階退背景）|
| ch9 s11 ★★ | b4 | warn-line-b-fill | A+C+G（警語性質聚焦合理）| 輕量+ | motif/crash-line（放大）|
| ch9 s13 ★★★ | b3 | power-thief-fill | A+B+C+E+G + 縮小化雙圈圍邊 + 整屏 cream micro-shake 150ms（全片最強）| 全套+ | motif/boom-double-ring（首尾呼應 ch1 s8）· motif/red-stamp · motif/yellow-highlight |

### §8.4 polish 級套用（非 punchline 但有特殊 FX 加成）

| step | id | 套用 motif / FX |
| --- | --- | --- |
| ch2 s4 | cliffhanger-qmark | 問號 720° 完整旋轉 + motif/yellow-highlight |
| ch3 s3 | ok-decided | motif/halftone-burst 微縮版（半徑 60px） |
| ch4 s2 | reject-stamp | motif/ink-splatter 輕量版（4 點、半徑 40-80px） |
| ch5 s4 | learning-points | motif/ink-splatter 微縮（4 關鍵詞各 1 個小黑點、半徑 20-40px） |
| ch7 s1 | rewrite-declare | motif/screen-shake 輕量版（±2px、1 次、80ms） |
| ch8 s1 | reverse-thinking | 章內 1.2s cubic-bezier 底色 fade + halftone opacity 0→1 漸入 |

---

## §9 全域 v3 polish（cinematic 加料）

> **基石**: 本 section 對齊 [docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md](../docs/superpowers/specs/2026-05-17-demo-visual-tier-b-upgrade-design.md)
> **不破壞既有設計**: 本 section 純粹「在 cream 紙感上多加一層 cinematic 氛圍 + climax 衝擊」、Neo-brutalism DNA 100% 保留

### §9.1 章節色票背景漸層

每章 cream 底（`#FFFDF5`）外加一層該章副色的對角漸層：

```css
main { background: linear-gradient(135deg, #FFFDF5 0%, var(--chapter-tint) 100%); }
```

`--chapter-tint` 值見 [§6 章節色票統一表](#6-章節色票統一表)。

**章節切換**: tint 過渡走 [§9.3 View Transitions API](#93-view-transitions-api--章節-cross-fade) 500ms cross-fade。

### §9.2 SVG 紙紋 noise grain（全域）

全屏覆蓋層、`pointer-events: none`、`z-index: 1`（在背景漸層上、所有 sticker 下）：

```css
.global-grain {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.15 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  mix-blend-mode: multiply;
  opacity: 0.5;
}
```

**上限**: opacity ≤ 0.6（再高搶 sticker 焦點）、baseFrequency ≥ 0.7（再低看到大斑塊、破紙感）。

### §9.3 View Transitions API · 章節 cross-fade

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

**Fallback**: Safari < 18 / Firefox 全版本 → 純 React state 切換、無動畫但功能不損。
**相容**: 仍保留既有 [§10 章節間 Transition fade-bridge](#10-章節間-transition-fade-bridge)（0.8-1.2s）、兩者疊加不衝突。

### §9.4 動態 halftone 漂移

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

**規範**: 60s 完成 cycle、`linear` easing（ease-in-out 會被察覺）、垂直向上、`prefers-reduced-motion: reduce` 必須關閉。

### §9.5 Beat indicator · 隱藏式

底部固定 1.5% 高度區塊、平時 `opacity: 0`、滑鼠進入 bottom 32px 內 0.6s 淡入到 0.7、移開 1s 淡出。

**佈局**: 88 個小方塊水平排列（對應全片 88 beat、跨章不分隔）、每個 ~10×4px:

- 已過 beat: `#000` 黑色實心
- 當前 beat: `#FF6B6B` 紅色實心 + scale 1.1
- 未到 beat: 透明 + 1.5px 黑邊輪廓
- 章節邊界（9 章 → 8 個邊界）: 方塊間 4px 黃色 `#FFD93D` 隔條

**右上角同步文字**: `step M / 57 · beat N / X · ch K`（11px、`color: #666`、Space Grotesk 700）

**作用**: 演講者下意識掌握剩餘節奏、觀眾 hover 看到「快結束了」收尾期待感。

### §9.6 環境裝飾幾何 · 各章常駐 (ambient shapes)

每章 4-6 個微旋轉幾何 sticker 常駐邊角、CSS 緩慢浮動、`z-index: 0`（在所有 sticker 下、grain 上）。

- **形狀限定**: `star` / `square` / `circle` / `triangle` / `outline-question` / `pill` 六種
- **配色取**: 章節副色 + climax 色（避主色避免搶焦點）
- **微旋轉**: ±3°-8°
- **浮動**: `translateY(±8px) translateX(±4px)` 4-8s `ease-in-out infinite`、每個 sticker 起始 phase 隨機 offset
- **位置**: 4 角為主、可有 1-2 個浮在中段邊緣（離主元素 30%+）
- **上限**: 6 個/章（超過會與 sticker 搶焦點）

各章配置見 [§6 章節色票統一表](#6-章節色票統一表)。

### §9.7 prefers-reduced-motion 規範

所有動態效果在 `prefers-reduced-motion: reduce` 環境必須降級：

- §9.4 動態 halftone 漂移 → 關閉動畫、保持靜態
- §8.1 climax A screen shake → 改純 scale punch（不晃畫面）
- §8.1 climax B halftone burst → 縮短至 200ms、不放射
- §8.1 climax C slow-mo overshoot → 縮短至 200ms、直接 scale 0→1
- §8.1 climax E splatter → 同時出現、不 stagger
- §8.1 climax G spotlight → 改 200ms instant 暗化

---

## §10 章節間 Transition fade-bridge

每章末強制插入一個 0.8-1.2s 的 **fade-bridge auto-transition**（不算進 step 計數、不需點擊、自動播放）：

1. 上一章主色 fade-out（300ms）
2. cream 純畫面 hold（200-400ms）
3. 下一章主色用 halftone dots 微染滲入（500ms）
4. 下一章 step 1 enter 動畫接上

**例外**: ch 1 → ch 2（白日夢→理性）· ch 4 → ch 5（戰鬥→崩盤）· ch 8 → ch 9（突破→收尾）三個情緒大轉折拉長到 1.5s。

---

## §11 Coverage Matrix（cross-file 一致性追蹤）

> **用途**: 修改三檔任一處時、查本表確認其他兩處是否同步。
> **異動規則**: 改 motif 時、outline.md / visual.md §7 / asset-production.md §5 三處需同步。

### §11.1 Motif coverage

| Motif ID | outline.md 引用 | visual.md §7 | asset-production.md §5 |
| --- | --- | --- | --- |
| boom-double-ring | ch1 s8（首發）· ch9 s13（縮小化、首尾呼應） | ✓ | ch1 · ch9 |
| crash-line | ch5 s1（首發）· ch6 s1（rhyme）· ch9 s11（放大警語） | ✓ | ch5 · ch6 · ch9 |
| red-stamp | ch4 s2（首發）· ch4 s3 · ch6 s6 · ch7 s6 · ch9 s13 | ✓ | ch4 · ch6 · ch7 · ch9 |
| yellow-highlight | ch1 s8（首發）· 全片 punchline 共用 | ✓ | 全章 |
| girl-new | ch6 s3（首發）· ch9 s5（灰階退背景） | ✓ | ch6 · ch9 |
| girl-veteran | ch7 s7（首發）· ch9 s6 | ✓ | ch7 · ch9 |
| 13-stairs | ch7 s3（首發）· ch9 s8（背景縮小裝飾） | ✓ | ch7 · ch9 |
| flip-20-to-50 | ch8 s4（首發）· ch9 s9（背景 loop） | ✓ | ch8 · ch9 |
| sudoku-board | ch7 s5 · ch8 s2（首發）· ch8 s3 | ✓ | ch7 · ch8 |
| spotlight-vignette | ch6 s6（首發）· ch7 s7 · ch9 s11 · ch9 s13 | ✓ | (隨 ★★★ climax 自動套) |
| halftone-burst | ch3 s3（微縮）· ch6 s6（首發）· ch7 s6 · ch7 s7 · ch9 s13 | ✓ | (隨 climax FX B 套) |
| ink-splatter | ch4 s2（輕量）· ch4 s3（首發）· ch5 s4（微縮）· ch6 s6 · ch7 s6 · ch7 s7 · ch9 s13 | ✓ | (隨 climax FX E 套) |
| screen-shake | ch6 s6 b3（首發）· ch7 s1（輕量）· ch7 s7 · ch9 s5 · ch9 s11 · ch9 s13 | ✓ | (隨 climax FX A 套) |

### §11.2 Climax FX coverage

| FX 代號 | 套用 step·beat |
| --- | --- |
| A screen-shake | 全部 10 個 punchline + ch7 s1 polish |
| B halftone-burst | ch6 s6 b3 · ch7 s6 b3 · ch7 s7 b6（雙 burst）· ch9 s13 b3 · ch3 s3（polish 微縮） |
| C slow-mo overshoot | 全部 10 個 punchline |
| E ink-splatter | ch4 s2（polish）· ch4 s3 b3 · ch5 s4（polish）· ch6 s6 b3 · ch7 s6 b3 · ch7 s7 b4/b5 · ch9 s13 b3 |
| G spotlight-vignette | ch6 s6 b3 · ch7 s7 b4/b5 · ch9 s11 b4 · ch9 s13 b3 |

### §11.3 ★ Star Legend

| 標記 | 意義 | step |
| --- | --- | --- |
| ★★★ | 全片三大笑點 climax、節奏控制必須完美、`?presenter=1` 重點檢視 | ch6 s6 備胎 · ch7 s7 老油條 · ch9 s13 電費小偷 |
| ★★ | 全片第二重一拍、僅次三大 ★★★ | ch9 s11 警語「人生第一次的外向 · 換來一輩子的內向」 |
| punchline | 走 [§2 Punchline Placeholder 模式](outline.md) | 共 10 個（見 §8.3 表）|
| polish | 非 punchline 但有特殊 FX 加成 | 共 6 個（見 §8.4 表）|

---

## §12 Web_style.md 摘要 Mirror（速查表）

> **完整版**: [web_style.md](web_style.md)（390 行 Neo-brutalism design system spec）。本節僅 mirror HTML agent 最常用 token、避免跨檔翻。

### §12.1 Color Tokens

```ts
// src/tokens/colors.ts
export const colors = {
  bg:        '#FFFDF5',  // Cream canvas
  ink:       '#000000',  // 邊框、文字、陰影
  accent:    '#FF6B6B',  // Hot Red — primary action / climax
  secondary: '#FFD93D',  // Vivid Yellow — secondary / highlight
  muted:     '#C4B5FD',  // Soft Violet — tertiary / depth
  white:     '#FFFFFF',  // 對比面板用
} as const;
```

**規則**:
- 絕不用 subtle grays（`#333` / `#666` / `#999`）— 要嘛 ink 黑、要嘛色塊
- 高對比強制（WCAG AA、4.5:1）
- 色塊區段用「cream / 黃 / 紫 / 黑」alternation 創造節奏

### §12.2 Border / Shadow Tokens

| token | 值 | 用途 |
| --- | --- | --- |
| `border-thin` | `2px solid #000` | ghost button、subtle separator |
| `border-default` | `4px solid #000` | **預設**所有 card / sticker |
| `border-thick` | `6px solid #000` | hero、warning sticker、warning sticker（ch9 s11）|
| `border-massive` | `8px solid #000` | major section divider、boom-double-ring |
| `shadow-sm` | `4px 4px 0 0 #000` | small sticker、button |
| `shadow-md` | `8px 8px 0 0 #000` | **預設** card |
| `shadow-lg` | `12px 12px 0 0 #000` | hero、章節主元素 |
| `shadow-massive` | `16px 16px 0 0 #000` | ★★★ climax 主 stamp |
| `shadow-burst` | `20px 20px 0 0 #000` | climax 砸下後 shadow burst 終態 |

### §12.3 Radius / Rotation Tokens

- **Radius**: `0` (default、所有 card / sticker / hero) 或 `9999px / rounded-full` (pill badge / 圓 sticker)
- **絕不用**: `rounded-md` / `rounded-lg` / `rounded-xl` (中段圓角)
- **Rotation (sticker 微旋轉)**: `rotate-1` (1°) / `-rotate-2` (-2°) / `rotate-3` (3°) — 三檔之一、不自由角度
- **Decorative rotation**: 黃星 spin-slow 12s、紫方塊 float ±16px 4s（per §9.6）

### §12.4 Interaction Tokens

```css
/* Button push (mechanical click) */
.btn-push { transition: all 100ms linear; }
.btn-push:active {
  transform: translate(2px, 2px);
  box-shadow: none;
}

/* Card lift (sticker hover) */
.card-lift { transition: all 200ms ease-out; }
.card-lift:hover {
  transform: translateY(-8px);
  box-shadow: 16px 16px 0 0 #000;  /* 從 8px 升到 16px */
}

/* Sticker hover scale */
.sticker:hover {
  transform: scale(1.05) rotate(var(--rotation));  /* 保持原 rotation */
}
```

**動畫速度**:
- Buttons: `duration-100` (100ms)
- Cards/Hovers: `duration-200` ~ `duration-300`
- Easing: `ease-linear` (mechanical) / `ease-out` (natural)、**避免** `ease-in-out`

### §12.5 Pattern Backgrounds（直接複製貼上）

```css
/* Halftone dots */
.halftone-bg {
  background-image: radial-gradient(#000 1.5px, transparent 1.5px);
  background-size: 20px 20px;
}

/* Grid pattern (graph paper) */
.grid-bg {
  background-size: 40px 40px;
  background-image:
    linear-gradient(to right, rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0,0,0,0.1) 1px, transparent 1px);
}

/* Radial dots (large) */
.radial-dots-bg {
  background-image: radial-gradient(circle, #000 2px, transparent 2.5px);
  background-size: 30px 30px;
}
```

完整 noise SVG 見 [§9.2](#92-svg-紙紋-noise-grain-全域)。

### §12.6 Tailwind Setup（速查）

`tailwind.config.ts`:
```ts
export default {
  theme: {
    extend: {
      colors: {
        'neo-bg':        '#FFFDF5',
        'neo-ink':       '#000000',
        'neo-accent':    '#FF6B6B',
        'neo-secondary': '#FFD93D',
        'neo-muted':     '#C4B5FD',
      },
      fontFamily: {
        'grotesk': ['Space Grotesk', 'Noto Sans SC', 'sans-serif'],
      },
      boxShadow: {
        'neo-sm':      '4px 4px 0 0 #000',
        'neo':         '8px 8px 0 0 #000',
        'neo-lg':      '12px 12px 0 0 #000',
        'neo-massive': '16px 16px 0 0 #000',
      },
    },
  },
}
```

Google Fonts 載入：
```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700;900&display=block" rel="stylesheet">
```
