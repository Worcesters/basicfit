@echo off
echo ===========================================
echo    DEPLOIEMENT FINAL FLY.IO - HEALTH CHECK FIX
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Deploiement avec health check corrige...
flyctl deploy --app basicfit-v2

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DEPLOIEMENT REUSSI !
    
    echo.
    echo 2. Test de la page d'accueil...
    ping -n 5 127.0.0.1 >nul
    curl -s -w "Status: %%{http_code}\n" https://basicfit-v2.fly.dev/
    
    echo.
    echo 3. Test de l'API...
    curl -s -w "Status: %%{http_code}\n" https://basicfit-v2.fly.dev/api/users/
    
    echo.
    echo 🎉 MIGRATION RAILWAY → FLY.IO TERMINEE !
    echo.
    echo ✅ URLs disponibles:
    echo - Accueil: https://basicfit-v2.fly.dev/
    echo - Admin:   https://basicfit-v2.fly.dev/admin/
    echo - API:     https://basicfit-v2.fly.dev/api/
    echo.
    echo ✅ Android: Changez l'URL vers https://basicfit-v2.fly.dev/api/
    echo ✅ Cout: 0€ pour toujours sur Fly.io !
    
) else (
    echo ❌ ECHEC DU DEPLOIEMENT
    flyctl logs --app basicfit-v2 --no-tail
)

echo.
pause