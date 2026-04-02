"""
Storm Risk Visualization - Affiche les zones à risque d'orage sur une carte.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional


class StormRiskZoneManager:
    """Gère les zones de risque d'orage pour la visualisation."""
    
    # Couleurs de risque (hex)
    RISK_COLORS = {
        "NONE": "#00AA00",      # Vert
        "LOW": "#90EE90",       # Vert clair
        "MEDIUM": "#FFFF00",    # Jaune
        "HIGH": "#FFA500",      # Orange
        "SEVERE": "#FF0000"     # Rouge
    }
    
    def __init__(self, center_lat: float = 45.764, center_lon: float = 4.8357):
        """Initialise le gestionnaire de zones.
        
        Args:
            center_lat: Latitude du centre
            center_lon: Longitude du centre
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
    
    def create_risk_grid(self, forecasts: List[Dict], grid_size: int = 7) -> pd.DataFrame:
        """Crée une grille de zones à risque.
        
        Args:
            forecasts: List of 7-day forecast dictionaries
            grid_size: Taille de la grille (n x n)
            
        Returns:
            DataFrame avec les zones et niveaux de risque
        """
        zones = []
        
        # Trouver le risque maximal dans la période de 7 jours
        max_risk_level = self._get_max_risk(forecasts)
        
        # Créer une grille de zones autour du centre
        offset = 0.5 * (grid_size - 1) / 2
        
        for i in range(grid_size):
            for j in range(grid_size):
                lat = self.center_lat + (i - offset) * 0.08
                lon = self.center_lon + (j - offset) * 0.08
                
                zones.append({
                    "zone_id": f"zone_{i:02d}_{j:02d}",
                    "latitude": round(lat, 4),
                    "longitude": round(lon, 4),
                    "risk_level": max_risk_level,
                    "color": self.RISK_COLORS.get(max_risk_level, "#808080"),
                    "population_risk": "HIGH" if max_risk_level in ["HIGH", "SEVERE"] else "LOW",
                    "flight_restriction": max_risk_level in ["HIGH", "SEVERE"]
                })
        
        return pd.DataFrame(zones)
    
    def _get_max_risk(self, forecasts: List[Dict]) -> str:
        """Récupère le niveau de risque maximal.
        
        Args:
            forecasts: List of forecast dictionaries
            
        Returns:
            Max risk level
        """
        if not forecasts:
            return "NONE"
        
        risk_priority = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "SEVERE": 4}
        max_risk = max(
            risk_priority.get(f.get("storm_risk", "NONE"), 0) 
            for f in forecasts
        )
        
        risk_map = {0: "NONE", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "SEVERE"}
        return risk_map.get(max_risk, "NONE")
    
    def create_dashboard_summary(self, forecasts: List[Dict], 
                                 active_flights: int = 0) -> Dict:
        """Crée un résumé pour le dashboard.
        
        Args:
            forecasts: List of forecast dictionaries
            active_flights: Number of active flights in area
            
        Returns:
            Dictionary with dashboard data
        """
        severe_days = sum(1 for f in forecasts if f.get("is_severe", False))
        next_storm = next((f["date"] for f in forecasts if f.get("is_severe")), None)
        
        summary = {
            "forecast_period": "7 days",
            "severe_storm_days": severe_days,
            "next_storm_date": next_storm,
            "all_clear": severe_days == 0,
            "active_flights": active_flights,
            "flight_restrictions": severe_days > 0,
            "alert_level": "CRITICAL" if severe_days > 0 else "NORMAL",
            "recommendations": self._get_recommendations(severe_days, active_flights),
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def _get_recommendations(self, severe_days: int, active_flights: int) -> List[str]:
        """Retourne les recommandations selon la situation.
        
        Args:
            severe_days: Number of days with severe storms
            active_flights: Number of active flights
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if severe_days == 0:
            recommendations.append("Conditions meteorologiques normales")
        elif severe_days == 1:
            recommendations.append("Orage prevu - Vigilance accrue")
            recommendations.append("Restreindre les vols non essentiels")
        else:
            recommendations.append(f"Alertes: {severe_days} jour(s) avec orages severes!")
            recommendations.append("Evacuer les vols dans la zone affectee")
            recommendations.append("Rerouter les vols par voies alternatives")
        
        if active_flights > 0 and severe_days > 0:
            recommendations.append(
                f"URGENT: {active_flights} vol(s) actif(s) dans zones a risque"
            )
        
        return recommendations
    
    def export_to_geojson(self, zones_df: pd.DataFrame) -> Dict:
        """Exporte les zones en format GeoJSON pour cartographie.
        
        Args:
            zones_df: DataFrame de zones
            
        Returns:
            GeoJSON FeatureCollection
        """
        features = []
        
        for _, zone in zones_df.iterrows():
            feature = {
                "type": "Feature",
                "properties": {
                    "zone_id": zone["zone_id"],
                    "risk_level": zone["risk_level"],
                    "color": zone["color"],
                    "flight_restriction": zone["flight_restriction"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [zone["longitude"], zone["latitude"]]
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        }


def demo_risk_zones():
    """Démo des zones à risque."""
    print("\n" + "=" * 70)
    print("STORM RISK ZONES DEMO")
    print("=" * 70)
    
    # Exemple de prévisions
    example_forecasts = [
        {
            "date": "2026-04-02",
            "weather_code": 80,
            "storm_risk": "HIGH",
            "is_severe": True
        },
        {
            "date": "2026-04-03",
            "weather_code": 3,
            "storm_risk": "NONE",
            "is_severe": False
        },
        {
            "date": "2026-04-04",
            "weather_code": 1,
            "storm_risk": "NONE",
            "is_severe": False
        },
    ]
    
    manager = StormRiskZoneManager(center_lat=45.764, center_lon=4.8357)
    
    # Créer zones
    zones = manager.create_risk_grid(example_forecasts, grid_size=5)
    print("\nGenerated Risk Zones:")
    print(zones[["zone_id", "latitude", "longitude", "risk_level", "color", "flight_restriction"]].to_string())
    
    # Créer résumé
    summary = manager.create_dashboard_summary(example_forecasts, active_flights=3)
    print("\nDashboard Summary:")
    print(f"  Alert Level: {summary['alert_level']}")
    print(f"  Severe Storm Days: {summary['severe_storm_days']}")
    print(f"  Next Storm: {summary['next_storm_date']}")
    print(f"  Active Flights at Risk: {summary['active_flights']}")
    print("\nRecommendations:")
    for rec in summary['recommendations']:
        print(f"  - {rec}")
    
    # Export GeoJSON
    geojson = manager.export_to_geojson(zones)
    print(f"\nGeoJSON Features: {len(geojson['features'])} zones")
    print(f"Sample feature: {geojson['features'][0]['properties']}")


if __name__ == "__main__":
    demo_risk_zones()
