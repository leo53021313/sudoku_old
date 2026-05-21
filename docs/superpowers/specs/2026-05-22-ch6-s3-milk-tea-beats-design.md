# ch6 s3「新女生加分」加入 4 beats + 奶茶 img2img 角色 — 設計

> 日期：2026-05-22
> 範圍：`demo/presentation/` 單章節編輯（ch6 step3），新增一個 AI img2img 人物素材

## 1. 目標

把 ch6 s3 從「一次全部出現（女生 + `+` + 字幕）」改成 **4 個 click beat 的漸進揭示**，
並引入新角色「奶茶」（一個奶茶髮色 + 韓式鍋蓋頭的男生），對齊 `demo/script_new.md`
的 ch6 s3 口播：

> 今天有一個男生，他的頭髮顏色是奶茶色的，所以我們叫他奶茶。
> 奶茶他遇見了一個女生，很想追對方，所以一直嘗試跟對方聊天，每次對方有持續回訊息，奶茶就覺得對方也喜歡他。

敘事用途：奶茶把「對方持續回訊息」誤當「對方也喜歡我」，對應 ch6 的 RL 獎勵錯覺
（AI 把「填對一格 +1 分」當成唯一目標）。

## 2. Beat 結構

ch6 s3 由 1 beat → **4 beats**。舞台採「並肩相遇」：

| beat | id | 口播 cue | 畫面 |
|---|---|---|---|
| 0 | `milk-tea-enter` | 今天有一個男生、頭髮奶茶色 | 奶茶 sticker overshoot scale-in、置中（**還沒名牌**） |
| 1 | `name-tag` | 所以我們叫他奶茶 | 奶茶下方彈出名牌「奶茶」（黃底黑邊貼紙、overshoot） |
| 2 | `girl-enter` | 奶茶遇見了一個女生、很想追 | 奶茶左移讓位、女生（GirlNew）從右側滑入並肩、兩人微微面向彼此 |
| 3 | `reply-plus` | 每次對方持續回訊息就覺得對方也喜歡他 | 字幕進入 + 綠色 `+` 由下往上浮（沿用現有 interval 動畫） |

beat 3 字幕沿用現有那句：「奶茶只要看到對方持續回覆訊息，就會覺得對方也喜歡他。」

## 3. 受影響檔案

### 3.1 `demo/presentation/src/data/beat-manifest.js`
- ch6 → step 3 的 `beats` 陣列由 1 筆改為 4 筆（id / cue / scriptLines 如上）。
- 檔頭註解與 `manifest.totalBeats`：95 → **98**（`totalSteps` 58 不變）。
- 無 `localStorage` 持久化（游標走 URL sync，見 `state/useUrlSync.js`），**不需** bump 任何 key。

### 3.2 新檔 `demo/presentation/src/motifs/MilkTea.jsx`
- 鏡像 `GirlNew.jsx`，包 `AiSticker`，`src="/images/ai/ch6/milk-tea.png"`、`alt="奶茶"`。
- **多一層 `onError` fallback**：圖載入失敗（PNG 尚未生成）時改 render `AssetPlaceholder`（`type="[AI]"`、`todo="ch6-milk-tea"`）。
  這樣在使用者把 PNG 丟進路徑前，畫面不破圖；丟進去後自動顯示。
- 簽名比照 GirlNew：`{ width, rotation, shadow, ...rest }`。

### 3.3 `demo/presentation/src/chapters/ch6-sb3/Ch6Step3.jsx` 重構
- 從 `usePresentationContext()` 取 `beatIndex`，移除「一次全顯示」的版面。
- 改為並排 relative stage：
  - 奶茶 `<MilkTea>`：`beatIndex >= 0` 顯示；beat 0 置中、`beatIndex >= 2` 起向左平移讓位。
  - 名牌「奶茶」：`beatIndex >= 1` 顯示（黃底黑邊貼紙、overshoot scale-in）。
  - 女生 `<GirlNew>`：`beatIndex >= 2` 才從右側滑入（`x: 80 → 0`、opacity 0→1）。
  - `+` 浮動 interval 與 beat 3 字幕：`beatIndex >= 3` 才啟動 `setInterval` / 顯示（避免提早冒泡）。
- 動畫氣質沿用現有 overshoot ease `[0.34, 1.56, 0.64, 1]`；`+` 動畫與顏色（`#10B981`、黑描邊）沿用現狀。

### 3.4 `demo/asset-production-ai-prompts.md` §6 新增 #13 `ch6-milk-tea`
- 比照 #11 / #12 格式：用途 / 原路線 / 比例 / 重點 / Prompt / 驗收。
- **img2img 編輯型 prompt**（保留本人樣貌）。色票破例：髮色用一個平塗的奶茶／淺棕色，當刻意的色票延伸（哏就在髮色），其餘維持五色票。
- **隱私**：prompt、spec、commit 一律不寫真名，只用 "the person in the attached photo" 與暱稱「奶茶」。

#### img2img prompt 草稿（English，使用者連同照片一起貼給 Nano Banana 2 / GPT Image）
```
[Paste shared style prefix from §3]

EDIT THE ATTACHED PHOTO: Redraw the real person in the photo in the flat
illustration style described above, while PRESERVING their facial likeness and
identity (same face shape, same features) so they stay recognizable. Keep their
milk-tea / light-brown hair COLOR — render it as a single FLAT milk-tea tan fill
(a deliberate one-off palette extension; this hair color is the character's whole
joke), bold black outline, no gradient. Keep the Korean bowl-cut / round
mushroom-cap hairstyle clearly readable. Redraw as bold black ink outline + flat
color fill only, NO photo texture, NO gradient, NO blur, NO 3D.
Pose: 3/4 front-facing, head and upper torso, a friendly slightly-hopeful
expression (a guy who just met someone he likes). Plain top in soft violet
#C4B5FD. Cream #FFFDF5 plain background. Character takes ~75% of canvas height,
centered, clean sticker cutout. NO text.
Aspect ratio: 1:1 square.
```
- 驗收：一眼看出奶茶髮色 + 鍋蓋頭、保留本人辨識度、線條粗細一致黑邊、除髮色奶茶棕外不出現五色票以外雜色、無文字、可乾淨剪成 sticker。

### 3.5 素材落地（生圖通過後，使用者自行做）
- 把通過的圖存到 `demo/presentation/public/images/ai/ch6/milk-tea.png`。
- 一旦檔案就位，`MilkTea` 的 onError fallback 不再觸發，自動顯示真圖。

## 4. 不做（YAGNI）
- 不改 ch6 其他 step、不動 ch7/ch9 既有角色 callback。
- 不引入新動畫 motif 檔（名牌與滑入用 inline `motion`）。
- 不做圖生圖以外的素材變體；色票破例僅限髮色。

## 5. 驗收
- `npx tsc --noEmit`（或本專案對應 lint/build）通過。
- dev server：ch6 s3 連點 4 下依序揭示 奶茶 → 名牌 → 女生並肩 → 字幕+`+`；倒退鍵可逆。
- PNG 未就位時顯示 `[AI] ch6-milk-tea` placeholder、不破圖。
- `totalBeats` = 98，全片游標前進／後退無錯位。
