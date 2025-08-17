#!/usr/bin/env python
"""
Test de l'API Railway en production avec authentification
"""
import requests
import json

# Configuration
API_BASE = "https://basicfit-v2.fly.dev/api"
EMAIL = "jeremy.didier77@gmail.com"
PASSWORD = "jeremyd77"

def test_api_production():
    """Test complet de l'API Railway"""
    print("=== TEST API PRODUCTION RAILWAY ===")
    
    # 1. Test de connexion (login)
    print("\n[LOGIN] Test authentification...")
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    
    try:
        # Test d'abord si l'API est accessible
        base_url = "https://basicfit-v2.fly.dev"
        health_response = requests.get(base_url, timeout=10)
        print(f"Status base URL: {health_response.status_code}")
        
        # Test API root
        api_response = requests.get(f"{base_url}/api/", timeout=10)
        print(f"Status API root: {api_response.status_code}")
        
        login_response = requests.post(f"{API_BASE}/users/android/login/", json=login_data, timeout=10)
        print(f"Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"Login result: {login_result}")
            
            # Essayer différents champs pour le token
            token = login_result.get('access_token') or login_result.get('access') or login_result.get('token')
            print(f"[OK] Login reussi, token obtenu: {token[:20] if token else 'None'}...")
            
            # Headers avec token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
        elif login_response.status_code == 400:
            # Peut être que l'utilisateur n'existe pas, essayons de le créer
            print("[RETRY] Tentative de creation du compte...")
            register_data = {
                "email": EMAIL,
                "password": PASSWORD,
                "first_name": "Jeremy",
                "last_name": "Didier"
            }
            
            register_response = requests.post(f"{API_BASE}/users/android/register/", json=register_data, timeout=10)
            print(f"Status register: {register_response.status_code}")
            
            if register_response.status_code == 201:
                print("[OK] Compte cree avec succes")
                # Retry login
                login_response = requests.post(f"{API_BASE}/users/android/login/", json=login_data, timeout=10)
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    token = login_result.get('access')
                    print(f"[OK] Login apres creation reussi")
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                else:
                    print(f"[ERROR] Login apres creation echoue: {login_response.text}")
                    return
            else:
                print(f"[ERROR] Creation compte echouee: {register_response.text}")
                return
        else:
            print(f"[ERROR] Login echoue: {login_response.text}")
            return
            
    except Exception as e:
        print(f"[ERROR] Erreur connexion: {e}")
        return
    
    # 2. Test récupération des machines
    print("\n[MACHINES] Test recuperation machines...")
    try:
        machines_response = requests.get(f"{API_BASE}/machines/", headers=headers, timeout=10)
        print(f"Status machines: {machines_response.status_code}")
        
        if machines_response.status_code == 200:
            machines_data = machines_response.json()
            # L'API retourne une structure avec 'results' et 'count'
            machines = machines_data.get('results', [])
            count = machines_data.get('count', 0)
            print(f"[OK] {count} machines recuperees")
            
            # Trouver Supine Press
            supine_press = None
            for machine in machines:
                if 'supine' in machine.get('nom', '').lower():
                    supine_press = machine
                    break
            
            if supine_press:
                print(f"[OK] Supine Press trouvee: ID {supine_press['id']}")
            else:
                print("[WARNING] Supine Press non trouvee, utilisation de la premiere machine")
                supine_press = machines[0] if machines else None
                
        else:
            print(f"[ERROR] Erreur machines: {machines_response.text}")
            return
            
    except Exception as e:
        print(f"[ERROR] Erreur recuperation machines: {e}")
        return
    
    # 3. Test recommandation
    if supine_press:
        print(f"\n[RECOMMENDATION] Test recommandation pour {supine_press['nom']}...")
        try:
            # Test par ID
            rec_response = requests.get(
                f"{API_BASE}/workouts/recommendations/{supine_press['id']}/",
                headers=headers,
                timeout=10
            )
            print(f"Status recommandation: {rec_response.status_code}")
            
            if rec_response.status_code == 200:
                recommendation = rec_response.json()
                print(f"[OK] Recommandation recue:")
                print(f"  Success: {recommendation.get('success')}")
                if recommendation.get('success') and recommendation.get('data'):
                    data = recommendation['data']
                    print(f"  Poids: {data.get('poids_recommande')}kg")
                    print(f"  Series: {data.get('series_recommandees')}")
                    print(f"  Reps: {data.get('reps_recommandees')}")
                    print(f"  Source: {data.get('source')}")
                    print(f"  Notes: {data.get('notes', 'N/A')}")
                else:
                    print(f"  Erreur dans data: {recommendation}")
            else:
                print(f"[ERROR] Erreur recommandation: {rec_response.text}")
                
        except Exception as e:
            print(f"[ERROR] Erreur test recommandation: {e}")
    
    print("\n=== FIN TEST ===")

if __name__ == "__main__":
    test_api_production()