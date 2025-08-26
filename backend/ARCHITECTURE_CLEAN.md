# 🧹 Architecture Propre BasicFit v2

## Vue d'ensemble

Cette version de BasicFit v2 a été **complètement nettoyée** pour utiliser **uniquement la base de données** et supprimer tout stockage local ou logique de rétrocompatibilité.

## 🗄️ Modèles Unifiés

### 1. `ExerciceEffectueUnifie`
**Table unique** pour tous les exercices effectués dans l'application :
- Import CSV calendrier
- Entraînements manuels temps réel
- Exercices individuels
- Import externe

**Champs clés :**
- `source` : Origine de l'exercice (CSV_IMPORT, MANUEL_TEMPS_REEL, etc.)
- `date_exercice` : Date et heure de réalisation
- `nom_seance` : Nom de la séance (optionnel)
- `machine` : Machine utilisée (optionnel)
- `poids_utilise`, `series_effectuees`, `repetitions_totales`
- `volume_total` : Calculé automatiquement (poids × répétitions)

### 2. `CalendrierEntrainementSimple`
**Métadonnées des séances** d'entraînement :
- Principalement pour les imports CSV
- Les exercices individuels sont dans `ExerciceEffectueUnifie`
- Métriques globales de la séance

## 🔌 API Propre

### Endpoints Principaux

#### Import CSV Calendrier
```
POST /api/workouts/import-csv/
```
- Importe les données CSV dans `CalendrierEntrainementSimple`
- Crée automatiquement les exercices dans `ExerciceEffectueUnifie`
- Met à jour les métriques des séances

#### Enregistrement Exercice
```
POST /api/workouts/exercice/
```
- Enregistre un exercice effectué manuellement
- Crée ou met à jour la séance dans le calendrier
- Source : `MANUEL_TEMPS_REEL`

#### Récupération Données
```
GET /api/workouts/exercices/          # Tous les exercices
GET /api/workouts/calendrier/         # Calendrier complet
GET /api/workouts/historique/         # Historique et progression
GET /api/workouts/stats/              # Statistiques détaillées
```

#### Recommandations IA
```
GET /api/workouts/recommandations/                    # Recommandations générales
GET /api/workouts/recommandations/machine/<id>/       # Recommandations par machine
```
- **Basées uniquement** sur `ExerciceEffectueUnifie`
- Analyse de la progression et de la fréquence
- Plus de dépendance aux séances ou données locales

## 🔄 Flux de Données

### 1. Import CSV
```
CSV → CalendrierEntrainementSimple + ExerciceEffectueUnifie
```

### 2. Exercice Manuel
```
App Android → ExerciceEffectueUnifie → CalendrierEntrainementSimple (mise à jour)
```

### 3. Recommandations
```
ExerciceEffectueUnifie → Analyse IA → Recommandations personnalisées
```

## 🚫 Ce qui a été supprimé

- ❌ Tous les anciens modèles obsolètes
- ❌ Stockage local ou cache
- ❌ Logique de rétrocompatibilité
- ❌ Anciens endpoints complexes
- ❌ Système de séances séparées
- ❌ Données dupliquées

## ✅ Ce qui a été conservé

- ✅ Modèles unifiés (`ExerciceEffectueUnifie`, `CalendrierEntrainementSimple`)
- ✅ Base de données SQLite
- ✅ Authentification utilisateur
- ✅ Gestion des machines
- ✅ Système de recommandations basé sur les exercices effectués

## 🧪 Tests

Le fichier `test_api_clean.py` permet de tester tous les endpoints :
```bash
cd backend
python test_api_clean.py
```

## 📱 Compatibilité Android

L'application Android doit maintenant utiliser ces nouveaux endpoints :

1. **Import CSV** : `POST /api/workouts/import-csv/`
2. **Enregistrer exercice** : `POST /api/workouts/exercice/`
3. **Récupérer calendrier** : `GET /api/workouts/calendrier/`
4. **Recommandations** : `GET /api/workouts/recommandations/`

## 🔧 Migration

Pour migrer depuis l'ancienne version :

1. **Sauvegarder** les données existantes
2. **Supprimer** les anciennes tables
3. **Importer** les données dans le nouveau format
4. **Tester** la nouvelle API

## 🎯 Avantages

- **Simplicité** : Une seule table pour tous les exercices
- **Performance** : Plus de jointures complexes
- **Maintenance** : Code plus simple et maintenable
- **Évolutivité** : Facile d'ajouter de nouvelles sources
- **Cohérence** : Toutes les données au même endroit

## 🚨 Points d'attention

- **Pas de rétrocompatibilité** : L'ancienne API n'existe plus
- **Migration requise** : Les données existantes doivent être converties
- **Tests nécessaires** : Vérifier que tous les endpoints fonctionnent
- **Documentation Android** : Mettre à jour l'application mobile
