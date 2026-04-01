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
from src.database import PostgreSQLConnection, DataWarehouse


def load_data():
    """Load data from database.
    
    Returns:
        Tuple of (lightning_data, flights_data, disruptions_data)
    """
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
        
        # Load flights data (dummy for now)
        flights_df = pd.DataFrame()
        
        # Load disruptions data (dummy for now)
        disruptions_df = pd.DataFrame()
        
        db.disconnect()
        
        return lightning_df, flights_df, disruptions_df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def main():
    """Main dashboard application."""
    # Setup
    config = get_config()
    setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
    
    # Load data
    with st.spinner("Loading data..."):
        lightning_data, flights_data, disruptions_data = load_data()
    
    # Create and run dashboard
    dashboard = LightningDashboard()
    dashboard.run(
        lightning_data=lightning_data,
        flights_data=flights_data,
        disruptions_data=disruptions_data
    )


if __name__ == "__main__":
    main()
