#!/bin/bash
# Dashboard Launcher Script
# Launches the Lightning & Flight Disruption Monitor Dashboard

echo ""
echo "========================================="
echo "    DASHBOARD START-UP"
echo "========================================="
echo ""
echo "Opening Streamlit dashboard..."
echo "URL: http://localhost:8501"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

source venv/bin/activate
streamlit run app.py
