#!/usr/bin/env python
"""
Script pour diagnostiquer et corriger les progressions bloquées à 20kg
"""

import os
import sys
import django
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import ProgressionMachine
from apps.machines.models import Machine
from apps.users.models import User
from django.utils import timezone

def diagnostiquer_progressions_20kg():
    """
    Diagnostique les progressions bloquées à 20kg
    """
    print("🔍 Diagnostic des progressions bloquées à 20kg...")

    # Trouver toutes les progressions à 20kg
    progressions_20kg = ProgressionMachine.objects.filter(poids_actuel=20.0)

    print(f"📊 Trouvé {progressions_20kg.count()} progressions à 20kg")

    for progression in progressions_20kg:
        print(f"\n--- Progression: {progression.utilisateur.nom_complet} - {progression.machine.nom} ---")
        print(f"Poids actuel: {progression.poids_actuel}kg")
        print(f"Taux de réussite: {progression.taux_reussite}%")
        print(f"Nombre de séances: {progression.nombre_seances_machine}")
        print(f"Dernière progression: {progression.derniere_progression}")
        print(f"Peut progresser (historique): {progression.evaluer_progression_historique()}")
        print(f"Détecte stagnation: {progression.detecter_stagnation()}")
        print(f"Recommandation intelligente: {progression.calculer_recommandation_intelligente()}kg")

def corriger_progressions_20kg():
    """
    Corrige les progressions bloquées à 20kg en forçant la progression si nécessaire
    """
    print("\n🔧 Correction des progressions bloquées à 20kg...")

    progressions_20kg = ProgressionMachine.objects.filter(poids_actuel=20.0)
    corrigees = 0

    for progression in progressions_20kg:
        # Vérifier si la progression devrait être augmentée
        nouveau_poids = progression.calculer_recommandation_intelligente()

        if nouveau_poids > 20.0:
            ancien_poids = progression.poids_actuel
            progression.poids_actuel = nouveau_poids
            progression.progression_poids_total += (nouveau_poids - ancien_poids)
            progression.derniere_progression = timezone.now()
            progression.save()

            print(f"✅ Corrigé: {progression.utilisateur.nom_complet} - {progression.machine.nom}")
            print(f"   {ancien_poids}kg → {nouveau_poids}kg")
            corrigees += 1

    print(f"\n📈 {corrigees} progressions corrigées sur {progressions_20kg.count()}")

def analyser_causes_blocage():
    """
    Analyse les causes possibles du blocage à 20kg
    """
    print("\n🔍 Analyse des causes de blocage...")

    progressions_20kg = ProgressionMachine.objects.filter(poids_actuel=20.0)

    # Statistiques
    total = progressions_20kg.count()
    avec_taux_eleve = progressions_20kg.filter(taux_reussite__gte=80).count()
    avec_seances_suffisantes = progressions_20kg.filter(nombre_seances_machine__gte=3).count()
    sans_progression_recente = 0

    for progression in progressions_20kg:
        if progression.derniere_progression:
            if (timezone.now() - progression.derniere_progression) > timedelta(weeks=2):
                sans_progression_recente += 1
        else:
            sans_progression_recente += 1

    print(f"📊 Statistiques des progressions bloquées à 20kg:")
    print(f"   Total: {total}")
    print(f"   Avec taux de réussite ≥ 80%: {avec_taux_eleve}")
    print(f"   Avec ≥ 3 séances: {avec_seances_suffisantes}")
    print(f"   Sans progression récente (2+ semaines): {sans_progression_recente}")

if __name__ == "__main__":
    print("🚀 Script de diagnostic et correction des progressions bloquées à 20kg")
    print("=" * 70)

    # Diagnostic
    diagnostiquer_progressions_20kg()

    # Analyse des causes
    analyser_causes_blocage()

    # Demander confirmation pour la correction
    reponse = input("\n❓ Voulez-vous corriger les progressions bloquées ? (y/N): ")
    if reponse.lower() in ['y', 'yes', 'oui', 'o']:
        corriger_progressions_20kg()
    else:
        print("❌ Correction annulée")

    print("\n✅ Script terminé")