"""
Test Flight Routing API - Demonstrates enriched flight data with routing info.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.flight_routing_api import FlightRoutingAPI, AirlabsFlightAPI
import os


def test_flight_routing_api():
    """Test FlightRoutingAPI with real OpenSky data enriched with routing."""
    print("\n" + "="*70)
    print("TEST: Flight Routing API (OpenSky + Routing Enrichment)")
    print("="*70)
    
    try:
        # Create API instance for Paris area
        api = FlightRoutingAPI(lat=48.8527, lon=2.3510, radius_km=200)
        print("[OK] API initialisee (Paris, rayon 200km)")
        
        # Fetch flights
        print("\n[FETCHING] Recuperation des vols en temps reel...")
        result = api.fetch()
        
        flights = result.get("flights", [])
        error = result.get("error")
        
        if error:
            print(f"[ERREUR] {error}")
            return False
        
        print(f"[OK] {len(flights)} vols recuperes")
        
        if not flights:
            print("[INFO] Aucun vol dans le rayon. Essayez un rayon plus grand.")
            return True
        
        # Display sample flights
        print("\n" + "-"*70)
        print("VOLS ENRICHIS (avec départ/arrivée estimés)")
        print("-"*70)
        
        for i, flight in enumerate(flights[:5], 1):
            print(f"\n[VOL {i}]")
            print(f"  Flight Number: {flight.get('flight_number')}")
            print(f"  Departure:     {flight.get('departure')}")
            print(f"  Arrival:       {flight.get('arrival')}")
            print(f"  Position:      {flight.get('latitude'):.4f}, {flight.get('longitude'):.4f}")
            print(f"  Altitude:      {flight.get('altitude')} m")
            print(f"  Speed:         {flight.get('speed')} km/h")
            print(f"  Confidence:    {flight.get('routing_confidence', 0):.0%}")
            print(f"  Source:        {flight.get('source')}")
        
        # Summary
        print("\n" + "="*70)
        print("RESUME")
        print("="*70)
        print(f"Total vols fetches:        {len(flights)}")
        print(f"Tous avec routing:         {sum(1 for f in flights if f.get('departure') != 'UNKNOWN')}/{len(flights)}")
        print(f"Confidence moyenne:        {sum(f.get('routing_confidence', 0) for f in flights) / len(flights) if flights else 0:.0%}")
        print(f"Source:                    {result.get('source')}")
        print(f"Timestamp:                 {result.get('timestamp')}")
        
        api.close()
        return True
        
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def test_airlabs_api():
    """Test AirlabsFlightAPI for premium flight data."""
    print("\n" + "="*70)
    print("TEST: Airlabs Flight API (Premium Real Data)")
    print("="*70)
    
    # Get API key from environment
    api_key = os.getenv("AIRLABS_API_KEY")
    
    if not api_key:
        print("[INFO] AIRLABS_API_KEY not set")
        print("       Setup: https://airlabs.co")
        print("       Then: export AIRLABS_API_KEY=your_key")
        return True
    
    try:
        # Create API instance
        api = AirlabsFlightAPI(api_key=api_key, lat=48.8527, lon=2.3510, radius_km=200)
        print("[OK] Airlabs API initialisee (Paris, rayon 200km)")
        
        # Fetch flights
        print("\n[FETCHING] Recuperation des vols d'Airlabs...")
        result = api.fetch()
        
        flights = result.get("flights", [])
        error = result.get("error")
        
        if error:
            print(f"[ERREUR] {error}")
            if "API key" in error:
                print("        Obtenez une cle gratuite: https://airlabs.co")
            return False
        
        print(f"[OK] {len(flights)} vols recuperes")
        
        if not flights:
            print("[INFO] Aucun vol dans le rayon ou API limit atteint.")
            return True
        
        # Display sample flights
        print("\n" + "-"*70)
        print("VOLS AIRLABS (données réelles complètes)")
        print("-"*70)
        
        for i, flight in enumerate(flights[:3], 1):
            print(f"\n[VOL {i}]")
            print(f"  Flight Number: {flight.get('flight_number')}")
            print(f"  {flight.get('departure')} -> {flight.get('arrival')}")
            print(f"  Position:      {flight.get('latitude'):.4f}, {flight.get('longitude'):.4f}")
            print(f"  Altitude:      {flight.get('altitude')} m")
            print(f"  Départ:        {flight.get('departure_time')}")
            print(f"  Arrivée:       {flight.get('arrival_time')}")
            print(f"  Aircraft:      {flight.get('airplane')}")
        
        # Summary
        print("\n" + "="*70)
        print("RESUME AIRLABS")
        print("="*70)
        print(f"Total vols:  {len(flights)}")
        print(f"Complétude: 100% (départ/arrivée réels)")
        
        api.close()
        return True
        
    except Exception as e:
        print(f"[ERREUR] {str(e)}")
        return False


def compare_apis():
    """Compare different flight API options."""
    print("\n" + "="*70)
    print("COMPARAISON DES APIs DE VOL")
    print("="*70)
    
    apis_info = {
        "OpenSky Network": {
            "gratuit": "✅",
            "départ": "❌",
            "arrivée": "❌",
            "temps_reel": "✅",
            "données": "Position seulement",
            "limite": "Illimilité",
            "note": "API actuellement utilisée - PAS de départ/arrivée!"
        },
        "Flight Routing API": {
            "gratuit": "✅",
            "départ": "✅*",
            "arrivée": "✅*",
            "temps_reel": "✅",
            "données": "Position + Routing estimé",
            "limite": "Illimitité",
            "note": "Amélioration OpenSky - départ/arrivée ESTIMÉS"
        },
        "Airlabs API": {
            "gratuit": "✅ (500/mois)",
            "départ": "✅",
            "arrivée": "✅",
            "temps_reel": "✅",
            "données": "Position + Routing réel",
            "limite": "500 vols/mois",
            "note": "Gratuit limité - départ/arrivée RÉELS"
        },
        "Données DÉMO": {
            "gratuit": "✅",
            "départ": "✅",
            "arrivée": "✅",
            "temps_reel": "Simulation",
            "données": "Données démo réalistes",
            "limite": "Illimitité",
            "note": "RECOMMANDÉ pour démo - Déjà 17 perturbations!"
        }
    }
    
    for api_name, info in apis_info.items():
        print(f"\n{api_name}")
        print("-" * 50)
        for key, value in info.items():
            print(f"  {key:20}: {value}")


def main():
    """Main entry point."""
    print("\nFLIGHT APIs COM DÉPART ET ARRIVÉE")
    print("="*70)
    print("\nOptions d'utilisation:\n")
    print("  1) Données DÉMO (RECOMMANDÉ):")
    print("     python populate_demo_data.py")
    print("     -> 109 éclairs + 19 vols + 17 perturbations détectées\n")
    
    print("  2) OpenSky enrichi (gratuit, temps réel):")
    print("     APIFlightRoutingAPI utilise OpenSky + estimations\n")
    
    print("  3) Airlabs (gratuit 500/mois, données réelles):")
    print("     Obtenez clé: https://airlabs.co")
    print("     export AIRLABS_API_KEY=your_key\n")
    
    print("="*70)
    
    # Compare APIs
    compare_apis()
    
    # Test FlightRoutingAPI
    print("\n")
    flight_routing_ok = test_flight_routing_api()
    
    # Test Airlabs (if key available)
    print("\n")
    airlabs_ok = test_airlabs_api()
    
    # Summary
    print("\n" + "="*70)
    print("RECOMMANDATION")
    print("="*70)
    print("\nPour DÉMONSTRATION avec perturbations visibles:")
    print("  → python populate_demo_data.py")
    print("     Génère 17 perturbations prêtes à visualiser!\n")
    
    print("Pour DONNÉES RÉELLES en TEMPS RÉEL:")
    print("  → Intégrer FlightRoutingAPI ou Airlabs")
    print("     Voir GUIDE_FLIGHT_APIS.md pour détails")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
