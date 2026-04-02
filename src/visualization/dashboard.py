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
    
    def apply_lightning_filters(self, lightning_data: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply filters to lightning data.
        
        Args:
            lightning_data: Original lightning data
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered lightning data
        """
        if lightning_data.empty:
            return lightning_data
        
        df = lightning_data.copy()
        
        # Convert timestamp if not already datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        
        # Apply date range filter
        if "date_range" in filters and filters["date_range"]:
            date_range = filters["date_range"]
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                start_date = pd.Timestamp(date_range[0]).replace(hour=0, minute=0, second=0)
                end_date = pd.Timestamp(date_range[1]).replace(hour=23, minute=59, second=59)
                df = df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]
        
        # Apply minimum intensity filter
        if "min_intensity" in filters and "intensity" in df.columns:
            min_intensity = filters["min_intensity"]
            df = df[df["intensity"] >= min_intensity]
        
        return df
    
    def apply_flights_filters(self, flights_data: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Apply filters to flights data.
        
        Args:
            flights_data: Original flights data
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered flights data
        """
        if flights_data.empty:
            return flights_data
        
        df = flights_data.copy()
        
        # Convert timestamps if not already datetime
        for col in ["departure_time", "arrival_time", "timestamp"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        # Apply date range filter (use earliest timestamp column)
        if "date_range" in filters and filters["date_range"]:
            date_range = filters["date_range"]
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                start_date = pd.Timestamp(date_range[0]).replace(hour=0, minute=0, second=0)
                end_date = pd.Timestamp(date_range[1]).replace(hour=23, minute=59, second=59)
                
                # Filter by any available timestamp
                time_cols = [col for col in ["timestamp", "departure_time", "arrival_time"] if col in df.columns]
                if time_cols:
                    mask = pd.Series([False] * len(df), index=df.index)
                    for col in time_cols:
                        mask |= (df[col] >= start_date) & (df[col] <= end_date)
                    df = df[mask]
        
        return df
    
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
            st.header("🔧 Filters & Settings")
            
            today = pd.Timestamp.now().date()
            start_date = (pd.Timestamp.now() - pd.Timedelta(days=7)).date()
            
            # Minimum lightning intensity filter
            min_intensity = st.slider(
                "Minimum Lightning Intensity",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0
            )
            
            # Time scale selector
            time_scale = st.selectbox(
                "Lightning Timeline Scale",
                ["Hourly", "Daily"],
                index=1,
                help="Choose the time aggregation for the timeline graph"
            )
            
            # Add spacing before date picker
            st.divider()
            
            # Date range filter (moved to bottom for better accessibility)
            date_range = st.date_input(
                "📅 Select Date Range",
                value=(start_date, today)
            )
            
            filters = {
                "date_range": date_range,
                "min_intensity": min_intensity,
                "time_scale": time_scale,
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
            disruption_count = 0
            if not flights_data.empty and "disruption_probability" in flights_data.columns:
                disruption_count = len(flights_data[flights_data["disruption_probability"] > 0.5])
            st.metric("🚨 At-Risk Flights", disruption_count)
        
        with col4:
            avg_intensity = 0
            if not lightning_data.empty and "intensity" in lightning_data.columns:
                avg_intensity = lightning_data["intensity"].mean()
            st.metric("⚡ Avg Strike Intensity", f"{avg_intensity:.2f}")
        
        # Show last data received info
        st.divider()
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            if not lightning_data.empty and "timestamp" in lightning_data.columns:
                last_lightning = pd.to_datetime(lightning_data["timestamp"]).max()
                st.info(f"⚡ **Latest Lightning**: {last_lightning.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("⚡ **Latest Lightning**: No data")
        
        with col_info2:
            if not flights_data.empty:
                # Try multiple timestamp columns
                last_timestamp = None
                for col in ["timestamp", "departure_time", "arrival_time"]:
                    if col in flights_data.columns:
                        try:
                            ts = pd.to_datetime(flights_data[col]).max()
                            if pd.notna(ts):
                                last_timestamp = ts
                                break
                        except:
                            pass
                
                if last_timestamp:
                    st.info(f"✈️ **Latest Flight**: {last_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.info("✈️ **Latest Flight**: No data")
            else:
                st.info("✈️ **Latest Flight**: No data")
    
    def render_lightning_map(self, lightning_data: pd.DataFrame):
        """Render lightning strikes on a map.
        
        Args:
            lightning_data: Lightning strikes data with latitude and longitude
        """
        try:
            if lightning_data.empty or "latitude" not in lightning_data.columns or "longitude" not in lightning_data.columns:
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
    
    def render_timeline(self, lightning_data: pd.DataFrame, time_scale: str = "Daily"):
        """Render lightning strikes timeline with configurable time scale.
        
        Args:
            lightning_data: Lightning strikes data with timestamps
            time_scale: Time aggregation level ("Hourly", "Daily", "Weekly")
        """
        try:
            if lightning_data.empty or "timestamp" not in lightning_data.columns:
                st.warning("No timeline data available")
                return
            
            # Prepare data
            df_timeline = lightning_data.copy()
            df_timeline["timestamp"] = pd.to_datetime(df_timeline["timestamp"])
            
            # Group by selected time scale
            if time_scale == "Hourly":
                df_timeline["period"] = df_timeline["timestamp"].dt.floor("h")
                period_label = "Hour"
                date_format = "%Y-%m-%d %H:%M"
            elif time_scale == "Daily":
                df_timeline["period"] = df_timeline["timestamp"].dt.floor("D")
                period_label = "Date"
                date_format = "%Y-%m-%d"
            else:  # Weekly
                df_timeline["period"] = df_timeline["timestamp"].dt.floor("W")
                period_label = "Week"
                date_format = "%Y-W%U"
            
            timeline_data = df_timeline.groupby("period").size().reset_index(name="count")
            
            # Create figure with better styling
            fig = px.line(
                timeline_data,
                x="period",
                y="count",
                title=f"Lightning Strikes Over Time ({time_scale})",
                labels={"period": period_label, "count": "Number of Strikes"},
                markers=True,
                line_shape="linear"
            )
            
            # Enhance layout
            fig.update_layout(
                xaxis_title=period_label,
                yaxis_title="Number of Strikes",
                hovermode="x unified",
                font=dict(size=12),
                height=400
            )
            
            fig.update_traces(
                marker=dict(size=8, color="#FF6B35"),
                line=dict(color="#FF6B35", width=2)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Peak Activity", f"{timeline_data['count'].max()} strikes")
            with col2:
                st.metric("Average per Period", f"{timeline_data['count'].mean():.1f}")
            with col3:
                st.metric("Total Period Coverage", f"{len(timeline_data)} periods")
        
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
            if lightning_data is None:
                lightning_data = pd.DataFrame()
            if flights_data is None:
                flights_data = pd.DataFrame()
            if disruptions_data is None:
                disruptions_data = pd.DataFrame()
            
            # Render header
            self.render_header()
            
            # Render sidebar filters
            filters = self.render_sidebar()
            
            # Apply filters to data
            filtered_lightning = self.apply_lightning_filters(lightning_data, filters)
            filtered_flights = self.apply_flights_filters(flights_data, filters)
            
            # Render metrics (show both original and filtered counts)
            st.markdown("### 📊 Dashboard Metrics")
            st.markdown(f"*Showing filtered data (Lightning: {len(filtered_lightning)}/{len(lightning_data)}, Flights: {len(filtered_flights)}/{len(flights_data)})*")
            self.render_metrics(filtered_lightning, filtered_flights)
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📍 Lightning Map", "✈️ Flights", "🚨 Disruptions"])
            
            with tab1:
                self.render_lightning_map(filtered_lightning)
                self.render_timeline(filtered_lightning, time_scale=filters.get("time_scale", "Daily"))
            
            with tab2:
                self.render_flight_table(filtered_flights)
            
            with tab3:
                self.render_disruption_analysis(disruptions_data)
            
            self.logger.info("Dashboard rendered successfully")
        
        except Exception as e:
            self.logger.error(f"Error running dashboard: {str(e)}")
            st.error(f"Error running dashboard: {str(e)}")
