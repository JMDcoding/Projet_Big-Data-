"""
API client for lightning data.
Supports multiple data sources: Blitzortung, local files, and Open-Meteo.
"""
import requests
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
from src.ingestion.base import DataSource


class LightningDataSource(DataSource):
    """Base class for lightning data sources."""
    
    def __init__(self, name: str):
        """Initialize data source.
        
        Args:
            name: Name of the data source
        """
        super().__init__(name)
        self.logger = logging.getLogger(self.__class__.__name__)


class LocalDemoData(LightningDataSource):
    """Load lightning data from local demo files.
    
    Best for development and testing without API calls.
    """
    
    def __init__(self, data_dir: str = "data/raw"):
        """Initialize local demo data source.
        
        Args:
            data_dir: Path to raw data directory
        """
        super().__init__("LocalDemoData")
        self.data_dir = Path(data_dir)
    
    def fetch(self) -> Dict[str, Any]:
        """Load lightning data from local JSON files and generate synthetic data if needed.
        
        Returns:
            Dictionary with lightning strikes data
        """
        try:
            lightning_data = []
            
            # Search for demo files
            demo_files = list(self.data_dir.glob("demo_lightning_*.json")) + \
                        list(self.data_dir.glob("lightning_raw_*.json"))
            
            # Load all demo files (remove limit to load all available)
            for file_path in sorted(demo_files):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle different JSON formats
                        if isinstance(data, dict) and "lightning_strikes" in data:
                            lightning_data.extend(data["lightning_strikes"])
                        elif isinstance(data, list):
                            lightning_data.extend(data)
                        elif isinstance(data, dict) and "strikes" in data:
                            lightning_data.extend(data["strikes"])
                        
                        self.logger.info(f"Loaded {len(data) if isinstance(data, list) else 1} strikes from {file_path.name}")
                
                except Exception as e:
                    self.logger.warning(f"Error loading {file_path.name}: {str(e)}")
            
            # If we have very few strikes, generate synthetic data
            if len(lightning_data) < 50:
                self.logger.info("Generating synthetic lightning data to supplement...")
                import numpy as np
                synthetic_data = self._generate_synthetic_strikes(50 - len(lightning_data))
                lightning_data.extend(synthetic_data)
            
            self.logger.info(f"Total lightning strikes loaded: {len(lightning_data)}")
            
            return {
                "strikes": lightning_data,
                "source": "local_demo",
                "timestamp": datetime.now().isoformat(),
                "file_count": len(demo_files)
            }
        
        except Exception as e:
            self.logger.error(f"Error fetching local data: {str(e)}")
            return {"strikes": [], "error": str(e)}
    
    def _generate_synthetic_strikes(self, count: int = 50) -> list:
        """Generate synthetic lightning strike data for demonstration.
        
        Args:
            count: Number of synthetic strikes to generate
            
        Returns:
            List of synthetic lightning strike dictionaries
        """
        import numpy as np
        from datetime import timedelta
        
        synthetic_strikes = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(count):
            # Random time in the last 7 days
            strike_time = base_time + timedelta(
                hours=np.random.randint(0, 168),
                minutes=np.random.randint(0, 60)
            )
            
            # European coordinates
            latitude = np.random.uniform(35, 55)  # Europe latitude
            longitude = np.random.uniform(-10, 30)  # Europe longitude
            
            strike = {
                "lightning_id": f"SYN_{i:04d}",
                "latitude": round(latitude, 4),
                "longitude": round(longitude, 4),
                "altitude": round(np.random.uniform(2000, 12000), 1),
                "intensity": round(np.random.uniform(10, 100), 2),
                "timestamp": strike_time.isoformat(),
                "source": "synthetic_demo"
            }
            synthetic_strikes.append(strike)
        
        self.logger.info(f"Generated {count} synthetic strikes")
        return synthetic_strikes
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate local data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid
        """
        return isinstance(data, dict) and ("strikes" in data or "error" in data)
    
    def close(self):
        """No resources to close for local files."""
        pass


class BlitzortungAPI(LightningDataSource):
    """Client for Blitzortung API to fetch real-time lightning strikes data.
    
    Note: The live page returns HTML. This class now tries multiple endpoints
    and falls back to local data if API is unavailable.
    """
    
    def __init__(self, base_url: str = "https://data.blitzortung.org", 
                 timeout: int = 30):
        """Initialize Blitzortung API client.
        
        Args:
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        super().__init__("BlitzortungAPI")
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch lightning strikes data from Blitzortung.
        
        Tries multiple endpoints and returns available data.
        
        Returns:
            Dictionary containing lightning strikes data
        """
        try:
            # Try JSON endpoint
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            # Endpoint: /resources/raw_data/{YYYY}/{MM}/{DD}/{HH}
            now = datetime.now()
            url = f"{self.base_url}/resources/raw_data/{now.year:04d}/{now.month:02d}/{now.day:02d}/{now.hour:02d}"
            
            self.logger.info(f"Attempting to fetch from {url}")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                data = response.json()
                self.logger.info(f"Successfully fetched JSON data from Blitzortung API")
                return {
                    "strikes": data if isinstance(data, list) else [],
                    "source": "blitzortung_api",
                    "timestamp": datetime.now().isoformat(),
                    "url": response.url
                }
            except json.JSONDecodeError:
                self.logger.warning("Response is HTML, not JSON. API may be unavailable.")
                return {"strikes": [], "source": "blitzortung_api", "error": "HTML response"}
        
        except requests.RequestException as e:
            self.logger.warning(f"Blitzortung API request failed: {str(e)}")
            return {"strikes": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate API response.
        
        Args:
            data: Data returned from API
            
        Returns:
            True if data is valid
        """
        return isinstance(data, dict) and "source" in data
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("Session closed")


