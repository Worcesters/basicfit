#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.flyio')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Données du superutilisateur
email = 'admin@basicfit.com'
password = 'admin123'

# Supprimer l'utilisateur existant s'il existe
if User.objects.filter(email=email).exists():
    User.objects.filter(email=email).delete()
    print(f"Utilisateur existant {email} supprimé")

# Créer le superutilisateur
user = User.objects.create_superuser(
    username='admin',
    email=email,
    password=password,
    nom='Admin',
    prenom='System'
)

print(f"Superutilisateur créé avec succès:")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"Is superuser: {user.is_superuser}")
print(f"Is staff: {user.is_staff}")