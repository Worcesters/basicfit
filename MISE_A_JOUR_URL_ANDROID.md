# Mise à jour de l'URL API dans Android

## Après déploiement sur Railway

### 1. Récupérer l'URL de votre API
Une fois déployé sur Railway, votre URL sera quelque chose comme :
```
https://basicfit-production-xxxx.railway.app
```

### 2. Modifier ApiService.kt

Ouvrez le fichier : `android/app/src/main/java/com/basicfit/app/data/api/ApiService.kt`

Remplacez la ligne :
```kotlin
private const val BASE_URL = "http://192.168.1.48:8000/api/"
```

Par votre nouvelle URL Railway :
```kotlin
private const val BASE_URL = "https://votre-app.railway.app/api/"
```

### 3. Exemple complet
```kotlin
object ApiService {
    // URL de production Railway
    private const val BASE_URL = "https://basicfit-production-xxxx.railway.app/api/"

    // Le reste du code reste identique...
}
```

### 4. Recompiler l'app Android
```bash
cd android
./gradlew assembleDebug
```

### 5. Tester la connexion
1. Lancez l'app Android
2. Essayez de vous connecter
3. L'app utilisera maintenant l'API en ligne !

## Basculement automatique

Votre app est configurée pour :
- ✅ Utiliser l'API en ligne si disponible
- ✅ Basculer automatiquement vers le stockage local si pas de connexion
- ✅ Synchroniser quand la connexion revient

## URLs à retenir

### Railway
- **Dashboard** : https://railway.app/dashboard
- **API URL** : https://votre-app.railway.app/api/
- **Admin Django** : https://votre-app.railway.app/admin/

### API Endpoints disponibles
- `POST /api/users/android/login/` - Connexion
- `POST /api/users/android/register/` - Inscription
- `GET /api/users/android/profile/` - Profil utilisateur
- `POST /api/workouts/sauvegarder/` - Sauvegarder séance
- `GET /api/workouts/seances/stats/` - Statistiques
- `GET /api/workouts/seances/history/` - Historique

## Test rapide
Testez votre API avec :
```bash
curl https://votre-app.railway.app/api/info/
```

Doit retourner :
```json
{
    "message": "API BasicFit opérationnelle",
    "version": "1.0",
    "status": "OK"
}
```