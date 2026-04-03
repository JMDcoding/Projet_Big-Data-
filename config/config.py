"""
Configuration management for the Big Data Pipeline.

DATA STORAGE STRATEGY:
======================
All data is stored in PRODUCTION systems:
1. MinIO (Object Storage) - Primary data lake for raw/processed files
2. PostgreSQL (Database) - Indexed records for fast queries
3. Local filesystem - TEMPORARY STAGING ONLY (auto-cleaned)

NO DATA IS COMMITTED TO GIT. All local files are git-ignored.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Project root
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # ==================== DATABASE ====================
    # PostgreSQL configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))  # Default: 5433
    DB_NAME = os.getenv("DB_NAME", "lightning_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # ==================== API ====================
    # API configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://www.blitzortung.org/en/live_lightning_maps.php")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", 30))
    
    # ==================== DATA STORAGE ====================
    # TEMPORARY LOCAL STORAGE (auto-cleaned after upload to MinIO)
    # These paths are for staging data only
    DATA_RAW_PATH = os.getenv("DATA_RAW_PATH", str(PROJECT_ROOT / "data" / "raw"))
    DATA_PROCESSED_PATH = os.getenv("DATA_PROCESSED_PATH", str(PROJECT_ROOT / "data" / "processed"))
    
    # MinIO Object Storage (PRIMARY DATA LAKE)
    MINIO_HOST = os.getenv("MINIO_HOST", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET", "lightning-data")
    MINIO_USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"
    
    # ==================== LOGGING ====================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", str(PROJECT_ROOT / "logs" / "app.log"))
    
    @classmethod
    def get_db_url(cls):
        """Generate PostgreSQL connection URL."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    DB_NAME = "test_lightning_db"
    DEBUG = True


def get_config(env: str = None) -> Config:
    """Get configuration based on environment."""
    env = env or os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)


# Export DATABASE_CONFIG for backward compatibility
DATABASE_CONFIG = {
    "host": Config.DB_HOST,
    "port": Config.DB_PORT,
    "database": Config.DB_NAME,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD
}
