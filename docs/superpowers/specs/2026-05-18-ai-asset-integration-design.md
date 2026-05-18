# AI 生成素材整合進 demo/presentation/ 設計

> **狀態**：design approved（2026-05-18 brainstorming session）· 待 plan
> **背景**：使用者已用 GPT Image 2 / Nano Banana 2 生成 10 張 Neo-brutalism 風格插畫、放在 `demo/asset-experiments/`。這份 spec 規範如何把它們整合進現有 React 簡報、取代既有的 text-sticker / emoji / `<AssetPlaceholder>`。
> **配對檔**：
> - [demo/asset-production-ai-prompts.md](../../../demo/asset-production-ai-prompts.md) — 10 張的生成 prompt 跟驗收
> - [demo/asset-production.md](../../../demo/asset-production.md) — 原 D/E/A 三路線素材清單
> - [demo/presentation/](../../../demo/presentation/) — 9 章 React 簡報實作

## §0 四個策略決策（brainstorming 已確認）

| # | 決策 | 結論 | 為什麼 |
| --- | --- | --- | --- |
| 1 | 整合策略 | **全面取代**現有 text-sticker / emoji / placeholder | AI 視覺品質明顯優於 emoji 與純文字卡、風格一致性也強 |
| 2 | 包裝風格 | **背景裸貼 + sticker 包 Neo-brutalism card**（4px 黑邊 + 8px hard shadow + 微旋轉 ±3°） | 跟現有黃紅紫 text sticker 視覺語言一致；背景不包框避免「相框感」破壞 cinema 氛圍 |
| 3 | 檔案路徑 | `public/images/ai/ch<N>/<name>.png` 按章節分 | 未來新增 sticker 時不會跟 ch1 一坨混 |
| 4 | ch1 s4-s7 場景 | **Cinema mode**：MRT full-bleed 100vw × 100vh backdrop、AI 人物 sticker overlay | 最有「捷運上發呆」氛圍；犧牲 ambient-shapes 在這 4 step 的可見度 |

---

## §1 元件設計

新增 **2 個 component** 到 `src/components/`：

### 1.1 `AiBackdrop.jsx`

**用途**：cinema-mode 全螢幕背景圖（目前只有 `ch1-mrt-window.png` 一張）

**API**：
```jsx
<AiBackdrop src="/images/ai/ch1/mrt-window.png" alt="台北捷運車廂內視" />
```

**實作**（完整）：
```jsx
export function AiBackdrop({ src, alt = '' }) {
  return (
    <img
      src={src}
      alt={alt}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100vw',
        height: '100vh',
        objectFit: 'cover',
        objectPosition: 'center',
        zIndex: 5,
        pointerEvents: 'none',
      }}
    />
  );
}
```

**z-index 規約**：
- `ChapterTint` = 0、`AmbientShapes` = 0、`HalftoneBg` = 0、`GlobalGrain` = 1
- `AiBackdrop` = **5**（蓋掉 ambient/tint/halftone、但保留 grain 質感）
- `<main>` step content = 20（sticker / hero 都在這一層）
- `ChapterNav` / `ProgressBar` / `BeatIndicator` / `PresenterPanel` = 100+

### 1.2 `AiSticker.jsx`

**用途**：人物 / 物件 sticker 包裝（9 張 sticker 全部走這個）

**API**：
```jsx
<AiSticker
  src="/images/ai/ch1/girl-daydream.png"
  alt="正妹發呆中"
  width={280}
  rotation={-4}
  shadow={8}
/>
```

**Props**：
| prop | 型別 | 預設 | 說明 |
| --- | --- | --- | --- |
| `src` | string | required | 圖片路徑 |
| `alt` | string | `''` | 無障礙 alt text |
| `width` | number | `280` | sticker 寬度（px）、高度等比例 |
| `rotation` | number | `-3` | 旋轉角度（度） |
| `shadow` | number | `8` | hard shadow 偏移（px） |

