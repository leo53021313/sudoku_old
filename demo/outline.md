# Web Presentation Outline · Click-Driven Cinematic Edition

> **基石**：本 outline 對齊 `demo/script.md`（使用者個人化重寫定稿）。
> **形式**：**click-driven step presentation**——每步獨佔整屏、左鍵點擊推進下一步、右鍵點擊退回上一步。**不**是滾動敘事。
> **演講情境**：現場上台、桌面瀏覽器、演講者只需要左右鍵就能順暢推進。
> **主題**：Neo-brutalism + cinematic depth — cream `#FFFDF5` / 純黑 / 熱紅 `#FF6B6B` / 鮮黃 `#FFD93D` / 柔紫 `#C4B5FD`，詳 `demo/web_style.md`。
> **總時長**：約 12 分鐘口播 + 桌面 visualizer 30~60s（總 ≤ 15 分）。口播 ~3000 字 ÷ ~3.5 字/秒（含口語停頓 / 戲劇拉長）。
> **章節數**：9 章 / 57 step（含 ch8 visualizer step）。
> - ch1 從 6 step 加為 8 step（新增「繼續發呆」喜劇延續拍 + 拆解 sticker 累積動畫）
> - ch8 從 7 step 縮為 6 step（tensorboard 截圖挪到 ch9 step1）
> - ch9 從 14 step 縮為 13 step（MBTI + 業務工作合併為複合 step、降低結尾點擊密度）

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

| 類型 | 用途 | within-step 實作 |
|---|---|---|
| `cinematic` | 氛圍 hero / 全螢幕單一強訊息 | full-bleed、blur clear、慢動 mask reveal、留白 |
| `depth` | 多層深度場景（取代 parallax 的靜態版） | 多 layer translateY + opacity 模擬遠近、無 scroll 依賴 |
| `progressive` | 漸進揭示資訊 | 元素 stagger 進入（左鍵觸發 enter 後 50-150ms 一個） |
| `interactive` | 步內 hover / sub-click | hover 高亮 / 子卡放大 / 隨機切換、不影響推進 |
| `comparison` | 二元對比 | split-screen / 左右雙欄、可加 hover 雙向加重 |
| `timeline` | 時序事件、依序揭示 | 步內 horizontal 或 vertical 多卡 stagger、不需 scroll |
| `data-viz` | 數字 / 曲線 / 翻牌 | SVG stroke-dasharray draw、3D flip、CSS count-up |

### 響應式策略

- **Desktop (≥1280px)**：完整 depth 層、完整 hover 互動、字級照 web_style.md 規範
- **Tablet (≥768px)**：depth 簡化為 2 層、touch tap 替代 hover (hover 行為改成 tap 觸發)、字級降一級
- **mobile (<768px)**：**不在範圍**（演講場合只在桌面/平板播放）

### 全域 UI 規範

- 進度條：默認 `opacity: 0`、滑鼠近底部邊緣 32px 內 → 0.6s 淡入到 0.8、移開 1s 後淡出
- 章節 nav：默認隱藏、滑鼠近右上角 32px 內 → 浮現可跳章
- 無 header / footer / 品牌條 / 頁碼角標（per skill 「舞台無 chrome」原則）
- 演講者模式：URL `?presenter=1` 開 → 顯示 step 編號 + 下一步預覽（second screen 友善）

---

## 1. coldopen — 心虛開場 · 心理學系 · 捷運靈感（8 steps · ~70s）

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
- **step 8 (~10s)** — **BOOM · 兩個想法撞在一起**：三 sticker 在背景輕微抖動 1 拍 → 雙圈爆破覆蓋（黃外圈 + 紅內圈、border 8px、scale 0→1 overshoot）→ 中央 cream「**訓 練 AI 解 數 獨**」boom card（accent red AI 標、6px 黑邊、16px shadow、微旋轉 -2°）+ 下方 punchline「**靈感就是這麼 *莫名其妙* 地蹦出來**」（黃底高亮、微旋轉）
  ▸ **類型** `cinematic + data-viz` · **進場**: 三 sticker 抖動（150ms shake）→ 雙圈爆破 stagger（黃 first 80ms / 紅 second 120ms）→ boom card 從 scale 0.8 stamp（overshoot）→ punchline mask-reveal（720ms）· **重點 climax**: 爆破環 + boom card 的 zero-blur shadow 突顯
  ▸ **口播對應**: script.md L29「Boom，就這樣在我腦袋裡莫名其妙地把兩個想法結合在一起、訓練 AI 解數獨」+ L37「靈感就是這麼莫名其妙地蹦出來」

**口播節選**：
> 「我是心理學系畢業的⋯⋯某天搭捷運看著對面的正妹發呆⋯⋯腦袋冒出 Code Bullet 訓練 AI 玩 flappy bird⋯⋯又想到當兵解數獨⋯⋯Boom，靈感就是這麼莫名其妙地蹦出來。」

---

## 2. ml-map — 機器學習地圖（4 steps · ~50s）

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

**口播節選**：
> 「機器學習主要分三塊。supervised、unsupervised、RL⋯⋯當年 AlphaGo 打敗世界圍棋王、用的就是這招。那 ChatGPT 跟 Claude 又是哪一招？」

---

## 3. llm-vs-rl — ChatGPT 跟 Claude 在哪？（3 steps · ~35s）

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

**口播節選**：
> 「LLM 是模仿——模仿人類寫過的字。我這套不一樣——把 AI 丟進一個他什麼都不知道的房間、讓他自己摸出規則。OK 所以我要走純 RL、第一步是找資料。」

---

## 4. data-hunt — 找資料：從 Kaggle 到爬蟲（4 steps · ~50s）

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
- **step 3 (~14s)** — 「**終極目標：去每個數獨網站霸榜**」hero kicker → websudoku URL sticker（黑底 cream 字 mono 「websudoku.com」+ 紅色「**這個受害者**」標籤 sticker 微旋轉斜貼） + 副標「簡簡單單被我攻破」
  ▸ **類型** `cinematic + depth` · **進場**: kicker 從上 fade → URL sticker 從左 slide-in（mono font + cursor blink）→ 「這個受害者」紅 sticker 從右 stamp · **持續微動**: URL 後面 cursor 閃爍
