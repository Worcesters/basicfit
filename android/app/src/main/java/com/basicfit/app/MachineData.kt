package com.basicfit.app

// Data classes pour le système de machines et d'entraînements

data class Machine(
    val id: Int,
    val nom: String,
    val nomAnglais: String = "",
    val description: String,
    val instructions: String,
    val categorie: CategorieMachine,
    val groupeMusculairePrimaire: String,
    val incrementPoids: Double = 2.5,
    val poidsMinimum: Double = 5.0,
    val poidsMaximum: Double = 200.0,
    val niveauDifficulte: NiveauDifficulte = NiveauDifficulte.DEBUTANT,
    val popularite: Int = 0,
    val estDisponible: Boolean = true,
    val necessite_supervision: Boolean = false,
    val tags: List<String> = emptyList()
)

enum class CategorieMachine(val displayName: String, val couleur: String, val icone: String) {
    MUSCULATION("Musculation", "#e74c3c", "💪"),
    CARDIO("Cardio", "#3498db", "🏃"),
    CABLE("Câble", "#2ecc71", "🔗"),
    POIDS_LIBRE("Poids libre", "#f39c12", "🏋️"),
    MACHINE_GUIDEE("Machine guidée", "#9b59b6", "⚙️"),
    FONCTIONNEL("Fonctionnel", "#34495e", "🤸")
}

enum class NiveauDifficulte(val displayName: String) {
    DEBUTANT("Débutant"),
    INTERMEDIAIRE("Intermédiaire"),
    AVANCE("Avancé"),
    EXPERT("Expert")
}

data class ModeEntrainement(
    val id: Int,
    val nom: String,
    val description: String,
    val seriesRecommandees: Int,
    val repetitionsMin: Int,
    val repetitionsMax: Int,
    val reposEntreSeries: Int, // en secondes
    val couleur: String
)

data class ExerciceSeance(
    val id: Int,
    val machine: Machine,
    val mode: ModeEntrainement,
    val seriesPrevues: Int,
    val repetitionsPrevues: Int,
    val poidsPrevue: Double,
    val reposPrevue: Int,
    val ordreSeance: Int = 1
)

// Objet contenant toutes les données des machines
object MachineData {

    // Modes d'entraînement
    val modes = listOf(
        ModeEntrainement(
            id = 1,
            nom = "Force",
            description = "Entraînement orienté force avec charges lourdes et peu de répétitions",
            seriesRecommandees = 5,
            repetitionsMin = 1,
            repetitionsMax = 5,
            reposEntreSeries = 180,
            couleur = "#e74c3c"
        ),
        ModeEntrainement(
            id = 2,
            nom = "Prise de masse",
            description = "Entraînement pour la prise de masse musculaire avec volume modéré",
            seriesRecommandees = 3,
            repetitionsMin = 8,
            repetitionsMax = 12,
            reposEntreSeries = 90,
            couleur = "#3498db"
        ),
        ModeEntrainement(
            id = 3,
            nom = "Sèche",
            description = "Entraînement pour la sèche avec hautes répétitions",
            seriesRecommandees = 4,
            repetitionsMin = 12,
            repetitionsMax = 20,
            reposEntreSeries = 60,
            couleur = "#2ecc71"
        ),
        ModeEntrainement(
            id = 4,
            nom = "Endurance",
            description = "Développement de l'endurance musculaire",
            seriesRecommandees = 3,
            repetitionsMin = 15,
            repetitionsMax = 25,
            reposEntreSeries = 45,
            couleur = "#f39c12"
        )
    )

