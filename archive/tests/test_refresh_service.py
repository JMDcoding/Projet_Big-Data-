#!/usr/bin/env python3
"""
Quick test of the refresh service.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.utils.refresh_service import get_refresh_service

print("\n" + "="*60)
print("REFRESH SERVICE TEST")
print("="*60)

try:
    print("\n[*] Creating refresh service...")
    config = get_config()
    service = get_refresh_service(config)
    print("[OK] Service created")
    
    print("\n[*] Testing service initialization...")
    print("[OK] Service status:")
    status = service.get_status()
    print(f"    - Running: {status['is_running']}")
    print(f"    - Scheduled jobs: {len(status['jobs'])}")
    
    print("\n[OK] Refresh service is ready to use!")
    print("\nTo start the service, run:")
    print("    python refresh_service_standalone.py")
    print("\nOr use the dashboard:")
    print("    streamlit run app.py")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
