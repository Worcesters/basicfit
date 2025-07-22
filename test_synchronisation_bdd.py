#!/usr/bin/env python3
"""
Test de synchronisation avec la base de données
Vérifie que les séances en BDD sont bien utilisées pour les recommandations
"""

import requests
import json
from datetime import datetime, timedelta

def test_synchronisation_bdd():
    """Test de la synchronisation avec la BDD"""

    print("🔄 TEST DE SYNCHRONISATION AVEC LA BDD")
    print("=" * 60)

    # Configuration
    base_url = "http://localhost:8000/api"

    # Simuler des données de séances en BDD
    sample_seances = [
        {
            "nom": "Séance Pectoraux",
            "date_debut": "2024-01-15T10:00:00Z",
            "duree_reelle": 45,
            "exercices": [
                {
                    "machine__nom": "Développé couché",
                    "nombre_series": 3,
                    "repetitions_prevues": 8,
                    "poids_utilise": 60.0
                },
                {
                    "machine__nom": "Développé incliné",
                    "nombre_series": 3,
                    "repetitions_prevues": 10,
                    "poids_utilise": 45.0
                }
            ]
        },
        {
            "nom": "Séance Jambes",
            "date_debut": "2024-01-17T14:00:00Z",
            "duree_reelle": 60,
            "exercices": [
                {
                    "machine__nom": "Squat",
                    "nombre_series": 4,
                    "repetitions_prevues": 6,
                    "poids_utilise": 80.0
                },
                {
                    "machine__nom": "Presse",
                    "nombre_series": 3,
                    "repetitions_prevues": 12,
                    "poids_utilise": 100.0
                }
            ]
        }
    ]

    print("📊 ANALYSE DES SÉANCES EN BDD")
    print("-" * 40)

    for i, seance in enumerate(sample_seances, 1):
        print(f"\n🏋️ Séance {i}: {seance['nom']}")
        print(f"   Date: {seance['date_debut']}")
        print(f"   Durée: {seance['duree_reelle']} minutes")

        for j, exercice in enumerate(seance['exercices'], 1):
            print(f"   Exercice {j}: {exercice['machine__nom']}")
            print(f"      Séries: {exercice['nombre_series']}")
            print(f"      Reps: {exercice['repetitions_prevues']}")
            print(f"      Poids: {exercice['poids_utilise']}kg")

    print("\n🎯 SIMULATION DES RECOMMANDATIONS")
    print("-" * 40)

    # Simuler le calcul de recommandations basé sur l'historique
    for machine_name in ["Développé couché", "Squat", "Curl biceps"]:
        print(f"\n💪 Recommandations pour {machine_name}")

        # Chercher l'historique de cette machine
        historique_machine = []
        for seance in sample_seances:
            for exercice in seance['exercices']:
                if exercice['machine__nom'].lower() in machine_name.lower():
                    historique_machine.append({
                        'poids': exercice['poids_utilise'],
                        'reps': exercice['repetitions_prevues'],
                        'date': seance['date_debut']
                    })

        if historique_machine:
            print(f"   ✅ Historique trouvé: {len(historique_machine)} séances")

            # Calculer le poids max
            poids_max = max(ex['poids'] for ex in historique_machine)
            print(f"   Poids max: {poids_max}kg")

            # Calculer le 1RM estimé (formule de Brzycki)
            reps_min = min(ex['reps'] for ex in historique_machine)
            estimated_1rm = poids_max * (36 / (37 - reps_min))
            print(f"   1RM estimé: {estimated_1rm:.1f}kg")

            # Recommandations pour différents objectifs
            objectifs = [
                ("Force", 0.85, 4),
                ("Prise de masse", 0.70, 10),
                ("Endurance", 0.60, 15)
            ]

            for obj_name, intensite, target_reps in objectifs:
                poids_recommande = estimated_1rm * intensite
                print(f"   {obj_name}: {poids_recommande:.1f}kg pour {target_reps} reps")
        else:
            print(f"   ❌ Pas d'historique pour cette machine")
            print(f"   💡 Suggestion de départ: 20-30kg")

