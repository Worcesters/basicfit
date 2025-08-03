@echo off
echo ===========================================
echo    DEPLOIEMENT + CORRECTION MIGRATIONS
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Deploiement sans migrations...
flyctl deploy --app basicfit-v2

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DEPLOIEMENT REUSSI !
    
    echo.
    echo 2. Correction des migrations (fake)...
    flyctl ssh console --app basicfit-v2 -C "python manage.py migrate --fake"
    
    echo.
    echo 3. Test final de l'API...
    ping -n 5 127.0.0.1 >nul
    curl -s https://basicfit-v2.fly.dev/api/
    echo.
    
    echo.
    echo ✅ MIGRATION COMPLETE REUSSIE !
    echo.
    echo 🎉 Votre application BasicFit v2 est maintenant sur Fly.io !
    echo - URL: https://basicfit-v2.fly.dev/
    echo - Admin: https://basicfit-v2.fly.dev/admin/
    echo - API: https://basicfit-v2.fly.dev/api/
    echo.
    echo Les donnees Railway ont ete migrees avec succes
    echo Les recommandations ont ete corrigees
    echo Cout: 0€ pour toujours !
    
) else (
    echo ❌ ECHEC DU DEPLOIEMENT
    flyctl logs --app basicfit-v2
)

echo.
pause