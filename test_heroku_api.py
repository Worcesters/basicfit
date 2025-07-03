#!/usr/bin/env python3
"""
Script de test pour l'API BasicFit déployée sur Heroku
"""
import requests
import json

def test_heroku_api():
    """Test de l'API BasicFit sur Heroku"""

    # Demander l'URL Heroku
    app_name = input("🏷️  Nom de votre app Heroku (ex: basicfit-jeremy) : ")
    base_url = f"https://{app_name}.herokuapp.com"

    print(f"\n🌐 Test de l'API : {base_url}")
    print("=" * 50)

    # Test 1: API Info
    try:
        print("\n📊 Test 1 : API Info...")
        response = requests.get(f"{base_url}/api/workouts/info/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ API Info - Succès !")
            print(f"   📈 Séances: {data.get('total_seances', 0)}")
            print(f"   💪 Exercices: {data.get('total_exercices', 0)}")
            print(f"   📊 Séries: {data.get('total_series', 0)}")
            print(f"   💬 Message: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

    # Test 2: Inscription
    try:
        print("\n👤 Test 2 : Inscription...")
        test_user = {
            "email": "test@basicfit.com",
            "password": "testpass123",
            "nom": "Test",
            "prenom": "User"
        }

        response = requests.post(
            f"{base_url}/api/users/android/register/",
            json=test_user,
            timeout=10
        )

        if response.status_code in [200, 201]:
            print("✅ Inscription - Succès !")
            data = response.json()
            print(f"   🆔 User ID: {data.get('user_id', 'N/A')}")
            print(f"   📧 Email: {data.get('email', 'N/A')}")
        elif response.status_code == 400:
            print("⚠️  Utilisateur déjà existant (normal)")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

    # Test 3: Connexion
    try:
        print("\n🔐 Test 3 : Connexion...")
        login_data = {
            "email": "test@basicfit.com",
            "password": "testpass123"
        }

        response = requests.post(
            f"{base_url}/api/users/android/login/",
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Connexion - Succès !")
            data = response.json()
            print(f"   🔑 Token présent: {'access' in data}")
            print(f"   👤 Nom: {data.get('nom', 'N/A')} {data.get('prenom', 'N/A')}")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")

    print("\n🎯 Tests terminés !")
    print(f"\n📱 Pour l'app Android, utilisez :")
    print(f"   BASE_URL = \"{base_url}/\"")
    print(f"\n🌐 Interface admin Django :")
    print(f"   {base_url}/admin/")

    return True

if __name__ == "__main__":
    print("🚀 Test de l'API BasicFit sur Heroku")
    print("====================================")
    test_heroku_api()

    input("\n⏎ Appuyez sur Entrée pour quitter...")