@echo off
REM ============================================================
REM  launcher.bat — invoked by Windows when a `sudoku-demo:` URL
REM  is clicked in a browser.
REM
REM  Auto-detects the sudoku_old/ project root from its own path,
REM  so the same file works on any machine you copy the folder to.
REM
REM  Layout assumption:
REM    sudoku_old/
REM    └── demo/
REM        └── visualizer-launch/
REM            └── launcher.bat   <-- this file
REM ============================================================

setlocal

REM %~dp0 = directory of this .bat (ends with backslash)
REM Three levels up = sudoku_old/
set "ROOT=%~dp0..\..\.."

REM Resolve to an absolute, canonical path (strips ..\..\..)
for %%i in ("%ROOT%") do set "ROOT=%%~fi"

cd /d "%ROOT%"
python -m apprentice.demo.visualize

REM Window closes immediately after pygame quits; no `pause` so the
REM presenter doesn't see a stale cmd window after the demo.
endlocal
