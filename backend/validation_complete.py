#!/usr/bin/env python
"""
Script de validation complète du système de recommandation
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

def validation_complete():
    """
    Validation complète du système
    """
    print("🔍 VALIDATION COMPLÈTE DU SYSTÈME")
    print("=" * 70)

    # 1. Vérifier la structure de la base de données
    print("1️⃣ Vérification de la structure de la base de données...")

    user = User.objects.first()
    if not user:
        print("❌ ERREUR: Aucun utilisateur trouvé")
        return False

    machine = Machine.objects.filter(nom="Développé couché").first()
    if not machine:
        print("❌ ERREUR: Machine 'Développé couché' non trouvée")
        return False

    print(f"✅ Utilisateur: {user.nom_complet}")
    print(f"✅ Machine: {machine.nom}")
    print(f"✅ Increment poids: {machine.increment_poids}kg")
    print(f"✅ Poids maximum: {machine.poids_maximum}kg")

    # 2. Vérifier les progressions existantes
    print("\n2️⃣ Vérification des progressions existantes...")

    progressions = ProgressionMachine.objects.filter(utilisateur=user)
    print(f"📊 {progressions.count()} progressions trouvées")

    for prog in progressions:
        print(f"   {prog.machine.nom}: {prog.poids_actuel}kg, {prog.taux_reussite}%, {prog.nombre_seances_machine} séances")

    # 3. Test du scénario 59kg exact
    print("\n3️⃣ Test du scénario exact: 59kg × 12 reps (2 séries) puis 59kg × 10 reps (1 série)")

    # Créer une progression de test propre
    progression_test, created = ProgressionMachine.objects.get_or_create(
        utilisateur=user,
        machine=machine,
        defaults={
            'poids_actuel': 59.0,
            'taux_reussite': 66.7,  # 2/3 séries réussies
            'nombre_seances_machine': 5,
            'dernier_1rm': 82.0
        }
    )

    if not created:
        # Réinitialiser pour le test
        progression_test.poids_actuel = 59.0
        progression_test.taux_reussite = 66.7
        progression_test.nombre_seances_machine = 5
        progression_test.dernier_1rm = 82.0
        progression_test.save()

    print(f"📊 État initial:")
    print(f"   Poids actuel: {progression_test.poids_actuel}kg")
    print(f"   Taux de réussite: {progression_test.taux_reussite}%")
    print(f"   Nombre de séances: {progression_test.nombre_seances_machine}")
    print(f"   1RM estimé: {progression_test.dernier_1rm}kg")

    # 4. Tester la recommandation intelligente
    print("\n4️⃣ Test de la recommandation intelligente...")

    recommandation = progression_test.calculer_recommandation_intelligente()
    print(f"🎯 Recommandation: {recommandation}kg")

    # 5. Analyser chaque facteur
    print("\n5️⃣ Analyse détaillée des facteurs:")

    # Facteur 1: Taux de réussite
    taux = progression_test.taux_reussite
    print(f"   Taux de réussite: {taux}%")
    if taux >= 85:
        print(f"   ✅ Critère 1 SATISFAIT (≥ 85%)")
    elif taux >= 70:
        print(f"   ⚠️ Critère 1 PARTIEL (70-85%)")
    else:
        print(f"   ❌ Critère 1 NON SATISFAIT (< 70%)")

    # Facteur 2: Nombre de séances
    nb_seances = progression_test.nombre_seances_machine
    print(f"   Nombre de séances: {nb_seances}")
    if nb_seances >= 5:
        print(f"   ✅ Critère 2 SATISFAIT (≥ 5)")
    else:
        print(f"   ❌ Critère 2 NON SATISFAIT (< 5)")

    # Facteur 3: Stagnation
    jours_sans_prog = 0
    if progression_test.derniere_progression:
        jours_sans_prog = (timezone.now() - progression_test.derniere_progression).days
    print(f"   Jours sans progression: {jours_sans_prog}")
    if jours_sans_prog > 14:
        print(f"   ✅ Critère 3 SATISFAIT (> 14 jours)")
    else:
        print(f"   ❌ Critère 3 NON SATISFAIT (≤ 14 jours)")

    # Facteur 4: 1RM
    unrm = progression_test.dernier_1rm or 0
    ratio_1rm = unrm / progression_test.poids_actuel if progression_test.poids_actuel > 0 else 0
    print(f"   Ratio 1RM: {ratio_1rm:.2f}")
    if ratio_1rm > 1.3:
        print(f"   ✅ Critère 4 SATISFAIT (> 1.3)")
    else:
        print(f"   ❌ Critère 4 NON SATISFAIT (≤ 1.3)")

    # 6. Vérifier la logique exacte
    print("\n6️⃣ Vérification de la logique exacte:")

    increment = machine.increment_poids
    poids_actuel = progression_test.poids_actuel

    # Tester chaque condition
    condition1 = taux >= 85
    condition2 = taux >= 70 and jours_sans_prog > 14
    condition3 = nb_seances >= 5 and taux >= 60
    condition4 = ratio_1rm > 1.3

    print(f"   Condition 1 (taux ≥ 85%): {condition1}")
    print(f"   Condition 2 (taux 70-85% + stagnation): {condition2}")
    print(f"   Condition 3 (≥5 séances + taux ≥60%): {condition3}")
    print(f"   Condition 4 (ratio 1RM > 1.3): {condition4}")

    # Calculer manuellement la recommandation
    recommandation_manuelle = poids_actuel
    if condition1 or condition2 or condition3 or condition4:
        recommandation_manuelle = min(poids_actuel + increment, machine.poids_maximum)

    print(f"\n   Calcul manuel: {recommandation_manuelle}kg")
    print(f"   Calcul automatique: {recommandation}kg")

    if recommandation == recommandation_manuelle:
        print(f"   ✅ COHÉRENCE CONFIRMÉE")
    else:
        print(f"   ❌ INCOHÉRENCE DÉTECTÉE")
        return False

    # 7. Test de l'API
    print("\n7️⃣ Test de l'API...")

    try:
        from django.test import RequestFactory
        from apps.workouts.views import get_recommendation_by_id
        from rest_framework.test import force_authenticate

        factory = RequestFactory()
        request = factory.get(f'/api/workouts/recommendation/{machine.id}/')
        force_authenticate(request, user=user)

        response = get_recommendation_by_id(request, machine.id)

        if response.status_code == 200:
            data = response.data
            print(f"   ✅ API fonctionne")
            print(f"   Poids recommandé API: {data['poids_recommande']}kg")
            print(f"   Poids recommandé modèle: {recommandation}kg")

            if abs(data['poids_recommande'] - recommandation) < 0.1:
                print(f"   ✅ COHÉRENCE API CONFIRMÉE")
            else:
                print(f"   ❌ INCOHÉRENCE API DÉTECTÉE")
                return False
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Erreur test API: {e}")
        return False

    # 8. Résumé final
    print("\n8️⃣ RÉSUMÉ FINAL:")

    if recommandation > poids_actuel:
        print(f"   🎯 PROGRESSION RECOMMANDÉE: {poids_actuel}kg → {recommandation}kg (+{recommandation - poids_actuel}kg)")

        # Expliquer pourquoi
        if condition1:
            print(f"   💡 Raison: Taux de réussite élevé ({taux}% ≥ 85%)")
        elif condition2:
            print(f"   💡 Raison: Taux acceptable ({taux}%) et stagnation ({jours_sans_prog} jours)")
        elif condition3:
            print(f"   💡 Raison: Beaucoup d'expérience ({nb_seances} séances) et taux acceptable ({taux}%)")
        elif condition4:
            print(f"   💡 Raison: 1RM élevé (ratio {ratio_1rm:.2f} > 1.3)")
    else:
        print(f"   ⏸️ MAINTIEN: {recommandation}kg")
        print(f"   💡 Raison: Aucun critère de progression satisfait")

    print(f"\n✅ VALIDATION COMPLÈTE RÉUSSIE")
    return True

if __name__ == "__main__":
    success = validation_complete()
    if success:
        print("\n🎉 LE SYSTÈME FONCTIONNE CORRECTEMENT !")
    else:
        print("\n❌ PROBLÈMES DÉTECTÉS - CORRECTION NÉCESSAIRE")