#!/usr/bin/env python3
"""
Script de test pour le nouveau système calendrier CSV
Tests complets des nouvelles APIs de séances simples
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
    """Authentification et récupération du token"""
    print("Authentification...")
    
    auth_url = 'https://basicfit-v2.fly.dev/api/auth/login/'
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
    """Test récupération des séances simples"""
    print("\nTest recuperation seances simples...")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ GET /simple/ - {data.get('message', 'OK')}")
        print(f"   📊 {data.get('count', 0)} séances trouvées")
        
        return data.get('success', False)
        
    except requests.RequestException as e:
        print(f"❌ Erreur GET séances: {e}")
        return False

def test_csv_import(token):
    """Test import CSV"""
    print("\n📥 Test import CSV...")
    
    # CSV de test avec format machine,date,type
    csv_test = """machine,date,type
Tapis de course,2025-01-01,CARDIO
Vélo elliptique,2025-01-02,CARDIO
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
        print(f"✅ POST /simple/import/ - {result.get('message', 'OK')}")
        print(f"   📈 {result.get('imported_count', 0)} séances importées")
        print(f"   ⚠️  {result.get('errors_count', 0)} erreurs")
        
        if result.get('errors'):
            print("   Erreurs détaillées:")
            for error in result.get('errors', []):
                print(f"      - {error}")
        
        return result.get('success', False)
        
    except requests.RequestException as e:
        print(f"❌ Erreur import CSV: {e}")
        return False

def test_calendar_summary(token):
    """Test résumé calendrier"""
    print("\n📅 Test résumé calendrier...")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/summary/'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ GET /simple/summary/ - {data.get('message', 'OK')}")
        
        summary = data.get('data', {})
        print(f"   📊 Total séances: {summary.get('total_seances', 0)}")
        print(f"   📅 Total dates: {summary.get('total_dates', 0)}")
        print(f"   🕐 Dernière séance: {summary.get('derniere_seance', 'N/A')}")
        
        return data.get('success', False)
        
    except requests.RequestException as e:
        print(f"❌ Erreur résumé calendrier: {e}")
        return False

def test_add_seance_simple(token):
    """Test ajout d'une séance manuelle"""
    print("\n➕ Test ajout séance manuelle...")
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/add/'
    
    seance_data = {
        'machine': 'Test Machine Manuel',
        'date': '2025-08-07',  # Aujourd'hui
        'type': 'MUSCULATION',
        'duree': 45,
        'note': 8,
        'commentaire': 'Test ajout manuel via API'
    }
    
    try:
        response = requests.post(url, headers=headers, json=seance_data)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ POST /simple/add/ - {result.get('message', 'OK')}")
        
        if result.get('data'):
            seance = result['data']
            print(f"   🆔 ID: {seance.get('id')}")
            print(f"   🏋️  Machine: {seance.get('machine')}")
            print(f"   📅 Date: {seance.get('date')}")
        
        return result.get('success', False)
        
    except requests.RequestException as e:
        print(f"❌ Erreur ajout séance: {e}")
        return False

def test_delete_all_seances(token):
    """Test suppression de toutes les séances (ATTENTION!)"""
    print("\n🗑️  Test suppression TOUTES les séances...")
    
    # Demander confirmation
    confirm = input("⚠️  ATTENTION: Cela va supprimer TOUTES les séances de test. Continuer? (oui/NON): ")
    if confirm.lower() != 'oui':
        print("❌ Suppression annulée par l'utilisateur")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    url = f'{API_BASE_URL}/simple/delete-all/'
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ DELETE /simple/delete-all/ - {result.get('message', 'OK')}")
        print(f"   🗑️  {result.get('deleted_count', 0)} séances supprimées")
        
        return result.get('success', False)
        
    except requests.RequestException as e:
        print(f"❌ Erreur suppression: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=== TEST NOUVEAU SYSTEME CALENDRIER CSV ===")
    print(f"URL API: {API_BASE_URL}")
    
    # Authentification
    token = authenticate()
    if not token:
        print("❌ Impossible de s'authentifier. Arrêt des tests.")
        sys.exit(1)
    
    # Tests séquentiels
    tests = [
        ("Récupération séances", test_get_seances_simples),
        ("Import CSV", test_csv_import),
        ("Résumé calendrier", test_calendar_summary), 
        ("Ajout séance manuelle", test_add_seance_simple),
        # ("Suppression toutes séances", test_delete_all_seances),  # Commenté par sécurité
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func(token)
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur inattendue dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé final
    print("\n📋 === RÉSUMÉ DES TESTS ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! Le nouveau système calendrier fonctionne.")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué. Vérifier la configuration.")
        sys.exit(1)

if __name__ == '__main__':
    main()