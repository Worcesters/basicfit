package com.basicfit.app.presentation.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.basicfit.app.data.api.BasicFitApiService
import com.basicfit.app.data.models.User
import com.basicfit.app.data.api.UserProfileUpdate
import com.basicfit.app.data.models.UserStatistics
import com.basicfit.app.data.repositories.AuthRepository
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * ViewModel pour l'onglet Profil
 * Gère l'état du profil utilisateur et les statistiques
 */
class ProfileViewModel(
    private val authRepository: AuthRepository,
    private val apiService: BasicFitApiService,
    private val logger: Logger
) : ViewModel() {

    // État du profil utilisateur
    val currentUser = authRepository.currentUser

    // État des statistiques
    private val _statistics = MutableStateFlow<UserStatistics?>(null)
    val statistics: StateFlow<UserStatistics?> = _statistics.asStateFlow()

    // États de chargement
    private val _isLoadingProfile = MutableStateFlow(false)
    val isLoadingProfile: StateFlow<Boolean> = _isLoadingProfile.asStateFlow()

    private val _isLoadingStats = MutableStateFlow(false)
    val isLoadingStats: StateFlow<Boolean> = _isLoadingStats.asStateFlow()

    // États des erreurs
    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    // État du mode édition
    private val _isEditMode = MutableStateFlow(false)
    val isEditMode: StateFlow<Boolean> = _isEditMode.asStateFlow()

    // Messages de succès
    private val _successMessage = MutableStateFlow<String?>(null)
    val successMessage: StateFlow<String?> = _successMessage.asStateFlow()

    init {
        logger.info("PROFILE", "Initialisation du ProfileViewModel")
    }

    /**
     * Charger les statistiques utilisateur
     */
    fun loadStatistics() {
        viewModelScope.launch {
            try {
                _isLoadingStats.value = true
                _errorMessage.value = null

                logger.info("PROFILE", "Chargement des statistiques utilisateur...")

                val response = apiService.getUserStatistics()
                if (response.isSuccessful) {
                    val stats = response.body()
                    if (stats != null) {
                        _statistics.value = stats
                        logger.success("PROFILE", "Statistiques chargées: ${stats.totalSeances} séances")
                    } else {
                        logger.warning("PROFILE", "Statistiques vides reçues")
                        _statistics.value = UserStatistics() // Statistiques par défaut
                    }
                } else {
                    val errorMsg = "Erreur chargement statistiques: ${response.code()}"
                    logger.error("PROFILE", errorMsg)
                    _errorMessage.value = errorMsg
                }
            } catch (e: Exception) {
                logger.error("PROFILE", "Erreur lors du chargement des statistiques", exception = e)
                _errorMessage.value = "Erreur de connexion: ${e.message}"
            } finally {
                _isLoadingStats.value = false
            }
        }
    }

    /**
     * Rafraîchir le profil utilisateur
     */
    fun refreshProfile() {
        viewModelScope.launch {
            try {
                _isLoadingProfile.value = true
                _errorMessage.value = null

                logger.info("PROFILE", "Rafraîchissement du profil utilisateur...")

                val result = authRepository.refreshUserProfile()
                if (result.isSuccess) {
                    logger.success("PROFILE", "Profil rafraîchi avec succès")
                    _successMessage.value = "Profil mis à jour"
                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur inconnue"
                    logger.error("PROFILE", "Erreur rafraîchissement profil: $errorMsg")
                    _errorMessage.value = errorMsg
                }
            } catch (e: Exception) {
                logger.error("PROFILE", "Erreur lors du rafraîchissement", exception = e)
                _errorMessage.value = "Erreur de connexion: ${e.message}"
            } finally {
                _isLoadingProfile.value = false
            }
        }
    }

    /**
     * Mettre à jour le profil utilisateur
     */
    fun updateProfile(
        nom: String,
        prenom: String,
        dateNaissance: String,
        poids: Double,
        taille: Int,
        genre: String,
        niveauActivite: String,
        objectif: String
    ) {
        viewModelScope.launch {
            try {
                _isLoadingProfile.value = true
                _errorMessage.value = null

                logger.info("PROFILE", "Mise à jour du profil utilisateur...")

                val profileUpdate = UserProfileUpdate(
                    nom = nom.trim(),
                    prenom = prenom.trim(),
                    dateNaissance = dateNaissance,
                    poids = poids,
                    taille = taille,
                    genre = genre,
                    niveauActivite = niveauActivite,
                    objectif = objectif
                )

                val result = authRepository.updateUserProfile(profileUpdate)
                if (result.isSuccess) {
                    logger.success("PROFILE", "Profil mis à jour avec succès")
                    _successMessage.value = "Profil sauvegardé avec succès"
                    _isEditMode.value = false
                } else {
                    val errorMsg = result.exceptionOrNull()?.message ?: "Erreur de mise à jour"
                    logger.error("PROFILE", "Erreur mise à jour profil: $errorMsg")
                    _errorMessage.value = errorMsg
                }
            } catch (e: Exception) {
                logger.error("PROFILE", "Erreur lors de la mise à jour", exception = e)
                _errorMessage.value = "Erreur de connexion: ${e.message}"
            } finally {
                _isLoadingProfile.value = false
            }
        }
    }

    /**
     * Activer le mode édition
     */
    fun enableEditMode() {
        _isEditMode.value = true
        logger.debug("PROFILE", "Mode édition activé")
    }

    /**
     * Désactiver le mode édition
     */
    fun disableEditMode() {
        _isEditMode.value = false
        logger.debug("PROFILE", "Mode édition désactivé")
    }

    /**
     * Déconnexion de l'utilisateur
     */
    fun logout() {
        logger.info("PROFILE", "Déconnexion demandée par l'utilisateur")
        authRepository.logout()
    }

    /**
     * Effacer les messages d'erreur
     */
    fun clearErrorMessage() {
        _errorMessage.value = null
    }

    /**
     * Effacer les messages de succès
     */
    fun clearSuccessMessage() {
        _successMessage.value = null
    }

    /**
     * Calculer l'IMC de l'utilisateur
     */
    fun calculateBMI(): Double? {
        val user = currentUser.value
        return if (user != null && user.poids > 0 && user.taille > 0) {
            val tailleEnMetres = user.taille / 100.0
            user.poids / (tailleEnMetres * tailleEnMetres)
        } else null
    }

    /**
     * Obtenir l'interprétation de l'IMC
     */
    fun getBMICategory(bmi: Double): String {
        return when {
            bmi < 18.5 -> "Insuffisance pondérale"
            bmi < 25.0 -> "Poids normal"
            bmi < 30.0 -> "Surpoids"
            else -> "Obésité"
        }
    }

    override fun onCleared() {
        super.onCleared()
        logger.debug("PROFILE", "ProfileViewModel détruit")
    }
}