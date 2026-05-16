# Video Outline

> **主題**：`monochrome-print`（Neo-brutalism 黑白印刷氣質，整份覆蓋 `tokens.css` 走 cream/black/hot-red/yellow/violet 色票，詳 `prompt.md` §四 #2）
> **總時長**：約 12 分鐘口播 + 30~60s visualizer（總 ≤ 15 分）。口播 ~3000 字 ÷ ~3.5 字/秒（含口語停頓 / 戲劇拉長）
> **章節數**：9 章 / 57 步（含 viz step）
> **基石**：本 outline 對齊 `demo/script.md`（使用者個人化重寫定稿）。每章信息池 anchor 主要回 script.md 行號；補充技術 anchor 回 content.md / 真實程式碼。

---

## 1. coldopen — 心虛開場 · 心理學系背景 · 捷運靈感（6 steps · ~60s）

**信息池**（chapter agent 按需挂角標 / 副標 / sticker 文字）：
- 自我揭露：「**心虛**」「報告太不正經、請各位同學和老師多包涵」—— 來源 `script.md` L1
- 背景標籤：「**心理學系畢業**」（為後段 RL / 腦科學 / plasticity 鋪墊）—— 來源 `script.md` L5
- 主題揭露：「訓練出一個 AI、讓他自己學會如何解數獨」—— 來源 `script.md` L9
- 場景具象：「搭捷運來上學、正大光明地看著對面的正妹發呆」—— 來源 `script.md` L15
- 影片 anchor：**Code Bullet** flappy bird YouTuber 影片靈感氣泡（注意：是 flappy bird 不是踩地雷）—— 來源 `script.md` L19 + `content.md` §1.1
- 場景具象：「當兵時大家很無聊、沒有手機、唯一能玩的就是解數獨」—— 來源 `script.md` L25
- punchline 金句：「靈感就是這麼莫名其妙地蹦出來」—— 來源 `script.md` L37

**開發計畫**：

- step 1 (~10s) — 全螢幕「心虛」表情 sticker + 「報告太不正經、請各位同學和老師多包涵」字幕
- step 2 (~8s) — 「我是心理學系畢業的」標籤 sticker + 「敬請期待」（埋下後段 RL / 腦科學 / plasticity 的伏筆）
- step 3 (~10s) — 主題揭曉：「訓練 AI 解數獨」hero 大字 + 「我的期中主題」副標
- step 4 (~12s) — 過場「靈感哪來」+ 捷運場景 + 「正大光明地看著對面的正妹發呆」字幕 + 第一張 sticker（正妹）
- step 5 (~10s) — 第二張 sticker（Code Bullet flappy bird 影片氣泡）疊進來 + 「繼續發呆看著正妹」 + 第三張 sticker（當兵解數獨）疊進來
- step 6 (~10s) — 三張 sticker → Boom 撞在一起 → 第四張「**訓練 AI 解數獨**」全螢幕獨佔 + punchline 金句「靈感就是這麼莫名其妙地蹦出來」（cream 底、accent yellow 字）

口播節選：
> 「我是心理學系畢業的⋯⋯某天我一如往常搭捷運來上學，正大光明地看著對面的正妹發呆⋯⋯Boom，就這樣在我腦袋裡莫名其妙地把兩個想法結合在一起。」

---

## 2. ml-map — 機器學習地圖（4 steps · ~50s）

**信息池**：
- 三大塊：**supervised / unsupervised / RL**—— 來源 `script.md` L49-67
- 日常比喻：「看著答案抄筆記」「自己分類整理（折衣服）」「試錯加獎懲（訓練狗握手）」—— 來源 `script.md` L51-65
- 名人事件 anchor：**AlphaGo 打敗世界圍棋王**（給 RL 加重）—— 來源 `script.md` L67
- cliffhanger：「那 ChatGPT 跟 Claude 又是哪一招？」—— 來源 `script.md` L71

**開發計畫**：

