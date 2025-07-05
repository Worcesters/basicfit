# BasicFit - Documentation Technique Complète

## 📋 Vue d'ensemble du projet

**BasicFit** est une application mobile Android pour la gestion d'entraînements en salle de sport, avec un backend Django REST API hébergé sur Railway.

### 🎯 Fonctionnalités principales

- **Profil utilisateur personnalisé** avec calcul automatique des calories
- **Suivi des entraînements** avec historique et statistiques
- **Gestion des machines** de sport
- **Authentification sécurisée**
- **Synchronisation backend** temps réel

---

## 🏗️ Architecture du projet

```
Basicfitv2/
├── android/           # Application Android (Kotlin + Compose)
│   ├── app/
│   │   ├── src/main/java/com/basicfit/app/
│   │   │   ├── MainActivity.kt         # Interface principale
│   │   │   ├── BasicFitApplication.java # Application MultiDex
│   │   │   └── data/                   # Couche de données
│   │   └── build.gradle                # Configuration Android
│   ├── build.gradle                    # Configuration projet
│   └── gradlew                        # Script Gradle
├── backend/           # API Django REST
│   ├── apps/
│   │   ├── users/     # Gestion utilisateurs
│   │   ├── workouts/  # Gestion entraînements
│   │   └── machines/  # Gestion machines
│   ├── basicfit_project/
│   │   └── settings/  # Configuration Django
│   └── requirements.txt # Dépendances Python
└── README.md          # Documentation générale
```

---

## ⚙️ Configuration et Installation

### 🔧 Prérequis

**Pour le développement Android :**
- **Java 8** (JDK 1.8)
- **Android SDK** (API 21+)
- **Gradle 8.0+**

**Pour le backend :**
- **Python 3.9+**
- **Django 4.2+**
- **PostgreSQL** (en production)

### 📱 Installation de l'application Android

#### Option 1 : Installation directe (Recommandée)
1. **Télécharger l'APK** : `android/app/build/outputs/apk/debug/app-debug.apk`
2. **Activer les sources inconnues** :
   - Paramètres → Sécurité → Sources inconnues (Android < 8)
   - Paramètres → Applications → Accès spécial → Installer applications inconnues (Android 8+)
3. **Installer l'APK** en la touchant dans les fichiers

#### Option 2 : Compilation manuelle
```bash
# Naviguer vers le répertoire Android
cd android

# Nettoyer et compiler
./gradlew clean assembleDebug

# L'APK sera générée dans app/build/outputs/apk/debug/
```

#### Option 3 : Transfert alternatif
- **USB** : Copier l'APK via câble USB
- **Email** : S'envoyer l'APK par email
- **Google Drive** : Partager via cloud
- **Bluetooth** : Transfert direct

### 🚀 Déploiement du backend

Le backend est hébergé sur **Railway** à l'adresse :
```
https://basicfit-production.up.railway.app/
```

#### Configuration locale du backend
```bash
# Installer les dépendances
pip install -r backend/requirements.txt

# Configurer la base de données
cd backend
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## 🔥 Fonctionnalités avancées

### 👤 Profil utilisateur intelligent

L'application calcule automatiquement :

**Données collectées :**
- Âge (années)
- Poids (kg)
- Taille (cm)
- Genre (homme/femme)
- Niveau d'activité (5 niveaux)

**Calculs automatiques :**
- **IMC** : Indice de Masse Corporelle
- **Calories journalières** : Formule Mifflin-St Jeor

```kotlin
// Formule de calcul des calories
fun calculateDailyCalories(age: Int, weight: Double, height: Int, gender: String, activityLevel: String): Int {
    val bmr = if (gender == "homme") {
        (10 * weight + 6.25 * height - 5 * age + 5)
    } else {
        (10 * weight + 6.25 * height - 5 * age - 161)
    }

    val activityFactor = when (activityLevel) {
        "Sédentaire" -> 1.2
        "Léger" -> 1.375
        "Modéré" -> 1.55
        "Actif" -> 1.725
        "Très actif" -> 1.9
        else -> 1.55
    }

    return (bmr * activityFactor).toInt()
}
```

### 📊 Suivi des entraînements

**Métriques trackées :**
- Durée des séances
- Calories brûlées
- Poids soulevé total
- Performance (Excellent, Très bien, Bien)
- Historique complet

**Statistiques disponibles :**
- Nombre de séances totales
- Séances par semaine
- Streak (jours consécutifs)
- Records personnels

### 🏋️ Gestion des machines

**Fonctionnalités :**
- Catalogue des machines disponibles
- Historique d'utilisation
- Calcul du 1RM (Répétition Maximum)
- Temps de repos intelligent

---

## 🔒 Sécurité et authentification

### 🛡️ Backend (Django)

**Authentification :**
- JWT (JSON Web Tokens)
- Système d'utilisateurs Django
- Validation des emails
- Hashage des mots de passe (PBKDF2)

**Permissions :**
- API RESTful sécurisée
- Permissions basées sur les rôles
- CORS configuré pour l'application

### 📱 Application Android

**Stockage local :**
- SharedPreferences chiffrées
- Gestion des sessions
- Sauvegarde automatique des données

**Networking :**
- HTTPS uniquement
- Timeout et retry automatiques
- Gestion des erreurs réseau

---

## 🛠️ Développement et maintenance

### 🔧 Configuration Android

**build.gradle (app) :**
```gradle
android {
    compileSdk 34

    defaultConfig {
        applicationId "com.basicfit.app"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
        multiDexEnabled true
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.10.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.multidex:multidex:2.0.1'
    implementation 'com.squareup.okhttp3:okhttp:4.12.0'
    implementation 'com.google.code.gson:gson:2.10.1'
}
```

### 🐍 Configuration Django

**settings.py principal :**
```python
# Base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT'),
    }
}

