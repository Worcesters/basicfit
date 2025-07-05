package com.basicfit.app

// Enum pour les objectifs utilisateur
enum class ObjectifUtilisateur(val displayName: String, val calorieMultiplier: Double) {
    PERDRE_POIDS("Perdre du poids", 0.8),
    PRISE_MASSE("Prise de masse", 1.2),
    SECHE("Sèche", 0.75),
    MAINTENIR("Maintenir", 1.0)
}

// Data class pour les données d'exercice détaillées
data class ExerciseCalorieData(
    val name: String,
    val sets: Int,
    val reps: Int,
    val weight: Double,
    val restTime: Int,
    val intensity: String, // "Léger", "Modéré", "Intense"
    val oneRepMax: Double = 0.0
)

// Fonction améliorée pour calculer les calories brûlées par exercice
fun calculateExerciseCalories(
    exerciseData: ExerciseCalorieData,
    age: Int,
    weight: Double,
    gender: String
): Int {
    // Calcul du MET basé sur l'intensité et le pourcentage du 1RM
    val baseMetValue = when (exerciseData.intensity) {
        "Léger" -> 3.0
        "Modéré" -> 5.0
        "Intense" -> 8.0
        else -> 5.0
    }

    // Ajustement basé sur le pourcentage du 1RM utilisé
    val rmPercentage = if (exerciseData.oneRepMax > 0) {
        (exerciseData.weight / exerciseData.oneRepMax) * 100
    } else {
        50.0 // Valeur par défaut
    }

    val intensityMultiplier = when {
        rmPercentage > 85 -> 1.3 // Très intense
        rmPercentage > 70 -> 1.1 // Intense
        rmPercentage > 50 -> 1.0 // Modéré
        else -> 0.8 // Léger
    }

    val adjustedMet = baseMetValue * intensityMultiplier

    // Ajustement basé sur l'âge
    val ageMultiplier = when {
        age < 25 -> 1.1
        age < 35 -> 1.0
        age < 50 -> 0.95
        else -> 0.9
    }

    // Ajustement basé sur le genre
    val genderMultiplier = if (gender.lowercase() == "homme") 1.0 else 0.85

    // Durée totale de l'exercice (séries × temps + repos)
    val workTime = exerciseData.sets * 45 // 45 secondes par série en moyenne
    val totalRestTime = (exerciseData.sets - 1) * exerciseData.restTime
    val totalTime = (workTime + totalRestTime) / 60.0 // en minutes

    return ((adjustedMet * weight * (totalTime / 60.0) * ageMultiplier * genderMultiplier) * 1.05).toInt()
}

// Fonction pour calculer les calories brûlées pour une séance complète
fun calculateWorkoutCalories(
    exercises: List<ExerciseCalorieData>,
    age: Int,
    weight: Double,
    gender: String
): Int {
    return exercises.sumOf { exercise ->
        calculateExerciseCalories(exercise, age, weight, gender)
    }
}

// Fonction pour estimer le 1RM basé sur l'historique
fun estimateOneRepMax(weight: Double, reps: Int): Double {
    // Formule de Brzycki pour estimer le 1RM
    return if (reps > 1) {
        weight / (1.0278 - (0.0278 * reps))
    } else {
        weight
    }
}

// Fonction pour calculer le poids recommandé basé sur l'historique
fun calculateRecommendedWeight(
    exerciseName: String,
    workoutHistory: List<WorkoutEntry>,
    targetReps: Int = 12
): Double {
    // Chercher l'exercice dans l'historique
    val exerciseHistory = workoutHistory.flatMap { workout ->
        workout.exercises.filter { it.name == exerciseName }
    }.sortedByDescending { it.weight }

    return if (exerciseHistory.isNotEmpty()) {
        val lastPerformance = exerciseHistory.first()
        val estimatedOneRM = estimateOneRepMax(lastPerformance.weight, lastPerformance.reps)

        // Calculer le poids pour le nombre de répétitions cible
        val targetWeight = estimatedOneRM * (1.0278 - (0.0278 * targetReps))
        maxOf(targetWeight, 0.0)
    } else {
        0.0 // Aucune donnée historique
    }
}