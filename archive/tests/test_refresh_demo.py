#!/usr/bin/env python3
"""
Test starting the refresh service for a few seconds.
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.utils.refresh_service import get_refresh_service

print("\n" + "="*60)
print("REFRESH SERVICE DEMO")
print("="*60)

try:
    print("\n[*] Starting refresh service...")
    config = get_config()
    service = get_refresh_service(config)
    
    # Start the service
    service.start()
    
    print("[OK] Service started!")
    print("\nMonitoring for 10 seconds...\n")
    
    # Monitor for 10 seconds
    for i in range(10):
        time.sleep(1)
        status = service.get_status()
        
        if i % 2 == 0:
            print(f"[{i}s] Service running: {status['is_running']}")
            if status['jobs']:
                print(f"     Scheduled jobs: {len(status['jobs'])}")
                for job in status['jobs']:
                    print(f"       - {job['name']} (next: {job['next_run_time']})")
    
    print("\n[OK] Service demo complete!")
    print("\nService is now running continuously when:")
    print("  1. You launch the dashboard: streamlit run app.py")
    print("  2. Or you run: python refresh_service_standalone.py")
    print("\nRefresh Schedule:")
    print("  - Lightning: every 20 minutes (high priority)")
    print("  - Flights: every 2 hours")
    
    # Stop the service
    print("\n[*] Stopping demo service...")
    service.stop()
    print("[OK] Service stopped")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
