"""
Configuration Railway ULTRA-MINIMALE - Django + DRF seulement
"""
import os
from pathlib import Path
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ajouter le dossier apps au Python path
import sys
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Django settings essentiels
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-railway-minimal')
DEBUG = False
ALLOWED_HOSTS = ['*']

# Applications MINIMALES + apps locales
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    # Apps locales nécessaires
    'apps.core',
    'apps.users',
    'apps.machines',
    'apps.workouts',
]

# Middleware minimal
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'basicfit_project.urls'
WSGI_APPLICATION = 'basicfit_project.wsgi.application'

# Modèle User personnalisé
AUTH_USER_MODEL = 'users.User'

# Templates minimal
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database Railway
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3'
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# CORS basique
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework BASIQUE (sans JWT)
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Default field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

print("Configuration Railway MINIMALE chargée ")
