# Big Data Pipeline - Lightning & Flight Disruption Analysis

## 📋 Project Overview

This project implements a complete data pipeline for real-time lightning strike monitoring and flight disruption analysis. It follows modern data engineering practices with ETL architecture (Extract, Transform, Load).

**Key Features:**
- ⚡ Real-time lightning data from Blitzortung API
- ✈️ Flight data ingestion via web scraping
- 🔄 Full ETL pipeline with Python OOP
- 💾 Data Lake storage (JSON/CSV)
- 🗄️ PostgreSQL Data Warehouse
- 📊 Interactive Streamlit Dashboard

---

## 🏗️ Project Structure

```
Projet_Big-Data-/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── ingestion/                # Data collection
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract DataSource
│   │   ├── api_client.py        # Blitzortung API client
│   │   └── web_scraper.py       # Web scraping classes
│   ├── storage/                 # Data Lake storage
│   │   ├── __init__.py
│   │   └── data_lake.py         # JSON/CSV storage classes
│   ├── transformation/          # Data processing
│   │   ├── __init__.py
│   │   └── transformer.py       # Transformation logic
│   ├── database/                # Data Warehouse
│   │   ├── __init__.py
│   │   └── warehouse.py         # PostgreSQL management
│   ├── visualization/           # Dashboard
│   │   ├── __init__.py
│   │   └── dashboard.py         # Streamlit UI
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logger.py            # Logging setup
│       └── helpers.py           # Helper functions
├── config/                       # Configuration
│   ├── config.py                # Config classes
│   └── .env.example             # Environment variables template
├── data/                         # Data storage
│   ├── raw/                     # Raw data (Data Lake)
│   └── processed/               # Processed data
├── logs/                         # Logging
├── main.py                       # Main pipeline entry point
├── app.py                        # Streamlit dashboard
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip or conda

### 1. Clone and Setup Virtual Environment

```bash
# Navigate to project directory
cd "path/to/Projet_Big-Data-"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On MacOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy template
copy config\.env.example config\.env

# Edit config/.env with your settings:
# - Database credentials
# - API configuration
# - Data paths
```

### 4. Initialize Database

```bash
# Create PostgreSQL database
createdb lightning_db

# The pipeline will create tables automatically on first run
```

### 5. Run the Pipeline

```bash
# Main pipeline
python main.py

# Or run dashboard
streamlit run app.py
```

---

## 🔄 Pipeline Workflow

### 1. **Ingestion** 
- Fetch lightning data from Blitzortung API
- Scrape flight information from airline websites
- Validate incoming data

### 2. **Storage (Data Lake)**
- Store raw data in JSON/CSV format
- Maintain data lineage and history
- Enable data recovery

### 3. **Transformation**
- Clean and standardize data
- Handle missing values
- Add computed columns
- Merge multiple data sources

### 4. **Loading (Data Warehouse)**
- Create normalized tables
- Load transformed data into PostgreSQL
- Set up relationships between tables

### 5. **Visualization**
- Interactive dashboard with Streamlit
- Real-time lightning map
- Flight status monitoring
- Disruption risk analysis

---

## 📦 Key Classes and Architecture

### Ingestion Module
```python
# Base class for all data sources
class DataSource(ABC):
    def fetch() -> Any
    def validate(data) -> bool
    def extract() -> Any

# Specific implementations
class BlitzortungAPI(DataSource)
class WebScraper(DataSource)
```

### Storage Module
```python
class DataLake(ABC):
    def save(data, filename) -> str
    def load(filename) -> Any
    def delete(filename) -> bool

class JSONDataLake(DataLake)
class CSVDataLake(DataLake)
```

### Transformation Module
```python
class Transformer(ABC):
    def transform(data) -> Any

class LightningDataTransformer(Transformer)
class FlightDataTransformer(Transformer)
class DataMerger(Transformer)
```

### Database Module
```python
class PostgreSQLConnection(DatabaseConnection):
    def connect()
    def execute(query, params) -> List

class DataWarehouse:
    def create_lightning_table()
    def insert_lightning_data(data)
    def query_lightning_data(filters)
```

### Visualization Module
```python
class LightningDashboard:
    def render_header()
    def render_sidebar() -> Dict
    def render_lightning_map()
    def render_timeline()
    def run()
```

---

## ⚙️ Configuration

Edit `config/.env`:

```ini
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lightning_db
DB_USER=postgres
DB_PASSWORD=your_password

# API
API_BASE_URL=https://www.blitzortung.org/en/live_lightning_maps.php
API_TIMEOUT=30

# Data paths
DATA_RAW_PATH=./data/raw
DATA_PROCESSED_PATH=./data/processed

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## 📊 Database Schema

### lightning_strikes table
- `id`: Primary key
- `lightning_id`: Strike identifier
- `latitude`, `longitude`: Coordinates
- `altitude`: Strike altitude
- `intensity`: Strike intensity
- `timestamp`: Strike time
- `processed_at`: Processing time

### flights table
- `id`: Primary key
- `flight_number`: Flight ID
- `departure`, `arrival`: Airports
- `departure_time`, `arrival_time`: Times
- `aircraft_type`: Aircraft model

### flight_disruptions table
- `id`: Primary key
- `flight_id`: Reference to flight
- `lightning_id`: Reference to lightning strike
- `distance_km`: Distance to strike
- `risk_level`: Risk level (Low/Medium/High/Critical)
- `disruption_probability`: Probability score

---

## 🎯 Disruption Analysis

The system assesses flight disruption risk by analyzing:

1. **Distance Factor** (40%): How far is the lightning from flight path?
2. **Time Factor** (40%): When will the lightning strike vs. flight time?
3. **Intensity Factor** (20%): How intense is the lightning strike?

Risk levels are calculated as:
- **Low**: Probability < 20%
- **Medium**: Probability 20-50%
- **High**: Probability 50-80%
- **Critical**: Probability > 80%

---

## 🧪 Testing

Run tests for individual modules:

```bash
# Test API client
python -m pytest tests/test_api_client.py

# Test transformers
python -m pytest tests/test_transformer.py

# Test database
python -m pytest tests/test_warehouse.py
```

---

## 📈 Monitoring and Logging

All operations are logged to:
- **Console**: Real-time output
- **File**: `logs/app.log` (rotating file handler)

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🔐 Security Notes

⚠️ **Important:**
- Never commit `.env` file with real credentials
- Use environment variables for sensitive data
- Set proper PostgreSQL user permissions
- Keep dependencies updated

---

## 🤝 Contributing

1. Create a new branch for features
2. Follow PEP 8 style guide
3. Add docstrings to all classes and methods
4. Test thoroughly before merging

---

## 📝 License

This project is proprietary - Emineo Education

---

## 📞 Support

For issues or questions, contact the development team.

---

**Created:** April 2026  
**Last Updated:** April 2026
