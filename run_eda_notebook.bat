@echo off
REM EDA Notebook Launcher Script
REM Launches the Exploratory Data Analysis Notebook

echo.
echo =========================================
echo    EXPLORATORY DATA ANALYSIS (EDA)
echo    Notebook Launcher
echo =========================================
echo.

REM Vérifier si jupyter est installé
python -m pip show jupyter >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing Jupyter...
    python -m pip install jupyter jupyterlab notebook
    echo [*] Jupyter installed!
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Lancer Jupyter Lab (meilleure interface)
echo.
echo [*] Opening EDA Notebook with Jupyter Lab...
echo.
jupyter lab notebooks/eda_analysis.ipynb

pause
