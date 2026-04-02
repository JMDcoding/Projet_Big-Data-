@echo off
REM ============================================================================
REM PostgreSQL Database Cleanup Batch Script
REM ============================================================================
REM Exécute le nettoyage complet de la base de données PostgreSQL
REM Toutes les données de test seront supprimées
REM
REM USAGE: cleanup.bat
REM ============================================================================

echo.
echo ============================================================================
echo  PostgreSQL Database Cleanup
echo ============================================================================
echo.
echo Activating virtual environment...
call .\venv\Scripts\Activate.ps1

echo.
echo Launching cleanup script...
echo.

REM Run the interactive cleanup script
python cleanup_db_complete.py

if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: Cleanup failed
    echo ============================================================================
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo SUCCESS: Database cleanup completed!
echo ============================================================================
echo.
echo Next steps:
echo   1. Run: python main.py
echo   2. Pipeline will fetch ONLY from APIs
echo   3. Data stored in MinIO + PostgreSQL
echo.
pause
