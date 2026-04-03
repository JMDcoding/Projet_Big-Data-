#!/usr/bin/env python3
"""
Diagnostic script to test flight data flow.
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.database import PostgreSQLConnection, DataWarehouse

def test_database_connection():
    """Test database connection."""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)
    
    config = get_config()
    print(f"[*] Attempting to connect to {config.DB_HOST}:{config.DB_PORT}...")
    print(f"[*] Database: {config.DB_NAME}")
    print(f"[*] User: {config.DB_USER}")
    
    try:
        db = PostgreSQLConnection(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        db.connect()
        print("[✓] Database connection successful")
        return db
    except Exception as e:
        print(f"[✗] Database connection failed: {type(e).__name__}: {e}")
        return None

def test_flights_query(db):
    """Test flights data query."""
    print("\n" + "="*60)
    print("TEST 2: Query Flights Data")
    print("="*60)
    
    try:
        warehouse = DataWarehouse(db)
        
        # Try direct SQL query
        print("[*] Executing raw SQL query...")
        cursor = db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM flights;")
        count = cursor.fetchone()[0]
        print(f"[+] Total flights in database: {count}")
        
        # Try warehouse query
        print("[*] Using DataWarehouse.query_flights_data()...")
        flights = warehouse.query_flights_data()
        print(f"[+] Flights returned: {len(flights)}")
        
        if flights:
            import json
            print(f"[+] Sample flight (first record):")
            print(json.dumps(flights[0], indent=2, default=str))
            
            print(f"\n[+] Sample flight (last record):")
            print(json.dumps(flights[-1], indent=2, default=str))
        
        return flights
    
    except Exception as e:
        print(f"[✗] Query failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_dataframe_creation(flights_data):
    """Test DataFrame creation."""
    print("\n" + "="*60)
    print("TEST 3: Create DataFrame")
    print("="*60)
    
    if not flights_data:
        print("[✗] No flights data to create DataFrame from")
        return None
    
    try:
        df = pd.DataFrame(flights_data)
        print(f"[✓] DataFrame created successfully")
        print(f"[+] Rows: {len(df)}")
        print(f"[+] Columns: {list(df.columns)}")
        print(f"[+] Data types:\n{df.dtypes}")
        
        if not df.empty:
            print(f"\n[+] First 3 rows:")
            print(df.head(3))
        
        return df
    
    except Exception as e:
        print(f"[✗] DataFrame creation failed: {type(e).__name__}: {e}")
        return None

def test_flight_filters(flights_df):
    """Test flight filter logic."""
    print("\n" + "="*60)
    print("TEST 4: Apply Filters")
    print("="*60)
    
    if flights_df is None or flights_df.empty:
        print("[✗] No DataFrame to filter")
        return None
    
    try:
        from src.visualization import LightningDashboard
        dashboard = LightningDashboard()
        
        # Test with empty filters
        print("[*] Testing with empty filters...")
        filtered = dashboard.apply_flights_filters(flights_df, {})
        print(f"[+] Filtered rows (empty filters): {len(filtered)}")
        
        # Test with date range filter
        print("[*] Testing with date range filter...")
        import pandas as pd
        start_date = pd.Timestamp("2024-01-01")
        end_date = pd.Timestamp("2025-12-31")
        
        filters = {
            "date_range": (start_date.date(), end_date.date())
        }
        filtered = dashboard.apply_flights_filters(flights_df, filters)
        print(f"[+] Filtered rows (date range): {len(filtered)}")
        
        return filtered
    
    except Exception as e:
        print(f"[✗] Filter test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all tests."""
    print("\n" + "█"*60)
    print("FLIGHT DATA DIAGNOSTIC TEST")
    print("█"*60)
    
    # Test 1: Database connection
    db = test_database_connection()
    if not db:
        print("\n" + "="*60)
        print("DIAGNOSIS: PostgreSQL is not running or not accessible")
        print("="*60)
        print("\nTo fix this on Windows:")
        print("1. Open 'Services' (services.msc)")
        print("2. Find 'postgresql-x64-13' service")
        print("3. Right-click → Start")
        print("\nOr use command: pg_ctl -D path/to/data start")
        return
    
    # Test 2: Query flights
    flights_data = test_flights_query(db)
    
    # Test 3: Create DataFrame
    flights_df = test_dataframe_creation(flights_data)
    
    # Test 4: Apply filters
    if flights_df is not None:
        filtered_df = test_flight_filters(flights_df)
    
    # Cleanup
    if db:
        db.disconnect()
    
    print("\n" + "█"*60)
    print("DIAGNOSTIC COMPLETE")
    print("█"*60 + "\n")

if __name__ == "__main__":
    main()
