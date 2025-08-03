#!/usr/bin/env python3
"""
Test standalone du calculateur 1RM professionnel
Teste le cas problématique: 3x12 à 59kg
"""

import sys
import os
sys.path.append('apps/workouts')

from advanced_1rm_calculator import calculate_professional_recommendation, Advanced1RMCalculator, WorkoutData

def test_problematic_case():
    """Teste le cas problématique: 3x12 à 59kg"""
    print("=" * 60)
    print("TEST DU NOUVEAU SYSTÈME 1RM PROFESSIONNEL")
    print("=" * 60)
    
    # Cas problématique rapporté
    current_weight = 59.0
    current_reps = 12
    current_sets = 3
    
    print(f"\n📊 DONNÉES ACTUELLES:")
    print(f"   Poids: {current_weight}kg")
    print(f"   Répétitions: {current_reps}")
    print(f"   Séries: {current_sets}")
    print(f"   Volume total: {current_weight * current_reps * current_sets}kg")
    
    # Test 1: Calculer le 1RM avec toutes les formules
    calculator = Advanced1RMCalculator()
    workout_data = WorkoutData(
        poids=current_weight,
        reps=current_reps,
        sets=current_sets,
        tempo="3-1-2"
    )
    
    one_rm_result = calculator.calculate_comprehensive_1rm(workout_data)
    
    print(f"\n🧮 CALCUL 1RM PROFESSIONNEL:")
    print(f"   1RM estimé: {one_rm_result.get('estimated_1rm')}kg")
    print(f"   Fiabilité: {one_rm_result.get('reliability')}")
    print(f"   Nb formules utilisées: {len(one_rm_result.get('raw_estimates', {}))}")
    print(f"   Intervalle confiance: {one_rm_result.get('confidence_range')}")
    
    if one_rm_result.get('raw_estimates'):
        print(f"\n📈 DÉTAIL DES FORMULES:")
        for formule, valeur in one_rm_result['raw_estimates'].items():
            print(f"      {formule.capitalize()}: {valeur:.1f}kg")
    
    # Test 2: Calculer la recommandation pour maintenir le même objectif (10 reps)
    target_reps = 10
    target_sets = 3
    
    print(f"\n🎯 RECOMMANDATION POUR {target_sets}x{target_reps}:")
    
    recommendation = calculate_professional_recommendation(
        current_weight=current_weight,
        current_reps=current_reps,
        current_sets=current_sets,
        target_reps=target_reps,
        target_sets=target_sets,
        tempo="3-1-2"
    )
    
    if recommendation['success']:
        print(f"   ✅ Poids recommandé: {recommendation['recommended_weight']}kg")
        print(f"   📊 Volume actuel: {recommendation['current_volume']}kg")
        print(f"   📈 Volume cible: {recommendation['target_volume']}kg")
        print(f"   📊 Ratio volume: {recommendation['volume_ratio']}")
        print(f"   💪 Intensité actuelle: {recommendation['current_intensity_percent']}% du 1RM")
        print(f"   🎯 Intensité cible: {recommendation['target_intensity_percent']}% du 1RM")
        print(f"   ⚖️ Facteur physiologique: {recommendation['physiological_factor']}")
    else:
        print(f"   ❌ Erreur: {recommendation.get('message')}")
    
    # Test 3: Comparaison avec l'ancienne méthode (Brzycki simple)
    print(f"\n🔄 COMPARAISON AVEC ANCIENNE MÉTHODE:")
    old_1rm = current_weight * (36 / (37 - current_reps))
    old_recommendation_10_reps = old_1rm * 0.75  # ~75% pour 10 reps
    
    print(f"   Ancien 1RM (Brzycki): {old_1rm:.1f}kg")
    print(f"   Ancienne recommandation 10 reps: {old_recommendation_10_reps:.1f}kg")
    
    if recommendation['success']:
        improvement = recommendation['recommended_weight'] - old_recommendation_10_reps
        print(f"   🔧 Amélioration: {improvement:+.1f}kg ({improvement/old_recommendation_10_reps*100:+.1f}%)")
    
    # Test 4: Différentes zones de répétitions
    print(f"\n🏋️ RECOMMANDATIONS POUR DIFFÉRENTS OBJECTIFS:")
    test_cases = [
        (5, 4, "Force"),
        (8, 4, "Puissance"), 
        (10, 3, "Hypertrophie"),
        (15, 3, "Endurance")
    ]
    
    for test_reps, test_sets, objectif in test_cases:
        test_rec = calculate_professional_recommendation(
            current_weight=current_weight,
            current_reps=current_reps,
            current_sets=current_sets,
            target_reps=test_reps,
            target_sets=test_sets,
            tempo="3-1-2"
        )
        
        if test_rec['success']:
            print(f"   {objectif} ({test_sets}x{test_reps}): {test_rec['recommended_weight']:.1f}kg "
                  f"({test_rec['target_intensity_percent']:.0f}% 1RM)")

def test_edge_cases():
    """Teste des cas limites"""
    print(f"\n🧪 TEST DES CAS LIMITES:")
    
    edge_cases = [
        (20, 1, 5, "Force max (1 rep)"),
        (10, 25, 2, "Endurance extrême"),
        (100, 5, 1, "Charge très lourde"),
        (5, 3, 8, "Charge très légère")
    ]
    
    for weight, reps, sets, description in edge_cases:
        try:
            result = calculate_professional_recommendation(
                current_weight=weight,
                current_reps=reps,
                current_sets=sets,
                target_reps=10,
                target_sets=3
            )
            
            status = "✅" if result.get('success') else "❌"
            rec_weight = result.get('recommended_weight', 'N/A')
            print(f"   {status} {description}: {weight}x{reps}x{sets} → {rec_weight}kg")
            
        except Exception as e:
            print(f"   ❌ {description}: Erreur - {e}")

if __name__ == "__main__":
    test_problematic_case()
    test_edge_cases()
    
    print(f"\n" + "=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)