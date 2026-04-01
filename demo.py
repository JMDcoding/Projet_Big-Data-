"""
Demo script - Simple example showing the pipeline in action.
This demonstrates the architecture without requiring PostgreSQL.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.ingestion import BlitzortungAPI
from src.storage import JSONDataLake, CSVDataLake
from src.transformation import LightningDataTransformer, FlightDataTransformer, DataMerger
from src.utils import logger, calculate_distance, assess_disruption_risk
import pandas as pd


def demo_1_ingestion():
    """Demo: Récupérer les données d'une API"""
    print("\n" + "="*60)
    print("📡 DÉMO 1 : INGESTION DE DONNÉES")
    print("="*60)
    
    try:
        api = BlitzortungAPI()
        print("✓ Client API créé")
        print(f"  URL: {api.base_url}")
        print(f"  Timeout: {api.timeout}s")
        
        # Note: This would fetch real data if Blitzortung is available
        print("\n💡 En production, ceci récupérerait données réelles de Blitzortung")
        print("   Les données sont validées et structurées automatiquement")
        
    except Exception as e:
        print(f"⚠️  À titre démonstratif: {str(e)}")
    
    api.close()


def demo_2_data_lake():
    """Demo: Stocker les données brutes"""
    print("\n" + "="*60)
    print("💾 DÉMO 2 : DATA LAKE (Stockage Brut)")
    print("="*60)
    
    config = get_config()
    
    # Créer des données de test
    test_lightning_data = {
        "lightning_strikes": [
            {
                "lightning_id": "STR_001",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "altitude": 2000,
                "intensity": 85,
                "timestamp": datetime.now().isoformat()
            },
            {
                "lightning_id": "STR_002",
                "latitude": 48.8700,
                "longitude": 2.3600,
                "altitude": 1500,
                "intensity": 72,
                "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat()
            }
        ]
    }
    
    # Sauvegarder en JSON
    json_lake = JSONDataLake(config.DATA_RAW_PATH)
    json_path = json_lake.save(test_lightning_data, "demo_lightning_data")
    print(f"✓ Données sauvegardées (JSON): {json_path}")
    
    # Charger et afficher
    loaded_data = json_lake.load("demo_lightning_data")
    print(f"✓ {len(loaded_data['lightning_strikes'])} éclairs chargés")
    
    # Exporter en CSV
    csv_lake = CSVDataLake(config.DATA_RAW_PATH)
    flat_data = loaded_data['lightning_strikes']
    csv_path = csv_lake.save(flat_data, "demo_lightning_csv")
    print(f"✓ Données exportées (CSV): {csv_path}")


def demo_3_transformation():
    """Demo: Transformer et nettoyer les données"""
    print("\n" + "="*60)
    print("🔄 DÉMO 3 : TRANSFORMATION DE DONNÉES")
    print("="*60)
    
    # Données brutes
    raw_data = [
        {
            "lightning_id": "STR_001",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "altitude": 2000.5,
            "intensity": 85,
            "timestamp": "2026-04-01 11:30:00"
        },
        {
            "lightning_id": "STR_002",
            "latitude": "48.8700",  # String, sera converti en float
            "longitude": "2.3600",
            "altitude": None,       # Valeur manquante
            "intensity": 72,
            "timestamp": "2026-04-01 11:25:00"
        }
    ]
    
    print(f"Avant transformation: {len(raw_data)} enregistrements")
    
    # Transformer
    transformer = LightningDataTransformer()
    df_clean = transformer.transform(raw_data)
    
    print(f"Après transformation: {len(df_clean)} enregistrements")
    print("\nAperçu des données transformées:")
    print(df_clean.head())
    
    return df_clean


