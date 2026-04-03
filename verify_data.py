import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='lightning_db',
        user='postgres',
        password='postgres'
    )
    cur = conn.cursor()
    
    print('='*60)
    print('  DEMO DATA GENERATION VERIFICATION')
    print('='*60)
    
    # Query lightning_strikes
    cur.execute('SELECT COUNT(*) FROM lightning_strikes')
    lightning_count = cur.fetchone()[0]
    print('Lightning Strikes................. %10d records' % lightning_count)
    
    # Query flights
    cur.execute('SELECT COUNT(*) FROM flights')
    flights_count = cur.fetchone()[0]
    print('Flights........................... %10d records' % flights_count)
    
    # Query flight_disruptions
    cur.execute('SELECT COUNT(*) FROM flight_disruptions')
    disruptions_count = cur.fetchone()[0]
    print('Flight Disruptions............... %10d records' % disruptions_count)
    
    # Query storm_zones
    cur.execute('SELECT COUNT(*) FROM storm_zones')
    zones_count = cur.fetchone()[0]
    print('Storm Zones...................... %10d records' % zones_count)
    
    print('='*60)
    total = lightning_count + flights_count + disruptions_count + zones_count
    print('TOTAL RECORDS INSERTED........... %10d records' % total)
    print('='*60)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print('Error: %s' % str(e))
