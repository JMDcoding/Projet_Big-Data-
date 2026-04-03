# ðŸ“ PROJECT STRUCTURE GUIDE

**Last Updated:** April 3, 2026 (Session 8 - Cleanup Complete)

## Visual Overview

```
ðŸ¢ Projet_Big-Data-/
â”‚
â”œâ”€â”€â”€ ðŸŽ¯ MAIN APPLICATION
â”‚    â”œâ”€ app.py .......................... Streamlit dashboard (START HERE â–¶ï¸)
â”‚    â”œâ”€ requirements.txt ............... Python dependencies
â”‚    â”œâ”€ .env ........................... Configuration variables
â”‚    â””â”€ .gitignore ..................... Git ignore rules
â”‚
â”œâ”€â”€â”€ ðŸ“š DOCUMENTATION (READ THESE)
â”‚    â”œâ”€ README.md ...................... Full guide & tutorial (350+ lines)
â”‚    â”œâ”€ QUICK_START.txt ................ 3-step setup (5 minutes)
â”‚    â”œâ”€ MANIFEST.md .................... File reference guide
â”‚    â”œâ”€ CLEANUP_REPORT.md .............. This cleanup summary
â”‚    â””â”€ PROJECT_REPORT.md .............. Project status & metrics
â”‚
â”œâ”€â”€â”€ âš™ï¸ CONFIGURATION
â”‚    â””â”€ config/
â”‚       â”œâ”€ config.py ................... Environment-based settings
â”‚       â”œâ”€ __init__.py
â”‚       â””â”€ (database config, API keys, etc.)
â”‚
â”œâ”€â”€â”€ ðŸ’¾ SOURCE CODE (POO Architecture)
â”‚    â””â”€ src/
â”‚       â”œâ”€ database/ ................... Data access layer
â”‚       â”‚  â”œâ”€ warehouse.py ............ DataWarehouse class
â”‚       â”‚  â”œâ”€ __init__.py
â”‚       â”‚  â””â”€ (connection management)
â”‚       â”‚
â”‚       â”œâ”€ ingestion/ .................. External API clients
â”‚       â”‚  â”œâ”€ base.py ................. BaseAPI class
â”‚       â”‚  â”œâ”€ api_client.py ........... HTTP client
â”‚       â”‚  â”œâ”€ alternative_apis.py ..... Alternative weather
â”‚       â”‚  â”œâ”€ blitzortung_websocket.py  Lightning websocket
â”‚       â”‚  â”œâ”€ storm_forecast.py ....... Storm prediction
â”‚       â”‚  â”œâ”€ web_scraper.py .......... HTML scraper
â”‚       â”‚  â”œâ”€ __init__.py
â”‚       â”‚  â””â”€ (API integrations)
â”‚       â”‚
â”‚       â”œâ”€ transformation/ ............. Business logic & ETL
â”‚       â”‚  â”œâ”€ transformer.py .......... Data transformation
â”‚       â”‚  â”œâ”€ disruption_calculator.py  Disruption calculations
â”‚       â”‚  â”œâ”€ trajectory_predictor.py .. Flight trajectory
â”‚       â”‚  â”œâ”€ __init__.py
â”‚       â”‚  â””â”€ (business logistics)
â”‚       â”‚
â”‚       â”œâ”€ utils/ ...................... Utilities & helpers
â”‚       â”‚  â”œâ”€ logger.py ............... setup_logging() â† IMPORTANT
â”‚       â”‚  â”œâ”€ helpers.py .............. Data helpers
â”‚       â”‚  â”œâ”€ refresh_service.py ...... Data refresh scheduling
â”‚       â”‚  â”œâ”€ constants.py ............ Application constants
â”‚       â”‚  â”œâ”€ __init__.py
â”‚       â”‚  â””â”€ (cross-cutting concerns)
â”‚       â”‚
â”‚       â”œâ”€ visualization/ .............. UI components
â”‚       â”‚  â”œâ”€ dashboard.py ............ LightningDashboard class
â”‚       â”‚  â”œâ”€ components.py ........... UI components
â”‚       â”‚  â”œâ”€ __init__.py
â”‚       â”‚  â””â”€ (Streamlit interface)
â”‚       â”‚
â”‚       â””â”€ __init__.py
â”‚
â”œâ”€â”€â”€ ðŸ”§ PRODUCTION SCRIPTS
â”‚    â””â”€ scripts/
â”‚       â”œâ”€ setup_database.py .......... Initialize database âœ…
â”‚       â”œâ”€ refresh_data.py ............ Fetch real data from APIs âœ…
â”‚       â”œâ”€ populate_demo.py ........... Load demo data for testing âœ…
â”‚       â”œâ”€ reset_data.py .............. Clear all data âœ…
â”‚       â”œâ”€ verify_data.py ............. Check data counts âœ…
â”‚       â”œâ”€ initialize_db.py ........... Database utility
â”‚       â”œâ”€ __init__.py
â”‚       â””â”€ (automation & utilities)
â”‚
â”œâ”€â”€â”€ ðŸ§ª UNIT TESTS
â”‚    â””â”€ tests/
â”‚       â”œâ”€ test_*.py .................. Pytest test files (when added)
â”‚       â”œâ”€ conftest.py ................ Shared fixtures (optional)
â”‚       â””â”€ (pytest directory structure)
â”‚
â”œâ”€â”€â”€ ðŸ’¾ DATA STORAGE
â”‚    â”œâ”€ data/ .......................... Local data
â”‚    â”‚  â”œâ”€ minio/ ..................... MinIO object storage
â”‚    â”‚  â””â”€ local/ ..................... Local files
â”‚    â”‚
â”‚    â””â”€ data-lake/ .................... Raw data lake
â”‚       â””â”€ (staging area for raw data)
â”‚
â”œâ”€â”€â”€ ðŸ“Š JUPYTER NOTEBOOKS
â”‚    â””â”€ notebooks/
â”‚       â”œâ”€ eda_analysis.ipynb ......... Data analysis notebook
â”‚       â”œâ”€ README_EDA.md .............. Notebook documentation
â”‚       â””â”€ NOTEBOOK_REPORT.md ......... Notebook report
â”‚
â”œâ”€â”€â”€ ðŸ“‹ APPLICATION LOGS
â”‚    â””â”€ logs/
â”‚       â”œâ”€ app.log .................... Main application log
â”‚       â”œâ”€ database.log ............... Database operations log
â”‚       â””â”€ refresh.log ................ Data refresh service log
â”‚
â”œâ”€â”€â”€ ðŸ“¦ ARCHIVED FILES (Not in use - see CLEANUP_REPORT.md)
â”‚    â””â”€ archive/
â”‚       â”œâ”€ tests/ ..................... 985+ legacy test files
â”‚       â”œâ”€ utilities/ ................. 18 old utility scripts
â”‚       â”œâ”€ setup-scripts/ ............. 13 .bat/.ps1 files
â”‚       â”œâ”€ deprecated/ ................ 14+ old code/documentation
â”‚       â”œâ”€ README.md .................. Archive guide
â”‚       â””â”€ (1,038 files total - for reference only)
â”‚
â””â”€â”€â”€ ðŸ PYTHON ENVIRONMENT
     â””â”€ venv/
        â”œâ”€ Scripts/ ................... Python executable & tools
        â”œâ”€ Lib/ ....................... Installed packages
        â”œâ”€ Include/ ................... Header files
        â”œâ”€ pyvenv.cfg ................. Environment configuration
        â””â”€ (virtual environment)
```

