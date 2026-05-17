# 演講內容主檔（敘事 · Beat · Speaker Cue）

> **配對檔**: [outline-visual.md](outline-visual.md)（視覺 DNA / Motif / Climax / 色票 / v3 polish / Speaker Mode / Coverage Matrix）· [asset-production.md](asset-production.md)（素材生產路線）
> **口播 source of truth**: [script.md](script.md)（本檔僅引用行號、不可在 outline 改口播）
> **形式**: click-driven step presentation — 左鍵推進 beat、右鍵退、不滾動
> **總時長**: ~12.5 min 口播 + 桌面 visualizer 30~60s（總 ≤ 15 min）
> **章節數**: 9 章 / 57 step / ~88 beat

---

## §0 全域操作機制

- **滑鼠左鍵** → 推進到下一 beat（含跨 step、跨章節）
- **滑鼠右鍵** → 退回上一 beat
- **鍵盤備援** → `SPACE` / `→` = 左鍵；`←` = 右鍵；`Esc` = 顯示進度條
- **右鍵實作 note**: `document.addEventListener('contextmenu', e => e.preventDefault())` 禁用瀏覽器原生選單
- **滑鼠 hover** → 進度條 / 章節 nav 從邊角浮現、移開 0.5s 後淡出
- **不可** 用滾輪 / scroll / scrollIntoView 推進

## §1 Sub-step Beat 機制

每個 step 可拆成 1-N 個 **beat**。一次左鍵 = 推進一個 beat（不是整 step）。

- **beat 標註格式**: `▸ beat N [click/auto] <id>: <描述>`
  - `[click]` → 等待左鍵（給演講者鋪墊時間）
  - `[auto, Nms]` → 前一 beat 完成後自動觸發
- **預設**: 不寫 beats 的 step 視為單 beat
- **punchline 強制**: punchline 文字 / stamp / 數字 / 翻牌 必須獨立成 `[click]` beat、不可與前置元素同步進場
- **進度條**: 以 beat 為單位、`Esc` 顯示「step M / 57 · beat N / X」

## §2 Punchline Placeholder 模式（強制規範）

所有 punchline step 強制走兩拍模板：

```
[beat A] 預留視覺佔位（剪影 / 空 sticker / ??? / 閃爍游標 _）
         ← 演講者「開鋪」期間視覺已就位、給觀眾期待感
[beat B] click → placeholder 被填入 / morph / stamp 砸下
         ← 演講者「念出 punchline」當下視覺同步揭曉
```

不走 placeholder = 破梗 = 觀眾不會笑。

## §3 Speaker Cue 規範

punchline 與鋪墊 step 的每個 beat 可加：
- `· cue: "..."` — 演講者「觸發此 beat 之前」該說到的句子（短截、verbatim or 接近）
- `· wait: ...s` — 觸發後該停多久才推下一 beat

`?presenter=1` 模式在第二螢幕即時顯示「下一 beat 的 cue + wait」。

## §4 演講者模式

URL `?presenter=1` → 第二螢幕顯示 step 編號 + 下一步預覽 + **下一 beat 的 cue + wait**。詳細 layout / dry-run / 緊急 fallback 規格見 [outline-visual.md §5.6 Speaker Mode](outline-visual.md)。

## §4.5 Star Legend

| 標記 | 意義 | step |
| --- | --- | --- |
| ★★★ | 全片三大笑點 climax、節奏控制必須完美、`?presenter=1` 重點檢視 | ch6 s6 備胎 · ch7 s7 老油條 · ch9 s13 電費小偷 |
| ★★ | 全片第二重一拍 | ch9 s11 警語「人生第一次的外向 · 換來一輩子的內向」 |
| `punchline` | 走 §2 Punchline Placeholder 模式（拆 beat、預留 placeholder） | 共 10 個 |
| `polish` | 非 punchline 但有特殊 FX 加成 | 共 6 個（見 outline-visual.md §8.4） |

---

## §5 Step Manifest（57 step 一覽）

> **wait 欄** = 演講者「停拍」累計時間（動畫進場外）。⚠ = wait > 33% duration、🚩 = wait > 45% duration（需特別注意演講節奏、彩排時驗證）

| ch | step | beats | ~dur | wait | climax | tag | script.L |
|---|---|---|---|---|---|---|---|
| 1 | 1 心虛開場 | 1 | 10s | - | - | - | L1 |
| 1 | 2 心理學系 | 1 | 8s | - | - | - | L5 |
| 1 | 3 主題揭曉 | 1 | 10s | - | - | - | L9 |
| 1 | 4 捷運看正妹 | 1 | 10s | - | - | - | L15 |
| 1 | 5 Code Bullet | 1 | 8s | - | - | - | L19 |
| 1 | 6 繼續發呆 | 1 | 6s | - | - | - | L21 |
| 1 | 7 沒手機解數獨 | 1 | 8s | - | - | - | L25 |
| 1 | 8 BOOM | 3 | 12s | ~2s | A+C | punchline | L29-37 |
| 2 | 1 supervised | 1 | 14s | - | - | - | L49-55 |
| 2 | 2 unsupervised | 1 | 13s | - | - | - | L57-61 |
| 2 | 3 RL+AlphaGo | 1 | 15s | - | - | - | L63-67 |
| 2 | 4 cliffhanger | 1 | 8s | - | - | polish | L71 |
| 3 | 1 LLM 路線 | 1 | 14s | - | - | - | L75-77 |
| 3 | 2 VS 對比 | 1 | 14s | - | - | - | L81-89 |
| 3 | 3 OK 純 RL | 1 | 7s | - | - | polish | L93-95 |
| 4 | 1 Kaggle | 1 | 12s | - | - | - | L99-103 |
| 4 | 2 supervised 拒絕 | 1 | 11s | - | - | polish | L105-107 |
| 4 | 3 受害者 | 4 | 14s | ~2s | A+C+E | punchline | L111-121 |
| 4 | 4 封 IP + proxy | 1 | 13s | - | - | - | L125-133 |
| 5 | 1 結果我錯了 | 4 | 14s | ~3s | A+C | punchline | L141-147 |
| 5 | 2 838 行 | 1 | 8s | - | - | - | L151 |
| 5 | 3 debug 爆炸 | 1 | 7s | - | - | - | L153 |
| 5 | 4 第一件學到 | 1 | 15s | - | - | polish | L157-163 |
| 6 | 1 我又錯了 | 3 | 11s | ~3s | A+C | punchline | L171-173 |
| 6 | 2 套皮仔策略 | 1 | 9s | - | - | - | L167-177 |
| 6 | 3 新女生加分 | 1 | 12s | - | - | - | L181-185 |
| 6 | 4 曲線爬升 | 1 | 10s | - | - | - | L181 |
| 6 | 5 卡平段 | 1 | 12s | - | - | - | L187 |
| 6 | 6 備胎 ★★★ | 3 | 12s | **~5-6s ⚠** | A+B+C+E+G | punchline ★★★ | L189 |
| 6 | 7 偷吃步 | 1 | 7s | - | - | - | L195-199 |
| 7 | 1 重寫宣告 | 1 | 11s | - | - | polish | L201-205 |
| 7 | 2 顛倒驗證 | 1 | 14s | - | - | - | L201-205 |
| 7 | 3 13 招階梯 | 1 | 19s | - | - | - | L209-211 |
| 7 | 4 舊 vs 新 | 1 | 17s | - | - | - | L215-225 |
| 7 | 5 Action 擴增 | 1 | 13s | - | - | - | L229-233 |
| 7 | 6 機率 0 | 3 | 16s | ~4-5s | A+B+C+E | punchline | L237 |
| 7 | 7 老油條 ★★★ | 6 | 26s | ~8s | A+E+G×2 + B×2 | punchline ★★★ | L241-257 |
| 7 | 8 死結 | 1 | 20s | - | - | - | L265-269 |
| 8 | 1 反向思考 | 1 | 10s | - | - | polish | L273-275 |
| 8 | 2 3 格空 | 1 | 12s | - | - | - | L277-279 |
| 8 | 3 反向課程動畫 | 1 | 12s | - | - | - | L281-285 |
| 8 | 4 +20 → +50 翻牌 | 1 | 10s | - | - | - | L287-291 |
| 8 | 5 光講不夠看 | 1 | 9s | - | - | - | L297-299 |
| 8 | 6 visualizer 按鈕 | 1 | 10s+visualizer | - | - | - | L299 |
| 9 | 1 tensorboard + 磨合期 | 1 | 12s | - | - | - | L303-307 |
| 9 | 2 核心金句 | 1 | 14s | - | - | - | L309 |
| 9 | 3 RL 對等 | 1 | 12s | - | - | - | L313-317 |
| 9 | 4 飛機 + 鳥 | 1 | 10s | - | - | - | L319 |
| 9 | 5 戀愛 a callback | 4 | 18s | ~4.5s | A+C | punchline | L323-329 |
| 9 | 6 戀愛 b 4 考題 | 1 | 18s | - | - | - | L333-343 |
| 9 | 7 plasticity 引出 | 1 | 8s | - | - | - | L347-349 |
| 9 | 8 plasticity 三欄 | 1 | 12s | - | - | - | L351 |
| 9 | 9 plasticity 機制 | 1 | 12s | - | - | - | L353-355 |
| 9 | 10 MBTI + 業務工作 | 複合 | 22s | (auto) | - | - | L359-365 |
| 9 | 11 警語 ★★ | 4 | 18s | **~6-7s ⚠** | A+C+G | punchline ★★ | L367-369 |
| 9 | 12 職場祝福 | 1 | 12s | - | - | - | L371-373 |
| 9 | 13 電費小偷 ★★★ | 4 | 28s | **~13-15s 🚩** | A+B+C+E+G + boom-ring | punchline ★★★ | L375 |

**節奏紅旗解讀**:
- **ch6 s6 備胎** ⚠: beat 3 wait 3-4s（笑點）合理、總 5-6s 在 12s step 內、實際口播時間 ~6s 緊但 OK
- **ch9 s11 警語** ⚠: beat 4 wait 3-4s（反轉揭曉）合理、總 6-7s 在 18s step 內、口播 ~11s OK
- **ch9 s13 電費小偷** 🚩: beat 3 wait 5-7s + beat 4 wait 5s+ 合計 ~13-15s、扣動畫後**演講者實際口播只剩 ~10s**、彩排時請特別注意 cue 不要超時

---

## 1. coldopen — 心虛開場 · 心理學系 · 捷運靈感（8 step · ~72s）

> **敘事弧**: 心虛 → 心理學系 → 主題 → 捷運看正妹 → Code Bullet → 繼續發呆（喜劇）→ 當兵解數獨 → BOOM 兩個靈感結合

**信息池**:
- 自我揭露「心虛」「報告太不正經」（L1）
- 背景標籤「心理學系畢業」（為 RL/腦科學/plasticity 鋪墊）（L5）
- 主題揭露「訓練 AI 解數獨」（L9）
- 場景具象「捷運看正妹發呆」（L15）
- Code Bullet flappy bird 影片靈感（L19）
- 場景具象「當兵沒手機解數獨」（L25）
- punchline 金句「靈感就是這麼莫名其妙地蹦出來」（L37）

### step 1: 心虛開場 (10s · 單 beat)

- **顯示內容**: 全屏「心 虛」巨字 sticker（紅底、6px 黑邊、16px hard shadow、微旋轉 -3°）+ 角標「期中報告」黃 sticker + 字幕「報告太不正經、請各位同學和老師多包涵」
- **類型**: cinematic
- **進場**: 黑屏 → cream 紙質淡入(400ms) → 心虛 sticker scale 0.7→1 + rotate -3° (overshoot) → 字幕從左 mask-reveal
- **持續微動**: 心虛 sticker ±4px 4s ease-in-out infinite
- **口播對應**: script.md L1

### step 2: 心理學系畢業 + 敬請期待 (8s · 單 beat)

