#!/usr/bin/env python3
"""
Test direct des fonctions de recommandation générique
"""

import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.simple_recommendation import get_generic_recommendation, get_generic_recommendation_by_name

def test_generic_recommendations():
    print("=== TEST DES RECOMMANDATIONS GÉNÉRIQUES ===")
    
    # Test par ID
    print("\n1. Test recommandation générique par ID...")
    result = get_generic_recommendation(1)
    print(f"   Succès: {result.get('success')}")
    if result.get('success'):
        data = result['data']
        print(f"   Machine: {data.get('machine_nom')}")
        print(f"   Poids: {data.get('poids_recommande')}kg")
        print(f"   Séries: {data.get('series_recommandees')}")
        print(f"   Reps: {data.get('reps_recommandees')}")
        print(f"   Tempo: {data.get('tempo_recommande')}")
    else:
        print(f"   Erreur: {result.get('error')}")
    
    # Test par nom
    print("\n2. Test recommandation générique par nom...")
    result = get_generic_recommendation_by_name("Supine Press")
    print(f"   Succès: {result.get('success')}")
    if result.get('success'):
        data = result['data']
        print(f"   Machine: {data.get('machine_nom')}")
        print(f"   Poids: {data.get('poids_recommande')}kg")
        print(f"   Séries: {data.get('series_recommandees')}")
        print(f"   Reps: {data.get('reps_recommandees')}")
    else:
        print(f"   Erreur: {result.get('error')}")

if __name__ == "__main__":
    test_generic_recommendations()