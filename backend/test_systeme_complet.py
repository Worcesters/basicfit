#!/usr/bin/env python
"""
Script pour tester le système complet de recommandation avec le scénario 59kg
"""

import os
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine, SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.machines.models import Machine
from apps.users.models import User
from apps.core.models import ModeEntrainement
from django.utils import timezone

def simuler_scenario_59kg_complet():
    """
    Simule le scénario complet: 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)
    """
    print("🏋️ Simulation complète du scénario 59kg")
    print("=" * 70)

    # Récupérer l'utilisateur et la machine
    user = User.objects.first()
    machine = Machine.objects.filter(nom="Développé couché").first()

    if not user or not machine:
        print("❌ Utilisateur ou machine non trouvé")
        return

    # Créer une séance de test
    seance = SeanceEntrainement.objects.create(
        utilisateur=user,
        nom="Test scénario 59kg",
        date_prevue=timezone.now(),
        date_debut=timezone.now(),
        statut='TERMINEE'
    )

    # Créer l'exercice
    exercice = ExerciceSeance.objects.create(
        seance=seance,
        machine=machine,
        poids_prevu=59.0,
        poids_utilise=59.0,
        series_prevues=3,
        nombre_series=3,
        repetitions_prevues=12,
        repetitions_realisees=34,  # 12+12+10
        statut='TERMINE'
    )

    # Créer les 3 séries
    # Série 1: 59kg × 12 reps (réussie)
    serie1 = SeriExercice.objects.create(
        exercice=exercice,
        numero_serie=1,
        poids_prevu=59.0,
        poids_utilise=59.0,
        repetitions_prevues=12,
        repetitions_realisees=12,
        statut='REUSSIE'
    )

    # Série 2: 59kg × 12 reps (réussie)
    serie2 = SeriExercice.objects.create(
        exercice=exercice,
        numero_serie=2,
        poids_prevu=59.0,
        poids_utilise=59.0,
        repetitions_prevues=12,
        repetitions_realisees=12,
        statut='REUSSIE'
    )

    # Série 3: 59kg × 10 reps (échouée - 2 reps manquantes)
    serie3 = SeriExercice.objects.create(
        exercice=exercice,
        numero_serie=3,
        poids_prevu=12,
        poids_utilise=59.0,
        repetitions_prevues=12,
        repetitions_realisees=10,
        statut='ECHOUEE'
    )

    print(f"📊 Séance créée:")
    print(f"   Série 1: {serie1.poids_utilise}kg × {serie1.repetitions_realisees} reps → {'✅' if serie1.est_reussie else '❌'}")
    print(f"   Série 2: {serie2.poids_utilise}kg × {serie2.repetitions_realisees} reps → {'✅' if serie2.est_reussie else '❌'}")
    print(f"   Série 3: {serie3.poids_utilise}kg × {serie3.repetitions_realisees} reps → {'✅' if serie3.est_reussie else '❌'}")

    # Calculer le taux de réussite réel
    series_reussies = sum(1 for serie in [serie1, serie2, serie3] if serie.est_reussie)
    taux_reel = (series_reussies / 3) * 100
    print(f"   Taux de réussite: {series_reussies}/3 = {taux_reel:.1f}%")

    # Récupérer ou créer la progression
    progression, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        defaults={
            'poids_actuel': 59.0,
            'taux_reussite': taux_reel,
            'nombre_seances_machine': 1,
            'derniere_seance': seance
        }
    )

    if not created:
        # Mettre à jour la progression
        progression.poids_actuel = 59.0
        progression.taux_reussite = taux_reel
        progression.nombre_seances_machine += 1
        progression.derniere_seance = seance
        progression.save()

    print(f"\n📈 Progression mise à jour:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")
    print(f"   Nombre de séances: {progression.nombre_seances_machine}")

    # Tester la recommandation intelligente
    recommandation = progression.calculer_recommandation_intelligente()
    print(f"\n🎯 Recommandation intelligente: {recommandation}kg")

    if recommandation > progression.poids_actuel:
        print(f"   ✅ PROGRESSION RECOMMANDÉE: +{recommandation - progression.poids_actuel}kg")
    else:
        print(f"   ⏸️ MAINTIEN: {recommandation}kg")

    # Expliquer pourquoi
    print(f"\n💡 Explication:")
    if taux_reel >= 85:
        print(f"   → Progression car taux de réussite élevé ({taux_reel:.1f}% ≥ 85%)")
    elif taux_reel >= 70 and progression.nombre_seances_machine >= 3:
        print(f"   → Progression car taux acceptable ({taux_reel:.1f}%) et expérience ({progression.nombre_seances_machine} séances)")
    elif progression.nombre_seances_machine >= 5 and taux_reel >= 60:
        print(f"   → Progression car beaucoup d'expérience ({progression.nombre_seances_machine} séances) et taux acceptable ({taux_reel:.1f}%)")
    else:
        print(f"   → Maintien car taux insuffisant ({taux_reel:.1f}%) pour la progression")

    return progression, recommandation

def tester_api_recommandation():
    """
    Teste l'API de recommandation
    """
    print("\n🌐 Test de l'API de recommandation...")

    # Simuler une requête API
    from django.test import RequestFactory
    from apps.workouts.views import get_recommendation_by_id
    from rest_framework.test import force_authenticate

    factory = RequestFactory()
    user = User.objects.first()
    machine = Machine.objects.filter(nom="Développé couché").first()

    if not user or not machine:
        print("❌ Utilisateur ou machine non trouvé")
        return

    # Créer une requête
    request = factory.get(f'/api/workouts/recommendation/{machine.id}/')
    force_authenticate(request, user=user)

    try:
        # Appeler la vue
        from rest_framework.decorators import api_view, permission_classes
        from rest_framework.permissions import IsAuthenticated
        from rest_framework.response import Response

        # Simuler l'appel de la vue
        response = get_recommendation_by_id(request, machine.id)

        if response.status_code == 200:
            data = response.data
            print(f"✅ API fonctionne:")
            print(f"   Poids recommandé: {data['poids_recommande']}kg")
            print(f"   Peut progresser: {data['peut_progresser']}")
            print(f"   Taux de réussite: {data['taux_reussite']}%")
            print(f"   Source: {data['source']}")
        else:
            print(f"❌ Erreur API: {response.status_code}")

    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")

def nettoyer_donnees_test():
    """
    Nettoie les données de test
    """
    print("\n🧹 Nettoyage des données de test...")

    # Supprimer les séances de test
    seances_test = SeanceEntrainement.objects.filter(nom__contains="Test scénario")
    count = seances_test.count()
    seances_test.delete()
    print(f"   {count} séances de test supprimées")

if __name__ == "__main__":
    # Test complet
    progression, recommandation = simuler_scenario_59kg_complet()

    # Test API
    tester_api_recommandation()

    # Nettoyage
    nettoyer_donnees_test()

    print("\n✅ Test du système complet terminé")
    print(f"🎯 Résultat final: {recommandation}kg recommandé")