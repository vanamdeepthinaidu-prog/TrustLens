@echo off
setlocal enabledelayedexpansion
title VisionTrust AI - Air-Gapped Platform Launcher

echo ===============================================================================
echo        VisionTrust AI - Trustworthy Computer Vision Assurance (SIH26228)
echo                      Ministry of Defence / Indian Army DGIS
echo ===============================================================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ and ensure 'Add to PATH' is checked.
    pause
    exit /b 1
)

echo [*] Platform Mode: Air-Gapped / Offline Guaranteed
echo [*] Working Directory: %~dp0
echo [*] Starting Unified FastAPI Backend (Serving Frontend UI + APIs)...
echo.
echo -------------------------------------------------------------------------------
echo   * Web Dashboard UI:     http://localhost:8000
echo   * Interactive API Docs:  http://localhost:8000/docs
echo   * System Health Check:   http://localhost:8000/api/system/status
echo -------------------------------------------------------------------------------
echo.
echo [*] Launching your default web browser to http://localhost:8000 ...
echo [*] Keep this command prompt window open while using the platform.
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8000"

cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