- step 1 (~14s) — 第一塊揭示：**supervised** + 「看著答案抄筆記」+ 「老師給你題目跟答案、你硬背」插畫
- step 2 (~13s) — 第二塊揭示：**unsupervised** + 「自己分類整理」+ 折衣服圖示
- step 3 (~15s) — 第三塊揭示：**RL** + 「試錯加獎懲」+ 訓練狗握手圖示 + **AlphaGo** 標籤 sticker（accent red 底、黑邊、微旋轉）
- step 4 (~8s) — 全螢幕單句 cliffhanger「那 ChatGPT 跟 Claude 又是哪一招？」（換語氣 / 換主題）

口播節選：
> 「機器學習的訓練方法主要分三塊。supervised、unsupervised、RL⋯⋯當年 AlphaGo 打敗世界圍棋王、用的就是這招。」

---

## 3. llm-vs-rl — ChatGPT 跟 Claude 在哪？（3 steps · ~35s）

**信息池**：
- LLM 路線：**supervised + RLHF**——「把整個人類網路寫過的東西全部讀一遍 + 人類教他怎麼回」—— 來源 `script.md` L75-77
- 對比 anchor：「**LLM = 模仿**」 vs 「**我這套 = 自己摸出規則**」—— 來源 `script.md` L83-89
- 場景比喻：「把 AI 丟進一個他什麼都不知道的房間」—— 來源 `script.md` L89
- cliffhanger：「OK 所以我要走純 RL。第一步是找資料」—— 來源 `script.md` L93-95

**開發計畫**：

- step 1 (~14s) — 左欄「LLM」hero + 「supervised + RLHF」副標 + 「把整個人類網路寫過的東西全部讀一遍」標語
- step 2 (~14s) — 同畫面右欄「我的 AI」hero + 「**LLM 是模仿** vs **我要 AI 自己摸出規則**」強對比 + 房間 / 門 sticker
- step 3 (~7s) — 全螢幕單句「OK 所以我要走純 RL。第一步是找資料」

口播節選：
> 「LLM 是模仿——模仿人類寫過的字。我這套不一樣——我要把 AI 丟進一個他什麼都不知道的房間，讓他自己摸出規則。」

---

## 4. data-hunt — 找資料：從 Kaggle 到爬蟲（4 steps · ~50s）

**信息池**：
- 資料來源 anchor：**Kaggle**（先去）→ **websudoku.com**（後來爬）—— 來源 `script.md` L99 + L117
- 拒絕理由 anchor：「題目+答案 = supervised 路線」與「我要 AI 自己摸出規則」衝突 —— 來源 `script.md` L105-107
- 戰略 anchor：「終極目標霸榜各數獨網站 → 題目來源得從那些網站來」—— 來源 `script.md` L111-115
- 爬蟲 punchline：「**這個受害者**」+ 「沒有現代防爬蟲機制、簡簡單單被攻破」—— 來源 `script.md` L117-121
- 反爬 anchor：被封 IP → **proxy 池**（類似 VPN、一次擁有好幾萬個 IP）—— 來源 `script.md` L125-133

**開發計畫**：

- step 1 (~12s) — Kaggle 標籤 sticker + 「題目+完整答案 整理好的資料集」+ 「但問題來了」叉叉動畫覆蓋
- step 2 (~11s) — 「supervised 路線拒絕」紅 stamp + 「我要 AI 自己摸出規則」對比
- step 3 (~14s) — 「終極目標：去每個數獨網站霸榜」+ websudoku URL sticker（「**這個受害者**」標籤）+ 「簡簡單單被我攻破」
- step 4 (~13s) — 「才爬到 20 題就被封 IP」紅警示 + proxy 池視覺示意（類似 VPN、好幾萬個 IP 切換動畫）

口播節選：
> 「Kaggle 這個平台⋯⋯但問題來了。題目加答案這種格式、就是 supervised 路線⋯⋯於是我找到了 websudoku.com 這個受害者⋯⋯我請出了反反爬蟲的工具 - proxy。」

---

## 5. legacy — 一句搞定的幻想 → 800 多行單檔（4 steps · ~50s）

