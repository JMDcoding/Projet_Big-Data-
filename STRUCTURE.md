# 📁 PROJECT STRUCTURE GUIDE

**Last Updated:** April 3, 2026 (Session 8 - Cleanup Complete)

## Visual Overview

```
🏢 Projet_Big-Data-/
│
├─── 🎯 MAIN APPLICATION
│    ├─ app.py .......................... Streamlit dashboard (START HERE ▶️)
│    ├─ requirements.txt ............... Python dependencies
│    ├─ .env ........................... Configuration variables
│    └─ .gitignore ..................... Git ignore rules
│
├─── 📚 DOCUMENTATION (READ THESE)
│    ├─ README.md ...................... Full guide & tutorial (350+ lines)
│    ├─ QUICK_START.txt ................ 3-step setup (5 minutes)
│    ├─ MANIFEST.md .................... File reference guide
│    ├─ CLEANUP_REPORT.md .............. This cleanup summary
│    └─ PROJECT_REPORT.md .............. Project status & metrics
│
├─── ⚙️ CONFIGURATION
│    └─ config/
│       ├─ config.py ................... Environment-based settings
│       ├─ __init__.py
│       └─ (database config, API keys, etc.)
│
├─── 💾 SOURCE CODE (POO Architecture)
│    └─ src/
│       ├─ database/ ................... Data access layer
│       │  ├─ warehouse.py ............ DataWarehouse class
│       │  ├─ __init__.py
│       │  └─ (connection management)
│       │
│       ├─ ingestion/ .................. External API clients
│       │  ├─ base.py ................. BaseAPI class
│       │  ├─ api_client.py ........... HTTP client
│       │  ├─ alternative_apis.py ..... Alternative weather
│       │  ├─ blitzortung_websocket.py  Lightning websocket
│       │  ├─ storm_forecast.py ....... Storm prediction
│       │  ├─ web_scraper.py .......... HTML scraper
│       │  ├─ __init__.py
│       │  └─ (API integrations)
│       │
│       ├─ transformation/ ............. Business logic & ETL
│       │  ├─ transformer.py .......... Data transformation
│       │  ├─ disruption_calculator.py  Disruption calculations
│       │  ├─ trajectory_predictor.py .. Flight trajectory
│       │  ├─ __init__.py
│       │  └─ (business logistics)
│       │
│       ├─ utils/ ...................... Utilities & helpers
│       │  ├─ logger.py ............... setup_logging() ← IMPORTANT
│       │  ├─ helpers.py .............. Data helpers
│       │  ├─ refresh_service.py ...... Data refresh scheduling
│       │  ├─ constants.py ............ Application constants
│       │  ├─ __init__.py
│       │  └─ (cross-cutting concerns)
│       │
│       ├─ visualization/ .............. UI components
│       │  ├─ dashboard.py ............ LightningDashboard class
│       │  ├─ components.py ........... UI components
│       │  ├─ __init__.py
│       │  └─ (Streamlit interface)
│       │
│       └─ __init__.py
│
├─── 🔧 PRODUCTION SCRIPTS
│    └─ scripts/
│       ├─ setup_database.py .......... Initialize database ✅
│       ├─ refresh_data.py ............ Fetch real data from APIs ✅
│       ├─ populate_demo.py ........... Load demo data for testing ✅
│       ├─ reset_data.py .............. Clear all data ✅
│       ├─ verify_data.py ............. Check data counts ✅
│       ├─ initialize_db.py ........... Database utility
│       ├─ __init__.py
│       └─ (automation & utilities)
│
├─── 🧪 UNIT TESTS
│    └─ tests/
│       ├─ test_*.py .................. Pytest test files (when added)
│       ├─ conftest.py ................ Shared fixtures (optional)
│       └─ (pytest directory structure)
│
├─── 💾 DATA STORAGE
│    ├─ data/ .......................... Local data
│    │  ├─ minio/ ..................... MinIO object storage
│    │  └─ local/ ..................... Local files
│    │
│    └─ data-lake/ .................... Raw data lake
│       └─ (staging area for raw data)
│
├─── 📊 JUPYTER NOTEBOOKS
│    └─ notebooks/
│       ├─ eda_analysis.ipynb ......... Data analysis notebook
│       ├─ README_EDA.md .............. Notebook documentation
│       └─ NOTEBOOK_REPORT.md ......... Notebook report
│
├─── 📋 APPLICATION LOGS
│    └─ logs/
│       ├─ app.log .................... Main application log
│       ├─ database.log ............... Database operations log
│       └─ refresh.log ................ Data refresh service log
│
├─── 📦 ARCHIVED FILES (Not in use - see CLEANUP_REPORT.md)
│    └─ archive/
│       ├─ tests/ ..................... 985+ legacy test files
│       ├─ utilities/ ................. 18 old utility scripts
│       ├─ setup-scripts/ ............. 13 .bat/.ps1 files
│       ├─ deprecated/ ................ 14+ old code/documentation
│       ├─ README.md .................. Archive guide
│       └─ (1,038 files total - for reference only)
│
└─── 🐍 PYTHON ENVIRONMENT
     └─ venv/
        ├─ Scripts/ ................... Python executable & tools
        ├─ Lib/ ....................... Installed packages
        ├─ Include/ ................... Header files
        ├─ pyvenv.cfg ................. Environment configuration
        └─ (virtual environment)
```

---

## 🎯 Quick Navigation

### I Want To...

**Run the dashboard:**
```bash
streamlit run app.py
```

**Set up the database:**
```bash
python scripts/setup_database.py
```

**Load demo data:**
```bash
python scripts/populate_demo.py
```

**See what data is in database:**
```bash
python scripts/verify_data.py
```

**Refresh with real API data:**
```bash
python scripts/refresh_data.py
```

