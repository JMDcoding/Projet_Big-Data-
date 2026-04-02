#!/usr/bin/env python3
"""
Quick test: Fetch flights from OpenSky Network
"""
import sys
sys.path.insert(0, '.')

from src.ingestion.alternative_apis import OpenSkyAlternative

print("🚀 Testing OpenSky Network API...")
print("")

api = OpenSkyAlternative(lat=48.8527, lon=2.3510, radius_km=100)

try:
    print("📍 Fetching flights around Paris (radius 100km)...")
    data = api.fetch()
    
    flights = data.get("flights", [])
    print(f"✅ SUCCESS: Found {len(flights)} flights")
    print("")
    
    if flights:
        print("Sample flights:")
        for flight in flights[:5]:
            f = flight.get('flight_number', 'N/A')
            lat = flight.get('latitude', 0)
            lon = flight.get('longitude', 0)
            alt = flight.get('altitude', 0)
            print(f"  {f:10} @ ({lat:.2f}, {lon:.2f}) Alt: {alt}m")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
