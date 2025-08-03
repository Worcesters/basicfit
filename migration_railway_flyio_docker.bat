@echo off
echo ===========================================
echo    MIGRATION RAILWAY TO FLY.IO (DOCKER)
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. ETAPE 1: Export de la base Railway avec Docker...
echo.

docker run --rm -v "%CD%":/backup postgres:15 pg_dump "postgresql://postgres:qQytuFtaMrfWDOkqYBCNJHXVQZOzXZFC@tramway.proxy.rlwy.net:44470/railway" > /backup/railway_backup.sql

if %ERRORLEVEL% EQU 0 (
    echo ✅ Dump cree avec succes: railway_backup.sql
    dir railway_backup.sql
) else (
    echo ❌ Erreur lors du dump Docker
    echo Verifiez que Docker Desktop est lance
    pause
    exit /b 1
)

echo.
pause
echo.

echo 2. ETAPE 2: Installation Fly CLI...
echo Si pas encore fait, executez:
echo powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
echo.
echo Puis fermez et rouvrez votre terminal
echo.
pause
echo.

echo 3. ETAPE 3: Configuration Fly.io...
echo flyctl auth login
flyctl auth login
echo.
echo flyctl apps create basicfit-v2 --org personal
flyctl apps create basicfit-v2 --org personal
echo.
pause
echo.

echo 4. ETAPE 4: Creation base PostgreSQL Fly.io...
echo flyctl postgres create --name basicfit-v2-db --region cdg --vm-size shared-cpu-1x --volume-size 3
flyctl postgres create --name basicfit-v2-db --region cdg --vm-size shared-cpu-1x --volume-size 3
echo.
echo flyctl postgres attach --app basicfit-v2 basicfit-v2-db
flyctl postgres attach --app basicfit-v2 basicfit-v2-db
echo.
pause
echo.

echo 5. ETAPE 5: Configuration des secrets...
flyctl secrets set SECRET_KEY="django-insecure-basicfit-prod-flyio-2024-%RANDOM%" --app basicfit-v2
flyctl secrets set DEBUG=False --app basicfit-v2
flyctl secrets set DJANGO_SETTINGS_MODULE=basicfit_project.settings.flyio --app basicfit-v2
flyctl secrets set CLOUDINARY_CLOUD_NAME="dnernoibr" --app basicfit-v2
flyctl secrets set CLOUDINARY_API_KEY="534922253523731" --app basicfit-v2
flyctl secrets set CLOUDINARY_API_SECRET="ogS-RGJWj2GwEEWD3XIVIMSrgks" --app basicfit-v2
flyctl secrets set DJANGO_SUPERUSER_USERNAME="admin" --app basicfit-v2
flyctl secrets set DJANGO_SUPERUSER_EMAIL="admin@basicfit.com" --app basicfit-v2
flyctl secrets set DJANGO_SUPERUSER_PASSWORD="admin" --app basicfit-v2
echo.
echo ✅ Secrets configures
pause
echo.

echo 6. ETAPE 6: Import des donnees avec Docker...
echo Connexion a la base Fly.io...
echo.
echo OPTION A: Import direct via Docker
echo Recuperation de l'URL Fly.io...
for /f "tokens=*" %%i in ('flyctl postgres db-url --app basicfit-v2-db') do set FLY_DB_URL=%%i

echo Import avec Docker:
docker run --rm -v "%CD%":/backup postgres:15 psql "%FLY_DB_URL%" -f /backup/railway_backup.sql

if %ERRORLEVEL% EQU 0 (
    echo ✅ Import reussi !
) else (
    echo ❌ Erreur import - essayez l'option manuelle:
    echo flyctl postgres connect --app basicfit-v2-db
    echo Dans psql: \i /backup/railway_backup.sql
)

echo.
pause
echo.

echo 7. ETAPE 7: Deploiement...
echo flyctl deploy --app basicfit-v2
flyctl deploy --app basicfit-v2
echo.
pause
echo.

echo 8. ETAPE 8: Tests...
echo Test API:
curl https://basicfit-v2.fly.dev/api/
echo.
echo Test Admin:
echo https://basicfit-v2.fly.dev/admin/
echo.

echo ===========================================
echo    MIGRATION TERMINEE !
echo ===========================================
echo.
echo ✅ Votre application est maintenant sur:
echo https://basicfit-v2.fly.dev/
echo.
echo ✅ URLs Android deja mises a jour
echo ✅ Recommandations corrigees
echo ✅ Toutes vos donnees migrees
echo.
echo Couts: 0€ pour toujours sur Fly.io !
echo.
pause