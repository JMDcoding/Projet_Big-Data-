"""
Streamlit dashboard application.
"""
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.utils import setup_logging, logger
from src.visualization import LightningDashboard

# Try to import database modules
try:
    from src.database import PostgreSQLConnection, DataWarehouse
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    PostgreSQLConnection = None
    DataWarehouse = None

# Try to import refresh service
try:
    from src.utils.refresh_service import get_refresh_service
    HAS_REFRESH_SERVICE = True
except ImportError:
    HAS_REFRESH_SERVICE = False
    get_refresh_service = None


@st.cache_resource
def initialize_refresh_service():
    """Initialize the data refresh service (cached to run once per session).
    
    Returns:
        RefreshService instance or None if not available
    """
    if not HAS_REFRESH_SERVICE:
        logger.warning("Refresh service not available")
        return None
    
    try:
        config = get_config()
        service = get_refresh_service(config)
        
        # Only start if not already running
        if not service.is_running:
            service.start()
            logger.info("Data refresh service started")
        
        return service
    except Exception as e:
        logger.error(f"Failed to initialize refresh service: {str(e)}")
        return None


def load_data():
    """Load data from database.
    
    Returns:
        Tuple of (lightning_data, flights_data, disruptions_data)
    """
    if not HAS_DATABASE:
        st.error(
            "❌ **PostgreSQL Database Not Available**\n\n"
            "The dashboard cannot load data because PostgreSQL is not installed or running.\n\n"
            "**To fix this:**\n"
            "1. Install PostgreSQL on port 5433 (https://www.postgresql.org/download/)\n"
            "2. Create a database named `lightning_db`\n"
            "3. Run: `python initialize_db.py`\n"
            "4. Run: `python main.py` to load data\n"
            "5. Restart the dashboard"
        )
        logger.info("PostgreSQL not available - database mode disabled")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    try:
        config = get_config()
        db = PostgreSQLConnection(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        db.connect()
        
        warehouse = DataWarehouse(db)
        
        # Load lightning data
        lightning_data = warehouse.query_lightning_data()
        lightning_df = pd.DataFrame(lightning_data) if lightning_data else pd.DataFrame()
        
        # Load flights data
        flights_data = warehouse.query_flights_data()
        flights_df = pd.DataFrame(flights_data) if flights_data else pd.DataFrame()
        
        # Load disruptions data
        disruptions_data = warehouse.query_disruptions_data()
        disruptions_df = pd.DataFrame(disruptions_data) if disruptions_data else pd.DataFrame()
        
        db.disconnect()
        
        return lightning_df, flights_df, disruptions_df
    
    except Exception as e:
        error_msg = str(e)
        if "refused" in error_msg.lower() or "connection" in error_msg.lower():
            st.error(
                "❌ **PostgreSQL Connection Failed**\n\n"
                f"**Error:** {error_msg}\n\n"
                "**Solution:** Make sure PostgreSQL is running on port 5433:\n"
                "- Windows: Start PostgreSQL service or run `pg_ctl -D \"C:\\Program Files\\PostgreSQL\\13\\data\" start`\n"
                "- Linux/Mac: Run `sudo service postgresql start` or `brew services start postgresql`\n\n"
                "**Then:** Run `python main.py` to load data into the database"
            )
        else:
            st.error(f"❌ **Error loading data:** {error_msg}")
        logger.error(f"Error loading data: {error_msg}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def main():
    """Main dashboard application."""
    # Setup
    config = get_config()
    setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
    
    # Initialize refresh service (will only run once per session)
    refresh_service = initialize_refresh_service()
    
    # Load data
    with st.spinner("Loading data..."):
        lightning_data, flights_data, disruptions_data = load_data()
    
    # Create and run dashboard
    dashboard = LightningDashboard()
    
    # Add refresh service status to sidebar if available
    if refresh_service and refresh_service.is_running:
        with st.sidebar:
            st.divider()
            st.markdown("### 🔄 Auto-Refresh Status")
            
            status = refresh_service.get_status()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Lightning**")
                if status["last_lightning_refresh"]:
                    last_refresh = status["last_lightning_refresh"].strftime("%H:%M:%S")
                    st.caption(f"Last: {last_refresh}")
                else:
                    st.caption("Pending...")
            
            with col2:
                st.markdown("**Flights**")
                if status["last_flights_refresh"]:
                    last_refresh = status["last_flights_refresh"].strftime("%H:%M:%S")
                    st.caption(f"Last: {last_refresh}")
                else:
                    st.caption("Pending...")
    
    dashboard.run(
        lightning_data=lightning_data,
        flights_data=flights_data,
        disruptions_data=disruptions_data
    )


if __name__ == "__main__":
    main()
