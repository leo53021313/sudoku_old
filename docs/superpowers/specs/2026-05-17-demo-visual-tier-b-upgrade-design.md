# Demo Visual Upgrade · Tier B (cinematic polish) · Design

**Date**: 2026-05-17
**Scope**: `demo/outline.md` 視覺升級規範
**Constraint**: 不動 `demo/script.md`、不動既有 88 beat 結構、不動章節數
**Stack**: Vite + React + Tailwind v4 + Motion (Framer Motion) + lucide-react（全免費）

---

## 1 · 目標

把 `demo/outline.md` 的視覺規範從「已對齊 script 的 step 級設計」升級到「cinematic 氛圍 + climax 視覺衝擊」的全片整合版本，讓 12.5 分鐘演講從「會動的 Neo-brutalism 簡報」變成「電影感互動敘事」，而不靠任何付費工具或破壞既有 visual DNA。

### 非目標

- 不動 `demo/script.md`（口播稿已定稿）
- 不重寫 88 beat 的 cue / wait 節奏（既有設計已對齊口播）
- 不增減 step 數、不重排章節結構
- 不替換 `visualizer-launch/` URL scheme 機制
- 不加聲音設計（使用者明確拒絕 Howler.js）
- 不換 cursor（使用者明確拒絕 custom cursor）
- 不加 cinematic letterbox bars（使用者明確拒絕）
- 不破格 Neo-brutalism（不採 Tier C「監視器模式」破格方案）

---

## 2 · 技術堆疊

| 工具 | 角色 | 不選的替代 |
|---|---|---|
| **Vite** | dev server + static folder 打包 | ~~Next.js~~（不需 SSR） |
| **React** | 88 beat 元件化、motif 復用、presenter mode | ~~vanilla JS~~（88 beat 狀態機過大） |
| **Tailwind v4** | Neo-brutalism utility token（hard shadow / cream / 微旋轉） | ~~CSS-in-JS~~（多餘） |
| **Motion (Framer Motion)** | 全部動畫（包含 3 ★★★ climax timeline） | ~~GSAP~~（付費 SplitText 不要、Motion v11 `useAnimate` 夠用） |
| **lucide-react** | Route A icon（大腦 / 門 / 封鎖 / 神經網路 / 狗 / 衣服） | ~~Phosphor React~~（lucide 已涵蓋） |

**明確剔除**：GSAP、Howler.js、SplitType、TypeScript（可選但非必要）、Three.js、Lottie、Rive、Slidev、Reveal.js、Lenis、Theatre.js

**部署目標**：`demo/presentation/dist/` 一個靜態 folder，與 `demo/visualizer-launch/` 並列。`pnpm build` 後可雙擊 `index.html` 或 `npx serve dist` 啟動。

---

## 3 · Tier B 加料包 · 全域視覺氛圍（6 項）

這 6 項是全域常駐效果、所有章節都套用、不影響 step 級設計。寫入 `demo/outline.md` 頂部新 section「全域視覺升級 v3」。

### 3.1 章節色票背景漸層

每章 cream 底（`#FFFDF5`）外加一層該章副色的對角漸層：

```css
background: linear-gradient(135deg, #FFFDF5 0%, var(--chapter-tint) 100%);
--chapter-tint: rgba(<chapter-secondary-rgb>, 0.08);
```

**`--chapter-tint` 配色表**（取自 outline.md 既有章節色票）：

| ch | 主情緒 | --chapter-tint 取色 | 視覺效果 |
|---|---|---|---|
| 1 coldopen | 白日夢 | `rgba(196,181,253,0.08)` 紫 | 微夢幻 |
| 2 ml-map | 教學理性 | `rgba(0,0,0,0.04)` 黑線 | 微紙稿 |
| 3 llm-vs-rl | 對比分歧 | `rgba(196,181,253,0.06)` 紫 | 微衝突 |
| 4 data-hunt | 戰鬥 | `rgba(255,217,61,0.06)` 黃 | 微緊張 |
| 5 legacy | 崩盤 #1 | `rgba(255,107,107,0.07)` 紅 | 微警報 |
| 6 sb3 | 戀愛錯覺 | `rgba(255,182,193,0.10)` 粉 | 微甜膩 |
| 7 reasoner | 嚴肅死結 | `rgba(0,0,0,0.05)` 黑 | 微沉重 |
| 8 apprentice | 突破光明 | `rgba(255,217,61,0.10)` 金黃 | 微希望 |
| 9 callback | 收斂哲思 | `rgba(196,181,253,0.07)` 紫 | 微遠 |

