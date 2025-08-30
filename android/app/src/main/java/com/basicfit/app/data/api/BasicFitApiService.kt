package com.basicfit.app.data.api

import com.basicfit.app.data.models.*
import com.basicfit.app.data.repositories.*
import retrofit2.Response
import retrofit2.http.*

/**
 * Interface API pour BasicFit
 * Définit tous les endpoints utilisés par l'application
 */
interface BasicFitApiService {
    
    // ==================== AUTHENTIFICATION ====================
    
    @POST("api/users/android/login/")
    suspend fun login(@Body credentials: LoginRequest): Response<LoginResponse>
    
    @POST("api/users/android/register/")
    suspend fun register(@Body userData: RegisterRequest): Response<LoginResponse>
    
    @GET("api/users/android/profile/")
    suspend fun getUserProfile(): Response<User>
    
    @PUT("api/users/android/profile/")
    suspend fun updateUserProfile(@Body profileData: UserProfileUpdate): Response<User>
    
    // ==================== MACHINES ====================
    
    @GET("api/machines/")
    suspend fun getMachines(): Response<List<Machine>>
    
    @GET("api/machines/{id}/")
    suspend fun getMachine(@Path("id") id: Int): Response<Machine>
    
    @GET("api/machines/categories/")
    suspend fun getMachineCategories(): Response<List<MachineCategory>>
    
    // ==================== RECOMMANDATIONS ====================
    
    @GET("api/workouts/recommandations/{machineId}/")
    suspend fun getMachineRecommendation(@Path("machineId") machineId: Int): Response<MachineRecommendation>
    
    @GET("api/workouts/recommandations/session/")
    suspend fun getSessionRecommendations(
        @Query("mode") mode: String = "PRISE_MASSE",
        @Query("nb_machines") nbMachines: Int = 6
    ): Response<RecommendationsResponse>
    
    // ==================== ENTRAÎNEMENTS ====================
    
    @POST("api/workouts/sauvegarder/")
    suspend fun saveWorkout(@Body workout: WorkoutSession): Response<WorkoutSaveResponse>
    
    @GET("api/workouts/stats/")
    suspend fun getUserStatistics(): Response<UserStatistics>
    
    @GET("api/workouts/history/")
    suspend fun getWorkoutHistory(
        @Query("limit") limit: Int = 20,
        @Query("offset") offset: Int = 0
    ): Response<WorkoutHistoryResponse>
    
    // ==================== CALENDRIER ====================
    
    @GET("api/workouts/calendrier/")
    suspend fun getWorkoutHistory(): Response<WorkoutHistoryResponse>
    
    @GET("api/workouts/calendrier/monthly/{year}/{month}/")
    suspend fun getMonthlySummary(@Path("year") year: Int, @Path("month") month: Int): Response<MonthlySummary>
    
    @POST("api/workouts/import-csv/")
    suspend fun importCsvSessions(@Body csvData: CsvImportRequest): Response<CsvImportResponse>
    
    @DELETE("api/workouts/seance/{id}/")
    suspend fun deleteWorkout(@Path("id") workoutId: Int): Response<Unit>
    
    @DELETE("api/workouts/clear-all/")
    suspend fun deleteAllSessions(): Response<Unit>
    
    // ==================== LOGS ET MONITORING ====================
    
    @GET("api/system/logs/")
    suspend fun getSystemLogs(): Response<SystemLogsResponse>
    
    @POST("api/system/logs/upload/")
    suspend fun uploadLogs(@Body logs: LogUploadRequest): Response<LogUploadResponse>
    
    @DELETE("api/system/logs/clear/")
    suspend fun clearSystemLogs(): Response<Unit>
}

// ==================== DATA TRANSFER OBJECTS ====================

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

data class LoginResponse(
    val access: String,
    val refresh: String,
    val user: User
)

data class RecommendationsResponse(
    val mode_entrainement: String,
    val nb_machines_demandees: Int,
    val nb_recommendations: Int,
    val recommendations: List<MachineRecommendation>
)

data class WorkoutHistoryResponse(
    val results: List<WorkoutSession>,
    val count: Int,
    val has_more: Boolean
)

data class CsvImportRequest(
    val csvData: String
)

data class CsvImportResponse(
    val success: Boolean,
    val message: String,
    val importedCount: Int,
    val errors: List<String> = emptyList()
)

data class UserProfileUpdate(
    val nom: String? = null,
    val prenom: String? = null,
    val dateNaissance: String? = null,
    val poids: Double? = null,
    val taille: Int? = null,
    val genre: String? = null,
    val niveauActivite: String? = null,
    val objectif: String? = null
)