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
    
    print("="*80)
    print("FINAL VERIFICATION - Database Contents")
    print("="*80)
    
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes")
    total_strikes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lightning_strikes WHERE source='Demo-Generator-Final'")
    demo_strikes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    total_flights = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights WHERE source='Demo-Generator-Final'")
    demo_flights = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_disruptions")
    total_disruptions = cursor.fetchone()[0]
    
    print(f"\nLightning Strikes:")
    print(f"  Total in database: {total_strikes}")
    print(f"  Demo generator (v2-Final): {demo_strikes}")
    
    print(f"\nFlights:")
    print(f"  Total in database: {total_flights}")
    print(f"  Demo generator (v2-Final): {demo_flights}")
    
    print(f"\nFlight Disruptions:")
    print(f"  Total in database: {total_disruptions}")
    
    print(f"\n" + "="*80)
    print("VERIFICATION SUMMARY:")
    print("="*80)
    print(f"Lightning strikes: {demo_strikes} >= 20 ? {'✓ PASS' if demo_strikes >= 20 else '✗ FAIL'}")
    print(f"Flights: {demo_flights} >= 15 ? {'✓ PASS' if demo_flights >= 15 else '✗ FAIL'}")
    print(f"Flight disruptions: {total_disruptions} >= 15 ? {'✓ PASS' if total_disruptions >= 15 else '✗ FAIL'}")
    
    if demo_strikes >= 20 and demo_flights >= 15 and total_disruptions >= 15:
        print("\n✓✓✓ ALL CRITERIA MET! ✓✓✓")
    
    print("="*80)
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
