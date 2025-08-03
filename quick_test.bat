@echo off
echo ===========================================
echo    TEST RAPIDE - DIAGNOSTIC 503
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Status application...
flyctl status --app basicfit-v2

echo.
echo 2. Test SSH direct pour verifier Django...
flyctl ssh console --app basicfit-v2 -C "curl -I http://localhost:8000/"

echo.
echo 3. Test des variables d'environnement...
flyctl ssh console --app basicfit-v2 -C "python manage.py check --deploy"

echo.
pause