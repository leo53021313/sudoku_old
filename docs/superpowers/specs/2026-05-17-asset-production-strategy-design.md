# Asset Production Strategy · D / E / A 三路線混合

> **狀態**：已套用至 `demo/outline.md` §素材清單
> **影響範圍**：本片所有素材的產製方式 + 新素材決策樹
> **日期**：2026-05-17

## 背景與痛點

`demo/outline.md` 的素材清單裡有約 80-90 條素材條目、原本一律標 `📦` (純 CSS / SVG)。實際產製時遇到瓶頸：

- **Claude 自製 SVG 在「場景插畫」類嚴重翻車**——使用者形容「很醜、一眼看不出來是什麼」
- 痛點集中在類別 B（場景插畫、需具象 recognizability），不在 A（文字 sticker）/ C（裝飾母題）/ D（資料視覺化）

技術根因：Claude 寫 SVG 是「**蒙眼寫座標**」、沒有視覺反饋。所以：

- **簡單形狀**（圓 / 方 / 星 / 箭頭 / 黃底 sticker）→ OK
- **構圖場景**（老師指著黑板 + 學生抄寫）→ 容易失敗
- **有個性的角色**（有表情的人臉 / 動作姿勢）→ 通常翻車

## 驗證實驗

針對 ch2 step1 supervised 場景「老師 + 學生 + 紙張」做 3 輪迭代：

| 版本 | 策略 | 結果 |
|---|---|---|
| v1 | 蒙眼直接產 | 兩個一模一樣火柴人、紙張漂浮、無互動 |
| v2 | 道具放大 + 人物縮小 + 駝背 silhouette + 標籤輔助 + 故事流向 | 整體構圖仍亂、學生姿態看不出在抄筆記 |
| v3 | 學生改背面視角（避開臉 + 動態姿態） | 學生仍像 blob、使用者判定不過 |

**結論**：Route E（自製 SVG）對「**多角色互動 + 動態姿態 + 表情**」場景有結構性上限、即使 3 輪迭代 + frontend-design skill 輔助也達不到「放進演講不丟人」門檻。

對比 Route A（Phosphor icon library）同場景版：5 張 icon 並列卡片（老師→答案→筆記←學生）、10 分鐘產出、視覺自動一致。**勝出**。

## 設計決策

**素材分類為 5 條路線**：

| 路線 | 用法 | 適用情境 | 工時/張 |
|---|---|---|---|
| **[D]** 文字隱喻 | HTML + CSS + Neo-brutalism sticker | 純概念 / 情緒 / 標語 / hero / kicker | 2-5 min |
| **[E]** 自製 SVG | Claude 生 SVG + `frontend-design` skill | 單一物件 / 對稱 / 幾何結構 | 10-30 min |
| **[A]** Icon library | Phosphor / Lucide + Neo-brutalism wrapper | 多角色互動 / 人物 / 動物 / 設備 | 5-15 min |
| **[✓]** 真實素材 | 引用既有檔案 / 截圖 | 程式碼 / tensorboard / visualizer | 路徑可指 |
| **[⛔]** 紅線 | 不可挂的素材 | 偽造截圖 / 假 logo / 假數據 | — |

**全片預期混合比例**：D ≈ 80% · E ≈ 12% · A ≈ 8% · ✓ 點綴。

**重要章節指派**：
- ch 2 ml-map 整章走 [A]（三大塊插畫是整片唯一的「多角色互動 + 重複」場景）
- ch 5 legacy 整章走 [D]（情緒崩盤章、視覺主體是文字）

## 決策樹（新素材必查）

按順序問下來：

1. 是「文字 / 標語 / sticker / hero / kicker / 字幕」？ → **[D]**
2. 是「單一物件 + 對稱 / 幾何」（飛機、星、圓餅、盤面、曲線、翻牌、階梯、漂浮幾何裝飾）？ → **[E]**
3. 是「多角色互動 / 人物動作 / 動物 / 設備識別」？ → **[A]**
4. 是「真實檔案 / 截圖 / 既存 demo」？ → **[✓]** + 路徑
5. 都不是 → 停下來、跟使用者確認

**陷阱題**（容易誤判）：

- 「**人 + 道具**」場景 → 看主體：人主體 = [A]；道具主體（人很小退到副位）= [E]
- 「**多 sticker 並列**」（4 個考題 grid、3 欄對位）→ 純文字色塊組合 = [D]
- 「**漂浮幾何裝飾**」（黃星 / 紫方塊 / 描邊問號）→ 單一幾何 = [E]
- 「**符號 +/+/+ 浮動**」 → 純 CSS 動畫 = [D]

## Route E 製作 SOP

每個 [E] 素材依序執行：

