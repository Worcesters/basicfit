#!/usr/bin/env python3
"""
Script pour corriger les taux de réussite à 0% dans les progressions
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine, ExerciceSeance, SeriExercice
from django.utils import timezone
from datetime import timedelta

def fix_taux_reussite():
    print("=== CORRECTION DES TAUX DE RÉUSSITE ===")
    
    # Récupérer toutes les progressions avec taux de réussite à 0%
    progressions_zero = ProgressionMachine.objects.filter(taux_reussite=0.0)
    
    print(f"Trouvé {progressions_zero.count()} progressions avec taux de réussite à 0%")
    
    for progression in progressions_zero:
        print(f"\n[CORRECTION] {progression.utilisateur.email} - {progression.machine.nom}")
        print(f"   Ancien taux: {progression.taux_reussite}%")
        print(f"   Seances: {progression.nombre_seances_machine}")
        print(f"   Poids actuel: {progression.poids_actuel}kg")
        
        # Calculer le taux de réussite basé sur les séances récentes
        recent_exercises = ExerciceSeance.objects.filter(
            seance__utilisateur=progression.utilisateur,
            machine=progression.machine,
            seance__statut='TERMINEE',
            seance__date_debut__gte=timezone.now() - timedelta(days=60)
        ).order_by('-seance__date_debut')[:10]  # 10 dernières séances max
        
        if recent_exercises.exists():
            total_series = 0
            series_reussies = 0
            
            for exercise in recent_exercises:
                series = exercise.series.all()
                for serie in series:
                    total_series += 1
                    # Considérer une série réussie si elle atteint 80% des reps prévues
                    if serie.repetitions_realisees >= serie.repetitions_prevues * 0.8:
                        series_reussies += 1
            
            if total_series > 0:
                nouveau_taux = (series_reussies / total_series) * 100
                progression.taux_reussite = nouveau_taux
                progression.save()
                print(f"   [OK] Nouveau taux calcule: {nouveau_taux:.1f}% ({series_reussies}/{total_series} series reussies)")
            else:
                # Si pas de séries détaillées, utiliser un taux optimiste
                progression.taux_reussite = 75.0
                progression.save()
                print(f"   [OK] Taux par defaut applique: 75.0% (pas de donnees de series)")
        else:
            # Si aucune séance récente, utiliser un taux modéré
            progression.taux_reussite = 70.0
            progression.save()
            print(f"   [OK] Taux par defaut applique: 70.0% (pas de seances recentes)")
    
    print(f"\n[TERMINE] Correction terminee pour {progressions_zero.count()} progressions")

def test_progression_supine_press():
    print("\n=== TEST PROGRESSION SUPINE PRESS ===")
    
    try:
        from apps.users.models import User
        user = User.objects.get(email='jeremy.didier77@gmail.com')
        
        progression = ProgressionMachine.objects.get(
            utilisateur=user,
            machine__nom='Supine Press'
        )
        
        print(f"Utilisateur: {user.email}")
        print(f"Machine: {progression.machine.nom}")
        print(f"Poids actuel: {progression.poids_actuel}kg")
        print(f"Dernier 1RM: {progression.dernier_1rm}kg")
        print(f"Taux réussite: {progression.taux_reussite}%")
        print(f"Nombre séances: {progression.nombre_seances_machine}")
        
        # Tester la recommandation
        nouvelle_recommandation = progression.calculer_recommandation_professionnelle()
        print(f"Nouvelle recommandation: {nouvelle_recommandation}kg")
        
        # Si le taux est maintenant bon (≥75%), il devrait y avoir progression
        if progression.taux_reussite >= 75 and progression.poids_actuel < nouvelle_recommandation:
            print("[SUCCESS] Le systeme devrait maintenant progresser !")
        else:
            print("[INFO] Peut necessiter plus de seances pour progresser")
            
    except Exception as e:
        print(f"[ERROR] Erreur test: {e}")

if __name__ == "__main__":
    fix_taux_reussite()
    test_progression_supine_press()