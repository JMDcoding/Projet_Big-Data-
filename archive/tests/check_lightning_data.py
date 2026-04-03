#!/usr/bin/env python3
"""
Check lightning data in PostgreSQL database.
Vérifier que les données d'éclairs sont bien dans la base de données.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import DataWarehouse, PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("check_lightning_data")


def main():
    """Check lightning data in database."""
    print("\n" + "="*80)
    print("  CHECKING LIGHTNING DATA IN DATABASE")
    print("="*80 + "\n")
    
    try:
        # Connect to database
        logger.info("Connecting to PostgreSQL...")
        db_conn = PostgreSQLConnection(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        db_conn.connect()
        warehouse = DataWarehouse(db_conn)
        logger.info("✅ Connected\n")
        
        # Check lightning table
        logger.info("📊 Checking lightning_strikes table...")
        query = "SELECT COUNT(*) FROM lightning_strikes;"
        result = warehouse.db.execute(query)
        total_count = result[0][0] if result else 0
        logger.info(f"   Total lightning strikes: {total_count}\n")
        
        # Check by source
        logger.info("📍 Lightning data by source:")
        query = "SELECT source, COUNT(*) as count FROM lightning_strikes GROUP BY source;"
        results = warehouse.db.execute(query)
        if results:
            for row in results:
                logger.info(f"   • {row[0]}: {row[1]} records")
        else:
            logger.warning("   No data grouped by source")
        print()
        
        # Check date range
        logger.info("📅 Lightning date range:")
        query = "SELECT MIN(timestamp), MAX(timestamp) FROM lightning_strikes;"
        result = warehouse.db.execute(query)
        if result and result[0][0]:
            min_date = result[0][0]
            max_date = result[0][1]
            logger.info(f"   From: {min_date}")
            logger.info(f"   To:   {max_date}")
        else:
            logger.warning("   No timestamp data found")
        print()
        
        # Check intensity distribution
        logger.info("📊 Lightning intensity distribution:")
        query = """
        SELECT 
            CASE 
                WHEN intensity = 0 THEN 'None (0)'
                WHEN intensity < 20 THEN 'Low (1-19)'
                WHEN intensity < 50 THEN 'Medium (20-49)'
                WHEN intensity < 75 THEN 'High (50-74)'
                ELSE 'Very High (75+)'
            END as intensity_range,
            COUNT(*) as count
        FROM lightning_strikes
        GROUP BY intensity_range
        ORDER BY intensity_range;
        """
        results = warehouse.db.execute(query)
        if results:
            for row in results:
                logger.info(f"   • {row[0]}: {row[1]} records")
        else:
            logger.warning("   No intensity data found")
        print()
        
        # Sample recent data
        logger.info("⚡ Sample of recent lightning strikes (latest 10):")
        query = """
        SELECT timestamp, latitude, longitude, intensity, source
        FROM lightning_strikes
        ORDER BY timestamp DESC
        LIMIT 10;
        """
        results = warehouse.db.execute(query)
        if results:
            for i, row in enumerate(results, 1):
                logger.info(f"   {i}. {row[0]} | Lat: {row[1]:.4f}, Lon: {row[2]:.4f} | Intensity: {row[3]:.1f} | {row[4]}")
        else:
            logger.warning("   No recent data found")
        print()
        
        # Summary
        if total_count > 0:
            logger.info("✅ Lightning data IS present in database")
        else:
            logger.error("❌ NO lightning data found in database")
            logger.error("   Run: python fetch_real_lightning.py")
        
        db_conn.disconnect()
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
