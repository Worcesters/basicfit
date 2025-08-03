@echo off
echo ===========================================
echo    DIAGNOSTIC DEPLOYMENT FLY.IO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification statut application...
flyctl status --app basicfit-v2
echo.

echo 2. Verification logs...
flyctl logs --app basicfit-v2
echo.

echo 3. Test santé de l'application...
echo Tentative de connexion a l'API...
curl -v https://basicfit-v2.fly.dev/api/
echo.

echo 4. Test admin Django...
curl -v https://basicfit-v2.fly.dev/admin/
echo.

echo 5. Verification secrets...
flyctl secrets list --app basicfit-v2
echo.

echo 6. Verification base de donnees...
flyctl postgres list --org personal
echo.

echo ===========================================
echo    DIAGNOSTIC TERMINE
echo ===========================================
echo.
pause