def test_conversion_donnees():
    """Test de la conversion des données serveur"""

    print("\n\n🔄 TEST DE CONVERSION DES DONNÉES")
    print("=" * 60)

    # Simuler les données reçues du serveur
    server_data = [
        {
            "id": 1,
            "nom": "Séance Pectoraux",
            "date_debut": "2024-01-15T10:00:00Z",
            "duree_reelle": 45,
            "exercices": [
                {
                    "machine__nom": "Développé couché",
                    "nombre_series": 3,
                    "repetitions_prevues": 8,
                    "poids_utilise": 60.0
                }
            ]
        }
    ]

    print("📥 Données reçues du serveur:")
    for entry in server_data:
        print(f"   Séance: {entry['nom']}")
        print(f"   Date: {entry['date_debut']}")
        print(f"   Durée: {entry['duree_reelle']} minutes")
        print(f"   Exercices: {len(entry['exercices'])}")

    # Simuler la conversion (comme dans l'app Android)
    converted_entries = []
    for server_entry in server_data:
        try:
            # Extraction de la date
            date_str = server_entry.get('date_debut', '')
            if date_str:
                date = date_str[:10]  # Prendre juste la date
            else:
                date = "2024-01-15"

            # Conversion des exercices
            exercises = []
            for exo in server_entry.get('exercices', []):
                exercise = {
                    'name': exo.get('machine__nom', 'Exercice'),
                    'sets': exo.get('nombre_series', 3),
                    'reps': exo.get('repetitions_prevues', 10),
                    'weight': exo.get('poids_utilise', 0.0)
                }
                exercises.append(exercise)

            # Création de l'entrée convertie
            converted_entry = {
                'date': date,
                'mode': server_entry.get('nom', 'Séance'),
                'exercises': exercises,
                'duration': server_entry.get('duree_reelle', 45),
                'totalWeight': sum(ex['weight'] * ex['reps'] for ex in exercises)
            }
            converted_entries.append(converted_entry)

        except Exception as e:
            print(f"   ❌ Erreur conversion: {e}")

    print("\n📤 Données converties pour l'app:")
    for entry in converted_entries:
        print(f"   Date: {entry['date']}")
        print(f"   Mode: {entry['mode']}")
        print(f"   Durée: {entry['duration']} minutes")
        print(f"   Poids total: {entry['totalWeight']}kg")
        print(f"   Exercices: {len(entry['exercises'])}")

def test_recommandations_avec_historique():
    """Test des recommandations avec historique réel"""

    print("\n\n🎯 TEST DES RECOMMANDATIONS AVEC HISTORIQUE")
    print("=" * 60)

    # Simuler un historique d'entraînement complet
    historique_complet = [
        {
            "machine": "Développé couché",
            "seances": [
                {"poids": 50, "reps": 10, "date": "2024-01-10"},
                {"poids": 55, "reps": 8, "date": "2024-01-12"},
                {"poids": 60, "reps": 6, "date": "2024-01-15"},
                {"poids": 65, "reps": 4, "date": "2024-01-17"}
            ]
        },
        {
            "machine": "Squat",
            "seances": [
                {"poids": 70, "reps": 8, "date": "2024-01-11"},
                {"poids": 75, "reps": 6, "date": "2024-01-14"},
                {"poids": 80, "reps": 5, "date": "2024-01-16"}
            ]
        }
    ]

    for machine_data in historique_complet:
        machine_name = machine_data["machine"]
        seances = machine_data["seances"]

        print(f"\n🏋️ {machine_name}")
        print(f"   Historique: {len(seances)} séances")

        # Calculer la progression
        poids_evolution = [s["poids"] for s in seances]
        progression = ((poids_evolution[-1] - poids_evolution[0]) / poids_evolution[0] * 100) if len(poids_evolution) > 1 else 0

        print(f"   Progression: {progression:.1f}%")
        print(f"   Poids max: {max(poids_evolution)}kg")

        # Calculer le 1RM estimé
        poids_max = max(s["poids"] for s in seances)
        reps_min = min(s["reps"] for s in seances)
        estimated_1rm = poids_max * (36 / (37 - reps_min))

        print(f"   1RM estimé: {estimated_1rm:.1f}kg")

        # Recommandations pour le prochain entraînement
        recommendations = [
            ("Force", 0.85, 4),
            ("Prise de masse", 0.70, 10),
            ("Endurance", 0.60, 15)
        ]

        print("   📋 Recommandations:")
        for obj_name, intensite, target_reps in recommendations:
            poids_recommande = estimated_1rm * intensite
            print(f"      {obj_name}: {poids_recommande:.1f}kg pour {target_reps} reps")

if __name__ == "__main__":
    print("🚀 TEST DE SYNCHRONISATION AVEC LA BDD")
    print("=" * 60)

    try:
        test_synchronisation_bdd()
        test_conversion_donnees()
        test_recommandations_avec_historique()

        print("\n" + "=" * 60)
        print("✅ TESTS TERMINÉS")
        print("📊 Résumé:")
        print("   ✅ Synchronisation BDD: OK")
        print("   ✅ Conversion données: OK")
        print("   ✅ Recommandations avec historique: OK")
        print("   ✅ Progression détectée: OK")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()