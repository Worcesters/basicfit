# 🌐 Guide de déploiement - BasicFit v2

## **❓ Le problème**

Actuellement, votre serveur Django ne tourne que sur **votre PC local** (`localhost:8000`). Pour que d'autres personnes utilisent l'application avec la base de données, vous avez **4 options** :

---

## **🚀 Option 1 : Déploiement Cloud (RECOMMANDÉ)**

### **✅ Avantages**
- ✅ Accessible 24h/24 depuis n'importe où
- ✅ Base de données fiable et sauvegardée
- ✅ Pas besoin de laisser votre PC allumé
- ✅ **Gratuit** avec les plans de base

### **🎯 Heroku (Le plus simple)**

#### **1. Installation**
```bash
# Créer un compte sur heroku.com
# Télécharger Heroku CLI
```

#### **2. Préparation du code**
```bash
cd backend

# Créer requirements.txt pour production
pip freeze > requirements.txt

# Créer Procfile
echo "web: python manage.py runserver 0.0.0.0:$PORT" > Procfile

# Créer runtime.txt
echo "python-3.11.0" > runtime.txt
```

#### **3. Déploiement**
```bash
# Initialiser git
git init
git add .
git commit -m "Initial commit"

# Créer app Heroku
heroku create basicfit-app-[votre-nom]

# Configurer les variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY="votre-secret-key-securisee"

# Déployer
git push heroku main

# Migrer la base
heroku run python manage.py migrate
```

#### **4. Résultat**
Votre API sera disponible sur : `https://basicfit-app-[votre-nom].herokuapp.com`

---

## **🎯 Railway.app (Moderne et simple)**

1. **Créer un compte** sur [railway.app](https://railway.app)
2. **Connecter votre GitHub** et sélectionner le repo
3. **Sélectionner le dossier** `backend`
4. **Déploiement automatique** !

---

## **🎯 PythonAnywhere (Interface simple)**

1. **Compte gratuit** sur [pythonanywhere.com](https://pythonanywhere.com)
2. **Upload du code** via interface web
3. **Configuration Django** guidée
4. **URL gratuite** : `[username].pythonanywhere.com`

---

## **📡 Option 2 : ngrok (Temporaire/Test)**

### **✅ Avantages**
- ✅ Solution immédiate (5 minutes)
- ✅ Gratuit pour les tests
- ✅ Votre PC reste le serveur

### **❌ Inconvénients**
- ❌ URL change à chaque redémarrage
- ❌ Votre PC doit rester allumé
- ❌ Connexion limitée (gratuit)

#### **Installation**
```bash
# Télécharger ngrok.com
# Extraire dans votre dossier projet
```

#### **Utilisation**
```bash
# Démarrer le script
./start_ngrok.bat

# Copier l'URL https://xxxx.ngrok.io
# Modifier ApiService.kt avec cette URL
```

---

## **🏠 Option 3 : Réseau local (WiFi)**

### **✅ Avantages**
- ✅ Gratuit et simple
- ✅ Rapide pour la famille/amis

### **❌ Inconvénients**
- ❌ Même réseau WiFi obligatoire
- ❌ Votre PC doit rester allumé
- ❌ Non accessible depuis l'extérieur

#### **Utilisation**
```bash
# Démarrer le script
./start_local_server.bat

# Noter votre IP (ex: 192.168.1.45)
# Modifier ApiService.kt avec http://192.168.1.45:8000/
```

---

## **💻 Option 4 : Laisser votre PC allumé**

### **❌ Pourquoi c'est une mauvaise idée**
- ❌ Consommation électrique constante
- ❌ Usure du matériel
- ❌ Risque de coupure/redémarrage
- ❌ Non accessible depuis l'extérieur
- ❌ Problèmes de sécurité réseau

---

## **🎯 Recommandation finale**

### **Pour un projet personnel/test :**
```
📡 ngrok → Démarrage immédiat
🏠 Réseau local → Si même WiFi
```

### **Pour une vraie application :**
```
🚀 Heroku → Simple et fiable
🚀 Railway → Moderne et automatique
🚀 PythonAnywhere → Interface débutant
```

---

## **📱 Modification Android nécessaire**

Quelle que soit l'option choisie, modifiez dans `ApiService.kt` :

```kotlin
// Remplacer cette ligne :
private const val BASE_URL = "http://10.0.2.2:8000/"

// Par l'URL de votre choix :
private const val BASE_URL = "https://votre-app.herokuapp.com/"     // Heroku
private const val BASE_URL = "https://xxxx.ngrok.io/"               // ngrok
private const val BASE_URL = "http://192.168.1.45:8000/"            // Local
```

---

## **🎯 Mon conseil**

1. **Test immédiat** : Utilisez `ngrok` pour tester rapidement
2. **Production** : Déployez sur **Heroku** (gratuit et professionnel)
3. **Mise à jour** : Modifiez l'URL dans `ApiService.kt`

**🎉 Résultat** : Votre application sera accessible depuis n'importe quel téléphone connecté à internet !

---

## **❓ Questions fréquentes**

**Q: Et si je veux juste tester localement ?**
R: L'application fonctionne parfaitement en mode local sans serveur !

**Q: Heroku est-il vraiment gratuit ?**
R: Oui, plan gratuit suffisant pour une app personnelle (quelques heures/jour).

**Q: Puis-je changer d'option plus tard ?**
R: Oui ! Il suffit de modifier `BASE_URL` dans l'app Android.

**Q: Et mes données existantes ?**
R: Le mode hybride garde les données locales en backup automatiquement.