---

## ðŸŽ¯ Quick Navigation

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
python scripts/diagnostics/verify_data.py
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
â†’ Create class in `src/ingestion/`
â†’ Inherit from `BaseAPI`
â†’ Call from `scripts/refresh_data.py`

**Add new visualization:**
â†’ Create component in `src/visualization/`
â†’ Call from `app.py`

**Add new calculation/transformation:**
â†’ Create class in `src/transformation/`
â†’ Use from `scripts/` or during ETL

**Debug something:**
â†’ Check `logs/app.log`
â†’ Run with `--logger.level=debug`

**Understand architecture:**
â†’ Read `README.md`
â†’ Check `docs/MANIFEST.md`
â†’ Look at docstrings in `src/`

---

## ðŸ“Š Directory Statistics

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

## ðŸ”‘ Key Files

| File | Purpose | Type | Edit? |
|------|---------|------|-------|
| app.py | Main dashboard | Python | âœï¸ Modify |
| README.md | Documentation | Markdown | âœï¸ Update |
| config.py | Settings | Python | âš ï¸ Careful |
| src/ | Application code | Python | âœï¸ Modify |
| scripts/ | Utilities | Python | âš ï¸ Test first |
| archive/ | Old code | Python | âŒ Reference only |
| venv/ | Dependencies | Virtual env | âš ï¸ Don't modify |

---

