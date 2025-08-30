#!/usr/bin/env python3
"""
Test simple de l'API des machines
"""
import urllib.request
import json

def test_machines_api():
    """Tester que l'API des machines retourne un tableau"""
    url = "http://127.0.0.1:8000/api/workouts/machines/"
    print(f"🧪 Test de l'API des machines: {url}")

    try:
        response = urllib.request.urlopen(url)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))

            if isinstance(data, list):
                print(f"✅ SUCCÈS: API retourne un tableau avec {len(data)} machines")
                if len(data) > 0:
                    print(f"   Première machine: {data[0].get('nom', 'N/A')}")
                return True
            else:
                print(f"❌ ÉCHEC: API retourne {type(data)} au lieu d'un tableau")
                print(f"   Contenu: {data}")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.getcode()}")
            return False

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Test de la Correction BEGIN_ARRAY")
    print("=" * 50)

    success = test_machines_api()

    print("\n" + "=" * 50)
    if success:
        print("🎉 CORRECTION RÉUSSIE: L'API des machines fonctionne !")
    else:
        print("❌ CORRECTION ÉCHOUÉE: L'erreur persiste")
    print("=" * 50)
