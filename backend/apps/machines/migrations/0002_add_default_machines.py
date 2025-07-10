from django.db import migrations

DEFAULT_MACHINES = [
    ("Chest Press", "Travail des pectoraux, triceps et deltoïdes antérieurs", "1. Ajustez le siège à hauteur des épaules\n2. Placez le dos bien contre le dossier\n3. Saisissez les poignées, paumes vers le bas\n4. Poussez lentement vers l'avant en contractant les pectoraux\n5. Revenez en position initiale en contrôlant le mouvement\n6. Gardez les coudes légèrement fléchis en fin de mouvement"),
    ("Supine Press", "Press horizontale allongée ciblant la poitrine", "1. Allongez-vous sur le banc, pieds au sol\n2. Positionnez la barre au niveau de la poitrine\n3. Prise légèrement plus large que les épaules\n4. Descendez la barre jusqu'à effleurer la poitrine\n5. Remontez en poussant fermement\n6. Gardez les omoplates serrées tout au long du mouvement"),
    ("Landmine Shoulder Press", "Renforce les épaules et le haut des pectoraux", "1. Placez-vous debout face à la barre landmine\n2. Saisissez l'extrémité de la barre d'une main\n3. Positionnez la barre à hauteur d'épaule\n4. Poussez en diagonale vers le haut et l'avant\n5. Contrôlez la descente jusqu'à l'épaule\n6. Alternez les bras entre les séries"),
    ("Cable Lateral Raise", "Isolation des deltoïdes latéraux", "1. Placez-vous debout, câble en position basse\n2. Saisissez la poignée avec la main opposée au câble\n3. Bras légèrement fléchi, élevez latéralement\n4. Montez jusqu'à hauteur d'épaule maximum\n5. Redescendez lentement en contrôlant\n6. Gardez le buste droit pendant tout l'exercice"),
    ("Pec Deck", "Travail ciblé des pectoraux", "1. Ajustez le siège pour aligner les coudes aux épaules\n2. Placez le dos contre le dossier\n3. Posez les avant-bras contre les coussinets\n4. Rapprochez les coudes devant la poitrine\n5. Serrez en contractant les pectoraux\n6. Revenez lentement à la position de départ"),
    ("Rope Triceps Pushdown", "Isolation des triceps", "1. Fixez la corde en position haute du câble\n2. Tenez-vous debout, coudes le long du corps\n3. Saisissez les extrémités de la corde\n4. Poussez vers le bas en gardant les coudes fixes\n5. Écartez légèrement les mains en bas du mouvement\n6. Remontez en contrôlant jusqu'aux pectoraux"),
    ("Chin Assist", "Développement des dorsaux et biceps", "1. Ajustez l'assistance selon votre niveau\n2. Placez les genoux sur la plateforme d'assistance\n3. Saisissez la barre, prise supination (paumes vers vous)\n4. Tirez-vous vers le haut jusqu'à dépasser la barre\n5. Descendez lentement en contrôlant\n6. Gardez le tronc gainé pendant tout l'exercice"),
    ("Cable Row", "Travail du dos (milieu) et des biceps", "1. Asseyez-vous face au câble, jambes légèrement fléchies\n2. Saisissez la barre ou poignée, bras tendus\n3. Tirez vers l'abdomen en serrant les omoplates\n4. Gardez le dos droit, poitrine sortie\n5. Contrôlez le retour en extension\n6. Ne vous penchez pas vers l'avant en fin de mouvement"),
    ("Lat Pulldown", "Renforce le dos et les bras", "1. Ajustez le cale-cuisses pour être bien maintenu\n2. Saisissez la barre avec une prise large\n3. Penchez-vous légèrement vers l'arrière\n4. Tirez la barre vers le haut de la poitrine\n5. Serrez les dorsaux en bas du mouvement\n6. Remontez lentement en gardant la tension"),
    ("Face Pull", "Renforcement de l'arrière des épaules et trapèzes", "1. Réglez le câble à hauteur du visage\n2. Saisissez la corde avec les deux mains\n3. Reculez pour tendre le câble\n4. Tirez vers le visage en écartant les coudes\n5. Visez entre les yeux et le front\n6. Serrez les omoplates en fin de mouvement"),
    ("EZ Curl Machine", "Isolation des biceps", "1. Ajustez le siège selon votre taille\n2. Placez les bras sur le pupitre\n3. Saisissez la barre EZ, prise naturelle\n4. Fléchissez lentement en contractant les biceps\n5. Montez jusqu'à la contraction maximale\n6. Redescendez en contrôlant, sans verrouiller complètement"),
    ("Leg Press", "Renforce quadriceps, fessiers et ischios", "1. Installez-vous sur la machine, dos contre le dossier\n2. Placez les pieds largeur d'épaules sur la plateforme\n3. Descendez en fléchissant les genoux à 90°\n4. Poussez en utilisant les talons\n5. Remontez sans verrouiller complètement les genoux\n6. Gardez les genoux alignés avec les pieds"),
    ("Leg Curl Machine", "Travail des ischios-jambiers", "1. Allongez-vous face contre la machine\n2. Placez les chevilles sous les boudins\n3. Agrippez les poignées pour vous stabiliser\n4. Fléchissez les jambes vers les fessiers\n5. Contractez bien les ischios en haut\n6. Redescendez lentement sans relâcher la tension"),
    ("Hip Thrust Machine", "Renforce les fessiers", "1. Positionnez-vous dos contre le banc\n2. Placez la barre sur les hanches avec un coussin\n3. Pieds à plat, largeur d'épaules\n4. Poussez le bassin vers le haut en contractant les fessiers\n5. Alignez hanches, genoux et épaules en haut\n6. Redescendez en contrôlant sans poser complètement"),
    ("Standing Calf Raise", "Travail des mollets", "1. Placez-vous debout sur la machine\n2. Positionnez les épaules sous les coussinets\n3. Avant-pieds sur la plateforme, talons dans le vide\n4. Montez sur la pointe des pieds le plus haut possible\n5. Marquez un temps d'arrêt en contraction\n6. Redescendez lentement en étirant les mollets"),
    ("Cable Woodchop", "Renforce les obliques et le tronc", "1. Réglez le câble en position haute\n2. Placez-vous de côté par rapport au câble\n3. Saisissez la poignée à deux mains\n4. Tirez en diagonale vers la hanche opposée\n5. Pivotez le tronc en gardant les bras tendus\n6. Contrôlez le retour et alternez les côtés"),
    ("Dumbbell Curl (assise)", "Isolation des biceps", "1. Asseyez-vous sur un banc, dos droit\n2. Tenez un haltère dans chaque main\n3. Bras le long du corps, paumes vers l'avant\n4. Fléchissez alternativement en contractant les biceps\n5. Montez jusqu'à l'épaule sans bouger le coude\n6. Redescendez lentement en contrôlant"),
    ("Overhead Rope Extension", "Travail du long triceps", "1. Fixez la corde en position haute\n2. Tournez le dos au câble, saisissez la corde\n3. Inclinez-vous légèrement vers l'avant\n4. Étendez les bras au-dessus de la tête\n5. Fléchissez uniquement aux coudes\n6. Remontez en gardant les coudes fixes"),
]


def add_default_machines(apps, schema_editor):
    Categorie = apps.get_model("machines", "CategorieMachine")
    Machine = apps.get_model("machines", "Machine")

    # Récupère ou crée la catégorie MUSCULATION
    cat, _ = Categorie.objects.get_or_create(
        nom="MUSCULATION",
        defaults={
            "description": "Machines de musculation",
            "couleur": "#00C9A7",
        },
    )

    for nom, desc, util in DEFAULT_MACHINES:
        Machine.objects.update_or_create(
            nom=nom,
            defaults={
                "description": desc,
                "instructions": util,
                "categorie": cat,
            },
        )


def remove_default_machines(apps, schema_editor):
    Machine = apps.get_model("machines", "Machine")
    Machine.objects.filter(nom__in=[m[0] for m in DEFAULT_MACHINES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("machines", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_default_machines, remove_default_machines),
    ]