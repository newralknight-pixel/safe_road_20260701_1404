@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -m venv .venv
  if errorlevel 1 (
    echo Python was not found. Install Python 3 first, then run this file again.
    pause
    exit /b 1
  )
)

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install requirements.
  pause
  exit /b 1
)

if not exist "tools\cloudflared.exe" (
  echo Downloading Cloudflare Tunnel...
  mkdir tools 2>nul
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'tools\cloudflared.exe'"
  if errorlevel 1 (
    echo Failed to download cloudflared.
    pause
    exit /b 1
  )
)

echo Starting local detector server...
start "Safe Road Server" cmd /k ".venv\Scripts\python.exe server.py"

echo Waiting for server...
timeout /t 5 /nobreak >nul

echo.
echo A public trycloudflare.com URL will appear below.
echo Keep this window and the server window open while using the app.
echo.
"tools\cloudflared.exe" tunnel --url http://127.0.0.1:8000
pause
