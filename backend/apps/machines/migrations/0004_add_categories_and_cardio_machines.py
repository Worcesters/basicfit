from django.db import migrations

def add_categories_and_machines(apps, schema_editor):
    Categorie = apps.get_model('machines', 'CategorieMachine')
    Machine = apps.get_model('machines', 'Machine')
    GroupeMusculaire = apps.get_model('machines', 'GroupeMusculaire')

    # Créer ou récupérer les catégories
    categories = {}
    for nom, display_name, couleur, icone in [
        ('MUSCULATION', 'Musculation', '#e74c3c', '💪'),
        ('CABLE', 'Câble', '#3498db', '🔗'),
        ('CARDIO', 'Cardio', '#2ecc71', '🏃'),
        ('POIDS_LIBRE', 'Poids libre', '#f39c12', '🏋️'),
        ('MACHINE_GUIDEE', 'Machine guidée', '#9b59b6', '⚙️'),
        ('FONCTIONNEL', 'Fonctionnel', '#34495e', '🤸'),
    ]:
        cat, created = Categorie.objects.get_or_create(
            nom=nom,
            defaults={
                'description': f'Machines de {display_name.lower()}',
                'couleur': couleur,
                'icone': icone,
            }
        )
        categories[nom] = cat

    # Créer ou récupérer les groupes musculaires
    groupes = {}
    for nom, couleur in [
        ('Pectoraux', '#e74c3c'),
        ('Dos', '#3498db'),
        ('Épaules', '#f39c12'),
        ('Biceps', '#9b59b6'),
        ('Triceps', '#1abc9c'),
        ('Quadriceps', '#27ae60'),
        ('Ischio-jambiers', '#e67e22'),
        ('Fessiers', '#8e44ad'),
        ('Mollets', '#16a085'),
        ('Abdos', '#e74c3c'),
        ('Cardio', '#2ecc71'),
    ]:
        groupe, created = GroupeMusculaire.objects.get_or_create(
            nom=nom,
            defaults={'couleur': couleur}
        )
        groupes[nom] = groupe

    # Machines existantes avec catégories multiples
    MACHINES_MULTI_CATEGORIES = {
        "Cable Lateral Raise": {
            'instructions': "1. Placez-vous debout, câble en position basse\n2. Saisissez la poignée avec la main opposée au câble\n3. Bras légèrement fléchi, élevez latéralement\n4. Montez jusqu'à hauteur d'épaule maximum\n5. Redescendez lentement en contrôlant\n6. Gardez le buste droit pendant tout l'exercice",
            'description': "Isolation des deltoïdes latéraux avec câble",
            'tags': "epaules,isolation,deltoides,cable,debout,debutant",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Épaules'],
            'groupes_secondaires': ['Dos'],
            'niveau': 'DEBUTANT',
            'poids_min': 5.0,
            'poids_max': 50.0,
        },
        "Rope Triceps Pushdown": {
            'instructions': "1. Fixez la corde en position haute du câble\n2. Tenez-vous debout, coudes le long du corps\n3. Saisissez les extrémités de la corde\n4. Poussez vers le bas en gardant les coudes fixes\n5. Écartez légèrement les mains en bas du mouvement\n6. Remontez en contrôlant jusqu'aux pectoraux",
            'description': "Isolation des triceps avec corde",
            'tags': "triceps,isolation,cable,debout,debutant",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Triceps'],
            'groupes_secondaires': ['Épaules'],
            'niveau': 'DEBUTANT',
            'poids_min': 5.0,
            'poids_max': 80.0,
        },
        "Cable Row": {
            'instructions': "1. Asseyez-vous face au câble, jambes légèrement fléchies\n2. Saisissez la barre ou poignée, bras tendus\n3. Tirez vers l'abdomen en serrant les omoplates\n4. Gardez le dos droit, poitrine sortie\n5. Contrôlez le retour en extension\n6. Ne vous penchez pas vers l'avant en fin de mouvement",
            'description': "Travail du dos (milieu) et des biceps",
            'tags': "dos,biceps,row,cable,assise,intermediaire",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Dos'],
            'groupes_secondaires': ['Biceps'],
            'niveau': 'INTERMEDIAIRE',
            'poids_min': 10.0,
            'poids_max': 120.0,
        },
        "Face Pull": {
            'instructions': "1. Réglez le câble à hauteur du visage\n2. Saisissez la corde avec les deux mains\n3. Reculez pour tendre le câble\n4. Tirez vers le visage en écartant les coudes\n5. Visez entre les yeux et le front\n6. Serrez les omoplates en fin de mouvement",
            'description': "Renforcement de l'arrière des épaules et trapèzes",
            'tags': "epaules,trapèzes,arriere,deltoides,cable,intermediaire",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Épaules'],
            'groupes_secondaires': ['Dos'],
            'niveau': 'INTERMEDIAIRE',
            'poids_min': 5.0,
            'poids_max': 40.0,
        },
        "Cable Woodchop": {
            'instructions': "1. Réglez le câble en position haute\n2. Placez-vous de côté par rapport au câble\n3. Saisissez la poignée à deux mains\n4. Tirez en diagonale vers la hanche opposée\n5. Pivotez le tronc en gardant les bras tendus\n6. Contrôlez le retour et alternez les côtés",
            'description': "Renforce les obliques et le tronc",
            'tags': "abdos,obliques,rotation,cable,intermediaire",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Abdos'],
            'groupes_secondaires': ['Épaules'],
            'niveau': 'INTERMEDIAIRE',
            'poids_min': 5.0,
            'poids_max': 60.0,
        },
        "Overhead Rope Extension": {
            'instructions': "1. Fixez la corde en position haute\n2. Tournez le dos au câble, saisissez la corde\n3. Inclinez-vous légèrement vers l'avant\n4. Étendez les bras au-dessus de la tête\n5. Fléchissez uniquement aux coudes\n6. Remontez en gardant les coudes fixes",
            'description': "Travail du long triceps",
            'tags': "triceps,overhead,cable,isolation,intermediaire",
            'categories': ['MUSCULATION', 'CABLE'],
            'groupes_primaires': ['Triceps'],
            'groupes_secondaires': ['Épaules'],
            'niveau': 'INTERMEDIAIRE',
            'poids_min': 5.0,
            'poids_max': 50.0,
        },
    }

    # Nouvelles machines cardio
    MACHINES_CARDIO = {
        "Vélo elliptique": {
            'instructions': "1. Montez sur la machine et saisissez les poignées\n2. Réglez la résistance selon votre niveau\n3. Alternez les mouvements de pédalage et de bras\n4. Gardez le dos droit et les abdos contractés\n5. Maintenez un rythme régulier\n6. Hydratez-vous régulièrement pendant l'effort",
            'description': "Cardio complet sollicitant jambes et bras",
            'tags': "cardio,elliptique,complet,debutant",
            'categories': ['CARDIO'],
            'groupes_primaires': ['Cardio'],
            'groupes_secondaires': ['Quadriceps', 'Fessiers'],
            'niveau': 'DEBUTANT',
            'poids_min': 0.0,
            'poids_max': 0.0,
        },
        "Tapis de course": {
            'instructions': "1. Montez sur le tapis et démarrez à vitesse lente\n2. Augmentez progressivement la vitesse\n3. Gardez une posture droite, regardez devant vous\n4. Posez le pied du talon vers la pointe\n5. Balancez naturellement les bras\n6. Hydratez-vous et respirez régulièrement",
            'description': "Course à pied en intérieur",
            'tags': "cardio,course,pied,debutant",
            'categories': ['CARDIO'],
            'groupes_primaires': ['Cardio'],
            'groupes_secondaires': ['Quadriceps', 'Ischio-jambiers'],
            'niveau': 'DEBUTANT',
            'poids_min': 0.0,
            'poids_max': 0.0,
        },
        "Rameur": {
            'instructions': "1. Asseyez-vous et attachez vos pieds\n2. Saisissez la poignée, dos droit\n3. Commencez par pousser avec les jambes\n4. Puis tirez avec le dos et les bras\n5. Revenez en sens inverse : bras, dos, jambes\n6. Gardez un mouvement fluide et contrôlé",
            'description': "Cardio complet sollicitant tout le corps",
            'tags': "cardio,rameur,complet,intermediaire",
            'categories': ['CARDIO'],
            'groupes_primaires': ['Cardio'],
            'groupes_secondaires': ['Dos', 'Biceps'],
            'niveau': 'INTERMEDIAIRE',
            'poids_min': 0.0,
            'poids_max': 0.0,
        },
        "Vélo stationnaire": {
            'instructions': "1. Ajustez la hauteur de selle et du guidon\n2. Réglez la résistance selon votre niveau\n3. Placez vos pieds sur les pédales\n4. Gardez le dos droit et les abdos contractés\n5. Maintenez un rythme régulier\n6. Hydratez-vous pendant l'effort",
            'description': "Cardio ciblant principalement les jambes",
            'tags': "cardio,velo,jambes,debutant",
            'categories': ['CARDIO'],
            'groupes_primaires': ['Cardio'],
            'groupes_secondaires': ['Quadriceps', 'Fessiers'],
            'niveau': 'DEBUTANT',
            'poids_min': 0.0,
            'poids_max': 0.0,
        },
        "Stepper": {
            'instructions': "1. Montez sur la machine et saisissez les poignées\n2. Réglez la résistance selon votre niveau\n3. Alternez les mouvements de montée/descente\n4. Gardez le dos droit et les abdos contractés\n5. Maintenez un rythme régulier\n6. Hydratez-vous régulièrement",
            'description': "Simulation d'escaliers pour cardio",
            'tags': "cardio,stepper,escaliers,debutant",
            'categories': ['CARDIO'],
            'groupes_primaires': ['Cardio'],
            'groupes_secondaires': ['Quadriceps', 'Fessiers'],
            'niveau': 'DEBUTANT',
            'poids_min': 0.0,
            'poids_max': 0.0,
        },
    }

    # Mettre à jour les machines existantes avec catégories multiples
    for nom, data in MACHINES_MULTI_CATEGORIES.items():
        try:
            machine = Machine.objects.get(nom=nom)
            # Mettre à jour les instructions et tags
            machine.instructions = data['instructions']
            machine.tags = data['tags']
            machine.description = data['description']
            machine.niveau_difficulte = data['niveau']
            machine.poids_minimum = data['poids_min']
            machine.poids_maximum = data['poids_max']

            # Mettre à jour la catégorie principale (première de la liste)
            machine.categorie = categories[data['categories'][0]]
            machine.save()

            # Ajouter les groupes musculaires
            machine.groupes_musculaires_primaires.clear()
            for groupe_nom in data['groupes_primaires']:
                machine.groupes_musculaires_primaires.add(groupes[groupe_nom])

            machine.groupes_musculaires_secondaires.clear()
            for groupe_nom in data['groupes_secondaires']:
                machine.groupes_musculaires_secondaires.add(groupes[groupe_nom])

        except Machine.DoesNotExist:
            print(f"Machine {nom} non trouvée")

    # Créer les nouvelles machines cardio
    for nom, data in MACHINES_CARDIO.items():
        machine, created = Machine.objects.get_or_create(
            nom=nom,
            defaults={
                'description': data['description'],
                'instructions': data['instructions'],
                'categorie': categories['CARDIO'],
                'niveau_difficulte': data['niveau'],
                'poids_minimum': data['poids_min'],
                'poids_maximum': data['poids_max'],
                'tags': data['tags'],
                'est_disponible': True,
                'popularite': 70,
            }
        )

        if created:
            # Ajouter les groupes musculaires
            for groupe_nom in data['groupes_primaires']:
                machine.groupes_musculaires_primaires.add(groupes[groupe_nom])
            for groupe_nom in data['groupes_secondaires']:
                machine.groupes_musculaires_secondaires.add(groupes[groupe_nom])


def reverse_add_categories_and_machines(apps, schema_editor):
    # Supprimer les nouvelles machines cardio
    Machine = apps.get_model('machines', 'Machine')
    cardio_machines = [
        "Vélo elliptique", "Tapis de course", "Rameur",
        "Vélo stationnaire", "Stepper"
    ]
    Machine.objects.filter(nom__in=cardio_machines).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("machines", "0003_enrich_machines"),
    ]
    operations = [
        migrations.RunPython(add_categories_and_machines, reverse_add_categories_and_machines),
    ]