package com.basicfit.app

// Enums pour remplacer MachineData
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

// Classe Machine pour remplacer MachineData.Machine
data class Machine(
    val id: Int,
    val nom: String,
    val nomAnglais: String = "",
    val description: String,
    val instructions: String,
    val categorie: CategorieMachine = CategorieMachine.MUSCULATION,
    val groupeMusculairePrimaire: String,
    val incrementPoids: Double = 2.5,
    val poidsMinimum: Double = 5.0,
    val poidsMaximum: Double = 200.0,
    val niveauDifficulte: NiveauDifficulte = NiveauDifficulte.DEBUTANT,
    val popularite: Int = 0,
    val estDisponible: Boolean = true,
    val necessite_supervision: Boolean = false,
    val tags: List<String> = emptyList(),
    val imageGif: String? = null,
    val tempo: String? = null
)

// Classe Exercise pour remplacer MachineData.Exercise
data class Exercise(
    val name: String,
    val sets: Int,
    val reps: Int,
    val weight: Double,
    val totalWeight: Double = weight * sets
)

// Classe simple pour les enregistrements d'exercices
data class ExerciseRecord(
    val name: String,
    val sets: Int,
    val reps: Int,
    val weight: Double
) {
    // Calculer le poids total comme propriété calculée
    val totalWeight: Double get() = weight * sets
}

