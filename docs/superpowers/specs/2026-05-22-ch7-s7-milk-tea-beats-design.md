# ch7 s7「老油條 ★★★」加入奶茶 + 7-beat 重排 — 設計

> 日期：2026-05-22
> 範圍：`demo/presentation/` 單章節編輯（ch7 step7）。無新 AI 素材（沿用既有 `milk-tea.png` / `girl-veteran.png`）。
> 關聯：延續 [2026-05-22-ch6-s3-milk-tea-beats-design.md](2026-05-22-ch6-s3-milk-tea-beats-design.md) 引入的奶茶角色。

## 1. 目標

把 ch7 s7 從 6 beats → **7 beats**，並把整段主角改為「奶茶」，對齊 `demo/script_new.md` ch7 s7：

> 這種感覺就像是奶茶他為了雪恥，特地去網路上看了一堆與女生聊天的攻略，正當奶茶以為這次可以跟女生有進一步的發展時／女生直接出陷阱題給他，例如「我和你媽一起掉進水裡，你會先救誰」？又例如「你覺得我該不該去運動？」／答該去運動＝嫌那個女生胖／答不用＝沒在關心女生的身體健康／奶茶一看到這種題目人都傻了，網路上也沒有一個正確解答。

敘事用途：對應 reasoner 版本「AI 永遠拿不到解出題目的大獎」——奶茶面對沒有正解的陷阱題而當機。

## 2. 舞台（左右對峙）

奶茶在左（水平翻轉面向右）、老油條女生在右，兩個側角色用**絕對定位** flank 中央那欄（標題／陷阱題卡／❌ 答案／punchline）。中央欄沿用現有結構與動畫，不打散卡片與填答機制。

## 3. Beat 結構（6 → 7）

| beat | id | 口播 cue | 畫面 |
|---|---|---|---|
| 0 | `milk-tea-study` | 奶茶為了雪恥看了一堆攻略、以為能更進一步 | 奶茶入場（左、翻轉面向右）+ 旁邊「戀愛攻略」黃皮書 [D] sticker |
| 1 | `girl-traps` | 結果女生直接出陷阱題 | 老油條女生入場（右）+ 標題「女生陷阱題」clip-reveal |
| 2 | `trap-1` | 例如和你媽掉水裡先救誰 | 「救誰」紅卡從左滑入 |
| 3 | `trap-2-question` | 又例如該不該去運動 | 「運動」紫卡從右滑入 + 兩個 ❌??? 填空淡入（anticipation 抖動） |
| 4 | `answer-a-fill` | 答該運動→嫌她胖 | 左填空 → ❌ 嫌那個女生胖（climax A+G + screen shake + aftermath settle） |
| 5 | `answer-b-fill` | 答不用→不關心健康 | 右填空 → ❌ 你不關心健康（climax A+G + screen shake + aftermath settle） |
| 6 | `milk-tea-freeze` | 奶茶人都傻了、網路上也沒正確解答 | 奶茶 grayscale + 頭頂浮動 ❓❓❓ + screen shake；「兩面不討好」punchline（climax B 雙爆） |

## 4. 機制改動（相對現有 `Ch7Step7.jsx`）

- **climax 觸發 beat 順移 +1**：原 beat 3/4/5 → 改 **4/5/6**（`climaxA` beat 4、`climaxB` beat 5、`climaxBoth` beat 6）。`aftermathA/B` 計時器對應移到 beat 4/5。
- **移除原 auto-advance**：原本 beat 4→5（answer-b → both-flash）400ms 自動推進的 `useEffect` 刪除。結尾 freeze 改為 presenter 點擊觸發（喜劇節奏更好掌握），即 beat 6 為 `type:'click'`（原 both-flash 是 `type:'auto'`）。
- **中央欄 beat 閾值整體 +1**：標題與女生 `beatIndex>=1`（原 >=0）、trap-1 `>=2`（原 >=1）、trap-2＋填空 `>=3`（原 >=2，`anticipationActive = beatIndex===3`）、answer-a fill `>=4`（原 >=3）、answer-b fill `>=5`（原 >=4）、final「兩面不討好」`>=6`（原 >=5）。
- **奶茶**：`beatIndex>=0` 入場，外層 `motion.div` 絕對定位於左側；內層包一個 `transform: scaleX(-1)` 的 div 讓奶茶面向右（硬陰影方向隨之翻到左下，可接受、dev 微調）。`beatIndex>=6` 時外層 `style.filter='grayscale(1)'`（帶 transition）並在 effect 內 `triggerShake()` 一次；frozen 時額外 render 3 個浮動 `?`（紅字黑描邊、循環上浮）。
- **戀愛攻略書**：純文字 [D] sticker（黃底黑邊、`戀愛攻略`），絕對定位於奶茶手邊，`beatIndex>=0` 顯示。無新素材。
- **女生**：沿用 `GirlVeteran` motif，改 `beatIndex>=1` 入場，定位右側。

## 5. 受影響檔案

- `demo/presentation/src/data/beat-manifest.js`：ch7（id:7）step 7 的 beats 由 6 筆改 7 筆（id/cue/climax 如上）；`duration` 26→30；`motifs` 加 `'milk-tea'`；頂部 `totalBeats` 98→99（`totalSteps` 不變）。
- `demo/presentation/src/state/usePresentation.test.js`：`totalBeats` 斷言 98→99；新增 ch7 s7 有 7 beats 的測試。
- `demo/presentation/src/chapters/ch7-reasoner/Ch7Step7.jsx`：整檔改寫如上（加奶茶+攻略、beat 閾值順移、移除 auto-advance、freeze FX）。

## 6. 不做（YAGNI）
- 不生新 AI 素材（freeze 用特效、攻略書用 [D] 文字）。
- 不改 ch7 其他 step、不動 ch6/ch9 既有奶茶/女生使用處。
- 不新增 motif 檔（攻略書與 ❓ 用 inline `motion`）。

## 7. 驗收
- `npm run test:run` 全綠（含新 ch7 s7 7-beats 測試、`totalBeats=99`）。
- `npm run build` 無錯。
- dev server ch7 s7 連點 7 下：奶茶+攻略 → 女生+標題 → 救誰卡 → 運動卡+填空 → ❌嫌胖（爆+shake）→ ❌不關心（爆+shake）→ 奶茶灰階+❓+兩面不討好；倒退可逆。
- 全片 `totalBeats=99`，游標前進後退無錯位。
