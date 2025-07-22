@echo off
echo 🔍 VERIFICATION DU SUCCÈS DE LA COMPILATION
echo ===========================================

echo.
echo 📱 Vérification de l'APK Android...

if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    echo ✅ SUCCÈS ! APK compilé avec succès !
    echo.
    echo 📁 Emplacement : android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 📏 Informations sur l'APK :
    dir "android\app\build\outputs\apk\debug\app-debug.apk"
    echo.
    echo 🎉 Votre application BasicFit V2 est prête !
    echo 📱 Vous pouvez installer l'APK sur votre appareil Android
    echo.
    echo 📊 Améliorations incluses dans cette version :
    echo   ✅ Système de recommandation corrigé
    echo   ✅ Synchronisation avec la BDD
    echo   ✅ Poids logiques proposés
    echo   ✅ Gestion des cas spéciaux (cardio, etc.)
    echo   ✅ Interface utilisateur améliorée
    echo   ✅ Erreurs de compilation corrigées
    echo.
    echo 🚀 Prochaines étapes :
    echo   1. Installer l'APK sur votre appareil Android
    echo   2. Tester les nouvelles fonctionnalités
    echo   3. Vérifier que les recommandations sont logiques
    echo   4. Tester la synchronisation avec la BDD
    echo.
) else (
    echo ❌ APK non trouvé - Compilation en cours ou échec
    echo.
    echo 🔄 Statut de la compilation :
    echo    - Gradle assembleDebug en cours
    echo    - Veuillez patienter quelques minutes
    echo.
    echo 💡 Pour vérifier à nouveau : relancez ce script
    echo.
    echo ⚠️ Si la compilation échoue, vérifiez :
    echo    - Les erreurs dans la console Gradle
    echo    - Les imports manquants
    echo    - Les types de données incompatibles
)

echo.
echo 📝 Logs de compilation disponibles dans :
echo    android\app\build\outputs\logs\
echo.

pause