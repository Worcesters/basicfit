#!/usr/bin/env python3
"""
Test direct des insertions BDD avec logs détaillés
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User
from apps.workouts.models_simple import SeanceSimple
from apps.workouts.views_refactored import save_workout_professional
from apps.workouts.workout_service import WorkoutSaveService
import logging

def test_direct_insertions():
    print("=" * 60)
    print("TEST DIRECT INSERTIONS BDD AVEC LOGS")
    print("=" * 60)
    
    # Setup logging pour voir nos logs
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Récupérer l'utilisateur de test
    try:
        user = User.objects.get(email='test@example.com')
        print(f"[USER] Utilisateur trouvé: {user.email} (ID: {user.id})")
    except User.DoesNotExist:
        print("[ERROR] Utilisateur test non trouvé")
        return False
    
    # Test 1: Import CSV direct via SeanceSimple
    print("\n[TEST1] Import CSV direct via SeanceSimple...")
    csv_data = [
        {'machine': 'Tapis de course', 'date': '2025-01-17', 'type': 'CARDIO'},
        {'machine': 'Développé couché', 'date': '2025-01-17', 'type': 'MUSCULATION'},
        {'machine': 'Squat', 'date': '2025-01-17', 'type': 'FORCE'},
    ]
    
    try:
        # Compter avant
        count_before = SeanceSimple.objects.filter(utilisateur=user).count()
        print(f"[COUNT] SeanceSimple avant: {count_before}")
        
        # Import
        imported_count, errors = SeanceSimple.import_from_csv_data(user, csv_data)
        
        # Compter après
        count_after = SeanceSimple.objects.filter(utilisateur=user).count()
        print(f"[COUNT] SeanceSimple après: {count_after}")
        print(f"[RESULT] Importées: {imported_count}, Erreurs: {len(errors)}")
        
        if errors:
            print(f"[ERRORS] {errors}")
            
    except Exception as e:
        print(f"[ERROR] Import CSV failed: {e}")
    
    # Test 2: Sauvegarde workout via WorkoutSaveService
    print("\n[TEST2] Sauvegarde workout via WorkoutSaveService...")
    workout_data = {
        "nom": "Test Direct Workout",
        "date": "2025-01-17T15:00:00Z",
        "duree": 60,
        "note_ressenti": 9,
        "commentaire": "Test insertion directe",
        "exercices": [
            {
                "nom": "Développé couché",
                "series": 4,
                "reps": 8,
                "poids": 85.0
            },
            {
                "nom": "Squat",
                "series": 4,
                "reps": 10,
                "poids": 120.0
            }
        ]
    }
    
    try:
        from apps.workouts.models import SeanceEntrainement
        
        # Compter avant
        count_before = SeanceEntrainement.objects.filter(utilisateur=user).count()
        print(f"[COUNT] SeanceEntrainement avant: {count_before}")
        
        # Sauvegarde
        save_service = WorkoutSaveService()
        session, created, message = save_service.save_workout(user, workout_data)
        
        # Compter après
        count_after = SeanceEntrainement.objects.filter(utilisateur=user).count()
        print(f"[COUNT] SeanceEntrainement après: {count_after}")
        print(f"[RESULT] Créé: {created}, Message: {message}")
        
        if session:
            print(f"[SESSION] ID: {session.id}, Nom: {session.nom}")
            print(f"[EXERCISES] Nombre d'exercices: {session.exercices.count()}")
            
    except Exception as e:
        print(f"[ERROR] Workout save failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST DIRECT TERMINÉ")
    print("Vérifiez maintenant les logs sur Fly.io avec: fly logs -a basicfit-v2")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = test_direct_insertions()
    exit(0 if success else 1)