    // Machines disponibles
    val machines = listOf(
        // PECTORAUX
        Machine(
            id = 1,
            nom = "Développé couché",
            nomAnglais = "Bench Press",
            description = "Exercice de base pour les pectoraux, épaules et triceps",
            instructions = "Allongez-vous sur le banc, pieds au sol. Saisissez la barre avec une prise légèrement plus large que les épaules. Descendez la barre jusqu'à la poitrine puis remontez en contrôlant le mouvement.",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Pectoraux",
            incrementPoids = 2.5,
            poidsMinimum = 20.0,
            poidsMaximum = 200.0,
            niveauDifficulte = NiveauDifficulte.INTERMEDIAIRE,
            popularite = 95,
            tags = listOf("pectoraux", "triceps", "épaules", "base", "polyarticulaire")
        ),
        Machine(
            id = 2,
            nom = "Développé incliné",
            nomAnglais = "Incline Bench Press",
            description = "Variante du développé couché pour cibler le haut des pectoraux",
            instructions = "Même technique que le développé couché sur un banc incliné à 30-45°",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Pectoraux",
            incrementPoids = 2.5,
            poidsMinimum = 15.0,
            poidsMaximum = 150.0,
            niveauDifficulte = NiveauDifficulte.INTERMEDIAIRE,
            popularite = 80,
            tags = listOf("pectoraux", "haut pectoraux", "épaules")
        ),
        Machine(
            id = 3,
            nom = "Pec Deck",
            nomAnglais = "Pec Deck",
            description = "Machine d'isolation pour les pectoraux",
            instructions = "Assis sur la machine, placez vos avant-bras contre les coussinets et rapprochez-les devant vous",
            categorie = CategorieMachine.MACHINE_GUIDEE,
            groupeMusculairePrimaire = "Pectoraux",
            incrementPoids = 5.0,
            poidsMinimum = 10.0,
            poidsMaximum = 100.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 70,
            tags = listOf("pectoraux", "isolation", "sécurisé")
        ),

        // DOS
        Machine(
            id = 4,
            nom = "Tirage vertical",
            nomAnglais = "Lat Pulldown",
            description = "Exercice pour développer la largeur du dos",
            instructions = "Asseyez-vous face à la machine, saisissez la barre avec une prise large. Tirez la barre vers le haut de la poitrine en contractant les dorsaux.",
            categorie = CategorieMachine.MACHINE_GUIDEE,
            groupeMusculairePrimaire = "Dos",
            incrementPoids = 2.5,
            poidsMinimum = 10.0,
            poidsMaximum = 150.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 85,
            tags = listOf("dos", "dorsaux", "largeur", "traction")
        ),
        Machine(
            id = 5,
            nom = "Rowing assis",
            nomAnglais = "Seated Row",
            description = "Exercice pour l'épaisseur du dos",
            instructions = "Assis sur la machine, tirez la poignée vers votre abdomen en contractant les dorsaux",
            categorie = CategorieMachine.CABLE,
            groupeMusculairePrimaire = "Dos",
            incrementPoids = 2.5,
            poidsMinimum = 15.0,
            poidsMaximum = 120.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 80,
            tags = listOf("dos", "dorsaux", "épaisseur", "rowing")
        ),
        Machine(
            id = 6,
            nom = "Tractions",
            nomAnglais = "Pull-ups",
            description = "Exercice au poids du corps pour le dos",
            instructions = "Suspendez-vous à la barre et tirez votre corps vers le haut jusqu'à ce que votre menton dépasse la barre",
            categorie = CategorieMachine.FONCTIONNEL,
            groupeMusculairePrimaire = "Dos",
            incrementPoids = 0.0,
            poidsMinimum = 0.0,
            poidsMaximum = 50.0, // poids assisté
            niveauDifficulte = NiveauDifficulte.AVANCE,
            popularite = 90,
            tags = listOf("dos", "poids du corps", "fonctionnel", "difficile")
        ),

        // JAMBES
        Machine(
            id = 7,
            nom = "Leg Press",
            nomAnglais = "Leg Press",
            description = "Machine pour développer les quadriceps et fessiers",
            instructions = "Placez-vous sur la machine, pieds sur la plateforme largeur d'épaules. Descendez en fléchissant les genoux puis remontez en poussant sur les talons.",
            categorie = CategorieMachine.MACHINE_GUIDEE,
            groupeMusculairePrimaire = "Jambes",
            incrementPoids = 10.0,
            poidsMinimum = 50.0,
            poidsMaximum = 500.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 90,
            tags = listOf("quadriceps", "fessiers", "jambes", "sécurisé")
        ),
        Machine(
            id = 8,
            nom = "Squat",
            nomAnglais = "Squat",
            description = "Exercice roi pour les jambes et fessiers",
            instructions = "Debout, barre sur les épaules, descendez en fléchissant hanches et genoux puis remontez",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Jambes",
            incrementPoids = 5.0,
            poidsMinimum = 20.0,
            poidsMaximum = 300.0,
            niveauDifficulte = NiveauDifficulte.INTERMEDIAIRE,
            popularite = 95,
            necessite_supervision = true,
            tags = listOf("jambes", "fessiers", "quadriceps", "roi", "polyarticulaire")
        ),
        Machine(
            id = 9,
            nom = "Extension quadriceps",
            nomAnglais = "Leg Extension",
            description = "Isolation des quadriceps",
            instructions = "Assis sur la machine, étendez les jambes en contractant les quadriceps",
            categorie = CategorieMachine.MACHINE_GUIDEE,
            groupeMusculairePrimaire = "Jambes",
            incrementPoids = 2.5,
            poidsMinimum = 10.0,
            poidsMaximum = 100.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 75,
            tags = listOf("quadriceps", "isolation", "jambes")
        ),
        Machine(
            id = 10,
            nom = "Curl ischios",
            nomAnglais = "Leg Curl",
            description = "Isolation des ischio-jambiers",
            instructions = "Allongé sur la machine, fléchissez les jambes en contractant les ischio-jambiers",
            categorie = CategorieMachine.MACHINE_GUIDEE,
            groupeMusculairePrimaire = "Jambes",
            incrementPoids = 2.5,
            poidsMinimum = 10.0,
            poidsMaximum = 80.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 70,
            tags = listOf("ischio-jambiers", "isolation", "jambes")
        ),

        // ÉPAULES
        Machine(
            id = 11,
            nom = "Développé militaire",
            nomAnglais = "Military Press",
            description = "Exercice pour les épaules et triceps",
            instructions = "Debout ou assis, poussez la barre au-dessus de la tête en gardant le dos droit",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Épaules",
            incrementPoids = 2.5,
            poidsMinimum = 10.0,
            poidsMaximum = 100.0,
            niveauDifficulte = NiveauDifficulte.INTERMEDIAIRE,
            popularite = 85,
            tags = listOf("épaules", "triceps", "développé", "stabilité")
        ),
        Machine(
            id = 12,
            nom = "Élévations latérales",
            nomAnglais = "Lateral Raises",
            description = "Isolation du deltoïde moyen",
            instructions = "Debout, élevez les haltères sur les côtés jusqu'à la hauteur des épaules",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Épaules",
            incrementPoids = 1.0,
            poidsMinimum = 2.0,
            poidsMaximum = 30.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 80,
            tags = listOf("épaules", "deltoïdes", "isolation", "haltères")
        ),

        // BRAS
        Machine(
            id = 13,
            nom = "Curl biceps",
            nomAnglais = "Bicep Curl",
            description = "Exercice d'isolation pour les biceps",
            instructions = "Debout ou assis, fléchissez les coudes en contractant les biceps",
            categorie = CategorieMachine.POIDS_LIBRE,
            groupeMusculairePrimaire = "Bras",
            incrementPoids = 1.0,
            poidsMinimum = 5.0,
            poidsMaximum = 50.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 85,
            tags = listOf("biceps", "bras", "isolation", "curl")
        ),
        Machine(
            id = 14,
            nom = "Extension triceps",
            nomAnglais = "Tricep Extension",
            description = "Exercice d'isolation pour les triceps",
            instructions = "Étendez les coudes en contractant les triceps, gardez les coudes fixes",
            categorie = CategorieMachine.CABLE,
            groupeMusculairePrimaire = "Bras",
            incrementPoids = 1.0,
            poidsMinimum = 5.0,
            poidsMaximum = 60.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 80,
            tags = listOf("triceps", "bras", "isolation", "extension")
        ),

        // CARDIO
        Machine(
            id = 15,
            nom = "Tapis de course",
            nomAnglais = "Treadmill",
            description = "Appareil de cardio pour la course et la marche",
            instructions = "Réglez la vitesse et l'inclinaison selon votre niveau et vos objectifs",
            categorie = CategorieMachine.CARDIO,
            groupeMusculairePrimaire = "Cardio",
            incrementPoids = 0.0,
            poidsMinimum = 0.0,
            poidsMaximum = 0.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 95,
            tags = listOf("cardio", "course", "marche", "endurance")
        ),
        Machine(
            id = 16,
            nom = "Vélo elliptique",
            nomAnglais = "Elliptical",
            description = "Appareil de cardio à faible impact",
            instructions = "Pédalez en gardant une posture droite, utilisez les poignées pour un travail complet",
            categorie = CategorieMachine.CARDIO,
            groupeMusculairePrimaire = "Cardio",
            incrementPoids = 0.0,
            poidsMinimum = 0.0,
            poidsMaximum = 0.0,
            niveauDifficulte = NiveauDifficulte.DEBUTANT,
            popularite = 85,
            tags = listOf("cardio", "faible impact", "corps entier")
        ),
        Machine(
            id = 17,
            nom = "Rameur",
            nomAnglais = "Rowing Machine",
            description = "Appareil de cardio travaillant tout le corps",
            instructions = "Tirez en utilisant les jambes puis le dos et les bras, revenez en sens inverse",
            categorie = CategorieMachine.CARDIO,
            groupeMusculairePrimaire = "Cardio",
            incrementPoids = 0.0,
            poidsMinimum = 0.0,
            poidsMaximum = 0.0,
            niveauDifficulte = NiveauDifficulte.INTERMEDIAIRE,
            popularite = 75,
            tags = listOf("cardio", "corps entier", "dos", "technique")
        )
    )

