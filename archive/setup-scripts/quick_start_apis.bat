@echo off
REM QUICK START: Test toutes les solutions API de vol disponibles

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║        FLIGHT API SOLUTIONS - QUICK START                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1] Testing Demo Data (QUICKEST - 5min)
echo     This has flight departure/arrival pre-generated
echo.

if exist populate_demo_data.py (
    echo     Running populate_demo_data.py...
    python populate_demo_data.py
    echo.
    
    if exist verify_demo_data.py (
        echo     Verifying data...
        python verify_demo_data.py
        echo.
    )
) else (
    echo     X populate_demo_data.py not found
    echo.
)

echo [2] Testing FlightRoutingAPI (REAL-TIME FREE)
echo     OpenSky flights with estimated departure/arrival
echo.

if exist test_flight_apis.py (
    echo     Running test_flight_apis.py...
    echo.
    python test_flight_apis.py
    echo.
) else (
    echo     X test_flight_apis.py not found
    echo.
)

echo [3] Optional: Testing Airlabs API (REAL DATA)
echo     Requires API key from https://airlabs.co ^(free tier available^)
echo.

if "%AIRLABS_API_KEY%"=="" (
    echo     Note: AIRLABS_API_KEY not set
    echo     To test Airlabs:
    echo       1. Get free API key: https://airlabs.co
    echo       2. Set env: set AIRLABS_API_KEY=your_key
    echo       3. Run: python test_flight_apis.py
) else (
    echo     AIRLABS_API_KEY detected - testing...
    python test_flight_apis.py
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    NEXT STEPS                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 1. VIEW PERTURBATIONS:
echo    python app.py
echo    ^-> Open http://localhost:8501
echo    ^-> See 17 disruptions ^(demo data is ready!^)
echo.
echo 2. INTEGRATE FLIGHT ROUTING API:
echo    python flight_routing_etl_example.py
echo    ^-> Fetches real OpenSky flights with routing
echo.
echo 3. INTEGRATION IN YOUR CODE:
echo    from src.ingestion.flight_routing_api import FlightRoutingAPI
echo    api = FlightRoutingAPI^(lat=48.85, lon=2.35^)
echo    result = api.fetch^(^)
echo.
echo 4. DOCUMENTATION:
echo    See FLIGHT_API_SELECTION_GUIDE.md for complete comparison
echo.
