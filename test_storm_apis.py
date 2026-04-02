"""
Test d'APIs pour prévision d'orages et zones à risques.
Trouve les meilleures sources de prévisions de tempêtes actuelles/futures.
"""
import requests
from datetime import datetime, timedelta
import json

print("=" * 70)
print("TEST D'APIs DE PRÉVISION D'ORAGES")
print("=" * 70)

# Coordonnées de test (Lyon, France)
LAT, LON = 45.764, 4.8357

# ========== 1. OpenWeatherMap API ==========
print("\n1️⃣  OPENWEATHERMAP (Alerts + Current)")
print("-" * 70)

try:
    # Essayer sans clé (données publiques)
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid=demo"
    resp = requests.get(url, timeout=5)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        if "weather" in data:
            weather = data["weather"][0]
            print(f"✅ Conditions: {weather.get('main')} - {weather.get('description')}")
        if "alerts" in data:
            print(f"⚠️  Alertes: {len(data['alerts'])} alert(s) active(s)")
    else:
        print(f"❌ Nécessite clé API (401 Unauthorized)")
        
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

# ========== 2. Open-Meteo Weather Alerts ==========
print("\n2️⃣  OPEN-METEO WEATHER ALERTS (Libre, pas de clé)")
print("-" * 70)

try:
    # Open-Meteo a un endpoint pour les alertes météorologiques
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=Europe/Paris"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        data = resp.json()
        current = data.get("current_weather", {})
        print(f"✅ Météo actuelle: Windspeed {current.get('windspeed', 0)} km/h")
        
        # Vérifier les prévisions
        daily = data.get("daily", {})
        weather_codes = daily.get("weather_code", [])
        
        # Codes météo indiquant des orages: 80, 81, 82, 85, 86
        storm_codes = [80, 81, 82, 85, 86, 95, 96, 99]
        has_storm = any(code in storm_codes for code in weather_codes[:3])
        
        if has_storm:
            print(f"⚠️  ALERTE: Orages prévus dans les 3 prochains jours!")
        else:
            print(f"✓ Pas d'orages majeurs prévus dans les 3 jours")
            
    else:
        print(f"❌ Erreur API: {resp.status_code}")
        
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

# ========== 3. Weather.gov (NOAA) - USA seulement ==========
print("\n3️⃣  WEATHER.GOV / NOAA (USA uniquement)")
print("-" * 70)

try:
    # Pour les coordonnées USA
    points_url = f"https://api.weather.gov/points/{LAT},{LON}"
    resp = requests.get(points_url, timeout=5)
    
    if resp.status_code == 200:
        print(f"✅ Service disponible (mais pour coordonnées USA)")
    else:
        print(f"⚠️  Service NOAA: Pour USA uniquement (France = {resp.status_code})")
        
except Exception as e:
    print(f"⚠️  NOAA non disponible: {str(e)}")

# ========== 4. Weatherbit.io ==========
print("\n4️⃣  WEATHERBIT.IO (Prévisions + Alertes)")
print("-" * 70)

try:
    # Weatherbit a un endpoint pour les alertes
    url = f"https://api.weatherbit.io/v2.0/current?lat={LAT}&lon={LON}&key=demo"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        data = resp.json()
        alerts = data.get("alerts", [])
        if alerts:
            print(f"✅ {len(alerts)} alerte(s) active(s):")
            for alert in alerts:
                print(f"   - {alert.get('title')}")
        else:
            print(f"✓ Pas d'alertes actives")
    else:
        print(f"⚠️  Nécessite clé gratuite (key=demo ne fonctionne pas)")
        
except Exception as e:
    print(f"❌ Erreur: {str(e)}")

# ========== 5. Tomorrow.io (Modern meteo) ==========
print("\n5️⃣  TOMORROW.IO (Données avancées, gratuit)")
print("-" * 70)

try:
    # Tomorrow.io a une API gratuite avec données détaillées
    url = f"https://api.weatherapi.com/v1/current.json?key=demo&q={LAT},{LON}&aqi=yes"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        print(f"✅ WeatherAPI disponible (gratuit)")
        data = resp.json()
        condition = data.get("current", {}).get("condition", {}).get("text", "")
        print(f"   Condition: {condition}")
    else:
        print(f"⚠️  Clé nécessaire")
        
