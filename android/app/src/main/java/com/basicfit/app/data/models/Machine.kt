package com.basicfit.app.data.models

import com.google.gson.annotations.SerializedName

/**
 * Modèle de données pour les machines d'exercice
 */
data class Machine(
    @SerializedName("id") val id: Int,
    @SerializedName("nom") val nom: String,
    @SerializedName("description") val description: String = "",
    @SerializedName("instructions") val instructions: String = "",
    @SerializedName("groupe_musculaire") val groupeMusculaire: String = "",
    @SerializedName("categorie") val categorie: MachineCategory? = null,
    @SerializedName("categories") val categories: List<MachineCategory> = emptyList(),
    @SerializedName("image_gif") val imageGif: String? = null,
    @SerializedName("increment_poids") val incrementPoids: Double = 2.5,
    @SerializedName("poids_minimum") val poidsMinimum: Double = 0.0,
    @SerializedName("poids_maximum") val poidsMaximum: Double = 200.0,
    @SerializedName("type_exercice") val typeExercice: String = "REPETITIONS"
) {
    fun getCategoriesNames(): String = categories.joinToString(", ") { it.nom }
    
    fun getMainCategory(): String = categorie?.nom ?: categories.firstOrNull()?.nom ?: "AUTRE"
    
    fun isCardio(): Boolean = getMainCategory() == "CARDIO" || typeExercice == "DUREE"
}

/**
 * Catégorie de machine
 */
data class MachineCategory(
    @SerializedName("id") val id: Int,
    @SerializedName("nom") val nom: String,
    @SerializedName("description") val description: String = ""
)

/**
 * Recommandation d'exercice pour une machine
 */
data class MachineRecommendation(
    @SerializedName("machine_id") val machineId: Int,
    @SerializedName("machine_nom") val machineNom: String,
    @SerializedName("poids_recommande") val poidsRecommande: Double,
    @SerializedName("series_recommandees") val seriesRecommandees: Int,
    @SerializedName("repetitions_recommandees") val repetitionsRecommandees: Int,
    @SerializedName("repos_recommande") val reposRecommande: Int,
    @SerializedName("notes") val notes: String = "",
    @SerializedName("recommandation_source") val recommandationSource: String = "",
    @SerializedName("progression_info") val progressionInfo: ProgressionInfo? = null
)

/**
 * Informations de progression
 */
data class ProgressionInfo(
    @SerializedName("poids_actuel") val poidsActuel: Double,
    @SerializedName("taux_reussite") val tauxReussite: Double,
    @SerializedName("nombre_seances") val nombreSeances: Int,
    @SerializedName("dernier_1rm") val dernier1RM: Double?,
    @SerializedName("progression_totale") val progressionTotale: Double
)