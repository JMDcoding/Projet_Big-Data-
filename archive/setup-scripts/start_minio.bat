@echo off
REM MinIO Server Startup Script for Windows

REM Check if minio.exe exists in the current directory
if not exist "minio.exe" (
    echo.
    echo [ERROR] minio.exe not found in the current directory
    echo.
    echo Please:
    echo 1. Download MinIO from: https://min.io/download
    echo 2. Place minio.exe in this directory: %CD%
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

REM Create data directory if it doesn't exist
if not exist "data\minio" (
    mkdir data\minio
    echo Created data\minio directory
)

REM Set environment variables
set MINIO_ACCESS_KEY=minioadmin
set MINIO_SECRET_KEY=minioadmin
set MINIO_ADDRESS=localhost:9000

REM Start MinIO server
echo.
echo Starting MinIO Server...
echo Access: http://localhost:9000
echo API: http://localhost:9000
echo Console: http://localhost:9001 (if available in your version)
echo Username: %MINIO_ACCESS_KEY%
echo Password: %MINIO_SECRET_KEY%
echo.

minio.exe server data\minio

pause
