# 📊 EDA Analysis Notebook - Guide d'Utilisation

**Fichier**: `notebooks/eda_analysis.ipynb`  
**Date**: 1 avril 2026  
**Objectif**: Analyse exploratoire des données (EDA) pour évaluer la qualité des données

## 🎯 Contenu du Notebook

Le notebook contient **7 sections** d'analyse complète:

### Section 1️⃣: Charger et Explorer les Données
- Importe les bibliothèques Python (pandas, numpy, matplotlib, seaborn)
- Charge les données depuis le Data Lake
- Affiche les informations de base (shape, dtypes, statistiques)

**Outputs**:
- Dimensions du dataset
- Types de données
- Statistiques descriptives (moyenne, médiane, min, max, etc.)

### Section 2️⃣: Calculer le Pourcentage de Données Manquantes
- Calcule le nombre et le % de valeurs NaN par colonne
- Affiche un tableau récapitulatif
- Génère 2 visualisations

**Outputs**:
- Tableau: Colonne | Valeurs Manquantes | % Manquantes
- **Graphique 1**: Pourcentage manquant par colonne (horizontal bar)
- **Graphique 2**: Niveau de complétude (bar chart coloré)

### Section 3️⃣: Identifier les Valeurs Aberrantes
- Utilise la méthode **IQR** (Interquartile Range)
- Détecte les outliers avec Q1 - 1.5×IQR et Q3 + 1.5×IQR
- Calcule le % d'aberrantes par colonne

**Outputs**:
- Tableau: Colonne | Valeurs Aberrantes | % Aberrantes
- **Graphique**: Boxplots pour chaque colonne numérique
  - Les points rouges = valeurs aberrantes
  - Les lignes = quartiles (Q1, Médiane, Q3)

### Section 4️⃣: Générer la Matrice de Corrélation
- Calcule les corrélations de **Pearson** entre variables numériques
- Valeurs de -1 (corrélation négative) à +1 (corrélation positive)
- Identifie les corrélations fortes (|r| > 0.7)

**Outputs**:
- Tableau: Matrice de corrélation complète
- Liste des corrélations fortes avec les paires de variables

### Section 5️⃣: Heatmap de Corrélation
- Visualisation graphique de la matrice de corrélation
- **Couleurs**:
  - 🔴 Rouge = corrélation positive (proche de 1)
  - 🔵 Bleu = corrélation négative (proche de -1)
  - ⚪ Blanc = pas de corrélation (proche de 0)

**Output**: 
- **Graphique Heatmap**: Grille colorée avec valeurs annotées

### Section 6️⃣: Diagrammes d'Analyse
Contient 3 visualisations supplémentaires:

#### 6.1 Histogrammes des Distributions
- Un histogramme par colonne numérique
- Affiches simultanément la **moyenne** (ligne rouge) et **médiane** (ligne verte)
- Montre la forme de la distribution (normale, asymétrique, etc.)

#### 6.2 Diagramme Comparatif
- Barres groupées: Manquantes vs Aberrantes
- Permet de comparer rapidement la qualité par colonne
- Chaque pourcentage est affiché sur sa barre

### Section 7️⃣: Résumé et Recommandations
- Résumé global de la qualité des données
- Liste des colonnes avec problèmes
- **Recommandations d'actions** en 5 points:
  1. ✅ Imputation des manquantes
  2. ✅ Traitement des aberrantes
  3. ✅ Normalisation des données
  4. ✅ Nettoyage général
  5. ✅ Validation post-nettoyage

## 🚀 Comment Utiliser le Notebook

### Prérequis
```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat # Windows

# Installer les packages
pip install jupyter notebook pandas numpy matplotlib seaborn
```

### Lancer le Notebook

#### Option 1: Jupyter Notebook (Interface web)
```bash
jupyter notebook notebooks/eda_analysis.ipynb
```
Le notebook s'ouvrira dans votre navigateur à `http://localhost:8888`

#### Option 2: Jupyter Lab (Meilleure interface)
```bash
pip install jupyterlab
jupyter lab notebooks/eda_analysis.ipynb
```

#### Option 3: VS Code (Intégré)
1. Ouvrir VS Code dans le dossier du projet
2. Ouvrir le fichier `notebooks/eda_analysis.ipynb`
3. Cliquer sur "Run All" ou exécuter cellule par cellule

### Exécuter le Notebook

