"""
Helper utilities for the pipeline.
"""
from typing import Tuple, Dict
import math


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1, lon1: First coordinate (latitude, longitude)
        lat2, lon2: Second coordinate (latitude, longitude)
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_time_difference(time1, time2) -> int:
    """Calculate time difference in minutes.
    
    Args:
        time1, time2: Timestamp values
        
    Returns:
        Time difference in minutes
    """
    import pandas as pd
    
    if isinstance(time1, str):
        time1 = pd.to_datetime(time1)
    if isinstance(time2, str):
        time2 = pd.to_datetime(time2)
    
    return int(abs((time2 - time1).total_seconds() / 60))


def assess_disruption_risk(distance_km: float, time_diff_minutes: int, 
                          intensity: float = 50) -> Dict[str, any]:
    """Assess flight disruption risk based on lightning proximity.
    
    Args:
        distance_km: Distance from flight path to lightning strike
        time_diff_minutes: Time difference between flight and strike
        intensity: Lightning strike intensity (0-100)
        
    Returns:
        Dictionary with risk level and probability
    """
    # Risk factors
    distance_threshold = 100  # km
    time_threshold = 60  # minutes
    intensity_threshold = 50  # intensity units
    
    # Calculate base risk
    distance_risk = max(0, 1 - (distance_km / distance_threshold))
    time_risk = max(0, 1 - (time_diff_minutes / time_threshold))
    intensity_risk = intensity / 100
    
    # Combined probability
    probability = (distance_risk * 0.4 + time_risk * 0.4 + intensity_risk * 0.2)
    
    # Determine risk level
    if probability < 0.2:
        risk_level = "Low"
    elif probability < 0.5:
        risk_level = "Medium"
    elif probability < 0.8:
        risk_level = "High"
    else:
        risk_level = "Critical"
    
    return {
        "risk_level": risk_level,
        "disruption_probability": round(probability, 2),
        "distance_km": round(distance_km, 2),
        "time_diff_minutes": time_diff_minutes
    }


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographical coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        True if coordinates are valid
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180
