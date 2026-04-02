#!/usr/bin/env python3
"""
Blitzortung WebSocket Real-Time Lightning Data Demo
Receives live lightning strikes from Blitzortung WebSocket server
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

# Setup logging
logging.basicConfig(
    format='%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from src.ingestion.blitzortung_websocket import BlitzortungWebSocketDataSource


def main():
    """Run Blitzortung WebSocket listener."""
    logger.info("=" * 80)
    logger.info("⚡ BLITZORTUNG WEBSOCKET REAL-TIME LIGHTNING MONITOR")
    logger.info("=" * 80)
    
    try:
        # Initialize WebSocket data source
        logger.info("🔌 Initializing Blitzortung WebSocket connection...")
        
        # Create data source
        ws_source = BlitzortungWebSocketDataSource(
            ws_url="wss://ws.blitzortung.org/ws"
        )
        
        # Start listening
        ws_source.start()
        
        logger.info("✅ WebSocket connected!")
        logger.info("")
        logger.info("📊 Real-time lightning strike stream:")
        logger.info("-" * 80)
        
        strike_count = 0
        last_update = time.time()
        
        # Listen for strikes
        while True:
            time.sleep(1)
            
            # Get accumulated strikes
            data = ws_source.fetch()
            strikes = data.get("strikes", [])
            
            if strikes:
                strike_count += len(strikes)
                logger.info(f"⚡ NEW STRIKES RECEIVED: {len(strikes)}")
                
                for strike in strikes:
                    lat = strike.get("latitude", 0)
                    lon = strike.get("longitude", 0)
                    intensity = strike.get("intensity", "-")
                    timestamp = strike.get("timestamp", "?")
                    
                    logger.info(
                        f"   🧲 Strike @ ({lat:.2f}, {lon:.2f}) | "
                        f"Intensity: {intensity} | Time: {timestamp}"
                    )
            
            # Show status every 30 seconds
            now = time.time()
            if now - last_update >= 30:
                status = ws_source.client.get_status()
                logger.info("")
                logger.info("📈 CONNECTION STATUS:")
                logger.info(f"   ✓ Connected: {status['is_connected']}")
                logger.info(f"   ✓ Strikes Received: {status['strikes_received']}")
                logger.info(f"   ✓ Buffer Size: {status['buffer_size']}")
                logger.info(f"   ✓ Uptime: {status['uptime_seconds']:.0f}s")
                logger.info("")
                
                last_update = now
    
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 80)
        logger.info("🛑 STOPPING WEBSOCKET LISTENER")
        logger.info("=" * 80)
        
        ws_source.stop()
        
        logger.info(f"✅ Total strikes received: {strike_count}")
        logger.info("✅ WebSocket listener stopped")
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        if 'ws_source' in locals():
            ws_source.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
