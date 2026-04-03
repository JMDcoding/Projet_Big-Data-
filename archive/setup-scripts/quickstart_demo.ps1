# Quick start script for demo data (PowerShell)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "DEMARRAGE RAPIDE - DONNEES DE DEMO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if ($env:VIRTUAL_ENV -eq "") {
    Write-Host "[!] Virtual environment non active" -ForegroundColor Yellow
    Write-Host "    Activez avec: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Virtual environment active" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python disponible: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Python non trouve" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Choisissez une action:" -ForegroundColor Cyan
Write-Host "  1) Population complete (inclut verification)"
Write-Host "  2) Population seule"
Write-Host "  3) Verification seule"
Write-Host "  4) Quitter"
Write-Host ""

$choice = Read-Host "Entrez votre choix [1-4]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Lancement du workflow complet..." -ForegroundColor Cyan
        python demo_workflow.py
    }
    "2" {
        Write-Host ""
        Write-Host "Lancement de la population..." -ForegroundColor Cyan
        python populate_demo_data.py
    }
    "3" {
        Write-Host ""
        Write-Host "Lancement de la verification..." -ForegroundColor Cyan
        python verify_demo_data.py
    }
    "4" {
        Write-Host "Au revoir!" -ForegroundColor Green
    }
    default {
        Write-Host "[ERREUR] Choix invalide" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fini!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
