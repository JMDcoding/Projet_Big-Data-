"""
API client for Blitzortung lightning data.
"""
import requests
import logging
from typing import Dict, List, Any
from datetime import datetime
from src.ingestion.base import DataSource


class BlitzortungAPI(DataSource):
    """Client for Blitzortung API to fetch lightning strikes data."""
    
    def __init__(self, base_url: str = "https://www.blitzortung.org/en/live_lightning_maps.php", 
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
        """Fetch lightning strikes data from Blitzortung API.
        
        Returns:
            Dictionary containing lightning strikes data
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            params = {
                "map": "1",
                "period": "1440",  # Last 24 hours
            }
            
            response = self.session.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            self.logger.info("Successfully fetched data from Blitzortung API")
            return {
                "raw_response": response.text,
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat(),
                "url": response.url
            }
        
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate API response.
        
        Args:
            data: Data returned from API
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            if not isinstance(data, dict):
                self.logger.warning("Response is not a dictionary")
                return False
            
            if "status_code" not in data or data["status_code"] != 200:
                self.logger.warning(f"Unexpected status code: {data.get('status_code')}")
                return False
            
            if "raw_response" not in data or not data["raw_response"]:
                self.logger.warning("Empty response from API")
                return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("Session closed")
