"""
Simple demo data generator - Lightning, Flights and Disruptions
Adapted to match actual database schema.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
import psycopg2
from config.config import Config

print("=" * 80)
print("DEMO DATA GENERATOR - Lightning Strikes, Flights & Disruptions")
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
    
    # Generate Lightning Data
    print("\n[2] Generating Lightning Strike Data...")
    now = datetime.utcnow()
    zones = [
        ("Paris", 48.8527, 2.3510, (40, 75)),
        ("London", 51.5074, -0.1278, (35, 70)),
        ("Berlin", 52.5200, 13.4050, (45, 80)),
        ("Amsterdam", 52.3676, 4.9041, (40, 65)),
        ("Brussels", 50.8503, 4.3517, (45, 75)),
    ]
    
    lightning_data = []
    insert_lightning = """
    INSERT INTO lightning_strikes 
    (lightning_id, latitude, longitude, altitude, intensity, timestamp)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (lightning_id) DO NOTHING
    """
    
    for zone_idx, (zone_name, lat, lon, intensity_range) in enumerate(zones):
        num_strikes = random.randint(2, 4)
        for strike_idx in range(num_strikes):
            timestamp = now + timedelta(hours=random.uniform(0, 8))
            intensity = random.uniform(*intensity_range)
            
            lat_offset = random.uniform(-0.3, 0.3)
            lon_offset = random.uniform(-0.3, 0.3)
            
            lightning_id = f"demo_{zone_name.lower()}_{zone_idx}_{strike_idx}"
            
            cursor.execute(insert_lightning, (
                lightning_id,
                lat + lat_offset,
                lon + lon_offset,
                3000 + random.randint(0, 5000),
                intensity,
                timestamp.isoformat()
            ))
            
            lightning_data.append({
                "lightning_id": lightning_id,
                "latitude": lat + lat_offset,
                "longitude": lon + lon_offset,
                "intensity": intensity,
                "timestamp": timestamp.isoformat(),
                "zone": zone_name
            })
            
            print(f"    Lightning in {zone_name:12} - Intensity: {intensity:5.1f}%")
    
    conn.commit()
    print(f"    SUCCESS - Generated {len(lightning_data)} lightning strikes")
    
    # Generate Flight Data
    print("\n[3] Generating Flight Data...")
    flights_data = []
    origins = ["Paris-CDG", "London-LHR", "Berlin-TXL", "Amsterdam-AMS"]
    destinations = ["Madrid-MAD", "Milano-MXP", "Barcelona-BCN", "Frankfurt-FRA"]
    
    insert_flight = """
    INSERT INTO flights 
    (flight_id, origin, destination, latitude, longitude, departure_time, arrival_time)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (flight_id) DO NOTHING
    """
    
    for i in range(10):
        origin = random.choice(origins)
        dest = random.choice(destinations)
        flight_id = f"demo_FL{1000+i}"
        
        departure_time = now + timedelta(hours=random.uniform(0, 12))
        arrival_time = departure_time + timedelta(hours=random.uniform(1, 4))
        
        mid_lat = (50.0 + random.uniform(-5, 5))
        mid_lon = (5.0 + random.uniform(-5, 5))
        
        cursor.execute(insert_flight, (
            flight_id,
            origin,
            dest,
            mid_lat,
            mid_lon,
            departure_time.isoformat(),
            arrival_time.isoformat()
        ))
        
        flights_data.append({
            "flight_id": flight_id,
            "departure": origin,
            "arrival": dest,
            "latitude": mid_lat,
            "longitude": mid_lon,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat()
        })
        
        print(f"    Flight {flight_id:12} - {origin:12} to {dest:12}")
    
    conn.commit()
    print(f"    SUCCESS - Generated {len(flights_data)} flights")
    
    # Generate Disruptions
    print("\n[4] Generating Flight Disruptions...")
    disruptions = []
    
    # Find natural disruptions (flights near lightning)
    for flight in flights_data:
        flight_lat = flight["latitude"]
        flight_lon = flight["longitude"]
        dep_time = datetime.fromisoformat(flight["departure_time"])
        
        for lightning in lightning_data:
            l_lat = lightning["latitude"]
            l_lon = lightning["longitude"]
            l_time = datetime.fromisoformat(lightning["timestamp"])
            
            # Simple distance calculation
            lat_diff = abs(flight_lat - l_lat)
            lon_diff = abs(flight_lon - l_lon)
            distance = (lat_diff**2 + lon_diff**2) ** 0.5 * 111  # km
            
            # Check time window
            time_diff = abs((l_time - dep_time).total_seconds() / 60)  # minutes
            
            if distance < 80 and time_diff < 30:  # Within 80km and 30 minutes
                disruptions.append({
                    "flight_id": flight["flight_id"],
                    "lightning_id": lightning["lightning_id"],
                    "distance_km": distance,
                    "time_difference_minutes": int(time_diff),
                    "risk_level": "HIGH" if distance < 50 else "MEDIUM",
                    "disruption_probability": max(0.5, 1.0 - (distance / 100))
                })
    
    print(f"    Found {len(disruptions)} natural disruptions")
    
    # Add more if needed to reach minimum
    if len(disruptions) < 5:
        additional = 5 - len(disruptions)
        print(f"    Generating {additional} additional disruptions...")
        for _ in range(additional):
            disruptions.append({
                "flight_id": random.choice(flights_data)["flight_id"],
                "lightning_id": random.choice(lightning_data)["lightning_id"],
                "distance_km": random.uniform(10, 100),
                "time_difference_minutes": random.randint(5, 30),
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "disruption_probability": random.uniform(0.3, 0.9)
            })
    
    # Insert disruptions
    insert_disruption = """
    INSERT INTO flight_disruptions 
    (flight_id, lightning_id, distance_km, time_difference_minutes, risk_level, disruption_probability, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    for disruption in disruptions:
        cursor.execute(insert_disruption, (
            disruption["flight_id"],
            disruption["lightning_id"],
            disruption["distance_km"],
            disruption["time_difference_minutes"],
            disruption["risk_level"],
            disruption["disruption_probability"],
            datetime.utcnow().isoformat()
        ))
    
    conn.commit()
    print(f"    SUCCESS - Generated {len(disruptions)} disruptions")
    
    # Verify counts
    print("\n[5] Verifying inserted data...")
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes")
    lightning_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    flights_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions")
    disruptions_count = cursor.fetchone()[0]
    
    print(f"    Lightning strikes count: {lightning_count}")
    print(f"    Flights count: {flights_count}")
    print(f"    Flight disruptions count: {disruptions_count}")
    
    # Final status
    print("\n[6] FINAL STATUS")
    if lightning_count > 0 and flights_count > 0 and disruptions_count > 0:
        print("    SUCCESS - All demo data generated successfully!")
    else:
        print("    WARNING - Some data counts are zero")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
