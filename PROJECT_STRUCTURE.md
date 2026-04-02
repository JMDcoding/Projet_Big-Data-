# Architecture Nettoyée - Data Lake Lightning

## 📁 Structure du Projet

```
Projet_Big-Data-/
├── app.py                          # Dashboard Streamlit
├── main.py                         # Pipeline ETL principal
├── demo.py                         # Démonstration des fonctionnalités
├── initialize_db.py                # Initialisation PostgreSQL
├── requirements.txt                # Dépendances Python
│
├── config/
│   └── config.py                   # Configuration centralisée
│
├── src/
│   ├── __init__.py
│   ├── database/                   # PostgreSQL operations
│   │   ├── __init__.py
│   │   └── warehouse.py            # Data warehouse queries
│   │
│   ├── ingestion/                  # Data sources
│   │   ├── __init__.py
│   │   ├── api_client.py           # Lightning & Flight APIs
│   │   ├── base.py                 # Base classes
│   │   └── web_scraper.py
│   │
│   ├── storage/                    # Data lake implementations
│   │   ├── __init__.py
│   │   └── data_lake.py            # JSON/CSV/MinIO storage
│   │
│   ├── transformation/             # ETL logic
│   │   ├── __init__.py
│   │   └── transformer.py          # Data normalization
│   │
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   └── logger.py               # Logging setup
│   │
│   └── visualization/              # Dashboard
│       ├── __init__.py
│       └── dashboard.py            # Streamlit components
│
├── data/                           # EMPTY - For MinIO staging only
│   ├── raw/                        # Temporary staging (git-ignored)
│   │   └── .gitkeep
│   └── processed/                  # Temporary output (git-ignored)
│       └── .gitkeep
│
├── notebooks/                      # Jupyter notebooks (no data)
│   └── eda_analysis.ipynb
│
├── logs/                           # Application logs (git-ignored)
│   └── .gitkeep
│
├── scripts/                        # Utility scripts
│   ├── start_minio.bat
│   └── start_minio.ps1
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md
│   ├── README_MINIO.md
│   ├── POSTGRESQL_SETUP.md
│   └── API_DATA_FREQUENCY.md
│
├── .gitignore                      # Excludes all data files
├── .git/                           # Version control
└── venv/                           # Virtual environment (git-ignored)
```

## 🗄️ Stratégie de Stockage des Données

### ❌ PAS DE DONNÉES LOCALES

Toutes les données sont stockées dans:

| Stockage | Rôle | Redondance | Accès |
|----------|------|-----------|-------|
| **MinIO** | Data Lake (archival, object storage) | ✅ S3-compatible backup | S3 API |
| **PostgreSQL** | Database (indexed, queryable) | ✅ Database backups | SQL queries |
| **Git** | Code & config uniquement | ✅ GitHub/backup | Version control |

### 📊 Flux de Données

```
API Data Sources
    ↓
[LocalDemoData, BlitzortungAPI, OpenSkyAPI, etc]
    ↓
Transformation (Pandas)
    ↓
┌─────────────────┐
│ MinIO (Primary) │ ← Files se sauvegardent ici automatiquement
└─────────────────┘
    ↓
PostgreSQL Database
(lightning_strikes, flights, flight_disruptions tables)
    ↓
Streamlit Dashboard
(Real-time visualization via queries)
```

## 🚀 Lancer le Système

### 1. Démarrer les services

```powershell
# Terminal 1: MinIO (Object Storage)
.\start_minio.ps1

# Terminal 2: PostgreSQL (Database)
# Déjà configuré - vérifie qu'il tourne sur port 5433

# Terminal 3: Pipeline ETL
python main.py

# Terminal 4: Dashboard
streamlit run app.py
```

### 2. Vérifier les services

```powershell
# MinIO Browser
http://localhost:9000

# PostgreSQL
psql -h localhost -p 5433 -U postgres -d lightning_db

# Dashboard Streamlit
http://localhost:8505
```

## 📋 Fichiers à NE PAS commiter

Tous les fichiers suivants sont **git-ignored** ✅:

```
✗ data/raw/*.json
✗ data/raw/*.csv  
✗ data/processed/*
✗ logs/*.log
✗ app.log
✗ .env
✗ *.db
✗ data/minio/*
```

## 🔧 Configuration

Toute la configuration est dans `config/config.py`:

```python
# Database
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "lightning_db"

# MinIO (Object Storage)
MINIO_HOST = "localhost:9000"
MINIO_BUCKET = "lightning-data"

# Paths (temporary staging only)
DATA_RAW_PATH = "./data/raw"
DATA_PROCESSED_PATH = "./data/processed"
```

## 📦 Pipeline de Données

### De A à Z:

1. **Ingestion** (main.run_ingestion)
   - Fetch data from APIs
   - LocalDemoData → 50 lightning strikes
   - OpenSkyAPI → 3000+ flights
   
2. **Transformation** (main.run_transformation)
   - Normalize schemas
   - Handle timestamps
   - Validate data quality

3. **Storage** (main.run_storage)
   - Save to MinIO (JSON) ← **PRIMARY**
   - Save to PostgreSQL (indexed)
   - Delete local temp files

4. **Visualization** (app.py - Streamlit)
   - Query PostgreSQL for real-time data
   - Display 50 lightning strikes
   - Display 3000+ flights
   - Show filters & timeline

## 🧑‍💻 Développement

### Ajouter une nouvelle source de données

1. Créer une classe dans `src/ingestion/api_client.py`:
   ```python
   class MyDataSource(DataSource):
       def extract(self):
           # Fetch data
           return {"data": [...]}
   ```

2. Ajouter au pipeline dans `main.py`:
   ```python
   self.data_sources["my_source"] = MyDataSource()
   ```

### Ajouter un nouveau stockage

1. Créer une classe dans `src/storage/data_lake.py`:
   ```python
   class MyStorage(DataLake):
       def save(self, data, filename):
           # Save to your system
   ```

2. Utiliser dans `main.run_storage()`:
   ```python
   self.my_storage.save(data, filename)
   ```

## 🔍 Troubleshooting

**Q: Pas de données dans le dashboard?**
- ✅ Vérifiez que MinIO et PostgreSQL tournent
- ✅ Lancez `python main.py` pour charger les données
- ✅ Vérifiez que PostgreSQL est accessible sur port 5433

**Q: MinIO dit "bucket does not exist"?**
- ✅ MinIO crée automatiquement le bucket à la première utilisation
- ✅ Vérifiez que minio.exe fonctionne

**Q: Données locales persistantes?**
- ✅ Videz `data/raw/` et `data/processed/`
- ✅ Redémarrez le pipeline

## 📚 Documentation

- [API Data Frequency](API_DATA_FREQUENCY.md)
- [PostgreSQL Setup](POSTGRESQL_SETUP.md)
- [MinIO Integration](README_MINIO.md)
- [Architecture Details](ARCHITECTURE.md)
- [Quick Start](QUICK_START.md)

---

**Dernière mise à jour**: 2026-04-01
**Status**: ✅ Nettoyé et organisé
