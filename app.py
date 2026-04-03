"""
Lightning & Flight Disruption Dashboard Application.

Main Streamlit application for monitoring lightning strikes and flight disruptions.
Application Streamlit principale pour surveiller les éclairs et perturbations de vol.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.utils.logger import setup_logging
from src.visualization.dashboard import LightningDashboard
from src.database.warehouse import PostgreSQLConnection, DataWarehouse


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = None


def load_data():
    """Load data from database.
    
    Returns:
        Tuple of (lightning_df, flights_df, disruptions_df) or error tuple
    """
    try:
        import pandas as pd
        
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
        
        # Load all data
        lightning_data = warehouse.query_lightning_data() or []
        flights_data = warehouse.query_flights_data() or []
        disruptions_data = warehouse.query_disruptions_data() or []
        
        # Convert to DataFrames
        lightning_df = pd.DataFrame(lightning_data) if lightning_data else pd.DataFrame()
        flights_df = pd.DataFrame(flights_data) if flights_data else pd.DataFrame()
        disruptions_df = pd.DataFrame(disruptions_data) if disruptions_data else pd.DataFrame()
        
        db.disconnect()
        
        return lightning_df, flights_df, disruptions_df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


def main():
    """Main application entry point."""
    # Setup
    config = get_config()
    setup_logging(log_file=config.LOG_FILE, level=config.LOG_LEVEL)
    
    # Initialize session state
    initialize_session_state()
    
    # Page configuration
    st.set_page_config(
        page_title="⚡ Lightning & Flight Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar controls
    with st.sidebar:
        st.title("🔧 Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("⚡ Clear Cache", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        st.divider()
    
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