- **顯示內容**: 「心 理 學 系 · 畢業」card hero（白底、6px 黑邊、12px shadow、微旋轉 -2°）+ 紅色箭頭 + 黃色高亮「敬請期待」sticker（伏筆 RL/腦科學/plasticity）
- **類型**: cinematic + depth
- **進場**: 主 card 從右下 translateY + rotate (overshoot) → 箭頭從卡片左側 stroke-draw → 「敬請期待」黃 sticker 從右側 scale 0→1 stamp
- **口播對應**: script.md L5

### step 3: 主題揭曉 — 訓練 AI 解數獨 (10s · 單 beat)

- **顯示內容**: 上方 kicker「期中主題」黑底 cream 字 + 中央 cinematic hero「訓 練 AI 解 數 獨」（AI 紅底、解數獨黃底兩塊強調 box、text-stroke 描邊樣式）+ 四個漂浮裝飾形狀（紫方塊 / 黃星旋轉 / 紅圓 hard shadow / 描邊問號）
- **類型**: cinematic + depth
- **進場**: kicker 從左 slide-in → hero scale 0.85 + letter-spacing 0.1em → scale 1 + letter-spacing -0.04em (overshoot 720ms) → 4 裝飾物 stagger 從各角飛入
- **持續微動**: 黃星 spin-slow 12s、紫方塊 float ±16px 4s
- **口播對應**: script.md L9

### step 4: 捷運上正大光明看正妹 (10s · 單 beat)

- **顯示內容**: 過場字幕「靈感哪來呢？某天捷運上⋯」+ 捷運窗景視覺（紫底窗 + 黑邊、車廂線條 backdrop）+ 第一張 sticker「正妹發呆中」黃底 cloud 樣式（左下、微旋轉 -4°）
- **類型**: depth + progressive
- **進場**: 捷運背景 fade-in(300ms) → 字幕從上 fade-down → 窗景 stamp-in → 正妹 sticker 從左下 stamp-in (stagger 240ms)
- **depth layers**: 背景線條 0.5 opacity / 中景窗 1.0 / 前景 sticker 1.2
- **口播對應**: script.md L15

### step 5: Code Bullet flappy bird 靈感 (8s · 單 beat)

- **顯示內容**: 捷運背景延續 + 第一張 sticker（正妹左下）+ 第二張 sticker「Code Bullet · flappy bird」紫底（右上、微旋轉 3°）+ 思考氣球線從正妹 → flappy bird 虛線連接
- **類型**: progressive
- **進場**: 左鍵觸發 → 第二張 sticker 從右上 stamp-in(240ms) + 思考線 stroke-draw(600ms)
- **口播對應**: script.md L19

### step 6: 繼續發呆（喜劇延續拍）(6s · 單 beat)

- **顯示內容**: 捷運背景與兩 sticker 維持不動 + 中央正妹 sticker 上方「⋯⋯」省略號氣球（cream 底、黑邊框、輕微浮動）+ 角標小字「然後我繼續發呆⋯」
- **類型**: cinematic + interactive
- **進場**: 「⋯⋯」氣球 stamp-in(300ms) + 緩慢 pulse(1s ease-in-out infinite)
- **氣質**: 喜劇半拍、給觀眾笑點 + 演講者口語停頓、強化反差為 BOOM 鋪墊
- **口播對應**: script.md L21

### step 7: 當兵沒手機解數獨 (8s · 單 beat)

- **顯示內容**: 捷運背景延續 + 三張 sticker（正妹左下 + flappy bird 右上 + 紅底白字「沒手機·解數獨」右下、微旋轉 2°）
- **類型**: progressive
- **進場**: 第三張 sticker 從右下 stamp-in(240ms)、其他不重畫
- **口播對應**: script.md L25

### step 8: BOOM · 兩個靈感結合 (12s · 3 beat · punchline · placeholder)

```
┌──────────────────────────────────────┐
│   ◯◯◯ ← 雙圈爆破 (黃外 + 紅內)         │
│   ◯●◯  motif/boom-double-ring 首發    │ ← beat 1
│   ◯◯◯                                │
│                                      │
│   ┌──────────────────────────┐       │
│   │  訓 練 AI 解 數 獨        │ ← beat 2 (auto)
│   │  (cream + 6px 黑邊)      │       │
│   └──────────────────────────┘       │
│                                      │
│ [靈感就是這麼 *莫名其妙* 地蹦出來]    │ ← beat 3
│   (黃底 placeholder → mask-reveal)    │
└──────────────────────────────────────┘
背景三 sticker (正妹 / flappy / 解數獨) 抖動 150ms
```

- **顯示內容**: 三 sticker 抖動 → 雙圈爆破 → 中央 cream boom card「訓 練 AI 解 數 獨」→ 下方 punchline 黃底高亮「靈感就是這麼莫名其妙地蹦出來」
- **類型**: cinematic + data-viz
- **placeholder**: 下方黃底高亮 box 預留位、內容 hold 到 beat 3
- **Motif**: `motif/boom-double-ring`（首發）· `motif/yellow-highlight`
- **Climax 火力 輕量**: A+C → outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` boom-burst: 三 sticker 背景輕微抖動(150ms shake) → 雙圈爆破覆蓋（黃外圈 + 紅內圈、border 8px、scale 0→1 overshoot、stagger 黃 80ms / 紅 120ms）
  - · cue: "Boom——"（演講者話一出口就點）
- **beat 2** `[auto, 400ms]` boom-card: 中央 cream「訓 練 AI 解 數 獨」boom card stamp 進場（accent red AI 標、6px 黑邊、16px shadow、微旋轉 -2°、scale 0.8→1 overshoot）
  - · 自動觸發、銜接「兩個想法結合在一起、訓練 AI 解數獨」口播
- **beat 3** `[click]` punchline-reveal: 下方預留黃底空高亮 box → 填入「靈感就是這麼 *莫名其妙* 地蹦出來」mask-reveal(720ms 左到右)
  - · cue: "很多人問我靈感哪來的、我也不知道怎麼解釋——靈感就是這麼"（「莫名其妙」前點下、字一邊出演講者一邊念）
  - · wait: 1-2s 觀眾消化

- **口播對應**: script.md L29 (beat 1-2) + L35-37 (beat 3)

---

## 2. ml-map — 機器學習地圖（4 step · ~50s）

> **敘事弧**: supervised（抄筆記）→ unsupervised（折衣服）→ RL + AlphaGo → cliffhanger「ChatGPT/Claude 是哪一招？」

**信息池**:
- 三大塊 supervised / unsupervised / RL（L49-67）
- 日常比喻「看著答案抄筆記」「自己分類整理（折衣服）」「試錯加獎懲（訓狗握手）」（L51-65）
- 名人事件 AlphaGo 打敗世界圍棋王（L67）
- cliffhanger「那 ChatGPT 跟 Claude 又是哪一招？」（L71）

### step 1: supervised — 看著答案抄筆記 (14s · 單 beat)

- **顯示內容**: 上方 kicker「機器學習 · ①/3」黑底白字 + 中央「supervised」大字 + 副標「白話：看著答案抄筆記」+ 右側「老師給題目+答案·你硬背」插畫（純 SVG 老師線稿 + 學生 + 紙張）
- **類型**: cinematic + depth
- **進場**: kicker 從上 slide-in → 「supervised」大字 mask-reveal 左到右 → 副標 fade-up → 右側插畫 stagger（老師 → 學生 → 紙張）
- **口播對應**: script.md L49-55

### step 2: unsupervised — 自己分類整理 (13s · 單 beat)

- **顯示內容**: kicker「②/3」+ 「unsupervised」大字 + 副標「自己分類整理」+ 右側折衣服插畫（一堆衣服 → 三疊分顏色、純 SVG）
- **類型**: cinematic + depth
- **進場**: kicker 切換 +1 動畫 → unsupervised 大字 mask-reveal → 衣服堆 stagger 散開（一堆 → 三疊 1200ms）
- **口播對應**: script.md L57-61

### step 3: RL + AlphaGo (15s · 單 beat)

- **顯示內容**: kicker「③/3」+ 「RL · reinforcement learning」大字 + 副標「試錯加獎懲」+ 訓練狗握手插畫 + **AlphaGo 標籤 sticker**（accent red 底、黑邊、微旋轉 -2°、stamp-in）
- **類型**: cinematic + depth + data-viz
- **進場**: kicker 切換 → RL 大字 mask-reveal → 狗握手插畫 → **AlphaGo sticker 砸下** (scale 1.4→1 snap, overshoot)
- **持續微動**: AlphaGo sticker 浮動
- **climax**: AlphaGo sticker 砸下瞬間
- **口播對應**: script.md L63-67

### step 4: cliffhanger「ChatGPT/Claude 是哪一招？」 (8s · 單 beat)

- **顯示內容**: 全螢幕單句「那 ChatGPT 跟 Claude · 又是哪一招？」cream 底 + 黑大字 + 中央問號黃底大字（旋轉 -8°）
- **類型**: cinematic
- **進場**: cream 底 fade-up → 問句 mask-reveal 左到右(800ms) → 問號 sticker 從天上 drop-in (overshoot bounce) + **720° 完整旋轉**（與 drop-in 同步、暗示「問題在飛轉」）
- **Motif**: `motif/yellow-highlight`（問號用黃底放大 +10%）
- **氣質**: 換語氣、留 1-2s 給演講者口播 cliffhanger
- **口播對應**: script.md L71

---

## 3. llm-vs-rl — ChatGPT 跟 Claude 在哪？（3 step · ~35s）

> **敘事弧**: LLM = supervised + RLHF → VS 對比「LLM 模仿 vs 我這套自己摸出規則」→ OK 純 RL、第一步找資料

**信息池**:
- LLM 路線「supervised + RLHF」「整個人類網路寫過的東西全部讀一遍 + 人類教他怎麼回」（L75-77）
- 對比 anchor「LLM = 模仿」vs「我這套 = 自己摸出規則」（L83-89）
- 場景比喻「把 AI 丟進什麼都不知道的房間」（L89）
- cliffhanger「OK 所以我要走純 RL、第一步找資料」（L93-95）

### step 1: LLM 路線 (14s · 單 beat)

- **顯示內容**: 左欄「LLM」hero（佔 60% 寬）+ 副標「supervised + RLHF」紫底標籤 + 底下「把整個人類網路寫過的東西全部讀一遍」標語 + 背景文字流動效果（低密度灰色字 grid 微動）
- **類型**: cinematic + depth
- **進場**: 左欄 wipe-in 左到右 → 「LLM」大字 stamp(overshoot) → 副標 + 背景文字 grid stagger fade-in
- **持續微動**: 背景文字 grid 緩慢 translateY 上飄
- **口播對應**: script.md L75-77

### step 2: VS 對比 (14s · 單 beat)

```
┌──────────────────────────┐ ┃ ┌──────────────────────────┐
│         LLM              │ ┃ │       我的 AI             │
│  ┌────────────────┐      │ ┃ │                          │
│  │supervised+RLHF │      │ ┃ │     ┌───────┐            │
│  └────────────────┘      │ ┃ │     │ 房 門 │ Phosphor   │
│                          │ ┃ │     └───────┘ Door icon  │
│  把整個人類網路寫過的     │ ┃ │                          │
│  東西全部讀一遍          │ ┃ │                          │
│                          │ ┃ │                          │
│ ▒▒ 背景文字 grid 微動 ▒▒  │ ┃ │                          │
│                          │ ┃ │                          │
│ [LLM = 模仿] (紅 stamp)  │ ┃ │ [自己摸出規則] (黃 stamp) │
└──────────────────────────┘ ┃ └──────────────────────────┘
         60%             [VS]            40%
                       (旋轉 sticker、6px 黑色分隔線)
