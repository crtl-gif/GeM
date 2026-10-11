@echo off
setlocal
cd /d "%~dp0"
title GeM Tender Assistant

echo.
echo ============================================
echo        GeM Tender Assistant
echo ============================================
echo.

if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -m venv .venv
  ) else (
    where python >nul 2>nul
    if errorlevel 1 (
      echo Python was not found.
      echo Install Python 3.11+ from https://www.python.org/downloads/
      echo Select "Add Python to PATH" during installation.
      pause
      exit /b 1
    )
    python -m venv .venv
  )
  if errorlevel 1 goto failed
  set "NEED_INSTALL=1"
)

if not exist ".venv\setup_complete.txt" set "NEED_INSTALL=1"
if defined NEED_INSTALL (
  echo Installing dependencies. This may take a few minutes on first run...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 goto failed
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto failed
  echo setup complete>" .venv\setup_complete.txt"
  if errorlevel 1 goto failed
)

echo Launching the desktop app...
".venv\Scripts\python.exe" desktop_app.py
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Setup or launch failed. Review the error above.
pause
exit /b 1