- **step 4 (~13s)** — 「**才爬 20 題就被封 IP**」紅警示 hero + IP 封鎖圖示（黑邊框 + 紅色斜線）→ **proxy 池視覺化**：「類似 VPN · 好幾萬個 IP」+ 多個半透明 IP 小卡 grid（30+ 卡）漂浮 + 隨機 IP 切換動畫（每 200ms 一個卡高亮 + 切下個 IP 數字）
  ▸ **類型** `data-viz + cinematic` · **進場**: 紅警示 hero 進來 (800ms hold) → 警示淡化、IP grid 從中央 burst-out (stagger 30 個 30ms 間隔) → IP 切換動畫啟動 · **climax**: IP grid burst 瞬間 · **持續微動**: 隨機卡片高亮輪播

**口播節選**：
> 「Kaggle 是 supervised 路線、拒絕⋯⋯找到 websudoku 這個受害者⋯⋯結果 20 題就被封 IP⋯⋯我請出反反爬蟲工具 proxy。」

---

## 5. legacy — 一句搞定的幻想 → 800 多行單檔（4 steps · ~50s）

**信息池**：
- 戲劇崩盤句：「我以為⋯⋯**結果我錯了**」—— 來源 `script.md` L141-145
- 程式碼 anchor：**`legacy/app/sudoku/torch_agent.py` 一檔 838 行**（畫面值；口播照 script 走「800 多行」）—— 來源 `script.md` L151 + 真實程式碼 `legacy/app/sudoku/torch_agent.py`
- debug 痛點 anchor：「每改一個地方都東倒西歪、我自己都看不懂、debug 成本爆炸」—— 來源 `script.md` L153
- 第一件學到 anchor：「**不能再這樣偷懶全靠 AI 了。架構、演算法都得自己先想清楚、再請 AI 分工**」—— 來源 `script.md` L157-159
- 過渡 anchor：「放棄這個版本、轉而當個套皮仔」—— 來源 `script.md` L163

**開發計畫**：

- **step 1 (~13s)** — **cream 底 + 強紅邊框崩盤感** + 「我那時候還很天真」上方字幕 + 中央 prompt 對話框 sticker「**幫我寫一個訓練 AI 解數獨的程式**」（cream 底、6px 黑邊、12px shadow、模擬 chat input）+ 下方獨立崩盤句「**⋯⋯結果我錯了**」（cream 大字、6px 紅邊、16px shadow、微旋轉 1°）
  ▸ **類型** `cinematic` · **進場**: cream 持續 → halftone dots 加密 1.5× → 字幕 fade-up → prompt 對話框 stamp-in → **climax**: 「⋯⋯結果我錯了」mask-reveal + 紅邊框 flash 兩次 (200ms 一次、200ms 間隔) + 強紅 shadow burst 從 8px → 16px
  ▸ **設計來源**: 原版「底色切黑」會脫離 web_style.md cream 主畫布的 visual DNA、改為「cream + 6px 紅邊框 + halftone 加密 + 雙重 flash」表達崩盤感（保 brutalism 連續性、不破 visual cohesion）
- **step 2 (~8s)** — **「800 多行的單一檔案」程式碼 sticker** ：cream 上一坨深色文字塊（讀真實 `legacy/app/sudoku/torch_agent.py` 部分內容、syntax 高亮輕量化）+ 角標「`torch_agent.py · 838 lines`」+ 副標「**什麼都塞在裡面**」
  ▸ **類型** `cinematic + data-viz` · **進場**: 程式碼 sticker 從下方快速 slide-up（佔 70% 高、400ms）→ 角標 stamp-in 右上 · **climax**: 角標 838 數字 count-up 動畫 (0 → 838、600ms) · **持續微動**: 程式碼塊內輕微捲動 (背景慢速 translateY、暗示「巨量」)
  ▸ **節奏修正**: 原版 14s 進場過慢、口播只有 script.md L151「他產出了一個 800 多行的單一檔案、什麼都塞在裡面」(~6s)。縮到 8s 避免演講者卡空白
- **step 3 (~7s)** — **debug 痛點**：cream 上「**每改一個地方都東倒西歪**」hero + 紅色叉叉飛來飛去動畫 (chaotic、6-8 個叉叉隨機位置 spawn + scale + fade) + 「**debug 成本爆炸**」hero kicker
  ▸ **類型** `cinematic + data-viz` · **進場**: hero 文字 fade-in (300ms) → 紅叉叉 burst 一波（爆炸感、500ms）→ 持續隨機 spawn 叉叉 · **climax**: 「debug 成本爆炸」punchline mask-reveal · **氣質**: chaotic、視覺亂、暗示痛苦
  ▸ **節奏修正**: 原版 13s、口播 script.md L153 「後面我每改一個地方都東倒西歪、我自己都看不懂、debug 成本爆炸」(~7s)。縮到 7s 對齊
- **step 4 (~15s)** — **第一件學到 hero 標語**：「**架構、演算法都得自己先想清楚、再請 AI 分工**」（cream 底、黑大字、關鍵詞「架構」「演算法」「自己」「分工」黃底高亮 sticker）+ 過渡 footer「轉而當個套皮仔 →」
  ▸ **類型** `cinematic` · **進場**: chaotic 叉叉 fade-out → 底色穩定 → hero 標語慢速 mask-reveal 從左到右 (1200ms) → 4 個關鍵詞 stagger 黃底高亮 (per word 250ms) · **climax**: 4 黃底全亮的瞬間 · **轉場**: footer 從下 slide-up、暗示下章
  ▸ **節奏修正**: 原 10s → 15s。把 step 2+3 省下來的 12s 挪一半到此 step、讓金句節奏放慢、給觀眾消化 + 演講者口播 script L157-163「我學到的第一件事」+「自己手刻整套訓練系統就是浪費時間」雙段口播時間