    // Fonction pour obtenir les machines par catégorie
    fun getMachinesByCategorie(categorie: CategorieMachine): List<Machine> {
        return machines.filter { it.categorie == categorie }
    }

    // Fonction pour obtenir les machines par groupe musculaire
    fun getMachinesByGroupeMusculaire(groupe: String): List<Machine> {
        return machines.filter { it.groupeMusculairePrimaire == groupe }
    }

    // Fonction pour obtenir les machines recommandées selon le profil
    fun getMachinesRecommandees(age: Int, poids: Double, taille: Int, genre: String, niveau: String): List<Machine> {
        val machinesRecommandees = mutableListOf<Machine>()

        // Filtrer selon le niveau d'expérience
        val niveauDifficulte = when (niveau) {
            "Sédentaire", "Léger" -> NiveauDifficulte.DEBUTANT
            "Modéré" -> NiveauDifficulte.INTERMEDIAIRE
            "Actif" -> NiveauDifficulte.AVANCE
            "Très actif" -> NiveauDifficulte.EXPERT
            else -> NiveauDifficulte.DEBUTANT
        }

        // Machines de base selon l'âge
        when {
            age < 30 -> {
                // Jeunes : exercices polyarticulaires et poids libres
                machinesRecommandees.addAll(machines.filter {
                    it.tags.contains("polyarticulaire") || it.categorie == CategorieMachine.POIDS_LIBRE
                })
            }
            age in 30..50 -> {
                // Adultes : mélange machines et poids libres
                machinesRecommandees.addAll(machines.filter {
                    it.categorie == CategorieMachine.MACHINE_GUIDEE || it.niveauDifficulte <= niveauDifficulte
                })
            }
            else -> {
                // Seniors : machines sécurisées et cardio
                machinesRecommandees.addAll(machines.filter {
                    it.categorie == CategorieMachine.MACHINE_GUIDEE || it.categorie == CategorieMachine.CARDIO
                })
            }
        }

        // Ajustements selon le genre
        if (genre.lowercase() == "femme") {
            // Ajouter plus de machines pour les jambes et fessiers
            machinesRecommandees.addAll(machines.filter {
                it.groupeMusculairePrimaire == "Jambes" || it.tags.contains("fessiers")
            })
        } else {
            // Ajouter plus de machines pour le haut du corps
            machinesRecommandees.addAll(machines.filter {
                it.groupeMusculairePrimaire in listOf("Pectoraux", "Dos", "Épaules")
            })
        }

        return machinesRecommandees.distinctBy { it.id }.take(10)
    }

