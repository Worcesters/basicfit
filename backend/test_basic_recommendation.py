#!/usr/bin/env python3
"""
Test basique du système de recommandation
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_basic_recommendation():
    """Test basique du système de recommandation"""
    print("=== TEST BASIQUE DU SYSTEME DE RECOMMANDATION ===")
    
    try:
        # 1. Récupérer un utilisateur existant ou utiliser le premier
        user = User.objects.first()
        if not user:
            print("ERREUR: Aucun utilisateur trouvé dans la base")
            return False
            
        print(f"Utilisateur: {user.email}")
        
        # 2. Générer un token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        print("Token JWT genere")
        
        # 3. Tester l'endpoint
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Test avec Supine Press (ID 1)
        print("Test endpoint /api/workouts/recommendation/id/1/")
        response = client.get('/api/workouts/recommendation/id/1/')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Machine: {data.get('machine_nom', 'N/A')}")
            print(f"Poids: {data.get('poids_recommande', 'N/A')}kg")
            print(f"Series: {data.get('series_recommandees', 'N/A')}")
            print(f"Reps: {data.get('reps_recommandees', 'N/A')}")
            print(f"Source: {data.get('source', 'N/A')}")
            
            # Vérifier le poids
            poids = data.get('poids_recommande', 0)
            if poids >= 20:  # Au moins 20kg
                print(f"OK: Poids correct: {poids}kg")
                return True
            else:
                print(f"ERREUR: Poids trop faible: {poids}kg")
                return False
        else:
            print(f"ERREUR: {response.status_code}")
            print(response.content.decode())
            return False
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_machine_existence():
    """Vérifier que les machines existent"""
    print("\n=== VERIFICATION DES MACHINES ===")
    
    from apps.machines.models import Machine
    
    machines = Machine.objects.all()
    print(f"Nombre de machines: {machines.count()}")
    
    if machines.count() > 0:
        machine = machines.first()
        print(f"Première machine: {machine.nom} (ID: {machine.id})")
        return True
    else:
        print("ERREUR: Aucune machine trouvée")
        return False

if __name__ == '__main__':
    print("Démarrage des tests...")
    
    machine_ok = test_machine_existence()
    if not machine_ok:
        print("ECHEC: Pas de machines")
        sys.exit(1)
    
    recommendation_ok = test_basic_recommendation()
    
    if recommendation_ok:
        print("\nSUCCES: Tous les tests passent")
    else:
        print("\nECHEC: Des tests ont echoue")
        sys.exit(1)