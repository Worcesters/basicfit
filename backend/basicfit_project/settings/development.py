"""
Configuration de développement Django pour BasicFit
Railway utilise ce fichier par défaut, on redirige vers railway.py
"""

# Pour Railway : utiliser les settings de production
from .railway import *

# Override pour développement si nécessaire
DEBUG = False  # Garder False pour Railway
ALLOWED_HOSTS = ['*', '.railway.app', 'localhost', '127.0.0.1']