# Quick Start - Auto Refresh Service

## Démarrer le Dashboard avec Refresh Automatique

### Option 1: Dashboard avec Refresh Intégré (Recommandé)
```bash
streamlit run app.py
```
✅ Le service de refresh démarre automatiquement en arrière-plan  
✅ Vous verrez "Auto-Refresh Status" dans la barre latérale  
✅ Les données se mettent à jour toutes les 20 min (éclairs) / 2h (vols)

### Option 2: Service de Refresh Autonome

**Windows CMD:**
```batch
start_refresh_service.bat
```

**Windows PowerShell:**
```powershell
.\start_refresh_service.ps1
```

**Linux/Mac:**
```bash
python refresh_service_standalone.py
```

Puis lancez le dashboard dans un autre terminal:
```bash
streamlit run app.py
```

## Calendrier de Mise à Jour

| Donnée | Fréquence | Raison |
|--------|-----------|--------|
| ⚡ Éclairs | Tous les **20 min** | Haute priorité, situation change vite |
| ✈️ Vols | Toutes les **2 heures** | Moins critique, changement plus lent |

## Où Voir les Mises à Jour

1. **Dashboard Streamlit**
   - Sidebar: "Auto-Refresh Status" avec timestamps
   - Tab "Lightning Map": mise à jour avec nouvelles données
   - Tab "Flights": nouvelle liste des vols

2. **Logs**
   - `logs/lightning_pipeline.log`
   - Recherchez: "Lightning refresh completed"
   - Exemple: `INFO - Lightning refresh completed: 52 records loaded in 3.2s`

3. **Base de Données PostgreSQL**
   - Table `lightning_strikes`: nouveaux enregistrements
   - Table `flights`: nouveaux enregistrements

## Vérifier que ça Marche

```python
# Test depuis Python
python -c "
from src.database import PostgreSQLConnection, DataWarehouse
from config.config import get_config
import pandas as pd

config = get_config()
db = PostgreSQLConnection(host=config.DB_HOST, port=config.DB_PORT, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASSWORD)
db.connect()
wh = DataWarehouse(db)

lightning = wh.query_lightning_data()
flights = wh.query_flights_data()

print(f'Éclairs: {len(lightning)} | Vols: {len(flights)}')
db.disconnect()
"
```

## Personnaliser les Intervalles

Pour changer la fréquence de mise à jour, éditez:
**`src/utils/refresh_service.py`**

```python
# Ligne ~75: Lightning refresh
IntervalTrigger(minutes=20),  # Changer 20 à votre valeur

# Ligne ~85: Flights refresh  
IntervalTrigger(hours=2),     # Changer 2 à votre valeur
```

Puis redémarrez le service.

## Quelques Cas d'Usage

- **Monitoring Temps Réel**: Observez la carte des éclairs et les vols affectés
- **Alertes**: Créez des alertes basées sur les mises à jour
- **Analyse**: Comparez les données avant/après les rafraîchissements
- **Intégration**: Le service push les données à MinIO pour l'archivage

## Dépannage

**Q: Le service ne démarre pas**
- Vérifiez que PostgreSQL tourne (port 5433)
- Vérifiez les identifiants DB dans `config/config.py`

**Q: Les données ne se mettent pas à jour**
- Regardez dans `logs/lightning_pipeline.log`
- Vérifiez la connectivité à l'API (OpenSky, etc.)

**Q: Ça consomme trop ressources**
- Augmentez les intervalles (20→60 min pour éclairs, 2→4 heures pour vols)

## Structure des Fichiers

```
├── app.py                              # Dashboard (démarre le service)
├── refresh_service_standalone.py      # Service régulière
├── start_refresh_service.bat           # Lanceur Windows CMD
├── start_refresh_service.ps1           # Lanceur Windows PowerShell
├── src/utils/refresh_service.py       # Service principal
└── README_REFRESH_SERVICE.md          # Documentation complète
```

## Prochaines Étapes

1. ✅ Lancez le dashboard: `streamlit run app.py`
2. ✅ Observez les mises à jour dans la sidebar
3. ✅ Attendez 20 minutes pour voir les nouvelles données
4. 📊 Créez des visualisations basées sur les tendances
5. 🚨 Configurer des alertes pour les situations à risque
