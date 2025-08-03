@echo off
echo ===========================================
echo    DIAGNOSTIC 503 - VERIFICATION STATUS
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Status des machines...
flyctl status --app basicfit-v2

echo.
echo 2. Logs en temps reel...
flyctl logs --app basicfit-v2 --no-tail

echo.
echo 3. Redemarrage de l'application...
flyctl apps restart basicfit-v2

echo.
pause