## ðŸš€ Entry Points

**For Users:**
â†’ **`app.py`** - Streamlit dashboard (`streamlit run app.py`)

**For Developers:**
â†’ **`src/`** - Application code (modify here)
â†’ **`scripts/`** - Data operations (run these)
â†’ **`config/`** - Configuration (update settings)

**For Learning:**
â†’ **`README.md`** - Full documentation
â†’ **`archive/tests/`** - Example test patterns
â†’ **`docs/`** - Additional guides (if available)

---

## âœ… File Organization Rules

**KEEP in root:**
- Main entry point (app.py)
- Configuration (.env)
- Dependencies (requirements.txt)
- Primary documentation (README.md)
- Essential guides (QUICK_START.txt)

**ORGANIZE in folders:**
- Application code â†’ `src/`
- Utilities â†’ `scripts/`
- Data â†’ `data/` or `data-lake/`
- Tests â†’ `tests/`
- Configuration â†’ `config/`
- Logs â†’ `logs/`

**ARCHIVE:**
- Old code â†’ `archive/`
- Test files â†’ `archive/tests/`
- Deprecated docs â†’ `archive/deprecated/`

---

## ðŸ“ File Naming Conventions

```
âœ… GOOD:
   app.py                  (main entry point)
   warehouse.py            (class name = file name)
   token_logger.py         (functionality clear)
   test_database.py        (test file clear)
   
âŒ BAD:
   main.py / main_fixed.py (ambiguous)
   test1.py / check.py     (unclear purpose)
   utils.py                (too generic)
   script.py               (too generic)
```

---

## ðŸ”„ Data Flow

```
ðŸ“¥ INGESTION
   â”œâ”€ Open-Meteo API (weather)
   â”œâ”€ OpenSky API (position)
   â””â”€ Airlabs API (flights)
        â†“ (fetch_data from src/ingestion)
        
âš¡ TRANSFORMATION
   â”œâ”€ Clean & validate
   â”œâ”€ Calculate disruptions (disruption_calculator.py)
   â””â”€ Predict trajectories (trajectory_predictor.py)
        â†“ (transform_data)

ðŸ’¾ STORAGE
   â”œâ”€ PostgreSQL database
   â”œâ”€ Tables: lightning_strikes, flights, flight_disruptions
   â””â”€ Data warehouse (DataWarehouse class)
        â†“ (query from database)

ðŸ“Š VISUALIZATION
   â”œâ”€ Streamlit dashboard (app.py)
   â”œâ”€ Lightning map (Plotly)
   â”œâ”€ Timeline chart
   â””â”€ Statistics panels
        â†“ (LightningDashboard class)

ðŸ‘ï¸ USER SEES
   â”œâ”€ Real-time lightning data
   â”œâ”€ Flight information
   â””â”€ Disruption forecasts
```

---

## ðŸŽ“ Learning Path

1. **First:** Read `README.md` (10 min)
2. **Then:** Run `python scripts/setup_database.py` (1 min)
3. **Then:** Run `streamlit run app.py` (2 min)
4. **See:** Dashboard with demo data (1 min)
5. **Understand:** Read `docs/MANIFEST.md` (5 min)
6. **Explore:** Look at `src/` folder structure (10 min)
7. **Code:** Modify something in `src/` (30 min)
8. **Extend:** Add new functionality (1+ hour)

---

## âš ï¸ Important Notes

1. **Never modify files in `archive/`** - They're for reference only
2. **Always use virtual environment** - `venv` must be activated
3. **Keep `.env` safe** - Contains credentials (don't commit)
4. **Update `requirements.txt`** - When adding new packages
5. **Document changes** - Update README.md when needed
6. **Test before committing** - Run scripts to verify

---

## ðŸ†˜ Troubleshooting

**Project feels disorganized?**
â†’ You're probably looking in `archive/` - that's old code!
â†’ Focus on `src/` and `scripts/` instead

**Can't find a file?**
â†’ Check `docs/MANIFEST.md` for cross-reference
â†’ Or check `archive/` if it's older code

**Confused about structure?**
â†’ Read `docs/CLEANUP_REPORT.md` for organization details
â†’ Check this file for visual overview

**Something broken?**
â†’ Check `logs/app.log` for errors
â†’ Run `scripts/verify_data.py` to check data
â†’ Check your virtual environment

---

**Status:** âœ… ORGANIZED & PRODUCTION READY
**Last Updated:** April 3, 2026
**Version:** 2.0 (Post-cleanup organization)



