@echo off
echo ===========================================
echo    MIGRATION BASE DE DONNEES FLY.IO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Execution des migrations Django...
flyctl ssh console --app basicfit-v2 -C "python manage.py migrate --noinput"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ MIGRATIONS REUSSIES !
    
    echo.
    echo 2. Creation du superuser...
    flyctl ssh console --app basicfit-v2 -C "python manage.py shell -c \"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@basicfit.com', 'admin')
    print('Superuser cree avec succes')
else:
    print('Superuser existe deja')
\""
    
    echo.
    echo 3. Import des machines (si necessaire)...
    flyctl ssh console --app basicfit-v2 -C "python manage.py import_machines || echo 'Import machines non necessaire'"
    
    echo.
    echo ✅ CONFIGURATION TERMINEE !
    echo Admin disponible: https://basicfit-v2.fly.dev/admin/
    echo Login: admin / admin
    
) else (
    echo ❌ ERREUR lors des migrations
    echo Verifiez les logs:
    flyctl logs --app basicfit-v2
)

echo.
pause