**口播節選**：
> 「丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude⋯⋯結果我錯了。他產出 800 多行的單一檔案⋯⋯架構自己要先想清楚、再請 AI 分工。」

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

- **step 1 (~10s)** — 過渡：上方「正當我以為成了套皮仔⋯⋯」字幕 + 中央獨立崩盤句「**⋯⋯我又錯了**」（cream 底大字、6px 紅邊框、微旋轉 -1°、stamp-in）
  ▸ **類型** `cinematic` · **進場**: 字幕 fade-down → 崩盤句 stamp-in + 紅邊 flash · **氣質**: 重複 ch5 step 1 的崩盤感、形成 motif
- **step 2 (~9s)** — 套皮仔策略：左側「**社群現成 Python 工具箱**」標籤 sticker（紫底、微旋轉）+ 右側 「**只要他填對一格 · 就給分數**」計分表 hero（卡片化、黑邊 + shadow + 填對 = +1 動畫）
  ▸ **類型** `cinematic + data-viz` · **進場**: 左 label slide-in → 右計分表 card stamp-in → 內部「+1」數字動畫 (count-up 0 → 1)
- **step 3 (~12s)** — **戀愛 hook a 出場**：cream 底 + 中央「**剛認識的新女生**」sticker（粉紅色 + 微旋轉、暗示「新鮮」）+ 「+/+/+」浮動加分動畫（多個綠色 + 符號從下浮起）+ 副標「**聊天都覺得對方也喜歡你**」
  ▸ **類型** `cinematic + progressive` · **進場**: 中央 sticker stamp-in → 「+/+/+」符號連續 spawn from below + float-up + fade (持續動畫) → 副標 fade-up · **持續微動**: 加分符號連續浮動
- **step 4 (~10s)** — 左側保留新女生 sticker + 右側「**AI 得分曲線**」(SVG path、黑線粗、cream 底)、scroll-trigger 概念棄、改 enter 時 path stroke-dasharray 0 → 100% 自動 draw（2s）、爬升曲線 + 標籤「+/+/+」對應點亮
  ▸ **類型** `data-viz` · **進場**: 曲線從左到右 stroke-draw（2s ease-out）+ 對應 +/+/+ 沿曲線標記 stagger · **climax**: 曲線完成的瞬間
- **step 5 (~12s)** — **瓶頸**：曲線進入畫面停留、卡平段 highlighted (紅色背景帶) + 字幕「**拿那些必拿的固定分數 · 就不思進取**」+ 「一直沒辦法完整解出一道題」副標 + 新女生 sticker 慢慢淡化 / 變灰
  ▸ **類型** `data-viz + cinematic` · **進場**: 卡平段紅色 highlight band fade-in → 字幕 mask-reveal → 新女生 sticker grayscale 漸變 (1s) · **氣質**: 從亢奮 → 失落
- **step 6 (~10s)** — **戀愛 hook a 收**：cinematic 全屏 → 中央「**備胎**」紅 stamp sticker (旋轉 -3°、超大 stamp-in、shadow 16px、scale 1.4 → 1 砸下感) + 副標「看似有進展 · 結果什麼都沒發生」
  ▸ **類型** `cinematic` · **進場**: 黑色閃一下 (100ms flash) → 「備胎」stamp 從天上砸下 (scale 1.4 → 1, overshoot, 紅邊 flash) → 副標 fade-up · **climax**: stamp 砸下瞬間
- **step 7 (~7s)** — 揭穿全屏：「**偷吃步**」紅 stamp 左上 + 「**計分標準寫錯了 · AI 就會找漏洞作弊**」hero 中央（cream 底、黑大字、紅底 + 黃底 雙色強調）
  ▸ **類型** `cinematic` · **進場**: 紅 stamp stamp-in → hero 文字 mask-reveal → 雙色強調 box stagger fade-in
  ▸ **D1 修正**: 原版這裡轉場 footer「我只好整個計分獎勵系統重寫」與 ch 7 step 1 主 hero「我只好整個計分獎勵系統重寫」是同一句、口播 (script.md L201) 只念一次但畫面出兩次。改為純做「偷吃步 / 找漏洞作弊」punchline 收尾、轉場留給 ch 7 step 1 開「重寫」hero

**口播節選**：
> 「填對一格就給分數⋯⋯剛開始得分急遽增長⋯⋯結果只把你當備胎⋯⋯計分標準寫錯了、AI 就會找漏洞作弊。」

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

- **step 1 (~11s)** — 過渡：「**我只好整個計分獎勵系統重寫**」hero（cream 底、黑大字、「重寫」黃底高亮）+ kicker「核心想法只有一個」
  ▸ **類型** `cinematic` · **進場**: hero mask-reveal + 「重寫」黃底 highlight slide-in · **氣質**: 嚴肅、轉折
- **step 2 (~14s)** — 顛倒驗證宣告 full-screen 標語：「**用人類玩數獨的解題技巧 · 反過來驗證 AI 的每一步**」（超大 typography、關鍵詞「反過來」紅底 + 「驗證」黃底 highlight）
  ▸ **類型** `cinematic` · **進場**: 文字 mask-reveal 慢動 (1200ms) → 關鍵詞 stagger highlight · **climax**: 「反過來」「驗證」雙 highlight 同時亮 · **持續微動**: 主標題輕微 letter-spacing 微動
