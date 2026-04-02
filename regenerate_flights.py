#!/usr/bin/env python3
"""
Script to clear flights table and regenerate data.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from main import DataPipeline

print("\n" + "="*60)
print("CLEANING AND REGENERATING FLIGHT DATA")
print("="*60)

try:
    config = get_config()
    print("\n[*] Creating pipeline...")
    pipeline = DataPipeline()
    
    # Connect to database
    print("[*] Connecting to database...")
    if not pipeline.connect_database():
        print("[ERROR] Failed to connect to database")
        exit(1)
    print("[OK] Database connected")
    
    # Clear old flights data
    print("\n[*] Clearing old flight data...")
    cursor = pipeline.db_connection.connection.cursor()
    cursor.execute("DELETE FROM flights;")
    pipeline.db_connection.connection.commit()
    print("[OK] Flight table cleared")
    
    print("[*] Step 1: Ingesting flights...")
    ingestion_result = pipeline.run_ingestion_flights()
    
    if ingestion_result["status"] != "success":
        print(f"[ERROR] Ingestion failed: {ingestion_result.get('message')}")
        exit(1)
    
    raw_data = ingestion_result["raw_data"]
    print(f"[OK] Ingested {ingestion_result['records']} flights from {ingestion_result['source']}")
    
    print("[*] Step 2: Transforming flights...")
    transformation_result = pipeline.run_transformation_flights(raw_data)
    print(f"[OK] Transformed {transformation_result['records']} flights")
    
    print("[*] Step 3: Loading flights into database...")
    loading_result = pipeline.run_loading_flights(transformation_result["dataframe"])
    print(f"[OK] Loaded {loading_result.get('records_loaded', '?')} flights into database")
    
    print("[*] Step 4: Storing flights to MinIO...")
    storage_result = pipeline.run_storage_flights(transformation_result["dataframe"])
    print(f"[OK] Stored flights data")
    
    print("\n[OK] Flights data regenerated successfully!")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
