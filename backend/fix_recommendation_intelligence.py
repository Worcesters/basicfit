#!/usr/bin/env python
"""
Script pour diagnostiquer et corriger les problèmes de recommandation intelligente
"""

import os
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine, SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.machines.models import Machine
from apps.users.models import User
from apps.core.models import ModeEntrainement
from django.utils import timezone

def diagnostiquer_problemes_recommandation():
    """
    Diagnostique les problèmes avec la recommandation intelligente
    """
    print("🔍 Diagnostic des problèmes de recommandation intelligente...")

    # Récupérer toutes les progressions
    progressions = ProgressionMachine.objects.all()

    print(f"📊 Total progressions: {progressions.count()}")

    for progression in progressions:
        print(f"\n--- Progression: {progression.utilisateur.nom_complet} - {progression.machine.nom} ---")
        print(f"Poids actuel: {progression.poids_actuel}kg")
        print(f"Taux de réussite: {progression.taux_reussite}%")
        print(f"Nombre de séances: {progression.nombre_seances_machine}")
        print(f"Seuil de progression: {progression.seuil_progression}%")

        # Analyser les dernières séances
        derniere_seance = progression.derniere_seance
        if derniere_seance:
            print(f"Dernière séance: {derniere_seance.nom} ({derniere_seance.date_debut})")

            # Analyser les exercices de la dernière séance
            exercices = derniere_seance.exercices.filter(machine=progression.machine)
            if exercices.exists():
                exercice = exercices.first()
                print(f"Exercice trouvé: {exercice.poids_utilise}kg × {exercice.repetitions_realisees} reps")

                # Analyser les séries
                series = exercice.series.all()
                series_reussies = sum(1 for serie in series if serie.est_reussie)
                taux_reel = (series_reussies / len(series)) * 100 if series else 0
                print(f"Séries réussies: {series_reussies}/{len(series)} = {taux_reel:.1f}%")

                # Comparer avec le taux stocké
                print(f"Taux stocké vs réel: {progression.taux_reussite}% vs {taux_reel:.1f}%")

        # Tester la recommandation intelligente
        recommandation = progression.calculer_recommandation_intelligente()
        print(f"Recommandation intelligente: {recommandation}kg")

        # Analyser pourquoi ça ne fonctionne pas
        peut_progresser = progression.evaluer_progression_historique()
        stagnation = progression.detecter_stagnation()
        print(f"Peut progresser (historique): {peut_progresser}")
        print(f"Détecte stagnation: {stagnation}")

def corriger_taux_reussite():
    """
    Corrige le taux de réussite basé sur les dernières séances
    """
    print("\n🔧 Correction du taux de réussite...")

    progressions = ProgressionMachine.objects.all()
    corrigees = 0

    for progression in progressions:
        # Récupérer les 5 dernières séances pour cette machine
        derniere_seance = progression.derniere_seance
        if not derniere_seance:
            continue

        # Calculer le taux de réussite basé sur les dernières séances
        exercices_recents = ExerciceSeance.objects.filter(
            seance__utilisateur=progression.utilisateur,
            machine=progression.machine,
            seance__date_debut__gte=derniere_seance.date_debut - timedelta(days=30)
        ).order_by('-seance__date_debut')[:5]

        if exercices_recents.exists():
            total_series = 0
            series_reussies = 0

            for exercice in exercices_recents:
                series = exercice.series.all()
                total_series += len(series)
                series_reussies += sum(1 for serie in series if serie.est_reussie)

            if total_series > 0:
                nouveau_taux = (series_reussies / total_series) * 100
                ancien_taux = progression.taux_reussite

                if abs(nouveau_taux - ancien_taux) > 5:  # Seuil de différence significative
                    progression.taux_reussite = nouveau_taux
                    progression.save()
                    print(f"✅ Corrigé {progression.machine.nom}: {ancien_taux}% → {nouveau_taux:.1f}%")
                    corrigees += 1
                else:
                    print(f"ℹ️ {progression.machine.nom}: Taux OK ({ancien_taux}%)")

    print(f"\n📈 {corrigees} progressions corrigées")

