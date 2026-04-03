"""
Populate demo/test data into database.
Charger des données de test dans la base de données.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from config.config import Config
from src.database.warehouse import PostgreSQLConnection
from src.utils.logger import setup_logging

logger = setup_logging("populate_demo")

print("\n" + "="*80)
print("  POPULATE DEMO DATA")
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
    
    # Insert demo lightning data
    logger.info("💾 Inserting demo lightning data...")
    now = datetime.utcnow()
    
    demo_storms = [
        {"zone": "Paris", "lat": 48.8527, "lon": 2.3510, "hour": 0, "intensity": 65},
        {"zone": "Paris", "lat": 48.7, "lon": 2.5, "hour": 6, "intensity": 45},
        {"zone": "Germany", "lat": 52.52, "lon": 13.40, "hour": 2, "intensity": 75},
        {"zone": "Germany", "lat": 52.3, "lon": 13.6, "hour": 8, "intensity": 60},
        {"zone": "Spain", "lat": 40.4168, "lon": -3.7038, "hour": 4, "intensity": 70},
        {"zone": "Italy", "lat": 41.9028, "lon": 12.4964, "hour": 1, "intensity": 80},
    ]
    
    cursor = db_conn.connection.cursor()
    insert_query = """
    INSERT INTO lightning_strikes 
    (lightning_id, latitude, longitude, altitude, intensity, timestamp, source, processed_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (lightning_id) DO NOTHING
    """
    
    for i, storm in enumerate(demo_storms, 1):
        timestamp = now + timedelta(hours=storm['hour'])
        lightning_id = f"{storm['zone'].lower()}_{timestamp.strftime('%Y%m%d_%H%M')}"
        
        cursor.execute(insert_query, (
            lightning_id,
            storm['lat'],
            storm['lon'],
            0,
            storm['intensity'],
            timestamp.isoformat(),
            "Demo-Data",
            datetime.utcnow().isoformat()
        ))
        print(f"  {i:2}. {storm['zone']:12} - Intensity: {storm['intensity']}")
    
    db_conn.connection.commit()
    cursor.close()
    
    logger.info(f"\n✅ Demo data loaded successfully")
    logger.info("\n📊 Next steps:")
    logger.info("   1. Run dashboard: streamlit run app.py")
    logger.info("   2. Go to: http://localhost:8501")
    
    db_conn.disconnect()

except Exception as e:
    logger.error(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
