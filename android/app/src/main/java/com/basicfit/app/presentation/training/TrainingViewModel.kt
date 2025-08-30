package com.basicfit.app.presentation.training

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.basicfit.app.data.models.*
import com.basicfit.app.data.repositories.MachineRepository
import com.basicfit.app.data.repositories.WorkoutRepository
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * ViewModel pour l'onglet Entraînement
 * Gère la sélection des machines, recommandations et séances
 */
class TrainingViewModel(
    private val workoutRepository: WorkoutRepository,
    private val machineRepository: MachineRepository,
    private val logger: Logger
) : ViewModel() {

    // États des données
    val machines = machineRepository.machines
    val recommendations = workoutRepository.currentRecommendations
    val activeWorkout = workoutRepository.activeWorkout

    // États de l'interface
    private val _currentScreen = MutableStateFlow(TrainingScreen.MACHINE_SELECTION)
    val currentScreen: StateFlow<TrainingScreen> = _currentScreen.asStateFlow()

    private val _selectedMachines = MutableStateFlow<List<Machine>>(emptyList())
    val selectedMachines: StateFlow<List<Machine>> = _selectedMachines.asStateFlow()

    private val _workoutName = MutableStateFlow("")
    val workoutName: StateFlow<String> = _workoutName.asStateFlow()

    private val _trainingMode = MutableStateFlow("PRISE_MASSE")
    val trainingMode: StateFlow<String> = _trainingMode.asStateFlow()

    // États de chargement et messages
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    // Recherche et filtres pour machines
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _filteredMachines = MutableStateFlow<List<Machine>>(emptyList())
    val filteredMachines: StateFlow<List<Machine>> = _filteredMachines.asStateFlow()

    init {
        logger.info("TRAINING", "Initialisation du TrainingViewModel")

        // Observer les machines pour appliquer les filtres
        viewModelScope.launch {
            combine(machines, searchQuery) { machineList: List<Machine>, query: String ->
                Pair(machineList, query)
            }.collect { (machineList, query) ->
                applyMachineFilters(machineList, query)
            }
        }

        // Charger les machines si pas déjà fait
        if (machines.value.isEmpty()) {
            loadMachines()
        }
    }

    /**
     * Charger les machines disponibles
     */
    fun loadMachines() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = machineRepository.loadMachines()
                if (result.isFailure) {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de chargement"
                    _errorMessage.value = errorMsg
                    logger.error("TRAINING", "Erreur chargement machines: $errorMsg")
                } else {
                    logger.success("TRAINING", "Machines chargées: ${result.getOrNull()?.size ?: 0}")
                }
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Mettre à jour la recherche de machines
     */
    fun updateMachineSearch(query: String) {
        _searchQuery.value = query
        logger.debug("TRAINING", "Recherche machines: '$query'")
    }

    /**
     * Sélectionner/désélectionner une machine
     */
    fun toggleMachineSelection(machine: Machine) {
        val currentSelected = _selectedMachines.value.toMutableList()

        if (currentSelected.contains(machine)) {
            currentSelected.remove(machine)
            logger.debug("TRAINING", "Machine désélectionnée: ${machine.nom}")
        } else if (currentSelected.size < 10) { // Limite de 10 machines par séance
            currentSelected.add(machine)
            logger.debug("TRAINING", "Machine sélectionnée: ${machine.nom}")
        } else {
            _errorMessage.value = "Maximum 10 machines par séance"
            return
        }

        _selectedMachines.value = currentSelected
    }

    /**
     * Effacer la sélection de machines
     */
    fun clearMachineSelection() {
        _selectedMachines.value = emptyList()
        logger.debug("TRAINING", "Sélection de machines effacée")
    }

    /**
     * Définir le nom de l'entraînement
     */
    fun setWorkoutName(name: String) {
        _workoutName.value = name.trim()
    }

    /**
     * Définir le mode d'entraînement
     */
    fun setTrainingMode(mode: String) {
        _trainingMode.value = mode
        logger.debug("TRAINING", "Mode d'entraînement: $mode")
    }

    /**
     * Obtenir les recommandations intelligentes
     */
    fun loadIntelligentRecommendations() {
        viewModelScope.launch {
            if (_selectedMachines.value.isEmpty()) {
                _errorMessage.value = "Sélectionnez d'abord des machines"
                return@launch
            }

            _isLoading.value = true

            try {
                logger.info("TRAINING", "Chargement recommandations intelligentes...")

                val result = workoutRepository.getSessionRecommendations(
                    mode = _trainingMode.value,
                    nbMachines = _selectedMachines.value.size
                )

                if (result.isSuccess) {
                    val recommendationsReceived = result.getOrNull() ?: emptyList()
                    logger.success("TRAINING", "Recommandations reçues: ${recommendationsReceived.size}")
                    _successMessage.value = "Recommandations chargées avec succès"
                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de recommandations"
                    _errorMessage.value = errorMsg
                    logger.error("TRAINING", "Erreur recommandations: $errorMsg")
                }
            } catch (e: Exception) {
                val errorMsg = "Erreur lors du chargement des recommandations: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("TRAINING", errorMsg, exception = e)
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Démarrer l'entraînement
     */
    fun startWorkout() {
        viewModelScope.launch {
            if (_selectedMachines.value.isEmpty()) {
                _errorMessage.value = "Sélectionnez au moins une machine"
                return@launch
            }

            if (_workoutName.value.isBlank()) {
                _errorMessage.value = "Donnez un nom à votre séance"
                return@launch
            }

            try {
                val workoutName = _workoutName.value.ifBlank {
                    "Séance ${java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("dd/MM HH:mm"))}"
                }

                logger.info("TRAINING", "Démarrage séance: $workoutName")

                val activeSession = workoutRepository.startWorkoutSession(
                    workoutName = workoutName,
                    selectedMachines = _selectedMachines.value,
                    recommendations = recommendations.value
                )

                _currentScreen.value = TrainingScreen.WORKOUT_IN_PROGRESS
                _successMessage.value = "Séance démarrée !"

            } catch (e: Exception) {
                val errorMsg = "Erreur lors du démarrage: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("TRAINING", errorMsg, exception = e)
            }
        }
    }

    /**
     * Compléter une série
     */
    fun completeSet(weight: Double, reps: Int, restTime: Int = 90) {
        val success = workoutRepository.completeSet(weight, reps, restTime)
        if (success) {
            logger.debug("TRAINING", "Série complétée: ${weight}kg x $reps")

            // Vérifier si toute la séance est terminée
            if (workoutRepository.isWorkoutCompleted()) {
                _successMessage.value = "Séance terminée ! Sauvegarde en cours..."
                completeWorkout()
            }
        } else {
            _errorMessage.value = "Erreur lors de l'enregistrement de la série"
        }
    }

    /**
     * Passer à l'exercice suivant
     */
    fun moveToNextExercise() {
        val success = workoutRepository.moveToNextExercise()
        if (!success) {
            _errorMessage.value = "Vous êtes déjà au dernier exercice"
        }
    }

    /**
     * Revenir à l'exercice précédent
     */
    fun moveToPreviousExercise() {
        val success = workoutRepository.moveToPreviousExercise()
        if (!success) {
            _errorMessage.value = "Vous êtes déjà au premier exercice"
        }
    }

    /**
     * Terminer et sauvegarder l'entraînement
     */
    fun completeWorkout() {
        viewModelScope.launch {
            _isLoading.value = true

            try {
                val result = workoutRepository.completeAndSaveWorkout()

                if (result.isSuccess) {
                    val saveResponse = result.getOrNull()
                    _successMessage.value = "Séance sauvegardée avec succès !"
                    _currentScreen.value = TrainingScreen.WORKOUT_COMPLETED
                    logger.success("TRAINING", "Séance sauvegardée: ${saveResponse?.id}")

                    // Réinitialiser pour la prochaine séance
                    resetWorkoutSession()

                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de sauvegarde"
                    _errorMessage.value = "Erreur sauvegarde: $errorMsg"
                    logger.error("TRAINING", "Erreur sauvegarde: $errorMsg")
                }
            } catch (e: Exception) {
                val errorMsg = "Erreur lors de la sauvegarde: ${e.message}"
                _errorMessage.value = errorMsg
                logger.error("TRAINING", errorMsg, exception = e)
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Abandonner l'entraînement
     */
    fun cancelWorkout() {
        workoutRepository.cancelWorkout()
        _currentScreen.value = TrainingScreen.MACHINE_SELECTION
        resetWorkoutSession()
        logger.info("TRAINING", "Séance abandonnée par l'utilisateur")
    }

    /**
     * Revenir à la sélection de machines
     */
    fun backToMachineSelection() {
        _currentScreen.value = TrainingScreen.MACHINE_SELECTION
    }

    /**
     * Démarrer une nouvelle séance
     */
    fun startNewWorkout() {
        resetWorkoutSession()
        _currentScreen.value = TrainingScreen.MACHINE_SELECTION
        logger.info("TRAINING", "Préparation nouvelle séance")
    }

    /**
     * Obtenir le pourcentage de progression
     */
    fun getWorkoutProgress(): Float {
        return workoutRepository.getWorkoutProgress()
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
     * Appliquer les filtres sur les machines
     */
    private fun applyMachineFilters(machines: List<Machine>, query: String) {
        val filtered = if (query.isBlank()) {
            machines
        } else {
            machines.filter { machine ->
                machine.nom.contains(query, ignoreCase = true) ||
                machine.description.contains(query, ignoreCase = true) ||
                machine.groupeMusculaire.contains(query, ignoreCase = true)
            }
        }
        _filteredMachines.value = filtered
    }

    /**
     * Réinitialiser la session d'entraînement
     */
    private fun resetWorkoutSession() {
        _selectedMachines.value = emptyList()
        _workoutName.value = ""
        _searchQuery.value = ""
    }

    override fun onCleared() {
        super.onCleared()
        logger.debug("TRAINING", "TrainingViewModel détruit")
    }
}

/**
 * États possibles de l'écran d'entraînement
 */
enum class TrainingScreen {
    MACHINE_SELECTION,     // Sélection des machines
    WORKOUT_IN_PROGRESS,   // Séance en cours
    WORKOUT_COMPLETED      // Séance terminée
}