#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='lightning_db',
        user='postgres',
        password=''
    )
    cursor = conn.cursor()
    cursor.execute('''
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    ''')
    tables = cursor.fetchall()
    print('📊 Tables dans la base PostgreSQL:')
    for table in tables:
        print(f'  - {table[0]}')
    conn.close()
except Exception as e:
    print(f'❌ Erreur: {e}')
