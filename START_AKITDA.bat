@echo off
title AKITDA Event & Member Suite 2026
color 0B
echo ===================================================================
echo     AKITDA General Body 2026 (10 Dec 2026) - Event Suite
echo ===================================================================
echo.
echo Starting AKITDA Local Server and Control Panel...
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH!
    echo Please install Python 3.8+ or add it to PATH.
    pause
    exit /b
)

python app.py

if %errorlevel% neq 0 (
    echo.
    echo An unexpected error occurred while running the application.
    pause
)