**章節切換時**：tint 過渡走 View Transitions API（見 3.3）、500ms cross-fade。

### 3.2 SVG 紙紋 noise grain

全屏覆蓋層、`pointer-events: none`、`z-index: 1`（在背景漸層上、所有 sticker 下）：

```css
.global-grain {
  position: fixed; inset: 0; z-index: 1; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.15 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  mix-blend-mode: multiply;
  opacity: 0.5;
}
```

**規範**：opacity 不可超過 0.6（再高會搶 sticker 焦點）、baseFrequency 不可低於 0.7（再低會看到大斑塊、破壞紙感）。

### 3.3 View Transitions API · 章節 cross-fade

章節切換（不是 step 切換）時走瀏覽器原生 View Transitions：

```js
function navigateToChapter(chId) {
  if (!document.startViewTransition) {
    setChapter(chId); // graceful fallback
    return;
  }
  document.startViewTransition(() => setChapter(chId));
}
```

**CSS**：

```css
::view-transition-old(root) { animation: fade-out 0.5s ease-out forwards; }
::view-transition-new(root) { animation: fade-in 0.6s ease-out forwards; }
@keyframes fade-out { to { opacity: 0; } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
```

**fallback**：Safari / Firefox 不支援 View Transitions 時、退化為純 React state 切換（無動畫、不影響功能）。

**注意**：仍保留 outline.md 既有的「章節間 fade-bridge auto-transition」（0.8-1.2s）—— View Transitions 是「章節主體 cross-fade」、fade-bridge 是「色票 hold 中介」、兩者不衝突。

### 3.4 動態 halftone 漂移

既有 halftone dots 背景（`background-image: radial-gradient(#000 1.5px, transparent 1.5px); background-size: 20px 20px;`）加上極緩慢漂移：

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

**規範**：60s 完成一個完整 cycle、`linear` easing（不是 ease-in-out、會被察覺）、垂直向上。`prefers-reduced-motion: reduce` 必須關閉。

### 3.5 Beat indicator · 隱藏式

底部固定 1.5% 高度區塊、平時 `opacity: 0`、滑鼠進入 bottom 32px 內 0.6s 淡入到 0.7、移開 1s 淡出。

**佈局**：88 個小方塊水平排列（對應全片 88 beat、跨章不分隔）、每個方塊 ~10×4px：

- 已過 beat：`#000` 黑色實心
- 當前 beat：`#FF6B6B` 紅色實心 + scale 1.1
- 未到 beat：透明 + 1.5px 黑邊輪廓
- 章節邊界（9 章 → 8 個邊界）：在方塊間插 4px 黃色 `#FFD93D` 隔條

**右上角同步顯示文字**：`step M / 57 · beat N / X · ch K`（11px、`color: #666`、Space Grotesk 700）

**作用**：
1. 演講者下意識掌握剩餘節奏（特別是 climax 之前要不要加速）
2. 觀眾 hover 一下能看到「快結束了」的暗示、產生收尾期待感

### 3.6 環境裝飾幾何 · 各章常駐

每章 4-6 個微旋轉幾何 sticker 常駐邊角、CSS 緩慢浮動、`z-index: 0`（在所有 sticker 下、grain 上）。

**規範**：
- 形狀僅限 6 種：`star`（5 角星、`clip-path` 多邊形）、`square`、`circle`、`triangle`、`outline-question`（描邊問號）、`pill`（圓角矩形）
- 配色取「章節副色 + climax 色」（避開主色避免搶焦點）
- 微旋轉 ±3°-8°
- 浮動動畫：`translateY(±8px) translateX(±4px)`、4-8s `ease-in-out infinite`
- 位置：4 角為主、可有 1-2 個浮在中段邊緣（離主元素 30%+ 距離）

**Per-chapter ambient shapes 配置**（寫入 outline.md 每章 header）：