**實作**（完整）：
```jsx
export function AiSticker({ src, alt = '', width = 280, rotation = -3, shadow = 8 }) {
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
        style={{ display: 'block', width, height: 'auto' }}
      />
    </div>
  );
}
```

**為什麼分兩個元件而非 `mode="backdrop|sticker"` prop**：backdrop 沒有 border / shadow / rotation、sticker 必須有；硬塞同一個會 props 互斥 + readability 差。Single Responsibility 比 abstraction 優先。

### 1.3 `AssetPlaceholder.jsx` 命運

**保留不動**。仍有 motif shells 待填（ch6 girl-new、ch7 girl-veteran、ch8 sudoku-board 等）會繼續用。AI 路線只取代有對應圖的 10 個位置。

---

## §2 檔案目錄結構

### 2.1 新建目錄

```
demo/presentation/public/images/ai/
├── ch1/
│   ├── mrt-window.png          ← demo/asset-experiments/ch1-mrt-window.png
│   ├── girl-daydream.png       ← demo/asset-experiments/ch1-girl-daydream.png
│   ├── codebullet-flappy.png   ← demo/asset-experiments/ch1-codebullet-flappy.png
│   └── soldier-sudoku.png      ← demo/asset-experiments/ch1-soldier-sudoku.png
├── ch2/
│   ├── teacher-notes.png       ← demo/asset-experiments/ch2-teacher-notes.png
│   ├── folding-clothes.png     ← demo/asset-experiments/ch2-folding-clothes.png
│   └── dog-handshake.png       ← demo/asset-experiments/ch2-dog-handshake.png
└── ch9/
    ├── airplane-bird.png       ← demo/asset-experiments/ch9-airplane-bird.png
    ├── brain-reward.png        ← demo/asset-experiments/ch9-brain-reward.png（s3 + s5 共用）
    └── neural-network.png      ← demo/asset-experiments/ch9-neural-network.png
```

### 2.2 搬移腳本（PowerShell）

```powershell
$src = 'demo/asset-experiments'
$dst = 'demo/presentation/public/images/ai'
New-Item -ItemType Directory -Force -Path "$dst/ch1","$dst/ch2","$dst/ch9" | Out-Null

@{
  'ch1-mrt-window.png'         = 'ch1/mrt-window.png'
  'ch1-girl-daydream.png'      = 'ch1/girl-daydream.png'
  'ch1-codebullet-flappy.png'  = 'ch1/codebullet-flappy.png'
  'ch1-soldier-sudoku.png'     = 'ch1/soldier-sudoku.png'
  'ch2-teacher-notes.png'      = 'ch2/teacher-notes.png'
  'ch2-folding-clothes.png'    = 'ch2/folding-clothes.png'
  'ch2-dog-handshake.png'      = 'ch2/dog-handshake.png'
  'ch9-airplane-bird.png'      = 'ch9/airplane-bird.png'
  'ch9-brain-reward.png'       = 'ch9/brain-reward.png'
  'ch9-neural-network.png'     = 'ch9/neural-network.png'
} | ForEach-Object { $_.GetEnumerator() } | ForEach-Object {
  Copy-Item "$src/$($_.Key)" "$dst/$($_.Value)" -Force
}
```

**為什麼 copy 不是 move**：保留 `asset-experiments/` 當原始底片、若要重生只動 experiments、production 路徑穩定。

### 2.3 不入 .gitignore

整 `public/images/ai/` 提交進 git（PNG 約 10 × 200KB = 2MB、可接受）。不用 Git LFS。

---

## §3 取代清單（10 個 step）

### 3.1 ch1 coldopen（4 step 共用同一張 MRT backdrop + 3 張 sticker stagger）

