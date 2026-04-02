# Start the data refresh service in background
# Usage: .\start_refresh_service.ps1

param(
    [switch]$NoWindow = $false
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting Data Refresh Service" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $scriptPath

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Start service
Write-Host ""
Write-Host "Starting refresh service..." -ForegroundColor Green
Write-Host ""

if ($NoWindow) {
    # Run in same window
    python refresh_service_standalone.py
} else {
    # Run in new window
    $processArgs = @{
        FilePath = "powershell"
        ArgumentList = "-NoExit", "-Command", "python refresh_service_standalone.py"
        WindowStyle = "Normal"
    }
    Start-Process @processArgs
    
    Write-Host "Service window opened in background" -ForegroundColor Green
}

Write-Host ""
Write-Host "The dashboard will now receive automatic data updates:" -ForegroundColor Cyan
Write-Host "  - Lightning data: every 20 minutes" -ForegroundColor Yellow
Write-Host "  - Flights data: every 2 hours" -ForegroundColor Yellow
Write-Host ""