| ch | shapes（位置 · 形狀 · 顏色 · 微旋轉） |
|---|---|
| 1 coldopen | TL 黃星 +15° · TR 紫方塊 -8° · BL 紅圓 0° · BR 描邊? +12° · 中右 黃圓 -3° |
| 2 ml-map | TL 黑outline star -10° · TR 灰線方塊 +5° · BL 黑pill 0° · BR 紅圓 -8°（為 AlphaGo climax 鋪） |
| 3 llm-vs-rl | TL 紫方塊 -5° · TR 黃圓 +10° · BL 紫三角 +3° · BR 黃菱形 -7° · 中下 紅? +8° |
| 4 data-hunt | TL 黑方塊 +5° · TR 黃星 -10° · BL 紅圓 +12° · BR 黑outline pill -3° |
| 5 legacy | TL 紅叉 +15°（既有 ch5 紅叉叉 motif）· TR 紅圓 -5° · BL 紅outline square +8° · BR 紅pill -3° |
| 6 sb3 | TL 粉圓 +10° · TR 紅心-形（用 clip-path）-6° · BL 粉方塊 +3° · BR 紅pill -10° · 中左 灰圓 +5°（暗示備胎前夕） |
| 7 reasoner | TL 紅方塊 -8° · TR 紫星 +12° · BL 黃菱形 +5° · BR 黑outline? -10° · 中右 紫圓 +3° · 中左 紅三角 -5° |
| 8 apprentice | TL 黃星 +10°（強）· TR 紫方塊 -8° · BL 金圓 +3° · BR 黃+號 -12° |
| 9 callback | TL 紫圓 +5° · TR 紅星 -10° · BL 紫outline square +8° · BR 灰? -3°（呼應沉思氣質） |

**不可變動**：形狀總數每章不超過 6 個（超過 → 視覺密度過高、與 sticker 搶焦點）。

---

## 4 · 三大 ★★★ Climax 視覺加成（5 項效果）

僅套用於三個 ★★★ punchline 拍：**ch6 s6 備胎**、**ch7 s7 老油條**、**ch9 s13 電費小偷**。對應 `beat N` 描述中的 `[click]` punchline reveal beat（不是鋪墊 beat）。

### 4.1 效果定義

| 代號 | 名稱 | 觸發時機 | 規格 |
|---|---|---|---|
| **A** | Screen shake 微震 | stamp 砸下瞬間 | 150ms 內整個 `<main>` 容器 `translate(±5px, ±3px)` 隨機 3 次（每次 50ms） |
| **B** | Halftone 同心圓爆破 | stamp 砸下瞬間（與 A 同步） | 從 stamp 中心向外放射 3 圈 dots、500ms scale 0→3、opacity 1→0、`mask: radial-gradient` 控形 |
| **C** | Slow-mo overshoot 4 拍 | stamp 進場動畫 | scale 0 → 1.4 (160ms) → 1.0 (200ms) → 0.95 (120ms) → 1.0 (120ms)、共 600ms、bezier `(0.34, 1.56, 0.64, 1)` |
| **E** | 黑墨噴濺 splatter | stamp 砸下瞬間（A/B 同步） | 周圍 8 個不規則黑墨點（SVG inline path）stagger spawn 80ms 間隔、scale 0→1 overshoot、半徑 80-180px 隨機 |
| **G** | Spotlight 聚焦暗化 | punchline 揭曉那一拍開始、climax 全程 hold | 全屏 `radial-gradient(circle at <stamp-center>, transparent 25%, rgba(0,0,0,0.6) 100%)` overlay、`mix-blend-mode: multiply`、500ms 淡入、stamp 自身保亮 |

### 4.2 套用映射

| step | beat | 套用 |
|---|---|---|
| ch6 s6 beat 3 「備胎」 | `bei-tai-fill` | A + B + C + E + G |
| ch7 s7 beat 4 「❌ 嫌她胖」 | `answer-a-fill` | A + E + G（C 不用、文字 mask reveal 不是 stamp）|
| ch7 s7 beat 5 「❌ 你不關心健康」 | `answer-b-fill` | A + E + G |
| ch7 s7 beat 6 「雙 ❌ flash」 | `both-flash` | B（雙 burst from 兩個 ❌）|
| ch9 s13 beat 3 「電費小偷」 | `power-thief-fill` | A + B + C + E + G + 整屏 shake（已在 outline 內、本 spec 強化） |