except Exception as e:
    print(f"⚠️  Erreur: {str(e)}")

# ========== 6. ALERTES SPC (Storm Prediction Center) ==========
print("\n6️⃣  ALERTES SPC / NOAA (Données publiques)")
print("-" * 70)

try:
    # SPC a des données publiques sur les alertes
    url = "https://www.spc.noaa.gov/climo/report/today_otlk_1730utc_0d.txt"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        print(f"✅ Prévisions SPC disponibles (format texte)")
        lines = resp.text.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"   {line[:70]}")
    else:
        print(f"⚠️  Endpoint non disponible")
        
except Exception as e:
    print(f"⚠️  Erreur: {str(e)}")

# ========== 7. Meteoblue ==========
print("\n7️⃣  METEOBLUE (API gratuite)")
print("-" * 70)

try:
    # Meteoblue a une API gratuite
    url = f"https://my.meteoblue.com/packages/basic-1?apikey=demo&lat={LAT}&lon={LON}&format=json"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        print(f"✅ Meteoblue disponible (gratuit)")
    else:
        print(f"⚠️  Clé API nécessaire")
        
except Exception as e:
    print(f"⚠️  Erreur: {str(e)}")

# ========== 8. Visualcrossing ==========
print("\n8️⃣  VISUALCROSSING (Prévisions + Historiques)")
print("-" * 70)

try:
    # Visual Crossing a une API gratuite
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LAT},{LON}/today?key=demo&include=alerts"
    resp = requests.get(url, timeout=5)
    
    if resp.status_code == 200:
        print(f"✅ Visual Crossing disponible")
        data = resp.json()
        if "alerts" in data:
            print(f"   Alertes: {len(data['alerts'])} active(s)")
    else:
        print(f"⚠️  Clé gratuite disponible sur le site")
        
except Exception as e:
    print(f"⚠️  Erreur: {str(e)}")

print("\n" + "=" * 70)
print("RÉSUMÉ - RECOMMANDATIONS POUR PRÉVISIONS D'ORAGES")
print("=" * 70)

recommendations = """
🏆 MEILLEURES OPTIONS (Gratuites ou freemium):

1. ⭐ OPEN-METEO WEATHER ALERTS
   - ✅ Complètement gratuit, pas de clé
   - ✅ Prévisions à 10 jours
   - ✅ Codes météo pour identifier les orages (80-99)
   - ✅ API simple et rapide
   - 📊 Endpoint: /forecast avec daily + weather_code

2. ⭐ WEATHERAPI.COM
   - ✅ Gratuit (3M appels/mois)
   - ✅ Alertes en temps réel
   - ✅ Conditions actuelles + prévisions
   - ✅ Données de qualité
   - 📊 Endpoint: /current.json con aqi=yes

3. ⭐ OPENWEATHERMAP
   - ✅ Data gratuite (plan free)
   - ✅ Alertes météorologiques
   - ✅ One Call API 3.0
   - ⚠️  Nécessite clé API gratuite
   - 📊 Endpoint: /data/2.5/weather

4.💎 TOMORROW.IO (optionnel, payant mais très précis)
   - ✅ Prévisions ultra-précises
   - ✅ Alertes en temps réel
   - ⚠️  Payant ($99+/mois)
   - 📊 Données météorologiques les plus avancées

---

🎯 IMPLÉMENTATION RECOMMANDÉE:

Pour intégrer aux risques d'orages:
1. Utiliser Open-Meteo (gratuit, pas de clé)
2. Interpréter les codes météo (80-99 = orages)
3. Calculer la probabilité de foudre
4. Mapper les zones à risque sur le dashboard
5. Alerter si orage prévu + vols actifs à proximité

CODES MÉTÉO DANGEREUX:
- 80-82: Averses
- 85-86: Averses de neige
- 95-99: ORAGES VIOLENTS ⚠️
"""

print(recommendations)
