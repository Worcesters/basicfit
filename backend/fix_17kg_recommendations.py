#!/usr/bin/env python
"""
Script pour corriger définitivement le problème des recommandations fixées à 17kg
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine

def fix_17kg_recommendations():
    print("CORRECTION DES RECOMMANDATIONS 17KG")
    print("=" * 40)
    
    # Récupérer toutes les progressions
    progressions = ProgressionMachine.objects.all()
    progressions_mises_a_jour = 0
    
    for progression in progressions:
        # Calculer la vraie recommandation
        recommandation_calculee = progression.calculer_recommandation_professionnelle()
        
        # Vérifier si elle est différente du poids actuel
        if abs(progression.poids_actuel - recommandation_calculee) > 0.1:
            ancien_poids = progression.poids_actuel
            
            # Mettre à jour
            progression.poids_actuel = recommandation_calculee
            progression.save()
            
            print(f"OK {progression.utilisateur.email} - {progression.machine.nom}")
            print(f"   {ancien_poids}kg -> {recommandation_calculee}kg")
            print(f"   1RM: {progression.dernier_1rm}kg, Seances: {progression.nombre_seances_machine}")
            
            progressions_mises_a_jour += 1
        else:
            print(f"DEJA A JOUR {progression.machine.nom}: ({progression.poids_actuel}kg)")
    
    print(f"\nRÉSULTAT:")
    print(f"  {progressions_mises_a_jour} progressions mises à jour")
    print(f"  {progressions.count() - progressions_mises_a_jour} déjà correctes")
    
    # Vérification finale
    print(f"\nVERIFICATION FINALE:")
    progressions_17kg = ProgressionMachine.objects.filter(poids_actuel=17.0)
    if progressions_17kg.exists():
        print(f"ATTENTION: {progressions_17kg.count()} progressions encore a 17kg:")
        for prog in progressions_17kg:
            print(f"   {prog.machine.nom}: {prog.dernier_1rm} 1RM, {prog.taux_reussite}% reussite")
    else:
        print("OK: Aucune progression a 17kg detectee!")
    
    return progressions_mises_a_jour

if __name__ == "__main__":
    fix_17kg_recommendations()