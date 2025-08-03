@echo off
echo ===========================================
echo    BUILD ANDROID CLEAN - NOUVELLE URL FLY.IO
echo ===========================================
echo.

cd /d "%~dp0\android"

echo 1. Nettoyage complet du cache...
./gradlew clean

echo.
echo 2. Nettoyage cache Gradle...
./gradlew cleanBuildCache

echo.
echo 3. Build APK debug sans cache...
./gradlew assembleDebug --no-build-cache --rerun-tasks

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ APK COMPILE AVEC SUCCES !
    echo.
    echo APK disponible dans:
    echo android\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo ✅ L'application Android pointe maintenant vers:
    echo https://basicfit-v2.fly.dev/api/
    echo.
    echo 🎉 Migration Railway → Fly.io terminée !
) else (
    echo ❌ ERREUR lors de la compilation
)

echo.
pause