"""
Reset all data in database.
Réinitialiser complètement la base de données.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from src.database.warehouse import PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("reset_data")

print("\n" + "="*80)
print("  RESET DATABASE")
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
    logger.info("✅ Connected\n")
    
    cursor = db_conn.connection.cursor()
    
    # Clear all data (in dependency order)
    logger.info("🧹 Clearing data...")
    
    try:
        cursor.execute("DELETE FROM flight_disruptions;")
        db_conn.connection.commit()
        logger.info("   ✓ Disruptions cleared")
    except:
        pass
    
    try:
        cursor.execute("DELETE FROM flights;")
        db_conn.connection.commit()
        logger.info("   ✓ Flights cleared")
    except:
        pass
    
    try:
        cursor.execute("DELETE FROM lightning_strikes;")
        db_conn.connection.commit()
        logger.info("   ✓ Lightning strikes cleared")
    except:
        pass
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes;")
    lightning_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM flights;")
    flights_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions;")
    disruptions_count = cursor.fetchone()[0]
    
    logger.info("\n📋 Verification:")
    logger.info(f"   Lightning strikes: {lightning_count}")
    logger.info(f"   Flights: {flights_count}")
    logger.info(f"   Disruptions: {disruptions_count}")
    
    logger.info("\n✅ DATABASE RESET COMPLETE")
    logger.info("\n💡 Next: Run 'python scripts/populate_demo.py' to reload data")
    
    cursor.close()
    db_conn.disconnect()

except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