### 4.3 一般 punchline step 用「climax 輕量版」

剩 7 個 punchline placeholder step 用 A + C 兩項（去除 B/E/G 的視覺重度、避免疲勞）：

| step | beat | 套用 |
|---|---|---|
| ch1 s8 beat 3 punchline-reveal | A + C |
| ch4 s3 beat 3 victim-stamp | A + C + E（取「stamp 砸下」邏輯）|
| ch5 s1 beat 4 crash-fill | A + C |
| ch6 s1 beat 3 crash-fill | A + C |
| ch7 s6 beat 3 zero-drop | A + B + C + E（「0」字屬實體 stamp 性質）|
| ch9 s5 beat 4 punchline-hero | A + C |
| ch9 s11 beat 4 warn-line-b-fill | A + C + G（警語性質、聚焦合理）|

### 4.4 動畫實作 reference（給後續 plan 用）

Motion v11 `useAnimate` sequence 範例（不寫進 outline.md、僅供 plan / 實作 agent 參考）：

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

---

## 5 · Motif Library 新增 4 個

寫入 outline.md `## Motif Library` section 表格：

| Motif ID | 首次出現 | 視覺定義 | 復用點 |
|---|---|---|---|
| `motif/spotlight-vignette` | ch6 s6 beat 3（備胎） | 全屏 radial gradient overlay、from transparent → rgba(0,0,0,0.6)、`mix-blend-mode: multiply`、500ms 淡入 | ch7 s7 beat 4/5、ch9 s11 beat 4、ch9 s13 beat 3 |
| `motif/halftone-burst` | ch6 s6 beat 3（備胎） | 從 stamp 中心放射 3 圈 dots、scale 0→3 opacity 1→0、500ms、與 `motif/boom-double-ring` 語彙互補 | ch7 s6 beat 3「0」、ch7 s7 beat 6、ch9 s13 beat 3 |
| `motif/ink-splatter` | ch4 s3 beat 3（受害者） | SVG 8 個不規則黑墨點 path、stagger 80ms scale 0→1 overshoot、半徑 80-180px 隨機 | ch6 s6 beat 3、ch7 s6 beat 3、ch7 s7 beat 4/5、ch9 s13 beat 3 |
| `motif/screen-shake` | ch6 s6 beat 3（備胎） | `<main>` 容器 translate(±5px,±3px) 隨機 3 次共 150ms | ch7 s7 beat 4/5、ch9 s5 beat 4、ch9 s11 beat 4、ch9 s13 beat 3 |

**新增原則**（同既有 outline 規範）：任何視覺元素若打算復用於 ≥ 2 step，必須登錄 motif library。

---

## 6 · 修改範圍 · outline.md 編輯指南

實作 agent 依以下順序編輯 `demo/outline.md`：

### 6.1 新增頂部「全域視覺升級 v3」section

**位置**：插在 `## 全域設計原則` section 之後、`## 1. coldopen` 之前。

**內容**：將本 spec section 3（Tier B 加料包）、section 4（Climax 加成）、section 5（新增 motif）的規範完整移植過去、加 cross-link 到既有 `## Motif Library` 與 `## 章節情緒色票`。

**估計增加行數**：~180 行。

### 6.2 每章 header 加 ambient shapes 規格

**位置**：每章 `**章節色票**：...` 行下方、`**信息池**：...` 行上方插入新行：

```markdown
**Ambient shapes**：TL 黃星 +15° · TR 紫方塊 -8° · BL 紅圓 0° · BR 描邊? +12° · 中右 黃圓 -3°（取自 [§3.6 全域 ambient shapes 配置表](#36-環境裝飾幾何--各章常駐)）
```

**估計增加行數**：9 章 × ~3 行 = ~30 行。

### 6.3 10 個 punchline step 加 climax 引用

**位置**：每個 punchline placeholder step 的「**placeholder 模式**」行下方加新行：

