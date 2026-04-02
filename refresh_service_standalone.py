#!/usr/bin/env python3
"""
Standalone data refresh service.
Run this in a separate terminal for continuous data refresh.

Usage:
    python refresh_service_standalone.py
"""
import sys
from pathlib import Path
import time
import signal

sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.utils import setup_logging
from src.utils.refresh_service import get_refresh_service


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nStopping refresh service...")
    service.stop()
    print("Service stopped. Goodbye!")
    sys.exit(0)


if __name__ == "__main__":
    # Setup logging
    config = get_config()
    setup_logging(log_file=str(config.LOG_FILE), level=config.LOG_LEVEL)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start service
    print("\n" + "="*70)
    print("LIGHTNING & FLIGHTS DATA REFRESH SERVICE")
    print("="*70)
    print("\nStarting data refresh service...\n")
    
    service = get_refresh_service(config)
    service.start()
    
    print("\nRefresh Service Running:")
    print("  - Lightning: refreshed every 20 minutes")
    print("  - Flights: refreshed every 2 hours")
    print("\nPress Ctrl+C to stop.\n")
    
    # Keep service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
