# 期中專案 Presentation —— Claude Code 指令書

> **檔案位置 / Working directory 約定**：
> - 本檔位置 = `<真實期中專案>/demo/prompt.md`
> - 姐妹檔 = `demo/content.md`、`demo/web_style.md`
> - **Working directory = `<真實期中專案>/` 根目錄**（不是 `demo/`！）—— 這樣訓練程式碼資料夾 `legacy/`、`sb3/`、`reasoner/`、`apprentice/` 可以用相對 working dir 的乾淨路徑引用、不用到處塞 `../`。
> - **演講相關產出物統一放 `demo/` 子目錄**（`script.md` / `outline.md` / `presentation/` / `audio-segments.json` 等）—— 詳見第六節 #14。
>
> 本檔是「**怎麼做**」的指令書、`content.md` 是「**做什麼**」的內容素材。article 來源說明見第七節開頭 ⚠️。
>
> ⚠️ **別跟 `apprentice/demo/` 搞混**：那個 `demo/` 是 apprentice 訓練子目錄（裡面有 `visualize.py`），跟根目錄的 `demo/`（演講工作目錄）是不同層級的資料夾。

---

## 一、我是誰、要產什麼

- 我是**心理學系**轉「Python AI 應用工程師職訓班」的學生。
- 期中專案：**用強化學習（RL）訓練 AI 解數獨**。
- 要產出：一份 **15 分鐘以內的互動式 HTML presentation**。
- **演講形式 = 現場手動**：我會親自在課堂上手動操作 + 口播，**不錄屏、不合成音檔、不走 `?auto=1` mode**。`narrations.ts` 仍要寫——它是 step 數的單一真相源 + 我的提詞稿。

## 二、觀眾、語氣、長度

- **觀眾**：Python 班轉職同學。**沒寫過程式背景、期中還沒學到 ML / RL**，只跟著學了 requests / BeautifulSoup / Docker。
- **語氣**：第一人稱口語 + 自嘲 + 風趣。專業術語第一次出現要在當下用日常比喻解釋（例：「reward function 就是給 AI 打分數的標準」）。
- **長度**：總長 ≤ 15 分鐘、9 章（見 `content.md` 大綱）。
- **語言**：**繁體中文**（逐字稿 + 畫面文字）。程式碼 / 變數名 / 套件名 / 演算法名保留英文。

## 二.5、聲紋 DNA（口播語氣校準錨點）

> 「風趣」是 Claude 在中文最容易翻車的維度——以下是「聲紋校準錨點」。
> 寫 `script.md` 前先讀本節、寫完每段問自己「這句聽起來像不像那邊那個人在講」。
> 違反**反面樣本**任一條 = 立刻重寫，不要狡辯。

### 正面樣本（保留這個味道，可在 script.md 直接出現或變形使用）

**A. 結構性招式**

| 招式 | 範本 | 用在哪 |
|------|------|--------|
| **「啊我不一樣」反差自貶** | 「大家剛出社會應該都是所謂的薪水小偷吧？啊我不一樣，我是個電費小偷⋯⋯」 | 開場 / 轉場 / 介紹自己角色 |
| **「我以為⋯⋯我錯了」** | 「就在我以為這樣就萬事大吉了⋯⋯**我錯了**。」（獨立短句崩盤） | 95%→0% 反轉、卡 20M 步反轉 |
| **「終極武器」戲劇話術** | 「於是我又拿出了我的終極武器——AI」 | 走投無路時的轉場 |
| **共感型自嘲（把全場拉成共犯）** | 「然後跟現代人一樣，繼續狂操 AI」 | 任何技術選型 / 工具借用的橋段 |

**B. 用詞偏好**

- **動詞重疊加重**：狂用猛用、狂操猛操、開了又開、改了又改（身體感、有戲）
- **擬人化 AI 當賤學生**：「他乾脆擺爛」「不思進取」「不想嘗試解完題目」「他終於說喜歡我了」（AI = 一個會偷懶 / 鬧脾氣的同學或對象）
- **自我標籤**：「套皮仔」「電費小偷」（自我命名、不假裝謙虛）
- **時間 / 數量具象**：「整整兩個禮拜」「狂操了 14 次」「3 個空格慢慢加到 10 個」（別用「很久」「很多次」「一些」）

