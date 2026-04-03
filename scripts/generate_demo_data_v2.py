"""
Demo data generator v2 - Complete version
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
print("DEMO DATA GENERATOR v2 - Lightning, Flights & Disruptions")
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
        cursor.execute("DELETE FROM flights WHERE source='Demo-Generator-v2'")
        cursor.execute("DELETE FROM lightning_strikes WHERE source='Demo-Generator-v2'")
        conn.commit()
        print("    SUCCESS - Previous data cleaned")
    except Exception as e:
        print(f"    (cleanup issue: {e})")
        conn.rollback()
    
    # ========================================================================
    # Generate Lightning Data
    # ========================================================================
    print("\n[3] Generating Lightning Strikes...")
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
    
    lightning_ids_map = {}  # Map lightning_id -> database id
    lightning_data_map = {}  # Map lightning_id -> (lat, lon, timestamp)
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
                RETURNING id
            """, (
                lightning_id, lat+lat_offset, lon+lon_offset,
                3000+random.randint(0, 5000), intensity,
                timestamp.isoformat(), "Demo-Generator-v2"
            ))
            db_id = cursor.fetchone()[0]
            lightning_ids_map[lightning_id] = db_id
            lightning_data_map[lightning_id] = (lat+lat_offset, lon+lon_offset, timestamp)
            lightning_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {lightning_count} lightning strikes created")
    
    # ========================================================================
    # Generate Flight Data
    # ========================================================================
    print("\n[4] Generating Flights...")
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
        ("CA1500", "Paris", "Rome", 1.5, 3),
    ]
    
    flights_map = {}  # Map flight_number -> (db_id, dep_time, arr_time)
    flights_count = 0
    
    for flight_num, origin, dest, dep_offset, duration in routes:
        departure_time = now + timedelta(hours=dep_offset)
        arrival_time = departure_time + timedelta(hours=duration)
        
        cursor.execute("""
            INSERT INTO flights 
            (flight_number, departure, arrival, route, departure_time, arrival_time, aircraft_type, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            flight_num, origin, dest, f"{origin}-{dest}",
            departure_time.isoformat(), arrival_time.isoformat(),
            random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380"]),
            "Demo-Generator-v2"
        ))
        db_id = cursor.fetchone()[0]
        flights_map[flight_num] = (db_id, departure_time, arrival_time)
        flights_count += 1
    
    conn.commit()
    print(f"    SUCCESS - {flights_count} flights created")
    
    # ========================================================================
    # Generate Flight Disruptions
    # ========================================================================
    print("\n[5] Calculating Flight Disruptions...")
    
    disruptions_count = 0
    
    # Match flights with lightning based on spatial/temporal proximity
    for flight_num, (flight_id, dep_time, arr_time) in flights_map.items():
        for lightning_id, db_lightning_id in lightning_ids_map.items():
            lat, lon, lightning_time = lightning_data_map[lightning_id]
            
            # Check temporal proximity (within flight window +/- 10 min)
            time_buffer_start = dep_time - timedelta(minutes=10)
            time_buffer_end = arr_time + timedelta(minutes=10)
            
            if time_buffer_start <= lightning_time <= time_buffer_end:
                # Estimate flight path - add variation around lightning location
                flight_lat = lat + random.uniform(-0.5, 0.5)
                flight_lon = lon + random.uniform(-0.5, 0.5)
                
                # Calculate distance (simplified Haversine)
                lat_diff = abs(flight_lat - lat)
                lon_diff = abs(flight_lon - lon)
                distance_km = ((lat_diff**2 + lon_diff**2)**0.5) * 111
                
                # Calculate time difference in minutes
                time_diff = abs((lightning_time - dep_time).total_seconds() / 60)
                
                # Check spatial proximity (< 80 km)
                if distance_km < 80:
                    # Calculate disruption probability
                    distance_risk = 1.0 - (distance_km / 80)
                    time_risk = 1.0 if time_diff < 30 else 0.3
                    disruption_prob = distance_risk * time_risk * 0.85
                    
                    # Risk level based on probability
                    if disruption_prob > 0.70:
                        risk_level = "HIGH"
                    elif disruption_prob > 0.40:
                        risk_level = "MEDIUM"
                    else:
                        risk_level = "LOW"
                    
                    # Insert disruption
                    cursor.execute("""
                        INSERT INTO flight_disruptions 
                        (flight_id, lightning_id, distance_km, time_difference_minutes, risk_level, disruption_probability, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        flight_id, db_lightning_id, round(distance_km, 2),
                        int(time_diff), risk_level, round(disruption_prob, 3),
                        datetime.now().isoformat()
                    ))
                    
                    disruptions_count += 1
    
    conn.commit()
    print(f"    Found {disruptions_count} natural disruptions from proximity matching")
    
    # If we don't have enough disruptions, create additional random ones
    if disruptions_count < 15 and len(flights_map) > 0 and len(lightning_ids_map) > 0:
        additional_needed = 15 - disruptions_count
        print(f"    Creating {additional_needed} additional random disruptions to reach 15+...")
        
        attempts = 0
        max_attempts = 50
        flight_ids_list = list(flights_map.values())
        lightning_ids_list = list(lightning_ids_map.values())
        
        while disruptions_count < 15 and attempts < max_attempts:
            attempts += 1
            flight_id = random.choice(flight_ids_list)[0]
            lightning_id = random.choice(lightning_ids_list)
            
            # Check if combination already exists
            cursor.execute("""
                SELECT id FROM flight_disruptions 
                WHERE flight_id = %s AND lightning_id = %s
            """, (flight_id, lightning_id))
            
            if cursor.fetchone() is None:
                distance_km = random.uniform(10, 75)
                time_diff = random.randint(1, 27)
                risk_levels = ["LOW", "MEDIUM", "HIGH"]
                weights = [2, 3, 5]  # More HIGH risk for realism
                risk_level = random.choices(risk_levels, weights=weights, k=1)[0]
                
                # Probability based on risk level
                prob_map = {"LOW": 0.35, "MEDIUM": 0.65, "HIGH": 0.88}
                disruption_prob = prob_map[risk_level]
                
                cursor.execute("""
                    INSERT INTO flight_disruptions 
                    (flight_id, lightning_id, distance_km, time_difference_minutes, risk_level, disruption_probability, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    flight_id, lightning_id, round(distance_km, 2),
                    time_diff, risk_level, round(disruption_prob, 3),
                    datetime.now().isoformat()
                ))
                
                disruptions_count += 1
                conn.commit()
    
    print(f"    SUCCESS - Total disruptions created: {disruptions_count}")
    
    # ========================================================================
    # Verify final counts
    # ========================================================================
    print("\n[6] Verifying inserted data...")
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes WHERE source='Demo-Generator-v2'")
    final_lightning = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights WHERE source='Demo-Generator-v2'")
    final_flights = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions")
    final_disruptions = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    # Display summary
    print("\n" + "=" * 80)
    print("DEMO DATA GENERATION SUMMARY")
    print("=" * 80)
    print(f"  Lightning Strikes:      {final_lightning:3} records")
    print(f"  Flights:                {final_flights:3} records")
    print(f"  Flight Disruptions:     {final_disruptions:3} records")
    print("=" * 80)
    
    if final_disruptions >= 15:
        print("\n✓ SUCCESS! Generated 15+ disruptions for the dashboard!")
    else:
        print(f"\n⚠ WARNING: Only {final_disruptions} disruptions (target 15+)")
    
    print("\nNext steps:")
    print("  1. Launch dashboard:  streamlit run app.py")
    print("  2. View lightning strikes on the map")
    print("  3. Check flight disruptions in data tables")
    print("  4. Review timeline and statistics\n")

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        try:
            conn.close()
        except:
            pass
    sys.exit(1)
