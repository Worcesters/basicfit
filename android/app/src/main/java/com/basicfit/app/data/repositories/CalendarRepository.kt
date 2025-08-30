package com.basicfit.app.data.repositories

import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.api.CsvImportRequest
import com.basicfit.app.data.api.CsvImportResponse
import com.basicfit.app.data.models.*
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDate
import java.time.format.DateTimeFormatter

/**
 * Repository pour la gestion du calendrier et de l'historique des entraînements
 * Gère l'affichage des séances par date et les statistiques
 */
class CalendarRepository(
    private val apiService: BasicFitApiService,
    private val logger: Logger
) {

    // État de l'historique des entraînements
    private val _workoutHistory = MutableStateFlow<List<WorkoutSession>>(emptyList())
    val workoutHistory: StateFlow<List<WorkoutSession>> = _workoutHistory.asStateFlow()

    // État de chargement
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Mois et année actuellement affichés
    private val _currentMonth = MutableStateFlow(LocalDate.now().withDayOfMonth(1))
    val currentMonth: StateFlow<LocalDate> = _currentMonth.asStateFlow()

    // Résumé mensuel
    private val _monthlySummary = MutableStateFlow<MonthlySummary?>(null)
    val monthlySummary: StateFlow<MonthlySummary?> = _monthlySummary.asStateFlow()

    /**
     * Charger l'historique des entraînements
     */
    suspend fun loadWorkoutHistory(): Result<List<WorkoutSession>> {
        return try {
            _isLoading.value = true
            logger.info("CALENDAR", "Chargement historique des entraînements")

            val response = apiService.getWorkoutHistory()

            if (response.isSuccessful) {
                val historyData = response.body()
                if (historyData != null) {
                    _workoutHistory.value = historyData.results
                    logger.success("CALENDAR", "Historique chargé: ${historyData.results.size} séances")
                    Result.success(historyData.results)
                } else {
                    logger.error("CALENDAR", "Données historique vides")
                    Result.failure(Exception("Aucune donnée disponible"))
                }
            } else {
                val errorMsg = "Erreur historique: ${response.code()} - ${response.message()}"
                logger.error("CALENDAR", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("CALENDAR", "Erreur lors du chargement historique", exception = e)
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }

    /**
     * Charger le résumé d'un mois spécifique
     */
    suspend fun loadMonthlySummary(year: Int, month: Int): Result<MonthlySummary> {
        return try {
            _isLoading.value = true
            logger.info("CALENDAR", "Chargement résumé mensuel: $year-$month")

            val response = apiService.getMonthlySummary(year, month)

            if (response.isSuccessful) {
                val summary = response.body()
                if (summary != null) {
                    _monthlySummary.value = summary
                    logger.success("CALENDAR", "Résumé mensuel chargé: ${summary.totalSeances} séances")
                    Result.success(summary)
                } else {
                    logger.error("CALENDAR", "Résumé mensuel vide")
                    Result.failure(Exception("Aucune donnée disponible"))
                }
            } else {
                val errorMsg = "Erreur résumé mensuel: ${response.code()}"
                logger.error("CALENDAR", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("CALENDAR", "Erreur lors du chargement résumé mensuel", exception = e)
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }

    /**
     * Importer des séances depuis un fichier CSV
     */
    suspend fun importCsvData(csvContent: String): Result<CsvImportResponse> {
        return try {
            _isLoading.value = true
            logger.info("CALENDAR", "Import CSV en cours...")

            val importRequest = CsvImportRequest(csvData = csvContent)
            val response = apiService.importCsvSessions(importRequest)

            if (response.isSuccessful) {
                val importResult = response.body()
                if (importResult != null) {
                    logger.success("CALENDAR", "Import réussi: ${importResult.importedCount} séances importées")

                    // Recharger l'historique après import
                    loadWorkoutHistory()

                    Result.success(importResult)
                } else {
                    logger.error("CALENDAR", "Réponse import vide")
                    Result.failure(Exception("Erreur lors de l'import"))
                }
            } else {
                val errorMsg = "Erreur import CSV: ${response.code()} - ${response.message()}"
                logger.error("CALENDAR", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("CALENDAR", "Erreur lors de l'import CSV", exception = e)
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }

    /**
     * Obtenir les séances d'une date spécifique
     */
    fun getWorkoutsForDate(date: LocalDate): List<WorkoutSession> {
        val dateString = date.format(DateTimeFormatter.ISO_LOCAL_DATE)
        return _workoutHistory.value.filter { workout ->
            workout.date == dateString
        }
    }

    /**
     * Obtenir les dates avec séances pour un mois spécifique
     */
    fun getDatesWithWorkouts(year: Int, month: Int): Set<LocalDate> {
        return _workoutHistory.value.mapNotNull { workout ->
            try {
                val workoutDate = LocalDate.parse(workout.date)
                if (workoutDate.year == year && workoutDate.monthValue == month) {
                    workoutDate
                } else null
            } catch (e: Exception) {
                null
            }
        }.toSet()
    }

    /**
     * Changer le mois affiché
     */
    fun changeMonth(newMonth: LocalDate) {
        logger.debug("CALENDAR", "Mois changé: ${newMonth.format(DateTimeFormatter.ofPattern("MM/yyyy"))}")
    }

    /**
     * Passer au mois suivant
     */
    fun nextMonth() {
        logger.debug("CALENDAR", "Mois suivant")
    }

    /**
     * Passer au mois précédent
     */
    fun previousMonth() {
        logger.debug("CALENDAR", "Mois précédent")
    }

    /**
     * Aller au mois actuel
     */
    fun goToCurrentMonth() {
        logger.debug("CALENDAR", "Retour au mois actuel")
    }

    /**
     * Supprimer une séance
     */
    suspend fun deleteWorkout(workoutId: Int): Result<Boolean> {
        return try {
            logger.info("CALENDAR", "Suppression séance ID: $workoutId")

            val response = apiService.deleteWorkout(workoutId)

            if (response.isSuccessful) {
                // Mettre à jour la liste locale
                _workoutHistory.value = _workoutHistory.value.filter { it.id != workoutId }
                logger.success("CALENDAR", "Séance supprimée")
                Result.success(true)
            } else {
                val errorMsg = "Erreur suppression: ${response.code()}"
                logger.error("CALENDAR", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("CALENDAR", "Erreur lors de la suppression", exception = e)
            Result.failure(e)
        }
    }

    /**
     * Supprimer toutes les séances de l'historique
     */
    suspend fun deleteAllSessions(): Result<Boolean> {
        return try {
            logger.info("CALENDAR", "Suppression de toutes les séances...")
            val response = apiService.deleteAllSessions()

            if (response.isSuccessful) {
                logger.success("CALENDAR", "Toutes les séances supprimées")
                loadWorkoutHistory() // Recharger l'historique après la suppression
                Result.success(true)
            } else {
                val errorMsg = "Erreur suppression de toutes les séances: ${response.code()}"
                logger.error("CALENDAR", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("CALENDAR", "Erreur lors de la suppression de toutes les séances", exception = e)
            Result.failure(e)
        }
    }

    /**
     * Obtenir les statistiques générales
     */
    fun getGeneralStats(): CalendarStats {
        val workouts = _workoutHistory.value
        val totalWorkouts = workouts.size
        val totalDuration = workouts.sumOf { it.duree }
        val averageDuration = if (totalWorkouts > 0) totalDuration / totalWorkouts else 0

        val thisMonth = LocalDate.now()
        val thisMonthWorkouts = workouts.count { workout ->
            try {
                val workoutDate = LocalDate.parse(workout.date)
                workoutDate.year == thisMonth.year && workoutDate.monthValue == thisMonth.monthValue
            } catch (e: Exception) {
                false
            }
        }

        return CalendarStats(
            totalSeances = totalWorkouts,
            totalMinutes = totalDuration,
            moyenneDuree = averageDuration,
            seancesCeMois = thisMonthWorkouts
        )
    }

    /**
     * Effacer toutes les données locales
     */
    fun clearLocalData() {
        _workoutHistory.value = emptyList()
        _monthlySummary.value = null
        logger.info("CALENDAR", "Données locales effacées")
    }
}

/**
 * Statistiques du calendrier
 */
data class CalendarStats(
    val totalSeances: Int,
    val totalMinutes: Int,
    val moyenneDuree: Int,
    val seancesCeMois: Int
)

/**
 * Résumé mensuel
 */
data class MonthlySummary(
    val year: Int,
    val month: Int,
    val totalSeances: Int,
    val totalMinutes: Int,
    val exercicesPrincipaux: List<String>,
    val progression: Map<String, Double> = emptyMap()
)