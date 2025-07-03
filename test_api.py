#!/usr/bin/env python3
"""
Script de test rapide pour l'API Django BasicFit
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Test de l'API Django BasicFit")
    print("=" * 50)

    # Test endpoint d'info
    print("\n1️⃣ Test endpoint d'information...")
    try:
        response = requests.get(f"{BASE_URL}/api/workouts/info/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data.get('message', 'API fonctionnelle')}")
        else:
            print(f"❌ ERREUR: Status {response.status_code}")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        print("⚠️  Assurez-vous que le serveur Django est démarré:")
        print("   cd backend && python manage.py runserver")
        return

    # Test création de compte
    print("\n2️⃣ Test création de compte...")
    try:
        test_user = {
            "email": "test@basicfit.com",
            "password": "test123456",
            "nom": "Test",
            "prenom": "User"
        }
        response = requests.post(f"{BASE_URL}/api/users/android/register/", json=test_user)
        data = response.json()
        if data.get('success'):
            print(f"✅ SUCCESS: Compte créé pour {data['user']['email']}")
        else:
            print(f"⚠️  INFO: {data.get('message', 'Compte existe déjà')}")
    except Exception as e:
        print(f"❌ ERREUR: {e}")

    print("\n✨ Tests terminés !")
    print(f"\n🌐 URLs utiles :")
    print(f"   - API Info: {BASE_URL}/api/workouts/info/")
    print(f"   - Admin: {BASE_URL}/admin/")

if __name__ == "__main__":
    test_api()
