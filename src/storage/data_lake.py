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
import pandas as pd
import numpy as np


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and pandas types."""
    
    def default(self, obj):
        """Convert datetime and pandas types to serializable format."""
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, (pd.Series, np.ndarray)):
            return obj.tolist()
        elif pd.isna(obj):
            return None
        else:
            return super().default(obj)


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
                json.dump(data, f, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
            
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
            
            with open(filepath, "r", encoding="latin-1") as f:
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
            df = pd.read_csv(filepath, encoding="latin-1")
            
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


class MinIODataLake(DataLake):
    """MinIO-based data lake storage (S3-compatible object storage)."""
    
    def __init__(self, storage_path: str = "data-lake", minio_host: str = "localhost:9000", 
                 access_key: str = "minioadmin", secret_key: str = "minioadmin", 
                 bucket_name: str = "lightning-data", use_ssl: bool = False):
        """Initialize MinIO data lake.
        
        Args:
            storage_path: Unused (required for compatibility with DataLake)
            minio_host: MinIO server host:port
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket_name: Bucket name for storage
            use_ssl: Whether to use SSL/TLS
        """
        super().__init__(storage_path)
        
        try:
            from minio import Minio
            from minio.error import S3Error
            
            self.minio_client = Minio(
                minio_host,
                access_key=access_key,
                secret_key=secret_key,
                secure=use_ssl
            )
            self.bucket_name = bucket_name
            self.S3Error = S3Error
            
            # Create bucket if it doesn't exist
            self._ensure_bucket_exists()
            self.logger.info(f"MinIO data lake initialized: {minio_host}/{bucket_name}")
        
        except ImportError:
            self.logger.error("minio package not installed. Install with: pip install minio")
            raise
        except Exception as e:
            self.logger.error(f"Error initializing MinIO: {str(e)}")
            raise
    
    def _ensure_bucket_exists(self) -> bool:
        """Ensure bucket exists, create if needed.
        
        Returns:
            True if bucket exists or was created
        """
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                self.logger.info(f"Created bucket: {self.bucket_name}")
            return True
        except self.S3Error as e:
            self.logger.warning(f"Could not ensure bucket: {str(e)}")
            return False
    
    def save(self, data: Any, filename: str) -> str:
        """Save data to MinIO.
        
        Args:
            data: Data to save
            filename: Object name in MinIO
            
        Returns:
            Object path (bucket/filename)
        """
        try:
            from io import BytesIO
            
            # Determine content type and convert data
            if filename.endswith(".json"):
                content = json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False)
                content_type = "application/json"
            elif filename.endswith(".csv"):
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    content = df.to_csv(index=False)
                else:
                    content = data
                content_type = "text/csv"
            else:
                content = json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False)
                filename = f"{filename}.json"
                content_type = "application/json"
            
            # Convert to bytes
            content_bytes = content.encode('utf-8')
            
            # Upload to MinIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=filename,
                data=BytesIO(content_bytes),
                length=len(content_bytes),
                content_type=content_type
            )
            
            object_path = f"{self.bucket_name}/{filename}"
            self.logger.info(f"Data saved to MinIO: {object_path}")
            return object_path
        
        except Exception as e:
            self.logger.error(f"Error saving to MinIO: {str(e)}")
            raise
    
    def load(self, filename: str) -> Any:
        """Load data from MinIO.
        
        Args:
            filename: Object name in MinIO
            
        Returns:
            Loaded data
        """
        try:
            # Get object from MinIO
            response = self.minio_client.get_object(self.bucket_name, filename)
            content = response.read().decode('utf-8')
            response.close()
            
            # Parse based on filename
            if filename.endswith(".json"):
                data = json.loads(content)
            elif filename.endswith(".csv"):
                from io import StringIO
                df = pd.read_csv(StringIO(content))
                data = df.to_dict('records')
            else:
                data = json.loads(content)
            
            self.logger.info(f"Data loaded from MinIO: {self.bucket_name}/{filename}")
            return data
        
        except Exception as e:
            self.logger.error(f"Error loading from MinIO: {str(e)}")
            raise
    
    def delete(self, filename: str) -> bool:
        """Delete object from MinIO.
        
        Args:
            filename: Object name in MinIO
            
        Returns:
            True if deletion successful
        """
        try:
            self.minio_client.remove_object(self.bucket_name, filename)
            self.logger.info(f"Object deleted from MinIO: {self.bucket_name}/{filename}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error deleting from MinIO: {str(e)}")
            return False
    
    def list_files(self) -> List[str]:
        """List all objects in bucket.
        
        Returns:
            List of object names
        """
        try:
            objects = self.minio_client.list_objects(self.bucket_name)
            filenames = [obj.object_name for obj in objects]
            self.logger.info(f"Found {len(filenames)} objects in MinIO bucket")
            return filenames
        
        except Exception as e:
            self.logger.error(f"Error listing MinIO objects: {str(e)}")
            return []
    
    def get_bucket_info(self) -> Dict:
        """Get bucket information.
        
        Returns:
            Dictionary with bucket stats
        """
        try:
            objects = list(self.minio_client.list_objects(self.bucket_name))
            total_size = sum(obj.size for obj in objects)
            
            return {
                "bucket_name": self.bucket_name,
                "object_count": len(objects),
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024)
            }
        except Exception as e:
            self.logger.error(f"Error getting bucket info: {str(e)}")
            return {}
