@echo off
title VisionTrust AI - Full Stack Dev Launcher
echo ===============================================================================
echo Starting VisionTrust AI in Dual-Server Development Mode
echo ===============================================================================
echo.
echo Starting Backend API Server (Port 8000)...
start "VisionTrust Backend (8000)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --reload --port 8000"

echo Starting Frontend Vite Server (Port 5173)...
start "VisionTrust Frontend (5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend running on: http://localhost:8000 (Docs: http://localhost:8000/docs)
echo Frontend running on: http://localhost:5173
echo.
pause

