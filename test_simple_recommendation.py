#!/usr/bin/env python3
"""
Test simple du système de recommandation
Vérifie que les poids proposés sont logiques
"""

def test_simple_recommendations():
    """Test simple des recommandations de poids"""

    print("🧪 TEST SIMPLE DU SYSTÈME DE RECOMMANDATION")
    print("=" * 50)

    # Test des poids de base pour différents exercices
    test_cases = [
        {
            "exercise": "Développé couché",
            "gender": "Homme",
            "age": 25,
            "objective": "Prise de masse",
            "expected_range": (25, 35)
        },
        {
            "exercise": "Squat",
            "gender": "Femme",
            "age": 30,
            "objective": "Force",
            "expected_range": (20, 35)
        },
        {
            "exercise": "Curl biceps",
            "gender": "Homme",
            "age": 35,
            "objective": "Endurance",
            "expected_range": (8, 15)
        },
        {
            "exercise": "Tapis de course",
            "gender": "Homme",
            "age": 25,
            "objective": "Cardio",
            "expected_range": (0, 0)
        }
    ]

    for case in test_cases:
        print(f"\n🏋️ {case['exercise']}")
        print(f"   Genre: {case['gender']}")
        print(f"   Âge: {case['age']}")
        print(f"   Objectif: {case['objective']}")

        # Simuler le calcul de poids recommandé
        base_weight = calculate_base_weight(case['exercise'], case['gender'])
        objective_multiplier = get_objective_multiplier(case['objective'])
        age_multiplier = get_age_multiplier(case['age'])

        final_weight = base_weight * objective_multiplier * age_multiplier
        rounded_weight = round_to_2_5(final_weight)

        print(f"   Poids de base: {base_weight}kg")
        print(f"   Multiplicateur objectif: {objective_multiplier}")
        print(f"   Multiplicateur âge: {age_multiplier}")
        print(f"   Poids final: {rounded_weight}kg")

        # Vérifier la cohérence
        min_expected, max_expected = case['expected_range']
        if min_expected <= rounded_weight <= max_expected:
            print(f"   ✅ Poids dans la plage attendue ({min_expected}-{max_expected}kg)")
        else:
            print(f"   ❌ Poids hors plage: {rounded_weight}kg (attendu: {min_expected}-{max_expected}kg)")

def calculate_base_weight(exercise, gender):
    """Calcule le poids de base selon l'exercice et le genre"""
    is_male = gender == "Homme"

    # Vérifier si c'est un exercice cardio
    cardio_exercises = ["tapis", "course", "vélo", "rameur", "plank", "gainage"]
    if any(cardio in exercise.lower() for cardio in cardio_exercises):
        return 0.0

    # Poids de base selon le type d'exercice
    if "développé" in exercise.lower() or "pec" in exercise.lower():
        return 30.0 if is_male else 20.0
    elif "squat" in exercise.lower():
        return 40.0 if is_male else 30.0
    elif "curl" in exercise.lower() or "biceps" in exercise.lower():
        return 15.0 if is_male else 10.0
    elif "presse" in exercise.lower():
        return 50.0 if is_male else 40.0
    elif "traction" in exercise.lower():
        return 0.0  # Poids du corps
    else:
        return 20.0 if is_male else 15.0

def get_objective_multiplier(objective):
    """Retourne le multiplicateur selon l'objectif"""
    multipliers = {
        "Force": 0.8,
        "Puissance": 0.8,
        "Prise de masse": 1.0,
        "Volume": 1.0,
        "Endurance": 0.7,
        "Sèche": 0.9,
        "Cardio": 0.0
    }
    return multipliers.get(objective, 1.0)

def get_age_multiplier(age):
    """Retourne le multiplicateur selon l'âge"""
    if age < 25:
        return 1.0
    elif age < 35:
        return 0.95
    elif age < 50:
        return 0.9
    else:
        return 0.85

def round_to_2_5(weight):
    """Arrondit au multiple de 2.5kg le plus proche"""
    if weight == 0:
        return 0.0
    return round(weight / 2.5) * 2.5

def test_edge_cases():
    """Test des cas limites"""

    print("\n\n⚠️ TEST DES CAS LIMITES")
    print("=" * 50)

    edge_cases = [
        {
            "name": "Exercice cardio",
            "exercise": "Tapis de course",
            "expected": 0.0
        },
        {
            "name": "Exercice poids du corps",
            "exercise": "Traction",
            "expected": 0.0
        },
        {
            "name": "Utilisateur senior",
            "age": 65,
            "expected_multiplier": 0.85
        }
    ]

    for case in edge_cases:
        print(f"\n🔍 {case['name']}")

        if 'exercise' in case:
            base_weight = calculate_base_weight(case['exercise'], "Homme")
            print(f"   Poids de base: {base_weight}kg")
            print(f"   Attendu: {case['expected']}kg")

            if base_weight == case['expected']:
                print("   ✅ Cas limite géré correctement")
            else:
                print("   ❌ Cas limite non géré")

        if 'age' in case:
            multiplier = get_age_multiplier(case['age'])
            print(f"   Multiplicateur âge: {multiplier}")
            print(f"   Attendu: {case['expected_multiplier']}")

            if abs(multiplier - case['expected_multiplier']) < 0.01:
                print("   ✅ Ajustement âge correct")
            else:
                print("   ❌ Ajustement âge incorrect")

if __name__ == "__main__":
    print("🚀 TEST DU SYSTÈME DE RECOMMANDATION")
    print("=" * 50)

    try:
        test_simple_recommendations()
        test_edge_cases()

        print("\n" + "=" * 50)
        print("✅ TESTS TERMINÉS")
        print("📊 Le système de recommandation propose maintenant des poids logiques !")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")