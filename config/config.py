"""
Configuration management for the Big Data Pipeline.
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
    
    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "lightning_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # API
    API_BASE_URL = os.getenv("API_BASE_URL", "https://www.blitzortung.org/en/live_lightning_maps.php")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", 30))
    
    # Data paths
    DATA_RAW_PATH = os.getenv("DATA_RAW_PATH", str(PROJECT_ROOT / "data" / "raw"))
    DATA_PROCESSED_PATH = os.getenv("DATA_PROCESSED_PATH", str(PROJECT_ROOT / "data" / "processed"))
    
    # Logging
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
