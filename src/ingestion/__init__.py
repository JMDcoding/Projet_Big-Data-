"""
Initialization for ingestion module.
"""
from src.ingestion.base import DataSource
from src.ingestion.api_client import BlitzortungAPI
from src.ingestion.web_scraper import WebScraper, AirlineFlightScraper

__all__ = [
    "DataSource",
    "BlitzortungAPI",
    "WebScraper",
    "AirlineFlightScraper",
]
