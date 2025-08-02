# Dockerfile pour BasicFit v2 - Fly.io
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=basicfit_project.settings.flyio

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation des dépendances Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY backend/ .

# Création des répertoires nécessaires
RUN mkdir -p logs staticfiles media

# Collection des fichiers statiques
RUN python manage.py collectstatic --noinput --settings=basicfit_project.settings.flyio

# Exposition du port
EXPOSE 8000

# Commande par défaut
CMD ["gunicorn", "basicfit_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]