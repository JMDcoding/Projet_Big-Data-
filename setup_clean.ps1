#!/usr/bin/env powershell
<#
.SYNOPSIS
    Initialize and clean the Big Data Pipeline project

.DESCRIPTION
    Ensures the project structure is clean and ready for operation:
    - Removes all local data files
    - Creates necessary directories with .gitkeep
    - Verifies configuration
    - Shows startup instructions

.EXAMPLE
    .\setup_clean.ps1
#>

Write-Host "Big Data Pipeline - Setup & Clean" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[*] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green

# Check venv
Write-Host "[*] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Virtual environment found" -ForegroundColor Green

# Activate venv
Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Clean local data
Write-Host "[*] Cleaning local data files..." -ForegroundColor Yellow
if (Test-Path "data\raw") {
    Get-ChildItem "data\raw" -Exclude ".gitkeep" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Cleaned data/raw/" -ForegroundColor Green
}
if (Test-Path "data\processed") {
    Get-ChildItem "data\processed" -Exclude ".gitkeep" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Cleaned data/processed/" -ForegroundColor Green
}
if (Test-Path "logs") {
    Get-ChildItem "logs" -Exclude ".gitkeep" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Cleaned logs/" -ForegroundColor Green
}

# Remove Python cache
Write-Host "[*] Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path "." -Name "__pycache__" -Recurse | ForEach-Object { Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path "." -Name ".pytest_cache" -Recurse | ForEach-Object { Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue }
Write-Host "[OK] Cache cleaned" -ForegroundColor Green

# Ensure directory structure
Write-Host "[*] Ensuring directory structure..." -ForegroundColor Yellow
@("data\raw", "data\processed", "logs", "notebooks") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
    if (-not (Test-Path "$_\.gitkeep")) {
        New-Item -Path "$_\.gitkeep" -Force | Out-Null
    }
}
Write-Host "[OK] Directory structure verified" -ForegroundColor Green

# Verify config
Write-Host "[*] Verifying configuration..." -ForegroundColor Yellow
if (-not (Test-Path "config\config.py")) {
    Write-Host "[ERROR] config/config.py not found" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Configuration file exists" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==============" -ForegroundColor Green
Write-Host ""
Write-Host "Project Structure:" -ForegroundColor Cyan
Write-Host "  ✓ Python environment ready"
Write-Host "  ✓ Local data cleaned (all data goes to MinIO/PostgreSQL)"
Write-Host "  ✓ Directories initialized"
Write-Host "  ✓ Configuration verified"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start MinIO:      .\start_minio.ps1"
Write-Host "  2. Start PostgreSQL: (should already be running on port 5433)"
Write-Host "  3. Load data:        python main.py"
Write-Host "  4. View dashboard:   streamlit run app.py"
Write-Host ""
Write-Host "Data Storage Strategy:" -ForegroundColor Cyan
Write-Host "  - MinIO Object Storage:  Primary data lake"
Write-Host "  - PostgreSQL Database:   Indexed records for queries"
Write-Host "  - Local filesystem:      TEMPORARY STAGING ONLY (auto-cleaned)"
Write-Host ""
Write-Host "All data files are git-ignored (.gitignore configured)" -ForegroundColor Yellow
Write-Host ""