- **step 3 (~19s)** — **13 招大階梯**：cream 底、13 張小 sticker 從低（naked single / hidden single）排到高（X-Wing / Swordfish / **XY-Wing** / **XYZ-Wing**），階梯式由左下到右上排列、低階小且樸素、高階大且華麗（**X-Wing 跟 XYZ-Wing 最大、最華麗** · accent yellow / accent violet 底、6px 黑邊、微旋轉 -3° / 4°、12px shadow）+ 角標「**13 招 · 真實技巧名**」
  ▸ **類型** `progressive + interactive` · **進場**: 13 張 sticker 從低到高 stagger stamp-in（每張 80ms 間隔、1s 共完成）· **互動**: hover 任一 sticker → 該 sticker scale 1.15 + 其他 dim opacity 0.5 + tooltip 浮出該招中文簡介 · **climax**: 13 張全 stamp 完的瞬間
- **step 4 (~17s)** — **舊 vs 新對比動畫**：split-screen 60/40、左「**舊：填對一格就給分**」（只有一招亮 + 一個分數浮現）vs 右「**新：可以用哪一招解釋？**」（每張技巧都可以亮 + 高招分數更高、+1 +2 +3 浮動）
  ▸ **類型** `comparison + data-viz + interactive` · **進場**: split-screen wipe-in → 左側單一招亮起 + 數字 +1 → 右側多招陸續亮起 + 不同高度分數浮動 stagger · **互動**: hover 左 / 右 → 該側放大 dim 對立側 · **climax**: 右側 X-Wing 亮 + +3 分浮起
- **step 5 (~13s)** — Action 擴增：「**多了一倍可以做的事**」hero + 中央 9×9 mini 盤面動畫，「**填一個數字**」(綠) + 「**劃掉這格不可能是這個數**」(紅斜線) 兩種動作示意動畫 + 副標「消去類技巧才能展示出來」
  ▸ **類型** `data-viz + interactive` · **進場**: hero 上方 fade-in → mini 盤面 stamp-in → 填數字綠動畫 → 劃掉紅斜線動畫 (stagger 600ms) · **持續微動**: 盤面 loop 動畫示意兩動作交替
- **step 6 (~14s)** — **慘烈結果**：cinematic 全屏紅底 + cream 大字「練了 **兩千多萬次**」(數字 count-up 0 → 2,000,000+) + 下方「完整解出一道題的機率還是 **0**」（「0」超大字、accent yellow 底）
  ▸ **類型** `cinematic + data-viz` · **進場**: 底色閃紅 → 「兩千多萬次」count-up 動畫 (2s) → 下方「0」字從上 drop-in (overshoot bounce、scale 0 → 1.4 → 1) · **climax**: 「0」砸下瞬間 + 紅底 flash
- **step 7 (~22s)** — **戀愛 hook b 全面展開**：cream 底 + 上方 hero「**老油條女生陷阱題**」黃底高亮 + 中央 **2 張陷阱考題 sticker** 並排（旋轉不同方向）：
  - 左：「**和你媽一起掉進水裡 · 你會先救誰？**」（紅底 cream 字、微旋轉 -3°）
  - 右：「**你覺得我該不該去運動？**」（紫底 cream 字、微旋轉 4°） + 下方兩個答案箭頭「說要 → ❌ 嫌她胖」「說不用 → ❌ 不關心健康」
  ▸ **類型** `interactive + comparison` · **進場**: hero mask-reveal → 兩 sticker 從外側 swing-in (overshoot)、stagger 240ms → 「該不該運動」右側 sticker 兩答案箭頭 stagger 浮現 · **互動**: hover 任一 sticker → 放大 + 對應答案 ❌ 紅 flash · **climax**: 兩個 ❌ 紅 flash 同時 · **氣質**: 滑稽、共鳴
- **step 8 (~20s)** — **死結**：cinematic 黑底 → cream 大字「**AI 永遠拿不到「整題解完」那個大獎**」+ 副標「**就跟我不知道陷阱題的正確解答一樣**」+ 角落「**反向思考⋯**」鋪墊 footer
  ▸ **類型** `cinematic` · **進場**: 底色 cream → 黑 fade (800ms) → 主標 mask-reveal 慢動 (1500ms) → 副標 fade-up → footer 從下 slide-in · **氣質**: 沉重、留白、為下章鋪墊 · **轉場**: 「反向思考⋯」footer 提示下章方向

**口播節選**：
> 「13 招數獨技巧——naked single、X-Wing、XY-Wing⋯⋯練了兩千多萬次、解出整題機率還是 0⋯⋯就跟我不知道老油條陷阱題的正確解答一樣。」

---

## 8. apprentice — 反向課程 + visualizer（6 steps · ~66s + visualizer 30~60s）

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

## 9. callback — AI 也在訓練我（13 steps · ~192s）

> **結尾長章例外**：超過 OUTLINE-FORMAT 建議的「每章 3~8 步」上限，因 script.md L303-375 結尾為壓軸大段、無法切兩章保持節奏。原 14 step 已合併 MBTI + 業務工作 (step 10+11 → step 10) 縮成 13 step、降低結尾點擊密度。

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
- **step 5 (~16s)** — **戀愛 a callback**：split-screen 雙欄對照
  - 左欄「**回訊息**」綠色 + 號 浮動 (多個 +/+/+ 從下浮起)
  - 右欄「**已讀不回**」紅色 − 號 沉下 (多個 -/-/- 從上沉)
  - 中央大腦 sticker (黑線稿 + 內部紫色 reward 漂浮)
  - 下方紅底全屏 hero「**跟 AI 訓練一模一樣**」
  ▸ **類型** `comparison + data-viz + cinematic` · **進場**: split wipe-in → 左欄 +/+/+ 連續 spawn (持續) → 右欄 -/-/- 連續 spawn (持續) → 大腦 sticker stamp-in → 下方紅底 hero mask-reveal · **持續微動**: +/+/+ 跟 -/-/- 連續浮動 · **climax**: 紅底 hero 砸下
