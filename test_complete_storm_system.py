#!/usr/bin/env python
"""
Complete Storm Forecast + Risk Zone Integration Test
Tests the entire system: Forecast -> Risk Zones -> Alerts
"""
import sys
sys.path.insert(0, '.')

from src.ingestion.api_client import StormForecastAPI
from src.visualization.risk_zones import StormRiskZoneManager

print("\n" + "=" * 80)
print("COMPLETE STORM FORECAST SYSTEM TEST")
print("=" * 80)

# Test cities
cities = [
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Lyon", "lat": 45.764, "lon": 4.8357},
    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698}
]

total_alerts = 0

for city in cities:
    print(f"\n{'='*80}")
    print(f"CITY: {city['name']} ({city['lat']}, {city['lon']})")
    print(f"{'='*80}")
    
    # 1. Fetch storm forecast
    print(f"\n1. FETCHING STORM FORECAST...")
    api = StormForecastAPI(latitude=city["lat"], longitude=city["lon"])
    forecast_result = api.extract()
    
    if forecast_result['status'] != 'success':
        print(f"   ❌ Failed: {forecast_result.get('error')}")
        continue
    
    forecasts = forecast_result['forecasts']
    print(f"   ✅ Forecasts received: {len(forecasts)} days")
    print(f"   Severe storms: {forecast_result['severe_storms']} day(s)")
    
    # Show first 3 days
    print(f"\n2. 3-DAY FORECAST:")
    print(f"   {'Date':<12} {'Code':<6} {'Risk':<10} {'Action':<20}")
    print(f"   {'-'*50}")
    
    for f in forecasts[:3]:
        date = f['date'][:10]
        code = f['weather_code']
        risk = f['storm_risk']
        
        if risk == "SEVERE":
            action = "CLOSE ALL FLIGHTS"
        elif risk == "HIGH":
            action = "RESTRICT FLIGHTS"
        elif risk == "MEDIUM":
            action = "MONITOR CLOSELY"
        else:
            action = "NORMAL OPS"
        
        print(f"   {date:<12} {code:<6} {risk:<10} {action:<20}")
    
    # 2. Create risk zones
    if forecast_result['severe_storms'] > 0:
        print(f"\n3. GENERATING RISK ZONES...")
        manager = StormRiskZoneManager(
            center_lat=city["lat"], 
            center_lon=city["lon"]
        )
        
        zones = manager.create_risk_grid(forecasts, grid_size=5)
        print(f"   ✅ Zones created: {len(zones)} zones")
        print(f"   Zone risk levels: {zones['risk_level'].unique().tolist()}")
        print(f"   Flight restrictions: {zones['flight_restriction'].sum()} zones affected")
        
        # 3. Create dashboard summary
        print(f"\n4. DASHBOARD ALERT SUMMARY...")
        summary = manager.create_dashboard_summary(forecasts, active_flights=3)
        
        print(f"   Alert Level: {summary['alert_level']}")
        print(f"   Status: {summary['severe_storm_days']} severe day(s) forecast")
        print(f"   Active flights at risk: {summary['active_flights']}")
        
        # 4. Recommendations
        if summary['recommendations']:
            print(f"\n5. RECOMMENDATIONS:")
            for rec in summary['recommendations']:
                print(f"   ⚠️  {rec}")
            
            total_alerts += 1
    else:
        print(f"\n✅ NO SEVERE STORMS FORECAST")
        print(f"   Safe for all flight operations")

# Final Summary
print(f"\n\n" + "=" * 80)
print("SYSTEM STATUS SUMMARY")
print("=" * 80)
print(f"Cities analyzed: {len(cities)}")
print(f"Cities with storm alerts: {total_alerts}")
print(f"Overall status: {'CRITICAL' if total_alerts > 0 else 'NORMAL'}")

if total_alerts > 0:
    print(f"\n🚨 ALERT ACTIONS:")
    print(f"   - Activate emergency protocols")
    print(f"   - Notify flight operations")
    print(f"   - Reroute flights away from risk zones")
    print(f"   - Set up continuous monitoring")
else:
    print(f"\n✅ All systems normal - Proceed with standard operations")

print("\n" + "=" * 80)
