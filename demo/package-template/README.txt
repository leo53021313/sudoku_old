================================================================
 Sudoku AI Demo · 給演講者的快速指南
================================================================

【第一次使用】

  1. 把整個 sudoku_demo 資料夾從 Google Drive 下載解壓
     建議放在桌面或 D:\demo\，不要放在 OneDrive 同步資料夾
     （路徑含空白沒關係，含中文也行）

  2. 確認電腦有 Python 3.10 或以上版本
     - 沒裝的話從 https://www.python.org/downloads/ 下載安裝
     - 安裝時務必勾選「Add Python to PATH」
     - 已裝過可以開命令提示字元打 python --version 確認

  3. 雙擊 SETUP.bat
     - 自動建立 .venv\ 虛擬環境（不會污染系統 Python）
     - 自動安裝 pygame / numpy / gymnasium / SB3 / sb3-contrib / torch
       第一次跑大約需要 5-15 分鐘（torch 約 2 GB）
     - 自動寫 HKCU 註冊 sudoku-demo: 網址協定（不需要 admin）
     - 看到 SETUP COMPLETE 就成功了


【演講當天】

  雙擊 START.bat
    - 瀏覽器自動開啟簡報頁面（http://localhost:8765/）
    - 背景有一個最小化的 cmd 視窗叫 "Sudoku Demo Server" 在跑本機伺服器
    - 推進到第 8 章「點我看 AI 即時解數獨 →」貼紙按鈕的步驟
    - 點按鈕 → pygame 視窗 1-2 秒內彈出，AI 解一道數獨 30-60 秒
    - 關掉 pygame 視窗 → 回到簡報，左鍵繼續推進到第 9 章

  注意：簡報用的是 click-driven、不是自動播放
    - 滑鼠左鍵 / 空白鍵 / 右方向鍵 = 推進
    - 右上角有 chapter / step 顯示


【演講結束後】

  - 把背景那個最小化的 "Sudoku Demo Server" 視窗關掉
    （否則本機 port 8765 一直被佔用）
  - 不再需要這套東西的話：雙擊 UNINSTALL.bat 清掉 .venv\ 跟註冊表
  - 或者直接把整個 sudoku_demo 資料夾刪掉也可以


【疑難排解】

  Q: 雙擊 SETUP.bat 跳出「找不到 python」
  A: Python 沒裝或沒加進 PATH。重裝 Python 並勾「Add to PATH」。

  Q: pip install 卡很久 / torch 下載失敗
  A: 多半是網路或硬碟空間問題。確認硬碟有 5 GB 以上空間，
     用穩定網路重跑 SETUP.bat（已下載的快取會繼續用）。

  Q: 雙擊 START.bat 但瀏覽器打開後是空白頁
  A: (a) 等個幾秒，伺服器可能還沒起來，重新整理頁面
     (b) port 8765 被別的程式佔用？關掉那些程式重試
     (c) 手動瀏覽器網址列輸入 http://localhost:8765/

  Q: 點按鈕沒反應，pygame 視窗沒跳出來
  A: (a) 確認 SETUP.bat 跑到底（包含「Registered」訊息）
     (b) 在瀏覽器網址列直接貼 sudoku-demo:run 測試
         應該會跳出 Windows 確認對話框
     (c) 還是不行就改成：另開檔案總管，到
         demo\visualizer-launch\ 雙擊 launcher.bat 直接啟動

  Q: pygame 視窗一閃就關
  A: 從本資料夾打開命令提示字元，跑：
        .venv\Scripts\python.exe -m apprentice.demo.visualize
     會印出實際錯誤訊息。常見原因：模型 checkpoint 不見了，
     或 torch 沒裝乾淨。

================================================================