**信息池**：
- 戲劇崩盤句：「我以為⋯⋯**結果我錯了**」—— 來源 `script.md` L141-145
- 程式碼 anchor：**`legacy/app/sudoku/torch_agent.py` 一檔 838 行**（畫面值；口播照 script 走「800 多行」）—— 來源 `script.md` L151 + 真實程式碼 `legacy/app/sudoku/torch_agent.py`
- debug 痛點 anchor：「每改一個地方都東倒西歪、我自己都看不懂、debug 成本爆炸」—— 來源 `script.md` L153
- 第一件學到 anchor：「**不能再這樣偷懶全靠 AI 了。架構、演算法都得自己先想清楚、再請 AI 分工**」—— 來源 `script.md` L157-159
- 過渡 anchor：「放棄這個版本、轉而當個套皮仔」—— 來源 `script.md` L163

**開發計畫**：

- step 1 (~13s) — 「我那時候還很天真」+ prompt 對話框「**幫我寫一個訓練 AI 解數獨的程式**」+ 獨立崩盤句「⋯⋯**結果我錯了**」（黑底白字、微旋轉）
- step 2 (~14s) — 「**800 多行的單一檔案**」程式碼 sticker（單檔等比例縮小成一坨黑色文字塊）+ 角標「`torch_agent.py`」+ 「什麼都塞在裡面」
- step 3 (~13s) — debug 痛點：「每改一個地方都東倒西歪」+ 紅色叉叉飛來飛去動畫 + 「debug 成本爆炸」punchline
- step 4 (~10s) — 第一件學到 hero 標語：「**架構、演算法都得自己先想清楚、再請 AI 分工**」+ 過渡「放棄這個版本、轉而當個套皮仔」

口播節選：
> 「不如我丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude⋯⋯結果我錯了。他產出了一個 800 多行的單一檔案⋯⋯不能再這樣偷懶全靠 AI 了。」

---

## 6. sb3 — 套皮仔 + 戀愛 hook a · 新女生加分到備胎（7 steps · ~70s）

**信息池**：
- 套皮仔 anchor：「社群已經有現成的 Python 工具箱、負責訓練的數學邏輯底層架構」—— 來源 `script.md` L167-169
- 戲劇崩盤句：「正當我以為成了套皮仔、就能成功訓練 AI⋯⋯**我又錯了**」—— 來源 `script.md` L171-173
- 計分策略 anchor：「**只要他填對一格就給分數**」—— 來源 `script.md` L177
- **戀愛 hook a 出場**：「就像剛認識新女生、每次聊天你都覺得對方也喜歡你、一直給你加分」—— 來源 `script.md` L181-183
- 瓶頸 anchor：「AI 只拿那些必拿的固定分數就不思進取、一直沒辦法完整解出一道題」—— 來源 `script.md` L187
- **戀愛 hook a 收**：「這個女生只把你當**備胎**、看似有進展、結果什麼都沒發生」—— 來源 `script.md` L189
- 揭穿 anchor：「AI 學會了**偷吃步**——只拿必拿的分數、就以為這樣行了」+ 「**計分標準寫錯了、AI 就會找漏洞作弊**」—— 來源 `script.md` L195-199

**開發計畫**：

- step 1 (~10s) — 過渡：「正當我以為成了套皮仔⋯⋯」 + 獨立崩盤句「**⋯⋯我又錯了**」（黑底白字、微旋轉）
- step 2 (~9s) — 套皮仔策略：「社群現成 Python 工具箱」標籤 sticker + 「**只要他填對一格就給分數**」計分表 hero
- step 3 (~12s) — **戀愛 hook a 出場**：「剛認識的新女生」sticker + 加分動畫（+ + + 浮起）+ 「聊天都覺得對方也喜歡你」
- step 4 (~10s) — 「AI 得分急遽增長」曲線爬升（CSS / SVG 概念示意）+ 「一直給你加分」對位
- step 5 (~12s) — 瓶頸：曲線卡住 + 「**拿那些必拿的固定分數就不思進取**」+ 「一直沒辦法完整解出一道題」
- step 6 (~10s) — **戀愛 hook a 收**：「**備胎**」紅 stamp sticker（微旋轉）+ 「看似有進展、結果什麼都沒發生」
- step 7 (~7s) — 揭穿：「**偷吃步**」紅 stamp + 「**計分標準寫錯了、AI 就會找漏洞作弊**」hero + 過渡進 ch7

