from django.db import migrations

DEFAULT_MACHINES = [
    ("Chest Press", "Travail des pectoraux, triceps et deltoïdes antérieurs", "Assis, pousser les poignées vers l'avant"),
    ("Supine Press", "Press horizontale allongée ciblant la poitrine", "Allongé sur le dos, pousser la barre ou les poignées vers le haut"),
    ("Landmine Shoulder Press", "Renforce les épaules et le haut des pectoraux", "Debout ou à genoux, pousser la barre en diagonale avec une main"),
    ("Cable Lateral Raise", "Isolation des deltoïdes latéraux", "Tirer le câble latéralement bras tendu"),
    ("Pec Deck", "Travail ciblé des pectoraux", "Ramener les bras vers l’avant en position assise"),
    ("Rope Triceps Pushdown", "Isolation des triceps", "Pousser la corde vers le bas en écartant les bras"),
    ("Chin Assist", "Développement des dorsaux et biceps", "Tractions assistées avec les genoux sur la plateforme"),
    ("Cable Row", "Travail du dos (milieu) et des biceps", "Tirer la barre ou poignée vers l’abdomen en position assise"),
    ("Lat Pulldown", "Renforce le dos et les bras", "Tirer la barre vers le haut de la poitrine"),
    ("Face Pull", "Renforcement de l'arrière des épaules et trapèzes", "Tirer la corde vers le visage, coudes hauts"),
    ("EZ Curl Machine", "Isolation des biceps", "Curl guidé en position assise"),
    ("Leg Press", "Renforce quadriceps, fessiers et ischios", "Pousser la plateforme avec les jambes"),
    ("Leg Curl Machine", "Travail des ischios-jambiers", "Plier les jambes vers les fessiers"),
    ("Hip Thrust Machine", "Renforce les fessiers", "Pousser le bassin vers le haut avec support"),
    ("Standing Calf Raise", "Travail des mollets", "Monter sur la pointe des pieds en charge"),
    ("Cable Woodchop", "Renforce les obliques et le tronc", "Tirer le câble en diagonale comme un mouvement de hache"),
    ("Dumbbell Curl (assise)", "Isolation des biceps", "Curl en position assise avec haltères"),
    ("Overhead Rope Extension", "Travail du long triceps", "Extension des bras derrière la tête avec corde"),
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