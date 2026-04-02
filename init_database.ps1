# PostgreSQL Database Initialization Script (PowerShell)

Write-Host "====================================" -ForegroundColor Green
Write-Host "PostgreSQL Database Initialization" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow

$venv_activate = ".\venv\Scripts\Activate.ps1"

if (-Not (Test-Path $venv_activate)) {
    Write-Host "❌ Virtual environment not found at $venv_activate" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

& $venv_activate

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Run initialization script
Write-Host "Starting database initialization..." -ForegroundColor Yellow
Write-Host ""

python initialize_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Database initialization failed!" -ForegroundColor Red
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "- PostgreSQL is running" -ForegroundColor Gray
    Write-Host "- .env file is properly configured" -ForegroundColor Gray
    Write-Host "- Database credentials are correct" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "✅ All done! Your database is ready." -ForegroundColor Green
