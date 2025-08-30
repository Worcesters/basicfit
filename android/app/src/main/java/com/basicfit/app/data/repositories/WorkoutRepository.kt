package com.basicfit.app.data.repositories

import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.api.RecommendationsResponse
import com.basicfit.app.data.models.*
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Repository pour la gestion des entraînements
 * Gère les séances, recommandations et sauvegarde
 */
class WorkoutRepository(
    private val apiService: BasicFitApiService,
    private val logger: Logger
) {
    
    // États des recommandations
    private val _currentRecommendations = MutableStateFlow<List<MachineRecommendation>>(emptyList())
    val currentRecommendations: StateFlow<List<MachineRecommendation>> = _currentRecommendations.asStateFlow()
    
    // Séance en cours
    private val _activeWorkout = MutableStateFlow<ActiveWorkoutSession?>(null)
    val activeWorkout: StateFlow<ActiveWorkoutSession?> = _activeWorkout.asStateFlow()
    
    // État de chargement
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    /**
     * Obtenir les recommandations pour une séance
     */
    suspend fun getSessionRecommendations(mode: String = "PRISE_MASSE", nbMachines: Int = 6): Result<List<MachineRecommendation>> {
        return try {
            _isLoading.value = true
            logger.info("TRAINING", "Récupération des recommandations: mode=$mode, nb=$nbMachines")
            
            val response = apiService.getSessionRecommendations(mode, nbMachines)
            
            if (response.isSuccessful) {
                val recommendationsResponse = response.body()
                if (recommendationsResponse != null) {
                    _currentRecommendations.value = recommendationsResponse.recommendations
                    logger.success("TRAINING", "Recommandations reçues: ${recommendationsResponse.recommendations.size} machines")
                    Result.success(recommendationsResponse.recommendations)
                } else {
                    logger.error("TRAINING", "Réponse de recommandations vide")
                    Result.failure(Exception("Aucune recommandation disponible"))
                }
            } else {
                val errorMsg = "Erreur recommandations: ${response.code()} - ${response.message()}"
                logger.error("TRAINING", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("TRAINING", "Erreur lors de la récupération des recommandations", exception = e)
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }
    
    /**
     * Obtenir une recommandation spécifique pour une machine
     */
    suspend fun getMachineRecommendation(machineId: Int): Result<MachineRecommendation> {
        return try {
            logger.info("TRAINING", "Récupération recommandation pour machine ID: $machineId")
            
            val response = apiService.getMachineRecommendation(machineId)
            
            if (response.isSuccessful) {
                val recommendation = response.body()
                if (recommendation != null) {
                    logger.success("TRAINING", "Recommandation machine reçue: ${recommendation.poidsRecommande}kg")
                    Result.success(recommendation)
                } else {
                    logger.error("TRAINING", "Recommandation machine vide")
                    Result.failure(Exception("Recommandation introuvable"))
                }
            } else {
                val errorMsg = "Erreur recommandation machine: ${response.code()}"
                logger.error("TRAINING", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("TRAINING", "Erreur lors de la récupération de la recommandation machine", exception = e)
            Result.failure(e)
        }
    }
    
    /**
     * Démarrer une nouvelle séance d'entraînement
     */
    fun startWorkoutSession(
        workoutName: String,
        selectedMachines: List<Machine>,
        recommendations: List<MachineRecommendation>
    ): ActiveWorkoutSession {
        logger.info("TRAINING", "Démarrage séance: $workoutName avec ${selectedMachines.size} machines")
        
        val exercises = selectedMachines.mapIndexed { index, machine ->
            val recommendation = recommendations.find { it.machineId == machine.id }
            
            ActiveExercise(
                machine = machine,
                recommendation = recommendation ?: createDefaultRecommendation(machine),
                completedSets = mutableListOf(),
                currentSetIndex = 0,
                isCompleted = false
            )
        }
        
        val activeSession = ActiveWorkoutSession(
            workoutName = workoutName,
            exercises = exercises,
            startTime = System.currentTimeMillis(),
            currentExerciseIndex = 0,
            isCompleted = false
        )
        
        _activeWorkout.value = activeSession
        logger.success("TRAINING", "Séance démarrée avec ${exercises.size} exercices")
        return activeSession
    }
    
    /**
     * Compléter une série pour l'exercice en cours
     */
    fun completeSet(weight: Double, reps: Int, restTime: Int = 90): Boolean {
        val activeSession = _activeWorkout.value ?: return false
        val currentExercise = activeSession.getCurrentExercise() ?: return false
        
        val completedSet = CompletedSet(
            weight = weight,
            reps = reps,
            restTime = restTime,
            timestamp = System.currentTimeMillis()
        )
        
        currentExercise.completedSets.add(completedSet)
        currentExercise.currentSetIndex++
        
        // Vérifier si l'exercice est terminé
        if (currentExercise.currentSetIndex >= currentExercise.recommendation.seriesRecommandees) {
            currentExercise.isCompleted = true
            logger.success("TRAINING", "Exercice ${currentExercise.machine.nom} terminé")
        }
        
        _activeWorkout.value = activeSession.copy()
        
        logger.debug("TRAINING", "Série complétée: ${weight}kg x ${reps} reps")
        return true
    }
    
    /**
     * Passer à l'exercice suivant
     */
    fun moveToNextExercise(): Boolean {
        val activeSession = _activeWorkout.value ?: return false
        
        if (activeSession.currentExerciseIndex < activeSession.exercises.size - 1) {
            val updatedSession = activeSession.copy(
                currentExerciseIndex = activeSession.currentExerciseIndex + 1
            )
            _activeWorkout.value = updatedSession
            
            val nextExercise = updatedSession.getCurrentExercise()
            logger.info("TRAINING", "Passage à l'exercice suivant: ${nextExercise?.machine?.nom}")
            return true
        }
        return false
    }
    
    /**
     * Revenir à l'exercice précédent
     */
    fun moveToPreviousExercise(): Boolean {
        val activeSession = _activeWorkout.value ?: return false
        
        if (activeSession.currentExerciseIndex > 0) {
            val updatedSession = activeSession.copy(
                currentExerciseIndex = activeSession.currentExerciseIndex - 1
            )
            _activeWorkout.value = updatedSession
            
            val previousExercise = updatedSession.getCurrentExercise()
            logger.info("TRAINING", "Retour à l'exercice précédent: ${previousExercise?.machine?.nom}")
            return true
        }
        return false
    }
    
    /**
     * Terminer et sauvegarder la séance
     */
    suspend fun completeAndSaveWorkout(): Result<WorkoutSaveResponse> {
        val activeSession = _activeWorkout.value 
            ?: return Result.failure(Exception("Aucune séance active"))
        
        return try {
            logger.info("TRAINING", "Sauvegarde de la séance: ${activeSession.workoutName}")
            
            // Calculer la durée
            val durationMinutes = ((System.currentTimeMillis() - activeSession.startTime) / 60000).toInt()
            
            // Convertir en format API
            val exercises = activeSession.exercises.map { activeExercise ->
                val totalReps = activeExercise.completedSets.sumOf { it.reps }
                val averageWeight = if (activeExercise.completedSets.isNotEmpty()) {
                    activeExercise.completedSets.map { it.weight }.average()
                } else activeExercise.recommendation.poidsRecommande
                
                ExerciseRecord(
                    nom = activeExercise.machine.nom,
                    poids = averageWeight,
                    series = activeExercise.completedSets.size.coerceAtLeast(1),
                    reps = if (activeExercise.completedSets.isNotEmpty()) {
                        (totalReps / activeExercise.completedSets.size.coerceAtLeast(1))
                    } else activeExercise.recommendation.repetitionsRecommandees,
                    repos = activeExercise.recommendation.reposRecommande,
                    typeExercice = if (activeExercise.machine.isCardio()) "DUREE" else "REPETITIONS"
                )
            }
            
            val workoutSession = WorkoutSession(
                nom = activeSession.workoutName,
                date = java.time.LocalDate.now().toString(),
                duree = durationMinutes.coerceAtLeast(1),
                exercices = exercises,
                noteRessenti = 7, // Pourra être personnalisé plus tard
                commentaire = "Séance complétée via l'application"
            )
            
            val response = apiService.saveWorkout(workoutSession)
            
            if (response.isSuccessful) {
                val saveResponse = response.body()
                if (saveResponse != null) {
                    // Marquer la séance comme terminée et la nettoyer
                    _activeWorkout.value = null
                    logger.success("TRAINING", "Séance sauvegardée avec succès: ID ${saveResponse.id}")
                    Result.success(saveResponse)
                } else {
                    logger.error("TRAINING", "Réponse de sauvegarde vide")
                    Result.failure(Exception("Erreur de sauvegarde"))
                }
            } else {
                val errorMsg = "Erreur sauvegarde: ${response.code()} - ${response.message()}"
                logger.error("TRAINING", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("TRAINING", "Erreur lors de la sauvegarde", exception = e)
            Result.failure(e)
        }
    }
    
    /**
     * Abandonner la séance en cours
     */
    fun cancelWorkout() {
        val activeSession = _activeWorkout.value
        if (activeSession != null) {
            logger.info("TRAINING", "Abandon de la séance: ${activeSession.workoutName}")
            _activeWorkout.value = null
        }
    }
    
    /**
     * Vérifier si toute la séance est terminée
     */
    fun isWorkoutCompleted(): Boolean {
        val activeSession = _activeWorkout.value ?: return false
        return activeSession.exercises.all { it.isCompleted }
    }
    
    /**
     * Obtenir le pourcentage de progression de la séance
     */
    fun getWorkoutProgress(): Float {
        val activeSession = _activeWorkout.value ?: return 0f
        val totalExercises = activeSession.exercises.size
        val completedExercises = activeSession.exercises.count { it.isCompleted }
        
        return if (totalExercises > 0) {
            completedExercises.toFloat() / totalExercises
        } else 0f
    }
    
    // ==================== MÉTHODES PRIVÉES ====================
    
    /**
     * Créer une recommandation par défaut pour une machine
     */
    private fun createDefaultRecommendation(machine: Machine): MachineRecommendation {
        return MachineRecommendation(
            machineId = machine.id,
            machineNom = machine.nom,
            poidsRecommande = machine.poidsMinimum + machine.incrementPoids,
            seriesRecommandees = 3,
            repetitionsRecommandees = if (machine.isCardio()) 20 else 10,
            reposRecommande = 90,
            notes = "Recommandation par défaut - première utilisation",
            recommandationSource = "default"
        )
    }
}

/**
 * Séance d'entraînement active
 */
data class ActiveWorkoutSession(
    val workoutName: String,
    val exercises: List<ActiveExercise>,
    val startTime: Long = System.currentTimeMillis(),
    var currentExerciseIndex: Int = 0,
    var isCompleted: Boolean = false
) {
    fun getCurrentExercise(): ActiveExercise? {
        return if (currentExerciseIndex < exercises.size) {
            exercises[currentExerciseIndex]
        } else null
    }
    
    fun getProgress(): Float {
        val totalExercises = exercises.size
        val completedExercises = exercises.count { it.isCompleted }
        return if (totalExercises > 0) completedExercises.toFloat() / totalExercises else 0f
    }
    
    fun getDurationMinutes(): Int {
        return ((System.currentTimeMillis() - startTime) / 60000).toInt()
    }
}