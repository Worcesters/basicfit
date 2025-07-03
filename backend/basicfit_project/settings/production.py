"""
Configuration de production Django pour BasicFit
"""
from .base import *

# Debug désactivé en production
DEBUG = False

# Hosts autorisés en production (à configurer selon l'environnement)
ALLOWED_HOSTS = [
    'basicfit-api.herokuapp.com',  # Exemple pour Heroku
    'localhost',
    '127.0.0.1',
]

# Configuration CORS stricte en production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://basicfit-app.com",  # Remplacer par le domaine de production
]

# Configuration du cache Redis en production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Configuration email en production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Sécurité renforcée en production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuration HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuration des fichiers statiques pour production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'