| step | 拿掉 | 放入 |
| --- | --- | --- |
| `Ch1Step4.jsx` | `<AssetPlaceholder type="[E]" 720×400>` MRT card + 黃底「正妹發呆中」文字 sticker | `<AiBackdrop src="/images/ai/ch1/mrt-window.png">` + `<AiSticker src="/images/ai/ch1/girl-daydream.png" rotation={-4} width={280}>` 放 absolute bottom-left 14%/8% |
| `Ch1Step5.jsx` | 同 s4 + 紫底「Code Bullet · flappy bird」文字 sticker | `<AiBackdrop>` + girl `<AiSticker>` persisted + `<AiSticker src=".../codebullet-flappy.png" rotation={3} width={280}>` 放 top-right 14%/8% |
| `Ch1Step6.jsx` | 同 s5 視覺 + 「⋯⋯」省略號氣球 | 同 s5 視覺（girl + flappy bird persisted）+ 「⋯⋯」氣球（保留純 HTML） |
| `Ch1Step7.jsx` | 同 s5 + 紅底「沒手機·解數獨」文字 sticker | 同 s5（girl + flappy bird persisted）+ `<AiSticker src=".../soldier-sudoku.png" rotation={2} width={280}>` 放 bottom-right 14%/8% |

**關鍵衝突解法 — MRT backdrop 跨 step 共用避免重 mount**：
- 把 `<AiBackdrop>` 從 `Ch1StepN.jsx` 升級到 `Ch1.jsx`（chapter 層）
- 條件 render：`{step >= 4 && step <= 7 && <AiBackdrop src="..." />}`
- step 4→5→6→7 之間 React 不會 unmount/remount `<img>`、不會重新解碼、視覺不會閃
- 各 step component 只負責自己的 sticker

### 3.2 ch2 ml-map（3 step、每 step 換一張右側插畫）

| step | 拿掉 | 放入 |
| --- | --- | --- |
| `Ch2Step1.jsx` | 右側 absolute 三卡疊「老師 → 題目+答案 → 學生硬背」純文字 stack | `<AiSticker src="/images/ai/ch2/teacher-notes.png" rotation={-2} width={420}>` 同位置 |
| `Ch2Step2.jsx` | 右側「👕👖👔 一堆 → 紅/黃/紫 三色 card」迷你 layout | `<AiSticker src=".../folding-clothes.png" rotation={3} width={420}>` 同位置 |
| `Ch2Step3.jsx` | 左下 absolute「🐕 ↔ 🤝」64px emoji | `<AiSticker src=".../dog-handshake.png" rotation={-3} width={420}>` 同位置 |

**保留**：ch2 三 step 的「機器學習 ①/②/③」kicker、`supervised/unsupervised/RL` 大字 mask-reveal、「白話：...」黃/紫底 sticker、ch2 s3 的 AlphaGo 紅 stamp。

### 3.3 ch9 callback

| step | 拿掉 | 放入 |
| --- | --- | --- |
| `Ch9Step3.jsx` | 左卡 🧠 96px emoji + 右卡 🕸️ 96px emoji | 左卡內貼 `<img src="/images/ai/ch9/brain-reward.png" style={{width:'70%'}}>`（裸貼、卡本身已是黑邊框）+ 右卡內貼 `<img src=".../neural-network.png" style={{width:'70%'}}>` |
| `Ch9Step4.jsx` | ✈️ 200px emoji + 自寫 SVG 雙向箭頭 + 🐦 200px emoji | `<AiSticker src=".../airplane-bird.png" rotation={0} width={900}>`（整張 16:9、內含飛機+鳥並置）。**保留**現有 SVG 箭頭 path（疊在中央、做出「鳥 ← 飛機」模仿方向） |
| `Ch9Step5.jsx` | 中央 🧠 160px emoji | `<AiSticker src=".../brain-reward.png" rotation={0} width={320}>` 同位置（含原 scale 動畫） |

**關鍵衝突解法 — ch9 s3 黑卡背景 vs PNG cream 底**：
- 問題：`brain-reward.png` 本身是 cream 底 + 黑線、若直接貼進黑色左卡內、圖片矩形會切出一塊白色矩形、視覺不協調
- **解法**：左卡背景從 `#000` 改成 `#FFFDF5`（cream）、跟右卡視覺對稱；「腦科學 RL」文字用紅底高亮 sticker 維持「左 RL 黑/右 AI 白」的對比強度（高亮從 background 移到 label）
- 動畫保留：`clipPath: inset(0 100% 0 0) → inset(0 0 0 0)` 從左 wipe-in

