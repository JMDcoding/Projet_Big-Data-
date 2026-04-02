"""
Flight Trajectory Predictor - Predicts flight paths and identifies danger zones.
Calculates future positions and assesses collision risks with weather/hazards.
"""
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple


class TrajectoryPredictor:
    """Predicts flight trajectories and identifies potential dangers."""
    
    def __init__(self):
        """Initialize trajectory predictor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        # Earth radius in kilometers
        self.EARTH_RADIUS_KM = 6371
    
    def predict_trajectories(self, 
                            flights_data: pd.DataFrame,
                            lightning_data: pd.DataFrame,
                            prediction_minutes: int = 60) -> pd.DataFrame:
        """Predict flight trajectories and identify danger zones.
        
        Args:
            flights_data: DataFrame with flight information
            lightning_data: DataFrame with lightning strike locations
            prediction_minutes: How many minutes ahead to predict (default: 60)
            
        Returns:
            DataFrame with predicted trajectories and danger assessments
        """
        if flights_data.empty or lightning_data.empty:
            return pd.DataFrame()
        
        predictions = []
        
        for _, flight in flights_data.iterrows():
            try:
                # Calculate predicted positions
                future_positions = self._calculate_future_positions(
                    flight, 
                    prediction_minutes
                )
                
                if not future_positions:
                    continue
                
                # Assess danger zones along trajectory
                for time_step, position in enumerate(future_positions):
                    danger_assessment = self._assess_danger_zone(
                        position,
                        lightning_data,
                        flight
                    )
                    
                    prediction = {
                        'flight_id': flight.get('flight_number', 'UNKNOWN'),
                        'flight_number': flight.get('flight_number', 'UNKNOWN'),
                        'current_position': {
                            'latitude': flight.get('latitude'),
                            'longitude': flight.get('longitude'),
                            'altitude': flight.get('altitude')
                        },
                        'predicted_position': {
                            'latitude': position['latitude'],
                            'longitude': position['longitude'],
                            'altitude': position['altitude']
                        },
                        'time_minutes_ahead': (time_step + 1) * 5,  # 5-minute steps
                        'distance_traveled_km': position['distance_km'],
                        'heading': flight.get('heading', 0),
                        'velocity_kmh': flight.get('velocity', 0),
                        'danger_level': danger_assessment['risk_level'],
                        'danger_probability': danger_assessment['risk_probability'],
                        'nearest_lightning_distance_km': danger_assessment['nearest_lightning_km'],
                        'lightning_strikes_in_zone': danger_assessment['strikes_in_zone'],
                        'collision_risk': danger_assessment['collision_risk'],
                        'predicted_at': datetime.now().isoformat()
                    }
                    predictions.append(prediction)
                    
            except Exception as e:
                self.logger.warning(f"Error predicting trajectory for flight: {str(e)}")
                continue
        
        self.logger.info(f"Predicted trajectories for {len(set(p['flight_number'] for p in predictions))} flights")
        return pd.DataFrame(predictions)
    
    def _calculate_future_positions(self, 
                                    flight: pd.Series, 
                                    prediction_minutes: int,
                                    step_minutes: int = 5) -> List[Dict]:
        """Calculate future positions along flight trajectory.
        
        Args:
            flight: Flight data series
            prediction_minutes: Minutes to predict ahead
            step_minutes: Step size in minutes (default: 5)
            
        Returns:
            List of predicted positions
        """
        try:
            current_lat = flight.get('latitude')
            current_lon = flight.get('longitude')
            current_alt = flight.get('altitude', 10000)
            heading = flight.get('heading', 0)
            velocity_kmh = flight.get('velocity', 500)
            vertical_rate = flight.get('vertical_rate', 0)  # meters per minute
            
            if None in [current_lat, current_lon, heading]:
                return []
            
            positions = []
            num_steps = prediction_minutes // step_minutes
            distance_per_step = (velocity_kmh / 60) * step_minutes  # km per step
            
            for step in range(1, num_steps + 1):
                # Calculate new lat/lon based on heading and distance
                lat, lon = self._calculate_new_position(
                    current_lat,
                    current_lon,
                    heading,
                    distance_per_step
                )
                
                # Calculate altitude change (vertical_rate in meters/min, convert to km)
                altitude_change = (vertical_rate * step_minutes) / 1000
                new_altitude = max(0, current_alt + altitude_change)
                
                positions.append({
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': new_altitude,
                    'distance_km': distance_per_step * step,
                    'time_step': step
                })
            
            return positions
        
        except Exception as e:
            self.logger.warning(f"Error calculating future positions: {str(e)}")
            return []
    
    def _calculate_new_position(self, lat: float, lon: float, 
                               heading: float, distance_km: float) -> Tuple[float, float]:
        """Calculate new lat/lon after traveling distance in heading direction.
        
        Uses Haversine formula for great circle navigation.
        
        Args:
            lat: Current latitude
            lon: Current longitude
            heading: Direction in degrees (0=North, 90=East, 180=South, 270=West)
            distance_km: Distance to travel
            
        Returns:
            Tuple of (new_latitude, new_longitude)
        """
        # Convert to radians
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        heading_rad = np.radians(heading)
        angular_distance = distance_km / self.EARTH_RADIUS_KM
        
        # Calculate new position using spherical trigonometry
        new_lat_rad = np.arcsin(
            np.sin(lat_rad) * np.cos(angular_distance) +
            np.cos(lat_rad) * np.sin(angular_distance) * np.cos(heading_rad)
        )
        
        new_lon_rad = lon_rad + np.arctan2(
            np.sin(heading_rad) * np.sin(angular_distance) * np.cos(lat_rad),
            np.cos(angular_distance) - np.sin(lat_rad) * np.sin(new_lat_rad)
        )
        
        return np.degrees(new_lat_rad), np.degrees(new_lon_rad)
    
    def _assess_danger_zone(self, predicted_pos: Dict, 
                           lightning_data: pd.DataFrame,
                           flight: pd.Series) -> Dict:
        """Assess danger in predicted position zone.
        
        Args:
            predicted_pos: Predicted position dictionary
            lightning_data: DataFrame with lightning strikes
            flight: Original flight data
            
        Returns:
            Dictionary with danger assessment
        """
        try:
            if lightning_data.empty:
                return {
                    'risk_level': 'MINIMAL',
                    'risk_probability': 0.0,
                    'nearest_lightning_km': float('inf'),
                    'strikes_in_zone': 0,
                    'collision_risk': 'NONE'
                }
            
            # Calculate distance to each lightning strike
            distances = []
            for _, strike in lightning_data.iterrows():
                dist = self._haversine_distance(
                    predicted_pos['latitude'],
                    predicted_pos['longitude'],
                    strike.get('latitude'),
                    strike.get('longitude')
                )
                distances.append(dist)
            
            distances = np.array(distances)
            nearest_distance = np.min(distances) if len(distances) > 0 else float('inf')
            
            # Count strikes within danger radius (50 km for aircraft)
            danger_radius = 50  # km
            strikes_in_zone = np.sum(distances <= danger_radius)
            
            # Assess collision risk
            altitude_m = predicted_pos.get('altitude', 10000) * 1000  # Convert to meters
            flight_departure_alt = flight.get('departure_time')
            flight_arrival_alt = flight.get('arrival_time')
            
            collision_risk = 'NONE'
            risk_probability = 0.0
            risk_level = 'MINIMAL'
            
            if nearest_distance <= 10:  # Very close (10 km)
                collision_risk = 'CRITICAL'
                risk_probability = min(0.95, 0.5 + (strikes_in_zone * 0.2))
                risk_level = 'CRITICAL'
            elif nearest_distance <= 25:  # Close (25 km)
                collision_risk = 'HIGH'
                risk_probability = min(0.90, 0.3 + (strikes_in_zone * 0.15))
                risk_level = 'HIGH'
            elif nearest_distance <= 50:  # Moderate distance (50 km)
                collision_risk = 'MEDIUM'
                risk_probability = min(0.70, 0.1 + (strikes_in_zone * 0.1))
                risk_level = 'MEDIUM'
            elif nearest_distance <= 100:  # Far distance (100 km)
                collision_risk = 'LOW'
                risk_probability = 0.05 + (strikes_in_zone * 0.02)
                risk_level = 'LOW'
            else:
                collision_risk = 'NONE'
                risk_probability = 0.0
                risk_level = 'MINIMAL'
            
            return {
                'risk_level': risk_level,
                'risk_probability': risk_probability,
                'nearest_lightning_km': nearest_distance,
                'strikes_in_zone': int(strikes_in_zone),
                'collision_risk': collision_risk
            }
        
        except Exception as e:
            self.logger.warning(f"Error assessing danger zone: {str(e)}")
            return {
                'risk_level': 'UNKNOWN',
                'risk_probability': 0.5,
                'nearest_lightning_km': -1,
                'strikes_in_zone': 0,
                'collision_risk': 'UNKNOWN'
            }
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points.
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
        lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2)
        
        c = 2 * np.arcsin(np.sqrt(a))
        return self.EARTH_RADIUS_KM * c
    
    def identify_critical_paths(self, 
                               predictions_df: pd.DataFrame,
                               risk_threshold: str = 'HIGH') -> pd.DataFrame:
        """Identify flight paths with critical danger levels.
        
        Args:
            predictions_df: DataFrame with trajectory predictions
            risk_threshold: Minimum risk level to flag ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
            
        Returns:
            DataFrame with critical flight paths
        """
        if predictions_df.empty:
            return pd.DataFrame()
        
        risk_levels = ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        threshold_idx = risk_levels.index(risk_threshold)
        critical_mask = predictions_df['danger_level'].apply(
            lambda x: risk_levels.index(x) >= threshold_idx if x in risk_levels else False
        )
        
        critical_paths = predictions_df[critical_mask].copy()
        self.logger.info(f"Identified {len(critical_paths)} critical trajectory segments")
        
        return critical_paths.sort_values('danger_probability', ascending=False)
