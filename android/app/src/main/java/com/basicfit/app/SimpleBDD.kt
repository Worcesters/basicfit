package com.basicfit.app

import android.content.Context
import android.util.Log
import kotlinx.coroutines.*
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import okhttp3.Interceptor
import com.google.gson.annotations.SerializedName

/**
 * Système de communication BDD simplifié et robuste
 * Gère uniquement : import CSV, récupération données, sauvegarde workouts
 */
object SimpleBDD {
    private const val TAG = "SimpleBDD"
    private const val BASE_URL = "https://basicfit-v2.fly.dev/api/"
    
    private var api: SimpleBDDApi? = null
    
    // ===== DATA CLASSES =====
    data class CsvImportRequest(
        @SerializedName("csv_data") val csvData: String
    )
    
    data class CsvImportResponse(
        @SerializedName("success") val success: Boolean,
        @SerializedName("message") val message: String,
        @SerializedName("imported_count") val importedCount: Int = 0,
        @SerializedName("total_lines") val totalLines: Int = 0,
        @SerializedName("errors_count") val errorsCount: Int = 0,
        @SerializedName("errors") val errors: List<String> = emptyList()
    )
    
    data class SessionsResponse(
        @SerializedName("success") val success: Boolean,
        @SerializedName("data") val data: List<SessionData> = emptyList(),
        @SerializedName("count") val count: Int = 0,
        @SerializedName("message") val message: String = ""
    )
    
    data class SessionData(
        @SerializedName("id") val id: Int,
        @SerializedName("machine") val machine: String,
        @SerializedName("date") val date: String,
        @SerializedName("type") val type: String,
        @SerializedName("duree") val duree: Int? = null
    )
    
    data class WorkoutSaveRequest(
        @SerializedName("nom") val nom: String,
        @SerializedName("date") val date: String,
        @SerializedName("duree") val duree: Int,
        @SerializedName("note_ressenti") val noteRessenti: Int,
        @SerializedName("commentaire") val commentaire: String,
        @SerializedName("exercices") val exercices: List<ExerciceData>
    )
    
    data class ExerciceData(
        @SerializedName("nom") val nom: String,
        @SerializedName("series") val series: Int,
        @SerializedName("reps") val reps: Int,
        @SerializedName("poids") val poids: Double
    )
    
    data class WorkoutSaveResponse(
        @SerializedName("success") val success: Boolean,
        @SerializedName("message") val message: String,
        @SerializedName("created") val created: Boolean = false,
        @SerializedName("data") val data: Map<String, Any>? = null
    )
    
    // ===== API INTERFACE =====
    interface SimpleBDDApi {
        @POST("workouts/simple/import/")
        suspend fun importCsv(@Body request: CsvImportRequest): Response<CsvImportResponse>
        
        @GET("workouts/simple/")
        suspend fun getSessions(): Response<SessionsResponse>
        
        @GET("workouts/history/")
        suspend fun getWorkoutHistory(): Response<SessionsResponse>
        
        @POST("workouts/save/")
        suspend fun saveWorkout(@Body request: WorkoutSaveRequest): Response<WorkoutSaveResponse>
        
        @GET("users/android/ping/")
        suspend fun ping(): Response<Map<String, Any>>
    }
    