**C. 慣用連接詞（口播節拍的骨架）**

然後、接下來、結果、於是、所以、最後、就在我以為⋯⋯、重點是、最扯的是

### 反面樣本（這些絕對禁止、踩到立刻重寫）

- ❌ **雙語穿插**：「hold on 一下」「let me tell you」「anyway」「so basically」
- ❌ **觀眾 hedging 問句**：「對不對？」「是不是？」「大家有沒有發現？」（口語感假、像在帶課）
- ❌ **過甜 marker**：「嗚嗚」「QAQ」「ㄎㄎ」「哭啊」
- ❌ **書面連接詞**：然而、因此、由於、儘管、縱然、即便如此、值得注意的是
- ❌ **講師 / 雞湯腔**：「我們可以發現」「值得一提的是」「這讓我學到」「原來人生跟⋯⋯一樣」
- ❌ **偽口語 AI 腔**：「結果咧～大翻車」「好兄弟 hold 住」「家人們」「絕了」（中國抖音腔、不是台灣口語）
- ❌ **真道歉自貶**：「不好意思我隨便講」「我可能講得不太好」（保留自嘲、刪除真道歉——自嘲是 confidence，道歉是 uncertainty）

### 三句檢查（每段寫完問一次）

1. **這句我會在課後跟同學吃便當時講嗎？** 不會 → 重寫。
2. **這句中了上面任何反面樣本的詞嗎？** 中一個 → 刪掉重來。
3. **戲劇化 setup 後面的崩盤句夠不夠短、夠不夠 punchy？**（範本：「⋯⋯我錯了」、「⋯⋯0 分」、「⋯⋯結果他擺爛」、「⋯⋯整整兩個禮拜白費」）

## 三、成功 criteria

雙標並重，**A + B 兩條都要達**：

- **A · 同學聽懂核心概念**
  講完一週後，同學能說「啊 RL 就是 AI 試錯」「AI 會作弊背 shortcut」「cold start 要反過來破解」。
- **B · 同學被個人故事吸引**
  講完同學記得「那個從心理學跨來的、跟 AI 談戀愛的傢伙」。

❌ **不追求**：老師/評審加分、密集數據顯擺、技術深度炫技。

⚠️ **取捨規則**：當技術深度跟情緒故事打架時，**保 B、技術走「夠用就好」**。Ch 5–8 的 📌 技術背景區塊裡細節**只挂在畫面當素材，不念進口播稿**。

## 四、工具與素材

1. **`web-video-presentation` skill**：透過 Claude Code 的 `Skill` 工具呼叫（全域已安裝）。**嚴格按它的 `SKILL.md` 工作流走**，所有硬節點不可跳過：
   - Phase 1.2 產出 `script.md` + `outline.md` 後停在 **Checkpoint Plan**。
   - 第 1 章主線程做完後**停下來等使用者驗收**才繼續。
   - Phase 2 結束停在 **Checkpoint Audio** —— **使用者已選現場手動演講，回答「不合成」直接進 Phase 4**。
   - 每章交付前走 `references/CHAPTER-CRAFT.md` 完工自檢。
2. **`./demo/web_style.md`**：視覺風格全部走這套 **Neo-brutalism**。**不准修改本檔**。
   - scaffold 時挑 `monochrome-print` 當底（黑白基調最接近）。
   - 整份覆蓋 `presentation/src/styles/tokens.css`，把 `web_style.md` 的色票翻譯成 tokens：
     - `--shell` / `--surface`：`#FFFDF5`（cream）
     - `--text`：`#000000`（純黑，不要灰階）
     - `--accent`：`#FF6B6B`（hot red）
     - `--accent-soft`：`#FFD93D`（vivid yellow）
     - `--accent-glow`：`#C4B5FD`（soft violet）
     - `--font-display-en`：`Space Grotesk`（weights 700 / 900）
     - `--font-display-cn`：`Noto Sans TC`（weight 900，繁體中文 fallback）
     - `--rule`：4px solid black（不准 1px）
   - 每章 CSS **只用 token 寫顏色/字體**，動畫/版面用 Neo-brutalism 結構性手法。下列是**視覺工具箱（按需挑、不是每章 checklist）**：黑邊厚框、零模糊 hard offset shadow、sticker 旋轉層疊、文字描邊、halftone / grid / noise 紋理底。**每章只主打 1–2 種手法，不要全部堆疊**——堆滿等於沒主視覺。具體 token / 屬性值由 Claude 看 `web_style.md` 自行對應。
