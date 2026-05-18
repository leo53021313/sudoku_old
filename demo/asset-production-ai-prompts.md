# AI 圖片生成提示詞清單

> **狀態**：v1 的 10 張已通過驗收並整合進 [demo/presentation/](presentation/)（commit `a00edb9` ~ `30a3d97`、`79f2327` polish）
> **用途**：給 GPT Image 2 / Nano Banana 2（Gemini 3 Pro Image）用的 prompt
> **流程**：你拿這份 prompt 去生圖 → 存進 `demo/asset-experiments/` → 通過驗收後搬到 `demo/presentation/public/images/ai/ch<N>/` 並整合進對應 step
> **v2 延伸**：[§6 延伸：ch6/ch7 戀愛 hook 人物 sticker](#6-延伸ch6ch7-戀愛-hook-人物-sticker)

---

## §1 為什麼這份清單跟原本 D/E/A 路線不同？

原本 [asset-production.md §1](asset-production.md) 把 80% 走 [D] 文字 sticker、12% [E] 自製 SVG、8% [A] icon library。AI 圖片生成不是要全面取代、而是專門攻三類「D/E/A 都不夠好」的甜蜜點：

| AI 強項 | 為什麼 D/E/A 不好用 |
| --- | --- |
| 複雜人物場景（老師教學、軍人解數獨、訓練狗握手） | [A] Phosphor icon 太簡單拼湊、[E] 自製人物會崩（已踩過 v1 火柴人 → v3 背面視角三輪雷） |
| 有氛圍 / 透視的背景（捷運車廂、窗外景色） | [E] 純幾何 SVG 缺氛圍、[A] 無對應 icon |
| 需風格一致的角色 sticker（正妹、軍人、youtuber） | [D] 純文字 sticker 沒有人物識別感、不夠生動 |

### AI 圖片**不該**做的素材（維持原路線）

- **任何含中文 / 英文文字的素材** → AI 文字輸出極不可靠、文字一律用 [D] 在前端疊上去
- **精確幾何**（9×9 數獨盤面、MBTI 圓餅圖、SVG 曲線、13 招大階梯）→ 維持 [E]
- **需動畫 / 互動的元素**（翻牌、scale 動畫、hover）→ 維持 [E] / [D]
- **真實截圖**（tensorboard、torch_agent.py code wall）→ 維持 [✓]
- **品牌標籤**（Kaggle / AlphaGo / Code Bullet 文字 sticker）→ 維持 [D]、絕不挂真 logo
- **單純幾何 sticker**（漂浮黃星 / 紫方塊 / 描邊問號）→ 維持 [E]

---

## §2 候選素材總表

| # | 代號 | 用途位置 | 原路線 | 改 AI 後預期 | 優先度 |
| --- | --- | --- | --- | --- | --- |
| 1 | `ch1-mrt-window` | ch1 s4-7 捷運背景 | [E] 紫底窗 + 車廂線條 | 真實透視 + 窗外光景、敘事感增強 | ★★★ |
| 2 | `ch1-girl-daydream` | ch1 s4 正妹 sticker | [D] 黃底文字「正妹發呆中」 | 真實人物剪影、與捷運背景融合 | ★★★ |
| 3 | `ch1-codebullet-flappy` | ch1 s5 Code Bullet sticker | [D] 紫底文字「Code Bullet · flappy bird」 | youtuber + 鳥 + 管子場景、視覺梗 | ★★ |
| 4 | `ch1-soldier-sudoku` | ch1 s7 沒手機 sticker | [D] 紅底文字「沒手機·解數獨」 | 軍人坐著解報紙數獨、共鳴感 | ★★ |
| 5 | `ch2-teacher-notes` | ch2 s1 supervised 插畫 | [A] Phosphor `Chalkboard + User` | 老師指黑板 + 學生抄筆記、課堂感 | ★★★ |
| 6 | `ch2-folding-clothes` | ch2 s2 unsupervised 插畫 | [A] Phosphor `Shirt + StackSimple` | 衣服按顏色分三疊、整理感 | ★★ |
| 7 | `ch2-dog-handshake` | ch2 s3 RL 插畫 | [A] Phosphor `Dog` + Lucide `Handshake` | 人蹲下伸手 + 狗給掌、互動瞬間 | ★★★ |
| 8 | `ch9-airplane-bird` | ch9 s4 飛機+鳥並置 | [E] 自製黑線稿 | 兩物件 side-by-side 線稿、輕振翅 | ★★ |
| 9 | `ch9-brain-reward` | ch9 s5 中央大腦 sticker | [A] Phosphor `Brain` + 內部紫色 reward 浮動 | 大腦剖面 + 內部 +/- token、概念化 | ★ |
| 10 | `ch9-neural-network` | ch9 s3 AI RL 側 icon | [A] Phosphor `GraphBranching` | 節點 + 連線、抽象但有結構 | ★ |

**建議優先測試**：★★★ 三項 + ★★ 五項 = 共 8 個。若 ★★★ 都不夠好就棄、若 ★★★ 都過關再決定是否擴張。

---

## §3 共用風格前綴（每個 prompt 都套這段）

> 把這段「共用前綴」放在每個 prompt 開頭、再接該素材專屬描述。AI 生圖時建議全段一次貼。

### English (推薦：GPT Image 2 / Nano Banana 2 對英文 prompt 最穩定)

```
Neo-brutalism illustration in DIY zine / punk poster aesthetic.
Hand-drawn black ink outlines, 4-6 pixel thick uniform stroke weight, no anti-aliasing softness.
Flat color fill only — NO gradients, NO blur, NO photorealism, NO 3D rendering, NO drop shadows with blur.
Limited palette: cream background #FFFDF5, pure black #000000 outlines, hot red #FF6B6B, vivid yellow #FFD93D, soft violet #C4B5FD. Use 2-3 of these colors max per image.
Hard-edged offset shadow blocks at 45-degree bottom-right angle in solid black, zero blur radius.
Composition: single focal subject, asymmetric placement, slight rotation feel (sticker-on-laptop vibe).
Style references: Keith Haring line work + 1990s zine cutouts + risograph print + Bauhaus poster.
NO text, NO words, NO letters, NO numbers, NO captions — pure visual only (text will be overlaid in HTML afterward).
Aspect ratio: 4:3 (1200×900) unless specified otherwise.
```

### 中文版（備用、若要本地化）

```
Neo-brutalism 風格插畫、DIY zine / punk poster 美學。
手繪黑色墨線輪廓、4-6 像素粗細均勻、無 anti-alias 柔化。
僅使用平塗色彩——絕無漸層、絕無模糊、絕無寫實照片、絕無 3D 渲染、絕無柔邊陰影。
有限色票：cream 底色 #FFFDF5、純黑 #000000 線條、亮紅 #FF6B6B、鮮黃 #FFD93D、淡紫 #C4B5FD。每張圖最多用 2-3 色。
硬邊偏移陰影色塊、45 度右下方向、純黑、零模糊半徑。
構圖：單一聚焦主體、非對稱擺放、有「貼紙感」的微旋轉氛圍。
風格參考：Keith Haring 線條 + 1990 年代 zine 剪貼 + risograph 印刷 + Bauhaus 海報。
不要文字、不要任何字母 / 數字 / 標題（文字會在 HTML 中後製疊上）。
比例：4:3（1200×900）除非另註。
```

---

## §4 個別素材 prompt（10 個）

---

### 1. `ch1-mrt-window` 捷運車廂窗景

**用途**：[ch1 step 4-7](outline.md) 「靈感哪來呢？某天捷運上⋯」過場 + 後續三 sticker 的背景底襯
**原路線**：[E] 紫底窗 + 黑邊、車廂線條 backdrop、結構性 SVG
**比例**：16:9 寬背景（1920×1080）
**重點**：要當「背景襯底」用、不能搶 sticker 焦點 → 物件要少、留 1/3 中央空白給 sticker 疊

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: Interior of a Taipei MRT (metro) subway carriage from passenger's eye-level point of view. Long perspective view down the carriage corridor with parallel seats on left and right. Large rectangular windows on both sides showing abstract motion-blurred outside scenery (suggest urban tunnel walls speeding by, using soft violet #C4B5FD streaks but kept FLAT, not blurred).
Composition: deep one-point perspective vanishing into the back of the carriage. Empty handrail loops hanging from the ceiling. Floor with parallel lines. Cream background dominates, black ink outlines define all structural elements, violet used only for the window glass tint.
Mood: calm, contemplative, slightly nostalgic — the "daydreaming on a train" feeling.
Aspect ratio: 16:9 wide background, leave the center 30% relatively sparse so foreground sticker characters can be overlaid later in HTML.
```

**驗收**：一眼看出「捷運車廂內、有窗、有縱深」、中央留白足夠疊角色 sticker。

---

### 2. `ch1-girl-daydream` 正妹發呆 sticker

**用途**：[ch1 step 4](outline.md) 「正大光明看著正妹發呆」第一張角色 sticker、放捷運背景左下
**原路線**：[D] 黃底文字 sticker「正妹發呆中」
**比例**：1:1 sticker（800×800）、透明背景或 cream 底
**重點**：角色要 friendly / harmless、避開「物化女性」陷阱、純粹「車廂裡發呆的乘客」感

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A young woman with shoulder-length black hair sitting on an MRT subway seat, viewed from a 3/4 side angle, hands folded on her lap, gazing softly out the window. Casual outfit — plain top (vivid yellow #FFD93D fill) and dark pants. Slightly thoughtful, neutral facial expression — eyes half-lidded, lips relaxed. Simple, kind, NOT sexualized.
Style: bold black ink outline character only, no scene background (cream #FFFDF5 plain backdrop). Character takes up 70% of canvas height, centered.
Treat as a sticker — single subject, clean cutout silhouette, suitable for placing on top of another image.
Aspect ratio: 1:1 square.
```

**驗收**：人物表情自然 / 無不適感、輪廓可清楚剪下當 sticker 用、衣服色票符合 #FFD93D。

---

### 3. `ch1-codebullet-flappy` Code Bullet × Flappy Bird sticker

**用途**：[ch1 step 5](outline.md) 「腦袋冒出 Code Bullet flappy bird」第二張思考氣球 sticker
**原路線**：[D] 紫底文字「Code Bullet · flappy bird」純文字
**比例**：1:1 sticker（800×800）
**重點**：要讓人秒看出「youtuber 寫 AI 玩 flappy bird」這個梗、但不能挂真實 logo

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A cartoon scene showing a generic male figure (silhouette, back-view, sitting at a desk with a laptop) controlling a small chunky bird character. The bird is a stylized 8-bit-ish chunky bird in vivid yellow #FFD93D, flying between two green pipes (use soft violet #C4B5FD instead of green to stay in palette). The scene suggests "person teaching computer to play a video game".
Composition: split layout — laptop user on the left 40%, bird-and-pipes mini game scene on the right 60%, with a dashed arrow line connecting laptop screen to the game scene (suggests "controlled by code").
Background: cream #FFFDF5 plain.
Aspect ratio: 1:1 square.
```

**驗收**：能認出「人 → 寫程式 → 操控 flappy 風格鳥」、不挂真 logo、色票對。

---

### 4. `ch1-soldier-sudoku` 軍人沒手機解數獨 sticker

**用途**：[ch1 step 7](outline.md) 「當兵沒手機解數獨」第三張 sticker
**原路線**：[D] 紅底白字「沒手機·解數獨」
**比例**：1:1 sticker（800×800）
**重點**：要有「百無聊賴 / 軍營」氛圍、不能畫真實軍裝細節（避法律 / 識別問題）、用「光頭 + 簡化制服」剪影即可

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A young man with a shaved buzz-cut head, wearing a plain olive-green simplified uniform top (use hot red #FF6B6B to stay in palette, NOT realistic green), sitting cross-legged on the floor, leaning against a wall, holding a folded newspaper and a pencil, frowning slightly at a Sudoku puzzle. Bored, idle posture.
Detail: the newspaper shows a 9×9 grid (just the grid lines, NO numbers written — text will be overlaid later). A simple wall-clock or bunk bed silhouette in the background hints at "barracks / military service".
Style: bold black outlines, flat fills only, character takes 65% of canvas.
Background: cream #FFFDF5.
Aspect ratio: 1:1 square.
```

**驗收**：能認出「軍人在解報紙數獨、無聊」、不違反軍裝管制、grid 是空的（文字後製）。

---

### 5. `ch2-teacher-notes` 老師教學 + 學生抄筆記

**用途**：[ch2 step 1](outline.md) supervised 三大塊第一塊
**原路線**：[A] Phosphor `Chalkboard + User`、卡片 + 連接箭頭結構
**比例**：4:3 橫向（1200×900）
**重點**：要清楚表達「老師指著黑板、學生在寫」這個 supervised 隱喻、雙人互動是 AI 強項

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A classroom scene with two figures. LEFT: a teacher figure (shoulder-up + extended arm), standing beside a large chalkboard, pointing at the board with a pointer stick. The chalkboard is filled with abstract geometric marks and symbols (NO actual letters or numbers — just dashes, dots, lines, circles). RIGHT: a student figure (head + shoulders + hands), seated, hunched over an open notebook, holding a pencil and writing.
Color blocking: teacher's outfit hot red #FF6B6B fill, chalkboard soft violet #C4B5FD fill, student's outfit vivid yellow #FFD93D fill, notebook page plain cream.
Composition: 50/50 left-right split, both characters face center (slight 3/4 angle). Bold black ink outlines define everything.
Mood: focused, instructive, like a 1980s educational poster.
Aspect ratio: 4:3 horizontal.
```

**驗收**：能秒認出「老師 → 學生抄筆記」、無真實文字、色塊分明。

---

### 6. `ch2-folding-clothes` 折衣服分顏色

**用途**：[ch2 step 2](outline.md) unsupervised 三大塊第二塊
**原路線**：[A] Phosphor `Shirt + StackSimple`
**比例**：4:3 橫向（1200×900）
**重點**：要表達「混亂衣堆 → 分顏色三疊」的「自動分類」概念、可省略人物聚焦衣服

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A clothes-folding scene with a clear before/after split. LEFT 40%: a chaotic messy pile of mixed t-shirts (3 colors: hot red #FF6B6B, vivid yellow #FFD93D, soft violet #C4B5FD), tangled and overlapping. A large bold black arrow points from left to right in the middle. RIGHT 60%: three NEATLY folded stacks of t-shirts, one stack per color, arranged in a row — red stack, yellow stack, violet stack, each as a clean rectangular pile with bold black outlines suggesting "folded edges".
Composition: clearly tells the story "mess → sorted by color". NO human figure needed (focus on the clothes / system).
Background: cream #FFFDF5.
Aspect ratio: 4:3 horizontal.
```

**驗收**：左混亂、右分三疊、箭頭明確、無文字。

---

### 7. `ch2-dog-handshake` 訓練狗握手

**用途**：[ch2 step 3](outline.md) RL 三大塊第三塊
**原路線**：[A] Phosphor `Dog` + Lucide `Handshake`
**比例**：4:3 橫向（1200×900）
**重點**：「人蹲下 + 狗給掌」的經典 RL 訓練畫面、互動瞬間是 AI 強項、可選擇加一個獎勵 token（餅乾 / 骨頭）

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A classic dog-training scene. LEFT: a person crouching down on one knee, side view, extending their left hand forward, palm open. RIGHT: a small to medium-sized dog (cartoon style, perky ears, sitting on its haunches), lifting its right front paw to meet the person's hand — the paw-handshake moment captured. ABOVE the dog: a small floating treat / biscuit shape with a sparkle / star indicating "reward".
Color blocking: person's outfit hot red #FF6B6B fill, dog's body vivid yellow #FFD93D fill with black outline details, the floating treat soft violet #C4B5FD.
Composition: 50/50 left-right, both facing each other, the meeting paw-and-hand is the focal point in the center.
Mood: warm, simple, clearly tells "reward shapes behavior" story.
Aspect ratio: 4:3 horizontal.
```

**驗收**：人+狗握手畫面清楚、有 reward token、無文字、可愛但不卡通膩。

---

### 8. `ch9-airplane-bird` 飛機 + 鳥 並置線稿

**用途**：[ch9 step 4](outline.md) 「AI 在模仿人類 · 就像飛機是人類模仿鳥」
**原路線**：[E] 自製黑線稿（飛機 + 鳥並置、黃填充）
**比例**：16:9 橫向（1600×900）
**重點**：兩個物件 side-by-side、風格一致是關鍵、給 AI 生比 Phosphor 取現成 icon 更能保證一致

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: Two iconic flying objects side by side, drawn in the EXACT same flat illustration style. LEFT 50%: a stylized small bird in flight (side profile, wings spread, suggesting flapping motion with one wing slightly up and one slightly down), bold black outline, vivid yellow #FFD93D body fill. RIGHT 50%: a small propeller airplane (side profile, classic biplane or Cessna silhouette, also side view, wings horizontal), bold black outline, vivid yellow #FFD93D body fill. Both fly LEFTWARD (so the bird faces left, the plane faces left).
Both subjects are roughly the same on-canvas size and at the same vertical height.
Background: cream #FFFDF5 plain. The bird should clearly be on the left (the "original"), the plane clearly on the right (the "imitation"). NO arrow between them (an arrow will be added in HTML later).
Mood: educational diagram, "biomimicry" feeling.
Aspect ratio: 16:9 horizontal.
```

**驗收**：兩物件大小一致、線條粗細一致、色票一致、左右排列清楚、無連接箭頭（後製）。

---

### 9. `ch9-brain-reward` 大腦 + reward token

**用途**：[ch9 step 5 beat 1](outline.md) 戀愛 a 雙欄中央 sticker
**原路線**：[A] Phosphor `Brain` + 內部紫色 reward 漂浮
**比例**：1:1 sticker（800×800）
**重點**：大腦剖面（不是寫實腦科書那種、是 punk zine 風格）+ 內部浮動 + / - token、概念化

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A stylized side-view of a human brain, simplified to its essential lobe silhouette with a few bold internal fold lines (think Keith Haring brain icon, NOT medical anatomy). The brain outline is bold black, the brain body is filled with cream #FFFDF5 (so internals are visible). INSIDE the brain area, scatter 5-7 small floating tokens: alternating "+" plus-signs in hot red #FF6B6B and "-" minus-signs in soft violet #C4B5FD, each as a small circular badge with thick black outline. Tokens float at slight rotations, suggesting movement.
Composition: brain centered, takes 75% of canvas. Background cream.
Mood: conceptual, suggests "reward and punishment shaping the mind".
Aspect ratio: 1:1 square.
```

**驗收**：大腦輪廓 stylized 不寫實、內部能看到 +/- token、色票對。

---

### 10. `ch9-neural-network` 神經網路抽象插畫

**用途**：[ch9 step 3](outline.md) 「AI 訓練 RL」側、跟大腦 sticker 配對
**原路線**：[A] Phosphor `GraphBranching` / `Tree`
**比例**：1:1 sticker（800×800）
**重點**：要跟同 step 的大腦 sticker（#9）視覺平衡、結構感重於寫實

**Prompt (English)**:
```
[Paste shared style prefix above]

Subject: A stylized illustration of a simple feed-forward neural network. 4 vertical columns of circular nodes from left to right: column 1 has 3 nodes (input), column 2 has 5 nodes (hidden), column 3 has 5 nodes (hidden), column 4 has 2 nodes (output). All nodes are bold black-outlined circles filled with cream #FFFDF5. Every node in one column connects to every node in the next column via thin black lines (creating a dense web). Highlight a few connection lines in hot red #FF6B6B and a few node fills in vivid yellow #FFD93D to suggest "active signal flow".
Composition: network fills 80% of canvas, centered. Symmetric vertical layout.
Mood: technical-but-friendly, like an infographic from a children's science book.
Aspect ratio: 1:1 square.
```

**驗收**：能秒看出「神經網路」結構、節點+連線清楚、跟 #9 大腦 sticker 在風格上能成對。

---

## §5 後續決策流程

1. **拿這份 prompt 去 GPT Image 2 / Nano Banana 2 跑** — 建議先跑 ★★★ 三項（`ch1-mrt-window` / `ch1-girl-daydream` / `ch2-teacher-notes` / `ch2-dog-handshake`）
2. **截圖貼回對話 / 存 `demo/asset-experiments/`** — 我可以幫你比對「AI 版 vs 原 D/E/A 版」哪個更貼合 Neo-brutalism DNA
3. **過關的素材**：再回頭改 [asset-production.md](asset-production.md) 加 `[AI]` 路線、把對應素材標 `[AI]` + 紀錄 prompt 連結
4. **不過關的素材**：直接丟棄、維持原 D/E/A 路線

### 驗收紅線（任何 AI 圖出來如果踩到一條就要重生 or 棄）

- [ ] 圖中有「亂碼文字 / 偽中文 / 偽英文字母」→ 棄（這是 AI 圖最常見失敗）
- [ ] 出現 cream / 黑 / 紅 / 黃 / 紫以外的雜色 → 重生（明確要求 limited palette）
- [ ] 有 gradient / blur / 寫實光影 / 3D 渲染 → 重生（不符 Neo-brutalism）
- [ ] 線條粗細不一致 / 沒有黑邊 → 重生（核心 DNA 是 bold black outline）
- [ ] 人物表情怪 / 比例詭異 → 看情況、若超過 2 輪修不好就降回 [A] icon library

### 工時對比預估

| 路線 | 工時/張 | 一致性風險 | 適合範疇 |
| --- | --- | --- | --- |
| [D] 文字 | 2-5 min | 極低 | 純概念、純文字 |
| [E] 自製 SVG | 10-30 min | 中（人物易崩） | 幾何、結構 |
| [A] icon library | 5-15 min | 低（icon set 風格固定） | 簡單物件 |
| **[AI] 圖片生成** | **3-10 min/張 + 0-3 輪 retry** | **中（風格漂移、要 prompt 鎖死）** | **複雜場景、人物互動、有氛圍背景** |

預期 AI 路線總工時：10 張 × ~15 分鐘（含 retry）= **~2.5 小時** 可拿到全套素材。

---

## §6 延伸：ch6/ch7 戀愛 hook 人物 sticker

> **狀態**：v2 提案、待你生圖
> **挑選依據**：v1 ★★★ 全套驗收通過後、把同個 AI 路線擴張到全片 2 個最重要的「戀愛 hook」笑點 character sticker（[outline.md](outline.md) 紀錄為 motif/girl-new、motif/girl-veteran、跨章節復用）

### §6.1 候選素材總表（新增 2 個）

| # | 代號 | 用途位置 | 原路線 | 改 AI 後預期 | 優先度 |
| --- | --- | --- | --- | --- | --- |
| 11 | `ch6-girl-new` | ch6 s3 戀愛 hook a「剛認識的新女生」+ ch9 s5 callback 灰階退背景 | [D] 粉紅 #FFB6C1 文字 sticker「剛認識的新女生 ✨」 | 鮮活角色插畫、初遇期亢奮、灰階退背景時仍可辨識為「同一個女生」 | ★★★ |
| 12 | `ch7-girl-veteran` | ch7 s7 老油條陷阱題 hook + ch9 s6 callback 4 魔王考題 sticker grid | [D] 紅/紫文字陷阱題 sticker（2 個）+ ❌ 答案 sticker | 帶眉挑/微笑的「老油條」角色、暗示「她在設陷阱」、跟 girl-new 視覺呼應但氣質截然不同 | ★★★ |

**敘事對比**（同一段「戀愛比喻 AI」故事的兩段）：

| 比較 | girl-new（ch6 s3） | girl-veteran（ch7 s7） |
| --- | --- | --- |
| 階段 | 剛認識、初遇期 | 已交往一陣、進入挑戰期 |
| 表情 | 開心、燦爛、有點小害羞 | 知道你被她耍、嘴角壞壞上揚 |
| 氛圍 | 粉紅、亮、+ + + 加分浮動 | 紅+紫、暗、setting traps |
| 視覺記號 | 閃光 ✨、紅暈 cheek | 眉挑、wink、手指比向你 |
| 復用 | ch9 s5 戀愛 a callback（灰階退背景） | ch9 s6 戀愛 b callback（4 魔王考題 sticker grid） |

### §6.2 個別 prompt

---

#### 11. `ch6-girl-new` 剛認識的新女生 sticker

**用途**：
- [ch6 s3](outline.md) 「**剛認識的新女生**」中央 sticker、配「+/+/+」浮動加分動畫 + 副標「聊天都覺得對方也喜歡你」
- [ch9 s5](outline.md) 戀愛 a callback、退到背景、灰階 + opacity 0.3 ghost

**原路線**：[D] 粉紅底文字 sticker「剛認識的新女生 ✨」
**比例**：1:1 sticker（800×800）
**重點**：
- 必須跟 `ch1-girl-daydream`（v1 已生）**不同角色**——她是發呆的、這個是燦爛的初遇期
- 表情要明顯「對著鏡頭笑」、暗示「對方也喜歡你的錯覺」
- 灰階後仍要可辨識（避免太多依賴粉紅色定義角色）
- 可帶 1-2 個 sparkle ✨ 圖示（但用線條 stroke 畫、不要寫實光暈）
- 鏡頭視角：3/4 正面、可半身

**Prompt (English)**:
```
[Paste shared style prefix from §3 above]

Subject: A young woman with shoulder-length black hair styled with a slight outward curl at the ends, looking directly at the viewer with a bright, slightly bashful smile (lips closed but corners turned up clearly). 3/4 front-facing pose, head and upper torso visible, one hand raised near her cheek in a small wave or playful gesture. Casual outfit — a plain top in hot red #FF6B6B (NOT pink, to stay in palette), simple neckline.
Around her head: 2-3 small bold-outlined sparkle marks (4-point sparkle shapes, like ✨ but drawn as flat geometric stars, NOT light-bursts) in vivid yellow #FFD93D. Add subtle blush marks on her cheeks (small flat circular pink-ish patches — use soft violet #C4B5FD to stay in palette, NOT pink — like a comic-book blush).
Style: clearly DIFFERENT character from a calmer/sad sitting girl — this one is alive, expressive, "excited to meet you" energy. Bold black ink outlines, flat fills, no gradient, no realism.
Background: cream #FFFDF5 plain. Character takes 75% of canvas height, centered.
Test: if rendered in grayscale at 30% opacity, the body language and smile must still read as "happy young woman".
Aspect ratio: 1:1 square.
```

**驗收**：
- 燦爛笑容能秒看出「初遇期亢奮」
- 跟 ch1-girl-daydream 的「發呆內向」氣質明顯不同（避免觀眾混淆是同一角色不同 step）
- 灰階測試：縮圖灰階 opacity 30% 後輪廓 / 姿態仍清楚（callback 用）
- 色票嚴格：紅 / 黃 / 紫 / 黑 / cream（NO pink — 用 violet 代替 cheek blush）

---

#### 12. `ch7-girl-veteran` 老油條陷阱題 sticker

**用途**：
- [ch7 s7](outline.md) 老油條陷阱題 hook、配 2 個陷阱題 sticker（「和你媽掉進水裡你會先救誰」「該不該運動」）+ ❌ 答案
- [ch9 s6](outline.md) 戀愛 b callback 4 魔王考題 sticker grid 視覺繼承

**原路線**：[D] 紅/紫文字陷阱題 sticker（純文字）
**比例**：1:1 sticker（800×800）
**重點**：
- 必須跟 `ch6-girl-new`（同樣是「女生」概念）**氣質截然不同**——她是「老油條 / 知道你會掉坑」的 expression
- 表情關鍵字：smirk、knowing look、eyebrow raised、可帶手指比向觀眾或環抱手肘
- 不可畫成「壞女人 / 反派」（避免性別歧視觀感）——是「狡黠的、看穿你的、調皮的」、像玩 prank 一樣
- 鏡頭視角：可微側身、半身、頭部稍歪
- 不可挂任何文字（陷阱題本身用 HTML text sticker 疊上去）

**Prompt (English)**:
```
[Paste shared style prefix from §3 above]

Subject: A young woman with shoulder-length black hair, viewed in a 3/4 side angle, body slightly turned away but head looking back over her shoulder toward the viewer. Expression: a knowing smirk — lips closed and curled up on ONE side only (asymmetric smile, "I know something you don't"), ONE eyebrow visibly raised. Eyes half-lidded with a sharp, sly look. One hand under her chin in a thoughtful / scheming gesture (index finger touching her chin lightly), the other hand on her hip.
Casual outfit — a plain top in soft violet #C4B5FD (signals her "veteran" status visually contrasting with girl-new's red top), simple cut.
Style: bold black ink outlines, flat fills. NO menacing villain-coded features (no fangs, no shadow over eyes, no exaggerated devil look) — the vibe should be "you've been caught in my trap and you don't even realize it yet" charm, NOT cruelty.
Background: cream #FFFDF5 plain. Character takes 75% of canvas height, centered.
Distinguishing markers vs the "girl-new" sticker: this one has ONE-sided smirk vs symmetric smile, raised eyebrow, hand-on-chin scheming pose, violet outfit vs red — clearly the SAME drawing style but a DIFFERENT character archetype.
Aspect ratio: 1:1 square.
```

**驗收**：
- 「老油條」 / 「smirk」表情明顯、可秒看出「她設了陷阱」
- 跟 ch6-girl-new 視覺風格一致（同筆觸、同色票邏輯）但角色感截然不同
- 不踩「邪惡反派」陷阱（無 fangs / dark eye shadow / 誇張惡相）
- 紫色衣服跟 girl-new 紅色衣服形成 callback 對比、讓觀眾潛意識感受「同樣是女生但不同階段」
- 色票嚴格：紅 / 黃 / 紫 / 黑 / cream

---

### §6.3 v2 工時預估

| 項目 | 工時 |
| --- | --- |
| 你生 2 張圖（含 retry） | ~30-60 min |
| 我整合 ch6 s3 + ch7 s7 + ch9 s5 / s6 callback | ~30 min（subagent-driven、3-4 個小 commit） |
| **總計** | **~1.5 小時** |

### §6.4 整合策略（生圖通過後）

1. 把 2 張圖搬到 `demo/presentation/public/images/ai/ch6/girl-new.png` + `demo/presentation/public/images/ai/ch7/girl-veteran.png`
2. 取代 `src/motifs/GirlNew.jsx` 跟 `GirlVeteran.jsx`（目前都是 `<AssetPlaceholder>` shell）改成 `<AiSticker>` 包裝
3. 既有的 `Ch6Step3.jsx`（內含粉紅文字 sticker）+ `Ch7Step7.jsx`（內含紅/紫陷阱題）保留架構、把人物文字 sticker 改用 `<GirlNew />` / `<GirlVeteran />` motif component（陷阱題文字本身 [D] 保留）
4. `Ch9Step5.jsx` 既有的「剛認識的新女生」grayscale 背景文字 sticker → 改用 `<GirlNew />` motif + grayscale filter
5. `Ch9Step6.jsx` 4 個魔王考題 sticker grid → 4 張各加一個 `<GirlVeteran />` mini sticker 在卡片角落（暗示「同一個老油條」）

——但是這部分等你生圖通過再寫 plan。
