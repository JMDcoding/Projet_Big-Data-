"""
Fetch real storm/lightning data from weather API (Open-Meteo).

Instead of generating random lightning, we:
  1. Fetch precipitation data from Open-Meteo API
  2. Identify storm areas (high precipitation)
  3. Create "lightning zones" with radius for each storm
  4. Store with intensity proportional to rainfall

Open-Meteo is free, no API key needed: https://open-meteo.com
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import requests
import json

sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import DataWarehouse, PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("fetch_real_lightning")

# European storm zones to monitor
STORM_ZONES = [
    {"name": "Paris", "lat": 48.8527, "lon": 2.3510, "radius_km": 150},
    {"name": "Belgium", "lat": 50.5039, "lon": 4.4699, "radius_km": 120},
    {"name": "Germany", "lat": 52.5200, "lon": 13.4050, "radius_km": 300},
    {"name": "London", "lat": 51.5074, "lon": -0.1278, "radius_km": 150},
    {"name": "Alpine", "lat": 46.8182, "lon": 10.3860, "radius_km": 200},
    {"name": "Italy", "lat": 41.9028, "lon": 12.4964, "radius_km": 250},
    {"name": "Scandinavia", "lat": 59.3293, "lon": 18.0686, "radius_km": 400},
    {"name": "Spain", "lat": 40.4168, "lon": -3.7038, "radius_km": 300},
    {"name": "Switzerland", "lat": 46.9479, "lon": 7.4474, "radius_km": 150},
    {"name": "Netherlands", "lat": 52.3676, "lon": 4.9041, "radius_km": 100},
]


def fetch_weather_data(lat: float, lon: float) -> dict:
    """Fetch weather data from Open-Meteo API.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Weather data including precipitation
    """
    try:
        # Open-Meteo free API endpoint
        url = "https://api.open-meteo.com/v1/forecast"
        
        # Get data for next 7 days
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation",  # Get hourly precipitation
            "daily": "precipitation_sum",  # Daily total precipitation
            "timezone": "UTC"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    except Exception as e:
        logger.warning(f"   Failed to fetch weather for ({lat}, {lon}): {str(e)}")
        return None


def identify_storms(zone: dict, weather_data: dict) -> list:
    """Identify storm events from weather data.
    
    Args:
        zone: Zone info (name, lat, lon, radius)
        weather_data: Data from Open-Meteo
        
    Returns:
        List of storm events detected
    """
    storms = []
    
    if not weather_data:
        return storms
    
    try:
        daily = weather_data.get("daily", {})
        precip_sum = daily.get("precipitation_sum", [])
        times = daily.get("time", [])
        
        # Define storm threshold (precipitation > 2mm is notable)
        STORM_THRESHOLD = 2.0
        
        for i, (time_str, precip) in enumerate(zip(times, precip_sum)):
            if precip is None:
                continue
            
            # If significant precipitation, it's a storm
            if precip > STORM_THRESHOLD:
                # Normalize precipitation to intensity (0-100)
                # Low rain (2-5mm) = low intensity (20-40)
                # Medium rain (5-20mm) = medium intensity (40-70)
                # High rain (>20mm) = high intensity (70-100)
                intensity = min(100, 20 + (precip * 4))
                
                storm = {
                    "zone_name": zone["name"],
                    "latitude": zone["lat"],
                    "longitude": zone["lon"],
                    "radius_km": zone["radius_km"],
                    "timestamp": time_str,
                    "precipitation_mm": round(precip, 2),
                    "intensity": round(intensity, 1),
                    "source": "Open-Meteo-Weather-API"
                }
                storms.append(storm)
        
        return storms
    
    except Exception as e:
        logger.warning(f"   Error identifying storms: {str(e)}")
        return []


def clear_lightning_table(warehouse: DataWarehouse) -> bool:
    """Delete all lightning from database.
    
    Args:
        warehouse: DataWarehouse instance
        
    Returns:
        True if successful
    """
    try:
        logger.info("🧹 Clearing lightning disruptions first...")
        query_disruptions = "DELETE FROM flight_disruptions;"
        try:
            warehouse.db.execute(query_disruptions)
            logger.info("✅ Disruptions cleared")
        except Exception as e:
            # Table might not exist if this is first run after reset
            if "does not exist" in str(e).lower() or "n'existe pas" in str(e).lower():
                logger.info("   ℹ️  flight_disruptions table doesn't exist (normal after reset)")
            else:
                logger.warning(f"   ⚠️  Could not clear disruptions: {str(e)}")
        
        logger.info("🧹 Clearing lightning strikes table...")
        query_lightning = "DELETE FROM lightning_strikes;"
        warehouse.db.execute(query_lightning)
        
        # Verify
        count_query = "SELECT COUNT(*) FROM lightning_strikes;"
        result = warehouse.db.execute(count_query)
        count = result[0][0] if result else 0
        
        logger.info(f"✅ Lightning table cleared. Remaining: {count}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error clearing lightning table: {str(e)}")
        return False


def insert_lightning_to_database(warehouse: DataWarehouse, storms: list) -> int:
    """Insert storm/lightning data into database.
    
    Args:
        warehouse: DataWarehouse instance
        storms: List of storm events
        
    Returns:
        Number of storms inserted
    """
    logger.info("💾 Inserting lightning strikes into database...")
    
    if not storms:
        logger.warning("   No storms to insert")
        return 0
    
    try:
        records = []
        for storm in storms:
            record = {
                "id": f"{storm['zone_name']}_{storm['timestamp']}",
                "latitude": storm["latitude"],
                "longitude": storm["longitude"],
                "altitude": 0,  # Not available from weather API
                "signal": storm["intensity"],
                "timestamp": f"{storm['timestamp']}T12:00:00Z",  # Midday
                "source": storm["source"],
                "processed_at": datetime.utcnow().isoformat()
            }
            records.append(record)
        
        warehouse.insert_lightning_data(records)
        
        # Verify insertion
        count_query = "SELECT COUNT(*) FROM lightning_strikes;"
        result = warehouse.db.execute(count_query)
        count = result[0][0] if result else 0
        
        logger.info(f"✅ {count} total lightning strikes in database")
        return count
    
    except Exception as e:
        logger.error(f"❌ Error inserting lightning: {str(e)}")
        return 0


def show_sample_storms(warehouse: DataWarehouse, limit: int = 15):
    """Display sample of inserted storms.
    
    Args:
        warehouse: DataWarehouse instance
        limit: Number to display
    """
    logger.info(f"\n⚡ Sample of {limit} storm zones detected:")
    logger.info("-" * 120)
    
    try:
        query = f"""
        SELECT latitude, longitude, intensity, timestamp, source 
        FROM lightning_strikes 
        ORDER BY intensity DESC
        LIMIT {limit};
        """
        results = warehouse.db.execute(query)
        
        if results:
            for i, strike in enumerate(results, 1):
                logger.info(f"{i:2}. Lat: {strike[0]:8.4f} | Lon: {strike[1]:8.4f} | "
                           f"Intensity: {strike[2]:5.1f} | Time: {strike[3]} | {strike[4]}")
        else:
            logger.info("   No storms found")
    
    except Exception as e:
        logger.error(f"Error displaying sample: {str(e)}")


def main():
    """Main execution flow."""
    print("\n" + "="*130)
    print("  FETCH REAL STORM/LIGHTNING DATA FROM WEATHER API")
    print("="*130)
    
    # Connect to database
    logger.info("📡 Connecting to PostgreSQL...")
    try:
        db_conn = PostgreSQLConnection(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        db_conn.connect()
        warehouse = DataWarehouse(db_conn)
        logger.info("✅ Connected to database")
    
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {str(e)}")
        return False
    
    try:
        # Step 1: Clear existing lightning
        if not clear_lightning_table(warehouse):
            return False
        
        # Step 2: Fetch storms from all zones
        logger.info(f"\n⛈️  Fetching weather data from {len(STORM_ZONES)} European zones...")
        logger.info("-" * 130)
        
        all_storms = []
        
        for zone in STORM_ZONES:
            logger.info(f"📍 {zone['name']:15} ({zone['lat']:8.4f}, {zone['lon']:8.4f})")
            
            # Fetch weather data
            weather = fetch_weather_data(zone["lat"], zone["lon"])
            
            if weather:
                # Identify storms
                storms = identify_storms(zone, weather)
                all_storms.extend(storms)
                
                logger.info(f"   ✓ Found {len(storms)} storm events")
            else:
                logger.info(f"   ⚠️  Could not fetch weather data")
        
        if not all_storms:
            logger.warning("\n⚠️  No storms detected in any zone")
            logger.info("   This might mean:")
            logger.info("   • No significant precipitation in forecast")
            logger.info("   • Weather API temporarily unavailable")
            warehouse.db.disconnect()
            return False
        
        logger.info(f"\n✅ Detected {len(all_storms)} storm events total")
        
        # Step 3: Insert into database
        inserted_count = insert_lightning_to_database(warehouse, all_storms)
        
        if inserted_count == 0:
            logger.error("❌ No storms were inserted")
            warehouse.db.disconnect()
            return False
        
        # Step 4: Show sample
        show_sample_storms(warehouse)
        
        # Success summary
        logger.info("\n" + "="*130)
        logger.info("✅ STORM/LIGHTNING DATA FETCH COMPLETED")
        logger.info("="*130)
        logger.info(f"Total storm zones inserted: {inserted_count}")
        logger.info(f"Data source: Open-Meteo Free Weather API")
        logger.info(f"Coverage: 10 European regions (7-day forecast)")
        logger.info(f"\nData characteristics:")
        logger.info(f"  • Radius: Zone-specific (100-400 km)")
        logger.info(f"  • Intensity: Proportional to precipitation (0-100)")
        logger.info(f"  • Timestamp: Real forecast data")
        logger.info(f"\nNext steps:")
        logger.info(f"  1. Fetch real flights: python fetch_airlabs_flights.py")
        logger.info(f"       (requires AIRLABS_API_KEY environment variable)")
        logger.info(f"  2. OR use OpenSky flights: python fetch_real_flights.py")
        logger.info(f"  3. Analyze perturbations: python app.py")
        logger.info("="*130 + "\n")
        
        warehouse.db.disconnect()
        return True
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        warehouse.db.disconnect()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
