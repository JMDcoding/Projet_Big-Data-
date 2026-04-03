#!/bin/bash
# Quick start script for demo data

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "=========================================="
echo "DEMARRAGE RAPIDE - DONNEES DE DEMO"
echo "=========================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}[!] Virtual environment non activé${NC}"
    echo "    Activez avec: source venv/bin/activate (Linux/Mac) ou venv\Scripts\activate (Windows)"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Virtual environment activé"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Python non trouvé"
    exit 1
fi

echo -e "${GREEN}[OK]${NC} Python disponible"
echo ""

# Menu
echo "Choisissez une action:"
echo "  1) Population complète (inclut vérification)"
echo "  2) Population seule"
echo "  3) Vérification seule"
echo "  4) Quitter"
echo ""
read -p "Entrez votre choix [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Lancement du workflow complet..."
        python demo_workflow.py
        ;;
    2)
        echo ""
        echo "Lancement de la population..."
        python populate_demo_data.py
        ;;
    3)
        echo ""
        echo "Lancement de la vérification..."
        python verify_demo_data.py
        ;;
    4)
        echo "Au revoir!"
        ;;
    *)
        echo -e "${RED}[ERREUR]${NC} Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Fini!"
echo "=========================================="
echo ""
