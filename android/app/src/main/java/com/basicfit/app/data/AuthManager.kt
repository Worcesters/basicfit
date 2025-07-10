package com.basicfit.app.data

import android.content.Context
import com.basicfit.app.ApiService
import com.basicfit.app.LoginRequest
import com.basicfit.app.RegisterRequest
import com.basicfit.app.AuthResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class AuthManager(private val context: Context) {

    private val apiService by lazy {
        ApiService.getInstance().apply {
            if (!isApiAvailable()) {
                initialize(context)
            }
        }.getApi()
    }

    /**
     * Connexion utilisateur.
     * @return Result<AuthResponse> – success si l’API répond success=true
     */
    suspend fun login(email: String, password: String): Result<AuthResponse> = withContext(Dispatchers.IO) {
        return@withContext try {
            val response = apiService.login(LoginRequest(email = email, password = password))
            if (response.success && response.token != null) {
                // Sauvegarder le token
                ApiService.getInstance().saveAuthToken(context, response.token)
            }
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Inscription utilisateur.
     */
    suspend fun register(
        email: String,
        password: String,
        nom: String,
        prenom: String,
        dateNaissance: String? = null,
        poids: Double? = null,
        taille: Int? = null,
        genre: String? = null,
        objectifSportif: String? = null,
        niveauExperience: String? = null
    ): Result<AuthResponse> = withContext(Dispatchers.IO) {
        val request = RegisterRequest(
            email = email,
            password = password,
            nom = nom,
            prenom = prenom,
            date_naissance = dateNaissance,
            poids = poids,
            taille = taille,
            genre = genre,
            objectif_sportif = objectifSportif,
            niveau_experience = niveauExperience
        )
        return@withContext try {
            val response = apiService.register(request)
            if (response.success && response.token != null) {
                ApiService.getInstance().saveAuthToken(context, response.token)
            }
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        ApiService.getInstance().clearAuthToken(context)
    }
}