    // Groupes musculaires disponibles
    val groupesMusculaires = listOf(
        "Pectoraux", "Dos", "Jambes", "Épaules", "Bras", "Cardio"
    )

    // Presets d'entraînement
    data class WorkoutPreset(
        val nom: String,
        val emoji: String,
        val focusMusculaire: String,
        val machines: List<Machine>
    )

    val workoutPresets = listOf(
        WorkoutPreset(
            nom = "Push",
            emoji = "💪",
            focusMusculaire = "Pectoraux + Épaules + Triceps",
            machines = listOf(
                machines.first { it.nom == "Développé couché" },
                machines.first { it.nom == "Développé incliné" },
                machines.first { it.nom == "Développé militaire" },
                machines.first { it.nom == "Élévations latérales" },
                machines.first { it.nom == "Extension triceps" }
            )
        ),
        WorkoutPreset(
            nom = "Pull",
            emoji = "🔙",
            focusMusculaire = "Dos + Biceps",
            machines = listOf(
                machines.first { it.nom == "Tractions" },
                machines.first { it.nom == "Tirage vertical" },
                machines.first { it.nom == "Rowing assis" },
                machines.first { it.nom == "Curl biceps" }
            )
        ),
        WorkoutPreset(
            nom = "Legs",
            emoji = "🦵",
            focusMusculaire = "Quadriceps + Ischio + Mollets",
            machines = listOf(
                machines.first { it.nom == "Squat" },
                machines.first { it.nom == "Leg Press" },
                machines.first { it.nom == "Extension quadriceps" },
                machines.first { it.nom == "Curl ischios" }
            )
        ),
        WorkoutPreset(
            nom = "Full Body",
            emoji = "🏋️",
            focusMusculaire = "Corps entier",
            machines = listOf(
                machines.first { it.nom == "Développé couché" },
                machines.first { it.nom == "Tirage vertical" },
                machines.first { it.nom == "Squat" },
                machines.first { it.nom == "Développé militaire" },
                machines.first { it.nom == "Rowing assis" }
            )
        ),
        WorkoutPreset(
            nom = "Upper Body",
            emoji = "💪",
            focusMusculaire = "Haut du corps",
            machines = listOf(
                machines.first { it.nom == "Développé couché" },
                machines.first { it.nom == "Tirage vertical" },
                machines.first { it.nom == "Développé militaire" },
                machines.first { it.nom == "Curl biceps" },
                machines.first { it.nom == "Extension triceps" }
            )
        ),
        WorkoutPreset(
            nom = "Core + Cardio",
            emoji = "🔥",
            focusMusculaire = "Abdos + Cardio",
            machines = listOf(
                machines.first { it.nom == "Tapis de course" },
                machines.first { it.nom == "Vélo elliptique" },
                machines.first { it.nom == "Rameur" }
            )
        )
    )
}
