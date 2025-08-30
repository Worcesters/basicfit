package com.basicfit.app.presentation.log

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.basicfit.app.data.models.AppLog
import com.basicfit.app.data.models.LogLevel
import com.basicfit.app.data.repositories.LogRepository
import com.basicfit.app.data.repositories.LogStats
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * ViewModel pour l'onglet Log
 * Gère l'affichage des logs, filtres et statistiques de monitoring
 */
class LogViewModel(
    private val logRepository: LogRepository,
    private val logger: Logger
) : ViewModel() {

    // États des données
    val logs = logRepository.logs
    val isLoading = logRepository.isLoading
    val selectedLogLevel = logRepository.selectedLogLevel
    val selectedCategory = logRepository.selectedCategory

    // État de l'interface
    private val _currentView = MutableStateFlow(LogView.LOGS)
    val currentView: StateFlow<LogView> = _currentView.asStateFlow()

    private val _selectedLog = MutableStateFlow<AppLog?>(null)
    val selectedLog: StateFlow<AppLog?> = _selectedLog.asStateFlow()

    // États de messages
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    // Statistiques
    private val _logStats = MutableStateFlow<LogStats?>(null)
    val logStats: StateFlow<LogStats?> = _logStats.asStateFlow()

    // Options de filtres
    private val _availableCategories = MutableStateFlow<List<String>>(emptyList())
    val availableCategories: StateFlow<List<String>> = _availableCategories.asStateFlow()

    private val _availableLogLevels = MutableStateFlow<List<LogLevel>>(emptyList())
    val availableLogLevels: StateFlow<List<LogLevel>> = _availableLogLevels.asStateFlow()

    // État de recherche
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _filteredLogs = MutableStateFlow<List<AppLog>>(emptyList())
    val filteredLogs: StateFlow<List<AppLog>> = _filteredLogs.asStateFlow()

    init {
        logger.info("LOG", "Initialisation du LogViewModel")

        // Observer les changements de logs pour mettre à jour les filtres et stats
        viewModelScope.launch {
            logs.collect { logList ->
                updateAvailableFilters()
                updateStats()
                applySearchFilter(logList)
            }
        }

        // Observer les changements de recherche
        viewModelScope.launch {
            combine(logs, searchQuery) { logList: List<AppLog>, query: String ->
                Pair(logList, query)
            }.collect { (logList, query) ->
                applySearchFilter(logList, query)
            }
        }

        // Charger les données au démarrage
        loadInitialData()

        // Ajouter quelques logs de test au démarrage
        addTestLogs()
    }

    /**
     * Charger les données initiales
     */
    private fun loadInitialData() {
        viewModelScope.launch {
            logger.info("LOG", "Chargement données logs...")

            val result = logRepository.loadServerLogs()
            if (result.isFailure) {
                val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de chargement"
                logger.error("LOG", "Erreur chargement logs: $errorMsg")
                _errorMessage.value = "Impossible de charger les logs serveur"
            } else {
                logger.success("LOG", "Logs chargés avec succès")
            }
        }
    }

    /**
     * Ajouter des logs de test pour démonstration
     */
    private fun addTestLogs() {
        logRepository.addLocalLog(LogLevel.INFO, "SYSTEM", "Application démarrée")
        logRepository.addLocalLog(LogLevel.SUCCESS, "AUTH", "Connexion utilisateur réussie")
        logRepository.addLocalLog(LogLevel.DEBUG, "API", "Appel API: /api/users/profile")
        logRepository.addLocalLog(LogLevel.WARNING, "NETWORK", "Connexion lente détectée")
        logRepository.addLocalLog(LogLevel.ERROR, "DATABASE", "Échec de synchronisation des données",
            Exception("Connection timeout"))
    }

    /**
     * Changer la vue affichée
     */
    fun setView(view: LogView) {
        _currentView.value = view
        logger.debug("LOG", "Vue changée: $view")
    }

    /**
     * Sélectionner un log pour affichage détaillé
     */
    fun selectLog(log: AppLog) {
        _selectedLog.value = log
        logger.debug("LOG", "Log sélectionné: ${log.id}")
    }

    /**
     * Désélectionner le log
     */
    fun clearSelectedLog() {
        _selectedLog.value = null
    }

    /**
     * Définir le filtre de niveau
     */
    fun setLogLevelFilter(level: LogLevel) {
        logRepository.setLogLevelFilter(level)
    }

    /**
     * Définir le filtre de catégorie
     */
    fun setCategoryFilter(category: String) {
        logRepository.setCategoryFilter(category)
    }

    /**
     * Mettre à jour la recherche
     */
    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
        logger.debug("LOG", "Recherche logs: '$query'")
    }

    /**
     * Recharger les logs depuis le serveur
     */
    fun refreshLogs() {
        viewModelScope.launch {
            logger.info("LOG", "Rafraîchissement des logs...")

            val result = logRepository.loadServerLogs()
            if (result.isSuccess) {
                _successMessage.value = "Logs mis à jour"
                logger.success("LOG", "Logs rafraîchis")
            } else {
                val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de rechargement"
                _errorMessage.value = errorMsg
                logger.error("LOG", "Erreur rafraîchissement: $errorMsg")
            }
        }
    }

    /**
     * Uploader les logs locaux vers le serveur
     */
    fun uploadLocalLogs() {
        viewModelScope.launch {
            logger.info("LOG", "Upload des logs locaux...")

            val result = logRepository.uploadLocalLogs()
            if (result.isSuccess) {
                _successMessage.value = "Logs synchronisés avec le serveur"
                logger.success("LOG", "Upload logs réussi")
            } else {
                val errorMsg = result.exceptionOrNull()?.message ?: "Erreur d'upload"
                _errorMessage.value = errorMsg
                logger.error("LOG", "Erreur upload: $errorMsg")
            }
        }
    }

    /**
     * Effacer les logs locaux
     */
    fun clearLocalLogs() {
        logRepository.clearLocalLogs()
        _successMessage.value = "Logs locaux effacés"
        logger.info("LOG", "Logs locaux effacés via UI")
    }

    /**
     * Effacer les logs serveur
     */
    fun clearServerLogs() {
        viewModelScope.launch {
            logger.info("LOG", "Suppression des logs serveur...")

            val result = logRepository.clearServerLogs()
            if (result.isSuccess) {
                _successMessage.value = "Logs serveur supprimés"
                logger.success("LOG", "Logs serveur supprimés")
            } else {
                val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de suppression"
                _errorMessage.value = errorMsg
                logger.error("LOG", "Erreur suppression serveur: $errorMsg")
            }
        }
    }

    /**
     * Exporter les logs
     */
    fun exportLogs(): String {
        val exportContent = logRepository.exportLogsAsText()
        _successMessage.value = "Export des logs généré"
        logger.info("LOG", "Export logs demandé via UI")
        return exportContent
    }

    /**
     * Ajouter un log de test
     */
    fun addTestLog(level: String, category: String, message: String) {
        val logLevel = when (level.uppercase()) {
            "ERROR" -> LogLevel.ERROR
            "WARNING" -> LogLevel.WARNING
            "INFO" -> LogLevel.INFO
            "DEBUG" -> LogLevel.DEBUG
            "SUCCESS" -> LogLevel.SUCCESS
            else -> LogLevel.INFO
        }

        val exception = if (level == "ERROR") {
            Exception("Exception de test pour démonstration")
        } else null

        logRepository.addLocalLog(logLevel, category, message, exception)
        _successMessage.value = "Log de test ajouté"
        logger.debug("LOG", "Log de test ajouté: [$level] $category - $message")
    }

    /**
     * Réinitialiser tous les filtres
     */
    fun resetFilters() {
        logRepository.setLogLevelFilter(LogLevel.INFO)
        logRepository.setCategoryFilter("ALL")
        _searchQuery.value = ""
        logger.debug("LOG", "Filtres réinitialisés")
    }

    /**
     * Obtenir le nombre de logs par niveau
     */
    fun getLogCountByLevel(): Map<String, Int> {
        val allLogs = logs.value
        return mapOf(
            "ERROR" to allLogs.count { it.level == LogLevel.ERROR },
            "WARNING" to allLogs.count { it.level == LogLevel.WARNING },
            "INFO" to allLogs.count { it.level == LogLevel.INFO },
            "DEBUG" to allLogs.count { it.level == LogLevel.DEBUG },
            "SUCCESS" to allLogs.count { it.level == LogLevel.SUCCESS }
        )
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
     * Mettre à jour les options de filtres disponibles
     */
    private fun updateAvailableFilters() {
        _availableCategories.value = logRepository.getAvailableCategories()
        _availableLogLevels.value = logRepository.getAvailableLogLevels()
    }

    /**
     * Mettre à jour les statistiques
     */
    private fun updateStats() {
        _logStats.value = logRepository.getLogStats()
    }

    /**
     * Appliquer le filtre de recherche textuelle
     */
    private fun applySearchFilter(logList: List<AppLog>, query: String = _searchQuery.value) {
        val filtered = if (query.isBlank()) {
            logList
        } else {
            logList.filter { log ->
                log.message.contains(query, ignoreCase = true) ||
                log.tag.contains(query, ignoreCase = true) ||
                log.level.displayName.contains(query, ignoreCase = true) ||
                (log.exception?.message?.contains(query, ignoreCase = true) == true)
            }
        }
        _filteredLogs.value = filtered
    }

    override fun onCleared() {
        super.onCleared()
        logger.debug("LOG", "LogViewModel détruit")
    }
}

/**
 * Vues possibles de l'onglet Log
 */
enum class LogView {
    LOGS,        // Vue principale des logs
    STATS,       // Vue des statistiques
    SETTINGS,    // Vue des paramètres et actions
    DETAILS      // Vue détaillée d'un log
}