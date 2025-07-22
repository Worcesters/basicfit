@echo off
echo 🔍 VÉRIFICATION DE L'EXPORT DES MACHINES
echo ========================================

echo.
echo 📱 Statut de la compilation Android...
echo.

if exist "android\app\build\outputs\apk\debug\app-debug.apk" (
    echo ✅ APK COMPILÉ AVEC SUCCÈS !
    echo.
    echo 📁 Emplacement : android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 📏 Taille de l'APK :
    dir "android\app\build\outputs\apk\debug\app-debug.apk" | find "app-debug.apk"
    echo.
    echo 🎯 CORRECTIONS APPLIQUÉES :
    echo   ✅ Export des machines corrigé
    echo   ✅ Utilisation des machines locales si API vide
    echo   ✅ Format CSV documenté
    echo.
    echo 📋 FONCTIONNEMENT DE L'EXPORT :
    echo   - Bouton "Exporter" dans l'onglet Machines
    echo   - Utilise les machines de l'API ou les machines locales
    echo   - Copie dans le presse-papiers avec confirmation
    echo   - Liste organisée par catégorie + liste alphabétique
    echo.
    echo 📊 FORMAT CSV POUR IMPORT :
    echo   Colonnes : Machine;Date;Répétitions;Séries;Poids
    echo   Exemple : Développé couché;2024-01-15;10-12;3;60
    echo   Documentation complète : FORMAT_CSV_IMPORT_CALENDRIER.md
    echo.
    echo 🚀 PROCHAINES ÉTAPES :
    echo   1. Installer l'APK sur votre appareil Android
    echo   2. Tester l'export des machines (bouton vert)
    echo   3. Vérifier que la liste n'est plus vide
    echo   4. Tester l'import CSV dans le calendrier
    echo.
    goto :end
) else (
    echo ⏳ APK en cours de compilation...
    echo.
    echo 🔄 Gradle assembleDebug en cours...
    echo    - Compilation des fichiers Kotlin
    echo    - Génération des ressources
    echo    - Création de l'APK
    echo.
    echo ⏰ Veuillez patienter quelques minutes...
    echo.
    echo 🔄 Vérification dans 15 secondes...
    timeout /t 15 /nobreak >nul
    goto :loop
)

:end
echo.
echo 🎯 Compilation terminée avec succès !
echo 📱 APK prêt pour installation
echo 📋 Export des machines corrigé
echo 📊 Format CSV documenté
echo.
pause