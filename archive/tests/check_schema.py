#!/usr/bin/env python
"""Check lightning table schema."""
from src.database.warehouse import PostgreSQLConnection
from config.config import get_config

config = get_config()
db = PostgreSQLConnection(
    host=config.DB_HOST, 
    port=config.DB_PORT, 
    database=config.DB_NAME, 
    user=config.DB_USER, 
    password=config.DB_PASSWORD
)
db.connect()

# Check lightning table structure
cursor = db.connection.cursor()
query = """
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'lightning'
ORDER BY ordinal_position
"""
cursor.execute(query)

cols = cursor.fetchall()
print('\nLightning Table Columns:')
print("-" * 50)
for col in cols:
    nullable = "✓" if col[2] == 'YES' else "✗"
    print(f'  {col[0]:20} | {col[1]:15} | Nullable: {nullable}')

cursor.close()
db.disconnect()
