@echo off
title Parking Violation System - Server
echo ============================================
echo   Starting Parking Violation System...
echo ============================================
echo.
echo [INFO] Activating virtual environment...
if exist ".\venv\Scripts\python.exe" (
    .\venv\Scripts\python.exe backend/app.py
) else (
    echo [ERROR] Virtual environment (venv) not found.
    echo Please ensure the 'venv' folder exists in the project root.
    pause
)
pause
