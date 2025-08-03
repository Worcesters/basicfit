#!/usr/bin/env python
"""
Test les progressions avec l'API Fly.io pour jeremy.didier77@gmail.com
"""
import requests
import json

def test_progression_flyio():
    """Test la progression sur Fly.io"""
    print("=== TEST PROGRESSION FLY.IO ===")
    
    API_BASE = "https://basicfit-v2.fly.dev/api"
    EMAIL = "jeremy.didier77@gmail.com"
    PASSWORD = "jeremyd77"
    
    # 1. Login
    print("1. Login...")
    login_data = {"email": EMAIL, "password": PASSWORD}
    login_response = requests.post(f"{API_BASE}/users/android/login/", json=login_data, timeout=10)
    
    if login_response.status_code != 200:
        print(f"[ERROR] Login echoue: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result.get('token')
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    print("[OK] Login reussi")
    
    # 2. Récupérer les machines
    print("\n2. Machines...")
    machines_response = requests.get(f"{API_BASE}/machines/", headers=headers, timeout=10)
    if machines_response.status_code == 200:
        machines_data = machines_response.json()
        machines = machines_data.get('results', [])
        print(f"[OK] {len(machines)} machines trouvees")
        
        # Chercher Supine Press (et tester plusieurs machines)
        test_machines = []
        for machine in machines:
            if 'supine' in machine.get('nom', '').lower() or 'press' in machine.get('nom', '').lower():
                test_machines.append(machine)
                print(f"Machine trouvee: {machine['nom']} (ID: {machine['id']})")
            if len(test_machines) >= 3:  # Tester 3 machines
                break
        
        # Tester toutes les machines trouvées
        supine_press = test_machines[0] if test_machines else machines[0]
    else:
        print(f"[ERROR] Machines: {machines_response.status_code}")
        return
    
    # 3. Test recommandation pour Supine Press
    if supine_press:
        print(f"\n3. Test recommandation pour {supine_press['nom']}...")
        rec_url = f"{API_BASE}/workouts/recommendation/id/{supine_press['id']}/"
        rec_response = requests.get(rec_url, headers=headers, timeout=10)
        
        print(f"Status: {rec_response.status_code}")
        if rec_response.status_code == 200:
            rec_data = rec_response.json()
            print(f"Recommandation: {json.dumps(rec_data, indent=2)}")
            
            if rec_data.get('success') and rec_data.get('data'):
                data = rec_data['data']
                print(f"\n[RESULTATS]")
                print(f"Poids recommande: {data.get('poids_recommande')}kg")
                print(f"Series: {data.get('series_recommandees')}")
                print(f"Reps: {data.get('reps_recommandees')}")
                print(f"Source: {data.get('source')}")
                print(f"Notes: {data.get('notes')}")
                print(f"Dernier 1RM: {data.get('dernier_1rm')}")
                print(f"Nombre seances: {data.get('nombre_seances')}")
        else:
            print(f"[ERROR] Recommandation: {rec_response.text}")
    
    # 4. Tester les séances du calendrier (utilisé par le bouton Sync BDD)
    print(f"\n4. Test séances calendrier (Sync BDD)...")
    seances_url = f"{API_BASE}/workouts/seances/"  # URL du bouton Sync BDD
    seances_response = requests.get(seances_url, headers=headers, timeout=10)
    
    print(f"Status seances: {seances_response.status_code}")
    if seances_response.status_code == 200:
        seances_data = seances_response.json()
        print(f"Type response: {type(seances_data)}")
        
        if isinstance(seances_data, dict):
            if 'results' in seances_data:
                seances = seances_data['results']
            elif 'data' in seances_data:
                seances = seances_data['data']
            else:
                seances = []
                print(f"Structure inattendue: {list(seances_data.keys())}")
        else:
            seances = seances_data
        
        print(f"[OK] {len(seances)} seances trouvees")
        
        # Afficher les détails
        if len(seances) > 0:
            for i, seance in enumerate(seances[:3]):
                print(f"  Seance {i+1}: {seance}")
        else:
            print("  Aucune séance dans la réponse - d'où le message 'ne trouve rien'")
    else:
        print(f"[ERROR] Seances: {seances_response.status_code} - {seances_response.text[:200]}")

if __name__ == "__main__":
    test_progression_flyio()