hover 任一側 → 該側 zoom 1.02 + 對立側 dim 0.6
```

- **顯示內容**: 右欄「我的 AI」hero（佔 40%）+ 中央粗 6px 黑色分隔線 + 「VS」大字旋轉 sticker + 「LLM = 模仿」紅 stamp（左欄）vs「自己摸出規則」黃 stamp（右欄）+ 右欄底房間 / 門 SVG icon（門關著、AI 在房內）
- **類型**: comparison + interactive
- **進場**: 右欄 wipe-in 右到左 → VS sticker 從 scale 0 stamp 中央 → 兩 stamp 同時砸下（紅左、黃右）→ 房間 icon fade-in
- **互動**: hover 左欄 → 左欄 zoom 1.02 + 右欄 dim 0.6（反之亦然）、純視覺不影響推進
- **口播對應**: script.md L81-89

### step 3: OK 純 RL · 找資料 (7s · 單 beat)

- **顯示內容**: 全螢幕單句「OK · 所以我要走純 RL / 第一步是找資料」cream 底大字（OK 紅底、純 RL 黃底）
- **類型**: cinematic
- **進場**: split-screen 兩半 collapse → cream 全屏 → 標題 mask-reveal
- **Motif 套用**: `motif/halftone-burst` 微縮版（半徑限 60px、不放射超出 OK box、500ms scale 0→2 opacity 1→0、「OK」紅底高亮切換到位瞬間觸發、暗示「決定下了」）
- **氣質**: 短促、cliffhanger
- **口播對應**: script.md L93-95

---

## 4. data-hunt — 找資料：從 Kaggle 到爬蟲（4 step · ~50s）

> **敘事弧**: Kaggle (supervised) → 拒絕 → 終極目標霸榜 → 受害者 websudoku → 封 IP → proxy 池

**信息池**:
- 資料來源 Kaggle（先去）→ websudoku.com（後來爬）(L99 + L117)
- 拒絕「題目+答案 = supervised」與「我要 AI 自己摸出規則」衝突（L105-107）
- 戰略「終極目標霸榜 → 題目來源得從那些網站」（L111-115）
- 爬蟲 punchline「這個受害者」+ 「沒有現代防爬蟲、簡簡單單被攻破」（L117-121）
- 反爬「20 題就被封 IP」→ proxy 池（類似 VPN、好幾萬個 IP）（L125-133）

### step 1: Kaggle 介紹 (12s · 單 beat)

- **顯示內容**: Kaggle 標籤 sticker（黃底、微旋轉 2°）+ 「題目+完整答案 整理好的資料集」副標 + 兩三個資料 card 浮現 + 角落「但問題來了」紅色叉叉動畫覆蓋（從中心 burst-out）
- **類型**: progressive + cinematic
- **進場**: Kaggle sticker stamp-in → 資料 card stagger（3 張 100ms 間隔）→ 紅色叉叉 burst-in (scale 0→1.2→1 overshoot) 覆蓋 70% 畫面
- **climax**: 紅色叉叉 burst 瞬間
- **口播對應**: script.md L99-103

### step 2: supervised 路線拒絕 (11s · 單 beat)

- **顯示內容**: 「supervised 路線 · 拒絕」紅 stamp full-bleed（旋轉 -5°、stamp-in、shadow 大）+ 右側對比「我要 AI · 自己摸出規則」黃底 sticker
- **類型**: cinematic + comparison
- **進場**: 紅 stamp 從天上 drop(overshoot bounce) → 右側黃 sticker stamp-in
- **Motif 套用**: `motif/ink-splatter` 輕量版（4 個黑點、半徑 40-80px、紅 stamp 砸下瞬間配合、強化「最終決定」氣勢）
- **climax**: 紅 stamp 砸下瞬間
- **口播對應**: script.md L105-107

### step 3: 終極目標 + 受害者 (14s · 4 beat · punchline · placeholder)

- **顯示內容**: 「終極目標：去每個數獨網站霸榜」hero + websudoku URL sticker（黑底 cream 字 mono「websudoku.com」+ cursor 閃爍）+ 預留紅 sticker 空形狀（beat 3 填「這個受害者」）+ 副標「簡簡單單被我攻破」
- **類型**: cinematic + depth
- **placeholder**: URL sticker 旁紅 sticker 空形狀、文字 hold 到 beat 3
- **Motif**: `motif/red-stamp`
- **Climax 火力 輕量+**: A+C+E（stamp 性質、ink-splatter 配合）→ outline-visual.md §8
- **持續微動**: URL 後 cursor 閃爍

**Beat 結構**:
- **beat 1** `[click]` kicker: 上方 hero「終極目標：去每個數獨網站霸榜」從上 fade-in
  - · cue: "我的終極目標是把我訓練好的 AI 拿去每個數獨網站..."
- **beat 2** `[click]` url-sticker: 中央 websudoku URL sticker 從左 slide-in（黑底 cream 字 mono + cursor 閃爍）
  - · cue: "於是我找到了 websudoku.com..."
- **beat 3** `[click]` victim-stamp: URL 旁預留紅 sticker 形狀 → 文字「這個受害者」打入 + 紅 stamp 微旋轉斜貼 + A+C+E
  - · cue: "..."（演講者直接念出「這個受害者」當下點、梗一說就視覺同步）
  - · wait: 1-2s 笑點
- **beat 4** `[auto, 200ms]` subtitle: 副標「簡簡單單被我攻破」fade-up

- **口播對應**: script.md L111-121

### step 4: 封 IP + proxy 池 (13s · 單 beat)

```
┌──────────────────────────────────────────┐
│      [才爬 20 題就被封 IP] (紅警示)        │
│                                          │
│         proxy 池 · 好幾萬個 IP            │
│                                          │
│   ▣ ▣ ▣ ▣ ▣ ▣  ← 30+ IP 小卡 grid          │
│   ▣ ▣ ▣ ▣ ▣ ▣     (半透明、漂浮)          │
│   ▣ ★ ▣ ▣ ▣ ▣  ← 每 200ms 一個高亮         │
│   ▣ ▣ ▣ ▣ ▣ ▣     + IP 數字切換            │
│   ▣ ▣ ▣ ▣ ▣ ▣                            │
└──────────────────────────────────────────┘
```

- **顯示內容**: 「才爬 20 題就被封 IP」紅警示 hero + IP 封鎖圖示（黑邊框 + 紅斜線）→ **proxy 池視覺化**「類似 VPN · 好幾萬個 IP」+ 多個半透明 IP 小卡 grid (30+ 卡) 漂浮 + 隨機 IP 切換動畫（每 200ms 一個卡高亮 + 切下個 IP 數字）
- **類型**: data-viz + cinematic
- **進場**: 紅警示 hero(800ms hold) → 警示淡化、IP grid 從中央 burst-out(stagger 30 個 30ms 間隔) → IP 切換動畫啟動
- **climax**: IP grid burst 瞬間
- **持續微動**: 隨機卡片高亮輪播
- **口播對應**: script.md L125-133

---

## 5. legacy — 一句搞定的幻想 → 800 多行單檔（4 step · ~51s）

> **敘事弧**: 天真期 → 丟 prompt 給 Claude →「結果我錯了」#1 崩盤 → 838 行單檔 → debug 爆炸 → 第一件學到「架構自己想清楚再請 AI 分工」→ 套皮仔過渡

**信息池**:
- 戲劇崩盤「我以為⋯⋯結果我錯了」（L141-145）
- 程式碼 `legacy/app/sudoku/torch_agent.py` 838 行（畫面值；口播照「800 多行」）（L151）
- debug 痛點「每改一個地方都東倒西歪、自己都看不懂、debug 成本爆炸」（L153）
- 第一件學到「不能再偷懶全靠 AI。架構、演算法自己先想清楚、再請 AI 分工」（L157-159）
- 過渡「放棄這版本、轉而當套皮仔」（L163）

### step 1: 結果我錯了 (14s · 4 beat · punchline · placeholder)

- **顯示內容**: cream + 強紅邊崩盤感 + 上方字幕「我那時候很天真」+ prompt 對話框「幫我寫一個訓練 AI 解數獨的程式」sticker + 下方崩盤句空框（cream 大字框、6px 紅邊、微旋轉 1°、閃爍游標 `_`）→ beat 4 填入「⋯⋯結果我錯了」
- **類型**: cinematic
- **placeholder**: 「結果我錯了」位置預留 cream 大字框 + 6px 紅邊 + 閃爍游標、文字 hold 到 beat 4
- **Motif 首發**: `motif/crash-line`（後續 ch6 s1、ch9 s11 復用）
- **Climax 火力 輕量**: A+C 跟紅邊 flash 2× 疊加 → outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` kicker: 「我那時候很天真」字幕 fade-up + halftone dots 加密 1.5×
  - · cue: "我那時候還很天真、覺得——"
- **beat 2** `[click]` prompt-box: 中央 prompt 對話框「幫我寫一個訓練 AI 解數獨的程式」stamp-in（cream 底、6px 黑邊、12px shadow、模擬 chat input）
  - · cue: "不如我丟一句『幫我寫一個訓練 AI 解數獨的程式』給 Claude？他應該能搞定吧？"
- **beat 3** `[click]` placeholder-frame: 下方崩盤句空框出現（cream 大字框、6px 紅邊、16px shadow、微旋轉 1°、閃爍游標、無文字）
  - · cue: "⋯⋯"（演講者拖長尾音、給空框出現的反應時間）
  - · wait: 1s 留白
- **beat 4** `[click]` crash-fill: 空框內 mask-reveal 填入「⋯⋯結果我錯了」+ 紅邊 flash 2×(200ms 一次、200ms 間隔) + shadow burst 8px→16px + A+C
  - · cue: "結果我錯了"（演講者念出當下視覺同步爆）
  - · wait: 2s 觀眾消化

- **口播對應**: script.md L141-147

### step 2: 838 行單檔 (8s · 單 beat)

- **顯示內容**: cream 上一坨深色文字塊（讀真實 `legacy/app/sudoku/torch_agent.py` 部分內容、syntax 高亮輕量化）+ 角標「`torch_agent.py · 838 lines`」+ 副標「什麼都塞在裡面」
- **類型**: cinematic + data-viz
- **進場**: 程式碼 sticker 從下方快速 slide-up(佔 70% 高、400ms) → 角標 stamp-in 右上
- **climax**: 角標 838 數字 count-up(0→838、600ms)
- **持續微動**: 程式碼塊內輕微捲動（背景慢速 translateY、暗示「巨量」）
- **效能 note**: 838 行全 DOM 會卡、實作時用 virtual scroll（只 render viewport 內 ~30 行 + 背景 translateY 模擬）
- **口播對應**: script.md L151

### step 3: debug 爆炸 (7s · 單 beat)

- **顯示內容**: 「每改一個地方都東倒西歪」hero + 紅色叉叉飛來飛去動畫（chaotic、6-8 個叉叉隨機位置 spawn + scale + fade）+ 「debug 成本爆炸」punchline kicker
- **類型**: cinematic + data-viz
- **進場**: hero 文字 fade-in(300ms) → 紅叉叉 burst 一波(爆炸感、500ms) → 持續隨機 spawn 叉叉
- **climax**: 「debug 成本爆炸」punchline mask-reveal
- **氣質**: chaotic、視覺亂、暗示痛苦
- **口播對應**: script.md L153

### step 4: 第一件學到 + 套皮仔過渡 (15s · 單 beat)

- **顯示內容**: 「架構、演算法都得自己先想清楚、再請 AI 分工」cream 底黑大字 hero（關鍵詞「架構」「演算法」「自己」「分工」黃底高亮 sticker）+ 過渡 footer「轉而當個套皮仔 →」
- **類型**: cinematic
- **進場**: chaotic 叉叉 fade-out → 底色穩定 → hero 標語慢速 mask-reveal 左到右(1200ms) → 4 關鍵詞 stagger 黃底高亮(per word 250ms)
- **Motif 套用**: `motif/ink-splatter` 微縮（4 關鍵詞 stagger 黃底高亮時、每個關鍵詞下方加 1 個小黑點、半徑 20-40px、隨機位置、與該詞 highlight 同時出、強化金句的物理書寫感）
- **climax**: 4 黃底全亮的瞬間
- **轉場**: footer 從下 slide-up、暗示下章
- **口播對應**: script.md L157-163

---

## 6. sb3 — 套皮仔 + 戀愛 hook a · 新女生加分到備胎（7 step · ~73s）

> **敘事弧**: 套皮仔 → 「我又錯了」#2 崩盤 → 計分策略「填對一格就給分」→ 新女生加分（戀愛 hook a 出場）→ 曲線爬升 → 卡平段 → 備胎 ★★★ → 偷吃步揭穿

