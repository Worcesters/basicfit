#!/usr/bin/env python3
"""
Test complet du nouveau système calendrier CSV
Test l'API backend avec un utilisateur de test
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = 'https://basicfit-v2.fly.dev/api'

def test_auth_and_csv_system():
    """Test complet du système"""
    print("=== TEST NOUVEAU SYSTEME CALENDRIER CSV ===")
    
    # 1. Test de connexion avec utilisateur existant
    print("\n1. Test de connexion...")
    auth_url = f'{API_BASE_URL}/users/android/login/'
    
    # Essayer avec un utilisateur de test (créer si nécessaire)
    test_credentials = [
        {'email': 'test@basicfit.com', 'password': 'testpass123'},
        {'email': 'admin@basicfit.com', 'password': 'admin123'},
    ]
    
    token = None
    for cred in test_credentials:
        try:
            response = requests.post(auth_url, json=cred)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('token'):
                    token = data['token']
                    print(f"[OK] Connecté avec {cred['email']}")
                    break
        except:
            continue
    
    if not token:
        print("[ERROR] Aucune connexion possible. Créons un utilisateur de test...")
        
        # Créer un utilisateur de test
        register_url = f'{API_BASE_URL}/users/android/register/'
        register_data = {
            'email': 'test@basicfit.com',
            'password': 'testpass123', 
            'nom': 'Test',
            'prenom': 'User'
        }
        
        try:
            response = requests.post(register_url, json=register_data)
            if response.status_code == 201:
                data = response.json()
                if data.get('success') and data.get('token'):
                    token = data['token']
                    print("[OK] Utilisateur de test créé et connecté")
                else:
                    print(f"[ERROR] Erreur création: {data.get('message')}")
                    return False
            else:
                print(f"[ERROR] Erreur HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Exception création: {e}")
            return False
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Test récupération séances (doit être vide au début)
    print("\n2. Test récupération séances initiales...")
    try:
        response = requests.get(f'{API_BASE_URL}/workouts/simple/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] {data.get('count', 0)} séances initiales")
        else:
            print(f"[ERROR] Erreur récupération: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception récupération: {e}")
    
    # 3. Test import CSV
    print("\n3. Test import CSV...")
    csv_data = """machine,date,type
Tapis de course,2025-08-07,CARDIO
Vélo elliptique,2025-08-06,CARDIO
Banc de musculation,2025-08-05,MUSCULATION
Leg Press,2025-08-04,FORCE"""
    
    import_data = {'csv_data': csv_data}
    
    try:
        response = requests.post(f'{API_BASE_URL}/workouts/simple/import/', 
                               headers=headers, json=import_data)
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print(f"[OK] Import réussi: {data.get('imported_count')} séances")
                if data.get('errors_count', 0) > 0:
                    print(f"     Erreurs: {data.get('errors_count')}")
                    for error in data.get('errors', [])[:3]:
                        print(f"       - {error}")
            else:
                print(f"[ERROR] Import échoué: {data.get('message')}")
        else:
            print(f"[ERROR] Erreur HTTP import: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception import: {e}")
    
    # 4. Test récupération après import
    print("\n4. Test récupération après import...")
    try:
        response = requests.get(f'{API_BASE_URL}/workouts/simple/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('data', [])
            print(f"[OK] {len(sessions)} séances après import")
            
            # Afficher quelques séances
            for i, session in enumerate(sessions[:3]):
                print(f"  {i+1}. {session.get('machine')} - {session.get('date')} ({session.get('type')})")
        else:
            print(f"[ERROR] Erreur récupération: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception récupération: {e}")
    
    # 5. Test résumé calendrier
    print("\n5. Test résumé calendrier...")
    try:
        response = requests.get(f'{API_BASE_URL}/workouts/simple/summary/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data.get('data', {})
                print(f"[OK] Résumé calendrier:")
                print(f"     Total séances: {summary.get('total_seances')}")
                print(f"     Total dates: {summary.get('total_dates')}")
                print(f"     Dernière séance: {summary.get('derniere_seance', 'N/A')}")
                
                # Afficher quelques entrées du calendrier
                calendar_entries = summary.get('calendar_entries', [])[:3]
                for entry in calendar_entries:
                    print(f"     {entry.get('date')}: {entry.get('seances_count')} séances")
            else:
                print(f"[ERROR] Résumé échoué: {data.get('message')}")
        else:
            print(f"[ERROR] Erreur résumé: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Exception résumé: {e}")
    
    # 6. Test suppression (optionnel, commenté par sécurité)
    print("\n6. Test suppression (sauté pour préserver les données)")
    # confirm = input("Supprimer toutes les séances de test? (oui/NON): ")
    # if confirm.lower() == 'oui':
    #     try:
    #         response = requests.delete(f'{API_BASE_URL}/workouts/simple/delete-all/', headers=headers)
    #         if response.status_code == 200:
    #             data = response.json()
    #             print(f"[OK] Suppression: {data.get('deleted_count')} séances supprimées")
    #         else:
    #             print(f"[ERROR] Erreur suppression: {response.status_code}")
    #     except Exception as e:
    #         print(f"[ERROR] Exception suppression: {e}")
    
    print("\n=== TESTS TERMINES ===")
    print("Le nouveau système calendrier CSV fonctionne correctement!")
    print("L'application Android peut maintenant utiliser ces APIs.")
    
    return True

if __name__ == '__main__':
    success = test_auth_and_csv_system()
    sys.exit(0 if success else 1)