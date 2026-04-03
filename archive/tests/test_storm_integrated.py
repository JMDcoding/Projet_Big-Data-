#!/usr/bin/env python
"""
Complete Storm Forecast System - Simplified Test
"""
import sys
sys.path.insert(0, '.')

try:
    from src.ingestion.api_client import StormForecastAPI
    from src.visualization.risk_zones import StormRiskZoneManager
    
    print("\n[STORM FORECAST SYSTEM - INTEGRATED TEST]\n")
    
    # Example data (avoiding live API calls)
    example_forecasts = [
        {
            "date": "2026-04-02",
            "weather_code": 80,
            "temperature_max": 14.5,
            "precipitation": 0.7,
            "storm_risk": "HIGH",
            "is_severe": True
        },
        {
            "date": "2026-04-03",
            "weather_code": 61,
            "temperature_max": 12.0,
            "precipitation": 0.2,
            "storm_risk": "LOW",
            "is_severe": False
        },
        {
            "date": "2026-04-04",
            "weather_code": 3,
            "temperature_max": 16.2,
            "precipitation": 0.0,
            "storm_risk": "NONE",
            "is_severe": False
        }
    ]
    
    print("1. STORM FORECAST DATA:")
    print("   Date       | Code | Risk   | Temp(C) | Rain(mm)")
    print("   -----------|------|--------|---------|--------")
    for f in example_forecasts:
        print(f"   {f['date']} | {f['weather_code']:4} | {f['storm_risk']:6} | {f['temperature_max']:6.1f} | {f['precipitation']:6.1f}")
    
    print("\n2. RISK ZONE GENERATION:")
    manager = StormRiskZoneManager(center_lat=48.8566, center_lon=2.3522)
    zones = manager.create_risk_grid(example_forecasts, grid_size=5)
    
    print(f"   Generated {len(zones)} zones in 5x5 grid")
    print(f"   Risk levels: {zones['risk_level'].unique().tolist()}")
    print(f"   Restricted zones: {zones['flight_restriction'].sum()}")
    
    print("\n3. DASHBOARD ALERT SYSTEM:")
    summary = manager.create_dashboard_summary(example_forecasts, active_flights=3)
    
    print(f"   Alert Level: {summary['alert_level']}")
    print(f"   Severe storm days: {summary['severe_storm_days']}")
    print(f"   Next storm date: {summary['next_storm_date']}")
    print(f"   Active flights at risk: {summary['active_flights']}")
    
    print("\n4. RECOMMENDATIONS:")
    for rec in summary['recommendations']:
        print(f"   - {rec}")
    
    print("\n5. GEOJSON EXPORT:")
    geojson = manager.export_to_geojson(zones)
    print(f"   GeoJSON created with {len(geojson['features'])} features")
    print(f"   Ready for mapping (Folium, Mapbox, etc.)")
    
    print("\n[SYSTEM STATUS: OPERATIONAL]")
    print("[ALERT STATUS: CRITICAL - Storm forecast active]\n")
    
except Exception as e:
    print(f"[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()
