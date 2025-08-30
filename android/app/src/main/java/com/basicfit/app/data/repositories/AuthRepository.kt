package com.basicfit.app.data.repositories

import android.content.Context
import android.content.SharedPreferences
import com.basicfit.app.data.api.*
import com.basicfit.app.data.models.User
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Repository pour la gestion de l'authentification
 * Gère les tokens, l'état de connexion et les informations utilisateur
 */
class AuthRepository(
    private val apiService: BasicFitApiService,
    private val logger: Logger
) {

    // État de l'authentification
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    private val _authToken = MutableStateFlow<String?>(null)
    val authToken: StateFlow<String?> = _authToken.asStateFlow()

    init {
        // Charger les données d'authentification au démarrage
        loadAuthData()
    }

    /**
     * Charger les données d'authentification depuis le stockage local
     */
    private fun loadAuthData() {
        // TODO: Implémenter le chargement depuis SharedPreferences
        logger.info("AUTH", "Chargement des données d'authentification")
    }

    /**
     * Connexion utilisateur
     */
    suspend fun login(email: String, password: String): Result<User> {
        return try {
            logger.info("AUTH", "Tentative de connexion pour: $email")

            val request = LoginRequest(email, password)
            val response = apiService.login(request)

            if (response.isSuccessful) {
                val loginResponse = response.body()
                if (loginResponse != null) {
                    // Sauvegarder les tokens et les données utilisateur
                    saveAuthData(
                        accessToken = loginResponse.access,
                        refreshToken = loginResponse.refresh,
                        user = loginResponse.user
                    )

                    _isLoggedIn.value = true
                    _currentUser.value = loginResponse.user
                    _authToken.value = loginResponse.access

                    logger.success("AUTH", "Connexion réussie pour: ${loginResponse.user.getDisplayName()}")
                    Result.success(loginResponse.user)
                } else {
                    logger.error("AUTH", "Réponse de connexion vide")
                    Result.failure(Exception("Réponse du serveur invalide"))
                }
            } else {
                val errorMsg = "Erreur de connexion: ${response.code()} - ${response.message()}"
                logger.error("AUTH", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("AUTH", "Erreur lors de la connexion", details = e.message)
            Result.failure(e)
        }
    }

    /**
     * Inscription utilisateur
     */
    suspend fun register(email: String, password: String, nom: String, prenom: String): Result<User> {
        return try {
            logger.info("AUTH", "Tentative d'inscription pour: $email")

            val request = RegisterRequest(email, password, nom, prenom)
            val response = apiService.register(request)

            if (response.isSuccessful) {
                val loginResponse = response.body()
                if (loginResponse != null) {
                    saveAuthData(
                        accessToken = loginResponse.access,
                        refreshToken = loginResponse.refresh,
                        user = loginResponse.user
                    )

                    _isLoggedIn.value = true
                    _currentUser.value = loginResponse.user
                    _authToken.value = loginResponse.access

                    logger.success("AUTH", "Inscription réussie pour: ${loginResponse.user.getDisplayName()}")
                    Result.success(loginResponse.user)
                } else {
                    logger.error("AUTH", "Réponse d'inscription vide")
                    Result.failure(Exception("Réponse du serveur invalide"))
                }
            } else {
                val errorMsg = "Erreur d'inscription: ${response.code()} - ${response.message()}"
                logger.error("AUTH", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("AUTH", "Erreur lors de l'inscription", details = e.message)
            Result.failure(e)
        }
    }

    /**
     * Déconnexion
     */
    fun logout() {
        logger.info("AUTH", "Déconnexion de l'utilisateur")

        // TODO: Effacer les données d'authentification du SharedPreferences

        _isLoggedIn.value = false
        _currentUser.value = null
        _authToken.value = null

        logger.success("AUTH", "Déconnexion réussie")
    }

    /**
     * Récupérer le profil utilisateur depuis l'API
     */
    suspend fun refreshUserProfile(): Result<User> {
        return try {
            if (!_isLoggedIn.value) {
                return Result.failure(Exception("Utilisateur non connecté"))
            }

            logger.info("AUTH", "Récupération du profil utilisateur")
            val response = apiService.getUserProfile()

            if (response.isSuccessful) {
                val user = response.body()
                if (user != null) {
                    _currentUser.value = user
                    saveUserData(user)
                    logger.success("AUTH", "Profil utilisateur mis à jour")
                    Result.success(user)
                } else {
                    logger.error("AUTH", "Profil utilisateur vide")
                    Result.failure(Exception("Profil utilisateur introuvable"))
                }
            } else {
                val errorMsg = "Erreur récupération profil: ${response.code()}"
                logger.error("AUTH", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("AUTH", "Erreur lors de la récupération du profil", details = e.message)
            Result.failure(e)
        }
    }

    /**
     * Mettre à jour le profil utilisateur
     */
    suspend fun updateUserProfile(profileUpdate: UserProfileUpdate): Result<User> {
        return try {
            logger.info("AUTH", "Mise à jour du profil utilisateur")
            val response = apiService.updateUserProfile(profileUpdate)

            if (response.isSuccessful) {
                val user = response.body()
                if (user != null) {
                    _currentUser.value = user
                    saveUserData(user)
                    logger.success("AUTH", "Profil utilisateur mis à jour avec succès")
                    Result.success(user)
                } else {
                    logger.error("AUTH", "Réponse de mise à jour vide")
                    Result.failure(Exception("Erreur de mise à jour"))
                }
            } else {
                val errorMsg = "Erreur mise à jour profil: ${response.code()}"
                logger.error("AUTH", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("AUTH", "Erreur lors de la mise à jour du profil", details = e.message)
            Result.failure(e)
        }
    }

    /**
     * Récupérer l'utilisateur actuel
     */
    suspend fun getCurrentUser(): Result<User> {
        return try {
            logger.info("AUTH", "Récupération du profil utilisateur")

            val response = apiService.getUserProfile()

            if (response.isSuccessful) {
                val user = response.body()
                if (user != null) {
                    _currentUser.value = user
                    logger.success("AUTH", "Profil utilisateur récupéré: ${user.getDisplayName()}")
                    Result.success(user)
                } else {
                    logger.error("AUTH", "Réponse profil vide")
                    Result.failure(Exception("Impossible de récupérer le profil"))
                }
            } else {
                val errorMsg = "Erreur récupération profil: ${response.code()}"
                logger.error("AUTH", errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            logger.error("AUTH", "Erreur lors de la récupération du profil", details = e.message)
            Result.failure(e)
        }
    }

    // ==================== MÉTHODES PRIVÉES ====================

    private fun saveAuthData(accessToken: String, refreshToken: String, user: User) {
        // TODO: Implémenter le stockage avec SharedPreferences
        logger.info("AUTH", "Données auth sauvegardées pour: ${user.getDisplayName()}")
    }

    private fun saveUserData(user: User) {
        // TODO: Implémenter le stockage utilisateur
        logger.info("AUTH", "Données utilisateur sauvegardées: ${user.getDisplayName()}")
    }
}