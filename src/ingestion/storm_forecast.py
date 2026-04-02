"""
Storm Forecast API - Détecte les orages actuels et à venir.
Intégration Open-Meteo pour identifier les zones à risque.
"""
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class StormForecastAPI:
    """
    Récupère les prévisions d'orages via Open-Meteo.
    
    Codes météorologiques:
    - 80-82: Averses (potentiellement des orages)
    - 85-86: Averses de neige/pluie neigeuse
    - 95-99: ORAGES VIOLENTS ⚠️
    """
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self, latitude: float = 45.764, longitude: float = 4.8357):
        """
        Initialise le client de prévisions d'orages.
        
        Args:
            latitude: Latitude (défaut: Lyon)
            longitude: Longitude (défaut: Lyon)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract(self) -> Dict:
        """
        Récupère les prévisions de tempête pour les 7 prochains jours.
        
        Returns:
            Dict with storm forecasts and risk assessment
        """
        try:
            self.logger.info(f"Fetching storm forecast for ({self.latitude}, {self.longitude})")
            
            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "Europe/Paris",
                "forecast_days": 7
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract and analyze storm data
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            codes = daily.get("weather_code", [])
            temps_max = daily.get("temperature_2m_max", [])
            precips = daily.get("precipitation_sum", [])
            
            # Analyze storm risk
            forecasts = []
            for i, (date, code, temp, precip) in enumerate(zip(dates, codes, temps_max, precips)):
                risk = self._assess_storm_risk(code)
                
                forecast = {
                    "date": date,
                    "weather_code": code,
                    "temperature_max": temp,
                    "precipitation": precip,
                    "storm_risk": risk,
                    "is_severe": risk in ["SEVERE", "HIGH"],
                    "source": "open_meteo_storms"
                }
                forecasts.append(forecast)
            
            return {
                "status": "success",
                "location": f"({self.latitude}, {self.longitude})",
                "forecasts": forecasts,
                "next_7_days": forecasts,
                "severe_storms": [f for f in forecasts if f["is_severe"]],
                "timestamp": datetime.now().isoformat(),
                "source": "open_meteo"
            }
        
        except Exception as e:
            self.logger.error(f"Error fetching storm forecast: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "source": "open_meteo"
            }
    
    def _assess_storm_risk(self, weather_code: int) -> str:
        """
        Évalue le niveau de risque d'orage selon le code météo WMO.
        
        Args:
            weather_code: Code météo WMO (0-99)
            
        Returns:
            Risk level: NONE, LOW, MEDIUM, HIGH, SEVERE
        """
        # WMO Weather interpretation codes
        if weather_code in [95, 96, 99]:
            return "SEVERE"  # Thunderstorms with hail/heavy
        elif weather_code in [80, 81, 82]:
            return "HIGH"    # Showers (possibly thunderstorms)
        elif weather_code in [85, 86]:
            return "MEDIUM"  # Freezing rain/snow
        elif weather_code in [50, 51, 53, 55, 56, 57, 58, 61, 63, 65, 66, 67, 68, 71, 73, 75]:
            return "LOW"     # Light/moderate rain or snow
        else:
            return "NONE"    # Clear, cloudy but no rain
    
    def get_risk_zones(self, forecasts: List[Dict], 
                      grid_size: int = 5) -> pd.DataFrame:
        """
        Crée une grille de zones à risque pour le dashboard.
        
        Args:
            forecasts: List of forecast dictionaries
            grid_size: Size of risk grid (n x n)
            
        Returns:
            DataFrame with risk zones
        """
        zones = []
        
        # Create a grid around the base coordinates
        for i in range(grid_size):
            for j in range(grid_size):
                # Calculate offset from center (0.5 degrees = ~55km)
                offset = 0.5 * (grid_size - 1) / 2
                lat = self.latitude + (i - offset) * 0.1
                lon = self.longitude + (j - offset) * 0.1
                
                # Get average risk for this zone
                severe_count = sum(1 for f in forecasts if f["is_severe"])
                avg_risk = "HIGH" if severe_count > 0 else "LOW"
                
                zones.append({
                    "zone_id": f"zone_{i}_{j}",
                    "latitude": lat,
                    "longitude": lon,
                    "risk_level": avg_risk,
                    "severe_storm_days": severe_count,
                    "color": self._get_risk_color(avg_risk)
                })
        
        return pd.DataFrame(zones)
    
    def _get_risk_color(self, risk_level: str) -> str:
        """
        Retourne la couleur pour le dashboard selon le risque.
        
        Args:
            risk_level: Risk level string
            
        Returns:
            Hex color code
        """
        colors = {
            "NONE": "#00FF00",      # Green - Safe
            "LOW": "#90EE90",       # Light green
            "MEDIUM": "#FFFF00",    # Yellow
            "HIGH": "#FF8C00",      # Orange
            "SEVERE": "#FF0000"     # Red - Critical
        }
        return colors.get(risk_level, "#808080")
    
    def create_alert(self, forecasts: List[Dict]) -> Optional[Dict]:
        """
        Crée une alerte si des orages sévères sont prévus.
        
        Args:
            forecasts: List of forecast dictionaries
            
        Returns:
            Alert dictionary if severe storms expected, else None
        """
        severe = [f for f in forecasts if f["is_severe"]]
        
        if not severe:
            return None
        
        earliest = severe[0]
        
        alert = {
            "alert_type": "SEVERE_STORM_WARNING",
            "severity": "HIGH",
            "location": f"({self.latitude}, {self.longitude})",
            "start_date": earliest["date"],
            "message": f"⚠️ ALERTE: Orages prévus le {earliest['date']}",
            "recommended_action": "Restreindre les vols à proximité",
            "affected_days": len(severe),
            "timestamp": datetime.now().isoformat()
        }
        
        return alert


def demo_storm_forecasts():
    """Demonstration de la détection d'orages."""
    print("\n" + "=" * 70)
    print("STORM FORECAST DEMONSTRATION")
    print("=" * 70)
    
    # Test multiple locations
    locations = [
        {"name": "Lyon", "lat": 45.764, "lon": 4.8357},
        {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
        {"name": "Marseille", "lat": 43.2965, "lon": 5.3698}
    ]
    
    for loc in locations:
        print(f"\n[{loc['name']}] ({loc['lat']}, {loc['lon']})")
        print("-" * 70)
        
        api = StormForecastAPI(latitude=loc["lat"], longitude=loc["lon"])
        result = api.extract()
        
        if result["status"] == "success":
            forecasts = result["next_7_days"]
            
            # Show forecast summary
            print(f"{'Date':<12} {'Code':<6} {'Risk':<10} {'TempMax':<8} {'Rain(mm)':<8}")
            print("-" * 70)
            
            for f in forecasts[:7]:
                date = f["date"][:10]
                code = f["weather_code"]
                risk = f["storm_risk"]
                temp = f"{f['temperature_max']:.1f}"
                rain = f"{f['precipitation']:.1f}"
                
                print(f"{date:<12} {code:<6} {risk:<10} {temp:<8} {rain:<8}")
            
            # Alert if severe
            if result["severe_storms"]:
                alert = api.create_alert(forecasts)
                if alert:
                    print(f"\n[ALERT] {alert['message']}")
                    print(f"   Action: {alert['recommended_action']}")
            else:
                print(f"\nOK: No severe storms forecast for next 7 days")



if __name__ == "__main__":
    demo_storm_forecasts()
