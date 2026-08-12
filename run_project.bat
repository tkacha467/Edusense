@echo off
title EduSense AI Launcher

echo ==========================================
echo        Starting EduSense AI Platform
echo ==========================================
echo.

echo [1/3] Starting FastAPI Backend...

start "EduSense Backend" /D "%~dp0backend" cmd /k python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

timeout /t 5 >nul

echo.
echo [2/3] Starting React Frontend...

start "EduSense Frontend" /D "%~dp0frontend" cmd /k npm run dev

timeout /t 5 >nul

echo.
echo [3/3] Opening Browser...

start http://localhost:5173

echo.
echo ==========================================
echo EduSense AI Started Successfully
echo ==========================================

pause