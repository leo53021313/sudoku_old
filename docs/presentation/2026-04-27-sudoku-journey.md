---
marp: true
theme: gaia
paginate: true
size: 16:9
backgroundColor: #fff
style: |
  section {
    font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', sans-serif;
    font-size: 26px;
  }
  section.lead h1 {
    font-size: 56px;
    color: #2c3e50;
  }
  section.lead h2 {
    color: #7f8c8d;
    font-weight: 400;
  }
  h1 { color: #2c3e50; font-size: 38px; }
  h2 { color: #34495e; font-size: 30px; }
  h3 { color: #16a085; font-size: 26px; }
  code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 22px;
  }
  pre {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 12px;
    border-radius: 6px;
    font-size: 20px;
  }
  blockquote {
    border-left: 4px solid #e74c3c;
    color: #555;
    font-style: italic;
  }
  .small { font-size: 20px; color: #7f8c8d; }
  .red { color: #e74c3c; font-weight: bold; }
  .green { color: #27ae60; font-weight: bold; }
---

<!-- _class: lead -->

# 我訓練了一個會解數獨的 AI

## ……然後花了三倍時間在修自己的 bug

<br>

**一個學期的踩坑回憶錄**

---

## TL;DR

- 用強化學習（RL）訓練 AI 解數獨
- 寫了 **兩個版本**：自寫 PyTorch PPO → 遷移到 SB3 MaskablePPO
- 順便寫了一個 **爬蟲 + GUI**，因為要餵題目
- 修了 **19 個生產化 bug**（重點其實在這）

<br>

> 「AI 部分占 30% 工時，剩下 70% 在跟自己的 bug 搏鬥」
> ——本人，凌晨三點，2026

---

## 為什麼選數獨？

| 優點 | 缺點 |
|---|---|
| ✅ 規則明確（不像對話 AI 要猜「合不合理」） | ❌ 解出來沒掌聲 |
| ✅ 答案唯一（對就是對） | ❌ 因為手機 App 也會解 |
| ✅ 規模剛好（81 格，不用租 GPU 農場） | ❌ 沒人看了會驚呼「天才」 |
| ✅ 題目免費（網路上抓不完） | ❌ 但會被網站 ban IP |

<br>

**結論**：適合用來「真的學懂 RL」，而不是「炫技」

---

## 第一版的天真

「應該不難吧？這不就是個 729 維的分類問題嗎？」

```
觀察空間：9×9 = 81 格
動作空間：9 × 9 × 9 = 729（哪格 × 填什麼）
獎勵：填對 +1，填錯 -1
```

訓練 100k 步後……

模型學會了：**永遠填同一格**

因為填重複格會被環境拒絕（沒效果），等於什麼都沒發生，
**也沒有負獎勵**🙃

---

## 悟道 #1：Action Mask

不要讓笨蛋「自己學會」分辨笨方法。

直接 **告訴它** 哪些動作不能選：

```python
def action_masks(self):
    return self._compute_legal_fills()  # bool array of 729
```

<br>

✅ 不再卡同一格
❌ 但訓練還是慢得像在等水煮開（500k 步還在跟「同列不能重複」搏鬥）

---

## 悟道 #2：把規則織進網路結構

**直覺**：CNN 看了夠多數獨應該會「自己學會約束」
**現實**：CNN 表示：我不要

**Constraint Heads**：27 個專家小頭
（9 列 + 9 行 + 9 宮，每個專看一條約束）

```python
row_out = torch.stack([row_head(row_i) for r in range(9)], dim=1)
col_out = torch.stack([col_head(col_j) for c in range(9)], dim=2)
box_out = torch.stack([box_head(box_k) for b in range(9)], dim=1)
```

→ 訓練速度直接 5× 起跳 🚀

---

## ⚠️ 靜默 Bug 警告

看起來人畜無害的程式碼：

```python
col_out = torch.zeros(B, 9, 9, H)
for c in range(9):
    col_out[:, :, c, :] = col_head(...)   # ❌ 梯度斷掉
```

**Autograd 默默放棄了 18/27 個 head 的梯度。**
**沒有錯誤訊息**。模型一直在「假裝」訓練，loss 還會下降，騙你 200k 步。

修法：
```python
col_out = torch.stack([col_head(...) for c in range(9)], dim=2)  # ✅
```

> 教訓：**沉默的失敗最可怕**。寧可大聲崩潰，也不要假裝沒事。

---

## 悟道 #3：Teacher + Curriculum

**Teacher（BC loss）**：找一個寫死的解題器當老師，AI 模仿它

**Curriculum（4 階段難度遞增）**：

| Stage | 題目組成 | 通過門檻 |
|---|---|---|
| 1 | L1: 100% | success ≥ 75% |
| 2 | L1:60% L2:40% | success ≥ 65% |
| 3 | L1:20% L2:40% L3:40% | success ≥ 55% |
| 4 | L1-L4 全混 | （終點） |

**結果**：終於可以收斂了，可喜可賀 🎉

---

## 為什麼遷移到 SB3

我那個自己寫的 PPO：

| 項目 | 自寫 | SB3 |
|---|---|---|
| Vectorized env | ❌ 單環境 | ✅ 8× SubprocVecEnv |
| GAE / clip / entropy | 自己算 | 內建 |
| 加 feature 成本 | 改 200 行 | 改 3 行 |
| 學習價值 | ⭐⭐⭐⭐⭐ | ⭐ |

<br>

**心得**：學完原理就該換框架。
**不要當保守派，工程效率才是真實力。**

---

## 但是……題目從哪來？

要訓練 → 要題目 → 要爬 → 於是寫了：

- 🕷 HTTP 爬蟲 + Proxy 池（不然 IP 一下就被擋）
- 💾 SQLite 池（WAL mode、retry、migration）
- 🖼 PyQt6 GUI（因為 `print` 看不夠）
- 🧵 多執行緒 worker

<br>

> 「我只是想訓練 AI，怎麼變成在寫資料中介層？」

**真相**：90% 的 ML 工程不是 ML。

---

## 19 個生產化 Bug

研究模式 → 生產模式 的距離 = **19 個 bug**

| Wave | 數量 | 類型 |
|---|---|---|
| Wave 1 | 5 | 崩潰類（DB 鎖死、編碼、GUI 凍結） |
| Wave 2 | 6 | 邏輯類（TOCTOU、resume 狀態流失） |
| Wave 3 | 8 | 防禦類（沉默失敗、競態條件） |

<br>

<span class="red">**沒有一個 bug 是「AI 的問題」**</span>
全部都是工程問題。

---

## 我最愛的 Bug 集（1/2）

### 🤡 Bug A：Windows 不認識 ≥

```
UnicodeEncodeError: 'cp950' codec can't encode character '≥'
```
訓練跑到一半 `print` 一個 `≥` 直接崩潰。
**中文 Windows 的祖傳鍋。**

### 🧨 Bug B：`-inf × 0 = NaN`

IEEE 754 規定的，PyTorch 照做。
某個 BC loss 在「老師棄權」時整個變 NaN，毒害 optimizer。
**訓練看起來在跑，loss 全 NaN，model 全死。**

---

## 我最愛的 Bug 集（2/2）

### 🪦 Bug C：殭屍 flag

```python
self._refresh_error_shown = False  # 設
self._refresh_error_shown = True   # 又設
# ……從來沒人讀
```
v11 重構時把讀取拿掉了，flag 變殭屍，**活著沒用，刪了沒人發現**。

### 🌀 Bug D：Box head reshape 順序錯

`permute(0,1,3,2,4,5)` 少寫一個 swap，
網路在訓練 **「轉置版的 9×9」**——視覺看起來一樣，**梯度全錯**。
跑了 200k 步才被一個 `torch.allclose` 抓到。

---

## 心得 1：工程紀律

1. **TDD 不是教條** — 是你 24 小時後不會記得自己改了什麼的保險
2. **Commit 要小** — `git bisect` 救過我至少 3 次
3. **Defensive code 不是恐懼** — 是對未來自己的善意
4. **沉默失敗 > 大聲崩潰** — 寧可 raise 也不要 return 假資料

<br>

> 「程式碼不是寫給電腦看的，是寫給 **三個月後忘光的自己** 看的。」

---

## 心得 2：AI 不是魔法

「丟資料給 model 它就會」**是課本騙你的。**

真正讓它 work 的是：

- 🎯 **Action mask**（規則）
- 🏗 **Constraint heads**（結構）
- 👨‍🏫 **Teacher**（先驗）
- 📚 **Curriculum**（順序）

<br>

**AI 是放大器**：
- 好的 prior × 大算力 = 好結果
- 沒有 prior，算力只會把 random 放大成 **expensive random** 💸

---

<!-- _class: lead -->

# 謝謝大家 🙇

📂 GitHub：`leo53021313/sudoku_old`
📊 19 個 bug 的完整故事在 `HISTORY.md`
🛠 設計決策都記在 `CLAUDE.md`

<br>

> 「寫 AI 的部分很簡單，
> 難的是讓它在一台 Windows 上跑三天不崩。」

<br>

## Q & A
