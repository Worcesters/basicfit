#!/usr/bin/env python3
"""
Script de diagnostic pour le problème des recommandations bloquées sur 20kg
"""

def test_recommendation_diagnostic():
    """Teste le diagnostic des recommandations"""

    print("🔍 DIAGNOSTIC DES RECOMMANDATIONS")
    print("=" * 50)

    # Simuler différents scénarios
    test_cases = [
        {
            "machine": "Développé couché",
            "genre": "Homme",
            "objectif": "Prise de masse",
            "age": 25,
            "historique": True,
            "poids_historique": [30, 35, 40, 45, 50]
        },
        {
            "machine": "Machine inconnue",
            "genre": "Homme",
            "objectif": "Force",
            "age": 30,
            "historique": False,
            "poids_historique": []
        },
        {
            "machine": "Curl biceps",
            "genre": "Femme",
            "objectif": "Endurance",
            "age": 28,
            "historique": True,
            "poids_historique": [8, 10, 12]
        },
        {
            "machine": "Tapis de course",
            "genre": "Homme",
            "objectif": "Sèche",
            "age": 35,
            "historique": False,
            "poids_historique": []
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {case['machine']}")
        print(f"   Genre: {case['genre']}")
        print(f"   Objectif: {case['objectif']}")
        print(f"   Âge: {case['age']}")
        print(f"   Historique: {'Oui' if case['historique'] else 'Non'}")

        if case['historique']:
            print(f"   Poids utilisés: {case['poids_historique']} kg")
            max_weight = max(case['poids_historique'])
            avg_weight = sum(case['poids_historique']) / len(case['poids_historique'])
            print(f"   Poids max: {max_weight} kg")
            print(f"   Poids moyen: {avg_weight:.1f} kg")

            # Simuler le calcul de recommandation avec historique
            if "Tapis" in case['machine'] or "Cardio" in case['machine']:
                recommended_weight = 0.0
                print(f"   ✅ Recommandation cardio: {recommended_weight} kg")
            else:
                # Simuler le calcul basé sur le 1RM
                estimated_1rm = max_weight * 1.1  # Approximation
                if case['objectif'] == "Force":
                    recommended_weight = estimated_1rm * 0.8
                elif case['objectif'] == "Prise de masse":
                    recommended_weight = estimated_1rm * 0.7
                elif case['objectif'] == "Endurance":
                    recommended_weight = estimated_1rm * 0.6
                else:
                    recommended_weight = estimated_1rm * 0.65

                print(f"   ✅ Recommandation avec historique: {recommended_weight:.1f} kg")
        else:
            # Simuler le calcul de poids de départ
            base_weight = calculate_starting_weight(case['machine'], case['genre'], case['age'], case['objectif'])
            print(f"   ⚠️ Poids de départ: {base_weight} kg")

            if base_weight in [20.0, 15.0]:
                print(f"   ❌ PROBLÈME DÉTECTÉ: Poids par défaut utilisé!")
                print(f"   💡 Suggestion: Ajouter des patterns pour '{case['machine']}'")
            else:
                print(f"   ✅ Poids de départ adapté")

    print(f"\n🎯 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    print("Problèmes possibles:")
    print("1. Pas d'historique pour certaines machines")
    print("2. Patterns manquants dans calculateStartingWeight")
    print("3. Synchronisation BDD non fonctionnelle")
    print("4. Machine non reconnue par le système")

    print("\nSolutions recommandées:")
    print("1. Effectuer quelques séances pour créer un historique")
    print("2. Ajouter des patterns spécifiques pour les machines problématiques")
    print("3. Vérifier la synchronisation avec la base de données")
    print("4. Consulter les logs de l'application pour plus de détails")

def calculate_starting_weight(machine_name, gender, age, objectif):
    """Simule le calcul de poids de départ"""

    is_male = gender == "Homme"

    # Patterns de base
    base_weight = 0.0

    if "développé" in machine_name.lower() or "bench" in machine_name.lower():
        base_weight = 30.0 if is_male else 20.0
    elif "squat" in machine_name.lower():
        base_weight = 40.0 if is_male else 30.0
    elif "curl" in machine_name.lower():
        base_weight = 15.0 if is_male else 10.0
    elif "tapis" in machine_name.lower() or "cardio" in machine_name.lower():
        base_weight = 0.0
    elif "machine inconnue" in machine_name.lower():
        # Cas problématique - retourne le poids par défaut
        base_weight = 20.0 if is_male else 15.0
    else:
        # Logique intelligente pour les autres machines
        machine_lower = machine_name.lower()
        if "press" in machine_lower:
            base_weight = 25.0 if is_male else 18.0
        elif "lift" in machine_lower:
            base_weight = 30.0 if is_male else 20.0
        elif "fly" in machine_lower:
            base_weight = 12.0 if is_male else 8.0
        else:
            base_weight = 18.0 if is_male else 12.0

    # Ajustements par âge
    age_multiplier = 1.0
    if age < 25:
        age_multiplier = 1.0
    elif age < 35:
        age_multiplier = 0.95
    elif age < 50:
        age_multiplier = 0.9
    else:
        age_multiplier = 0.85

    # Ajustements par objectif
    objective_multiplier = 1.0
    if objectif == "Force":
        objective_multiplier = 0.8
    elif objectif == "Endurance":
        objective_multiplier = 0.7
    elif objectif == "Sèche":
        objective_multiplier = 0.9

    final_weight = base_weight * age_multiplier * objective_multiplier

    # Arrondir à 2.5kg près
    rounded_weight = round(final_weight / 2.5) * 2.5

    return rounded_weight

if __name__ == "__main__":
    test_recommendation_diagnostic()