- **step 6 (~18s)** — **戀愛 b callback**：cream 底 + 上方「**以為穩了 · 結果魔王關卡**」hero + 中央 **4 個考題 sticker grid 並排** (2×2、每張不同底色 + 微旋轉)：
  - 「**前女友跟我比 · 誰比較好？**」（黃底）
  - 「**你心中的女神是誰？**」（紫底）
  - 「**你喜歡我哪裡？**」（紅底 cream 字）
  - 「**猜猜看 · 今天我哪裡不一樣？**」（cream 底 + 描邊）
  ▸ **類型** `interactive + cinematic` · **進場**: hero fade → 4 sticker 從 grid 中心 stagger stamp-in (each 150ms 間隔) · **互動**: hover 任一 sticker → scale 1.1 + shadow 加深 + 其他 dim 0.5 + 該題下方浮現「⋯⋯（沒有正解）」副標 · **氣質**: 滑稽、共鳴
- **step 7 (~8s)** — **plasticity 引出**：cinematic 全屏 cream → 上方「最後再跟大家分享」kicker → 中央「**大腦可塑性 · plasticity**」hero (中文 + 英文並列、英文 letter-spacing 撐開)
  ▸ **類型** `cinematic` · **進場**: kicker fade-down → hero mask-reveal 慢動 (1000ms) + 「plasticity」英文 letter-spacing 0.3em → 0.05em 收緊 · **氣質**: 學術感、慢拍
- **step 8 (~12s)** — **plasticity 三欄對位**：cream 底、三欄並列：
  - 欄 1: 「**AI** 沒天生會 · 解數獨」(紅底 sticker)
  - 欄 2: 「**你** 出生不會 · 講話」(黃底 sticker)
  - 欄 3: 「**你** 不是天生會 · 跟人相處」(紫底 sticker)
  - 中央巨字「**一樣**」(cream 底、黑超大字、stamp-in)
  ▸ **類型** `comparison + cinematic` · **進場**: 三欄 stagger fade-up (each 200ms 間隔) → 中央「一樣」從 scale 0 砸下 (overshoot + 紅邊 flash) · **climax**: 「一樣」砸下瞬間
- **step 9 (~12s)** — **plasticity 機制**：cinematic + 中央「**每次都把我們重新塑造一次**」hero + 上方副標「每改一次 reward function、每談一場戀愛、每學一個新東西」(三項 stagger reveal)
  ▸ **類型** `cinematic + progressive` · **進場**: 副標三項 stagger fade-up (each 240ms 間隔) → 主 hero mask-reveal 慢動 + 「重新塑造」黃底高亮 · **氣質**: 哲思、慢動
- **step 10 (~22s)** — **MBTI 自我故事 + 業務工作變 E**（合併原 step 10+11）：cream 底 + 上方「我真的是一個 **極度的 I 人**」kicker
  - **第一拍 (0-9s)**：中央 **MBTI 圓餅視覺**（圓餅完整黑邊、I 紫色填滿 100%、E 0%、cream 中心）+ 右側「**極度 I 人**」標籤 sticker（紫底、6px 黑邊、微旋轉 -3°、stamp-in）+ 副標「明明我很 E」（黃底高亮）
  - **第二拍 (9-22s)**：圓餅 sticker 縮到左側 30% 寬、右側 70% 拉出 **「業務工作」標籤 sticker** (黃底、微旋轉 2°、stamp-in) + **I → E 漸變條** (水平條、從紫色 I → 紅色 E、indicator 動畫從 I 0% 移到 60%、4s) + 副標「天天逼自己跟陌生人講話 · 才慢慢變得比較 E」
  ▸ **類型** `data-viz + progressive` · **進場**: kicker fade-down → 圓餅 0% → 100% I 填滿動畫 (1.5s) → 「極度 I 人」sticker 砸下 (overshoot) → 副標 fade-up · **第二拍觸發**: 步內第二拍由 step 內動畫自動觸發（hold 1.5s 後）、不需要演講者額外點擊 → 圓餅縮側 (600ms ease) → 業務 sticker stamp-in → 漸變條 fade-in → indicator 移動 (4s) → 副標 stagger · **climax**: 圓餅 100% I 填滿瞬間 + indicator 抵達 60% 瞬間
  ▸ **合併來源**: 原 step 10 (14s MBTI) + step 11 (14s 業務工作) = 28s。合併為單一複合 step (22s)、保兩段資訊密度但縮一個點擊節點（ch 9 從 14 step → 13 step、降低結尾點擊密度）。對應 script.md L359-365 連續一段、原本就沒有 `---` 分隔
- **step 11 (~16s)** — **不被擊敗 · 警語 cinematic full-bleed**：cream 底（halftone dots 加密 1.5×）+ 上方「從挫敗中學習就行了」kicker + 中央 **警語 sticker**「**人生第一次的外向 · 換來一輩子的內向**」（cream 底、accent red 大字、6px 紅邊框、20px hard shadow、微旋轉 -2°、超大字）+ 下方副標「但是不要停滯不前」
  ▸ **類型** `cinematic` · **進場**: halftone dots 加密 (400ms) → 警語 sticker 從 scale 1.3 → 1 snap (overshoot + 紅邊 flash 兩次、200ms 一次) + shadow burst 從 8px → 20px → 副標 fade-up · **climax**: 警語 sticker 砸下、整片最重的一拍 + shadow burst
  ▸ **設計來源**: 原版用「黑底紅字」會脫離 web_style.md cream 主畫布的 visual DNA。改為「cream + accent red 大字 + 6px 紅邊 + 20px shadow + halftone 加密」表達警語的重量感（保 brutalism 連續性、力道靠 shadow + flash + halftone 加密、不靠切黑底）
- **step 12 (~12s)** — **職場祝福**：cream 底回歸 + 上方「繼續嘗試跟其他女生聊天」kicker + 中央「**祝大家未來在職場上 · 不被挫敗給擊敗**」hero（黑大字、「不被挫敗給擊敗」紅底高亮、cream 字）+ 下方「不是每個女生都那麼老油條」副標
  ▸ **類型** `cinematic` · **進場**: kicker fade-down → hero mask-reveal + 紅底高亮 slide-in → 副標 fade-up · **氣質**: 正能量、收斂、為最後笑話鋪墊
