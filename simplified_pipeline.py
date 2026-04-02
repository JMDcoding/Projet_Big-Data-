#!/usr/bin/env python3
"""
Simplified pipeline using working APIs only.
Uses:
- OpenSky Network for flights (tested and working)
- Blitzortung WebSocket for lightning (real-time)
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path.cwd()))

from config.config import get_config
from src.utils.logger import setup_logging
from src.ingestion.alternative_apis import OpenSkyAlternative
from src.ingestion.blitzortung_websocket import BlitzortungWebSocketDataSource
from src.database.warehouse import PostgreSQLConnection, DataWarehouse


class SimplifiedPipeline:
    """Simplified pipeline using only tested APIs."""
    
    def __init__(self, config=None):
        """Initialize simplified pipeline."""
        self.config = config or get_config()
        self.logger = setup_logging(log_file=str(self.config.LOG_FILE))
        
        # Data sources (TESTED & WORKING)
        self.flights_api = OpenSkyAlternative(
            lat=48.8527,  # Paris
            lon=2.3510,
            radius_km=100
        )
        
        self.lightning_ws = None
        
        # Database
        self.db = None
        self.warehouse = None
    
    def initialize(self):
        """Initialize database and WebSocket connections."""
        try:
            self.logger.info("📡 Initializing connections...")
            
            # Connect to database
            self.db = PostgreSQLConnection(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            self.db.connect()
            self.warehouse = DataWarehouse(self.db)
            self.logger.info("✅ PostgreSQL connected")
            
            # Start WebSocket
            self.logger.info("Starting Blitzortung WebSocket...")
            self.lightning_ws = BlitzortungWebSocketDataSource()
            self.lightning_ws.start()
            self.logger.info("✅ WebSocket started")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def fetch_flights(self):
        """Fetch flight data from OpenSky Network."""
        try:
            self.logger.info("📍 Fetching flights from OpenSky Network...")
            
            data = self.flights_api.fetch()
            flights = data.get("flights", [])
            
            if flights:
                self.logger.info(f"✅ Got {len(flights)} flights")
                
                # Save to database
                self.warehouse.insert_flight_data(flights)
                self.logger.info(f"💾 Saved {len(flights)} flights to PostgreSQL")
                
                return flights
            else:
                self.logger.warning("No flights found")
                return []
        
        except Exception as e:
            self.logger.error(f"Flight fetch error: {str(e)}")
            return []
    
    def fetch_lightning(self):
        """Fetch lightning data from WebSocket."""
        try:
            if not self.lightning_ws or not self.lightning_ws.is_connected():
                self.logger.warning("WebSocket not connected")
                return []
            
            data = self.lightning_ws.fetch()
            strikes = data.get("strikes", [])
            
            if strikes:
                self.logger.info(f"⚡ Got {len(strikes)} lightning strikes")
                
                # Save to database
                self.warehouse.insert_lightning_data(strikes)
                self.logger.info(f"💾 Saved {len(strikes)} strikes to PostgreSQL")
                
                return strikes
            
            return []
        
        except Exception as e:
            self.logger.error(f"Lightning fetch error: {str(e)}")
            return []
    
    def run_once(self):
        """Run pipeline once (fetch all data)."""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🚀 STARTING SIMPLIFIED PIPELINE")
            self.logger.info("=" * 80)
            self.logger.info("")
            
            # Initialize
            if not self.initialize():
                return False
            
            # Fetch data
            flights = self.fetch_flights()
            strikes = self.fetch_lightning()
            
            # Summary
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("📊 RESULTS")
            self.logger.info("=" * 80)
            self.logger.info(f"✈️  Flights: {len(flights)}")
            self.logger.info(f"⚡ Strikes: {len(strikes)}")
            self.logger.info("=" * 80)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Close connections."""
        try:
            if self.lightning_ws:
                self.lightning_ws.stop()
            
            if self.db:
                self.db.disconnect()
        
        except Exception as e:
            self.logger.error(f"Cleanup error: {str(e)}")


def main():
    """Run simplified pipeline."""
    pipeline = SimplifiedPipeline()
    
    try:
        success = pipeline.run_once()
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n✅ Stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
