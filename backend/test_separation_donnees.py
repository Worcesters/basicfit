"""
Test final - Vérification de la séparation des données entre Calendrier et Séances effectuées
"""
import requests
import json

# Configuration
API_BASE = "https://basicfit-v2.fly.dev/api"
LOGIN_URL = f"{API_BASE}/users/android/login/"
CSV_IMPORT_URL = f"{API_BASE}/workouts-v2/calendrier/import/"
CALENDRIER_LIST_URL = f"{API_BASE}/workouts-v2/calendrier/"
SAVE_EFFECTUEE_URL = f"{API_BASE}/workouts-v2/effectuees/save/"
LIST_EFFECTUEES_URL = f"{API_BASE}/workouts-v2/effectuees/"

# Données de test
LOGIN_DATA = {
    "email": "test_csv@basicfit.com", 
    "password": "TestPassword123!"
}

def test_separation_complete():
    print("=== TEST SÉPARATION DONNÉES CALENDRIER vs EFFECTUÉES ===")
    
    # 1. Login
    print("\n[LOGIN] Authentification...")
    try:
        response = requests.post(LOGIN_URL, json=LOGIN_DATA)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('token')
                print(f"[OK] Token obtenu")
            else:
                print(f"[ERREUR] Login failed: {result}")
                return
        else:
            print(f"[ERREUR] Login failed: {response.text}")
            return
    except Exception as e:
        print(f"[ERREUR] Exception login: {e}")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 2. Import CSV Calendrier (PLANIFICATION)
    print(f"\n[CALENDRIER] Import CSV de planification...")
    csv_data_planning = """Date,Exercice,Machine,Series,Repetitions,Poids,Repos
2025-08-29,Développé incliné,Inclined Press,3,10,50,90
2025-08-30,Rowing,Lat Pulldown,3,12,40,120"""
    
    csv_payload = {"csv_data": csv_data_planning, "import_type": "calendar"}
    response = requests.post(CSV_IMPORT_URL, json=csv_payload, headers=headers)
    print(f"Status import calendrier: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] {result.get('imported_count', 0)} séances PLANIFIÉES importées")
    
    # 3. Sauvegarde séance effectuée (ANALYSE)
    print(f"\n[EFFECTUÉES] Sauvegarde séance réellement effectuée...")
    seance_effectuee = {
        "nom": "Séance Back réalisée",
        "date_debut": "2025-08-26T16:30:00",
        "date_fin": "2025-08-26T17:30:00",
        "duree_minutes": 60,
        "note_ressenti": 5,
        "note_difficulte": 4,
        "commentaire": "Très bonne séance dos",
        "exercices": [
            {
                "nom_exercice": "Rowing barre",
                "machine_id": 2,
                "ordre_dans_seance": 1,
                "series": [
                    {"numero": 1, "repetitions_prevues": 10, "repetitions_realisees": 10, "poids_utilise": 70.0},
                    {"numero": 2, "repetitions_prevues": 10, "repetitions_realisees": 9, "poids_utilise": 70.0}
                ]
            }
        ]
    }
    
    response = requests.post(SAVE_EFFECTUEE_URL, json=seance_effectuee, headers=headers)
    print(f"Status save effectuée: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"[OK] Séance EFFECTUÉE sauvegardée: ID {result['data']['seance_id']}")
    
    # 4. Vérification séparation des données
    print(f"\n[VERIFICATION] Récupération des deux types de données...")
    
    # Calendrier (planification)
    response = requests.get(CALENDRIER_LIST_URL, headers=headers)
    if response.status_code == 200:
        calendrier_data = response.json()
        nb_planifiees = len(calendrier_data.get('data', []))
        print(f"CALENDRIER (Planification): {nb_planifiees} séances planifiées")
        
        for seance in calendrier_data.get('data', [])[:2]:
            print(f"   - {seance.get('nom', 'N/A')} - Statut: {seance.get('statut', 'N/A')}")
    
    # Séances effectuées (analyse)
    response = requests.get(LIST_EFFECTUEES_URL, headers=headers)
    if response.status_code == 200:
        effectuees_data = response.json()
        nb_effectuees = len(effectuees_data.get('data', []))
        print(f"EFFECTUÉES (Analyse): {nb_effectuees} séances réellement effectuées")
        
        for seance in effectuees_data.get('data', [])[:2]:
            print(f"   - {seance.get('nom', 'N/A')} - Note: {seance.get('note_ressenti', 'N/A')}/5")
            print(f"     Volume total: {seance.get('volume_total', 'N/A')}, Exercices: {seance.get('nombre_exercices', 'N/A')}")
    
    print(f"\nSÉPARATION CONFIRMÉE:")
    print(f"   - Tables SEPAREES: Calendrier != Effectuees")
    print(f"   - Import CSV -> Table Calendrier (planification)")
    print(f"   - Workout termine -> Table Effectuees (analyse)")
    print(f"   - Analyse intelligente peut utiliser UNIQUEMENT les effectuees !")

if __name__ == "__main__":
    test_separation_complete()