3. **`./demo/content.md`**：演講敘事素材池（hook 庫、9 章大綱、📌 技術細節池）。**Phase 1.2 寫 `script.md` / `outline.md` 時的主要敘事來源**。
4. **訓練程式碼（四個版本）**：根目錄下 `legacy/`、`sb3/`、`reasoner/`、`apprentice/`。讀其 README / HISTORY / 主訓練檔，**驗證 `content.md` 📌 技術背景的數字、檔名、現況仍正確**——數字不准用 content.md 抄、要從程式碼真實讀。
5. **Pygame visualizer**：**`apprentice/demo/visualize.py`**（目前是 pygame 桌面版、**pygbag WASM 編譯尚未完成**——這是 ch 8 整合的前置工作，詳見第六節 #7）。
6. **題目資料來源**：https://www.websudoku.com/ + 自架 proxy 池爬蟲。

## 五、視覺與內容紅線

**Neo-brutalism + SKILL 兩邊都要過：**

- ✅ `border-4` 黑邊、hard offset shadow（4–16px、零模糊）、cream `#FFFDF5` 底、accent 紅黃紫、Space Grotesk 900 + Noto Sans TC、sticker 旋轉、halftone/grid/noise 紋理。
- ✅ 1920×1080 16:9 固定舞台、隱形 chrome、step driven、`narrations.ts` 是 step 數真相源。
- ✅ 每章必須有 CSS/SVG/Canvas 視覺演示。
- ❌ 紫粉 / 藍紫對角漸層、emoji 當 icon、假數據 / 假 logo、整章單一入場動畫、`blur()` / `backdrop-blur`、平滑漸層、`rounded-md/lg`、灰階（`#333` / `#666`）。
- ❌ 頁眉、頁腳、頁碼、品牌條。

**Claude 不該做的事（反例清單）：**

- ❌ **把 hook 當笑話硬丟**：hook 要融進敘事節拍。戀愛 hook 配合該版本當下訓練心情融進去（legacy 曖昧期 / sb3 假性甜蜜 / reasoner 冷戰 / apprentice 磨合）——詳見 `content.md` 1.1。
- ❌ **把 📌 技術背景的細節念進口播稿**：那些是給畫面挂的、不是給觀眾聽的。`SubprocVecEnv`、`net_arch={"pi":[128],"vf":[128,128]}`、`TECH_BONUS` 數值表這種詞**禁止出現在 `script.md`**。
- ❌ **編程式碼數字**：20.3M、+50、`target_empty=3`、檔名⋯⋯一律從 `legacy/sb3/reasoner/apprentice/` 真實程式碼讀，不准照 content.md 抄。
- ❌ **用 content.md 文字當口播稿**：content.md 是書面語，口播稿要重寫成口語節拍（句長 ≤ 30 字、避免從屬子句、口頭 marker「對」「然後」「結果咧」之類自然出現）。
- ❌ **單獨開一章講 meta 教訓**：那條主軸是隱性穿插，不是雞湯一章。
- ❌ **改了 `script.md` 卻沒同步 `narrations.ts` / `.tsx`**：使用者**會多次改 script.md**——每次改完**必須同步更新對應章節的 narrations.ts step 文字 + .tsx step 條件 + 畫面文字**，讓畫面跟 script 對齊。詳見第六節 #12。
- ❌ **挂偽造的訓練曲線截圖**：`legacy/` / `sb3/` / `reasoner/` 沒有歷史 log（見 `content.md` 二、素材可用性盤點）——ch 5–7 訓練曲線一律用 CSS / SVG 概念示意動畫，**不准生成假 tensorboard 截圖、不准用 placeholder 圖片冒充真實 log**。
  - ⚠️ **這條是整份檔最常被忽略的紅線**——畫面氣勢不夠時 Claude 容易自動生成假 log。每章 outline 階段就要決定「真實素材 / 概念示意」二選一、不要 fallback 到「先放截圖」。
