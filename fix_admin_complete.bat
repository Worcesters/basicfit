@echo off
echo ===========================================
echo    REPARATION COMPLETE ADMIN DJANGO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Connexion SSH pour reparation...
flyctl ssh console --app basicfit-v2

echo.
pause