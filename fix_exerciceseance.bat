@echo off
echo ===========================================
echo    FIX EXERCICESEANCE ERROR 500
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification logs erreur ExerciceSeance...
flyctl logs --app basicfit-v2 --no-tail | findstr "exerciceseance"

echo.
echo 2. Connexion SSH pour debug...
flyctl ssh console --app basicfit-v2

echo.
pause