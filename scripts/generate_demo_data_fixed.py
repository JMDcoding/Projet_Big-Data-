"""
Demo data generator v2 - Fixed version for actual schema
Generates: Lightning strikes, Flights, and Flight Disruptions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
import psycopg2
from config.config import Config

print("=" * 80)
print("DEMO DATA GENERATOR v2 - Lightning, Flights & Disruptions (FIXED)")
print("=" * 80)

try:
    # Connect to database
    print("\n[1] Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    cursor = conn.cursor()
    print("    SUCCESS - Connected")
    
    # Clean up previous demo data
    print("\n[2] Cleaning up previous demo data...")
    try:
        cursor.execute("DELETE FROM flight_disruptions")
        cursor.execute("DELETE FROM flights WHERE source='Demo-Generator-v2-Fixed'")
        cursor.execute("DELETE FROM lightning_strikes WHERE source='Demo-Generator-v2-Fixed'")
        conn.commit()
        print("    SUCCESS - Previous data cleaned")
    except Exception as e:
        print(f"    (cleanup issue: {e})")
        conn.rollback()
    
    # Generate Lightning Data
    print("\n[3] Generating Lightning Strikes...")
    now = datetime.now()
    zones = [
        ("Paris", 48.8527, 2.3510, (40, 75)),
        ("London", 51.5074, -0.1278, (35, 70)),
        ("Berlin", 52.5200, 13.4050, (45, 80)),
        ("Amsterdam", 52.3676, 4.9041, (40, 65)),
        ("Brussels", 50.8503, 4.3517, (45, 75)),
        ("Frankfurt", 50.1109, 8.6821, (50, 85)),
        ("Madrid", 40.4168, -3.7038, (60, 90)),
        ("Milano", 45.4642, 9.1900, (55, 80)),
        ("Barcelona", 41.3851, 2.1734, (65, 85)),
        ("Rome", 41.9028, 12.4964, (70, 90)),
    ]
    
    lightning_data_map = {}
    lightning_count = 0
    
    for zone_idx, (zone_name, lat, lon, intensity_range) in enumerate(zones):
        num_strikes = random.randint(2, 4)
        for strike_idx in range(num_strikes):
            timestamp = now + timedelta(hours=random.uniform(-8, 8))
            intensity = random.uniform(*intensity_range)
            lat_offset = random.uniform(-0.3, 0.3)
            lon_offset = random.uniform(-0.3, 0.3)
            lightning_id = f"{zone_name.lower()}_{zone_idx}_{strike_idx}_{timestamp.strftime('%H%M%S')}"
            
            cursor.execute("""
                INSERT INTO lightning_strikes 
                (lightning_id, latitude, longitude, altitude, intensity, timestamp, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                lightning_id, lat+lat_offset, lon+lon_offset,
                3000+random.randint(0, 5000), intensity,
                timestamp, "Demo-Generator-v2-Fixed"
            ))
            lightning_data_map[lightning_id] = (lat+lat_offset, lon+lon_offset, timestamp)
            lightning_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {lightning_count} lightning strikes created")
    
    # Generate Flight Data
    print("\n[4] Generating Flights...")
    routes = [
        ("AF100", "Paris", "London", 0.5, 1.5),
        ("BA200", "London", "Berlin", 1.0, 2.5),
        ("LH300", "Berlin", "Frankfurt", 0.5, 1.0),
        ("LX400", "Zurich", "Vienna", 1.0, 1.5),
        ("IB500", "Madrid", "Barcelona", 1.5, 2.0),
        ("AZ600", "Milano", "Rome", 1.0, 1.5),
        ("KL700", "Amsterdam", "Paris", 1.0, 1.5),
        ("SN800", "Brussels", "Amsterdam", 0.5, 1.0),
        ("TK900", "Istanbul", "London", 3.0, 4.0),
        ("RYR01", "Dublin", "London", 0.75, 1.25),
        ("UAL02", "London", "New York", 7.0, 8.0),
        ("DAL03", "Paris", "Atlanta", 9.0, 10.5),
        ("AAL04", "Madrid", "Miami", 9.5, 10.5),
        ("EZY05", "Barcelona", "London", 2.0, 2.5),
        ("VIR06", "Amsterdam", "Newark", 7.5, 9.0),
    ]
    
    flight_ids = []
    flight_count = 0
    
    for flight_code, origin, dest, dur_min, dur_max in routes:
        for i in range(1):
            departure = now + timedelta(hours=random.uniform(-12, 12))
            duration = random.uniform(dur_min, dur_max)
            arrival = departure + timedelta(hours=duration)
            status = random.choice(['on_time', 'delayed', 'delayed'])
            cursor.execute("""
                INSERT INTO flights 
                (flight_code, origin, destination, departure, arrival, status, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (flight_code, origin, dest, departure, arrival, status, "Demo-Generator-v2-Fixed"))
            flight_ids.append(flight_code)
            flight_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {flight_count} flights created")
    
    # Generate Flight Disruption Data
    print("\n[5] Generating Flight Disruptions...")
    disruption_count = 0
    
    for i, flight_code in enumerate(flight_ids[:len(flight_ids)]):
        if random.random() < 0.8:
            num_disruptions = random.randint(1, 2)
            for j in range(num_disruptions):
                if i < len(lightning_data_map):
                    lightning_ids = list(lightning_data_map.keys())
                    if lightning_ids:
                        lightning_id = random.choice(lightning_ids)
                        lat, lon, ts = lightning_data_map[lightning_id]
                        
                        cursor.execute("""
                            INSERT INTO flight_disruptions 
                            (flight_code, lightning_id, latitude, longitude, description)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (flight_code, lightning_id, lat, lon, f"Lightning impact zone {j+1}"))
                        disruption_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {disruption_count} flight disruptions created")
    
    # Verify Data
    print("\n[6] VERIFYING DATA...")
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes WHERE source='Demo-Generator-v2-Fixed'")
    ls_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights WHERE source='Demo-Generator-v2-Fixed'")
    f_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions")
    fd_count = cursor.fetchone()[0]
    
    print(f"\n    Lightning strikes: {ls_count} (target: 20+)")
    print(f"    Flights: {f_count} (target: 15+)")
    print(f"    Flight disruptions: {fd_count} (target: 15+)")
    
    if ls_count >= 20 and f_count >= 15 and fd_count >= 15:
        print("\nV ALL TARGETS MET!")
    else:
        print("\n? Some targets not met yet")
    
    conn.close()
    print("\n" + "=" * 80)
    print("Demo Data Generation Complete!")
    print("=" * 80)
    
except Exception as e:
    print(f"\nX ERROR: {e}")
    import traceback
    traceback.print_exc()
