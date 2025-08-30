package com.basicfit.app.data.models

import com.google.gson.annotations.SerializedName
import java.time.LocalDate
import java.time.LocalDateTime

/**
 * Séance d'entraînement complète
 */
data class WorkoutSession(
    @SerializedName("id") val id: Int = 0,
    @SerializedName("nom") val nom: String,
    @SerializedName("date") val date: String,
    @SerializedName("duree") val duree: Int, // en minutes
    @SerializedName("exercices") val exercices: List<ExerciseRecord>,
    @SerializedName("note_ressenti") val noteRessenti: Int = 7,
    @SerializedName("commentaire") val commentaire: String = "",
    @SerializedName("statut") val statut: String = "TERMINEE"
) {
    fun getTotalWeight(): Double = exercices.sumOf { it.poids * it.reps * it.series }

    fun getTotalExercises(): Int = exercices.size

    fun getFormattedDate(): String {
        return try {
            val date = LocalDate.parse(date)
            "${date.dayOfMonth}/${date.monthValue}/${date.year}"
        } catch (e: Exception) {
            date
        }
    }

    fun getFormattedDuration(): String {
        val hours = duree / 60
        val minutes = duree % 60
        return if (hours > 0) {
            "${hours}h${minutes.toString().padStart(2, '0')}"
        } else {
            "${minutes}min"
        }
    }
}

/**
 * Enregistrement d'un exercice
 */
data class ExerciseRecord(
    @SerializedName("nom") val nom: String,
    @SerializedName("poids") val poids: Double,
    @SerializedName("series") val series: Int,
    @SerializedName("reps") val reps: Int,
    @SerializedName("repos") val repos: Int = 90, // en secondes
    @SerializedName("type_exercice") val typeExercice: String = "REPETITIONS"
) {
    fun getVolume(): Double = poids * reps * series

    fun isCardio(): Boolean = typeExercice == "DUREE"

    fun getFormattedWeight(): String = if (poids % 1.0 == 0.0) {
        "${poids.toInt()}kg"
    } else {
        "${poids}kg"
    }
}

/**
 * Exercice en cours pendant une séance
 */
data class ActiveExercise(
    val machine: Machine,
    val recommendation: MachineRecommendation,
    val completedSets: MutableList<CompletedSet> = mutableListOf(),
    var currentSetIndex: Int = 0,
    var isCompleted: Boolean = false
) {
    fun getCurrentSet(): Int = currentSetIndex + 1
    fun getTotalSets(): Int = recommendation.seriesRecommandees
    fun getProgress(): Float = if (getTotalSets() > 0) currentSetIndex.toFloat() / getTotalSets() else 0f
}

/**
 * Série complétée
 */
data class CompletedSet(
    val weight: Double,
    val reps: Int,
    val restTime: Int = 90,
    val timestamp: Long = System.currentTimeMillis()
)

/**
 * Entrée du calendrier
 */
data class CalendarEntry(
    @SerializedName("id") val id: Int = 0,
    @SerializedName("date_entrainement") val dateEntrainement: String,
    @SerializedName("nom_seance") val nomSeance: String,
    @SerializedName("duree_totale_minutes") val dureeTotaleMinutes: Int,
    @SerializedName("nombre_exercices") val nombreExercices: Int,
    @SerializedName("volume_total_seance") val volumeTotalSeance: Double,
    @SerializedName("commentaire") val commentaire: String = ""
) {
    fun getFormattedDate(): String {
        return try {
            val date = LocalDate.parse(dateEntrainement)
            "${date.dayOfMonth}/${date.monthValue}"
        } catch (e: Exception) {
            dateEntrainement
        }
    }
}

/**
 * Réponse API pour sauvegarde de séance
 */
data class WorkoutSaveResponse(
    @SerializedName("id") val id: Int,
    @SerializedName("nom") val nom: String,
    @SerializedName("statut") val statut: String,
    @SerializedName("message") val message: String
)