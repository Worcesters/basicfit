# Architecture BasicFit v2 - Guide Complet

## 🏗️ Vue d'ensemble

L'application BasicFit v2 est structurée en architecture modulaire professionnelle avec :
- **Backend Django** avec API REST
- **Application Android native** en Kotlin
- **Base de données PostgreSQL**
- **Déploiement Docker** prêt pour production

## 📊 Modèles de Données Principaux

### Core Models
```python
# apps/core/models.py
- TimeStampedModel (base abstraite avec created_at/updated_at)
- SoftDeletableModel (suppression douce)
- ModeEntrainement (Force, Prise de masse, Sèche, etc.)
```

### User Models
```python
# apps/users/models.py
- User (modèle utilisateur personnalisé)
  * Champs : email, prenom, nom, objectif_sportif, niveau_experience
  * Propriétés calculées : nom_complet, age, imc
- ProfilUtilisateur (profil étendu)
```

### Machine Models
```python
# apps/machines/models.py
- GroupeMusculaire (Pectoraux, Dos, Biceps, etc.)
- CategorieMachine (Musculation, Poids libre, etc.)
- Machine (équipements avec caractéristiques techniques)
- VarianteMachine (variantes d'exercices)
```

### Workout Models
```python
# apps/workouts/models.py
- SeanceEntrainement (séance complète avec métriques)
- ExerciceSeance (exercice dans une séance)
- SeriExercice (série individuelle avec détails)
- ProgressionMachine (suivi progression par machine/mode)
```

## 🧮 Logique Métier Clé

### Calcul 1RM (Formule de Brzycki)
```python
def calculer_1rm_brzycki(poids, repetitions):
    if repetitions < 37:
        return poids * (36 / (37 - repetitions))
    return None
```

### Progression Automatique
```python
def evaluer_progression(exercice_seance):
    # Calcule le taux de réussite des séries
    # Si ≥ 90% de réussite → progression du poids
    # Sinon → maintien ou ajustement
```

### Recommandations par Mode
- **Force** : 85-95% 1RM, 3-5 reps, 3-5 min repos
- **Prise de masse** : 65-80% 1RM, 8-12 reps, 60-90s repos
- **Sèche** : 50-70% 1RM, 12-20 reps, 30-60s repos

## 🌐 API REST Endpoints

### Authentification
```
POST /api/auth/login/          # Connexion JWT
POST /api/auth/refresh/        # Refresh token
POST /api/auth/verify/         # Vérification token
```

### Utilisateurs
```
GET  /api/users/me/            # Profil actuel
PUT  /api/users/me/            # Modifier profil
POST /api/users/register/      # Inscription
POST /api/users/password/reset/ # Reset password
```

### Machines
```
GET  /api/machines/                    # Liste machines
GET  /api/machines/{id}/               # Détail machine
GET  /api/machines/popular/            # Top machines
GET  /api/machines/by-category/{cat}/  # Par catégorie
```

### Entraînements
```
GET  /api/workouts/seances/            # Mes séances
POST /api/workouts/seances/            # Nouvelle séance
PUT  /api/workouts/seances/{id}/start/ # Démarrer
PUT  /api/workouts/seances/{id}/finish/ # Terminer

GET  /api/workouts/progressions/       # Mes progressions
GET  /api/workouts/stats/user/         # Statistiques
```

## 📱 Architecture Android

### Structure Modulaire
```
android/app/src/main/java/com/basicfit/app/
├── data/                    # Couche données
│   ├── api/                # Services API
│   ├── database/           # Room database
│   ├── repository/         # Repositories
│   └── preferences/        # DataStore
├── domain/                 # Logique métier
│   ├── model/             # Modèles domaine
│   ├── repository/        # Interfaces repo
│   └── usecase/           # Cas d'usage
├── presentation/           # Interface utilisateur
│   ├── ui/                # Composables Jetpack Compose
│   ├── viewmodel/         # ViewModels
│   ├── theme/             # Thème Material 3
│   └── navigation/        # Navigation Compose
└── utils/                 # Utilitaires
```

