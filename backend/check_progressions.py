#!/usr/bin/env python3
"""
Vérifier les progressions en base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.workouts.models import ProgressionMachine, Machine, ModeEntrainement

User = get_user_model()

def check_progressions():
    """Vérifier les progressions en base"""
    print("=== VERIFICATION DES PROGRESSIONS ===")
    
    # Lister tous les utilisateurs
    users = User.objects.all()
    print(f"Nombre d'utilisateurs: {users.count()}")
    
    for user in users:
        print(f"\nUtilisateur: {user.email} (ID: {user.id})")
        
        # Vérifier ses progressions
        progressions = ProgressionMachine.objects.filter(utilisateur=user)
        print(f"  Nombre de progressions: {progressions.count()}")
        
        for prog in progressions:
            print(f"  - {prog.machine.nom}: {prog.poids_actuel}kg x {prog.repetitions_actuelles} (mode: {prog.mode_entrainement.nom})")
    
    # Vérifier spécifiquement Supine Press
    print(f"\n=== SUPINE PRESS PROGRESSIONS ===")
    try:
        supine_machine = Machine.objects.get(nom__icontains="Supine Press")
        print(f"Machine Supine Press trouvée: ID {supine_machine.id}")
        
        supine_progressions = ProgressionMachine.objects.filter(machine=supine_machine)
        print(f"Progressions Supine Press: {supine_progressions.count()}")
        
        for prog in supine_progressions:
            print(f"  {prog.utilisateur.email}: {prog.poids_actuel}kg x {prog.repetitions_actuelles}")
            
    except Machine.DoesNotExist:
        print("Machine Supine Press non trouvée")
    
    # Créer des données de test si nécessaire
    print(f"\n=== CREATION DONNEES TEST ===")
    test_user = users.filter(email="test@railway.com").first()
    if test_user:
        try:
            supine_machine = Machine.objects.get(nom__icontains="Supine Press")
            mode_force, _ = ModeEntrainement.objects.get_or_create(
                nom="Force",
                defaults={'description': 'Entraînement de force générale'}
            )
            
            # Créer une progression de 60kg pour test
            progression, created = ProgressionMachine.objects.get_or_create(
                utilisateur=test_user,
                machine=supine_machine,
                mode_entrainement=mode_force,
                defaults={
                    'poids_actuel': 60.0,
                    'repetitions_actuelles': 8,
                    'series_actuelles': 3,
                    'niveau_maitrise': 85,
                    'historique_charges': '[55.0, 57.5, 60.0]',
                    'historique_performances': '[10, 9, 8]'
                }
            )
            
            if created:
                print(f"  ✅ Progression Supine Press créée: 60kg x 8")
            else:
                # Mettre à jour si elle existe
                progression.poids_actuel = 60.0
                progression.repetitions_actuelles = 8
                progression.niveau_maitrise = 85
                progression.save()
                print(f"  ⬆️  Progression Supine Press mise à jour: 60kg x 8")
                
        except Machine.DoesNotExist:
            print("  ❌ Machine Supine Press non trouvée pour créer progression")
    
    print("\n=== VERIFICATION FINALE ===")
    # Re-vérifier après création
    if test_user:
        progressions = ProgressionMachine.objects.filter(utilisateur=test_user)
        for prog in progressions:
            print(f"  {prog.machine.nom}: {prog.poids_actuel}kg")

if __name__ == '__main__':
    check_progressions()