#!/usr/bin/env python3
"""
Script de test pour l'API BasicFit déployée sur Railway
"""
import requests
import json
from datetime import datetime

# À remplacer par votre URL Railway
RAILWAY_URL = "https://votre-app.railway.app"
API_URL = f"{RAILWAY_URL}/api"

def test_api_info():
    """Test de l'endpoint d'information de l'API"""
    print("🔍 Test de l'API info...")
    try:
        response = requests.get(f"{API_URL}/info/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API Info OK :", data)
            return True
        else:
            print(f"❌ Erreur API Info : {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def test_user_registration():
    """Test de création d'utilisateur"""
    print("\n👤 Test d'inscription utilisateur...")

    test_user = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

    try:
        response = requests.post(
            f"{API_URL}/users/android/register/",
            json=test_user,
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            print("✅ Inscription réussie !")
            print(f"   Token: {data.get('access', 'N/A')[:20]}...")
            return data.get('access'), test_user
        else:
            print(f"❌ Erreur inscription : {response.status_code}")
            print(f"   Réponse : {response.text}")
            return None, test_user

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return None, test_user

def test_user_login(user_data):
    """Test de connexion utilisateur"""
    print("\n🔐 Test de connexion...")

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    try:
        response = requests.post(
            f"{API_URL}/users/android/login/",
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Connexion réussie !")
            print(f"   Token: {data.get('access', 'N/A')[:20]}...")
            return data.get('access')
        else:
            print(f"❌ Erreur connexion : {response.status_code}")
            print(f"   Réponse : {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return None

def test_workout_save(token):
    """Test de sauvegarde de séance"""
    print("\n💪 Test de sauvegarde de séance...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    workout_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "exercices": [
            {
                "nom": "Développé couché",
                "series": [
                    {"reps": 10, "poids": 80.0},
                    {"reps": 8, "poids": 85.0}
                ]
            }
        ],
        "duree_minutes": 45,
        "notes": "Test depuis Railway"
    }

    try:
        response = requests.post(
            f"{API_URL}/workouts/sauvegarder/",
            json=workout_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            print("✅ Séance sauvegardée !")
            print(f"   ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Erreur sauvegarde : {response.status_code}")
            print(f"   Réponse : {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 TEST DE L'API BASICFIT SUR RAILWAY")
    print("=" * 50)
    print(f"URL testée : {API_URL}")
    print()

    # Mise à jour de l'URL si nécessaire
    if "votre-app" in RAILWAY_URL:
        print("⚠️  ATTENTION : Mettez à jour RAILWAY_URL avec votre vraie URL !")
        print("   Modifiez la ligne 10 de ce fichier avec votre URL Railway")
        print()
        return

    # Test 1 : API Info
    if not test_api_info():
        print("\n❌ L'API n'est pas accessible. Vérifiez :")
        print("   1. URL correcte")
        print("   2. Déploiement Railway réussi")
        print("   3. Service en ligne")
        return

    # Test 2 : Inscription
    token, user_data = test_user_registration()
    if not token:
        print("\n❌ Test d'inscription échoué")
        return

    # Test 3 : Connexion
    token = test_user_login(user_data)
    if not token:
        print("\n❌ Test de connexion échoué")
        return

    # Test 4 : Sauvegarde séance
    test_workout_save(token)

    print("\n" + "=" * 50)
    print("🎉 TESTS TERMINÉS !")
    print("=" * 50)
    print("\n📱 Votre API Railway est prête pour Android !")
    print(f"   URL à utiliser : {API_URL}/")
    print("\n📋 Prochaines étapes :")
    print("   1. Mettez à jour ApiService.kt avec cette URL")
    print("   2. Recompilez l'app Android")
    print("   3. Testez la connexion depuis l'app")

if __name__ == "__main__":
    main()