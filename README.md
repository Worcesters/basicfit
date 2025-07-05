# 🏋️ BasicFit - Application de Fitness

Une application mobile Android moderne pour gérer vos entraînements en salle de sport avec calcul intelligent des calories.

## 🎯 Fonctionnalités

✅ **Profil personnalisé** avec calcul automatique des calories
✅ **Suivi des entraînements** complet avec statistiques
✅ **Gestion des machines** de sport
✅ **Historique détaillé** des séances
✅ **Interface moderne** Material Design
✅ **Backend sécurisé** avec synchronisation temps réel

## 🚀 Installation rapide

### 📱 Installer l'application

1. **Télécharger** l'APK : [`android/app/build/outputs/apk/debug/app-debug.apk`](android/app/build/outputs/apk/debug/app-debug.apk)
2. **Activer les sources inconnues** dans les paramètres Android
3. **Installer** l'APK en la touchant

### 🔧 Développement

```bash
# Compiler l'application
cd android
./gradlew assembleDebug

# Lancer le backend localement
cd backend
pip install -r requirements.txt
python manage.py runserver
```

## 🔥 Nouveautés

### 👤 Profil intelligent
- Calcul automatique des **calories journalières**
- **IMC** calculé en temps réel
- Paramètres personnalisés (âge, poids, taille, activité)

### 📊 Suivi avancé
- **Historique complet** des séances
- **Statistiques** détaillées
- **Streak** et records personnels

## 🛠️ Technologies

- **Android** : Kotlin + Jetpack Compose
- **Backend** : Django REST API
- **Base de données** : PostgreSQL
- **Déploiement** : Railway
- **Authentification** : JWT

## 📖 Documentation

Pour plus de détails techniques, consultez la [**Documentation technique complète**](DOCUMENTATION_TECHNIQUE.md).

## 🌐 Backend

L'API est hébergée sur Railway :
**URL :** `https://basicfit-production.up.railway.app/`

## 📊 Calcul des calories

L'application utilise la **formule de Mifflin-St Jeor** pour calculer précisément vos besoins caloriques quotidiens basés sur :
- Âge et genre
- Poids et taille
- Niveau d'activité physique

## 🎨 Interface

Interface moderne avec **Material Design 3** :
- 🎨 Design épuré et intuitif
- 📱 Responsive sur tous les écrans
- 🌟 Animations fluides
- 🎯 UX optimisée

## 🔐 Sécurité

- 🛡️ Authentification JWT sécurisée
- 🔒 Données chiffrées
- 🌐 HTTPS uniquement
- 🔑 Gestion des sessions robuste

## 📱 Compatibilité

- **Android 5.0+** (API 21+)
- **MultiDex** pour une meilleure compatibilité
- **Taille** : 6.4 MB

---

**Version actuelle :** 1.0.0
**Dernière mise à jour :** Janvier 2025

🚀 **Prêt à transformer vos entraînements ?**