### Technologies Android
- **Jetpack Compose** pour l'UI moderne
- **Hilt** pour l'injection de dépendances
- **Retrofit** pour les appels API
- **Room** pour la base locale
- **Navigation Compose** pour la navigation
- **Material 3** pour le design

## 🐳 Déploiement Docker

### Services Docker
```yaml
# docker-compose.yml
services:
  db:          # PostgreSQL 15
  redis:       # Cache Redis
  backend:     # Django API
  nginx:       # Reverse proxy (prod)
```

### Commandes de Déploiement
```bash
# Développement
./deploy.sh dev backend    # Backend seulement
./deploy.sh dev android    # Android seulement
./deploy.sh dev all        # Tout déployer

# Production
./deploy.sh prod all       # Déploiement production

# Utilitaires
./deploy.sh dev test       # Tests
./deploy.sh dev logs       # Voir les logs
./deploy.sh dev clean      # Nettoyage
```

## 🔒 Sécurité Implémentée

### Backend Django
- **JWT Authentication** avec refresh tokens
- **CSRF Protection** activée
- **Permissions DRF** granulaires par endpoint
- **Validation stricte** des données entrantes
- **HTTPS** forcé en production
- **Secrets** gérés par variables d'environnement

### Android
- **Token sécurisé** dans DataStore chiffré
- **Network Security Config**
- **ProGuard** pour l'obfuscation en release
- **Validation côté client** avant API calls

## 📈 Fonctionnalités Avancées

### Progression Intelligente
1. **Analyse automatique** des performances
2. **Ajustement des charges** selon les résultats
3. **Recommandations personnalisées** par objectif
4. **Historique détaillé** des progressions

### Métriques Avancées
- **Volume d'entraînement** (poids × reps × séries)
- **Tonnage total** par séance/semaine/mois
- **Évolution 1RM** avec graphiques
- **Taux de réussite** par machine/exercice

### Interface Utilisateur
- **Design Material 3** moderne et accessible
- **Navigation intuitive** avec bottom navigation
- **Feedback temps réel** pendant l'entraînement
- **Graphiques interactifs** pour les stats
- **Mode sombre/clair** automatique

## 🚀 Démarrage Rapide

### 1. Backend Django
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configuration
cp .env.sample .env
# Éditer .env avec vos paramètres

# Base de données
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
python manage.py createsuperuser
python manage.py runserver
```

### 2. Android
```bash
cd android
./gradlew assembleDebug
# Ouvrir dans Android Studio pour développement
```

### 3. Docker (Recommandé)
```bash
# Démarrage complet
docker-compose up -d

# API : http://localhost:8000/api/
# Admin : http://localhost:8000/admin/
# Docs : http://localhost:8000/api/docs/
```

## 📚 Documentation Technique

### Guides Développement
- **Backend** : `backend/README.md` (à créer)
- **Android** : `android/README.md` (à créer)
- **API** : Documentation Swagger sur `/api/docs/`

### Tests
```bash
# Backend
cd backend && python manage.py test

# Android
cd android && ./gradlew test
```

### Monitoring
- **Logs Django** : `backend/logs/django.log`
- **Health Check** : `GET /api/core/health/`
- **Métriques** : Intégrables avec Prometheus

---

## 🎯 Prochaines Étapes de Développement

1. **Implémenter les Views Django** manquantes
2. **Créer les écrans Android** en Compose
3. **Ajouter les tests unitaires** complets
4. **Intégrer les notifications push**
5. **Optimiser les performances** API et mobile
6. **Ajouter l'analytique** utilisateur
7. **Mode hors-ligne** Android avec synchronisation

Cette architecture solide permet un développement rapide et maintenable, avec toutes les bonnes pratiques modernes intégrées ! 🚀