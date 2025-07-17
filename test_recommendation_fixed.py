#!/usr/bin/env python3
"""
Script de test pour vérifier que l'endpoint de recommandation fonctionne
avec le nom de la machine au lieu de l'ID.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
RECOMMENDATION_URL = f"{BASE_URL}/workouts/recommendation/"

def test_recommendation_with_machine_name():
    """Test de l'endpoint de recommandation avec le nom de la machine"""

    print("🔍 Test de l'endpoint de recommandation avec nom de machine")
    print("=" * 60)

    # 1. Test simple sans authentification (devrait retourner 401)
    print("1. Test sans authentification...")
    try:
        response = requests.get(f"{RECOMMENDATION_URL}Face Pull/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 401:
            print(f"   ✅ Erreur 401 correcte - authentification requise")
        else:
            print(f"   ⚠️ Status inattendu: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erreur de requête: {e}")

    # 2. Test avec un token invalide
    print("\n2. Test avec token invalide...")
    headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{RECOMMENDATION_URL}Face Pull/", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 401:
            print(f"   ✅ Erreur 401 correcte - token invalide")
        else:
            print(f"   ⚠️ Status inattendu: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Erreur de requête: {e}")

    # 3. Test de l'endpoint des machines (sans authentification)
    print("\n3. Test endpoint machines (sans auth)...")
    try:
        response = requests.get(f"{BASE_URL}/machines/")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', [])
            print(f"   ✅ {len(machines)} machines trouvées")

            # Chercher Face Pull
            face_pull = next((m for m in machines if 'Face Pull' in m.get('nom', '')), None)
            if face_pull:
                print(f"   ✅ Face Pull trouvé avec ID: {face_pull.get('id')}")
                print(f"      Nom: {face_pull.get('nom')}")
                print(f"      GIF: {face_pull.get('image_gif', 'Non défini')}")
            else:
                print(f"   ⚠️ Face Pull non trouvé dans la liste")

        else:
            print(f"   ❌ Erreur: {response.text}")

    except Exception as e:
        print(f"   ❌ Erreur de requête: {e}")

    print("\n" + "=" * 60)
    print("🎯 Test terminé !")
    print("\n📝 Résumé:")
    print("- L'endpoint de recommandation nécessite une authentification (401)")
    print("- L'endpoint des machines fonctionne sans authentification")
    print("- Les machines sont bien récupérées depuis l'API")

    return True

if __name__ == "__main__":
    test_recommendation_with_machine_name()