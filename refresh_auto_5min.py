#!/usr/bin/env python3
"""
Auto-refresh service demo: Fetch API data every 5 minutes
Runs continuously and logs each refresh
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.cwd()))

# Setup logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from config.config import get_config
from src.utils.refresh_service import DataRefreshService


def main():
    """Run the auto-refresh service continuously."""
    logger.info("=" * 70)
    logger.info("🔄 AUTO-REFRESH SERVICE - Every 5 Minutes")
    logger.info("=" * 70)
    
    try:
        config = get_config()
        logger.info("✅ Configuration loaded")
        
        # Create and start the refresh service
        service = DataRefreshService(config)
        logger.info("📡 Starting refresh service...")
        
        service.start()
        logger.info("✅ Refresh service started successfully!")
        logger.info("")
        logger.info("📊 Schedule:")
        logger.info("   • Lightning data: Every 5 minutes")
        logger.info("   • Flight data: Every 5 minutes")
        logger.info("")
        logger.info("💾 Data destinations:")
        logger.info("   • MinIO (S3): data/minio/lightning, data/minio/flights")
        logger.info("   • PostgreSQL: lightning, flights tables")
        logger.info("")
        logger.info("-" * 70)
        logger.info("Press Ctrl+C to stop the service")
        logger.info("-" * 70)
        logger.info("")
        
        # Keep the service running
        while True:
            time.sleep(10)
            
            # Display status every 30 seconds
            if service.is_running:
                status = service.get_status()
                jobs = status.get('scheduled_jobs', [])
                
                if jobs:
                    for job in jobs:
                        logger.info(
                            f"📍 {job['name']:<30} | "
                            f"Next run: {job['next_run_time']}"
                        )
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("🛑 Stopping refresh service...")
        logger.info("=" * 70)
        
        if 'service' in locals() and service:
            service.stop()
            logger.info("✅ Refresh service stopped")
        
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
