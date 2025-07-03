# Guide de déploiement sur Railway

## Pourquoi Railway ?
- Vraiment gratuit (pas de carte requise)
- Plus simple que Heroku
- Déploiement automatique depuis GitHub

## Étapes de déploiement

### 1. Préparer le projet
```bash
cd backend
```

### 2. Créer un compte Railway
- Allez sur https://railway.app
- Connectez-vous avec GitHub

### 3. Déployer depuis GitHub
- Cliquez sur "New Project"
- Sélectionnez "Deploy from GitHub repo"
- Choisissez votre repo BasicFit
- Railway détecte automatiquement le Django

### 4. Variables d'environnement
Dans Railway, ajoutez ces variables :
```
DJANGO_SETTINGS_MODULE=basicfit_project.settings.production
SECRET_KEY=votre-clé-secrète-ici
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### 5. Configuration automatique
Railway va :
- Installer les dépendances depuis requirements.txt
- Détecter le Procfile
- Créer une base de données PostgreSQL
- Déployer automatiquement

### 6. Tester l'API
Votre URL sera : `https://votre-app.railway.app/api/`

## Avantages Railway vs Heroku
✅ Vraiment gratuit
✅ Pas de carte requise
✅ PostgreSQL inclus
✅ Déploiement plus simple
✅ Plus rapide

## Script automatique pour Railway

Créez `START_RAILWAY.bat` :
```bash
@echo off
echo === Déploiement BasicFit sur Railway ===
echo.
echo 1. Allez sur https://railway.app
echo 2. Connectez-vous avec GitHub
echo 3. New Project -> Deploy from GitHub repo
echo 4. Sélectionnez votre repo BasicFit
echo 5. Railway fait le reste automatiquement !
echo.
echo URL de votre API : https://votre-app.railway.app/api/
pause
```