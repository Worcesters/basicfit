# BasicFit v2 - Application de Suivi de Performances en Salle de Sport

Une application complète de suivi de performances sportives avec backend Django et application mobile Android native, orientée progression personnalisée par machine et mode d'entraînement.

## 🚀 Fonctionnalités

### 🔐 Authentification
- Système d'inscription/connexion sécurisé avec JWT
- Gestion des profils utilisateurs complets
- Réinitialisation de mot de passe

### 🏋️‍♂️ Gestion des Machines
- Catalogue complet des machines de musculation
- Catégorisation par groupes musculaires
- Variantes d'exercices pour chaque machine
- Instructions détaillées et médias

### 📊 Suivi des Entraînements
- Création et gestion de séances d'entraînement
- Suivi détaillé par exercice et série
- Calcul automatique du 1RM (formule de Brzycki)
- Métriques avancées (volume, tonnage, progression)

### 📈 Progression Intelligente
- Adaptation automatique des charges selon les performances
- Recommandations personnalisées par mode d'entraînement
- Historique détaillé des progressions
- Statistiques et analyses

### 🎯 Modes d'Entraînement
- **Force** : 5×5 avec charges lourdes
- **Prise de masse** : 3×12 avec volume optimisé
- **Sèche** : Plus de répétitions, charges modérées
- **Endurance** : Hautes répétitions
- **Powerlifting** : Charges maximales

## 🏗️ Architecture Technique

### Backend (Django)
```
backend/
├── basicfit_project/          # Configuration projet
│   ├── settings/              # Settings modulaires (dev/prod)
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # Configuration WSGI
├── apps/                     # Applications modulaires
│   ├── core/                 # Modèles de base et utilitaires
│   ├── users/                # Gestion utilisateurs
│   ├── machines/             # Machines et équipements
│   └── workouts/             # Séances et progression
├── requirements.txt          # Dépendances Python
└── manage.py                # Script de gestion Django
```

### Mobile (Android - Kotlin)
```
android/
├── app/src/main/
│   ├── java/com/basicfit/
│   │   ├── ui/               # Interface utilisateur
│   │   ├── data/             # Couche données (API, Room)
│   │   ├── domain/           # Logique métier
│   │   └── utils/            # Utilitaires
│   ├── res/                  # Ressources (layouts, strings)
│   └── AndroidManifest.xml   # Configuration app
├── build.gradle              # Configuration Gradle
└── proguard-rules.pro        # Obfuscation
```

## 🛠️ Installation et Déploiement

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour développement local)
- PostgreSQL 15+
- Android Studio (pour l'app mobile)

### 1. Démarrage rapide avec Docker

```bash
# Cloner le projet
git clone <repository-url>
cd Basicfitv2

# Démarrer l'environnement complet
docker-compose up -d

# Créer un superutilisateur Django
docker-compose exec backend python manage.py createsuperuser

# Charger les données de test
docker-compose exec backend python manage.py loaddata fixtures/initial_data.json
```

L'API sera accessible sur : http://localhost:8000/api/
L'administration Django : http://localhost:8000/admin/
Documentation API : http://localhost:8000/api/docs/

### 2. Développement local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Variables d'environnement
cp .env.sample .env
# Éditer .env avec vos paramètres

# Migrations et serveur
python manage.py migrate
python manage.py runserver

# Android
cd android
./gradlew assembleDebug
# Ouvrir dans Android Studio
```

## 📱 API REST

### Authentification
```http
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/verify/
```

### Utilisateurs
```http
GET /api/users/me/                    # Profil actuel
PUT /api/users/me/                    # Modifier profil
POST /api/users/register/             # Inscription
POST /api/users/password/reset/       # Reset password
```

### Machines
```http
GET /api/machines/                    # Liste des machines
GET /api/machines/{id}/               # Détail machine
GET /api/machines/popular/            # Machines populaires
GET /api/machines/by-category/{cat}/  # Par catégorie
```

### Entraînements
```http
GET /api/workouts/seances/            # Mes séances
POST /api/workouts/seances/           # Nouvelle séance
PUT /api/workouts/seances/{id}/start/ # Démarrer séance
PUT /api/workouts/seances/{id}/finish/ # Terminer séance

GET /api/workouts/progressions/       # Mes progressions
GET /api/workouts/stats/user/         # Statistiques
```

## 🧮 Calculs Métiers

### Formule 1RM (Brzycki)
```
1RM ≈ Poids × (36 / (37 - répétitions))
```

### Progression Automatique
- **Seuil de réussite** : 90% des séries réussies
- **Augmentation** : +1 incrément machine (généralement 2,5kg)
- **Échec** : Maintien ou réduction de 5%

### Recommandations par Mode
- **Force** : 85-95% 1RM, 3-5 reps, repos 3-5min
- **Prise de masse** : 65-80% 1RM, 8-12 reps, repos 60-90s
- **Sèche** : 50-70% 1RM, 12-20 reps, repos 30-60s

## 🔒 Sécurité

- **JWT** avec refresh tokens et blacklist
- **Permissions DRF** granulaires
- **CSRF** protection activée
- **HTTPS** en production (Nginx + SSL)
- **Validation** stricte des données
- **Rate limiting** sur les API

## 🧪 Tests

```bash
# Backend
cd backend
pytest
python manage.py test

# Android
cd android
./gradlew test
./gradlew connectedAndroidTest
```

## 📦 Déploiement Production

### Backend (Heroku/AWS)
```bash
# Variables d'environnement production
export DJANGO_SETTINGS_MODULE=basicfit_project.settings.production
export DEBUG=False
export SECRET_KEY=your-production-secret

# Déploiement
docker-compose -f docker-compose.prod.yml up -d
```

### Android (Google Play)
```bash
cd android
./gradlew assembleRelease
# Signer l'APK avec votre keystore
# Upload sur Google Play Console
```

## 🤝 Contribution

1. Fork du projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit des changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- **Email** : support@basicfit.com
- **Documentation** : [Wiki du projet](wiki-url)
- **Issues** : [GitHub Issues](issues-url)

---

**Développé avec ❤️ pour la communauté fitness**