- **step 13 (~22s)** — **電費小偷結尾笑話 verbatim** cinematic 最終：
  - 上方 kicker「最後再補個笑話」fade-in
  - 中央上「想必大家未來出職場後都是 · **薪水小偷**」對位 sticker (黑底 cream 字、微旋轉 2°)
  - 中央下「但我不一樣 · 我是 **電費小偷**」FINAL sticker（accent red 底、cream 大字、6px 黑邊、16px hard shadow、微旋轉 -3°、超大、stamp-in）
  - 底部 footer「我這兩個月 · 一直用班上的電腦 · 瘋狂訓練我的 AI」progressive type-in
  - 整屏右下角浮現「— END —」minimal footer (純黑字、cream 底、無 chrome)
  ▸ **類型** `cinematic` · **進場**: kicker fade-in → 「薪水小偷」sticker stamp-in (stagger 600ms) → **「電費小偷」FINAL sticker 砸下** (scale 1.5 → 1 snap、overshoot bounce、紅邊 flash、shadow burst 從 8px → 16px) → 底部 footer progressive type (字逐字打字效果 1.5s) → 「— END —」浮現 · **climax**: 電費小偷 sticker 砸下瞬間 + shadow burst (全片最強 reveal) · **氣質**: punchline 爆破、收尾、留 3-4s 讓觀眾笑

**口播節選**：
> 「這兩個月、我不只在訓練 AI、AI 也在訓練我⋯⋯大腦可塑性 plasticity⋯⋯我真的是極度的 I 人、明明我很 E⋯⋯祝大家在職場上不被挫敗給擊敗。我是電費小偷、我這兩個月一直用班上的電腦瘋狂訓練我的 AI。」

---

## 素材清單

> 標註規則：✓ 已就位（路徑可指）/ ⚠️ 待製作或待提供 / 📦 純 CSS / SVG 構造（不需要外部素材）

### 1. coldopen
- 📦 「**心 虛**」巨字 sticker（純 CSS）+ 黃色「期中報告」角標
- 📦 「**心理學系**」card + 紅箭頭 + 黃底「敬請期待」高亮
- 📦 「**訓 練 AI 解 數 獨**」hero（text-stroke 樣式、紅底 + 黃底 box 強調）+ 4 漂浮裝飾物（紫方塊 / 黃星 / 紅圓 / 描邊問號）
- 📦 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop）+ 多層 depth
- 📦 4 張靈感串聯 sticker（正妹 / Code Bullet flappy bird / 沒手機解數獨 / 訓練 AI 解數獨）—— 純 CSS / SVG
- 📦 BOOM 雙圈爆破動畫（黃外圈 + 紅內圈）+ punchline 黃底高亮

### 2. ml-map
- 📦 三大塊插畫（抄筆記 / 折衣服 / 訓練狗握手）—— 純 CSS / SVG
- 📦 AlphaGo 標籤 sticker（**文字 sticker、不挂真實 logo 或圍棋盤照片**）
- 📦 kicker 切換動畫「①/②/③」
- 📦 cliffhanger 黃底問號 sticker

### 3. llm-vs-rl
- 📦 split-screen 60/40 對比版型 (LLM vs 我的 AI)
- 📦 中央 VS 大字 sticker + 紅底/黃底 stamp 對比
- 📦 房間 / 門 SVG icon (cream 上、純 SVG)
- 📦 背景文字流動效果 (低密度文字 grid 微動)

### 4. data-hunt
- 📦 Kaggle 標籤 sticker（**文字 sticker、不挂 Kaggle 真 logo**）+ 多張資料 card 浮現
- 📦 「supervised 路線拒絕」紅 stamp（旋轉、stamp-in）
- 📦 websudoku URL sticker「**這個受害者**」（純文字 mono + 紅標籤 + cursor 閃爍）
- 📦 「20 題就被封 IP」紅警示 + IP 封鎖圖示
- 📦 **proxy 池視覺化**：30+ IP 小卡 grid 漂浮 + 隨機切換動畫（純 CSS）

### 5. legacy
- ✓ **`legacy/app/sudoku/torch_agent.py` 真實檔案 838 行**——可直接讀檔做程式碼 sticker、count-up 角標 838
- 📦 prompt 對話框「**幫我寫一個訓練 AI 解數獨的程式**」sticker
- 📦 「**⋯⋯結果我錯了**」獨立崩盤句 sticker
- 📦 紅色叉叉 burst 動畫（chaotic spawn）
- 📦 第一件學到 hero + 4 個關鍵詞黃底高亮 stagger

### 6. sb3
- 📦 「**社群現成 Python 工具箱**」標籤 + 「**填對一格 · 給分**」計分表 hero
- 📦 「剛認識的新女生」sticker（粉紅 + 微旋轉）+ 「+/+/+」加分動畫
- 📦 SVG 曲線爬升（stroke-dasharray draw）→ 卡平段紅 highlight band
- 📦 新女生 sticker grayscale 漸變
- 📦 **「備胎」FINAL stamp sticker**（紅、超大、微旋轉、16px shadow）
- 📦 「**偷吃步**」紅 stamp + 「**找漏洞作弊**」hero (紅 + 黃雙色強調)
- ⚠️ **禁挂偽造 tensorboard 截圖**（曲線一律 SVG 概念示意、`prompt.md` §五紅線）

### 7. reasoner
- 📦 **13 招大階梯**（13 個技巧 sticker、X-Wing 跟 XYZ-Wing 最大；技巧名清單從 `reasoner/solver/techniques/` 取真實檔名）+ hover tooltip
- 📦 「舊作法 vs 新作法」split-screen 對比動畫 + 多招亮 + 分數浮動
- 📦 9×9 mini 盤面 + 填數字綠 + 劃掉紅斜線 loop 動畫
- 📦 「**兩千多萬次**」count-up + 「**0**」紅底超大字 hero
- 📦 **戀愛 hook b 陷阱題 sticker**：「**和你媽掉進水裡你會先救誰**」「**該不該運動**」（含兩答案都錯 ❌ 箭頭）+ hover 互動
- 📦 死結 cinematic 黑底 hero + 反向思考 footer 鋪墊
- ⚠️ **禁挂 `TECH_BONUS` 整張數值表 / `net_arch` / `SubprocVecEnv` 等字串**（假數據顯擺反例，`prompt.md` §五）

