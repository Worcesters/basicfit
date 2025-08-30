package com.basicfit.app.data.repositories

import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.models.AppLog
import com.basicfit.app.data.models.LogLevel
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Repository pour la gestion des logs et du monitoring système
 * Gère l'affichage des logs, statistiques et exportation
 */
class LogRepository(
    private val apiService: BasicFitApiService,
    private val logger: Logger
) {

    // Liste des logs
    private val _logs = MutableStateFlow<List<AppLog>>(emptyList())
    val logs: StateFlow<List<AppLog>> = _logs.asStateFlow()

    // État de chargement
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Filtres
    private val _selectedLogLevel = MutableStateFlow(LogLevel.INFO)
    val selectedLogLevel: StateFlow<LogLevel> = _selectedLogLevel.asStateFlow()

    private val _selectedCategory = MutableStateFlow("ALL")
    val selectedCategory: StateFlow<String> = _selectedCategory.asStateFlow()

    // Logs locaux en mémoire (pour les logs en temps réel)
    private val localLogs = mutableListOf<AppLog>()

    /**
     * Charger les logs depuis l'API
     */
    suspend fun loadServerLogs(): Result<List<AppLog>> {
        return try {
            _isLoading.value = true
            logger.info("LOG", "Chargement logs serveur")

            val response = apiService.getSystemLogs()

            if (response.isSuccessful) {
                val serverLogs = response.body()?.logs ?: emptyList()

                // Combiner avec les logs locaux
                val allLogs: List<AppLog> = (localLogs + serverLogs).sortedByDescending { log -> log.timestamp }
                _logs.value = allLogs

                logger.success("LOG", "Logs chargés: ${serverLogs.size} serveur, ${localLogs.size} local")
                Result.success(allLogs)
            } else {
                val errorMsg = "Erreur chargement logs: ${response.code()}"
                logger.error("LOG", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("LOG", "Erreur lors du chargement des logs", exception = e)

            // En cas d'erreur, afficher au moins les logs locaux
            _logs.value = localLogs.sortedByDescending { it.timestamp }
            Result.failure(e)
        } finally {
            _isLoading.value = false
        }
    }

    /**
     * Ajouter un log local
     */
    fun addLocalLog(
        level: LogLevel,
        tag: String,
        message: String,
        exception: Throwable? = null
    ) {
        val log = AppLog(
            id = System.currentTimeMillis().toString(),
            level = level,
            tag = tag,
            message = message,
            details = exception?.message,
            exception = exception
        )

        localLogs.add(0, log) // Ajouter au début

        // Limiter à 1000 logs locaux max
        if (localLogs.size > 1000) {
            localLogs.removeAt(localLogs.size - 1)
        }

        // Mettre à jour la liste filtrée
        applyFilters()

        logger.debug("LOG", "Log local ajouté: [$level] $tag - $message")
    }

    /**
     * Envoyer les logs locaux vers le serveur
     */
    suspend fun uploadLocalLogs(): Result<Boolean> {
        return try {
            if (localLogs.isEmpty()) {
                return Result.success(true)
            }

            logger.info("LOG", "Upload ${localLogs.size} logs vers serveur")

            val uploadRequest = LogUploadRequest(logs = localLogs)
            val response = apiService.uploadLogs(uploadRequest)

            if (response.isSuccessful) {
                val result = response.body()
                if (result?.success == true) {
                    logger.success("LOG", "Upload logs réussi: ${result.uploadedCount} logs")

                    // Optionnel: vider les logs locaux après upload réussi
                    // localLogs.clear()

                    Result.success(true)
                } else {
                    logger.error("LOG", "Échec upload logs: ${result?.message}")
                    Result.failure(Exception(result?.message ?: "Upload failed"))
                }
            } else {
                val errorMsg = "Erreur upload logs: ${response.code()}"
                logger.error("LOG", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("LOG", "Erreur lors de l'upload des logs", exception = e)
            Result.failure(e)
        }
    }

    /**
     * Définir le filtre de niveau
     */
    fun setLogLevelFilter(level: LogLevel) {
        _selectedLogLevel.value = level
        applyFilters()
        logger.debug("LOG", "Filtre niveau: $level")
    }

    /**
     * Définir le filtre de catégorie
     */
    fun setCategoryFilter(category: String) {
        _selectedCategory.value = category
        applyFilters()
        logger.debug("LOG", "Filtre catégorie: $category")
    }

    /**
     * Effacer tous les logs locaux
     */
    fun clearLocalLogs() {
        localLogs.clear()
        applyFilters()
        logger.info("LOG", "Logs locaux effacés")
    }

    /**
     * Supprimer les logs serveur
     */
    suspend fun clearServerLogs(): Result<Boolean> {
        return try {
            logger.info("LOG", "Suppression logs serveur")

            val response = apiService.clearSystemLogs()

            if (response.isSuccessful) {
                logger.success("LOG", "Logs serveur supprimés")

                // Recharger pour afficher seulement les logs locaux
                _logs.value = localLogs.sortedByDescending { it.timestamp }

                Result.success(true)
            } else {
                val errorMsg = "Erreur suppression logs: ${response.code()}"
                logger.error("LOG", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("LOG", "Erreur lors de la suppression des logs serveur", exception = e)
            Result.failure(e)
        }
    }

    /**
     * Obtenir les statistiques des logs
     */
    fun getLogStats(): LogStats {
        val allLogs = _logs.value

        val errorCount = allLogs.count { it.level == LogLevel.ERROR }
        val warningCount = allLogs.count { it.level == LogLevel.WARNING }
        val infoCount = allLogs.count { it.level == LogLevel.INFO }
        val debugCount = allLogs.count { it.level == LogLevel.DEBUG }

        val categoryStats = allLogs.groupBy { it.tag }
            .mapValues { it.value.size }
            .toList()
            .sortedByDescending { it.second }
            .take(5)

        val recentErrors = allLogs
            .filter { it.level == LogLevel.ERROR }
            .take(10)

        return LogStats(
            totalLogs = allLogs.size,
            errorCount = errorCount,
            warningCount = warningCount,
            infoCount = infoCount,
            debugCount = debugCount,
            topCategories = categoryStats,
            recentErrors = recentErrors
        )
    }

    /**
     * Exporter les logs en format texte
     */
    fun exportLogsAsText(): String {
        val logs = _logs.value
        val exportBuilder = StringBuilder()

        exportBuilder.appendLine("=== EXPORT LOGS BasicFit ===")
        exportBuilder.appendLine("Date d'export: ${LocalDateTime.now().format(DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss"))}")
        exportBuilder.appendLine("Nombre de logs: ${logs.size}")
        exportBuilder.appendLine("=====================================")
        exportBuilder.appendLine()

        logs.forEach { log ->
            exportBuilder.appendLine("[${log.level}] ${log.getFormattedTimestamp()} - ${log.tag}")
            exportBuilder.appendLine("Message: ${log.message}")

            log.exception?.let { exception ->
                exportBuilder.appendLine("Exception: ${exception.message}")
            }

            exportBuilder.appendLine("---")
            exportBuilder.appendLine()
        }

        logger.info("LOG", "Export logs généré: ${logs.size} entrées")
        return exportBuilder.toString()
    }

    /**
     * Obtenir les catégories disponibles
     */
    fun getAvailableCategories(): List<String> {
        val categories = _logs.value.map { it.tag }.distinct().sorted()
        return listOf("ALL") + categories
    }

    /**
     * Obtenir les niveaux disponibles
     */
    fun getAvailableLogLevels(): List<LogLevel> {
        return listOf(LogLevel.INFO, LogLevel.ERROR, LogLevel.WARNING, LogLevel.DEBUG, LogLevel.SUCCESS)
    }

    // ==================== MÉTHODES PRIVÉES ====================

    /**
     * Appliquer les filtres aux logs
     */
    private fun applyFilters() {
        val level = _selectedLogLevel.value
        val category = _selectedCategory.value

        var filteredLogs = (localLogs + (_logs.value - localLogs)).sortedByDescending { it.timestamp }

        if (level != LogLevel.INFO) {
            filteredLogs = filteredLogs.filter { it.level == level }
        }

        if (category != "ALL") {
            filteredLogs = filteredLogs.filter { it.tag == category }
        }

        _logs.value = filteredLogs
    }
}

/**
 * Statistiques des logs
 */
data class LogStats(
    val totalLogs: Int,
    val errorCount: Int,
    val warningCount: Int,
    val infoCount: Int,
    val debugCount: Int,
    val topCategories: List<Pair<String, Int>>,
    val recentErrors: List<AppLog>
)

/**
 * Requête d'upload de logs
 */
data class LogUploadRequest(
    val logs: List<AppLog>
)

/**
 * Réponse d'upload de logs
 */
data class LogUploadResponse(
    val success: Boolean,
    val message: String,
    val uploadedCount: Int
)

/**
 * Réponse des logs système
 */
data class SystemLogsResponse(
    val logs: List<AppLog>,
    val totalCount: Int
)