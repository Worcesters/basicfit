@echo off
echo 🔍 VERIFICATION DU STATUT DE CONSTRUCTION
echo =========================================

echo.
echo 📱 Vérification de l'APK Android...

if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    echo ✅ APK construit avec succès !
    echo 📁 Emplacement : android\app\build\outputs\apk\debug\app-debug.apk
    echo 📏 Taille :
    dir "android\app\build\outputs\apk\debug\app-debug.apk" | find "app-debug.apk"
) else (
    echo ❌ APK non trouvé - Construction en cours...
    echo.
    echo 🔄 Pour construire l'APK manuellement :
    echo    cd android
    echo    ./gradlew assembleDebug
)

echo.
echo 🌐 Vérification de l'API Django...

cd backend
if exist "manage.py" (
    echo ✅ Backend Django trouvé
    echo.
    echo 🔧 Pour déployer l'API :
    echo    railway up
) else (
    echo ❌ Backend Django non trouvé
)

echo.
echo 📊 Résumé du déploiement :
echo   1. APK Android : Construction en cours
echo   2. API Django : Prêt pour déploiement
echo.
echo 🚀 Pour déployer complètement :
echo   - Attendre la fin de la construction de l'APK
echo   - Exécuter deploy_complete.bat
echo.

pause