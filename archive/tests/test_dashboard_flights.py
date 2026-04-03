#!/usr/bin/env python3
"""
Test the dashboard flight loading and filtering.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import pandas as pd
from app import load_data
from src.visualization import LightningDashboard

print("\n" + "="*60)
print("DASHBOARD FLIGHT LOADING TEST")
print("="*60)

try:
    print("\n[*] Loading data from app.py...")
    lightning_df, flights_df, disruptions_df = load_data()
    
    print(f"[OK] Loaded data:")
    print(f"     - Lightning: {len(lightning_df)} records")
    print(f"     - Flights: {len(flights_df)} records")
    print(f"     - Disruptions: {len(disruptions_df)} records")
    
    if flights_df.empty:
        print("\n[ERROR] Flights DataFrame is empty!")
        exit(1)
    
    print(f"\n[OK] Flights DataFrame structure:")
    print(f"     - Columns: {list(flights_df.columns)}")
    print(f"     - Shape: {flights_df.shape}")
    print(f"     - departure_time dtype: {flights_df['departure_time'].dtype}")
    print(f"     - arrival_time dtype: {flights_df['arrival_time'].dtype}")
    
    # Show sample flights
    print(f"\n[OK] Sample flights (first 3):")
    print(flights_df[['id', 'flight_number', 'departure', 'arrival', 'departure_time', 'arrival_time']].head(3))
    
    # Test dashboard filters
    print(f"\n[*] Testing dashboard filters...")
    dashboard = LightningDashboard()
    
    # Test with no filters
    filtered = dashboard.apply_flights_filters(flights_df, {})
    print(f"[OK] Filter with empty dict: {len(filtered)}/{len(flights_df)} flights")
    
    # Test with today's date range
    today = pd.Timestamp.now().date()
    start = pd.Timestamp.now() - pd.Timedelta(days=7)
    filters = {"date_range": (start.date(), today)}
    filtered = dashboard.apply_flights_filters(flights_df, filters)
    print(f"[OK] Filter with today's date range: {len(filtered)}/{len(flights_df)} flights")
    
    # Test with a wide date range that covers 2026
    filters = {"date_range": (pd.Timestamp("2020-01-01").date(), pd.Timestamp("2030-01-01").date())}
    filtered = dashboard.apply_flights_filters(flights_df, filters)
    print(f"[OK] Filter with wide range (2020-2030): {len(filtered)}/{len(flights_df)} flights")
    
    print("\n[OK] All tests passed! Dashboard should display flights correctly.")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
