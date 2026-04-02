#!/usr/bin/env python3
"""
Auto-cleanup PostgreSQL - Non-interactive version
Run directly to clear all test data
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed")
    sys.exit(1)

def auto_cleanup():
    """Automatically cleanup database with hardcoded credentials."""
    try:
        print("\n" + "="*70)
        print("🗑️  AUTO-CLEANUP: Suppression complète de toutes les données")
        print("="*70 + "\n")
        
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="lightning_db",
            user="postgres",
            password=""
        )
        
        cursor = conn.cursor()
        
        tables = ['lightning', 'flight_disruptions']
        total_deleted = 0
        
        print("Suppression en cours...")
        print("-" * 70)
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table};")
                count = cursor.rowcount
                total_deleted += count
                
                # Verify deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                remaining = cursor.fetchone()[0]
                
                print(f"✅ {table:20} | Supprimé: {count:5} enregistrements | Restant: {remaining}")
            except Exception as e:
                print(f"⚠️  {table:20} | Erreur: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("-" * 70)
        print(f"\n✅ SUCCÈS: {total_deleted} enregistrements au total supprimés")
        print("🎯 Base de données prête pour données API pures uniquement\n")
        print("="*70 + "\n")
        
        return True
    
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = auto_cleanup()
    sys.exit(0 if success else 1)
