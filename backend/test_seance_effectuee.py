"""
Test sauvegarde séances effectuées avec nouvelle API séparée
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE = "https://basicfit-v2.fly.dev/api"
LOGIN_URL = f"{API_BASE}/users/android/login/"
SAVE_EFFECTUEE_URL = f"{API_BASE}/workouts-v2/effectuees/save/"
LIST_EFFECTUEES_URL = f"{API_BASE}/workouts-v2/effectuees/"

# Données de test
LOGIN_DATA = {
    "email": "test_csv@basicfit.com", 
    "password": "TestPassword123!"
}

# Exemple de séance effectuée
SEANCE_EFFECTUEE = {
    "nom": "Séance Pectoraux Test",
    "date_debut": "2025-08-26T14:30:00",
    "date_fin": "2025-08-26T15:45:00",
    "duree_minutes": 75,
    "note_ressenti": 4,
    "note_difficulte": 3,
    "commentaire": "Bonne séance, progression sur le développé couché",
    "exercices": [
        {
            "nom_exercice": "Développé couché",
            "machine_id": 2,  # Supine Press
            "ordre_dans_seance": 1,
            "series": [
                {"numero": 1, "repetitions_prevues": 10, "repetitions_realisees": 10, "poids_utilise": 60.0},
                {"numero": 2, "repetitions_prevues": 10, "repetitions_realisees": 9, "poids_utilise": 60.0},
                {"numero": 3, "repetitions_prevues": 10, "repetitions_realisees": 8, "poids_utilise": 60.0}
            ]
        },
        {
            "nom_exercice": "Incliné haltères", 
            "machine_id": 1,  # Assume une machine
            "ordre_dans_seance": 2,
            "series": [
                {"numero": 1, "repetitions_prevues": 12, "repetitions_realisees": 12, "poids_utilise": 20.0},
                {"numero": 2, "repetitions_prevues": 12, "repetitions_realisees": 11, "poids_utilise": 20.0},
                {"numero": 3, "repetitions_prevues": 12, "repetitions_realisees": 10, "poids_utilise": 20.0}
            ]
        }
    ]
}

def test_seance_effectuee():
    print("=== TEST SAUVEGARDE SÉANCE EFFECTUÉE ===")
    
    # 1. Login
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
    
    # 2. Sauvegarder séance effectuée
    print(f"\n[SAVE] Test sauvegarde vers {SAVE_EFFECTUEE_URL}")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(SAVE_EFFECTUEE_URL, json=SEANCE_EFFECTUEE, headers=headers)
        print(f"Status save: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"[OK] Séance sauvegardée: {result}")
        else:
            print(f"[ERREUR] Save failed")
    except Exception as e:
        print(f"[ERREUR] Exception save: {e}")
    
    # 3. Vérifier les séances effectuées
    print(f"\n[VERIFICATION] Liste séances effectuées depuis {LIST_EFFECTUEES_URL}")
    try:
        response = requests.get(LIST_EFFECTUEES_URL, headers=headers)
        print(f"Status list: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Séances effectuées récupérées:")
            if isinstance(result, dict) and 'data' in result:
                print(f"Nombre de séances: {len(result['data'])}")
                for seance in result['data'][:2]:  # Afficher 2 premières
                    print(f"- {seance.get('nom', 'N/A')} le {seance.get('date_debut', 'N/A')}")
                    print(f"  Durée: {seance.get('duree_minutes', 'N/A')} min, Exercices: {seance.get('nombre_exercices', 'N/A')}")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"[ERREUR] Récupération séances failed: {response.text}")
    except Exception as e:
        print(f"[ERREUR] Exception list: {e}")

if __name__ == "__main__":
    test_seance_effectuee()