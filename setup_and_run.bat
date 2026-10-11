@echo off
setlocal
cd /d "%~dp0"
title GeM Tender Assistant Setup

echo.
echo ============================================
echo      GeM Tender Assistant - First Run
echo ============================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON=py"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/
    echo During installation, tick "Add Python to PATH".
    pause
    exit /b 1
  )
  set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating a private Python environment...
  %PYTHON% -m venv .venv
  if errorlevel 1 goto failed
)

echo Installing required packages. This can take a few minutes on first run...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

echo.
echo Setup complete. Starting GeM Tender Assistant...
".venv\Scripts\python.exe" desktop_app.py
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Setup or launch failed. Check the error shown above and try again.
pause
exit /b 1
