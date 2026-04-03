# Lightning & Flight Disruption Dashboard

Application Python de démonstration pour ingérer des données météo/vols, les stocker en base PostgreSQL et les afficher dans un dashboard Streamlit.

## Fonctionnement général

Le flux principal est le suivant:

1. Ingestion des données (API/scraping + données de démo).
2. Transformation/normalisation.
3. Stockage local et/ou MinIO selon le mode d’exécution.
4. Chargement PostgreSQL.
5. Visualisation dans le dashboard Streamlit.

Point d’entrée interface: [app.py](app.py)

## Arborescence ordonnée

```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── config/
├── src/
├── scripts/
│   ├── diagnostics/
│   ├── sql/
│   └── shell/
├── docs/
├── notebooks/
├── data/
├── logs/
└── archive/
```

## Où sont les fichiers importants

- Application:
	- [app.py](app.py)
	- [src/visualization/dashboard.py](src/visualization/dashboard.py)
	- [src/database/warehouse.py](src/database/warehouse.py)
- Configuration:
	- [config/config.py](config/config.py)
- Docker:
	- [Dockerfile](Dockerfile)
	- [docker-compose.yml](docker-compose.yml)
- Scripts métier:
	- [scripts/setup_database.py](scripts/setup_database.py)
	- [scripts/generate_demo_data_final.py](scripts/generate_demo_data_final.py)
- Scripts de vérification et diagnostic:
	- [scripts/diagnostics/final_verification.py](scripts/diagnostics/final_verification.py)
	- [scripts/diagnostics/verify_data.py](scripts/diagnostics/verify_data.py)
	- [scripts/diagnostics/check_schema.py](scripts/diagnostics/check_schema.py)
- Scripts SQL utilitaires:
	- [scripts/sql/cleanup.sql](scripts/sql/cleanup.sql)
	- [scripts/sql/cleanup_complete.sql](scripts/sql/cleanup_complete.sql)
	- [scripts/sql/recreate_flight_disruptions.sql](scripts/sql/recreate_flight_disruptions.sql)
- Documentation complémentaire:
	- [docs/QUICK_START.txt](docs/QUICK_START.txt)
	- [docs/STRUCTURE.md](docs/STRUCTURE.md)
	- [docs/MANIFEST.md](docs/MANIFEST.md)
	- [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)

## Prérequis

- Python 3.14 (ou compatible environnement local)
- Docker Desktop
- (Mode local sans Docker) PostgreSQL disponible

## Configuration `.env`

Créer un fichier `.env` à la racine:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=lightning_db
DB_USER=postgres
DB_PASSWORD=postgres
MINIO_HOST=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=lightning-data
MINIO_USE_SSL=false
LOG_LEVEL=INFO
```

## Lancement recommandé (Docker)

```bash
docker compose up --build
```

Services démarrés:

- Dashboard: http://localhost:8505
- PostgreSQL: localhost:5433
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

Le compose exécute aussi:

- `db-init` pour créer/initialiser les tables
- `demo-data` pour injecter un jeu de démonstration

## Lancement local (hors Docker)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Si port occupé:

```bash
streamlit run app.py --server.port 8506
```

## Vérifications de fonctionnement

```bash
python scripts/diagnostics/final_verification.py
python scripts/diagnostics/verify_data.py
```

## Dernières modifications

1. Rangement des fichiers racine:
	 - déplacement des scripts de diagnostic vers [scripts/diagnostics](scripts/diagnostics)
	 - déplacement des scripts SQL vers [scripts/sql](scripts/sql)
	 - déplacement des scripts shell vers [scripts/shell](scripts/shell)
	 - déplacement des rapports/documentation vers [docs](docs)
2. Documentation README alignée sur la nouvelle arborescence et les nouvelles commandes.
3. Docker opérationnel avec démarrage complet dashboard + base + data de démonstration.
4. Requête de lecture Lightning alignée sur la table `lightning_strikes` dans [src/database/warehouse.py](src/database/warehouse.py).

## Dépannage rapide

1. Dashboard ne démarre pas:
	 - vérifier que le port 8505 est libre
	 - sinon utiliser 8506 en local
2. Erreur DB:
	 - vérifier `DB_PASSWORD` dans `.env`
	 - vérifier que PostgreSQL écoute sur le bon port
3. Données absentes:
	 - relancer `docker compose up --build`
	 - exécuter les scripts de vérification dans [scripts/diagnostics](scripts/diagnostics)
