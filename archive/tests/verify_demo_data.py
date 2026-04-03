"""
Verify demo data has been correctly populated in the database.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse
from src.utils.logger import setup_logging

# Setup logging
logger = setup_logging(log_file="logs/verify_demo_data.log", level="INFO")


class DemoDataVerifier:
    """Verify demo data population and display statistics."""
    
    def __init__(self):
        """Initialize verifier."""
        self.config = get_config()
        self.db_connection = PostgreSQLConnection(
            host=self.config.DB_HOST,
            port=self.config.DB_PORT,
            database=self.config.DB_NAME,
            user=self.config.DB_USER,
            password=self.config.DB_PASSWORD
        )
        self.warehouse = None
    
    def run(self):
        """Run verification."""
        print("\n" + "="*70)
        print("VERIFICATION DES DONNEES DE DEMO")
        print("="*70)
        
        try:
            # Connect to database
            self.db_connection.connect()
            self.warehouse = DataWarehouse(self.db_connection)
            print("[OK] Connexion a PostgreSQL etablie\n")
            
            # Verify lightning data
            print("1. DONNEES D'ECLAIRS")
            print("-" * 70)
            self._verify_lightning_data()
            
            # Verify flights data
            print("\n2. DONNEES DE VOLS")
            print("-" * 70)
            self._verify_flights_data()
            
            # Verify disruptions data
            print("\n3. PERTURBATIONS DETAILLEES")
            print("-" * 70)
            self._verify_disruptions_data()
            
            # Summary statistics
            print("\n" + "="*70)
            print("RESUME DES DONNEES")
            print("="*70)
            self._display_summary()
            
        except Exception as e:
            logger.error(f"Erreur lors de la verification: {str(e)}")
            print(f"\n[ERREUR] {str(e)}")
        finally:
            self.db_connection.disconnect()
    
    def _verify_lightning_data(self):
        """Verify and display lightning data."""
        try:
            data = self.warehouse.query_lightning_data()
            
            if not data:
                print("[VIDE] Aucune donnee d'eclairs trouvee")
                return
            
            print(f"[OK] {len(data)} eclairs trouves\n")
            
            # Group by intensity
            high = [d for d in data if d.get('intensity', 0) > 80]
            medium = [d for d in data if 40 < d.get('intensity', 0) <= 80]
            low = [d for d in data if d.get('intensity', 0) <= 40]
            
            print(f"  - Haute intensite (>80):      {len(high):3d}")
            print(f"  - Intensite moyenne (40-80):  {len(medium):3d}")
            print(f"  - Basse intensite (<40):      {len(low):3d}")
            
            # Show sample records
            print("\n  Exemples (premiers 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"    {i}. ID={record.get('lightning_id', 'N/A'):8s} "
                      f"Intensity={record.get('intensity', 0):5.1f} "
                      f"Lat={record.get('latitude', 0):7.3f} "
                      f"Lon={record.get('longitude', 0):7.3f}")
        
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
    
    def _verify_flights_data(self):
        """Verify and display flights data."""
        try:
            data = self.warehouse.query_flights_data()
            
            if not data:
                print("[VIDE] Aucune donnee de vols trouvee")
                return
            
            print(f"[OK] {len(data)} vols trouves\n")
            
            # Group by route
            routes = {}
            for record in data:
                route = f"{record.get('departure', 'N/A')}-{record.get('arrival', 'N/A')}"
                routes[route] = routes.get(route, 0) + 1
            
            print(f"  Routes uniques: {len(routes)}")
            
            # Show aircraft types
            aircraft_types = {}
            for record in data:
                ac_type = record.get('aircraft_type', 'Unknown')
                aircraft_types[ac_type] = aircraft_types.get(ac_type, 0) + 1
            
            print(f"  Types d'aeronefs:")
            for ac_type, count in sorted(aircraft_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {ac_type}: {count}")
            
            # Show sample records
            print("\n  Exemples (premiers 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"    {i}. {record.get('flight_number', 'N/A')} "
                      f"{record.get('departure', 'N/A')}-{record.get('arrival', 'N/A')} "
                      f"({record.get('aircraft_type', 'N/A')})")
        
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
    
    def _verify_disruptions_data(self):
        """Verify and display disruptions data."""
        try:
            data = self.warehouse.query_disruptions_data()
            
            if not data:
                print("[VIDE] Aucune perturbation trouvree")
                print("\nNote: Les perturbations sont calculees en fonction de la")
                print("proximite entre les eclairs et les vols. Si aucune n'est trouvee,")
                print("c'est que les donnees ne se chevauchent pas geographiquement/temporellement.")
                return
            
            print(f"[OK] {len(data)} perturbations detectees\n")
            
            # Group by risk level
            risk_levels = {}
            for record in data:
                level = record.get('risk_level', 'UNKNOWN')
                risk_levels[level] = risk_levels.get(level, 0) + 1
            
            print(f"  Par niveau de risque:")
            for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                count = risk_levels.get(level, 0)
                if count > 0:
                    print(f"    - {level:8s}: {count:3d}")
            
            # Average probability
            probs = [record.get('disruption_probability', 0) for record in data]
            avg_prob = sum(probs) / len(probs) if probs else 0
            print(f"\n  Probabilite moyenne de perturbation: {avg_prob:.2%}")
            
            # Show sample records
            print("\n  Exemples (premiers 3):")
            for i, record in enumerate(data[:3], 1):
                print(f"    {i}. Flight ID={record.get('flight_id', 'N/A'):3s} "
                      f"Risk={record.get('risk_level', 'N/A'):8s} "
                      f"Distance={record.get('distance_km', 0):6.1f}km "
                      f"Prob={record.get('disruption_probability', 0):.0%}")
        
        except Exception as e:
            print(f"[ERREUR] {str(e)}")
    
    def _display_summary(self):
        """Display overall summary statistics."""
        try:
            lightning = self.warehouse.query_lightning_data()
            flights = self.warehouse.query_flights_data()
            disruptions = self.warehouse.query_disruptions_data()
            
            print(f"Eclairs:      {len(lightning) if lightning else 0:3d} records")
            print(f"Vols:         {len(flights) if flights else 0:3d} records")
            print(f"Perturbations: {len(disruptions) if disruptions else 0:3d} records")
            
            if lightning:
                intensities = [d.get('intensity', 0) for d in lightning]
                print(f"\nIntensite des eclairs:")
                print(f"  Min: {min(intensities):5.1f}")
                print(f"  Max: {max(intensities):5.1f}")
                print(f"  Moy: {sum(intensities)/len(intensities):5.1f}")
            
            print("\n" + "="*70)
            print("VERIFICATION COMPLETE")
            print("="*70 + "\n")
        
        except Exception as e:
            logger.error(f"Error displaying summary: {str(e)}")


def main():
    """Main entry point."""
    verifier = DemoDataVerifier()
    verifier.run()


if __name__ == "__main__":
    main()
