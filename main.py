"""
Main pipeline orchestrator for lightning data processing.
Uses local demo data by default, with fallback to APIs.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.utils.logger import setup_logging
from src.ingestion.api_client import LocalDemoData, BlitzortungAPI, OpenMeteoAPI, OpenSkyAPI, SyntheticFlightData
from src.storage.data_lake import JSONDataLake, CSVDataLake, MinIODataLake
from src.transformation.transformer import LightningDataTransformer
from src.transformation.disruption_calculator import DisruptionCalculator

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
    1. Fetch data from source (Local Demo -> Blitzortung API -> Open-Meteo)
    2. Validate and transform data
    3. Store in Data Lake (JSON/CSV)
    4. Load into PostgreSQL Data Warehouse
    """
    
    def __init__(self, config=None):
        """Initialize the pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.logger = setup_logging(log_file=str(self.config.LOG_FILE))
        
        self.logger.info("=" * 70)
        self.logger.info("LIGHTNING DATA PIPELINE INITIALIZED")
        self.logger.info("=" * 70)
        
        # Initialize data sources (in priority order)
        self.data_sources = {
            "local_demo": LocalDemoData(data_dir=self.config.DATA_RAW_PATH),
            "blitzortung": BlitzortungAPI(),
            "open_meteo": OpenMeteoAPI()
        }
        
        # Initialize flight data sources (in priority order)
        self.flight_sources = {
            "opensky": OpenSkyAPI(),
            "synthetic": SyntheticFlightData()
        }
        
        # Initialize storage (JSON/CSV in local file system)
        self.json_lake = JSONDataLake(self.config.DATA_RAW_PATH)
        self.csv_lake = CSVDataLake(self.config.DATA_RAW_PATH)
        
        # Initialize MinIO storage (object storage)
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
    
    def run_ingestion(self, source_priority: list = None) -> dict:
        """Run data ingestion from available sources.
        
        Try sources in priority order: local_demo -> blitzortung -> open_meteo
        
        Args:
            source_priority: List of source names to try (default: all)
            
        Returns:
            Dictionary with ingestion results
        """
        if source_priority is None:
            source_priority = ["local_demo", "blitzortung", "open_meteo"]
        
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
        
        if not raw_data or not raw_data.get("strikes"):
            self.logger.error("No data source was successful!")
            return {
                "status": "failed",
                "message": "No data available from any source",
                "records": 0
            }
        
        self.logger.info(f"Using data from: {source_used}")
        
        # Save raw data
        try:
            timestamp = datetime.now().isoformat().replace(":", "-")
            filename = f"lightning_raw_{timestamp}"
            self.json_lake.save(raw_data, filename)
            self.logger.info(f"Raw data saved to: {filename}.json")
        except Exception as e:
            self.logger.warning(f"Failed to save raw data: {str(e)}")
        
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
                error_msg = "MinIO is REQUIRED but not available. Cannot proceed."
                self.logger.error(error_msg)
                return {
                    "status": "failed",
                    "error": error_msg,
                    "records": 0
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
        """Run flight data ingestion from available sources.
        
        Try sources in priority order: opensky -> synthetic
        
        Args:
            source_priority: List of source names to try (default: all)
            
        Returns:
            Dictionary with ingestion results
        """
        if source_priority is None:
            source_priority = ["opensky", "synthetic"]
        
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
        
        if not flight_data or not flight_data.get("flights"):
            self.logger.error("No flight data source was successful!")
            return {
                "status": "failed",
                "message": "No flight data available from any source",
                "records": 0
            }
        
        self.logger.info(f"Using flight data from: {source_used}")
        
        # Save raw data
        try:
            timestamp = datetime.now().isoformat().replace(":", "-")
            filename = f"flights_raw_{timestamp}"
            self.json_lake.save(flight_data, filename)
            self.logger.info(f"Raw flight data saved to: {filename}.json")
        except Exception as e:
            self.logger.warning(f"Failed to save raw flight data: {str(e)}")
        
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
    
    def run_loading_flights(self, df) -> dict:
        """Load transformed flight data into PostgreSQL.
        
        Args:
            df: Transformed flight DataFrame
            
        Returns:
            Dictionary with loading results
        """
        self.logger.info("Flight Database Loading")
        self.logger.info("-" * 70)
        
        if not self.warehouse:
            self.logger.warning("Database not connected. Skipping flight database loading.")
            return {"status": "skipped", "reason": "database_not_connected"}
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            self.logger.info(f"Loading {len(records)} flight records into PostgreSQL")
            
            # Insert into database
            self.warehouse.insert_flights_data(records)
            
            self.logger.info(f"[OK] Successfully loaded {len(records)} flight records")
            
            return {
                "status": "success",
                "records_loaded": len(records)
            }
        
        except Exception as e:
            self.logger.error(f"Flight database loading failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def run_storage_flights(self, df) -> dict:
        """Store transformed flight data in Data Lake (MinIO ONLY).
        
        IMPORTANT: NO LOCAL STORAGE - All data goes to MinIO
        
        Args:
            df: Transformed flight DataFrame
            
        Returns:
            Dictionary with storage results
        """
        self.logger.info("Flight Data Storage (MinIO ONLY - No Local Storage)")
        self.logger.info("-" * 70)
        
        try:
            # MinIO (object storage) - PRIMARY STORAGE
            if not self.use_minio or not self.minio_lake:
                error_msg = "MinIO is REQUIRED but not available. Cannot proceed."
                self.logger.error(error_msg)
                return {
                    "status": "failed",
                    "error": error_msg,
                    "records": 0
                }
            
            timestamp = datetime.now().isoformat().replace(":", "-")
            
            try:
                # Prepare flight data
                flight_data = df.to_dict('records')
                
                # Save to MinIO (only JSON for flights)
                json_path = f"flights/{timestamp}/processed_flights.json"
                self.minio_lake.save(flight_data, json_path)
                self.logger.info(f"[OK] Flight data saved to MinIO: {json_path}")
                
                return {
                    "status": "success",
                    "minio_path": json_path,
                    "records": len(df),
                    "storage_type": "MinIO (Primary Data Lake)"
                }
            
            except Exception as e:
                self.logger.error(f"MinIO flight storage failed: {str(e)}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "records": 0
                }
        
        except Exception as e:
            self.logger.error(f"Flight storage failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def compute_disruptions(self, lightning_records: list, flights_records: list) -> dict:
        """Calculate flight disruption risks based on lightning strikes.
        
        Args:
            lightning_records: List of lightning strike records from DB
            flights_records: List of flight records from DB
            
        Returns:
            Dictionary with disruption calculation results
        """
        self.logger.info("")
        self.logger.info("DISRUPTION CALCULATION")
        self.logger.info("-" * 70)
        
        try:
            if not lightning_records or not flights_records:
                self.logger.warning("Missing data for disruption calculation")
                return {
                    "status": "success",
                    "disruptions_calculated": 0,
                    "message": "No lightning or flight data to analyze"
                }
            
            # Calculate disruptions
            import pandas as pd
            disruptions = self.disruption_calculator.calculate_disruptions(
                lightning_records,
                flights_records
            )
            
            if disruptions and self.warehouse:
                # Save disruptions to database
                try:
                    self.warehouse.insert_disruptions_data(disruptions)
                    self.logger.info(f"[OK] {len(disruptions)} disruption records saved to database")
                except Exception as e:
                    self.logger.error(f"Failed to save disruptions: {str(e)}")
            
            # Save disruptions to MinIO if available
            if disruptions and self.use_minio and self.minio_lake:
                try:
                    timestamp = datetime.now().isoformat().replace(":", "-")
                    disruption_path = f"disruptions/{timestamp}/calculated_disruptions.json"
                    self.minio_lake.save(disruptions, disruption_path)
                    self.logger.info(f"[OK] Disruptions saved to MinIO: {disruption_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to save disruptions to MinIO: {str(e)}")
            
            return {
                "status": "success",
                "disruptions_calculated": len(disruptions),
                "critical_flights": len([d for d in disruptions if d.get("risk_level") == "CRITICAL"]),
                "high_risk_flights": len([d for d in disruptions if d.get("risk_level") == "HIGH"])
            }
        
        except Exception as e:
            self.logger.error(f"Disruption calculation failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "disruptions_calculated": 0
            }
    
    def run(self, include_database=True) -> dict:
        """Run the complete pipeline.
        
        Args:
            include_database: Whether to load data into database
            
        Returns:
            Dictionary with pipeline results
        """
        try:
            results = {"started_at": datetime.now().isoformat()}
            
            # Phase 1: Ingestion
            ingestion_result = self.run_ingestion()
            results["ingestion"] = ingestion_result
            
            if ingestion_result["status"] != "success":
                self.logger.error("Pipeline failed at ingestion phase")
                results["status"] = "failed"
                return results
            
            raw_data = ingestion_result["raw_data"]
            
            # Phase 2: Transformation
            transformation_result = self.run_transformation(raw_data)
            results["transformation"] = transformation_result
            
            if transformation_result["status"] != "success":
                self.logger.error("Pipeline failed at transformation phase")
                results["status"] = "failed"
                return results
            
            df = transformation_result["dataframe"]
            
            # Store for disruption calculation
            self.last_lightning_df = df
            
            # Phase 3: Storage
            storage_result = self.run_storage(df)
            results["storage"] = storage_result
            
            # Phase 4: Database Loading (optional)
            if include_database:
                self.connect_database()
                loading_result = self.run_loading(df)
                results["loading"] = loading_result
            
            # ========== FLIGHT DATA PIPELINE ==========
            
            # Flight Phase 1: Ingestion
            flight_ingestion_result = self.run_ingestion_flights()
            results["flight_ingestion"] = flight_ingestion_result
            
            if flight_ingestion_result["status"] == "success":
                flight_raw_data = flight_ingestion_result["raw_data"]
                
                # Flight Phase 2: Transformation
                flight_transformation_result = self.run_transformation_flights(flight_raw_data)
                results["flight_transformation"] = flight_transformation_result
                
                if flight_transformation_result["status"] == "success":
                    flight_df = flight_transformation_result["dataframe"]
                    
                    # Store for disruption calculation
                    self.last_flights_df = flight_df
                    
                    # Flight Phase 3: Storage
                    flight_storage_result = self.run_storage_flights(flight_df)
                    results["flight_storage"] = flight_storage_result
                    
                    # Flight Phase 4: Database Loading
                    if include_database and self.warehouse:
                        flight_loading_result = self.run_loading_flights(flight_df)
                        results["flight_loading"] = flight_loading_result
            
            # ========== DISRUPTION ANALYSIS ==========
            # Calculate flight disruptions based on lightning strikes
            if self.last_lightning_df is not None and self.last_flights_df is not None:
                try:
                    lightning_data = self.last_lightning_df.to_dict('records')
                    flights_data = self.last_flights_df.to_dict('records')
                    
                    if lightning_data and flights_data:
                        disruption_result = self.compute_disruptions(lightning_data, flights_data)
                        results["disruptions"] = disruption_result
                except Exception as e:
                    self.logger.error(f"Disruption analysis skipped: {str(e)}")
            
            # Summary
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("PIPELINE EXECUTION SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info("")
            self.logger.info("LIGHTNING DATA:")
            self.logger.info(f"  Source: {ingestion_result['source']}")
            self.logger.info(f"  Records Ingested: {ingestion_result['records']}")
            self.logger.info(f"  Records Transformed: {transformation_result['records']}")
            self.logger.info(f"  Records Stored: {storage_result.get('records', 0)}")
            if include_database:
                self.logger.info(f"  Records Loaded to DB: {loading_result.get('records_loaded', 0)}")
            self.logger.info("")
            self.logger.info("FLIGHT DATA:")
            if flight_ingestion_result["status"] == "success":
                self.logger.info(f"  Source: {flight_ingestion_result['source']}")
                self.logger.info(f"  Records Ingested: {flight_ingestion_result['records']}")
                if flight_transformation_result["status"] == "success":
                    self.logger.info(f"  Records Transformed: {flight_transformation_result['records']}")
                    if include_database and "flight_loading" in results:
                        self.logger.info(f"  Records Loaded to DB: {results['flight_loading'].get('records_loaded', 0)}")
            else:
                self.logger.warning(f"  Status: {flight_ingestion_result['message']}")
            self.logger.info("=" * 70)
            
            results["status"] = "success"
            results["completed_at"] = datetime.now().isoformat()
            
            return results
        
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            }
        
        finally:
            # Cleanup
            if self.db_connection:
                self.db_connection.disconnect()


def main():
    """Main entry point."""
    try:
        # Initialize pipeline
        config = get_config()
        pipeline = DataPipeline(config)
        
        # Run complete pipeline
        results = pipeline.run(include_database=True)
        
        # Print final status
        if results["status"] == "success":
            print("\n[OK] PIPELINE COMPLETED SUCCESSFULLY")
            sys.exit(0)
        else:
            print("\n[ERROR] PIPELINE FAILED")
            print(f"Error: {results.get('error', 'Unknown error')}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