# API REST
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "https://basicfit-production.up.railway.app",
]
```

### 🔄 Workflow de développement

1. **Développement local** : `python manage.py runserver`
2. **Tests** : `python manage.py test`
3. **Migrations** : `python manage.py makemigrations && python manage.py migrate`
4. **Compilation Android** : `./gradlew assembleDebug`
5. **Déploiement** : Push sur Railway (automatique)

---

## 📡 API Endpoints

### 🔐 Authentification
```
POST /api/auth/login/          # Connexion
POST /api/auth/register/       # Inscription
POST /api/auth/refresh/        # Refresh token
```

### 👤 Utilisateurs
```
GET  /api/users/profile/       # Profil utilisateur
PUT  /api/users/profile/       # Mise à jour profil
POST /api/users/change-password/ # Changer mot de passe
```

### 🏋️ Entraînements
```
GET  /api/workouts/            # Liste des entraînements
POST /api/workouts/            # Créer un entraînement
GET  /api/workouts/{id}/       # Détail entraînement
PUT  /api/workouts/{id}/       # Modifier entraînement
DELETE /api/workouts/{id}/     # Supprimer entraînement
```

### 🏃 Machines
```
GET  /api/machines/            # Liste des machines
GET  /api/machines/{id}/       # Détail machine
POST /api/machines/use/        # Utiliser une machine
```

---

## 🐛 Résolution des problèmes

### ❌ Problèmes courants Android

**Erreur "Parse error" :**
- Vérifier la compatibilité Android (min API 21)
- Activer les sources inconnues
- Vérifier l'espace disque disponible

**Erreur de compilation :**
- Vérifier Java 8 installé
- Nettoyer le projet : `./gradlew clean`
- Vérifier les dépendances Gradle

**Problèmes de connexion :**
- Vérifier la connexion internet
- Tester l'URL du backend
- Vérifier les permissions réseau

### ⚠️ Problèmes Backend

**Erreur 500 :**
- Vérifier les logs Railway
- Contrôler les variables d'environnement
- Vérifier la base de données

**Erreur CORS :**
- Ajouter l'origine dans `CORS_ALLOWED_ORIGINS`
- Vérifier les headers de requête

---

## 📊 Monitoring et analytics

### 📈 Métriques disponibles

**Côté application :**
- Nombre d'utilisateurs actifs
- Séances d'entraînement par jour
- Temps moyen par séance
- Machines les plus utilisées

**Côté backend :**
- Requêtes API par minute
- Temps de réponse moyen
- Taux d'erreur
- Utilisation des ressources

### 🔍 Logs et debugging

**Android :**
```bash
# Logs en temps réel
adb logcat | grep BasicFit

# Logs spécifiques
adb logcat -s BasicFitApp
```

**Django :**
```python
# Configuration logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🚀 Optimisations de performance

### 📱 Android

**Optimisations implémentées :**
- MultiDex pour les applications volumineuses
- Chargement paresseux des composants
- Cache des images et données
- Compression des requêtes réseau

### 🐍 Backend

**Optimisations actives :**
- Mise en cache des requêtes fréquentes
- Optimisation des requêtes SQL
- Compression gzip des réponses
- Pool de connexions base de données

---

## 🔐 Sécurité avancée

### 🛡️ Mesures de sécurité

**Application :**
- Obfuscation du code (en production)
- Validation côté client et serveur
- Chiffrement des données sensibles
- Protection contre les attaques XSS

**Backend :**
- Rate limiting sur les API
- Validation stricte des entrées
- Protection CSRF
- Headers de sécurité configurés

---

## 📝 Notes de version

### Version 1.0.0 (Actuelle)
- ✅ Profil utilisateur avec calcul de calories
- ✅ Suivi des entraînements complet
- ✅ Interface moderne Material Design
- ✅ Backend Railway configuré
- ✅ MultiDex pour compatibilité élargie

### Roadmap future
- 🔄 Synchronisation hors ligne
- 📊 Analytics avancées
- 🏆 Système de badges et récompenses
- 👥 Fonctionnalités sociales
- 🎯 IA pour recommandations personnalisées

---

## 📞 Support et contact

Pour toute question technique ou problème :

1. **Vérifier cette documentation** complète
2. **Consulter les logs** d'erreur
3. **Tester les solutions** proposées
4. **Documenter le problème** avec détails

---

**Dernière mise à jour :** Janvier 2025
**Version documentation :** 1.0.0
**Compatibilité :** Android 5.0+ (API 21+)