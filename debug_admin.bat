@echo off
echo ===========================================
echo    DEBUG ADMIN 500 ERROR
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification des logs d'erreur...
flyctl logs --app basicfit-v2 --no-tail

echo.
echo 2. Test collectstatic...
flyctl ssh console --app basicfit-v2 -C "python manage.py collectstatic --noinput"

echo.
echo 3. Verification des permissions...
flyctl ssh console --app basicfit-v2 -C "ls -la staticfiles/"

echo.
pause