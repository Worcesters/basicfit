package com.basicfit.app

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import kotlinx.coroutines.*
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import com.google.gson.annotations.SerializedName

/**
 * Système d'authentification simplifié et robuste
 * Gère uniquement l'essentiel : login, register, token storage
 */
object SimpleAuth {
    private const val TAG = "SimpleAuth"
    private const val PREFS_NAME = "basicfit_auth"
    private const val KEY_TOKEN = "auth_token"
    private const val KEY_USER_EMAIL = "user_email"
    private const val KEY_USER_ID = "user_id"
    
    private const val BASE_URL = "https://basicfit-v2.fly.dev/api/"
    
    private var api: SimpleAuthApi? = null
    
    // ===== DATA CLASSES =====
    data class LoginRequest(
        val email: String,
        val password: String
    )
    
    data class RegisterRequest(
        val email: String,
        val password: String,
        val nom: String,
        val prenom: String
    )
    
    data class AuthResponse(
        @SerializedName("message") val message: String,
        @SerializedName("user") val user: UserData?,
        @SerializedName("tokens") val tokens: TokenData?,
        @SerializedName("token") val token: String? = null,
        @SerializedName("success") val success: Boolean = true
    )
    
    data class UserData(
        @SerializedName("id") val id: Int,
        @SerializedName("email") val email: String,
        @SerializedName("prenom") val prenom: String,
        @SerializedName("nom") val nom: String
    )
    
    data class TokenData(
        @SerializedName("access") val access: String,
        @SerializedName("refresh") val refresh: String
    )
    
    // ===== API INTERFACE =====
    interface SimpleAuthApi {
        @POST("users/android/login/")
        suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
        
        @POST("users/android/register/")
        suspend fun register(@Body request: RegisterRequest): Response<AuthResponse>
        
        @GET("users/android/ping/")
        suspend fun ping(): Response<Map<String, Any>>
    }
    
    // ===== INITIALIZATION =====
    fun initialize(context: Context) {
        if (api == null) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            val client = OkHttpClient.Builder()
                .addInterceptor(logging)
                .build()
            
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            
            api = retrofit.create(SimpleAuthApi::class.java)
            Log.i(TAG, "SimpleAuth initialized with base URL: $BASE_URL")
        }
    }
    
    // ===== AUTH FUNCTIONS =====
    suspend fun login(context: Context, email: String, password: String): AuthResult {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                Log.d(TAG, "Tentative de connexion pour: $email")
                
                val response = api!!.login(LoginRequest(email, password))
                
                if (response.isSuccessful) {
                    val authResponse = response.body()
                    if (authResponse != null && authResponse.success) {
                        // Extraire le token
                        val token = authResponse.tokens?.access 
                            ?: authResponse.token
                            ?: return@withContext AuthResult.Error("Aucun token reçu")
                        
                        // Sauvegarder les données
                        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                        prefs.edit().apply {
                            putString(KEY_TOKEN, token)
                            putString(KEY_USER_EMAIL, email)
                            authResponse.user?.id?.let { putInt(KEY_USER_ID, it) }
                            apply()
                        }
                        
                        Log.i(TAG, "Connexion réussie pour: $email")
                        AuthResult.Success(token, authResponse.user)
                    } else {
                        Log.w(TAG, "Réponse API non successful")
                        AuthResult.Error(authResponse?.message ?: "Erreur de connexion")
                    }
                } else {
                    Log.w(TAG, "Échec HTTP: ${response.code()}")
                    AuthResult.Error("Erreur réseau: ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception lors du login", e)
                AuthResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    suspend fun register(context: Context, email: String, password: String, nom: String, prenom: String): AuthResult {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                Log.d(TAG, "Tentative d'inscription pour: $email")
                
                val response = api!!.register(RegisterRequest(email, password, nom, prenom))
                
                if (response.isSuccessful) {
                    val authResponse = response.body()
                    if (authResponse != null && authResponse.success) {
                        // Extraire le token
                        val token = authResponse.tokens?.access 
                            ?: authResponse.token
                            ?: return@withContext AuthResult.Error("Aucun token reçu")
                        
                        // Sauvegarder les données
                        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
                        prefs.edit().apply {
                            putString(KEY_TOKEN, token)
                            putString(KEY_USER_EMAIL, email)
                            authResponse.user?.id?.let { putInt(KEY_USER_ID, it) }
                            apply()
                        }
                        
                        Log.i(TAG, "Inscription réussie pour: $email")
                        AuthResult.Success(token, authResponse.user)
                    } else {
                        Log.w(TAG, "Réponse API non successful")
                        AuthResult.Error(authResponse?.message ?: "Erreur d'inscription")
                    }
                } else {
                    Log.w(TAG, "Échec HTTP inscription: ${response.code()}")
                    AuthResult.Error("Erreur réseau: ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception lors de l'inscription", e)
                AuthResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    // ===== TOKEN MANAGEMENT =====
    fun getToken(context: Context): String? {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_TOKEN, null)
    }
    
    fun getUserEmail(context: Context): String? {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_USER_EMAIL, null)
    }
    
    fun getUserId(context: Context): Int {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getInt(KEY_USER_ID, -1)
    }
    
    fun isLoggedIn(context: Context): Boolean {
        return getToken(context) != null
    }
    
    fun logout(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().clear().apply()
        Log.i(TAG, "Déconnexion effectuée")
    }
    
    // ===== TEST FUNCTIONS =====
    suspend fun testConnection(context: Context): Boolean {
        return try {
            initialize(context)
            val response = api!!.ping()
            response.isSuccessful
        } catch (e: Exception) {
            Log.e(TAG, "Test de connexion échoué", e)
            false
        }
    }
}

// ===== RESULT CLASS =====
sealed class AuthResult {
    data class Success(val token: String, val user: SimpleAuth.UserData?) : AuthResult()
    data class Error(val message: String) : AuthResult()
}