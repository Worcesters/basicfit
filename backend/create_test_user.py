#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth.models import User

def create_test_user():
    """Crée un utilisateur de test"""
    username = "testuser"
    email = "test@example.com"
    password = "testpass123"

    try:
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"✅ L'utilisateur '{username}' existe déjà")
            return True

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name="Test",
            last_name="User"
        )

        print(f"✅ Utilisateur '{username}' créé avec succès")
        print(f"   Email: {email}")
        print(f"   Mot de passe: {password}")
        return True

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return False

if __name__ == "__main__":
    create_test_user()