"""
Generate complete demo dataset with lightning strikes, flights, and disruptions.
Génère un ensemble de données démo complet avec éclairs, vols et perturbations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
import logging
from config.config import Config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse
from src.utils.logger import setup_logging
from src.transformation.disruption_calculator import DisruptionCalculator

logger = setup_logging("generate_demo_complete")

print("\n" + "="*90)
print("  COMPLETE DEMO DATA GENERATOR - Lightning, Flights & Disruptions")
print("="*90 + "\n")

# ============================================================================
# CONFIGURATION
# ============================================================================

DEMO_ZONES = [
    # (name, latitude, longitude, intensity_range)
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

DEMO_ROUTES = [
    # (flight_number, origin, destination, departure_offset_hours, duration_hours)
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

# ============================================================================
# MAIN SCRIPT
# ============================================================================

try:
    # ========================================================================
    # Step 1: Connect to Database
    # ========================================================================
    logger.info("Step 1️⃣: Connecting to PostgreSQL...")
    db_conn = PostgreSQLConnection(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    db_conn.connect()
    warehouse = DataWarehouse(db_conn)
    logger.info("✅ Connected to database\n")
    
    # ========================================================================
    # Step 2: Generate Lightning Data
    # ========================================================================
    logger.info("Step 2️⃣: Generating lightning strike data...")
    now = datetime.utcnow()
    lightning_data = []
    cursor = db_conn.connection.cursor()
    
    # Generate multiple lightning strikes in each zone
    for zone_idx, (zone_name, lat, lon, intensity_range) in enumerate(DEMO_ZONES):
        # Generate 1-3 lightning strikes per zone
        num_strikes = random.randint(1, 3)
        for strike_idx in range(num_strikes):
            timestamp = now + timedelta(hours=random.uniform(0, 8))
            intensity = random.uniform(*intensity_range)
            
            # Add some randomness to exact location within zone
            lat_offset = random.uniform(-0.3, 0.3)  # ~30km variation
            lon_offset = random.uniform(-0.3, 0.3)
            
            lightning_id = f"{zone_name.lower()}_{zone_idx}_{strike_idx}_{timestamp.strftime('%H%M%S')}"
            
            insert_query = """
            INSERT INTO lightning_strikes 
            (lightning_id, latitude, longitude, altitude, intensity, timestamp, source, processed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (lightning_id) DO NOTHING
            """
            
            cursor.execute(insert_query, (
                lightning_id,
                lat + lat_offset,
                lon + lon_offset,
                3000 + random.randint(0, 5000),  # Altitude 3-8km
                intensity,
                timestamp.isoformat(),
                "Demo-Generator",
                datetime.utcnow().isoformat()
            ))
            
            lightning_data.append({
                "lightning_id": lightning_id,
                "latitude": lat + lat_offset,
                "longitude": lon + lon_offset,
                "intensity": intensity,
                "timestamp": timestamp.isoformat(),
                "zone": zone_name
            })
            
            print(f"  ⚡ {zone_name:12} - Intensity: {intensity:5.1f}% - Time: {timestamp.strftime('%H:%M')}")
    
    db_conn.connection.commit()
    logger.info(f"✅ Generated {len(lightning_data)} lightning strikes\n")
    
    # ========================================================================
    # Step 3: Generate Flight Data
    # ========================================================================
    logger.info("Step 3️⃣: Generating flight data...")
    flights_data = []
    
    # Create zones lookup
    zones_lookup = {name: (lat, lon) for name, lat, lon, _ in DEMO_ZONES}
    
    for route_idx, (flight_num, origin, dest, dep_offset, duration) in enumerate(DEMO_ROUTES):
        origin_lat, origin_lon = zones_lookup[origin]
        dest_lat, dest_lon = zones_lookup[dest]
        
        departure_time = now + timedelta(hours=dep_offset)
        arrival_time = departure_time + timedelta(hours=duration)
        
        # Generate intermediate position (simplified - could use interpolation)
        mid_lat = (origin_lat + dest_lat) / 2 + random.uniform(-0.2, 0.2)
        mid_lon = (origin_lon + dest_lon) / 2 + random.uniform(-0.2, 0.2)
        
        route_str = f"{origin}-{dest}"
        
        # Use correct schema: flight_number, departure, arrival, route, departure_time, arrival_time, aircraft_type, source
        insert_query = """
        INSERT INTO flights 
        (flight_number, departure, arrival, route, 
         departure_time, arrival_time, aircraft_type, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """
        
        cursor.execute(insert_query, (
            flight_num,
            origin,
            dest,
            route_str,
            departure_time.isoformat(),
            arrival_time.isoformat(),
            random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A380"]),
            "Demo-Generator"
        ))
        
        flights_data.append({
            "flight_number": flight_num,
            "departure": origin,
            "arrival": dest,
            "route": route_str,
            "latitude": mid_lat,
            "longitude": mid_lon,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat()
        })
        
        print(f"  ✈️  {flight_num:8} - {origin:12} → {dest:12} - {departure_time.strftime('%H:%M')} - {arrival_time.strftime('%H:%M')}")
    
    db_conn.connection.commit()
    logger.info(f"✅ Generated {len(flights_data)} flights\n")
    
    # ========================================================================
    # Step 4: Calculate Disruptions (Based on proximity)
    # ========================================================================
    logger.info("Step 4️⃣: Calculating flight disruptions...")
    
    disruptions = []
    
    # For each flight, find nearby lightning strikes and create disruptions
    for flight in flights_data:
        flight_lat = flight["latitude"]
        flight_lon = flight["longitude"]
        dep_time = datetime.fromisoformat(flight["departure_time"])
        arr_time = datetime.fromisoformat(flight["arrival_time"])
        
        # Find lightning strikes near this flight path
        for lightning in lightning_data:
            l_lat = lightning["latitude"]
            l_lon = lightning["longitude"]
            l_time = datetime.fromisoformat(lightning["timestamp"])
            
            # Calculate distance (simplified Haversine)
            lat_diff = abs(flight_lat - l_lat)
            lon_diff = abs(flight_lon - l_lon)
            distance = (lat_diff**2 + lon_diff**2) ** 0.5 * 111  # Convert to km (~111 km per degree)
            
            # Check if lightning is near flight path and during flight time
            time_window = 30  # minutes
            time_diff = abs((l_time - dep_time).total_seconds() / 60)  # minutes
            
            if distance < 80 and time_diff < time_window:  # Within 80km and 30 minutes
                disruption = {
                    "flight_number": flight["flight_number"],
                    "disruption_type": random.choice(["ROUTE_DEVIATION", "DELAY", "ALTITUDE_CHANGE", "SPEED_REDUCTION"]),
                    "impact_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                    "lightning_id": lightning["lightning_id"],
                    "risk_probability": max(0.5, 1.0 - (distance / 100)),  # Higher risk closer to lightning
                    "estimated_delay_minutes": int(random.uniform(5, 60 * (1.0 - distance/100))),
                    "affected_aircraft_count": 1,
                    "timestamp": l_time.isoformat(),
                    "processed_at": datetime.utcnow().isoformat()
                }
                disruptions.append(disruption)
    
    logger.info(f"✅ Calculated {len(disruptions)} natural disruptions")
    
    # If not enough disruptions, add more by connecting random flights to random lightning
    if len(disruptions) < 15:
        logger.info(f"⚠️  Only {len(disruptions)} disruptions found. Generating additional ones...")
        
        additional_needed = 15 - len(disruptions)
        for i in range(additional_needed):
            lightning = random.choice(lightning_data)
            flight = random.choice(flights_data)
            
            disruption = {
                "flight_number": flight["flight_number"],
                "disruption_type": random.choice(["ROUTE_DEVIATION", "DELAY", "ALTITUDE_CHANGE", "SPEED_REDUCTION"]),
                "impact_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "lightning_id": lightning["lightning_id"],
                "risk_probability": random.uniform(0.5, 1.0),
                "estimated_delay_minutes": random.randint(5, 100),
                "affected_aircraft_count": 1,
                "timestamp": datetime.utcnow().isoformat(),
                "processed_at": datetime.utcnow().isoformat()
            }
            disruptions.append(disruption)
        
        logger.info(f"✅ Added {additional_needed} generated disruptions")
    
    logger.info(f"✅ Total disruptions available: {len(disruptions)}\n")
    
    # ========================================================================
    # Step 5: Insert Disruptions
    # ========================================================================
    logger.info("Step 5️⃣: Inserting disruption records...")
    
    insert_disruption_query = """
    INSERT INTO flight_disruptions 
    (flight_number, disruption_type, impact_level, lightning_id, 
     risk_probability, estimated_delay_minutes, affected_aircraft_count,
     timestamp, processed_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (flight_number, lightning_id) DO NOTHING
    """
    
    for idx, disruption in enumerate(disruptions, 1):
        try:
            cursor.execute(insert_disruption_query, (
                disruption.get("flight_number", f"DEMO{idx}"),
                disruption.get("disruption_type", "DELAY"),
                disruption.get("impact_level", "MEDIUM"),
                disruption.get("lightning_id", f"AUTO_{idx}"),
                disruption.get("risk_probability", 0.75),
                disruption.get("estimated_delay_minutes", 30),
                disruption.get("affected_aircraft_count", 1),
                disruption.get("timestamp", datetime.utcnow().isoformat()),
                disruption.get("processed_at", datetime.utcnow().isoformat())
            ))
        except Exception as e:
            logger.warning(f"  ⚠️  Could not insert disruption {idx}: {str(e)}")
    
    db_conn.connection.commit()
    cursor.close()
    logger.info(f"✅ Inserted {len(disruptions)} disruptions into database\n")
    
    # ========================================================================
    # Step 6: Verification
    # ========================================================================
    logger.info("Step 6️⃣: Verifying data...")
    
    # Count records
    verify_cursor = db_conn.connection.cursor()
    
    verify_cursor.execute("SELECT COUNT(*) as count FROM lightning_strikes")
    lightning_count = verify_cursor.fetchone()[0]
    
    verify_cursor.execute("SELECT COUNT(*) as count FROM flights")
    flights_count = verify_cursor.fetchone()[0]
    
    verify_cursor.execute("SELECT COUNT(*) as count FROM flight_disruptions")
    disruptions_count = verify_cursor.fetchone()[0]
    
    verify_cursor.close()
    
    print("\n" + "="*90)
    print("  📊 DATA SUMMARY")
    print("="*90)
    print(f"  ⚡ Lightning Strikes:      {lightning_count:3} records")
    print(f"  ✈️  Flights:                {flights_count:3} records")
    print(f"  ⚠️  Flight Disruptions:     {disruptions_count:3} records")
    print("="*90 + "\n")
    
    if disruptions_count >= 15:
        print("  ✅ SUCCESS! Generated 15+ disruptions for demo")
    else:
        print(f"  ⚠️  WARNING: Only generated {disruptions_count} disruptions (target: 15+)")
    
    logger.info("📚 Next steps:")
    logger.info("   1. Launch dashboard: streamlit run app.py")
    logger.info("   2. View lightning strikes on map")
    logger.info("   3. See flight disruptions in data")
    logger.info("   4. Check timeline and statistics")
    
    db_conn.disconnect()
    print("\n✅ Demo data generation complete!\n")

except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
