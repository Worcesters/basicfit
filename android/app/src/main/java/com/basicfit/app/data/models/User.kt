package com.basicfit.app.data.models

import com.google.gson.annotations.SerializedName
import java.time.LocalDate

/**
 * Modèle de données pour l'utilisateur
 */
data class User(
    @SerializedName("id") val id: Int = 0,
    @SerializedName("email") val email: String = "",
    @SerializedName("nom") val nom: String = "",
    @SerializedName("prenom") val prenom: String = "",
    @SerializedName("date_naissance") val dateNaissance: String = "",
    @SerializedName("poids") val poids: Double = 0.0,
    @SerializedName("taille") val taille: Int = 0,
    @SerializedName("genre") val genre: String = "",
    @SerializedName("niveau_activite") val niveauActivite: String = "",
    @SerializedName("objectif") val objectif: String = "MAINTENIR"
) {
    fun getAge(): Int? {
        return try {
            if (dateNaissance.isNotEmpty()) {
                val birthDate = LocalDate.parse(dateNaissance)
                val now = LocalDate.now()
                now.year - birthDate.year
            } else null
        } catch (e: Exception) {
            null
        }
    }
    
    fun getDisplayName(): String = if (nom.isNotEmpty() && prenom.isNotEmpty()) {
        "$prenom $nom"
    } else if (nom.isNotEmpty()) {
        nom
    } else {
        email.substringBefore("@")
    }
}

/**
 * Données du profil utilisateur pour mise à jour
 */
data class UserProfileUpdate(
    @SerializedName("nom") val nom: String,
    @SerializedName("prenom") val prenom: String,
    @SerializedName("date_naissance") val dateNaissance: String,
    @SerializedName("poids") val poids: Double,
    @SerializedName("taille") val taille: Int,
    @SerializedName("genre") val genre: String,
    @SerializedName("niveau_activite") val niveauActivite: String,
    @SerializedName("objectif") val objectif: String
)

/**
 * Statistiques utilisateur
 */
data class UserStatistics(
    @SerializedName("total_seances") val totalSeances: Int = 0,
    @SerializedName("total_minutes") val totalMinutes: Int = 0,
    @SerializedName("total_calories") val totalCalories: Int = 0,
    @SerializedName("seances_excellentes") val seancesExcellentes: Int = 0,
    @SerializedName("record_poids") val recordPoids: Double = 0.0,
    @SerializedName("exercices_favoris") val exercicesFavoris: List<String> = emptyList(),
    @SerializedName("progression_generale") val progressionGenerale: Double = 0.0
)