#!/usr/bin/env python3
"""
Script de test pour l'API BasicFit déployée sur Railway
URL: https://basicfit-production.up.railway.app
"""
import requests
import json

RAILWAY_URL = "https://basicfit-production.up.railway.app"

def test_api_status():
    """Test si l'API Railway répond"""
    print("🔍 Test de l'API Railway...")
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        print(f"✅ Statut HTTP: {response.status_code}")
        if response.status_code == 200:
            print("✅ API Railway est en ligne !")
            return True
        else:
            print(f"⚠️ Réponse inattendue: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_api_admin():
    """Test de l'interface admin Django"""
    print("\n🔍 Test de l'admin Django...")
    try:
        response = requests.get(f"{RAILWAY_URL}/admin/", timeout=10)
        if response.status_code == 200:
            print("✅ Interface admin accessible !")
            return True
        else:
            print(f"⚠️ Admin status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur admin: {e}")
        return False

def test_api_endpoints():
    """Test des endpoints API"""
    print("\n🔍 Test des endpoints API...")

    # Test endpoints potentiels
    endpoints = [
        "/api/",
        "/api/users/",
        "/api/workouts/",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=5)
            print(f"  {endpoint}: {response.status_code}")
        except:
            print(f"  {endpoint}: ❌ Erreur")

if __name__ == "__main__":
    print("🚀 TEST DE L'API RAILWAY BasicFit")
    print("=" * 50)

    # Tests de base
    api_ok = test_api_status()
    admin_ok = test_api_admin()

    if api_ok:
        test_api_endpoints()

        print("\n🎉 RÉSUMÉ:")
        print(f"✅ API Railway: {'OK' if api_ok else 'ERREUR'}")
        print(f"✅ Admin Django: {'OK' if admin_ok else 'ERREUR'}")
        print(f"\n🌐 Votre API est accessible à:")
        print(f"   {RAILWAY_URL}")
        print(f"   {RAILWAY_URL}/admin/")

        if api_ok and admin_ok:
            print("\n📱 PRÊT POUR ANDROID !")
            print("Votre app peut maintenant se connecter à Railway !")

    else:
        print("\n❌ L'API Railway n'est pas accessible")
        print("Vérifiez le statut dans Railway dashboard")