**ch9 s4 airplane-bird 整圖 width 為何 900？**：原 emoji 兩個 200px + 中間 48px gap + arrow 120px ≈ 568px 寬。AI 圖整張 16:9 含飛機+鳥比例約 1600×900、若放 width=900 則跨主畫面約 50% 寬、視覺重量足。但 prompt 圖中央留白由 HTML SVG 箭頭覆蓋（不另疊一個 sticker 上去、否則破風格）。

---

## §4 動畫與互動保留清單

每 step 既有 `motion.div` 動畫（initial / animate / transition / delay）**全部保留**、只改 children；尤其：

| step | 必須保留的動畫 |
| --- | --- |
| Ch1Step4 | MRT scale 0.85→1 overshoot delay 0.7s；girl x:-200/y:100 → 0/0 scale 0.7→1 overshoot delay 1.0s |
| Ch1Step5 | flappy bird x:200/y:-100 → 0/0 overshoot delay 0.4s；思考線 SVG path stroke-dasharray draw delay 0.5s |
| Ch1Step7 | soldier x:200/y:100 → 0/0 overshoot |
| Ch2Step1-3 | kicker fade-down、大字 clipPath mask-reveal、白話 sticker fade-up、右側插畫 fade-in（delay 1.4s）。把現有 stack 取代成 `<AiSticker>` 不影響這些動畫、只是內容變圖片 |
| Ch9Step3 | 左卡 clipPath wipe 從左、右卡 clipPath wipe 從右、中央「=」scale 0→1 rotate -10 overshoot |
| Ch9Step4 | 飛機/鳥 emoji x:-100/100 → 0 入場 + 鳥 y:[0,-6,0] 1.2s 拍翅 loop。**改用 AiSticker 後**：整張 airplane-bird 圖整體入場、無法獨立拍翅；可接受（拍翅效果原本就在 AI 圖內以「one wing up one wing down」靜態姿態暗示） |
| Ch9Step5 | beat 0 brain scale 0→1 overshoot；beat 1 左 + 浮動；beat 2 右 - 浮動；beat 3 hero stamp + climax A+C + shake |

---

## §5 改動範圍 summary

### 新增檔案（2）
- `demo/presentation/src/components/AiBackdrop.jsx`
- `demo/presentation/src/components/AiSticker.jsx`

### 新增 asset（10）
- `demo/presentation/public/images/ai/ch1/{mrt-window,girl-daydream,codebullet-flappy,soldier-sudoku}.png`
- `demo/presentation/public/images/ai/ch2/{teacher-notes,folding-clothes,dog-handshake}.png`
- `demo/presentation/public/images/ai/ch9/{airplane-bird,brain-reward,neural-network}.png`

### 修改檔案（10）
- `demo/presentation/src/chapters/ch1-coldopen/Ch1.jsx`（加 MRT backdrop 跨 step 邏輯）
- `demo/presentation/src/chapters/ch1-coldopen/Ch1Step4.jsx`、`Ch1Step5.jsx`、`Ch1Step6.jsx`、`Ch1Step7.jsx`
- `demo/presentation/src/chapters/ch2-ml-map/Ch2Step1.jsx`、`Ch2Step2.jsx`、`Ch2Step3.jsx`
- `demo/presentation/src/chapters/ch9-callback/Ch9Step3.jsx`、`Ch9Step4.jsx`、`Ch9Step5.jsx`

### 不動檔案
- `AssetPlaceholder.jsx`、`Sticker.jsx`、`Hero.jsx` 維持原樣（用於未填的 motif shells）
- `Ch1Step1-3`、`Ch1Step8`、`Ch3-Ch8`、`Ch9Step1-2`、`Ch9Step6-13`：不在這次 AI 整合範圍

