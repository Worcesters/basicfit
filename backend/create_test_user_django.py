#!/usr/bin/env python3
"""
Créer un utilisateur de test via Django
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User

def create_test_user():
    try:
        # Supprimer l'ancien utilisateur s'il existe
        User.objects.filter(email='test@example.com').delete()
        
        # Créer un nouvel utilisateur de test
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        
        print(f"[SUCCESS] Utilisateur créé: {user.email} (ID: {user.id})")
        
        # Vérifier que le mot de passe fonctionne
        if user.check_password('test123'):
            print(f"[VERIFY] Mot de passe vérifié avec succès")
        else:
            print(f"[ERROR] Problème avec le mot de passe")
        
        return user
        
    except Exception as e:
        print(f"[ERROR] Erreur création utilisateur: {e}")
        return None

if __name__ == '__main__':
    user = create_test_user()
    if user:
        print(f"Utilisateur prêt pour les tests: {user.email}")
    else:
        print("Échec création utilisateur")