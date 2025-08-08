package com.basicfit.app

import android.util.Log
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Gestionnaire de logs global pour l'application BasicFit
 */
object AppLogger {
    
    data class LogEntry(
        val timestamp: String = LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")),
        val level: LogLevel,
        val tag: String,
        val message: String
    ) {
        override fun toString(): String = "[$timestamp] ${level.emoji} [$tag] $message"
    }
    
    enum class LogLevel(val emoji: String, val color: androidx.compose.ui.graphics.Color) {
        DEBUG("🔍", androidx.compose.ui.graphics.Color(0xFF6B7280)),
        INFO("ℹ️", androidx.compose.ui.graphics.Color(0xFF3B82F6)),
        SUCCESS("✅", androidx.compose.ui.graphics.Color(0xFF10B981)),
        WARNING("⚠️", androidx.compose.ui.graphics.Color(0xFFF59E0B)),
        ERROR("❌", androidx.compose.ui.graphics.Color(0xFFEF4444)),
        CSV("📊", androidx.compose.ui.graphics.Color(0xFF8B5CF6)),
        API("🌐", androidx.compose.ui.graphics.Color(0xFF06B6D4))
    }
    
    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs.asStateFlow()
    
    private val MAX_LOGS = 200 // Limitation pour éviter la surcharge mémoire
    
    fun d(tag: String, message: String) {
        addLog(LogLevel.DEBUG, tag, message)
        Log.d(tag, message)
    }
    
    fun i(tag: String, message: String) {
        addLog(LogLevel.INFO, tag, message)
        Log.i(tag, message)
    }
    
    fun success(tag: String, message: String) {
        addLog(LogLevel.SUCCESS, tag, message)
        Log.i(tag, "SUCCESS: $message")
    }
    
    fun w(tag: String, message: String) {
        addLog(LogLevel.WARNING, tag, message)
        Log.w(tag, message)
    }
    
    fun e(tag: String, message: String, throwable: Throwable? = null) {
        val fullMessage = if (throwable != null) {
            "$message\n${throwable.stackTraceToString()}"
        } else message
        
        addLog(LogLevel.ERROR, tag, fullMessage)
        Log.e(tag, message, throwable)
    }
    
    fun csv(tag: String, message: String) {
        addLog(LogLevel.CSV, tag, message)
        Log.i(tag, "CSV: $message")
    }
    
    fun api(tag: String, message: String) {
        addLog(LogLevel.API, tag, message)
        Log.i(tag, "API: $message")
    }
    
    private fun addLog(level: LogLevel, tag: String, message: String) {
        val currentLogs = _logs.value.toMutableList()
        currentLogs.add(0, LogEntry(level = level, tag = tag, message = message))
        
        // Limiter le nombre de logs
        if (currentLogs.size > MAX_LOGS) {
            currentLogs.removeAt(currentLogs.size - 1)
        }
        
        _logs.value = currentLogs
    }
    
    fun clear() {
        _logs.value = emptyList()
    }
    
    fun exportLogs(): String {
        return _logs.value.joinToString("\n") { it.toString() }
    }
}