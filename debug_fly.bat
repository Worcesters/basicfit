@echo off
echo ===========================================
echo    DEBUG FLY.IO - DIAGNOSTIC COMPLET
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Logs complets de l'application...
flyctl logs --app basicfit-v2

echo.
echo 2. Statut des machines...
flyctl status --app basicfit-v2

echo.
echo 3. Liste des secrets configures...
flyctl secrets list --app basicfit-v2

echo.
echo 4. Test connexion base de donnees...
flyctl ssh console --app basicfit-v2 -C "python manage.py check --database default"

echo.
echo 5. Test Django settings...
flyctl ssh console --app basicfit-v2 -C "python manage.py check"

echo.
pause