@echo off
REM 一鍵啟動 Sudoku Demo：TensorBoard + eval_sb3.py
REM 用法：直接雙擊或在 cmd 執行 demo.bat

echo [Demo] 啟動 TensorBoard（背景視窗）...
start "TensorBoard" cmd /k "tensorboard --logdir sb3\runs --port 6006"

echo [Demo] 等 TensorBoard 啟動 5 秒...
timeout /t 5 /nobreak > nul

echo [Demo] 開瀏覽器到 TensorBoard...
start http://localhost:6006

echo [Demo] 跑 eval_sb3 解 L1 + L2 各 3 題...
cd sb3
python eval_sb3.py --model models\sudoku_sb3_ckpt_400000_steps.zip ^
    --difficulty 1,2 --n-puzzles 3 --debug-n 3

echo.
echo [Demo] eval 結束。TensorBoard 視窗請手動關閉。
pause
