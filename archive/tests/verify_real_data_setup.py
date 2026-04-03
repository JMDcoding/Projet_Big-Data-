#!/usr/bin/env python3
"""
Quick verification script to test new data fetching capabilities
Vérifie que tout fonctionne correctement avec les données réelles
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_section(text):
    """Print formatted section"""
    print(f"\n▶ {text}")
    print(f"  {'-'*56}\n")

def check_api_keys():
    """Check environment variables for APIs"""
    print_section("Checking API Keys")
    
    airlabs_key = os.getenv("AIRLABS_API_KEY")
    if airlabs_key:
        print(f"  ✅ AIRLABS_API_KEY found (value: {airlabs_key[:10]}...)")
    else:
        print(f"  ❌ AIRLABS_API_KEY not set")
        print(f"     To enable real flight times:")
        print(f"     1. Register at https://airlabs.co")
        print(f"     2. Copy API key from dashboard")
        print(f"     3. Run: export AIRLABS_API_KEY='your_key'")
        print(f"     (Script will use OpenSky fallback)")
    
    return airlabs_key

def test_imports():
    """Test that all required imports work"""
    print_section("Testing Python Imports")
    
    imports = {
        "requests": "HTTP library",
        "psycopg2": "PostgreSQL driver",
        "python-dotenv": ".env file support",
    }
    
    missing = []
    for lib, desc in imports.items():
        try:
            __import__(lib.replace("-", "_"))
            print(f"  ✅ {lib:20} - {desc}")
        except ImportError:
            print(f"  ❌ {lib:20} - {desc}")
            missing.append(lib)
    
    return len(missing) == 0

def test_database():
    """Test database connection"""
    print_section("Testing Database Connection")
    
    try:
        import psycopg2
        from config.config import get_database_connection
        
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM flights")
            flight_count = cursor.fetchone()[0]
            print(f"  ✅ Database connected")
            print(f"     Current flights: {flight_count}")
            cursor.close()
            conn.close()
            return True
        else:
            print(f"  ❌ Could not connect to database")
            return False
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def test_open_meteo_api():
    """Test Open-Meteo API (weather/storms)"""
    print_section("Testing Open-Meteo API (Weather)")
    
    try:
        import requests
        
        params = {
            "latitude": 48.8527,
            "longitude": 2.3510,
            "hourly": "precipitation",
            "forecast_days": 7
        }
        
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            precipitation = data.get("hourly", {}).get("precipitation", [])
            print(f"  ✅ Open-Meteo API working")
            print(f"     Forecast hours: {len(precipitation)}")
            print(f"     Sample precipitation: {precipitation[0]} mm")
            return True
        else:
            print(f"  ❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API Error: {e}")
        return False

def test_airlabs_api(api_key):
    """Test Airlabs API (flights with real times)"""
    print_section("Testing Airlabs API (Flight Data)")
    
    if not api_key:
        print(f"  ⏭️  Skipped (no API key set)")
        print(f"     Set AIRLABS_API_KEY to enable")
        return None
    
    try:
        import requests
        
        params = {
            "api_key": api_key,
            "limit": "1"
        }
        
        response = requests.get(
            "https://airlabs.co/api/v9/flights",
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("response"):
                flight = data["response"][0]
                print(f"  ✅ Airlabs API working")
                print(f"     Flight: {flight.get('flight_number')}")
                print(f"     From: {flight.get('dep_iata')} → {flight.get('arr_iata')}")
                print(f"     Times: {flight.get('dep_time')} / {flight.get('arr_time')}")
                return True
            else:
                print(f"  ⚠️  No flights in response (normal if none in flight)")
                return True
        else:
            print(f"  ❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API Error: {e}")
        return False

def check_scripts_exist():
    """Check if new scripts exist"""
    print_section("Checking Script Files")
    
    scripts = {
        "fetch_real_lightning.py": "Weather-based lightning fetch",
        "fetch_airlabs_flights.py": "Airlabs-based flights with real times",
        "fetch_real_data.py": "Orchestrator (recommended)",
        "fetch_real_flights.py": "OpenSky fallback flights",
    }
    
    base_path = Path(__file__).parent
    all_exist = True
    
    for script, desc in scripts.items():
        path = base_path / script
        if path.exists():
            print(f"  ✅ {script:30} - {desc}")
        else:
            print(f"  ❌ {script:30} - MISSING!")
            all_exist = False
    
    return all_exist

def show_next_steps(has_api_key):
    """Show recommended next steps"""
    print_header("📋 Next Steps")
    
    if has_api_key:
        print("""
1. Run the orchestrator (gets both real storms & flights):
   python fetch_real_data.py

2. Verify data in database:
   python verify_demo_data.py

3. Launch dashboard:
   python app.py
        """)
    else:
        print("""
1. (OPTIONAL) For better flight times, setup Airlabs:
   • Register at https://airlabs.co
   • Copy API key
   • Run: export AIRLABS_API_KEY='your_key'

2. Fetch real data (works with or without Airlabs):
   python fetch_real_data.py

3. Verify data in database:
   python verify_demo_data.py

4. Launch dashboard:
   python app.py
        """)

def main():
    """Run all checks"""
    print_header("🔍 Real Data Configuration Check")
    
    results = {}
    
    # Check API keys
    api_key = check_api_keys()
    
    # Check imports
    results["imports"] = test_imports()
    if not results["imports"]:
        print("\n❌ Cannot proceed: missing Python dependencies")
        print("   Run: pip install -r requirements.txt")
        return
    
    # Check database
    results["database"] = test_database()
    
    # Check APIs
    results["open_meteo"] = test_open_meteo_api()
    results["airlabs"] = test_airlabs_api(api_key)
    
    # Check scripts
    results["scripts"] = check_scripts_exist()
    
    # Summary
    print_header("✅ Summary")
    
    working = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None])
    
    print(f"\nServices working: {working}/{total}")
    
    if results.get("open_meteo") and results.get("scripts"):
        print("✅ Ready to fetch REAL weather data!")
    
    if results.get("airlabs") and results.get("scripts"):
        print("✅ Ready to fetch REAL flight data with actual times!")
    
    if not results.get("airlabs") and results.get("scripts"):
        print("⚠️  Will use OpenSky for flights (estimated times)")
    
    # Next steps
    show_next_steps(api_key is not None)

if __name__ == "__main__":
    main()