def ameliorer_recommandation_intelligente():
    """
    Améliore la logique de recommandation intelligente
    """
    print("\n🚀 Amélioration de la recommandation intelligente...")

    # Modifier la méthode calculer_recommandation_intelligente pour être plus intelligente
    progressions = ProgressionMachine.objects.all()

    for progression in progressions:
        # Calculer une recommandation basée sur plusieurs facteurs
        recommandation = calculer_recommandation_avancee(progression)

        print(f"🏋️ {progression.machine.nom}: {progression.poids_actuel}kg → {recommandation}kg")

        # Mettre à jour la progression si nécessaire
        if recommandation != progression.poids_actuel:
            ancien_poids = progression.poids_actuel
            progression.poids_actuel = recommandation
            if recommandation > ancien_poids:
                progression.progression_poids_total += (recommandation - ancien_poids)
                progression.derniere_progression = timezone.now()
            progression.save()
            print(f"   ✅ Progression mise à jour: {ancien_poids}kg → {recommandation}kg")

def calculer_recommandation_avancee(progression):
    """
    Calcule une recommandation avancée basée sur plusieurs facteurs
    """
    # Facteur 1: Taux de réussite récent
    taux_reussite = progression.taux_reussite

    # Facteur 2: Nombre de séances
    nombre_seances = progression.nombre_seances_machine

    # Facteur 3: Dernière progression
    jours_sans_progression = 0
    if progression.derniere_progression:
        jours_sans_progression = (timezone.now() - progression.derniere_progression).days

    # Facteur 4: 1RM estimé
    unrm_estime = progression.dernier_1rm or 0

    # Logique de recommandation
    increment = progression.machine.increment_poids
    poids_actuel = progression.poids_actuel

    # Cas 1: Taux de réussite élevé (> 85%)
    if taux_reussite >= 85:
        return min(poids_actuel + increment, progression.machine.poids_maximum)

    # Cas 2: Taux de réussite moyen (70-85%) et stagnation
    elif taux_reussite >= 70 and jours_sans_progression > 14:
        return min(poids_actuel + increment, progression.machine.poids_maximum)

    # Cas 3: Beaucoup de séances (> 5) et taux > 60%
    elif nombre_seances >= 5 and taux_reussite >= 60:
        return min(poids_actuel + increment, progression.machine.poids_maximum)

    # Cas 4: 1RM élevé par rapport au poids actuel
    elif unrm_estime > 0 and (unrm_estime / poids_actuel) > 1.3:
        return min(poids_actuel + increment, progression.machine.poids_maximum)

    # Sinon, maintenir le poids actuel
    return poids_actuel

def tester_recommandation_ameliorée():
    """
    Teste la recommandation améliorée
    """
    print("\n🧪 Test de la recommandation améliorée...")

    # Créer un scénario de test
    user = User.objects.first()
    if not user:
        print("❌ Aucun utilisateur trouvé")
        return

    machine = Machine.objects.first()
    if not machine:
        print("❌ Aucune machine trouvée")
        return

    # Créer une progression de test
    progression, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        defaults={
            'poids_actuel': 59.0,
            'taux_reussite': 75.0,
            'nombre_seances_machine': 5,
            'dernier_1rm': 82.0
        }
    )

    print(f"📊 Test avec {progression.machine.nom}:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")
    print(f"   Nombre de séances: {progression.nombre_seances_machine}")
    print(f"   1RM estimé: {progression.dernier_1rm}kg")

    # Tester la recommandation améliorée
    recommandation = calculer_recommandation_avancee(progression)
    print(f"   Recommandation améliorée: {recommandation}kg")

    if recommandation > progression.poids_actuel:
        print(f"   ✅ PROGRESSION RECOMMANDÉE: +{recommandation - progression.poids_actuel}kg")
    else:
        print(f"   ⏸️ MAINTIEN: {recommandation}kg")

if __name__ == "__main__":
    print("🚀 Diagnostic et correction de la recommandation intelligente")
    print("=" * 70)

    # Diagnostic
    diagnostiquer_problemes_recommandation()

    # Correction
    corriger_taux_reussite()

    # Amélioration
    ameliorer_recommandation_intelligente()

    # Test
    tester_recommandation_ameliorée()

    print("\n✅ Diagnostic et correction terminés")