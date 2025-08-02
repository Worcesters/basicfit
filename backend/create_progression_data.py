#!/usr/bin/env python3
"""
Créer des données de progression pour tester les recommandations 60kg
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.machines.models import Machine
from apps.workouts.models import ProgressionMachine, ModeEntrainement

User = get_user_model()

def create_progression_data():
    """Créer des données de progression pour l'utilisateur"""
    print("=== CREATION DES DONNEES DE PROGRESSION ===")
    
    try:
        # 1. Récupérer l'utilisateur
        user = User.objects.first()
        if not user:
            print("ERREUR: Aucun utilisateur trouvé")
            return False
            
        print(f"Utilisateur: {user.email}")
        
        # 2. Récupérer la machine Développé Couché
        machine = Machine.objects.get(id=1)
        print(f"Machine: {machine.nom}")
        
        # 3. Créer/récupérer le mode Force
        mode_force, created = ModeEntrainement.objects.get_or_create(
            nom="Force",
            defaults={'description': 'Entraînement de force générale'}
        )
        if created:
            print("Mode Force créé")
        else:
            print("Mode Force existant")
        
        # 4. Créer/mettre à jour la progression avec 55kg (pour qu'elle passe à 60kg)
        progression, created = ProgressionMachine.objects.get_or_create(
            utilisateur=user,
            machine=machine,
            mode_entrainement=mode_force,
            defaults={
                'poids_actuel': 55.0,  # 55kg pour que la recommandation passe à 60kg
                'repetitions_actuelles': 10,
                'series_actuelles': 3,
                'dernier_1rm': 75.0,
                'nombre_seances_machine': 5,
                'taux_reussite': 0.85,  # 85% de réussite pour déclencher une progression
                'progression_poids_total': 15.0,  # Progression de 15kg depuis le début
                'increment_automatique': True,
            }
        )
        
        if created:
            print(f"Progression créée: {progression.poids_actuel}kg")
        else:
            # Mettre à jour la progression existante
            progression.poids_actuel = 55.0
            progression.repetitions_actuelles = 10
            progression.series_actuelles = 3
            progression.taux_reussite = 0.85
            progression.nombre_seances_machine = 5
            progression.dernier_1rm = 75.0
            progression.save()
            print(f"Progression mise à jour: {progression.poids_actuel}kg")
        
        print("=== DONNEES CREEES ===")
        print(f"Poids actuel: {progression.poids_actuel}kg")
        print(f"Taux réussite: {progression.taux_reussite * 100}%")
        print(f"Avec un taux de {progression.taux_reussite * 100}% (>= 80%), le système devrait recommander une progression")
        print(f"Progression attendue: 55kg + 2.5kg = 57.5kg (ou 55kg + 5% = 57.75kg)")
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_progression_data()
    if success:
        print("\nSUCCES: Données de progression créées")
    else:
        print("\nECHEC: Erreur lors de la création")
        sys.exit(1)