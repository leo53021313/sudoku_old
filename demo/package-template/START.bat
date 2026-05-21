@echo off
REM ============================================================
REM  START.bat - opens the presentation in the default browser.
REM
REM    1. Starts a local http server on port 8765 (background,
REM       minimized cmd window). The bundled HTML uses absolute
REM       paths so a real server is required - file:// won't work.
REM    2. Opens the browser at http://localhost:8765/
REM
REM    To stop the server after the talk, close the minimized
REM    "Sudoku Demo Server" window.
REM ============================================================

setlocal
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "DIST=%ROOT%\demo\presentation\dist"
set "VENV_PY=%ROOT%\.venv\Scripts\python.exe"
set "PORT=8765"

if not exist "%DIST%\index.html" (
    echo ERROR: %DIST%\index.html not found.
    echo Did you finish running SETUP.bat?
    pause
    exit /b 1
)

if exist "%VENV_PY%" (
    set "PY=%VENV_PY%"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo ERROR: no Python available. Run SETUP.bat first.
        pause
        exit /b 1
    )
    set "PY=python"
)

REM Spawn the http server in a background, minimized cmd window so the
REM presenter sees the browser, not a terminal.
start "Sudoku Demo Server" /MIN cmd /c ""%PY%" -m http.server %PORT% --directory "%DIST%""

REM Give the server ~1s to bind the port before opening the browser.
timeout /t 1 /nobreak >nul

start "" http://localhost:%PORT%/

echo.
echo Presentation should now be open in your default browser.
echo The local server is running minimized as "Sudoku Demo Server".
echo Close that window after the presentation to stop the server.
echo.
endlocal
