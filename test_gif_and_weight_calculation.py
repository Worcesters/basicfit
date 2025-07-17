#!/usr/bin/env python3
"""
Script de test pour vérifier les GIFs et le calcul de poids recommandé
"""

import requests
import json

def test_gifs_and_weight_calculation():
    """Test l'API pour vérifier les GIFs et les données nécessaires au calcul de poids"""

    base_url = "https://basicfit-production.up.railway.app/api"

    try:
        # Test de l'endpoint machines
        print("🔍 Test de l'API machines...")
        response = requests.get(f"{base_url}/machines/", timeout=10)

        if response.status_code == 200:
            data = response.json()
            machines = data.get('results', data)
            print(f"✅ API accessible - {len(machines)} machines récupérées")

            # Vérifier les GIFs et groupes musculaires
            gif_count = 0
            muscle_group_count = 0

            for i, machine in enumerate(machines[:10]):  # Test sur les 10 premières
                nom = machine.get('nom', 'N/A')
                image_gif = machine.get('image_gif')
                groupes_musculaires = machine.get('groupes_musculaires_primaires', [])

                print(f"\n📋 Machine {i+1}: {nom}")

                # Vérifier le GIF
                if image_gif:
                    gif_count += 1
                    print(f"   ✅ GIF: {image_gif}")
                else:
                    print(f"   ❌ Pas de GIF")

                # Vérifier les groupes musculaires
                if groupes_musculaires:
                    muscle_group_count += 1
                    groupes = [g.get('nom', '') for g in groupes_musculaires]
                    print(f"   ✅ Groupes musculaires: {', '.join(groupes)}")
                else:
                    print(f"   ❌ Pas de groupes musculaires")

                # Vérifier les autres champs nécessaires
                poids_min = machine.get('poids_minimum', 0)
                poids_max = machine.get('poids_maximum', 200)
                print(f"   📊 Poids: {poids_min}-{poids_max}kg")

                # Simuler le calcul de poids recommandé
                categorie = machine.get('categorie', '')
                if 'cardio' in nom.lower():
                    print(f"   🏃 Cardio - pas de poids recommandé")
                else:
                    # Logique simplifiée de calcul de poids
                    base_weight = 20.0  # Poids par défaut
                    if any(g in nom.lower() for g in ['pectoraux', 'chest']):
                        base_weight = 30.0
                    elif any(g in nom.lower() for g in ['dos', 'back']):
                        base_weight = 25.0
                    elif any(g in nom.lower() for g in ['jambes', 'legs']):
                        base_weight = 40.0

                    print(f"   💪 Poids recommandé estimé: {base_weight}kg")

            print(f"\n📊 Résumé:")
            print(f"   GIFs disponibles: {gif_count}/{len(machines[:10])}")
            print(f"   Groupes musculaires: {muscle_group_count}/{len(machines[:10])}")

        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Réponse: {response.text}")

    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_gifs_and_weight_calculation()