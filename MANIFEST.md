# Project Manifest - File Reference Guide

**Last Updated:** Session 8 - Project Reorganization Complete
**Total Files:** ~100+ core + venv + __pycache__

## 📋 Quick Navigation

- [Root Level](#root-level)
- [Configuration](#configuration)
- [Source Code](#source-code)
- [Scripts](#scripts)
- [Tests](#tests)
- [Data & Logs](#data--logs)

---

## Root Level

### Main Application Files

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | **Main Streamlit dashboard entry point** | ✅ Production |
| `README.md` | **Comprehensive tutorial & documentation** | ✅ Production |
| `QUICK_START.txt` | **3-step 5-minute setup guide** | ✅ Production |
| `MANIFEST.md` | This file - project file reference | ✅ Reference |
| `requirements.txt` | Python package dependencies | ✅ Production |

### Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, DB port, logs) |
| `.gitignore` | Git ignore rules |
| `pytest.ini` | Pytest configuration (if using tests) |

### Archived/Removed

| File | Reason | Status |
|------|--------|--------|
| `app_BACKUP.py` | Old app version | ❌ Deleted (Session 8) |
| `README_BACKUP.md` | Old README | ❌ Deleted (Session 8) |
| 60+ legacy files | Cleanup complete | ❌ Deleted (Session 8) |

---

## Configuration

**Location:** `config/`

| File | Class/Function | Purpose |
|------|---|---------|
| `config.py` | `Config`, `ConfigDev`, `ConfigProd` | Environment-based config management |
| | `get_config()` | Returns appropriate config for environment |
| | `DATABASE_CONFIG` | PostgreSQL connection dict |

**Usage Example:**
```python
from config.config import get_config
config = get_config()  # Returns ConfigDev or ConfigProd
print(config.DATABASE_URL)  # Access configuration
```

---

## Source Code

### Database Layer

**Location:** `src/database/`

| File | Class | Purpose |
|------|-------|---------|
| `warehouse.py` | `DataWarehouse` | High-level data access abstraction |
| | `PostgreSQLConnection` | Low-level PostgreSQL connection management |

**Key Methods:**
```python
warehouse = DataWarehouse()
warehouse.get_all_lightning()
warehouse.insert_lightning(data)
warehouse.delete_all_lightning()
```

### Ingestion (APIs & Data Fetching)

**Location:** `src/ingestion/`

| File | Class | Purpose |
|------|-------|---------|
| `base.py` | `BaseAPI` | Abstract base class for all APIs |
| `api_client.py` | `APIClient` | Generic HTTP client for external APIs |
| `alternative_apis.py` | `AlternativeWeatherAPI`, etc. | Alternative weather data sources |
| `blitzortung_websocket.py` | `BlitzortungWebSocket` | Lightning strike websocket client |
| `storm_forecast.py` | `StormForecastAPI` | Storm prediction API client |
| `web_scraper.py` | `WebScraper` | HTML scraping utilities |

**Integration Pattern:**
```python
# All inherit from BaseAPI
class MyAPI(BaseAPI):
    def fetch_data(self):
        # Fetch from external source
    
    def transform_data(self):
        # Clean and structure data
```

### Transformation (Business Logic)

**Location:** `src/transformation/`

| File | Class | Purpose |
|------|-------|---------|
| `transformer.py` | `DataTransformer` | Generic ETL patterns |
| `disruption_calculator.py` | `DisruptionCalculator` | Calculates flight disruption risk |
| `trajectory_predictor.py` | `TrajectoryPredictor` | Predicts flight paths |

**Example:**
```python
calc = DisruptionCalculator()
risk = calc.calculate_disruption_risk(lightning_data, flight_data)
```

### Utilities

**Location:** `src/utils/`

| File | Function/Class | Purpose |
|------|---|---------|
| `logger.py` | `setup_logging()` | Initialize application logger |
| | `get_logger()` | Get named logger instance |
| `helpers.py` | Various functions | Data validation, formatting, etc. |
| `refresh_service.py` | `RefreshService` | Automated data refresh scheduling |
| `constants.py` | Constants | Application-wide constants |

**Usage:**
```python
from src.utils.logger import setup_logging
logger = setup_logging("app.log", "INFO")
logger.info("Application started")
```

### Visualization (Streamlit)

**Location:** `src/visualization/`

| File | Class | Purpose |
|------|-------|---------|
| `dashboard.py` | `LightningDashboard` | Main Streamlit dashboard class |
| | `Dashboard` | Supporting dashboard utilities |
| `components.py` | Various | Reusable UI components |

**Main Component:**
```python
class LightningDashboard:
    def render_map(self)      # Display lightning on map
    def render_timeline()     # Show chronological data
    def render_stats()        # Display statistics
```

---

## Scripts

**Location:** `scripts/` - Utility entry points for automation

| File | Purpose | Usage |
|------|---------|-------|
| `setup_database.py` | Initialize database with schema | `python scripts/setup_database.py` |
| `refresh_data.py` | Fetch data from all APIs | `python scripts/refresh_data.py` |
| `populate_demo.py` | Load 6 demo lightning records | `python scripts/populate_demo.py` |
| `verify_data.py` | Print current data counts | `python scripts/verify_data.py` |
| `reset_data.py` | Clear all data (preserve schema) | `python scripts/reset_data.py` |
| `__init__.py` | Makes scripts a Python package | (Internal) |

**Typical Workflow:**
```bash
# 1. Initialize database
python scripts/setup_database.py

# 2. Load demo or real data
python scripts/populate_demo.py
# OR
python scripts/refresh_data.py

# 3. Verify data loaded
python scripts/verify_data.py

# 4. Run dashboard
streamlit run app.py
```

---

## Tests

**Location:** `tests/` (if present)

| File | Type | Purpose |
|------|------|---------|
| `test_*.py` | Unit Tests | Individual component testing |
| `conftest.py` | Fixtures | Shared test fixtures (if present) |

**Run Tests:**
```bash
pytest tests/
```

---

## Data & Logs

### Data Storage

**Location:** `data/`

| Directory | Purpose |
|-----------|---------|
| `data/minio/` | MinIO object storage (if enabled) |
| `data-lake/` | Raw data lake storage |

### Logs

**Location:** `logs/`

| File | Purpose |
|------|---------|
| `app.log` | Main application logs |
| `database.log` | Database operation logs |
| `refresh.log` | Data refresh service logs |

---

## Database Schema

### Tables

| Table | Records | Purpose |
|-------|---------|---------|
| `lightning_strikes` | ~18-24 | Lightning detection data |
| `flights` | ~300+ | Flight information |
| `flight_disruptions` | 0+ | Calculated disruption records |

### Example: lightning_strikes Schema
```
- id (int, primary key)
- latitude (float)
- longitude (float)
- intensity (float)
- timestamp (datetime)
- location (varchar)
```

---

## Dependencies

**Location:** `requirements.txt`

Key packages installed:
- `streamlit` - Web dashboard framework
- `psycopg2` - PostgreSQL driver
- `pandas` - Data manipulation
- `plotly` - Interactive visualizations
- `requests` - HTTP client
- `python-dotenv` - Environment variables
- `pytz` - Timezone handling

---

## Environment Variables (.env)

**Required Variables:**

```ini
# Database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lightning_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# APIs
AIRLABS_API_KEY=your_airlabs_key
OPENMETEO_KEY=free

# Application
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
ENVIRONMENT=dev
```

---

## Quick Reference: File Purposes

### If you need to...

| Goal | File | Function |
|------|------|----------|
| **Start the dashboard** | `app.py` | Line: `if __name__ == "__main__":` |
| **Fetch lightning data** | `src/ingestion/base.py` | `fetch_data()` |
| **Calculate disruption risk** | `src/transformation/disruption_calculator.py` | `calculate_disruption_risk()` |
| **Initialize database** | `scripts/setup_database.py` | `python scripts/setup_database.py` |
| **Load demo data** | `scripts/populate_demo.py` | `python scripts/populate_demo.py` |
| **Configure settings** | `config/config.py` | Update `ConfigDev` or `ConfigProd` class |
| **Add logging** | `src/utils/logger.py` | `setup_logging()` |
| **Access database** | `src/database/warehouse.py` | `DataWarehouse` class |
| **Understand architecture** | `README.md` | Full documentation |
| **Quick start** | `QUICK_START.txt` | 3-step setup |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Session 8 | Project restructured to POO, 60 files cleaned |
| 0.9 | Session 7 | Dashboard and database fixes |
| 0.8 | Session 6 | Real data integration |

---

## Support

- **Documentation:** See `README.md`
- **Quick Setup:** See `QUICK_START.txt`
- **Issues:** Check `logs/app.log`
- **Code Structure:** This file + docstrings in source

---

**Project Status:** ✅ Production Ready
**Last Testing:** Session 8 - All systems verified
**Next Steps:** Deploy or extend with new features

