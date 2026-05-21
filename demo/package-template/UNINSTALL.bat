@echo off
REM ============================================================
REM  UNINSTALL.bat - remove URL scheme registration and venv.
REM
REM    Does NOT delete the package folder itself. You can delete
REM    the whole folder afterwards if you no longer need it.
REM ============================================================

setlocal
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo.
echo ============================================================
echo  Sudoku AI Demo - UNINSTALL
echo ============================================================
echo.

echo [1/2] Removing 'sudoku-demo:' URL scheme from HKCU...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Remove-Item -Path 'HKCU:\Software\Classes\sudoku-demo' -Recurse -Force -ErrorAction SilentlyContinue"
echo   Done.
echo.

echo [2/2] Removing %ROOT%\.venv ...
if exist "%ROOT%\.venv" (
    rmdir /s /q "%ROOT%\.venv"
    echo   Done.
) else (
    echo   .venv does not exist, skipping.
)
echo.

echo ============================================================
echo  UNINSTALL COMPLETE.
echo  You may now delete the folder if you don't need it anymore.
echo ============================================================
echo.
pause
endlocal
