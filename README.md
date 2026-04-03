# Lightning & Flight Disruption Dashboard

Application Python de démonstration pour ingérer des données météo/vols, les stocker en base PostgreSQL, et les afficher dans un dashboard Streamlit.

## Ce que fait le projet

Le projet suit un flux simple:

1. Ingestion de données éclair et vol depuis les sources disponibles.
2. Transformation et normalisation des données.
3. Sauvegarde locale dans `data/`.
4. Chargement en base PostgreSQL.
5. Visualisation dans Streamlit.
6. Vérification des volumes et du schéma via scripts dédiés.

Le point d’entrée principal du dashboard est [app.py](app.py).

## Structure utile

- [app.py](app.py): point d’entrée Streamlit.
- [config/config.py](config/config.py): configuration de l’application et des variables d’environnement.
- [src/database/warehouse.py](src/database/warehouse.py): connexion PostgreSQL et requêtes de lecture/écriture.
- [src/ingestion/api_client.py](src/ingestion/api_client.py): clients d’ingestion API.
- [src/ingestion/web_scraper.py](src/ingestion/web_scraper.py): extraction par scraping.
- [src/storage/data_lake.py](src/storage/data_lake.py): stockage local et MinIO.
- [src/visualization/dashboard.py](src/visualization/dashboard.py): composants du dashboard.
- [final_verification.py](final_verification.py): vérification finale des volumes en base.
- [verify_data.py](verify_data.py): contrôle rapide des données chargées.

## Prérequis

- Python 3.14 ou compatible avec l’environnement local.
- PostgreSQL accessible sur `localhost:5433`.
- Un fichier `.env` à la racine du projet.

## Configuration `.env`

Créer un fichier `.env` à la racine avec au minimum:

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

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Démarrage avec Docker

```bash
docker compose up --build
```

La pile démarre alors:

- PostgreSQL sur `localhost:5433`
- MinIO sur `localhost:9000` et `localhost:9001`
- initialisation de la base via `db-init`
- chargement des données de démonstration via `demo-data`
- dashboard Streamlit sur `http://localhost:8505`

Le service `demo-data` alimente la base avec un jeu de démonstration contenant des éclairs, des vols et des perturbations.

## Lancer le programme

```bash
streamlit run app.py
```

Si le port `8501` est déjà utilisé:

```bash
streamlit run app.py --server.port 8506
```

Le dashboard est alors accessible sur:

- `http://localhost:8501`
- ou `http://localhost:8506` si tu utilises un port alternatif
- ou `http://localhost:8505` via Docker Compose

## Vérifier que tout fonctionne

```bash
python final_verification.py
python verify_data.py
```

Ces scripts vérifient les données présentes en base et les tables actuellement utilisées:

- `lightning_strikes`
- `flights`
- `flight_disruptions`

## Données et traitement

Le projet ne se contente pas d’afficher des données brutes. Le flux actuel inclut:

- ingestion,
- transformation,
- stockage local,
- chargement PostgreSQL,
- puis affichage dans Streamlit.

Le dashboard lit les données depuis PostgreSQL via [src/database/warehouse.py](src/database/warehouse.py).

## Remarques importantes

- Les scripts `final_verification.py` et `verify_data.py` ont été alignés sur le schéma réel de la base.
- La table de lecture utilisée pour les éclairs est `lightning_strikes`.
- Si tu veux repartir d’un environnement propre, conserve le `.env` mais supprime seulement les artefacts temporaires dans `data/` et `logs/`.

## Dépannage rapide

Si le dashboard ne démarre pas:

1. Vérifie que l’environnement virtuel est activé.
2. Vérifie que `streamlit` est installé.
3. Vérifie que PostgreSQL écoute bien sur `localhost:5433`.
4. Vérifie que le fichier `.env` contient `DB_PASSWORD`.
5. Essaie un autre port avec `--server.port 8506`.

Si la connexion à la base échoue, le plus fréquent est une mauvaise valeur de `DB_PASSWORD` dans `.env`.

## État attendu après exécution

Après un lancement correct, tu dois pouvoir:

- ouvrir le dashboard dans le navigateur,
- voir les données chargées depuis PostgreSQL,
- exécuter les scripts de vérification sans erreur,
- confirmer que le schéma contient bien les tables de production du projet.
