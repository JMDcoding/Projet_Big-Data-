# 🚀 Démarrage Rapide - Projet Big Data

## ✅ Votre Projet est Prêt !

Vous avez maintenant une structure complète et professionnelle pour votre pipeline de données. Voici comment commencer :

---

## 📋 Étape 1 : Vérifier la Structure du Projet

```
Projet_Big-Data-/
├── src/                      # Code source (POO)
│   ├── ingestion/           # Récupération données (API + scraping)
│   ├── storage/             # Data Lake (JSON/CSV)
│   ├── transformation/      # Nettoyage et transformation
│   ├── database/            # PostgreSQL Data Warehouse
│   ├── visualization/       # Dashboard Streamlit
│   └── utils/               # Utilitaires et logging
├── config/                  # Configuration (.env)
├── data/                    # Données brutes et traitées
├── logs/                    # Fichiers journaux
├── main.py                  # Script principal du pipeline
├── app.py                   # Application dashboard
├── requirements.txt         # Dépendances Python
└── README.md               # Documentation complète
```

---

## 🔧 Étape 2 : Configurer PostgreSQL (Optionnel pour tests)

### Installation PostgreSQL
1. Téléchargez depuis https://www.postgresql.org/download/windows/
2. Installez avec le mot de passe par défaut

### Créer la base de données
```bash
# Line de commande (Windows)
createdb lightning_db
```

### Configurer les credentials
```bash
# Éditez config/.env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lightning_db
DB_USER=postgres
DB_PASSWORD=votre_mot_de_passe
```

---

## 🎯 Étape 3 : Installer les Dépendances Manquantes (PostgreSQL)

Si vous allez utiliser PostgreSQL :

```bash
# Activez l'environnement
venv\Scripts\activate

# Installez le driver PostgreSQL
pip install psycopg2-binary

# Ou via conda (plus facile sur Windows)
conda install psycopg2
```

---

## ▶️ Étape 4 : Exécuter le Pipeline

### Option A : Pipeline complet (Ingestion → Transformation → Chargement)
```bash
# Activez l'environnement
venv\Scripts\activate

# Exécutez le pipeline
python main.py
```

### Option B : Dashboard Streamlit
```bash
# Activez l'environnement
venv\Scripts\activate

# Lancez le dashboard
streamlit run app.py

# Accédez à http://localhost:8501
```

### Option C : Tests d'architecture
```bash
venv\Scripts\activate
python test_architecture.py
```

---

## 📌 Architecture POO Implémentée

### **Ingestion (Collecte de données)**
```python
from src.ingestion import BlitzortungAPI, WebScraper

# Récupérer les éclairs en temps réel
api = BlitzortungAPI()
data = api.extract()

# Scraper les données de vols
scraper = AirlineFlightScraper(url)
flights = scraper.extract()
```

### **Stockage (Data Lake)**
```python
from src.storage import JSONDataLake, CSVDataLake

# Sauvegarder structure brutes
json_lake = JSONDataLake("./data/raw")
json_lake.save(data, "lightning_strikes")

# Exporter en CSV
csv_lake = CSVDataLake("./data/raw")
csv_lake.save(data, "flights")
```

### **Transformation**
```python
from src.transformation import LightningDataTransformer, DataMerger

# Transformer les données
transformer = LightningDataTransformer()
df_clean = transformer.transform(raw_data)

# Fusionner plusieurs sources
merger = DataMerger()
df_combined = merger.transform({"lightning": df1, "flights": df2})
```

### **Base de Données**
```python
from src.database import PostgreSQLConnection, DataWarehouse

# Connexion
db = PostgreSQLConnection(host, port, database, user, password)
db.connect()

# Data Warehouse
warehouse = DataWarehouse(db)
warehouse.create_lightning_table()
warehouse.insert_lightning_data(data)
```

### **Dashboard**
```python
from src.visualization import LightningDashboard

dashboard = LightningDashboard()
dashboard.run(lightning_data=df, flights_data=df2)
```

