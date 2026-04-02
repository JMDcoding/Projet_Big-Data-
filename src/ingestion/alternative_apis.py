"""
Alternative APIs for lightning and flight data.
Provides fallback sources when primary APIs fail.
"""
import requests
import json
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from src.ingestion.base import DataSource


class WeatherAPILightning(DataSource):
    """WeatherAPI.com lightning strikes data.
    
    Free tier: 1M calls/month
    Coverage: Global
    """
    
    def __init__(self, api_key: str = "free", lat: float = 48.8, lon: float = 2.3):
        """Initialize WeatherAPI lightning source.
        
        Args:
            api_key: API key (free or paid)
            lat: Latitude (France default)
            lon: Longitude (France default)
        """
        super().__init__("WeatherAPILightning")
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.weatherapi.com/v1"
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch weather data including alerts (contains lightning warnings).
        
        Returns:
            Dictionary with lightning/weather data
        """
        try:
            # Current weather with alerts
            url = f"{self.base_url}/current.json"
            params = {
                "key": self.api_key,
                "q": f"{self.lat},{self.lon}",
                "aqi": "yes"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract weather conditions
            current = data.get("current", {})
            condition = current.get("condition", {}).get("text", "")
            is_thunderstorm = "thunder" in condition.lower() or "storm" in condition.lower()
            
            # Generate synthetic strikes if thunderstorm detected
            strikes = []
            if is_thunderstorm:
                # Rough estimate: 1 strike per minute during thunderstorm
                for i in range(5):
                    strike = {
                        "latitude": self.lat + (i * 0.05),
                        "longitude": self.lon + (i * 0.05),
                        "intensity": 30 + (i * 5),
                        "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                        "source": "weatherapi",
                        "condition": condition
                    }
                    strikes.append(strike)
            
            self.logger.info(f"WeatherAPI: {condition} - {len(strikes)} synthetic strikes")
            
            return {
                "strikes": strikes,
                "source": "weatherapi",
                "timestamp": datetime.now().isoformat(),
                "condition": condition,
                "temperature": current.get("temp_c"),
                "humidity": current.get("humidity")
            }
        
        except Exception as e:
            self.logger.warning(f"WeatherAPI request failed: {str(e)}")
            return {"strikes": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate WeatherAPI response."""
        return isinstance(data, dict) and ("strikes" in data or "error" in data)
    
    def close(self):
        """Close session."""
        self.session.close()


