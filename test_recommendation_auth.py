#!/usr/bin/env python3
"""
Script de test pour vérifier l'authentification et les recommandations
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/users/android/login/"
RECOMMENDATION_URL = f"{BASE_URL}/workouts/recommendation/"

def test_login():
    """Test de connexion pour obtenir un token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }

    print("🔐 Test de connexion...")
    response = requests.post(LOGIN_URL, json=login_data)

    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('token'):
            print("✅ Connexion réussie!")
            return data['token']
        else:
            print(f"❌ Échec de connexion: {data}")
            return None
    else:
        print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
        return None

def test_recommendation_with_auth(token, machine_name):
    """Test de recommandation avec authentification"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{RECOMMENDATION_URL}{machine_name}/"
    print(f"\n🔍 Test recommandation pour '{machine_name}'...")
    print(f"URL: {url}")

    response = requests.get(url, headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Recommandation obtenue:")
        print(f"   Machine: {data.get('machine_nom')}")
        print(f"   Poids recommandé: {data.get('poids_recommande')} kg")
        print(f"   Séries: {data.get('series_recommandees')}")
        print(f"   Répétitions: {data.get('reps_recommandees')}")
        print(f"   Repos: {data.get('repos_recommande')} sec")
        print(f"   Source: {data.get('source')}")
    else:
        print(f"❌ Erreur: {response.text}")

def test_recommendation_without_auth(machine_name):
    """Test de recommandation sans authentification (doit échouer)"""
    url = f"{RECOMMENDATION_URL}{machine_name}/"
    print(f"\n🔍 Test recommandation SANS AUTH pour '{machine_name}'...")

    response = requests.get(url)

    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctement protégé (401 Unauthorized)")
    else:
        print(f"❌ Problème: {response.text}")

def main():
    print("🧪 Tests d'authentification et recommandations")
    print("=" * 50)

    # Test 1: Connexion
    token = test_login()

    if not token:
        print("\n❌ Impossible de continuer sans token")
        return

    # Test 2: Recommandation avec authentification
    test_recommendation_with_auth(token, "Face Pull")
    test_recommendation_with_auth(token, "Chest Press")

    # Test 3: Recommandation sans authentification
    test_recommendation_without_auth("Face Pull")

    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()