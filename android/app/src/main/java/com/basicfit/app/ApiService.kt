package com.basicfit.app

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import okhttp3.Interceptor
import okhttp3.RequestBody
import okhttp3.ResponseBody
import android.content.Context
import android.content.SharedPreferences
import com.google.gson.annotations.SerializedName
import java.util.concurrent.TimeUnit

// ==============================================
// DATA CLASSES POUR LES RÉPONSES API
// ==============================================

data class LoginRequest(
    val email: String,
    val password: String
)

data class RegisterRequest(
    val email: String,
    val password: String,
    val nom: String,
    val prenom: String,
    val date_naissance: String? = null,
    val poids: Double? = null,
    val taille: Int? = null,
    val genre: String? = null,
    val objectif_sportif: String? = null,
    val niveau_experience: String? = null
)

data class AuthResponse(
    val success: Boolean,
    val message: String,
    val user: UserResponse? = null,
    val token: String? = null
)

data class UserResponse(
    val id: Int,
    val email: String,
    val nom: String,
    val prenom: String,
    @SerializedName("date_inscription")
    val dateInscription: String? = null,
    @SerializedName("total_seances")
    val totalSeances: Int? = null
)

data class WorkoutRequest(
    val nom: String,
    val date_debut: String,
    val duree_minutes: Int,
    val exercises: List<ExerciseRequest>
)

data class ExerciseRequest(
    val nom: String,
    val series: Int,
    val repetitions: Int,
    val poids: Double
)

data class ApiResponse<T>(
    val success: Boolean,
    val message: String,
    val data: T? = null
)

// ==============================================
// INTERFACE API RETROFIT
// ==============================================

interface BasicFitApi {

    // Authentification
    @POST("users/android/login/")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("users/android/register/")
    suspend fun register(@Body request: RegisterRequest): AuthResponse

    @GET("users/android/profile/")
    suspend fun getProfile(): AuthResponse

    // Workouts
    @POST("workouts/sauvegarder/")
    suspend fun saveWorkout(@Body request: WorkoutRequest): ApiResponse<Any>

    @GET("workouts/seances/")
    suspend fun getWorkoutHistory(): ApiResponse<List<Any>>

    // Machines
    @GET("workouts/machines/")
    suspend fun getMachines(): ApiResponse<List<Any>>
}

// ==============================================
// CLIENT HTTP AVEC INTERCEPTEUR D'AUTHENTIFICATION
// ==============================================

class AuthInterceptor(private val context: Context) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val original = chain.request()

        val token = getAuthToken(context)

        val requestBuilder = original.newBuilder()
            .header("Content-Type", "application/json")
            .header("Accept", "application/json")

        if (token != null) {
            requestBuilder.header("Authorization", "Bearer $token")
        }

        val request = requestBuilder.build()
        return chain.proceed(request)
    }

    private fun getAuthToken(context: Context): String? {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        return prefs.getString("auth_token", null)
    }
}

// ==============================================
// SERVICE API PRINCIPAL
// ==============================================

class ApiService private constructor() {

    companion object {
        // URL de votre API Django sur Railway
        private const val BASE_URL = "https://basicfitv2-production.up.railway.app/api/"

        @Volatile
        private var INSTANCE: ApiService? = null

        fun getInstance(): ApiService {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: ApiService().also { INSTANCE = it }
            }
        }
    }

    private lateinit var api: BasicFitApi

    fun initialize(context: Context) {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor(context))
            .addInterceptor(loggingInterceptor)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        api = retrofit.create(BasicFitApi::class.java)
    }

    fun getApi(): BasicFitApi {
        if (!::api.isInitialized) {
            throw IllegalStateException("ApiService not initialized. Call initialize() first.")
        }
        return api
    }

    // Méthodes utilitaires
    fun saveAuthToken(context: Context, token: String) {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        prefs.edit().putString("auth_token", token).apply()
    }

    fun clearAuthToken(context: Context) {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        prefs.edit().remove("auth_token").apply()
    }

    fun getAuthToken(context: Context): String? {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        return prefs.getString("auth_token", null)
    }
}

// ==============================================
// GESTIONNAIRE D'AUTHENTIFICATION
// ==============================================

class AuthManager(private val context: Context) {

    private val apiService = ApiService.getInstance()

    init {
        apiService.initialize(context)
    }

    suspend fun login(email: String, password: String): Result<AuthResponse> {
        return try {
            val request = LoginRequest(email, password)
            val response = apiService.getApi().login(request)

            if (response.success && response.token != null) {
                // Sauvegarder le token
                apiService.saveAuthToken(context, response.token)

                // Sauvegarder les infos utilisateur
                response.user?.let { user ->
                    val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
                    prefs.edit().apply {
                        putString("user_email", user.email)
                        putString("user_nom", user.nom)
                        putString("user_prenom", user.prenom)
                        putBoolean("is_logged_in", true)
                        apply()
                    }
                }
            }

            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

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
    ): Result<AuthResponse> {
        return try {
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
            val response = apiService.getApi().register(request)

            if (response.success && response.token != null) {
                // Sauvegarder le token
                apiService.saveAuthToken(context, response.token)

                // Sauvegarder les infos utilisateur
                response.user?.let { user ->
                    val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
                    prefs.edit().apply {
                        putString("user_email", user.email)
                        putString("user_nom", user.nom)
                        putString("user_prenom", user.prenom)
                        putBoolean("is_logged_in", true)
                        apply()
                    }
                }
            }

            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getProfile(): Result<AuthResponse> {
        return try {
            val response = apiService.getApi().getProfile()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        apiService.clearAuthToken(context)
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        prefs.edit().clear().apply()
    }

    fun isLoggedIn(): Boolean {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        return prefs.getBoolean("is_logged_in", false) &&
               apiService.getAuthToken(context) != null
    }
}

// ==============================================
// GESTIONNAIRE DE SYNCHRONISATION DES DONNÉES
// ==============================================

class SyncManager(private val context: Context) {

    private val apiService = ApiService.getInstance()
    private val authManager = AuthManager(context)

    init {
        apiService.initialize(context)
    }

    suspend fun saveWorkoutToServer(
        nom: String,
        dateDebut: String,
        dureeMinutes: Int,
        exercises: List<ExerciseRecord>
    ): Result<Boolean> {
        return try {
            if (!authManager.isLoggedIn()) {
                return Result.failure(Exception("Utilisateur non connecté"))
            }

            val exerciseRequests = exercises.map {
                ExerciseRequest(
                    nom = it.name,
                    series = it.sets,
                    repetitions = it.reps,
                    poids = it.weight
                )
            }

            val request = WorkoutRequest(
                nom = nom,
                date_debut = dateDebut,
                duree_minutes = dureeMinutes,
                exercises = exerciseRequests
            )

            val response = apiService.getApi().saveWorkout(request)
            Result.success(response.success)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun syncWorkoutHistory(): Result<List<Any>> {
        return try {
            if (!authManager.isLoggedIn()) {
                return Result.failure(Exception("Utilisateur non connecté"))
            }

            val response = apiService.getApi().getWorkoutHistory()
            if (response.success) {
                Result.success(response.data ?: emptyList())
            } else {
                Result.failure(Exception(response.message))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}