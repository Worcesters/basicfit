"""
Configuration spécifique pour Railway - Autonome sans decouple
"""
import os
import sys
from pathlib import Path
import dj_database_url
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Django settings essentiels
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-railway-key-change-me')
DEBUG = False

# Hosts autorisés pour Railway
ALLOWED_HOSTS = [
    '.railway.app',
    'localhost',
    '127.0.0.1',
    '*'
]

# Applications Django
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.machines',
    'apps.workouts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

ROOT_URLCONF = 'basicfit_project.urls'
WSGI_APPLICATION = 'basicfit_project.wsgi.application'
AUTH_USER_MODEL = 'users.User'

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Templates
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

# Configuration CORS pour Railway
CORS_ALLOWED_ORIGINS = [
    "https://*.railway.app",
]
CORS_ALLOW_ALL_ORIGINS = True  # Pour le développement

# Configuration de la base de données Railway
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuration des fichiers statiques pour Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Middleware pour Railway
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

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuration JWT pour Railway
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# drf-spectacular Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'BasicFit API',
    'DESCRIPTION': 'API pour l\'application BasicFit',
    'VERSION': '1.0.0',
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuration des logs pour Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("Configuration Railway autonome chargée ✅")