# Sudoku RL — 一個學期的 RL 工程實踐

> 用強化學習（MaskablePPO）訓練 AI 解數獨。
> 重點不在 AI 演算法本身，而在「把 RL 從研究 notebook 推到生產品質」的工程旅程。

## TL;DR

- **兩代訓練系統**：`legacy/`（自寫 PyTorch PPO + PyQt6 GUI）→ `sb3/`（Stable-Baselines3 MaskablePPO，主力）
- **自帶資料管線**：`crawler/` HTTP 爬蟲 + Proxy 池 + PyQt6 GUI 抓題目
- **19 個生產化 Bug 修復**：完整紀錄見 [HISTORY.md](HISTORY.md)
- **設計決策**：每個「為什麼這樣寫」的答案在 [CLAUDE.md](CLAUDE.md)

## 專案結構

```
sudoku_old/
├── crawler/      # HTTP 爬蟲 + Proxy 池 + PyQt6 監控 GUI
├── data/         # 共用 puzzle_pool.db（兩代訓練系統共享）
├── docs/         # 簡報原始檔 + 設計規格
├── legacy/       # v1：自寫 PyTorch PPO + PyQt6 訓練 GUI（封存）
├── models/       # legacy 訓練產出
└── sb3/          # v2：MaskablePPO（主力，活躍開發）
```

## 快速試跑（Demo）

### 1. 看訓練曲線

```bash
tensorboard --logdir sb3/runs
```

### 2. 用訓練好的 Model 解題

```bash
cd sb3
python eval_sb3.py --model models/sudoku_sb3_ckpt_400000_steps.zip \
                   --difficulty 1,2 --n-puzzles 3 --debug-n 3
```

### 3. 一鍵啟動兩者（Windows）

```bash
demo.bat
```

## 訓練重點技術

- **26-channel observation**：9 ch one-hot board + 9 ch per-digit candidates + 8 ch aux features
- **729-action space + Action Mask**：禁止 agent 在違規動作上浪費學習
- **27 個 Constraint Heads**：9 列 + 9 行 + 9 宮，把規則織進網路結構
- **TeacherEngine + BC Loss**：4-level quality pyramid 提供先驗指導
- **4-stage Curriculum**：L1 → L1+L2 → L1+L2+L3 → 全難度，依成功率自動推進

## Tech Stack

Python 3.11 · PyTorch · Stable-Baselines3 · sb3-contrib · PyQt6 · SQLite (WAL) · requests + SOCKS proxy pool

## 課堂簡報

[2026-04-27 課堂簡報原始檔（Marp）](docs/presentation/2026-04-27-sudoku-journey.md)
