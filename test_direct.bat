@echo off
echo ===========================================
echo    TEST DIRECT DJANGO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Test Django direct avec wget...
flyctl ssh console --app basicfit-v2 -C "wget -qO- http://localhost:8000/ || echo 'Erreur Django'"

echo.
echo 2. Test API users...
flyctl ssh console --app basicfit-v2 -C "wget -qO- http://localhost:8000/api/users/ || echo 'Erreur API'"

echo.
echo 3. Verification processus...
flyctl ssh console --app basicfit-v2 -C "ps aux | grep gunicorn"

echo.
pause