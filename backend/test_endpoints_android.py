#!/usr/bin/env python
"""
Test spécifique des endpoints utilisés par l'application Android
"""
import requests
import json

# Configuration
API_BASE = "https://basicfit-v2.fly.dev/api"
EMAIL = "jeremy.didier77@gmail.com"
PASSWORD = "jeremyd77"

def test_android_endpoints():
    """Test des endpoints Android spécifiques"""
    print("=== TEST ENDPOINTS ANDROID ===")
    
    # 1. Login et récupération du token
    print("\n[LOGIN] Authentification...")
    login_data = {"email": EMAIL, "password": PASSWORD}
    
    try:
        login_response = requests.post(f"{API_BASE}/users/android/login/", json=login_data, timeout=10)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('token')
            print(f"[OK] Token obtenu: {token[:20]}...")
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        else:
            print(f"[ERROR] Login échoué: {login_response.text}")
            return
    except Exception as e:
        print(f"[ERROR] Erreur login: {e}")
        return
    
    # 2. Test des endpoints utilisés par Android
    endpoints_to_test = [
        ("/users/android/profile/", "GET", "Profil utilisateur"),
        ("/users/profile/stats/", "GET", "Statistiques utilisateur"),
        ("/machines/", "GET", "Liste des machines"),
        ("/workouts/history/", "GET", "Historique des entraînements"),
        ("/workouts/simple/", "GET", "Séances simples"),
        ("/workouts/simple/summary/", "GET", "Résumé calendrier"),
        ("/workouts/recommendations/FORCE/", "GET", "Recommandations intelligentes"),
        ("/workouts/progressions/", "GET", "Progressions utilisateur"),
    ]
    
    for endpoint, method, description in endpoints_to_test:
        print(f"\n[{method}] {description} - {endpoint}")
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'results' in data:
                            print(f"  [OK] Donnees: {len(data['results'])} elements")
                        elif 'data' in data:
                            if isinstance(data['data'], list):
                                print(f"  [OK] Donnees: {len(data['data'])} elements")
                            else:
                                print(f"  [OK] Donnees: Structure complexe")
                        elif 'success' in data:
                            print(f"  [OK] Success: {data['success']}")
                        else:
                            print(f"  [OK] Donnees recues")
                    else:
                        print(f"  [OK] Donnees: {len(data) if hasattr(data, '__len__') else 'OK'}")
                except:
                    print(f"  [OK] Reponse valide (non-JSON)")
            elif response.status_code == 404:
                print(f"  [WARNING] Endpoint non trouve")
            elif response.status_code == 401:
                print(f"  [WARNING] Non autorise (token invalide?)")
            elif response.status_code == 500:
                print(f"  [ERROR] Erreur serveur")
                print(f"    {response.text[:200]}...")
            else:
                print(f"  [WARNING] Erreur: {response.status_code}")
                print(f"    {response.text[:200]}...")
                
        except Exception as e:
            print(f"  [ERROR] Erreur requete: {e}")
    
    print("\n=== FIN TEST ENDPOINTS ANDROID ===")

if __name__ == "__main__":
    test_android_endpoints()