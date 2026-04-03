import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from config.config import Config
import psycopg2

try:
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='lightning_strikes'")
    print("LIGHTNING_STRIKES TABLE COLUMNS:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
