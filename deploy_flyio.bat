@echo off
echo ===========================================
echo    DEPLOYMENT BASICFIT V2 SUR FLY.IO
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification des fichiers...
if not exist "fly.toml" (
    echo ERREUR: Configuration fly.toml manquante !
    pause
    exit /b 1
)

if not exist "Dockerfile" (
    echo ERREUR: Dockerfile manquant !
    pause
    exit /b 1
)

if not exist "backend\basicfit_project\settings\flyio.py" (
    echo ERREUR: Configuration Django pour Fly.io manquante !
    pause
    exit /b 1
)

echo 2. Verification de Fly CLI...
flyctl version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Fly CLI n'est pas installe !
    echo Installez-le depuis: https://fly.io/docs/hands-on/install-flyctl/
    pause
    exit /b 1
)

echo 3. Connexion a Fly.io...
flyctl auth whoami >nul 2>&1
if errorlevel 1 (
    echo Connexion requise...
    flyctl auth login
)

echo 4. Creation de l'application Fly.io (si necessaire)...
flyctl apps list | findstr "basicfit-v2" >nul 2>&1
if errorlevel 1 (
    echo Creation de l'application basicfit-v2...
    flyctl apps create basicfit-v2 --org personal
)

echo 5. Creation de la base de donnees PostgreSQL...
flyctl postgres list | findstr "basicfit-v2-db" >nul 2>&1
if errorlevel 1 (
    echo Creation de la base PostgreSQL...
    flyctl postgres create --name basicfit-v2-db --region cdg
    echo Attendre la creation de la DB...
    timeout /t 30 >nul
    
    echo Attachement de la DB a l'application...
    flyctl postgres attach --app basicfit-v2 basicfit-v2-db
)

echo 6. Configuration des secrets...
echo Configuration des variables d'environnement securisees...
flyctl secrets set SECRET_KEY=django-insecure-basicfit-prod-flyio-2024-key --app basicfit-v2
flyctl secrets set DEBUG=False --app basicfit-v2
flyctl secrets set DJANGO_SETTINGS_MODULE=basicfit_project.settings.flyio --app basicfit-v2

echo 7. Premier deploiement...
echo Deploiement de l'application...
flyctl deploy --app basicfit-v2

echo 8. Verification du deploiement...
echo Test de l'API...
timeout /t 10 >nul
flyctl status --app basicfit-v2

echo.
echo ===========================================
echo    DEPLOYMENT FLY.IO TERMINE !
echo ===========================================
echo.
echo L'application est deployee sur:
echo https://basicfit-v2.fly.dev/
echo.
echo API Endpoints disponibles:
echo - https://basicfit-v2.fly.dev/api/
echo - https://basicfit-v2.fly.dev/api/users/android/login/
echo - https://basicfit-v2.fly.dev/api/users/android/register/
echo.
echo COMMANDES UTILES:
echo - flyctl logs --app basicfit-v2
echo - flyctl ssh console --app basicfit-v2
echo - flyctl postgres connect --app basicfit-v2-db
echo.
echo Pour mettre a jour Android, changez l'URL API vers:
echo https://basicfit-v2.fly.dev/
echo.
pause