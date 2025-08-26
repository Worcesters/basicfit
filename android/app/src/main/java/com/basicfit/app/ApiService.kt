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
import com.basicfit.app.data.*
import com.google.gson.*
import java.lang.reflect.Type
import java.time.LocalDate

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

data class UpdateProfileRequest(
    val nom: String? = null,
    val prenom: String? = null,
    val date_naissance: String? = null,
    val poids: Double? = null,
    val taille: Double? = null,
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
    val poids: Double? = null,
    val taille: Double? = null,
    @SerializedName("date_naissance")
    val dateNaissance: String? = null,
    @SerializedName("objectif_sportif")
    val objectifSportif: String? = null,
    @SerializedName("niveau_experience")
    val niveauExperience: String? = null,
    @SerializedName("date_inscription")
    val dateInscription: String? = null,
    @SerializedName("total_seances")
    val totalSeances: Int? = null,
    @SerializedName("est_premium")
    val estPremium: Boolean? = null
)

data class WorkoutRequest(
    val nom: String,
    @SerializedName("duree") val duree: Int,
    @SerializedName("exercices") val exercices: List<ExerciseRequest>
)

data class ExerciseRequest(
    val nom: String,
    val series: Int,
    @SerializedName("reps") val repetitions: Int,
    val poids: Double,
    val type_exercice: String = "REPETITIONS" // "REPETITIONS" ou "DUREE"
)

data class ApiResponse<T>(
    val success: Boolean,
    val message: String,
    val data: T? = null
)

data class MachineDto(
    val id: Int,
    val nom: String,
    val description: String? = null,
    val instructions: String? = null,
    val categorie: String? = null,
    val image_gif: String? = null, // Ajout du champ pour les GIFs
    val groupe_musculaire_primaires: List<Map<String, String>>? = null // Ajout pour les groupes musculaires
)

data class MachinesResponse(
    val results: List<MachineDto>,
    val count: Int
)

// Classe pour les statistiques utilisateur du backend
data class UserStatsDto(
    @SerializedName("seances_cette_semaine")
    val seancesCetteSemaine: Int,
    @SerializedName("total_seances")
    val totalSeances: Int,
    @SerializedName("derniere_seance")
    val derniereSeance: String?,
    @SerializedName("membre_depuis")
    val membreDepuis: String?,
    @SerializedName("est_premium")
    val estPremium: Boolean,
    @SerializedName("objectif_sportif")
    val objectifSportif: String?,
    @SerializedName("niveau_experience")
    val niveauExperience: String?
)

// Nouvelles classes pour la progression
data class CompleteWorkoutRequest(
    val nom: String,
    val duree: Int,
    val note_ressenti: Int,
    val commentaire: String? = null,
    val exercices: List<CompleteExerciseRequest>
)

data class CompleteExerciseRequest(
    val nom: String,
    val series: Int,
    val reps: Int,
    val poids: Double
)

// Nouvelle classe pour planifier une séance
data class PlanWorkoutRequest(
    val nom: String,
    val date: String,  // Format ISO: "2025-07-28T10:00:00Z"
    val duree: Int,
    val commentaire: String? = null
)

// Nouvelle classe pour l'import CSV
data class CsvImportRequest(
    val csv_data: String
)

// Classes pour les séances effectuées (nouvelle API)
data class SeanceEffectueeRequest(
    val nom: String,
    val date_debut: String,
    val date_fin: String,
    val note_ressenti: Int,
    val commentaire: String,
    val exercices: List<ExerciceEffectueData>
)

data class ExerciceEffectueData(
    val nom_exercice: String,
    val machine_id: Int,
    val series: List<SerieEffectueeData>
)