**信息池**:
- 套皮仔「社群現成 Python 工具箱、負責訓練的數學邏輯底層架構」（L167-169）
- 崩盤「正當我以為成了套皮仔、就能成功訓練 AI⋯⋯我又錯了」（L171-173）
- 計分策略「只要他填對一格就給分數」（L177）
- 戀愛 hook a 出場「就像剛認識新女生、每次聊天都覺得對方也喜歡你、一直給你加分」（L181-183）
- 瓶頸「AI 只拿那些必拿的固定分數就不思進取、一直沒辦法完整解出一道題」（L187）
- 戀愛 hook a 收「這個女生只把你當備胎」（L189）
- 揭穿「AI 學會了偷吃步」+ 「計分標準寫錯了、AI 就會找漏洞作弊」（L195-199）

### step 1: 我又錯了 (11s · 3 beat · punchline · placeholder)

- **顯示內容**: 上方字幕「正當我以為成了套皮仔⋯⋯」+ 中央崩盤句空框（cream 大字框 + 6px 紅邊 + 微旋轉 -1° + 閃爍游標）→ beat 3 填入「⋯⋯我又錯了」
- **類型**: cinematic
- **placeholder**: 「我又錯了」位置先放空框、文字 hold 到 beat 3
- **Motif 復用**: `motif/crash-line`（ch5 s1 首發、同款 motif rhyme）
- **Climax 火力 輕量**: A+C（與 ch5 s1 同款手法、motif rhyme 一致性）→ outline-visual.md §8
- **氣質**: 重複 ch5 s1 崩盤感、形成 motif rhyme「結果我錯了 → 我又錯了」雙拍

**Beat 結構**:
- **beat 1** `[click]` kicker: 上方字幕「正當我以為成了套皮仔⋯⋯」fade-down
  - · cue: "正當我以為成了套皮仔、就能成功訓練出解數獨的 AI..."
- **beat 2** `[click]` placeholder-frame: 中央崩盤句空框出現（同 ch5 s1 同款 motif、cream 大字框 + 6px 紅邊 + 微旋轉 -1° + 內部閃爍游標）
  - · cue: "⋯⋯"（拖長尾音、觀眾此時應該已經認出 motif）
  - · wait: 0.8s（比 ch5 s1 短、因為觀眾已熟悉這 motif）
- **beat 3** `[click]` crash-fill: 空框內 mask-reveal 填入「⋯⋯我又錯了」+ 紅邊 flash + shadow burst + A+C
  - · cue: "我又錯了"
  - · wait: 1-2s 觀眾反應（這次因「又」motif rhyme 應該更有反應）

- **口播對應**: script.md L171-173

### step 2: 套皮仔策略 + 填對給分 (9s · 單 beat)

- **顯示內容**: 左側「社群現成 Python 工具箱」標籤 sticker（紫底、微旋轉）+ 右側「只要他填對一格 · 就給分數」計分表 hero（卡片化、黑邊 + shadow + 填對 = +1 動畫）
- **類型**: cinematic + data-viz
- **進場**: 左 label slide-in → 右計分表 card stamp-in → 內部「+1」數字動畫(count-up 0→1)
- **口播對應**: script.md L167-177

### step 3: 戀愛 hook a 出場 — 新女生加分 (12s · 單 beat)

- **顯示內容**: cream 底 + 中央「剛認識的新女生」sticker（粉紅色 + 微旋轉、暗示「新鮮」）+ 「+/+/+」浮動加分動畫（多個綠色 + 符號從下浮起）+ 副標「聊天都覺得對方也喜歡你」
- **類型**: cinematic + progressive
- **Motif 首發**: `motif/girl-new`（後續 ch9 s5 戀愛 a callback 復用）
- **進場**: 中央 sticker stamp-in → 「+/+/+」符號連續 spawn from below + float-up + fade(持續動畫) → 副標 fade-up
- **持續微動**: 加分符號連續浮動
- **口播對應**: script.md L181-185

### step 4: AI 得分曲線爬升 (10s · 單 beat)

```
┌────────────────────────────────────────┐
│  [新女生]              得分曲線         │
│  (粉紅 sticker         ╱─── (卡平段)   │
│   左側保留)          ╱                 │
│                  ╱+ ╱                   │
│              ╱+   ╱                    │
│           ╱+    ← +/+/+ 沿曲線標記      │
│       ╱+                                │
│   ╱+                                    │
│ ╱                                       │
│ 0────────────────────────────────────→ │
│       SVG path stroke-dasharray 0→100%  │
│              (2s ease-out draw)          │
└────────────────────────────────────────┘
```

- **顯示內容**: 左側保留新女生 sticker + 右側「AI 得分曲線」(SVG path、黑線粗、cream 底)、enter 時 path stroke-dasharray 0→100% 自動 draw(2s)、爬升曲線 + 標籤「+/+/+」對應點亮
- **類型**: data-viz
- **進場**: 曲線從左到右 stroke-draw(2s ease-out) + 對應 +/+/+ 沿曲線標記 stagger
- **climax**: 曲線完成的瞬間
- **口播對應**: script.md L181

### step 5: 卡平段 · 不思進取 (12s · 單 beat)

- **顯示內容**: 曲線進入畫面停留、卡平段 highlighted(紅色背景帶) + 字幕「拿那些必拿的固定分數 · 就不思進取」+ 「一直沒辦法完整解出一道題」副標 + 新女生 sticker 慢慢淡化 / 變灰
- **類型**: data-viz + cinematic
- **進場**: 卡平段紅色 highlight band fade-in → 字幕 mask-reveal → 新女生 sticker grayscale 漸變(1s)
- **氣質**: 從亢奮 → 失落
- **口播對應**: script.md L187

### step 6: 備胎 ★★★ (12s · 3 beat · punchline · placeholder · 全 ch6 最重笑點)

```
┌────────────────────────────────────────┐
│                                        │
│      [⚫ 黑色閃爍 100ms]    ← beat 1     │
│                                        │
│   ┌───────────────────────────┐         │
│   │                           │         │
│   │  紅底 cream 邊 空白 sticker│ ← beat 2│
│   │     (內部「  」空白)       │  (placeholder)
│   │     旋轉 -3°、超大         │         │
│   └───────────────────────────┘         │
│                                        │
│   ╔═══════════════════════════╗ ← beat 3│
│   ║         備 胎              ║  fill   │
│   ║   (mask-reveal、scale 1.4→1│ + A+B+C │
│   ║    overshoot + shadow burst│ + E + G │
│   ╚═══════════════════════════╝ (★★★)  │
│                                        │
│  [看似有進展 · 結果什麼都沒發生]         │
└────────────────────────────────────────┘
   Climax 全套: A 震屏 / B halftone-burst /
   C overshoot / E ink-splatter / G spotlight
```

- **顯示內容**: 中央紅底 cream 邊空白 sticker（旋轉 -3°、超大、shadow 16px、內部空白字符）+ 下方副標「看似有進展 · 結果什麼都沒發生」→ beat 3 填入「備胎」
- **類型**: cinematic
- **placeholder**: 「備胎」位置預先放紅底 cream 邊空白 sticker、文字 hold 到 beat 3
- **Motif**: `motif/red-stamp`（紅 stamp 從天砸下、overshoot bounce、shadow burst）
- **Climax 火力 ★★★ 全套**: A + B + C + E + G（全片 #1 重要 climax 全火力）→ outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` flash: 黑色閃一下(100ms flash)
  - · cue: "結果後面開始遇到瓶頸——AI 只拿那些必拿的固定分數就不思進取了..."（鋪語境）
  - · wait: 0.5s 給觀眾「視覺從錯覺切到現實」反應時間
- **beat 2** `[click]` subtitle-and-placeholder: 中央紅底空白 sticker（內無字、僅 cream 邊輪廓）+ 下方副標「看似有進展 · 結果什麼都沒發生」fade-up
  - · cue: "換句話說、這個女生只把你當——"（拉長尾音「當——」、給空 sticker 出現的反應時間、觀眾此時應該開始猜了）
  - · wait: 1-2s 留懸念（這是全 step 最關鍵的停拍、演講者不要急著點下一 beat）
- **beat 3** `[click]` bei-tai-fill: 紅底空 sticker 內 mask-reveal 填入「備胎」+ scale 1.4→1 砸下感 overshoot + 紅邊 flash 2× + shadow burst 8px→20px + 全套 A+B+C+E+G
  - · cue: "備胎"（演講者念出當下視覺同步爆、節奏卡死、是 step 的 climax）
  - · wait: 3-4s 笑聲（ch6 最大笑點、不要急、停夠久再進 step 7）

- **climax**: beat 3 stamp 砸下瞬間（全 ch6 最重的一拍）
- **口播對應**: script.md L189

### step 7: 偷吃步 · 找漏洞作弊 (7s · 單 beat)

- **顯示內容**: 「偷吃步」紅 stamp 左上 + 「計分標準寫錯了 · AI 就會找漏洞作弊」hero 中央（cream 底、黑大字、紅底 + 黃底 雙色強調）
- **類型**: cinematic
- **進場**: 紅 stamp stamp-in → hero 文字 mask-reveal → 雙色強調 box stagger fade-in
- **口播對應**: script.md L195-199

---

## 7. reasoner — 重寫獎勵 + 13 招 + 戀愛 hook b · 老油條陷阱（8 step · ~138s）

> **敘事弧**: 重寫宣告 → 顛倒驗證 → 13 招階梯 → 舊 vs 新對比 → Action 擴增 → 兩千多萬次解出機率 0 → 老油條陷阱 ★★★ → 死結

**信息池**:
- 重寫宣告「整個計分獎勵系統重寫」+ 核心「用人類玩數獨的解題技巧、反過來驗證 AI 的每一步」（L201-205）
- 13 招技巧 naked single / hidden single / X-Wing / Swordfish / XY-Wing 等共 13 招（真實技巧名）（L209-211）
- 顛倒驗證 舊「填對給分」vs 新「AI 這一步、可以用人類技巧的哪一招解釋？越高階分越高」（L215-225）
- Action 擴增「多了劃掉這格不可能是這個數、消去類技巧才能展示」（L229-233）
- 慘烈結果「練了兩千多萬次——完整解出一道題的機率還是 0」（L237）
- 戀愛 hook b 出場 老油條陷阱題「和你媽一起掉進水裡你會先救誰」「該不該去運動」（L241-257）
- 死結「AI 一直卡在永遠拿不到整題解完那個大獎」+ 「就跟我不知道陷阱題正確解答一樣」（L265-269）
- 反思過渡「反向思考——先解出簡單陷阱題答案、之後從容面對」（L273-275）

### step 1: 重寫宣告 (11s · 單 beat)

- **顯示內容**: 「我只好整個計分獎勵系統重寫」hero（cream 底、黑大字、「重寫」黃底高亮）+ kicker「核心想法只有一個」
- **類型**: cinematic
- **進場**: hero mask-reveal + 「重寫」黃底 highlight slide-in
- **Motif 套用**: `motif/screen-shake` 輕量版（±2px、僅 1 次、80ms、「重寫」黃底高亮 slide-in 完成瞬間觸發、暗示「決心宣告」的重量感）
- **氣質**: 嚴肅、轉折
- **口播對應**: script.md L201-205

### step 2: 顛倒驗證宣告 (14s · 單 beat)

- **顯示內容**: 「用人類玩數獨的解題技巧 · 反過來驗證 AI 的每一步」超大 typography（關鍵詞「反過來」紅底 + 「驗證」黃底 highlight）
- **類型**: cinematic
- **進場**: 文字 mask-reveal 慢動(1200ms) → 關鍵詞 stagger highlight
- **climax**: 「反過來」「驗證」雙 highlight 同時亮
- **持續微動**: 主標題輕微 letter-spacing 微動
- **口播對應**: script.md L201-205

### step 3: 13 招大階梯 (19s · 單 beat)

