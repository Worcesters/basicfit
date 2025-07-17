#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User

def create_test_user():
    """Créer un utilisateur de test"""
    username = "test@example.com"
    email = "test@example.com"
    password = "testpass123"

    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        print(f"✅ L'utilisateur {username} existe déjà")
        user = User.objects.get(username=username)
        # Mettre à jour le mot de passe
        user.set_password(password)
        user.save()
        print("✅ Mot de passe mis à jour")
    else:
        # Créer un nouvel utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name="Test",
            last_name="User"
        )
        print(f"✅ Utilisateur {username} créé avec succès")

    return user

if __name__ == "__main__":
    print("🔧 Création de l'utilisateur de test...")
    user = create_test_user()
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Nom: {user.first_name} {user.last_name}")
    print("✅ Terminé!")