data class SerieEffectueeData(
    val numero: Int,
    val repetitions_prevues: Int,
    val repetitions_realisees: Int,
    val poids_utilise: Double
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

    @GET("users/profile/stats/")
    suspend fun getUserStats(): ApiResponse<UserStatsDto>

    @PUT("users/android/profile/update/")
    suspend fun updateProfile(@Body request: UpdateProfileRequest): AuthResponse

    // Workouts (anciens endpoints - calendrier/planification)
    @POST("workouts/save/")
    suspend fun saveWorkout(@Body request: WorkoutRequest): ApiResponse<Any>

    // Nouveau: Planifier une séance (calendrier)
    @POST("workouts/calendar/plan/")
    suspend fun planWorkout(@Body request: PlanWorkoutRequest): ApiResponse<Any>

    // NOUVEAU ENDPOINT CALENDRIER SIMPLIFIÉ (planification)
    @GET("workouts/history/")
    suspend fun getWorkoutHistory(): ApiResponse<List<Any>>
    
    // NOUVEAUX ENDPOINTS SÉANCES EFFECTUÉES (séparées du calendrier)
    @GET("workouts/seances-effectuees/")
    suspend fun getSeancesEffectuees(@Query("days") days: Int = 365): ApiResponse<List<Any>>
    
    @GET("workouts/progressions-effectuees/")
    suspend fun getProgressionsEffectuees(@Query("days") days: Int = 90): ApiResponse<List<Any>>
    
    @POST("workouts/seance-effectuee/")
    suspend fun saveSeanceEffectuee(@Body request: WorkoutRequest): ApiResponse<Any>
    
    // Endpoint health check pour debug
    @GET("workouts/calendar/health/")
    suspend fun getCalendarHealth(): ApiResponse<Any>


    // Machines
    // Retourne les machines avec leur wrapper de réponse
    @GET("machines/")
    suspend fun getMachines(): MachinesResponse




    @GET("users/android/ping/")
    suspend fun ping(): retrofit2.Response<Void>

    @POST("workouts/progressions/force-update/")
    suspend fun forceProgressionUpdate(): ApiResponse<Any>

    // ========== NOUVELLES APIs SEANCES SIMPLES ==========
    
    // Récupérer toutes les séances simples
    @GET("workouts/simple/")
    suspend fun getSimpleSessions(): SimpleSessionResponse

    // Importer des séances depuis CSV (nouvelle API séparée - calendrier)
    @POST("workouts-v2/calendrier/import/")
    suspend fun importCsvSessions(@Body request: CsvImportRequest): CsvImportResponse

    // Supprimer toutes les séances de l'utilisateur
    @DELETE("workouts/simple/delete-all/")
    suspend fun deleteAllSessions(): DeleteAllResponse

    // Sauvegarder une séance effectuée (nouvelle API séparée)
    @POST("workouts-v2/effectuees/save/")
    suspend fun saveSeanceEffectuee(@Body request: SeanceEffectueeRequest): ApiResponse<Any>

    // Récupérer le résumé calendrier
    @GET("workouts/simple/summary/")
    suspend fun getCalendarSummary(): CalendarSummaryResponse
    
    // ========== NOUVELLES APIs RECOMMANDATIONS INTELLIGENTES ==========
    
    // Récupérer les recommandations intelligentes basées sur les progressions
    @GET("workouts/recommendations/{mode_entrainement}/")
    suspend fun getIntelligentRecommendations(
        @Path("mode_entrainement") modeEntrainement: String,
        @Query("nb_machines") nbMachines: Int = 6
    ): IntelligentRecommendationsResponse
    
    // Récupérer les progressions d'un utilisateur
    @GET("workouts/progressions/")
    suspend fun getUserProgressions(
        @Query("mode_entrainement") modeEntrainement: String? = null
    ): ProgressionsResponse
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
        val response = chain.proceed(request)
        
        // Vérifier si le token est invalide (401/403)
        if (response.code == 401 || response.code == 403) {
            android.util.Log.w("AuthInterceptor", "Token invalide détecté (${response.code}), déconnexion automatique")
            // Déclencher la déconnexion automatique
            forceLogout(context)
        }
        
        return response
    }

    private fun getAuthToken(context: Context): String? {
        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
        return prefs.getString("auth_token", null)
    }
    
    private fun forceLogout(context: Context) {
        try {
            val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
            prefs.edit().apply {
                remove("auth_token")
                putBoolean("is_logged_in", false)
                putBoolean("force_logout", true) // Flag pour signaler à l'UI
                apply()
            }
            android.util.Log.i("AuthInterceptor", "Déconnexion automatique effectuée")
        } catch (e: Exception) {
            android.util.Log.e("AuthInterceptor", "Erreur lors de la déconnexion automatique: ${e.message}")
        }
    }
}

