@echo off
echo 🚀 DEPLOIEMENT COMPLET BASICFIT V2
echo ======================================

echo.
echo 📦 Déploiement de l'API Django sur Railway...
echo.

cd backend

echo 🔧 Installation des dépendances...
pip install -r requirements.txt

echo.
echo 🗄️ Migration de la base de données...
python manage.py migrate

echo.
echo 📊 Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo.
echo 🚀 Déploiement sur Railway...
railway up

echo.
echo ✅ Déploiement terminé !
echo.
echo 🌐 Votre API est accessible sur : https://basicfitv2-production.up.railway.app
echo.
echo 📱 L'APK Android sera disponible dans : android/app/build/outputs/apk/debug/
echo.

pause