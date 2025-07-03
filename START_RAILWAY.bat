@echo off
chcp 65001 >nul
color 0A
echo.
echo ===============================================
echo     🚀 DÉPLOIEMENT BASICFIT SUR RAILWAY
echo ===============================================
echo.
echo Railway est une alternative GRATUITE à Heroku
echo (pas de carte de crédit requise!)
echo.
echo 📋 ÉTAPES À SUIVRE :
echo.
echo 1️⃣  Allez sur https://railway.app
echo 2️⃣  Cliquez sur "Login" et connectez-vous avec GitHub
echo 3️⃣  Cliquez sur "New Project"
echo 4️⃣  Sélectionnez "Deploy from GitHub repo"
echo 5️⃣  Choisissez votre repo BasicFit (ou uploadez le dossier backend)
echo 6️⃣  Railway détecte automatiquement Django !
echo.
echo ⚙️  CONFIGURATION AUTOMATIQUE :
echo   ✅ Installe requirements.txt
echo   ✅ Utilise le Procfile
echo   ✅ Crée une base PostgreSQL
echo   ✅ Déploie en quelques minutes
echo.
echo 🌐 Votre API sera accessible sur :
echo    https://[votre-app].railway.app/api/
echo.
echo 📱 ANDROID : Remplacez l'URL dans ApiService.kt
echo.
echo ===============================================
echo   Appuyez sur une touche pour ouvrir Railway
echo ===============================================
pause >nul
start https://railway.app
echo.
echo Railway ouvert dans votre navigateur !
echo Suivez les étapes ci-dessus 👆
echo.
pause