### 8. apprentice
- 📦 「**反向思考**」hero + 紅底高亮
- 📦 9×9 數獨盤面（黑邊 + cream 格子 + Space Grotesk 700 數字、90% 已填、3 空 highlight）
- 📦 反向課程動畫：3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 空（連續一格一格擦掉 + 計數器 count-up、對齊 script「再加一格、再加一格」口語）
- 📦 **「+20 → +50」3D flip 翻牌動畫**（紅 → 黃、shadow 加深）
- ⚠️ **tensorboard 真實截圖**（success_rate 曲線 + curriculum target_empty 圖）——使用者匯出至 `demo/presentation/public/images/tensorboard/` 並提供路徑、**整片唯一可挂真截圖的地方**
- 📦 「光講不夠看」+ 向下大箭頭 stroke-draw + bounce
- 📦 **visualizer 大按鈕**（cream 底 + 粗黑邊 + 強陰影 + accent red 字、微旋轉、hover scale + shadow 加深 mechanical feedback、`href="sudoku-demo:run"`）
- ✓ **`apprentice/demo/visualize.py` 桌面 pygame 視窗**——透過 Windows custom URL scheme `sudoku-demo:` 自動啟動，演講者不需 Alt+Tab
- ✓ **`demo/visualizer-launch/` 一鍵啟動套件**（install.bat / uninstall.bat / launcher.bat / requirements-demo.txt / README.md）——所有 .bat 自動偵測 `sudoku_old/` 根目錄、portable 到任何 Windows 機器
- ⛔ **「tensorboard 截圖」已從 ch 8 移除**——挪去 ch 9 step 1 當「AI 在進步」的視覺證據

### 9. callback
- 📦 cinematic hero「**AI 也在訓練我**」大字 mask reveal + letter-spacing 收緊 + 紅底 flash
- 📦 「腦科學 RL = AI RL」split + 「**=**」大字 stamp（黃底圓 sticker）
- 📦 飛機 + 鳥 並置 sticker（黑線稿 + 黃填充、輕微振翅）
- 📦 戀愛 a 雙欄「+/+/+」「-/-/-」浮動 + 中央大腦 sticker + 紅底「跟 AI 一模一樣」
- 📦 戀愛 b 4 個魔王考題 sticker grid（2×2）+ hover 互動
- 📦 plasticity 三欄對位 sticker（AI 解數獨 / 出生講話 / 跟人相處）→ 中央「**一樣**」snap
- 📦 plasticity 機制 hero「每次都把我們重新塑造一次」+ 三項 stagger
- 📦 **MBTI 圓餅視覺**（0% → 100% I 填滿動畫）+ **「極度 I 人」紫色標籤 sticker**（原版用「INFJ」、改為 script.md L359 verbatim 字眼）
- 📦 **業務工作 sticker** + I → E 漸變條（indicator 從 I 移到中間）
- 📦 **警語 sticker「人生第一次的外向 · 換來一輩子的內向」**（黑底紅字、6px 紅邊、16px shadow、微旋轉、超大）
- 📦 「**不被挫敗給擊敗**」職場祝福 hero（紅底高亮）
- 📦 「**薪水小偷**」對位 sticker
- 📦 **「電費小偷」FINAL 超大字 sticker**（accent red 底、6px 黑邊、16px hard shadow、微旋轉、整片最強 reveal、stamp + shadow burst）
- 📦 「— END —」minimal footer

---

## 實作參考（不在本 outline 範圍、留給後續實作 agent）

> 以下僅供未來 chapter agent / 實作工程師參考、本 outline 不規定具體技術選型。

