"""
Main pipeline orchestrator - FIXED VERSION with demo fallback.
Uses real APIs when available, fallback to demo data when not.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.utils.logger import setup_logging
from src.ingestion.api_client import BlitzortungAPI, OpenMeteoAPI, AviationStackAPI
from src.ingestion.alternative_apis import OpenSkyAlternative
from src.storage.data_lake import JSONDataLake, CSVDataLake, MinIODataLake
from src.transformation.transformer import LightningDataTransformer
from src.transformation.disruption_calculator import DisruptionCalculator
from src.transformation.trajectory_predictor import TrajectoryPredictor

# Try to import database modules
try:
    from src.database.warehouse import PostgreSQLConnection, DataWarehouse
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    PostgreSQLConnection = None
    DataWarehouse = None


class DataPipeline:
    """Main data pipeline orchestrator.
    
    Workflow:
    1. Fetch data from source (Real APIs -> Fallback to Demo)
    2. Validate and transform data
    3. Store in Data Lake (JSON/CSV)
    4. Load into PostgreSQL Data Warehouse
    """
    
    def __init__(self, config=None, use_demo_fallback=True):
        """Initialize the pipeline.
        
        Args:
            config: Configuration object
            use_demo_fallback: Use demo data if real APIs fail
        """
        self.config = config or get_config()
        self.logger = setup_logging(log_file=str(self.config.LOG_FILE))
        self.use_demo_fallback = use_demo_fallback
        
        self.logger.info("=" * 70)
        self.logger.info("LIGHTNING DATA PIPELINE INITIALIZED (FIXED)")
        self.logger.info("=" * 70)
        
        # Initialize data sources (APIs only - no demo/test data)
        self.data_sources = {
            "blitzortung": BlitzortungAPI(),
            "open_meteo": OpenMeteoAPI()
        }
        
        # Initialize flight data sources (OpenSky Network - unlimited)
        self.flight_sources = {
            "opensky": OpenSkyAlternative(lat=48.8527, lon=2.3510, radius_km=100)
        }
        
        # Initialize MinIO storage (object storage) - PRIMARY DATA LAKE
        try:
            self.minio_lake = MinIODataLake(
                minio_host="localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                bucket_name="lightning-data"
            )
            self.logger.info("MinIO storage enabled")
            self.use_minio = True
        except Exception as e:
            self.logger.warning(f"MinIO not available: {str(e)} - Using local file system only")
            self.minio_lake = None
            self.use_minio = False
        
        # Initialize transformer
        self.lightning_transformer = LightningDataTransformer()
        
        # Initialize disruption calculator
        self.disruption_calculator = DisruptionCalculator()
        
        # Initialize trajectory predictor (for flight path analysis)
        self.trajectory_predictor = TrajectoryPredictor()
        
        # Store transformed data for disruption calculation
        self.last_lightning_df = None
        self.last_flights_df = None
        
        # Database (will be connected when needed)
        self.db_connection = None
        self.warehouse = None
        
        self.logger.info("Pipeline initialized successfully")
    
    def connect_database(self) -> bool:
        """Connect to PostgreSQL database.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not HAS_DATABASE:
            self.logger.warning("PostgreSQL module not available. Database loading skipped.")
            return False
        
        try:
            self.logger.info(f"Connecting to PostgreSQL at {self.config.DB_HOST}:{self.config.DB_PORT}/{self.config.DB_NAME}")
            
            self.db_connection = PostgreSQLConnection(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            self.db_connection.connect()
            self.warehouse = DataWarehouse(self.db_connection)
            
            self.logger.info("Database connected successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            self.logger.warning("Pipeline will continue without database.")
            return False
    
    def generate_demo_lightning_data(self, count=50) -> dict:
        """Generate realistic demo lightning data for testing.
        
        Args:
            count: Number of strike records to generate
            
        Returns:
            Dictionary with demo lightning data
        """
        self.logger.info(f"[FALLBACK] Generating {count} demo lightning strikes...")
        
        strikes = []
        now = datetime.now()
        
        for i in range(count):
            # Generate strikes around Lyon area (45.764, 4.8357)
            lat = 45.764 + (i % 5 - 2) * 0.05
            lon = 4.8357 + (i % 7 - 3) * 0.05
            
            strike = {
                "id": f"demo_strike_{i:05d}",
                "latitude": lat,
                "longitude": lon,
                "altitude": 0,
                "timestamp": (now - timedelta(minutes=i)).isoformat(),
                "distance": 0,
                "signal": 50,
                "source": "demo_fallback"
            }
            strikes.append(strike)
        
        return {
            "strikes": strikes,
            "source": "demo_fallback",
            "timestamp": now.isoformat()
        }
    
    def generate_demo_flights_data(self, count=20) -> dict:
        """Generate realistic demo flight data for testing.
        
        Args:
            count: Number of flight records to generate
            
        Returns:
            Dictionary with demo flight data
        """
        self.logger.info(f"[FALLBACK] Generating {count} demo flights...")
        
        flights = []
        now = datetime.now()
        
        for i in range(count):
            flight = {
                "flight_number": f"DEMO{i:03d}",
                "departure": "CDG",
                "arrival": "ORY",
                "latitude": 48.8527 + (i % 5 - 2) * 0.02,
                "longitude": 2.3510 + (i % 7 - 3) * 0.02,
                "altitude": 1000 + (i * 100),
                "velocity": 400 + (i * 5),
                "heading": (i * 18) % 360,
                "timestamp": now.isoformat(),
                "source": "demo_fallback"
            }
            flights.append(flight)
        
        return {
            "flights": flights,
            "source": "demo_fallback",
            "timestamp": now.isoformat()
        }
    
    def run_ingestion(self, source_priority: list = None) -> dict:
        """Run data ingestion from available APIs.
        
        Try sources in priority order: blitzortung -> open_meteo
        Falls back to demo data if use_demo_fallback=True
        
        Args:
            source_priority: List of source names to try (default: all)
            
        Returns:
            Dictionary with ingestion results
        """
        if source_priority is None:
            source_priority = ["blitzortung", "open_meteo"]
        
        self.logger.info("")
        self.logger.info("PHASE 1: DATA INGESTION")
        self.logger.info("-" * 70)
        
        raw_data = None
        source_used = None
        
        # Try each source in priority order
        for source_name in source_priority:
            if source_name not in self.data_sources:
                continue
            
            try:
                self.logger.info(f"Trying data source: {source_name}")
                source = self.data_sources[source_name]
                
                # Extract and validate
                result = source.extract()
                
                # Check if we got data
                if isinstance(result, dict) and "strikes" in result and result["strikes"]:
                    self.logger.info(f"[OK] {source_name}: {len(result['strikes'])} lightning strikes fetched")
                    raw_data = result
                    source_used = source_name
                    break
                elif isinstance(result, dict) and "error" not in result:
                    self.logger.warning(f"[SKIP] {source_name}: No data returned")
                else:
                    self.logger.warning(f"[SKIP] {source_name}: Error - {result.get('error')}")
            
            except Exception as e:
                self.logger.warning(f"[SKIP] {source_name}: Exception - {str(e)}")
        
        # Fallback to demo data if enabled
        if not raw_data or not raw_data.get("strikes"):
            if self.use_demo_fallback:
                return self.generate_demo_lightning_data(count=50)
            else:
                self.logger.error("No data source was successful!")
                return {
                    "status": "failed",
                    "message": "No data available from any source",
                    "records": 0
                }
        
        self.logger.info(f"Using data from: {source_used}")
        
        return {
            "status": "success",
            "source": source_used,
            "records": len(raw_data.get("strikes", [])),
            "raw_data": raw_data
        }
    
    def run_transformation(self, raw_data: dict) -> dict:
        """Run data transformation.
        
        Args:
            raw_data: Raw data from ingestion
            
        Returns:
            Dictionary with transformation results
        """
        self.logger.info("")
        self.logger.info("PHASE 2: DATA TRANSFORMATION")
        self.logger.info("-" * 70)
        
        try:
            strikes = raw_data.get("strikes", [])
            
            if not strikes:
                self.logger.error("No strikes data to transform")
                return {"status": "failed", "records": 0}
            
            self.logger.info(f"Starting transformation of {len(strikes)} records")
            
            # Transform data
            df = self.lightning_transformer.transform(strikes)
            
            self.logger.info(f"[OK] Transformed {len(df)} records")
            self.logger.info(f"Columns: {list(df.columns)}")
            
            return {
                "status": "success",
                "records": len(df),
                "dataframe": df,
                "columns": list(df.columns)
            }
        
        except Exception as e:
            self.logger.error(f"Transformation failed: {str(e)}")
            return {"status": "failed", "error": str(e), "records": 0}
    
    def run_storage(self, df) -> dict:
        """Store transformed data in Data Lake (MinIO ONLY).
        
        IMPORTANT: NO LOCAL STORAGE - All data goes to MinIO
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            Dictionary with storage results
        """
        self.logger.info("")
        self.logger.info("PHASE 3: DATA STORAGE (MinIO ONLY - No Local Storage)")
        self.logger.info("-" * 70)
        
        try:
            timestamp = datetime.now().isoformat().replace(":", "-")
            
            # MinIO (object storage) - PRIMARY STORAGE
            if not self.use_minio or not self.minio_lake:
                self.logger.warning("MinIO not available. Skipping MinIO storage.")
                return {
                    "status": "skipped",
                    "reason": "minio_unavailable",
                    "records": len(df)
                }
            
            try:
                # Save JSON to MinIO
                json_data = df.to_dict('records')
                json_file = f"lightning/{timestamp}/processed_lightning.json"
                self.minio_lake.save(json_data, json_file)
                self.logger.info(f"[OK] Data saved to MinIO: {json_file}")
                
                # Save CSV to MinIO
                csv_file = f"lightning/{timestamp}/processed_lightning.csv"
                self.minio_lake.save(df.to_dict('records'), csv_file)
                self.logger.info(f"[OK] Data saved to MinIO: {csv_file}")
                
                # Log bucket info
                bucket_info = self.minio_lake.get_bucket_info()
                self.logger.info(f"MinIO Bucket Stats: {bucket_info.get('object_count')} objects, "
                               f"{bucket_info.get('total_size_mb', 0):.2f} MB used")
                
                return {
                    "status": "success",
                    "minio_json": json_file,
                    "minio_csv": csv_file,
                    "records": len(df),
                    "storage_type": "MinIO (Primary Data Lake)"
                }
            
            except Exception as e:
                self.logger.error(f"MinIO storage failed: {str(e)}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "records": 0
                }
        
        except Exception as e:
            self.logger.error(f"Storage failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def run_loading(self, df) -> dict:
        """Load transformed data into PostgreSQL.
        
        Args:
            df: Transformed DataFrame
            
        Returns:
            Dictionary with loading results
        """
        self.logger.info("")
        self.logger.info("PHASE 4: DATABASE LOADING")
        self.logger.info("-" * 70)
        
        if not self.warehouse:
            self.logger.warning("Database not connected. Skipping database loading.")
            return {"status": "skipped", "reason": "database_not_connected"}
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            self.logger.info(f"Loading {len(records)} records into PostgreSQL")
            
            # Insert into database
            self.warehouse.insert_lightning_data(records)
            
            self.logger.info(f"[OK] Successfully loaded {len(records)} records")
            
            return {
                "status": "success",
                "records_loaded": len(records)
            }
        
        except Exception as e:
            self.logger.error(f"Database loading failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def run_ingestion_flights(self, source_priority: list = None) -> dict:
        """Run flight data ingestion.
        
        Try sources in priority order: opensky
        Falls back to demo data if use_demo_fallback=True
        
        Args:
            source_priority: List of source names to try (default: all)
            
        Returns:
            Dictionary with ingestion results
        """
        if source_priority is None:
            source_priority = ["opensky"]
        
        self.logger.info("")
        self.logger.info("FLIGHT DATA INGESTION")
        self.logger.info("-" * 70)
        
        flight_data = None
        source_used = None
        
        # Try each source in priority order
        for source_name in source_priority:
            if source_name not in self.flight_sources:
                continue
            
            try:
                self.logger.info(f"Trying flight source: {source_name}")
                source = self.flight_sources[source_name]
                
                # Extract and validate
                result = source.extract()
                
                # Check if we got data
                if isinstance(result, dict) and "flights" in result and result["flights"]:
                    self.logger.info(f"[OK] {source_name}: {len(result['flights'])} flights fetched")
                    flight_data = result
                    source_used = source_name
                    break
                elif isinstance(result, dict) and "error" not in result:
                    self.logger.warning(f"[SKIP] {source_name}: No data returned")
                else:
                    self.logger.warning(f"[SKIP] {source_name}: Error - {result.get('error')}")
            
            except Exception as e:
                self.logger.warning(f"[SKIP] {source_name}: Exception - {str(e)}")
        
        # Fallback to demo data if enabled
        if not flight_data or not flight_data.get("flights"):
            if self.use_demo_fallback:
                return self.generate_demo_flights_data(count=20)
            else:
                self.logger.error("No flight data source was successful!")
                return {
                    "status": "failed",
                    "message": "No flight data available from any source",
                    "records": 0
                }
        
        self.logger.info(f"Using flight data from: {source_used}")
        
        return {
            "status": "success",
            "source": source_used,
            "records": len(flight_data.get("flights", [])),
            "raw_data": flight_data
        }
    
    def run_transformation_flights(self, raw_data: dict) -> dict:
        """Run flight data transformation.
        
        Args:
            raw_data: Raw flight data from ingestion
            
        Returns:
            Dictionary with transformation results
        """
        self.logger.info("Flight Data Transformation")
        self.logger.info("-" * 70)
        
        try:
            flights = raw_data.get("flights", [])
            
            if not flights:
                self.logger.error("No flights data to transform")
                return {"status": "failed", "records": 0}
            
            self.logger.info(f"Starting transformation of {len(flights)} flight records")
            
            # Convert to DataFrame with proper format
            import pandas as pd
            df = pd.DataFrame(flights)
            
            # Ensure required columns
            required_cols = ["flight_number", "departure", "arrival", "latitude", "longitude", 
                           "altitude", "velocity", "heading", "timestamp", "source"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = None
            
            # Convert timestamp to datetime if needed
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            
            self.logger.info(f"[OK] Transformed {len(df)} flight records")
            self.logger.info(f"Columns: {list(df.columns)}")
            
            return {
                "status": "success",
                "records": len(df),
                "dataframe": df,
                "columns": list(df.columns)
            }
        
        except Exception as e:
            self.logger.error(f"Flight transformation failed: {str(e)}")
            return {"status": "failed", "error": str(e), "records": 0}
    
    def run(self, with_flights=True) -> bool:
        """Run the full pipeline.
        
        Args:
            with_flights: Whether to also ingest flight data
            
        Returns:
            True if pipeline succeeded, False otherwise
        """
        try:
            # Connect database
            self.connect_database()
            
            # ===== LIGHTNING DATA =====
            # Phase 1: Ingestion
            ingestion_result = self.run_ingestion()
            if not ingestion_result.get("strikes"):
                self.logger.error("Pipeline failed at ingestion phase")
                return False
            
            # Phase 2: Transformation
            transformation_result = self.run_transformation(ingestion_result)
            if transformation_result.get("status") == "failed":
                self.logger.error("Pipeline failed at transformation phase")
                return False
            
            df = transformation_result.get("dataframe")
            self.last_lightning_df = df
            
            # Phase 3: Storage
            storage_result = self.run_storage(df)
            self.logger.info(f"Storage result: {storage_result.get('status')}")
            
            # Phase 4: Database Loading
            loading_result = self.run_loading(df)
            self.logger.info(f"Loading result: {loading_result.get('status')}")
            
            # ===== FLIGHT DATA =====
            if with_flights:
                # Phase 1: Flight Ingestion
                flight_ingestion_result = self.run_ingestion_flights()
                if flight_ingestion_result.get("flights"):
                    # Phase 2: Flight Transformation
                    flight_transformation_result = self.run_transformation_flights(flight_ingestion_result)
                    if flight_transformation_result.get("status") != "failed":
                        self.last_flights_df = flight_transformation_result.get("dataframe")
            
            # Final summary
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 70)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            return False
        
        finally:
            # Cleanup database connection
            if self.db_connection:
                try:
                    self.db_connection.disconnect()
                except:
                    pass


def main():
    """Main entry point for the pipeline."""
    pipeline = DataPipeline(use_demo_fallback=True)
    
    success = pipeline.run()
    
    if success:
        print("\n[OK] PIPELINE EXECUTION SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n[ERROR] PIPELINE FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
