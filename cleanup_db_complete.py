#!/usr/bin/env python3
"""
PostgreSQL Database Cleanup Utility
Removes ALL data from all tables - clean slate for API data only
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

def cleanup_all_data(host, port, database, user, password):
    """Delete ALL data from all tables in the database.
    
    IMPORTANT: This completely empties the database - cannot be undone!
    """
    try:
        print("\n" + "="*70)
        print("PostgreSQL COMPLETE DATA CLEANUP")
        print("="*70)
        print("\n⚠️  ATTENTION: Cette opération SUPPRIMERA TOUTES les données!")
        print("   → Lightning strikes (lightning_strikes)")
        print("   → Flight disruptions (flight_disruptions)")
        print("\nConfirmation requise...\n")
        
        # Confirmation
        confirm = input("Tapez 'OUI SUPPRIMER' pour confirmer la suppression complète: ").strip()
        if confirm != "OUI SUPPRIMER":
            print("❌ Opération annulée")
            return False
        
        print("\n📡 Connexion à PostgreSQL...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # List all tables to delete
        tables = ['trajectories', 'disruptions', 'flights', 'lightning']
        
        print("\n🗑️  SUPPRESSION DES DONNÉES...")
        print("-" * 70)
        
        total_deleted = 0
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table};")
                count = cursor.rowcount
                total_deleted += count
                
                # Get table stats
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                remaining = cursor.fetchone()[0]
                
                status = "✅ OK" if remaining == 0 else "⚠️  FAIL"
                print(f"{status}  {table:20} | Supprimé: {count:5} | Restant: {remaining}")
            
            except psycopg2.ProgrammingError as e:
                print(f"⚠️  {table:20} | Table n'existe pas: {str(e)}")
                cursor.execute("ROLLBACK")
            except Exception as e:
                print(f"❌ {table:20} | Erreur: {str(e)}")
                cursor.execute("ROLLBACK")
        
        # Commit all deletions
        conn.commit()
        cursor.close()
        
        print("\n" + "-" * 70)
        print(f"✅ SUPPRESSION COMPLÉTÉE")
        print(f"   Total enregistrements supprimés: {total_deleted}")
        print(f"\n🎯 Base de données PRÊTE pour données API pures")
        print("="*70 + "\n")
        
        conn.close()
        return True
    
    except psycopg2.OperationalError as e:
        print(f"\n❌ ERREUR DE CONNEXION")
        print(f"   Impossible de se connecter à {user}@{host}:{port}/{database}")
        print(f"   {str(e)}")
        print("\n💡 Solutions:")
        print("   1. Vérifier que PostgreSQL est démarré")
        print("   2. Vérifier les identifiants (host, port, user, password)")
        print("   3. Vérifier que la base de données existe")
        return False
    
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("🔧 NETTOYEUR DE BASE DE DONNÉES POSTGRESQL")
    print("="*70)
    
    # Get connection parameters
    print("\n📝 Entrez vos identifiants PostgreSQL:")
    
    host = input("   Host [localhost]: ").strip() or "localhost"
    port = input("   Port [5433]: ").strip() or "5433"
    try:
        port = int(port)
    except ValueError:
        print("❌ Port invalide")
        return False
    
    database = input("   Database [lightning_db]: ").strip() or "lightning_db"
    user = input("   User [postgres]: ").strip() or "postgres"
    password = getpass.getpass("   Password (caché): ")
    
    print(f"\n🔗 Connexion à {user}@{host}:{port}/{database}...")
    
    if cleanup_all_data(host, port, database, user, password):
        print("✅ Succès!")
        return True
    else:
        print("❌ Échec!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
