package com.basicfit.app.data

import android.content.Context
import android.content.SharedPreferences
import com.basicfit.app.data.api.*
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.text.SimpleDateFormat
import java.util.*

/**
 * Repository hybride qui gère les données d'entraînement
 * Utilise l'API Django si disponible, sinon stockage local
 */
class WorkoutRepository(
    private val context: Context,
    private val authManager: AuthManager
) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("workout_data", Context.MODE_PRIVATE)

    private val apiRepository = ApiRepository()
    private val gson = Gson()

    // États
    private val _workoutHistory = MutableStateFlow<List<WorkoutSession>>(emptyList())
    val workoutHistory: StateFlow<List<WorkoutSession>> = _workoutHistory

    private val _workoutStats = MutableStateFlow<WorkoutStats?>(null)
    val workoutStats: StateFlow<WorkoutStats?> = _workoutStats

    private val _isOnlineMode = MutableStateFlow(false)
    val isOnlineMode: StateFlow<Boolean> = _isOnlineMode

    // Clés SharedPreferences
    private companion object {
        const val KEY_WORKOUT_HISTORY = "workout_history"
        const val KEY_WORKOUT_STATS = "workout_stats"
        const val KEY_IS_ONLINE_MODE = "is_online_mode"
        const val MAX_HISTORY_SIZE = 50
    }

    init {
        // Charger les données locales au démarrage
        loadLocalData()
    }

    /**
     * Activer/désactiver le mode en ligne
     */
    suspend fun setOnlineMode(enabled: Boolean) {
        _isOnlineMode.value = enabled
        prefs.edit().putBoolean(KEY_IS_ONLINE_MODE, enabled).apply()

        if (enabled) {
            // Synchroniser avec l'API
            syncWithApi()
        } else {
            // Utiliser les données locales
            loadLocalData()
        }
    }

    /**
     * Synchroniser avec l'API Django
     */
    suspend fun syncWithApi(): Result<String> {
        return try {
            val token = authManager.getToken()
            if (token == null) {
                _isOnlineMode.value = false
                return Result.failure(Exception("Non authentifié"))
            }

            // Récupérer les statistiques
            val statsResult = apiRepository.getWorkoutStats(token)
            if (statsResult.isSuccess) {
                val stats = statsResult.getOrNull()
                if (stats != null) {
                    val workoutStats = WorkoutStats(
                        total_seances = stats.total_seances,
                        total_minutes = stats.total_minutes,
                        total_calories = stats.total_calories,
                        seances_excellentes = stats.seances_excellentes,
                        record_poids = stats.record_poids,
                        exercices_favoris = stats.exercices_favoris,
                        progression_generale = stats.progression_generale
                    )
                    _workoutStats.value = workoutStats
                    saveWorkoutStats(workoutStats)
                }
            }

            // Récupérer l'historique
            val historyResult = apiRepository.getWorkoutHistory(token)
            if (historyResult.isSuccess) {
                val history = historyResult.getOrNull()
                if (history != null) {
                    _workoutHistory.value = history.results
                    saveWorkoutHistory(history.results)
                }
            }

            _isOnlineMode.value = true
            Result.success("Synchronisation réussie")

        } catch (e: Exception) {
            _isOnlineMode.value = false
            loadLocalData() // Retour aux données locales
            Result.failure(e)
        }
    }

    /**
     * Sauvegarder une séance
     */
    suspend fun saveWorkoutSession(
        nom: String,
        duree: Int,
        exercices: List<ExerciceData>,
        noteRessenti: Int = 7,
        commentaire: String = ""
    ): Result<String> {
        val seanceData = SeanceData(
            nom = nom,
            duree = duree,
            note_ressenti = noteRessenti,
            commentaire = commentaire,
            exercices = exercices
        )

        return if (_isOnlineMode.value) {
            // Sauvegarder via API
            saveWorkoutSessionOnline(seanceData)
        } else {
            // Sauvegarder localement
            saveWorkoutSessionLocal(seanceData)
        }
    }

    /**
     * Sauvegarder via API
     */
    private suspend fun saveWorkoutSessionOnline(seanceData: SeanceData): Result<String> {
        return try {
            val token = authManager.getToken()
            if (token == null) {
                return saveWorkoutSessionLocal(seanceData) // Fallback local
            }

            val result = apiRepository.sauvegarderSeance(token, seanceData)
            if (result.isSuccess) {
                val response = result.getOrNull()
                if (response?.success == true) {
                    // Synchroniser après la sauvegarde
                    syncWithApi()
                    Result.success("Séance sauvegardée en ligne")
                } else {
                    saveWorkoutSessionLocal(seanceData) // Fallback local
                }
            } else {
                saveWorkoutSessionLocal(seanceData) // Fallback local
            }
        } catch (e: Exception) {
            saveWorkoutSessionLocal(seanceData) // Fallback local
        }
    }

    /**
     * Sauvegarder localement
     */
    private fun saveWorkoutSessionLocal(seanceData: SeanceData): Result<String> {
        return try {
            val currentHistory = _workoutHistory.value.toMutableList()

            // Créer une nouvelle session
            val newSession = WorkoutSession(
                id = System.currentTimeMillis().toInt(),
                nom = seanceData.nom,
                date_debut = getCurrentDateString(),
                date_fin = getCurrentDateString(),
                duree_reelle = seanceData.duree,
                statut = "TERMINEE",
                nombre_exercices = seanceData.exercices.size,
                note_ressenti = seanceData.note_ressenti,
                exercices = seanceData.exercices.map { exercice ->
                    ExerciceSession(
                        machine = MachineData(
                            nom = exercice.nom,
                            groupe_musculaire = "Général"
                        ),
                        repetitions_realisees = exercice.reps,
                        poids_utilise = exercice.poids,
                        nombre_series = exercice.series,
                        note_ressenti = seanceData.note_ressenti
                    )
                }
            )

            // Ajouter au début de la liste
            currentHistory.add(0, newSession)

            // Limiter la taille
            if (currentHistory.size > MAX_HISTORY_SIZE) {
                currentHistory.removeAt(currentHistory.size - 1)
            }

            _workoutHistory.value = currentHistory
            saveWorkoutHistory(currentHistory)

            // Recalculer les stats
            updateLocalStats(currentHistory)

            Result.success("Séance sauvegardée localement")

        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Charger les données locales
     */
    private fun loadLocalData() {
        // Charger l'historique
        val historyJson = prefs.getString(KEY_WORKOUT_HISTORY, null)
        if (historyJson != null) {
            try {
                val type = object : TypeToken<List<WorkoutSession>>() {}.type
                val history = gson.fromJson<List<WorkoutSession>>(historyJson, type)
                _workoutHistory.value = history
            } catch (e: Exception) {
                _workoutHistory.value = getDefaultWorkoutHistory()
            }
        } else {
            _workoutHistory.value = getDefaultWorkoutHistory()
        }

        // Charger les stats
        val statsJson = prefs.getString(KEY_WORKOUT_STATS, null)
        if (statsJson != null) {
            try {
                val stats = gson.fromJson(statsJson, WorkoutStats::class.java)
                _workoutStats.value = stats
            } catch (e: Exception) {
                updateLocalStats(_workoutHistory.value)
            }
        } else {
            updateLocalStats(_workoutHistory.value)
        }

        // Mode en ligne
        _isOnlineMode.value = prefs.getBoolean(KEY_IS_ONLINE_MODE, false)
    }

    /**
     * Sauvegarder l'historique localement
     */
    private fun saveWorkoutHistory(history: List<WorkoutSession>) {
        prefs.edit()
            .putString(KEY_WORKOUT_HISTORY, gson.toJson(history))
            .apply()
    }

    /**
     * Sauvegarder les stats localement
     */
    private fun saveWorkoutStats(stats: WorkoutStats) {
        prefs.edit()
            .putString(KEY_WORKOUT_STATS, gson.toJson(stats))
            .apply()
    }

    /**
     * Mettre à jour les stats locales
     */
    private fun updateLocalStats(history: List<WorkoutSession>) {
        val totalSeances = history.size
        val totalMinutes = history.sumOf { it.duree_reelle ?: 0 }
        val totalCalories = totalMinutes * 5 // Estimation
        val seancesExcellentes = history.count { (it.note_ressenti ?: 0) >= 8 }
        val recordPoids = history.flatMap { it.exercices ?: emptyList() }
            .maxOfOrNull { it.poids_utilise } ?: 0f

        val exercicesFavoris = history
            .flatMap { it.exercices ?: emptyList() }
            .groupBy { it.machine.nom }
            .toList()
            .sortedByDescending { it.second.size }
            .take(3)
            .map { it.first }

        val stats = WorkoutStats(
            total_seances = totalSeances,
            total_minutes = totalMinutes,
            total_calories = totalCalories,
            seances_excellentes = seancesExcellentes,
            record_poids = recordPoids,
            exercices_favoris = exercicesFavoris,
            progression_generale = if (totalSeances > 0) 75.0f else 0f
        )

        _workoutStats.value = stats
        saveWorkoutStats(stats)
    }

    /**
     * Effacer toutes les données
     */
    fun clearAllData() {
        prefs.edit()
            .remove(KEY_WORKOUT_HISTORY)
            .remove(KEY_WORKOUT_STATS)
            .putBoolean(KEY_IS_ONLINE_MODE, false)
            .apply()

        _workoutHistory.value = emptyList()
        _workoutStats.value = null
        _isOnlineMode.value = false
    }

    /**
     * Obtenir la date actuelle formatée
     */
    private fun getCurrentDateString(): String {
        val format = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
        return format.format(Date())
    }

    /**
     * Historique par défaut pour les tests
     */
    private fun getDefaultWorkoutHistory(): List<WorkoutSession> {
        return listOf(
            WorkoutSession(
                id = 1,
                nom = "Séance test",
                date_debut = getCurrentDateString(),
                date_fin = getCurrentDateString(),
                duree_reelle = 45,
                statut = "TERMINEE",
                nombre_exercices = 3,
                note_ressenti = 8,
                exercices = listOf(
                    ExerciceSession(
                        machine = MachineData("Développé couché", "Pectoraux"),
                        repetitions_realisees = 30,
                        poids_utilise = 80f,
                        nombre_series = 3,
                        note_ressenti = 8
                    )
                )
            )
        )
    }
}