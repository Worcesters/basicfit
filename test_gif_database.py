#!/usr/bin/env python3
"""
Script pour vérifier les GIFs dans la base de données Django
"""

import requests
import json

def test_gif_database():
    """Test pour vérifier les GIFs dans la base de données"""

    base_url = "https://basicfit-production.up.railway.app/api"

    try:
        # Test de l'endpoint machines avec plus de détails
        print("🔍 Test détaillé de l'API machines...")
        response = requests.get(f"{base_url}/machines/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', data)
            print(f"✅ API accessible - {len(machines)} machines récupérées")

            # Chercher spécifiquement les machines avec des GIFs
            machines_with_gifs = []

            for i, machine in enumerate(machines):
                nom = machine.get('nom', 'N/A')
                image_gif = machine.get('image_gif')

                if image_gif:
                    machines_with_gifs.append({
                        'nom': nom,
                        'gif_url': image_gif
                    })
                    print(f"\n🎬 Machine avec GIF trouvée:")
                    print(f"   Nom: {nom}")
                    print(f"   URL GIF: {image_gif}")

                    # Tester si l'URL du GIF est accessible
                    try:
                        gif_response = requests.head(image_gif, timeout=5)
                        if gif_response.status_code == 200:
                            print(f"   ✅ GIF accessible")
                        else:
                            print(f"   ❌ GIF non accessible (status: {gif_response.status_code})")
                    except Exception as e:
                        print(f"   ❌ Erreur d'accès au GIF: {e}")

            if not machines_with_gifs:
                print("\n❌ Aucune machine avec GIF trouvée dans la base de données")
                print("   Cela signifie que:")
                print("   1. Aucun GIF n'a été uploadé dans l'admin Django")
                print("   2. Les GIFs ne sont pas correctement liés aux machines")
                print("   3. Il y a un problème de configuration des médias")

            # Afficher quelques exemples de machines pour debug
            print(f"\n📋 Exemples de machines (premières 5):")
            for i, machine in enumerate(machines[:5]):
                nom = machine.get('nom', 'N/A')
                image_gif = machine.get('image_gif')
                print(f"   {i+1}. {nom}")
                print(f"      GIF: {image_gif if image_gif else 'Aucun'}")

        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_gif_database()