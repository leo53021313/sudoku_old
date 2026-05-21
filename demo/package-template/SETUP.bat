@echo off
REM ============================================================
REM  SETUP.bat - first-time install on the presenter's machine.
REM
REM  Steps:
REM    1. Verify Python 3.10+ is on PATH
REM    2. Create .venv\ alongside this script
REM    3. pip install -r demo\visualizer-launch\requirements-demo.txt
REM       (into the venv, never the system Python)
REM    4. Register 'sudoku-demo:' URL scheme in HKCU pointing at
REM       demo\visualizer-launch\launcher.bat
REM
REM  Run once. Re-running is safe (idempotent).
REM ============================================================

setlocal
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "LAUNCHER=%ROOT%\demo\visualizer-launch\launcher.bat"
set "REQS=%ROOT%\demo\visualizer-launch\requirements-demo.txt"
set "VENV=%ROOT%\.venv"

echo.
echo ============================================================
echo  Sudoku AI Demo - SETUP
echo ============================================================
echo  Package root : %ROOT%
echo.

REM ---- 1. Python check -----------------------------------------
echo [1/4] Checking Python on PATH...
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ERROR: 'python' was not found on PATH.
    echo   Install Python 3.10 or later from
    echo     https://www.python.org/downloads/
    echo   and tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
python --version
echo   OK.
echo.

REM ---- 2. Create venv ------------------------------------------
REM Use pyvenv.cfg (not Scripts\python.exe) as the "venv is ready" marker.
REM A previous UNINSTALL.bat run can leave a Scripts\python.exe behind if
REM the file was locked at rmdir time, but pyvenv.cfg is always gone in
REM that case -- a missing pyvenv.cfg means the venv is broken and must
REM be rebuilt from scratch.
echo [2/4] Creating virtual environment at .venv\ ...
if exist "%VENV%\pyvenv.cfg" (
    echo   .venv already exists, skipping create.
) else (
    if exist "%VENV%" (
        echo   .venv folder found but pyvenv.cfg missing - removing and rebuilding...
        rmdir /s /q "%VENV%" >nul 2>&1
    )
    python -m venv "%VENV%"
    if errorlevel 1 (
        echo.
        echo   ERROR: failed to create venv.
        pause
        exit /b 1
    )
)
echo   OK.
echo.

REM ---- 3. pip install into venv --------------------------------
echo [3/4] Installing dependencies into venv (5-15 min on first run;
echo       PyTorch alone is ~2 GB)...
echo.
"%VENV%\Scripts\python.exe" -m pip install --upgrade pip
"%VENV%\Scripts\python.exe" -m pip install -r "%REQS%"
if errorlevel 1 (
    echo.
    echo   WARNING: pip install reported errors. The visualizer may
    echo   fail to start. Most common causes: network outage,
    echo   not enough disk space, or a corrupted pip cache.
    echo.
    pause
)
echo   Packages installed.
echo.

REM ---- 4. Register URL scheme ----------------------------------
echo [4/4] Registering 'sudoku-demo:' URL scheme in HKCU...
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
echo  SETUP COMPLETE.
echo.
echo  Next:  double-click START.bat to open the presentation.
echo  Later: double-click UNINSTALL.bat to remove venv + URL key.
echo ============================================================
echo.
pause
endlocal
