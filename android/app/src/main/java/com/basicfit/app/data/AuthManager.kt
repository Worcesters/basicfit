package com.basicfit.app.data

import android.content.Context
import android.content.SharedPreferences
import com.basicfit.app.data.api.ApiRepository
import com.basicfit.app.data.api.UserData
import com.google.gson.Gson
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Gestionnaire d'authentification utilisant l'API Django
 */
class AuthManager(private val context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("basicfit_auth", Context.MODE_PRIVATE)

    private val apiRepository = ApiRepository()
    private val gson = Gson()

    // États de l'authentification
    private val _isAuthenticated = MutableStateFlow(isLoggedIn())
    val isAuthenticated: StateFlow<Boolean> = _isAuthenticated

    private val _currentUser = MutableStateFlow(getCurrentUser())
    val currentUser: StateFlow<UserData?> = _currentUser

    // Clés pour SharedPreferences
    private companion object {
        const val KEY_TOKEN = "auth_token"
        const val KEY_USER_DATA = "user_data"
        const val KEY_IS_LOGGED_IN = "is_logged_in"
    }

    /**
     * Connexion avec l'API
     */
    suspend fun login(email: String, password: String): Result<UserData> {
        return try {
            val result = apiRepository.login(email, password)

            if (result.isSuccess) {
                val response = result.getOrNull()
                if (response?.success == true && response.token != null && response.user != null) {
                    // Sauvegarder les données d'authentification
                    saveAuthData(response.token, response.user)
                    _isAuthenticated.value = true
                    _currentUser.value = response.user
                    Result.success(response.user)
                } else {
                    Result.failure(Exception(response?.message ?: "Échec de la connexion"))
                }
            } else {
                Result.failure(result.exceptionOrNull() ?: Exception("Erreur réseau"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Inscription avec l'API
     */
    suspend fun register(email: String, password: String, nom: String, prenom: String): Result<UserData> {
        return try {
            val result = apiRepository.register(email, password, nom, prenom)

            if (result.isSuccess) {
                val response = result.getOrNull()
                if (response?.success == true && response.token != null && response.user != null) {
                    // Sauvegarder les données d'authentification
                    saveAuthData(response.token, response.user)
                    _isAuthenticated.value = true
                    _currentUser.value = response.user
                    Result.success(response.user)
                } else {
                    Result.failure(Exception(response?.message ?: "Échec de l'inscription"))
                }
            } else {
                Result.failure(result.exceptionOrNull() ?: Exception("Erreur réseau"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Récupérer le profil depuis l'API
     */
    suspend fun refreshProfile(): Result<UserData> {
        return try {
            val token = getToken()
            if (token != null) {
                val result = apiRepository.getProfile(token)

                if (result.isSuccess) {
                    val response = result.getOrNull()
                    if (response?.success == true && response.user != null) {
                        // Mettre à jour les données utilisateur
                        saveUserData(response.user)
                        _currentUser.value = response.user
                        Result.success(response.user)
                    } else {
                        Result.failure(Exception("Échec de la récupération du profil"))
                    }
                } else {
                    Result.failure(result.exceptionOrNull() ?: Exception("Erreur réseau"))
                }
            } else {
                Result.failure(Exception("Token non disponible"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Déconnexion
     */
    fun logout() {
        clearAuthData()
        _isAuthenticated.value = false
        _currentUser.value = null
    }

    /**
     * Vérifier si l'utilisateur est connecté
     */
    private fun isLoggedIn(): Boolean {
        return prefs.getBoolean(KEY_IS_LOGGED_IN, false) && getToken() != null
    }

    /**
     * Récupérer le token JWT
     */
    fun getToken(): String? {
        return prefs.getString(KEY_TOKEN, null)
    }

    /**
     * Récupérer les données utilisateur actuelles
     */
    private fun getCurrentUser(): UserData? {
        val userJson = prefs.getString(KEY_USER_DATA, null)
        return if (userJson != null) {
            try {
                gson.fromJson(userJson, UserData::class.java)
            } catch (e: Exception) {
                null
            }
        } else {
            null
        }
    }

    /**
     * Sauvegarder les données d'authentification
     */
    private fun saveAuthData(token: String, user: UserData) {
        prefs.edit()
            .putString(KEY_TOKEN, token)
            .putString(KEY_USER_DATA, gson.toJson(user))
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .apply()
    }

    /**
     * Sauvegarder uniquement les données utilisateur
     */
    private fun saveUserData(user: UserData) {
        prefs.edit()
            .putString(KEY_USER_DATA, gson.toJson(user))
            .apply()
    }

    /**
     * Effacer toutes les données d'authentification
     */
    private fun clearAuthData() {
        prefs.edit()
            .remove(KEY_TOKEN)
            .remove(KEY_USER_DATA)
            .putBoolean(KEY_IS_LOGGED_IN, false)
            .apply()
    }

    /**
     * Tester la connexion au serveur
     */
    suspend fun testConnection(): Result<String> {
        return try {
            val result = apiRepository.testConnection()
            if (result.isSuccess) {
                val response = result.getOrNull()
                val message = response?.get("message") as? String ?: "Connexion réussie"
                Result.success(message)
            } else {
                Result.failure(result.exceptionOrNull() ?: Exception("Erreur de connexion"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}