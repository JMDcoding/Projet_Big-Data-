"""
Database setup and initialization script.
Script d'initialisation de la base de données.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse
from src.utils.logger import setup_logging

logger = setup_logging("setup_database")


def setup_database():
    """Initialize database with all required tables."""
    print("\n" + "="*80)
    print("  DATABASE INITIALIZATION")
    print("="*80 + "\n")
    
    try:
        # Connect
        logger.info("📡 Connecting to PostgreSQL...")
        db_conn = PostgreSQLConnection(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        db_conn.connect()
        logger.info("✅ Connected\n")
        
        # Initialize warehouse
        warehouse = DataWarehouse(db_conn)
        warehouse.initialize_database()
        
        logger.info("\n✅ DATABASE INITIALIZATION COMPLETE")
        db_conn.disconnect()
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