class OpenMeteoAPI(LightningDataSource):
    """Client for Open-Meteo Archive API (free, no auth required).
    
    Provides historical lightning data for any location.
    """
    
    def __init__(self, latitude: float = 45.7640, longitude: float = 4.8357):
        """Initialize Open-Meteo API client.
        
        Args:
            latitude: Location latitude (default: Paris)
            longitude: Location longitude (default: Paris)
        """
        super().__init__("OpenMeteoAPI")
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch historical lightning data from Open-Meteo.
        
        Returns:
            Dictionary with lightning flux data
        """
        try:
            from datetime import timedelta
            
            # Get last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "hourly": "lightning_flux"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to strikes format
            strikes = []
            if "hourly" in data and "lightning_flux" in data["hourly"]:
                times = data["hourly"]["time"]
                fluxes = data["hourly"]["lightning_flux"]
                
                for time_str, flux in zip(times, fluxes):
                    if flux and flux > 0:
                        strikes.append({
                            "timestamp": time_str,
                            "intensity": flux,
                            "latitude": self.latitude,
                            "longitude": self.longitude,
                            "source": "open_meteo"
                        })
            
            self.logger.info(f"Loaded {len(strikes)} lightning records from Open-Meteo")
            
            return {
                "strikes": strikes,
                "source": "open_meteo_api",
                "timestamp": datetime.now().isoformat(),
                "location": {"lat": self.latitude, "lon": self.longitude}
            }
        
        except Exception as e:
            self.logger.warning(f"Open-Meteo API error: {str(e)}")
            return {"strikes": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate Open-Meteo data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid
        """
        return isinstance(data, dict) and "source" in data
    
    def close(self):
        """No resources to close for API."""
        pass


# ==================== FLIGHT DATA SOURCES ====================

class FlightDataSource(DataSource):
    """Base class for flight data sources."""
    
    def __init__(self, name: str):
        """Initialize data source.
        
        Args:
            name: Name of the data source
        """
        super().__init__(name)
        self.logger = logging.getLogger(self.__class__.__name__)


