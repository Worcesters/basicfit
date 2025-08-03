"""
Configuration de développement Django pour BasicFit
"""

# Utiliser les settings de base et production pour développement local
from .base import *
from .production import *

# Override pour développement local
DEBUG = True
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

# Base de données SQLite pour développement local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}