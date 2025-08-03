@echo off
echo ===========================================
echo    MIGRATION RAILWAY TO FLY.IO - BASICFIT
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. ETAPE 1: Export de la base Railway...
echo Execution du dump automatique...
echo.
pg_dump "postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway" > railway_backup.sql

if %ERRORLEVEL% EQU 0 (
    echo ✅ Dump cree avec succes: railway_backup.sql
    dir railway_backup.sql
) else (
    echo ❌ Erreur lors du dump - verifiez PostgreSQL client
    pause
    exit /b 1
)
echo.
pause
echo.

echo 2. ETAPE 2: Installation Fly CLI (si pas fait)...
echo powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
echo.
pause
echo.

echo 3. ETAPE 3: Configuration Fly.io...
echo flyctl auth login
echo flyctl apps create basicfit-v2 --org personal
echo.
pause
echo.

echo 4. ETAPE 4: Creation base PostgreSQL Fly.io...
echo flyctl postgres create --name basicfit-v2-db --region cdg --vm-size shared-cpu-1x --volume-size 3
echo flyctl postgres attach --app basicfit-v2 basicfit-v2-db
echo.
pause
echo.

echo 5. ETAPE 5: Configuration des secrets...
echo flyctl secrets set SECRET_KEY="django-insecure-basicfit-prod-flyio-2024-%RANDOM%" --app basicfit-v2
echo flyctl secrets set DEBUG=False --app basicfit-v2
echo flyctl secrets set DJANGO_SETTINGS_MODULE=basicfit_project.settings.flyio --app basicfit-v2
echo flyctl secrets set CLOUDINARY_CLOUD_NAME="dnernoibr" --app basicfit-v2
echo flyctl secrets set CLOUDINARY_API_KEY="534922253523731" --app basicfit-v2
echo flyctl secrets set CLOUDINARY_API_SECRET="ogS-RGJWj2GwEEWD3XIVIMSrgks" --app basicfit-v2
echo flyctl secrets set DJANGO_SUPERUSER_USERNAME="admin" --app basicfit-v2
echo flyctl secrets set DJANGO_SUPERUSER_EMAIL="admin@basicfit.com" --app basicfit-v2
echo flyctl secrets set DJANGO_SUPERUSER_PASSWORD="admin" --app basicfit-v2
echo.
pause
echo.

echo 6. ETAPE 6: Import des donnees...
echo flyctl postgres connect --app basicfit-v2-db
echo Dans psql: \i C:/Users/jerem/OneDrive/Documents/Basicfitv2/railway_backup.sql
echo.
pause
echo.

echo 7. ETAPE 7: Deploiement...
echo flyctl deploy --app basicfit-v2
echo.
pause
echo.

echo 8. ETAPE 8: Tests...
echo curl https://basicfit-v2.fly.dev/api/
echo curl https://basicfit-v2.fly.dev/admin/
echo.

echo ===========================================
echo    MIGRATION TERMINEE !
echo ===========================================
echo.
echo Votre application est maintenant sur:
echo https://basicfit-v2.fly.dev/
echo.
echo Les URLs Android ont deja ete mises a jour.
echo.
pause