# 🚀 Guide d'utilisation - BasicFit v2 avec API Django

## **📋 Vue d'ensemble**

Votre application BasicFit v2 dispose maintenant de **deux modes de fonctionnement** :

- **🌐 Mode en ligne** : Utilise l'API Django avec base de données
- **📱 Mode local** : Utilise le stockage local (comme avant)

## **🔧 Configuration du Backend**

### **1. Démarrer le serveur Django**

```bash
# Aller dans le dossier backend
cd backend

# Installer les dépendances (si pas fait)
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Démarrer le serveur
python manage.py runserver
```

Le serveur sera disponible sur : `http://localhost:8000`

### **2. Créer un superutilisateur (optionnel)**

```bash
python manage.py createsuperuser
```

### **3. Tester l'API**

Ouvrez votre navigateur : `http://localhost:8000/api/workouts/info/`

Vous devriez voir quelque chose comme :
```json
{
    "total_seances": 0,
    "total_exercices": 0,
    "total_series": 0,
    "message": "API workouts fonctionnelle ✅"
}
```

## **📱 Configuration de l'Application Android**

### **1. Modifier l'adresse IP (appareil physique)**

Si vous utilisez un **appareil physique** (pas l'émulateur), modifiez dans `ApiService.kt` :

```kotlin
// Remplacer cette ligne :
private const val BASE_URL = "http://10.0.2.2:8000/"

// Par votre IP locale :
private const val BASE_URL = "http://192.168.1.XXX:8000/"
```

Pour trouver votre IP :
- **Windows** : `ipconfig` dans cmd
- **Mac/Linux** : `ifconfig` dans terminal

### **2. Permissions réseau**

Vérifiez que le fichier `AndroidManifest.xml` contient :
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## **🎯 Utilisation de l'Application**

### **1. Première connexion**

1. **Lancer l'app Android**
2. **Tester la connexion** avec le bouton "Tester la connexion au serveur"
3. **Créer un compte** ou **se connecter**

### **2. Modes de fonctionnement**

#### **🌐 Mode en ligne (avec API)**
- ✅ Données synchronisées en temps réel
- ✅ Accessible depuis plusieurs appareils
- ✅ Sauvegarde automatique en base
- ⚠️ Nécessite une connexion internet

#### **📱 Mode local (hors ligne)**
- ✅ Fonctionne sans internet
- ✅ Rapide et responsive
- ✅ Données privées sur l'appareil
- ⚠️ Données uniquement sur cet appareil

### **3. Basculer entre les modes**

L'application **bascule automatiquement** :
- **Connecté + serveur accessible** → Mode en ligne
- **Pas de connexion ou erreur** → Mode local

## **🔄 API Endpoints Disponibles**

### **Authentification**
```
POST /api/users/android/login/      # Connexion
POST /api/users/android/register/   # Inscription
GET  /api/users/android/profile/    # Profil utilisateur
```

### **Séances d'entraînement**
```
GET  /api/workouts/seances/         # Liste des séances
POST /api/workouts/seances/         # Créer une séance
GET  /api/workouts/seances/stats/   # Statistiques
GET  /api/workouts/seances/history/ # Historique détaillé
POST /api/workouts/sauvegarder/     # Sauvegarder (simplifié)
```

### **Machines**
```
GET  /api/workouts/machines/        # Liste des machines
```

## **📊 Structure des Données**

### **Séance sauvegardée**
```json
{
  "nom": "Séance Pectoraux",
  "duree": 45,
  "note_ressenti": 8,
  "commentaire": "Excellente séance !",
  "exercices": [
    {
      "nom": "Développé couché",
      "series": 3,
      "reps": 10,
      "poids": 80.0
    }
  ]
}
```

### **Réponse statistiques**
```json
{
  "total_seances": 15,
  "total_minutes": 675,
  "total_calories": 3375,
  "seances_excellentes": 8,
  "record_poids": 120.0,
  "exercices_favoris": ["Développé couché", "Squat", "Soulevé de terre"],
  "progression_generale": 85.5
}
```

## **🐛 Résolution de problèmes**

### **Problème : "Erreur de connexion"**
1. Vérifiez que le serveur Django est démarré
2. Testez `http://localhost:8000/api/workouts/info/` dans votre navigateur
3. Vérifiez l'IP dans `ApiService.kt` (appareils physiques)
4. L'app basculera automatiquement en mode local

### **Problème : "Non authentifié"**
1. Reconnectez-vous dans l'application
2. Le token JWT peut avoir expiré (15 min par défaut)

### **Problème : Les données ne se synchronisent pas**
1. Vérifiez votre connexion internet
2. Force la synchronisation en se déconnectant/reconnectant
3. Les données locales sont conservées en cas d'échec

## **⚡ Avantages de cette Architecture**

### **🔄 Synchronisation intelligente**
- Sauvegarde en ligne si possible
- Fallback local automatique
- Pas de perte de données

### **📈 Évolutivité**
- Backend Django professionnel
- Base de données relationnelle
- API REST documentée

### **🛡️ Robustesse**
- Fonctionne avec ou sans réseau
- Gestion d'erreurs complète
- Données persistantes

## **📱 Interface Utilisateur**

L'application indique visuellement le mode :
- 🌐 **Icône cloud** = Mode en ligne
- 📱 **Icône local** = Mode hors ligne
- ⚠️ **Messages d'état** en cas de problème

## **🚀 Déploiement en Production**

Pour un déploiement réel :

1. **Backend** : Déployez sur Heroku, AWS, ou votre serveur
2. **Base de données** : PostgreSQL recommandée
3. **HTTPS** : Certificat SSL obligatoire
4. **Android** : Mettez à jour `BASE_URL` avec votre domaine

## **📞 Support**

En cas de problème :
1. Vérifiez les logs Django : `tail -f logs/django.log`
2. Vérifiez les logs Android dans logcat
3. L'application fonctionne toujours en mode local même si l'API est indisponible

---

**🎉 Félicitations !** Vous avez maintenant une application BasicFit complète avec backend Django et mode hybride en ligne/hors ligne !