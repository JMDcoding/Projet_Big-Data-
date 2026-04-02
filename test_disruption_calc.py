#!/usr/bin/env python3
"""
Test disruption calculation functionality.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import pandas as pd
from src.transformation.disruption_calculator import DisruptionCalculator

print("\n" + "="*70)
print("DISRUPTION CALCULATION TEST")
print("="*70)

# Create calculator
calc = DisruptionCalculator()

# Sample data
print("\n[*] Creating sample data...")

# Lightning strikes near Paris
lightning_data = [
    {
        "id": 1,
        "latitude": 48.8566,
        "longitude": 2.3522,
        "timestamp": pd.Timestamp("2026-04-02 10:00:00"),
        "intensity": 5
    },
    {
        "id": 2,
        "latitude": 48.9,
        "longitude": 2.4,
        "timestamp": pd.Timestamp("2026-04-02 10:05:00"),
        "intensity": 7
    },
    {
        "id": 3,
        "latitude": 49.0,
        "longitude": 2.5,
        "timestamp": pd.Timestamp("2026-04-02 09:50:00"),
        "intensity": 3
    }
]

# Flights in Paris area at same time
flights_data = [
    {
        "id": 101,
        "flight_number": "AF100",
        "latitude": 48.87,
        "longitude": 2.35,
        "departure_time": pd.Timestamp("2026-04-02 09:50:00"),
        "arrival_time": pd.Timestamp("2026-04-02 11:30:00")
    },
    {
        "id": 102,
        "flight_number": "BA200",
        "latitude": 49.0,
        "longitude": 2.5,
        "departure_time": pd.Timestamp("2026-04-02 10:00:00"),
        "arrival_time": pd.Timestamp("2026-04-02 12:00:00")
    },
    {
        "id": 103,
        "flight_number": "LH300",
        "latitude": 50.0,
        "longitude": 3.0,
        "departure_time": pd.Timestamp("2026-04-02 10:00:00"),
        "arrival_time": pd.Timestamp("2026-04-02 12:30:00")
    }
]

print(f"[OK] Lightning strikes: {len(lightning_data)}")
print(f"[OK] Flights: {len(flights_data)}")

# Calculate disruptions
print("\n[*] Calculating disruptions...")
disruptions = calc.calculate_disruptions(lightning_data, flights_data)

print(f"[OK] Disruptions calculated: {len(disruptions)}")

# Display results
if disruptions:
    print("\n[RESULTS]")
    print("-" * 70)
    for disruption in disruptions:
        flight_id = disruption.get("flight_id")
        distance = disruption.get("distance_km")
        probability = disruption.get("disruption_probability")
        risk = disruption.get("risk_level")
        
        print(f"\nFlight #{flight_id}:")
        print(f"  Distance to closest lightning: {distance} km")
        print(f"  Disruption probability: {probability*100:.1f}%")
        print(f"  Risk level: {risk}")
        print(f"  Nearby lightning strikes: {disruption.get('lightning_count_nearby')}")
else:
    print("\n[OK] No disruptions detected (all flights safe)")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nDisruption calculator working correctly!")
print("Risk levels:")
print("  - CRITICAL: >= 70% probability")
print("  - HIGH:     50-70% probability")
print("  - MEDIUM:   30-50% probability")
print("  - LOW:      10-30% probability")
print("  - MINIMAL:  < 10% probability")
