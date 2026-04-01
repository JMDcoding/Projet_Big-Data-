"""
Dashboard visualization using Streamlit.
"""
import logging
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import pandas as pd


class DashboardConfig:
    """Dashboard configuration."""
    
    PAGE_TITLE = "⚡ Lightning & Flight Disruption Monitor"
    PAGE_LAYOUT = "wide"
    THEME = "light"


class LightningDashboard:
    """Dashboard for visualizing lightning and flight disruption data."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._configure_page()
    
    def _configure_page(self):
        """Configure Streamlit page settings."""
        try:
            st.set_page_config(
                page_title=DashboardConfig.PAGE_TITLE,
                layout=DashboardConfig.PAGE_LAYOUT,
                initial_sidebar_state="expanded"
            )
            self.logger.info("Dashboard configured")
        except Exception as e:
            self.logger.error(f"Error configuring page: {str(e)}")
    
    def render_header(self):
        """Render dashboard header."""
        st.markdown("# ⚡ Lightning & Flight Disruption Monitor")
        st.markdown("---")
        st.markdown("Real-time monitoring of lightning strikes and potential flight disruptions")
    
    def render_sidebar(self) -> Dict:
        """Render sidebar with filters.
        
        Returns:
            Dictionary of selected filters
        """
        with st.sidebar:
            st.header("🔧 Filters")
            
            filters = {
                "date_range": st.date_input(
                    "Select Date Range",
                    value=(pd.Timestamp.now() - pd.Timedelta(days=7), pd.Timestamp.now())
                ),
                "region": st.selectbox(
                    "Select Region",
                    ["All", "Europe", "North America", "Asia", "Other"]
                ),
                "risk_level": st.multiselect(
                    "Risk Level",
                    ["Low", "Medium", "High", "Critical"],
                    default=["Medium", "High", "Critical"]
                ),
                "min_intensity": st.slider(
                    "Minimum Lightning Intensity",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0
                ),
            }
            
            return filters
    
    def render_metrics(self, lightning_data: pd.DataFrame, flights_data: pd.DataFrame):
        """Render key metrics.
        
        Args:
            lightning_data: Lightning strikes data
            flights_data: Flights data
        """
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⚡ Total Lightning Strikes", len(lightning_data))
        
        with col2:
            st.metric("✈️ Total Flights", len(flights_data))
        
        with col3:
            disruption_count = len(flights_data[flights_data.get("disruption_probability", 0) > 0.5])
            st.metric("🚨 At-Risk Flights", disruption_count)
        
        with col4:
            avg_intensity = lightning_data["intensity"].mean() if "intensity" in lightning_data else 0
            st.metric("⚡ Avg Strike Intensity", f"{avg_intensity:.2f}")
    
    def render_lightning_map(self, lightning_data: pd.DataFrame):
        """Render lightning strikes on a map.
        
        Args:
            lightning_data: Lightning strikes data with latitude and longitude
        """
        try:
            if lightning_data.empty or "latitude" not in lightning_data or "longitude" not in lightning_data:
                st.warning("No lightning data available")
                return
            
            fig = px.scatter_mapbox(
                lightning_data,
                lat="latitude",
                lon="longitude",
                hover_data=["intensity", "timestamp"],
                color="intensity",
                size="intensity",
                color_continuous_scale="YlOrRd",
                zoom=3,
                title="Lightning Strikes Map"
            )
            
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            self.logger.error(f"Error rendering map: {str(e)}")
            st.error(f"Error rendering map: {str(e)}")
    
    def render_timeline(self, lightning_data: pd.DataFrame):
        """Render lightning strikes timeline.
        
        Args:
            lightning_data: Lightning strikes data with timestamps
        """
        try:
            if lightning_data.empty or "timestamp" not in lightning_data:
                st.warning("No timeline data available")
                return
            
            # Group by hour
            df_timeline = lightning_data.copy()
            df_timeline["timestamp"] = pd.to_datetime(df_timeline["timestamp"])
            df_timeline["hour"] = df_timeline["timestamp"].dt.floor("H")
            
            timeline_data = df_timeline.groupby("hour").size().reset_index(name="count")
            
            fig = px.line(
                timeline_data,
                x="hour",
                y="count",
                title="Lightning Strikes Over Time",
                labels={"hour": "Time", "count": "Number of Strikes"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            self.logger.error(f"Error rendering timeline: {str(e)}")
            st.error(f"Error rendering timeline: {str(e)}")
    
    def render_flight_table(self, flights_data: pd.DataFrame):
        """Render flight data table.
        
        Args:
            flights_data: Flights data
        """
        try:
            if flights_data.empty:
                st.warning("No flight data available")
                return
            
            st.subheader("✈️ Flights Status")
            st.dataframe(flights_data, use_container_width=True)
        
        except Exception as e:
            self.logger.error(f"Error rendering flight table: {str(e)}")
            st.error(f"Error rendering table: {str(e)}")
    
    def render_disruption_analysis(self, disruptions_data: pd.DataFrame):
        """Render flight disruption analysis.
        
        Args:
            disruptions_data: Disruption data
        """
        try:
            if disruptions_data.empty:
                st.info("No disruptions detected")
                return
            
            st.subheader("🚨 Disruption Analysis")
            
            # Risk level distribution
            risk_dist = disruptions_data["risk_level"].value_counts()
            fig = px.pie(
                values=risk_dist.values,
                names=risk_dist.index,
                title="Disruption Risk Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed table
            st.dataframe(disruptions_data, use_container_width=True)
        
        except Exception as e:
            self.logger.error(f"Error rendering disruption analysis: {str(e)}")
            st.error(f"Error rendering analysis: {str(e)}")
    
    def run(self, lightning_data: Optional[pd.DataFrame] = None, 
            flights_data: Optional[pd.DataFrame] = None,
            disruptions_data: Optional[pd.DataFrame] = None):
        """Run the dashboard application.
        
        Args:
            lightning_data: Lightning strikes data
            flights_data: Flights data
            disruptions_data: Disruptions data
        """
        try:
            # Set default empty DataFrames
            lightning_data = lightning_data or pd.DataFrame()
            flights_data = flights_data or pd.DataFrame()
            disruptions_data = disruptions_data or pd.DataFrame()
            
            # Render header
            self.render_header()
            
            # Render sidebar filters
            filters = self.render_sidebar()
            
            # Render metrics
            self.render_metrics(lightning_data, flights_data)
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📍 Lightning Map", "✈️ Flights", "🚨 Disruptions"])
            
            with tab1:
                self.render_lightning_map(lightning_data)
                self.render_timeline(lightning_data)
            
            with tab2:
                self.render_flight_table(flights_data)
            
            with tab3:
                self.render_disruption_analysis(disruptions_data)
            
            self.logger.info("Dashboard rendered successfully")
        
        except Exception as e:
            self.logger.error(f"Error running dashboard: {str(e)}")
            st.error(f"Error running dashboard: {str(e)}")