// ==============================================
// SERVICE API PRINCIPAL
// ==============================================

class ApiService private constructor() {

    companion object {
        // URL de votre API Django sur Fly.io
        private const val BASE_URL = "https://basicfit-v2.fly.dev/api/"
        // URL locale pour les tests (si besoin)
        // private const val LOCAL_URL = "http://10.0.2.2:8000/api/"

        @Volatile
        private var INSTANCE: ApiService? = null

        fun getInstance(): ApiService {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: ApiService().also { INSTANCE = it }
            }
        }
    }

    private lateinit var api: BasicFitApi
    private var isInitialized = false

    fun initialize(context: Context) {
        try {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            }

            val client = OkHttpClient.Builder()
                .addInterceptor(AuthInterceptor(context))
                .addInterceptor(loggingInterceptor)
                .connectTimeout(10, TimeUnit.SECONDS) // Réduit pour détecter rapidement les problèmes
                .readTimeout(10, TimeUnit.SECONDS)
                .writeTimeout(10, TimeUnit.SECONDS)
                .build()

            // Gson avec support pour LocalDate
            val gson = GsonBuilder()
                .registerTypeAdapter(LocalDate::class.java, object : JsonDeserializer<LocalDate>, JsonSerializer<LocalDate> {
                    override fun deserialize(json: JsonElement?, typeOfT: Type?, context: JsonDeserializationContext?): LocalDate {
                        return LocalDate.parse(json?.asString ?: "1970-01-01")
                    }
                    
                    override fun serialize(src: LocalDate?, typeOfSrc: Type?, context: JsonSerializationContext?): JsonElement {
                        return JsonPrimitive(src?.toString())
                    }
                })
                .create()

            val retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build()

            api = retrofit.create(BasicFitApi::class.java)
            isInitialized = true
        } catch (e: Exception) {
            // En cas d'erreur, l'app fonctionnera en mode local uniquement
            isInitialized = false
        }
    }

    fun getApi(): BasicFitApi {
        if (!isInitialized) {
            throw IllegalStateException("ApiService not initialized. Call initialize() first.")
        }
        return api
    }

    // Fonction pour vérifier si l'API est disponible
    fun isApiAvailable(): Boolean {
        return isInitialized
    }

    // Nouvelle méthode pour tester la connectivité réelle
    suspend fun testServerConnectivity(): Boolean {
        return try {
            if (!isInitialized) {
                false
            } else {
                // Test simple avec un endpoint de ping
                val response = api.ping()
                response.isSuccessful
            }
        } catch (e: Exception) {
            false
        }
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

    // Récupérer l'historique des séances pour le calendrier
    suspend fun getCalendarHistory(): Result<List<WorkoutEntry>> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            // Utiliser getWorkoutHistory() qui fonctionne avec le backend existant
            val response = api.getWorkoutHistory()
            if (response.success && response.data != null) {
                val workoutEntries = response.data.mapNotNull { workoutData ->
                    convertWorkoutToWorkoutEntry(workoutData)
                }
                Result.success(workoutEntries)
            } else {
                Result.failure(Exception(response.message ?: "Erreur lors de la récupération de l'historique"))
            }
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur getCalendarHistory: ${e.message}")
            Result.failure(e)
        }
    }

    // Convertir les données de workout backend en WorkoutEntry
    private fun convertWorkoutToWorkoutEntry(workoutData: Any): WorkoutEntry? {
        return try {
            // Le backend retourne des Map<String, Any> pour les données de workout
            val workout = workoutData as? Map<String, Any> ?: return null
            
            // Parser la date - essayer différents formats
            val dateStr = workout["date"]?.toString() ?: workout["date_debut"]?.toString() ?: return null
            val date = try {
                when {
                    dateStr.contains("T") -> java.time.LocalDate.parse(dateStr.split("T")[0])
                    else -> java.time.LocalDate.parse(dateStr)
                }
            } catch (e: Exception) {
                android.util.Log.w("ApiService", "Erreur parsing date: $dateStr")
                return null
            }

            // Récupérer les informations de base
            val nom = workout["nom"]?.toString() ?: "Séance"
            val duree = (workout["duree"]?.toString()?.toIntOrNull()) ?: 
                       (workout["duree_totale"]?.toString()?.toIntOrNull()) ?: 0
            
            // Récupérer les exercices s'ils existent
            val exercicesData = workout["exercices"] as? List<Any> ?: emptyList()
            val exercises = exercicesData.mapNotNull { exerciceData ->
                val exercice = exerciceData as? Map<String, Any> ?: return@mapNotNull null
                try {
                    ExerciseRecord(
                        name = exercice["nom"]?.toString() ?: exercice["machine_nom"]?.toString() ?: "Exercice",
                        sets = exercice["series"]?.toString()?.toIntOrNull() ?: 1,
                        reps = exercice["repetitions"]?.toString()?.toIntOrNull() ?: 
                              exercice["reps"]?.toString()?.toIntOrNull() ?: 0,
                        weight = exercice["poids"]?.toString()?.toDoubleOrNull() ?: 
                               exercice["weight"]?.toString()?.toDoubleOrNull() ?: 0.0
                    )
                } catch (e: Exception) {
                    null
                }
            }

            WorkoutEntry(
                date = date,
                mode = nom,
                exercises = exercises,
                duration = duree,
                totalWeight = exercises.sumOf { it.weight * it.reps }
            )
        } catch (e: Exception) {
            android.util.Log.w("ApiService", "Erreur conversion workout: ${e.message}")
            null
        }
    }

    // Convertir UserResponse en ProfileData pour l'Android
    fun convertUserResponseToProfileData(user: UserResponse): ProfileData {
        // Mapper objectif_sportif vers les valeurs Android
        val objectifAndroid = when (user.objectifSportif?.uppercase()) {
            "PRISE_MASSE" -> "Prise de masse"
            "PERTE_POIDS", "SECHE" -> "Perte de poids"
            "REMISE_FORME" -> "Remise en forme"
            "FORCE" -> "Force"
            "ENDURANCE" -> "Endurance"
            "MAINTENIR", "MAINTIEN" -> "Maintenir"
            else -> "Maintenir"
        }

        // Mapper niveau_experience vers niveauActivite Android
        val niveauActiviteAndroid = when (user.niveauExperience?.uppercase()) {
            "DEBUTANT" -> "Débutant"
            "INTERMEDIAIRE" -> "Modéré"
            "AVANCE", "EXPERT" -> "Intensif"
            else -> "Modéré"
        }

        return ProfileData(
            nom = "${user.prenom} ${user.nom}".trim(),
            email = user.email,
            dateNaissance = user.dateNaissance ?: "1990-01-01",
            poids = user.poids ?: 70.0,
            taille = user.taille?.toInt() ?: 170,
            genre = "Homme", // Valeur par défaut - à améliorer si le backend ajoute ce champ
            niveauActivite = niveauActiviteAndroid,
            objectif = objectifAndroid
        )
    }

    // Récupérer les statistiques utilisateur depuis le backend
    suspend fun getUserStatistics(): Result<UserStatsDto> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            val response = api.getUserStats()
            if (response.success && response.data != null) {
                Result.success(response.data)
            } else {
                Result.failure(Exception(response.message ?: "Erreur lors de la récupération des statistiques"))
            }
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur getUserStatistics: ${e.message}")
            Result.failure(e)
        }
    }

    // Mettre à jour le profil utilisateur vers le backend
    suspend fun updateUserProfile(profileData: ProfileData): Result<UserResponse> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            // Mapper ProfileData Android vers le format backend
            val objectifBackend = when (profileData.objectif) {
                "Prise de masse" -> "PRISE_MASSE"
                "Perte de poids" -> "SECHE"
                "Remise en forme" -> "REMISE_FORME"
                "Force" -> "FORCE"
                "Endurance" -> "ENDURANCE"
                "Maintenir" -> "REMISE_FORME"
                else -> "REMISE_FORME"
            }

            val niveauBackend = when (profileData.niveauActivite) {
                "Débutant" -> "DEBUTANT"
                "Modéré" -> "INTERMEDIAIRE"
                "Intensif" -> "AVANCE"
                else -> "INTERMEDIAIRE"
            }

            // Séparer nom et prénom
            val nomComplets = profileData.nom.split(" ", limit = 2)
            val prenom = if (nomComplets.size > 1) nomComplets[0] else ""
            val nom = if (nomComplets.size > 1) nomComplets[1] else nomComplets[0]

            val request = UpdateProfileRequest(
                nom = nom,
                prenom = prenom,
                date_naissance = profileData.dateNaissance,
                poids = profileData.poids,
                taille = profileData.taille.toDouble(),
                objectif_sportif = objectifBackend,
                niveau_experience = niveauBackend
            )

            val response = api.updateProfile(request)
            if (response.success && response.user != null) {
                Result.success(response.user)
            } else {
                Result.failure(Exception(response.message ?: "Erreur lors de la mise à jour du profil"))
            }
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur updateUserProfile: ${e.message}")
            Result.failure(e)
        }
    }

    // ========== NOUVELLES METHODES SEANCES SIMPLES ==========
    
    // Récupérer toutes les séances simples
    suspend fun getSimpleSessions(): Result<List<SimpleSession>> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            val response = api.getSimpleSessions()
            if (response.success) {
                Result.success(response.data)
            } else {
                Result.failure(Exception(response.message))
            }
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur getSimpleSessions: ${e.message}")
            Result.failure(e)
        }
    }

    // Importer des séances depuis CSV
    suspend fun importCsvSessions(csvData: String): Result<CsvImportResponse> {
        return try {
            if (!isInitialized) {
                AppLogger.e("CSV_API", "❌ ApiService non initialisé")
                return Result.failure(Exception("ApiService non initialisé"))
            }

            AppLogger.api("CSV_API", "🚀 Début import CSV vers serveur")
            AppLogger.d("CSV_API", "   Taille données CSV: ${csvData.length} caractères")
            AppLogger.d("CSV_API", "   Premières lignes: ${csvData.take(200)}...")

            val request = CsvImportRequest(csv_data = csvData)
            AppLogger.d("CSV_API", "   Requête créée, envoi vers ${BASE_URL}/api/workouts/csv-import/")
            
            val response = api.importCsvSessions(request)
            
            AppLogger.success("CSV_API", "✅ Import CSV réussi: ${response.success}")
            AppLogger.d("CSV_API", "   Message: ${response.message}")
            AppLogger.d("CSV_API", "   Séances créées: ${response.imported_count}")
            AppLogger.d("CSV_API", "   Total lignes: ${response.total_lines}")
            AppLogger.d("CSV_API", "   Erreurs: ${response.errors_count}")
            if (response.errors.isNotEmpty()) {
                AppLogger.w("CSV_API", "   Détails erreurs: ${response.errors}")
            }
            
            Result.success(response)
        } catch (e: retrofit2.HttpException) {
            val errorBody = e.response()?.errorBody()?.string()
            AppLogger.e("CSV_API", "❌ Erreur HTTP ${e.code()}: ${e.message()}")
            AppLogger.e("CSV_API", "   URL: ${e.response()?.raw()?.request?.url}")
            AppLogger.e("CSV_API", "   Réponse serveur: $errorBody")
            Result.failure(Exception("HTTP ${e.code()}: $errorBody"))
        } catch (e: Exception) {
            AppLogger.e("CSV_API", "❌ Erreur importCsvSessions: ${e.message}", e)
            Result.failure(e)
        }
    }

    // Supprimer toutes les séances
    suspend fun deleteAllSessions(): Result<DeleteAllResponse> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            val response = api.deleteAllSessions()
            Result.success(response)
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur deleteAllSessions: ${e.message}")
            Result.failure(e)
        }
    }

    // Récupérer le résumé calendrier
    suspend fun getCalendarSummary(): Result<CalendarSummary> {
        return try {
            if (!isInitialized) {
                return Result.failure(Exception("ApiService non initialisé"))
            }

            val response = api.getCalendarSummary()
            if (response.success) {
                Result.success(response.data)
            } else {
                Result.failure(Exception(response.message))
            }
        } catch (e: Exception) {
            android.util.Log.e("ApiService", "Erreur getCalendarSummary: ${e.message}")
            Result.failure(e)
        }
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
            if (!apiService.isApiAvailable()) {
                return Result.failure(Exception("❌ Service non disponible. Vérifiez votre connexion internet."))
            }

            val request = LoginRequest(email, password)
            val response = apiService.getApi().login(request)

            if (response.success && response.token != null) {
                // Sauvegarder le token
                apiService.saveAuthToken(context, response.token)

                // Récupérer le profil complet après connexion réussie
                try {
                    val profileResponse = apiService.getApi().getProfile()
                    if (profileResponse.success && profileResponse.user != null) {
                        // Utiliser les données complètes du profil
                        val completeUser = profileResponse.user
                        val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
                        prefs.edit().apply {
                            putString("user_email", completeUser.email)
                            putString("user_nom", completeUser.nom)
                            putString("user_prenom", completeUser.prenom)
                            putBoolean("is_logged_in", true)
                            apply()
                        }
                        
                        // Retourner la réponse avec les données complètes du profil
                        return Result.success(response.copy(user = completeUser))
                    }
                } catch (e: Exception) {
                    android.util.Log.w("AuthManager", "Erreur récupération profil: ${e.message}")
                }

                // Fallback : utiliser les données de base de login
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
            Result.failure(Exception("❌ Erreur de connexion: ${e.message}"))
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
            if (!apiService.isApiAvailable()) {
                return Result.failure(Exception("❌ Service non disponible. Vérifiez votre connexion internet."))
            }

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
            // En cas d'erreur réseau
            Result.failure(Exception("❌ Erreur lors de l'inscription: ${e.message}"))
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

            // Construire les données pour la nouvelle API des séances effectuées
            val exercicesEffectues = exercises.mapIndexed { index, exercise ->
                // Simuler des séries (pour les anciennes données on fait 1 série avec les totaux)
                val seriesData = listOf(
                    SerieEffectueeData(
                        numero = 1,
                        repetitions_prevues = exercise.reps,
                        repetitions_realisees = exercise.reps,
                        poids_utilise = exercise.weight
                    )
                )
                
                // CORRECTION: Trouver le vrai machine_id
                val machineId = try {
                    // Recherche dans la liste des machines par nom
                    val machines = apiService.getApi().getMachines()
                    val foundMachine = machines.results.find { machine -> 
                        machine.nom.equals(exercise.name, ignoreCase = true) 
                    }
                    foundMachine?.id ?: 1 // Fallback si pas trouvé
                } catch (e: Exception) {
                    android.util.Log.w("ApiService", "⚠️ Impossible de trouver machine pour ${exercise.name}: ${e.message}")
                    1 // ID par défaut si erreur
                }
                
                android.util.Log.d("SEANCE_SAVE", "📝 Exercice: ${exercise.name} -> Machine ID: $machineId")
                
                ExerciceEffectueData(
                    nom_exercice = exercise.name,
                    machine_id = machineId,
                    series = seriesData
                )
            }

            val dateFin = try {
                val startTime = java.time.LocalDateTime.parse(dateDebut.replace("Z", ""))
                startTime.plusMinutes(dureeMinutes.toLong()).toString()
            } catch (e: Exception) {
                dateDebut // Fallback si parsing échoue
            }

            val request = SeanceEffectueeRequest(
                nom = nom,
                date_debut = dateDebut,
                date_fin = dateFin,
                note_ressenti = 7, // Valeur par défaut
                commentaire = "Séance synchronisée depuis l'app mobile",
                exercices = exercicesEffectues
            )

            // LOGS DÉTAILLÉS POUR DEBUG
            android.util.Log.d("SEANCE_SAVE", "🔄 Tentative sauvegarde séance effectuée:")
            android.util.Log.d("SEANCE_SAVE", "   • Nom: $nom")
            android.util.Log.d("SEANCE_SAVE", "   • Date début: $dateDebut")
            android.util.Log.d("SEANCE_SAVE", "   • Date fin: $dateFin")
            android.util.Log.d("SEANCE_SAVE", "   • Durée: $dureeMinutes min")
            android.util.Log.d("SEANCE_SAVE", "   • Nombre exercices: ${exercicesEffectues.size}")
            
            // Utiliser le nouvel endpoint pour les séances effectuées
            val response = apiService.getApi().saveSeanceEffectuee(request)
            
            if (response.success) {
                android.util.Log.d("SEANCE_SAVE", "✅ Séance sauvegardée avec succès dans la table SeanceEffectuee")
            } else {
                android.util.Log.e("SEANCE_SAVE", "❌ Échec sauvegarde séance effectuée")
            }
            
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
