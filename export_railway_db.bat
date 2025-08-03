@echo off
echo ===========================================
echo    EXPORT BASE DE DONNEES RAILWAY
echo ===========================================
echo.

cd /d "%~dp0"

echo Creation du dump de la base Railway...
echo.

pg_dump "postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway" > railway_backup.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ DUMP CREE AVEC SUCCES !
    echo Fichier: railway_backup.sql
    echo Taille:
    dir railway_backup.sql
    echo.
    echo Vous pouvez maintenant continuer avec la migration Fly.io
    echo Lancez: migration_railway_to_flyio.bat
) else (
    echo.
    echo ❌ ERREUR lors de la creation du dump
    echo Verifiez que PostgreSQL client est installe:
    echo choco install postgresql
    echo.
    echo Ou telecharger depuis: https://www.postgresql.org/download/windows/
)

echo.
pause