- ❌ **試圖改 `web-video-presentation/` skill 或 `web_style.md`**：這兩個是供參考的標準。需要新主題就在 scaffolded 出來的 `presentation/` 裡覆蓋 `tokens.css`，不要動 skill 本身。

## 六、我替使用者做的判斷（可逆 override 區）

| # | 決策 | 內容 |
|---|------|------|
| 1 | 演講形式 | **現場手動**——不錄屏、不合成音檔、不走 `?auto=1` |
| 2 | Skill 部署 | **全域 Skill 機制**——透過 `Skill` 工具呼叫，不寫死路徑 |
| 3 | 成功 criteria | **A + B 雙標**——技術 vs 故事打架時保 B |
| 4 | 章數 / 時長 | **9 章 / 15 分鐘**——**明確 override** SKILL.md「合理判斷每章 30~60s」（那條是 B 站短影片場景、不適用 15 分鐘演講） |
| 5 | scaffold 底主題 | `monochrome-print`（黑白排印氣質最接近 Neo-brutalism） |
| 6 | 視覺化型態 | step 推進 + 動畫 + Ch 08 末段 visualizer，**不嵌完整數獨遊戲**（15 分鐘塞不下、會偏離 RL 主題） |
| 7 | Ch 08 visualizer 整合 | **主路線：pygbag 編譯 → WASM → iframe**（保留現場 live AI inference 的氣勢）。入口 `apprentice/demo/visualize.py`。<br>**退路：OBS 錄 30s–60s mp4**——**只在 pygbag hard deadline 過了還跑不出來才啟用**（不預錄）。<br>**啟動 timing：Phase 1 scaffold 結束就開做、跟 Phase 2 寫稿平行**——不要拖到 Ch 8 才開工。<br>⚠️ **技術成本提醒**：`visualize.py` 走 SB3/PyTorch inference，pygame 邏輯 pygbag 編譯不難，但 WASM 環境裡 SB3 不能直接跑、PyTorch 要轉 ONNX + onnxruntime-web——實際工作量可能 3–5 天（不是 1 小時）。<br>**Hard deadline = Phase 2 寫到 Ch 4 之前**：這天還跑不出 iframe = pygbag 路線停手、改 OBS 錄 mp4。<br>**禁止**：演講者手動切桌面 pygame、Phase 2 開到 Ch 8 才開始處理。 |
| 8 | 正妹 hook | **保留**——這是整片的氣口、跟 Neo-brutalism 反主流氣質匹配，不要消毒 |
| 9 | 戀愛 hook | 散到 ch 5–8 每章開頭一句，配該版本訓練情緒色（曖昧 / 誤會 / 冷戰 / 磨合） |
| 10 | 時間分配 | ch 1–4 鋪陳每章 ~1–1.5 分；ch 5–8 重構每章 ~2–3 分；ch 8 拉到 ~3 分塞 visualizer；ch 9 收尾 ~1.5 分；總計 ~15 分 |
| 11 | 章節銜接主旋律 | **雙主線編織**——戀愛情緒色（曖昧/誤會/冷戰/磨合）當主旋律 + 教訓編號（教訓一/二/三/四）當邏輯骨架，**ch 5–8 每章章頭同時帶兩條線**，ch 9 合流。詳見 `content.md` 1.3 |
| 12 | Script ↔ HTML 對齊 | 使用者**會多次改 `./demo/script.md`**——每次改完**必須同步更新對應章節的 `narrations.ts`（提詞稿真相源）+ `<Chapter>.tsx` 的 step 條件 + 畫面文字**。**「同一句話 hardcode 兩處要改」這個 React 結構問題如何避免**（直接引用 narrations / 抽共用常數 / 其他），由 Claude 在 scaffold 時自行決定，不在此規範 |
| 13 | 歷史 log 可用性 | `legacy/` / `sb3/` / `reasoner/` **沒有歷史訓練 log**——ch 5–7 訓練曲線只能畫**概念示意動畫**（CSS / SVG），不挂真實截圖。只有 `apprentice/` **有 tensorboard + visualizer (`apprentice/demo/visualize.py`)** 可挂真實素材，是 ch 8 視覺氣勢最強的原因。詳見 `content.md` 二、素材可用性盤點 |
| 14 | 演講工作子目錄 | **所有 web-video-presentation 相關產出物統一放 `./demo/` 子目錄**（不要污染真實期中專案根目錄）。具體：`./demo/script.md`、`./demo/outline.md`、`./demo/presentation/`（scaffold 出來的 Vite 專案）、`./demo/audio-segments.json`、`./demo/public/audio/`（若有）。Working dir 仍是真實期中專案根目錄——這樣訓練程式碼路徑（`legacy/`、`sb3/`、`reasoner/`、`apprentice/`）保持乾淨無 `../`。Scaffold 指令是 `bash <skill>/scripts/scaffold.sh ./demo/presentation --theme=monochrome-print`（**注意 `./demo/presentation`、不是 `./presentation`**） |

