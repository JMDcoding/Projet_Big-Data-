"""
Simplified storm forecast API testing.
"""
import sys
sys.path.insert(0, '.')

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

print("=" * 70)
print("STORM FORECAST API TESTING")
print("=" * 70)

# Test coordinates (Lyon)
LAT, LON = 45.764, 4.8357

# Test 1: Open-Meteo (FREE, NO KEY)
print("\n1. OPEN-METEO FORECAST (FREE)")
print("-" * 70)
try:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=weather_code&timezone=Europe/Paris"
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        codes = data.get("daily", {}).get("weather_code", [])
        
        # Storm codes: 80-99
        storm_codes = [80, 81, 82, 85, 86, 95, 96, 99]
        has_storm = any(code in storm_codes for code in codes[:5])
        
        print(f"✅ SUCCESS - Weather codes received:")
        print(f"   Next 5 days: {codes[:5]}")
        print(f"   Storm risk: {'⚠️ HIGH' if has_storm else '✓ Low'}")
        print(f"   (Codes 80-99 = storms, 95+ = severe)")
    else:
        print(f"❌ Error: {resp.status_code}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Test 2: WeatherAPI (FREE TIER)
print("\n2. WEATHERAPI.COM (FREEMIUM)")
print("-" * 70)
try:
    url = f"https://api.weatherapi.com/v1/current.json?q={LAT},{LON}&aqi=yes"
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        data = resp.json()
        condition = data.get("current", {}).get("condition", {})
        print(f"✅ SUCCESS - Current conditions:")
        print(f"   Condition: {condition.get('text')}")
        print(f"   icon: {condition.get('icon')}")
        print(f"   Note: Requires free API key from weatherapi.com")
    else:
        print(f"⚠️ No API key - need registration at weatherapi.com")
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Test 3: OpenWeatherMap One Call
print("\n3. OPENWEATHERMAP ONE CALL (FREEMIUM)")
print("-" * 70)
try:
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,daily,alerts&appid=demo"
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        print(f"✅ Would work with API key")
    elif resp.status_code == 401:
        print(f"⚠️ API key required (free tier available)")
        print(f"   Register at: openweathermap.org/api/one-call-api-3")
    else:
        print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")

# Test 4: Simple weather check via HTML scrape (FALLBACK)
print("\n4. METEOFRANCE DATA (via open source)")
print("-" * 70)
try:
    # This is public forecast data
    url = f"https://www.previsions-meteo.ch/uploads/json/europe_france.json"
    resp = requests.get(url, timeout=10)
    
    if resp.status_code == 200:
        print(f"✅ French weather data available (public)")
        data = resp.json()
        if isinstance(data, dict):
            print(f"   Cities in data: {len(data)} regions")
    else:
        print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"⚠️ Status: {str(e)}")

print("\n" + "=" * 70)
print("SUMMARY & RECOMMENDATIONS")
print("=" * 70)

summary = """
🎯 BEST OPTION FOR RISK ZONES: Open-Meteo
   ✅ Completely FREE - no registration needed
   ✅ Provides weather codes for storm detection  
   ✅ Daily forecasts up to 16 days
   ✅ Weather code 95-99 = SEVERE STORMS ⚠️
   ✅ Simple REST API - lightweight
   
💡 Storm Detection Logic:
   - Weather codes 80, 81, 82 = Showers
   - Weather codes 85, 86 = Freezing rain
   - Weather codes 95, 96, 99 = THUNDERSTORMS ⚠️
   
📊 Integration Plan:
   1. Add StormForecastAPI class to api_client.py
   2. Query Open-Meteo daily forecasts
   3. Tag zones with storm risk (None/Low/Medium/High/Severe)
   4. Alert when: Storm forecast + Active flights in zone
   5. Color-code dashboard (🟢 Safe → 🔴 Critical)

Optional: Register for free on:
   - weatherapi.com (300k calls/month free)
   - openweathermap.org (1000 calls/day free)
"""

print(summary)
