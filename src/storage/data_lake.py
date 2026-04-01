"""
Storage management for raw data (Data Lake).
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class DataLake(ABC):
    """Abstract base class for data storage."""
    
    def __init__(self, storage_path: str):
        """Initialize data storage.
        
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def save(self, data: Any, filename: str) -> str:
        """Save data to storage.
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            Path to saved file
        """
        pass
    
    @abstractmethod
    def load(self, filename: str) -> Any:
        """Load data from storage.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            Loaded data
        """
        pass
    
    @abstractmethod
    def delete(self, filename: str) -> bool:
        """Delete a file from storage.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        pass
    
    def list_files(self) -> List[str]:
        """List all files in storage.
        
        Returns:
            List of filenames
        """
        try:
            files = [f.name for f in self.storage_path.iterdir() if f.is_file()]
            self.logger.info(f"Found {len(files)} files in storage")
            return files
        except Exception as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return []


class JSONDataLake(DataLake):
    """JSON-based data lake storage."""
    
    def save(self, data: Any, filename: str) -> str:
        """Save data to JSON file.
        
        Args:
            data: Data to save
            filename: Name of the JSON file
            
        Returns:
            Path to saved file
        """
        try:
            if not filename.endswith(".json"):
                filename = f"{filename}.json"
            
            filepath = self.storage_path / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Data saved to {filepath}")
            return str(filepath)
        
        except Exception as e:
            self.logger.error(f"Error saving JSON: {str(e)}")
            raise
    
    def load(self, filename: str) -> Dict:
        """Load data from JSON file.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            Loaded data as dictionary
        """
        try:
            if not filename.endswith(".json"):
                filename = f"{filename}.json"
            
            filepath = self.storage_path / filename
            
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.logger.info(f"Data loaded from {filepath}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error loading JSON: {str(e)}")
            raise
    
    def delete(self, filename: str) -> bool:
        """Delete JSON file.
        
        Args:
            filename: Name of the JSON file
            
        Returns:
            True if deletion successful
        """
        try:
            if not filename.endswith(".json"):
                filename = f"{filename}.json"
            
            filepath = self.storage_path / filename
            os.remove(filepath)
            self.logger.info(f"File deleted: {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            return False


class CSVDataLake(DataLake):
    """CSV-based data lake storage."""
    
    def save(self, data: List[Dict], filename: str) -> str:
        """Save data to CSV file.
        
        Args:
            data: List of dictionaries to save
            filename: Name of the CSV file
            
        Returns:
            Path to saved file
        """
        try:
            import pandas as pd
            
            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"
            
            filepath = self.storage_path / filename
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding="utf-8")
            
            self.logger.info(f"Data saved to {filepath}")
            return str(filepath)
        
        except Exception as e:
            self.logger.error(f"Error saving CSV: {str(e)}")
            raise
    
    def load(self, filename: str) -> List[Dict]:
        """Load data from CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Loaded data as list of dictionaries
        """
        try:
            import pandas as pd
            
            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"
            
            filepath = self.storage_path / filename
            df = pd.read_csv(filepath)
            
            self.logger.info(f"Data loaded from {filepath}")
            return df.to_dict("records")
        
        except Exception as e:
            self.logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def delete(self, filename: str) -> bool:
        """Delete CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            True if deletion successful
        """
        try:
            if not filename.endswith(".csv"):
                filename = f"{filename}.csv"
            
            filepath = self.storage_path / filename
            os.remove(filepath)
            self.logger.info(f"File deleted: {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting file: {str(e)}")
            return False
