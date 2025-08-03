#!/usr/bin/env python
"""
Créer des données de progression pour jeremy.didier77@gmail.com
"""
import os
import django
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.workouts.models import ProgressionMachine, ModeEntrainement, SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.machines.models import Machine
# from apps.users.models import ProfilFitness  # Pas besoin, champs dans User

User = get_user_model()

def create_jeremy_data():
    """Créer des données de progression pour Jeremy"""
    print("=== CREATION DONNEES JEREMY ===")
    
    # 1. Créer/récupérer l'utilisateur
    user, created = User.objects.get_or_create(
        email='jeremy.didier77@gmail.com',
        defaults={
            'username': 'jeremy.didier77@gmail.com',
            'first_name': 'Jeremy',
            'last_name': 'Didier'
        }
    )
    
    if created:
        user.set_password('jeremyd77')
        user.save()
        print(f"[OK] Utilisateur créé: {user.email}")
    else:
        print(f"[OK] Utilisateur existant: {user.email}")
    
    # 2. Mettre à jour le profil utilisateur
    user.poids = 75.0
    user.taille = 180.0
    user.niveau_experience = 'INTERMEDIAIRE'
    user.objectif_sportif = 'PRISE_MASSE'
    user.save()
    print(f"[OK] Profil utilisateur mis à jour")
    
    # 3. Récupérer les machines
    try:
        chest_press = Machine.objects.get(nom='Chest Press')
        print(f"[OK] Machine trouvée: {chest_press.nom}")
    except Machine.DoesNotExist:
        print("[ERROR] Machine Chest Press non trouvée")
        return
    
    try:
        supine_press = Machine.objects.get(nom__icontains='Supine')
        print(f"[OK] Machine trouvée: {supine_press.nom}")
    except Machine.DoesNotExist:
        supine_press = None
        print("[WARNING] Machine Supine Press non trouvée")
    
    # 4. Créer le mode d'entraînement
    mode_force, _ = ModeEntrainement.objects.get_or_create(
        nom="Force",
        defaults={'description': 'Entraînement de force générale'}
    )
    
    # 5. Créer des progressions
    print("\n=== CREATION PROGRESSIONS ===")
    
    # Progression Chest Press (59kg comme mentionné)
    progression_chest, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=chest_press,
        mode_entrainement=mode_force,
        defaults={
            'poids_actuel': Decimal('59.0'),
            'repetitions_actuelles': 10,
            'series_actuelles': 3,
            'dernier_1rm': Decimal('79.0'),
            'nombre_seances_machine': 5,
            'taux_reussite': Decimal('0.85'),
            'derniere_mise_a_jour': timezone.now()
        }
    )
    print(f"[OK] Progression Chest Press: {progression_chest.poids_actuel}kg")
    
    # Progression Supine Press si trouvée
    if supine_press:
        progression_supine, created = ProgressionMachine.objects.get_or_create(
            utilisateur=user,
            machine=supine_press,
            mode_entrainement=mode_force,
            defaults={
                'poids_actuel': Decimal('59.0'),
                'repetitions_actuelles': 12,
                'series_actuelles': 3,
                'dernier_1rm': Decimal('86.0'),
                'nombre_seances_machine': 3,
                'taux_reussite': Decimal('0.90'),
                'derniere_mise_a_jour': timezone.now()
            }
        )
        print(f"[OK] Progression Supine Press: {progression_supine.poids_actuel}kg")
    
    # 6. Créer des séances récentes
    print("\n=== CREATION SEANCES ===")
    
    # Séance d'il y a 3 jours
    date_seance1 = timezone.now() - timedelta(days=3)
    seance1, created = SeanceEntrainement.objects.get_or_create(
        utilisateur=user,
        date_debut=date_seance1,
        defaults={
            'statut': 'TERMINEE',
            'duree_totale': timedelta(minutes=45),
            'notes': 'Séance test - Chest Press'
        }
    )
    
    if created:
        # ExerciceSeance pour Chest Press
        exercice1 = ExerciceSeance.objects.create(
            seance=seance1,
            machine=chest_press,
            ordre=1,
            nombre_series=3,
            temps_repos_prevu=90
        )
        
        # Séries
        for i in range(3):
            SeriExercice.objects.create(
                exercice_seance=exercice1,
                numero_serie=i+1,
                poids_utilise=Decimal('57.0'),
                repetitions_realisees=10,
                temps_repos_reel=90
            )
        print(f"[OK] Séance 1 créée: {seance1.date_debut.date()}")
    
    # Séance d'il y a 1 jour
    date_seance2 = timezone.now() - timedelta(days=1)
    seance2, created = SeanceEntrainement.objects.get_or_create(
        utilisateur=user,
        date_debut=date_seance2,
        defaults={
            'statut': 'TERMINEE',
            'duree_totale': timedelta(minutes=50),
            'notes': 'Séance test - Progression'
        }
    )
    
    if created:
        # ExerciceSeance pour Chest Press
        exercice2 = ExerciceSeance.objects.create(
            seance=seance2,
            machine=chest_press,
            ordre=1,
            nombre_series=3,
            temps_repos_prevu=90
        )
        
        # Séries avec progression
        for i in range(3):
            SeriExercice.objects.create(
                exercice_seance=exercice2,
                numero_serie=i+1,
                poids_utilise=Decimal('59.0'),
                repetitions_realisees=10 if i < 2 else 8,  # Dernière série plus difficile
                temps_repos_reel=90
            )
        print(f"[OK] Séance 2 créée: {seance2.date_debut.date()}")
    
    print(f"\n=== RESUME ===")
    print(f"Utilisateur: {user.email}")
    print(f"Progressions: {ProgressionMachine.objects.filter(utilisateur=user).count()}")
    print(f"Séances: {SeanceEntrainement.objects.filter(utilisateur=user).count()}")
    print(f"Exercices: {ExerciceSeance.objects.filter(seance__utilisateur=user).count()}")
    print(f"Séries: {SeriExercice.objects.filter(exercice_seance__seance__utilisateur=user).count()}")

if __name__ == "__main__":
    create_jeremy_data()