@echo off
title WhatsApp Business AI Agent
echo ========================================================
echo   WhatsApp Business AI Agent - Development Launcher
echo ========================================================
echo.

echo [1/2] Starting Python FastAPI Backend on http://localhost:8000...
start "WhatsApp AI Backend" cmd /k "python main.py"

echo [2/2] Starting React Vite Client Simulator on http://localhost:3000...
start "WhatsApp AI Client" cmd /k "cd /d client && npm.cmd run dev"

echo.
echo ========================================================
echo   Services are running!
echo   - Backend & Webhook:  http://localhost:8000
echo   - Web Simulator UI:   http://localhost:3000
echo ========================================================
pause