口播節選：
> 「結果後面開始遇到瓶頸 - AI 只拿那些必拿的固定分數就不思進取了⋯⋯換句話說，這個女生只把你當備胎⋯⋯計分標準如果寫錯了，AI 就會找漏洞作弊。」

---

## 7. reasoner — 重寫獎勵 + 13 招 + 戀愛 hook b · 老油條陷阱（8 steps · ~130s）

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

- step 1 (~11s) — 過渡：「我只好整個計分獎勵系統重寫」hero + 「核心想法只有一個」副標
- step 2 (~14s) — 顛倒驗證宣告：「**用人類玩數獨的解題技巧、反過來驗證 AI 的每一步**」full-screen 標語
- step 3 (~19s) — **13 招大階梯**：13 張小 sticker 從低（naked single / hidden single）排到高（X-Wing / Swordfish / **XY-Wing**），**X-Wing 跟 XYZ-Wing 最大、最華麗**（accent yellow / accent violet 底、黑邊、微旋轉）
- step 4 (~17s) — 舊 vs 新對比動畫：左「填對一格就給分」（只有一招亮）vs 右「**可以用哪一招解釋**」（每張技巧都可以亮、高招分數更高）
- step 5 (~13s) — Action 擴增：「多了**劃掉這格不可能是這個數**」 + 消去動作示意動畫 + 「消去類技巧才能展示出來」
- step 6 (~14s) — 慘烈結果：「練了 **兩千多萬次**」大字 + 「完整解出一道題的機率還是 **0**」紅底 hero
- step 7 (~22s) — **戀愛 hook b 全面展開**：「老油條女生陷阱題」sticker（微旋轉）+ 「**和你媽一起掉進水裡**」考題 sticker + 「該不該運動：說要 → 嫌她胖 / 說不用 → 不關心」兩個答案都錯的陷阱箭頭
- step 8 (~20s) — 死結：「AI 永遠拿不到整題解完那個大獎」+ 「就跟我不知道陷阱題的正確解答一樣」+ 過渡「反向思考」鋪墊

口播節選：
> 「我去 Google 一堆數獨高手的招——naked single、hidden single、X-Wing、Swordfish、XY-Wing⋯⋯一共 13 招⋯⋯練了兩千多萬次——完整解出一道題的機率還是 0⋯⋯每道都是陷阱題。」

---

## 8. apprentice — 反向課程 + visualizer（7 steps · ~75s + visualizer 30~60s）

> 本章為視覺高潮 + 整片唯一可挂真實 tensorboard 截圖（使用者表示有素材可挂）+ 唯一現場可互動 visualizer

**信息池**：
- 反向思考 anchor：「**我把題目反過來給他**——一開始只給 3 格空的盤面、90% 都填好了、他一定解得出來」—— 來源 `script.md` L273-279
- 反向課程 anchor：「能穩定解、我再加一格空、再加一格⋯⋯讓難度跟著他的能力走」—— 來源 `script.md` L281-285
- 破關獎勵翻牌 anchor：「我同時把破關獎勵調更大——從 **+20 拉到 +50**」+ 「讓完成整題的訊號更明確、誘惑超過固定刷取部分分數的招數」—— 來源 `script.md` L287-291 + 真實程式碼 `reasoner/env/reward_computer.py:8 (=20)` + `apprentice/env/reward_computer.py:8 (=50)`
- 突破 anchor：「從 3 個空格慢慢加到 10 個——他**終於開始解出整題**」—— 來源 `script.md` L293
- 真實素材 anchor：**tensorboard 截圖**（勝率曲線 / curriculum step 圖）—— 使用者確認有素材可挂
- visualizer 大按鈕設計：cream 底 + 粗黑邊 + 強陰影 + accent red 字 + sticker 微旋轉、「點我看 AI 即時解數獨 →」—— 來源 `prompt.md` §六 #7

