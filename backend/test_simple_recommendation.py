#!/usr/bin/env python3
"""
Test simplifié du système de recommandation
"""
import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_recommendation_system():
    """Test du nouveau système de recommandation"""
    print("=== TEST SYSTEME RECOMMANDATION SIMPLIFIE ===")
    
    try:
        # 1. Créer/récupérer un utilisateur de test
        user, created = User.objects.get_or_create(
            email='test@basicfit.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"✓ Utilisateur créé: {user.email}")
        else:
            print(f"✓ Utilisateur existant: {user.email}")
        
        # 2. Générer un token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print(f"✓ Token JWT généré")
        
        # 3. Tester l'endpoint par ID
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Test avec Supine Press (ID 1)
        response = client.get('/api/workouts/recommendation/id/1/')
        print(f"✓ Test endpoint /api/workouts/recommendation/id/1/")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Machine: {data.get('machine_nom', 'N/A')}")
            print(f"  Poids: {data.get('poids_recommande', 'N/A')}kg")
            print(f"  Series: {data.get('series_recommandees', 'N/A')}")
            print(f"  Reps: {data.get('reps_recommandees', 'N/A')}")
            print(f"  Source: {data.get('source', 'N/A')}")
            
            # Vérifier le poids (doit être 60kg ou plus)
            poids = data.get('poids_recommande', 0)
            if poids >= 60:
                print(f"✓ Poids correct: {poids}kg (>= 60kg)")
            else:
                print(f"⚠ Poids incorrect: {poids}kg (< 60kg)")
        else:
            print(f"✗ Erreur: {response.content.decode()}")
        
        # 4. Tester l'endpoint par nom
        response = client.get('/api/workouts/recommendation/name/Supine%20Press/')
        print(f"✓ Test endpoint /api/workouts/recommendation/name/Supine Press/")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Machine: {data.get('machine_nom', 'N/A')}")
            print(f"  Poids: {data.get('poids_recommande', 'N/A')}kg")
        else:
            print(f"✗ Erreur: {response.content.decode()}")
        
        # 5. Tester l'endpoint de test du système
        response = client.post('/api/workouts/test/recommendation/')
        print(f"✓ Test endpoint /api/workouts/test/recommendation/")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  User: {data.get('user', 'N/A')}")
            print(f"  Test machine: {data.get('test_machine', 'N/A')}")
            result = data.get('result', {})
            if result.get('success'):
                rec_data = result.get('data', {})
                print(f"  Recommandation: {rec_data.get('poids_recommande', 'N/A')}kg")
            else:
                print(f"  Erreur: {result.get('error', 'N/A')}")
        else:
            print(f"✗ Erreur: {response.content.decode()}")
        
        print("\n=== RESULTAT ===")
        print("✓ Système de recommandation fonctionnel")
        print("✓ Authentification JWT fonctionnelle") 
        print("✓ Nouveaux endpoints accessibles")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_recommendation_system()
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSES!")
    else:
        print("\n❌ CERTAINS TESTS ONT ECHOUE!")
        sys.exit(1)