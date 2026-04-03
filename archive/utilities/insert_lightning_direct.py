#!/usr/bin/env python3
"""
Simple direct lightning data insertion from Open-Meteo API.
Insertion directe et simple pour tester.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from datetime import datetime
from config.config import Config
from src.database.warehouse import PostgreSQLConnection

# Connect to database
print("Connecting to PostgreSQL...")
db = PostgreSQLConnection(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)
db.connect()
print(f"✅ Connected to {Config.DB_NAME}")

# Simple European location
location = {
    "name": "Paris",
    "lat": 48.8527,
    "lon": 2.3510
}

print(f"\nFetching weather for {location['name']}...")
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": location['lat'],
    "longitude": location['lon'],
    "daily": "precipitation_sum",
    "timezone": "UTC"
}

response = requests.get(url, params=params)
print(f"API Response: {response.status_code}")

if response.status_code != 200:
    print(f"❌ API Error: {response.text}")
    sys.exit(1)

data = response.json()
daily = data.get("daily", {})
precip_sum = daily.get("precipitation_sum", [])
times = daily.get("time", [])

print(f"Received {len(precip_sum)} days of data")

# Find rainy days
storms = []
for time_str, precip in zip(times, precip_sum):
    if precip and precip > 2.0:  # precipitation > 2mm
        intensity = min(100, 20 + (precip * 4))
        storm = {
            "id": f"Paris_{time_str}",
            "latitude": location['lat'],
            "longitude": location['lon'],
            "altitude": 0,
            "intensity": round(intensity, 1),
            "timestamp": f"{time_str}T12:00:00Z",
            "source": "OpenMeteo-Test",
            "processed_at": datetime.utcnow().isoformat()
        }
        storms.append(storm)
        print(f"  Found storm: {time_str} - {precip}mm - Intensity: {intensity:.1f}")

print(f"\n💾 Total storms to insert: {len(storms)}")

if storms:
    # Direct SQL insert
    cursor = db.connection.cursor()
    insert_query = """
    INSERT INTO lightning_strikes 
    (lightning_id, latitude, longitude, altitude, intensity, timestamp, source, processed_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for storm in storms:
        print(f"Inserting: {storm['id']}")
        try:
            cursor.execute(insert_query, (
                storm['id'],
                storm['latitude'],
                storm['longitude'],
                storm['altitude'],
                storm['intensity'],
                storm['timestamp'],
                storm['source'],
                storm['processed_at']
            ))
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    # Commit all at once
    try:
        db.connection.commit()
        print(f"✅ Committed {len(storms)} records")
    except Exception as e:
        print(f"❌ Commit error: {str(e)}")
        db.connection.rollback()
    
    cursor.close()
    
    # Verify
    verify_cursor = db.connection.cursor()
    verify_cursor.execute("SELECT COUNT(*) FROM lightning_strikes;")
    count = verify_cursor.fetchone()[0]
    print(f"\n✅ Total records in database: {count}")
    
    if count > 0:
        verify_cursor.execute(
            "SELECT latitude, longitude, intensity, timestamp FROM lightning_strikes LIMIT 5;"
        )
        for row in verify_cursor.fetchall():
            print(f"  • Lat: {row[0]:.4f}, Lon: {row[1]:.4f}, Intensity: {row[2]:.1f}, Time: {row[3]}")
    
    verify_cursor.close()

db.disconnect()
print("\n✅ Done")