**開發計畫**：

- step 1 (~10s) — 過渡：「反向思考——先解簡單的陷阱題答案、之後從容面對老油條」+ 「AI 也是、我把題目反過來給他」hero
- step 2 (~12s) — 反向課程登場：盤面動畫「**只有 3 格空**」（90% 已填）+ 「他一定解得出來」標語
- step 3 (~12s) — 反向課程示意：盤面從 3 空 → 4 空 → 5 空 → 7 空 → 10 空（一格一格揭示）+ 「讓難度跟著他的能力走」
- step 4 (~10s) — 數字翻牌：「**+20 → +50**」大字翻牌動畫（破關獎勵調更大）+「誘惑超過刷部分分數的賤招」副標
- step 5 (~12s) — **真實 tensorboard 截圖**挂進來（勝率曲線 + curriculum step 圖）+ 「從 3 個空格慢慢加到 10 個——他**終於開始解出整題**」
- step 6 (~9s) — 過渡：「光講不夠看。給大家看一下 AI 即時解數獨的題目」hero
- step 7 (~10s + visualizer 30~60s) — visualizer 大按鈕獨佔整屏：cream 底 + 粗黑邊 + 強陰影 + accent red 字「**點我看 AI 即時解數獨 →**」+ 微旋轉 / 按下後 iframe（pygbag 主路線）或 `<video>`（OBS 退路）播放

口播節選：
> 「我的解法是把題目反過來給他——一開始只給 3 格空的盤面⋯⋯他能穩定解、我再加一格空⋯⋯破關獎勵從 +20 拉到 +50⋯⋯他終於開始解出整題。」

---

## 9. callback — AI 也在訓練我（14 steps · ~190s）

> **結尾長章例外**：超過 OUTLINE-FORMAT 建議的「每章 3~8 步」上限，因 script.md L303-375 結尾為壓軸大段、無法切兩章保持節奏。chapter agent 實作時可自行決定要不要拆 micro-step。

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
- **MBTI 自我故事 anchor**：「我真的是一個**極度的 I 人**、之前測 MBTI 我有 **100% 的時間都偏向 I 人**」「大家可能覺得我在講幹話、明明我很 E」—— 來源 `script.md` L359-361
- **業務工作變 E anchor**：「我後來逼自己跳脫舒適圈、去做了一份**業務工作**、天天逼自己跟陌生人講話、才慢慢變得比較 E」—— 來源 `script.md` L363
- 不被擊敗 anchor：「遇到不會回答的魔王陷阱題沒有關係、我們只要從**挫敗中學習**就行了。但是不要停滯不前——跟一個女生聊天、結果**人生第一次的外向、換來一輩子的內向**」—— 來源 `script.md` L367-369
- 職場祝福 anchor：「繼續嘗試跟其他女生聊天——不是每個女生都那麼老油條。也祝大家未來在職場上能夠保有同樣的精神——**不被挫敗給擊敗**」—— 來源 `script.md` L371-373
- **電費小偷結尾笑話 anchor (verbatim)**：「最後再補個笑話 - 想必大家未來出職場後都是薪水小偷。但我不一樣，我是**電費小偷**、我這**兩個月**一直用班上的電腦瘋狂訓練我的 AI」—— 來源 `script.md` L375

**開發計畫**：

