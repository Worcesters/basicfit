#!/usr/bin/env python3
"""
Script de test pour l'endpoint sauvegarder_seance_simple
"""
import requests
import json
from datetime import datetime, timezone

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
LOGIN_URL = f"{BASE_URL}/users/android/login/"
SAUVEGARDER_URL = f"{BASE_URL}/workouts/sauvegarder/"

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

def test_sauvegarder_seance(token):
    """Test de sauvegarde de séance"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Données de test pour une séance
    seance_data = {
        "nom": "Séance test",
        "duree": 45,
        "note_ressenti": 8,
        "commentaire": "Test depuis script Python",
        "exercices": [
            {
                "nom": "Face Pull",
                "series": 3,
                "reps": 12,
                "poids": 15.0
            },
            {
                "nom": "Chest Press",
                "series": 4,
                "reps": 10,
                "poids": 40.0
            }
        ]
    }

    print(f"\n💾 Test sauvegarde séance...")
    print(f"URL: {SAUVEGARDER_URL}")
    print(f"Données: {json.dumps(seance_data, indent=2)}")

    response = requests.post(SAUVEGARDER_URL, json=seance_data, headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print("✅ Séance sauvegardée avec succès!")
        print(f"   ID: {data.get('id')}")
        print(f"   Nom: {data.get('nom')}")
        print(f"   Statut: {data.get('statut')}")
        print(f"   Exercices: {data.get('nombre_exercices')}")
    else:
        print(f"❌ Erreur: {response.text}")
        try:
            error_data = response.json()
            print(f"   Détails: {error_data}")
        except:
            pass

def test_sauvegarder_sans_auth():
    """Test de sauvegarde sans authentification (doit échouer)"""
    seance_data = {
        "nom": "Séance test sans auth",
        "duree": 30,
        "exercices": []
    }

    print(f"\n💾 Test sauvegarde SANS AUTH...")

    response = requests.post(SAUVEGARDER_URL, json=seance_data)

    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctement protégé (401 Unauthorized)")
    else:
        print(f"❌ Problème: {response.text}")

def main():
    print("🧪 Tests de sauvegarde de séance")
    print("=" * 50)

    # Test 1: Connexion
    token = test_login()

    if not token:
        print("\n❌ Impossible de continuer sans token")
        return

    # Test 2: Sauvegarde avec authentification
    test_sauvegarder_seance(token)

    # Test 3: Sauvegarde sans authentification
    test_sauvegarder_sans_auth()

    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    main()