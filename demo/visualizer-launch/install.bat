@echo off
REM ============================================================
REM  install.bat — one-shot setup on a target machine.
REM
REM  Steps:
REM    1. Auto-detect sudoku_old/ project root from this file's path
REM    2. Verify Python is on PATH
REM    3. pip install -r requirements-demo.txt
REM    4. Register the `sudoku-demo:` URL scheme in HKCU
REM       (no admin needed; per-user only)
REM
REM  Run once per machine. Re-running is safe (idempotent).
REM ============================================================

setlocal

REM Resolve project root. %~dp0 already ends in a backslash (i.e. points
REM "inside" visualizer-launch), so two ..\ hops reach sudoku_old/.
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%..\.."
for %%i in ("%ROOT%") do set "ROOT=%%~fi"
set "LAUNCHER=%SCRIPT_DIR%launcher.bat"
for %%i in ("%LAUNCHER%") do set "LAUNCHER=%%~fi"

echo.
echo ============================================================
echo  Sudoku AI Visualizer - install
echo ============================================================
echo  Project root : %ROOT%
echo  Launcher     : %LAUNCHER%
echo.

REM ── Step 1: verify Python is reachable ───────────────────────
echo [1/3] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ERROR: 'python' not found on PATH.
    echo   Install Python 3.10+ from https://www.python.org/downloads/
    echo   and re-run this script. Make sure to tick "Add to PATH"
    echo   during install.
    echo.
    pause
    exit /b 1
)
python --version
echo   OK.
echo.

REM ── Step 2: pip install requirements ─────────────────────────
echo [2/3] Installing Python packages (this may take 5-10 minutes
echo       on first run, depending on your network and whether
echo       torch wheels are cached)...
echo.
python -m pip install --upgrade pip
python -m pip install -r "%SCRIPT_DIR%requirements-demo.txt"
if errorlevel 1 (
    echo.
    echo   WARNING: pip install reported errors. Registry will
    echo   still be registered, but you may need to fix the
    echo   Python environment manually before the visualizer
    echo   will start.
    echo.
)
echo   Packages installed.
echo.

REM ── Step 3: register URL scheme in HKCU ──────────────────────
echo [3/3] Registering 'sudoku-demo:' URL scheme in HKCU...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$key='HKCU:\Software\Classes\sudoku-demo';" ^
  "New-Item -Path $key -Force | Out-Null;" ^
  "Set-ItemProperty -Path $key -Name '(default)' -Value 'Sudoku AI Visualizer';" ^
  "Set-ItemProperty -Path $key -Name 'URL Protocol' -Value '';" ^
  "$cmd = \"$key\shell\open\command\";" ^
  "New-Item -Path $cmd -Force | Out-Null;" ^
  "Set-ItemProperty -Path $cmd -Name '(default)' -Value ('\"' + '%LAUNCHER%' + '\"');"
if errorlevel 1 (
    echo   ERROR: PowerShell registry write failed.
    pause
    exit /b 1
)
echo   Registered.
echo.

echo ============================================================
echo  DONE.
echo.
echo  Test by opening any browser tab and pasting:
echo     sudoku-demo:run
echo  into the address bar. The pygame window should appear.
echo.
echo  (First-time click: tick "Always allow" in the browser
echo  confirmation dialog to skip it in future.)
echo.
echo  To remove the URL scheme later, run: uninstall.bat
echo ============================================================
echo.
pause
endlocal