---

## 🧪 Tester le Projet

```bash
# Test complet de l'architecture
python test_architecture.py

# Sortie attendue :
# ✅ ALL TESTS PASSED!
```

---

## 🔍 Analyser les Disruptions Aériennes

```python
from src.utils import assess_disruption_risk

# Évaluer le risque
risk = assess_disruption_risk(
    distance_km=50,        # Distance éclair-trajectoire
    time_diff_minutes=15,  # Écart temps
    intensity=75           # Intensité éclair
)

# Résultat :
# {
#   'risk_level': 'High',
#   'disruption_probability': 0.75,
#   'distance_km': 50,
#   'time_diff_minutes': 15
# }
```

---

## 📊 Exemple d'Utilisation Complet

```python
#!/usr/bin/env python
"""Exemple : Pipeline complet"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import get_config
from src.ingestion import BlitzortungAPI
from src.storage import JSONDataLake
from src.transformation import LightningDataTransformer
from src.utils import logger

# Configuration
config = get_config()

# 1️⃣ INGESTION - Récupérer les données
api = BlitzortungAPI(
    base_url=config.API_BASE_URL,
    timeout=config.API_TIMEOUT
)
raw_data = api.extract()
logger.info(f"Ingéré {len(raw_data)} éclairs")

# 2️⃣ STOCKAGE - Sauvegarder en Data Lake
data_lake = JSONDataLake(config.DATA_RAW_PATH)
filepath = data_lake.save(raw_data, "lightning_raw")
logger.info(f"Sauvegardé à {filepath}")

# 3️⃣ TRANSFORMATION - Nettoyer et structurer
transformer = LightningDataTransformer()
df_clean = transformer.transform(raw_data)
logger.info(f"Transformé {len(df_clean)} enregistrements")

# 4️⃣ VISUALISATION
print("✅ Pipeline complet exécuté !")
print(f"📊 {len(df_clean)} éclairs traités")
print(f"📁 Données sauvegardées")
```

---

## 🐛 Dépannage

### Erreur : `ModuleNotFoundError: No module named 'psycopg2'`
→ PostgreSQL n'est pas nécessaire pour les tests. Installez si vous voulez l'utiliser :
```bash
pip install psycopg2-binary
```

### Erreur : `No module named 'streamlit'`
→ Streamlit est installé. Assurez-vous que l'environnement est activé :
```bash
venv\Scripts\activate
```

### Erreur : `ModuleNotFoundError: No module named 'src'`
→ Assurez-vous d'exécuter les scripts depuis le répertoire racine du projet.

---

## 📚 Documentation Complète

Consultez [README.md](README.md) pour :
- Architecture détaillée
- Classes et modules
- Schéma de base de données
- Configuration avancée
- Meilleurs pratiques

---

## 🎓 Prochaines Étapes

### Phase 1 : Base (✅ Complétée)
- ✅ Structure POO
- ✅ Ingestion API
- ✅ Data Lake
- ✅ Transformation
- ✅ Utils et logging

### Phase 2 : Production
- ⚙️ Implémenter le scraping réel des vols
- ⚙️ Connecter PostgreSQL
- ⚙️ Test des données réelles Blitzortung
- ⚙️ Affiner l'analyse de risque
- ⚙️ Optimiser les performances

### Phase 3 : Soutenance
- 📊 Finiser le dashboardInteractif
- 📈 Ajouter des graphiques avancés
- 📋 Documenter les résultats
- 🎤 Préparer la présentation

---

## 📞 Besoin d'Aide ?

Consultez les docstrings des classes :
```python
from src.ingestion import BlitzortungAPI
help(BlitzortungAPI)
```

Ou vérifiez les logs :
```bash
tail -f logs/app.log
```

---

**Votre pipeline est prêt à l'emploi ! 🎉**  
Commencez par exécuter `python main.py` ou `streamlit run app.py`
