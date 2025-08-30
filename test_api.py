#!/usr/bin/env python3
"""
Script de test pour vérifier les APIs BasicFit
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_URL = f"{BASE_URL}/admin/"

def test_admin_access():
    """Tester l'accès à l'admin Django"""
    print(f"🔧 Test de l'admin Django: {ADMIN_URL}")
    try:
        response = requests.get(ADMIN_URL)
        if response.status_code == 200:
            print("✅ Admin accessible")
        else:
            print(f"❌ Admin non accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_machines_api():
    """Tester l'API des machines"""
    print(f"\n🏋️ Test de l'API des machines: {BASE_URL}/api/workouts/machines/")
    try:
        response = requests.get(f"{BASE_URL}/api/workouts/machines/")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ API machines OK - {len(data)} machines trouvées")
                print(f"   Format JSON: {type(data)}")
            else:
                print(f"❌ Format JSON incorrect: {type(data)}")
                print(f"   Contenu: {data}")
        else:
            print(f"❌ Erreur API machines: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_csv_import():
    """Tester l'import CSV"""
    print(f"\n📁 Test de l'import CSV: {BASE_URL}/api/workouts/import-csv/")

    # Créer un fichier CSV de test
    csv_content = """date,nom,duree,note_ressenti,commentaire,exercices,series,reps,poids
2025-01-15T10:00:00,Séance Test,60,8,Test import,Bench Press,3,10,50"""

    files = {
        'csv_file': ('test.csv', csv_content, 'text/csv')
    }

    try:
        response = requests.post(f"{BASE_URL}/api/workouts/import-csv/", files=files)
        if response.status_code == 401:
            print("⚠️  Import CSV nécessite une authentification (normal)")
        elif response.status_code == 200:
            print("✅ Import CSV réussi")
        else:
            print(f"❌ Erreur import CSV: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    """Fonction principale"""
    print("🧪 Tests des APIs BasicFit")
    print("=" * 50)

    test_admin_access()
    test_machines_api()
    test_csv_import()

    print("\n" + "=" * 50)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
