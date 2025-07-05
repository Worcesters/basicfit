# 🚀 BasicFit v2 - Guide API Django + Android

## 📋 Vue d'ensemble

Votre application BasicFit Android est maintenant **complètement connectée** à une API Django déployée sur Railway. Les utilisateurs peuvent créer un compte, se connecter, et synchroniser automatiquement leurs entraînements dans la base de données.

## 🛠️ Architecture

```
📱 Application Android (Kotlin + Jetpack Compose)
    ↕️ (HTTP/JSON + JWT)
🌐 API Django REST (Railway)
    ↕️
🗄️ Base de données PostgreSQL (Railway)
```

## 🔧 Configuration Railway

### Étape 1 : Variables d'environnement
Connectez-vous à [Railway](https://railway.app) et configurez ces variables :

```env
DJANGO_SETTINGS_MODULE=basicfit_project.settings.railway
DEBUG=False
SECRET_KEY=votre-cle-secrete-ultra-securisee-2024
```

### Étape 2 : URL de l'API
Votre API sera accessible sur :
```
https://basicfitv2-production.up.railway.app/api/
```

### Étape 3 : Déploiement
Exécutez le script de déploiement :
```bash
deploy_api_railway.bat
```

## 📱 Fonctionnalités Android

### 🔐 Authentification
- **Inscription** : Création complète de compte avec profil utilisateur
- **Connexion** : Authentification sécurisée avec JWT
- **Déconnexion** : Nettoyage automatique des données locales
- **Persistence** : Connexion automatique au redémarrage

### 🏋️ Synchronisation des entraînements
- **Sauvegarde automatique** : Chaque entraînement terminé est envoyé sur le serveur
- **Mode hors-ligne** : Les données sont sauvegardées localement en cas de problème réseau
- **Historique synchronisé** : Récupération de l'historique depuis le serveur

### 💾 Gestion des données
- **Profil utilisateur** : Âge, poids, taille, objectifs sportifs
- **Entraînements** : Sessions complètes avec exercices, séries, poids, répétitions
- **Statistiques** : Calculs automatiques de calories, progression, etc.

## 🔌 Endpoints API

### Authentification
```
POST /api/users/android/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse123",
  "nom": "Dupont",
  "prenom": "Jean",
  "poids": 75.0,
  "taille": 180,
  "genre": "Homme",
  "objectif_sportif": "Prise de masse",
  "niveau_experience": "Modéré"
}

Response:
{
  "success": true,
  "message": "Compte créé avec succès",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nom": "Dupont",
    "prenom": "Jean"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

```
POST /api/users/android/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse123"
}

Response:
{
  "success": true,
  "message": "Connexion réussie",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nom": "Dupont",
    "prenom": "Jean"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Profil utilisateur
```
GET /api/users/android/profile/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nom": "Dupont",
    "prenom": "Jean",
    "date_inscription": "15/01/2024",
    "total_seances": 12
  }
}
```

### Sauvegarde d'entraînement
```
POST /api/workouts/sauvegarder/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "nom": "Push Day",
  "date_debut": "2024-01-15 10:00:00",
  "duree_minutes": 45,
  "exercises": [
    {
      "nom": "Développé couché",
      "series": 4,
      "repetitions": 10,
      "poids": 80.0
    },
    {
      "nom": "Développé incliné",
      "series": 3,
      "repetitions": 12,
      "poids": 70.0
    }
  ]
}

Response:
{
  "success": true,
  "message": "Entraînement sauvegardé avec succès"
}
```

## 🧪 Tests

### Test automatique de l'API
Exécutez le script de test :
```bash
python test_android_api.py
```

Ce script teste automatiquement :
- ✅ Connexion à l'API
- ✅ Inscription d'un utilisateur test
- ✅ Connexion avec les identifiants
- ✅ Récupération du profil
- ✅ Sauvegarde d'un entraînement

### Test depuis l'application Android
1. **Compilez l'app** : `cd android && .\gradlew assembleDebug`
2. **Installez l'APK** sur votre téléphone/émulateur
3. **Créez un compte** via l'interface d'inscription
4. **Effectuez un entraînement** et vérifiez la synchronisation

## 🔒 Sécurité

### JWT (JSON Web Tokens)
- **Expiration** : 7 jours pour l'access token
- **Refresh** : 30 jours pour le refresh token
- **Rotation** : Les tokens sont renouvelés automatiquement

### HTTPS
- **Communication chiffrée** : Toutes les requêtes passent en HTTPS
- **Headers sécurisés** : CORS et CSP configurés
- **Validation** : Toutes les données sont validées côté serveur

### Données utilisateur
- **Mots de passe** : Hachés avec Django (PBKDF2)
- **Données sensibles** : Jamais stockées en local sans chiffrement
- **RGPD** : Possibilité de suppression complète du compte

## 🐛 Dépannage

### L'application ne se connecte pas
1. Vérifiez que l'API Railway est en ligne : https://basicfitv2-production.up.railway.app/
2. Contrôlez les logs Railway dans le dashboard
3. Testez avec le script `test_android_api.py`

### Erreurs de synchronisation
- Les données sont sauvegardées localement en priorité
- La synchronisation se fait en arrière-plan
- En cas d'échec, les données restent disponibles localement

### Compilation Android échoue
```bash
cd android
.\gradlew clean
.\gradlew assembleDebug
```

## 📊 Monitoring

### Logs Railway
- Consultez les logs dans le dashboard Railway
- Surveillez les erreurs 500/400
- Vérifiez les temps de réponse

### Analytics Android
- Logs automatiques des erreurs de connexion
- Statistiques d'utilisation locale
- Métriques de synchronisation

## 🚀 Mise en production

### Optimisations recommandées
1. **Gestion d'erreurs** : Notifications utilisateur améliorées
2. **Cache** : Mise en cache intelligente des données
3. **Synchronisation** : Queue de synchronisation pour mode hors-ligne
4. **Performance** : Optimisation des requêtes Django

### Évolutions possibles
- **Notifications push** pour la motivation
- **Partage social** des performances
- **Coach IA** avec recommandations personnalisées
- **Synchronisation multi-appareils**

## 💡 Support

En cas de problème :
1. Consultez les logs (Railway + Android)
2. Testez avec `test_android_api.py`
3. Vérifiez la connectivité réseau
4. Contrôlez les variables d'environnement Railway

---
**🎉 Félicitations ! Votre application BasicFit est maintenant équipée d'une API Django complète et fonctionnelle !**