```
                                       ╔═════════╗
                                       ║XYZ-Wing ║ ← 最大華麗
                                    ╔═════════╗  ║ (accent 紫)
                                    ║ X-Wing  ║──╝  6px 邊
                                 ╔═════════╗  ║   12px shadow
                                 ║Swordfish║──╝
                              ╔═════════╗  ║
                              ║ XY-Wing │──╝
                           ╔═════════╗  ║
                           ║HiddenTri│──╝
                        ╔═════════╗  ║
                        ║Hidden Pr│──╝
                     ╔═════════╗  ║
                     ║Naked Tri│──╝
                  ╔═════════╗  ║
                  ║Naked Pr │──╝
               ╔═════════╗  ║
               ║Pointing │──╝
            ╔═════════╗  ║
            ║Box-Line │──╝
         ╔═════════╗  ║
         ║HiddenSng│──╝
      ╔═════════╗  ║
      ║NakedSng │──╝ ← 最小樸素 (accent 黃)
      ╚═════════╝       4px 邊、6px shadow
   低階     →     →     →     高階
   stagger stamp-in 80ms 間隔
   hover → 該 sticker scale 1.15 + 其他 dim 0.5 + tooltip 中文簡介
```

- **顯示內容**: cream 底、13 張小 sticker 從低（naked single / hidden single）排到高（X-Wing / Swordfish / **XY-Wing** / **XYZ-Wing**）、階梯式由左下到右上排列、低階小且樸素、高階大且華麗（**X-Wing 跟 XYZ-Wing 最大、最華麗** · accent yellow / accent violet 底、6px 黑邊、微旋轉 -3° / 4°、12px shadow）+ 角標「13 招 · 真實技巧名」
- **類型**: progressive + interactive
- **Motif 首發**: `motif/13-stairs`（後續 ch9 s8 plasticity 三欄背景縮小裝飾復用）
- **進場**: 13 張 sticker 從低到高 stagger stamp-in（每張 80ms 間隔、1s 共完成）
- **互動**: hover 任一 sticker → 該 sticker scale 1.15 + 其他 dim opacity 0.5 + tooltip 浮出該招中文簡介
- **climax**: 13 張全 stamp 完的瞬間
- **viewBox 建議**: 800×500（一般 600×360 容不下 13 階梯）
- **口播對應**: script.md L209-211

### step 4: 舊 vs 新對比 (17s · 單 beat)

```
┌──────────────────────┐ ┃ ┌──────────────────────────┐
│   舊：填對給分        │ ┃ │   新：哪一招解釋？         │
│                      │ ┃ │                          │
│  ┌──────────┐        │ ┃ │  ┌──────────┐ +1         │
│  │NakedSng  │ ★ 亮起 │ ┃ │  │NakedSng  │ ★          │
│  └──────────┘        │ ┃ │  └──────────┘            │
│  ┌──────────┐        │ ┃ │  ┌──────────┐ +2         │
│  │HiddenSng │        │ ┃ │  │HiddenSng │ ★          │
│  └──────────┘        │ ┃ │  └──────────┘            │
│  ┌──────────┐        │ ┃ │  ┌──────────┐ +3 ← climax│
│  │ X-Wing   │        │ ┃ │  │ X-Wing   │ ★ + 浮動    │
│  └──────────┘        │ ┃ │  └──────────┘            │
│                      │ ┃ │  ┌──────────┐ +3         │
│   +1 浮起           │ ┃ │  │XYZ-Wing  │ ★ + 浮動    │
│                      │ ┃ │  └──────────┘            │
│                      │ ┃ │                          │
└──────────────────────┘ ┃ └──────────────────────────┘
         60%                          40%
        (左單一招亮)         (右多招陸續亮 + 分數浮動)
hover 任一側 → 該側放大 + 對立側 dim
```

- **顯示內容**: split-screen 60/40、左「舊：填對一格就給分」（只有一招亮 + 一個分數浮現）vs 右「新：可以用哪一招解釋？」（每張技巧都可以亮 + 高招分數更高、+1 +2 +3 浮動）
- **類型**: comparison + data-viz + interactive
- **進場**: split-screen wipe-in → 左側單一招亮起 + 數字 +1 → 右側多招陸續亮起 + 不同高度分數浮動 stagger
- **互動**: hover 左/右 → 該側放大 dim 對立側
- **climax**: 右側 X-Wing 亮 + +3 分浮起
- **口播對應**: script.md L215-225

### step 5: Action 擴增 — 填數字 + 劃掉候選 (13s · 單 beat)

- **顯示內容**: 「多了一倍可以做的事」hero + 中央 9×9 mini 盤面動畫，「填一個數字」(綠) + 「劃掉這格不可能是這個數」(紅斜線) 兩種動作示意動畫 + 副標「消去類技巧才能展示出來」
- **類型**: data-viz + interactive
- **Motif 復用**: `motif/sudoku-board`（ch 8 s2 9×9 盤面同款）
- **進場**: hero 上方 fade-in → mini 盤面 stamp-in → 填數字綠動畫 → 劃掉紅斜線動畫(stagger 600ms)
- **持續微動**: 盤面 loop 動畫示意兩動作交替
- **口播對應**: script.md L229-233

### step 6: 兩千多萬次 · 機率 0 (16s · 3 beat · punchline · placeholder)

- **顯示內容**: 底色閃紅 → 全屏紅底 → cream 大字「練了兩千多萬次」count-up 0→2,000,000+ + 副標「完整解出一道題的機率還是」（句末預留閃爍游標）→ beat 3 填入「0」（超大字 accent yellow 底、紅底 flash）
- **類型**: cinematic + data-viz
- **placeholder**: 「機率還是」後預留閃爍游標 `_`、「0」hold 到 beat 3
- **Motif**: `motif/red-stamp`（「0」用紅 stamp 形式砸下）
- **Climax 火力 輕量+**: A+B+C+E（「0」實體 stamp 性質配重火力；不放 G 留給 ch7 s7 climax 之後）→ outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` count-up: 底色閃紅 → 全屏紅底進入 → cream 大字「練了 **兩千多萬次**」count-up 0→2,000,000+(2s 動畫)
  - · cue: "結果呢——練了兩千多萬次..."
  - · wait: 0.5s 給數字落定
- **beat 2** `[click]` subtitle-placeholder: 下方副標「完整解出一道題的機率還是」mask-reveal + 句末預留**閃爍游標 `_`** 佔位（無「0」字）
  - · cue: "完整解出一道題的機率還是——"（拉長尾音「還是——」、停拍給觀眾猜）
  - · wait: 1-2s 留懸念（觀眾此時應該已經猜到「0」）
- **beat 3** `[click]` zero-drop: 游標 `_` 消失 → 「0」超大字從上 drop-in（overshoot bounce、scale 0→1.4→1、accent yellow 底）+ 紅底 flash 2× + shadow burst + A+B+C+E
  - · cue: "零"（演講者念出當下視覺同步爆）
  - · wait: 2-3s 嘆息/笑聲（觀眾與演講者的「失敗共感」）

- **climax**: beat 3 「0」砸下瞬間 + 紅底 flash
- **口播對應**: script.md L237

### step 7: 老油條陷阱題 ★★★ (26s · 6 beat · punchline · placeholder · ch7 最大笑點群)

```
┌──────────────────────────────────────────┐
│         [老油條女生陷阱題]      ← beat 1  │
│                                          │
│  ┌─────────────┐         ┌─────────────┐  │
│  │ 掉進水裡    │         │ 該不該運動？│  │
│  │ 先救誰？    │         │             │  │
│  │ (紅底-3°)   │ ← beat 2│ (紫底+4°)   │← beat 3
│  └─────────────┘         └─────────────┘  │
│                                          │
│   說要 → [❌嫌那個女生胖]     ← beat 4    │
│        + A+E+G                           │
│                                          │
│   說不用 → [❌你不關心健康]   ← beat 5    │
│         + A+E+G                          │
│                                          │
│      (beat 6 auto: 雙 ❌ 同步 flash       │
│       + B × 2 雙 halftone-burst)          │
└──────────────────────────────────────────┘
hover 任一 sticker → 該 sticker 放大 + 對應 ❌ flash
```

- **顯示內容**: 上方 hero「老油條女生陷阱題」+ 左 sticker「和你媽一起掉進水裡 · 你會先救誰？」（紅底 cream 字、微旋轉 -3°）+ 右 sticker「你覺得我該不該去運動？」（紫底 cream 字、微旋轉 4°）+ 下方兩答案箭頭「說要 → ???」「說不用 → ???」placeholder → beat 4/5 各填「❌ 嫌那個女生胖」「❌ 你不關心健康」 → beat 6 雙 ❌ 同步 flash
- **類型**: interactive + comparison
- **Motif 首發**: `motif/girl-veteran`（後續 ch9 s6 戀愛 b 4 題復用同款 sticker 樣式）+ `motif/yellow-highlight`
- **placeholder**: 兩答案箭頭 ❌ 文字 hold（先「說要 → ???」「說不用 → ???」、beat 4/5 才填）
- **Climax 火力 ★★★ 分 beat 套**: beat 4/5 各 A+E+G、beat 6 雙 B（halftone-burst × 2 從兩 ❌ 同時放）→ outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` hero: 上方 hero「老油條女生陷阱題」mask-reveal + 黃底高亮（`motif/yellow-highlight` 復用）
  - · cue: "這個感覺就是、你剛開始學習如何跟女生互動..."
  - · wait: 0.5s
- **beat 2** `[click]` trap-1: 左 sticker「和你媽一起掉進水裡 · 你會先救誰？」從左 swing-in（紅底 cream 字、微旋轉 -3°、overshoot）
  - · cue: "但是那些女生都是老油條、他們都會問一些奇奇怪怪的問題。例如——和你媽一起掉進水裡你會先救誰？"
  - · wait: 2s 觀眾笑（這題本身就是 trigger）
- **beat 3** `[click]` trap-2-question: 右 sticker「你覺得我該不該去運動？」從右 swing-in（紫底 cream 字、微旋轉 4°、overshoot）+ **下方兩答案箭頭「???」placeholder 同步出現**
  - · cue: "每道都是陷阱題。舉個例子，『你覺得我該不該去運動？』這道題——"
  - · wait: 1s 給觀眾自己心裡想答案
- **beat 4** `[click]` answer-a-fill: 「說要」箭頭 placeholder「???」mask-reveal 填入「❌ 嫌那個女生胖」+ ❌ 紅 flash + A+E+G
  - · cue: "你回答要去運動——那就是你嫌那個女生胖"
  - · wait: 2s 笑點
- **beat 5** `[click]` answer-b-fill: 「說不用」箭頭 placeholder「???」mask-reveal 填入「❌ 你不關心健康」+ ❌ 紅 flash + A+E+G
  - · cue: "你回答不用去運動——那就是你不關心那個女生的身體健康"
  - · wait: 2s 笑點
- **beat 6** `[auto, 400ms]` both-flash: 兩 ❌ 同步雙 flash 強調「兩面不討好」+ 雙 halftone-burst（B×2 從兩 ❌ 同時放）+ 兩 sticker hover 互動啟用
  - · 氣質: 滑稽、共鳴、給觀眾消化雙 ❌ 反差

- **互動**: 步內 hover 任一 sticker → 該 sticker 放大 + 對應 ❌ 紅 flash（純視覺、不影響推進）
- **climax**: beat 6 雙 ❌ 同步 flash 瞬間
- **口播對應**: script.md L241-257

### step 8: 死結 (20s · 單 beat)

- **顯示內容**: cinematic 黑底 → cream 大字「AI 永遠拿不到『整題解完』那個大獎」+ 副標「就跟我不知道陷阱題的正確解答一樣」+ 角落「反向思考⋯」鋪墊 footer
- **類型**: cinematic
- **進場**: 底色 cream → 黑 fade(800ms) → 主標 mask-reveal 慢動(1500ms) → 副標 fade-up → footer 從下 slide-in
- **氣質**: 沉重、留白、為下章鋪墊
- **轉場**: 「反向思考⋯」footer 提示下章方向
- **口播對應**: script.md L265-269

---

## 8. apprentice — 反向課程 + visualizer（6 step · ~66s + visualizer 30~60s）