---

## §6 驗收標準

整合後啟動 `npm run dev`、跑這個 checklist：

### 6.1 視覺驗收（playwright + 人工）

- [ ] ch1 s4 進入時：MRT full-bleed 背景進場、女孩 sticker 從左下 overshoot 砸下、字幕「靈感哪來呢？某天捷運上⋯」從上 slide-in
- [ ] ch1 s5 / s6 / s7 切換：MRT 不閃、不重新解碼、女孩 sticker 跟 flappy / soldier sticker 漸進累積
- [ ] ch2 s1 / s2 / s3 切換：左主視覺（kicker + 大字 + 白話）不變、右側插畫從文字卡 → AI 圖
- [ ] ch9 s3：左卡 cream 底 + AI brain 圖 + 紅高亮「腦科學 RL」label / 右卡 cream 底 + AI neural net 圖 + 「AI 訓練 RL」label / 中央黃「=」stamp 保留
- [ ] ch9 s4：飛機 + 鳥 並置圖中央、HTML SVG 箭頭疊在中央、輕拍翅靜態姿勢
- [ ] ch9 s5：beat 0 顯示 AI brain sticker、beat 1/2 +/- 浮動、beat 3 紅底「跟 AI 訓練一模一樣」hero + climax

### 6.2 風格紅線（無一可違）

- [ ] 沒有任何 `<AssetPlaceholder>` 在這 10 個 step 中殘留（除外：motif shells）
- [ ] 沒有任何 emoji（✈️ 🐦 🧠 🕸️ 🐕 🤝 👕 👖 👔）在這 10 個 step 中殘留
- [ ] 所有 sticker 有 4px 黑邊 + 8px hard shadow + 微旋轉
- [ ] MRT backdrop 無黑邊框、full-bleed
- [ ] ch1 s4-s7 切換 MRT 圖無閃爍 / 無重新解碼（DevTools Network: 只 GET 一次）

### 6.3 無障礙

- [ ] 每個 `<AiSticker>` / `<AiBackdrop>` 都有有意義的 `alt` text
- [ ] `prefers-reduced-motion: reduce` 時、所有 stamp / overshoot 動畫 disable（既有規約、不需新加）

### 6.4 效能

- [ ] 10 張 PNG 總大小 < 3MB
- [ ] DevTools Lighthouse 跑 ch1 / ch2 / ch9：LCP < 2.5s
- [ ] PNG `loading="eager"` for backdrop（ch1 MRT）、`loading="lazy"` for sticker

---

## §7 後續延伸（不在這次範圍）

若這 10 張驗收順利、未來可考慮：
- ch6 s3 新女生 sticker（粉紅）→ AI 路線
- ch7 s7 老油條陷阱題人物 sticker → AI 路線
- ch5 程式碼 sticker → 維持 [✓] 真實檔案（不 AI）
- 更新 [asset-production.md](../../../demo/asset-production.md) 加 `[AI]` 路線、把通過的素材標 `[AI]`

---

## §8 風險與回退

| 風險 | 機率 | 回退策略 |
| --- | --- | --- |
| AI 圖在實際 dev server 視覺不協調 | 低（已通過 §4 驗收） | 單一 step 改回 emoji / placeholder、不整 chapter 回退 |
| MRT backdrop 升到 Ch1.jsx 跨 step 後、step 動畫不再有獨立進場 | 低 | MRT 進場動畫從 Ch1Step4 移到 Ch1.jsx 的 `step === 4` 觸發；後續 step 不重播 |
| `airplane-bird.png` 中央留白不夠、HTML SVG 箭頭蓋不住飛機/鳥 | 中 | 箭頭改用較小 size + 黑底 outline pill 包起來（半透明色塊放箭頭）|
| 黑卡改 cream 卡後、ch9 s3 兩卡視覺對比不夠 | 中 | 加 `border: 6px solid #000` 強化邊框、或左卡保留少量黑帶（如上方 border-top 8px 黑） |
