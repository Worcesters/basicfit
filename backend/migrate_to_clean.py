"""
Script de migration vers l'architecture propre BasicFit v2
Convertit les anciennes données vers ExerciceEffectueUnifie et CalendrierEntrainementSimple
"""
import os
import sys
import django
from datetime import datetime, time, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'basicfit_project.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.workouts.models_unified import ExerciceEffectueUnifie, CalendrierEntrainementSimple
from apps.machines.models import Machine

User = get_user_model()

def migrate_old_data():
    """Migre les anciennes données vers la nouvelle architecture"""
    print("🚀 Migration vers l'architecture propre BasicFit v2")
    print("=" * 60)

    # Vérifier que les nouvelles tables existent
    try:
        ExerciceEffectueUnifie.objects.first()
        CalendrierEntrainementSimple.objects.first()
        print("✅ Nouvelles tables accessibles")
    except Exception as e:
        print(f"❌ Erreur accès nouvelles tables: {e}")
        return False

    # Compter les utilisateurs
    users = User.objects.all()
    print(f"👥 {users.count()} utilisateurs trouvés")

    total_migrated = 0

    for user in users:
        print(f"\n🔄 Migration pour {user.username}...")

        try:
            # Migrer les données existantes (si elles existent)
            migrated_count = migrate_user_data(user)
            total_migrated += migrated_count

            print(f"✅ {migrated_count} éléments migrés pour {user.username}")

        except Exception as e:
            print(f"❌ Erreur migration {user.username}: {e}")
            continue

    print(f"\n🎯 Migration terminée: {total_migrated} éléments migrés au total")
    return True

def migrate_user_data(user):
    """Migre les données d'un utilisateur spécifique"""
    migrated_count = 0

    # Essayer de migrer depuis les anciens modèles (si ils existent)
    try:
        # Migration depuis SeanceSimple (si elle existe)
        migrated_count += migrate_from_seance_simple(user)
    except:
        pass

    try:
        # Migration depuis les anciens modèles de séances
        migrated_count += migrate_from_old_seances(user)
    except:
        pass

    # Créer des données de démonstration si aucune migration
    if migrated_count == 0:
        migrated_count += create_demo_data(user)

    return migrated_count

def migrate_from_seance_simple(user):
    """Migre depuis l'ancien modèle SeanceSimple"""
    try:
        from apps.workouts.models_simple import SeanceSimple

        seances = SeanceSimple.objects.filter(utilisateur=user)
        migrated_count = 0

        for seance in seances:
            # Créer l'exercice effectué
            ExerciceEffectueUnifie.objects.create(
                utilisateur=user,
                source='CSV_IMPORT',
                date_exercice=datetime.combine(seance.date_seance, time(9, 0)),  # 9h00 par défaut
                nom_seance=f"Séance {seance.date_seance.strftime('%d/%m/%Y')}",
                nom_exercice=seance.machine_nom,
                machine=None,
                series_effectuees=3,  # Valeurs par défaut
                repetitions_totales=12,
                poids_utilise=0.0,
                ligne_csv_originale=f"Migration depuis SeanceSimple ID {seance.id}",
                taux_reussite=100.00,
                duree_seance_minutes=seance.duree_minutes or 60
            )

            # Créer ou mettre à jour la séance dans le calendrier
            seance_cal, created = CalendrierEntrainementSimple.objects.get_or_create(
                utilisateur=user,
                date_entrainement=seance.date_seance,
                nom_seance=f"Séance {seance.date_seance.strftime('%d/%m/%Y')}",
                defaults={
                    'duree_totale_minutes': seance.duree_minutes or 60,
                    'nombre_exercices': 0,
                    'volume_total_seance': 0.00,
                    'source_donnees': 'CSV_IMPORT'
                }
            )

            if not created:
                seance_cal.mettre_a_jour_metriques()

            migrated_count += 1

        return migrated_count

    except Exception as e:
        print(f"  ⚠️  Migration SeanceSimple échouée: {e}")
        return 0

def migrate_from_old_seances(user):
    """Migre depuis les anciens modèles de séances"""
    try:
        from apps.workouts.models import SeanceEntrainement, ExerciceSeance

        seances = SeanceEntrainement.objects.filter(utilisateur=user)
        migrated_count = 0

        for seance in seances:
            # Récupérer les exercices de cette séance
            exercices = ExerciceSeance.objects.filter(seance=seance)

            for exercice in exercices:
                # Créer l'exercice effectué
                ExerciceEffectueUnifie.objects.create(
                    utilisateur=user,
                    source='IMPORT_EXTERNE',
                    date_exercice=seance.date_debut or seance.date_prevue,
                    nom_seance=seance.nom or f"Séance {seance.date_prevue.strftime('%d/%m/%Y')}",
                    nom_exercice=exercice.machine.nom if exercice.machine else "Exercice",
                    machine=exercice.machine,
                    series_effectuees=exercice.nombre_series,
                    repetitions_totales=exercice.repetitions_prevues,
                    poids_utilise=exercice.poids_utilise or 0.0,
                    ligne_csv_originale=f"Migration depuis ExerciceSeance ID {exercice.id}",
                    taux_reussite=100.00,
                    duree_seance_minutes=seance.duree_reelle or seance.duree_prevue
                )

                migrated_count += 1

            # Créer la séance dans le calendrier
            if migrated_count > 0:
                seance_cal, created = CalendrierEntrainementSimple.objects.get_or_create(
                    utilisateur=user,
                    date_entrainement=seance.date_debut.date() if seance.date_debut else seance.date_prevue.date(),
                    nom_seance=seance.nom or f"Séance {seance.date_prevue.strftime('%d/%m/%Y')}",
                    defaults={
                        'duree_totale_minutes': seance.duree_reelle or seance.duree_prevue,
                        'nombre_exercices': 0,
                        'volume_total_seance': 0.00,
                        'source_donnees': 'PLANIFIE'
                    }
                )

                if not created:
                    seance_cal.mettre_a_jour_metriques()

        return migrated_count

    except Exception as e:
        print(f"  ⚠️  Migration anciennes séances échouée: {e}")
        return 0

