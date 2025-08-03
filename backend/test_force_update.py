#!/usr/bin/env python
"""
Test direct de la fonction force_progression_update
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.workouts.workout_service import WorkoutSaveService

def test_force_progression_update():
    """Test de la mise à jour forcée des progressions"""
    User = get_user_model()
    user = User.objects.first()
    
    if not user:
        print("Aucun utilisateur trouvé")
        return
    
    print(f"Test pour utilisateur: {user.email}")
    
    # Récupérer les séances terminées récentes
    recent_sessions = SeanceEntrainement.objects.filter(
        utilisateur=user,
        statut='TERMINEE',
        date_debut__gte=timezone.now() - timedelta(days=7)
    ).prefetch_related('exercices__series')
    
    print(f"Séances récentes trouvées: {recent_sessions.count()}")
    
    updated_count = 0
    save_service = WorkoutSaveService()
    
    for session in recent_sessions:
        print(f"\nTraitement séance: {session.nom}")
        
        # Convertir les exercices au format attendu
        exercises = []
        for exercice in session.exercices.all():
            print(f"  Exercice: {exercice.machine.nom}")
            
            if exercice.series.exists():
                # Prendre les valeurs de la dernière série
                last_serie = exercice.series.last()
                print(f"    Dernière série: {last_serie.poids_utilise}kg x {last_serie.repetitions_realisees}")
                
                exercises.append({
                    'nom': exercice.machine.nom,
                    'series': exercice.nombre_series,
                    'reps': last_serie.repetitions_realisees,
                    'poids': last_serie.poids_utilise
                })
            else:
                print(f"    Aucune série trouvée")
        
        if exercises:
            try:
                print(f"    Mise à jour progressions...")
                save_service._update_machine_progressions(user, exercises)
                updated_count += 1
                print(f"    Progressions mises à jour")
            except Exception as e:
                print(f"    Erreur: {e}")
        else:
            print(f"    Pas d'exercices à traiter")
    
    print(f"\nRÉSULTAT: {updated_count} séances traitées")
    return {
        'success': True,
        'updated_sessions': updated_count,
        'message': f'Progressions mises à jour pour {updated_count} séances'
    }

if __name__ == "__main__":
    try:
        result = test_force_progression_update()
        print(f"\nSUCCESS: {result}")
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()