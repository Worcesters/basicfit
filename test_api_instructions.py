#!/usr/bin/env python
import requests
import json

def test_api_instructions():
    """Test l'API pour vérifier si les instructions sont bien renvoyées"""

    # URL de l'API
    base_url = "https://basicfit-production.up.railway.app/api"

    try:
        # Test de l'endpoint machines (sans auth)
        response = requests.get(f"{base_url}/machines/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', data)  # Gérer les deux formats possibles
            print(f"✅ API machines accessible - {len(machines)} machines récupérées")

            # Vérifier les instructions pour les premières machines
            for i, machine in enumerate(machines[:5]):
                nom = machine.get('nom', 'N/A')
                instructions = machine.get('instructions', '')

                if instructions and instructions.strip():
                    print(f"✅ {nom}: {len(instructions)} caractères")
                else:
                    print(f"❌ {nom}: PAS D'INSTRUCTIONS")

                # Afficher les premières lignes des instructions
                if instructions:
                    preview = instructions[:100] + "..." if len(instructions) > 100 else instructions
                    print(f"   Preview: {preview}")
                print()

        else:
            print(f"❌ Erreur API machines: {response.status_code}")
            print(f"Réponse: {response.text}")

        # Test de l'endpoint workouts/machines/ (avec auth)
        print("\n" + "="*50)
        print("Test endpoint workouts/machines/ (avec auth)")
        print("="*50)

        # Simuler un token d'authentification (pour test)
        headers = {
            'Authorization': 'Bearer test_token',
            'Content-Type': 'application/json'
        }

        response = requests.get(f"{base_url}/workouts/machines/", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', data)  # Gérer les deux formats possibles
            print(f"✅ API workouts/machines accessible - {len(machines)} machines récupérées")

            # Vérifier les instructions pour les premières machines
            for i, machine in enumerate(machines[:5]):
                nom = machine.get('nom', 'N/A')
                instructions = machine.get('instructions', '')

                if instructions and instructions.strip():
                    print(f"✅ {nom}: {len(instructions)} caractères")
                else:
                    print(f"❌ {nom}: PAS D'INSTRUCTIONS")

                # Afficher les premières lignes des instructions
                if instructions:
                    preview = instructions[:100] + "..." if len(instructions) > 100 else instructions
                    print(f"   Preview: {preview}")
                print()

        else:
            print(f"❌ Erreur API workouts/machines: {response.status_code}")
            print(f"Réponse: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_api_instructions()