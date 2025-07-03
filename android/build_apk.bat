@echo off
echo 🔧 Compilation de l'application BasicFit v2...
echo.

REM Nettoyer le projet
echo ✨ Nettoyage du projet...
if exist "build" rd /s /q "build"
if exist "app\build" rd /s /q "app\build"

REM Télécharger Gradle si nécessaire
echo 📦 Vérification de Gradle...
if not exist "gradle\wrapper\gradle-wrapper.jar" (
    echo ⬇️ Téléchargement du wrapper Gradle...
    curl -L -o gradle\wrapper\gradle-wrapper.jar https://github.com/gradle/gradle/raw/v8.4.0/gradle/wrapper/gradle-wrapper.jar
)

REM Compiler l'APK
echo 🏗️ Compilation de l'APK...
call gradlew.bat assembleDebug

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Compilation réussie !
    echo 📱 APK généré : app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo 💡 Pour installer sur votre téléphone :
    echo 1. Activez le mode développeur et le débogage USB
    echo 2. Copiez l'APK sur votre téléphone
    echo 3. Installez-le depuis le gestionnaire de fichiers
    echo.
) else (
    echo.
    echo ❌ Erreur de compilation
    echo 💡 Utilisez Android Studio pour plus de détails
    echo.
)

pause