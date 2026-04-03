"""
Fetch real flights from Airlabs API with REAL departure/arrival times.

Airlabs provides:
  - Actual airport codes
  - Real departure times
  - Real arrival times  
  - Aircraft information

Free tier: 500 flights/month (sufficient for demo)
Setup: Get API key from https://airlabs.co
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import time

sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import DataWarehouse, PostgreSQLConnection
from src.ingestion.flight_routing_api import AirlabsFlightAPI
from src.utils.logger import setup_logging

logger = setup_logging("fetch_airlabs_flights")


def verify_airlabs_key() -> str:
    """Verify Airlabs API key is available.
    
    Returns:
        API key if available
        
    Raises:
        ValueError: If API key not found
    """
    api_key = os.getenv("AIRLABS_API_KEY")
    
    if not api_key:
        logger.error("❌ AIRLABS_API_KEY environment variable not set")
        logger.info("\nTo get a free API key:")
        logger.info("  1. Visit: https://airlabs.co")
        logger.info("  2. Sign up with email")
        logger.info("  3. Copy API key from dashboard")
        logger.info("  4. Run: export AIRLABS_API_KEY='your_key'")
        raise ValueError("AIRLABS_API_KEY not configured")
    
    logger.info("✅ Airlabs API key found")
    return api_key


def clear_flights_table(warehouse: DataWarehouse) -> bool:
    """Delete all flights from database (and dependent disruptions).
    
    Args:
        warehouse: DataWarehouse instance
        
    Returns:
        True if successful
    """
    try:
        logger.info("🧹 Clearing flight disruptions first...")
        query_disruptions = "DELETE FROM flight_disruptions;"
        warehouse.db.execute(query_disruptions)
        logger.info("✅ Flight disruptions cleared")
        
        logger.info("🧹 Clearing flights table...")
        query_flights = "DELETE FROM flights;"
        warehouse.db.execute(query_flights)
        
        # Verify
        count_query = "SELECT COUNT(*) FROM flights;"
        result = warehouse.db.execute(count_query)
        count = result[0][0] if result else 0
        
        logger.info(f"✅ Flights table cleared. Remaining: {count}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error clearing flights table: {str(e)}")
        return False


def fetch_flights_from_airlabs(
    api_key: str,
    lat: float = 48.8527,
    lon: float = 2.3510,
    radius_km: int = 400,
    max_attempts: int = 5
) -> list:
    """Fetch real flights from Airlabs API.
    
    Args:
        api_key: Airlabs API key
        lat: Center latitude (default: Paris)
        lon: Center longitude (default: Paris)
        radius_km: Search radius in km
        max_attempts: Number of retry attempts
        
    Returns:
        List of flights with REAL departure/arrival times
    """
    logger.info(f"🛫 Fetching flights from Airlabs API...")
    logger.info(f"   Center: ({lat:.4f}, {lon:.4f}), Radius: {radius_km}km")
    logger.info(f"   (Real times from actual flight schedules)")
    
    all_flights = []
    
    # Try multiple times to get enough flights
    for attempt in range(max_attempts):
        try:
            api = AirlabsFlightAPI(api_key=api_key, lat=lat, lon=lon, radius_km=radius_km)
            result = api.fetch()
            flights = result.get("flights", [])
            api.close()
            
            if flights:
                logger.info(f"   Attempt {attempt+1}: Got {len(flights)} flights")
                all_flights.extend(flights)
                
                # If we have enough flights, stop
                if len(all_flights) >= 20:
                    break
            else:
                logger.info(f"   Attempt {attempt+1}: No flights in area (or API limit)")
            
            # Wait before retrying
            if attempt < max_attempts - 1 and not flights:
                logger.info(f"   Waiting 5 seconds before retry...")
                time.sleep(5)
        
        except Exception as e:
            logger.warning(f"   Attempt {attempt+1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(5)
    
    # Remove duplicates by flight_number + departure_time
    unique_flights = {}
    for flight in all_flights:
        flight_num = flight.get("flight_number", "UNKNOWN")
        dep_time = flight.get("departure_time", "")
        key = f"{flight_num}_{dep_time}"
        
        if key not in unique_flights:
            unique_flights[key] = flight
    
    flights = list(unique_flights.values())
    logger.info(f"✅ Got {len(flights)} unique flights from Airlabs")
    
    return flights


def transform_flights_for_database(flights: list) -> list:
    """Transform Airlabs flights to database schema.
    
    Args:
        flights: Raw flight data from Airlabs API
        
    Returns:
        List of records ready for database insertion
    """
    logger.info("🔄 Transforming flight data...")
    
    records = []
    missing_times = 0
    
    for flight in flights:
        try:
            # Get times from API (should always be present)
            departure_time = flight.get("departure_time")
            arrival_time = flight.get("arrival_time")
            
            # Check if times are real
            if not departure_time or not arrival_time:
                missing_times += 1
                logger.warning(f"   ⚠️  Flight {flight.get('flight_number')} missing times")
                continue  # Skip flights without real times
            
            # Create record with REAL times from API
            record = {
                "flight_number": flight.get("flight_number", "UNKNOWN"),
                "departure": flight.get("departure", "UNKNOWN"),
                "arrival": flight.get("arrival", "UNKNOWN"),
                "route": f"{flight.get('departure', 'UNKNOWN')}-{flight.get('arrival', 'UNKNOWN')}",
                "departure_time": departure_time,  # REAL from Airlabs
                "arrival_time": arrival_time,      # REAL from Airlabs
                "aircraft_type": flight.get("airplane") or flight.get("aircraft_type", "UNKNOWN"),
                "source": "Airlabs-API"
            }
            records.append(record)
        
        except Exception as e:
            logger.warning(f"   Failed to transform flight: {str(e)}")
            continue
    
    if missing_times > 0:
        logger.warning(f"⚠️  Skipped {missing_times} flights without real times")
    
    logger.info(f"✅ Transformed {len(records)} records with REAL times")
    return records


def insert_flights_to_database(warehouse: DataWarehouse, records: list) -> int:
    """Insert flight records into database.
    
    Args:
        warehouse: DataWarehouse instance
        records: List of flight records
        
    Returns:
        Number of flights inserted
    """
    logger.info("💾 Inserting flights into database...")
    
    if not records:
        logger.warning("   No records to insert")
        return 0
    
    try:
        warehouse.insert_flights_data(records)
        
        # Verify insertion
        count_query = "SELECT COUNT(*) FROM flights;"
        result = warehouse.db.execute(count_query)
        count = result[0][0] if result else 0
        
        logger.info(f"✅ {count} total flights in database")
        return count
    
    except Exception as e:
        logger.error(f"❌ Error inserting flights: {str(e)}")
        return 0


def show_sample_flights(warehouse: DataWarehouse, limit: int = 10):
    """Display sample of inserted flights.
    
    Args:
        warehouse: DataWarehouse instance
        limit: Number of flights to display
    """
    logger.info(f"\n📊 Sample of {limit} flights with REAL times:")
    logger.info("-" * 130)
    
    try:
        query = f"""
        SELECT flight_number, departure, arrival, departure_time, arrival_time, aircraft_type 
        FROM flights 
        ORDER BY departure_time 
        LIMIT {limit};
        """
        results = warehouse.db.execute(query)
        
        if results:
            for i, flight in enumerate(results, 1):
                logger.info(f"{i:2}. {flight[0]:10} | {flight[1]:4}→{flight[2]:4} | "
                           f"Depart: {flight[3]} | Arrive: {flight[4]} | {flight[5]}")
        else:
            logger.info("   No flights found")
    
    except Exception as e:
        logger.error(f"Error displaying sample: {str(e)}")


def main():
    """Main execution flow."""
    print("\n" + "="*130)
    print("  FETCH REAL FLIGHTS FROM AIRLABS WITH REAL DEPARTURE/ARRIVAL TIMES")
    print("="*130)
    
    # Step 0: Verify API key
    try:
        api_key = verify_airlabs_key()
    except ValueError as e:
        print(f"\n❌ {str(e)}\n")
        return False
    
    # Step 1: Connect to database
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
        print("\n⚠️  Make sure PostgreSQL is running and DATABASE_CONFIG is correct")
        return False
    
    try:
        # Step 2: Clear existing flights
        if not clear_flights_table(warehouse):
            return False
        
        # Step 3: Fetch real flights with REAL times
        flights = fetch_flights_from_airlabs(
            api_key=api_key,
            lat=48.8527,       # Paris
            lon=2.3510,
            radius_km=400,     # 400km radius covers Europe
            max_attempts=5
        )
        
        if not flights:
            logger.warning("⚠️  No flights fetched from Airlabs")
            logger.info("   Reasons might be:")
            logger.info("   • No active flights in area at this moment")
            logger.info("   • Airlabs API rate limit reached (500 calls/month)")
            logger.info("   • API key invalid or expired")
            warehouse.db.disconnect()
            return False
        
        # Step 4: Transform data
        records = transform_flights_for_database(flights)
        
        if not records:
            logger.error("❌ No valid records to insert")
            warehouse.db.disconnect()
            return False
        
        # Step 5: Insert into database
        inserted_count = insert_flights_to_database(warehouse, records)
        
        if inserted_count == 0:
            logger.error("❌ No flights were inserted")
            warehouse.db.disconnect()
            return False
        
        # Step 6: Show sample with REAL times
        show_sample_flights(warehouse)
        
        # Success summary
        logger.info("\n" + "="*130)
        logger.info("✅ FLIGHT FETCH COMPLETED SUCCESSFULLY")
        logger.info("="*130)
        logger.info(f"Total flights in database: {inserted_count}")
        logger.info(f"Departure/Arrival times: REAL (from Airlabs API)")
        logger.info(f"Data source: Airlabs API (https://airlabs.co)")
        logger.info(f"\nNext steps:")
        logger.info(f"  1. Fetch real lightning/storm data: python fetch_real_lightning.py")
        logger.info(f"  2. View dashboard: python app.py")
        logger.info(f"  3. Analyze perturbations")
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
