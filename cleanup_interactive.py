#!/usr/bin/env python3
"""
Interactive PostgreSQL cleanup utility.
Helps clean demo/test data from the BigData pipeline.
"""
import sys
import getpass
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

def cleanup_database(host, port, database, user, password):
    """Connect and clean demo data from PostgreSQL."""
    try:
        print("\n📡 Connexion à PostgreSQL...")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        tables = {
            'trajectories': 'Flight trajectory predictions',
            'disruptions': 'Airspace disruption data',
            'flights': 'Aircraft position data',
            'lightning': 'Lightning strike data'
        }
        
        print("\n🗑️  Suppression des données de démo...")
        total_deleted = 0
        
        for table, description in tables.items():
            try:
                cursor.execute(f"DELETE FROM {table};")
                count = cursor.rowcount
                total_deleted += count
                if count > 0:
                    print(f"✅ {table:20} ({description}): {count} enregistrements supprimés")
                else:
                    print(f"⚠️  {table:20} ({description}): table vide")
            except Exception as e:
                print(f"❌ {table:20}: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Total: {total_deleted} enregistrements supprimés")
        print("✅ Base de données nettoyée avec succès\n")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print("\nConseil: Vérifiez que PostgreSQL est en cours d'exécution")
        print("  Adresse: localhost:5433")
        print("  Base: lightning_db")
        print("  Utilisateur: postgres")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("PostgreSQL Cleanup Utility - Big Data Pipeline")
    print("=" * 60)
    
    # Ask for credentials
    print("\n📝 Veuillez entrer vos identifiants PostgreSQL:")
    
    host = input("   Host [localhost]: ").strip() or "localhost"
    port = input("   Port [5433]: ").strip() or "5433"
    try:
        port = int(port)
    except ValueError:
        print("❌ Port invalide")
        return False
    
    database = input("   Database [lightning_db]: ").strip() or "lightning_db"
    user = input("   User [postgres]: ").strip() or "postgres"
    password = getpass.getpass("   Password (hidden): ")
    
    # Confirmation
    print(f"\n🔍 Vérification de la connexion à {user}@{host}:{port}/{database}...")
    
    if cleanup_database(host, port, database, user, password):
        print("✅ Opération réussie!")
        return True
    else:
        print("❌ Opération échouée!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
