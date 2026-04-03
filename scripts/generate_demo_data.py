"""
Demo data generator - Simple version
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
print("DEMO DATA GENERATOR - Lightning, Flights & Disruptions")
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
    
    # Try to initialize schema
    print("\n[2] Ensuring schema...")
    try:
        cursor.execute("DELETE FROM flight_disruptions")
        cursor.execute("DELETE FROM flights WHERE source='Demo-Generator'")
        cursor.execute("DELETE FROM lightning_strikes WHERE source='Demo-Generator'")
        conn.commit()
        print("    Schema OK")
    except:
        print("    (schema may need creation - will try anyway)")
    
    # ========================================================================
    # Generate Lightning Data
    # ========================================================================
    print("\n[3] Generating Lightning...")
    now = datetime.utcnow()
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
    
    lightning_count = 0
    for zone_idx, (zone_name, lat, lon, intensity_range) in enumerate(zones):
        num_strikes = random.randint(1, 3)
        for strike_idx in range(num_strikes):
            timestamp = now + timedelta(hours=random.uniform(0, 8))
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
                timestamp.isoformat(), "Demo-Generator"
            ))
            lightning_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {lightning_count} lightning strikes")
    
    # ========================================================================
    # Generate Flight Data
    # ========================================================================
    print("\n[4] Generating Flights...")
    zones_lookup = {name: (lat, lon) for name, lat, lon, _ in zones}
    routes = [
        ("AF100", "Paris", "London", 0, 1.5),
        ("BA200", "London", "Berlin", 1, 2.5),
        ("LH300", "Berlin", "Frankfurt", 2, 1),
        ("KL400", "Amsterdam", "Brussels", 3, 1),
        ("SN500", "Brussels", "Madrid", 4, 3),
        ("IB600", "Madrid", "Barcelona", 5, 2),
        ("AZ700", "Milano", "Rome", 6, 1.5),
        ("VY800", "Barcelona", "Milano", 1, 2.5),
        ("AF900", "Paris", "Amsterdam", 2, 1.5),
        ("BA1000", "London", "Frankfurt", 3, 2),
        ("LH1100", "Frankfurt", "Barcelona", 4, 3),
        ("KL1200", "Amsterdam", "Paris", 5, 1.5),
        ("EK1300", "Berlin", "Madrid", 6, 4),
        ("UA1400", "London", "Barcelona", 0.5, 3.5),
        ("CA1500", "Paris", "Roma", 1.5, 3),
    ]
    
    flights_count = 0
    for flight_num, origin, dest, dep_offset, duration in routes:
        departure_time = now + timedelta(hours=dep_offset)
        arrival_time = departure_time + timedelta(hours=duration)
        
        cursor.execute("""
            INSERT INTO flights 
            (flight_number, departure, arrival, route, departure_time, arrival_time, aircraft_type, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            flight_num, origin, dest, f"{origin}-{dest}",
            departure_time.isoformat(), arrival_time.isoformat(),
            random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380"]),
            "Demo-Generator"
        ))
        flights_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {flights_count} flights")
    
    # ========================================================================
    # Generate Disruptions
    # ========================================================================
    print("\n[5] Generating Flight Disruptions...")
    disruptions = []
    
    # Find natural disruptions (flights near lightning)
    for flight_num, flight_data in flights_map.items():
        flight_lat = flight_data["latitude"]
        flight_lon = flight_data["longitude"]
        dep_time = flight_data["departure_time"]
        flight_id = flight_data["id"]
        
        for lightning_id, db_lightning_id in lightning_ids_map.items():
            # Find that lightning's location from DB
            cursor.execute("SELECT latitude, longitude, timestamp FROM lightning_strikes WHERE id = %s", (db_lightning_id,))
            result = cursor.fetchone()
            if result:
                l_lat, l_lon, l_time = result
                
                # Simple distance calculation
                lat_diff = abs(flight_lat - l_lat)
                lon_diff = abs(flight_lon - l_lon)
                distance = (lat_diff**2 + lon_diff**2) ** 0.5 * 111  # km
                
                # Check time window
                time_diff = abs((l_time - dep_time).total_seconds() / 60)  # minutes
                
                if distance < 80 and time_diff < 30:  # Within 80km and 30 minutes
                    disruptions.append({
                        "flight_id": flight_id,
                        "lightning_id": db_lightning_id,
                        "distance_km": distance,
                        "time_difference_minutes": int(time_diff),
                        "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                        "disruption_probability": max(0.5, 1.0 - (distance / 100))
                    })
    
    print(f"    Found {len(disruptions)} natural disruptions")
    
    # Add more if needed to reach 15
    if len(disruptions) < 15:
        additional = 15 - len(disruptions)
        print(f"    Generating {additional} additional disruptions...")
        for _ in range(additional):
            f_id = random.choice(list(flights_map.values()))["id"]
            l_id = random.choice(list(lightning_ids_map.values()))
            
            disruptions.append({
                "flight_id": f_id,
                "lightning_id": l_id,
                "distance_km": random.uniform(20, 80),
                "time_difference_minutes": random.randint(5, 30),
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "disruption_probability": random.uniform(0.5, 1.0)
            })
    
    # Insert disruptions
    insert_disruption = """
    INSERT INTO flight_disruptions 
    (flight_id, lightning_id, distance_km, time_difference_minutes, risk_level, disruption_probability)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for disruption in disruptions:
        cursor.execute(insert_disruption, (
            disruption["flight_id"],
            disruption["lightning_id"],
            disruption["distance_km"],
            disruption["time_difference_minutes"],
            disruption["risk_level"],
            disruption["disruption_probability"]
        ))
    
    conn.commit()
    print(f"    SUCCESS - Generated {len(disruptions)} disruptions")
    
    # ========================================================================
    # Verify counts
    # ========================================================================
    print("\n[6] Verifying inserted data...")
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes WHERE source='Demo-Generator'")
    lightning_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights WHERE source='Demo-Generator'")
    flights_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions")
    disruptions_count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Display summary
    print("\n" + "=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    print(f"  Lightning Strikes:      {lightning_count:3} records")
    print(f"  Flights:                {flights_count:3} records")
    print(f"  Flight Disruptions:     {disruptions_count:3} records")
    print("=" * 80)
    
    if disruptions_count >= 15:
        print("\nSUCCESS! Generated 15+ disruptions for the demo!")
    else:
        print(f"\nWARNING: Only {disruptions_count} disruptions (target 15+)")
    
    print("\nNext steps:")
    print("  1. Launch dashboard: streamlit run app.py")
    print("  2. View lightning strikes on the map")
    print("  3. See flight disruptions in data")
    print("  4. Check timeline and statistics\n")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