> **敘事弧**: 反向思考過渡 → 3 格空盤面 → 反向課程動畫 3→10 → +20 → +50 翻牌 → 光講不夠看 → visualizer 大按鈕

**信息池**:
- 反向思考「我把題目反過來給他——一開始只給 3 格空、90% 都填好了、他一定解得出來」（L273-279）
- 反向課程「能穩定解、再加一格空、再加一格⋯⋯讓難度跟著他的能力走」（L281-285）
- 破關獎勵翻牌「破關獎勵調更大——從 +20 拉到 +50」+ 「讓完成整題的訊號更明確」（L287-291）
- 突破「從 3 個空格慢慢加到 10 個——他終於開始解出整題」（L293）
- visualizer 大按鈕 + 桌面 pygame URL scheme 啟動

### step 1: 反向思考過渡 (10s · 單 beat)

- **顯示內容**: 黑底慢慢回 cream + 「反向思考 · 先解簡單的陷阱題答案」hero + 副標「之後從容面對老油條」+ 下方 footer「AI 也是、我把題目反過來給他 →」
- **類型**: cinematic
- **進場**: 底色 fade（純 CSS `background-color` 1.2s `cubic-bezier(0.4, 0.0, 0.2, 1)` 自然減速、同步 halftone dots opacity 0→1 漸入）→ hero mask-reveal + 「反向思考」紅底高亮 → footer slide-up
- **氣質**: 開朗、解題感
- **口播對應**: script.md L273-275

### step 2: 3 格空盤面 (12s · 單 beat)

- **顯示內容**: 中央 9×9 數獨盤面（黑邊、cream 格子、Space Grotesk 700 數字、90% 已填）+ 副標「只有 3 格空」+「他一定解得出來」kicker
- **類型**: data-viz + cinematic
- **Motif 首發**: `motif/sudoku-board`（後續 ch8 s3 + ch7 s5 mini 盤面復用）
- **進場**: 盤面從 scale 0.85 stamp-in → 「只有 3 格空」mask-reveal → 3 個空格 highlight 紅色 outline pulse
- **climax**: 3 空格 pulse 同步
- **口播對應**: script.md L277-279

### step 3: 反向課程動畫 3→10 (12s · 單 beat)

```
盤面: 9×9   每 ~500ms 擦掉一格、scale 0.95→1
時間軸:
t=0    t=500ms  t=1000ms  ...  t=3500ms
┌─┐    ┌─┐      ┌─┐             ┌─┐
│3│ → │4│  →   │5│  →  ...  →  │10│
└─┘    └─┘      └─┘             └─┘
3空    4空      5空              10空

計數器同步 count-up: 「空格: 3 → 10」
副標: [讓難度跟著他的能力走]
完成後盤面輕微 shake → 暗示「難度持續上升」
```

- **顯示內容**: 盤面從 3→4→5→6→7→8→9→10 空（連續一格一格自動揭示、每次格子被「擦掉」變空、~500ms 一格、scale 0.95→1 transition、共約 3.5s）+ 副標「讓難度跟著他的能力走」+ 計數器「空格: 3→10」count-up
- **類型**: data-viz + progressive
- **進場**: 自動進入動畫(~5s 完成 3→10)、計數器同步 count-up
- **持續微動**: 完成後盤面輕微 shake 暗示「難度持續上升」
- **口播對應**: script.md L281-285

### step 4: +20 → +50 翻牌 (10s · 單 beat)

- **顯示內容**: cinematic 全屏 → cream 底 + 中央「+20 → +50」大字翻牌動畫(3D flip rotateY 600ms、shadow 翻面換邊)、20 紅色、50 黃色 + 副標「破關獎勵調更大」+ 下方「誘惑超過刷部分分數的賤招」
- **類型**: data-viz + cinematic
- **Motif 首發**: `motif/flip-20-to-50`（後續 ch9 s9 plasticity 機制「reward 加加減減」背景 loop 復用）
- **進場**: 「+20」stamp-in → hold 500ms → flip 3D → 「+50」snap(overshoot、shadow 加深) → 副標 fade-up
- **climax**: flip 完成瞬間
- **口播對應**: script.md L287-291

### step 5: 光講不夠看 (9s · 單 beat)

- **顯示內容**: 「光講不夠看」hero kicker + 「給大家看一下 AI 即時解數獨的題目」副標 + 中央向下大箭頭（指向下一 step 的 visualizer 大按鈕）
- **類型**: cinematic
- **進場**: 「光講不夠看」mask-reveal → 「給大家看」fade-up → 向下大箭頭 stroke-draw + bounce
- **持續微動**: 箭頭 bounce 上下
- **口播對應**: script.md L297-299

### step 6: visualizer 大按鈕 (10s + visualizer 30~60s · 單 beat)

- **顯示內容**: 獨佔整屏 cream 底 + 「點我看 AI 即時解數獨 →」超大按鈕（粗黑邊 6px、強 hard shadow 16px、accent red 文字、微旋轉 -2°、hover 時 scale 1.05 + shadow 變深）
- **按鈕行為**: `href="sudoku-demo:run"` — 點擊直接觸發 Windows custom URL scheme、自動啟動桌面 pygame 視窗、不需要演講者手動 Alt+Tab
- **類型**: cinematic + interactive
- **進場**: 按鈕從 scale 0.8 stamp-in(overshoot)
- **互動**: hover 按鈕 → scale 1.05 + shadow 16px→20px + 紅底深一階（mechanical feedback、模仿物理 button）
- **啟動機制簡述**: HTML `<a href="sudoku-demo:run">` → 瀏覽器 custom protocol → HKCU registry → `demo/visualizer-launch/launcher.bat` → `python -m apprentice.demo.visualize` → pygame 視窗 0.5-1s 內 pop-up 並搶最上層
- **詳細部署**: [demo/visualizer-launch/README.md](visualizer-launch/README.md)
- **氣質**: 全片最強 cinematic moment、留給演講者切換實機
- **口播對應**: script.md L299

---

## 9. callback — AI 也在訓練我（13 step · ~204s）

> **敘事弧**: tensorboard + 磨合期 → 核心金句「AI 也在訓練我」→ RL 對等 → 飛機鳥模仿 → 戀愛 a callback → 戀愛 b 4 考題 → plasticity 引出 → plasticity 三欄 → plasticity 機制 → MBTI + 業務工作 → 警語「人生第一次的外向 · 換來一輩子的內向」★★ → 職場祝福 → 電費小偷 final ★★★

> **Motif callback 章**: 大量引用 [outline-visual.md §7 Motif Library](outline-visual.md) 母題、喚起觀眾前段視覺記憶 = callback 笑點力道 +30%

**信息池**:
- 過渡「AI 還在訓練中、但有在進步、我跟對方還在磨合期、最後我想跟大家講一件事」（L303-307）
- 核心金句「這兩個月、我不只在訓練 AI、AI 也在訓練我」（L309）
- RL 對等「試錯加獎懲——腦科學裡這叫 reinforcement learning、AI 訓練也叫 RL、其實是同一件事」（L313-317）
- 飛機鳥「AI 在模仿人類——就像當初的飛機、人類模仿鳥類才造出來」（L319）
- 戀愛 a callback「對方回訊息加分、已讀不回扣分、大腦根據 reward 重塑要不要當舔狗、跟 AI 訓練一模一樣」（L323-329）
- 戀愛 b callback 4 魔王考題（前女友比 / 心中女神 / 喜歡我哪裡 / 今天哪裡不一樣）（L333-343）
- plasticity 引出「大腦可塑性 plasticity」（L347-349）
- plasticity 三項對等「AI 沒天生會解數獨、出生不會講話、不是天生會跟人相處——一樣」（L351）
- plasticity 機制「每改一次 reward function、每談一場戀愛、每學一個新東西——每次都把我們重新塑造一次」（L353-355）
- MBTI「極度的 I 人、100% 偏向 I、明明我很 E」（L359-361）
- 業務工作變 E「逼自己跳脫舒適圈、業務工作、慢慢變得比較 E」（L363）
- 不被擊敗警語「從挫敗中學習、不要停滯不前、人生第一次的外向換來一輩子的內向、繼續嘗試不是每個女生都那麼老油條」（L367-371）
- 職場祝福「不被挫敗給擊敗」（L373）
- 電費小偷結尾笑話「想必大家未來都是薪水小偷。但我不一樣、我是電費小偷、這兩個月一直用班上的電腦瘋狂訓練我的 AI」（L375）

### step 1: tensorboard 截圖 + 磨合期 (12s · 單 beat)

- **顯示內容**: cream 底 + 上方字幕「AI 還在訓練中⋯⋯我跟對方還在磨合期」+ 左右雙圖：**真實 tensorboard 截圖**（左 success_rate 曲線、右 curriculum target_empty 圖；6px 黑邊 + 12px shadow 框）+ 下方副標「但你可以看到 · AI 是有在進步的」+ 中央「最後我想跟大家講一件事」hero（黑大字、stamp-in）
- **類型**: data-viz + cinematic
- **進場**: 字幕 fade-down → 左圖從左 slide-in → 右圖從右 slide-in(stagger 200ms) → 副標 fade-up → hero mask-reveal 慢動(900ms)
- **氣質**: 過渡、收斂、為金句鋪墊；真實素材給 callback「AI 在進步」具象視覺證據
- **資料來源**: ⚠️ tensorboard 截圖待匯出至 `demo/presentation/public/images/tensorboard/`
- **口播對應**: script.md L303-307

### step 2: 核心金句 — AI 也在訓練我 (14s · 單 beat)

- **顯示內容**: 「這兩個月 · 我不只在訓練 AI / AI · 也在訓練我」（cream 底、accent red 巨字、6px 黑邊框、letter-spacing 動畫、`hero-mega` 字級）
- **類型**: cinematic
- **進場**: 文字 mask-reveal 慢動 1200ms + letter-spacing 0.05em→0em 收緊
- **climax**: 「AI 也在訓練我」最後三字砸下（stamp + 紅底 flash）
- **氣質**: 全片金句、最重的 hero
- **口播對應**: script.md L309

### step 3: RL 對等 (12s · 單 beat)

- **顯示內容**: split-screen 左「腦科學 RL」（黑底 cream 字、大腦 sticker）/ 右「AI 訓練 RL」（cream 底黑字、神經網路 sticker）+ 中央「=」大字（黃底圓形 sticker、stamp-in）+ 下方「其實是同一件事」hero
- **類型**: comparison + cinematic
- **進場**: 左右 split wipe-in → 中央「=」stamp-in(overshoot) → 下方 hero mask-reveal
- **climax**: 「=」砸下瞬間
- **口播對應**: script.md L313-317

### step 4: 飛機 + 鳥模仿 (10s · 單 beat)

- **顯示內容**: cream 底 + 上方「AI 在模仿人類」hero + 中央飛機（純 SVG 線稿、黑線）+ 鳥（純 SVG 線稿、黃色填充）並置 + 中央「←」箭頭暗示「模仿」+ 副標「就像飛機 · 是人類模仿鳥類才造出來」
- **類型**: cinematic + depth
- **進場**: hero fade-in → 飛機從左 slide-in → 鳥從右 slide-in → 「←」箭頭 stroke-draw
- **持續微動**: 鳥輕微振翅、飛機輕微 yaw
- **口播對應**: script.md L319

### step 5: 戀愛 a callback — 跟 AI 一模一樣 (18s · 4 beat · punchline · placeholder)

```
┌──────────────────────────────────────┐
│   背景: motif/girl-new (粉紅、灰階     │
│         opacity 0.3、最底層)          │
│         ← beat 1 退入                │
│                                      │
│        ┌───────────┐                 │
│        │  大腦      │                 │
│        │ (黑線稿 +  │ ← beat 1 stamp-in
│        │  紫色 reward│                │
│        │  漂浮)     │                 │
│        └───────────┘                 │
│                                      │
│ 回訊息: + + +    │    已讀不回: - - - │
│  (綠↑浮起)       │     (紅↓沉)        │
│ ← beat 2 spawn   │   ← beat 3 spawn   │
│                                      │
│   ╔══════════════════════════════╗   │
│   ║   跟 AI 訓練 一模一樣          ║   │ ← beat 4
│   ║   (紅底 hero placeholder      ║   │ punchline
│   ║    + flash 2× + A+C climax)   ║   │
│   ╚══════════════════════════════╝   │
└──────────────────────────────────────┘
```

