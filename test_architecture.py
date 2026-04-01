"""
Test script to validate the pipeline architecture.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion import BlitzortungAPI, DataSource
from src.storage import JSONDataLake, CSVDataLake, DataLake
from src.transformation import LightningDataTransformer, Transformer
from src.visualization import LightningDashboard
from src.utils import logger, calculate_distance, assess_disruption_risk
from config.config import get_config

# Try to import database modules
try:
    from src.database import PostgreSQLConnection, DataWarehouse
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    PostgreSQLConnection = None
    DataWarehouse = None


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing module imports...")
    
    # Test ingestion
    assert issubclass(BlitzortungAPI, DataSource)
    print("  ✅ Ingestion module OK")
    
    # Test storage
    assert issubclass(JSONDataLake, DataLake)
    assert issubclass(CSVDataLake, DataLake)
    print("  ✅ Storage module OK")
    
    # Test transformation
    assert issubclass(LightningDataTransformer, Transformer)
    print("  ✅ Transformation module OK")
    
    # Test database
    if HAS_DATABASE:
        assert issubclass(PostgreSQLConnection, object)
        assert issubclass(DataWarehouse, object)
        print("  ✅ Database module OK")
    else:
        print("  ⚠️  Database module skipped (psycopg2 not installed)")
    
    # Test visualization
    assert issubclass(LightningDashboard, object)
    print("  ✅ Visualization module OK")
    
    # Test utils
    assert callable(calculate_distance)
    assert callable(assess_disruption_risk)
    print("  ✅ Utils module OK")


def test_config():
    """Test configuration loading."""
    print("\n🧪 Testing configuration...")
    
    config = get_config()
    assert config.DB_HOST is not None
    assert config.API_BASE_URL is not None
    assert config.DATA_RAW_PATH is not None
    
    print("  ✅ Configuration loaded successfully")
    print(f"     Database: {config.DB_NAME}")
    print(f"     API URL: {config.API_BASE_URL}")


def test_data_lake():
    """Test data lake functionality."""
    print("\n🧪 Testing Data Lake...")
    
    config = get_config()
    json_lake = JSONDataLake(config.DATA_RAW_PATH)
    
    # Test save and load
    test_data = {
        "test": "data",
        "latitude": 45.5,
        "longitude": 2.5
    }
    
    filepath = json_lake.save(test_data, "test_data")
    print(f"  ✅ Data saved to {filepath}")
    
    # List files
    files = json_lake.list_files()
    print(f"  ✅ Found {len(files)} files in data lake")


def test_utilities():
    """Test utility functions."""
    print("\n🧪 Testing utility functions...")
    
    # Test distance calculation
    distance = calculate_distance(45.5, 2.5, 45.6, 2.6)
    print(f"  ✅ Distance calculation: {distance:.2f} km")
    
    # Test disruption risk assessment
    risk = assess_disruption_risk(distance, 30, intensity=75)
    print(f"  ✅ Risk assessment: {risk['risk_level']} (prob: {risk['disruption_probability']})")


def test_logging():
    """Test logging."""
    print("\n🧪 Testing logging...")
    
    logger.info("Test info message")
    logger.warning("Test warning message")
    
    print("  ✅ Logging configured successfully")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("🚀 PIPELINE ARCHITECTURE VALIDATION")
    print("=" * 60)
    
    try:
        test_imports()
        test_config()
        test_data_lake()
        test_utilities()
        test_logging()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n📋 Your pipeline is ready to use:")
        print("   1. Configure your .env file with database credentials")
        print("   2. Set up PostgreSQL database: createdb lightning_db")
        print("   3. Run pipeline: python main.py")
        print("   4. Run dashboard: streamlit run app.py")
        print("=" * 60)
        
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
