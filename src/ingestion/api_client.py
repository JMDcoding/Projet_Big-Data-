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



class AviationStackAPI(FlightDataSource):
    """Client for AviationStack API - real-time flight data with complete route information.
    
    Provides detailed flight information including:
    - Origin & destination airports (IATA codes & names)
    - Departure and arrival times (scheduled vs actual)
    - Aircraft type
    - Airline information
    - Flight status
    
    Free API: https://aviationstack.com (100 requests/month free tier)
    """
    
    def __init__(self, min_latitude: float = 35, max_latitude: float = 55, 
                 min_longitude: float = -10, max_longitude: float = 30):
        """Initialize AviationStack API client.
        
        Args:
            min_latitude: Bounding box min latitude (default: Europe)
            max_latitude: Bounding box max latitude
            min_longitude: Bounding box min longitude
            max_longitude: Bounding box max longitude
        """
        super().__init__("AviationStackAPI")
        
        # IMPORTANT: Set your AviationStack API key
        # Get free API key at: https://aviationstack.com/
        self.api_key = "free"  # Free tier key (100 requests/month)
        self.base_url = "https://api.aviationstack.com/v1/flights"
        self.bbox = (min_latitude, max_latitude, min_longitude, max_longitude)
        self.timeout = 15
        self.logger.info("AviationStackAPI initialized - provides full route/destination data")
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch flight data from AviationStack API.
        
        Returns:
            Dictionary with flight data including destination info
        """
        try:
            params = {
                "access_key": self.api_key,
                "limit": 100
            }
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            flights = []
            if "data" in data and isinstance(data["data"], list):
                for flight in data["data"]:
                    try:
                        flight_dict = {
                            "flight_number": self._get_flight_number(flight),
                            "flight_iata": flight.get("flight", {}).get("iata", ""),
                            "flight_icao": flight.get("flight", {}).get("icao", ""),
                            
                            # Departure information
                            "departure_airport": flight.get("departure", {}).get("iata", ""),
                            "departure_airport_name": flight.get("departure", {}).get("airport", ""),
                            "departure_city": flight.get("departure", {}).get("city", ""),
                            "departure_country": flight.get("departure", {}).get("country", ""),
                            "departure_scheduled": flight.get("departure", {}).get("scheduled", ""),
                            "departure_actual": flight.get("departure", {}).get("actual", ""),
                            
                            # Arrival information
                            "arrival_airport": flight.get("arrival", {}).get("iata", ""),
                            "arrival_airport_name": flight.get("arrival", {}).get("airport", ""),
                            "arrival_city": flight.get("arrival", {}).get("city", ""),
                            "arrival_country": flight.get("arrival", {}).get("country", ""),
                            "arrival_scheduled": flight.get("arrival", {}).get("scheduled", ""),
                            "arrival_actual": flight.get("arrival", {}).get("actual", ""),
                            "arrival_estimated": flight.get("arrival", {}).get("estimated", ""),
                            
                            # Aircraft information
                            "aircraft_iata": flight.get("aircraft", {}).get("iata", ""),
                            "aircraft_icao": flight.get("aircraft", {}).get("icao", ""),
                            "aircraft_name": flight.get("aircraft", {}).get("name", ""),
                            
                            # Airline information
                            "airline_iata": flight.get("airline", {}).get("iata", ""),
                            "airline_icao": flight.get("airline", {}).get("icao", ""),
                            "airline_name": flight.get("airline", {}).get("name", ""),
                            
                            # Current position (if available)
                            "latitude": flight.get("live", {}).get("latitude"),
                            "longitude": flight.get("live", {}).get("longitude"),
                            "altitude": flight.get("live", {}).get("altitude"),
                            "direction": flight.get("live", {}).get("direction"),
                            
                            # Flight status
                            "flight_status": flight.get("flight_status", ""),
                            
                            # Timestamps
                            "timestamp": datetime.now().isoformat(),
                            "source": "aviationstack_api"
                        }
                        flights.append(flight_dict)
                    except Exception as e:
                        self.logger.warning(f"Error parsing flight data: {str(e)}")
                        continue
            
            self.logger.info(f"Fetched {len(flights)} flights from AviationStack - with destination data")
            
            return {
                "flights": flights,
                "source": "aviationstack_api",
                "timestamp": datetime.now().isoformat(),
                "record_count": len(flights)
            }
        
        except requests.exceptions.RequestException as e:
            if "401" in str(e) or "403" in str(e):
                self.logger.warning(
                    "AviationStack API auth failed. "
                    "Set AVIATIONSTACK_API_KEY environment variable or get key at aviationstack.com"
                )
            else:
                self.logger.warning(f"AviationStack API request failed: {str(e)}")
            return {"flights": [], "error": str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return {"flights": [], "error": str(e)}
    
    def _get_flight_number(self, flight: dict) -> str:
        """Extract flight number from API response."""
        flight_info = flight.get("flight", {})
        iata = flight_info.get("iata", "")
        icao = flight_info.get("icao", "")
        
        if iata:
            return iata
        elif icao:
            return icao
        else:
            airline_code = flight.get("airline", {}).get("iata", "XX")
            flight_num = flight.get("flight", {}).get("number", "0000")
            return f"{airline_code}{flight_num}"
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate flight data."""
        return isinstance(data, dict) and ("flights" in data or "error" in data)
    
    def close(self):
        """No resources to close."""
        pass

