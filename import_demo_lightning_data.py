#!/usr/bin/env python3
"""
Generate and import large amounts of demo lightning/storm data.
This is temporary - will be replaced with real API when found.
"""

import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

from config.config import get_config

# Geographic zones in France (main storm areas)
STORM_ZONES = {
    "Paris": {"lat": 48.8566, "lon": 2.3522, "name": "Île-de-France"},
    "Lyon": {"lat": 45.7640, "lon": 4.8357, "name": "Rhône-Alpes"},
    "Marseille": {"lat": 43.2965, "lon": 5.3698, "name": "Provence"},
    "Toulouse": {"lat": 43.6047, "lon": 1.4442, "name": "Midi-Pyrénées"},
    "Bordeaux": {"lat": 44.8378, "lon": -0.5792, "name": "Aquitaine"},
    "Nice": {"lat": 43.7102, "lon": 7.2620, "name": "Côte d'Azur"},
    "Nantes": {"lat": 47.2184, "lon": -1.5536, "name": "Pays de la Loire"},
    "Lille": {"lat": 50.6292, "lon": 3.0573, "name": "Nord-Pas-de-Calais"},
    "Strasbourg": {"lat": 48.5734, "lon": 7.7521, "name": "Alsace"},
    "Montpellier": {"lat": 43.6108, "lon": 3.8767, "name": "Languedoc"},
}

def generate_demo_lightning_data(
    count: int = 5000,
    days_back: int = 30
) -> list:
    """
    Generate large amounts of realistic demo lightning data.
    
    Args:
        count: Total number of strikes to generate
        days_back: Spread data over this many days
        
    Returns:
        List of strike dictionaries
    """
    strikes = []
    now = datetime.now()
    
    print(f"📊 Génération de {count} fausses données d'éclairs...")
    
    zones = list(STORM_ZONES.values())
    
    for i in range(count):
        # Distribute strikes across days
        days_offset = random.randint(0, days_back)
        time_offset = random.randint(0, 86400)  # Random second in day
        
        strike_time = now - timedelta(days=days_offset, seconds=time_offset)
        
        # Select random zone
        zone = random.choice(zones)
        
        # Add random variation around zone center (±0.2 degrees ≈ ±22km)
        lat = zone["lat"] + random.uniform(-0.2, 0.2)
        lon = zone["lon"] + random.uniform(-0.2, 0.2)
        
        # Realistic signal strength (30-100)
        signal = random.randint(30, 100)
        
        # Random distance from sensor (0-50km)
        distance = random.uniform(0, 50)
        
        # Alternate between different sources for realism
        sources = ["demo_fallback", "simulated", "synthetic"]
        source = random.choice(sources)
        
        strike = {
            "id": f"demo_strike_{i:08d}",
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude": round(random.uniform(500, 8000), 1),
            "timestamp": strike_time.isoformat(),
            "distance": round(distance, 2),
            "signal": signal,
            "source": source,
            "zone": zone["name"]
        }
        
        strikes.append(strike)
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            print(f"  ✓ {i + 1}/{count} records generated")
    
    print(f"✅ {count} fausses données d'éclairs générées\n")
    return strikes


def import_to_postgresql(strikes: list, config) -> bool:
    """
    Import generated strikes into PostgreSQL.
    
    Args:
        strikes: List of strike dictionaries
        config: Configuration object
        
    Returns:
        True if successful
    """
    try:
        print("📡 Connexion à PostgreSQL...")
        
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # Ensure table exists
        print("📋 Vérification de la table lightning_strikes...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lightning_strikes (
                id SERIAL PRIMARY KEY,
                lightning_id VARCHAR(50),
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                altitude FLOAT,
                intensity FLOAT,
                timestamp TIMESTAMP NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source VARCHAR(100)
            );
        """)
        conn.commit()
        
        # Insert strikes
        print(f"💾 Importation de {len(strikes)} éclairs dans PostgreSQL...")
        
        inserted = 0
        skipped = 0
        
        for i, strike in enumerate(strikes):
            try:
                cursor.execute(
                    sql.SQL("""
                        INSERT INTO lightning_strikes 
                        (lightning_id, latitude, longitude, altitude, intensity, timestamp, source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """),
                    (
                        strike["id"],
                        strike["latitude"],
                        strike["longitude"],
                        strike.get("altitude"),
                        strike.get("signal"),  # signal -> intensity
                        strike["timestamp"],
                        strike.get("source")
                    )
                )
                inserted += 1
                
                # Progress indicator
                if (i + 1) % 500 == 0:
                    print(f"  ✓ {i + 1}/{len(strikes)} importés")
                    
            except Exception as e:
                skipped += 1
                if skipped <= 5:  # Only show first 5 errors
                    print(f"  ⚠️  Erreur sur {strike['id']}: {str(e)}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Importation complétée:")
        print(f"   ✓ {inserted} records insérés")
        print(f"   ⚠️  {skipped} records ignorés (doublons)\n")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print("\n📝 Vérifiez que PostgreSQL est en cours d'exécution:")
        print(f"   - Host: {config.DB_HOST}")
        print(f"   - Port: {config.DB_PORT}")
        print(f"   - Database: {config.DB_NAME}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    print("=" * 70)
    print("🌩️  GÉNÉRATEUR DE DONNÉES DÉMO D'ORAGES/ÉCLAIRS")
    print("=" * 70)
    print("\n⚠️  NOTE: Ceci importe des fausses données de test.")
    print("   Elles seront remplacées par une vraie API une fois trouvée.\n")
    
    # Get configuration
    try:
        config = get_config()
    except Exception as e:
        print(f"❌ Erreur de configuration: {str(e)}")
        return False
    
    # Ask for number of records
    while True:
        try:
            count = input("Nombre d'éclairs à générer [5000]: ").strip() or "5000"
            count = int(count)
            if count <= 0:
                print("❌ Le nombre doit être positif")
                continue
            if count > 100000:
                confirm = input(f"⚠️  Générer {count} records? (y/n) [n]: ").strip().lower()
                if confirm != 'y':
                    continue
            break
        except ValueError:
            print("❌ Format invalide, entrez un nombre")
    
    while True:
        try:
            days = input("Étendre sur combien de jours [30]: ").strip() or "30"
            days = int(days)
            if days <= 0:
                print("❌ Le nombre doit être positif")
                continue
            break
        except ValueError:
            print("❌ Format invalide, entrez un nombre")
    
    print()
    
    # Generate data
    strikes = generate_demo_lightning_data(count=count, days_back=days)
    
    # Import to database
    if import_to_postgresql(strikes, config):
        print("✅ Opération réussie!")
        print(f"\n📊 Statistiques:")
        print(f"   ✓ {count} records générés et importés")
        print(f"   ✓ Répartition sur {days} jours")
        print(f"   ✓ {len(STORM_ZONES)} zones géographiques couvertes")
        print(f"\n🔄 API réelle: À intégrer quand disponible")
        return True
    else:
        print("❌ Échec de l'importation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
