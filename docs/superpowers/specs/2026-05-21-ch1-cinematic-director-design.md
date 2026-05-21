# Ch1 Coldopen · Cinematic Director Pass · Design

**Date**: 2026-05-21
**Scope**: `demo/presentation/src/chapters/ch1-coldopen/` — 8 step / 10 beat（s1-s7 各 1 beat + s8 3 beat）
**Source of truth**: [demo/outline.md §1 ch1](../../../demo/outline.md#L138-L238) · [demo/script.md L1-L37](../../../demo/script.md) · [demo/outline-visual.md](../../../demo/outline-visual.md) · [Tier B 升級 spec](2026-05-17-demo-visual-tier-b-upgrade-design.md)
**Format**: 9-field per-beat cinematic direction（per 2026-05-21 brainstorming agreement）
**Pilot status**: 9 章 per-chapter spec 系列的 ch1 模板樣本。批准後 fan out ch2-ch9 八個並行 subagent。

---

## §0 · Chapter Narrative Role

**Ch1 是整片 12.5 分鐘演講的「冷開場 (cold open)」**，承擔三個敘事任務、缺一不可：

1. **建立情感契約 (emotional contract)**：講者用「心虛」「報告太不正經」自降身段，邀請觀眾「跟我一起笑」而非「聽我演講」。整片之後所有「老師我搞砸了 → 後來我發現」的 self-deprecating 節拍，都靠 ch1 的姿態建立信任。
2. **植入兩個 callback 種子**：
   - 心理學系畢業 → ch9 s8 plasticity（腦科學收尾）
   - BOOM 的 `motif/boom-double-ring` → ch9 s13「電費小偷」最終 stamp 圍邊（首尾呼應）
3. **設定 deck 的視覺火力上限**：ch1 s8 BOOM 是觀眾看到的第一個 climax，它直接定義「這份簡報願意在 wow moment 投入多少」。若 s8 火力不到位，後面所有 ★★★ punchline 都會被觀眾預期下調。

**情緒曲線**：
- 進入點：低（心虛、自嘲）
- 中段保持低-中（敘事、場景）
- 微反差拉抬於 s5 / s7（兩個靈感點各一拍小驚喜）
- s6 喜劇半拍刻意「平」（反差為 s8 蓄勢）
- s8 為 ch1 唯一 peak，必須做到「觀眾忍不住笑出來 + 第一次感受到 wow」

**敘事節奏 thesis**：ch1 是「鋪陳 + 喜劇 + 第一個 wow」三合一，**不是教學內容**。所有 motion 都要服務「人物形象」(誠懇 + 不正經 + 腦袋會冒奇怪靈感的人) 而非「資訊傳遞」。**錯就錯在當成 ch2 那種教學 step 在做動畫——這章是人物 setup，不是知識點 setup**。

---

## §1 · Constraint Envelope

**繼承自 outline-visual.md §1 + Tier B spec，不可動**：
- 不動 `script.md` 口播（L1-L37 為 source of truth、cue 時間以此為準）
- 不動 8 step / 10 beat 結構（s8 必須維持 3 beat）
- Neo-brutalism DNA：cream `#FFFDF5` 底、純黑 4-6px border、8-16px hard shadow（zero blur）、Space Grotesk 700/900、微旋轉 -3°~4°、禁圓角中段
- 不加：聲音設計 / custom cursor / cinematic letterbox bars / Tier C 破格
- 動效禁忌：禁紫粉漸變、禁 `filter: blur > 4px`、禁 `ease-in-out` 慢動畫（>800ms）、禁 spring 軟反彈（用 cubic-bezier `[0.34, 1.56, 0.64, 1]` 硬 overshoot）

**可動**（本 spec 的工作面）：
- 每 beat 的元素進場邏輯 / 視線引導 / 停頓時長 / micro-transitions
- 章內 motif 變奏（s4-s7 的 sticker 進場姿勢可以做 ch1 專屬語彙）
- 既有 outline.md 規格但 JSX 缺漏的元素（s2「敬請期待」黃 sticker + s8 `motif/boom-double-ring` 視覺）—— 兩者皆為**敘事必要**，不視為新增 scope

---

## §2 · Chapter Motion Motifs（ch1 專屬 signature movement）

整章重複出現 4 個動作語彙，建立 ch1 的 motion identity：

| ID | 動作定義 | 觸發點 | 情緒功能 |
| --- | --- | --- | --- |
| `ch1/stamp-slap` | scale 0.7→1.4→1.0 overshoot + rotate ±2~3° + hard shadow 從 0 長到 final 偏移量（180ms 內完成）| s1 心虛 / s2 心理學系 / s3 AI/解數獨 emphasis box / s8 boom card | 「砰」一下到位、用 hard-shadow 的「長出來」動作模擬實體紙卡被拍上桌 |
| `ch1/sticker-fly-in` | translate 從畫面外角落 → 目標位置 + scale 0.7→1.0 + 微旋轉、cubic-bezier `[0.34, 1.56, 0.64, 1]`、500ms | s4 正妹 / s5 flappy bird / s7 軍人 | 三張 sticker 各從 deck 不同角落「飛進來」、每張保留個性 rotate（-4° / +3° / +2°）|
| `ch1/thought-bubble-grow` | 4 個圓 stagger 130ms、scale 0→1 overshoot、半徑 16 → 26 → 38 → 54 px 等比放大 | s5 第一條思考鏈 / s7 第二條思考鏈 | 「腦中冒出來的想法越來越具象、越來越大」的視覺隱喻 |
| `ch1/hold-and-quiver` | 元素就定位後 ±4px y-axis 浮動、4s loop ease-in-out | s1 心虛 sticker / s3 紫方塊 / 三 sticker 持續態 | 「畫面活著、在呼吸」、避免 hold 階段死寂 |

**繼承 Tier B Motif Library**：`motif/boom-double-ring`（s8 首發）· `motif/yellow-highlight`（s8 punchline）· `motif/spotlight-vignette`（s8 已用、本 spec 不擴張）

**章內克制**：ch1 故意**不使用** `motif/halftone-burst` / `motif/ink-splatter` / `motif/screen-shake`（強版）—— 這些保留給 ch4 / ch5 / ch6 / ch7 的真正崩盤拍。ch1 BOOM 是「腦中靈感結合的可愛 BOOM」、不是「世界毀滅的 BOOM」，刻意控制火力。

---

## §3 · Per-Step Per-Beat Cinematic Direction

### Step 1 · Beat 0 · `xinxu-opening`（心虛開場）

- **敘事角色**：opening / vulnerability hook —— 全片第一個畫面，定整片人物 tone。
- **目前問題**：
  - JSX：黑→cream fade 400ms 後 title scale 0.7→1 overshoot（delay 0.5s）+ presenter mask-reveal（delay 1.2s）。Title 永久 ±4px 浮動（4s loop）。
  - 缺點 1：黑屏只有 400ms、太快沒進入「黑屏儀式感」。觀眾還沒準備好就被拍進畫面。
  - 缺點 2：「心 虛」hero 用 `2026 資展會<br/>期中報告` 文字佔了主視覺位 —— 但口播第一句是「我真的很心虛」、視覺應該扣在「心虛」二字而非標題。outline.md 也明寫「全屏『心 虛』巨字 sticker」+ 角標「期中報告」。**現實作把主從關係顛倒**。
  - 缺點 3：presenter line「Presented by 王文杰」mask-reveal 完即靜止 —— 講者站著念第一句時，畫面是死的。
- **升級方向**：把畫面權重從「期中報告」翻轉回「心 虛」，用 1.2s 黑屏儀式 + 心虛字尾**輕微下沉**製造心理重量。
- **建議動畫**：
  - **0.0-1.2s** 黑屏。grain 紋已開始隱約浮現（opacity 0→0.15、`mix-blend-mode: multiply`）但 cream 還沒進來。
  - **1.2-1.6s** cream 從畫面**底部**向上 wipe-in（`clipPath: 'inset(100% 0 0 0)' → 'inset(0)'`、400ms cubic-bezier `[0.65, 0, 0.35, 1]`）。不是 fade、是「紙從下面被抽出來鋪好」。
  - **1.6-1.9s**「心 虛」hero（紅底 / 6px 黑邊 / 16px hard shadow、rotate -3°）以 `ch1/stamp-slap` 進場：scale 0.7→1.4(140ms)→1.0(160ms)，hard shadow 偏移量從 `0 0 0 0` 動畫到 `16px 16px 0 0` 同步長出（用 motion 的 `boxShadow` 關鍵幀）。
  - **1.9-2.3s** 右上角小 sticker「期中報告」（黃底 cream 字、12px 黑邊、rotate +6°）以 0.5 scale 從右上飛入、stamp-slap 微縮版。
  - **2.3-2.8s** 「Presented by 王文杰」從**左下角**而非置中、用 mask-reveal（`clipPath` 左到右、duration 500ms）。
  - **持續態**：「心 虛」二字維持 ±3px y-axis 緩慢浮動（5s loop、ease-in-out）+ 紅底卡片內部微妙的 **grain 流動**（背景 grain layer 走極慢 `background-position` translate、20s loop）。
- **建議 transition (in)**：from chapter loader → 1.2s 全黑 + grain 漸顯。
- **建議 transition (out, → s2)**：左鍵 → 「心虛」hero 不動、僅 cream 底色 + sticker + presenter line 一起 fade-out + scale 0.95（200ms）。「心虛」最後消失（200ms 後、scale 0.9 + opacity 0），製造「心虛感停留」殘像。
- **Motion timing**：黑屏 1200ms / cream wipe 400ms / 「心虛」stamp 300ms / 「期中報告」400ms / presenter 500ms。**總時長 2.8s**（口播 L1 約 8s、剩餘 5s 給講者鋪墊）。
- **視覺強化**：
  - 「心 虛」字級從目前隱含的 5.5rem **拉到 hero-mega 8rem**（per §1.5 Typography token）—— 因為這是全片第一個字、值得最大字級。
  - 「2026 資展會 / 期中報告」現有那張紅卡**整個拿掉**，移到右上角小 sticker（per outline.md 規格）。
  - 紅底 + 6px 黑邊 + 16px shadow 配色保留。額外加：紅底內部加入**極輕**的 halftone 點點紋理（`background-image` data-uri SVG、opacity 0.06）—— 在 hard shadow 之外多一層紙質感。
- **情緒目的**：1.2s 黑屏讓觀眾「準備聽」、心虛字砸下時觀眾「忍不住笑」、停頓 1s 讓笑聲落定後講者開口。
- **敘事作用**：建立人物姿態（誠懇、自嘲）、建立「這份簡報願意停頓」的節奏期待。
- **預期觀眾感受**：黑屏時微微緊張 → cream 出來時鬆一口氣 → 心虛字到位時笑 → 講者開口時已經被收服。

---

### Step 2 · Beat 0 · `psych-major-foreshadow`（心理學系 + 敬請期待）

- **敘事角色**：credentials + callback seed —— 唯一在 ch1 必須認真鋪墊的點。「心理學系」是 ch9 plasticity 收尾的伏筆，「敬請期待」是 callback 約定。
- **目前問題**：
  - JSX：只有一張白卡「心 理 學 系 · 畢業」（紅 kicker「背 景」），從右下 overshoot 進場。**結束**。
  - 缺點 1：outline 明寫要有 **紅色箭頭 + 「敬請期待」黃 sticker**（伏筆 RL/腦科學/plasticity）。現在完全沒有。callback 種子沒種、ch9 收尾收空氣。
  - 缺點 2：唯一一張卡固定不動、講者念完整段話畫面 7-8s 完全靜止。
  - 缺點 3：紅 kicker「背 景」+ 主體「心理學系」中間沒有視覺層級遞進、看起來像兩個獨立元素硬擺。
- **升級方向**：把畫面從「單一靜止卡」升級為「介紹卡 → 紅箭頭 → 敬請期待」三拍動態組合、種下 callback 種子。
- **建議動畫**：
  - **0.0-0.6s** 主卡（白底 6px 黑邊 12px shadow、rotate -2°）從右下 stamp-slap 進場（既有）。內容調整為 kicker「我是 ←」+ 主體「心 理 學 系」+ 副標「· 畢業」**三段層級**。kicker 字級降到 1rem、用紅色。
  - **0.6-1.1s** 主卡左側畫出紅色粗箭頭 SVG（stroke-dasharray draw、4px 黑邊 + 紅實心填、長度 ~200px、500ms `ease-out`），箭頭頭部停在主卡左緣外 32px 處。
  - **1.1-1.6s** 箭頭尾端（畫面左側）→ 「敬請期待」黃 sticker（黃底 cream 字、4px 黑邊、6px shadow、rotate -4°、字級 1.5rem）以 stamp-slap 微縮版進場（scale 0→1.2→1.0、150+150ms）。
  - **1.6s+** 黃 sticker 進入 `ch1/hold-and-quiver`（±4px y、4.5s loop）+ 右邊主卡靜止（已建立、不再搶焦點）。
- **建議 transition (in)**：from s1 → fade-bridge 300ms（既有全域）+ 主卡從右下進來與 fade-bridge 結束點同步（觀眾感覺「畫面接著就出主卡」、沒有空 frame）。
- **建議 transition (out, → s3)**：左鍵 → 「敬請期待」黃 sticker 先**單獨先發**（scale 1.1→0、180ms、好像「現在還不揭」的反向退場）→ 200ms 後主卡 + 箭頭一起 fade-out scale 0.95。
- **Motion timing**：主卡 600ms / 箭頭 draw 500ms / 黃 sticker 300ms。**總進場時長 1.6s**（口播 L5 約 7s、剩餘 5s 給講者鋪墊）。
- **視覺強化**：
  - 紅箭頭粗 8px、頭部尖角（zero radius、per §1.3 No rounded mid）—— 用 SVG `polygon` 而非 `marker-end`，確保 hard-edge。
  - 黃 sticker 字「敬請期待」加底線（2px 黑、`text-decoration-skip-ink: none`）—— 強調「這是個約定」。
  - 主卡內 kicker「我是 ←」字尾的 ← 是純文字字元、不是 SVG icon。手寫感、強化「自我介紹」口吻。
- **情緒目的**：箭頭 draw 出來時觀眾視線被引導向「敬請期待」、產生「等等會發生什麼？」的微期待。
- **敘事作用**：種下兩個 callback 種子（心理學 + 敬請期待）—— 這兩個將在 ch9 s8 / s9 plasticity 段被講者顯式 callback、強化「整場演講有結構」的高級感。
- **預期觀眾感受**：「噢、心理學系喔」（標籤化）→「敬請期待」進來時微笑、心裡偷偷標記「等等他會用心理學講什麼？」

---

### Step 3 · Beat 0 · `theme-reveal`（訓練 AI 解數獨）

- **敘事角色**：thesis statement —— 整片最直接的「我要做什麼」一句話。
- **目前問題**：
  - JSX：kicker「期中主題」左滑入 → hero「訓 練 AI 解 數 獨」（AI 紅 box + 解數獨 黃 box、scale + letter-spacing 動畫 720ms overshoot）→ 4 個 corner 裝飾物 stagger delay 1.0-1.3s + 黃星永久旋轉。
  - 缺點 1：4 個 corner 裝飾物**全部 delay 1.0s 之後才進場**、進場時 hero 已就位 —— 視線被裝飾物搶走、削弱 thesis 的權重。
  - 缺點 2：AI 紅 box 和 解數獨 黃 box 同時與 hero 動畫一起進場 —— 兩個 emphasis box 沒有獨立的「砸下」moment。
  - 缺點 3：hero 的 letter-spacing 動畫從 0.1em → -0.04em 是好點子但**幅度太小**、視覺上感覺不到「字在收緊」。
- **升級方向**：把畫面拆成「裝飾物先就位 → kicker → 訓練 → AI 砸下 → 解數獨 砸下」5 拍、讓 AI 和 解數獨兩個關鍵詞各自獨立有一個 stamp moment。
- **建議動畫**：
  - **-0.3-0.0s** 4 個 corner 裝飾物 stagger 60ms 進場（**比 hero 早**、scale 0→1 overshoot、各 200ms）。這 4 個是「畫面邊框」、要先建立空間。
  - **0.0-0.3s** kicker「期中主題」從左 slide-in（既有、加快到 300ms）。
  - **0.3-0.7s** hero「訓 練 □ □」（AI 和 解數獨位置先空著、僅顯示底色 placeholder）以 mask-reveal 從左到右進場（400ms），letter-spacing **從 0.15em → -0.05em**（拉大幅度、視覺感覺字在「咬合」）。
  - **0.7-1.0s** AI 紅 box 從 hero 上方 -60px **砸下**（drop-in、stamp-slap、scale 1.3→1.0、150+150ms）。
  - **1.0-1.3s** 解數獨 黃 box 從 hero 下方 +60px **砸上**（與 AI 相反方向、stamp-slap、scale 1.3→1.0、150+150ms）。**兩個 emphasis box 對撞、強化 "AI" ＆ "解數獨" 的對位感**。
  - **持續態**：黃星永久旋轉（既有、12s linear）+ 紫方塊 ±16px y-axis 浮動 4s loop（既有）。新增：AI 紅 box 與 解數獨 黃 box 各自獨立 ±2px micro-jitter（3s loop、phase 錯開）—— 兩個關鍵詞「一直在跳動」。
- **建議 transition (in)**：from s2 → fade-bridge 300ms（既有）。裝飾物進場與 fade-bridge 末段重疊（讓觀眾看到「畫面在堆」、不是「畫面切完才開始堆」）。
- **建議 transition (out, → s4)**：左鍵 → AI 和 解數獨 兩 box **不動**、kicker + hero「訓 練」+ 4 裝飾物 fade-out。AI/解數獨 兩 box 持續 ~200ms 後一起 scale 0.7 + opacity 0 退場 —— 製造「主題印在腦裡」殘像。
- **Motion timing**：corner 進場 200+60+60+60+60 = 440ms / kicker 300ms / hero mask-reveal 400ms / AI stamp 300ms / 解數獨 stamp 300ms。**總進場時長 1.3s**（口播 L9 約 8s、剩餘 6s 給講者）。
- **視覺強化**：
  - AI 紅 box rotate **-3°**、解數獨 黃 box rotate **+3°**（相反方向、構圖視覺平衡）。既有 -2° / +2° 拉大一級。
  - hero「訓 練」用 text-stroke（`-webkit-text-stroke: 3px black; color: transparent;`）—— 描邊空心字、為 AI/解數獨兩 box 的「實心填色」做反差。outline-visual.md §1.5 已提此技法用於「章主題揭曉的 hero 字」。
  - hero 後方背景加極淡的 9×9 sudoku grid 線（opacity 0.04、純線稿、不喧賓奪主）—— 為「解數獨」主題下視覺暗示。
- **情緒目的**：兩個 emphasis box 對撞時觀眾感受「AI」+「解數獨」這兩件原本不該結合的事被強行扣在一起的張力。
- **敘事作用**：明確 thesis、讓後續所有 step 都有「為這個 thesis 服務」的明確錨點。
- **預期觀眾感受**：「啊、是 AI + 解數獨」（清楚理解）+「兩個關鍵詞砸下時有種儀式感」。

---

### Step 4 · Beat 0 · `mrt-girl-arrival`（捷運看正妹）

- **敘事角色**：scene-setting / comedy ground —— 把觀眾帶進「具體場景」、為後續兩個靈感點建立空間。
- **目前問題**：
  - JSX：caption「靈感哪來呢？某天捷運上⋯」從上 y:-40 fade-down（delay 0.3s、500ms）+ 正妹 sticker 從左下 overshoot 進場（delay 1.0s、500ms）。MRT 背景圖由 Ch1.jsx parent 提供（per `showMrtBackdrop = stepId >= 4 && stepId <= 7`）。
  - 缺點 1：MRT 背景圖**直接出現**、沒有「環境正在進入」的儀式 —— 從 s3 純白底切到 s4 滿背景照片是個視覺斷層。
  - 缺點 2：caption 從上 fade-down 過於平凡、毫無「某天捷運上⋯」這句話該有的悠閒/回憶感。
  - 缺點 3：正妹 sticker 用 overshoot 進場 —— 但這是「回憶慢慢浮現」、不是「sticker 砸下」、進場語彙錯。
- **升級方向**：把 s4 變成「環境淡入 → 字幕悠閒滑入 → 正妹 sticker 像漂浮出來」的回憶 dream 質地，跟其他 step 的 stamp 語彙形成對比。
- **建議動畫**：
  - **0.0-0.6s** MRT 背景圖 fade-in（opacity 0→0.85、600ms ease-out、scale 1.04→1.00 緩慢 zoom-out）。zoom-out 暗示「鏡頭推回過去」。
  - **0.4-1.0s**（與 MRT 背景重疊）caption「靈感哪來呢？某天捷運上⋯」用 **letter-by-letter typewriter** 進場（每字 50ms、總計 ~600ms 把 12 字打完）—— 不是 mask-reveal、不是 fade、是逐字浮現、模擬「講者邊想邊說」。
  - **1.0-1.5s** 正妹 sticker 從**畫面左下 +60px 外**飄入（translate y -60→0、opacity 0→1、scale 0.85→1.0、`ease-out` 不 overshoot、500ms）—— **特別注意：不用 stamp-slap、用柔和進場**、因為這是「回憶人物登場」、不是事件。
  - **持續態**：正妹 sticker ±3px y-axis 4s loop（保留現有）+ 背景 MRT 圖內部極輕微的 `background-position` 緩慢水平 drift（30s loop、3px 範圍）—— 暗示捷運在動。
- **建議 transition (in)**：from s3 → fade-bridge 500ms（加長、因為 s4 是場景切換）+ 黑色淡入過度 100ms（極輕、`rgba(0,0,0,0.15)` 一閃即消、模擬「鏡頭眨眼」的剪接）。
- **建議 transition (out, → s5)**：**所有元素保留、不退場**。s5 是同場景進場、不需要 reset。左鍵 → 僅 caption 微微 fade（opacity 1→0.6）讓它退到背景、騰出位置給 s5 的 flappy bird sticker。
- **Motion timing**：MRT fade 600ms / caption typewriter 600ms / 正妹 sticker 500ms（500-1500ms 區間）。**總進場時長 1.5s**（口播 L13-L15 約 7s、剩餘 5s 給講者）。
- **視覺強化**：
  - MRT 背景圖加 `filter: brightness(0.92) saturate(0.85)` —— 降一點對比度、為前景 sticker（高飽和）留視覺空間。
  - caption 加微微 `text-shadow: 2px 2px 0 rgba(0,0,0,0.15)` —— 在照片背景上保住可讀性、但 shadow blur=0 維持 Neo-brutalism。
  - 正妹 sticker 周圍加 **2px cream 描邊**（在 sticker 圖外緣加一層 cream stroke）—— 從照片背景中「跳」出來。
- **情緒目的**：typewriter 字幕讓觀眾感受「講者在 narrate 一段回憶」、正妹 sticker 飄入帶來「啊原來這故事是這樣」的微笑。
- **敘事作用**：建立故事 ground truth（時間、地點、人物）—— s5 / s7 兩個靈感才能扣在這個 ground 上。
- **預期觀眾感受**：「噢、進入故事了」（明確感受到敘事節奏切換）+「正妹發呆 sticker 好可愛」（微笑）。

---

### Step 5 · Beat 0 · `flappy-bird-idea`（Code Bullet flappy bird 靈感）

- **敘事角色**：first idea arrival —— 故事中的「第一個小驚喜」。
- **目前問題**：
  - JSX：persisted 正妹 sticker + 新 flappy bird sticker 從右上 overshoot 進場（500ms）+ 4 個漸大的青綠思考泡泡 stagger 130ms。
  - 缺點 1：flappy bird sticker 用 **stamp-slap overshoot** 進場 —— 但這是「腦中冒出的靈感」、應該用「漂浮出來 + 微旋轉就位」的語彙、不是砸下。
  - 缺點 2：4 個思考泡泡進場後**靜止不動**、沒有「思路在連結」的動感 —— 應該有微妙的依序 pulse、暗示「思考流向」。
  - 缺點 3：思考泡泡用單純青綠實心 #2EC4B6 —— 顏色選對（冷色對比暖背景）但**形狀變化太小**、4 個都是圓、缺少視覺層次。
- **升級方向**：把 flappy bird sticker 進場語彙改成「dream-pop-in」（半透明 → 不透明 + 微旋轉就位）、思考泡泡進場後接 idle pulse、強化「靈感連結中」的氛圍。
- **建議動畫**：
  - **0.0-0.5s** flappy bird sticker 從右上 +120px / +60px 漂入（translate + scale 0.7→1.0、cubic-bezier `[0.16, 1, 0.3, 1]` 順滑加速減速、500ms）+ opacity 0→1。**進場時 rotate 從 0° → +3° 微旋轉**（落定後保持微旋轉、暗示「想法剛從口袋裡掉出來」）。
  - **0.5-1.05s** 4 個思考泡泡 `ch1/thought-bubble-grow`（既有規格、130ms stagger、scale 0→1、4 個半徑 16/26/38/54 px 漸大）。
  - **1.05s+** 4 個泡泡進入 **idle pulse sequence**：依序（最小 → 最大）做 scale 1.0→1.08→1.0 各 400ms、間隔 200ms，整輪 2.4s 循環。視覺效果是「一波 pulse 從正妹腦中流向 flappy bird」、持續暗示「思路在連結」。
- **建議 transition (in)**：from s4 → 無顯式 transition、所有 s4 元素 persist、flappy bird 直接進場（強化「故事正在繼續」、不是「新 step 開始」）。
- **建議 transition (out, → s6)**：左鍵 → flappy bird sticker 維持原位、4 個思考泡泡**整組 fade-out**（opacity 0、200ms）—— s6 的「⋯⋯」氣球會接替視覺焦點。
- **Motion timing**：flappy bird 進場 500ms / 泡泡 stagger 0.5-1.05s（總 550ms）/ idle pulse 從 1.05s 開始無限循環。**總進場時長 1.05s**（口播 L19 約 7s、剩餘 6s 給講者）。
- **視覺強化**：
  - 4 個思考泡泡的**第 4 個**（最大、最靠近 flappy bird）內部加一個極小的「！」感嘆號（cream 色、字級 18px、隨主體 pulse）—— 暗示「想到了」、視覺笑點。
  - 思考泡泡的 hard shadow 偏移也按比例放大（16px → 5px / 5px shadow，54px → 8px / 8px shadow）—— 保持視覺一致性。
  - flappy bird sticker 加極輕的 **idle wing-flap**（用 CSS `@keyframes` 對 sticker 圖做 `transform: skewY()` ±1° 微抖、800ms loop）—— 暗示「flappy bird 還在飛」。
- **情緒目的**：第 4 個泡泡的「！」笑點 + idle pulse 的視覺流向、讓觀眾「看見」靈感從腦中冒出的過程。
- **敘事作用**：第一個靈感點被視覺化、建立「s8 BOOM 是兩個靈感結合」的鋪墊。
- **預期觀眾感受**：「噢、flappy bird 那個梗」（會心一笑）+ 看見泡泡 pulse 時微微跟著節奏看泡泡走向。

---

### Step 6 · Beat 0 · `comedy-still`（繼續發呆）

- **敘事角色**：comedy half-beat / suspense rest —— 給觀眾笑、給 s8 BOOM 拉長蓄勢的反差節拍。
- **目前問題**：
  - JSX：兩 sticker persisted + 「⋯⋯」氣球（白底 4px 黑邊、cream 字、字級 32px、letter-spacing 0.2em）以 stamp-slap 進場 + 1s ease-in-out pulse（scale 1→1.08→1）+ 右下 caption「然後我繼續發呆⋯」（fade-in 500ms、delay 0.4s）。
  - 缺點 1：「⋯⋯」氣球的 pulse 太快（1s loop）—— 應該**慢得不耐煩**、強化「真的就只是在發呆、什麼都沒進展」的喜劇感。
  - 缺點 2：右下 caption「然後我繼續發呆⋯」與「⋯⋯」氣球**毫無視覺呼應** —— 應該共用 typography 或同步 pulse。
  - 缺點 3：s5 的 4 個思考泡泡此 step 完全消失 —— 但泡泡象徵「思路」、思路停了應該**留 1 個泡泡退色保留**（殘留物）、不是全消失。
- **升級方向**：拉長 pulse 週期、加 caption 的同步呼吸、保留 s5 最大泡泡作為「思路殘骸」、刻意把這拍做慢做無聊。
- **建議動畫**：
  - **0.0-0.3s** 「⋯⋯」氣球以**柔和** stamp 進場（scale 0→1.0、不 overshoot、300ms `ease-out`）。
  - **0.3s+** 氣球 idle 「**極慢呼吸**」：scale 1.0→1.04→1.0、**3 秒一輪**（既有 1s 改成 3s）、`ease-in-out`。
  - **0.4-1.0s** 右下 caption「然後我繼續發呆⋯」fade-in + 字尾「⋯」單獨從 opacity 0 → 0.6 → 1 慢慢出現（總計 600ms）—— 字尾的 ⋯ 跟氣球的 ⋯⋯ 視覺呼應。
  - **caption 持續態**：「⋯」字尾**獨立** opacity pulse（0.4 ↔ 1.0、2.5s loop、與氣球 pulse 異步）。
  - **保留**：s5 第 4 個（最大）思考泡泡**不全消、僅淡化**到 opacity 0.25、保留在原位、暗示「上一個 想法的殘骸」。
- **建議 transition (in)**：from s5 → 思考泡泡 1-3 fade-out（200ms）+ 第 4 個泡泡淡化到 0.25（與氣球進場同步）。
- **建議 transition (out, → s7)**：左鍵 → 「⋯⋯」氣球 + 右下 caption **同步 fade-out**（300ms）。**保留**第 4 個淡化泡泡（s7 會用它連接新的思考鏈、形成「殘骸 → 新思路」的視覺連續）。
- **Motion timing**：氣球進場 300ms / caption 600ms / pulse 3000ms loop / caption 字尾 pulse 2500ms loop。
- **視覺強化**：
  - 「⋯⋯」字體與右下 caption「⋯」字尾用**相同 letter-spacing（0.2em）+ 相同字級漸層**（氣球 32px / caption 18px、視覺上是「同一族」）。
  - 氣球右下角 +2px 偏移（往女生 sticker 反方向）—— 暗示「想法已經離開」。
  - 整個 step 的 grain 紋 opacity 微微上調（0.5 → 0.6）—— 加重「悶悶的空氣」質地。
- **情緒目的**：3 秒慢呼吸 + caption 字尾 pulse 製造「真的什麼都沒發生」的喜劇延宕、為 s8 BOOM 拉滿反差。
- **敘事作用**：suspense rest —— 觀眾以為故事「卡住了」、講者趁機停頓、為 s7 + s8 的雙拍蓄勢。
- **預期觀眾感受**：「⋯⋯欸他真的就停在這邊」（笑）+ 隱約感覺「等下應該會發生什麼」（期待）。

---

### Step 7 · Beat 0 · `soldier-idea`（當兵沒手機解數獨）

- **敘事角色**：second idea arrival —— 第二個靈感點到位、s8 BOOM 的關鍵預備拍。
- **目前問題**：
  - JSX：軍人 sticker 從右下 overshoot 進場（500ms、無 delay）+ 4 個新思考泡泡水平排列（從正妹→軍人、bottom 14% + 144px 中線、size 16/26/38/54）。
  - 缺點 1：軍人 sticker 進場用 stamp-slap、與 s5 flappy bird 進場語彙重複 —— 兩個靈感點動作一樣、缺乏個性區分。第二個靈感應該有「另一個方向冒出來」的不同進場。
  - 缺點 2：第二條思考鏈（水平）與 s5 第一條思考鏈（往上）**沒有視覺關聯** —— 兩條鏈像是兩個獨立事件、不是「兩條思路即將碰撞」。
  - 缺點 3：軍人 sticker 與正妹 sticker、flappy bird sticker 之間沒有空間上的「即將碰撞」暗示。
- **升級方向**：軍人 sticker 用「從下面爬上來」的進場（與 flappy bird 的「從上面降下來」對稱）、第二條思考鏈用「從 s6 殘骸泡泡延伸出來」的進場、視覺暗示「兩條思路正在會合」。
- **建議動畫**：
  - **0.0s** s6 殘留的第 4 個淡化泡泡（opacity 0.25、正妹腦上方）**緩慢沉到中線**位置（translate y +150px、800ms `ease-in-out`）+ opacity 0.25 → 0.8、size 微縮 54→38（變成新鏈的第 3 個泡泡的同款）。視覺上是「上次的想法降下來、變成新鏈的一環」。
  - **0.3-0.8s** 軍人 sticker 從**畫面右下 +60px / +120px 外**爬入（translate x -120 → 0、translate y -60 → 0、scale 0.85→1.0、cubic-bezier `[0.16, 1, 0.3, 1]`、500ms）+ rotate 從 +6° → +2° 旋進就位。**不用 stamp-slap**、用「爬入」語彙、與 flappy bird 的「漂入」呼應但方向相反。
  - **0.8-1.45s** 新思考鏈剩下 3 個泡泡（size 16 / 26 / 54）依序 stagger 130ms 進場（第 38 的位置已經被 s6 殘骸填了）。從正妹腦邊往軍人腦邊 stagger。
  - **1.45s+** 4 個泡泡進入「**對流 pulse**」：第 1 個（最小、靠正妹）pulse 完接第 4 個（最大、靠軍人）pulse、兩端互相呼應、再依序中間的 2、3、形成「兩個靈感點互相回應」的視覺節奏。整輪 2.8s 循環。
- **建議 transition (in)**：from s6 → s6 殘骸泡泡開始「沉到中線」與 s7 進場同步（沒有顯式 fade-bridge、敘事連續）。
- **建議 transition (out, → s8)**：左鍵 → **所有元素瞬間 dim 到 opacity 0.35**（150ms）—— 為 s8 spotlight vignette 進場做準備。三 sticker 維持在原位（s8 beat 0 會 shake 它們）。
- **Motion timing**：殘骸泡泡下沉 800ms / 軍人 sticker 進場 500ms / 新鏈 stagger 650ms / 對流 pulse 2800ms loop。**總進場時長 1.45s**（口播 L25 約 8s、剩餘 6s 給講者）。
- **視覺強化**：
  - 軍人 sticker 進場時加極輕的 **dust puff**（cream 色小三角形 SVG 從 sticker 底部噴出、scale 0→1.5 opacity 1→0、200ms）—— 暗示「踏進畫面」、強化「軍人」氣質。
  - 思考鏈泡泡的「對流 pulse」用色彩上做區隔：第 1、2 個（靠正妹）保持青綠 `#2EC4B6`、第 3、4 個（靠軍人）改成**淡紅** `#FF6B6B`（透明度 0.85） —— 兩端代表兩個不同的靈感顏色、中間泡泡是混色過渡（青綠 → 紅）。
  - 三 sticker 各自的 hard shadow 都加 +1° 額外 rotate（girl -5°、flappy +4°、soldier +3°）—— 加重「畫面要崩潰前的微微歪斜」。
- **情緒目的**：殘骸泡泡下沉 + 對流 pulse、讓觀眾**潛意識感受到「兩個東西在連結」**、為 s8 BOOM 蓄滿張力。
- **敘事作用**：第二個靈感就位、所有元件齊備、s8 一拍就能炸。
- **預期觀眾感受**：「啊、那兩個梗要結合了嗎？」（預期感被拉滿、開始期待 s8）。

---

### Step 8 · Beat 0 · `sticker-shake`（背景三 sticker 抖動 + spotlight 進場）

- **敘事角色**：BOOM pre-impact —— 為三 beat 連擊的第一拍、製造「事件正在發生」的緊張瞬間。
- **目前問題**：
  - JSX：三 sticker 已 wrap 在 `stickersScope` 容器、beat 0 進場時 animateStickers 觸發 150ms shake（x: [0,4,-4,2,-2,0]、y: [0,2,-2,1,-1,0]）。同時 SpotlightVignette `active={beatIndex >= 0}` 進場。Auto-advance 400ms 後到 beat 1。
  - 缺點 1：三 sticker 抖動幅度太小（±4px）—— 對於「BOOM 預備拍」的張力不夠、應該再大一級。
  - 缺點 2：抖動只有單純 translate、沒有 rotate jitter —— 三 sticker 各自 rotate 微抖能加倍「畫面要崩」的感覺。
  - 缺點 3：spotlight vignette 在 beat 0 就進來、但中央 boom card 還沒砸下、spotlight 中心點是空的、視覺空洞。
- **升級方向**：抖動幅度提升 + 加 rotate jitter + spotlight 延後到 beat 1（spotlight 中心要對齊 boom card）。
- **建議動畫**：
  - **0.0-0.15s** 三 sticker shake：x: [0, 6, -6, 4, -4, 0]、y: [0, 4, -4, 2, -2, 0]、**新增** rotate: [0, ±2, ∓2, ±1, ∓1, 0]（每張 sticker 用各自既有 rotation 為基準 ± jitter）。
  - **0.0-0.15s** 全屏 `<main>` 同步 micro-shake（±2px、與三 sticker 同節奏）—— 模擬「BOOM 的衝擊波還沒到、地板先震」。
  - **0.15-0.4s** 三 sticker 回位、保持 opacity 0.35 dim 狀態（既有 wrapping div）。
  - **0.4s** auto-advance → beat 1（既有規格）。
  - **不要在 beat 0 進 spotlight**：spotlight vignette 延後到 beat 1 與 boom card 同步進場。
- **建議 transition (in)**：from s7 → s7 的「dim 到 0.35」150ms transition 與 beat 0 shake 開始同步（無縫接續、視覺感覺「畫面震了一下、暗下來」）。
- **建議 transition (out, → beat 1)**：auto-advance 400ms 後直接進 beat 1、無顯式 transition（衝擊感不該有空檔）。
- **Motion timing**：shake 150ms / 等待 250ms / auto-advance @ 400ms。
- **視覺強化**：
  - 抖動時三 sticker 各自的 hard shadow **不變**（不是 sticker 隨機改 shadow、那會過度炫技）—— 只動 transform、shadow 保持實體感。
  - 全屏 grain 紋在 shake 期間 opacity 從 0.5 → 0.7（150ms 內、與 shake 同步）—— 「畫面顆粒度增加」的緊張感。
- **情緒目的**：150ms 的震動是「事件正要爆」的物理預告、觀眾呼吸停住。
- **敘事作用**：把 s7 鋪滿的張力轉換成「即將釋放」的瞬間 ——下一拍 BOOM 就出來。
- **預期觀眾感受**：「欸欸欸要發生什麼了」（坐直）。

---

### Step 8 · Beat 1 · `boom-burst`（雙圈爆破 + boom card 進場）

- **敘事角色**：first impact —— 整片**第一個** wow moment。也是 `motif/boom-double-ring` 的首發、它將在 ch9 s13 最終 callback。
- **目前問題**：
  - JSX：beat 1 時 boom card「訓 練 AI 解 數 獨」(cream + 6px 黑邊 + 16px shadow、rotate -2°、scale 0.8→1 overshoot、400ms `[0.34, 1.56, 0.64, 1]`) 進場 + SpotlightVignette 跟著上來。
  - **CRITICAL 缺點**：`motif/boom-double-ring`（黃外圈 + 紅內圈、border 8px、stagger stamp）**完全沒實作** —— 這是 outline.md 明寫的 motif 首發、是 deck 的視覺 signature 之一。沒有它、ch1 BOOM 視覺只是「卡片砸下」、不是「BOOM」、且 ch9 s13 的首尾呼應失效。
  - 缺點 2：boom card 單純 scale overshoot、沒有方向感（既不是從上砸下也不是從下震上來）—— 缺乏「兩個想法結合」的撞擊隱喻。
- **升級方向**：補上 `motif/boom-double-ring` 雙圈爆破 + 讓 boom card 從畫面中央「向外 + 向內」雙向撞合的姿態。
- **建議動畫**：
  - **0.0-0.08s** `motif/boom-double-ring` 黃外圈（半徑 280px、border 8px 黃、stagger 0、stamp scale 0→1.2→1.0、150+100ms）—— 從畫面中央放射狀爆出。
  - **0.08-0.20s** 紅內圈（半徑 200px、border 8px 紅、stagger 80ms 延遲、stamp scale 0→1.2→1.0、150+100ms）—— 比黃圈晚 80ms 進場、形成「雙圈節奏」。
  - **0.0-0.20s**（與雙圈同步）背景三 sticker 第二次抖動（150ms shake、與 beat 0 反向、x: [0, -4, 4, -2, 2, 0]）—— 雙圈爆破的「反作用力」。
  - **0.20-0.60s** boom card「訓 練 AI 解 數 獨」進場：**特殊雙向動畫**：
    - 卡片本體從 scale 1.5 → 0.9 → 1.0（壓縮 + 反彈、200ms + 200ms）—— 模擬「兩個想法**從外向內**壓進來、再彈到實體大小」。
    - 同時 rotate 從 +2° → -2°（旋進就位）。
    - hard shadow 從 `0 0 0 0` 動畫到 `16px 16px 0 0` 同步長出。
  - **0.20s** 同步：spotlight vignette 開始淡入（既有規格、500ms `ease-out`、中心對齊 boom card）。
  - **0.60s+** boom card 進入 `ch1/hold-and-quiver` 微浮動。
- **建議 transition (in)**：from beat 0 → 雙圈進場為 beat 0 dim 狀態的「視覺打破」、不需顯式 fade。
- **建議 transition (out, → beat 2)**：等待 click。雙圈 + boom card 維持原位、不退場。
- **Motion timing**：黃圈 250ms / 紅圈 250ms（@ 80ms）/ sticker shake 150ms / boom card 600ms（200ms 壓縮 + 200ms 彈、最後 200ms hold-quiver 開始）。
- **視覺強化**：
  - 雙圈用 SVG `<circle>` 純筆觸（fill: none、stroke: 黃/紅、stroke-width: 8）—— 不是 div border、避免 border 算法在大圓上的鋸齒。
  - 雙圈中心**不是螢幕正中央**、要對齊 boom card 中心（rotate -2° 後的視覺中心）—— 雙圈圍邊感才對。
  - 雙圈進場時加極輕的 stroke 邊緣「閃」（用 SVG `<filter>` `feGaussianBlur stdDeviation=0`、僅在 100ms 內把 stroke 顏色從 #FFE055 → #FFD93D 過度、暗示「亮一下」、不違反 zero-blur 原則因為 stdDeviation=0）。
- **情緒目的**：雙圈爆破讓觀眾**第一次看到 ch1 的火力上限**、boom card 的雙向壓縮給「兩個想法撞在一起」的物理感。
- **敘事作用**：本拍 = ch1 唯一 climax 的第一段、決定觀眾對全片視覺火力的期待。
- **預期觀眾感受**：雙圈爆出時「噢～」（驚嘆）+ boom card 砸下時心理收緊。

---

### Step 8 · Beat 2 · `punchline-reveal`（莫名其妙 punchline）

- **敘事角色**：punchline payoff —— ch1 的笑點 + 結尾、為 ch2 留出口。
- **目前問題**：
  - JSX：beat 2 時 YellowHighlight 進場 + 包裹的 motion.div scale keyframes [0.85, 1.4, 1.0, 0.95, 1.0]（600ms）+ climax.play() 觸發 A（screen shake）+ C（overshoot）+ triggerShake()。
  - 缺點 1：punchline「靈感就這麼莫名其妙地蹦出來」**所有字一起進場** —— 但口播提示「『莫名其妙』前點下、字一邊出演講者一邊念」（per outline.md L235 cue）—— 應該做 mask-reveal 左到右、節奏配合口播。
  - 缺點 2：「莫名其妙」是 punchline 字眼、應該**比其他字稍晚出現** + 用特別的視覺強調（既有的紅色 em 是好點子但不夠）。
  - 缺點 3：punchline 揭曉後**完全靜止**、為 ch2 留出口時畫面太死。
- **升級方向**：punchline 改 mask-reveal 左到右節奏 + 「莫名其妙」單獨砸下 + punchline 揭曉後留輕度氣口。
- **建議動畫**：
  - **0.0-0.10s** YellowHighlight 黃底 box 進場（既有 motif、scale 0→1.0、100ms）。box 內部**內容暫不顯示**（先留黃底空 placeholder）。
  - **0.10-0.45s** 「靈感就這麼 ___ 地蹦出來」mask-reveal 左到右（既有規格 720ms，但**留中間空格**給「莫名其妙」、總 mask-reveal 縮短到 350ms 因為文字少了 4 字）。
  - **0.45-0.55s** 「莫名其妙」（紅色 + 大一級字級從 2.5rem → 3rem）以 `ch1/stamp-slap` **獨立進場**（scale 0→1.3→1.0、150+100ms、rotate -3° → -1° 旋進就位）。同時觸發 climax A（screen shake、既有）+ B 縮小版（halftone-burst、僅從「莫名其妙」字中心、半徑限 80px、不放射超出 box）。
  - **0.55s+** punchline 進入「輕度氣口」：「莫名其妙」四字 idle 共同 ±2px y-axis（2.5s loop）+ 「靈感」「蹦出來」前後文字保持靜止、形成對比、強化「莫名其妙」是這拍唯一在動的字。
- **建議 transition (in)**：from beat 1 → 等待 click。
- **建議 transition (out, → ch2 first step)**：左鍵 → **章節間 fade-bridge**（既有全域、500-800ms cross-fade）。在 fade-out 期間、「莫名其妙」四字最後消失（其他元素先 fade 200ms、「莫名其妙」延後 200ms、scale 0.9 + opacity 0）—— 製造「punchline 殘像」、為 ch2 進入留印象。
- **Motion timing**：黃 box 100ms / 文字 mask-reveal 350ms（100-450ms 區間）/ 「莫名其妙」進場 250ms（450-700ms）/ climax A 150ms（與 stamp 同步）/ climax B 縮小版 500ms（與 stamp 同步開始）。**總時長 700ms**（口播 L35-L37 約 6s 含 1-2s wait、剩餘 5s 給講者）。
- **視覺強化**：
  - 「莫名其妙」字下方加極輕的 wavy underline（SVG path、紅色、2px、不是純直線、模擬手寫底線）—— 強調 punchline 字眼。
  - punchline box 的 hard shadow 比平常大一級（8px → 12px）—— 因為這是 ch1 結尾、視覺重量比一般 highlight 高。
  - climax B 縮小版的 halftone-burst dots 用**黃色 #FFD93D**（既有 motif 內定義）—— 與雙圈外圈呼應、整 step 視覺色彩串起。
- **情緒目的**：「莫名其妙」獨立砸下時觀眾笑點被精準命中、idle 氣口讓笑聲落定。
- **敘事作用**：ch1 的人物姿態收束、為 ch2 的教學內容做情感對位（喜劇→理性、人物→知識）。
- **預期觀眾感受**：「莫名其妙」一出現時放聲笑、1-2s 後 ch2 進來時帶著笑意聽教學內容。

---

## §4 · Chapter Exit Transition（ch1 → ch2）

從 punchline 揭曉的笑聲後、左鍵 → 進入 ch2 ml-map（教學/理性、cream + 黑色票、低視覺密度）。**語氣切換很大**（喜劇 → 教學）、transition 要負責「換頻道」。

**建議 exit choreography**：
1. **0.0-0.2s**：punchline 元素除「莫名其妙」全部 fade-out（既有規格）。「莫名其妙」單獨保留。
2. **0.2-0.4s**：「莫名其妙」scale 0.9 + opacity 0 退場 + 同步 ch1 chapter tint（紫 `rgba(196,181,253,0.08)`）開始向 ch2 tint（黑 `rgba(0,0,0,0.04)`）過渡（View Transitions API 500ms cross-fade、per outline-visual.md §9.3）。
3. **0.4-1.0s**：ch2 s1 kicker「機器學習 · ①/3」黑底白字從上 slide-in —— 用**直線進場**（無 overshoot）、與 ch1 的所有 overshoot 動畫**刻意對比** —— 視覺上告訴觀眾「這章節要正經了」。
4. **0.8-1.0s**：完成 transition、ch2 進入正常播放。

**情緒交棒**：ch1 結尾的紫色（陰柔、白日夢）→ ch2 開頭的黑色（理性、教學）= 從「感性故事」交棒到「理性教學」、視覺色票本身完成情緒切換。

---

## §5 · Cheap-Animation Risk Log

以下 5 個方向若做過頭、會把 ch1 從「電影級」拉回「廉價特效」：

1. **不要對「心 虛」加任何 glitch / shake idle 效果**。心虛是「靜靜的羞愧」、不是「驚恐」。靜止 + 微浮動就夠。任何「字晃動」「破碎效果」都是過度炫技。
2. **不要在 s4-s7 用過多 spotlight vignette**。Spotlight 是 s8 唯一保留的「focus 武器」、s4-s7 用了就稀釋 s8 的衝擊。s4-s7 全程只用 chapter tint + grain、no spotlight。
3. **不要把 s5 / s7 思考泡泡做成連線（dashed line / SVG path）**。outline.md 原版有「思考氣球線」、但實作改成「圓點漸大」是更高級的做法 —— 抽象 > 具象。**不要把它改回連線**，連線會變幼稚。
4. **不要在 s8 boom card 加 letter-spacing 動畫或字體變形**。boom card 的字級和字距是「就位」的、額外動字會分散主視覺焦點（雙圈爆破才是焦點）。
5. **不要在任何 step 加「卡片翻轉 (3D flip)」**。3D flip 是 ch8 s4「+20→+50 翻牌」motif 的保留動作、ch1 用了會搶 ch8 的視覺權重 + ch9 callback 力道。

---

## §6 · References

- **outline 引用**：[demo/outline.md §1 ch1 coldopen L138-L238](../../../demo/outline.md)
- **script 引用**：[demo/script.md L1-L37](../../../demo/script.md)
- **visual DNA**：[demo/outline-visual.md §1 / §2 / §6 / §7 / §8 / §9 / §10](../../../demo/outline-visual.md)
- **Tier B 全域升級**：[2026-05-17-demo-visual-tier-b-upgrade-design.md](2026-05-17-demo-visual-tier-b-upgrade-design.md)
- **既有 motif / climax 模組**：
  - `src/motifs/SpotlightVignette.jsx`（s8 已用）
  - `src/motifs/YellowHighlight.jsx`（s8 已用）
  - `src/climax/useClimax.js`（s8 已用）
- **新增 ch1 motif** 需登錄到 outline-visual.md §7 Motif Library（在 implementation plan 階段執行）：
  - `motif/boom-double-ring`（首發、s8 b1）—— outline-visual.md 已收錄、需確認實作對齊
  - （可選）`ch1/stamp-slap`、`ch1/sticker-fly-in`、`ch1/thought-bubble-grow`、`ch1/hold-and-quiver` 若要在後續章節復用、需提案加入 Motif Library

---

## §7 · Spec 內部一致性自檢

- 所有 motion timing 數字皆有具體秒數（無 "適當" / "稍微" 等模糊詞）✓
- 每 beat 的 9 欄齊全（敘事角色 / 目前問題 / 升級方向 / 動畫 / transition / timing / 視覺強化 / 情緒目的 / 敘事作用 / 預期觀眾感受）✓
- 所有「目前問題」皆對應實際 JSX 行為（非臆測）✓
- 所有「升級方向」皆在 Constraint Envelope 內（無違反 Neo-brutalism 或新增禁用技術）✓
- 章內 motion motifs §2 與每 beat 動畫描述一致 ✓
- 兩個既有 outline.md 規格但 JSX 未實作的元素（s2 「敬請期待」黃 sticker + s8 boom-double-ring）皆已標記為「敘事必要」且整合進升級設計 ✓
