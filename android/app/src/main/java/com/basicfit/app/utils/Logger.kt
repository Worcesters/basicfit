package com.basicfit.app.utils

import com.basicfit.app.data.models.AppLog
import com.basicfit.app.data.models.LogLevel
import com.basicfit.app.data.models.LogTag
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDateTime

/**
 * Système de logging centralisé pour l'application
 * Permet de tracer toutes les opérations et erreurs
 */
class Logger {
    
    private val _logs = MutableStateFlow<List<AppLog>>(emptyList())
    val logs: StateFlow<List<AppLog>> = _logs.asStateFlow()
    
    private val maxLogs = 1000 // Limite pour éviter une surcharge mémoire
    
    /**
     * Log de niveau DEBUG
     */
    fun debug(tag: String, message: String, details: String? = null) {
        addLog(LogLevel.DEBUG, tag, message, details)
    }
    
    /**
     * Log de niveau INFO
     */
    fun info(tag: String, message: String, details: String? = null) {
        addLog(LogLevel.INFO, tag, message, details)
    }
    
    /**
     * Log de niveau WARNING
     */
    fun warning(tag: String, message: String, details: String? = null) {
        addLog(LogLevel.WARNING, tag, message, details)
    }
    
    /**
     * Log de niveau ERROR
     */
    fun error(tag: String, message: String, details: String? = null, exception: Throwable? = null) {
        addLog(LogLevel.ERROR, tag, message, details, exception)
    }
    
    /**
     * Log de niveau SUCCESS
     */
    fun success(tag: String, message: String, details: String? = null) {
        addLog(LogLevel.SUCCESS, tag, message, details)
    }
    
    /**
     * Ajouter un log à la liste
     */
    private fun addLog(level: LogLevel, tag: String, message: String, details: String? = null, exception: Throwable? = null) {
        val currentLogs = _logs.value.toMutableList()
        
        val newLog = AppLog(
            timestamp = LocalDateTime.now(),
            level = level,
            tag = tag,
            message = message,
            details = details,
            exception = exception
        )
        
        currentLogs.add(0, newLog) // Ajouter au début pour avoir les plus récents en premier
        
        // Limiter le nombre de logs
        if (currentLogs.size > maxLogs) {
            currentLogs.removeAt(currentLogs.size - 1)
        }
        
        _logs.value = currentLogs
        
        // Log vers la console Android aussi
        when (level) {
            LogLevel.DEBUG -> android.util.Log.d(tag, message + if (details != null) " - $details" else "")
            LogLevel.INFO -> android.util.Log.i(tag, message + if (details != null) " - $details" else "")
            LogLevel.WARNING -> android.util.Log.w(tag, message + if (details != null) " - $details" else "")
            LogLevel.ERROR -> android.util.Log.e(tag, message + if (details != null) " - $details" else "", exception)
            LogLevel.SUCCESS -> android.util.Log.i(tag, "✓ $message" + if (details != null) " - $details" else "")
        }
    }
    
    /**
     * Filtrer les logs par niveau
     */
    fun getLogsByLevel(level: LogLevel): List<AppLog> {
        return _logs.value.filter { it.level == level }
    }
    
    /**
     * Filtrer les logs par tag
     */
    fun getLogsByTag(tag: String): List<AppLog> {
        return _logs.value.filter { it.tag == tag }
    }
    
    /**
     * Filtrer les logs par tag enum
     */
    fun getLogsByTag(tag: LogTag): List<AppLog> {
        return getLogsByTag(tag.name)
    }
    
    /**
     * Obtenir les logs des dernières 24h
     */
    fun getRecentLogs(): List<AppLog> {
        val oneDayAgo = LocalDateTime.now().minusDays(1)
        return _logs.value.filter { it.timestamp.isAfter(oneDayAgo) }
    }
    
    /**
     * Obtenir les logs d'erreur uniquement
     */
    fun getErrorLogs(): List<AppLog> {
        return _logs.value.filter { it.level == LogLevel.ERROR }
    }
    
    /**
     * Nettoyer tous les logs
     */
    fun clearLogs() {
        _logs.value = emptyList()
        info("SYSTEM", "Logs effacés")
    }
    
    /**
     * Obtenir un résumé des logs
     */
    fun getLogSummary(): LogSummary {
        val currentLogs = _logs.value
        return LogSummary(
            total = currentLogs.size,
            errors = currentLogs.count { it.level == LogLevel.ERROR },
            warnings = currentLogs.count { it.level == LogLevel.WARNING },
            success = currentLogs.count { it.level == LogLevel.SUCCESS },
            info = currentLogs.count { it.level == LogLevel.INFO },
            debug = currentLogs.count { it.level == LogLevel.DEBUG }
        )
    }
    
    /**
     * Exporter les logs en format texte
     */
    fun exportLogs(): String {
        val currentLogs = _logs.value
        val timestamp = LocalDateTime.now().format(
            java.time.format.DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss")
        )
        
        return buildString {
            appendLine("===== EXPORT LOGS BASICFIT =====")
            appendLine("Date d'export: $timestamp")
            appendLine("Total: ${currentLogs.size} logs")
            appendLine()
            
            currentLogs.forEach { log ->
                appendLine("[${log.getFormattedDate()} ${log.getFormattedTimestamp()}] ${log.level.displayName} - ${log.tag}")
                appendLine("Message: ${log.message}")
                if (log.details != null) {
                    appendLine("Détails: ${log.details}")
                }
                if (log.exception != null) {
                    appendLine("Exception: ${log.exception.message}")
                }
                appendLine("---")
            }
        }
    }
}

/**
 * Résumé des logs
 */
data class LogSummary(
    val total: Int,
    val errors: Int,
    val warnings: Int,
    val success: Int,
    val info: Int,
    val debug: Int
) {
    fun hasErrors(): Boolean = errors > 0
    fun hasWarnings(): Boolean = warnings > 0
}