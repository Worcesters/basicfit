package com.basicfit.app.presentation.calendar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.basicfit.app.data.models.WorkoutSession
import com.basicfit.app.data.repositories.MonthlySummary
import com.basicfit.app.data.repositories.CalendarRepository
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter

/**
 * ViewModel pour l'onglet Calendrier
 * Gère l'affichage du calendrier, import CSV et historique des séances
 */
class CalendarViewModel(
    private val calendarRepository: CalendarRepository,
    private val logger: Logger
) : ViewModel() {

    // États des données
    private val _workoutHistory = MutableStateFlow<List<WorkoutSession>>(emptyList())
    val workoutHistory: StateFlow<List<WorkoutSession>> = _workoutHistory.asStateFlow()

    private val _monthlySummary = MutableStateFlow<MonthlySummary?>(null)
    val monthlySummary: StateFlow<MonthlySummary?> = _monthlySummary.asStateFlow()

    private val _currentMonth = MutableStateFlow(LocalDate.now().withDayOfMonth(1))
    val currentMonth: StateFlow<LocalDate> = _currentMonth.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // État de l'interface
    private val _currentView = MutableStateFlow(CalendarView.CALENDAR)
    val currentView: StateFlow<CalendarView> = _currentView.asStateFlow()

    private val _selectedDate = MutableStateFlow<LocalDate?>(null)
    val selectedDate: StateFlow<LocalDate?> = _selectedDate.asStateFlow()

    private val _selectedWorkouts = MutableStateFlow<List<WorkoutSession>>(emptyList())
    val selectedWorkouts: StateFlow<List<WorkoutSession>> = _selectedWorkouts.asStateFlow()

    // États de messages
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    // État d'import CSV
    private val _isImporting = MutableStateFlow(false)
    val isImporting: StateFlow<Boolean> = _isImporting.asStateFlow()

    // Dates avec séances pour le mois courant
    private val _datesWithWorkouts = MutableStateFlow<Set<LocalDate>>(emptySet())
    val datesWithWorkouts: StateFlow<Set<LocalDate>> = _datesWithWorkouts.asStateFlow()

    // Statistiques
    private val _calendarStats = MutableStateFlow(calendarRepository.getGeneralStats())
    val calendarStats = _calendarStats.asStateFlow()

    init {
        logger.info("CALENDAR", "Initialisation du CalendarViewModel")

        // Observer les changements de mois pour mettre à jour les dates avec séances
        viewModelScope.launch {
            combine(
                currentMonth,
                workoutHistory
            ) { month: LocalDate, history: List<WorkoutSession> ->
                Pair(month, history)
            }.collect { (month, history) ->
                updateDatesWithWorkouts(month, history)
                updateStats()
            }
        }

        // Observer la date sélectionnée pour charger les séances
        viewModelScope.launch {
            selectedDate.collect { date ->
                date?.let { updateSelectedWorkouts(it) }
            }
        }

        // Charger les données au démarrage
        loadInitialData()
    }

    /**
     * Charger les données initiales
     */
    private fun loadInitialData() {
        viewModelScope.launch {
            logger.info("CALENDAR", "Chargement données initiales...")

            // Charger l'historique
            val historyResult = calendarRepository.loadWorkoutHistory()
            if (historyResult.isSuccess) {
                _workoutHistory.value = historyResult.getOrNull() ?: emptyList()
            } else {
                val errorMsg = historyResult.exceptionOrNull()?.message ?: "Erreur de chargement"
                logger.error("CALENDAR", "Erreur chargement historique: $errorMsg")
                _errorMessage.value = errorMsg
            }

            // Charger le résumé du mois courant
            val currentDate = LocalDate.now()
            val summaryResult = calendarRepository.loadMonthlySummary(
                currentDate.year,
                currentDate.monthValue
            )
            if (summaryResult.isSuccess) {
                _monthlySummary.value = summaryResult.getOrNull()
            } else {
                logger.debug("CALENDAR", "Pas de résumé mensuel disponible")
            }
        }
    }

    /**
     * Changer la vue affichée
     */
    fun setView(view: CalendarView) {
        _currentView.value = view
        logger.debug("CALENDAR", "Vue changée: $view")
    }

    /**
     * Sélectionner une date
     */
    fun selectDate(date: LocalDate) {
        _selectedDate.value = date
        logger.debug("CALENDAR", "Date sélectionnée: ${date.format(DateTimeFormatter.ISO_LOCAL_DATE)}")
    }

    /**
     * Désélectionner la date
     */
    fun clearSelectedDate() {
        _selectedDate.value = null
        _selectedWorkouts.value = emptyList()
    }

    /**
     * Naviguer au mois suivant
     */
    fun nextMonth() {
        calendarRepository.nextMonth()
        logger.debug("CALENDAR", "Mois suivant")
    }

    /**
     * Naviguer au mois précédent
     */
    fun previousMonth() {
        calendarRepository.previousMonth()
        logger.debug("CALENDAR", "Mois précédent")
    }

    /**
     * Retourner au mois actuel
     */
    fun goToCurrentMonth() {
        calendarRepository.goToCurrentMonth()
        logger.debug("CALENDAR", "Retour mois actuel")
    }

    /**
     * Importer des données CSV
     */
    fun importCsvData(csvContent: String) {
        viewModelScope.launch {
            _isImporting.value = true

            try {
                logger.info("CALENDAR", "Début import CSV...")

                val result = calendarRepository.importCsvData(csvContent)

                if (result.isSuccess) {
                    val importResult = result.getOrNull()
                    if (importResult != null) {
                        _successMessage.value = "Import réussi: ${importResult.importedCount} séances importées"
                        logger.success("CALENDAR", "Import CSV terminé: ${importResult.importedCount} séances")

                        // Recharger les statistiques
                        updateStats()
                    }
                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur d'import"
                    _errorMessage.value = errorMsg
                    logger.error("CALENDAR", "Erreur import CSV: $errorMsg")
                }
            } catch (e: Exception) {
                val errorMsg = "Erreur lors de l'import: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("CALENDAR", errorMsg, exception = e)
            } finally {
                _isImporting.value = false
            }
        }
    }

    /**
     * Supprimer une séance
     */
    fun deleteWorkout(workoutId: Int) {
        viewModelScope.launch {
            try {
                logger.info("CALENDAR", "Suppression séance ID: $workoutId")

                val result = calendarRepository.deleteWorkout(workoutId)

                if (result.isSuccess) {
                    _successMessage.value = "Séance supprimée avec succès"
                    logger.success("CALENDAR", "Séance supprimée")

                    // Mettre à jour la sélection si nécessaire
                    _selectedDate.value?.let { date ->
                        updateSelectedWorkouts(date)
                    }

                    updateStats()
                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de suppression"
                    _errorMessage.value = errorMsg
                    logger.error("CALENDAR", "Erreur suppression: $errorMsg")
                }
            } catch (e: Exception) {
                val errorMsg = "Erreur lors de la suppression: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("CALENDAR", errorMsg, exception = e)
            }
        }
    }

    /**
     * Recharger les données
     */
    fun refreshData() {
        viewModelScope.launch {
            logger.info("CALENDAR", "Rafraîchissement des données...")

            val result = calendarRepository.loadWorkoutHistory()
            if (result.isFailure) {
                val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de rechargement"
                _errorMessage.value = errorMsg
                logger.error("CALENDAR", "Erreur rafraîchissement: $errorMsg")
            } else {
                _successMessage.value = "Données mises à jour"
                logger.success("CALENDAR", "Données rafraîchies")
            }
        }
    }

    /**
     * Supprimer toutes les séances (réinitialisation)
     */
    suspend fun clearAllSessions() {
        viewModelScope.launch {
            try {
                logger.info("CALENDAR", "Suppression de toutes les séances...")

                val response = calendarRepository.deleteAllSessions()

                if (response.isSuccess) {
                    calendarRepository.clearLocalData()
                    _successMessage.value = "Toutes les séances ont été supprimées"
                    logger.success("CALENDAR", "Toutes les séances supprimées")

                    // Recharger les données
                    loadInitialData()
                } else {
                    val errorMsg = response.exceptionOrNull()?.message ?: "Erreur inconnue"
                    _errorMessage.value = errorMsg
                    logger.error("CALENDAR", "Erreur suppression: $errorMsg")
                }
            } catch (e: Exception) {
                val errorMsg = "Erreur lors de la suppression: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("CALENDAR", errorMsg, exception = e)
            }
        }
    }

    /**
     * Exporter l'historique en CSV
     */
    fun exportToCSV(): String {
        val workouts = workoutHistory.value
        val csvBuilder = StringBuilder()

        // En-têtes
        csvBuilder.appendLine("Date,Nom,Durée,Exercices,Note,Commentaire")

        // Données
        workouts.forEach { workout ->
            val exercisesList = workout.exercices.joinToString("; ") { "${it.nom} (${it.series}x${it.reps})" }
            csvBuilder.appendLine("\"${workout.date}\",\"${workout.nom}\",\"${workout.duree}\",\"$exercisesList\",\"${workout.noteRessenti ?: ""}\",\"${workout.commentaire ?: ""}\"")
        }

        logger.info("CALENDAR", "Export CSV généré: ${workouts.size} séances")
        _successMessage.value = "Export CSV généré"

        return csvBuilder.toString()
    }

    /**
     * Effacer les messages
     */
    fun clearMessages() {
        _errorMessage.value = null
        _successMessage.value = null
    }

    // ==================== MÉTHODES PRIVÉES ====================

    /**
     * Mettre à jour les dates avec séances pour le mois courant
     */
    private fun updateDatesWithWorkouts(month: LocalDate, history: List<WorkoutSession>) {
        val datesWithWorkouts = calendarRepository.getDatesWithWorkouts(month.year, month.monthValue)
        _datesWithWorkouts.value = datesWithWorkouts

        logger.debug("CALENDAR", "Dates avec séances mises à jour: ${datesWithWorkouts.size} dates")
    }

    /**
     * Mettre à jour les séances de la date sélectionnée
     */
    private fun updateSelectedWorkouts(date: LocalDate) {
        val workoutsForDate = calendarRepository.getWorkoutsForDate(date)
        _selectedWorkouts.value = workoutsForDate

        logger.debug("CALENDAR", "Séances pour ${date.format(DateTimeFormatter.ISO_LOCAL_DATE)}: ${workoutsForDate.size}")
    }

    /**
     * Mettre à jour les statistiques
     */
    private fun updateStats() {
        _calendarStats.value = calendarRepository.getGeneralStats()
    }

    override fun onCleared() {
        super.onCleared()
        logger.debug("CALENDAR", "CalendarViewModel détruit")
    }
}

/**
 * Vues possibles du calendrier
 */
enum class CalendarView {
    CALENDAR,    // Vue calendrier
    HISTORY,     // Vue historique liste
    IMPORT,      // Vue import CSV
    STATS        // Vue statistiques
}