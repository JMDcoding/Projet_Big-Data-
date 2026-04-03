#!/usr/bin/env python
"""Test database connectivity and data."""
try:
    import psycopg2
    
    # Direct connection
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='lightning_db',
        user='admin',
        password='admin'
    )
    
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    # Check flights
    cursor.execute("SELECT COUNT(*) FROM flights")
    count = cursor.fetchone()[0]
    print(f"Flights count: {count}")
    
    # Check lightning
    cursor.execute("SELECT COUNT(*) FROM lightning")
    count = cursor.fetchone()[0]
    print(f"Lightning strikes count: {count}")
    
    # Get sample flight
    if count > 0:
        cursor.execute("SELECT * FROM flights LIMIT 1")
        cols = [desc[0] for desc in cursor.description]
        print(f"Flight columns: {cols}")
        row = cursor.fetchone()
        if row:
            print(f"Sample flight: {dict(zip(cols, row))}")
    
    cursor.close()
    conn.close()
    print("✓ Database check complete")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