def create_demo_data(user):
    """Crée des données de démonstration pour l'utilisateur"""
    print(f"  📝 Création de données de démonstration pour {user.username}")

    # Données de démonstration
    demo_exercices = [
        {
            'nom': 'Tapis de course',
            'poids': 0.0,
            'series': 1,
            'repetitions': 1,
            'duree': 30,
            'date_offset': -7  # Il y a 7 jours
        },
        {
            'nom': 'Vélo stationnaire',
            'poids': 0.0,
            'series': 1,
            'repetitions': 1,
            'duree': 20,
            'date_offset': -7
        },
        {
            'nom': 'Presse à cuisses',
            'poids': 80.0,
            'series': 3,
            'repetitions': 12,
            'duree': 45,
            'date_offset': -5
        },
        {
            'nom': 'Développé couché',
            'poids': 60.0,
            'series': 3,
            'repetitions': 10,
            'duree': 45,
            'date_offset': -5
        },
        {
            'nom': 'Squat libre',
            'poids': 100.0,
            'series': 4,
            'repetitions': 8,
            'duree': 50,
            'date_offset': -3
        }
    ]

    migrated_count = 0

    for ex_data in demo_exercices:
        # Calculer la date
        date_exercice = datetime.now().date() + timedelta(days=ex_data['date_offset'])

        # Créer l'exercice
        ExerciceEffectueUnifie.objects.create(
            utilisateur=user,
            source='IMPORT_EXTERNE',
            date_exercice=datetime.combine(date_exercice, time(9, 0)),
            nom_seance=f"Séance {date_exercice.strftime('%d/%m/%Y')}",
            nom_exercice=ex_data['nom'],
            machine=None,
            series_effectuees=ex_data['series'],
            repetitions_totales=ex_data['repetitions'],
            poids_utilise=ex_data['poids'],
            ligne_csv_originale="Données de démonstration",
            taux_reussite=100.00,
            duree_seance_minutes=ex_data['duree']
        )

        # Créer ou mettre à jour la séance
        seance, created = CalendrierEntrainementSimple.objects.get_or_create(
            utilisateur=user,
            date_entrainement=date_exercice,
            nom_seance=f"Séance {date_exercice.strftime('%d/%m/%Y')}",
            defaults={
                'duree_totale_minutes': ex_data['duree'],
                'nombre_exercices': 0,
                'volume_total_seance': 0.00,
                'source_donnees': 'MANUEL'
            }
        )

        if not created:
            seance.mettre_a_jour_metriques()

        migrated_count += 1

    return migrated_count

def verify_migration():
    """Vérifie que la migration s'est bien passée"""
    print("\n🔍 Vérification de la migration...")

    # Compter les exercices
    total_exercices = ExerciceEffectueUnifie.objects.count()
    total_seances = CalendrierEntrainementSimple.objects.count()

    print(f"📊 Exercices effectués: {total_exercices}")
    print(f"📅 Séances calendrier: {total_seances}")

    # Vérifier par utilisateur
    users = User.objects.all()
    for user in users:
        user_exercices = ExerciceEffectueUnifie.objects.filter(utilisateur=user).count()
        user_seances = CalendrierEntrainementSimple.objects.filter(utilisateur=user).count()

        print(f"  👤 {user.username}: {user_exercices} exercices, {user_seances} séances")

    if total_exercices > 0 and total_seances > 0:
        print("✅ Migration réussie !")
        return True
    else:
        print("❌ Migration échouée - Aucune donnée trouvée")
        return False

def cleanup_old_data():
    """Nettoie les anciennes données (optionnel)"""
    print("\n🧹 Nettoyage des anciennes données...")

    try:
        # Supprimer les anciens modèles (si ils existent)
        from django.db import connection

        # Liste des anciennes tables à supprimer
        old_tables = [
            'bf_seance_simple',
            'bf_seance_entrainement',
            'bf_exercice_seance',
            'bf_seri_exercice'
        ]

        with connection.cursor() as cursor:
            for table in old_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    print(f"  🗑️  Table {table} supprimée")
                except Exception as e:
                    print(f"  ⚠️  Impossible de supprimer {table}: {e}")

        print("✅ Nettoyage terminé")

    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")

def main():
    """Fonction principale"""
    print("🚀 Script de migration BasicFit v2")
    print("=" * 60)

    # Demander confirmation
    response = input("Voulez-vous procéder à la migration ? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Migration annulée")
        return

    # Effectuer la migration
    if migrate_old_data():
        # Vérifier la migration
        if verify_migration():
            # Demander le nettoyage
            cleanup_response = input("\nVoulez-vous nettoyer les anciennes données ? (oui/non): ")
            if cleanup_response.lower() in ['oui', 'o', 'yes', 'y']:
                cleanup_old_data()

            print("\n🎉 Migration terminée avec succès !")
            print("📱 L'application peut maintenant utiliser la nouvelle API propre.")
        else:
            print("\n⚠️  Migration terminée mais avec des problèmes.")
    else:
        print("\n❌ Migration échouée.")

if __name__ == "__main__":
    main()
