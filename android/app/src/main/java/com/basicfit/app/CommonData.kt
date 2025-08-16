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

// Classe pour tracker les performances d'un exercice
data class ExercisePerformance(
    val machineName: String,
    val lastWeight: Double,
    val targetSets: Int,
    val targetReps: Int,
    val achievedSets: Int,
    val achievedReps: Int,
    val successRate: Double,
    val lastSessionDate: String,
    val recommendation: WeightRecommendation?
)

// Types de recommandation d'ajustement de poids
sealed class WeightRecommendation {
    data class Increase(val newWeight: Double, val reason: String) : WeightRecommendation()
    data class Decrease(val newWeight: Double, val reason: String) : WeightRecommendation()
    data class Maintain(val reason: String) : WeightRecommendation()
    object Pending : WeightRecommendation()
}

// Classe pour l'historique détaillé d'un exercice
data class ExerciseHistory(
    val machineName: String,
    val date: String,
    val sets: List<SetPerformance>
)

// Performance d'une série individuelle
data class SetPerformance(
    val setNumber: Int,
    val targetReps: Int,
    val achievedReps: Int,
    val weight: Double,
    val restTime: Int?, // en secondes
    val completed: Boolean
)

