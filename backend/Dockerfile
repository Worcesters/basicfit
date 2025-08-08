# ---- Base Image ----
    FROM python:3.11-slim

    # ---- Environnement système ----
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1

    # ---- Dépendances système pour PostgreSQL, gettext, etc. ----
    RUN apt-get update && apt-get install -y \
        gcc \
        libpq-dev \
        gettext \
        && rm -rf /var/lib/apt/lists/*

    # ---- Dossier de travail ----
    WORKDIR /app

    # ---- Copier les dépendances Python ----
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # ---- Copier tout le projet ----
    COPY . .

    # ---- Rendre le script de démarrage exécutable ----
    RUN chmod +x entrypoint.sh

    # ---- Créer un utilisateur non-root ----
    RUN adduser --disabled-password --gecos '' appuser && \
        chown -R appuser:appuser /app
    USER appuser

    # ---- Port exposé pour Gunicorn ----
    EXPOSE 8000

    # ---- Point d'entrée ----
    CMD ["bash", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn basicfit_project.wsgi:application --bind 0.0.0.0:8000 --workers 1"]
