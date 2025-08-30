#!/usr/bin/env python3
"""
Script de test simple pour vérifier les APIs BasicFit
"""
import urllib.request
import urllib.parse
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_admin_access():
    """Tester l'accès à l'admin Django"""
    print(f"🔧 Test de l'admin Django: {BASE_URL}/admin/")
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/admin/")
        if response.getcode() == 200:
            print("✅ Admin accessible")
        else:
            print(f"❌ Admin non accessible: {response.getcode()}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_machines_api():
    """Tester l'API des machines"""
    print(f"\n🏋️ Test de l'API des machines: {BASE_URL}/api/workouts/machines/")
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/api/workouts/machines/")
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            if isinstance(data, list):
                print(f"✅ API machines OK - {len(data)} machines trouvées")
                print(f"   Format JSON: {type(data)}")
                if len(data) > 0:
                    print(f"   Première machine: {data[0].get('nom', 'N/A')}")
            else:
                print(f"❌ Format JSON incorrect: {type(data)}")
                print(f"   Contenu: {data}")
        else:
            print(f"❌ Erreur API machines: {response.getcode()}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_home_page():
    """Tester la page d'accueil"""
    print(f"\n🏠 Test de la page d'accueil: {BASE_URL}/")
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/")
        if response.getcode() == 200:
            content = response.read().decode('utf-8')
            if "BasicFit v2 API" in content:
                print("✅ Page d'accueil accessible")
            else:
                print("⚠️  Page d'accueil accessible mais contenu inattendu")
        else:
            print(f"❌ Erreur page d'accueil: {response.getcode()}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    """Fonction principale"""
    print("🧪 Tests des APIs BasicFit")
    print("=" * 50)

    test_home_page()
    test_admin_access()
    test_machines_api()

    print("\n" + "=" * 50)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
