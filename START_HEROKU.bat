@echo off
title BasicFit - Déploiement Heroku
color 0A
echo.
echo 🚀 BASICFIT v2 - DEPLOIEMENT HEROKU
echo ====================================
echo.
echo 📋 Avant de commencer, assurez-vous d'avoir :
echo    ✅ Un compte Heroku (heroku.com)
echo    ✅ Heroku CLI installé
echo    ✅ Git installé
echo.
pause
echo.

REM Vérifier Heroku CLI
echo 🔍 Vérification Heroku CLI...
heroku --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Heroku CLI non trouvé !
    echo.
    echo 📥 Téléchargez-le sur : https://devcenter.heroku.com/articles/heroku-cli
    echo    Puis relancez ce script.
    pause
    exit /b 1
)

echo ✅ Heroku CLI trouvé !
echo.

REM Vérifier Git
echo 🔍 Vérification Git...
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git non trouvé !
    echo.
    echo 📥 Téléchargez-le sur : https://git-scm.com
    echo    Puis relancez ce script.
    pause
    exit /b 1
)

echo ✅ Git trouvé !
echo.

REM Connexion à Heroku
echo 🔐 Connexion à Heroku...
echo    ⚠️  Votre navigateur va s'ouvrir
pause
heroku login

echo.
echo 🎯 Étape suivante : Créer votre app Heroku
echo.
echo 💡 Choisissez un nom unique pour votre app :
echo    Exemple : basicfit-jeremy, basicfit-marie, etc.
echo.
set /p APP_NAME="🏷️  Nom de votre app Heroku : basicfit-"

echo.
echo 🚀 Création de l'app Heroku...
cd backend
heroku create basicfit-%APP_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Erreur lors de la création !
    echo    Le nom est peut-être déjà pris.
    echo    Relancez le script avec un autre nom.
    pause
    exit /b 1
)

echo.
echo ✅ App créée : basicfit-%APP_NAME%
echo.
echo 📖 Suite du déploiement :
echo    1. Ouvrez GUIDE_HEROKU.md
echo    2. Suivez les étapes 6 à 10
echo.
echo 🌐 Votre future URL sera :
echo    https://basicfit-%APP_NAME%.herokuapp.com
echo.

echo 📱 N'oubliez pas de modifier l'app Android :
echo    BASE_URL = "https://basicfit-%APP_NAME%.herokuapp.com/"
echo.

pause