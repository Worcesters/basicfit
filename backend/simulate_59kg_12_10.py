#!/usr/bin/env python
"""
Script pour simuler le scénario : 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)
"""

import os
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.users.models import User
from apps.machines.models import Machine, CategorieMachine, GroupeMusculaire
from apps.workouts.models import ProgressionMachine, SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.core.models import ModeEntrainement
from django.utils import timezone

def simulate_59kg_workout():
    """
    Simule une séance avec 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)
    """
    print("🏋️ Simulation : 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)")
    print("=" * 70)

    # Récupérer ou créer l'utilisateur de test
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            'nom': "Test",
            'prenom': "User",
            'objectif_sportif': "PRISE_MASSE",
            'date_naissance': date(1990, 1, 1)
        }
    )

    # Récupérer ou créer une machine (Développé couché)
    machine, created = Machine.objects.get_or_create(
        nom="Développé couché",
        defaults={
            'description': 'Machine pour travailler les pectoraux',
            'instructions': 'Allongez-vous sur le banc, saisissez la barre...',
            'increment_poids': 2.5,
            'poids_minimum': 20.0,
            'poids_maximum': 200.0
        }
    )

    # Récupérer ou créer le mode d'entraînement
    mode, created = ModeEntrainement.objects.get_or_create(
        nom='PRISE_MASSE',
        defaults={
            'series_recommandees': 3,
            'repetitions_min': 8,
            'repetitions_max': 12,
            'repos_entre_series': 90
        }
    )

    print(f"👤 Utilisateur: {user.nom_complet}")
    print(f"🏋️ Machine: {machine.nom}")
    print(f"📊 Mode d'entraînement: {mode.nom}")

    # Créer une séance d'entraînement
    seance = SeanceEntrainement.objects.create(
        utilisateur=user,
        mode_entrainement=mode,
        nom="Séance test - 59kg",
        date_prevue=timezone.now(),
        statut='TERMINEE',
        date_debut=timezone.now(),
        date_fin=timezone.now()
    )

    # Créer l'exercice avec les données spécifiées
    exercice = ExerciceSeance.objects.create(
        seance=seance,
        machine=machine,
        ordre_dans_seance=1,
        series_prevues=3,
        repetitions_prevues=12,  # Objectif initial
        poids_prevu=59.0,
        nombre_series=3,
        repetitions_realisees=34,  # 12 + 12 + 10 = 34 reps total
        poids_utilise=59.0,
        statut='TERMINE'
    )

    # Créer les 3 séries spécifiques
    series_data = [
        {'reps_prevues': 12, 'reps_realisees': 12, 'statut': 'REUSSIE'},
        {'reps_prevues': 12, 'reps_realisees': 12, 'statut': 'REUSSIE'},
        {'reps_prevues': 12, 'reps_realisees': 10, 'statut': 'ECHOUEE'}  # Échec sur la 3ème série
    ]

    for i, serie_data in enumerate(series_data):
        SeriExercice.objects.create(
            exercice=exercice,
            numero_serie=i + 1,
            repetitions_prevues=serie_data['reps_prevues'],
            poids_prevu=59.0,
            repetitions_realisees=serie_data['reps_realisees'],
            poids_utilise=59.0,
            statut=serie_data['statut']
        )

    print(f"\n📊 Détails de la séance:")
    print(f"   Série 1: 59kg × 12 reps ✅ (Réussie)")
    print(f"   Série 2: 59kg × 12 reps ✅ (Réussie)")
    print(f"   Série 3: 59kg × 10 reps ❌ (Échec - 2 reps manquantes)")
    print(f"   Total: 34 reps sur 36 prévues = {34/36*100:.1f}% de réussite")

    # Récupérer ou créer la progression
    progression, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        defaults={
            'mode_entrainement': mode,
            'poids_actuel': 59.0,
            'series_actuelles': 3,
            'repetitions_actuelles': 12,
            'derniere_seance': seance,
            'dernier_1rm': exercice.calculer_1rm_brzycki(),
            'nombre_seances_machine': 1,
            'progression_poids_total': 59.0,
            'taux_reussite': 66.7,  # 2 séries réussies sur 3
            'increment_automatique': True,
            'seuil_progression': 90.0
        }
    )

    if not created:
        # Mettre à jour la progression existante
        progression.poids_actuel = 59.0
        progression.derniere_seance = seance
        progression.dernier_1rm = exercice.calculer_1rm_brzycki()
        progression.nombre_seances_machine += 1

        # Calculer le taux de réussite de cette séance
        series_reussies = 2  # 2 séries réussies sur 3
        taux_reussite_seance = (series_reussies / 3) * 100
        progression.taux_reussite = taux_reussite_seance
        progression.save()

    print(f"\n📈 Analyse de la progression:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")
    print(f"   Nombre de séances: {progression.nombre_seances_machine}")
    print(f"   1RM estimé: {progression.dernier_1rm:.1f}kg")

    # Tester les différentes méthodes d'évaluation
    print(f"\n🔍 Évaluation de la progression:")
    print(f"   Peut progresser (historique): {progression.evaluer_progression_historique()}")
    print(f"   Détecte stagnation: {progression.detecter_stagnation()}")
    print(f"   Recommandation intelligente: {progression.calculer_recommandation_intelligente()}kg")

    # Tester avec l'exercice de la séance
    peut_progresser_avec_seance = progression.evaluer_progression(exercice)
    print(f"   Peut progresser (avec séance): {peut_progresser_avec_seance}")

    # Calculer la recommandation pour la prochaine séance
    recommandation = progression.calculer_recommandation_intelligente()

    print(f"\n🎯 Recommandation pour la prochaine séance:")
    if recommandation > 59.0:
        print(f"   ✅ PROGRESSION RECOMMANDÉE: {recommandation}kg")
        print(f"   📈 Augmentation: +{recommandation - 59.0}kg")
    else:
        print(f"   ⏸️ MAINTIEN: {recommandation}kg")
        print(f"   💡 Raison: Taux de réussite insuffisant ({progression.taux_reussite}% < {progression.seuil_progression}%)")

    # Analyser pourquoi
    print(f"\n🔍 Analyse détaillée:")
    print(f"   Seuil de progression: {progression.seuil_progression}%")
    print(f"   Taux de réussite actuel: {progression.taux_reussite}%")
    print(f"   Différence: {progression.taux_reussite - progression.seuil_progression}%")

    if progression.taux_reussite < progression.seuil_progression:
        print(f"   ❌ Pas de progression car le taux de réussite ({progression.taux_reussite}%)")
        print(f"      est inférieur au seuil requis ({progression.seuil_progression}%)")
    else:
        print(f"   ✅ Progression possible car le taux de réussite est suffisant")

    return progression

if __name__ == "__main__":
    progression = simulate_59kg_workout()
    print(f"\n✅ Simulation terminée!")