- **顯示內容**: 背景退入 `motif/girl-new` 灰階（ch6 粉紅新女生 sticker、opacity 0.3、最底層）+ 中央大腦 sticker（黑線稿 + 內部紫色 reward 漂浮）+ 左欄「回訊息」綠色 +/+/+ 連續 spawn → 右欄「已讀不回」紅色 -/-/- 連續 spawn → 下方紅底 hero 預留位 → beat 4 填入「跟 AI 訓練一模一樣」
- **類型**: comparison + data-viz + cinematic
- **Motif 復用**: `motif/girl-new`（ch6 s3 粉紅新女生 sticker 退背景、灰階、暗示「就是那個女生」）
- **placeholder**: 「跟 AI 訓練一模一樣」紅底 hero 預留位、文字 hold 到 beat 4
- **Climax 火力 輕量**: A+C → outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` bg-callback: 背景退入 `motif/girl-new`（ch6 粉紅新女生 sticker、灰階、opacity 0.3、最底層）+ 中央大腦 sticker（黑線稿 + 內部紫色 reward 漂浮）stamp-in
  - · cue: "追一個人的時候——"
- **beat 2** `[click]` left-positive: 左欄「回訊息」綠色 +/+/+ 連續 spawn 從下浮起（持續動畫）
  - · cue: "對方回訊息你就被加分"
  - · wait: 1s 給觀眾建立左右對照預期
- **beat 3** `[click]` right-negative: 右欄「已讀不回」紅色 -/-/- 連續 spawn 從上沉（持續動畫）
  - · cue: "已讀不回你就被扣分"
  - · wait: 1.5s 給觀眾感受加分扣分的拉扯
- **beat 4** `[click]` punchline-hero: 下方紅底全屏 hero 預留位 mask-reveal 填入「跟 AI 訓練一模一樣」+ 紅底 flash 2× + shadow burst + 中央大腦的紫色 reward 與兩側 +/+/- 漂浮同步加速 + A+C
  - · cue: "你的大腦根據這些 reward 反覆重塑要不要繼續當舔狗的判斷——跟 AI 訓練"（最後三字「一模一樣」前點下、字一邊出演講者一邊念）
  - · wait: 2s 觀眾領悟、回想 ch6/7 戀愛 hook

- **持續微動**: +/+/+ 與 -/-/- 連續浮動
- **climax**: beat 4 紅底 hero 砸下瞬間
- **口播對應**: script.md L323-329

### step 6: 戀愛 b callback — 4 個魔王考題 (18s · 單 beat)

```
┌──────────────────────────────────────────┐
│      [以為穩了 · 結果魔王關卡]             │
│                                          │
│   ┌──────────────┐  ┌──────────────┐      │
│   │ 前女友比較好? │  │ 心中女神是誰?│      │
│   │   (黃底)     │  │   (紫底)     │      │
│   │  rotate +2°  │  │  rotate -3°  │      │
│   └──────────────┘  └──────────────┘      │
│                                          │
│   ┌──────────────┐  ┌──────────────┐      │
│   │ 你喜歡我哪裡? │  │ 哪裡不一樣?  │      │
│   │ (紅底 cream字)│  │(cream+描邊)  │      │
│   │  rotate -1°  │  │  rotate +3°  │      │
│   └──────────────┘  └──────────────┘      │
│                                          │
│   stagger stamp-in (each 150ms 間隔)      │
│   hover → 該 sticker scale 1.1 + shadow 加深│
│        + 「⋯⋯（沒有正解）」副標浮現         │
└──────────────────────────────────────────┘
   motif/girl-veteran 繼承 ch7 s7 樣式 → callback +30%
```

- **顯示內容**: cream 底 + 上方「以為穩了 · 結果魔王關卡」hero + 中央 **4 個考題 sticker grid 並排**（2×2、每張不同底色 + 微旋轉）:
  - 「前女友跟我比 · 誰比較好？」（黃底）
  - 「你心中的女神是誰？」（紫底）
  - 「你喜歡我哪裡？」（紅底 cream 字）
  - 「猜猜看 · 今天我哪裡不一樣？」（cream 底 + 描邊）
- **類型**: interactive + cinematic
- **Motif 復用**: `motif/girl-veteran`（ch7 s7 老油條陷阱題 sticker 樣式繼承、4 個考題用同款「斜貼、不同底色、微旋轉」視覺語言、觀眾自動勾起 ch7 笑點記憶）
- **進場**: hero fade → 4 sticker 從 grid 中心 stagger stamp-in(each 150ms 間隔)
- **互動**: hover 任一 sticker → scale 1.1 + shadow 加深 + 其他 dim 0.5 + 該題下方浮現「⋯⋯（沒有正解）」副標
- **氣質**: 滑稽、共鳴
- **口播對應**: script.md L333-343

### step 7: plasticity 引出 (8s · 單 beat)

- **顯示內容**: cream 全屏 → 上方「最後再跟大家分享」kicker → 中央「大腦可塑性 · plasticity」hero（中英並列、英文 letter-spacing 撐開）
- **類型**: cinematic
- **進場**: kicker fade-down → hero mask-reveal 慢動(1000ms) + 「plasticity」英文 letter-spacing 0.3em → 0.05em 收緊
- **氣質**: 學術感、慢拍
- **口播對應**: script.md L347-349

### step 8: plasticity 三欄對位 (12s · 單 beat)

- **顯示內容**: cream 底、三欄並列：
  - 欄 1: 「**AI** 沒天生會 · 解數獨」（紅底 sticker）
  - 欄 2: 「**你** 出生不會 · 講話」（黃底 sticker）
  - 欄 3: 「**你** 不是天生會 · 跟人相處」（紫底 sticker）
  - 中央巨字「一樣」（cream 底、黑超大字、stamp-in）
- **類型**: comparison + cinematic
- **Motif 復用**: `motif/13-stairs`（背景以極淡 opacity 0.08、灰階的 ch7 13 招階梯縮小化平鋪、暗示「就像那 13 招 AI 也是學出來的」、視覺潛意識勾起 ch7 學習進階感、不搶前景文字焦點）
- **進場**: 三欄 stagger fade-up(each 200ms) → 中央「一樣」從 scale 0 砸下(overshoot + 紅邊 flash)
- **climax**: 「一樣」砸下瞬間
- **口播對應**: script.md L351

### step 9: plasticity 機制 — 每次都把我們重新塑造一次 (12s · 單 beat)

- **顯示內容**: 中央「每次都把我們重新塑造一次」hero + 上方副標「每改一次 reward function、每談一場戀愛、每學一個新東西」（三項 stagger reveal）
- **類型**: cinematic + progressive
- **Motif 復用**: `motif/flip-20-to-50`（背景以極淡 opacity 0.06、灰階的「+20→+50」3D flip 翻牌 loop 平鋪、暗示「reward 加加減減」循環）+ `motif/yellow-highlight`（「重新塑造」黃底）
- **進場**: 副標三項 stagger fade-up(each 240ms) → 主 hero mask-reveal 慢動 + 「重新塑造」黃底高亮
- **氣質**: 哲思、慢動
- **口播對應**: script.md L353-355

### step 10: MBTI 自我故事 + 業務工作變 E (22s · 複合 step · 兩拍)

```
┌────────────── 第一拍 (0-9s) ──────────────┐
│  [我真的是一個 極度的 I 人] kicker         │
│                                          │
│         ╭───────╮                        │
│         │ 100%  │      ┌──────────┐       │
│         │  I    │ ───→ │ 極度 I 人 │       │
│         │       │      │ (紫底 sticker)│   │
│         ╰───────╯      └──────────┘       │
│         圓餅 0→100%                       │
│         填滿 1.5s         [明明我很 E]    │
│                          (黃底高亮)        │
└────────────────────────────────────────────┘
              ↓ auto hold 1.5s 後觸發第二拍 ↓
┌────────────── 第二拍 (9-22s) ─────────────┐
│  ╭─────╮   ┌──────────────────────────┐  │
│  │ I 30%│  │   [業務工作] (黃底 sticker)│ │
│  │ E 60%│  │                          │  │
│  ╰─────╯   │   ━━━━━━━━━●━━━━━━━━━━━━│  │
│ 圓餅縮至  │   I 0%    ↑60%        E   │  │
│  30% 寬   │     (indicator 4s 移動)   │  │
│           │                          │  │
│           │  [跟陌生人講話 慢慢變比較 E]│  │
│           └──────────────────────────┘  │
└────────────────────────────────────────────┘
```

- **顯示內容**: cream 底 + 上方「我真的是一個 **極度的 I 人**」kicker
  - **第一拍 (0-9s)**: 中央 **MBTI 圓餅視覺**（圓餅完整黑邊、I 紫色填滿 100%、E 0%、cream 中心）+ 右側「極度 I 人」標籤 sticker（紫底、6px 黑邊、微旋轉 -3°、stamp-in）+ 副標「明明我很 E」（黃底高亮）
  - **第二拍 (9-22s)**: 圓餅 sticker 縮到左側 30% 寬、右側 70% 拉出「業務工作」標籤 sticker（黃底、微旋轉 2°、stamp-in）+ **I → E 漸變條**（水平條、從紫色 I → 紅色 E、indicator 動畫從 I 0% 移到 60%、4s）+ 副標「天天逼自己跟陌生人講話 · 才慢慢變得比較 E」
- **類型**: data-viz + progressive
- **進場**: kicker fade-down → 圓餅 0%→100% I 填滿動畫(1.5s) → 「極度 I 人」sticker 砸下(overshoot) → 副標 fade-up
- **第二拍觸發**: 步內第二拍由 step 內動畫自動觸發（hold 1.5s 後）、不需演講者額外點擊 → 圓餅縮側(600ms ease) → 業務 sticker stamp-in → 漸變條 fade-in → indicator 移動(4s) → 副標 stagger
- **climax**: 圓餅 100% I 填滿瞬間 + indicator 抵達 60% 瞬間
- **口播對應**: script.md L359-365

### step 11: 警語 — 人生第一次的外向 · 換來一輩子的內向 ★★ (18s · 4 beat · punchline · placeholder · 整片第二重一拍)

- **顯示內容**: 上方「從挫敗中學習就行了」kicker + 中央警語 sticker 空框（cream 底、6px 紅邊、微旋轉 -2°、超大、閃爍游標）+ 下方副標「但是不要停滯不前」→ beat 3 填上半「人生第一次的外向」→ beat 4 填下半「換來一輩子的內向」
- **類型**: cinematic
- **Motif 復用**: `motif/crash-line`（cream + 6px 紅邊 + flash、與 ch5/6 崩盤 motif 同源、放大成「警語」尺度）
- **placeholder**: 警語 sticker 空框預留、兩段 punchline 拆兩次 click 填入
- **Climax 火力 輕量+**: A+C+G（警語性質、聚焦合理、shadow burst 8px→20px 配 spotlight 暗化外圍）→ outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` kicker-and-frame: 上方「從挫敗中學習就行了」kicker fade-down + halftone dots 加密(400ms) + 中央警語 sticker 空框出現（cream 底、6px 紅邊、微旋轉 -2°、超大、閃爍游標 `_`）
  - · cue: "所以遇到不會回答的魔王陷阱題沒有關係、我們只要從挫敗中學習就行了..."
  - · wait: 1s 鋪正面語氣
- **beat 2** `[click]` subtitle: 下方副標「但是不要停滯不前」fade-up
  - · cue: "但是不要停滯不前——"（停拍、語氣轉折、觀眾預期反轉）
  - · wait: 1s
- **beat 3** `[click]` warn-line-a-fill: 警語空框內**上半行** mask-reveal 填入「人生第一次的外向」（accent red 大字）+ 紅邊 flash 1×
  - · cue: "跟一個女生聊天、結果——人生第一次的外向"
  - · wait: 1-1.5s 停拍、給觀眾預期下半反轉
