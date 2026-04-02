@echo off
REM Database initialization batch script for Windows

echo ====================================
echo PostgreSQL Database Initialization
echo ====================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Run initialization script
echo Starting database initialization...
python initialize_db.py

if errorlevel 1 (
    echo.
    echo ❌ Database initialization failed!
    echo Please check:
    echo - PostgreSQL is running
    echo - .env file is properly configured
    echo - Database credentials are correct
    pause
    exit /b 1
)

echo.
echo ✅ All done! Your database is ready.
pause