```markdown
▸ **Climax 加成**: A (screen-shake) + B (halftone-burst) + C (slow-mo) + E (ink-splatter) + G (spotlight) · 引用 [§4.2 套用映射表](#42-套用映射)
```

**對應 step**：
- ★★★ 三大：ch6 s6、ch7 s7、ch9 s13 → 完整 A+B+C+E+G
- 輕量版 7 個：ch1 s8、ch4 s3、ch5 s1、ch6 s1、ch7 s6、ch9 s5、ch9 s11 → A+C 起跳、視 step 性質加 B/E/G（per §4.3）

**估計增加行數**：10 step × ~2 行 = ~20 行。

### 6.4 視覺平淡 step 補強建議

下列 step 因為純鋪墊 / 轉場性質、視覺密度偏低。在「**開發計畫**」內每個對應 step 加一行：

```markdown
▸ **視覺補強**: <具體建議>
```

| step | 補強建議 |
|---|---|
| ch2 s4 (cliffhanger 問號) | 問號用 `motif/yellow-highlight` 黃底放大 +10%、enter 動畫加 rotate 8 圈完整旋轉一次 |
| ch3 s3 (OK 純 RL cliffhanger) | OK 標語切換時加 `motif/halftone-burst` 微縮版（不是 climax 規模、半徑限 60px） |
| ch4 s2 (supervised 拒絕 紅 stamp) | 加 `motif/ink-splatter` 輕量版（4 個黑點、半徑 40-80px） |
| ch5 s4 (架構金句 hero) | 4 個關鍵詞 stagger 黃底高亮時、每個加 `motif/ink-splatter` 1 個小黑點佐證「在白紙上寫字」感 |
| ch7 s1 (重寫 hero) | 「重寫」黃底高亮 slide-in 時加 80ms 整屏微震（screen-shake 輕量版、±2px） |
| ch8 s1 (反向思考過渡) | 黑底回 cream 過渡用 1.2s CSS `background-color` transition（cubic-bezier 自然減速）+ 同步 halftone dots fade-in、避免「色塊硬切」破壞 cinematic 氣質 |

**估計增加行數**：6 step × ~2 行 = ~12 行。

### 6.5 Motif Library 表新增 4 行

直接插入既有 `## Motif Library` 表格底部（per §5）。

**估計增加行數**：~5 行（含表頭調整）。

### 6.6 反向索引同步

`## 反向索引 · script.md 行號 → outline step` 表：在受影響 step 的「內容摘要」欄末尾追加 `· +climax/A+C` 或 `· +ambient` 等簡短標記。

**估計增加行數**：0（只改既有行尾、不增行）。

### 6.7 素材清單同步

每章「既有素材清單」section 末尾加新行：

```markdown
- **[D]** ambient shapes × 4-6（per §3.6 配置表）
- **[D]+[E]** 章節 tint 背景漸層（純 CSS）
```

`## 1. coldopen` 既有素材清單末尾額外加：

```markdown
- **[E]** 全屏 SVG noise grain（per §3.2、整片全域、僅此處列一次）
- **[E]** 動態 halftone 漂移（per §3.4、全域）
- **[D]+[E]** Beat indicator 隱藏式底部條（per §3.5、全域）
```

ch6 / ch7 / ch9 在 climax step 對應素材清單條目末尾加 `+ climax A/B/C/E/G`。

**估計增加行數**：~25 行。

---

### 修改範圍總計

| section | 增加行數 |
|---|---|
| 6.1 全域升級 section | ~180 |
| 6.2 章節 ambient shapes header | ~30 |
| 6.3 10 punchline climax 引用 | ~20 |
| 6.4 視覺補強 6 step | ~12 |
| 6.5 Motif Library 新增 | ~5 |
| 6.6 反向索引 | 0 |
| 6.7 素材清單同步 | ~25 |
| **合計** | **~272 行**（outline.md 目前 917 行 → 約 1189 行） |

---

## 7 · 驗收標準

實作完成後、outline.md 必須滿足：

