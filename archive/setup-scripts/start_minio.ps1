#!/usr/bin/env powershell
# MinIO Server Startup Script for Windows PowerShell

$minioPath = ".\minio.exe"
$dataPath = "data\minio"

Write-Host "MinIO Data Lake Server Startup" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if minio.exe exists
if (-not (Test-Path $minioPath)) {
    Write-Host "[ERROR] minio.exe not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please do the following:" -ForegroundColor Yellow
    Write-Host "1. Download MinIO from: https://min.io/download"
    Write-Host "2. Extract and place minio.exe in: $(Get-Location)"
    Write-Host "3. Run this script again"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Create data directory if needed
if (-not (Test-Path $dataPath)) {
    Write-Host "[+] Creating data directory: $dataPath" -ForegroundColor Green
    New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
}

# Set environment
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin"
$env:MINIO_ADDRESS = "localhost:9000"

Write-Host "[+] MinIO Server Configuration:" -ForegroundColor Green
Write-Host "    Access Key: $($env:MINIO_ACCESS_KEY)"
Write-Host "    Secret Key: $($env:MINIO_SECRET_KEY)"
Write-Host "    Address: $($env:MINIO_ADDRESS)"
Write-Host "    Data Path: $(Resolve-Path $dataPath)"
Write-Host ""
Write-Host "Starting MinIO Server..." -ForegroundColor Cyan
Write-Host "Access: http://localhost:9000" -ForegroundColor Yellow
Write-Host ""

# Start MinIO
& $minioPath server $dataPath
