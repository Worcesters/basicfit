#!/usr/bin/env python3
"""
Script pour tester l'API des machines et vérifier les URLs des GIFs
"""

import requests
import json

def test_machines_api():
    """Teste l'API des machines"""
    try:
        response = requests.get('http://localhost:8000/api/machines/')

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API accessible")
            print(f"Type de réponse: {type(data)}")
            print(f"Contenu: {json.dumps(data, indent=2)[:500]}...")

            # Essayer de comprendre la structure
            if isinstance(data, list):
                machines = data
                print(f"✅ {len(machines)} machines trouvées")

                for i, machine in enumerate(machines):
                    print(f"\n--- Machine {i+1} ---")
                    if isinstance(machine, dict):
                        print(f"Nom: {machine.get('nom', 'N/A')}")
                        print(f"ID: {machine.get('id', 'N/A')}")
                        print(f"Image GIF: {machine.get('image_gif', 'N/A')}")

                        # Vérifier si l'URL du GIF est accessible
                        gif_url = machine.get('image_gif')
                        if gif_url:
                            try:
                                gif_response = requests.head(gif_url, timeout=5)
                                print(f"GIF accessible: {gif_response.status_code == 200}")
                            except Exception as e:
                                print(f"GIF non accessible: {e}")
                        else:
                            print("Aucun GIF configuré")
                    else:
                        print(f"Machine {i+1}: {machine}")
            else:
                print(f"Format inattendu: {type(data)}")
                print(f"Contenu: {data}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_machines_api()