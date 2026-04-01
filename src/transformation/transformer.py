"""
Data transformation and processing.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pandas as pd


class Transformer(ABC):
    """Abstract base class for data transformers."""
    
    def __init__(self, name: str):
        """Initialize transformer.
        
        Args:
            name: Name of the transformer
        """
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def transform(self, data: Any) -> Any:
        """Transform data.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        pass


class LightningDataTransformer(Transformer):
    """Transformer for lightning strikes data."""
    
    def __init__(self):
        """Initialize lightning data transformer."""
        super().__init__("LightningDataTransformer")
    
    def transform(self, data: List[Dict]) -> pd.DataFrame:
        """Transform lightning data into structured DataFrame.
        
        Args:
            data: Raw lightning data
            
        Returns:
            Transformed DataFrame with structured columns
        """
        try:
            df = pd.DataFrame(data)
            
            # Clean and standardize columns
            df = self._standardize_columns(df)
            
            # Convert data types
            df = self._convert_types(df)
            
            # Handle missing values
            df = self._handle_missing_values(df)
            
            # Add computed columns
            df = self._add_computed_columns(df)
            
            self.logger.info(f"Successfully transformed {len(df)} lightning records")
            return df
        
        except Exception as e:
            self.logger.error(f"Error transforming data: {str(e)}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and structure.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized columns
        """
        # Convert to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with converted types
        """
        # Convert coordinates to float
        coord_columns = ["latitude", "lat", "longitude", "lon", "x", "y"]
        for col in coord_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Convert timestamps
        time_columns = ["timestamp", "time", "date", "datetime"]
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        # Drop rows where coordinates are missing
        coord_columns = ["latitude", "longitude"]
        df = df.dropna(subset=coord_columns, how="any")
        
        # Fill other missing values
        df = df.fillna({col: 0 for col in df.columns if col not in coord_columns})
        
        return df
    
    def _add_computed_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated columns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with computed columns
        """
        # Add unique ID if not present
        if "id" not in df.columns and "lightning_id" not in df.columns:
            df["lightning_id"] = range(1, len(df) + 1)
        
        # Add processing timestamp
        df["processed_at"] = pd.Timestamp.now()
        
        return df


class FlightDataTransformer(Transformer):
    """Transformer for flight data."""
    
    def __init__(self):
        """Initialize flight data transformer."""
        super().__init__("FlightDataTransformer")
    
    def transform(self, data: List[Dict]) -> pd.DataFrame:
        """Transform flight data into structured DataFrame.
        
        Args:
            data: Raw flight data
            
        Returns:
            Transformed DataFrame with structured columns
        """
        try:
            df = pd.DataFrame(data)
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            # Convert types
            df = self._convert_types(df)
            
            # Extract route information
            df = self._extract_routes(df)
            
            self.logger.info(f"Successfully transformed {len(df)} flight records")
            return df
        
        except Exception as e:
            self.logger.error(f"Error transforming flight data: {str(e)}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names."""
        df.columns = df.columns.str.lower().str.replace(" ", "_")
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate types."""
        time_columns = ["departure_time", "arrival_time"]
        for col in time_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        return df
    
    def _extract_routes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract and standardize route information."""
        if "departure" in df.columns and "arrival" in df.columns:
            df["route"] = df["departure"] + "-" + df["arrival"]
        
        return df


class DataMerger(Transformer):
    """Merge multiple data sources."""
    
    def __init__(self):
        """Initialize data merger."""
        super().__init__("DataMerger")
    
    def transform(self, data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge multiple DataFrames.
        
        Args:
            data_dict: Dictionary of DataFrames to merge
            
        Returns:
            Merged DataFrame
        """
        try:
            result = None
            
            for name, df in data_dict.items():
                if result is None:
                    result = df.copy()
                else:
                    # Add source identifier
                    df["source"] = name
                    result = pd.concat([result, df], ignore_index=True)
            
            self.logger.info(f"Merged {len(data_dict)} data sources")
            return result
        
        except Exception as e:
            self.logger.error(f"Error merging data: {str(e)}")
            raise
