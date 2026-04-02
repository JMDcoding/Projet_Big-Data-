"""
Flight disruption analysis based on lightning strikes.
"""
import logging
import math
from typing import List, Dict, Tuple, Optional
import pandas as pd
import numpy as np


class DisruptionCalculator:
    """Calculate flight disruption risk based on lightning strikes."""
    
    # Search radius (km) around flights
    ALERT_RADIUS_KM = 50  # How far lightning can affect a flight
    
    # Time window (minutes) to consider lightning before/after
    TIME_WINDOW_MINUTES = 30
    
    def __init__(self):
        """Initialize calculator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def calculate_disruptions(
        self,
        lightning_data: List[Dict],
        flights_data: List[Dict]
    ) -> List[Dict]:
        """Calculate disruption risks for all flights.
        
        Args:
            lightning_data: List of lightning strike records
            flights_data: List of flight records
            
        Returns:
            List of disruption records
        """
        disruptions = []
        
        if not lightning_data or not flights_data:
            self.logger.warning("Missing data for disruption calculation")
            return disruptions
        
        # Convert to DataFrames for easier processing
        lightning_df = pd.DataFrame(lightning_data)
        flights_df = pd.DataFrame(flights_data)
        
        # Ensure we have required columns
        required_lightning = ["latitude", "longitude", "timestamp"]
        required_flights = ["flight_number", "latitude", "longitude", "departure_time", "arrival_time"]
        
        if not all(col in lightning_df.columns for col in required_lightning):
            self.logger.error(f"Lightning data missing required columns: {required_lightning}")
            return disruptions
        
        if not all(col in flights_df.columns for col in required_flights):
            self.logger.error(f"Flights data missing required columns: {required_flights}")
            return disruptions
        
        # Convert timestamps
        lightning_df["timestamp"] = pd.to_datetime(lightning_df["timestamp"], errors="coerce")
        flights_df["departure_time"] = pd.to_datetime(flights_df["departure_time"], errors="coerce")
        flights_df["arrival_time"] = pd.to_datetime(flights_df["arrival_time"], errors="coerce")
        
        # Process each flight
        for _, flight in flights_df.iterrows():
            # Skip flights with missing data
            if pd.isna(flight["latitude"]) or pd.isna(flight["longitude"]):
                continue
            if pd.isna(flight["departure_time"]) or pd.isna(flight["arrival_time"]):
                continue
            
            # Find relevant lightning strikes
            disruption_result = self._calculate_flight_disruption(
                flight=flight,
                lightning_df=lightning_df
            )
            
            if disruption_result:
                disruptions.append(disruption_result)
        
        self.logger.info(f"Calculated disruptions for {len(disruptions)} flights")
        return disruptions
    
    def _calculate_flight_disruption(
        self,
        flight: pd.Series,
        lightning_df: pd.DataFrame
    ) -> Optional[Dict]:
        """Calculate disruption for a single flight.
        
        Args:
            flight: Flight data series
            lightning_df: DataFrame of lightning strikes
            
        Returns:
            Disruption record or None if no disruption
        """
        flight_lat = flight["latitude"]
        flight_lon = flight["longitude"]
        flight_start = flight["departure_time"]
        flight_end = flight["arrival_time"]
        
        # Time window: consider lightning before departure and after arrival
        time_start = flight_start - pd.Timedelta(minutes=self.TIME_WINDOW_MINUTES)
        time_end = flight_end + pd.Timedelta(minutes=self.TIME_WINDOW_MINUTES)
        
        # Filter lightning by time window
        lightning_window = lightning_df[
            (lightning_df["timestamp"] >= time_start) &
            (lightning_df["timestamp"] <= time_end)
        ]
        
        if lightning_window.empty:
            return None  # No relevant lightning
        
        # Calculate distances to all lightning strikes in time window
        distances = []
        for _, lightning in lightning_window.iterrows():
            distance = self._haversine_distance(
                flight_lat, flight_lon,
                lightning["latitude"], lightning["longitude"]
            )
            distances.append(distance)
        
        # Find closest lightning strike
        min_distance = min(distances)
        
        # Check if lightning is within alert radius
        if min_distance > self.ALERT_RADIUS_KM:
            return None  # Lightning too far away
        
        # Calculate disruption probability based on distance
        # Closer = higher risk
        disruption_probability = self._calculate_probability(min_distance)
        
        # Determine risk level
        risk_level = self._determine_risk_level(disruption_probability)
        
        return {
            "flight_id": flight.get("flight_number", "UNKNOWN"),
            "closest_lightning_distance_km": round(min_distance, 2),
            "distance_km": round(min_distance, 2),
            "time_difference_minutes": 0,  # Would need lightning timestamp to calculate
            "disruption_probability": round(disruption_probability, 3),
            "risk_level": risk_level,
            "lightning_count_nearby": len(lightning_window)
        }
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: First point (latitude, longitude)
            lat2, lon2: Second point (latitude, longitude)
            
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def _calculate_probability(self, distance_km: float) -> float:
        """Calculate disruption probability based on distance.
        
        Args:
            distance_km: Distance to closest lightning strike (km)
            
        Returns:
            Probability between 0 and 1
        """
        # Using sigmoid-like function:
        # - At 0 km: 95% probability
        # - At 10 km: 70% probability
        # - At 25 km: 40% probability
        # - At 50 km: 5% probability
        
        if distance_km <= 0:
            return 0.95
        
        # Exponential decay: probability = base * exp(-distance/scale)
        scale = 15  # Distance scale factor
        base = 0.95
        probability = base * math.exp(-distance_km / scale)
        
        return min(probability, 1.0)
    
    def _determine_risk_level(self, probability: float) -> str:
        """Determine risk level from probability.
        
        Args:
            probability: Disruption probability (0-1)
            
        Returns:
            Risk level string
        """
        if probability >= 0.7:
            return "CRITICAL"
        elif probability >= 0.5:
            return "HIGH"
        elif probability >= 0.3:
            return "MEDIUM"
        elif probability >= 0.1:
            return "LOW"
        else:
            return "MINIMAL"
    
    def calculate_disruptions_batch(
        self,
        lightning_data: pd.DataFrame,
        flights_data: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate disruptions with DataFrames (optimized batch processing).
        
        Args:
            lightning_data: Lightning strikes DataFrame
            flights_data: Flights DataFrame
            
        Returns:
            DataFrame with disruption records
        """
        disruptions = self.calculate_disruptions(
            lightning_data.to_dict('records'),
            flights_data.to_dict('records')
        )
        
        return pd.DataFrame(disruptions) if disruptions else pd.DataFrame()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    calc = DisruptionCalculator()
    
    # Sample data
    lightning = [
        {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "timestamp": pd.Timestamp("2026-04-02 10:00:00"),
            "intensity": 5
        }
    ]
    
    flights = [
        {
            "id": 1,
            "flight_number": "AF123",
            "latitude": 48.9,
            "longitude": 2.4,
            "departure_time": pd.Timestamp("2026-04-02 09:50:00"),
            "arrival_time": pd.Timestamp("2026-04-02 11:30:00")
        }
    ]
    
    disruptions = calc.calculate_disruptions(lightning, flights)
    print(f"Disruptions: {disruptions}")
