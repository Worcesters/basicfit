@echo off
echo ===========================================
echo    EXPORT RAILWAY DB VIA DOCKER
echo ===========================================
echo.

cd /d "%~dp0"

echo Creation du dump Railway avec Docker...
echo.

docker run --rm -v "%CD%":/backup postgres:15 pg_dump "postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway" > /backup/railway_backup.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DUMP CREE AVEC SUCCES !
    echo Fichier: railway_backup.sql
    echo Taille:
    dir railway_backup.sql
    echo.
    echo Vous pouvez maintenant continuer avec Fly.io
) else (
    echo.
    echo ❌ ERREUR lors du dump Docker
    echo Verifiez que Docker est lance
)

echo.
pause