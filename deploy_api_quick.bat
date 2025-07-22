@echo off
echo 🚀 DEPLOIEMENT RAPIDE API DJANGO
echo =================================

echo.
echo 📦 Déploiement sur Railway...

cd backend

echo 🔧 Vérification des dépendances...
if exist "requirements.txt" (
    echo ✅ requirements.txt trouvé
) else (
    echo ❌ requirements.txt manquant
    pause
    exit /b 1
)

echo.
echo 🚀 Déploiement sur Railway...
railway up

echo.
echo ✅ Déploiement terminé !
echo.
echo 🌐 Votre API est accessible sur : https://basicfitv2-production.up.railway.app
echo.

pause