# 🚀 Guide de déploiement Heroku - BasicFit v2

## **📋 Prérequis**

1. **Compte Heroku gratuit** : [Créer sur heroku.com](https://signup.heroku.com)
2. **Heroku CLI** : [Télécharger ici](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git** : [Télécharger ici](https://git-scm.com) (si pas installé)

---

## **🎯 Étape 1 : Installation Heroku CLI**

### **Téléchargement**
1. Allez sur [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
2. Téléchargez pour **Windows**
3. Installez avec les options par défaut

### **Vérification**
Ouvrez PowerShell et tapez :
```bash
heroku --version
```

Vous devriez voir quelque chose comme : `heroku/8.7.1 win32-x64 node-v18.19.0`

---

## **🔐 Étape 2 : Connexion à Heroku**

Dans PowerShell :
```bash
heroku login
```

Cela ouvrira votre navigateur pour vous connecter. Cliquez sur **"Log in"**.

---

## **🚀 Étape 3 : Créer l'application Heroku**

Dans votre dossier `backend` :
```bash
cd backend
heroku create basicfit-[votre-nom]
```

**Exemple** : `heroku create basicfit-jeremy`

⚠️ **Le nom doit être unique sur tout Heroku !**

---

## **📁 Étape 4 : Fichiers déjà préparés ✅**

Les fichiers suivants ont été créés automatiquement :

- ✅ `Procfile` - Instructions pour Heroku
- ✅ `requirements.txt` - Dépendances Python
- ✅ `runtime.txt` - Version Python
- ✅ `settings/heroku.py` - Configuration production

---

## **🗄️ Étape 5 : Base de données**

### **Option A : PostgreSQL (recommandé)**
```bash
heroku addons:create heroku-postgresql:mini
```

### **Option B : SQLite (simple)**
Rien à faire, déjà configuré !

---

## **🚀 Étape 6 : Déploiement**

### **Initialiser Git**
```bash
git init
git add .
git commit -m "Initial commit"
```

### **Ajouter Heroku comme remote**
```bash
heroku git:remote -a basicfit-[votre-nom]
```

### **Configurer les variables**
```bash
heroku config:set DJANGO_SETTINGS_MODULE=basicfit_project.settings.heroku
heroku config:set SECRET_KEY=your-super-secret-key-here
heroku config:set DEBUG=False
```

### **Déployer !**
```bash
git push heroku main
```

---

## **📊 Étape 7 : Configurer la base de données**

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## **🎉 Étape 8 : Tester votre API**

### **Obtenir votre URL**
```bash
heroku open
```

Votre API sera sur : `https://basicfit-[votre-nom].herokuapp.com`

### **Test rapide**
Allez sur : `https://basicfit-[votre-nom].herokuapp.com/api/workouts/info/`

Vous devriez voir :
```json
{
    "total_seances": 0,
    "total_exercices": 0,
    "total_series": 0,
    "message": "API workouts fonctionnelle ✅"
}
```

---

## **📱 Étape 9 : Modifier l'app Android**

Dans `android/app/src/main/java/com/basicfit/app/data/api/ApiService.kt` :

```kotlin
// Remplacer cette ligne :
private const val BASE_URL = "http://10.0.2.2:8000/"

// Par votre URL Heroku :
private const val BASE_URL = "https://basicfit-[votre-nom].herokuapp.com/"
```

⚠️ **N'oubliez pas le `/` à la fin !**

---

## **🔄 Étape 10 : Mettre à jour l'app (futur)**

Quand vous modifiez le code :

```bash
git add .
git commit -m "Description des changements"
git push heroku main
```

---

## **📊 Surveillance et logs**

### **Voir les logs**
```bash
heroku logs --tail
```

### **État de l'app**
```bash
heroku ps
```

### **Interface web**
```bash
heroku open
```

---

## **💰 Coûts Heroku**

### **Plan gratuit (Eco)**
- ✅ **0,01$/heure** (≈ 7$/mois si 24h/24)
- ✅ 1000 heures gratuites/mois avec carte bancaire
- ✅ L'app "dort" après 30min d'inactivité
- ✅ Réveil automatique à la première requête

### **Optimisation**
- ✅ App active seulement quand utilisée
- ✅ Parfait pour projets personnels
- ✅ Pas de limite d'utilisateurs

---

## **🐛 Dépannage**

### **Erreur : Application error**
```bash
heroku logs --tail
```

### **Erreur : Build failed**
Vérifiez que tous les fichiers sont bien commitées :
```bash
git status
git add .
git commit -m "Fix"
git push heroku main
```

### **Erreur : Module not found**
Vérifiez `requirements.txt` :
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push heroku main
```

---

## **✅ Checklist finale**

- [ ] Heroku CLI installé
- [ ] Connecté à Heroku (`heroku login`)
- [ ] App créée (`heroku create`)
- [ ] Variables configurées (`heroku config:set`)
- [ ] Code déployé (`git push heroku main`)
- [ ] Base migrée (`heroku run python manage.py migrate`)
- [ ] API testée (URL/api/workouts/info/)
- [ ] Android modifié (BASE_URL)

---

## **🎊 Félicitations !**

Votre application BasicFit est maintenant **accessible partout dans le monde** !

🌐 **URL** : `https://basicfit-[votre-nom].herokuapp.com`
📱 **App Android** : Fonctionne avec la vraie base de données
🔄 **Synchronisation** : Données partagées entre tous les appareils

---

## **📞 Support**

En cas de problème :
1. Consultez les logs : `heroku logs --tail`
2. Vérifiez le statut : `heroku ps`
3. Redémarrez : `heroku ps:restart`

**🎉 Votre app est en production !**