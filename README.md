# ⚡ Lightning & Flight Disruption Dashboard

**Moniteur en temps réel des éclairs et des perturbations de vol**

Un dashboard Streamlit pour analyser les données d'éclairs et calculer les perturbations potentielles de vols basées sur leur proximité spatiale et temporelle.

---

## 🚀 Démarrage Rapide (5 minutes)

### 1. Cloner le projet

```bash
git clone <repository-url>
cd Projet_Big-Data-
```

### 2. Installer PostgreSQL et créer la base

```bash
# Windows
# Télécharger et installer PostgreSQL 18:
# https://www.postgresql.org/download/windows/

# Après installation, créer la base de données:
psql -U postgres -c "CREATE DATABASE lightning_db;"
```

### 3. Setup Python et dépendances

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'env
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Initialiser la base de données

```bash
python scripts/setup_database.py
```

### 5. Charger les données

```bash
# Option A: Données de test (recommandé pour démarrage)
python scripts/populate_demo.py

# Option B: Données réelles depuis API
python scripts/refresh_data.py
```

### 6. Lancer le dashboard

```bash
streamlit run app.py
```

**➡️ Dashboard disponible à:** http://localhost:8501

---

## 📊 Architecture du Projet

```
Projet_Big-Data-/
├── README.md                 # Ce fichier (tutoriel complet)
├── requirements.txt          # Dépendances Python
├── app.py                    # Streamlit app (point d'entrée)
│
├── config/                   # Configuration
│   ├── __init__.py
│   └── config.py            # Variables d'env, DB, logging
│
├── src/                      # Code source principal (POO)
│   ├── __init__.py
│   ├── database/            # Couche base de données
│   │   ├── __init__.py
│   │   └── warehouse.py     # DataWarehouse, connexions
│   │
│   ├── ingestion/           # APIs et ingestion de données
│   │   ├── __init__.py
│   │   ├── base.py          # Classe abstraite API
│   │   ├── api_client.py    # Client HTTP générique
│   │   ├── alternative_apis.py
│   │   ├── storm_forecast.py
│   │   └── web_scraper.py
│   │
│   ├── transformation/      # Transformation et calculs
│   │   ├── __init__.py
│   │   ├── transformer.py   # ETL de base
│   │   ├── disruption_calculator.py
│   │   └── trajectory_predictor.py
│   │
│   ├── storage/             # Stockage (MinIO, etc.)
│   │   ├── __init__.py
│   │   └── data_lake.py
│   │
│   ├── utils/               # Utilitaires
│   │   ├── __init__.py
│   │   ├── logger.py        # Logging
│   │   ├── helpers.py       # Fonctions utilitaires
│   │   └── refresh_service.py
│   │
│   └── visualization/       # Dashboard Streamlit
│       ├── __init__.py
│       ├── dashboard.py     # Classe LightningDashboard
│       └── risk_zones.py    # Zones de risque
│
├── scripts/                 # Scripts utilitaires
│   ├── __init__.py
│   ├── setup_database.py   # Initialisation DB
│   ├── refresh_data.py     # Orchestration refresh
│   ├── fetch_lightning.py  # Fetch éclairs
│   ├── fetch_flights.py    # Fetch vols
│   ├── populate_demo.py    # Données de test
│   └── reset_data.py       # Nettoyage
│
├── tests/                   # Tests unitaires
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_apis.py
│   └── test_disruptions.py
│
├── notebooks/              # Jupyter notebooks
│   └── eda_analysis.ipynb  # Exploration de données
│
├── data/                   # Données locales
└── logs/                   # Fichiers de log
```

---

## 🔧 Configuration

### Variables d'environnement (`.env`)

Créez un fichier `.env` à la racine:

```env
# PostgreSQL
DB_HOST=localhost
DB_PORT=5433
DB_NAME=lightning_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe

# APIs (optionnels)
AIRLABS_API_KEY=votre_clé_airlabs
OPENSKY_USERNAME=votre_username
OPENSKY_PASSWORD=votre_password

# MinIO (optionnel)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Configuration Python (`config/config.py`)

- Tous les paramètres DB
- Chemins des fichiers
- Paramètres logging
- Configuration des APIs

---

## 📈 Utilisation

### Dashboard Principal

**URL:** http://localhost:8501

#### Onglets disponibles:

1. **📍 Lightning Map** - Carte des éclairs en Europe
2. **✈️ Flights** - Tableau des vols chargés
3. **🚨 Disruptions** - Analyses des perturbations

#### Contrôles Sidebar:

- **🔄 Refresh** - Recharger les données depuis DB
- **Sliders** - Filtrer par intensité d'éclair
- **Date Picker** - Sélectionner plage de dates
- **Timeline** - Vue hourly/daily des éclairs

### Scripts Utilitaires

#### Charger les données (recommandé d'abord):

```bash
# Données de test (13 records d'éclairs)
python scripts/populate_demo.py

# OU données réelles (Open-Meteo + Airlabs)
python scripts/refresh_data.py
```

#### Réinitialiser complètement:

```bash
# Supprimer tous les enregistrements
python scripts/reset_data.py

# Recréer les tables
python scripts/setup_database.py

