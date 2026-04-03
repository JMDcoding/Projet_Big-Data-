#!/usr/bin/env python3
"""
Recreate the flight_disruptions table that was accidentally dropped.
Recréer la table flight_disruptions supprimée accidentellement.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from src.database.warehouse import PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("recreate_flight_disruptions")

print("\n" + "="*80)
print("  RECREATING FLIGHT_DISRUPTIONS TABLE")
print("="*80 + "\n")

try:
    # Connect
    logger.info("📡 Connecting to PostgreSQL...")
    db = PostgreSQLConnection(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    db.connect()
    logger.info("✅ Connected\n")
    
    cursor = db.connection.cursor()
    
    # Step 1: Check if table exists
    logger.info("1️⃣  Checking if flight_disruptions table exists...")
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'flight_disruptions'
        );
    """)
    exists = cursor.fetchone()[0]
    
    if exists:
        logger.info("   ℹ️  Table already exists")
        db.connection.commit()
        db.disconnect()
        print("\n✅ Table flight_disruptions already exists\n")
        sys.exit(0)
    
    # Step 2: Create the table
    logger.info("2️⃣  Creating flight_disruptions table...")
    
    create_table_sql = """
    CREATE TABLE flight_disruptions (
        id SERIAL PRIMARY KEY,
        flight_id VARCHAR(255),
        lightning_id VARCHAR(255),
        distance_km FLOAT,
        time_difference_minutes INTEGER,
        risk_level VARCHAR(50),
        disruption_probability FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        db.connection.commit()
        logger.info("   ✓ Table created successfully")
    except Exception as e:
        logger.error(f"   ❌ Error creating table: {str(e)}")
        db.connection.rollback()
        raise
    
    # Step 3: Create indexes
    logger.info("3️⃣  Creating indexes...")
    
    indexes = [
        "CREATE INDEX idx_disruptions_flight_id ON flight_disruptions(flight_id);",
        "CREATE INDEX idx_disruptions_lightning_id ON flight_disruptions(lightning_id);",
        "CREATE INDEX idx_disruptions_risk_level ON flight_disruptions(risk_level);",
        "CREATE INDEX idx_disruptions_probability ON flight_disruptions(disruption_probability);",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            db.connection.commit()
            logger.info(f"   ✓ Index created")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not create index: {str(e)}")
            db.connection.rollback()
    
    # Step 4: Verify
    logger.info("4️⃣  Verifying table structure...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'flight_disruptions' 
        ORDER BY ordinal_position;
    """)
    
    logger.info("   Columns:")
    for col_name, col_type in cursor.fetchall():
        logger.info(f"     • {col_name}: {col_type}")
    
    db.connection.commit()
    
    # Success
    logger.info("\n✅ FLIGHT_DISRUPTIONS TABLE SUCCESSFULLY RECREATED")
    logger.info("="*80)
    logger.info("\nThe table is now empty and ready to receive disruption data.")
    logger.info("Disruptions will be calculated the next time data is loaded.\n")
    
    cursor.close()
    db.disconnect()

except Exception as e:
    logger.error(f"❌ Fatal error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
