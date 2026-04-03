"""
Automatic data refresh service using APScheduler.
Fetches lightning and flight data at regular intervals.
"""
import logging
import threading
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.config import get_config
from src.database import PostgreSQLConnection, DataWarehouse
from main import DataPipeline


class DataRefreshService:
    """Service for automatic data refresh from APIs."""
    
    def __init__(self, config=None):
        """Initialize the refresh service.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.daemon = True  # Run as daemon thread
        
        # Pipeline and database
        self.pipeline = None
        self.db_connection = None
        self.warehouse = None
        
        # Status tracking
        self.is_running = False
        self.last_lightning_refresh = None
        self.last_flights_refresh = None
        
        self.logger.info("DataRefreshService initialized")
    
    def start(self):
        """Start the refresh service with scheduled tasks."""
        if self.is_running:
            self.logger.warning("Service is already running")
            return
        
        try:
            # Initialize pipeline and database
            self.logger.info("Initializing pipeline and database...")
            self.pipeline = DataPipeline()
            
            if not self.pipeline.connect_database():
                self.logger.error("Failed to connect to database. Service cannot start.")
                return
            
            self.db_connection = self.pipeline.db_connection
            self.warehouse = self.pipeline.warehouse
            
            # Schedule lightning data refresh (every 5 minutes)
            self.scheduler.add_job(
                self._refresh_lightning_data,
                IntervalTrigger(minutes=5),
                id="refresh_lightning",
                name="Refresh Lightning Data",
                coalesce=True,
                max_instances=1,
                replace_existing=True
            )
            self.logger.info("Scheduled lightning refresh: every 5 minutes")
            
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
            
            self.logger.info("DataRefreshService started successfully")
            
            # Run first refresh immediately
            self.logger.info("Running initial data refresh...")
            self._refresh_lightning_data()
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """Stop the refresh service."""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            self.logger.info("DataRefreshService stopped")
        except Exception as e:
            self.logger.error(f"Error stopping service: {str(e)}")
    
    def _refresh_lightning_data(self):
        """Refresh lightning data from APIs."""
        try:
            self.logger.info("Refreshing lightning data...")
            
            timestamp_start = datetime.now()
            
            # Step 1: Ingest
            ingestion_result = self.pipeline.run_ingestion()
            
            if ingestion_result["status"] != "success":
                self.logger.warning(f"Lightning ingestion failed: {ingestion_result}")
                return
            
            records_ingested = ingestion_result["records"]
            
            # Step 2: Transform
            raw_data = ingestion_result["raw_data"]
            transformation_result = self.pipeline.run_transformation(raw_data)
            
            if transformation_result["status"] != "success":
                self.logger.warning(f"Lightning transformation failed: {transformation_result}")
                return
            
            # Step 3: Load to database
            df = transformation_result["dataframe"]
            loading_result = self.pipeline.run_loading(df)
            
            if loading_result["status"] != "success":
                self.logger.warning(f"Lightning loading failed: {loading_result}")
                return
            
            records_loaded = loading_result.get("records_loaded", 0)
            
            # Step 4: Store to MinIO
            self.pipeline.run_storage(df)
            
            timestamp_end = datetime.now()
            duration = (timestamp_end - timestamp_start).total_seconds()
            
            self.last_lightning_refresh = timestamp_end
            
            self.logger.info(
                f"Lightning refresh completed: "
                f"{records_loaded} records loaded in {duration:.1f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Lightning refresh failed: {str(e)}")
    
    def _refresh_flights_data(self):
        """Refresh flights data from APIs."""
        try:
            self.logger.info("Refreshing flights data...")
            
            timestamp_start = datetime.now()
            
            # Step 1: Ingest flights
            ingestion_result = self.pipeline.run_ingestion_flights()
            
            if ingestion_result["status"] != "success":
                self.logger.warning(f"Flights ingestion failed: {ingestion_result}")
                return
            
            records_ingested = ingestion_result["records"]
            
            # Step 2: Transform
            raw_data = ingestion_result["raw_data"]
            transformation_result = self.pipeline.run_transformation_flights(raw_data)
            
            if transformation_result["status"] != "success":
                self.logger.warning(f"Flights transformation failed: {transformation_result}")
                return
            
            # Step 3: Load to database
            df = transformation_result["dataframe"]
            loading_result = self.pipeline.run_loading_flights(df)
            
            if loading_result["status"] != "success":
                self.logger.warning(f"Flights loading failed: {loading_result}")
                return
            
            records_loaded = loading_result.get("records_loaded", 0)
            
            # Step 4: Store to MinIO
            self.pipeline.run_storage_flights(df)
            
            timestamp_end = datetime.now()
            duration = (timestamp_end - timestamp_start).total_seconds()
            
            self.last_flights_refresh = timestamp_end
            
            self.logger.info(
                f"Flights refresh completed: "
                f"{records_loaded} records loaded in {duration:.1f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Flights refresh failed: {str(e)}")
    
    def get_status(self) -> dict:
        """Get service status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "is_running": self.is_running,
            "last_lightning_refresh": self.last_lightning_refresh,
            "last_flights_refresh": self.last_flights_refresh,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time
                }
                for job in self.scheduler.get_jobs()
            ] if self.is_running else []
        }


# Global service instance
_service_instance: Optional[DataRefreshService] = None
_service_lock = threading.Lock()


def get_refresh_service(config=None) -> DataRefreshService:
    """Get or create the global refresh service instance.
    
    Args:
        config: Configuration object
        
    Returns:
        DataRefreshService instance
    """
    global _service_instance
    
    if _service_instance is None:
        with _service_lock:
            if _service_instance is None:
                _service_instance = DataRefreshService(config)
    
    return _service_instance


if __name__ == "__main__":
    # Example usage: python -m src.utils.refresh_service
    import sys
    from src.utils import setup_logging
    
    # Setup logging
    config = get_config()
    setup_logging(log_file=str(config.LOG_FILE))
    
    # Start service
    service = get_refresh_service(config)
    service.start()
    
    # Keep running
    try:
        print("Data refresh service running. Press Ctrl+C to stop.")
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping service...")
        service.stop()
        sys.exit(0)
