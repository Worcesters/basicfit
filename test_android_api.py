#!/usr/bin/env python3
"""
Script de test pour l'API Android BasicFit sur Railway
"""
import requests
import json

# Configuration
API_BASE_URL = "https://basicfitv2-production.up.railway.app/api"
TEST_USER = {
    "email": "test@basicfit.com",
    "password": "testpassword123",
    "nom": "Test User",
    "prenom": "Test"
}

def test_api_connection():
    """Test de connexion à l'API"""
    print("🔗 Test de connexion à l'API...")
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api', '')}/")
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_user_registration():
    """Test d'inscription utilisateur"""
    print("\n👤 Test d'inscription utilisateur...")

    data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "nom": TEST_USER["nom"],
        "prenom": TEST_USER["prenom"],
        "poids": 70.0,
        "taille": 175,
        "genre": "Homme",
        "objectif_sportif": "Prise de masse",
        "niveau_experience": "Modéré"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/users/android/register/",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                print("✅ Inscription réussie")
                return result.get("token")
            else:
                print(f"❌ Inscription échouée: {result.get('message')}")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erreur d'inscription: {e}")
        return None

def test_user_login():
    """Test de connexion utilisateur"""
    print("\n🔐 Test de connexion utilisateur...")

    data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/users/android/login/",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Connexion réussie")
                return result.get("token")
            else:
                print(f"❌ Connexion échouée: {result.get('message')}")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_user_profile(token):
    """Test de récupération du profil utilisateur"""
    print("\n👥 Test de profil utilisateur...")

    if not token:
        print("❌ Pas de token disponible")
        return False

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{API_BASE_URL}/users/android/profile/",
            headers=headers
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Profil récupéré avec succès")
                return True
            else:
                print(f"❌ Erreur profil: {result.get('message')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erreur de profil: {e}")
        return False

def test_workout_save(token):
    """Test de sauvegarde d'entraînement"""
    print("\n🏋️ Test de sauvegarde d'entraînement...")

    if not token:
        print("❌ Pas de token disponible")
        return False

    data = {
        "nom": "Test Workout Android",
        "date_debut": "2024-01-15 10:00:00",
        "duree_minutes": 45,
        "exercises": [
            {
                "nom": "Développé couché",
                "series": 4,
                "repetitions": 10,
                "poids": 80.0
            },
            {
                "nom": "Tirage vertical",
                "series": 3,
                "repetitions": 12,
                "poids": 70.0
            }
        ]
    }

    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{API_BASE_URL}/workouts/sauvegarder/",
            json=data,
            headers=headers
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                print("✅ Entraînement sauvegardé avec succès")
                return True
            else:
                print(f"❌ Erreur sauvegarde: {result.get('message')}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erreur de sauvegarde: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🔧 TEST DE L'API ANDROID BASICFIT SUR RAILWAY")
    print("=" * 60)

    # Test de connexion à l'API
    if not test_api_connection():
        print("\n❌ Impossible de continuer sans connexion API")
        return

    # Test d'inscription (peut échouer si l'utilisateur existe déjà)
    token = test_user_registration()

    # Test de connexion
    if not token:
        token = test_user_login()

    if not token:
        print("\n❌ Impossible de continuer sans token d'authentification")
        return

    print(f"\n🔑 Token obtenu: {token[:50]}...")

    # Test du profil utilisateur
    test_user_profile(token)

    # Test de sauvegarde d'entraînement
    test_workout_save(token)

    print("\n" + "=" * 60)
    print("✅ TESTS TERMINÉS")
    print("💡 Si tous les tests passent, l'application Android peut")
    print("   se connecter et synchroniser avec votre BDD Django !")
    print("=" * 60)

if __name__ == "__main__":
    main()