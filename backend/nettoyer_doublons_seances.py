#!/usr/bin/env python
"""
Script pour nettoyer les séances en double
"""

import os
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from apps.workouts.models import SeanceEntrainement, ExerciceSeance, SeriExercice
from apps.users.models import User

def identifier_doublons():
    print("🔍 IDENTIFICATION DES DOUBLONS")
    print("=" * 50)

    # Chercher les séances créées récemment
    date_recente = datetime.now() - timedelta(days=1)
    seances_recentes = SeanceEntrainement.objects.filter(
        created_at__gte=date_recente
    ).order_by('created_at')

    print(f"📅 Séances créées dans les dernières 24h: {seances_recentes.count()}")

    # Grouper par utilisateur et nom
    doublons_trouves = []

    for seance in seances_recentes:
        print(f"\n🔍 Séance: {seance.nom}")
        print(f"   - Utilisateur: {seance.utilisateur.nom_complet}")
        print(f"   - Date création: {seance.created_at}")
        print(f"   - Statut: {seance.statut}")
        print(f"   - Exercices: {seance.exercices.count()}")

        # Chercher des séances similaires
        seances_similaires = SeanceEntrainement.objects.filter(
            utilisateur=seance.utilisateur,
            nom__icontains=seance.nom.split()[0],  # Premier mot du nom
            created_at__gte=seance.created_at - timedelta(minutes=5),
            created_at__lte=seance.created_at + timedelta(minutes=5)
        ).exclude(id=seance.id)

        if seances_similaires.exists():
            print(f"   ⚠️ DOUBLONS TROUVÉS: {seances_similaires.count()}")
            for doublon in seances_similaires:
                print(f"      - ID: {doublon.id}, Nom: {doublon.nom}, Créé: {doublon.created_at}")
            doublons_trouves.append((seance, seances_similaires))
        else:
            print(f"   ✅ Aucun doublon")

    return doublons_trouves

def nettoyer_doublons(doublons):
    print(f"\n🧹 NETTOYAGE DES DOUBLONS")
    print("=" * 50)

    total_supprimes = 0

    for seance_principale, doublons in doublons:
        print(f"\n🔍 Traitement de la séance: {seance_principale.nom}")
        print(f"   - Séance principale: ID {seance_principale.id}")

        for doublon in doublons:
            print(f"   - Suppression du doublon: ID {doublon.id}")

            # Supprimer les exercices et séries du doublon
            exercices_doublon = doublon.exercices.all()
            for exercice in exercices_doublon:
                series_doublon = exercice.series.all()
                series_doublon.delete()
                print(f"      - Supprimé {series_doublon.count()} séries")
            exercices_doublon.delete()
            print(f"      - Supprimé {exercices_doublon.count()} exercices")

            # Supprimer la séance doublon
            doublon.delete()
            print(f"      - Séance doublon supprimée")
            total_supprimes += 1

    print(f"\n✅ NETTOYAGE TERMINÉ")
    print(f"   - Total séances supprimées: {total_supprimes}")

    return total_supprimes

def verifier_integrite():
    print(f"\n🔍 VÉRIFICATION INTÉGRITÉ")
    print("=" * 50)

    # Compter les séances restantes
    total_seances = SeanceEntrainement.objects.count()
    total_exercices = ExerciceSeance.objects.count()
    total_series = SeriExercice.objects.count()

    print(f"📊 État après nettoyage:")
    print(f"   - Séances: {total_seances}")
    print(f"   - Exercices: {total_exercices}")
    print(f"   - Séries: {total_series}")

    # Vérifier qu'il n'y a plus de doublons
    doublons_restants = identifier_doublons()
    if not doublons_restants:
        print(f"   ✅ Aucun doublon restant")
    else:
        print(f"   ⚠️ {len(doublons_restants)} doublons restants")

def proposer_correction_android():
    print(f"\n📱 CORRECTION ANDROID")
    print("=" * 50)

    print("🔧 POUR ÉVITER LES DOUBLONS À L'AVENIR:")
    print("   1. Dans MainActivity.kt, ligne 737:")
    print("      - Supprimer ou commenter la synchronisation automatique")
    print("      - Garder seulement la sauvegarde directe (ligne 3090)")

    print("   2. Ou ajouter une vérification de doublon:")
    print("      - Vérifier si une séance similaire existe déjà")
    print("      - Éviter de créer des doublons")

    print("   3. Ou utiliser un ID unique:")
    print("      - Générer un UUID pour chaque séance")
    print("      - Vérifier l'unicité avant sauvegarde")

if __name__ == "__main__":
    print("🧹 NETTOYAGE DES SÉANCES EN DOUBLE")
    print("=" * 70)

    # Identifier les doublons
    doublons = identifier_doublons()

    if doublons:
        print(f"\n⚠️ {len(doublons)} groupes de doublons trouvés")

        # Demander confirmation
        reponse = input("\nVoulez-vous nettoyer les doublons ? (o/n): ")

        if reponse.lower() in ['o', 'oui', 'y', 'yes']:
            nettoyer_doublons(doublons)
            verifier_integrite()
        else:
            print("❌ Nettoyage annulé")
    else:
        print("✅ Aucun doublon trouvé")

    proposer_correction_android()

    print(f"\n" + "=" * 70)
    print("✅ DIAGNOSTIC TERMINÉ")