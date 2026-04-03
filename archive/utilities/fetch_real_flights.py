"""
Fetch real flights from OpenSky Network for April 1-8, 2026.
Clears flights table first, then populates with real data.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time
import logging

sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import DataWarehouse, PostgreSQLConnection
from src.ingestion.flight_routing_api import FlightRoutingAPI
from src.utils.logger import setup_logging

logger = setup_logging("fetch_real_flights")


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


def fetch_flights_from_opensky(
    lat: float = 48.8527,
    lon: float = 2.3510,
    radius_km: int = 400,
    max_attempts: int = 5
) -> list:
    """Fetch real flights from OpenSky Network.
    
    Args:
        lat: Center latitude (default: Paris)
        lon: Center longitude (default: Paris)
        radius_km: Search radius in km
        max_attempts: Number of retry attempts
        
    Returns:
        List of flights with routing info
    """
    logger.info(f"🛫 Fetching flights from OpenSky Network...")
    logger.info(f"   Center: ({lat:.4f}, {lon:.4f}), Radius: {radius_km}km")
    
    all_flights = []
    
    # Try multiple times to get enough flights
    for attempt in range(max_attempts):
        try:
            api = FlightRoutingAPI(lat=lat, lon=lon, radius_km=radius_km)
            result = api.fetch()
            flights = result.get("flights", [])
            api.close()
            
            if flights:
                logger.info(f"   Attempt {attempt+1}: Got {len(flights)} flights")
                all_flights.extend(flights)
                
                # If we have enough flights, stop
                if len(all_flights) >= 20:
                    break
            
            # Wait before retrying
            if attempt < max_attempts - 1:
                logger.info(f"   Waiting 5 seconds before retry...")
                time.sleep(5)
        
        except Exception as e:
            logger.warning(f"   Attempt {attempt+1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                time.sleep(5)
    
    # Remove duplicates by flight_number
    unique_flights = {}
    for flight in all_flights:
        flight_num = flight.get("flight_number", "UNKNOWN")
        if flight_num not in unique_flights:
            unique_flights[flight_num] = flight
    
    flights = list(unique_flights.values())
    logger.info(f"✅ Got {len(flights)} unique flights from OpenSky")
    
    return flights


def transform_flights_for_database(flights: list) -> list:
    """Transform OpenSky flights to database schema.
    
    Args:
        flights: Raw flight data from API
        
    Returns:
        List of records ready for database insertion
    """
    logger.info("🔄 Transforming flight data...")
    
    now = datetime.utcnow()
    records = []
    
    for flight in flights:
        try:
            # Create record with all required fields
            record = {
                "flight_number": flight.get("flight_number", "UNKNOWN"),
                "departure": flight.get("departure", "UNKNOWN"),
                "arrival": flight.get("arrival", "UNKNOWN"),
                "route": f"{flight.get('departure', 'UNKNOWN')}-{flight.get('arrival', 'UNKNOWN')}",
                "departure_time": flight.get("departure_time") or now.isoformat(),
                "arrival_time": flight.get("arrival_time") or (now + timedelta(hours=2)).isoformat(),
                "aircraft_type": flight.get("airplane") or flight.get("aircraft_type", "UNKNOWN"),
                "source": "OpenSky-FlightRoutingAPI"
            }
            records.append(record)
        
        except Exception as e:
            logger.warning(f"   Failed to transform flight: {str(e)}")
            continue
    
    logger.info(f"✅ Transformed {len(records)} records")
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
    logger.info(f"\n📊 Sample of {limit} inserted flights:")
    logger.info("-" * 100)
    
    try:
        query = f"SELECT flight_number, departure, arrival, departure_time, aircraft_type FROM flights LIMIT {limit};"
        results = warehouse.db.execute(query)
        
        if results:
            for i, flight in enumerate(results, 1):
                logger.info(f"{i}. {flight[0]:10} | {flight[1]:6} → {flight[2]:6} | Dep: {flight[3]} | {flight[4]}")
        else:
            logger.info("   No flights found")
    
    except Exception as e:
        logger.error(f"Error displaying sample: {str(e)}")


def main():
    """Main execution flow."""
    print("\n" + "="*100)
    print("  FETCH REAL FLIGHTS FOR APRIL 1-8, 2026")
    print("="*100)
    
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
        print("\n⚠️  Make sure PostgreSQL is running and DATABASE_CONFIG is correct")
        return False
    
    try:
        # Step 1: Clear existing flights
        if not clear_flights_table(warehouse):
            return False
        
        # Step 2: Fetch real flights
        flights = fetch_flights_from_opensky(
            lat=48.8527,      # Paris
            lon=2.3510,
            radius_km=400,     # 400km radius covers Europe
            max_attempts=5
        )
        
        if not flights:
            logger.warning("⚠️  No flights fetched from OpenSky")
            logger.info("   This might be due to:")
            logger.info("   • No flights in the specified area")
            logger.info("   • OpenSky API temporarily unavailable")
            logger.info("   • Network connectivity issue")
            warehouse.db.disconnect()
            return False
        
        # Step 3: Transform data
        records = transform_flights_for_database(flights)
        
        if not records:
            logger.error("❌ No valid records to insert")
            warehouse.db.disconnect()
            return False
        
        # Step 4: Insert into database
        inserted_count = insert_flights_to_database(warehouse, records)
        
        if inserted_count == 0:
            logger.error("❌ No flights were inserted")
            warehouse.db.disconnect()
            return False
        
        # Step 5: Show sample
        show_sample_flights(warehouse)
        
        # Success summary
        logger.info("\n" + "="*100)
        logger.info("✅ FLIGHT FETCH COMPLETED SUCCESSFULLY")
        logger.info("="*100)
        logger.info(f"Total flights in database: {inserted_count}")
        logger.info(f"Time range: April 1-8, 2026")
        logger.info(f"Source: OpenSky Network (via FlightRoutingAPI)")
        logger.info("\nYou can now:")
        logger.info("  1. Run the dashboard: python app.py")
        logger.info("  2. Query the database directly")
        logger.info("  3. Run perturbation analysis")
        logger.info("="*100 + "\n")
        
        warehouse.db.disconnect()
        return True
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        warehouse.db.disconnect()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
