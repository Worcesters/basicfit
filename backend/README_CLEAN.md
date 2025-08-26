# 🧹 BasicFit v2 - Architecture Propre

## 🎯 Objectif

Cette version de BasicFit v2 a été **complètement nettoyée** pour résoudre les problèmes suivants :

1. ✅ **Import CSV** → S'enregistre maintenant dans `CalendrierEntrainementSimple`
2. ✅ **Exercices effectués** → S'enregistrent dans `ExerciceEffectueUnifie`
3. ✅ **Recommandations IA** → Basées uniquement sur les exercices effectués (plus de dépendance locale)

## 🚀 Démarrage Rapide

### 1. Installation
```bash
cd backend
pip install -r requirements.txt
```

### 2. Migration des données
```bash
python migrate_to_clean.py
```

### 3. Démarrage du serveur
```bash
python manage.py runserver
```

### 4. Test de l'API
```bash
python test_api_clean.py
```

## 🔌 Nouveaux Endpoints

### Import CSV Calendrier
```http
POST /api/workouts/import-csv/
Content-Type: application/json

{
  "csv_data": "machine,date,type,duree,poids,series,repetitions\nTapis,2025-01-15,CARDIO,30,0,1,1"
}
```

### Enregistrer un Exercice
```http
POST /api/workouts/exercice/
Content-Type: application/json

{
  "nom_exercice": "Squat libre",
  "poids": 100.0,
  "series": 4,
  "repetitions": 8,
  "machine_id": 1,
  "commentaire": "Exercice effectué"
}
```

### Récupérer le Calendrier
```http
GET /api/workouts/calendrier/
Authorization: Bearer <token>
```

### Recommandations IA
```http
GET /api/workouts/recommandations/
Authorization: Bearer <token>
```

## 📊 Structure des Données

### Table `ExerciceEffectueUnifie`
- **Source unique** pour tous les exercices
- **Traçabilité complète** de l'origine
- **Calcul automatique** du volume total

### Table `CalendrierEntrainementSimple`
- **Métadonnées des séances**
- **Métriques globales** mises à jour automatiquement
- **Liaison avec les exercices** via date et nom

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

## 🧪 Tests

### Test Manuel
```bash
# Test de l'import CSV
curl -X POST http://localhost:8000/api/workouts/import-csv/ \
  -H "Content-Type: application/json" \
  -d '{"csv_data": "machine,date,type\nTapis,2025-01-15,CARDIO"}'

# Test des exercices
curl -X GET http://localhost:8000/api/workouts/exercices/ \
  -H "Authorization: Bearer <token>"
```

### Test Automatique
```bash
python test_api_clean.py
```

## 📱 Intégration Android

### 1. Import CSV
```kotlin
val csvData = "machine,date,type\nTapis,2025-01-15,CARDIO"
val response = apiService.importCsv(csvData)
```

### 2. Enregistrer Exercice
```kotlin
val exercice = ExerciceData(
    nomExercice = "Squat",
    poids = 100.0,
    series = 4,
    repetitions = 8
)
val response = apiService.enregistrerExercice(exercice)
```

### 3. Récupérer Calendrier
```kotlin
val calendrier = apiService.getCalendrier()
```

## 🚨 Points d'Attention

### Avant la Migration
- ✅ **Sauvegarder** toutes les données existantes
- ✅ **Tester** sur un environnement de développement
- ✅ **Vérifier** que l'application Android est compatible

### Après la Migration
- ✅ **Tester** tous les endpoints
- ✅ **Vérifier** que les données sont correctes
- ✅ **Mettre à jour** l'application Android

## 🔧 Dépannage

### Problème : Tables non trouvées
```bash
python manage.py makemigrations
python manage.py migrate
```

### Problème : Données manquantes
```bash
python migrate_to_clean.py
```

### Problème : API non accessible
```bash
# Vérifier que le serveur tourne
python manage.py runserver

# Vérifier les logs
tail -f logs/django.log
```

## 📚 Documentation Complète

- **Architecture** : `ARCHITECTURE_CLEAN.md`
- **Modèles** : `apps/workouts/models_unified.py`
- **API** : `apps/workouts/api_clean.py`
- **URLs** : `apps/workouts/urls_clean.py`

## 🎉 Avantages de la Nouvelle Architecture

1. **Simplicité** : Une seule table pour tous les exercices
2. **Performance** : Plus de jointures complexes
3. **Maintenance** : Code plus simple et maintenable
4. **Évolutivité** : Facile d'ajouter de nouvelles sources
5. **Cohérence** : Toutes les données au même endroit
6. **Traçabilité** : Origine de chaque exercice clairement identifiée

## 🤝 Support

En cas de problème :
1. Vérifier les logs Django
2. Tester les endpoints individuellement
3. Vérifier la structure de la base de données
4. Consulter la documentation d'architecture