- step 1 (~10s) — 過渡：「AI 還在訓練中⋯⋯**我跟對方還在磨合期**」+ 「最後我想跟大家講一件事」hero
- step 2 (~14s) — 核心金句獨佔整屏：「**這兩個月、我不只在訓練 AI、AI 也在訓練我**」（cream 底、accent red 大字、黑邊）
- step 3 (~12s) — RL 對等動畫：左「腦科學 RL」/ 右「AI 訓練 RL」+ 中間 `=` 大字 + 「**其實是同一件事**」
- step 4 (~10s) — 飛機鳥 sticker：「AI 在模仿人類——就像飛機是人類模仿鳥類才造出來」+ 飛機 + 鳥 並置 sticker
- step 5 (~16s) — 戀愛 a callback：「追一個人」雙欄對照「回訊息 +」/「已讀不回 −」+ 大腦 sticker + 「reward 反覆重塑要不要繼續當舔狗」+ 「**跟 AI 訓練一模一樣**」紅底結尾
- step 6 (~18s) — 戀愛 b callback：「以為穩了結果魔王關卡」+ 四個考題 sticker 並排（「前女友跟我比誰比較好」「你心中的女神是誰」「你喜歡我哪裡」「猜猜看今天我哪裡不一樣」）
- step 7 (~8s) — plasticity 引出：「最後再跟大家分享一個我最喜歡的心理學底層概念——**大腦可塑性 plasticity**」hero
- step 8 (~12s) — plasticity 三欄對位：「AI 沒天生會解數獨」/「你出生不會講話」/「你不是天生會跟人相處」→ 中央「**一樣**」大字
- step 9 (~12s) — plasticity 機制：「每改一次 reward function、每談一場戀愛、每學一個新東西——**每次都把我們重新塑造一次**」標語
- step 10 (~14s) — **MBTI 自我故事**：「我真的是一個**極度的 I 人**」+ **「INFJ」**標籤 sticker + MBTI 圓餅「100% I」視覺
- step 11 (~14s) — **業務工作變 E**：「逼自己跳脫舒適圈、做了一份**業務工作**」業務工作 sticker + 「天天逼自己跟陌生人講話、才慢慢變得比較 E」對照動畫
- step 12 (~16s) — 不被擊敗：「從挫敗中學習就行了」hero + **警語 sticker**「**人生第一次的外向、換來一輩子的內向**」（黑底紅字、微旋轉）
- step 13 (~12s) — 職場祝福：「繼續嘗試跟其他女生聊天——不是每個女生都那麼老油條」+ 「祝大家未來在職場上**不被挫敗給擊敗**」hero
- step 14 (~22s) — **電費小偷結尾笑話 verbatim**：「最後再補個笑話」+ 「想必大家未來出職場後都是**薪水小偷**」（對位 sticker）+ 「但我不一樣、我是**電費小偷**」（電費小偷大字 sticker、accent red 底、微旋轉、final punchline）+ 「我這兩個月一直用班上的電腦瘋狂訓練我的 AI」收尾

口播節選：
> 「這兩個月、我不只在訓練 AI、AI 也在訓練我⋯⋯AI 沒有天生會解數獨、跟你出生不會講話、跟你不是天生就懂怎麼跟人相處——一樣⋯⋯我是電費小偷、我這兩個月一直用班上的電腦瘋狂訓練我的 AI。」

---

## 素材清單

> 標注規則：✓ 已就位（路徑可指）/ ⚠️ 待製作 / 📦 純 CSS 構造（不需要外部素材）

### 1. coldopen
- 📦 「心虛」表情 sticker（純 CSS / SVG 構造）
- 📦 心理學系背景標籤 sticker
- 📦 4 張靈感串聯 sticker（正妹 / Code Bullet flappy bird 影片氣泡 / 當兵解數獨 / 訓練 AI 解數獨）—— 純 CSS / SVG 構造

### 2. ml-map
- 📦 三大塊小場景圖（純 CSS / SVG 構造 — 抄筆記 / 折衣服 / 訓練狗握手）
- 📦 AlphaGo 標籤 sticker（**文字 sticker、不挂真實 logo / 圍棋盤照片**）

### 3. llm-vs-rl
- 📦 左右對比「LLM vs 我的 AI」（純 CSS / SVG 構造、房間 / 門 icon）