def demo_4_analysis():
    """Demo: Analyser les risques de disruption aérienne"""
    print("\n" + "="*60)
    print("✈️  DÉMO 4 : ANALYSE DE RISQUE DE DISRUPTION")
    print("="*60)
    
    # Données de vol simulées
    flights = [
        {
            "flight_number": "AF123",
            "departure": "Paris CDG",
            "arrival": "London LHR",
            "latitude": 48.5,
            "longitude": 2.4,
            "departure_time": datetime.now() + timedelta(hours=2)
        },
        {
            "flight_number": "BA456",
            "departure": "London LHR",
            "arrival": "Paris CDG",
            "latitude": 51.4,
            "longitude": -0.4,
            "departure_time": datetime.now() + timedelta(hours=1)
        }
    ]
    
    # Données d'éclairs simulées
    lightning = [
        {
            "lightning_id": "STR_001",
            "latitude": 48.8,
            "longitude": 2.5,
            "intensity": 85,
            "altitude": 2000,
            "timestamp": datetime.now() + timedelta(minutes=30)
        }
    ]
    
    print(f"✓ {len(flights)} vols analysés")
    print(f"✓ {len(lightning)} éclairs détectés")
    
    # Analyser les risques
    disruptions = []
    for flight in flights:
        for strike in lightning:
            distance = calculate_distance(
                flight["latitude"], flight["longitude"],
                strike["latitude"], strike["longitude"]
            )
            time_diff = int(
                (strike["timestamp"] - flight["departure_time"]).total_seconds() / 60
            )
            
            risk = assess_disruption_risk(distance, time_diff, strike["intensity"])
            
            disruptions.append({
                "flight": flight["flight_number"],
                "distance_km": distance,
                "time_diff_min": time_diff,
                "risk_level": risk["risk_level"],
                "probability": risk["disruption_probability"]
            })
    
    # Afficher résultats
    print("\nRésultats d'analyse:")
    for d in disruptions:
        print(f"\n  Vole: {d['flight']}")
        print(f"  Distance: {d['distance_km']:.2f} km")
        print(f"  Délai: {d['time_diff_min']} minutes")
        print(f"  Risque: {d['risk_level']} (probabilité: {d['probability']:.0%})")


def demo_5_merging():
    """Demo: Fusionner plusieurs sources de données"""
    print("\n" + "="*60)
    print("🔗 DÉMO 5 : FUSION DE DONNÉES")
    print("="*60)
    
    # Créer deux dataframes
    df_lightning = pd.DataFrame([
        {"id": 1, "latitude": 48.8, "longitude": 2.3, "intensity": 85},
        {"id": 2, "latitude": 48.9, "longitude": 2.4, "intensity": 72},
    ])
    
    df_flights = pd.DataFrame([
        {"id": 1, "flight": "AF123", "departure": "Paris", "arrival": "London"},
        {"id": 2, "flight": "BA456", "departure": "London", "arrival": "Paris"},
    ])
    
    print(f"✓ DataFrame 1 (Éclairs): {len(df_lightning)} lignes")
    print(f"✓ DataFrame 2 (Vols): {len(df_flights)} lignes")
    
    # Fusionner
    merger = DataMerger()
    df_merged = merger.transform({
        "lightning": df_lightning,
        "flights": df_flights
    })
    
    print(f"✓ Fusionné: {len(df_merged)} lignes")
    print("\nAperçu des données fusionnées:")
    print(df_merged.head())


def main():
    """Exécuter tous les demos"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  ⚡ DÉMONSTRATION - PIPELINE BIG DATA  ⚡".center(58) + "║")
    print("║" + " "*58 + "║")
    print("║" + "  Monitoring des Éclairs & Disruptions Aériennes".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        demo_1_ingestion()
        demo_2_data_lake()
        df = demo_3_transformation()
        demo_4_analysis()
        demo_5_merging()
        
        print("\n" + "="*60)
        print("✅ TOUS LES DEMOS COMPLÉTÉS AVEC SUCCÈS !")
        print("="*60)
        
        print("\n📚 Prochaines étapes:")
        print("  1. Consultez QUICK_START.md pour démarrer")
        print("  2. Modifiez config/.env avec vos paramètres PostgreSQL")
        print("  3. Exécutez: python main.py")
        print("  4. Lancez le dashboard: streamlit run app.py")
        
        print("\n📖 Documentation:")
        print("  - README.md : Architecture complète")
        print("  - QUICK_START.md : Guide de démarrage")
        print("  - Docstrings des classes : help(ClassName)")
        
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