- **beat 4** `[click]` warn-line-b-fill: 警語空框內**下半行** mask-reveal 填入「· 換來一輩子的內向」（accent red 大字）+ scale 1.3→1 snap 整 sticker overshoot + 紅邊 flash 2× + shadow burst 8px→20px + A+C+G
  - · cue: "換來一輩子的內向"（演講者念出當下視覺同步爆）
  - · wait: 3-4s 停拍（整片第二重的一拍、不要急、給觀眾完全消化反轉）

- **climax**: beat 4 警語全文落定 + shadow burst + 紅邊 flash（全 ch9 第二重 climax、僅次電費小偷 final）
- **口播對應**: script.md L367-369

### step 12: 職場祝福 — 不被挫敗給擊敗 (12s · 單 beat)

- **顯示內容**: cream 底回歸 + 上方「繼續嘗試跟其他女生聊天」kicker + 中央「祝大家未來在職場上 · 不被挫敗給擊敗」hero（黑大字、「不被挫敗給擊敗」紅底高亮、cream 字）+ 下方「不是每個女生都那麼老油條」副標
- **類型**: cinematic
- **進場**: kicker fade-down → hero mask-reveal + 紅底高亮 slide-in → 副標 fade-up
- **氣質**: 正能量、收斂、為最後笑話鋪墊
- **口播對應**: script.md L371-373

### step 13: 電費小偷 final ★★★ (28s · 4 beat · punchline · placeholder · 全片最後笑點 · 全片最強 climax · 🚩 wait 重)

```
┌──────────────────────────────────────────┐
│     [最後再補個笑話]              ← beat 1│
│                                          │
│ ┌──────────────────────────────────┐     │
│ │ 想必大家未來出職場後都是·薪水小偷 │ ← beat 2
│ │ (黑底 cream 字、+2°)              │     │
│ └──────────────────────────────────┘     │
│                                          │
│ ┌──────────────┐                         │
│ │ 我不一樣 → ? │ ← beat 2 placeholder    │
│ │ (cream底、紅?│                         │
│ │  6px黑邊、-3°)│                        │
│ └──────────────┘                         │
│       ↓ beat 3 morph                     │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓        │
│ ┃ 但我不一樣 · 我是 · 電費小偷    ┃ ← FINAL│
│ ┃ (accent red、cream大字、超大)   ┃        │
│ ┃ + motif/boom-double-ring 圍邊  ┃ ← climax│
│ ┃ + 整屏 micro-shake + 全套 A+B+C+E+G  │   │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛        │
│                                          │
│  [我這兩個月一直用班上的電腦       ← beat 4│
│   瘋狂訓練我的 AI]                  type-in │
│                                          │
│                              — END —     │
└──────────────────────────────────────────┘
   首尾呼應 ch1 s8 BOOM 雙圈 → 圓滿收尾
   ⚠ 節奏紅旗: beat 3 wait 5-7s + beat 4 wait 5s+ 合計 ~13-15s
   彩排時請特別注意 cue 不要超時
```

- **顯示內容**: 上方 kicker「最後再補個笑話」+ 中央上「想必大家未來出職場後都是 · 薪水小偷」對位 sticker（黑底 cream 字、微旋轉 2°）+ 中央下「我不一樣 → ?」空泡泡 placeholder（cream 底、6px 黑邊、紅色 ? 字、微旋轉 -3°）→ beat 3 morph 成「但我不一樣 · 我是 電費小偷」FINAL sticker → beat 4 底部 footer「我這兩個月 · 一直用班上的電腦 · 瘋狂訓練我的 AI」progressive type-in + 右下「— END —」
- **類型**: cinematic
- **Motif 復用**: `motif/boom-double-ring` 縮小化（「電費小偷」FINAL sticker 圍邊、首尾呼應 ch1 s8）+ `motif/red-stamp` + `motif/yellow-highlight`
- **placeholder**: 「電費小偷」位置先放「我不一樣 → ?」空泡泡、文字 hold 到 beat 3
- **Climax 火力 ★★★ 全套+ 加碼**: A+B+C+E+G + 縮小化雙圈圍邊 + 整屏 cream 底 micro-shake 150ms — **全片視覺火力最強的一拍**、首尾呼應 ch1 s8 BOOM → outline-visual.md §8

**Beat 結構**:
- **beat 1** `[click]` kicker: 上方 kicker「最後再補個笑話」fade-in
  - · cue: "最後再補個笑話——"
  - · wait: 1s
- **beat 2** `[click]` salary-thief: 中央上「想必大家未來出職場後都是 · 薪水小偷」對位 sticker stamp-in（黑底 cream 字、微旋轉 2°、scale 0.85→1 overshoot）+ 中央下「我不一樣 → ?」空泡泡同時出現（cream 底、6px 黑邊、紅色 ? 字、微旋轉 -3°）
  - · cue: "想必大家未來出職場後都是薪水小偷..."
  - · wait: 1.5-2s 給觀眾笑「薪水小偷」+ 看到空泡泡開始猜「他要說什麼」
- **beat 3** `[click]` power-thief-fill: 「我不一樣 → ?」空泡泡 → 紅 ? 消失 → 整個泡泡 morph 成 FINAL sticker（accent red 底、cream 大字、6px 黑邊、16px hard shadow、微旋轉 -3°、超大）+ mask-reveal 填入「但我不一樣 · 我是 電費小偷」+ scale 1.5→1 snap overshoot bounce + 紅邊 flash 3× + shadow burst 8px→20px + `motif/boom-double-ring` 縮小化雙圈圍繞 stamp（黃外圈 + 紅內圈、stagger 80ms / 120ms）+ 整屏 cream 底 micro-shake 150ms + 全套 A+B+C+E+G
  - · cue: "但我不一樣、我是——電費小偷"（演講者念出「電費小偷」當下視覺同步爆、整片節奏 climax）
  - · wait: 5-7s 觀眾大笑（全片最後笑點、絕對不要急著進 beat 4）
- **beat 4** `[click]` footer-and-end: 底部 footer「我這兩個月 · 一直用班上的電腦 · 瘋狂訓練我的 AI」progressive type-in（字逐字打字效果 1.5s）+ 整屏右下角浮現「— END —」minimal footer（純黑字、cream 底、無 chrome）
  - · cue: "我這兩個月一直用班上的電腦瘋狂訓練我的 AI"（演講者跟著字打的節奏念）
  - · wait: 5s+ 讓 END 字留在畫面、給掌聲時間、可永久 hold（不再有下一 step）

- **climax**: beat 3 電費小偷 stamp 砸下瞬間 + shadow burst + boom 雙圈 + 整屏 shake（全片最強 reveal、首尾呼應 ch1 s8 BOOM）
- **氣質**: punchline 爆破、收尾
- **口播對應**: script.md L375

---

## §6 反向索引: script.md L → outline step

| script.md L | outline step | 摘要 |
| --- | --- | --- |
| L1 | ch1 s1 | 心虛開場、報告太不正經 |
| L5 | ch1 s2 | 心理學系畢業 + 敬請期待伏筆 |
| L9 | ch1 s3 | 期中主題：訓練 AI 解數獨 |
| L13-L17 | ch1 s4 | 捷運上正大光明看正妹發呆 |
| L19 | ch1 s5 | Code Bullet flappy bird 靈感 |
| L21 | ch1 s6 | 繼續發呆（喜劇延續拍） |
| L25 | ch1 s7 | 當兵沒手機解數獨 |
| L29 | ch1 s8 b1-2 | BOOM · 兩個想法撞在一起 |
| L35-L37 | ch1 s8 b3 | 靈感就是這麼莫名其妙地蹦出來 |
| L41-L45 | ch2 lead-in | 機器學習的世界長什麼樣 |
| L49-L55 | ch2 s1 | supervised：看著答案抄筆記 |
| L57-L61 | ch2 s2 | unsupervised：折衣服分顏色 |
| L63-L67 | ch2 s3 | RL：試錯加獎懲、AlphaGo |
| L71 | ch2 s4 | cliffhanger：ChatGPT/Claude 是哪一招？ |
| L75-L77 | ch3 s1 | LLM = supervised + RLHF |
| L81-L89 | ch3 s2 | LLM 模仿 vs 我的 AI 自己摸出規則 |
| L93-L95 | ch3 s3 | OK 純 RL、第一步找資料 |
| L99-L107 | ch4 s1+s2 | Kaggle / supervised 路線拒絕 |
| L111-L121 | ch4 s3 | 霸榜目標 + websudoku 受害者 |
| L125-L133 | ch4 s4 | 20 題被封 IP + proxy 池 |
| L141-L147 | ch5 s1 | 我那時候很天真 / 丟一句 prompt / 我錯了 |
| L151 | ch5 s2 | 800 多行的單一檔案 |
| L153 | ch5 s3 | 每改一個地方都東倒西歪 / debug 成本爆炸 |
| L157-L163 | ch5 s4 | 第一件學到 / 架構自己先想清楚 / 套皮仔 |
| L167-L173 | ch6 s1 + s2 | 社群工具箱 / 套皮仔 / 我又錯了 |
| L177 | ch6 s2 | 填對一格就給分數 |
| L181-L185 | ch6 s3 | 新女生加分（戀愛 hook a 出場） |
| L187 | ch6 s4+s5 | 卡平段 / 不思進取 |
| L189 | ch6 s6 ★★★ | 備胎（戀愛 hook a 收） |
| L195-L199 | ch6 s7 | 偷吃步 / 計分標準寫錯 / 找漏洞作弊 |
| L201-L205 | ch7 s1+s2 | 整個計分系統重寫 / 用人類技巧反過來驗證 |
| L209-L211 | ch7 s3 | 13 招技巧名 |
| L215-L225 | ch7 s4 | 舊（填對給分）vs 新（用哪一招解釋）對比 |
| L229-L233 | ch7 s5 | Action 擴增：填數字 + 劃掉候選 |
| L237 | ch7 s6 | 兩千多萬次 · 完整解出機率 0 |
| L241-L257 | ch7 s7 ★★★ | 老油條陷阱題（戀愛 hook b 展開） |
| L265-L269 | ch7 s8 | 死結：永遠拿不到「整題解完」大獎 |
| L273-L275 | ch8 s1 | 反向思考 |
| L277-L279 | ch8 s2 | 一開始只給 3 格空 |
| L281-L285 | ch8 s3 | 再加一格、再加一格⋯⋯3→4→5→6→7→8→9→10 |
| L287-L291 | ch8 s4 | 破關獎勵 +20 → +50 |
| L293 | ch8 lead-out | 3 → 10、他終於開始解出整題 |
| L297-L299 | ch8 s5+s6 | 光講不夠看 / visualizer 按鈕 |
| L303-L307 | ch9 s1 | AI 還在訓練中 / 磨合期 / tensorboard 截圖 |
| L309 | ch9 s2 | 核心金句：AI 也在訓練我 |
| L313-L317 | ch9 s3 | 腦科學 RL = AI RL |
| L319 | ch9 s4 | 飛機 / 鳥：AI 在模仿人類 |
| L323-L329 | ch9 s5 | 戀愛 a callback：回訊息加分 / 已讀扣分 |
| L333-L343 | ch9 s6 | 戀愛 b callback：4 個魔王考題 |
| L347-L349 | ch9 s7 | 大腦可塑性 plasticity 引出 |
| L351 | ch9 s8 | plasticity 三欄對等 |
| L353-L355 | ch9 s9 | plasticity 機制：每次都把我們重新塑造一次 |
| L359-L361 | ch9 s10 第一拍 | 極度 I 人 + MBTI 100% I 圓餅 |
| L363-L365 | ch9 s10 第二拍 | 業務工作變 E + I→E 漸變條 |
| L367-L369 | ch9 s11 ★★ | 人生第一次的外向 · 換來一輩子的內向 |
| L371-L373 | ch9 s12 | 職場祝福：不被挫敗給擊敗 |
| L375 | ch9 s13 ★★★ | 電費小偷 final |