1. **全域升級 section 完整可實作**：寫死 CSS 範本、變量名、`useAnimate` sequence 範例都可被後續 plan 直接抄
2. **每章 ambient shapes 規格唯一**：不出現「TBD」「待定」「視情況」字眼
3. **10 punchline step 全部標 climax 引用**：對應 §4.2 / §4.3 套用映射
4. **6 個視覺補強 step 全部標補強建議**：建議具體可實作（不是「加強氣氛」這種空話）
5. **Motif Library 新增 4 個 motif 都有 ID、首次出現點、復用點**：跟既有 9 個 motif 格式一致
6. **反向索引 / 素材清單同步更新**：不留陳舊段落

實作 agent 完成後跑：

```bash
grep -c "Climax 加成" demo/outline.md   # 應為 10
grep -c "Ambient shapes" demo/outline.md  # 應為 9
grep -c "motif/spotlight-vignette" demo/outline.md  # 應 ≥ 5 (首發 1 + 復用 ≥ 4)
grep -c "motif/halftone-burst" demo/outline.md  # 應 ≥ 4
grep -c "motif/ink-splatter" demo/outline.md  # 應 ≥ 6
grep -c "motif/screen-shake" demo/outline.md  # 應 ≥ 6
```

---

## 8 · 風險與限制

### 8.1 已知風險

| 風險 | 緩解 |
|---|---|
| Tier B 加料 6 項全套用 → 視覺密度過高、搶 sticker 焦點 | grain ≤ 0.5 opacity、ambient shapes ≤ 6/ch、beat indicator hover 才顯、tint ≤ 0.10 opacity——全部都有上限 |
| Climax A 螢幕震、可能引起前庭敏感者不適 | `prefers-reduced-motion: reduce` 必須關閉 shake、改純 scale punch |
| 動態 halftone drift 60s 過快會被察覺、過慢無感 | 60s linear、實機測 ≥ 5 分鐘觀眾不應有意識察覺、若察覺 → 拉到 90s |
| View Transitions API 在 Safari < 18 / Firefox 全版本不支援 | 純 React state 切換 fallback、無動畫但功能不損 |
| Motion v11 `useAnimate` 在 SSR 環境會 warn | 不用 SSR（Vite SPA、純 client） |

### 8.2 不做的事

- 不寫每章「視覺品質評分」（這是 v4 範圍、本 spec 不做）
- 不加額外 motif（4 個就夠、再加會造成 motif library 過載）
- 不重新審視既有 9 個 motif（已穩定、不動）
- 不增 ★★★ climax 的數量（3 個是設計上限、再加會稀釋 climax 衝擊力）
- 不寫實作程式碼（本 spec 只規範 outline.md、實作交由後續 plan）

---

## 9 · 後續流程

本 spec 通過驗收後、由 `writing-plans` skill 產出實作 plan：

1. **Plan 範圍**：將 §6 各小節拆成獨立可執行任務（建議 6-8 個 task）
2. **執行方式**：可以走 `subagent-driven-development`（每個 6.X 一個 subagent）或單 session 順序執行
3. **驗收**：跑 §7 grep 檢核 + 人工檢視 outline.md 變更 diff
4. **後續 spec**（不在本範圍）：
   - v4 · 視覺品質評分系統（57 step 視覺密度 audit）
   - v5 · 實作 PoC（建立 `demo/presentation/` Vite project）

---

## 10 · 決策記錄（brainstorming session 摘要）

本 spec 由 2026-05-17 brainstorming session 產出、關鍵決策：

| Q | 選擇 | 剔除 |
|---|---|---|
| Q1 視覺野心 tier | Tier B（cinematic 加料） | Tier A（守規）、Tier C（破格） |
| Q2 Tier B 加料 | 1+2+4+6+7+8 | 3（custom cursor）、5（cinematic letterbox） |
| Q3 Climax 加成 | A+B+C+E+G | D（白閃 · 閃光敏感）、F（ink drip · CP 低）、H（halftone 密度爆衝 · 與 A 重複） |
| Q4 Custom cursor | 不換 | Style 1/2/3 |
| Q5 修改範圍 | B（平衡升級） | A（最小手術）、C（全面重寫） |
| 技術堆疊 | Vite+React+Tailwind v4+Motion+lucide-react | GSAP、Howler.js、SplitType、TypeScript、Three.js、Lottie、Rive |

使用者明確強調：**免費、簡單、無聲音**。所有技術 / 工具選擇必須通過這三個約束。
