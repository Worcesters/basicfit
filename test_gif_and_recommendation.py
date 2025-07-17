#!/usr/bin/env python3
"""
Script de test pour vérifier les GIFs et les recommandations
"""

import requests
import json

def test_gif_url():
    """Teste l'URL du GIF du Face Pull"""
    gif_url = "https://res.cloudinary.com/dnernoibr/image/upload/v1752739063/basicfit/machines/gifs/machine_pull-up.gif"

    print("🔍 Test de l'URL du GIF...")
    try:
        response = requests.head(gif_url, timeout=10)
        if response.status_code == 200:
            print("✅ GIF accessible")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'N/A')}")

            # Vérifier si c'est bien un GIF
            content_type = response.headers.get('content-type', '')
            if 'gif' in content_type.lower():
                print("✅ C'est bien un fichier GIF")
            else:
                print("⚠️ Le Content-Type n'indique pas un GIF")

        else:
            print(f"❌ GIF non accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors du test du GIF: {e}")

def test_api_machines_with_gif():
    """Teste l'API des machines pour voir si le GIF est bien retourné"""
    print("\n🔍 Test de l'API des machines...")
    try:
        response = requests.get('http://localhost:8000/api/machines/')

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', [])

            # Chercher le Face Pull
            face_pull = None
            for machine in machines:
                if 'face pull' in machine.get('nom', '').lower():
                    face_pull = machine
                    break

            if face_pull:
                print(f"✅ Face Pull trouvé: {face_pull['nom']}")
                gif_url = face_pull.get('image_gif')
                if gif_url:
                    print(f"✅ URL GIF: {gif_url}")
                    if gif_url == "https://res.cloudinary.com/dnernoibr/image/upload/v1752739063/basicfit/machines/gifs/machine_pull-up.gif":
                        print("✅ URL GIF correcte")
                    else:
                        print(f"⚠️ URL GIF différente: {gif_url}")
                else:
                    print("❌ Pas d'URL GIF dans l'API")
            else:
                print("❌ Face Pull non trouvé dans l'API")
        else:
            print(f"❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors du test de l'API: {e}")

def test_recommendation_endpoint():
    """Teste l'endpoint de recommandation"""
    print("\n🔍 Test de l'endpoint de recommandation...")

    # D'abord, récupérer les machines
    try:
        response = requests.get('http://localhost:8000/api/machines/')
        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', [])

            if machines:
                machine_id = machines[0]['id']
                machine_name = machines[0]['nom']

                print(f"   Test avec la machine: {machine_name} (ID: {machine_id})")

                # Tester l'endpoint de recommandation
                reco_url = f"http://localhost:8000/api/workouts/recommendation/{machine_id}/"
                reco_response = requests.get(reco_url)

                print(f"   URL testée: {reco_url}")
                print(f"   Statut: {reco_response.status_code}")

                if reco_response.status_code == 200:
                    reco_data = reco_response.json()
                    print("✅ Recommandation récupérée")
                    print(f"   Poids recommandé: {reco_data.get('poids_recommande')}kg")
                    print(f"   Source: {reco_data.get('source')}")
                elif reco_response.status_code == 401:
                    print("❌ Non autorisé - authentification requise")
                elif reco_response.status_code == 404:
                    print("❌ Endpoint non trouvé")
                else:
                    print(f"❌ Erreur: {reco_response.status_code}")
                    print(f"   Réponse: {reco_response.text}")
            else:
                print("❌ Aucune machine trouvée")
        else:
            print(f"❌ Erreur lors de la récupération des machines: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors du test de recommandation: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 TEST DES GIFS ET RECOMMANDATIONS")
    print("=" * 50)

    test_gif_url()
    test_api_machines_with_gif()
    test_recommendation_endpoint()

    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ")
    print("✅ Tests terminés")
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifier que l'application Android utilise AnimatedGifImage")
    print("   2. Tester l'authentification pour les recommandations")
    print("   3. Vérifier que les séances sont bien sauvegardées")

if __name__ == "__main__":
    main()