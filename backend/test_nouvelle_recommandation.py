#!/usr/bin/env python
"""
Script pour tester la nouvelle logique de recommandation avec le scénario 59kg
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

def tester_scenario_59kg():
    """
    Teste le scénario 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)
    avec la nouvelle logique de recommandation
    """
    print("🏋️ Test du scénario 59kg avec la nouvelle logique de recommandation")
    print("=" * 70)

    # Récupérer l'utilisateur et la machine
    user = User.objects.first()
    machine = Machine.objects.filter(nom="Développé couché").first()

    if not user or not machine:
        print("❌ Utilisateur ou machine non trouvé")
        return

    # Récupérer la progression existante
    progression = ProgressionMachine.objects.filter(
        utilisateur=user,
        machine=machine
    ).first()

    if not progression:
        print("❌ Progression non trouvée")
        return

    print(f"👤 Utilisateur: {user.nom_complet}")
    print(f"🏋️ Machine: {machine.nom}")
    print(f"📊 État initial:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")
    print(f"   Nombre de séances: {progression.nombre_seances_machine}")
    print(f"   1RM estimé: {progression.dernier_1rm}kg")

    # Tester la nouvelle recommandation intelligente
    recommandation = progression.calculer_recommandation_intelligente()
    print(f"\n🎯 Recommandation intelligente: {recommandation}kg")

    if recommandation > progression.poids_actuel:
        print(f"   ✅ PROGRESSION RECOMMANDÉE: +{recommandation - progression.poids_actuel}kg")
    else:
        print(f"   ⏸️ MAINTIEN: {recommandation}kg")

    # Analyser les facteurs
    print(f"\n🔍 Analyse des facteurs:")

    # Facteur 1: Taux de réussite
    taux_reussite = progression.taux_reussite
    print(f"   Taux de réussite: {taux_reussite}%")
    if taux_reussite >= 85:
        print(f"   ✅ Facteur 1: Taux élevé (> 85%)")
    elif taux_reussite >= 70:
        print(f"   ⚠️ Facteur 1: Taux moyen (70-85%)")
    else:
        print(f"   ❌ Facteur 1: Taux faible (< 70%)")

    # Facteur 2: Nombre de séances
    nombre_seances = progression.nombre_seances_machine
    print(f"   Nombre de séances: {nombre_seances}")
    if nombre_seances >= 5:
        print(f"   ✅ Facteur 2: Beaucoup de séances (≥ 5)")
    else:
        print(f"   ⚠️ Facteur 2: Peu de séances (< 5)")

    # Facteur 3: Dernière progression
    jours_sans_progression = 0
    if progression.derniere_progression:
        jours_sans_progression = (timezone.now() - progression.derniere_progression).days
    print(f"   Jours sans progression: {jours_sans_progression}")
    if jours_sans_progression > 14:
        print(f"   ✅ Facteur 3: Stagnation détectée (> 14 jours)")
    else:
        print(f"   ⚠️ Facteur 3: Progression récente (< 14 jours)")

    # Facteur 4: 1RM estimé
    unrm_estime = progression.dernier_1rm or 0
    ratio_1rm = unrm_estime / progression.poids_actuel if progression.poids_actuel > 0 else 0
    print(f"   1RM estimé: {unrm_estime}kg (ratio: {ratio_1rm:.2f})")
    if ratio_1rm > 1.3:
        print(f"   ✅ Facteur 4: 1RM élevé (ratio > 1.3)")
    else:
        print(f"   ⚠️ Facteur 4: 1RM normal (ratio ≤ 1.3)")

    # Expliquer la décision
    print(f"\n💡 Explication de la recommandation:")
    if recommandation > progression.poids_actuel:
        if taux_reussite >= 85:
            print(f"   → Progression car taux de réussite élevé ({taux_reussite}% ≥ 85%)")
        elif taux_reussite >= 70 and jours_sans_progression > 14:
            print(f"   → Progression car taux moyen ({taux_reussite}%) et stagnation ({jours_sans_progression} jours)")
        elif nombre_seances >= 5 and taux_reussite >= 60:
            print(f"   → Progression car beaucoup de séances ({nombre_seances}) et taux acceptable ({taux_reussite}%)")
        elif ratio_1rm > 1.3:
            print(f"   → Progression car 1RM élevé (ratio {ratio_1rm:.2f} > 1.3)")
        else:
            print(f"   → Progression par détection de stagnation")
    else:
        print(f"   → Maintien car aucun critère de progression n'est satisfait")
        print(f"   → Taux: {taux_reussite}% (seuil: 85%), Séances: {nombre_seances} (seuil: 5)")
        print(f"   → Stagnation: {jours_sans_progression} jours (seuil: 14), Ratio 1RM: {ratio_1rm:.2f} (seuil: 1.3)")

def comparer_ancienne_nouvelle_logique():
    """
    Compare l'ancienne et la nouvelle logique de recommandation
    """
    print("\n🔄 Comparaison ancienne vs nouvelle logique...")

    user = User.objects.first()
    machine = Machine.objects.filter(nom="Développé couché").first()

    if not user or not machine:
        return

    progression = ProgressionMachine.objects.filter(
        utilisateur=user,
        machine=machine
    ).first()

    if not progression:
        return

    print(f"📊 Comparaison pour {machine.nom}:")
    print(f"   Poids actuel: {progression.poids_actuel}kg")
    print(f"   Taux de réussite: {progression.taux_reussite}%")

    # Ancienne logique (simulée)
    ancienne_recommandation = progression.poids_actuel  # Pas de progression
    if progression.evaluer_progression_historique():
        ancienne_recommandation = progression.poids_actuel + progression.machine.increment_poids

    # Nouvelle logique
    nouvelle_recommandation = progression.calculer_recommandation_intelligente()

    print(f"   Ancienne logique: {ancienne_recommandation}kg")
    print(f"   Nouvelle logique: {nouvelle_recommandation}kg")

    if nouvelle_recommandation > ancienne_recommandation:
        print(f"   ✅ Amélioration: +{nouvelle_recommandation - ancienne_recommandation}kg")
    elif nouvelle_recommandation < ancienne_recommandation:
        print(f"   ⚠️ Réduction: {nouvelle_recommandation - ancienne_recommandation}kg")
    else:
        print(f"   ➡️ Même résultat")

if __name__ == "__main__":
    tester_scenario_59kg()
    comparer_ancienne_nouvelle_logique()
    print("\n✅ Test terminé")