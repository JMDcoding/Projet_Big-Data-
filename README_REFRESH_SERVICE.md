# Automatic Data Refresh Service

## Overview

The project now includes an **automatic data refresh service** that continuously fetches the latest lightning and flight data from APIs at regular intervals.

### Refresh Schedule

- **⚡ Lightning Data**: Every **20 minutes** (high priority)
- **✈️ Flights Data**: Every **2 hours**
- **🗄️ Storage**: All data is saved to PostgreSQL and MinIO (if available)

## How to Use

### Option 1: Use Integrated Refresh (Recommended)

The refresh service starts automatically when you launch the Streamlit dashboard.

```bash
streamlit run app.py
```

**Status Display:**
- The dashboard sidebar shows "Auto-Refresh Status" with timestamps of the last refresh for each data type
- The service runs in the background while you use the dashboard

### Option 2: Run Standalone Refresh Service

For continuous background refresh without using Streamlit, run the standalone service:

#### Windows Command Prompt:
```batch
start_refresh_service.bat
```

#### Windows PowerShell:
```powershell
.\start_refresh_service.ps1
```

#### Linux/Mac Terminal:
```bash
python refresh_service_standalone.py
```

The service will:
1. Start automatically
2. Fetch lightning data immediately
3. Fetch flights data immediately
4. Continue refreshing on schedule

### Option 3: Run Service from Python

```python
from src.utils.refresh_service import get_refresh_service
from config.config import get_config

config = get_config()
service = get_refresh_service(config)
service.start()

# Service is now running in background
# Check status:
status = service.get_status()
print(status)
```

## Service Status

Monitor the refresh service status:

```python
status = service.get_status()
print({
    "is_running": status["is_running"],
    "last_lightning_refresh": status["last_lightning_refresh"],
    "last_flights_refresh": status["last_flights_refresh"],
    "scheduled_jobs": status["jobs"]
})
```

## Configuration

### Change Refresh Intervals

Edit `src/utils/refresh_service.py`:

```python
# Lightning refresh (minutes)
IntervalTrigger(minutes=20),  # Change 20 to desired minutes

# Flights refresh (hours)
IntervalTrigger(hours=2),     # Change 2 to desired hours
```

### Disable Integrated Refresh

If you don't want the Streamlit dashboard to refresh data automatically, you can disable it by editing `app.py`:

```python
# Comment out this line in main():
# refresh_service = initialize_refresh_service()
```

## Logging

The refresh service logs all activities to:
- Console output (when running standalone)
- Log file: `logs/lightning_pipeline.log`

Look for messages like:
```
INFO - DataRefreshService started successfully
INFO - Refreshing lightning data...
INFO - Lightning refresh completed: 52 records loaded in 3.2s
INFO - Refreshing flights data...
INFO - Flights refresh completed: 2902 records loaded in 1.5s
```

## Requirements

The following packages must be installed:
- `apscheduler>=3.10.0` - For job scheduling
- `minio>=7.1.0` - For object storage

Install them:
```bash
pip install -r requirements.txt
```

## Troubleshooting

### Service doesn't start
- Check that PostgreSQL is running on port 5433
- Verify database credentials in `config/config.py`
- Check log file for errors

### Data not updating
- Verify the API endpoints are reachable (OpenSky, etc.)
- Check network connectivity
- Review log file for API errors

### Performance issues
- Increase refresh intervals if system is slow
- Consider running service on separate machine for heavy workloads
- Monitor disk space for data/minio/

## Architecture

```
┌─────────────────────────────────────────┐
│    Streamlit Dashboard (app.py)         │
│  ┌───────────────────────────────────┐  │
│  │  Auto-Refresh Service             │  │
│  │  (integrated, optional)           │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ Or Standalone Refresh Service           │
│ (refresh_service_standalone.py)         │
│ APScheduler → Periodic Tasks            │
└─────────────────────────────────────────┘
                    ↓
            ┌───────────────┐
            │ Every 20 min: │ Lightning API
            │ Every 2 hrs:  │ Flights API
            └───────────────┘
                    ↓
        ┌───────────────────────┐
        │  Transformation      │
        │  (DataFrame)         │
        └───────────────────────┘
                    ↓
        ┌─────────────┬─────────────┐
        ↓             ↓
    PostgreSQL    MinIO (S3)
  (indexed DB)  (object storage)
```

## Health Checks

To verify the service is working:

```python
# Check if data is being updated
from src.database import PostgreSQLConnection, DataWarehouse
from config.config import get_config

config = get_config()
db = PostgreSQLConnection(...)
db.connect()
warehouse = DataWarehouse(db)

# Count records
lightning = warehouse.query_lightning_data()
flights = warehouse.query_flights_data()

print(f"Lightning: {len(lightning)} records")
print(f"Flights: {len(flights)} records")
```

## Next Steps

1. ✅ Start the refresh service
2. ✅ Watch data load in real-time every 20 minutes (lightning) / 2 hours (flights)
3. ✅ Dashboard automatically reflects latest data
4. 📊 Create alerts based on data changes
5. 🔔 Implement notifications for high-risk situations