## 七、Phase 1 啟動 checklist

> ⚠️ 這份 `prompt.md` + `content.md` **充當 `web-video-presentation` skill Phase 1.1 的 article 來源**。Phase 1.1 **直接判定『有 article』**——不用反問使用者「你有 article 嗎」，直接進 Phase 1.2。

按順序執行：

1. **讀 `./demo/content.md`**——拿故事敘事 / Hook 庫 / 9 章大綱 / 📌 技術背景。**特別注意「二、素材可用性盤點」**——它決定 ch 5–8 視覺挂真實素材還是概念示意，是整份檔最重要的非顯性策略。
2. **讀四個訓練版本資料夾**——`legacy/`、`sb3/`、`reasoner/`、`apprentice/` 的 README / HISTORY / 主訓練檔——**驗證 `content.md` 📌 技術背景的數字現況仍正確**。發現有過時就以程式碼為準，告訴使用者哪幾條要更新。
3. **按 SKILL.md Phase 1.2 一次產出 `./demo/script.md` + `./demo/outline.md`**（**注意路徑：產出物放 `./demo/` 子目錄**，見第六節 #14）：
   - `./demo/script.md`：B 站口語風 + 第一人稱 + 自嘲 + 繁體中文。**口播稿絕對不含 📌 區的技術術語**。
   - `./demo/outline.md`：9 章切分 + 每章 step 數 + 每章首段抽**信息池**（從 `./demo/content.md` 各章 📌 區 + 真實程式碼資料夾抽）+ 末尾素材清單。
4. **停在 Checkpoint Plan**——按 SKILL.md 跟使用者對齊**這次客製化擴成 6 件事**（稿子 / outline / 主題 / 素材 / 開發模式 / **章節銜接口語節拍範例**）。第 6 件 = 你要先生 ch 5 + ch 6 章頭的口語節拍實例給使用者看（雙主線編織怎麼落地，見 `content.md` 1.3），**不要自己直接進 Phase 2**。
5. **scaffold 之前**：先確認使用者要用哪個開發模式（A 逐章 / B 順序 / C 並行）。scaffold 命令是 `bash <skill-path>/scripts/scaffold.sh ./demo/presentation --theme=monochrome-print`（**`./demo/presentation`、不是 `./presentation`**，見第六節 #14）。scaffold 完成後**整份覆蓋** `./demo/presentation/src/styles/tokens.css` 走 Neo-brutalism（tokens 列表見本檔第四節第 2 條）。
6. **第 1 章主線程做完後強制停下來等使用者驗收**——不可跳過。
7. **Phase 1 scaffold 結束、立刻啟動 visualizer 前置作業**（跟 Phase 2 寫稿平行、不互卡）：
   - **第一步**：讀 `apprentice/demo/visualize.py`、本機 pygame 跑得起來、模型 checkpoint 路徑正確。
   - **第二步（主路線 · pygbag）**：評估 inference pipeline 改寫工作量（SB3 → ONNX + onnxruntime-web）、開始改寫 + 編譯。
   - **第三步（hard deadline）**：**Phase 2 寫到 Ch 4 之前**還跑不出可用 iframe → 停手、走退路。別繼續燒時間。
   - **退路**：走到這步才啟用——OBS 錄 30s–60s mp4 放 `./demo/presentation/public/video/visualizer.mp4`、Ch 8 按鈕觸發 `<video>`。
