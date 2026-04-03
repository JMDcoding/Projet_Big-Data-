"""
Verify data in database.
Vérifier les données de la base de données.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from src.database.warehouse import DataWarehouse, PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("verify_data")

print("\n" + "="*80)
print("  DATA VERIFICATION")
print("="*80 + "\n")

try:
    logger.info("📡 Connecting to PostgreSQL...")
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
    
    # Check lightning data
    logger.info("⚡ Lightning Strikes:")
    query = "SELECT COUNT(*) FROM lightning_strikes;"
    result = warehouse.db.execute(query)
    lightning_count = result[0][0] if result else 0
    logger.info(f"   Total: {lightning_count}")
    
    if lightning_count > 0:
        query = "SELECT COUNT(DISTINCT source) FROM lightning_strikes;"
        result = warehouse.db.execute(query)
        sources = result[0][0]
        logger.info(f"   Data sources: {sources}")
    
    # Check flights data
    logger.info("\n✈️  Flights:")
    query = "SELECT COUNT(*) FROM flights;"
    result = warehouse.db.execute(query)
    flights_count = result[0][0] if result else 0
    logger.info(f"   Total: {flights_count}")
    
    # Check disruptions
    logger.info("\n🚨 Disruptions:")
    query = "SELECT COUNT(*) FROM flight_disruptions;"
    result = warehouse.db.execute(query)
    disruptions_count = result[0][0] if result else 0
    logger.info(f"   Total: {disruptions_count}")
    
    # Summary
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    logger.info(f"Lightning Strikes: {lightning_count}")
    logger.info(f"Flights: {flights_count}")
    logger.info(f"Disruptions: {disruptions_count}")
    
    if lightning_count == 0:
        logger.warning("\n💡 Tip: Run 'python scripts/populate_demo.py' to load demo data")
    
    db_conn.disconnect()

except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
