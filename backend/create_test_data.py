#!/usr/bin/env python
"""
Script pour créer des données de test
"""

import os
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User
from apps.machines.models import Machine, CategorieMachine, GroupeMusculaire
from apps.workouts.models import ProgressionMachine
from apps.core.models import ModeEntrainement

def create_test_data():
    """
    Crée des données de test pour tester les recommandations
    """
    print("🚀 Création des données de test...")

    # Créer les catégories
    categorie_muscu, _ = CategorieMachine.objects.get_or_create(
        nom='MUSCULATION',
        defaults={'description': 'Machines de musculation'}
    )

    # Créer les groupes musculaires
    pectoraux, _ = GroupeMusculaire.objects.get_or_create(
        nom='Pectoraux',
        defaults={'description': 'Muscles de la poitrine'}
    )

    dos, _ = GroupeMusculaire.objects.get_or_create(
        nom='Dos',
        defaults={'description': 'Muscles du dos'}
    )

    jambes, _ = GroupeMusculaire.objects.get_or_create(
        nom='Jambes',
        defaults={'description': 'Muscles des jambes'}
    )

    # Créer les modes d'entraînement
    mode_masse, _ = ModeEntrainement.objects.get_or_create(
        nom='PRISE_MASSE',
        defaults={
            'series_recommandees': 3,
            'repetitions_min': 8,
            'repetitions_max': 12,
            'repos_entre_series': 90
        }
    )

    # Créer des machines de test
    machines_data = [
        {
            'nom': 'Développé couché',
            'description': 'Machine pour travailler les pectoraux',
            'instructions': 'Allongez-vous sur le banc, saisissez la barre...',
            'categorie': categorie_muscu,
            'groupes_primaires': [pectoraux],
            'increment_poids': 2.5,
            'poids_minimum': 20.0,
            'poids_maximum': 200.0
        },
        {
            'nom': 'Traction à la barre',
            'description': 'Machine pour travailler le dos',
            'instructions': 'Suspendez-vous à la barre, tirez vers le haut...',
            'categorie': categorie_muscu,
            'groupes_primaires': [dos],
            'increment_poids': 2.5,
            'poids_minimum': 0.0,
            'poids_maximum': 100.0
        },
        {
            'nom': 'Squat',
            'description': 'Machine pour travailler les jambes',
            'instructions': 'Placez la barre sur vos épaules, fléchissez les genoux...',
            'categorie': categorie_muscu,
            'groupes_primaires': [jambes],
            'increment_poids': 5.0,
            'poids_minimum': 20.0,
            'poids_maximum': 300.0
        }
    ]

    machines_created = 0
    for machine_data in machines_data:
        machine, created = Machine.objects.get_or_create(
            nom=machine_data['nom'],
            defaults={
                'description': machine_data['description'],
                'instructions': machine_data['instructions'],
                'categorie': machine_data['categorie'],
                'increment_poids': machine_data['increment_poids'],
                'poids_minimum': machine_data['poids_minimum'],
                'poids_maximum': machine_data['poids_maximum']
            }
        )

        if created:
            # Ajouter les groupes musculaires
            for groupe in machine_data['groupes_primaires']:
                machine.groupes_musculaires_primaires.add(groupe)
            machines_created += 1
            print(f"✅ Machine créée: {machine.nom}")
        else:
            print(f"ℹ️ Machine existante: {machine.nom}")

    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            'nom': "Test",
            'prenom': "User",
            'objectif_sportif': "PRISE_MASSE",
            'date_naissance': date(1990, 1, 1)
        }
    )

    if created:
        print(f"✅ Utilisateur créé: {user.email}")
    else:
        print(f"ℹ️ Utilisateur existant: {user.email}")

    # Créer des progressions de test
    progressions_created = 0
    for machine in Machine.objects.all():
        progression, created = ProgressionMachine.objects.get_or_create(
            utilisateur=user,
            machine=machine,
            defaults={
                'mode_entrainement': mode_masse,
                'poids_actuel': 20.0,
                'taux_reussite': 85.0,
                'nombre_seances_machine': 5,
                'progression_poids_total': 10.0
            }
        )

        if created:
            progressions_created += 1
            print(f"✅ Progression créée pour {machine.nom}")
        else:
            print(f"ℹ️ Progression existante pour {machine.nom}")

    print(f"\n📊 Résumé:")
    print(f"   Machines créées: {machines_created}")
    print(f"   Progressions créées: {progressions_created}")
    print(f"   Total machines: {Machine.objects.count()}")
    print(f"   Total progressions: {ProgressionMachine.objects.count()}")

if __name__ == "__main__":
    create_test_data()
    print("\n✅ Données de test créées avec succès!")