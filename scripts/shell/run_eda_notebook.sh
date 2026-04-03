#!/bin/bash
# EDA Notebook Launcher Script
# Launches the Exploratory Data Analysis Notebook

echo ""
echo "========================================="
echo "   EXPLORATORY DATA ANALYSIS (EDA)"
echo "   Notebook Launcher"
echo "========================================="
echo ""

# Vérifier si jupyter est installé
if ! python -m pip show jupyter &> /dev/null; then
    echo "[*] Installing Jupyter..."
    python -m pip install jupyter jupyterlab notebook
    echo "[*] Jupyter installed!"
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer Jupyter Lab (meilleure interface)
echo ""
echo "[*] Opening EDA Notebook with Jupyter Lab..."
echo ""
jupyter lab notebooks/eda_analysis.ipynb
