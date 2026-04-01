"""
Main pipeline orchestrator.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.utils import setup_logging, logger
from src.ingestion import BlitzortungAPI
from src.storage import JSONDataLake, CSVDataLake
from src.transformation import LightningDataTransformer, DataMerger
from src.database import PostgreSQLConnection, DataWarehouse


class DataPipeline:
    """Main data pipeline orchestrator."""
    
    def __init__(self, config=None):
        """Initialize the pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.api_client = BlitzortungAPI(
            base_url=self.config.API_BASE_URL,
            timeout=self.config.API_TIMEOUT
        )
        
        self.json_lake = JSONDataLake(self.config.DATA_RAW_PATH)
        self.csv_lake = CSVDataLake(self.config.DATA_RAW_PATH)
        
        self.lightning_transformer = LightningDataTransformer()
        
        # Database (will be connected when needed)
        self.db_connection = None
        self.warehouse = None
        
        self.logger.info("Pipeline initialized")
    
    def connect_database(self):
        """Connect to PostgreSQL database."""
        try:
            self.db_connection = PostgreSQLConnection(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            self.db_connection.connect()
            self.warehouse = DataWarehouse(self.db_connection)
            self.logger.info("Database connected and warehouse initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def run_ingestion(self):
        """Run data ingestion from API.
        
        Returns:
            Extracted data
        """
        try:
            self.logger.info("Starting data ingestion...")
            
            # Fetch from API
            raw_data = self.api_client.extract()
            
            # Save raw data
            timestamp = datetime.now().isoformat().replace(":", "-")
            filename = f"lightning_raw_{timestamp}"
            self.json_lake.save(raw_data, filename)
            
            self.logger.info("Data ingestion completed successfully")
            return raw_data
        
        except Exception as e:
            self.logger.error(f"Ingestion failed: {str(e)}")
            raise
    
    def run_transformation(self, raw_data):
        """Transform raw data.
        
        Args:
            raw_data: Raw data from ingestion
            
        Returns:
            Transformed DataFrame
        """
        try:
            self.logger.info("Starting data transformation...")
            
            # Transform data
            df_transformed = self.lightning_transformer.transform(raw_data)
            
            self.logger.info(f"Transformation completed: {len(df_transformed)} records")
            return df_transformed
        
        except Exception as e:
            self.logger.error(f"Transformation failed: {str(e)}")
            raise
    
    def run_loading(self, df_transformed):
        """Load data to database.
        
        Args:
            df_transformed: Transformed DataFrame
        """
        try:
            if not self.warehouse:
                self.connect_database()
            
            self.logger.info("Starting data loading to database...")
            
            # Create tables if they don't exist
            self.warehouse.create_lightning_table()
            self.warehouse.create_flights_table()
            self.warehouse.create_disruptions_table()
            
            # Convert DataFrame to list of dicts
            data = df_transformed.to_dict("records")
            
            # Insert data
            self.warehouse.insert_lightning_data(data)
            
            self.logger.info("Data loading completed successfully")
        
        except Exception as e:
            self.logger.error(f"Loading failed: {str(e)}")
            raise
    
    def run_full_pipeline(self):
        """Run the complete pipeline.
        
        Returns:
            Transformed data
        """
        try:
            self.logger.info("=" * 50)
            self.logger.info("STARTING DATA PIPELINE")
            self.logger.info("=" * 50)
            
            # 1. Ingestion
            raw_data = self.run_ingestion()
            
            # 2. Transformation
            df_transformed = self.run_transformation(raw_data)
            
            # 3. Loading
            self.run_loading(df_transformed)
            
            self.logger.info("=" * 50)
            self.logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 50)
            
            return df_transformed
        
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {str(e)}")
            raise
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.api_client.close()
            if self.db_connection:
                self.db_connection.disconnect()
            self.logger.info("Resources cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    # Setup logging
    config = get_config()
    setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
    
    # Run pipeline
    pipeline = DataPipeline(config)
    try:
        result = pipeline.run_full_pipeline()
        print("\n✅ Pipeline completed successfully!")
        print(f"📊 Processed {len(result)} records")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)
