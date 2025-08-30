package com.basicfit.app.data.models

import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Modèle pour les logs de l'application
 */
data class AppLog(
    val id: String = System.currentTimeMillis().toString(),
    val timestamp: LocalDateTime = LocalDateTime.now(),
    val level: LogLevel,
    val tag: String,
    val message: String,
    val details: String? = null,
    val exception: Throwable? = null
) {
    fun getFormattedTimestamp(): String {
        return timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss"))
    }
    
    fun getFormattedDate(): String {
        return timestamp.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"))
    }
    
    fun getFullMessage(): String = buildString {
        append("[$level] $tag: $message")
        if (details != null) {
            append("\nDétails: $details")
        }
        if (exception != null) {
            append("\nErreur: ${exception.message}")
        }
    }
}

/**
 * Niveaux de log
 */
enum class LogLevel(val displayName: String, val priority: Int) {
    DEBUG("Debug", 0),
    INFO("Info", 1),
    WARNING("Attention", 2),
    ERROR("Erreur", 3),
    SUCCESS("Succès", 1);
    
    fun getColor(): androidx.compose.ui.graphics.Color {
        return when (this) {
            DEBUG -> androidx.compose.ui.graphics.Color.Gray
            INFO -> androidx.compose.ui.graphics.Color.Blue
            WARNING -> androidx.compose.ui.graphics.Color(0xFFFF9800)
            ERROR -> androidx.compose.ui.graphics.Color.Red
            SUCCESS -> androidx.compose.ui.graphics.Color.Green
        }
    }
}

/**
 * Catégories de logs par onglet
 */
enum class LogTag(val displayName: String) {
    PROFILE("Profil"),
    MACHINE("Machine"),
    TRAINING("Entraînement"),
    CALENDAR("Calendrier"),
    AUTH("Authentification"),
    API("API"),
    DATABASE("Base de données"),
    SYSTEM("Système")
}