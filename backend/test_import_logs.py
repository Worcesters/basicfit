#!/usr/bin/env python3
"""
Test des logs d'insertion BDD - Import CSV
"""
import requests
import json

def test_import_csv_avec_logs():
    BASE_URL = "https://basicfit-v2.fly.dev/api"
    
    print("=" * 60)
    print("TEST IMPORT CSV AVEC LOGS DETAILLES")
    print("=" * 60)
    
    # Etape 1: Se connecter avec un utilisateur de test
    print("\n[LOGIN] Connexion utilisateur test...")
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        r = requests.post(f"{BASE_URL}/users/auth/login/", json=login_data, timeout=10)
        if r.status_code == 200:
            auth_data = r.json()
            token = auth_data.get('access_token')
            print(f"[OK] Connexion reussie - Token: {token[:20]}...")
        else:
            print(f"[ERROR] Echec connexion: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Erreur connexion: {e}")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Etape 2: Verifier les donnees existantes
    print("\n[CHECK] Verification donnees existantes...")
    try:
        # Compter SeanceSimple
        r = requests.get(f"{BASE_URL}/workouts/simple/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[COUNT] SeanceSimple existantes: {data.get('count', 0)}")
        
        # Compter SeanceEntrainement  
        r = requests.get(f"{BASE_URL}/workouts/history/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[COUNT] SeanceEntrainement existantes: {data.get('count', 0)}")
    except Exception as e:
        print(f"[WARN] Erreur verification: {e}")
    
    # Etape 3: Import CSV de test
    print("\n[IMPORT] Import CSV de test...")
    csv_test_data = """machine,date,type
Tapis de course,2025-01-15,CARDIO
Developpe couche,2025-01-15,MUSCULATION
Squat,2025-01-15,FORCE
Velo elliptique,2025-01-16,CARDIO
Leg press,2025-01-16,MUSCULATION"""
    
    import_payload = {
        "csv_data": csv_test_data
    }
    
    try:
        print(f"[SEND] Envoi de {len(csv_test_data.split('\\n'))-1} lignes CSV...")
        r = requests.post(f"{BASE_URL}/workouts/simple/import/", 
                         json=import_payload, headers=headers, timeout=30)
        
        print(f"[STATUS] Statut reponse: {r.status_code}")
        print(f"[RESPONSE] Reponse complete: {r.text}")
        
        if r.status_code in [200, 201]:
            data = r.json()
            print(f"[SUCCESS] Import reussi!")
            print(f"   - Lignes importees: {data.get('imported_count', 0)}")
            print(f"   - Lignes totales: {data.get('total_lines', 0)}")
            print(f"   - Erreurs: {data.get('errors_count', 0)}")
            if data.get('errors'):
                print(f"   - Details erreurs: {data['errors']}")
        else:
            print(f"[ERROR] Echec import: {r.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erreur import: {e}")
        return False
    
    # Etape 4: Verification apres import
    print("\n[VERIFY] Verification apres import...")
    try:
        # Compter SeanceSimple apres
        r = requests.get(f"{BASE_URL}/workouts/simple/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[COUNT] SeanceSimple apres import: {data.get('count', 0)}")
            if data.get('data'):
                print(f"[EXAMPLE] Exemple de seance: {data['data'][0]}")
        
        # Verifier si ca apparait dans l'historique
        r = requests.get(f"{BASE_URL}/workouts/history/", headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"[COUNT] SeanceEntrainement apres import: {data.get('count', 0)}")
            
    except Exception as e:
        print(f"[WARN] Erreur verification finale: {e}")
    
    # Etape 5: Test sauvegarde entrainement termine
    print("\n[WORKOUT] Test sauvegarde entrainement termine...")
    workout_data = {
        "nom": "Test Entrainement Logs",
        "date": "2025-01-17T10:00:00Z",
        "duree": 45,
        "note_ressenti": 8,
        "commentaire": "Test avec logs detailles",
        "exercices": [
            {
                "nom": "Developpe couche",
                "series": 3,
                "reps": 10,
                "poids": 80.0
            },
            {
                "nom": "Squat",
                "series": 3,
                "reps": 12,
                "poids": 100.0
            }
        ]
    }
    
    try:
        print(f"[SEND] Envoi entrainement termine...")
        r = requests.post(f"{BASE_URL}/workouts/save/", 
                         json=workout_data, headers=headers, timeout=30)
        
        print(f"[STATUS] Statut reponse: {r.status_code}")
        print(f"[RESPONSE] Reponse: {r.text}")
        
        if r.status_code in [200, 201]:
            data = r.json()
            print(f"[SUCCESS] Sauvegarde reussie!")
            print(f"   - Cree: {data.get('created', False)}")
            print(f"   - Message: {data.get('message', '')}")
            if data.get('data'):
                print(f"   - ID seance: {data['data'].get('id')}")
        else:
            print(f"[ERROR] Echec sauvegarde: {r.text}")
            
    except Exception as e:
        print(f"[ERROR] Erreur sauvegarde: {e}")
    
    print("\n" + "=" * 60)
    print("TEST TERMINE - Verifiez les logs sur Fly.io:")
    print("fly logs -a basicfit-v2")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = test_import_csv_avec_logs()
    exit(0 if success else 1)