    // ===== INITIALIZATION =====
    private fun initialize(context: Context) {
        if (api == null) {
            val logging = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }
            
            // Intercepteur pour ajouter automatiquement le token
            val authInterceptor = Interceptor { chain ->
                val token = SimpleAuth.getToken(context)
                val request = if (token != null) {
                    chain.request().newBuilder()
                        .header("Authorization", "Bearer $token")
                        .header("Content-Type", "application/json")
                        .build()
                } else {
                    chain.request()
                }
                
                val response = chain.proceed(request)
                
                // Si unauthorized, déconnecter automatiquement
                if (response.code == 401 || response.code == 403) {
                    Log.w(TAG, "Token invalide, déconnexion automatique")
                    SimpleAuth.logout(context)
                }
                
                response
            }
            
            val client = OkHttpClient.Builder()
                .addInterceptor(authInterceptor)
                .addInterceptor(logging)
                .build()
            
            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
            
            api = retrofit.create(SimpleBDDApi::class.java)
            Log.i(TAG, "SimpleBDD initialized")
        }
    }
    
    // ===== CSV IMPORT =====
    suspend fun importCsv(context: Context, csvData: String): BDDResult<CsvImportResponse> {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                
                if (!SimpleAuth.isLoggedIn(context)) {
                    return@withContext BDDResult.Error("Non connecté")
                }
                
                Log.d(TAG, "Import CSV - ${csvData.length} caractères")
                Log.d(TAG, "User: ${SimpleAuth.getUserEmail(context)}")
                
                val response = api!!.importCsv(CsvImportRequest(csvData))
                
                if (response.isSuccessful) {
                    val result = response.body()
                    if (result != null) {
                        Log.i(TAG, "Import CSV réussi: ${result.importedCount} séances")
                        BDDResult.Success(result)
                    } else {
                        Log.w(TAG, "Réponse import CSV vide")
                        BDDResult.Error("Réponse vide")
                    }
                } else {
                    Log.w(TAG, "Échec import CSV: ${response.code()}")
                    BDDResult.Error("Erreur ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception import CSV", e)
                BDDResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    // ===== GET SESSIONS =====
    suspend fun getSessions(context: Context): BDDResult<List<SessionData>> {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                
                if (!SimpleAuth.isLoggedIn(context)) {
                    return@withContext BDDResult.Error("Non connecté")
                }
                
                Log.d(TAG, "Récupération des séances...")
                
                val response = api!!.getSessions()
                
                if (response.isSuccessful) {
                    val result = response.body()
                    if (result != null && result.success) {
                        Log.i(TAG, "Séances récupérées: ${result.count}")
                        BDDResult.Success(result.data)
                    } else {
                        Log.w(TAG, "Pas de séances trouvées")
                        BDDResult.Success(emptyList())
                    }
                } else {
                    Log.w(TAG, "Échec récupération séances: ${response.code()}")
                    BDDResult.Error("Erreur ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception récupération séances", e)
                BDDResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    // ===== GET WORKOUT HISTORY =====
    suspend fun getWorkoutHistory(context: Context): BDDResult<List<SessionData>> {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                
                if (!SimpleAuth.isLoggedIn(context)) {
                    return@withContext BDDResult.Error("Non connecté")
                }
                
                Log.d(TAG, "Récupération historique workouts...")
                
                val response = api!!.getWorkoutHistory()
                
                if (response.isSuccessful) {
                    val result = response.body()
                    if (result != null && result.success) {
                        Log.i(TAG, "Historique récupéré: ${result.count}")
                        BDDResult.Success(result.data)
                    } else {
                        Log.w(TAG, "Pas d'historique trouvé")
                        BDDResult.Success(emptyList())
                    }
                } else {
                    Log.w(TAG, "Échec récupération historique: ${response.code()}")
                    BDDResult.Error("Erreur ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception récupération historique", e)
                BDDResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    // ===== SAVE WORKOUT =====
    suspend fun saveWorkout(context: Context, workout: WorkoutSaveRequest): BDDResult<WorkoutSaveResponse> {
        return withContext(Dispatchers.IO) {
            try {
                initialize(context)
                
                if (!SimpleAuth.isLoggedIn(context)) {
                    return@withContext BDDResult.Error("Non connecté")
                }
                
                Log.d(TAG, "Sauvegarde workout: ${workout.nom}")
                
                val response = api!!.saveWorkout(workout)
                
                if (response.isSuccessful) {
                    val result = response.body()
                    if (result != null && result.success) {
                        Log.i(TAG, "Workout sauvegardé: ${result.message}")
                        BDDResult.Success(result)
                    } else {
                        Log.w(TAG, "Échec sauvegarde workout")
                        BDDResult.Error(result?.message ?: "Erreur sauvegarde")
                    }
                } else {
                    Log.w(TAG, "Échec sauvegarde workout: ${response.code()}")
                    BDDResult.Error("Erreur ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception sauvegarde workout", e)
                BDDResult.Error("Erreur: ${e.message}")
            }
        }
    }
    
    // ===== TEST CONNECTION =====
    suspend fun testConnection(context: Context): Boolean {
        return try {
            initialize(context)
            val response = api!!.ping()
            response.isSuccessful
        } catch (e: Exception) {
            Log.e(TAG, "Test connexion échoué", e)
            false
        }
    }
}

// ===== RESULT CLASS =====
sealed class BDDResult<T> {
    data class Success<T>(val data: T) : BDDResult<T>()
    data class Error<T>(val message: String) : BDDResult<T>()
}