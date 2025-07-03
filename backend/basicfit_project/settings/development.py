"""
Configuration de développement Django pour BasicFit
"""
from .base import *

# Debug activé en développement
DEBUG = True

# Hosts autorisés en développement
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Applications additionnelles pour le développement
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

# Middleware additionnel pour le développement
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# Configuration de la Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Configuration CORS plus permissive en développement
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Désactiver le cache en développement
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Configuration email pour développement (affichage console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging plus verbeux en développement
import copy
_LOGGING = copy.deepcopy(LOGGING)
_LOGGING['loggers']['apps']['level'] = 'DEBUG'
_LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING = _LOGGING