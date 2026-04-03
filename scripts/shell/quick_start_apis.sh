#!/bin/bash
# QUICK START: Test toutes les solutions API de vol disponibles

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        FLIGHT API SOLUTIONS - QUICK START                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}[1] Testing Demo Data (QUICKEST - 5min)${NC}"
echo "    This has flight departure/arrival pre-generated"
echo ""

if [ -f "populate_demo_data.py" ]; then
    echo -e "    ${GREEN}✓${NC} Running populate_demo_data.py..."
    python populate_demo_data.py
    echo ""
    
    if [ -f "verify_demo_data.py" ]; then
        echo -e "    ${GREEN}✓${NC} Verifying data..."
        python verify_demo_data.py
        echo ""
    fi
else
    echo -e "    ${RED}✗${NC} populate_demo_data.py not found"
    echo ""
fi

echo -e "${BLUE}[2] Testing FlightRoutingAPI (REAL-TIME FREE)${NC}"
echo "    OpenSky flights with estimated departure/arrival"
echo ""

if [ -f "test_flight_apis.py" ]; then
    echo -e "    ${GREEN}✓${NC} Running test_flight_apis.py..."
    echo ""
    python test_flight_apis.py
    echo ""
else
    echo -e "    ${RED}✗${NC} test_flight_apis.py not found"
    echo ""
fi

echo -e "${BLUE}[3] Optional: Testing Airlabs API (REAL DATA)${NC}"
echo "    Requires API key from https://airlabs.co (free tier available)"
echo ""

if [ -z "$AIRLABS_API_KEY" ]; then
    echo -e "    ${YELLOW}⚠${NC}  AIRLABS_API_KEY not set"
    echo "    To test Airlabs:"
    echo "      1. Get free API key: https://airlabs.co"
    echo "      2. Export: export AIRLABS_API_KEY='your_key'"
    echo "      3. Run: python test_flight_apis.py"
else
    echo -e "    ${GREEN}✓${NC} AIRLABS_API_KEY detected - testing..."
    python test_flight_apis.py
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    NEXT STEPS                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1. VIEW PERTURBATIONS:"
echo "   python app.py"
echo "   → Open http://localhost:8501"
echo "   → See 17 disruptions (demo data is ready!)"
echo ""
echo "2. INTEGRATE FLIGHT ROUTING API:"
echo "   python flight_routing_etl_example.py"
echo "   → Fetches real OpenSky flights with routing"
echo ""
echo "3. INTEGRATION IN YOUR CODE:"
echo "   from src.ingestion.flight_routing_api import FlightRoutingAPI"
echo "   api = FlightRoutingAPI(lat=48.85, lon=2.35)"
echo "   result = api.fetch()"
echo ""
echo "4. DOCUMENTATION:"
echo "   See FLIGHT_API_SELECTION_GUIDE.md for complete comparison"
echo ""
