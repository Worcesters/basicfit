#!/usr/bin/env python3
"""
Test login avec utilisateur qui fonctionne
"""
import requests
import json

def test_login_working():
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("=" * 60)
    print("TEST LOGIN UTILISATEUR QUI FONCTIONNE")
    print("=" * 60)
    
    # Test avec l'utilisateur créé récemment
    login_data = {
        "email": "testapi@example.com",
        "password": "testapi123"
    }
    
    print(f"[TEST] Tentative login: {login_data['email']}")
    
    try:
        r = requests.post(f"{BASE_URL}/users/auth/login/", json=login_data, timeout=10)
        
        print(f"[STATUS] Code: {r.status_code}")
        print(f"[RESPONSE] {r.text}")
        
        if r.status_code == 200:
            data = r.json()
            token = data.get('access_token') or data.get('token')
            
            if token:
                print(f"[SUCCESS] Login réussi!")
                print(f"[TOKEN] {token[:50]}...")
                
                # Test d'un endpoint protégé
                headers = {'Authorization': f'Bearer {token}'}
                
                print(f"\n[TEST] Test endpoint protégé...")
                r2 = requests.get(f"{BASE_URL}/workouts/simple/", headers=headers, timeout=10)
                print(f"[STATUS] /workouts/simple/: {r2.status_code}")
                
                if r2.status_code == 200:
                    data2 = r2.json()
                    print(f"[SUCCESS] Accès API autorisé - Count: {data2.get('count', 0)}")
                    
                    # Test import CSV
                    print(f"\n[TEST] Test import CSV...")
                    csv_data = "machine,date,type\nTest API Machine,2025-01-17,AUTRE"
                    
                    r3 = requests.post(f"{BASE_URL}/workouts/simple/import/", 
                                     json={"csv_data": csv_data}, 
                                     headers=headers, timeout=30)
                    print(f"[STATUS] Import CSV: {r3.status_code}")
                    print(f"[RESPONSE] {r3.text}")
                    
                else:
                    print(f"[ERROR] Accès refusé: {r2.text}")
                
                return token
            else:
                print(f"[ERROR] Pas de token dans la réponse")
                return None
        else:
            print(f"[ERROR] Login failed: {r.text}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        return None

def create_working_user():
    """Créer un utilisateur qui fonctionne via l'API directement"""
    import os
    import django

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
    django.setup()

    from apps.users.models import User
    
    try:
        # Supprimer l'ancien
        User.objects.filter(email='testapi@example.com').delete()
        
        # Créer nouveau
        user = User.objects.create_user(
            username='testapi',
            email='testapi@example.com',
            password='testapi123',
            first_name='Test',
            last_name='API',
            is_active=True
        )
        
        print(f"[SUCCESS] Utilisateur créé: {user.email} (ID: {user.id})")
        print(f"[CREDENTIALS] Email: testapi@example.com, Password: testapi123")
        
        return user
        
    except Exception as e:
        print(f"[ERROR] Création utilisateur: {e}")
        return None

if __name__ == '__main__':
    print("Création d'un utilisateur test qui fonctionne...")
    user = create_working_user()
    
    if user:
        print("\nTest de connexion API...")
        token = test_login_working()
        
        if token:
            print(f"\n" + "=" * 60)
            print("UTILISATEUR DE TEST PRÊT!")
            print("Utilisez dans l'app Android:")
            print("Email: testapi@example.com")
            print("Password: testapi123")
            print("=" * 60)
        else:
            print(f"\n[ERROR] Problème de connexion malgré la création utilisateur")
    else:
        print(f"\n[ERROR] Impossible de créer l'utilisateur")