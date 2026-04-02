@echo off
REM Setup & Clean script for Big Data Pipeline
REM Windows Batch version

setlocal enabledelayedexpansion

echo.
echo Big Data Pipeline - Setup ^& Clean
echo ==================================
echo.

REM Check Python
echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set pythonver=%%i
echo [OK] %pythonver%

REM Check venv
echo [*] Checking virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo Please run: python -m venv venv
    exit /b 1
)
echo [OK] Virtual environment found

REM Activate venv
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Clean local data
echo [*] Cleaning local data files...
if exist "data\raw" (
    for /f %%f in ('dir /b data\raw ^| findstr /v "^gitkeep"') do del /q data\raw\%%f 2>nul
    echo [OK] Cleaned data/raw/
)
if exist "data\processed" (
    for /f %%f in ('dir /b data\processed ^| findstr /v "^gitkeep"') do del /q data\processed\%%f 2>nul
    echo [OK] Cleaned data/processed/
)
if exist "logs" (
    for /f %%f in ('dir /b logs ^| findstr /v "^gitkeep"') do del /q logs\%%f 2>nul
    echo [OK] Cleaned logs/
)

REM Create directories
echo [*] Ensuring directory structure...
if not exist "data\raw" mkdir data\raw
if not exist "data\processed" mkdir data\processed
if not exist "logs" mkdir logs

if not exist "data\raw\.gitkeep" (type nul > data\raw\.gitkeep)
if not exist "data\processed\.gitkeep" (type nul > data\processed\.gitkeep)
if not exist "logs\.gitkeep" (type nul > logs\.gitkeep)

echo [OK] Directory structure verified

REM Verify config
echo [*] Verifying configuration...
if not exist "config\config.py" (
    echo [ERROR] config/config.py not found
    exit /b 1
)
echo [OK] Configuration file exists

REM Summary
echo.
echo Setup Complete!
echo ==============
echo.
echo Project Structure:
echo   [OK] Python environment ready
echo   [OK] Local data cleaned (all data goes to MinIO/PostgreSQL)
echo   [OK] Directories initialized
echo   [OK] Configuration verified
echo.
echo Next Steps:
echo   1. Start MinIO:      start_minio.bat
echo   2. Start PostgreSQL: (should already be running on port 5433)
echo   3. Load data:        python main.py
echo   4. View dashboard:   streamlit run app.py
echo.
echo Data Storage Strategy:
echo   - MinIO Object Storage:  Primary data lake
echo   - PostgreSQL Database:   Indexed records for queries
echo   - Local filesystem:      TEMPORARY STAGING ONLY (auto-cleaned)
echo.
echo All data files are git-ignored (.gitignore configured)
echo.
pause
