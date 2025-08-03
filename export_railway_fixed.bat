@echo off
echo ===========================================
echo    EXPORT RAILWAY DB VIA DOCKER (FIXED)
echo ===========================================
echo.

cd /d "%~dp0"

echo Creation du dump Railway avec Docker...
echo.

docker run --rm -v "%cd%:/backup" postgres:15 sh -c "pg_dump 'postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway' > /backup/railway_backup.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DUMP CREE AVEC SUCCES !
    echo Fichier: railway_backup.sql
    if exist railway_backup.sql (
        echo Taille:
        dir railway_backup.sql
    ) else (
        echo ❌ Fichier non trouve - probleme de creation
    )
) else (
    echo.
    echo ❌ ERREUR lors du dump Docker
)

echo.
pause