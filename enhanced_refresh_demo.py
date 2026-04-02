#!/usr/bin/env python3
"""
Enhanced Refresh Service Demo - Real-time Lightning + Periodic Flights
Uses WebSocket for live lightning strikes and polling for flights
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

# Setup logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from src.utils.enhanced_refresh_service import get_enhanced_refresh_service


def main():
    """Run enhanced refresh service."""
    logger.info("=" * 80)
    logger.info("⚡ ENHANCED REFRESH SERVICE - WebSocket Lightning + Polling Flights")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📊 Data Sources:")
    logger.info("   • Lightning: Blitzortung WebSocket (real-time)")
    logger.info("   • Flights: AviationStack API (every 5 minutes)")
    logger.info("   • Disruptions: Calculated from lightning + flights")
    logger.info("")
    logger.info("💾 Storage:")
    logger.info("   • MinIO (S3 object storage)")
    logger.info("   • PostgreSQL (lightning, flights tables)")
    logger.info("")
    
    try:
        # Initialize and start service
        service = get_enhanced_refresh_service(use_websocket=True)
        logger.info("Starting enhanced refresh service...")
        
        service.start()
        
        logger.info("✅ Service started successfully!")
        logger.info("")
        logger.info("-" * 80)
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 80)
        logger.info("")
        
        # Display status updates
        last_status_time = time.time()
        
        while True:
            time.sleep(5)
            
            # Show status every 30 seconds
            now = time.time()
            if now - last_status_time >= 30:
                status = service.get_status()
                
                logger.info("")
                logger.info("📈 SERVICE STATUS:")
                logger.info(f"   ✓ Running: {status['is_running']}")
                logger.info(f"   ✓ WebSocket Lightning: {status['websocket_enabled']}")
                
                if status['websocket_status']:
                    ws_status = status['websocket_status']
                    logger.info(f"   ✓ WebSocket Connected: {ws_status.get('is_connected', False)}")
                    logger.info(f"   ✓ Strikes Received: {ws_status.get('strikes_received', 0)}")
                
                logger.info(f"   ✓ Strikes Processed: {status['websocket_strikes_processed']}")
                logger.info(f"   ✓ Last Lightning Refresh: {status['last_lightning_refresh']}")
                logger.info(f"   ✓ Last Flights Refresh: {status['last_flights_refresh']}")
                
                if status['scheduled_jobs']:
                    logger.info("   ✓ Scheduled Jobs:")
                    for job in status['scheduled_jobs']:
                        logger.info(f"      - {job['name']}: {job['next_run_time']}")
                logger.info("")
                
                last_status_time = now
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("🛑 STOPPING SERVICE")
        logger.info("=" * 80)
        
        if 'service' in locals():
            service.stop()
        
        logger.info("✅ Service stopped")
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        if 'service' in locals():
            service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
