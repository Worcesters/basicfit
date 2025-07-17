#!/usr/bin/env python3
"""
Script pour tester l'endpoint workouts/machines/ et vérifier les GIFs
"""

import requests
import json

def test_workouts_machines():
    """Test pour vérifier l'endpoint workouts/machines/"""

    base_url = "https://basicfit-production.up.railway.app/api"

    try:
        print("🔍 Test de l'endpoint workouts/machines/...")

        # Test sans authentification d'abord
        response = requests.get(f"{base_url}/workouts/machines/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', data)
            print(f"✅ API accessible - {len(machines)} machines récupérées")

            # Chercher les machines avec des GIFs
            machines_with_gifs = []

            for machine in machines:
                nom = machine.get('nom', 'N/A')
                image_gif = machine.get('image_gif')

                if image_gif:
                    machines_with_gifs.append({
                        'nom': nom,
                        'gif_url': image_gif
                    })
                    print(f"\n🎬 Machine avec GIF: {nom}")
                    print(f"   URL: {image_gif}")

                    # Vérifier si l'URL est absolue
                    if image_gif.startswith('http'):
                        print(f"   ✅ URL absolue")

                        # Tester l'accès au GIF
                        try:
                            gif_response = requests.head(image_gif, timeout=5)
                            if gif_response.status_code == 200:
                                print(f"   ✅ GIF accessible")
                                print(f"   📏 Taille: {gif_response.headers.get('content-length', 'N/A')} bytes")
                            else:
                                print(f"   ❌ GIF non accessible (status: {gif_response.status_code})")
                        except Exception as e:
                            print(f"   ❌ Erreur d'accès: {e}")
                    else:
                        print(f"   ❌ URL relative - problème de configuration")
                else:
                    print(f"\n📋 Machine sans GIF: {nom}")

            if not machines_with_gifs:
                print("\n❌ Aucune machine avec GIF trouvée")
            else:
                print(f"\n📊 Résumé: {len(machines_with_gifs)} machines avec GIFs")

        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_workouts_machines()