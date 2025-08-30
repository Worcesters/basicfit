#!/usr/bin/env python
"""
Script de migration vers l'architecture unifiée BasicFit v2
Migre toutes les données des anciennes tables vers la nouvelle table unique
"""
import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.production')
django.setup()

from apps.workouts.models_refactored import SeanceEffectuee, ExerciceEffectue
from apps.workouts.models_calendar import CalendrierEntrainement, ExerciceCalendrier
from apps.workouts.models_unified import ExerciceEffectueUnifie, CalendrierEntrainementSimple
from apps.users.models import User

def migrate_seances_effectuees():
    """Migre les séances effectuées vers la table unifiée"""
    print("🔄 Migration des séances effectuées...")

    migrated_count = 0
    seances = SeanceEffectuee.objects.all()

    for seance in seances:
        print(f"  📅 Migration séance: {seance.nom} du {seance.date_debut}")

        # Créer ou récupérer l'entrée calendrier simple
        calendrier_simple, created = CalendrierEntrainementSimple.objects.get_or_create(
            utilisateur=seance.utilisateur,
            date_entrainement=seance.date_debut.date(),
            nom_seance=seance.nom or "Séance migrée",
            defaults={
                'duree_totale_minutes': seance.duree_minutes or 60,
                'source_donnees': 'MANUEL',
                'commentaire': f"Migré depuis SeanceEffectuee (ID: {seance.id})"
            }
        )

        # Migrer tous les exercices de cette séance
        exercices = ExerciceEffectue.objects.filter(seance=seance)

        for exercice in exercices:
            # Créer l'exercice unifié
            exercice_unifie, created = ExerciceEffectueUnifie.objects.get_or_create(
                utilisateur=seance.utilisateur,
                date_exercice=seance.date_debut,
                nom_exercice=exercice.nom_exercice,
                machine=exercice.machine,
                source='MANUEL_TEMPS_REEL',
                defaults={
                    'nom_seance': seance.nom or "Séance migrée",
                    'duree_seance_minutes': seance.duree_minutes,
                    'series_effectuees': exercice.series_realisees,
                    'repetitions_totales': exercice.repetitions_totales,
                    'poids_utilise': exercice.poids_moyen or 0,
                    'taux_reussite': exercice.taux_reussite or 100.0,
                    'commentaire_utilisateur': "",
                }
            )

            if created:
                migrated_count += 1
                print(f"    ✅ Exercice migré: {exercice.nom_exercice}")

        # Mettre à jour les métriques du calendrier
        calendrier_simple.mettre_a_jour_metriques()

    print(f"✅ Migration terminée: {migrated_count} exercices migrés depuis SeanceEffectuee")
    return migrated_count

def migrate_calendrier_entrainements():
    """Migre les entraînements du calendrier vers la table unifiée"""
    print("🔄 Migration des entraînements calendrier...")

    migrated_count = 0
    calendriers = CalendrierEntrainement.objects.all()

    for calendrier in calendriers:
        print(f"  📅 Migration calendrier: {calendrier.nom_seance} du {calendrier.date_entrainement}")

        # Créer ou récupérer l'entrée calendrier simple
        calendrier_simple, created = CalendrierEntrainementSimple.objects.get_or_create(
            utilisateur=calendrier.utilisateur,
            date_entrainement=calendrier.date_entrainement,
            nom_seance=calendrier.nom_seance,
            defaults={
                'duree_totale_minutes': calendrier.duree_minutes,
                'source_donnees': calendrier.source_donnees,
                'commentaire': f"Migré depuis CalendrierEntrainement (ID: {calendrier.id})"
            }
        )

        # Migrer tous les exercices de ce calendrier
        exercices = ExerciceCalendrier.objects.filter(calendrier=calendrier)

        for exercice in exercices:
            # Créer l'exercice unifié
            exercice_unifie, created = ExerciceEffectueUnifie.objects.get_or_create(
                utilisateur=calendrier.utilisateur,
                date_exercice=datetime.combine(calendrier.date_entrainement, datetime.min.time()),
                nom_exercice=exercice.nom_exercice,
                machine=exercice.machine,
                source='CSV_IMPORT',
                defaults={
                    'nom_seance': calendrier.nom_seance,
                    'duree_seance_minutes': calendrier.duree_minutes,
                    'series_effectuees': exercice.series_effectuees,
                    'repetitions_totales': exercice.repetitions_totales,
                    'poids_utilise': exercice.poids_utilise,
                    'taux_reussite': 100.0,  # Assumé pour les imports CSV
                    'ligne_csv_originale': f"Migré depuis ExerciceCalendrier (ID: {exercice.id})",
                }
            )

            if created:
                migrated_count += 1
                print(f"    ✅ Exercice migré: {exercice.nom_exercice}")

        # Mettre à jour les métriques du calendrier
        calendrier_simple.mettre_a_jour_metriques()

    print(f"✅ Migration terminée: {migrated_count} exercices migrés depuis CalendrierEntrainement")
    return migrated_count

def show_stats():
    """Affiche les statistiques avant/après migration"""
    print("\n📊 STATISTIQUES DES DONNÉES")
    print("=" * 50)

    print("🗂️ Anciennes tables:")
    print(f"  SeanceEffectuee: {SeanceEffectuee.objects.count()}")
    print(f"  ExerciceEffectue: {ExerciceEffectue.objects.count()}")
    print(f"  CalendrierEntrainement: {CalendrierEntrainement.objects.count()}")
    print(f"  ExerciceCalendrier: {ExerciceCalendrier.objects.count()}")

    print("\n✨ Nouvelles tables:")
    print(f"  ExerciceEffectueUnifie: {ExerciceEffectueUnifie.objects.count()}")
    print(f"  CalendrierEntrainementSimple: {CalendrierEntrainementSimple.objects.count()}")

    print("\n📈 Répartition par source dans la table unifiée:")
    from django.db.models import Count
    repartition = ExerciceEffectueUnifie.objects.values('source').annotate(count=Count('id'))
    for item in repartition:
        print(f"  {item['source']}: {item['count']} exercices")

if __name__ == "__main__":
    print("🚀 MIGRATION VERS L'ARCHITECTURE UNIFIÉE BASICFIT V2")
    print("=" * 60)

    # Statistiques avant migration
    show_stats()

    # Demander confirmation
    response = input("\n❓ Voulez-vous procéder à la migration ? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration annulée")
        sys.exit(0)

    print("\n🔄 DÉBUT DE LA MIGRATION...")

    try:
        # Migrer les données
        count1 = migrate_seances_effectuees()
        count2 = migrate_calendrier_entrainements()

        total_migrated = count1 + count2

        print(f"\n🎉 MIGRATION TERMINÉE AVEC SUCCÈS!")
        print(f"📊 Total migré: {total_migrated} exercices")

        # Statistiques après migration
        show_stats()

        print("\n✅ Vous pouvez maintenant:")
        print("  1. Utiliser l'interface admin pour voir vos données dans 'Exercices effectués'")
        print("  2. Tester l'API unifiée: /api/workouts/exercices-unifies/")
        print("  3. Activer les nouvelles méthodes Android si vous le souhaitez")

    except Exception as e:
        print(f"\n❌ ERREUR PENDANT LA MIGRATION: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)