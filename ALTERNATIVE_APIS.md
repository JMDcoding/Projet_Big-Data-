# APIs Alternatives - Données d'Éclairs et Vols

## Vue d'ensemble

Si vous rencontrez des problèmes avec les APIs actuelles, voici des alternatives éprouvées pour récupérer les données.

## ⚡ APIs pour les ÉCLAIRS

### 1. **Blitzortung API** (Actuel)
- **Type**: HTTP REST + WebSocket
- **Couverture**: Mondial
- **Données**: Localisation, intensité, timestamps
- **Gratuit**: Oui
- **Fiabilité**: ⭐⭐⭐⭐⭐ (Excellente)
- **Latence**: Temps réel (WebSocket)
- **Problèmes connus**: Nécessite parfois de l'authentification
- **Solution**: Utiliser WebSocket au lieu du HTTP

### 2. **OpenMeteo API** (Actuel)
- **Type**: HTTP REST
- **Couverture**: Mondial
- **Données**: Historique foudre, météo
- **Gratuit**: Oui (illimité)
- **Fiabilité**: ⭐⭐⭐⭐ (Très bonne)
- **Latence**: 5-30 secondes
- **Problèmes connus**: Données historiques seulement, pas en temps réel
- **Alternative si besoin**: Utiliser WeatherAPI ou OpenWeather

### 3. **WeatherAPI** (Alternative)
- **Type**: HTTP REST
- **Couverture**: Mondial
- **Données**: Conditions météo, alertes orages
- **Gratuit**: 1M appels/mois
- **Fiabilité**: ⭐⭐⭐⭐ (Très bonne)
- **Latence**: 2-5 secondes
- **Avantages**: Pas de limite quota libre, facile à utiliser
- **Setup**: 
  ```python
  api = WeatherAPILightning(api_key="free", lat=48.8, lon=2.3)
  data = api.fetch()
  ```

### 4. **OpenWeather API** (Alternative)
- **Type**: HTTP REST
- **Couverture**: Mondial
- **Données**: Alertes météo incluant foudre
- **Gratuit**: 60 appels/min
- **Fiabilité**: ⭐⭐⭐⭐⭐ (Excellente)
- **Latence**: 1-3 secondes
- **Avantages**: Très fiable, couverture complète
- **Setup**:
  ```python
  api = OpenWeatherLightning(api_key="votre_clé", lat=48.8, lon=2.3)
  data = api.fetch()
  ```
- **Note**: Nécessite une clé API gratuite de https://openweathermap.org

## ✈️ APIs pour les VOLS

### 1. **AviationStack** (Actuel)
- **Type**: HTTP REST
- **Couverture**: Mondial
- **Données**: Route complète, horaires, statut
- **Gratuit**: 100 req/mois
- **Fiabilité**: ⭐⭐⭐⭐ (Très bonne)
- **Latence**: 5-10 secondes
- **Problèmes**: Quota limité (100/mois)
- **Solution**: Combiner avec ADS-B Exchange

### 2. **ADS-B Exchange** (Alternative - Recommandée)
- **Type**: HTTP REST
- **Couverture**: Mondial (ADS-B en temps réel)
- **Données**: Position, altitude, vitesse, cap
- **Gratuit**: Oui (best effort, pas de limite officiellement)
- **Fiabilité**: ⭐⭐⭐⭐⭐ (Excellente)
- **Latence**: Temps réel (<1s)
- **Avantages**: Aucun quota, données actuelles, aucune clé nécessaire
- **Setup**:
  ```python
  api = ADSBExchangeAPI(lat=48.8, lon=2.3, radius_km=100)
  data = api.fetch()
  ```
- **Site**: https://www.adsbexchange.com

### 3. **OpenSky Network** (Alternative)
- **Type**: HTTP REST
- **Couverture**: Mondial (ADS-B/MLAT)
- **Données**: Position, altitude, vitesse, identité
- **Gratuit**: ~200 req/heure
- **Fiabilité**: ⭐⭐⭐⭐ (Très bonne)
- **Latence**: 1-5 secondes
- **Avantages**: Très fiable, bien documenté
- **Setup**:
  ```python
  api = OpenSkyAlternative(lat=48.8, lon=2.3, radius_km=50)
  data = api.fetch()
  ```
- **Site**: https://opensky-network.org

## 📊 Comparaison rapide

### Éclairs
| API | Couverture | Gratuit | Latence | Fiabilité |
|-----|-----------|---------|---------|-----------|
| Blitzortung | Mondial | ✅ | Temps réel | ⭐⭐⭐⭐⭐ |
| OpenMeteo | Mondial | ✅ | Historique | ⭐⭐⭐⭐ |
| WeatherAPI | Mondial | ✅ | 2-5s | ⭐⭐⭐⭐ |
| OpenWeather | Mondial | ✅ | 1-3s | ⭐⭐⭐⭐⭐ |

