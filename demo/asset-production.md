# 素材生產手冊（Route D / E / A）

> **配對檔**: [outline.md](outline.md)（敘事 + beat + speaker cue）· [outline-visual.md](outline-visual.md)（視覺 DNA / Motif / Climax）
> **產製策略**: 所有素材依「D / E / A 三路線」分派產製、新增素材必須按決策樹判斷路線
> **基石**: 踩過 v1 火柴人 → v2 道具放大 → v3 背面視角三輪 Route E 迭代後總結——「**多角色互動 + 動態姿態 + 表情**」走 Route E 直接翻車、必須走 Route A

---

## §1 產製路線分類

| 路線 | 用法 | 適用情境 | 工時/張 |
| --- | --- | --- | --- |
| **[D]** 文字隱喻 | HTML + CSS + Neo-brutalism sticker（純文字 + 色塊 + 黑邊 + hard shadow） | 純概念 / 情緒 / 標語 / hero / 角標 / punchline / kicker 字幕 | 2-5 min |
| **[E]** 自製 SVG | Claude 直接生 SVG、可搭 `frontend-design` skill 輔助 | 單一物件 / 對稱結構 / 幾何形狀 / 結構性圖形（曲線、盤面、圓餅、翻牌、階梯） | 10-30 min |
| **[A]** Icon library | phosphoricons.com / lucide.dev 找 icon + Neo-brutalism wrapper | 多角色互動場景 / 人物動作 / 動物 / 設備識別 | 5-15 min |
| **[✓]** 真實素材 | 引用既有檔案 / 截圖 / Pygame visualizer | 程式碼 sticker、tensorboard 真截圖、visualizer iframe | 路徑可指 |
| **[⛔]** 紅線 | 不可挂的素材（偽造截圖、假 logo、假數據顯擺） | 防破口 | — |

**全片預期混合比例**: D ≈ 80% · E ≈ 12% · A ≈ 8% · ✓ 點綴。
**ch 2 全章走 [A]**（三大塊插畫）、**ch 5 全章走 [D]**（情緒崩盤章）、其餘章節混用。

---

## §2 新增素材決策樹

新素材必須**逐題**順問下來：

1. 是「**文字 / 標語 / sticker / hero / kicker / 字幕**」？ → **[D]**
2. 是「**單一物件 + 對稱 / 幾何**」（飛機、星、圓餅、盤面、曲線、翻牌、階梯、漂浮幾何裝飾）？ → **[E]**
3. 是「**多角色互動 / 人物動作 / 動物 / 設備識別**」（老師教學、訓練狗、神經網路、IP 封鎖、大腦）？ → **[A]**
4. 是「**真實檔案 / 截圖 / 既存 demo**」？ → **[✓]** + 路徑
5. 都不是 → **停下來、跟使用者確認**、不要硬塞

### 陷阱題

- **「人 + 道具」場景** → 看主體：**人**主體 = [A]；**道具**主體（人很小退到副位）= [E]
- **「多 sticker 並列」**（4 個考題 grid、3 欄對位）→ 純文字色塊組合 = [D]、即使是 4-N 個
- **「ch 1 漂浮裝飾物」**（黃星 / 紫方塊 / 描邊問號 / 紅圓）→ 單一幾何 = [E]、不是 [D]
- **「符號 +/+/+ 浮動」** → 純 CSS 動畫的符號 = [D] 系（不需要 SVG 結構）

---

## §3 Route E 製作 SOP

每個 [E] 素材依序執行：

1. **避地雷檢查**: 場景含「2+ 角色互動 / 動態姿態 / 臉部表情」之一 → **STOP**、降級到 Route A
2. **構圖分區**: viewBox 切 2-3 個敘事區、共用底線、留呼吸空間
3. **道具優於人物**: 放大語意承載物（黑板、紙、盤面、翻牌、曲線）、縮小人形或避免人形
4. **silhouette 分化**: 若必須有人形、靠 silhouette + 服裝色 + 姿態剪影分化（不靠臉）；優先考慮**背面視角**避開臉
5. **標籤輔助**: 補小型黃黑 sticker 標識身分（「老師 / 學生 / SUPERVISED」）— Neo-brutalism 本來就鼓勵
6. **故事流向**: 箭頭 + 浮動 token + 視線虛線、把因果鏈視覺化
7. **嚴守 web_style.md**: cream `#FFFDF5` 底 / 4px 黑邊 / 8-16px hard offset shadow zero blur / 紅 `#FF6B6B` / 黃 `#FFD93D` / 紫 `#C4B5FD` / Space Grotesk 900
8. **迭代上限**: 截圖人工驗收最多 **2-3 輪**、超過仍認不出 → 降級到 Route A 或 D

