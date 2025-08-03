@echo off
echo ===========================================
echo    CORRECTION MIGRATIONS FLY.IO
echo ===========================================
echo.

cd /d "%~dp0"

echo Le probleme: migration 'image_gif' tente de creer une colonne qui existe deja
echo.

echo 1. Marquer les migrations comme appliquees (fake)...
flyctl ssh console --app basicfit-v2 -C "python manage.py migrate --fake"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ MIGRATIONS MARQUEES COMME APPLIQUEES !
    
    echo.
    echo 2. Verification statut migrations...
    flyctl ssh console --app basicfit-v2 -C "python manage.py showmigrations"
    
    echo.
    echo 3. Redemarrage de l'application...
    flyctl restart --app basicfit-v2
    
    echo.
    echo 4. Test de l'API...
    ping -n 6 127.0.0.1 >nul
    curl -s https://basicfit-v2.fly.dev/api/
    
    echo.
    echo ✅ CORRECTION TERMINEE !
    echo Application disponible: https://basicfit-v2.fly.dev/
    
) else (
    echo ❌ ERREUR lors de la correction
    echo Verifiez les logs:
    flyctl logs --app basicfit-v2
)

echo.
pause