# Recharger
python scripts/populate_demo.py
```

#### Vérifier l'état:

```bash
# Vérifier les données
python scripts/verify_data.py
```

---

## 🌩️ Données & APIs

### Sources de Données

| Source | Type | API | Clé Requise |
|--------|------|-----|-------------|
| **Open-Meteo** | Météo/Tempêtes | Forecast (7j) | ❌ Non |
| **Airlabs** | Données de vols | Historique complet | ✅ Oui (gratuit) |
| **OpenSky Network** | Positions vols | Tracking ADS-B | ❌ Non |

### Schéma de Données

#### `lightning_strikes`
```sql
- lightning_id (PK): VARCHAR(255)
- latitude: DECIMAL(10,8)
- longitude: DECIMAL(11,8)
- intensity: DECIMAL(5,2)          -- 0-100
- timestamp: TIMESTAMP
- source: VARCHAR(100)             -- Open-Meteo, Demo, etc.
```

#### `flights`
```sql
- id (PK): INTEGER (auto-increment)
- flight_number: VARCHAR(20)
- departure: VARCHAR(4)             -- IATA code
- arrival: VARCHAR(4)               -- IATA code
- departure_time: TIMESTAMP         -- RÉEL depuis API
- arrival_time: TIMESTAMP           -- RÉEL depuis API
- source: VARCHAR(100)              -- Airlabs, OpenSky, etc.
```

#### `flight_disruptions`
```sql
- id (PK): INTEGER
- flight_id: VARCHAR(255) (FK)
- lightning_id: VARCHAR(255) (FK)
- distance_km: FLOAT
- risk_level: VARCHAR(50)           -- LOW, MEDIUM, HIGH
- disruption_probability: FLOAT     -- 0-1
```

---

## 🔌 API Integration

### Ajouter une nouvelle source de données

1. Créer une classe API dans `src/ingestion/`:

```python
from src.ingestion.base import BaseAPI

class MonAPI(BaseAPI):
    """Nouvelle API source."""
    
    def __init__(self, api_key=None):
        super().__init__("MonAPI", api_key)
    
    def fetch_data(self, params):
        """Fetch depuis API."""
        # Implémentation
        pass
    
    def transform_data(self, raw_data):
        """Transformer au format standardisé."""
        # Implémentation
        pass
```

2. Intégrer dans scripts:

```python
# scripts/fetch_my_data.py
from src.ingestion.mon_api import MonAPI

api = MonAPI(api_key="key")
data = api.fetch_data(params)
transformed = api.transform_data(data)
warehouse.insert_lightning_data(transformed)
```

---

## 🧪 Tests

Exécuter les tests:

```bash
# Tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_database.py -v
pytest tests/test_apis.py -v
```

---

## 🐛 Troubleshooting

### Erreur: "ERREUR: la relation 'flight_disruptions' n'existe pas"

**Solution:**
```bash
python scripts/setup_database.py
```

### Erreur: "could not connect to PostgreSQL"

**Vérifier:**
1. PostgreSQL s'exécute: `services.msc`
2. Port correct (5433): Check `postgresql.conf`
3. Credentials dans `.env` correctes
4. Database existe: `psql -U postgres -l`

### Pas de données affichées

**Options:**
```bash
# 1. Charger données test
python scripts/populate_demo.py

# 2. Vérifier données en DB
python scripts/verify_data.py

# 3. Recharger données réelles
python scripts/refresh_data.py
```

### Dashboard affiche "no data" après refresh

**Solution:**
1. Cliquer le bouton "🔄 Refresh" du dashboard
2. Aller sur onglet "✈️ Flights" et vérifier
3. Si toujours vide: `python scripts/populate_demo.py`

---

## 📚 Documentation Supplémentaire

### Structure POO

Le projet utilise une architecture orientée objet:

- **BaseAPI**: Classe abstraite pour toutes les APIs
- **DataWarehouse**: Couche d'accès base de données
- **LightningDashboard**: Dashboard avec méthodes de rendu
- **DisruptionCalculator**: Logique de calcul des perturbations

### Patterns Utilisés

- **Factory Pattern**: Création d'instances API
- **Singleton Pattern**: Configuration, Logger
- **Observer Pattern**: Refresh service (optionnel)
- **MVC Pattern**: Streamlit + Models + Views

---

## 🚀 Déploiement

### Local (Development)
```bash
streamlit run app.py
```

### Production (Recommandé)

```bash
# Utiliser Streamlit Cloud ou Docker
streamlit run app.py --server.port 8080
```

### Docker

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

Lancer:
```bash
docker build -t dashboard .
docker run -p 8501:8501 dashboard
```

---

## 🤝 Contribution

Pour contribuer au projet:

1. Fork le repository
2. Créer une branche: `git checkout -b feature/ma-feature`
3. Commit: `git commit -am 'Ajouter feature'`
4. Push: `git push origin feature/ma-feature`
5. Créer une PR

### Code Style

- Utiliser `black` pour le formatage
- Respecter PEP8
- Ajouter docstrings pour toutes les classes/fonctions
- Ajouter des tests pour les nouvelles features

---

## 📝 Licensing

Projet d'étude - Utilisation libre

---

## 🙋 Support

**Questions?** 
- Consulter la section Troubleshooting
- Vérifier les logs: `logs/app.log`
- Examiner les tests: `tests/`

**Problèmes?**
- Recréer la base: `python scripts/setup_database.py`
- Recharger les données: `python scripts/populate_demo.py`
- Redémarrer l'app: `Ctrl+C` + `streamlit run app.py`

---

## 📊 Métriques & Monitoring

Le dashboard affiche automatiquement:

- **Total Lightning Strikes**: Nombre total d'éclairs
- **Total Flights**: Nombre de vols chargés
- **At-Risk Flights**: Vols à risque (probabilité > 50%)
- **Avg Strike Intensity**: Intensité moyenne des éclairs

---

## 🔄 Auto-Refresh (Optionnel)

Pour activer le refresh automatique toutes les 5 minutes:

```bash
python -m src.utils.refresh_service
```

(Nécessite MinIO ou S3 pour stockage distribuable)

---

**Dernier update:** Avril 2026
**Version:** 2.0 - POO & Stable Release