---

## §4 Route A 製作 SOP

每個 [A] 素材依序執行：

1. **找 icon**: 去 [phosphoricons.com](https://phosphoricons.com/) 或 [lucide.dev](https://lucide.dev/) 搜關鍵字（中英）、複製 SVG（推薦 Phosphor `regular` weight）
2. **覆寫 stroke**: 把 `stroke="currentColor"` 改 `stroke="#000"`、`stroke-width="4"`（Phosphor 預設 16px 在 256 viewBox、scale 後正好 ~4px、與 Neo-brutalism 邊框 token 一致）
3. **加色塊背景**: icon 外層包一個 Neo-brutalism card：4px 黑邊 + 8px hard shadow + 主色填底（紅 / 黃 / 紫 / cream）
4. **多 icon 並列**: 用「卡片 + 連接箭頭」結構敘事、每張卡內一個 icon + 一個短文字標籤
5. **標籤旋轉**: sticker 標籤微旋轉 ±3°、配 hard shadow
6. **禁忌**: 絕不用 Phosphor `bold` 或 `fill` 風格（線太細 / 太實心、跟 Neo-brutalism 不協調）

### 常用 icon 對應（按本片需求）

| 素材 | Phosphor / Lucide icon |
| --- | --- |
| 老師教學 | `Chalkboard` / `ChalkboardSimple` + `User` |
| 學生抄筆記 | `GraduationCap` + `Notebook` + `Pencil` |
| 折衣服 | `Shirt` + `StackSimple` |
| 訓練狗握手 | `Dog`（Phosphor）+ `Handshake`（Lucide） |
| 房間 / 門 | `Door` |
| IP 封鎖 | `Prohibit` / `ShieldSlash` |
| 大腦 | `Brain` |
| 神經網路 | `GraphBranching` / `Tree` |

**注意 ch 9 飛機+鳥走 [E] 不走 [A]**: 因為要「飛機線稿 + 鳥線稿並列、風格一致」、Phosphor 的 `Airplane` 跟手繪 SVG 線稿混搭會違和、整 step 自製。

---

## §5 各章既有素材清單

> 標註：**[D]** 文字 · **[E]** 自製 SVG · **[A]** icon library · **[✓]** 真實素材 · **[⛔]** 紅線

### §5.0 全域素材（每章共用、僅列一次、規格見 outline-visual.md）

- **[D]+[E]** ambient shapes 4-6 個/章（per [outline-visual.md §6 章節色票統一表](outline-visual.md) + §9.6 規範）
- **[D]+[E]** 章節 tint 背景漸層（per outline-visual.md §6 + §9.1）
- **[E]** 全屏 SVG noise grain（per outline-visual.md §9.2）
- **[E]** 動態 halftone 漂移（per outline-visual.md §9.4）
- **[D]+[E]** Beat indicator 隱藏式底部 88 方塊條（per outline-visual.md §9.5）
- **[D]** View Transitions API 章節 cross-fade（per outline-visual.md §9.3）

### §5.1 章節素材

#### 1. coldopen（~10 個素材）

- **[D]** 「**心 虛**」巨字 sticker（純 CSS）+ 黃色「期中報告」角標
- **[D]** 「**心理學系**」card + 紅箭頭 + 黃底「敬請期待」高亮
- **[D]+[E]** 「**訓 練 AI 解 數 獨**」hero（[D] text-stroke 樣式 + 紅黃 box）+ **[E]** 4 漂浮裝飾物（紫方塊 / 黃星 / 紅圓 / 描邊問號）
- **[E]** 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop、結構性 SVG）+ 多層 depth
- **[D]** 4 張靈感串聯 sticker（正妹 / Code Bullet flappy bird / 沒手機解數獨 / 訓練 AI 解數獨）
- **[E]+[D]** BOOM 雙圈爆破動畫（[E] 黃外圈 + 紅內圈幾何）+ **[D]** punchline 黃底高亮

#### 2. ml-map（整章走 [A]，~6 個素材）

- **[A]** **三大塊插畫**（抄筆記 / 折衣服 / 訓練狗握手）— 從 Phosphor 取 `Chalkboard + User`、`Shirt + StackSimple`、`Dog`，套 Neo-brutalism wrapper（卡片 + 連接箭頭結構）
- **[D]** AlphaGo 標籤 sticker（**文字 sticker、不挂真實 logo 或圍棋盤照片**）
- **[D]** kicker 切換動畫「①/②/③」
- **[D]** cliffhanger 黃底問號 sticker（問號 720° 旋轉）

#### 3. llm-vs-rl（~5 個素材）

- **[D]** split-screen 60/40 對比版型（純 CSS layout）
- **[D]** 中央 VS 大字 sticker + 紅底/黃底 stamp 對比
- **[A]** 房間 / 門 SVG icon — Phosphor `Door`
- **[E]** 背景文字流動效果（低密度文字 grid 微動、結構性）

#### 4. data-hunt（~7 個素材）

- **[D]** Kaggle 標籤 sticker（**文字 sticker、不挂 Kaggle 真 logo**）+ 多張資料 card 浮現
- **[D]** 「supervised 路線拒絕」紅 stamp（旋轉、stamp-in）
- **[D]** websudoku URL sticker「**這個受害者**」（純文字 mono + 紅標籤 + cursor 閃爍）
- **[D]+[A]** 「20 題就被封 IP」紅警示（[D] 文字 + [A] Phosphor `Prohibit` 封鎖圖示）
- **[E]** **proxy 池視覺化**：30+ IP 小卡 grid 漂浮 + 隨機切換動畫（結構性陣列）

#### 5. legacy（整章走 [D]，除程式碼 sticker 走 [✓]，~6 個素材）

- **[✓]** **`legacy/app/sudoku/torch_agent.py` 真實檔案 838 行** — 直接讀檔做程式碼 sticker、count-up 角標 838
- **[D]** prompt 對話框「**幫我寫一個訓練 AI 解數獨的程式**」sticker
- **[D]** 「**⋯⋯結果我錯了**」獨立崩盤句 sticker
- **[E]** 紅色叉叉 burst 動畫（chaotic spawn、幾何粒子）
- **[D]** 第一件學到 hero + 4 個關鍵詞黃底高亮 stagger

#### 6. sb3（~8 個素材）

- **[D]** 「**社群現成 Python 工具箱**」標籤 + 「**填對一格 · 給分**」計分表 hero
- **[D]+[E]** 「剛認識的新女生」sticker（[D] 粉紅 + 微旋轉文字）+ **[E]** 「+/+/+」加分動畫（符號浮動、純 CSS 也可走 [D]）
- **[E]** SVG 曲線爬升（stroke-dasharray draw）→ 卡平段紅 highlight band
- **[D]** 新女生 sticker grayscale 漸變（CSS filter）
- **[D]** **「備胎」FINAL stamp sticker**（紅、超大、微旋轉、16px shadow）
- **[D]** 「**偷吃步**」紅 stamp + 「**找漏洞作弊**」hero（紅 + 黃雙色強調）
- **[⛔]** **禁挂偽造 tensorboard 截圖**（曲線一律 SVG 概念示意）

#### 7. reasoner（~10 個素材、章節最 dense）

- **[E]** **13 招大階梯**（13 個技巧 sticker 結構性堆疊、X-Wing 跟 XYZ-Wing 最大；技巧名清單從 `reasoner/solver/techniques/` 取真實檔名）+ hover tooltip
- **[D]+[E]** 「舊作法 vs 新作法」split-screen 對比動畫（[D] 文字 sticker + [E] mini 盤面）+ 多招亮 + 分數浮動
- **[E]** 9×9 mini 盤面 + 填數字綠 + 劃掉紅斜線 loop 動畫（純結構性 SVG）
- **[D]** 「**兩千多萬次**」count-up + 「**0**」紅底超大字 hero
- **[D]** **戀愛 hook b 陷阱題 sticker**：「**和你媽掉進水裡你會先救誰**」「**該不該運動**」（含兩答案都錯 ❌ 箭頭）+ hover 互動
- **[D]** 死結 cinematic 黑底 hero + 反向思考 footer 鋪墊
- **[⛔]** **禁挂 `TECH_BONUS` 整張數值表 / `net_arch` / `SubprocVecEnv` 等字串**（假數據顯擺反例）

#### 8. apprentice（~8 個素材）

- **[D]** 「**反向思考**」hero + 紅底高亮
- **[E]** 9×9 數獨盤面（黑邊 + cream 格子 + Space Grotesk 700 數字、90% 已填、3 空 highlight）
- **[E]** 反向課程動畫：3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 空（連續一格一格擦掉 + 計數器 count-up、對齊 script「再加一格、再加一格」口語）
- **[E]** **「+20 → +50」3D flip 翻牌動畫**（紅 → 黃、shadow 加深）
- **[D]+[E]** 「光講不夠看」hero（[D] 文字 + [E] 向下大箭頭 stroke-draw + bounce）
- **[D]** **visualizer 大按鈕**（cream 底 + 粗黑邊 + 強陰影 + accent red 字、微旋轉、hover scale + shadow 加深、`href="sudoku-demo:run"`）
- **[✓]** **`apprentice/demo/visualize.py` 桌面 pygame 視窗** — 透過 Windows custom URL scheme `sudoku-demo:` 自動啟動
- **[✓]** **`demo/visualizer-launch/` 一鍵啟動套件**（install.bat / uninstall.bat / launcher.bat / requirements-demo.txt / README.md）— 所有 .bat 自動偵測 `sudoku_old/` 根目錄、portable 到任何 Windows 機器

#### 9. callback（~14 個素材、章節第二 dense）

- **[D]** cinematic hero「**AI 也在訓練我**」大字 mask reveal + letter-spacing 收緊 + 紅底 flash
- **[✓]** **tensorboard 真實截圖**（success_rate 曲線 + curriculum target_empty 圖）— 使用者匯出至 `demo/presentation/public/images/tensorboard/`、**整片唯一可挂真截圖的地方**
- **[D]+[A]** 「腦科學 RL = AI RL」split + 「**=**」大字 stamp（[D] split layout + [A] Phosphor `Brain` 大腦 icon + `GraphBranching` 神經網路 icon、黃底圓 sticker `=`）
- **[E]** 飛機 + 鳥 並置 sticker（自製黑線稿 + 黃填充、輕微振翅；**因要風格一致、不用 Phosphor**）
- **[D]+[A]+[E]** 戀愛 a 雙欄：[E] 「+/+/+」「-/-/-」浮動符號 + [A] 中央大腦 sticker（Phosphor `Brain`）+ [D] 紅底「跟 AI 一模一樣」hero
- **[D]** 戀愛 b 4 個魔王考題 sticker grid（2×2）+ hover 互動（純文字色塊）
- **[D]** plasticity 三欄對位 sticker（AI 解數獨 / 出生講話 / 跟人相處）→ 中央「**一樣**」snap
- **[D]** plasticity 機制 hero「每次都把我們重新塑造一次」+ 三項 stagger
- **[E]+[D]** **MBTI 圓餅視覺**（[E] 0% → 100% I 填滿幾何）+ **[D]** 「極度 I 人」紫色標籤 sticker（script.md L359 verbatim）
- **[D]+[E]** **業務工作 sticker**（[D] 文字）+ **[E]** I → E 漸變條（水平 indicator 動畫）
- **[D]** **警語 sticker「人生第一次的外向 · 換來一輩子的內向」**（cream 底、accent red 大字、6px 紅邊、20px shadow、微旋轉、超大）
- **[D]** 「**不被挫敗給擊敗**」職場祝福 hero（紅底高亮）
- **[D]** 「**薪水小偷**」對位 sticker
- **[D]** **「電費小偷」FINAL 超大字 sticker**（accent red 底、6px 黑邊、16px hard shadow、微旋轉、整片最強 reveal、stamp + shadow burst + `motif/boom-double-ring` 圍邊）
- **[D]** 「— END —」minimal footer

**全片總計**: ~74 個章節素材 + 6 個全域素材 = **~80 個素材**。

---

## §6 File Naming Convention

### 目錄結構

```
demo/presentation/
├── src/
│   ├── chapters/
│   │   ├── ch1-coldopen/
│   │   │   ├── Ch1Step1.tsx          # step 1 主元件
│   │   │   ├── Ch1Step2.tsx
│   │   │   ├── ...
│   │   │   └── assets/                # 章節私有素材
│   │   │       ├── boom-double-ring.svg
│   │   │       └── mrt-window.svg
│   │   ├── ch2-ml-map/
│   │   └── ...
│   ├── motifs/                        # 跨章節 motif 共用 component
│   │   ├── BoomDoubleRing.tsx
│   │   ├── CrashLine.tsx
│   │   └── ...
│   ├── climax/                        # Climax FX A-G
│   │   ├── ScreenShake.tsx
│   │   ├── HalftoneBurst.tsx
│   │   └── ...
│   ├── tokens/                        # 設計 token
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   └── shared/                        # 共用 component
│       ├── ProgressBar.tsx
│       ├── ChapterNav.tsx
│       └── PresenterPanel.tsx
└── public/
    └── images/
        ├── tensorboard/               # ch9 s1 真截圖
        │   ├── success-rate.png
        │   └── curriculum-target-empty.png
        └── code-walls/                # ch5 s2 程式碼截圖
            └── torch-agent-838.png
```

### 命名規約

| 類型 | 命名格式 | 範例 |
| --- | --- | --- |
| Step component | `Ch<N>Step<M>.tsx` (PascalCase) | `Ch6Step6.tsx` |
| Motif component | `<MotifName>.tsx`（PascalCase、無 `motif/` 前綴） | `RedStamp.tsx` |
| Climax FX | `<ClimaxLetter><Name>.tsx` | `AScreenShake.tsx` |
| SVG asset | `<short-name>.svg`（kebab-case） | `mrt-window.svg` |
| 章節私有 SVG | `chapters/ch<N>-<name>/assets/<short>.svg` | `chapters/ch1-coldopen/assets/sticker-girl.svg` |
| 真實截圖 | `public/images/<category>/<descriptive>.png` | `public/images/tensorboard/success-rate.png` |

---

## §7 素材完工驗收 Checklist

### 通用驗收（所有路線）

- [ ] 一眼能認出該素材代表的「敘事意義」（不需配文字解釋）
- [ ] 嚴守 [web_style.md](web_style.md) Neo-brutalism DNA：cream 底 / 4-6px 純黑邊 / 8-16px hard offset shadow zero blur / 微旋轉 ±3°~4°
- [ ] 色票限 `#FFFDF5` / `#000000` / `#FF6B6B` / `#FFD93D` / `#C4B5FD` / `#FFFFFF`、不引入新色
- [ ] 字體 Space Grotesk 700/900（Latin）+ Noto Sans SC 700/900（中文）
- [ ] 不違反設計禁忌：無 blur > 4px、無圓角中段、無紫粉漸變、無軟陰影

### [D] 文字 sticker 驗收

- [ ] 字級對齊 [outline-visual.md §1.5 Typography Scale](outline-visual.md)
- [ ] 內邊距使用 spacing scale 規範值（8/12/16/24px）
- [ ] 微旋轉以 `rotate-1` / `-rotate-2` / `rotate-3` 三檔之一
- [ ] hover 互動實作 push/lift 效果（per web_style.md 機制）

### [E] 自製 SVG 驗收

- [ ] viewBox 為固定 600×360（除特殊案例如 13 招階梯走 800×500）
- [ ] 所有 stroke 統一 4px、`stroke="#000"`、`stroke-linejoin="miter"`（鋭角）
- [ ] 無 inline style、所有屬性走 SVG attribute（`fill="#FF6B6B"` not `style="fill:..."`）
- [ ] 通過 SVGO 壓縮、確保無 `<metadata>` / `<defs>` 冗餘
- [ ] 截圖人工驗收 2-3 輪內過關、否則降級

### [A] Icon library wrapper 驗收

- [ ] 從 phosphoricons.com 或 lucide.dev 取 `regular` weight
- [ ] 覆寫 `stroke="#000"`、`stroke-width="4"`
- [ ] 包 Neo-brutalism card（4px 黑邊 + 8px hard shadow + 主色背景）
- [ ] 多 icon 並列用「卡片 + 連接箭頭」結構、非自由排列

### [✓] 真實素材驗收

- [ ] 程式碼 sticker：直接從 repo 讀檔（不複製貼上、避免漂移）
- [ ] 真實截圖：放 `public/images/<category>/`、檔名 kebab-case
- [ ] 截圖周圍加 Neo-brutalism 框（6px 黑邊 + 12px shadow）統一視覺
- [ ] 截圖 alt text 清楚（無障礙）

### [⛔] 紅線清單（絕對不可挂）

- [ ] 偽造 tensorboard 截圖、假數據顯擺曲線
- [ ] 真實 logo（Kaggle / AlphaGo / Code Bullet / OpenAI / Anthropic）— 一律用文字 sticker 替代
- [ ] `TECH_BONUS` 數值表、`net_arch` config、`SubprocVecEnv` 等 SB3 / 程式內部字串
- [ ] 帶水印 / 版權問題的 stock photo
