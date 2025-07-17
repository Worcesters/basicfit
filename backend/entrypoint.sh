#!/bin/sh

echo "📦 Collecte des fichiers statiques"
python manage.py collectstatic --noinput

echo "⚙️ Application des migrations"
python manage.py migrate --noinput --run-syncdb
echo "🔧 Vérification des migrations machines"
python manage.py migrate machines --noinput

echo "👤 Création du superuser si nécessaire"
python manage.py shell << END
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print("✅ Superuser créé :", username)
    else:
        print("ℹ️ Superuser déjà existant :", username)
else:
    print("⚠️ Variables DJANGO_SUPERUSER_* manquantes")
END

echo "🚀 Démarrage du serveur"
exec gunicorn --bind 0.0.0.0:8000 --workers 3 basicfit_project.wsgi:application
