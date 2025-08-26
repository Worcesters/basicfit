#!/usr/bin/env python3
"""
Créer un utilisateur directement via l'API pour qu'il soit en PostgreSQL
"""
import requests
import json

def create_user_via_api():
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("=" * 60)
    print("CRÉATION UTILISATEUR VIA API (PostgreSQL)")
    print("=" * 60)
    
    # Données d'inscription
    register_data = {
        "email": "testprod@example.com",
        "password": "testprod123",
        "nom": "Test",
        "prenom": "Production"
    }
    
    print(f"[REGISTER] Création utilisateur: {register_data['email']}")
    
    try:
        # Test d'inscription via endpoint Android
        r = requests.post(f"{BASE_URL}/users/android/register/", json=register_data, timeout=10)
        
        print(f"[STATUS] Register: {r.status_code}")
        print(f"[RESPONSE] {r.text}")
        
        if r.status_code in [200, 201]:
            print(f"[SUCCESS] Utilisateur créé via API!")
        elif "already exists" in r.text.lower() or "existe déjà" in r.text.lower():
            print(f"[INFO] Utilisateur existe déjà - continuons avec le test de connexion")
        else:
            print(f"[ERROR] Échec création: {r.text}")
            return None
        
        # Test de connexion immédiat
        print(f"\n[LOGIN] Test connexion...")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        r2 = requests.post(f"{BASE_URL}/users/auth/login/", json=login_data, timeout=10)
        
        print(f"[STATUS] Login: {r2.status_code}")
        print(f"[RESPONSE] {r2.text}")
        
        if r2.status_code == 200:
            data = r2.json()
            token = data.get('access_token') or data.get('token')
            if not token and data.get('tokens'):
                token = data['tokens'].get('access')
            
            if token:
                print(f"[SUCCESS] Login réussi!")
                print(f"[TOKEN] {token[:50]}...")
                
                # Test endpoint protégé
                headers = {'Authorization': f'Bearer {token}'}
                
                r3 = requests.get(f"{BASE_URL}/workouts/simple/", headers=headers, timeout=10)
                print(f"[API] /workouts/simple/: {r3.status_code}")
                
                if r3.status_code == 200:
                    data3 = r3.json()
                    print(f"[SUCCESS] API accessible - Count: {data3.get('count', 0)}")
                    
                    print(f"\n" + "=" * 60)
                    print("UTILISATEUR PRODUCTION PRÊT!")
                    print(f"Email: {register_data['email']}")
                    print(f"Password: {register_data['password']}")
                    print("Utilisez ces credentials dans l'app Android")
                    print("=" * 60)
                    
                    return register_data
                else:
                    print(f"[ERROR] API inaccessible: {r3.text}")
            else:
                print(f"[ERROR] Pas de token dans la réponse")
        else:
            print(f"[ERROR] Login failed: {r2.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        
    return None

def test_register_endpoint():
    """Test si l'endpoint de register existe"""
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("=" * 40)
    print("TEST ENDPOINTS DISPONIBLES")
    print("=" * 40)
    
    endpoints_to_test = [
        "/users/auth/register/",
        "/users/android/register/",
        "/auth/register/",
        "/users/register/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            # Test avec données vides pour voir si l'endpoint existe
            r = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
            print(f"[{r.status_code}] {endpoint}")
            if r.status_code != 404:
                print(f"    Response: {r.text[:100]}...")
        except Exception as e:
            print(f"[ERROR] {endpoint}: {e}")

if __name__ == '__main__':
    # D'abord tester quels endpoints existent
    test_register_endpoint()
    
    print(f"\n")
    
    # Essayer de créer un utilisateur
    user = create_user_via_api()