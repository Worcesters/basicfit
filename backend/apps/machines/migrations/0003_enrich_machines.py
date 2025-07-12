from django.db import migrations

def enrich_machines(apps, schema_editor):
    Machine = apps.get_model('machines', 'Machine')
    Categorie = apps.get_model('machines', 'CategorieMachine')

    # Dictionnaire enrichi : nom -> (instructions, tags, categorie)
    ENRICHED = {
        "Chest Press": (
            "1. Ajustez le siège à hauteur des épaules\n2. Placez le dos bien contre le dossier\n3. Saisissez les poignées, paumes vers le bas\n4. Poussez lentement vers l'avant en contractant les pectoraux\n5. Revenez en position initiale en contrôlant le mouvement\n6. Gardez les coudes légèrement fléchis en fin de mouvement",
            "pectoraux,triceps,deltoides,polyarticulaire,debutant",
            "MUSCULATION"
        ),
        "Supine Press": (
            "1. Allongez-vous sur le banc, pieds au sol\n2. Positionnez la barre au niveau de la poitrine\n3. Prise légèrement plus large que les épaules\n4. Descendez la barre jusqu'à effleurer la poitrine\n5. Remontez en poussant fermement\n6. Gardez les omoplates serrées tout au long du mouvement",
            "pectoraux,force,polyarticulaire,intermediaire",
            "MUSCULATION"
        ),
        "Landmine Shoulder Press": (
            "1. Placez-vous debout face à la barre landmine\n2. Saisissez l'extrémité de la barre d'une main\n3. Positionnez la barre à hauteur d'épaule\n4. Poussez en diagonale vers le haut et l'avant\n5. Contrôlez la descente jusqu'à l'épaule\n6. Alternez les bras entre les séries",
            "epaules,pectoraux,unilateral,intermediaire",
            "MUSCULATION"
        ),
        "Cable Lateral Raise": (
            "1. Placez-vous debout, câble en position basse\n2. Saisissez la poignée avec la main opposée au câble\n3. Bras légèrement fléchi, élevez latéralement\n4. Montez jusqu'à hauteur d'épaule maximum\n5. Redescendez lentement en contrôlant\n6. Gardez le buste droit pendant tout l'exercice",
            "epaules,isolation,deltoides,debout,debutant",
            "MUSCULATION"
        ),
        "Pec Deck": (
            "1. Ajustez le siège pour aligner les coudes aux épaules\n2. Placez le dos contre le dossier\n3. Posez les avant-bras contre les coussinets\n4. Rapprochez les coudes devant la poitrine\n5. Serrez en contractant les pectoraux\n6. Revenez lentement à la position de départ",
            "pectoraux,isolation,debout,debutant",
            "MUSCULATION"
        ),
        "Rope Triceps Pushdown": (
            "1. Fixez la corde en position haute du câble\n2. Tenez-vous debout, coudes le long du corps\n3. Saisissez les extrémités de la corde\n4. Poussez vers le bas en gardant les coudes fixes\n5. Écartez légèrement les mains en bas du mouvement\n6. Remontez en contrôlant jusqu'aux pectoraux",
            "triceps,isolation,cable,debout,debutant",
            "MUSCULATION"
        ),
        "Chin Assist": (
            "1. Ajustez l'assistance selon votre niveau\n2. Placez les genoux sur la plateforme d'assistance\n3. Saisissez la barre, prise supination (paumes vers vous)\n4. Tirez-vous vers le haut jusqu'à dépasser la barre\n5. Descendez lentement en contrôlant\n6. Gardez le tronc gainé pendant tout l'exercice",
            "dos,biceps,assiste,traction,debout,debutant",
            "MUSCULATION"
        ),
        "Cable Row": (
            "1. Asseyez-vous face au câble, jambes légèrement fléchies\n2. Saisissez la barre ou poignée, bras tendus\n3. Tirez vers l'abdomen en serrant les omoplates\n4. Gardez le dos droit, poitrine sortie\n5. Contrôlez le retour en extension\n6. Ne vous penchez pas vers l'avant en fin de mouvement",
            "dos,biceps,row,assise,intermediaire",
            "MUSCULATION"
        ),
        "Lat Pulldown": (
            "1. Ajustez le cale-cuisses pour être bien maintenu\n2. Saisissez la barre avec une prise large\n3. Penchez-vous légèrement vers l'arrière\n4. Tirez la barre vers le haut de la poitrine\n5. Serrez les dorsaux en bas du mouvement\n6. Remontez lentement en gardant la tension",
            "dos,dorsaux,traction,assise,debutant",
            "MUSCULATION"
        ),
        "Face Pull": (
            "1. Réglez le câble à hauteur du visage\n2. Saisissez la corde avec les deux mains\n3. Reculez pour tendre le câble\n4. Tirez vers le visage en écartant les coudes\n5. Visez entre les yeux et le front\n6. Serrez les omoplates en fin de mouvement",
            "epaules,trapèzes,arriere,deltoides,cable,intermediaire",
            "MUSCULATION"
        ),
        "EZ Curl Machine": (
            "1. Ajustez le siège selon votre taille\n2. Placez les bras sur le pupitre\n3. Saisissez la barre EZ, prise naturelle\n4. Fléchissez lentement en contractant les biceps\n5. Montez jusqu'à la contraction maximale\n6. Redescendez en contrôlant, sans verrouiller complètement",
            "biceps,isolation,assise,debutant",
            "MUSCULATION"
        ),
        "Leg Press": (
            "1. Installez-vous sur la machine, dos contre le dossier\n2. Placez les pieds largeur d'épaules sur la plateforme\n3. Descendez en fléchissant les genoux à 90°\n4. Poussez en utilisant les talons\n5. Remontez sans verrouiller complètement les genoux\n6. Gardez les genoux alignés avec les pieds",
            "jambes,quadriceps,fessiers,polyarticulaire,intermediaire",
            "MUSCULATION"
        ),
        "Leg Curl Machine": (
            "1. Allongez-vous face contre la machine\n2. Placez les chevilles sous les boudins\n3. Agrippez les poignées pour vous stabiliser\n4. Fléchissez les jambes vers les fessiers\n5. Contractez bien les ischios en haut\n6. Redescendez lentement sans relâcher la tension",
            "ischios,jambiers,isolation,allonge,debutant",
            "MUSCULATION"
        ),
        "Hip Thrust Machine": (
            "1. Positionnez-vous dos contre le banc\n2. Placez la barre sur les hanches avec un coussin\n3. Pieds à plat, largeur d'épaules\n4. Poussez le bassin vers le haut en contractant les fessiers\n5. Alignez hanches, genoux et épaules en haut\n6. Redescendez en contrôlant sans poser complètement",
            "fessiers,glutes,force,polyarticulaire,intermediaire",
            "MUSCULATION"
        ),
        "Standing Calf Raise": (
            "1. Placez-vous debout sur la machine\n2. Positionnez les épaules sous les coussinets\n3. Avant-pieds sur la plateforme, talons dans le vide\n4. Montez sur la pointe des pieds le plus haut possible\n5. Marquez un temps d'arrêt en contraction\n6. Redescendez lentement en étirant les mollets",
            "mollets,calves,debout,isolation,debutant",
            "MUSCULATION"
        ),
        "Cable Woodchop": (
            "1. Réglez le câble en position haute\n2. Placez-vous de côté par rapport au câble\n3. Saisissez la poignée à deux mains\n4. Tirez en diagonale vers la hanche opposée\n5. Pivotez le tronc en gardant les bras tendus\n6. Contrôlez le retour et alternez les côtés",
            "abdos,obliques,rotation,cable,intermediaire",
            "MUSCULATION"
        ),
        "Dumbbell Curl (assise)": (
            "1. Asseyez-vous sur un banc, dos droit\n2. Tenez un haltère dans chaque main\n3. Bras le long du corps, paumes vers l'avant\n4. Fléchissez alternativement en contractant les biceps\n5. Montez jusqu'à l'épaule sans bouger le coude\n6. Redescendez lentement en contrôlant",
            "biceps,haltères,assise,isolation,debutant",
            "MUSCULATION"
        ),
        "Overhead Rope Extension": (
            "1. Fixez la corde en position haute\n2. Tournez le dos au câble, saisissez la corde\n3. Inclinez-vous légèrement vers l'avant\n4. Étendez les bras au-dessus de la tête\n5. Fléchissez uniquement aux coudes\n6. Remontez en gardant les coudes fixes",
            "triceps,overhead,cable,isolation,intermediaire",
            "MUSCULATION"
        ),
    }

    for nom, (instructions, tags, categorie_nom) in ENRICHED.items():
        try:
            machine = Machine.objects.get(nom=nom)
            cat = Categorie.objects.get(nom=categorie_nom)
            machine.instructions = instructions
            machine.tags = tags
            machine.categorie = cat
            machine.save()
        except Exception as e:
            print(f"Erreur pour {nom}: {e}")


def reverse_enrich_machines(apps, schema_editor):
    # Pas de reverse, on ne supprime pas les enrichissements
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("machines", "0002_add_default_machines"),
    ]
    operations = [
        migrations.RunPython(enrich_machines, reverse_enrich_machines),
    ]