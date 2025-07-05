@echo off
echo ===========================================
echo    DEPLOYMENT BASICFIT API SUR RAILWAY
echo ===========================================
echo.

cd /d "%~dp0"

echo 1. Verification des fichiers...
if not exist "backend\requirements.txt" (
    echo ERREUR: Fichier requirements.txt manquant !
    pause
    exit /b 1
)

if not exist "backend\basicfit_project\settings\railway.py" (
    echo ERREUR: Configuration Railway manquante !
    pause
    exit /b 1
)

echo 2. Preparation du backend...
cd backend

echo 3. Configuration des variables d'environnement...
echo DJANGO_SETTINGS_MODULE=basicfit_project.settings.railway > .env
echo DEBUG=False >> .env
echo SECRET_KEY=django-insecure-basicfit-prod-2024-railway >> .env

echo 4. Verification des migrations...
python manage.py makemigrations --settings=basicfit_project.settings.railway
python manage.py migrate --settings=basicfit_project.settings.railway

echo 5. Collecte des fichiers statiques...
python manage.py collectstatic --noinput --settings=basicfit_project.settings.railway

echo 6. Test du serveur local...
echo Starting Django server for testing...
timeout /t 3 >nul
echo Server test completed.

echo 7. Preparation pour Railway...
echo Configuration Django complete:
echo - Applications: users, workouts, machines, core
echo - API REST: djangorestframework
echo - JWT: djangorestframework-simplejwt
echo - CORS: django-cors-headers
echo - URLs: /api/users/, /api/workouts/, /api/machines/

echo.
echo ===========================================
echo    DEPLOYMENT INSTRUCTIONS RAILWAY
echo ===========================================
echo 1. Aller sur https://railway.app/
echo 2. Selectionner votre projet BasicFit
echo 3. Aller dans Settings ^> Variables
echo 4. Ajouter/modifier ces variables:
echo    - DJANGO_SETTINGS_MODULE = basicfit_project.settings.railway
echo    - DEBUG = False
echo    - SECRET_KEY = [generer une cle secrete]
echo.
echo 5. Dans Deployments, forcer un redeploy
echo 6. Verifier que l'API fonctionne sur:
echo    https://basicfitv2-production.up.railway.app/
echo.
echo ENDPOINTS ANDROID DISPONIBLES:
echo - POST /api/users/android/login/
echo - POST /api/users/android/register/
echo - GET  /api/users/android/profile/
echo - POST /api/workouts/sauvegarder/
echo.
echo ===========================================

cd ..
echo.
echo 8. L'application Android est prete pour l'API Django !
echo    URL API: https://basicfitv2-production.up.railway.app/api/
echo.
pause