### Vols
| API | Couverture | Gratuit | Latence | Fiabilité |
|-----|-----------|---------|---------|-----------|
| AviationStack | Mondial | ⚠️ (100/mois) | 5-10s | ⭐⭐⭐⭐ |
| ADS-B Exchange | Mondial | ✅ | <1s | ⭐⭐⭐⭐⭐ |
| OpenSky | Mondial | ⚠️ (200/h) | 1-5s | ⭐⭐⭐⭐ |

## 🔧 Tester les APIs

Lancez le test de compatibilité:

```bash
python test_alternative_apis.py
```

Output:
```
⚡ TESTING LIGHTNING DATA SOURCES
🔌 Testing Blitzortung API...
   ✅ OK - 12 strikes found
🔌 Testing OpenMeteo API...
   ✅ OK - 8 strikes found
🔌 Testing WeatherAPI...
   ✅ OK - 5 strikes found
🔌 Testing OpenWeather...
   ⚠️  No data (no storm detected)

✈️  TESTING FLIGHT DATA SOURCES
🔌 Testing AviationStack...
   ❌ FAILED - Quota exceeded
🔌 Testing ADS-B Exchange...
   ✅ OK - 42 flights found
🔌 Testing OpenSky Network...
   ✅ OK - 31 flights found

📊 SUMMARY
✅ Lightning: Use Blitzortung API, OpenMeteo API, WeatherAPI
✅ Flights: Use ADS-B Exchange, OpenSky Network
```

## 🚀 Comment changer les APIs utilisées

### Option 1: Modifier `main.py`

```python
# Avant (Actuel)
lightning_sources = {"blitzortung": BlitzortungAPI(), "openmeteo": OpenMeteoAPI()}
flight_sources = {"aviationstack": AviationStackAPI()}

# Après (Alternatives)
from src.ingestion.alternative_apis import WeatherAPILightning, ADSBExchangeAPI

lightning_sources = {
    "blitzortung": BlitzortungAPI(),
    "weatherapi": WeatherAPILightning(api_key="free"),
}
flight_sources = {
    "adsb": ADSBExchangeAPI(lat=48.8, lon=2.3),
    "opensky": OpenSkyAlternative(lat=48.8, lon=2.3),
}
```

### Option 2: Configuration par environnement

Créer `.env`:
```
LIGHTNING_API=blitzortung,weatherapi
FLIGHT_API=adsb,opensky
```

### Option 3: Fallback automatique

Si une API échoue, essayer la suivante:

```python
for api_name, api in lightning_sources.items():
    try:
        data = api.fetch()
        if data.get("strikes"):
            break
    except Exception as e:
        logger.warning(f"{api_name} failed: {e}")
```

## 🔑 Clés API gratuites

### WeatherAPI
- Gratuit: https://www.weatherapi.com/signup.aspx
- Incluent: 1M appels/mois

### OpenWeather
- Gratuit: https://openweathermap.org/api
- Incluent: 60 appels/min

### AviationStack
- Gratuit: https://aviationstack.com
- Incluent: 100 appels/mois

## ⚙️ Configuration recommandée

Pour la **meilleure fiabilité**, combinez:

```python
# Éclairs: Blitzortung (WebSocket) + OpenMeteo (fallback)
lightning_sources = {
    "blitzortung_ws": BlitzortungWebSocketDataSource(),  # Temps réel
    "openmeteo": OpenMeteoAPI(),  # Fallback
    "weatherapi": WeatherAPILightning(api_key="free"),  # Fallback 2
}

# Vols: ADS-B + OpenSky (pas de quota)
flight_sources = {
    "adsb": ADSBExchangeAPI(),  # Temps réel, pas de quota
    "opensky": OpenSkyAlternative(),  # Fallback
}
```

## 📝 Dépannage

### "No data received"
- Vérifier la couverture dans votre région
- Essayer une autre API de la liste
- Vérifier les logs: `tail -f logs/app.log`

### "API quota exceeded"
- Réduire la fréquence des appels
- Combiner avec une API sans quota
- Utiliser ADS-B Exchange (pas de limites)

### "Connection timeout"
- Vérifier la connexion internet
- Augmenter le timeout: `response = session.get(url, timeout=30)`
- Essayer une API alternative

## 📚 Références

- **Blitzortung**: https://www.blitzortung.org
- **OpenMeteo**: https://open-meteo.com
- **WeatherAPI**: https://www.weatherapi.com
- **OpenWeather**: https://openweathermap.org
- **ADS-B Exchange**: https://www.adsbexchange.com
- **OpenSky**: https://opensky-network.org

---

**Version**: 1.0  
**Dernière mise à jour**: April 2, 2026