1. **避地雷檢查**：場景含「2+ 角色互動 / 動態姿態 / 臉部表情」之一 → STOP、降級到 Route A
2. **構圖分區**：viewBox 切 2-3 個敘事區、共用底線、留呼吸空間
3. **道具優於人物**：放大語意承載物、縮小人形或避免人形
4. **silhouette 分化**：必須有人形時靠 silhouette + 服裝色分化、不靠臉；優先考慮背面視角
5. **標籤輔助**：補小型黃黑 sticker 標識身分（「老師 / 學生 / SUPERVISED」）
6. **故事流向**：箭頭 + 浮動 token + 視線虛線
7. **嚴守 web_style.md**：cream `#FFFDF5` 底 / 4px 黑邊 / 8-16px hard offset shadow zero blur / 紅 `#FF6B6B` / 黃 `#FFD93D` / 紫 `#C4B5FD` / Space Grotesk 900
8. **迭代上限**：截圖人工驗收最多 2-3 輪、超過仍認不出 → 降級到 Route A 或 D

**提示詞模板**：

> 「產一張 Neo-brutalism 風格 SVG、viewBox 600×360、場景 = `[描述]`。要素 = `[清單]`。每個要素粗略位置 = `[區塊]`。風格 = cream #FFFDF5 底 / 4px 黑邊 / 8-16px hard offset shadow zero blur / 紅 #FF6B6B / 黃 #FFD93D / 紫 #C4B5FD / Space Grotesk 900。驗收 = 一眼看得出 `[關鍵語意]`。」

## Route A 製作 SOP

每個 [A] 素材依序執行：

1. **找 icon**：[phosphoricons.com](https://phosphoricons.com/) 或 [lucide.dev](https://lucide.dev/)、推薦 Phosphor `regular` weight
2. **覆寫 stroke**：`stroke="#000"`、`stroke-width="4"`（與 Neo-brutalism token 一致）
3. **加色塊背景**：4px 黑邊 + 8px hard shadow + 主色填底
4. **多 icon 並列**：「卡片 + 連接箭頭」結構敘事
5. **標籤旋轉**：±3° + hard shadow
6. **禁忌**：絕不用 Phosphor `bold` 或 `fill` 風格（不協調）

**常用 icon 對應表**（按本片需求）：

| 素材 | icon |
|---|---|
| 老師教學 | Phosphor `Chalkboard` + `User` |
| 學生抄筆記 | Phosphor `GraduationCap` + `Notebook` + `Pencil` |
| 折衣服 | Phosphor `Shirt` + `StackSimple` |
| 訓練狗握手 | Phosphor `Dog` + Lucide `Handshake` |
| 房間 / 門 | Phosphor `Door` |
| IP 封鎖 | Phosphor `Prohibit` / `ShieldSlash` |
| 大腦 | Phosphor `Brain` |
| 神經網路 | Phosphor `GraphBranching` / `Tree` |

**例外**：ch 9 step 4 飛機 + 鳥走 [E] 不走 [A]——要「飛機線稿 + 鳥線稿並列、風格一致」、Phosphor 跟手繪 SVG 混搭會違和。

## 套用方式

`demo/outline.md` §素材清單已整段重寫：

1. **頂部**新增「產製路線分類 + 決策樹 + Route E/A SOP」（前述四節）
2. **每章既有素材條目**：`📦` 全部改為對應的 `[D]` / `[E]` / `[A]` / `[✓]` / `[⛔]` 標籤
3. **複合素材**用 `[D]+[E]` 等組合標記（例：「剛認識的新女生 sticker + +/+/+ 加分動畫」拆 [D]+[E]）
4. **章節注記**：ch 2 標「整章走 [A]」、ch 5 標「整章走 [D]」

新增素材時 chapter agent / 實作工程師應：

1. 對著決策樹判斷路線
2. 依該路線 SOP 執行
3. 在素材清單對應章節加入新條目、前綴標路線

## 未涵蓋 / 未來工作

- **icon 對應表**：列了 8 個本片用得到的、其他類型素材若出現需自行擴充
- **Route E 提示詞模板**：可進一步抽出為共用工具 / Claude prompt template、目前嵌在 outline.md 裡
- **Route A 實作示範**：已在 brainstorm session 視覺驗證、實作章節時仍需手動套 wrapper、未抽成 React component（可在 scaffold `presentation/` 時再做）
- **既存 sb3 / reasoner 訓練 log 缺漏問題**（ch 5-7 的視覺證據）：本 spec 不處理、由 `prompt.md` §五紅線管控

## 不變更

- `web_style.md`：完全不動、本策略只規範產製方式、不動視覺 token
- `prompt.md`：完全不動、§五紅線（禁挂偽造截圖等）仍是上位規範
- `script.md`：完全不動、本策略只動視覺層
- outline.md 的 step 內容、beat 機制、Motif Library、章節色票：完全不動、只動 §素材清單
