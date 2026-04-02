"""
Enhanced refresh service with Blitzortung WebSocket support.
Streams lightning data in real-time via WebSocket while polling flights periodically.
"""
import logging
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.config import get_config
from src.database import PostgreSQLConnection, DataWarehouse
from main import DataPipeline

# Try to import WebSocket client
try:
    from src.ingestion.blitzortung_websocket import BlitzortungWebSocketDataSource
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    BlitzortungWebSocketDataSource = None


class EnhancedDataRefreshService:
    """Enhanced refresh service with real-time WebSocket support for lightning data.
    
    Features:
    - Real-time lightning data via Blitzortung WebSocket
    - Periodic flight data polling (every 5 minutes)
    - Automatic database synchronization
    - Fallback to HTTP if WebSocket unavailable
    """
    
    def __init__(self, config=None, use_websocket: bool = True):
        """Initialize enhanced refresh service.
        
        Args:
            config: Configuration object
            use_websocket: Whether to use WebSocket for lightning data (default: True)
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.use_websocket = use_websocket and HAS_WEBSOCKET
        
        if use_websocket and not HAS_WEBSOCKET:
            self.logger.warning(
                "WebSocket requested but websocket-client not installed. "
                "Falling back to HTTP polling."
            )
        
        # Scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.daemon = True
        
        # Pipeline and database
        self.pipeline = None
        self.db_connection = None
        self.warehouse = None
        
        # WebSocket client (if enabled)
        self.ws_client = None
        
        # Status tracking
        self.is_running = False
        self.last_lightning_refresh = None
        self.last_flights_refresh = None
        self.websocket_strikes_processed = 0
        
        self.logger.info(
            f"EnhancedDataRefreshService initialized "
            f"(WebSocket: {'✓ Enabled' if self.use_websocket else '✗ Disabled'})"
        )
    
    def start(self):
        """Start the enhanced refresh service."""
        if self.is_running:
            self.logger.warning("Service is already running")
            return
        
        try:
            # Initialize pipeline and database
            self.logger.info("Initializing pipeline and database...")
            self.pipeline = DataPipeline()
            
            if not self.pipeline.connect_database():
                self.logger.error("Failed to connect to database")
                return
            
            self.db_connection = self.pipeline.db_connection
            self.warehouse = self.pipeline.warehouse
            
            # Start WebSocket if enabled
            if self.use_websocket:
                self._start_websocket()
            
            # Schedule flights data refresh (every 5 minutes)
            self.scheduler.add_job(
                self._refresh_flights_data,
                IntervalTrigger(minutes=5),
                id="refresh_flights",
                name="Refresh Flights Data",
                coalesce=True,
                max_instances=1,
                replace_existing=True
            )
            self.logger.info("Scheduled flights refresh: every 5 minutes")
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            
            self.logger.info("✅ EnhancedDataRefreshService started successfully")
            
            # Run initial flight refresh
            self.logger.info("Running initial flight data refresh...")
            self._refresh_flights_data()
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {str(e)}")
            self.is_running = False
    
    def _start_websocket(self):
        """Start the Blitzortung WebSocket client."""
        try:
            self.logger.info("Starting Blitzortung WebSocket connection...")
            
            self.ws_client = BlitzortungWebSocketDataSource(
                ws_url="wss://ws.blitzortung.org/ws"
            )
            self.ws_client.start()
            
            # Start background thread to sync WebSocket strikes to database
            sync_thread = threading.Thread(
                target=self._sync_websocket_strikes,
                daemon=True
            )
            sync_thread.start()
            
            self.logger.info("✅ Blitzortung WebSocket started")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket: {str(e)}")
            self.use_websocket = False
    
    def _sync_websocket_strikes(self):
        """Continuously sync WebSocket strikes to database."""
        while self.is_running:
            try:
                if self.ws_client and self.ws_client.is_connected():
                    # Get accumulated strikes from WebSocket
                    data = self.ws_client.fetch()
                    strikes = data.get("strikes", [])
                    
                    if strikes:
                        # Save to database
                        self.logger.info(
                            f"💾 Syncing {len(strikes)} WebSocket strikes to database..."
                        )
                        
                        try:
                            self.warehouse.insert_lightning_data(strikes)
                            self.websocket_strikes_processed += len(strikes)
                            self.last_lightning_refresh = datetime.now()
                            
                            self.logger.info(
                                f"✅ Synced {len(strikes)} strikes "
                                f"(Total: {self.websocket_strikes_processed})"
                            )
                        except Exception as e:
                            self.logger.error(f"Failed to insert strikes: {str(e)}")
                
                # Check every 2 seconds
                time.sleep(2)
            
            except Exception as e:
                self.logger.error(f"WebSocket sync error: {str(e)}")
                time.sleep(5)
    
    def _refresh_flights_data(self):
        """Refresh flights data from API."""
        try:
            self.logger.info("🔄 Refreshing flights data...")
            
            if not self.pipeline:
                self.logger.error("Pipeline not initialized")
                return
            
            # Fetch flights
            flights_data = self.pipeline.run_ingestion_flights()
            
            if flights_data and len(flights_data) > 0:
                self.logger.info(f"✅ Fetched {len(flights_data)} flights")
                self.last_flights_refresh = datetime.now()
            else:
                self.logger.warning("No flights data received")
        
        except Exception as e:
            self.logger.error(f"Error refreshing flights: {str(e)}")
    
    def stop(self):
        """Stop the refresh service."""
        if not self.is_running:
            return
        
        try:
            self.logger.info("Stopping EnhancedDataRefreshService...")
            
            # Stop WebSocket
            if self.ws_client:
                self.ws_client.stop()
            
            # Stop scheduler
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            
            # Close database
            if self.db_connection:
                self.db_connection.disconnect()
            
            self.is_running = False
            self.logger.info("✅ EnhancedDataRefreshService stopped")
        
        except Exception as e:
            self.logger.error(f"Error stopping service: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status.
        
        Returns:
            Status dictionary
        """
        ws_status = {}
        if self.ws_client:
            ws_status = self.ws_client.client.get_status()
        
        return {
            "is_running": self.is_running,
            "last_lightning_refresh": self.last_lightning_refresh,
            "last_flights_refresh": self.last_flights_refresh,
            "websocket_enabled": self.use_websocket,
            "websocket_strikes_processed": self.websocket_strikes_processed,
            "websocket_status": ws_status,
            "scheduled_jobs": [
                {
                    "name": job.name,
                    "next_run_time": str(job.next_run_time)
                }
                for job in self.scheduler.get_jobs()
            ] if self.scheduler.running else []
        }


# Global singleton instance
_enhanced_service_instance = None


def get_enhanced_refresh_service(config=None, use_websocket: bool = True):
    """Get or create enhanced refresh service singleton.
    
    Args:
        config: Configuration object
        use_websocket: Whether to use WebSocket
        
    Returns:
        EnhancedDataRefreshService instance
    """
    global _enhanced_service_instance
    
    if _enhanced_service_instance is None:
        _enhanced_service_instance = EnhancedDataRefreshService(
            config=config,
            use_websocket=use_websocket
        )
    
    return _enhanced_service_instance
