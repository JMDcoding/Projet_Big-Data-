"""
Base ingestion classes for data collection.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    def __init__(self, name: str):
        """Initialize data source.
        
        Args:
            name: Name of the data source
        """
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch(self) -> Any:
        """Fetch data from source.
        
        Returns:
            Data fetched from the source
        """
        pass
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate fetched data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    def extract(self) -> Any:
        """Extract and validate data.
        
        Returns:
            Validated data
            
        Raises:
            ValueError: If data validation fails
        """
        try:
            data = self.fetch()
            if not self.validate(data):
                raise ValueError(f"Data validation failed for {self.name}")
            self.logger.info(f"Successfully extracted data from {self.name}")
            return data
        except Exception as e:
            self.logger.error(f"Error extracting data from {self.name}: {str(e)}")
            raise
