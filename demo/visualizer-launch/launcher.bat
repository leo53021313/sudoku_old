@echo off
REM ============================================================
REM  launcher.bat - invoked by Windows when a 'sudoku-demo:' URL
REM  is clicked in a browser.
REM
REM  Auto-detects the package root from its own path, so the same
REM  file works on any machine you copy the folder to.
REM
REM  Layout assumption (with ASCII slashes only - cmd parses these
REM  comments under whatever code page the browser hands us, and
REM  non-ASCII chars break the parser on URL-scheme invocation):
REM
REM    sudoku_demo/
REM        demo/
REM            visualizer-launch/
REM                launcher.bat   <-- this file
REM ============================================================

setlocal

REM %~dp0 = directory of this .bat (ends with backslash, so the path
REM        already points "inside" visualizer-launch). Two ..\ hops
REM        from there land at the package root (sudoku_old/ or sudoku_demo/).
set "ROOT=%~dp0..\.."

REM Resolve to an absolute, canonical path
for %%i in ("%ROOT%") do set "ROOT=%%~fi"

cd /d "%ROOT%"

REM Prefer the bundled venv (created by SETUP.bat) so the demo machine doesn't
REM need apprentice deps installed in the system Python. Fall back to system
REM python if no venv is present (e.g. during dev on the original repo).
REM
REM Check pyvenv.cfg, not just Scripts\python.exe -- if UNINSTALL.bat ran
REM while python.exe was held by another process, Scripts\python.exe can
REM survive a half-rmdir while pyvenv.cfg + Lib\ are gone, leaving a broken
REM venv that fails with "No pyvenv.cfg file" on every invocation.
if exist "%ROOT%\.venv\pyvenv.cfg" (
    "%ROOT%\.venv\Scripts\python.exe" -m apprentice.demo.visualize
) else (
    python -m apprentice.demo.visualize
)

REM Window closes immediately after pygame quits; no `pause` so the
REM presenter doesn't see a stale cmd window after the demo.
endlocal
