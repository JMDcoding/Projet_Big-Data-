"""
Database initialization script.
Creates all tables in PostgreSQL at startup.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse
from src.utils.logger import setup_logging

# Setup logging
logger = setup_logging(log_file=str(Config.LOG_FILE), level=Config.LOG_LEVEL)


def initialize_database():
    """Initialize database with all required tables."""
    
    try:
        logger.info("Starting database initialization...")
        
        # Create PostgreSQL connection
        logger.info(f"Connecting to PostgreSQL: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        
        db_connection = PostgreSQLConnection(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        
        # Connect to database
        db_connection.connect()
        
        # Initialize Data Warehouse
        warehouse = DataWarehouse(db_connection)
        
        # Create all tables and indexes
        success = warehouse.initialize_database()
        
        # Check table status
        if success:
            logger.info("")
            logger.info("Database Status:")
            status = warehouse.check_table_status()
            for table_name, table_info in status.items():
                if isinstance(table_info, dict) and "error" not in table_info:
                    row_count = table_info.get("row_count", 0)
                    columns = len(table_info.get("columns", []))
                    logger.info(f"  [OK] {table_name}: {row_count} rows, {columns} columns")
        
        # Disconnect
        db_connection.disconnect()
        
        logger.info("")
        logger.info("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        logger.info("All tables created and ready for data ingestion.")
        
        return True
        
    except Exception as e:
        logger.error(f"DATABASE INITIALIZATION FAILED: {str(e)}")
        logger.error("Make sure PostgreSQL is running and your .env file is configured correctly.")
        return False


if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
