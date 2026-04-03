#!/usr/bin/env python3
"""
Insert demo lightning data for testing.
Insertion de données de test pour démonstration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from config.config import Config
from src.database.warehouse import PostgreSQLConnection

print("\n" + "="*80)
print("  INSERTING DEMO LIGHTNING DATA")
print("="*80 + "\n")

# Connect to database
print("📡 Connecting to PostgreSQL...")
db = PostgreSQLConnection(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)
db.connect()
print("✅ Connected\n")

# Create demo storms across European regions
now = datetime.utcnow()

demo_storms = [
    # Paris region - 3 storms
    {"zone": "Paris", "lat": 48.8527, "lon": 2.3510, "hour_offset": 0, "intensity": 65},
    {"zone": "Paris", "lat": 48.7, "lon": 2.5, "hour_offset": 6, "intensity": 45},
    {"zone": "Paris", "lat": 48.9, "lon": 2.2, "hour_offset": 12, "intensity": 55},
    
    # Germany region - 3 storms
    {"zone": "Germany", "lat": 52.5200, "lon": 13.4050, "hour_offset": 2, "intensity": 75},
    {"zone": "Germany", "lat": 52.3, "lon": 13.6, "hour_offset": 8, "intensity": 60},
    {"zone": "Germany", "lat": 52.7, "lon": 13.2, "hour_offset": 14, "intensity": 50},
    
    # Spain region - 3 storms
    {"zone": "Spain", "lat": 40.4168, "lon": -3.7038, "hour_offset": 4, "intensity": 70},
    {"zone": "Spain", "lat": 40.2, "lon": -3.5, "hour_offset": 10, "intensity": 55},
    {"zone": "Spain", "lat": 40.6, "lon": -3.9, "hour_offset": 16, "intensity": 65},
    
    # Italy region - 2 storms
    {"zone": "Italy", "lat": 41.9028, "lon": 12.4964, "hour_offset": 1, "intensity": 80},
    {"zone": "Italy", "lat": 41.5, "lon": 12.2, "hour_offset": 9, "intensity": 70},
    
    # UK region - 2 storms
    {"zone": "UK", "lat": 51.5074, "lon": -0.1278, "hour_offset": 3, "intensity": 48},
    {"zone": "UK", "lat": 51.7, "lon": -0.3, "hour_offset": 11, "intensity": 52},
]

print(f"💾 Inserting {len(demo_storms)} demo lightning strikes...\n")

cursor = db.connection.cursor()
insert_query = """
INSERT INTO lightning_strikes 
(lightning_id, latitude, longitude, altitude, intensity, timestamp, source, processed_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (lightning_id) DO NOTHING
"""

inserted = 0
for i, storm in enumerate(demo_storms, 1):
    timestamp = now + timedelta(hours=storm['hour_offset'])
    lightning_id = f"{storm['zone'].lower()}_{timestamp.strftime('%Y%m%d_%H%M')}"
    
    try:
        cursor.execute(insert_query, (
            lightning_id,
            storm['lat'],
            storm['lon'],
            0,  # altitude not available
            storm['intensity'],
            timestamp.isoformat(),
            "Demo-Test-Data",
            datetime.utcnow().isoformat()
        ))
        inserted += 1
        print(f"  {i:2}. {storm['zone']:12} - Lat: {storm['lat']:8.4f}, Lon: {storm['lon']:9.4f}, "
              f"Intensity: {storm['intensity']:3} - {timestamp.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"  {i:2}. ❌ Error: {str(e)}")

# Commit
try:
    db.connection.commit()
    print(f"\n✅ Successfully inserted {inserted} demo lightning strikes\n")
except Exception as e:
    print(f"\n❌ Commit error: {str(e)}")
    db.connection.rollback()

# Verify
print("📊 Verification:")
verify_cursor = db.connection.cursor()
verify_cursor.execute("SELECT COUNT(*) FROM lightning_strikes;")
total = verify_cursor.fetchone()[0]
print(f"   Total records in database: {total}")

verify_cursor.execute("SELECT COUNT(DISTINCT source) as sources FROM lightning_strikes;")
sources = verify_cursor.fetchone()[0]
print(f"   Data sources: {sources}")

verify_cursor.execute("""
    SELECT source, COUNT(*) as count 
    FROM lightning_strikes 
    GROUP BY source;
""")
print(f"\n   By source:")
for row in verify_cursor.fetchall():
    print(f"     • {row[0]}: {row[1]} records")

verify_cursor.close()
db.disconnect()

print("\n✅ Done! Now run: python app.py")
print("\n" + "="*80 + "\n")
