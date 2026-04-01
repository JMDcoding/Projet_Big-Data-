"""
Web scraper using BeautifulSoup and Selenium.
"""
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from src.ingestion.base import DataSource


class WebScraper(DataSource, ABC):
    """Abstract base class for web scrapers."""
    
    def __init__(self, name: str, url: str, timeout: int = 30):
        """Initialize web scraper.
        
        Args:
            name: Name of the scraper
            url: URL to scrape
            timeout: Request timeout in seconds
        """
        super().__init__(name)
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def fetch(self) -> str:
        """Fetch HTML content from URL.
        
        Returns:
            HTML content as string
            
        Raises:
            requests.RequestException: If request fails
        """
        try:
            response = self.session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            self.logger.info(f"Successfully fetched content from {self.url}")
            return response.text
        
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {self.url}: {str(e)}")
            raise
    
    def validate(self, data: str) -> bool:
        """Validate HTML content.
        
        Args:
            data: HTML content
            
        Returns:
            True if content is valid HTML, False otherwise
        """
        try:
            if not isinstance(data, str) or not data.strip():
                return False
            
            soup = BeautifulSoup(data, "html.parser")
            return soup.find() is not None
        
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    @abstractmethod
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML content and extract structured data.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of extracted data dictionaries
        """
        pass
    
    def extract(self) -> List[Dict[str, Any]]:
        """Extract and parse data from web page.
        
        Returns:
            List of extracted data
            
        Raises:
            ValueError: If data validation fails
        """
        try:
            html = self.fetch()
            if not self.validate(html):
                raise ValueError(f"HTML validation failed for {self.url}")
            
            data = self.parse(html)
            self.logger.info(f"Successfully extracted {len(data)} records from {self.name}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error extracting data: {str(e)}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("Session closed")


class AirlineFlightScraper(WebScraper):
    """Scraper for flight information from airline websites."""
    
    def __init__(self, url: str):
        """Initialize airline flight scraper.
        
        Args:
            url: URL to scrape flight data from
        """
        super().__init__("AirlineFlightScraper", url)
    
    def parse(self, html: str) -> List[Dict[str, Any]]:
        """Parse flight information from HTML.
        
        Args:
            html: HTML content containing flight data
            
        Returns:
            List of flight dictionaries
        """
        flights = []
        soup = BeautifulSoup(html, "html.parser")
        
        # This is a template - customize based on actual website structure
        flight_rows = soup.find_all("tr", class_="flight-row")
        
        for row in flight_rows:
            try:
                flight_data = {
                    "flight_number": row.find("td", class_="flight-number").text.strip(),
                    "departure": row.find("td", class_="departure").text.strip(),
                    "arrival": row.find("td", class_="arrival").text.strip(),
                    "departure_time": row.find("td", class_="departure-time").text.strip(),
                    "arrival_time": row.find("td", class_="arrival-time").text.strip(),
                }
                flights.append(flight_data)
            except AttributeError as e:
                self.logger.warning(f"Error parsing flight row: {str(e)}")
                continue
        
        return flights