- **觸發機制**：`mousedown` 監聽（button 0 = 左鍵 next、button 2 = 右鍵 prev）+ `keydown` 監聽（`Space` / `ArrowRight` = next、`ArrowLeft` = prev、`Escape` = toggle progress bar）
- **右鍵實作**：`document.addEventListener('contextmenu', e => e.preventDefault())` 必須在 mount 時設置、unmount 時 remove
- **動畫庫**：簡單 transition 用純 CSS（最大宗）；複雜 timeline 用 [GSAP](https://gsap.com/)（13 招階梯 / 電費小偷 final 等 climax）；React 風格 reveal 可選 [Framer Motion](https://motion.dev/) `useAnimate`
- **字體**：Space Grotesk 700/900（Latin）+ Noto Sans SC 700/900（中文）
- **無障礙**：`prefers-reduced-motion` 媒體查詢內、所有 stamp / overshoot / parallax 動畫切回 instant；hover 互動需有 focus 版本（鍵盤 tab）
- **效能**：所有動畫用 `transform` + `opacity` 屬性（GPU-friendly）；避免 `width/height` 變動觸發 layout；code wall 視窗化（virtual scroll）避免 838 行全 DOM
- **演講者模式**：URL `?presenter=1` 開啟（第二螢幕顯示「下一 step 預覽 + 口播 cue」）、現場用單螢幕模式

---

## 反向索引 · script.md 行號 → outline step

> **用途**：每次改 `script.md` 一段口播時、查本表可立刻知道要動 outline.md 的哪幾個 step。
> **格式**：script.md 行號區間 → 章節 step + 內容摘要。
> **依 script.md 章節分段順序排列**。

| script.md 行號 | 對應 outline step | 內容摘要 |
|---|---|---|
| L1 | ch 1 step 1 | 心虛開場、報告太不正經、請各位同學和老師多包涵 |
| L5 | ch 1 step 2 | 心理學系畢業 + 敬請期待伏筆 |
| L9 | ch 1 step 3 | 期中主題：訓練 AI 解數獨 |
| L13-L17 | ch 1 step 4 | 捷運上正大光明看著正妹發呆 |
| L19 | ch 1 step 5 | 腦袋冒出 Code Bullet flappy bird |
| L21 | ch 1 step 6 | 繼續發呆看著正妹（喜劇延續拍） |
| L25 | ch 1 step 7 | 當兵沒手機解數獨 |
| L29 | ch 1 step 8 | Boom · 兩個想法撞在一起：訓練 AI 解數獨 |
| L35-L37 | ch 1 step 8 punchline | 靈感就是這麼莫名其妙地蹦出來 |
| L41-L45 | ch 2 lead-in | 機器學習的世界長什麼樣 |
| L49-L55 | ch 2 step 1 | supervised：看著答案抄筆記 |
| L57-L61 | ch 2 step 2 | unsupervised：折衣服分顏色 |
| L63-L67 | ch 2 step 3 | RL：試錯加獎懲、AlphaGo |
| L71 | ch 2 step 4 | cliffhanger：那 ChatGPT 跟 Claude 又是哪一招？ |
| L75-L77 | ch 3 step 1 | LLM = supervised + RLHF |
| L81-L89 | ch 3 step 2 | LLM 模仿 vs 我的 AI 自己摸出規則 |
| L93-L95 | ch 3 step 3 | OK 純 RL、第一步找資料 |
| L99-L107 | ch 4 step 1+2 | Kaggle / supervised 路線拒絕 |
| L111-L121 | ch 4 step 3 | 霸榜目標 + websudoku 受害者 |
| L125-L133 | ch 4 step 4 | 20 題被封 IP + proxy 池 |
| L141-L147 | ch 5 step 1 | 我那時候很天真 / 丟一句 prompt / 我錯了 |
| L151 | ch 5 step 2 | 800 多行的單一檔案 |
| L153 | ch 5 step 3 | 每改一個地方都東倒西歪 / debug 成本爆炸 |
| L157-L163 | ch 5 step 4 | 第一件學到 / 架構自己先想清楚 / 套皮仔 |
| L167-L173 | ch 6 step 1+2 | 社群工具箱 / 套皮仔 / 我又錯了 |
| L177 | ch 6 step 2 | 填對一格就給分數 |
| L181-L185 | ch 6 step 3 | 新女生加分（戀愛 hook a 出場） |
| L187 | ch 6 step 4+5 | 卡平段 / 不思進取 |
| L189 | ch 6 step 6 | 備胎（戀愛 hook a 收） |
| L195-L199 | ch 6 step 7 | 偷吃步 / 計分標準寫錯 / 找漏洞作弊 |
| L201-L205 | ch 7 step 1+2 | 整個計分系統重寫 / 用人類技巧反過來驗證 |
| L209-L211 | ch 7 step 3 | 13 招技巧名（naked / hidden / X-Wing / Swordfish / XY-Wing） |
| L215-L225 | ch 7 step 4 | 舊（填對一格給分）vs 新（用哪一招解釋）對比 |
| L229-L233 | ch 7 step 5 | Action 擴增：填數字 + 劃掉候選 |
| L237 | ch 7 step 6 | 兩千多萬次 · 完整解出機率 0 |
| L241-L257 | ch 7 step 7 | 老油條陷阱題（戀愛 hook b 展開） |
| L265-L269 | ch 7 step 8 | 死結：永遠拿不到「整題解完」大獎 |
| L273-L275 | ch 8 step 1 | 反向思考 |
| L277-L279 | ch 8 step 2 | 一開始只給 3 格空 |
| L281-L285 | ch 8 step 3 | 再加一格、再加一格⋯⋯3→4→5→6→7→8→9→10 |
| L287-L291 | ch 8 step 4 | 破關獎勵 +20 → +50 |
| L293 | ch 8 lead-out | 3 → 10、他終於開始解出整題 |
| L297-L299 | ch 8 step 5+6 | 光講不夠看 / 給大家看 AI 即時解數獨 + visualizer 按鈕 |
| L303-L307 | ch 9 step 1 | AI 還在訓練中 / 磨合期 / 最後一件事（tensorboard 截圖此處挂） |
| L309 | ch 9 step 2 | 核心金句：這兩個月、我不只在訓練 AI、AI 也在訓練我 |
| L313-L317 | ch 9 step 3 | 腦科學 RL = AI RL、其實是同一件事 |
| L319 | ch 9 step 4 | 飛機 / 鳥：AI 在模仿人類 |
| L323-L329 | ch 9 step 5 | 戀愛 a callback：回訊息加分 / 已讀扣分 |
| L333-L343 | ch 9 step 6 | 戀愛 b callback：4 個魔王考題 |
| L347-L349 | ch 9 step 7 | 大腦可塑性 plasticity 引出 |
| L351 | ch 9 step 8 | plasticity 三欄對等（AI 解數獨 / 出生講話 / 跟人相處） |
| L353-L355 | ch 9 step 9 | plasticity 機制：每次都把我們重新塑造一次 |
| L359-L361 | ch 9 step 10 第一拍 | 極度 I 人 + MBTI 100% I 圓餅 |
| L363-L365 | ch 9 step 10 第二拍 | 業務工作變 E + I→E 漸變條 |
| L367-L369 | ch 9 step 11 | 人生第一次的外向 · 換來一輩子的內向 |
| L371-L373 | ch 9 step 12 | 職場祝福：不被挫敗給擊敗 |
| L375 | ch 9 step 13 | 電費小偷 final（薪水小偷 + 電費小偷 + END） |

**注意事項**：
- 同一行可能對應到多個 step（例如 L201 = ch 6 step 7 提示 + ch 7 step 1 主 hero）
- 同一個 step 可能對應多行 script（例如 ch 9 step 10 合併 L359-365）
- 演講者改 script 一段時、本表配合 outline 章節「**口播對應**」欄位（部分 step 已標）反查
