# Generated manually on 2025-01-27

from django.db import migrations
from django.utils import timezone


def add_new_machines(apps, schema_editor):
    Machine = apps.get_model('machines', 'Machine')
    CategorieMachine = apps.get_model('machines', 'CategorieMachine')
    GroupeMusculaire = apps.get_model('machines', 'GroupeMusculaire')

    # Récupérer la catégorie "Machine guidée"
    machine_guidee = CategorieMachine.objects.get(nom="MACHINE_GUIDEE")

    # Récupérer ou créer le groupe musculaire "Bras"
    bras, created = GroupeMusculaire.objects.get_or_create(
        nom="Bras",
        defaults={
            'description': "Muscles des bras (biceps, triceps)",
            'couleur': "#e74c3c",
            'icone': "💪",
            'ordre_affichage': 5
        }
    )

        # Ajouter Seated Triceps Press
    seated_triceps = Machine.objects.create(
        nom="Seated Triceps Press",
        nom_anglais="Seated Triceps Press",
        description="Machine guidée pour l'isolation des triceps en position assise",
        instructions="Assis sur la machine, placez vos avant-bras sur les coussinets et étendez les coudes en contractant les triceps. Gardez le dos droit et les coudes fixes.",
        categorie=machine_guidee,
        increment_poids=2.5,
        poids_minimum=10.0,
        poids_maximum=80.0,
        niveau_difficulte="DEBUTANT",
        popularite=75,
        est_disponible=True,
        necessite_supervision=False,
        tags="triceps,bras,isolation,machine guidée,assise"
    )
    seated_triceps.groupes_musculaires_primaires.add(bras)

    # Ajouter Dip Assist
    dip_assist = Machine.objects.create(
        nom="Dip Assist",
        nom_anglais="Dip Assist",
        description="Machine assistée pour les dips, permettant de travailler les triceps et pectoraux",
        instructions="Placez vos genoux sur la plateforme et vos mains sur les barres parallèles. Descendez en fléchissant les coudes puis remontez en poussant sur les triceps et pectoraux.",
        categorie=machine_guidee,
        increment_poids=5.0,
        poids_minimum=20.0,
        poids_maximum=150.0,
        niveau_difficulte="INTERMEDIAIRE",
        popularite=70,
        est_disponible=True,
        necessite_supervision=False,
        tags="triceps,pectoraux,dips,assisté,polyarticulaire"
    )
    dip_assist.groupes_musculaires_primaires.add(bras)


def remove_new_machines(apps, schema_editor):
    Machine = apps.get_model('machines', 'Machine')
    Machine.objects.filter(nom__in=["Seated Triceps Press", "Dip Assist"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('machines', '0006_remove_machinecategorie_machines_mac_machine_123456_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(add_new_machines, remove_new_machines),
    ]