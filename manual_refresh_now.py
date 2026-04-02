#!/usr/bin/env python3
"""
Quick manual refresh test - fetch data once immediately.
Useful for testing without waiting 20 minutes.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.utils import setup_logging
from main import DataPipeline

print("\n" + "="*70)
print("MANUAL DATA REFRESH TEST")
print("="*70)

try:
    config = get_config()
    setup_logging(log_file=str(config.LOG_FILE))
    
    pipeline = DataPipeline()
    
    print("\n[*] Connecting to database...")
    if not pipeline.connect_database():
        print("[ERROR] Cannot connect to database")
        exit(1)
    
    print("[OK] Connected")
    
    # Test Lightning
    print("\n[*] Fetching lightning data immediately...")
    ingestion = pipeline.run_ingestion()
    if ingestion["status"] == "success":
        print(f"[OK] Lightning: {ingestion['records']} records")
        transform = pipeline.run_transformation(ingestion["raw_data"])
        print(f"[OK] Transformed: {transform['records']} records")
        load = pipeline.run_loading(transform["dataframe"])
        print(f"[OK] Loaded to DB: {load.get('records_loaded', '?')} records")
    
    # Test Flights
    print("\n[*] Fetching flights data immediately...")
    ingestion = pipeline.run_ingestion_flights()
    if ingestion["status"] == "success":
        print(f"[OK] Flights: {ingestion['records']} records")
        transform = pipeline.run_transformation_flights(ingestion["raw_data"])
        print(f"[OK] Transformed: {transform['records']} records")
        load = pipeline.run_loading_flights(transform["dataframe"])
        print(f"[OK] Loaded to DB: {load.get('records_loaded', '?')} records")
    
    print("\n[OK] Manual refresh complete!")
    print("\nNow you can:")
    print("  1. Refresh the dashboard (F5) to see new data")
    print("  2. Or start the auto-refresh service for continuous updates")
    print("     streamlit run app.py")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