1. **Toutes les cellules**: Cliquez sur ⏯️ "Run All" dans la barre d'outils
2. **Cellule par cellule**: Sélectionnez chaque cellule et appuyez sur **Shift + Enter**
3. **De la position actuelle jusqu'à la fin**: Cliquez sur ⏩ "Run Below"

## 📊 Interprétation des Résultats

### Pourcentage de Données Manquantes
- **0-5%**: ✅ Excellent, peu d'imputation nécessaire
- **5-20%**: ⚠️ Acceptable, implémenter une stratégie d'imputation
- **20-50%**: 🔴 Problématique, considérer la suppression
- **>50%**: ❌ Non recommandé, supprimer la colonne

### Pourcentage d'Aberrantes
- **0-2%**: ✅ Excellent, normal dans les données réelles
- **2-5%**: ⚠️ Acceptable, vérifier et potentiellement corriger
- **5-10%**: 🔴 Élevé, investigation recommandée
- **>10%**: ❌ Très problématique, erreur de mesure potentielle

### Matrice de Corrélation
- **|r| > 0.9**: Corrélation très forte (problème de multicollinéarité)
- **0.7 < |r| ≤ 0.9**: Corrélation forte (à surveiller)
- **0.4 < |r| ≤ 0.7**: Corrélation modérée (normal)
- **|r| ≤ 0.4**: Corrélation faible (peu de relation)

### Distribution (Histogramme)
- **Distribution Normale** (courbe en cloche): Données bien équilibrées
- **Asymétrique à droite**: Plus de petites valeurs
- **Asymétrique à gauche**: Plus de grandes valeurs
- **Bimodale**: Deux pics = deux groupes de données

## 💾 Exporter les Résultats

### Format PDF
1. Dans Jupyter: File > Print Preview
2. Appuyez sur Ctrl+P
3. Sélectionnez "Imprimer vers PDF"

### Format HTML
1. Dans Jupyter: File > Download as > HTML (.html)
2. Ouvre dans un navigateur pour partager

### Format Markdown
1. Dans Jupyter: File > Download as > Markdown (.md)
2. Idéal pour les documents GitHub/Wiki

## 🔧 Modifier le Notebook

### Charger Vos Propres Données
Modifiez la cellule 4 (fonction `load_data_from_datalake()`):

```python
# Remplacer par votre chemin
df = pd.read_csv('chemin/vers/votre/fichier.csv')
# ou
df = pd.read_json('chemin/vers/votre/fichier.json')
```

### Ajouter d'Autres Analyses
Ajoutez des cellules Python supplémentaires:
1. Placez le curseur après une cellule
2. Appuyez sur **+Code** ou **+Markdown**
3. Écrivez votre code

### Exemple d'Ajout: Skewness & Kurtosis
```python
from scipy import stats

for col in numeric_columns:
    skewness = stats.skew(df[col].dropna())
    kurtosis = stats.kurtosis(df[col].dropna())
    print(f"{col}: Skewness={skewness:.2f}, Kurtosis={kurtosis:.2f}")
```

## ❓ Troubleshooting

### Erreur: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas numpy matplotlib seaborn
```

### Erreur: "No such file found"
Vérifier que le notebook est dans le dossier `notebooks/`

### Les graphiques ne s'affichent pas
Ajouter en début de notebook:
```python
%matplotlib inline
```

## 📈 Cas d'Usage

### Avant la Transformation de Données
Lancez EDA pour décider de la stratégie de nettoyage

### Avant le Machine Learning
Vérifiez les correlations pour éviter la multicollinéarité

### Audit de Qualité
Générez un rapport PDF pour documenter la qualité des données

### Documentation du Dataset
Exportez le notebook comme rapport pour les stakeholders

## 🎓 Concepts Clés

| Concept | Définition | Seuil |
|---------|-----------|--------|
| **Données Manquantes** | Valeurs NaN/null | < 5% OK |
| **Aberrantes (Outliers)** | Valeurs extrêmes détectées par IQR | < 2% OK |
| **Corrélation** | Relation linéaire entre 2 variables | -1 à +1 |
| **IQR** | Q3 - Q1 (écart inter-quartile) | Mesure dispersion |
| **Skewness** | Asymétrie de la distribution | -1 à +1 |
| **Distribution Normale** | Forme de cloche symétrique | Idéal pour ML |

---

**Créé avec ❤️ pour le projet Big Data & IA**  
Pour plus d'infos: Consultez [README.md](../README.md) et [ARCHITECTURE.md](../ARCHITECTURE.md)
