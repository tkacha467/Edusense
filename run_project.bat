@echo off
title EduSense AI Platform Launcher
color 0A

echo ========================================================
echo               EduSense AI Platform Launcher
echo ========================================================
echo.

:: Set environment defaults for development
set SECRET_KEY=dev_secret_key_edusense_ai_2026_super_secure
set DATABASE_URL=sqlite:///./edusense.db

echo [1/4] Running Database Table Initialization ^& Seed...
python "%~dp0backend\app\seeds\seed_demo_data.py"

if %ERRORLEVEL% NEQ 0 (
    echo [!] Database seeding had warnings, continuing...
) else (
    echo [+] Database verified and seeded successfully.
)
echo.

echo [2/4] Starting FastAPI Backend (Port 8000)...
start "EduSense Backend" /D "%~dp0backend" cmd /k "set SECRET_KEY=dev_secret_key_edusense_ai_2026_super_secure && set DATABASE_URL=sqlite:///./edusense.db && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 4 >nul

echo.
echo [3/4] Starting Vite React Frontend (Port 5173)...
start "EduSense Frontend" /D "%~dp0frontend" cmd /k "npm run dev"

timeout /t 4 >nul

echo.
echo [4/4] Launching Browser Application...
start http://localhost:5173

echo.
echo ========================================================
echo   EduSense AI Platform Running: http://localhost:5173
echo ========================================================
echo   Backend API Docs: http://localhost:8000/docs
echo ========================================================
echo.

pause