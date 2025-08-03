#!/usr/bin/env python3
"""
Test des recommandations authentifiées après correction des taux de réussite
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.simple_recommendation import get_simple_recommendation_by_name
from apps.users.models import User
from apps.workouts.models import ProgressionMachine

def test_authenticated_recommendation():
    print("=== TEST RECOMMANDATION AUTHENTIFIEE ===")
    
    try:
        # Utiliser le compte test qui existe
        user = User.objects.get(email='test@example.com')
        print(f"Utilisateur trouve: {user.email}")
        
        # Tester la recommandation pour Supine Press
        result = get_simple_recommendation_by_name(user, "Supine Press")
        
        print(f"\nResultat API:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            data = result['data']
            print(f"  Machine: {data.get('machine_nom')}")
            print(f"  Poids recommande: {data.get('poids_recommande')}kg")
            print(f"  Source: {data.get('source')}")
            print(f"  Taux reussite: {data.get('taux_reussite')}%")
            print(f"  Nombre seances: {data.get('nombre_seances')}")
            print(f"  Dernier 1RM: {data.get('dernier_1rm')}")
            
            # Vérifier si c'est basé sur la progression BDD
            if data.get('source') in ['progression_utilisateur', 'recommandation_personnalisee']:
                print("  [SUCCESS] Utilise la progression de la BDD !")
            else:
                print("  [INFO] Utilise une recommandation generique")
        else:
            print(f"  Erreur: {result.get('error')}")
            
        # Vérifier la progression en BDD
        print(f"\n=== VERIFICATION PROGRESSION BDD ===")
        progression = ProgressionMachine.objects.get(
            utilisateur=user,
            machine__nom='Supine Press'
        )
        
        print(f"Progression BDD:")
        print(f"  Poids actuel: {progression.poids_actuel}kg")
        print(f"  Taux reussite: {progression.taux_reussite}%")
        print(f"  Nombre seances: {progression.nombre_seances_machine}")
        print(f"  Dernier 1RM: {progression.dernier_1rm}kg")
        
        # Test de la recommandation professionnelle
        nouvelle_recommandation = progression.calculer_recommandation_professionnelle()
        print(f"  Recommandation calculee: {nouvelle_recommandation}kg")
        
        if progression.taux_reussite >= 75:
            print("  [SUCCESS] Taux de reussite OK pour progression")
        else:
            print("  [WARNING] Taux de reussite trop bas")
            
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    test_authenticated_recommendation()