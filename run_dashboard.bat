@echo off
REM Dashboard Launcher Script
REM Launches the Lightning & Flight Disruption Monitor Dashboard

echo.
echo =========================================
echo    DASHBOARD START-UP
echo =========================================
echo.
echo Opening Streamlit dashboard...
echo URL: http://localhost:8501
echo.
echo Press CTRL+C in the terminal to stop the server
echo.

call venv\Scripts\activate.bat
streamlit run app.py

pause