### 4. data-hunt
- 📦 Kaggle 標籤 sticker（**文字 sticker、不挂 Kaggle 真 logo**）
- 📦 websudoku URL sticker「這個受害者」（純文字、不挂截圖）
- 📦 「supervised 路線拒絕」紅 stamp
- 📦 「20 題就被封 IP」紅警示 + proxy 池 VPN 切換視覺示意（純構造）

### 5. legacy
- ✓ **`legacy/app/sudoku/torch_agent.py` 真實檔案 838 行**（口播 800 多行、可直接讀檔做 sticker 視覺）—— 路徑 `legacy/app/sudoku/torch_agent.py`
- 📦 「⋯⋯我錯了」獨立崩盤句 sticker
- 📦 prompt 對話框「幫我寫一個訓練 AI 解數獨的程式」sticker
- 📦 debug 紅色叉叉飛來飛去動畫

### 6. sb3
- 📦 「**只要他填對一格就給分數**」計分表 sticker
- 📦 **「新女生加分」sticker**（加分動畫 + + + 浮起、純構造）
- 📦 曲線爬升 → 卡住動畫（CSS / SVG 概念示意、**禁挂偽造 tensorboard 截圖** — `prompt.md` §五紅線）
- 📦 **「備胎」紅 stamp sticker**（微旋轉）
- 📦 「**偷吃步**」紅 stamp + 「**找漏洞作弊**」hero

### 7. reasoner
- 📦 **13 招大階梯**（13 個技巧 sticker、X-Wing 跟 XYZ-Wing 最大；技巧名清單從 `reasoner/solver/techniques/` 取真實檔名）
- 📦 「舊作法 vs 新作法」對比動畫（純 CSS 構造）
- 📦 消去動作示意動畫（劃掉這格不可能是這個數）
- 📦 「**兩千多萬次**」大字 + 「**0**」紅底 hero
- 📦 **戀愛 hook b 系列 sticker**：「老油條女生」「**和你媽一起掉進水裡**」「該不該運動」考題 + 兩個答案都錯的陷阱箭頭

### 8. apprentice
- ⚠️ **`apprentice/demo/visualize.py` → pygbag WASM 包裝**（**整片唯一現場可互動素材**）—— 原始檔已存在 (✓)、但 pygbag → iframe 包裝待落地
  - 主路線：pygbag → WASM → iframe（前置工作：`prompt.md` §六 #7 + §七 #7 排程；Phase 2 寫到 Ch 4 之前是 hard deadline）
  - 退路：OBS 錄 30s–60s mp4
- ⚠️ **tensorboard 真實截圖**（勝率曲線 + curriculum step 圖）—— 使用者表示有素材可挂、**整片唯一可挂真截圖的地方**；待落地動作：使用者匯出截圖至 `demo/assets/tensorboard/` 並提供確切路徑
- 📦 反向課程盤面動畫（3 空 → 4 空 → 5 空 → 7 空 → 10 空、一格一格揭示）
- 📦 「**+20 → +50**」翻牌動畫
- 📦 visualizer 大按鈕（cream 底 + 粗黑邊 + 強陰影 + accent red 字、微旋轉）

### 9. callback
- 📦 「腦科學 RL = AI RL」對等動畫 + 中間 `=` 大字
- 📦 飛機 + 鳥 並置 sticker
- 📦 戀愛 a 雙欄「回訊息 + / 已讀不回 −」+ 大腦 sticker
- 📦 戀愛 b 四個魔王考題 sticker 並排
- 📦 plasticity 三欄對位 sticker（AI 解數獨 / 出生講話 / 跟人相處 → 一樣）
- 📦 **「INFJ」MBTI sticker + 100% I 圓餅視覺**
- 📦 **業務工作 sticker**（跟陌生人講話對照動畫）
- 📦 **警語 sticker「人生第一次的外向、換來一輩子的內向」**（黑底紅字、微旋轉）
- 📦 「不被挫敗給擊敗」職場祝福 hero
- 📦 **電費小偷 final 大字 sticker**（accent red 底、黑邊、微旋轉、整片最強 punchline 之一）
- 📦 「**薪水小偷**」對位 sticker
