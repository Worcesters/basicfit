#!/usr/bin/env python3
"""
Script pour vérifier les IDs des machines dans l'API
"""

import requests

def check_machine_ids():
    """Vérifie les IDs des machines dans l'API"""
    try:
        response = requests.get('http://localhost:8000/api/machines/')

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', [])

            print("IDs des machines dans l'API Django:")
            for machine in machines[:15]:  # Afficher les 15 premières
                print(f"ID {machine['id']}: {machine['nom']}")

            # Chercher le Face Pull
            face_pull = None
            for machine in machines:
                if 'face pull' in machine['nom'].lower():
                    face_pull = machine
                    break

            if face_pull:
                print(f"\n✅ Face Pull trouvé:")
                print(f"   ID: {face_pull['id']}")
                print(f"   Nom: {face_pull['nom']}")
                print(f"   GIF: {face_pull.get('image_gif', 'N/A')}")
            else:
                print("\n❌ Face Pull non trouvé")

        else:
            print(f"❌ Erreur API: {response.status_code}")

    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_machine_ids()