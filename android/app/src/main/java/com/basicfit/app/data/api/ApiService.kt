package com.basicfit.app.data.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

/**
 * Service API pour communiquer avec le backend Django
 */

// Data classes pour les réponses
data class LoginResponse(
    val success: Boolean,
    val message: String,
    val user: UserData? = null,
    val token: String? = null
)

data class UserData(
    val id: Int,
    val email: String,
    val nom: String,
    val prenom: String,
    val date_inscription: String? = null,
    val total_seances: Int? = null
)

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

data class WorkoutStats(
    val total_seances: Int,
    val total_minutes: Int,
    val total_calories: Int,
    val seances_excellentes: Int,
    val record_poids: Float,
    val exercices_favoris: List<String>,
    val progression_generale: Float
)

data class WorkoutStatsResponse(
    val success: Boolean? = null,
    val total_seances: Int,
    val total_minutes: Int,
    val total_calories: Int,
    val seances_excellentes: Int,
    val record_poids: Float,
    val exercices_favoris: List<String>,
    val progression_generale: Float
)

data class SeanceData(
    val nom: String,
    val duree: Int,
    val note_ressenti: Int,
    val commentaire: String,
    val exercices: List<ExerciceData>
)

data class ExerciceData(
    val nom: String,
    val series: Int,
    val reps: Int,
    val poids: Float
)

data class SeanceResponse(
    val success: Boolean,
    val message: String? = null,
    val id: Int? = null
)

data class WorkoutHistoryResponse(
    val success: Boolean,
    val results: List<WorkoutSession>,
    val count: Int,
    val has_more: Boolean
)

data class WorkoutSession(
    val id: Int,
    val nom: String,
    val date_debut: String,
    val date_fin: String,
    val duree_reelle: Int?,
    val statut: String,
    val nombre_exercices: Int,
    val note_ressenti: Int?,
    val exercices: List<ExerciceSession>? = null
)

data class ExerciceSession(
    val machine: MachineData,
    val repetitions_realisees: Int,
    val poids_utilise: Float,
    val nombre_series: Int,
    val note_ressenti: Int?
)

data class MachineData(
    val nom: String,
    val groupe_musculaire: String
)

// Interface Retrofit
interface ApiService {

    @POST("api/users/android/login/")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @POST("api/users/android/register/")
    suspend fun register(@Body request: RegisterRequest): LoginResponse

    @GET("api/users/android/profile/")
    suspend fun getProfile(@Header("Authorization") token: String): LoginResponse

    @POST("api/workouts/sauvegarder/")
    suspend fun sauvegarderSeance(
        @Header("Authorization") token: String,
        @Body seance: SeanceData
    ): SeanceResponse

    @GET("api/workouts/seances/stats/")
    suspend fun getWorkoutStats(@Header("Authorization") token: String): WorkoutStatsResponse

    @GET("api/workouts/seances/history/")
    suspend fun getWorkoutHistory(
        @Header("Authorization") token: String,
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0
    ): WorkoutHistoryResponse

    @GET("api/workouts/info/")
    suspend fun getWorkoutsInfo(): Map<String, Any>
}

/**
 * Singleton pour gérer l'API
 */
object ApiClient {
    private const val BASE_URL = "http://10.0.2.2:8000/" // Émulateur Android
    // Pour un appareil physique, remplacez par votre IP : "http://192.168.1.XXX:8000/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val httpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    private val retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(httpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)

    fun formatAuthToken(token: String): String = "Bearer $token"
}

/**
 * Repository pour gérer les données
 */
class ApiRepository {
    private val apiService = ApiClient.apiService

    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return try {
            val response = apiService.login(LoginRequest(email, password))
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun register(email: String, password: String, nom: String, prenom: String): Result<LoginResponse> {
        return try {
            val response = apiService.register(RegisterRequest(email, password, nom, prenom))
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getProfile(token: String): Result<LoginResponse> {
        return try {
            val response = apiService.getProfile(ApiClient.formatAuthToken(token))
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun sauvegarderSeance(token: String, seance: SeanceData): Result<SeanceResponse> {
        return try {
            val response = apiService.sauvegarderSeance(ApiClient.formatAuthToken(token), seance)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getWorkoutStats(token: String): Result<WorkoutStatsResponse> {
        return try {
            val response = apiService.getWorkoutStats(ApiClient.formatAuthToken(token))
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getWorkoutHistory(token: String, limit: Int = 20, offset: Int = 0): Result<WorkoutHistoryResponse> {
        return try {
            val response = apiService.getWorkoutHistory(ApiClient.formatAuthToken(token), limit, offset)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun testConnection(): Result<Map<String, Any>> {
        return try {
            val response = apiService.getWorkoutsInfo()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}