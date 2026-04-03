@echo off
REM Start the data refresh service in background

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ======================================
echo Starting Data Refresh Service
echo ======================================

if not exist venv\ (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start service in a new window
start "Data Refresh Service" cmd /k "python refresh_service_standalone.py"

echo.
echo Service window opened in background
echo The dashboard will now receive automatic data updates
echo.
echo Lightning data: every 20 minutes
echo Flights data: every 2 hours
echo.
pause