**Clear all data (keep schema):**
```bash
python scripts/reset_data.py
```

**Add new data fetching logic:**
→ Create class in `src/ingestion/`
→ Inherit from `BaseAPI`
→ Call from `scripts/refresh_data.py`

**Add new visualization:**
→ Create component in `src/visualization/`
→ Call from `app.py`

**Add new calculation/transformation:**
→ Create class in `src/transformation/`
→ Use from `scripts/` or during ETL

**Debug something:**
→ Check `logs/app.log`
→ Run with `--logger.level=debug`

**Understand architecture:**
→ Read `README.md`
→ Check `MANIFEST.md`
→ Look at docstrings in `src/`

---

## 📊 Directory Statistics

| Directory | Files | Purpose |
|-----------|-------|---------|
| Root | 7 | Main entry point + docs |
| src/ | 25+ | Core application code |
| scripts/ | 6 | Production utilities |
| config/ | 1-2 | Configuration |
| data/ | Variable | Local data storage |
| logs/ | 3+ | Application logs |
| archive/ | 1,038 | Old/test files (archived) |
| venv/ | 1000+ | Python environment |
| notebooks/ | 3+ | Jupyter notebooks |

---

## 🔑 Key Files

| File | Purpose | Type | Edit? |
|------|---------|------|-------|
| app.py | Main dashboard | Python | ✏️ Modify |
| README.md | Documentation | Markdown | ✏️ Update |
| config.py | Settings | Python | ⚠️ Careful |
| src/ | Application code | Python | ✏️ Modify |
| scripts/ | Utilities | Python | ⚠️ Test first |
| archive/ | Old code | Python | ❌ Reference only |
| venv/ | Dependencies | Virtual env | ⚠️ Don't modify |

---

## 🚀 Entry Points

**For Users:**
→ **`app.py`** - Streamlit dashboard (`streamlit run app.py`)

**For Developers:**
→ **`src/`** - Application code (modify here)
→ **`scripts/`** - Data operations (run these)
→ **`config/`** - Configuration (update settings)

**For Learning:**
→ **`README.md`** - Full documentation
→ **`archive/tests/`** - Example test patterns
→ **`docs/`** - Additional guides (if available)

---

## ✅ File Organization Rules

**KEEP in root:**
- Main entry point (app.py)
- Configuration (.env)
- Dependencies (requirements.txt)
- Primary documentation (README.md)
- Essential guides (QUICK_START.txt)

**ORGANIZE in folders:**
- Application code → `src/`
- Utilities → `scripts/`
- Data → `data/` or `data-lake/`
- Tests → `tests/`
- Configuration → `config/`
- Logs → `logs/`

**ARCHIVE:**
- Old code → `archive/`
- Test files → `archive/tests/`
- Deprecated docs → `archive/deprecated/`

---

## 📝 File Naming Conventions

```
✅ GOOD:
   app.py                  (main entry point)
   warehouse.py            (class name = file name)
   token_logger.py         (functionality clear)
   test_database.py        (test file clear)
   
❌ BAD:
   main.py / main_fixed.py (ambiguous)
   test1.py / check.py     (unclear purpose)
   utils.py                (too generic)
   script.py               (too generic)
```

---

## 🔄 Data Flow

```
📥 INGESTION
   ├─ Open-Meteo API (weather)
   ├─ OpenSky API (position)
   └─ Airlabs API (flights)
        ↓ (fetch_data from src/ingestion)
        
⚡ TRANSFORMATION
   ├─ Clean & validate
   ├─ Calculate disruptions (disruption_calculator.py)
   └─ Predict trajectories (trajectory_predictor.py)
        ↓ (transform_data)

💾 STORAGE
   ├─ PostgreSQL database
   ├─ Tables: lightning_strikes, flights, flight_disruptions
   └─ Data warehouse (DataWarehouse class)
        ↓ (query from database)

📊 VISUALIZATION
   ├─ Streamlit dashboard (app.py)
   ├─ Lightning map (Plotly)
   ├─ Timeline chart
   └─ Statistics panels
        ↓ (LightningDashboard class)

👁️ USER SEES
   ├─ Real-time lightning data
   ├─ Flight information
   └─ Disruption forecasts
```

---

## 🎓 Learning Path

1. **First:** Read `README.md` (10 min)
2. **Then:** Run `python scripts/setup_database.py` (1 min)
3. **Then:** Run `streamlit run app.py` (2 min)
4. **See:** Dashboard with demo data (1 min)
5. **Understand:** Read `MANIFEST.md` (5 min)
6. **Explore:** Look at `src/` folder structure (10 min)
7. **Code:** Modify something in `src/` (30 min)
8. **Extend:** Add new functionality (1+ hour)

---

## ⚠️ Important Notes

1. **Never modify files in `archive/`** - They're for reference only
2. **Always use virtual environment** - `venv` must be activated
3. **Keep `.env` safe** - Contains credentials (don't commit)
4. **Update `requirements.txt`** - When adding new packages
5. **Document changes** - Update README.md when needed
6. **Test before committing** - Run scripts to verify

---

## 🆘 Troubleshooting

**Project feels disorganized?**
→ You're probably looking in `archive/` - that's old code!
→ Focus on `src/` and `scripts/` instead

**Can't find a file?**
→ Check `MANIFEST.md` for cross-reference
→ Or check `archive/` if it's older code

**Confused about structure?**
→ Read `CLEANUP_REPORT.md` for organization details
→ Check this file for visual overview

**Something broken?**
→ Check `logs/app.log` for errors
→ Run `scripts/verify_data.py` to check data
→ Check your virtual environment

---

**Status:** ✅ ORGANIZED & PRODUCTION READY
**Last Updated:** April 3, 2026
**Version:** 2.0 (Post-cleanup organization)

