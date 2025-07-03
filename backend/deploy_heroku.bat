@echo off
echo 🚀 Déploiement BasicFit sur Heroku
echo ====================================
echo.

REM Vérifier si git est initialisé
if not exist .git (
    echo 📂 Initialisation du repository Git...
    git init
    echo "# BasicFit API" > README.md
)

echo 📝 Configuration des variables d'environnement...
heroku config:set DJANGO_SETTINGS_MODULE=basicfit_project.settings.heroku
heroku config:set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%
heroku config:set DEBUG=False

echo 📦 Ajout des fichiers...
git add .
git commit -m "Deploy to Heroku"

echo 🚀 Déploiement vers Heroku...
git push heroku main

echo 📊 Migration de la base de données...
heroku run python manage.py migrate

echo 👤 Création du superutilisateur...
heroku run python manage.py createsuperuser --noinput --email admin@basicfit.com --username admin

echo ✅ Déploiement terminé !
echo.
echo 🌐 Votre API est disponible sur :
heroku open

pause