#!/usr/bin/env python3
"""
Completely reset the lightning table and refill with fresh data from Open-Meteo API.
Réinitialise complètement la table d'éclairs et la remplit avec des données fraîches.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("reset_lightning_table")


def drop_and_recreate_lightning_table(db_conn):
    """Drop and recreate the lightning_strikes table from scratch.
    
    Args:
        db_conn: PostgreSQL connection
        
    Returns:
        True if successful, False otherwise
    """
    logger.info("📋 Dropping and recreating lightning_strikes table...")
    
    try:
        cursor = db_conn.connection.cursor()
        
        # Step 1: Drop dependent tables first
        logger.info("   1. Dropping dependent tables...")
        
        # Drop flight_disruptions first (references flights and lightning)
        try:
            cursor.execute("DROP TABLE IF EXISTS flight_disruptions CASCADE;")
            db_conn.connection.commit()
            logger.info("   ✓ Dropped flight_disruptions table")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not drop flight_disruptions: {str(e)}")
            db_conn.connection.rollback()
        
        # Step 2: Drop lightning_strikes table
        logger.info("   2. Dropping lightning_strikes table...")
        try:
            cursor.execute("DROP TABLE IF EXISTS lightning_strikes CASCADE;")
            db_conn.connection.commit()
            logger.info("   ✓ Dropped lightning_strikes table")
        except Exception as e:
            logger.error(f"   ❌ Error dropping table: {str(e)}")
            db_conn.connection.rollback()
            return False
        
        # Step 3: Recreate the table with proper schema
        logger.info("   3. Recreating lightning_strikes table...")
        
        create_table_sql = """
        CREATE TABLE lightning_strikes (
            lightning_id VARCHAR(255) PRIMARY KEY,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            altitude DECIMAL(10, 4),
            intensity DECIMAL(5, 2) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            source VARCHAR(100),
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            cursor.execute(create_table_sql)
            db_conn.connection.commit()
            logger.info("   ✓ Created new lightning_strikes table")
        except Exception as e:
            logger.error(f"   ❌ Error creating table: {str(e)}")
            db_conn.connection.rollback()
            return False
        
        # Create index on timestamp for faster queries (separate commits)
        logger.info("   4. Creating indexes...")
        try:
            cursor.execute("CREATE INDEX idx_lightning_timestamp ON lightning_strikes(timestamp);")
            db_conn.connection.commit()
            logger.info("   ✓ Created timestamp index")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not create timestamp index: {str(e)}")
            db_conn.connection.rollback()
        
        try:
            cursor.execute("CREATE INDEX idx_lightning_intensity ON lightning_strikes(intensity);")
            db_conn.connection.commit()
            logger.info("   ✓ Created intensity index")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not create intensity index: {str(e)}")
            db_conn.connection.rollback()
        
        # Verify the table exists and is empty
        cursor.execute("SELECT COUNT(*) FROM lightning_strikes;")
        count = cursor.fetchone()[0]
        logger.info(f"   ✓ Table ready: {count} records (should be 0)")
        
        cursor.close()
        return True
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        db_conn.connection.rollback()
        return False


def main():
    """Main execution."""
    print("\n" + "="*80)
    print("  RESET LIGHTNING TABLE - DROP AND RECREATE")
    print("="*80 + "\n")
    
    try:
        # Connect to database
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
        
        # Drop and recreate
        success = drop_and_recreate_lightning_table(db_conn)
        
        if success:
            logger.info("\n✅ Lightning table successfully reset!")
            logger.info("\n📝 Next step: Run 'python fetch_real_lightning.py' to populate with new data")
        else:
            logger.error("\n❌ Failed to reset lightning table")
        
        db_conn.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
