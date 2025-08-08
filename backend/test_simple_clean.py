#!/usr/bin/env python3
"""
Script de test pour le nouveau systeme calendrier CSV
Tests complets des nouvelles APIs de seances simples
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = 'https://basicfit-v2.fly.dev/api/workouts'

# Données de test pour l'authentification
EMAIL_TEST = 'test@basicfit.com'  
PASSWORD_TEST = 'testpass123'

def authenticate():
    """Authentification et recuperation du token"""
    print("Authentification...")
    
    auth_url = 'https://basicfit-v2.fly.dev/api/users/android/login/'
    auth_data = {
        'email': EMAIL_TEST,
        'password': PASSWORD_TEST
    }
    
    try:
        response = requests.post(auth_url, json=auth_data)
        response.raise_for_status()
        
        data = response.json()
        if data.get('success'):
            token = data.get('access_token')
            print(f"[OK] Authentifie avec succes")
            return token
        else:
            print(f"[ERROR] Echec authentification: {data.get('message')}")
            return None
            
    except requests.RequestException as e:
        print(f"[ERROR] Erreur reseau auth: {e}")
        return None

def test_get_seances_simples(token):
    """Test recuperation des seances simples"""
    print("\nTest recuperation seances simples...")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"[OK] GET /simple/ - {data.get('message', 'OK')}")
        print(f"     {data.get('count', 0)} seances trouvees")
        
        return data.get('success', False)
        
    except requests.RequestException as e:
        print(f"[ERROR] Erreur GET seances: {e}")
        return False

def test_csv_import(token):
    """Test import CSV"""
    print("\nTest import CSV...")
    
    # CSV de test avec format machine,date,type
    csv_test = """machine,date,type
Tapis de course,2025-01-01,CARDIO
Velo elliptique,2025-01-02,CARDIO
Banc de musculation,2025-01-03,MUSCULATION
Rameur,2025-01-04,CARDIO
Leg Press,2025-01-05,FORCE"""
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/import/'
    data = {'csv_data': csv_test}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"[OK] POST /simple/import/ - {result.get('message', 'OK')}")
        print(f"     {result.get('imported_count', 0)} seances importees")
        print(f"     {result.get('errors_count', 0)} erreurs")
        
        if result.get('errors'):
            print("     Erreurs detaillees:")
            for error in result.get('errors', []):
                print(f"       - {error}")
        
        return result.get('success', False)
        
    except requests.RequestException as e:
        print(f"[ERROR] Erreur import CSV: {e}")
        return False

def test_calendar_summary(token):
    """Test resume calendrier"""
    print("\nTest resume calendrier...")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/summary/'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"[OK] GET /simple/summary/ - {data.get('message', 'OK')}")
        
        summary = data.get('data', {})
        print(f"     Total seances: {summary.get('total_seances', 0)}")
        print(f"     Total dates: {summary.get('total_dates', 0)}")
        print(f"     Derniere seance: {summary.get('derniere_seance', 'N/A')}")
        
        return data.get('success', False)
        
    except requests.RequestException as e:
        print(f"[ERROR] Erreur resume calendrier: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=== TEST NOUVEAU SYSTEME CALENDRIER CSV ===")
    print(f"URL API: {API_BASE_URL}")
    
    # Authentification
    token = authenticate()
    if not token:
        print("[ERROR] Impossible de s'authentifier. Arret des tests.")
        sys.exit(1)
    
    # Tests sequentiels
    tests = [
        ("Recuperation seances", test_get_seances_simples),
        ("Import CSV", test_csv_import),
        ("Resume calendrier", test_calendar_summary),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func(token)
            results.append((test_name, success))
        except Exception as e:
            print(f"[ERROR] Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Resume final
    print("\n=== RESUME DES TESTS ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {test_name}")
    
    print(f"\nResultat: {passed}/{total} tests reussis")
    
    if passed == total:
        print("Tous les tests sont passes! Le nouveau systeme calendrier fonctionne.")
        sys.exit(0)
    else:
        print("Certains tests ont echoue. Verifier la configuration.")
        sys.exit(1)

if __name__ == '__main__':
    main()