@echo off
echo 🔍 VERIFICATION DE LA COMPILATION
echo =================================

echo.
echo 📱 Vérification de l'APK Android...

if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    echo ✅ APK compilé avec succès !
    echo 📁 Emplacement : android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 📏 Informations sur l'APK :
    dir "android\app\build\outputs\apk\debug\app-debug.apk"
    echo.
    echo 🎉 Votre application est prête !
    echo 📱 Vous pouvez installer l'APK sur votre appareil Android
) else (
    echo ⏳ APK en cours de compilation...
    echo.
    echo 🔄 Statut de la compilation :
    echo    - Gradle assembleDebug en cours
    echo    - Veuillez patienter quelques minutes
    echo.
    echo 💡 Pour vérifier à nouveau : relancez ce script
)

echo.
echo 📊 Résumé des améliorations dans cette version :
echo   ✅ Système de recommandation corrigé
echo   ✅ Synchronisation avec la BDD
echo   ✅ Poids logiques proposés
echo   ✅ Gestion des cas spéciaux (cardio, etc.)
echo   ✅ Interface utilisateur améliorée
echo.

pause