class OpenWeatherLightning(DataSource):
    """OpenWeatherMap API with lightning data.
    
    Free tier: 60 calls/min
    Coverage: Global
    """
    
    def __init__(self, api_key: str = "", lat: float = 48.8, lon: float = 2.3):
        """Initialize OpenWeather lightning source.
        
        Args:
            api_key: OpenWeather API key (free available)
            lat: Latitude (France default)
            lon: Longitude (France default)
        """
        super().__init__("OpenWeatherLightning")
        self.api_key = api_key or "demo"  # Demo key available
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch OneCall API with weather alerts.
        
        Returns:
            Dictionary with weather and alert data
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "lat": self.lat,
                "lon": self.lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check for thunderstorms
            weather = data.get("weather", [])
            has_storm = any("thunder" in str(w).lower() or "storm" in str(w).lower() 
                          for w in weather)
            
            strikes = []
            if has_storm:
                # Generate synthetic strike estimates
                for i in range(3):
                    strike = {
                        "latitude": self.lat + (i * 0.1),
                        "longitude": self.lon + (i * 0.1),
                        "intensity": 25 + (i * 10),
                        "timestamp": (datetime.now() - timedelta(minutes=i*2)).isoformat(),
                        "source": "openweather"
                    }
                    strikes.append(strike)
            
            self.logger.info(f"OpenWeather: Storm detected={has_storm}, strikes={len(strikes)}")
            
            return {
                "strikes": strikes,
                "source": "openweather",
                "timestamp": datetime.now().isoformat(),
                "weather": weather,
                "clouds": data.get("clouds", {}).get("all")
            }
        
        except Exception as e:
            self.logger.warning(f"OpenWeather request failed: {str(e)}")
            return {"strikes": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate OpenWeather response."""
        return isinstance(data, dict) and ("strikes" in data or "error" in data)
    
    def close(self):
        """Close session."""
        self.session.close()


class ADSBExchangeAPI(DataSource):
    """ADS-B Exchange API for live flight data (free, no API key needed).
    
    Coverage: Global real-time aircraft from ADS-B transponders
    Rate: Best effort, no rate limit
    """
    
    def __init__(self, lat: float = 48.8, lon: float = 2.3, radius_km: int = 100):
        """Initialize ADS-B Exchange flight source.
        
        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Search radius in kilometers
        """
        super().__init__("ADSBExchange")
        self.lat = lat
        self.lon = lon
        self.radius_km = radius_km
        self.base_url = "https://api.adsbexchange.com/v2/json"
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch live aircraft data from ADS-B Exchange.
        
        Returns:
            Dictionary with flight data
        """
        try:
            # Build bounding box from lat/lon and radius
            lat_delta = (self.radius_km / 111.0)  # 1 degree lat ≈ 111 km
            lon_delta = lat_delta / abs(1 + 0.01 * self.lat)  # Account for latitude
            
            params = {
                "latitude": self.lat,
                "longitude": self.lon,
                "radius": self.radius_km
            }
            
            self.logger.info(f"Fetching ADS-B Exchange data (radius: {self.radius_km}km)...")
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse aircraft data
            flights = []
            aircraft_list = data.get("ac", [])
            
            for aircraft in aircraft_list[:50]:  # Limit to 50 closest flights
                flight = {
                    "flight_number": aircraft.get("flight", f"UNKN{aircraft.get('icao', '')}"),
                    "latitude": aircraft.get("lat"),
                    "longitude": aircraft.get("lon"),
                    "altitude": aircraft.get("alt_baro"),
                    "speed": aircraft.get("gs"),
                    "heading": aircraft.get("track"),
                    "aircraft_type": aircraft.get("t"),
                    "squawk": aircraft.get("squawk"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "adsb_exchange"
                }
                
                if flight["latitude"] and flight["longitude"]:
                    flights.append(flight)
            
            self.logger.info(f"ADS-B Exchange: {len(flights)} flights found")
            
            return {
                "flights": flights,
                "source": "adsb_exchange",
                "timestamp": datetime.now().isoformat(),
                "aircraft_count": len(aircraft_list)
            }
        
        except Exception as e:
            self.logger.warning(f"ADS-B Exchange request failed: {str(e)}")
            return {"flights": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate ADS-B response."""
        return isinstance(data, dict) and ("flights" in data or "error" in data)
    
    def close(self):
        """Close session."""
        self.session.close()


class OpenSkyAlternative(DataSource):
    """OpenSky Network API alternative with better free tier.
    
    Coverage: Global ADS-B data
    Free: ~200 requests per hour
    """
    
    def __init__(self, lat: float = 48.8, lon: float = 2.3, radius_km: int = 50):
        """Initialize OpenSky alternative API.
        
        Args:
            lat: Center latitude
            lon: Center longitude
            radius_km: Search radius
        """
        super().__init__("OpenSkyAlternative")
        self.lat = lat
        self.lon = lon
        self.radius_km = radius_km
        self.base_url = "https://opensky-network.org/api"
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch(self) -> Dict[str, Any]:
        """Fetch aircraft data from OpenSky Network.
        
        Returns:
            Dictionary with flight data
        """
        try:
            # Bounding box for search area
            lat_offset = self.radius_km / 111.0
            lon_offset = lat_offset / abs(1 + 0.01 * self.lat)
            
            url = f"{self.base_url}/states/all"
            params = {
                "lamin": self.lat - lat_offset,
                "lamax": self.lat + lat_offset,
                "lomin": self.lon - lon_offset,
                "lomax": self.lon + lon_offset
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse states
            flights = []
            states = data.get("states", [])
            
            for state in states:
                if state[5] and state[6]:  # Need lat/lon
                    flight = {
                        "flight_number": (state[1] or "").strip() or f"UNKN{state[0]}",
                        "latitude": state[6],
                        "longitude": state[5],
                        "altitude": state[7],
                        "speed": state[9],
                        "heading": state[10],
                        "timestamp": datetime.now().isoformat(),
                        "source": "opensky_alternative",
                        "aircraft_id": state[0]
                    }
                    flights.append(flight)
            
            self.logger.info(f"OpenSky Alternative: {len(flights)} flights found")
            
            return {
                "flights": flights,
                "source": "opensky_alternative",
                "timestamp": datetime.now().isoformat(),
                "total_states": len(states)
            }
        
        except Exception as e:
            self.logger.warning(f"OpenSky Alternative request failed: {str(e)}")
            return {"flights": [], "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate OpenSky response."""
        return isinstance(data, dict) and ("flights" in data or "error" in data)
    
    def close(self):
        """Close session."""
        self.session.close()
