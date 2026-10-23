@echo off
rem Double-click: start the wiki server (if not running) and open the wiki in Chrome.
setlocal
cd /d "%~dp0"
set "PORT=8770"
set "URL=http://127.0.0.1:%PORT%/"

rem Is the server already up?
curl -s -o nul "%URL%api/tree" && goto open

set "PY=python"
where python >nul 2>nul || set "PY=py"
echo Starting wiki server on %URL% ...
start "Math Wiki server" /min %PY% serve.py --no-browser --port %PORT%

rem Wait up to 15 seconds for the server.
for /l %%i in (1,1,15) do (
  curl -s -o nul "%URL%api/tree" && goto open
  timeout /t 1 /nobreak >nul
)
echo The server did not start. Check the "Math Wiki server" window for errors.
pause
exit /b 1

:open
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if not defined CHROME if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if defined CHROME (
  start "" "%CHROME%" "%URL%"
) else (
  echo Chrome not found; opening the default browser.
  start "" "%URL%"
)
exit /b 0
