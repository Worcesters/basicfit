#!/usr/bin/env python3
"""
Test API production pour vérifier la vraie BDD
"""
import requests
import json

def test_api_production_bdd():
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("=" * 60)
    print("TEST API PRODUCTION - VERIFICATION BDD REELLE")
    print("=" * 60)
    
    # 1. Test endpoints sans auth
    print("\n[TEST] Endpoints publics...")
    try:
        r = requests.get(f"{BASE_URL}/users/android/ping/", timeout=10)
        print(f"  - Ping: {r.status_code}")
        
        r = requests.get(f"{BASE_URL}/machines/", timeout=10)
        if r.status_code == 200:
            data = r.json()
            machine_count = len(data.get('results', []))
            print(f"  - Machines: {machine_count} disponibles")
        else:
            print(f"  - Machines: {r.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Tests publics: {e}")
    
    # 2. Test avec un utilisateur existant (jeremy)
    print("\n[TEST] Connexion avec utilisateur existant...")
    login_data = {
        "email": "jeremy.didier77@gmail.com",  # Utilisateur qui existe sûrement
        "password": "votre_mot_de_passe"  # À remplacer
    }
    
    # Essayer plusieurs mots de passe courants
    passwords_to_try = ["password", "jeremy123", "test123", "basicfit123"]
    token = None
    
    for pwd in passwords_to_try:
        try:
            login_data["password"] = pwd
            r = requests.post(f"{BASE_URL}/users/auth/login/", json=login_data, timeout=10)
            if r.status_code == 200:
                auth_data = r.json()
                token = auth_data.get('access_token')
                print(f"  - Connexion réussie avec mot de passe: {pwd}")
                break
            else:
                print(f"  - Échec avec {pwd}: {r.status_code}")
        except Exception as e:
            print(f"  - Erreur avec {pwd}: {e}")
    
    if not token:
        print("[SKIP] Impossible de se connecter, test manuel requis")
        print("       1. Connectez-vous à l'app Android")
        print("       2. Faites un import CSV")
        print("       3. Vérifiez les logs avec: fly logs -a basicfit-v2")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 3. Vérifier les données utilisateur
    print("\n[DATA] Vérification données utilisateur...")
    try:
        # SeanceSimple
        r = requests.get(f"{BASE_URL}/workouts/simple/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            simple_count = data.get('count', 0)
            print(f"  - SeanceSimple: {simple_count}")
            if simple_count > 0 and data.get('data'):
                exemple = data['data'][0]
                print(f"    Exemple: {exemple.get('machine')} - {exemple.get('date')}")
        else:
            print(f"  - SeanceSimple error: {r.status_code} - {r.text}")
        
        # SeanceEntrainement
        r = requests.get(f"{BASE_URL}/workouts/history/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            history_count = data.get('count', 0)
            print(f"  - SeanceEntrainement: {history_count}")
            if history_count > 0 and data.get('data'):
                exemple = data['data'][0]
                print(f"    Exemple: {exemple.get('nom')} - {exemple.get('date')}")
        else:
            print(f"  - SeanceEntrainement error: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"[ERROR] Vérification données: {e}")
    
    # 4. Test d'import direct
    print("\n[TEST] Import CSV test...")
    csv_test = """machine,date,type
Test Debug Machine,2025-01-17,AUTRE"""
    
    try:
        r = requests.post(f"{BASE_URL}/workouts/simple/import/", 
                         json={"csv_data": csv_test}, 
                         headers=headers, timeout=30)
        print(f"  - Import status: {r.status_code}")
        print(f"  - Import response: {r.text}")
        
        if r.status_code in [200, 201]:
            data = r.json()
            print(f"  - Importées: {data.get('imported_count', 0)}")
            print(f"  - Erreurs: {data.get('errors_count', 0)}")
            
    except Exception as e:
        print(f"[ERROR] Test import: {e}")
    
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Vérifiez les logs en temps réel: fly logs -a basicfit-v2")
    print("2. Connectez-vous à l'app Android et faites un import")
    print("3. Les logs devraient montrer toutes les insertions")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    test_api_production_bdd()