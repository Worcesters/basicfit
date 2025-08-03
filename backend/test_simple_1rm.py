#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple du calculateur 1RM professionnel
Teste le cas problématique: 3x12 à 59kg
"""

import sys
import os
sys.path.append('apps/workouts')

from advanced_1rm_calculator import calculate_professional_recommendation, Advanced1RMCalculator, WorkoutData

def test_problematic_case():
    """Teste le cas problématique: 3x12 à 59kg"""
    print("=" * 60)
    print("TEST DU NOUVEAU SYSTEME 1RM PROFESSIONNEL")
    print("=" * 60)
    
    # Cas problématique rapporté
    current_weight = 59.0
    current_reps = 12
    current_sets = 3
    
    print(f"\nDONNEES ACTUELLES:")
    print(f"   Poids: {current_weight}kg")
    print(f"   Repetitions: {current_reps}")
    print(f"   Series: {current_sets}")
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
    
    print(f"\nCALCUL 1RM PROFESSIONNEL:")
    print(f"   1RM estime: {one_rm_result.get('estimated_1rm')}kg")
    print(f"   Fiabilite: {one_rm_result.get('reliability')}")
    print(f"   Nb formules utilisees: {len(one_rm_result.get('raw_estimates', {}))}")
    
    if one_rm_result.get('raw_estimates'):
        print(f"\nDETAIL DES FORMULES:")
        for formule, valeur in one_rm_result['raw_estimates'].items():
            print(f"      {formule.capitalize()}: {valeur:.1f}kg")
    
    # Test 2: Calculer la recommandation pour maintenir le même objectif (10 reps)
    target_reps = 10
    target_sets = 3
    
    print(f"\nRECOMMANDATION POUR {target_sets}x{target_reps}:")
    
    recommendation = calculate_professional_recommendation(
        current_weight=current_weight,
        current_reps=current_reps,
        current_sets=current_sets,
        target_reps=target_reps,
        target_sets=target_sets,
        tempo="3-1-2"
    )
    
    if recommendation['success']:
        print(f"   Poids recommande: {recommendation['recommended_weight']}kg")
        print(f"   Volume actuel: {recommendation['current_volume']}kg")
        print(f"   Volume cible: {recommendation['target_volume']}kg")
        print(f"   Ratio volume: {recommendation['volume_ratio']}")
        print(f"   Intensite actuelle: {recommendation['current_intensity_percent']}% du 1RM")
        print(f"   Intensite cible: {recommendation['target_intensity_percent']}% du 1RM")
    else:
        print(f"   Erreur: {recommendation.get('message')}")
    
    # Test 3: Comparaison avec l'ancienne méthode (Brzycki simple)
    print(f"\nCOMPARAISON AVEC ANCIENNE METHODE:")
    old_1rm = current_weight * (36 / (37 - current_reps))
    old_recommendation_10_reps = old_1rm * 0.75  # ~75% pour 10 reps
    
    print(f"   Ancien 1RM (Brzycki): {old_1rm:.1f}kg")
    print(f"   Ancienne recommandation 10 reps: {old_recommendation_10_reps:.1f}kg")
    
    if recommendation['success']:
        improvement = recommendation['recommended_weight'] - old_recommendation_10_reps
        print(f"   Amelioration: {improvement:+.1f}kg ({improvement/old_recommendation_10_reps*100:+.1f}%)")

if __name__ == "__main__":
    test_problematic_case()
    print("\n" + "=" * 60)
    print("TESTS TERMINES")
    print("=" * 60)