# 🗑️ Guide Complet: Nettoyage PostgreSQL

## 📋 Problème

Vous avez actuellement des données de test/démo dans PostgreSQL. Vous voulez tout supprimer pour recommencer avec **uniquement des données pures provenant des APIs**.

## ✅ Solutions Fournies

Trois outils ont été créés pour nettoyer votre base de données:

### **Option 1️⃣: Script Python INTERACTIF (RECOMMANDÉ) ⭐**

```bash
.\venv\Scripts\Activate.ps1
python cleanup_db_complete.py
```

**Caractéristiques:**
- ✅ Demande confirmation avant suppression (sécurisé)
- ✅ Affiche statistiques détaillées
- ✅ Montre le nombre de lignes supprimées par table
- ✅ Vérifie que les tables sont vides après suppression
- ✅ Facile à utiliser

**Prompt:**
```
Tapez 'OUI SUPPRIMER' pour confirmer la suppression complète: OUI SUPPRIMER
```

---

### **Option 2️⃣: Script Python AUTOMATIQUE**

```bash
.\venv\Scripts\Activate.ps1
python cleanup_auto.py
```

**Caractéristiques:**
- ✅ Exécution directe sans confirmation
- ✅ Idéal pour automatisation/scripts
- ✅ Résumé des résultats

---

### **Option 3️⃣: Script SQL DIRECT**

Pour exécuter avec `psql`:

```bash
psql -h localhost -p 5433 -U postgres -d lightning_db -f cleanup_complete.sql
```

**Caractéristiques:**
- ✅ Exécution directe sans dépendances Python
- ✅ Vérifie les counts restants
- ✅ Résumé en SQL

---

## ⚠️ Problème d'Authentification PostgreSQL

Si vous avez une erreur `fe_sendauth: no password supplied`, utilisez UNE de ces solutions:

### **Solution A: Définir variable d'environnement (PLUS SIMPLE)**

```powershell
$env:PGPASSWORD = "votre_mot_de_passe_postgres"
python cleanup_db_complete.py
```

Remplacez `votre_mot_de_passe_postgres` par votre vrai mot de passe.

### **Solution B: Créer fichier .pgpass**

1. Créer/éditer: `C:\Users\Barraud\.pgpass`
2. Ajouter:
```
localhost:5433:lightning_db:postgres:votre_mot_de_passe
127.0.0.1:5433:lightning_db:postgres:votre_mot_de_passe
```
3. Définir permissions:
```powershell
icacls "C:\Users\Barraud\.pgpass" /inheritance:r /grant:r "$($env:USERNAME):(F)"
```

---

## 📊 Que Sera Supprimé

| Table | Avant | Après |
|-------|-------|-------|
| **lightning** | N enregistrements | 0 |
| **flights** | N enregistrements | 0 |
| **disruptions** | N enregistrements | 0 |
| **trajectories** | N enregistrements | 0 |

---

## 🎯 Procédure Complète

### 1️⃣ Nettoyer la base de données

```bash
# Activer venv
.\venv\Scripts\Activate.ps1

# Exécuter le nettoyage
python cleanup_db_complete.py
```

### 2️⃣ Vérifier que c'est vide

```bash
python.exe -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5433, database='lightning_db', user='postgres', password='')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM lightning WHERE 1=1;')
print(f'Lightning records: {cursor.fetchone()[0]}')
cursor.close()
conn.close()
"
```

### 3️⃣ Lancer le pipeline avec données API

```bash
python main.py
```

Le pipeline va maintenant:
- ✅ Récupérer données UNIQUEMENT des APIs (Blitzortung, Open-Meteo, AviationStack)
- ✅ Stocker dans MinIO (data lake)
- ✅ Charger dans PostgreSQL (base de données propre)
- ✅ Zéro donnée locale (`data/raw` n'existe pas)

---

## 💾 Fichiers Créés

```
📁 Projet_Big-Data-/
├── cleanup_db_complete.py     ← Script Python interactif (RECOMMANDÉ)
├── cleanup_auto.py             ← Script Python automatique
├── cleanup_complete.sql        ← Script SQL direct
└── README_CLEANUP.md           ← Ce fichier
```

---

## ✨ Résultat Attendu

Après exécution:

```
======================================================================
PostgreSQL COMPLETE DATA CLEANUP
======================================================================

⚠️  ATTENTION: Cette opération SUPPRIMERA TOUTES les données!
   → Lightning strikes
   → Flights
   → Disruptions
   → Trajectories

Suppression en cours...
----------------------------------------------------------------------
✅ lightning          | Supprimé:   500 | Restant: 0
✅ flights            | Supprimé:  3000 | Restant: 0
✅ disruptions        | Supprimé:  2000 | Restant: 0
✅ trajectories       | Supprimé:   500 | Restant: 0
----------------------------------------------------------------------

✅ SUCCÈS: 6000 enregistrements au total supprimés
🎯 Base de données prête pour données API pures uniquement

======================================================================
```

---

## 🔗 Ressources

- **AviationStack API** (Vols): https://aviationstack.com
- **Blitzortung API** (Éclairs): https://www.blitzortung.org
- **Open-Meteo API** (Données historiques): https://open-meteo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

## 🚨 Attention

⚠️ **Cette opération est IRRÉVERSIBLE** - Assurez-vous vraiment de vouloir supprimer toutes les données!

Une fois supprimées:
- ❌ Les données ne peuvent pas être récupérées (sans backup)
- ✅ Mais le pipeline va immédiatement recevoir de nouvelles données des APIs

---

## ✅ Checklist

- [ ] J'ai lu ce guide complètement
- [ ] J'ai défini mon mot de passe PostgreSQL (`$env:PGPASSWORD` ou `.pgpass`)
- [ ] J'ai exécuté `python cleanup_db_complete.py`
- [ ] J'ai confirmé avec `OUI SUPPRIMER`
- [ ] Les counts affichent tous 0
- [ ] Je suis prêt à lancer le pipeline avec `python main.py`

Une fois tout cela fait, votre système sera complètement purifié et prêt pour des données API authentiques!
