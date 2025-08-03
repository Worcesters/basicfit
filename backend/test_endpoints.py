#!/usr/bin/env python3
"""
Test simple des endpoints de recommandation
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    print("=== TEST DES ENDPOINTS DE RECOMMANDATION ===")
    
    # Test endpoint machines
    print("\n1. Test endpoint machines...")
    try:
        response = requests.get(f"{BASE_URL}/api/workouts/machines/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            machines = response.json()
            print(f"   Machines trouvées: {len(machines)}")
            if machines:
                print(f"   Première machine: {machines[0].get('nom', 'N/A')}")
        else:
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test endpoint recommandation par ID (sans auth)
    print("\n2. Test endpoint recommandation par ID...")
    try:
        response = requests.get(f"{BASE_URL}/api/workouts/recommendation/id/1/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test endpoint recommandation par nom (sans auth)
    print("\n3. Test endpoint recommandation par nom...")
    try:
        response = requests.get(f"{BASE_URL}/api/workouts/recommendation/name/Supine%20Press/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_endpoints()