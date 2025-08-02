#!/usr/bin/env python3
"""
Créer des séances récentes pour simuler une progression réussie
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.machines.models import Machine
from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice, ModeEntrainement

User = get_user_model()

def create_recent_workouts():
    """Créer des séances récentes avec progression réussie"""
    print("=== CREATION DE SEANCES RECENTES ===")
    
    try:
        # 1. Récupérer l'utilisateur et la machine
        user = User.objects.first()
        machine = Machine.objects.get(id=1)
        mode_force = ModeEntrainement.objects.get(nom="Force")
        
        print(f"Utilisateur: {user.email}")
        print(f"Machine: {machine.nom}")
        
        # 2. Créer 3 séances récentes avec progression
        base_date = timezone.now() - timedelta(days=10)
        
        workouts_data = [
            {'date': base_date, 'poids': 50.0, 'reps': 10},  # Il y a 10 jours
            {'date': base_date + timedelta(days=3), 'poids': 52.5, 'reps': 10},  # Il y a 7 jours
            {'date': base_date + timedelta(days=6), 'poids': 55.0, 'reps': 10},  # Il y a 4 jours
        ]
        
        created_count = 0
        
        for i, workout_data in enumerate(workouts_data):
            # Créer la séance
            seance = SeanceEntrainement.objects.create(
                utilisateur=user,
                mode_entrainement=mode_force,
                nom=f"Développé Couché #{i+1}",
                date_prevue=workout_data['date'],
                date_debut=workout_data['date'],
                date_fin=workout_data['date'] + timedelta(minutes=45),
                statut='TERMINEE',
                note_ressenti=8,
                note_difficulte=7
            )
            
            # Créer l'exercice
            exercice = ExerciceSeance.objects.create(
                seance=seance,
                machine=machine,
                ordre_dans_seance=1,
                series_prevues=3,
                repetitions_prevues=workout_data['reps'],
                poids_prevu=workout_data['poids'],
                repos_prevu=90,
                nombre_series=3,
                repetitions_realisees=workout_data['reps'] * 3,  # 3 séries
                poids_utilise=workout_data['poids'],
                statut='TERMINE'
            )
            
            # Créer les séries
            for j in range(3):
                SeriExercice.objects.create(
                    exercice=exercice,
                    numero_serie=j+1,
                    poids_prevu=workout_data['poids'],
                    poids_utilise=workout_data['poids'],
                    repetitions_prevues=workout_data['reps'],
                    repetitions_realisees=workout_data['reps'],
                    repos_prevu=90,
                    statut='TERMINE'
                )
            
            created_count += 1
            print(f"Séance créée: {workout_data['date'].strftime('%d/%m')} - {workout_data['poids']}kg x {workout_data['reps']}")
        
        print(f"\n{created_count} séances créées avec progression:")
        print("50kg → 52.5kg → 55kg")
        print("Cette progression constante devrait donner un taux de réussite élevé")
        print("Le système devrait maintenant recommander 57.5kg ou plus")
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_recent_workouts()
    if success:
        print("\nSUCCES: Séances récentes créées")
    else:
        print("\nECHEC: Erreur lors de la création")
        sys.exit(1)