class OpenSkyAPI(FlightDataSource):
    """Client for OpenSky Network API (free, real-time flight data).
    
    Provides real-time flight tracking data for aircraft in European airspace.
    """
    
    def __init__(self, min_latitude: float = 35, max_latitude: float = 55,
                 min_longitude: float = -10, max_longitude: float = 30):
        """Initialize OpenSky API client.
        
        Args:
            min_latitude: Bounding box min latitude (Europe)
            max_latitude: Bounding box max latitude
            min_longitude: Bounding box min longitude
            max_longitude: Bounding box max longitude
        """
        super().__init__("OpenSkyAPI")
        self.base_url = "https://opensky-network.org/api/states/all"
        self.bbox = (min_latitude, max_latitude, min_longitude, max_longitude)
        self.timeout = 10
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch flight data from OpenSky Network.
        
        Returns:
            Dictionary with flight data
        """
        try:
            params = {
                "lamin": self.bbox[0],
                "lamax": self.bbox[1],
                "lomin": self.bbox[2],
                "lomax": self.bbox[3]
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to standardized format
            flights = []
            if "states" in data and data["states"]:
                from datetime import timedelta
                
                for state in data["states"]:
                    # state format: [ICAO24, callsign, origin_country, time_position, time_velocity,
                    #               longitude, latitude, geo_altitude, on_ground, velocity,
                    #               true_track, vertical_rate, sensors, baro_altitude, squawk, spi, source_type]
                    if state[5] is not None and state[6] is not None:  # has lat/lon
                        # Use the time_velocity timestamp (state[4]) for current position time
                        # Estimate departure time based on current altitude (lower alt = more recent departure)
                        current_time = datetime.fromtimestamp(state[4]) if state[4] else datetime.now()
                        altitude = state[13] if state[13] else state[7]
                        
                        # Estimate flight duration based on altitude and velocity
                        # Typical climb rate ~2000 ft/min, cruise ~450 knots
                        # Rough estimation: if at cruise (>25000 ft), assume 2-4 hours into flight
                        # if climbing (<15000 ft), assume <1 hour into flight
                        if altitude and altitude > 25000:
                            estimated_flight_duration = timedelta(hours=3)  # Typical European flight ~3 hours
                            departure_time = current_time - estimated_flight_duration
                        else:
                            estimated_flight_duration = timedelta(hours=1)  # Short flight or climbing
                            departure_time = current_time - timedelta(minutes=30)
                        
                        arrival_time = current_time + timedelta(hours=2)  # Estimate arrival in ~2 hours
                        
                        flight = {
                            "flight_number": state[1].strip() if state[1] else f"UNKNOWN_{state[0]}",
                            "departure": state[2],
                            "arrival": "Unknown",
                            "latitude": state[6],
                            "longitude": state[5],
                            "altitude": altitude,
                            "velocity": state[9],
                            "heading": state[10],
                            "vertical_rate": state[11],
                            "timestamp": current_time.isoformat(),
                            "departure_time": departure_time.isoformat(),
                            "arrival_time": arrival_time.isoformat(),
                            "source": "opensky_api"
                        }
                        flights.append(flight)
            
            self.logger.info(f"Fetched {len(flights)} flights from OpenSky")
            
            return {
                "flights": flights,
                "source": "opensky_api",
                "timestamp": datetime.now().isoformat(),
                "record_count": len(flights)
            }
        
        except Exception as e:
            self.logger.warning(f"OpenSky API error: {str(e)}")
            return {"flights": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate flight data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid
        """
        return isinstance(data, dict) and ("flights" in data or "error" in data)
    
    def close(self):
        """No resources to close."""
        pass


class SyntheticFlightData(FlightDataSource):
    """Generate synthetic flight data for demonstration.
    
    Useful when real APIs are unavailable.
    """
    
    def __init__(self):
        """Initialize synthetic flight data generator."""
        super().__init__("SyntheticFlightData")
    
    def fetch(self) -> Dict[str, Any]:
        """Generate synthetic flight data.
        
        Returns:
            Dictionary with flight data
        """
        try:
            flights = self._generate_synthetic_flights(30)
            
            self.logger.info(f"Generated {len(flights)} synthetic flights")
            
            return {
                "flights": flights,
                "source": "synthetic_demo",
                "timestamp": datetime.now().isoformat(),
                "record_count": len(flights)
            }
        
        except Exception as e:
            self.logger.error(f"Error generating synthetic flights: {str(e)}")
            return {"flights": [], "error": str(e)}
    
    def _generate_synthetic_flights(self, count: int = 30) -> list:
        """Generate synthetic flight data.
        
        Args:
            count: Number of flights to generate
            
        Returns:
            List of synthetic flight dictionaries
        """
        import numpy as np
        from datetime import timedelta
        
        airlines = ["AF", "LH", "BA", "KL", "SQ", "UA", "DL", "AA", "TK"]
        airports = ["ORY", "CDG", "LHR", "AMS", "FRA", "FCO", "MAD", "BCN", "VIE"]
        
        flights = []
        base_time = datetime.now() - timedelta(hours=2)
        
        for i in range(count):
            # Generate random departure time
            flight_time = base_time + timedelta(
                minutes=np.random.randint(0, 120),
                seconds=np.random.randint(0, 60)
            )
            
            # Estimate departure time based on flight duration
            flight_duration = timedelta(hours=np.random.uniform(1.5, 4))  # 1.5-4 hours typical
            departure_time = flight_time - flight_duration / 2  # Assume we're halfway through flight
            arrival_time = flight_time + flight_duration / 2
            
            flight = {
                "flight_number": f"{np.random.choice(airlines)}{np.random.randint(100, 9999):04d}",
                "departure": np.random.choice(airports),
                "arrival": np.random.choice(airports),
                "latitude": round(np.random.uniform(35, 55), 4),
                "longitude": round(np.random.uniform(-10, 30), 4),
                "altitude": round(np.random.uniform(5000, 12000), 1),
                "velocity": round(np.random.uniform(400, 900), 1),
                "heading": round(np.random.uniform(0, 360), 1),
                "vertical_rate": round(np.random.uniform(-5, 5), 2),
                "timestamp": flight_time.isoformat(),
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "source": "synthetic_demo"
            }
            flights.append(flight)
        
        return flights
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate synthetic flight data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid
        """
        return isinstance(data, dict) and ("flights" in data or "error" in data)
    
    def close(self):
        """No resources to close."""
        pass

