@echo off
REM ============================================================
REM  uninstall.bat — removes the `sudoku-demo:` URL scheme
REM  registration from HKCU. Does NOT uninstall Python packages
REM  (use `pip uninstall` for that if needed).
REM ============================================================

setlocal

echo.
echo Removing 'sudoku-demo:' URL scheme from HKCU...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "if (Test-Path 'HKCU:\Software\Classes\sudoku-demo') {" ^
  "  Remove-Item -Path 'HKCU:\Software\Classes\sudoku-demo' -Recurse -Force;" ^
  "  Write-Host '  Removed.';" ^
  "} else {" ^
  "  Write-Host '  Not registered (nothing to remove).';" ^
  "}"

echo.
pause
endlocal
