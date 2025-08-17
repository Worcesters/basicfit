package com.basicfit.app.data

import java.time.LocalDate
import java.time.format.DateTimeFormatter

/**
 * Modèle pour les séances simples (nouveau système CSV)
 * Compatible avec le backend SeanceSimple
 */
data class SimpleSession(
    val id: Long = 0,
    val machine: String,
    val date: LocalDate,
    val type: SessionType,
    val duree: Int? = null,
    val note: Int? = null,
    val commentaire: String = "",
    val createdAt: String = ""
)

enum class SessionType(val displayName: String, val apiValue: String) {
    CARDIO("Cardio", "CARDIO"),
    MUSCULATION("Musculation", "MUSCULATION"), 
    FORCE("Force", "FORCE"),
    ENDURANCE("Endurance", "ENDURANCE"),
    GAINAGE("Gainage", "GAINAGE"),
    AUTRE("Autre", "AUTRE");

    companion object {
        fun fromApiValue(apiValue: String): SessionType {
            return values().find { it.apiValue == apiValue } ?: AUTRE
        }

        fun fromString(str: String): SessionType {
            return when (str.uppercase()) {
                "CARDIO", "TAPIS", "VELO", "VÉLO", "RAMEUR", "ELLIPTIQUE" -> CARDIO
                "MUSCULATION", "MUSCU" -> MUSCULATION
                "FORCE" -> FORCE
                "ENDURANCE" -> ENDURANCE
                "GAINAGE", "PLANK", "CORE" -> GAINAGE
                else -> AUTRE
            }
        }
    }
}

/**
 * Réponse de l'API pour les séances simples
 */
data class SimpleSessionResponse(
    val success: Boolean,
    val data: List<SimpleSession>,
    val count: Int,
    val message: String
)

/**
 * Réponse de l'API pour l'import CSV
 */
data class CsvImportResponse(
    val success: Boolean,
    val imported_count: Int,
    val total_lines: Int,
    val errors_count: Int,
    val message: String,
    val errors: List<String> = emptyList()
)

/**
 * Réponse de l'API pour la suppression
 */
data class DeleteAllResponse(
    val success: Boolean,
    val deleted_count: Int,
    val message: String
)

/**
 * Résumé du calendrier
 */
data class CalendarSummary(
    val calendar_entries: List<CalendarEntry>,
    val total_seances: Int,
    val total_dates: Int,
    val derniere_seance: String?
)

data class CalendarEntry(
    val date: String,
    val seances_count: Int,
    val seances: List<CalendarSessionInfo>,
    val types: List<String>
)

data class CalendarSessionInfo(
    val id: Long,
    val machine: String,
    val type: String,
    val duree: Int?
)

/**
 * Réponse de l'API pour le résumé calendrier
 */
data class CalendarSummaryResponse(
    val success: Boolean,
    val data: CalendarSummary,
    val message: String
)

/**
 * Modèles pour les recommandations intelligentes
 */
data class IntelligentRecommendation(
    val machine_id: Long,
    val machine_nom: String,
    val machine_categorie: String,
    val poids_recommande: Double,
    val series_recommandees: Int,
    val repetitions_recommandees: Int,
    val repos_recommande: Int,
    val notes: String,
    val progression_info: ProgressionInfo,
    val recommandation_source: String
)

data class ProgressionInfo(
    val poids_actuel: Double,
    val taux_reussite: Double,
    val nombre_seances: Int,
    val dernier_1rm: Double?,
    val progression_totale: Double
)

data class IntelligentRecommendationsResponse(
    val success: Boolean,
    val data: List<IntelligentRecommendation>,
    val message: String,
    val mode_entrainement: String,
    val count: Int
)

/**
 * Modèles pour les progressions utilisateur
 */
data class UserProgression(
    val id: Long,
    val machine_id: Long,
    val machine_nom: String,
    val mode_entrainement: String,
    val poids_actuel: Double,
    val taux_reussite: Double,
    val nombre_seances_machine: Int,
    val dernier_1rm: Double?,
    val progression_poids_total: Double,
    val derniere_progression: String?,
    val derniere_seance: String?
)

data class ProgressionsResponse(
    val success: Boolean,
    val data: List<UserProgression>,
    val message: String,
    val count: Int
)