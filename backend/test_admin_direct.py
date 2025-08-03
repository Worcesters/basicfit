#!/usr/bin/env python
"""
Test direct avec l'admin Fly.io pour vérifier les données
"""
import requests

def test_admin_flyio():
    """Test direct de l'admin Fly.io"""
    print("=== TEST ADMIN FLY.IO ===")
    
    # URL admin
    admin_url = "https://basicfit-v2.fly.dev/admin/"
    
    # Tester la page admin
    print(f"Test admin: {admin_url}")
    try:
        response = requests.get(admin_url, timeout=10)
        print(f"Status admin: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] Admin accessible")
            
            # Tester l'API des séances
            seances_api = "https://basicfit-v2.fly.dev/api/workouts/"
            print(f"\nTest API séances: {seances_api}")
            seances_response = requests.get(seances_api, timeout=10)
            print(f"Status séances: {seances_response.status_code}")
            
            # Tester l'API des machines
            machines_api = "https://basicfit-v2.fly.dev/api/machines/"
            print(f"\nTest API machines: {machines_api}")
            machines_response = requests.get(machines_api, timeout=10)
            print(f"Status machines: {machines_response.status_code}")
            
            if machines_response.status_code == 200:
                machines = machines_response.json()
                print(f"[OK] {len(machines) if isinstance(machines, list) else 'N/A'} machines trouvees")
                print(f"Type machines: {type(machines)}")
                print(f"Contenu: {str(machines)[:200]}...")
            
            # Tester une recommandation directement
            print(f"\nTest recommandation directe:")
            rec_url = "https://basicfit-v2.fly.dev/api/workouts/recommendation/simple/1/"
            rec_response = requests.get(rec_url, timeout=10)
            print(f"Status recommandation: {rec_response.status_code}")
            print(f"Réponse: {rec_response.text[:200]}...")
            
        else:
            print(f"[ERROR] Admin non accessible: {response.text[:200]}")
            
    except Exception as e:
        print(f"[ERROR] Erreur: {e}")

if __name__ == "__main__":
    test_admin_flyio()