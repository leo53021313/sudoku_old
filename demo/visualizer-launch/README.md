# Sudoku AI Visualizer · 一鍵啟動套件

把 sudoku_old/ 整個資料夾搬到任何一台 Windows 電腦上、跑一次 `install.bat`、
之後 HTML 簡報的「點我看 AI 即時解數獨 →」按鈕就能直接呼叫桌面 pygame
視窗，不用手動 Alt+Tab。

## 一次性設定（在目標電腦做一次）

1. 把 `sudoku_old/` 解壓到任意位置（例如 `D:\demo\sudoku_old\`）
2. 雙擊 `demo\visualizer-launch\install.bat`
   - 自動偵測 `sudoku_old/` 根目錄
   - 自動 `pip install` 六個套件（pygame / numpy / gymnasium / SB3 / sb3-contrib / torch）
   - 自動寫 HKCU registry 註冊 `sudoku-demo:` URL scheme
   - 全程不需要 admin 權限
3. 在瀏覽器網址列貼 `sudoku-demo:run` 測試 → 應該看到 pygame 視窗跳出
4. 首次點擊時瀏覽器會跳「是否允許打開 Sudoku AI Visualizer？」對話框，勾「永遠允許」之後就不會再跳

## HTML 簡報那一顆按鈕

```html
<a href="sudoku-demo:run" class="big-button">
  點我看 AI 即時解數獨 →
</a>
```

## 演講當天的流程

1. 開好 HTML 簡報（瀏覽器）
2. 推進到 ch 8 step 7（visualizer 大按鈕步驟）
3. 滑鼠點按鈕
4. pygame 視窗 0.5-1s 內跳出、自動搶到最上層
5. AI 解數獨 30-60 秒
6. 關掉 pygame 視窗
7. 簡報自動回到最上層、左鍵繼續到 ch 9

## 演講結束後（如不想留 registry）

雙擊 `demo\visualizer-launch\uninstall.bat`

## 要帶哪些檔案到另一台電腦？最小化清單

```
sudoku_old/
├── apprentice/
│   ├── __init__.py
│   ├── env/                  # SudokuGymEnv + RewardComputer + obs_helpers
│   ├── solver/               # HumanSolver + 13 招 techniques/
│   ├── solver_ext/           # backtracking solve
│   ├── data_pkg/             # PuzzlePoolDB
│   ├── model/                # features_extractor (load checkpoint 用)
│   ├── train/
│   │   ├── __init__.py
│   │   └── ppo.py            # SudokuMaskablePPO
│   ├── demo/
│   │   ├── __init__.py
│   │   └── visualize.py      # 主程式
│   └── models/
│       ├── apprentice_ckpt_<最新N>_steps.zip
│       ├── apprentice_ckpt_<最新N>_steps_vecnorm.pkl
│       └── apprentice_ckpt_<最新N>_steps_curriculum.json
├── data/
│   └── puzzle_pool.db        # 不要拷 .bak/.corrupt/.old/.shm/.wal
└── demo/
    ├── presentation/dist/    # HTML 簡報 build 之後的靜態檔（演講時用）
    └── visualizer-launch/    # 本資料夾全部
        ├── install.bat
        ├── uninstall.bat
        ├── launcher.bat
        ├── requirements-demo.txt
        └── README.md
```

**不要拷貝**：`apprentice/tests/` · `apprentice/eval/` · `apprentice/configs/` ·
`apprentice/train/train.py` · `apprentice/train/curriculum_*.py` ·
`apprentice/models/` 裡的其他 checkpoint。

整包約 13 MB（不含 HTML 簡報 build）。

## 找出最新 checkpoint 的指令

在原機（這台）執行：

```powershell
ls apprentice\models\ | Where-Object { $_.Name -match 'apprentice_ckpt_\d+_steps\.zip$' } |
  Sort-Object { [int]($_.Name -replace 'apprentice_ckpt_(\d+)_steps\.zip','$1') } |
  Select-Object -Last 1
```

對應的 `_vecnorm.pkl` 與 `_curriculum.json` 也一併帶上。

## 疑難排解

| 症狀 | 排查 |
|------|------|
| 點 URL 沒反應 | (a) 在網址列直接貼 `sudoku-demo:run` 看是否跳對話框 (b) 確認 install.bat 跑完且看到「Registered」訊息 (c) `regedit` 開 `HKCU\Software\Classes\sudoku-demo` 看 key 是否存在 |
| pygame 視窗一閃就關 | launcher.bat 開 cmd 跑一次 `python -m apprentice.demo.visualize`，看終端錯誤訊息 |
| `python: command not found` | Python 未裝或未加 PATH。重裝 Python 並勾「Add to PATH」 |
| pip install torch 失敗 | 通常網路問題或磁碟空間。手動 `python -m pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| `No checkpoint found in apprentice/models/` | checkpoint 沒帶過來、或檔名跟 `apprentice_ckpt_<N>_steps.zip` pattern 不符 |
