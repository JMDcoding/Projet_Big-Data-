import psycopg2
from config.config import Config

conn = psycopg2.connect(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD
)
cursor = conn.cursor()

# Get all tables
cursor.execute("""
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public'
""")
tables = cursor.fetchall()
print('Available tables:')
for t in tables:
    print(f'  - {t[0]}')

# Check flight_disruptions columns
print('\nFlight_disruptions columns:')
cursor.execute("""
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'flight_disruptions'
ORDER BY ordinal_position
""")
cols = cursor.fetchall()
for c in cols:
    print(f'  - {c[0]:25} ({c[1]})')

cursor.close()
conn.close()
