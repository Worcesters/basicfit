@echo off
echo ===========================================
echo    EXPORT RAILWAY DB VIA DOCKER (PG16)
echo ===========================================
echo.

cd /d "%~dp0"

echo Creation du dump Railway avec PostgreSQL 16...
echo.

docker run --rm -v "%cd%:/backup" postgres:16 sh -c "pg_dump 'postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway' > /backup/railway_backup_latest.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DUMP CREE AVEC SUCCES !
    echo Fichier: railway_backup_latest.sql
    if exist railway_backup_latest.sql (
        echo Taille:
        dir railway_backup_latest.sql
    ) else (
        echo ❌ Fichier non trouve - probleme de creation
    )
) else (
    echo.
    echo ❌ ERREUR lors du dump Docker
)

echo.
pause