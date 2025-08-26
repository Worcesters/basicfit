"""
Test complet CSV import avec création d'utilisateur
"""
import requests
import json

# Configuration
API_BASE = "https://basicfit-v2.fly.dev/api"
REGISTER_URL = f"{API_BASE}/users/android/register/"
LOGIN_URL = f"{API_BASE}/users/android/login/"
CSV_IMPORT_URL = f"{API_BASE}/workouts-v2/calendrier/import/"
CALENDRIER_LIST_URL = f"{API_BASE}/workouts-v2/calendrier/"

# Données de test
REGISTER_DATA = {
    "email": "test_csv@basicfit.com",
    "password": "TestPassword123!",
    "prenom": "Test",
    "nom": "User"
}

LOGIN_DATA = {
    "email": "test_csv@basicfit.com", 
    "password": "TestPassword123!"
}

# Exemple de données CSV simulées
CSV_DATA = """Date,Exercice,Machine,Series,Repetitions,Poids,Repos
2025-08-27,Développé couché,Supine Press,3,10,60,90
2025-08-27,Squats,Leg Press,3,12,80,120
2025-08-28,Tractions,Lat Pulldown,3,8,40,90"""

def test_csv_import_complete():
    print("=== TEST COMPLET IMPORT CSV CALENDRIER ===")
    
    # 1. Registration
    print("\n[REGISTER] Création utilisateur test...")
    try:
        response = requests.post(REGISTER_URL, json=REGISTER_DATA)
        print(f"Status register: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code not in [200, 201, 400]:  # 400 si user existe déjà
            print(f"[ERREUR] Register failed")
            return
    except Exception as e:
        print(f"[ERREUR] Exception register: {e}")
    
    # 2. Login
    print("\n[LOGIN] Authentification...")
    try:
        response = requests.post(LOGIN_URL, json=LOGIN_DATA)
        print(f"Status login: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('token')
                print(f"[OK] Token obtenu: {token[:20]}...")
            else:
                print(f"[ERREUR] Login failed: {result}")
                return
        else:
            print(f"[ERREUR] Login failed: {response.text}")
            return
    except Exception as e:
        print(f"[ERREUR] Exception login: {e}")
        return
    
    # 3. Test import CSV
    print(f"\n[CSV IMPORT] Test import vers {CSV_IMPORT_URL}")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    csv_payload = {
        "csv_data": CSV_DATA,
        "import_type": "calendar"
    }
    
    try:
        response = requests.post(CSV_IMPORT_URL, json=csv_payload, headers=headers)
        print(f"Status import: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Import réussi: {result}")
        else:
            print(f"[ERREUR] Import failed")
    except Exception as e:
        print(f"[ERREUR] Exception import: {e}")
    
    # 4. Vérifier le calendrier
    print(f"\n[VERIFICATION] Liste calendrier depuis {CALENDRIER_LIST_URL}")
    try:
        response = requests.get(CALENDRIER_LIST_URL, headers=headers)
        print(f"Status calendrier: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Calendrier récupéré:")
            if isinstance(result, dict) and 'results' in result:
                print(f"Nombre d'entrées: {len(result['results'])}")
                for entry in result['results'][:3]:  # Afficher 3 premières
                    print(f"- {entry.get('nom', 'N/A')} le {entry.get('date_prevue', 'N/A')}")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[ERREUR] Récupération calendrier failed: {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception calendrier: {e}")

if __name__ == "__main__":
    test_csv_import_complete()