"""
Populate demo data with comprehensive test cases.
Includes lightning strikes, flights, and flight disruptions.
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.database.warehouse import PostgreSQLConnection, DataWarehouse
from src.utils.logger import setup_logging

# Setup logging
logger = setup_logging(log_file="logs/populate_demo_data.log", level="INFO")


class DemoDataGenerator:
    """Generate comprehensive demo data with all test cases."""
    
    # Reference airports
    AIRPORTS = {
        "CDG": {"latitude": 49.0127, "longitude": 2.5497, "name": "Paris Charles de Gaulle"},
        "ORY": {"latitude": 48.7252, "longitude": 2.3592, "name": "Paris Orly"},
        "LHR": {"latitude": 51.4700, "longitude": -0.4543, "name": "London Heathrow"},
        "BRU": {"latitude": 50.9023, "longitude": 4.4844, "name": "Brussels Zaventem"},
        "AMS": {"latitude": 52.3081, "longitude": 4.7642, "name": "Amsterdam Schiphol"},
        "FCO": {"latitude": 41.8002, "longitude": 12.2388, "name": "Rome Fiumicino"},
        "MAD": {"latitude": 40.4718, "longitude": -3.5626, "name": "Madrid Barajas"},
        "TXL": {"latitude": 52.5520, "longitude": 13.2887, "name": "Berlin Tegel"},
    }
    
    def __init__(self):
        """Initialize demo data generator."""
        self.config = get_config()
        self.db_connection = PostgreSQLConnection(
            host=self.config.DB_HOST,
            port=self.config.DB_PORT,
            database=self.config.DB_NAME,
            user=self.config.DB_USER,
            password=self.config.DB_PASSWORD
        )
        self.warehouse = None
        self.base_time = datetime.now() - timedelta(hours=6)
    
    def generate_lightning_strikes(self) -> list:
        """Generate geographically distributed lightning strike data across Europe.
        
        Test cases covered:
        - Multiple geographic zones across Europe
        - Varying intensity levels
        - Overlapping flight paths with lightning
        - Dense clusters and scattered patterns
        """
        strikes = []
        strike_id = 1
        
        # Define storm zones across Europe with characteristics
        storm_zones = [
            # Zone 1: Paris-Northern France (HIGH intensity cluster)
            {
                "name": "Paris",
                "lat": 48.8566, "lon": 2.3522,
                "radius": 0.6,
                "count": 12,
                "intensity_range": (85, 99),
                "time_window": (0, 120),
                "altitude_range": (1500, 3500)
            },
            # Zone 2: Belgium-Netherlands (MEDIUM-HIGH intensity)
            {
                "name": "Belgium",
                "lat": 50.9023, "lon": 4.4844,
                "radius": 0.5,
                "count": 10,
                "intensity_range": (60, 85),
                "time_window": (15, 135),
                "altitude_range": (1200, 3000)
            },
            # Zone 3: Germany (MEDIUM intensity)
            {
                "name": "Germany",
                "lat": 52.5520, "lon": 13.2887,
                "radius": 1.0,
                "count": 14,
                "intensity_range": (50, 75),
                "time_window": (30, 150),
                "altitude_range": (1000, 2800)
            },
            # Zone 4: UK-London area (MEDIUM intensity)
            {
                "name": "London",
                "lat": 51.4700, "lon": -0.4543,
                "radius": 0.7,
                "count": 10,
                "intensity_range": (55, 80),
                "time_window": (40, 160),
                "altitude_range": (1300, 3200)
            },
            # Zone 5: Alpine region (MEDIUM intensity)
            {
                "name": "Alpine",
                "lat": 48.2082, "lon": 16.3738,  # Vienna area
                "radius": 0.8,
                "count": 11,
                "intensity_range": (50, 75),
                "time_window": (50, 170),
                "altitude_range": (1800, 4000)
            },
            # Zone 6: Mediterranean - Italy (LOW-MEDIUM intensity)
            {
                "name": "Italy",
                "lat": 41.8002, "lon": 12.2388,  # Rome
                "radius": 1.2,
                "count": 13,
                "intensity_range": (40, 70),
                "time_window": (60, 180),
                "altitude_range": (1000, 2500)
            },
            # Zone 7: Scandinavia (LOW intensity scattered)
            {
                "name": "Scandinavia",
                "lat": 59.3293, "lon": 18.0686,  # Stockholm
                "radius": 2.0,
                "count": 12,
                "intensity_range": (25, 55),
                "time_window": (70, 190),
                "altitude_range": (800, 2200)
            },
            # Zone 8: Southern Spain (LOW-MEDIUM intensity)
            {
                "name": "Spain",
                "lat": 40.4718, "lon": -3.5626,  # Madrid
                "radius": 1.5,
                "count": 10,
                "intensity_range": (35, 65),
                "time_window": (80, 200),
                "altitude_range": (1200, 2800)
            },
            # Zone 9: Switzerland region (MEDIUM intensity)
            {
                "name": "Switzerland",
                "lat": 47.3769, "lon": 8.5472,  # Zurich
                "radius": 0.6,
                "count": 9,
                "intensity_range": (50, 75),
                "time_window": (25, 145),
                "altitude_range": (1500, 3500)
            },
            # Zone 10: Northern France (MEDIUM intensity)
            {
                "name": "Northern France",
                "lat": 50.6292, "lon": 3.0573,  # Lille
                "radius": 0.7,
                "count": 8,
                "intensity_range": (55, 80),
                "time_window": (35, 155),
                "altitude_range": (1200, 2900)
            }
        ]
        
        # Generate strikes for each zone
        for zone in storm_zones:
            for i in range(zone["count"]):
                lat_offset = random.uniform(-zone["radius"], zone["radius"])
                lon_offset = random.uniform(-zone["radius"], zone["radius"])
                
                strikes.append({
                    "lightning_id": f"STR_{strike_id:04d}",
                    "latitude": zone["lat"] + lat_offset,
                    "longitude": zone["lon"] + lon_offset,
                    "altitude": random.uniform(zone["altitude_range"][0], zone["altitude_range"][1]),
                    "intensity": random.uniform(zone["intensity_range"][0], zone["intensity_range"][1]),
                    "timestamp": self.base_time + timedelta(minutes=random.randint(zone["time_window"][0], zone["time_window"][1])),
                    "source": "blitzortung"
                })
                strike_id += 1
        
        return strikes
    
    def generate_flights(self) -> list:
        """Generate flight data that will intersect with lightning zones.
        
        Strategy:
        - Create flights passing through lightning-affected areas
        - Synchronize flight times with lightning activity windows
        - Ensure departure/arrival times overlap with storm activity
        - Mix of routes that are affected and unaffected by lightning
        """
        flights = []
        flight_num = 1000
        
        # Define flight routes that cross through or near lightning zones
        flight_routes = [
            # Routes crossing Paris zone (HIGH risk)
            {
                "departure": "CDG", "arrival": "LHR",
                "cross_zone": "Paris", "zone_lat": 48.8566, "zone_lon": 2.3522,
                "time_offset": 30  # Depart 30 min into lightning activity
            },
            {
                "departure": "ORY", "arrival": "AMS", 
                "cross_zone": "Paris", "zone_lat": 48.8566, "zone_lon": 2.3522,
                "time_offset": 50
            },
            {
                "departure": "CDG", "arrival": "BRU",
                "cross_zone": "Belgium", "zone_lat": 50.9023, "zone_lon": 4.4844,
                "time_offset": 45
            },
            
            # Routes crossing Belgium zone (MEDIUM risk)
            {
                "departure": "LHR", "arrival": "CDG",
                "cross_zone": "Belgium", "zone_lat": 50.9023, "zone_lon": 4.4844,
                "time_offset": 60
            },
            {
                "departure": "AMS", "arrival": "ORY",
                "cross_zone": "Belgium", "zone_lat": 50.9023, "zone_lon": 4.4844,
                "time_offset": 40
            },
            
            # Routes crossing Germany zone (MEDIUM risk)
            {
                "departure": "TXL", "arrival": "ORY",
                "cross_zone": "Germany", "zone_lat": 52.5520, "zone_lon": 13.2887,
                "time_offset": 70
            },
            {
                "departure": "TXL", "arrival": "FCO",
                "cross_zone": "Germany", "zone_lat": 52.5520, "zone_lon": 13.2887,
                "time_offset": 75
            },
            {
                "departure": "CDG", "arrival": "AMS",
                "cross_zone": "Germany", "zone_lat": 52.5520, "zone_lon": 13.2887,
                "time_offset": 80
            },
            
            # Routes crossing London zone
            {
                "departure": "CDG", "arrival": "LHR",
                "cross_zone": "London", "zone_lat": 51.4700, "zone_lon": -0.4543,
                "time_offset": 35
            },
            {
                "departure": "ORY", "arrival": "LHR",
                "cross_zone": "London", "zone_lat": 51.4700, "zone_lon": -0.4543,
                "time_offset": 90
            },
            
            # Routes crossing Alpine region
            {
                "departure": "FCO", "arrival": "CDG",
                "cross_zone": "Alpine", "zone_lat": 48.2082, "zone_lon": 16.3738,
                "time_offset": 100
            },
            {
                "departure": "BRU", "arrival": "FCO",
                "cross_zone": "Alpine", "zone_lat": 48.2082, "zone_lon": 16.3738,
                "time_offset": 65
            },
            
            # Routes crossing Italy zone
            {
                "departure": "CDG", "arrival": "FCO",
                "cross_zone": "Italy", "zone_lat": 41.8002, "zone_lon": 12.2388,
                "time_offset": 110
            },
            {
                "departure": "BRU", "arrival": "MAD",
                "cross_zone": "Italy", "zone_lat": 41.8002, "zone_lon": 12.2388,
                "time_offset": 120
            },
            
            # Routes crossing Spain zone
            {
                "departure": "CDG", "arrival": "MAD",
                "cross_zone": "Spain", "zone_lat": 40.4718, "zone_lon": -3.5626,
                "time_offset": 130
            },
            {
                "departure": "ORY", "arrival": "MAD",
                "cross_zone": "Spain", "zone_lat": 40.4718, "zone_lon": -3.5626,
                "time_offset": 140
            },
            
            # Routes crossing Northern France
            {
                "departure": "TXL", "arrival": "CRL",  # Brussels Charleroi - adds variety
                "cross_zone": "Northern France", "zone_lat": 50.6292, "zone_lon": 3.0573,
                "time_offset": 85
            },
            {
                "departure": "LHR", "arrival": "ORY",
                "cross_zone": "Northern France", "zone_lat": 50.6292, "zone_lon": 3.0573,
                "time_offset": 95
            },
            
            # Routes avoiding lightning zones (control group)
            {
                "departure": "MAD", "arrival": "LHR",
                "cross_zone": None, "zone_lat": None, "zone_lon": None,
                "time_offset": 150
            },
            {
                "departure": "FCO", "arrival": "AMS",
                "cross_zone": None, "zone_lat": None, "zone_lon": None,
                "time_offset": 160
            }
        ]
        
        for route in flight_routes:
            dep_airport = self.AIRPORTS.get(route["departure"])
            arr_airport = self.AIRPORTS.get(route["arrival"])
            
            # Skip if airport not defined
            if not dep_airport or not arr_airport:
                continue
            
            # Use crossing zone position if provided, otherwise use midpoint
            if route["cross_zone"]:
                flight_lat = route["zone_lat"] + random.uniform(-0.3, 0.3)
                flight_lon = route["zone_lon"] + random.uniform(-0.3, 0.3)
                # Synchronize flight time to overlap with lightning window
                dep_time = self.base_time + timedelta(minutes=route["time_offset"])
            else:
                # Midpoint position for non-affected flights
                flight_lat = (dep_airport["latitude"] + arr_airport["latitude"]) / 2
                flight_lon = (dep_airport["longitude"] + arr_airport["longitude"]) / 2
                dep_time = self.base_time + timedelta(minutes=random.randint(200, 250))
            
            arr_time = dep_time + timedelta(hours=random.randint(1, 3))
            
            flights.append({
                "flight_number": f"AF{flight_num}",
                "departure": route["departure"],
                "arrival": route["arrival"],
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "current_position_latitude": flight_lat,
                "current_position_longitude": flight_lon,
                "altitude": random.uniform(8000, 12000),
                "speed": random.uniform(450, 550),
                "aircraft_type": random.choice(["A380", "B777", "A350", "B787", "A320", "E190"]),
                "airline": random.choice(["Air France", "British Airways", "KLM", "Lufthansa", "Brussels Airlines", "SWISS", "Alitalia"]),
                "status": "in_flight"
            })
            flight_num += 1
        
        return flights
    
    def populate_lightning_strikes(self, strikes_data: list) -> tuple:
        """Populate lightning strikes table.
        
        Args:
            strikes_data: List of lightning strike records
            
        Returns:
            Tuple of (number inserted, mapping of lightning_id to db_id)
        """
        try:
            # Transform data to match database schema
            transformed = []
            for strike in strikes_data:
                transformed.append({
                    "id": strike["lightning_id"],
                    "latitude": strike["latitude"],
                    "longitude": strike["longitude"],
                    "altitude": strike["altitude"],
                    "signal": strike["intensity"],  # 'signal' is mapped to 'intensity' in db
                    "timestamp": strike["timestamp"],
                    "source": strike.get("source", "demo"),
                    "processed_at": datetime.now()
                })
            
            self.warehouse.insert_lightning_data(transformed)
            logger.info("[OK] {} eclairs inseres".format(len(transformed)))
            
            # Retrieve actual IDs from database
            inserted_data = self.warehouse.query_lightning_data()
            lightning_id_map = {record["lightning_id"]: record["id"] for record in inserted_data}
            
            return len(transformed), lightning_id_map
        except Exception as e:
            logger.error("[ERREUR] Insertion eclairs: {}".format(str(e)))
            return 0, {}
    
    def populate_flights(self, flights_data: list) -> tuple:
        """Populate flights table.
        
        Args:
            flights_data: List of flight records
            
        Returns:
            Tuple of (number inserted, mapping of flight_number to db_id)
        """
        try:
            # Transform data to match database schema
            transformed = []
            for flight in flights_data:
                departure = flight["departure"]
                arrival = flight["arrival"]
                route = f"{departure}-{arrival}"
                
                transformed.append({
                    "flight_number": flight["flight_number"],
                    "departure": departure,
                    "arrival": arrival,
                    "route": route,
                    "departure_time": flight["departure_time"],
                    "arrival_time": flight["arrival_time"],
                    "aircraft_type": flight["aircraft_type"],
                    "source": "demo"
                })
            
            self.warehouse.insert_flights_data(transformed)
            logger.info("[OK] {} vols inseres".format(len(transformed)))
            
            # Retrieve actual IDs from database
            inserted_data = self.warehouse.query_flights_data()
            flight_id_map = {record["flight_number"]: record["id"] for record in inserted_data}
            
            return len(transformed), flight_id_map
        except Exception as e:
            logger.error("[ERREUR] Insertion vols: {}".format(str(e)))
            return 0
    
    def calculate_and_populate_disruptions(self, strikes_data: list, flights_data: list, 
                                          lightning_id_map: dict, flight_id_map: dict) -> int:
        """Calculate disruptions based on lightning strikes and flights.
        
        Args:
            strikes_data: Original lightning data
            flights_data: Original flight data
            lightning_id_map: Mapping of lightning_id -> database id
            flight_id_map: Mapping of flight_number -> database id
            
        Returns:
            Number of disruptions inserted
        """
        disruptions = []
        
        # Constants from DisruptionCalculator
        ALERT_RADIUS_KM = 50
        TIME_WINDOW_MINUTES = 30
        
        for flight in flights_data:
            flight_number = flight["flight_number"]
            flight_db_id = flight_id_map.get(flight_number)
            
            if not flight_db_id:
                logger.warning("[WARN] Vol {} non trouve dans la BD, perturbation ignoree".format(flight_number))
                continue
            
            flight_lat = flight["current_position_latitude"]
            flight_lon = flight["current_position_longitude"]
            dep_time = flight["departure_time"]
            arr_time = flight["arrival_time"]
            
            affected_strikes = []
            
            for strike in strikes_data:
                strike_lat = strike["latitude"]
                strike_lon = strike["longitude"]
                strike_time = strike["timestamp"]
                
                # Calculate distance (simplified Haversine)
                distance = self._calculate_distance(flight_lat, flight_lon, strike_lat, strike_lon)
                
                # Check if strike is within alert radius
                if distance <= ALERT_RADIUS_KM:
                    # Check if strike occurs during flight window + buffer
                    time_before = dep_time - timedelta(minutes=TIME_WINDOW_MINUTES)
                    time_after = arr_time + timedelta(minutes=TIME_WINDOW_MINUTES)
                    
                    if time_before <= strike_time <= time_after:
                        affected_strikes.append({
                            "lightning_id": strike["lightning_id"],
                            "distance_km": distance,
                            "intensity": strike["intensity"],
                            "time_diff_minutes": int((strike_time - dep_time).total_seconds() / 60)
                        })
            
            # Create disruption record if strikes affected flight
            if affected_strikes:
                # Determine risk level
                max_intensity = max(s["intensity"] for s in affected_strikes)
                min_distance = min(s["distance_km"] for s in affected_strikes)
                
                if max_intensity > 80:
                    risk_level = "CRITICAL"
                    probability = 0.95
                elif max_intensity > 60:
                    risk_level = "HIGH"
                    probability = 0.75
                elif max_intensity > 40:
                    risk_level = "MEDIUM"
                    probability = 0.50
                else:
                    risk_level = "LOW"
                    probability = 0.25
                
                disruptions.append({
                    "flight_id": flight_db_id,
                    "distance_km": min_distance,
                    "time_difference_minutes": 0,
                    "disruption_probability": probability,
                    "risk_level": risk_level
                })
        
        # Insert disruptions
        try:
            if disruptions:
                self.warehouse.insert_disruptions_data(disruptions)
                logger.info("[OK] {} perturbations inserees".format(len(disruptions)))
            else:
                logger.info("[INFO] Aucune perturbation detectee")
            return len(disruptions)
        except Exception as e:
            logger.error("[ERREUR] Insertion perturbations: {}".format(str(e)))
            return 0
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    def run(self):
        """Run complete demo data population."""
        print("\n" + "="*70)
        print("POPULATION DE DONNEES DE DEMO COMPLETES")
        print("="*70)
        
        try:
            # Connect to database
            self.db_connection.connect()
            self.warehouse = DataWarehouse(self.db_connection)
            print("[OK] Connexion a PostgreSQL etablie")
            
            # Generate data
            print("\n[1/2] Generation de donnees d'eclairs...")
            lightning_data = self.generate_lightning_strikes()
            print("      > {} eclairs generes".format(len(lightning_data)))
            
            print("\n[2/2] Generation de donnees de vols...")
            flights_data = self.generate_flights()
            print("      > {} vols generes".format(len(flights_data)))
            
            # Populate database
            print("\n[INSERTION] Population de la base de donnees...")
            strike_count, lightning_id_map = self.populate_lightning_strikes(lightning_data)
            flight_count, flight_id_map = self.populate_flights(flights_data)
            disruption_count = self.calculate_and_populate_disruptions(
                lightning_data, flights_data, lightning_id_map, flight_id_map
            )
            
            # Summary
            print("\n" + "="*70)
            print("RESUME DE LA POPULATION")
            print("="*70)
            print("[OK] Eclairs inseres:          {:3d}".format(strike_count))
            print("[OK] Vols inseres:             {:3d}".format(flight_count))
            print("[OK] Perturbations deteclees:  {:3d}".format(disruption_count))
            print("\nCAS DE TEST COUVERTS:")
            print("  * Clusters d'eclairs haute intensite (CRITICAL)")
            print("  * Eclairs intensite moyenne (HIGH/MEDIUM)")
            print("  * Eclairs disperses basse intensite (LOW)")
            print("  * Vols passant par zones a risque")
            print("  * Vols evitant zones a risque")
            print("  * Vols avec differents horaires et durees")
            print("="*70)
            print("\nPROCHAINES ETAPES:")
            print("  1. Executez: python verify_demo_data.py")
            print("     -> pour verifier les donnees inserees")
            print("  2. Executez: python app.py")
            print("     -> pour lancer le dashboard Streamlit")
            print("="*70 + "\n")
            
        except Exception as e:
            logger.error("Erreur lors de la population: {}".format(str(e)))
            print("[ERREUR] {}".format(str(e)))
        finally:
            self.db_connection.disconnect()


def main():
    """Main entry point."""
    generator = DemoDataGenerator()
    generator.run()


if __name__ == "__main__":
    main()
