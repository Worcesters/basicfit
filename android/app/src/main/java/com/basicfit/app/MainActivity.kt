package com.basicfit.app

import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.google.gson.reflect.TypeToken
import java.time.LocalDate
import java.time.LocalTime
import java.time.Period
import java.time.format.DateTimeFormatter
import kotlinx.coroutines.delay
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import kotlinx.coroutines.MainScope
import com.basicfit.app.data.AuthManager
import kotlin.math.roundToInt
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.ui.graphics.Brush
import androidx.core.view.WindowCompat
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.foundation.Image
import androidx.compose.ui.res.painterResource
import com.basicfit.app.R
import coil.compose.AsyncImage
import coil.request.ImageRequest
import coil.decode.GifDecoder
import coil.ImageLoader
import androidx.compose.ui.layout.ContentScale
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext

// Palette couleur globale
val Mint = Color(0xFF00C9A7)
val SoftBlue = Color(0xFF6DD5ED)
val LightBackground = Color(0xFFF0F4F8)
val TextPrimary = Color(0xFF083D3B) // teal foncé, bonne lisibilité
val TextSecondary = Color(0xFF4E6E6E)
val Accent = Mint                    // accent principal
val AccentLight = SoftBlue.copy(alpha = .15f)  // fond doux

// Data classes
data class ProfileData(
    val nom: String,
    val email: String,
    val dateNaissance: String,
    val poids: Double,
    val taille: Int,
    val genre: String,
    val niveauActivite: String,
    val objectif: String = "Maintenir"
)

data class WorkoutEntry(
    val date: LocalDate,
    val mode: String,
    val exercises: List<ExerciseRecord>,
    val duration: Int,
    val totalWeight: Double
)

data class ExerciseRecord(
    val name: String,
    val sets: Int,
    val reps: Int,
    val weight: Double
)

data class ExerciseRecommendation(
    val sets: Int,
    val reps: Int,
    val weight: Double,
    val restTime: Int,
    val notes: String,
    val tempo: String = "3-1-2"  // Nouveau champ pour le tempo
)

// Data classes pour l'entraînement avancé
data class WorkoutSession(
    val workoutName: String,
    val exercises: List<ExerciseSession>,
    val startTime: Long = System.currentTimeMillis(),
    var currentExerciseIndex: Int = 0,
    var isCompleted: Boolean = false
)

data class ExerciseSession(
    val machine: Machine,
    val targetSets: Int,
    val targetReps: Int,
    val recommendedWeight: Double,
    val restTime: Int, // en secondes
    val sets: MutableList<SetRecord> = mutableListOf(),
    var isCompleted: Boolean = false
)

data class SetRecord(
    val weight: Double,
    val reps: Int,
    val completed: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

// Classe DataManager pour gérer les données
class DataManager(private val context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
    // Gson avec support LocalDate (format ISO)
    private val gson: Gson = GsonBuilder()
        .registerTypeAdapter(java.time.LocalDate::class.java, object : com.google.gson.JsonSerializer<java.time.LocalDate>, com.google.gson.JsonDeserializer<java.time.LocalDate> {
            override fun serialize(src: java.time.LocalDate?, typeOfSrc: java.lang.reflect.Type?, context: com.google.gson.JsonSerializationContext?): com.google.gson.JsonElement {
                return com.google.gson.JsonPrimitive(src?.toString())
            }

            override fun deserialize(json: com.google.gson.JsonElement?, typeOfT: java.lang.reflect.Type?, context: com.google.gson.JsonDeserializationContext?): java.time.LocalDate {
                if (json == null) return java.time.LocalDate.now()

                return if (json.isJsonPrimitive && json.asJsonPrimitive.isString) {
                    // Nouveau format ISO "yyyy-MM-dd"
                    java.time.LocalDate.parse(json.asString)
                } else if (json.isJsonObject) {
                    // Ancien format Gson par défaut : objet avec year / month / day
                    val obj = json.asJsonObject
                    val year = obj["year"]?.asInt ?: obj["YEAR"]?.asInt ?: 1970
                    // Certains dumps contiennent monthValue, d'autres month (1-12)
                    val month = obj["monthValue"]?.asInt ?: obj["month"]?.asInt ?: 1
                    val day = obj["dayOfMonth"]?.asInt ?: obj["day"]?.asInt ?: 1
                    java.time.LocalDate.of(year, month, day)
                } else {
                    // Valeur inattendue → date par défaut
                    java.time.LocalDate.now()
                }
            }
        })
        .create()

    fun saveProfileData(profile: ProfileData) {
        val json = gson.toJson(profile)
        prefs.edit().putString("profile_data", json).apply()
    }

    fun loadProfileData(): ProfileData {
        val json = prefs.getString("profile_data", null)
        return if (json != null) {
            try {
                gson.fromJson(json, ProfileData::class.java)
            } catch (e: Exception) {
                ProfileData("", "", "", 70.0, 170, "Homme", "Modéré", "Maintenir")
            }
        } else {
            ProfileData("", "", "", 70.0, 170, "Homme", "Modéré", "Maintenir")
        }
    }

    fun saveWorkoutHistory(workoutHistory: List<WorkoutEntry>) {
        val json = gson.toJson(workoutHistory)
        prefs.edit().putString("workout_history", json).apply()
    }

    fun loadWorkoutHistory(): List<WorkoutEntry> {
        val json = prefs.getString("workout_history", null)
        return if (json != null) {
            val type = object : TypeToken<List<WorkoutEntry>>() {}.type
            gson.fromJson(json, type)
        } else {
            emptyList()
        }
    }

    fun getTotalStats(): Triple<Int, Int, Int> {
        val workoutHistory = loadWorkoutHistory()
        // Filtrer uniquement les séances complétées
        val completedWorkouts = workoutHistory.filter { it.duration > 0 }
        val totalSessions = completedWorkouts.size
        val totalMinutes = completedWorkouts.sumOf { it.duration }
        val totalCalories = completedWorkouts.sumOf { calculateBurnedCalories(loadProfileData().poids, it.duration, "Modéré") }
        return Triple(totalSessions, totalMinutes, totalCalories)
    }

    fun isUserLoggedIn(): Boolean {
        // On considère l'utilisateur connecté uniquement si le flag est présent
        // ET si un token d'authentification est stocké.
        val flag = prefs.getBoolean("is_logged_in", false)
        val token = prefs.getString("auth_token", null)
        return flag && !token.isNullOrBlank()
    }

    fun setUserLoggedIn(isLoggedIn: Boolean) {
        prefs.edit().putBoolean("is_logged_in", isLoggedIn).apply()
    }

    fun clearUserData() {
        prefs.edit().clear().apply()
    }

    fun resetStats() {
        // Réinitialiser les statistiques pour les nouveaux utilisateurs
        prefs.edit()
            .remove("workout_history")
            .apply()
    }

    // Nouvelles méthodes pour sauvegarder l'état d'entraînement en cours
    fun saveCurrentWorkoutSession(session: WorkoutSession?) {
        if (session != null) {
            val json = gson.toJson(session)
            prefs.edit().putString("current_workout_session", json).apply()
        } else {
            prefs.edit().remove("current_workout_session").apply()
        }
    }

    fun loadCurrentWorkoutSession(): WorkoutSession? {
        val json = prefs.getString("current_workout_session", null)
        return if (json != null) {
            try {
                gson.fromJson(json, WorkoutSession::class.java)
            } catch (e: Exception) {
                null
            }
        } else {
            null
        }
    }

    fun saveWorkoutInProgress(isInProgress: Boolean) {
        prefs.edit().putBoolean("workout_in_progress", isInProgress).apply()
    }

    fun isWorkoutInProgress(): Boolean {
        return prefs.getBoolean("workout_in_progress", false)
    }

    fun clearCurrentWorkout() {
        prefs.edit()
            .remove("current_workout_session")
            .putBoolean("workout_in_progress", false)
            .apply()
    }
}

// Fonction pour convertir l'historique serveur en format local
fun convertServerHistoryToLocal(serverHistory: List<Any>): List<WorkoutEntry> {
    return serverHistory.mapNotNull { serverEntry ->
        try {
            val entry = serverEntry as? Map<*, *>
            if (entry != null) {
                val dateStr = entry["date_debut"] as? String ?: entry["date_prevue"] as? String
                val date = if (dateStr != null) {
                    try {
                        LocalDate.parse(dateStr.substring(0, 10))
                    } catch (e: Exception) {
                        LocalDate.now()
                    }
                } else LocalDate.now()

                val exercices = (entry["exercices"] as? List<*>)?.mapNotNull { exo ->
                    val exoMap = exo as? Map<*, *>
                    if (exoMap != null) {
                        ExerciseRecord(
                            name = exoMap["machine__nom"] as? String ?: "Exercice",
                            sets = (exoMap["nombre_series"] as? Number)?.toInt() ?: 3,
                            reps = (exoMap["repetitions_prevues"] as? Number)?.toInt() ?: 10,
                            weight = (exoMap["poids_utilise"] as? Number)?.toDouble() ?: 0.0
                        )
                    } else null
                } ?: emptyList()

                WorkoutEntry(
                    date = date,
                    mode = entry["nom"] as? String ?: "Séance",
                    exercises = exercices,
                    duration = (entry["duree_reelle"] as? Number)?.toInt() ?: 45,
                    totalWeight = exercices.sumOf { it.weight * it.reps }
                )
            } else null
        } catch (e: Exception) {
            android.util.Log.e("ConvertServerHistory", "Erreur conversion: ${e.message}")
            null
        }
    }
}

// Fonctions utilitaires
fun calculateAge(dateNaissance: String): Int {
    return try {
        // Accepte ISO (yyyy-MM-dd) et format français (dd/MM/yyyy)
        val formats = listOf(
            DateTimeFormatter.ofPattern("yyyy-MM-dd"),
            DateTimeFormatter.ofPattern("dd/MM/yyyy")
        )
        val birthDate = formats.firstNotNullOf { fmt ->
            runCatching { LocalDate.parse(dateNaissance, fmt) }.getOrNull()
        }
        val currentDate = LocalDate.now()
        Period.between(birthDate, currentDate).years
    } catch (e: Exception) {
        25
    }
}

fun calculateBMI(weight: Double, height: Int): Double {
    return if (weight > 0 && height > 0) {
        val heightM = height / 100.0
        weight / (heightM * heightM)
    } else {
        0.0
    }
}

fun getBmiCategory(bmi: Double): String {
    return when {
        bmi == 0.0 -> "N/A"
        bmi < 18.5 -> "Insuffisance pondérale"
        bmi < 25 -> "Corpulence normale"
        bmi < 30 -> "Surpoids"
        else -> "Obésité"
    }
}

fun calculateDailyCalories(age: Int, weight: Double, height: Int, gender: String, niveauActivite: String): Int {
    val bmr = if (gender.lowercase() == "homme") {
        (10 * weight + 6.25 * height - 5 * age + 5)
    } else {
        (10 * weight + 6.25 * height - 5 * age - 161)
    }

    val activityFactor = when (niveauActivite) {
        "Sédentaire" -> 1.2
        "Léger" -> 1.375
        "Modéré" -> 1.55
        "Actif" -> 1.725
        "Très actif" -> 1.9
        else -> 1.55
    }

    return (bmr * activityFactor).toInt()
}

fun calculateGoalBasedCalories(age: Int, weight: Double, height: Int, gender: String, niveauActivite: String, objectif: String): Int {
    val basalCalories = calculateDailyCalories(age, weight, height, gender, niveauActivite)

    return when (objectif) {
        "Perdre du poids" -> (basalCalories * 0.8).toInt() // Déficit de 20%
        "Prise de masse" -> (basalCalories * 1.2).toInt() // Surplus de 20%
        "Sèche" -> (basalCalories * 0.75).toInt() // Déficit de 25%
        else -> basalCalories // Maintenir
    }
}

fun getNutritionalRecommendations(objectif: String, weight: Double): Map<String, String> {
    return when (objectif) {
        "Perdre du poids" -> mapOf(
            "Protéines" to "${(weight * 2.2).toInt()}g/jour",
            "Glucides" to "${(weight * 2.0).toInt()}g/jour",
            "Lipides" to "${(weight * 0.8).toInt()}g/jour",
            "Conseil" to "Déficit calorique de 300-500 kcal/jour"
        )
        "Prise de masse" -> mapOf(
            "Protéines" to "${(weight * 2.5).toInt()}g/jour",
            "Glucides" to "${(weight * 4.0).toInt()}g/jour",
            "Lipides" to "${(weight * 1.2).toInt()}g/jour",
            "Conseil" to "Surplus calorique de 300-500 kcal/jour"
        )
        "Sèche" -> mapOf(
            "Protéines" to "${(weight * 2.8).toInt()}g/jour",
            "Glucides" to "${(weight * 1.5).toInt()}g/jour",
            "Lipides" to "${(weight * 0.6).toInt()}g/jour",
            "Conseil" to "Déficit calorique strict de 500-700 kcal/jour"
        )
        else -> mapOf(
            "Protéines" to "${(weight * 2.0).toInt()}g/jour",
            "Glucides" to "${(weight * 3.0).toInt()}g/jour",
            "Lipides" to "${(weight * 1.0).toInt()}g/jour",
            "Conseil" to "Maintenir l'équilibre calorique"
        )
    }
}

fun getPersonalizedTips(profile: ProfileData): List<String> {
    val tips = mutableListOf<String>()
    val age = calculateAge(profile.dateNaissance)
    val bmi = calculateBMI(profile.poids, profile.taille)

    if (age < 25) {
        tips.add("Concentrez-vous sur l'apprentissage des mouvements de base")
    } else if (age > 50) {
        tips.add("Privilégiez les exercices de mobilité et d'équilibre")
    }

    when {
        bmi < 18.5 -> tips.add("Augmentez vos apports caloriques et focalisez sur la prise de masse")
        bmi > 25 -> tips.add("Combinez exercices cardiovasculaires et musculation")
        bmi > 30 -> tips.add("Commencez par des exercices à faible impact")
    }

    when (profile.niveauActivite) {
        "Sédentaire" -> tips.add("Commencez progressivement avec 2-3 séances par semaine")
        "Très actif" -> tips.add("Variez vos entraînements pour éviter la stagnation")
    }

    return tips
}

fun calculateBurnedCalories(weight: Double, duration: Int, intensity: String): Int {
    val metValue = when (intensity) {
        "Léger" -> 3.0
        "Modéré" -> 5.0
        "Intense" -> 8.0
        else -> 5.0
    }
    return ((metValue * weight * (duration / 60.0)) * 1.05).toInt()
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Couleur de la barre de statut
        WindowCompat.setDecorFitsSystemWindows(window, true)
        window.statusBarColor = Mint.toArgb()
        setContent {
            MycTheme {
                MainScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen() {
    val context = LocalContext.current
    val dataManager = remember { DataManager(context) }

    var selectedTabIndex by remember { mutableStateOf(0) }
    var profileData by remember { mutableStateOf(dataManager.loadProfileData()) }
    var workoutHistory by remember { mutableStateOf(dataManager.loadWorkoutHistory()) }
    var workoutInProgress by remember { mutableStateOf(dataManager.isWorkoutInProgress()) }
    var currentWorkoutMachines by remember { mutableStateOf<List<Machine>>(emptyList()) }
    var currentWorkoutName by remember { mutableStateOf("") }
    var isLoggedIn by remember { mutableStateOf(dataManager.isUserLoggedIn()) }
    var showWorkoutSummary by remember { mutableStateOf(false) }
    var lastWorkoutSummary by remember { mutableStateOf<WorkoutSummary?>(null) }
    var showStatistics by remember { mutableStateOf(false) }
    var syncStatus by remember { mutableStateOf("") }
    var lastSyncTime by remember { mutableStateOf("") }
    var connectionStatus by remember { mutableStateOf("Vérification...") }
    var isOnline by remember { mutableStateOf(false) }
    var selectedCalendarEntry by remember { mutableStateOf<WorkoutEntry?>(null) }

    // État pour forcer la mise à jour des recommandations
    var forceRecommendationUpdate by remember { mutableStateOf(0) }

    // Restaurer l'état d'entraînement en cours si nécessaire
    LaunchedEffect(Unit) {
        if (dataManager.isWorkoutInProgress()) {
            val savedSession = dataManager.loadCurrentWorkoutSession()
            if (savedSession != null) {
                // Restaurer l'état d'entraînement
                currentWorkoutName = savedSession.workoutName
                currentWorkoutMachines = savedSession.exercises.map { it.machine }
                workoutInProgress = true

                // Afficher une notification de restauration
                android.widget.Toast.makeText(
                    context,
                    "✅ Votre entraînement a été restauré",
                    android.widget.Toast.LENGTH_SHORT
                ).show()
            } else {
                // État incohérent, nettoyer
                dataManager.clearCurrentWorkout()
                workoutInProgress = false
            }
        }
    }

    // Vérifier la connectivité au démarrage
    LaunchedEffect(Unit) {
        try {
            val apiService = ApiService.getInstance()
            apiService.initialize(context)
            val serverReachable = apiService.isServerReachable()
            isOnline = serverReachable
            connectionStatus = if (serverReachable) "🟢 Connecté au serveur" else "🔴 Mode hors ligne"
        } catch (e: Exception) {
            isOnline = false
            connectionStatus = "🔴 Mode hors ligne"
        }
    }

    // Synchroniser automatiquement les données pour les utilisateurs connectés
    LaunchedEffect(isLoggedIn, isOnline) {
        if (isLoggedIn && isOnline) {
            val syncManager = SyncManager(context)
            try {
                android.util.Log.d("CalendarSync", "🔄 Début synchronisation automatique calendrier")
                // Récupérer l'historique depuis le serveur
                val serverHistory = syncManager.syncWorkoutHistory()
                serverHistory.onSuccess { history ->
                    // Fusionner avec l'historique local
                    val serverWorkoutHistory = convertServerHistoryToLocal(history)
                    val newHistory = (workoutHistory + serverWorkoutHistory).distinctBy { 
                        "${it.date}_${it.mode}_${it.duration}" 
                    }
                    if (newHistory.size != workoutHistory.size) {
                        workoutHistory = newHistory
                        dataManager.saveWorkoutHistory(workoutHistory)
                        android.util.Log.d("CalendarSync", "✅ Calendrier synchronisé: ${workoutHistory.size} séances")
                    } else {
                        android.util.Log.d("CalendarSync", "ℹ️ Aucune nouvelle séance à synchroniser")
                    }
                }
                serverHistory.onFailure { error ->
                    android.util.Log.w("CalendarSync", "⚠️ Échec synchronisation: ${error.message}")
                }
            } catch (e: Exception) {
                android.util.Log.e("CalendarSync", "❌ Erreur synchronisation calendrier: ${e.message}")
            }
        }
    }

    if (!isLoggedIn) {
        // Écran de connexion/inscription
        AuthScreen(
            onLoginSuccess = { userProfile ->
                profileData = userProfile
                dataManager.saveProfileData(userProfile)
                dataManager.setUserLoggedIn(true)
                // On réinitialise l'historique local afin d'éviter d'afficher 200 séances par défaut
                // pour les nouveaux comptes ou les utilisateurs venant de se connecter sans données.
                dataManager.resetStats()
                isLoggedIn = true

                // Synchroniser les données depuis le serveur
                val syncManager = SyncManager(context)
                kotlinx.coroutines.GlobalScope.launch {
                    try {
                        // Récupérer l'historique depuis le serveur
                        val serverHistory = syncManager.syncWorkoutHistory()
                        kotlinx.coroutines.MainScope().launch {
                                                    serverHistory.onSuccess { history ->
                            // Fusionner avec l'historique local
                            val serverWorkoutHistory = convertServerHistoryToLocal(history)
                            workoutHistory = (workoutHistory + serverWorkoutHistory).distinctBy { it.date }
                            dataManager.saveWorkoutHistory(workoutHistory)
                            android.util.Log.d("Sync", "Historique synchronisé: ${workoutHistory.size} séances")
                        }
                        }
                    } catch (e: Exception) {
                        // Continuer avec les données locales en cas d'erreur réseau
                    }
                }
            }
        )
    } else if (showStatistics) {
        // Écran des statistiques
        StatisticsScreen(
            profileData = profileData,
            workoutHistory = workoutHistory,
            onBack = { showStatistics = false }
        )
    } else if (showWorkoutSummary && lastWorkoutSummary != null) {
        // Écran de récapitulatif d'entraînement
        WorkoutSummaryScreen(
            workoutSummary = lastWorkoutSummary!!,
            workoutHistory = workoutHistory,
            profileData = profileData,
            onContinue = {
                showWorkoutSummary = false
                lastWorkoutSummary = null
            }
        )
    } else if (selectedCalendarEntry != null) {
        // Écran de détails d'une séance du calendrier
        CalendarEntryDetailScreen(
            entry = selectedCalendarEntry!!,
            workoutHistory = workoutHistory,
            profileData = profileData,
            onBack = {
                selectedCalendarEntry = null
            },
            onStartWorkout = { machines, workoutName ->
                selectedCalendarEntry = null
                currentWorkoutMachines = machines
                currentWorkoutName = workoutName
                workoutInProgress = true
            },
            onWorkoutHistoryChange = { newWorkoutHistory ->
                workoutHistory = newWorkoutHistory
                dataManager.saveWorkoutHistory(workoutHistory)
            }
        )
    } else if (workoutInProgress) {
        // Écran d'entraînement en cours
        WorkoutInProgressScreen(
            workoutName = currentWorkoutName,
            machines = currentWorkoutMachines,
            profileData = profileData,
            workoutHistory = workoutHistory,
            dataManager = dataManager,
            onFinishWorkout = { duration, exercisesCompleted ->
                // Sauvegarder la séance
                val newEntry = WorkoutEntry(
                    date = LocalDate.now(),
                    mode = currentWorkoutName,
                    exercises = exercisesCompleted,
                    duration = duration,
                    totalWeight = exercisesCompleted.sumOf { it.weight * it.reps }
                )
                workoutHistory = workoutHistory + newEntry
                dataManager.saveWorkoutHistory(workoutHistory)

                // SUPPRIMÉ: Premier envoi pour éviter les doublons
                // L'envoi au serveur est maintenant géré uniquement par SyncManager plus bas

                // Nettoyer l'état d'entraînement sauvegardé
                dataManager.clearCurrentWorkout()

                // Créer le récapitulatif
                val age = calculateAge(profileData.dateNaissance)
                val totalCalories = calculateBurnedCalories(profileData.poids, duration, profileData.niveauActivite)
                val personalRecords = emptyList<String>() // Simplifié pour l'instant

                lastWorkoutSummary = WorkoutSummary(
                    workoutName = currentWorkoutName,
                    date = LocalDate.now(),
                    duration = duration,
                    totalCalories = totalCalories,
                    totalVolume = exercisesCompleted.sumOf { it.weight * it.reps },
                    exercicesCompleted = exercisesCompleted,
                    averageRest = 90, // Valeur par défaut
                    personalRecords = personalRecords
                )

                // Forcer la mise à jour des recommandations pour le prochain entraînement
                // Les recommandations se mettront à jour automatiquement grâce au remember(workoutHistory)
                
                // AJOUT: Synchronisation de la séance terminée vers l'API
                val syncManager = SyncManager(context)
                kotlinx.coroutines.GlobalScope.launch {
                    try {
                        android.util.Log.d("WorkoutSync", "🔄 Synchronisation séance terminée: ${newEntry.mode}")
                        val result = syncManager.saveWorkoutToServer(
                            nom = newEntry.mode,
                            dateDebut = "${newEntry.date}T${LocalTime.now()}",
                            dureeMinutes = newEntry.duration,
                            exercises = newEntry.exercises
                        )
                        
                        if (result.isSuccess) {
                            android.util.Log.d("WorkoutSync", "✅ Séance terminée synchronisée avec la BDD")
                            kotlinx.coroutines.MainScope().launch {
                                android.widget.Toast.makeText(context, "✅ Séance synchronisée avec la base de données", android.widget.Toast.LENGTH_SHORT).show()
                            }
                        } else {
                            android.util.Log.e("WorkoutSync", "❌ Erreur sync BDD: ${result.exceptionOrNull()?.message}")
                        }
                    } catch (e: Exception) {
                        android.util.Log.e("WorkoutSync", "❌ Exception sync séance: ${e.message}")
                    }
                }

                // Passer à l'écran de récapitulatif
                workoutInProgress = false
                currentWorkoutMachines = emptyList()
                currentWorkoutName = ""
                showWorkoutSummary = true
            },
            onExitWorkout = {
                // Nettoyer l'état d'entraînement sauvegardé
                dataManager.clearCurrentWorkout()
                workoutInProgress = false
                currentWorkoutMachines = emptyList()
                currentWorkoutName = ""
            }
        )
    } else {
        // Interface normale (après connexion)
        AppMainInterface(
            selectedTabIndex = selectedTabIndex,
            onTabChange = { selectedTabIndex = it },
            profileData = profileData,
            workoutHistory = workoutHistory,
            dataManager = dataManager,
            onProfileUpdate = { newProfile ->
                profileData = newProfile
                dataManager.saveProfileData(newProfile)
            },
            onStartWorkout = { machines, workoutName ->
                currentWorkoutMachines = machines
                currentWorkoutName = workoutName
                workoutInProgress = true
            },
            onShowStatistics = { showStatistics = true },
            onCsvImported = { imported ->
                // Fusionne les entrées par date
                val combined = (workoutHistory + imported).groupBy { it.date }.map { (date, entries) ->
                    if (entries.size == 1) {
                        entries.first()
                    } else {
                        // concatène les exercices & somme la durée/poids
                        val allExercises = entries.flatMap { it.exercises }
                        WorkoutEntry(
                            date = date,
                            mode = "Import CSV",
                            exercises = allExercises,
                            duration = entries.sumOf { it.duration },
                            totalWeight = allExercises.sumOf { it.weight * it.reps }
                        )
                    }
                }
                workoutHistory = combined.sortedBy { it.date }
                dataManager.saveWorkoutHistory(workoutHistory)

                // AJOUT: Envoi des séances importées par CSV vers l'API
                val syncManager = SyncManager(context)
                val apiService = ApiService.getInstance()
                apiService.initialize(context)
                
                kotlinx.coroutines.GlobalScope.launch {
                    try {
                        var successCount = 0
                        var errorCount = 0
                        
                        imported.forEach { importedEntry ->
                            android.util.Log.d("CsvImport", "🔍 Traitement séance: ${importedEntry.mode} du ${importedEntry.date}")
                            android.util.Log.d("CsvImport", "   Durée: ${importedEntry.duration} min")
                            android.util.Log.d("CsvImport", "   Exercices: ${importedEntry.exercises.size}")
                            
                            try {
                                // Pour les séances importées CSV (planifiées), utiliser planWorkout
                                android.util.Log.d("CsvImport", "📤 Planification séance vers API...")
                                
                                val planRequest = PlanWorkoutRequest(
                                    nom = importedEntry.mode,
                                    date = "${importedEntry.date}T12:00:00Z",
                                    duree = if (importedEntry.exercises.isEmpty()) 45 else importedEntry.exercises.size * 5, // Estimation
                                    commentaire = "Importé depuis CSV - ${importedEntry.exercises.size} exercices"
                                )
                                
                                val response = apiService.getApi().planWorkout(planRequest)
                                
                                if (response.success) {
                                    successCount++
                                    android.util.Log.d("CsvImport", "✅ Séance CSV planifiée: ${importedEntry.mode}")
                                } else {
                                    errorCount++
                                    android.util.Log.e("CsvImport", "❌ Erreur planification CSV: ${response.message}")
                                }
                            } catch (e: Exception) {
                                errorCount++
                                android.util.Log.e("CsvImport", "❌ Exception planification CSV: ${e.message}")
                                android.util.Log.e("CsvImport", "   Séance: ${importedEntry.mode}")
                            }
                        }
                        
                        kotlinx.coroutines.MainScope().launch {
                            android.widget.Toast.makeText(context, "✅ Import CSV synchronisé avec la base de données", android.widget.Toast.LENGTH_LONG).show()
                        }
                        
                    } catch (e: Exception) {
                        android.util.Log.e("CsvImport", "❌ Erreur synchronisation CSV: ${e.message}")
                        kotlinx.coroutines.MainScope().launch {
                            android.widget.Toast.makeText(context, "⚠️ Import local réussi, erreur synchronisation serveur", android.widget.Toast.LENGTH_LONG).show()
                        }
                    }
                }
            },
                onWorkoutHistoryChange = { newWorkoutHistory ->
        workoutHistory = newWorkoutHistory
        dataManager.saveWorkoutHistory(workoutHistory)

        // SUPPRIMÉ: Double synchronisation qui cause les doublons
        // La synchronisation se fait maintenant uniquement lors de la fin de séance
    },
            onLogout = {
                dataManager.setUserLoggedIn(false)
                dataManager.clearUserData()
                isLoggedIn = false
                profileData = ProfileData("", "", "", 70.0, 170, "Homme", "Modéré", "Maintenir")
                workoutHistory = emptyList()
            },
            selectedCalendarEntry = selectedCalendarEntry,
            onCalendarEntrySelect = { entry ->
                selectedCalendarEntry = entry
            }
        )
    }
}

@Composable
fun AuthScreen(
    onLoginSuccess: (ProfileData) -> Unit
) {
    val context = LocalContext.current
    val authManager = remember { AuthManager(context) }

    var isLoginMode by remember { mutableStateOf(true) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var nom by remember { mutableStateOf("") }
    var dateNaissance by remember { mutableStateOf("") }
    var poids by remember { mutableStateOf("") }
    var taille by remember { mutableStateOf("") }
    var genre by remember { mutableStateOf("Homme") }
    var niveauActivite by remember { mutableStateOf("Modéré") }
    var objectif by remember { mutableStateOf("Maintenir") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }
    // Nouvelle visibilité pour les champs mot de passe
    var passwordVisible by remember { mutableStateOf(false) }
    var confirmPasswordVisible by remember { mutableStateOf(false) }

    // Fonction pour gérer l'authentification
    fun handleAuth() {
        isLoading = true
        errorMessage = ""

        if (isLoginMode) {
            // Connexion
            if (email.isNotBlank() && password.isNotBlank()) {
                // Lancer la requête de connexion avec une coroutine
                GlobalScope.launch {
                    try {
                        val result = authManager.login(email, password)
                        MainScope().launch {
                            result.onSuccess { response ->
                                if (response.success) {
                                    // Créer le ProfileData avec les données de l'utilisateur
                                    val userProfile = ProfileData(
                                        nom = response.user?.nom ?: "",
                                        email = response.user?.email ?: email,
                                        dateNaissance = "1990-01-01", // Valeur par défaut
                                        poids = 70.0,
                                        taille = 170,
                                        genre = "Homme",
                                        niveauActivite = "Modéré",
                                        objectif = "Maintenir"
                                    )
                                    onLoginSuccess(userProfile)
                                } else {
                                    errorMessage = if (response.message.contains("Invalid", ignoreCase = true) ||
                                                      response.message.contains("incorrects", ignoreCase = true) ||
                                                      response.message.contains("not found", ignoreCase = true)) {
                                        "Email ou mot de passe incorrect"
                                    } else {
                                        response.message ?: "Erreur de connexion"
                                    }
                                }
                            }.onFailure { exception ->
                                errorMessage = when {
                                    exception.message?.contains("Network", ignoreCase = true) == true ->
                                        "Problème de connexion réseau"
                                    exception.message?.contains("timeout", ignoreCase = true) == true ->
                                        "Connexion trop lente, veuillez réessayer"
                                    else -> "Impossible de se connecter au serveur"
                                }
                            }
                            isLoading = false
                        }
                    } catch (e: Exception) {
                        MainScope().launch {
                            errorMessage = "Erreur de connexion inattendue"
                            isLoading = false
                        }
                    }
                }
            } else {
                errorMessage = "Veuillez remplir tous les champs"
                isLoading = false
            }
        } else {
            // Inscription
            if (email.isNotBlank() && password.isNotBlank() &&
                password == confirmPassword && nom.isNotBlank()) {

                // Lancer la requête d'inscription avec une coroutine
                GlobalScope.launch {
                    try {
                        val result = authManager.register(
                            email = email,
                            password = password,
                            nom = nom,
                            prenom = nom.split(" ").firstOrNull() ?: nom,
                            dateNaissance = dateNaissance.ifBlank { "1990-01-01" },
                            poids = poids.toDoubleOrNull() ?: 70.0,
                            taille = taille.toIntOrNull() ?: 170,
                            genre = genre,
                            objectifSportif = objectif,
                            niveauExperience = niveauActivite
                        )
                        MainScope().launch {
                            result.onSuccess { response ->
                                if (response.success) {
                                    // Créer le ProfileData avec les données de l'utilisateur
                                    val userProfile = ProfileData(
                                        nom = response.user?.nom ?: nom,
                                        email = response.user?.email ?: email,
                                        dateNaissance = dateNaissance.ifBlank { "1990-01-01" },
                                        poids = poids.toDoubleOrNull() ?: 70.0,
                                        taille = taille.toIntOrNull() ?: 170,
                                        genre = genre,
                                        niveauActivite = niveauActivite,
                                        objectif = objectif
                                    )
                                    onLoginSuccess(userProfile)
                                } else {
                                    errorMessage = response.message
                                }
                            }.onFailure { exception ->
                                errorMessage = "Erreur d'inscription: ${exception.message}"
                            }
                            isLoading = false
                        }
                    } catch (e: Exception) {
                        MainScope().launch {
                            errorMessage = "Erreur d'inscription: ${e.message}"
                            isLoading = false
                        }
                    }
                }
            } else {
                when {
                    email.isBlank() -> errorMessage = "Email requis"
                    password.isBlank() -> errorMessage = "Mot de passe requis"
                    password != confirmPassword -> errorMessage = "Les mots de passe ne correspondent pas"
                    nom.isBlank() -> errorMessage = "Nom requis"
                    else -> errorMessage = "Veuillez remplir tous les champs obligatoires"
                }
                isLoading = false
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo et titre
        Image(
            painter = painterResource(id = R.drawable.ic_app_logo),
            contentDescription = "Logo Myc",
            modifier = Modifier
                .size(120.dp)
                .padding(bottom = 16.dp)
        )

        Text(
            text = "Myc",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Accent,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        Text(
            text = if (isLoginMode) "Connectez-vous à votre compte" else "Créez votre compte",
            fontSize = 16.sp,
            color = Color.Gray,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        LazyColumn(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp)
                    ) {
                        // Champs communs (connexion et inscription)
                        OutlinedTextField(
                            value = email,
                            onValueChange = { email = it },
                            label = { Text("Email") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email)
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        OutlinedTextField(
                            value = password,
                            onValueChange = { password = it },
                            label = { Text("Mot de passe") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                            visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                            trailingIcon = {
                                val visibilityIcon = if (passwordVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility
                                val description = if (passwordVisible) "Masquer le mot de passe" else "Afficher le mot de passe"
                                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                                    Icon(imageVector = visibilityIcon, contentDescription = description)
                                }
                            }
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        if (!isLoginMode) {
                            OutlinedTextField(
                                value = confirmPassword,
                                onValueChange = { confirmPassword = it },
                                label = { Text("Confirmer le mot de passe") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                                visualTransformation = if (confirmPasswordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                                trailingIcon = {
                                    val visibilityIcon = if (confirmPasswordVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility
                                    val description = if (confirmPasswordVisible) "Masquer le mot de passe" else "Afficher le mot de passe"
                                    IconButton(onClick = { confirmPasswordVisible = !confirmPasswordVisible }) {
                                        Icon(imageVector = visibilityIcon, contentDescription = description)
                                    }
                                }
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            // Champs supplémentaires pour l'inscription
                            OutlinedTextField(
                                value = nom,
                                onValueChange = { nom = it },
                                label = { Text("Nom complet") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            // Sélecteur de date (format français)
                            val dateFormatterFr = remember { DateTimeFormatter.ofPattern("dd/MM/yyyy") }
                            val contextDate = LocalContext.current

                            OutlinedTextField(
                                value = if (dateNaissance.isBlank()) "" else try {
                                    LocalDate.parse(dateNaissance).format(dateFormatterFr)
                                } catch (_: Exception) { dateNaissance },
                                onValueChange = {},
                                label = { Text("Date de naissance") },
                                modifier = Modifier.fillMaxWidth(),
                                readOnly = true,
                                singleLine = true,
                                placeholder = { Text("JJ/MM/AAAA") },
                                trailingIcon = {
                                    IconButton(onClick = {
                                        val today = LocalDate.now()
                                        val init = try { LocalDate.parse(dateNaissance) } catch (_: Exception) { today.minusYears(25) }
                                        val datePickerDialog = android.app.DatePickerDialog(
                                            contextDate,
                                            { _, y, m, d ->
                                                val picked = LocalDate.of(y, m + 1, d)
                                                dateNaissance = picked.toString()
                                            },
                                            init.year,
                                            init.monthValue - 1,
                                            init.dayOfMonth
                                        )
                                        // Appliquer un fond blanc au DatePicker
                                        datePickerDialog.window?.setBackgroundDrawableResource(android.R.color.white)
                                        datePickerDialog.show()
                                    }) {
                                        Icon(Icons.Default.DateRange, contentDescription = "Choisir la date")
                                    }
                                }
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                OutlinedTextField(
                                    value = poids,
                                    onValueChange = { poids = it },
                                    label = { Text("Poids (kg)") },
                                    modifier = Modifier.weight(1f),
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                                )

                                OutlinedTextField(
                                    value = taille,
                                    onValueChange = { taille = it },
                                    label = { Text("Taille (cm)") },
                                    modifier = Modifier.weight(1f),
                                    singleLine = true,
                                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                                )
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            // Sélection du genre
                            Text(
                                text = "Genre",
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                listOf("Homme", "Femme").forEach { genreOption ->
                                    Button(
                                        onClick = { genre = genreOption },
                                        modifier = Modifier.weight(1f),
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (genre == genreOption) Accent else Color(0xFFF5F5F5),
                                            contentColor = if (genre == genreOption) Color.White else Color(0xFF666666)
                                        )
                                    ) {
                                        Text(genreOption)
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            // Niveau d'activité
                            Text(
                                text = "Niveau d'activité",
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                            LazyRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                items(listOf("Sédentaire", "Léger", "Modéré", "Actif", "Très actif")) { niveau ->
                                    Button(
                                        onClick = { niveauActivite = niveau },
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (niveauActivite == niveau) Accent else Color(0xFFF5F5F5),
                                            contentColor = if (niveauActivite == niveau) Color.White else Color(0xFF666666)
                                        )
                                    ) {
                                        Text(niveau, fontSize = 12.sp)
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(16.dp))

                            // Objectif
                            Text(
                                text = "Objectif",
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                            LazyRow(
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                items(listOf("Maintenir", "Perdre du poids", "Prise de masse", "Sèche")) { obj ->
                                    Button(
                                        onClick = { objectif = obj },
                                        colors = ButtonDefaults.buttonColors(
                                            containerColor = if (objectif == obj) Accent else Color(0xFFF5F5F5),
                                            contentColor = if (objectif == obj) Color.White else Color(0xFF666666)
                                        )
                                    ) {
                                        Text(obj, fontSize = 12.sp)
                                    }
                                }
                            }

                            Spacer(modifier = Modifier.height(16.dp))
                        } // fin des champs d'inscription

                        if (errorMessage.isNotEmpty()) {
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = errorMessage,
                                color = Color.Red,
                                fontSize = 14.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        // Bouton principal
                        Button(
                            onClick = { handleAuth() },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(48.dp),
                            enabled = !isLoading,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Accent
                            )
                        ) {
                            if (isLoading) {
                                CircularProgressIndicator(
                                    color = Color.White,
                                    modifier = Modifier.size(20.dp)
                                )
                            } else {
                                Text(
                                    text = if (isLoginMode) "Se connecter" else "S'inscrire",
                                    color = Color.White,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Bouton de basculement
                        TextButton(
                            onClick = {
                                isLoginMode = !isLoginMode
                                errorMessage = ""
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = if (isLoginMode) {
                                    "Pas de compte ? S'inscrire"
                                } else {
                                    "Déjà un compte ? Se connecter"
                                },
                                color = Accent
                            )
                        }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppMainInterface(
    selectedTabIndex: Int,
    onTabChange: (Int) -> Unit,
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    dataManager: DataManager,
    onProfileUpdate: (ProfileData) -> Unit,
    onStartWorkout: (List<Machine>, String) -> Unit,
    onShowStatistics: () -> Unit,
    onCsvImported: (List<WorkoutEntry>) -> Unit,
    onWorkoutHistoryChange: (List<WorkoutEntry>) -> Unit,
    onLogout: () -> Unit,
    selectedCalendarEntry: WorkoutEntry?,
    onCalendarEntrySelect: (WorkoutEntry?) -> Unit
) {
    val navItems = listOf(
        NavigationItem("Profil", Icons.Default.Person),
        NavigationItem("Machines", Icons.Default.FitnessCenter),
        NavigationItem("Entraînement", Icons.Default.PlayArrow),
        NavigationItem("Calendrier", Icons.Default.DateRange)
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(LightBackground)
    ) {
        // Header
        TopAppBar(
            title = {
                Text(
                    text = "Myc",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Mint
            )
        )

        // Content
        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
        ) {
            when (selectedTabIndex) {
                0 -> ProfileScreen(
                    profileData = profileData,
                    workoutHistory = workoutHistory,
                    onSaveProfile = onProfileUpdate,
                    onShowStatistics = onShowStatistics,
                    onLogout = onLogout
                )
                1 -> MachinesScreen(
                    profileData = profileData,
                    workoutHistory = workoutHistory
                )
                2 -> WorkoutScreen(
                    profileData = profileData,
                    workoutHistory = workoutHistory,
                    onStartWorkout = onStartWorkout
                )
                3 -> CalendarScreen(
                    workoutHistory = workoutHistory,
                    onWorkoutHistoryChange = onWorkoutHistoryChange,
                    onCsvImported = onCsvImported,
                                    onEntryClick = { entry ->
                    onCalendarEntrySelect(entry)
                },
                    onGoToWorkout = { onTabChange(2) }
                )
            }
        }

        // Bottom Navigation
        NavigationBar(
            containerColor = Mint,
            contentColor = Color.White,
            modifier = Modifier.navigationBarsPadding()
        ) {
            navItems.forEachIndexed { index, item ->
                NavigationBarItem(
                    icon = {
                        Icon(
                            imageVector = item.icon,
                            contentDescription = item.title,
                            tint = if (selectedTabIndex == index) Color.White else Color(0x80FFFFFF)
                        )
                    },
                    label = {
                        Text(
                            text = item.title,
                            color = if (selectedTabIndex == index) Color.White else Color(0x80FFFFFF),
                            fontSize = 12.sp
                        )
                    },
                    selected = selectedTabIndex == index,
                    onClick = { onTabChange(index) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = Color.White,
                        selectedTextColor = Color.White,
                        unselectedIconColor = Color(0x80FFFFFF),
                        unselectedTextColor = Color(0x80FFFFFF),
                        indicatorColor = Color.Transparent
                    )
                )
            }
        }
    }
}

@Composable
fun ProfileScreen(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    onSaveProfile: (ProfileData) -> Unit,
    onShowStatistics: () -> Unit,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    val dataManager = remember { DataManager(context) }

    var isEditing by remember { mutableStateOf(false) }
    var nom by remember { mutableStateOf(profileData.nom) }
    var email by remember { mutableStateOf(profileData.email) }
    var dateNaissance by remember { mutableStateOf(profileData.dateNaissance) }
    var poids by remember { mutableStateOf(profileData.poids.toString()) }
    var taille by remember { mutableStateOf(profileData.taille.toString()) }
    var genre by remember { mutableStateOf(profileData.genre) }
    var niveauActivite by remember { mutableStateOf(profileData.niveauActivite) }
    var objectif by remember { mutableStateOf(profileData.objectif) }

    // Calculer l'âge
    val age = calculateAge(dateNaissance)

    // Calculer les données en temps réel
    val weightNum = poids.toDoubleOrNull() ?: 70.0
    val heightNum = taille.toIntOrNull() ?: 170
    val bmi = calculateBMI(weightNum, heightNum)
    val bmiCategory = getBmiCategory(bmi)
    val caloriesPerDay = calculateDailyCalories(age, weightNum, heightNum, genre, niveauActivite)
    val goalCalories = calculateGoalBasedCalories(age, weightNum, heightNum, genre, niveauActivite, objectif)
    val nutritionalRecommendations = getNutritionalRecommendations(objectif, weightNum)
    val recommendations = getPersonalizedTips(profileData)
    val (totalSessions, totalMinutes, totalCalories) = dataManager.getTotalStats()

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            // Header avec bouton édition et statut de connexion
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Mon Profil",
                        fontSize = 28.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    IconButton(
                        onClick = {
                            if (isEditing) {
                                // Sauvegarder
                                val newProfile = ProfileData(
                                    nom = nom,
                                    email = email,
                                    dateNaissance = dateNaissance,
                                    poids = poids.toDoubleOrNull() ?: 70.0,
                                    taille = taille.toIntOrNull() ?: 170,
                                    genre = genre,
                                    niveauActivite = niveauActivite,
                                    objectif = objectif
                                )
                                onSaveProfile(newProfile)
                            }
                            isEditing = !isEditing
                        }
                    ) {
                        Icon(
                            imageVector = if (isEditing) Icons.Default.Check else Icons.Default.Edit,
                            contentDescription = if (isEditing) "Sauvegarder" else "Éditer",
                            tint = Accent
                        )
                    }
                }

                // (Bloc de test connexion supprimé)
            }
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Informations personnelles",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )

                    if (isEditing) {
                        // Mode édition
                        OutlinedTextField(
                            value = nom,
                            onValueChange = { nom = it },
                            label = { Text("Nom") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedTextField(
                            value = email,
                            onValueChange = { email = it },
                            label = { Text("Email") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        // Sélecteur date naissance – format JJ/MM/AAAA
                        val dateFormatterFr = remember { DateTimeFormatter.ofPattern("dd/MM/yyyy") }
                        val contextDate = LocalContext.current

                        OutlinedTextField(
                            value = if (dateNaissance.isBlank()) "" else try {
                                LocalDate.parse(dateNaissance).format(dateFormatterFr)
                            } catch (_: Exception) { dateNaissance },
                            onValueChange = {},
                            label = { Text("Date de naissance") },
                            modifier = Modifier.fillMaxWidth(),
                            readOnly = true,
                            singleLine = true,
                            placeholder = { Text("JJ/MM/AAAA") },
                            trailingIcon = {
                                IconButton(onClick = {
                                    val today = LocalDate.now()
                                    val init = try { LocalDate.parse(dateNaissance) } catch (_: Exception) { today.minusYears(25) }
                                    val datePickerDialog = android.app.DatePickerDialog(
                                        contextDate,
                                        { _, y, m, d ->
                                            val picked = LocalDate.of(y, m + 1, d)
                                            dateNaissance = picked.toString()
                                        },
                                        init.year,
                                        init.monthValue - 1,
                                        init.dayOfMonth
                                    )
                                    // Appliquer un fond blanc au DatePicker
                                    datePickerDialog.window?.setBackgroundDrawableResource(android.R.color.white)
                                    datePickerDialog.show()
                                }) {
                                    Icon(Icons.Default.DateRange, contentDescription = "Choisir la date")
                                }
                            }
                        )

                        Spacer(modifier = Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            OutlinedTextField(
                                value = poids,
                                onValueChange = { poids = it },
                                label = { Text("Poids (kg)") },
                                modifier = Modifier.weight(1f),
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )

                            OutlinedTextField(
                                value = taille,
                                onValueChange = { taille = it },
                                label = { Text("Taille (cm)") },
                                modifier = Modifier.weight(1f),
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        // Objectif – choix rapide
                        Text("Objectif", fontSize = 14.sp, color = Color.Gray)
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            items(listOf("Maintenir", "Perdre du poids", "Prise de masse", "Sèche")) { obj ->
                                Button(
                                    onClick = { objectif = obj },
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = if (objectif == obj) Accent else Color(0xFFF5F5F5),
                                        contentColor = if (objectif == obj) Color.White else Color(0xFF666666)
                                    )
                                ) { Text(obj, fontSize = 12.sp) }
                            }
                        }

                    } else {
                        // Mode affichage
                        InfoRow("Nom", nom)
                        InfoRow("Email", email)
                        InfoRow("Âge", "$age ans")
                        InfoRow("Poids", "${weightNum.toInt()} kg")
                        InfoRow("Taille", "${heightNum} cm")
                        InfoRow("Genre", genre)
                        InfoRow("Niveau d'activité", niveauActivite)
                        InfoRow("Objectif", objectif)
                        InfoRow("IMC", "${"%.1f".format(bmi)} ($bmiCategory)")
                    }
                }
            }
        }

        // Statistiques
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFF8F9FA))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Statistiques",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        StatCard("Séances", totalSessions.toString())
                        StatCard("Minutes", totalMinutes.toString())
                        StatCard("Calories", totalCalories.toString())
                    }
                }
            }
        }

        // Recommandations nutritionnelles
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFE3F2FD))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "🍽️ Recommandations nutritionnelles",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )

                    Text(
                        text = "Pour votre objectif : ${objectif}",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = Color(0xFF1976D2),
                        modifier = Modifier.padding(bottom = 8.dp)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        NutritionCard(
                            icon = "🔥",
                            label = "Calories/jour",
                            value = "$goalCalories kcal",
                            subtitle = "Objectif"
                        )
                        NutritionCard(
                            icon = "🥩",
                            label = "Protéines/jour",
                            value = nutritionalRecommendations["Protéines"] ?: "0g",
                            subtitle = "Minimum"
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        NutritionCard(
                            icon = "🍞",
                            label = "Glucides/jour",
                            value = nutritionalRecommendations["Glucides"] ?: "0g",
                            subtitle = "Énergie"
                        )
                        NutritionCard(
                            icon = "🥑",
                            label = "Lipides/jour",
                            value = nutritionalRecommendations["Lipides"] ?: "0g",
                            subtitle = "Essentiels"
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Conseil principal
                    Card(
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFBBDEFB)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Text(
                                text = "💡 Conseil nutrition",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1976D2)
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = nutritionalRecommendations["Conseil"] ?: "Maintenez une alimentation équilibrée",
                                fontSize = 12.sp,
                                color = Color(0xFF424242)
                            )
                        }
                    }
                }
            }
        }

        // Conseils personnalisés
        if (recommendations.isNotEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8))
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Conseils personnalisés",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent,
                            modifier = Modifier.padding(bottom = 12.dp)
                        )

                        recommendations.forEach { tip ->
                            Text(
                                text = "• $tip",
                                fontSize = 14.sp,
                                color = Color(0xFF2E2E2E),
                                modifier = Modifier.padding(vertical = 2.dp)
                            )
                        }
                    }
                }
            }
        }

        // Bouton statistiques
        item {
            Button(
                onClick = onShowStatistics,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50),
                    contentColor = Color.White
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Analytics,
                        contentDescription = "Statistiques",
                        tint = Color.White
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "📊 Voir les statistiques",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        // BOUTON DE TEST - Forcer mise à jour des progressions (temporaire)
        item {
            Spacer(modifier = Modifier.height(16.dp))
            
            Button(
                onClick = {
                    kotlinx.coroutines.GlobalScope.launch {
                        try {
                            val apiService = ApiService.getInstance()
                            apiService.initialize(context)
                            val response = apiService.getApi().forceProgressionUpdate()
                            
                            kotlinx.coroutines.MainScope().launch {
                                if (response.success) {
                                    android.widget.Toast.makeText(
                                        context,
                                        "✅ Progressions mises à jour ! Testez une recommandation.",
                                        android.widget.Toast.LENGTH_LONG
                                    ).show()
                                } else {
                                    android.widget.Toast.makeText(
                                        context,
                                        "❌ Erreur: ${response.message}",
                                        android.widget.Toast.LENGTH_LONG
                                    ).show()
                                }
                            }
                        } catch (e: Exception) {
                            kotlinx.coroutines.MainScope().launch {
                                android.widget.Toast.makeText(
                                    context,
                                    "❌ Erreur: ${e.message}",
                                    android.widget.Toast.LENGTH_LONG
                                ).show()
                            }
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50),
                    contentColor = Color.White
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("🔧 FORCER MAJ RECOMMANDATIONS (TEST)")
            }
        }
        
        /*
        // Bouton de déconnexion (désactivé pour l'instant ; code conservé à titre de référence)
        item {
            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onLogout,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFF5252),
                    contentColor = Color.White
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.ExitToApp,
                        contentDescription = "Déconnexion",
                        tint = Color.White
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Se déconnecter",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
        */
    }
}

@Composable
fun MachinesScreen(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>
) {
    val context = LocalContext.current
    // Utiliser une liste vide par défaut pour tester le chargement depuis l'API uniquement
    var machines by remember { mutableStateOf<List<Machine>>(emptyList()) }

    // Charger depuis l'API à la première composition
    LaunchedEffect(Unit) {
        try {
            val api = ApiService.getInstance().apply { initialize(context) }.getApi()
            val fetched = api.getMachines()
            if (fetched.isNotEmpty()) {
                // Mapper MachineDto vers Machine du côté app (en conservant les champs principaux)
                val remoteMachines = fetched.mapNotNull { dto ->
                    try {
                        // Debug: afficher les données reçues
                        android.util.Log.d("MachineDebug", "Machine: ${dto.nom}, Instructions: '${dto.instructions}'")

                        Machine(
                            id = dto.id,
                            nom = dto.nom,
                            description = dto.description ?: "",
                            instructions = dto.instructions ?: "",
                            categorie = CategorieMachine.values().find { it.name.equals(dto.categorie ?: "", true) }
                                ?: CategorieMachine.MUSCULATION,
                            groupeMusculairePrimaire = dto.groupe_musculaire_primaires?.firstOrNull()?.get("nom") ?: "",
                            incrementPoids = 2.5,
                            poidsMinimum = 0.0,
                            poidsMaximum = 200.0,
                            imageGif = dto.image_gif // Ajout du mapping du GIF
                        )
                    } catch (_: Exception) { null }
                }
                machines = remoteMachines
            }
        } catch (e: Exception) {
            // Garde la liste locale en cas d'erreur réseau
            android.util.Log.e("MachineDebug", "Erreur API: ${e.message}")
        }
    }

    var selectedCategory by remember { mutableStateOf<CategorieMachine?>(null) }
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header avec titre et bouton d'export
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Machines disponibles",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Accent
            )

            // Bouton d'export des machines
            Button(
                onClick = {
                    // Créer le contenu de l'export avec les machines chargées
                    val machinesToExport = if (machines.isNotEmpty()) machines else MachineData.machines
                    val exportContent = buildString {
                        appendLine("📋 LISTE COMPLÈTE DES MACHINES EN BASE DE DONNÉES")
                        appendLine("=".repeat(50))
                        appendLine()
                        appendLine("Total: ${machinesToExport.size} machines")
                        appendLine()

                        // Grouper par catégorie
                        val machinesByCategory = machinesToExport.groupBy { it.categorie }
                        machinesByCategory.forEach { (category, machinesInCategory) ->
                            appendLine("🏋️ ${category.displayName} (${machinesInCategory.size} machines)")
                            appendLine("-".repeat(30))
                            machinesInCategory.forEach { machine ->
                                appendLine("• ${machine.nom}")
                                if (machine.groupeMusculairePrimaire.isNotEmpty()) {
                                    appendLine("  Groupe: ${machine.groupeMusculairePrimaire}")
                                }
                                if (machine.description.isNotEmpty()) {
                                    appendLine("  Description: ${machine.description}")
                                }
                                appendLine()
                            }
                            appendLine()
                        }

                        // Liste simple par ordre alphabétique
                        appendLine("📝 LISTE ALPHABÉTIQUE SIMPLE")
                        appendLine("=".repeat(30))
                        machinesToExport.sortedBy { it.nom }.forEach { machine ->
                            appendLine("• ${machine.nom}")
                        }
                    }

                    // Copier dans le presse-papiers
                    val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
                    val clip = android.content.ClipData.newPlainText("Machines BasicFit", exportContent)
                    clipboard.setPrimaryClip(clip)

                    // Afficher un toast de confirmation
                    android.widget.Toast.makeText(context, "📋 Liste exportée dans le presse-papiers !", android.widget.Toast.LENGTH_LONG).show()
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4CAF50)
                ),
                shape = RoundedCornerShape(8.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Download,
                        contentDescription = "Exporter",
                        tint = Color.White,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "Exporter",
                        color = Color.White,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }

        // Barre de recherche
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Rechercher une machine...") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = "Rechercher",
                    tint = Accent
                )
            },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Icon(
                            imageVector = Icons.Default.Clear,
                            contentDescription = "Effacer",
                            tint = Color.Gray
                        )
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Accent,
                focusedLabelColor = Accent
            ),
            singleLine = true
        )

        // Filtres par catégorie
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            item {
                Button(
                    onClick = { selectedCategory = null },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (selectedCategory == null) Accent else Color.White,
                        contentColor = if (selectedCategory == null) Color.White else Color(0xFF666666)
                    ),
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier.height(36.dp)
                ) {
                    Text(
                        text = "Toutes",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
            items(CategorieMachine.values()) { category ->
                Button(
                    onClick = { selectedCategory = category },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (selectedCategory == category) Accent else Color.White,
                        contentColor = if (selectedCategory == category) Color.White else Color(0xFF666666)
                    ),
                    shape = RoundedCornerShape(20.dp),
                    modifier = Modifier.height(36.dp)
                ) {
                    Text(
                        text = "${category.icone} ${category.displayName}",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }

        // Liste des machines filtrées
        val machinesFiltrees = machines.filter { machine ->
            val matchesCategory = selectedCategory == null || machine.categorie == selectedCategory
            val matchesSearch = searchQuery.isEmpty() ||
                machine.nom.contains(searchQuery, ignoreCase = true) ||
                machine.nomAnglais.contains(searchQuery, ignoreCase = true) ||
                machine.groupeMusculairePrimaire.contains(searchQuery, ignoreCase = true) ||
                machine.description.contains(searchQuery, ignoreCase = true) ||
                machine.tags.any { it.contains(searchQuery, ignoreCase = true) }

            matchesCategory && matchesSearch
        }

        // Affichage du nombre de résultats
        if (searchQuery.isNotEmpty()) {
            Text(
                text = "${machinesFiltrees.size} machine(s) trouvée(s)",
                fontSize = 14.sp,
                color = Color.Gray,
                modifier = Modifier.padding(bottom = 8.dp)
            )
        }

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(machinesFiltrees) { machine ->
                MachineCard(machine = machine)
            }
        }

        // Message si aucun résultat
        if (machinesFiltrees.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "🔍",
                        fontSize = 48.sp,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    Text(
                        text = "Aucune machine trouvée",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Text(
                        text = if (searchQuery.isNotEmpty()) "Essayez un autre terme de recherche" else "Changez les filtres",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun MachineCard(machine: Machine) {
    var expanded by remember { mutableStateOf(false) }
    var recommendation by remember { mutableStateOf<ExerciseRecommendation?>(null) }
    var isLoadingRecommendation by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current

    // Charger la recommandation quand la carte est développée
    LaunchedEffect(expanded) {
        if (expanded && recommendation == null && !isLoadingRecommendation) {
            isLoadingRecommendation = true
            try {
                android.util.Log.d("MachineCard", "🔍 Chargement recommandation pour: ${machine.nom} (ID: ${machine.id})")
                
                // Vérifier si l'utilisateur est connecté
                val prefs = context.getSharedPreferences("BasicFitPrefs", Context.MODE_PRIVATE)
                val isLoggedIn = prefs.getBoolean("is_logged_in", false)
                val token = prefs.getString("auth_token", null)
                
                android.util.Log.d("MachineCard", "🔐 État connexion - Connecté: $isLoggedIn, Token: ${token?.take(10)}...")
                
                if (!isLoggedIn || token.isNullOrBlank()) {
                    android.util.Log.w("MachineCard", "⚠️ Utilisateur non connecté - Pas de recommandation")
                    errorMessage = "Non connecté"
                    return@LaunchedEffect
                }
                
                val rec = getRecommendationFromAPI(machine.id, context)
                
                if (rec != null) {
                    android.util.Log.d("MachineCard", "✅ Recommandation chargée: ${rec.weight}kg, ${rec.sets}x${rec.reps}")
                    recommendation = rec
                    errorMessage = null
                } else {
                    android.util.Log.w("MachineCard", "⚠️ getRecommendationFromAPI a retourné null")
                    errorMessage = "Aucune recommandation trouvée"
                }
            } catch (e: Exception) {
                android.util.Log.e("MachineCard", "❌ Erreur recommandation: ${e.message}")
                android.util.Log.e("MachineCard", "❌ Stack trace: ${e.stackTrace.contentToString()}")
                errorMessage = "Erreur: ${e.message?.take(50)}"
            } finally {
                isLoadingRecommendation = false
            }
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { expanded = !expanded },
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header de la carte
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "${machine.categorie.icone} ${machine.nom}",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2E2E2E)
                    )
                    Text(
                        text = machine.groupeMusculairePrimaire,
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                    Text(
                        text = machine.niveauDifficulte.displayName,
                        fontSize = 12.sp,
                        color = when (machine.niveauDifficulte) {
                            NiveauDifficulte.DEBUTANT -> Color(0xFF4CAF50)
                            NiveauDifficulte.INTERMEDIAIRE -> Color(0xFFFF9800)
                            NiveauDifficulte.AVANCE -> Accent
                            NiveauDifficulte.EXPERT -> Color(0xFFF44336)
                        },
                        fontWeight = FontWeight.Medium
                    )
                }

                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (expanded) "Réduire" else "Développer",
                    tint = Accent
                )
            }

            // Affichage du GIF si présent
            if (expanded && !machine.imageGif.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                AnimatedGifImage(
                    imageUrl = machine.imageGif,
                    contentDescription = "Démonstration GIF",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                )
            }

            // Contenu développable
            if (expanded) {
                Spacer(modifier = Modifier.height(12.dp))

                // Description
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = "Description",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = machine.description,
                            fontSize = 12.sp,
                            color = Color(0xFF666666)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Instructions
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = "Instructions d'utilisation",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        android.util.Log.d("MachineDebug", "Affichage instructions pour ${machine.nom}: '${machine.instructions}'")
                        Text(
                            text = machine.instructions,
                            fontSize = 12.sp,
                            color = Color(0xFF666666)
                        )

                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Recommandation
                Card(
                    colors = CardDefaults.cardColors(containerColor = Color(0xFFE3F2FD)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            text = "🎯 Recommandation",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        
                        if (isLoadingRecommendation) {
                            Text(
                                text = "Chargement de la recommandation...",
                                fontSize = 12.sp,
                                color = Color.Gray
                            )
                        } else if (recommendation != null) {
                            Text(
                                text = "Poids: ${recommendation!!.weight.toInt()}kg",
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                color = Color(0xFF1976D2)
                            )
                            Text(
                                text = "Séries: ${recommendation!!.sets} | Répétitions: ${recommendation!!.reps} | Repos: ${recommendation!!.restTime}s",
                                fontSize = 12.sp,
                                color = Color(0xFF666666)
                            )
                            Text(
                                text = "Tempo recommandé: ${recommendation!!.tempo}",
                                fontSize = 12.sp,
                                color = Color(0xFF2E7D32),
                                fontWeight = FontWeight.Medium
                            )
                            if (recommendation!!.notes.isNotBlank()) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = recommendation!!.notes,
                                    fontSize = 11.sp,
                                    color = Color(0xFF888888),
                                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                                )
                            }
                        } else {
                            Text(
                                text = errorMessage ?: "Recommandation non disponible",
                                fontSize = 12.sp,
                                color = Color.Red
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun WorkoutScreen(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    onStartWorkout: (List<Machine>, String) -> Unit
) {
    var selectedMode by remember { mutableStateOf<String?>(null) }
    var selectedMachines by remember { mutableStateOf<List<Machine>>(emptyList()) }
    var selectedPreset by remember { mutableStateOf<MachineData.WorkoutPreset?>(null) }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "🏋️ Planifier un entraînement",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Accent
            )
        }

        item {
            // Choix du type d'entraînement
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Type d'entraînement",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent,
                        modifier = Modifier.padding(bottom = 12.dp)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Button(
                            onClick = { selectedMode = "manuel" },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (selectedMode == "manuel") Mint else LightBackground,
                                contentColor = if (selectedMode == "manuel") Color.White else Color(0xFF666666)
                            )
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text("⚙️", fontSize = 20.sp)
                                Text("Sélection manuelle", fontSize = 12.sp, textAlign = TextAlign.Center)
                            }
                        }

                        Button(
                            onClick = { selectedMode = "preset" },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (selectedMode == "preset") Mint else LightBackground,
                                contentColor = if (selectedMode == "preset") Color.White else Color(0xFF666666)
                            )
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text("🎯", fontSize = 20.sp)
                                Text("Presets coach", fontSize = 12.sp, textAlign = TextAlign.Center)
                            }
                        }
                    }
                }
            }
        }

        // Contenu selon le mode sélectionné
        if (selectedMode == "preset") {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Programmes prêts",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent,
                            modifier = Modifier.padding(bottom = 12.dp)
                        )

                        LazyRow(
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            items(MachineData.workoutPresets) { preset ->
                                Card(
                                    modifier = Modifier
                                        .width(200.dp)
                                        .clickable { selectedPreset = preset },
                                    colors = CardDefaults.cardColors(
                                        containerColor = if (selectedPreset == preset) Accent else Color(0xFFF8F9FA)
                                    )
                                ) {
                                    Column(
                                        modifier = Modifier.padding(16.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        Text(
                                            text = preset.emoji,
                                            fontSize = 32.sp
                                        )
                                        Spacer(modifier = Modifier.height(8.dp))
                                        Text(
                                            text = preset.nom,
                                            fontSize = 16.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = if (selectedPreset == preset) Color.White else Color(0xFF2E2E2E)
                                        )
                                        Text(
                                            text = preset.focusMusculaire,
                                            fontSize = 12.sp,
                                            color = if (selectedPreset == preset) Color(0x80FFFFFF) else Color.Gray,
                                            textAlign = TextAlign.Center
                                        )
                                        Spacer(modifier = Modifier.height(8.dp))
                                        Text(
                                            text = "${preset.machines.size} exercices",
                                            fontSize = 12.sp,
                                            color = if (selectedPreset == preset) Color.White else Accent
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (selectedPreset != null) {
                item {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8))
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Text(
                                text = "Aperçu du programme",
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Accent,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )

                            selectedPreset!!.machines.forEach { machine ->
                                Text(
                                    text = "• ${machine.nom} (${machine.groupeMusculairePrimaire})",
                                    fontSize = 14.sp,
                                    color = Color(0xFF2E2E2E),
                                    modifier = Modifier.padding(vertical = 2.dp)
                                )
                            }
                        }
                    }
                }
            }
        }

        if (selectedMode == "manuel") {
            item {
                ManualWorkoutSelection(
                    selectedMachines = selectedMachines,
                    onMachinesUpdate = { selectedMachines = it }
                )
            }
        }

        // Bouton de démarrage
        if ((selectedMode == "preset" && selectedPreset != null) ||
            (selectedMode == "manuel" && selectedMachines.isNotEmpty())) {
            item {
                Button(
                    onClick = {
                        val machines = if (selectedMode == "preset") {
                            selectedPreset!!.machines
                        } else {
                            selectedMachines
                        }
                        val workoutName = if (selectedMode == "preset") {
                            "Preset: ${selectedPreset!!.nom}"
                        } else {
                            "Manuel (${selectedMachines.size} exercices)"
                        }
                        onStartWorkout(machines, workoutName)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Accent
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.PlayArrow,
                            contentDescription = "Démarrer",
                            tint = Color.White
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "🚀 DÉMARRER LA SÉANCE",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ManualWorkoutSelection(
    selectedMachines: List<Machine>,
    onMachinesUpdate: (List<Machine>) -> Unit
) {
    val context = LocalContext.current
    // Liste vide au démarrage – sera peuplée par la réponse réseau
    var machinesCatalog by remember { mutableStateOf<List<Machine>>(emptyList()) }
    var selectedCategory by remember { mutableStateOf<CategorieMachine?>(null) }
    var searchQuery by remember { mutableStateOf("") }

    // Chargement distant au premier affichage
    LaunchedEffect(Unit) {
        try {
            val api = ApiService.getInstance().apply { initialize(context) }.getApi()
            val fetched = api.getMachines()
            if (fetched.isNotEmpty()) {
                val remote = fetched.map { dto ->
                    Machine(
                        id = dto.id,
                        nom = dto.nom,
                        description = dto.description ?: "",
                        instructions = dto.instructions ?: "",
                        categorie = CategorieMachine.values().find { it.name.equals(dto.categorie ?: "", true) }
                            ?: CategorieMachine.MUSCULATION,
                        groupeMusculairePrimaire = dto.groupe_musculaire_primaires?.firstOrNull()?.get("nom") ?: "",
                        incrementPoids = 2.5,
                        poidsMinimum = 0.0,
                        poidsMaximum = 200.0,
                        imageGif = dto.image_gif
                    )
                }
                machinesCatalog = remote
            }
        } catch (_: Exception) { }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Sélection manuelle",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Mint,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            // Champ de recherche
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text("Rechercher une machine...") },
                leadingIcon = {
                    Icon(imageVector = Icons.Default.Search, contentDescription = null, tint = Mint)
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { searchQuery = "" }) {
                            Icon(imageVector = Icons.Default.Clear, contentDescription = "Effacer", tint = Color.Gray)
                        }
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Mint,
                    focusedLabelColor = Mint
                ),
                singleLine = true
            )

            // Filtres par catégorie
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.padding(bottom = 16.dp)
            ) {
                item {
                    Button(
                        onClick = { selectedCategory = null },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (selectedCategory == null) Mint else Color.White,
                            contentColor = if (selectedCategory == null) Color.White else Color(0xFF666666)
                        ),
                        shape = RoundedCornerShape(20.dp),
                        modifier = Modifier.height(36.dp)
                    ) {
                        Text("Toutes", fontSize = 12.sp)
                    }
                }
                items(CategorieMachine.values()) { category ->
                    Button(
                        onClick = { selectedCategory = category },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (selectedCategory == category) Mint else Color.White,
                            contentColor = if (selectedCategory == category) Color.White else Color(0xFF666666)
                        ),
                        shape = RoundedCornerShape(20.dp),
                        modifier = Modifier.height(36.dp)
                    ) {
                        Text("${category.icone} ${category.displayName}", fontSize = 12.sp)
                    }
                }
            }

            // Compteur de machines sélectionnées
            if (selectedMachines.isNotEmpty()) {
                Text(
                    text = "${selectedMachines.size} machine(s) sélectionnée(s)",
                    fontSize = 14.sp,
                    color = Accent,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }

            // Liste des machines
            val machinesFiltrees = machinesCatalog.filter { machine ->
                val matchesCat = selectedCategory == null || machine.categorie == selectedCategory
                val matchesSearch = searchQuery.isBlank() ||
                    machine.nom.contains(searchQuery, true) ||
                    machine.groupeMusculairePrimaire.contains(searchQuery, true)
                matchesCat && matchesSearch
            }

            LazyColumn(
                modifier = Modifier.height(300.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(machinesFiltrees) { machine ->
                    val isSelected = selectedMachines.contains(machine)

                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                if (isSelected) {
                                    onMachinesUpdate(selectedMachines - machine)
                                } else {
                                    onMachinesUpdate(selectedMachines + machine)
                                }
                            },
                        colors = CardDefaults.cardColors(
                            containerColor = if (isSelected) Mint else Color(0xFFF8F9FA)
                        )
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = machine.categorie.icone,
                                fontSize = 20.sp,
                                modifier = Modifier.padding(end = 12.dp)
                            )

                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = machine.nom,
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (isSelected) Color.White else Color(0xFF2E2E2E)
                                )
                                Text(
                                    text = machine.groupeMusculairePrimaire,
                                    fontSize = 12.sp,
                                    color = if (isSelected) Color(0x80FFFFFF) else Color.Gray
                                )
                            }

                            if (isSelected) {
                                Icon(
                                    imageVector = Icons.Default.CheckCircle,
                                    contentDescription = "Sélectionné",
                                    tint = Color.White
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun InfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            fontSize = 14.sp,
            color = Color.Gray
        )
        Text(
            text = value,
            fontSize = 14.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun StatCard(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Accent
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = Color.Gray
        )
    }
}

@Composable
fun NutritionCard(
    icon: String,
    label: String,
    value: String,
    subtitle: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.width(100.dp)
    ) {
        Text(
            text = icon,
            fontSize = 20.sp,
            modifier = Modifier.padding(bottom = 4.dp)
        )
        Text(
            text = value,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF1976D2),
            textAlign = TextAlign.Center
        )
        Text(
            text = label,
            fontSize = 11.sp,
            color = Color.Gray,
            textAlign = TextAlign.Center
        )
        Text(
            text = subtitle,
            fontSize = 10.sp,
            color = Color(0xFF666666),
            textAlign = TextAlign.Center
        )
    }
}

data class NavigationItem(
    val title: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)

@Composable
fun MycTheme(content: @Composable () -> Unit) {
    val colorScheme = lightColorScheme(
        primary = Mint,
        primaryContainer = SoftBlue,
        secondary = SoftBlue,
        secondaryContainer = SoftBlue,
        background = LightBackground,
        surface = Color.White,
        onPrimary = Color.White,
        onSecondary = Color.White,
        onBackground = TextPrimary,
        onSurface = TextPrimary
    )
    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WorkoutInProgressScreen(
    workoutName: String,
    machines: List<Machine>,
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    dataManager: DataManager,
    onFinishWorkout: (Int, List<ExerciseRecord>) -> Unit,
    onExitWorkout: () -> Unit
) {
    val context = LocalContext.current  // Ajout de cette ligne manquante

    // Sélection de l'objectif de la séance
    var selectedGoal by remember { mutableStateOf<String?>(null) }

    // État pour forcer la mise à jour des recommandations
    var forceRecommendationUpdate by remember { mutableStateOf(0) }

    // Construit la session en fonction de l'objectif choisi
    var currentWorkoutSession by remember(selectedGoal, workoutHistory, forceRecommendationUpdate) {
        mutableStateOf(
            // Forcer la création d'une nouvelle session quand l'objectif change
            if (selectedGoal != null) {
                WorkoutSession(
                workoutName = workoutName,
                exercises = machines.map { machine ->
                    val goalObjective = when (selectedGoal) {
                        "Puissance" -> "Puissance"
                        "Volume" -> "Volume"
                        "Endurance" -> "Endurance"
                        else -> profileData.objectif
                    }
                    android.util.Log.d("Recommendation", "Recalcul des recommandations pour ${machine.nom} avec objectif: $goalObjective")
                    
                    // Utiliser directement le calcul local pour l'instant (l'API sera utilisée en temps réel dans CurrentExerciseCard)
                    val recommendation = calculateWorkoutRecommendations(
                        machine = machine,
                        workoutHistory = workoutHistory.map { it.toWorkoutSession() },
                        profileData = profileData.copy(objectif = goalObjective)
                    )
                    ExerciseSession(
                        machine = machine,
                        targetSets = recommendation.sets,
                        targetReps = recommendation.reps,
                        recommendedWeight = recommendation.weight,
                        restTime = recommendation.restTime
                    )
                }
            )
            } else {
                // Essayer de restaurer une session sauvegardée
                dataManager.loadCurrentWorkoutSession() ?: WorkoutSession(
                    workoutName = workoutName,
                    exercises = emptyList()
                )
            }
        )
    }

    // Sauvegarder automatiquement l'état de la session
    LaunchedEffect(currentWorkoutSession) {
        dataManager.saveCurrentWorkoutSession(currentWorkoutSession)
        dataManager.saveWorkoutInProgress(true)
    }

    // Sauvegarder automatiquement l'état toutes les 30 secondes
    LaunchedEffect(Unit) {
        while (true) {
            delay(30000) // 30 secondes
            if (dataManager.isWorkoutInProgress()) {
                dataManager.saveCurrentWorkoutSession(currentWorkoutSession)
            }
        }
    }

    // Forcer la mise à jour des recommandations quand l'historique change
    LaunchedEffect(workoutHistory) {
        android.util.Log.d("Recommendation", "Historique mis à jour, forcement du recalcul des recommandations")
        forceRecommendationUpdate++
    }

    // Dialog pour choisir l'objectif avant de commencer réellement
    if (selectedGoal == null) {
        AlertDialog(
            onDismissRequest = {},
            confirmButton = {},
            title = { Text("Choisissez votre objectif") },
            text = {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    val goals = listOf("Puissance", "Volume", "Endurance")
                    goals.forEach { goal ->
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                                .clickable { selectedGoal = goal },
                            colors = CardDefaults.cardColors(containerColor = AccentLight)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(
                                    text = goal,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Accent
                                )

                                // Afficher un exemple de recommandation pour cet objectif
                                val exampleRecommendation = when (goal) {
                                    "Puissance" -> "💪 2-5 reps • Charges lourdes • Repos long (2-4 min)"
                                    "Volume" -> "📈 6-12 reps • Charges moyennes • Repos moyen (1-2 min)"
                                    "Endurance" -> "🏃 15-30 reps • Charges légères • Repos court (30-60 sec)"
                                    else -> ""
                                }

                                Text(
                                    text = exampleRecommendation,
                                    fontSize = 12.sp,
                                    color = Color.Gray,
                                    modifier = Modifier.padding(top = 4.dp)
                                )
                            }
                        }
                    }
                }
            }
        )
        return // Ne montre pas la suite tant que l'objectif n'est pas choisi
    }

    var showExitDialog by remember { mutableStateOf(false) }
    var isResting by remember { mutableStateOf(false) }
    var restTimeRemaining by remember { mutableStateOf(0) }

    // Gestion du timer de repos
    LaunchedEffect(isResting, restTimeRemaining) {
        if (isResting && restTimeRemaining > 0) {
            delay(1000)
            restTimeRemaining--
        } else if (isResting && restTimeRemaining == 0) {
            isResting = false
        }
    }

    if (isResting) {
        // Écran de repos
        RestScreen(
            timeRemaining = restTimeRemaining,
            onSkipRest = {
                isResting = false
                restTimeRemaining = 0
            },
            onFinishRest = {
                isResting = false
            }
        )
    } else if (showExitDialog) {
        // Dialog de confirmation pour quitter l'entraînement
        AlertDialog(
            onDismissRequest = { showExitDialog = false },
            title = { Text("Quitter l'entraînement ?") },
            text = {
                Text("Votre progression sera sauvegardée automatiquement. Vous pourrez reprendre votre entraînement plus tard.")
            },
            confirmButton = {
                Button(
                    onClick = {
                        // Sauvegarder l'état avant de quitter
                        dataManager.saveCurrentWorkoutSession(currentWorkoutSession)
                        showExitDialog = false
                        onExitWorkout()
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE57373))
                ) {
                    Text("Quitter", color = Color.White)
                }
            },
            dismissButton = {
                Button(
                    onClick = { showExitDialog = false },
                    colors = ButtonDefaults.buttonColors(containerColor = Accent)
                ) {
                    Text("Continuer", color = Color.White)
                }
            }
        )
    } else {
        // Écran d'entraînement principal
        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFFF5F5F5))
        ) {
            // Header
            TopAppBar(
                title = {
                    Text(
                        text = "Entraînement en cours",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                },
                navigationIcon = {
                    IconButton(onClick = {
                        // Sauvegarder l'état avant de quitter
                        dataManager.saveCurrentWorkoutSession(currentWorkoutSession)
                        showExitDialog = true
                    }) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Quitter",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Mint
                ),
                actions = {
                    if (!currentWorkoutSession.isCompleted && currentWorkoutSession.exercises.size > 1) {
                        IconButton(onClick = {
                            // Passer l'exercice : le mettre en fin de liste
                            val list = currentWorkoutSession.exercises.toMutableList()
                            val current = list.removeAt(currentWorkoutSession.currentExerciseIndex)
                            list.add(current)
                            currentWorkoutSession = currentWorkoutSession.copy(exercises = list)
                        }) {
                            Icon(imageVector = Icons.Default.SkipNext, contentDescription = "Passer", tint = Color.White)
                        }
                    }
                },
            )

            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    // Informations de la séance
                    WorkoutProgressCard(
                        workoutSession = currentWorkoutSession,
                        profileData = profileData
                    )
                }

                // Affiche l'exercice en cours uniquement si la séance n'est pas terminée
                if (!currentWorkoutSession.isCompleted && currentWorkoutSession.currentExerciseIndex < currentWorkoutSession.exercises.size) {
                    item {
                        // Exercice en cours
                        val currentExercise = currentWorkoutSession.exercises[currentWorkoutSession.currentExerciseIndex]
                        CurrentExerciseCard(
                            exerciseSession = currentExercise,
                            profileData = profileData,
                            onSetCompleted = { weight, reps ->
                                // Ajouter la série terminée
                                currentExercise.sets.add(
                                    SetRecord(weight = weight, reps = reps, completed = true)
                                )

                                // Vérifier si l'exercice est terminé
                                if (currentExercise.sets.size >= currentExercise.targetSets) {
                                    currentExercise.isCompleted = true

                                    // Passer à l'exercice suivant
                                    if (currentWorkoutSession.currentExerciseIndex < currentWorkoutSession.exercises.size - 1) {
                                        currentWorkoutSession = currentWorkoutSession.copy(
                                            currentExerciseIndex = currentWorkoutSession.currentExerciseIndex + 1
                                        )
                                    } else {
                                        // Séance terminée
                                        currentWorkoutSession = currentWorkoutSession.copy(
                                            isCompleted = true
                                        )
                                    }
                                } else {
                                    // Démarrer le repos entre les séries
                                    restTimeRemaining = currentExercise.restTime
                                    isResting = true
                                }
                            },
                            onRemove = {
                                // Supprimer l'exercice en cours
                                val updatedExercises = currentWorkoutSession.exercises.toMutableList()
                                updatedExercises.removeAt(currentWorkoutSession.currentExerciseIndex)

                                if (updatedExercises.isEmpty()) {
                                    // Si plus d'exercices, terminer la séance
                                    currentWorkoutSession = currentWorkoutSession.copy(
                                        exercises = emptyList(),
                                        isCompleted = true
                                    )
                                } else {
                                    // Ajuster l'index de l'exercice courant
                                    val newIndex = if (currentWorkoutSession.currentExerciseIndex >= updatedExercises.size) {
                                        updatedExercises.size - 1
                                    } else {
                                        currentWorkoutSession.currentExerciseIndex
                                    }

                                    currentWorkoutSession = currentWorkoutSession.copy(
                                        exercises = updatedExercises,
                                        currentExerciseIndex = newIndex
                                    )
                                }
                            }
                        )
                    }
                }

                // Exercices suivants
                items(currentWorkoutSession.exercises.drop(currentWorkoutSession.currentExerciseIndex + 1)) { exercise ->
                    UpcomingExerciseCard(
                        exerciseSession = exercise,
                        onRemove = {
                            // Supprimer l'exercice de la liste
                            val updatedExercises = currentWorkoutSession.exercises.toMutableList()
                            val exerciseIndex = updatedExercises.indexOf(exercise)
                            if (exerciseIndex != -1) {
                                updatedExercises.removeAt(exerciseIndex)
                                currentWorkoutSession = currentWorkoutSession.copy(exercises = updatedExercises)

                                // Ajuster l'index de l'exercice courant si nécessaire
                                if (currentWorkoutSession.currentExerciseIndex >= updatedExercises.size) {
                                    currentWorkoutSession = currentWorkoutSession.copy(
                                        currentExerciseIndex = updatedExercises.size - 1
                                    )
                                }
                            }
                        }
                    )
                }

                // Bouton terminer si séance finie
                if (currentWorkoutSession.isCompleted) {
                    item {
                        Button(
                            onClick = {
                                val duration = ((System.currentTimeMillis() - currentWorkoutSession.startTime) / 60000).toInt()
                                val exercisesCompleted = currentWorkoutSession.exercises.map { exercise ->
                                    val bestSet = exercise.sets.maxByOrNull { it.weight * it.reps } ?: exercise.sets.last()
                                    ExerciseRecord(
                                        name = exercise.machine.nom,
                                        sets = exercise.sets.size,
                                        reps = bestSet.reps,
                                        weight = bestSet.weight
                                    )
                                }

                                // Sauvegarder localement
                                onFinishWorkout(duration, exercisesCompleted)

                                // Nettoyer l'état d'entraînement sauvegardé
                                dataManager.clearCurrentWorkout()

                                // NOTE: La sauvegarde se fait automatiquement dans onFinishWorkout
                                // Pas besoin de sauvegarder ici pour éviter les doublons
                                android.util.Log.d("WorkoutSync", "ℹ️ Entraînement terminé - Sauvegarde automatique via onFinishWorkout")
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(56.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFF4CAF50)
                            ),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Check,
                                    contentDescription = "Terminer",
                                    tint = Color.White
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "🎉 TERMINER LA SÉANCE",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color.White
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    // Dialog de confirmation de sortie
    if (showExitDialog) {
        AlertDialog(
            onDismissRequest = { showExitDialog = false },
            title = { Text("Quitter l'entraînement ?") },
            text = { Text("Êtes-vous sûr de vouloir quitter votre entraînement en cours ? Votre progression sera perdue.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showExitDialog = false
                        onExitWorkout()
                    }
                ) {
                    Text("Quitter", color = Accent)
                }
            },
            dismissButton = {
                TextButton(
                    onClick = { showExitDialog = false }
                ) {
                    Text("Continuer")
                }
            }
        )
    }
}

@Composable
fun RestScreen(
    timeRemaining: Int,
    onSkipRest: () -> Unit,
    onFinishRest: () -> Unit
) {
    val progress = remember(timeRemaining) {
        if (timeRemaining > 0) (timeRemaining.toFloat() / 90f) else 0f
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF1E1E1E))
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "💤 Temps de repos",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color.White,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Timer circulaire
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.size(200.dp)
        ) {
            CircularProgressIndicator(
                progress = progress,
                modifier = Modifier.fillMaxSize(),
                color = Accent,
                strokeWidth = 8.dp
            )

            Text(
                text = "${timeRemaining}s",
                fontSize = 48.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        Text(
            text = "Préparez-vous pour la prochaine série",
            fontSize = 16.sp,
            color = Color.Gray,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(48.dp))

        Button(
            onClick = onSkipRest,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Accent
            )
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.SkipNext,
                    contentDescription = "Passer",
                    tint = Color.White
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "PASSER",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }
        }
    }
}

@Composable
fun WorkoutProgressCard(
    workoutSession: WorkoutSession,
    profileData: ProfileData
) {
    val completedExercises = workoutSession.exercises.count { it.isCompleted }
    val totalExercises = workoutSession.exercises.size
    val progress = if (totalExercises > 0) completedExercises.toFloat() / totalExercises.toFloat() else 0f

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = workoutSession.workoutName,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Text(
                        text = "Objectif: ${profileData.objectif}",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Text(
                    text = "$completedExercises/$totalExercises",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Accent
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = Accent,
                trackColor = Color(0xFFE0E0E0)
            )
        }
    }
}

@Composable
fun CurrentExerciseCard(
    exerciseSession: ExerciseSession,
    profileData: ProfileData,
    onSetCompleted: (Double, Int) -> Unit,
    onRemove: () -> Unit = {}
) {
    var weight by remember { mutableStateOf("") }
    var reps by remember { mutableStateOf("") }
    var duration by remember { mutableStateOf("") }
    
    // État pour la recommandation API
    var apiRecommendation by remember { mutableStateOf<ExerciseRecommendation?>(null) }
    var isLoadingRecommendation by remember { mutableStateOf(false) }
    val context = LocalContext.current

    // Charger la recommandation depuis l'API
    LaunchedEffect(exerciseSession.machine.id) {
        isLoadingRecommendation = true
        try {
            android.util.Log.d("CurrentExercise", "🔄 Chargement recommandation API pour: ${exerciseSession.machine.nom}")
            val rec = getRecommendationFromAPI(exerciseSession.machine.id, context)
            if (rec != null) {
                apiRecommendation = rec
                android.util.Log.d("CurrentExercise", "✅ Recommandation API chargée: ${rec.weight}kg")
            } else {
                android.util.Log.w("CurrentExercise", "⚠️ Pas de recommandation API disponible")
            }
        } catch (e: Exception) {
            android.util.Log.e("CurrentExercise", "❌ Erreur recommandation API: ${e.message}")
        } finally {
            isLoadingRecommendation = false
        }
    }

    // Préremplissage selon la progression des séries
    LaunchedEffect(exerciseSession.sets.size, apiRecommendation) {
        if (exerciseSession.sets.isNotEmpty()) {
            val last = exerciseSession.sets.last()
            weight = String.format(java.util.Locale.US, "%.1f", last.weight).trimEnd('0').trimEnd('.')
            reps = last.reps.toString()
        } else {
            // Utiliser l'API en priorité, sinon la valeur par défaut
            val recommendedWeight = apiRecommendation?.weight ?: exerciseSession.recommendedWeight
            weight = String.format(java.util.Locale.US, "%.1f", recommendedWeight).trimEnd('0').trimEnd('.')
            reps = (apiRecommendation?.reps ?: exerciseSession.targetReps).toString()
        }
    }

    // Utiliser la recommandation API si disponible, sinon les valeurs par défaut
    val recommendation = apiRecommendation ?: ExerciseRecommendation(
        sets = exerciseSession.targetSets,
        reps = exerciseSession.targetReps,
        weight = exerciseSession.recommendedWeight,
        restTime = exerciseSession.restTime,
        notes = "💪 Recommandation personnalisée • Technique contrôlée • Progression adaptée",
        tempo = exerciseSession.machine.tempo ?: "3-1-2"
    )

    // Vérifier si c'est une machine cardio ou un exercice basé sur le temps
    val isCardioMachine = exerciseSession.machine.categorie == CategorieMachine.CARDIO ||
        exerciseSession.machine.nom.contains("Plank", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Gainage", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Burpee", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Mountain Climber", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Jumping Jack", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Squat Jump", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Lunge", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Wall Sit", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Push-up", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Pompe", ignoreCase = true)

    // Afficher un message si pas de poids recommandé (utiliser API en priorité)
    val actualRecommendedWeight = apiRecommendation?.weight ?: exerciseSession.recommendedWeight
    val weightDisplay = when {
        actualRecommendedWeight > 0 -> {
            val source = if (apiRecommendation != null) "API" else "local"
            "${actualRecommendedWeight.toInt()} kg ${if (isLoadingRecommendation) "(chargement...)" else "($source)"}"
        }
        actualRecommendedWeight == 0.0 -> {
            // Calculer une suggestion de poids de départ
            val suggestedWeight = calculateStartingWeight(exerciseSession.machine, profileData)
            if (suggestedWeight > 0) "${suggestedWeight.toInt()}kg (suggestion)" else "Poids à déterminer"
        }
        else -> "Poids à déterminer"
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = AccentLight)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header exercice
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "${exerciseSession.machine.categorie.icone} ${exerciseSession.machine.nom}",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Text(
                        text = exerciseSession.machine.groupeMusculairePrimaire,
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                // Bouton de suppression pour l'exercice en cours
                IconButton(
                    onClick = onRemove,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Supprimer cet exercice",
                        tint = Color(0xFFE57373), // Rouge clair
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            // Ajout du compteur de série
            Text(
                text = "Série ${exerciseSession.sets.size + 1} / ${exerciseSession.targetSets}",
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                color = Color(0xFF4CAF50),
                modifier = Modifier.padding(vertical = 4.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Affichage du GIF de la machine (si présent)
            if (!exerciseSession.machine.imageGif.isNullOrBlank()) {
                AnimatedGifImage(
                    imageUrl = exerciseSession.machine.imageGif,
                    contentDescription = "Démonstration GIF",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
            }

            // Recommandations
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        text = "📋 Recommandations",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Spacer(modifier = Modifier.height(4.dp))

                    if (isCardioMachine) {
                        // Recommandations pour cardio
                        val cardioType = when {
                            exerciseSession.machine.nom.contains("Plank", ignoreCase = true) -> "Gainage"
                            exerciseSession.machine.nom.contains("Gainage", ignoreCase = true) -> "Gainage"
                            exerciseSession.machine.nom.contains("Burpee", ignoreCase = true) -> "Cardio intense"
                            exerciseSession.machine.nom.contains("Mountain Climber", ignoreCase = true) -> "Cardio intense"
                            exerciseSession.machine.nom.contains("Jumping Jack", ignoreCase = true) -> "Cardio"
                            exerciseSession.machine.nom.contains("Squat Jump", ignoreCase = true) -> "Cardio intense"
                            exerciseSession.machine.nom.contains("Lunge", ignoreCase = true) -> "Cardio"
                            exerciseSession.machine.nom.contains("Wall Sit", ignoreCase = true) -> "Gainage"
                            exerciseSession.machine.nom.contains("Push-up", ignoreCase = true) -> "Musculation"
                            exerciseSession.machine.nom.contains("Pompe", ignoreCase = true) -> "Musculation"
                            else -> "Cardio"
                        }

                        Text(
                            text = "⏱️ Durée: ${exerciseSession.targetReps} minutes • Type: $cardioType",
                            fontSize = 12.sp,
                            color = Color(0xFF666666)
                        )
                        Text(
                            text = when {
                                cardioType == "Gainage" -> "💡 Maintenez la position et respirez profondément"
                                cardioType == "Cardio intense" -> "💡 Rythme soutenu, récupération active"
                                else -> "💡 Maintenez un rythme régulier et respirez profondément"
                            },
                            fontSize = 11.sp,
                            color = Color(0xFF4CAF50),
                            fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                        )
                    } else {
                        // Recommandations pour musculation
                                                        Text(
                                    text = "🎯 OBJECTIF: ${profileData.objectif}",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Accent
                                )
                                Text(
                                    text = "📊 DÉTAILS: ${exerciseSession.targetReps} reps • ${exerciseSession.targetSets} sets • ${exerciseSession.restTime}s repos",
                                    fontSize = 10.sp,
                                    color = Color.Gray
                                )
                        Text(
                            text = "Poids: $weightDisplay • Reps: ${exerciseSession.targetReps} • Repos: ${exerciseSession.restTime}s",
                            fontSize = 12.sp,
                            color = Color(0xFF666666)
                        )

                        // Afficher une suggestion si pas d'historique (utiliser API en priorité)
                        if (actualRecommendedWeight == 0.0) {
                            val suggestedWeight = calculateStartingWeight(exerciseSession.machine, profileData)
                            if (suggestedWeight > 0) {
                                Text(
                                    text = "💡 Suggestion de départ: ${suggestedWeight.toInt()}kg",
                                    fontSize = 11.sp,
                                    color = Color(0xFF4CAF50),
                                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                                )
                            }
                        }
                    }

                                        Text(
                        text = "💪 Recommandation personnalisée • Technique contrôlée • Progression adaptée",
                        fontSize = 12.sp,
                        color = Color(0xFF666666)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            if (isCardioMachine) {
                // Interface pour cardio - champ de temps personnalisé
                var cardioDuration by remember { mutableStateOf(exerciseSession.targetReps.toString()) }

                Column {
                    Text(
                        text = "⏱️ Marquez votre temps d'exercice",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = Accent,
                        modifier = Modifier.padding(bottom = 8.dp)
                    )

                    OutlinedTextField(
                        value = cardioDuration,
                        onValueChange = { cardioDuration = it },
                        label = { Text("Durée (minutes)") },
                        placeholder = { Text("Ex: 15") },
                        modifier = Modifier.fillMaxWidth(),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Button(
                        onClick = {
                            val cardioTime = cardioDuration.toIntOrNull() ?: exerciseSession.targetReps
                            // Pour cardio, on envoie 0 poids et la durée en reps
                            onSetCompleted(0.0, cardioTime)
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(56.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF4CAF50)
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = "✅ TERMINER L'EXERCICE CARDIO",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            } else {
                // Interface pour musculation - champs poids et reps
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    val weightPattern = remember { Regex("^\\d{0,3}(\\.\\d?)?") }
                    OutlinedTextField(
                        value = weight,
                        onValueChange = { input ->
                            if (weightPattern.matches(input)) weight = input
                        },
                        label = { Text("Poids (kg)") },
                        placeholder = {
                            Text(
                                when {
                                    exerciseSession.recommendedWeight > 0 ->
                                        "Recommandé: ${exerciseSession.recommendedWeight.toInt()}kg"
                                    else -> {
                                        val suggested = calculateStartingWeight(exerciseSession.machine, profileData)
                                        if (suggested > 0) "Suggestion: ${suggested.toInt()}kg" else "À déterminer"
                                    }
                                }
                            )
                        },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        singleLine = true
                    )

                    OutlinedTextField(
                        value = reps,
                        onValueChange = { reps = it },
                        label = { Text("Reps") },
                        modifier = Modifier.weight(1f),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Bouton valider série
                Button(
                    onClick = {
                        val weightValue = weight.toDoubleOrNull() ?: 0.0
                        val repsValue = reps.toIntOrNull() ?: 0
                        if (weightValue > 0 && repsValue > 0) {
                            onSetCompleted(weightValue, repsValue)
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Accent
                    )
                ) {
                    Text(
                        text = "✅ VALIDER LA SÉRIE",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }
        }
    }
}

@Composable
fun UpcomingExerciseCard(
    exerciseSession: ExerciseSession,
    onRemove: () -> Unit = {}
) {
    val isCardioMachine = exerciseSession.machine.categorie == CategorieMachine.CARDIO ||
        exerciseSession.machine.nom.contains("Plank", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Gainage", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Burpee", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Mountain Climber", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Jumping Jack", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Squat Jump", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Lunge", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Wall Sit", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Push-up", ignoreCase = true) ||
        exerciseSession.machine.nom.contains("Pompe", ignoreCase = true)

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF8F9FA))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = exerciseSession.machine.categorie.icone,
                    fontSize = 24.sp,
                    modifier = Modifier.padding(end = 12.dp)
                )

                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = exerciseSession.machine.nom,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF666666)
                    )
                    Text(
                        text = if (isCardioMachine) {
                            "${exerciseSession.targetReps} minutes"
                        } else {
                            "${exerciseSession.targetSets} séries × ${exerciseSession.targetReps} reps"
                        },
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }

                // Bouton de suppression
                IconButton(
                    onClick = onRemove,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Supprimer cet exercice",
                        tint = Color(0xFFE57373), // Rouge clair
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            // Affichage du GIF de la machine (si présent)
            if (!exerciseSession.machine.imageGif.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                AnimatedGifImage(
                    imageUrl = exerciseSession.machine.imageGif,
                    contentDescription = "Démonstration GIF",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(150.dp)
                )
            }
        }
    }
}

// Fonction pour calculer les recommandations d'entraînement
fun calculateWorkoutRecommendations(
    machine: Machine,
    workoutHistory: List<WorkoutSession>,
    profileData: ProfileData
): ExerciseRecommendation {
    android.util.Log.d("Recommendation", "=== DÉBUT CALCUL RECOMMANDATION ===")
    android.util.Log.d("Recommendation", "Machine: ${machine.nom}")
    android.util.Log.d("Recommendation", "Objectif: ${profileData.objectif}")
    android.util.Log.d("Recommendation", "Historique total: ${workoutHistory.size} séances")

    // Diagnostic pour identifier les problèmes
    diagnoseRecommendationIssue(machine, workoutHistory, profileData)

    val age = calculateAge(profileData.dateNaissance)
    val objectif = profileData.objectif

    // 1) ANALYSE DE L'HISTORIQUE
    val exerciseRecords = workoutHistory.flatMap { it.exercises }
        .filter { it.machine.nom.equals(machine.nom, ignoreCase = true) }

    val historyCount = exerciseRecords.size
    val recentRecords = exerciseRecords.takeLast(5)

    android.util.Log.d("Recommendation", "Exercices trouvés pour ${machine.nom}: $historyCount")
    android.util.Log.d("Recommendation", "Séances récentes analysées: ${recentRecords.size}")

    // Extraire les poids réels des séries effectuées
    val actualWeights = recentRecords.flatMap { exerciseSession ->
        exerciseSession.sets.map { set -> set.weight }
    }.filter { it > 0 } // Filtrer les poids valides

    android.util.Log.d("Recommendation", "Poids réels extraits: ${actualWeights.size} valeurs")
    if (actualWeights.isNotEmpty()) {
        android.util.Log.d("Recommendation", "Poids trouvés: ${actualWeights.joinToString(", ")} kg")
    }

    // 2) DÉTERMINATION DU NIVEAU D'EXPÉRIENCE
    val experienceLevel = when {
        historyCount < 3 -> "Débutant"
        historyCount < 10 -> "Intermédiaire"
        historyCount < 25 -> "Avancé"
        else -> "Expert"
    }

    android.util.Log.d("Recommendation", "Niveau: $experienceLevel")

    // 3) CALCUL DES RÉPÉTITIONS SELON L'OBJECTIF
    val (targetReps, intensityPercentage) = when (objectif) {
        "Force", "Puissance" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(5, 75.0)
                "Intermédiaire" -> Pair(4, 80.0)
                "Avancé" -> Pair(3, 85.0)
                else -> Pair(2, 90.0)
            }
        }
        "Prise de masse", "Volume" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(12, 65.0)
                "Intermédiaire" -> Pair(10, 70.0)
                "Avancé" -> Pair(8, 75.0)
                else -> Pair(6, 80.0)
            }
        }
        "Endurance" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(15, 55.0)
                "Intermédiaire" -> Pair(20, 60.0)
                "Avancé" -> Pair(25, 65.0)
                else -> Pair(30, 70.0)
            }
        }
        "Sèche" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(12, 60.0)
                "Intermédiaire" -> Pair(15, 65.0)
                "Avancé" -> Pair(18, 70.0)
                else -> Pair(20, 75.0)
            }
        }
        else -> {
            // Objectif par défaut - Prise de masse
            when (experienceLevel) {
                "Débutant" -> Pair(12, 65.0)
                "Intermédiaire" -> Pair(10, 70.0)
                "Avancé" -> Pair(8, 75.0)
                else -> Pair(6, 80.0)
            }
        }
    }

    android.util.Log.d("Recommendation", "Reps cibles: $targetReps")
    android.util.Log.d("Recommendation", "Intensité: ${intensityPercentage}%")

    // 4) CALCUL DU POIDS RECOMMANDÉ
    val recommendedWeight = if (actualWeights.isNotEmpty()) {
        val avgWeight = actualWeights.average()
        val maxWeight = actualWeights.maxOrNull() ?: avgWeight
        android.util.Log.d("Recommendation", "Poids moyens: $avgWeight kg")
        android.util.Log.d("Recommendation", "Poids max: $maxWeight kg")

        // Calculer le 1RM estimé avec la formule de Brzycki
        val estimated1RM = maxWeight * (36 / (37 - targetReps.toDouble()))
        android.util.Log.d("Recommendation", "1RM estimé: $estimated1RM kg")

        // Recommander un poids basé sur l'intensité du 1RM
        val recommendedWeightFrom1RM = estimated1RM * (intensityPercentage / 100.0)
        android.util.Log.d("Recommendation", "Poids recommandé (1RM): $recommendedWeightFrom1RM kg")

        recommendedWeightFrom1RM
    } else {
        android.util.Log.d("Recommendation", "❌ PAS D'HISTORIQUE - Utilisation du poids de départ")
        val startingWeight = calculateStartingWeight(machine, profileData)
        android.util.Log.d("Recommendation", "Poids de départ calculé: $startingWeight kg")

        // Vérifier si c'est un poids par défaut problématique
        if (startingWeight == 20.0 || startingWeight == 15.0) {
            android.util.Log.w("Recommendation", "⚠️ ATTENTION: Poids par défaut détecté ($startingWeight kg)")
            android.util.Log.w("Recommendation", "   Machine: ${machine.nom}")
            android.util.Log.w("Recommendation", "   Genre: ${profileData.genre}")
            android.util.Log.w("Recommendation", "   Objectif: $objectif")
            android.util.Log.w("Recommendation", "   Âge: $age")
        }

        startingWeight
    }

    // 5) CALCUL DES SÉRIES ET REPOS
    val (sets, restTime) = when (objectif) {
        "Force", "Puissance" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(3, 180)
                "Intermédiaire" -> Pair(4, 180)
                "Avancé" -> Pair(5, 180)
                else -> Pair(6, 180)
            }
        }
        "Prise de masse", "Volume" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(3, 90)
                "Intermédiaire" -> Pair(4, 90)
                "Avancé" -> Pair(5, 90)
                else -> Pair(6, 90)
            }
        }
        "Endurance" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(3, 60)
                "Intermédiaire" -> Pair(4, 60)
                "Avancé" -> Pair(5, 60)
                else -> Pair(6, 60)
            }
        }
        "Sèche" -> {
            when (experienceLevel) {
                "Débutant" -> Pair(4, 75)
                "Intermédiaire" -> Pair(5, 75)
                "Avancé" -> Pair(6, 75)
                else -> Pair(7, 75)
            }
        }
        else -> {
            // Objectif par défaut
            when (experienceLevel) {
                "Débutant" -> Pair(3, 90)
                "Intermédiaire" -> Pair(4, 90)
                "Avancé" -> Pair(5, 90)
                else -> Pair(6, 90)
            }
        }
    }

    // 6) ADAPTATION POUR LES EXERCICES CARDIO
    val finalTargetReps = when {
        machine.categorie == CategorieMachine.CARDIO -> targetReps * 60 // Convertir en secondes
        machine.nom.contains("Tapis", ignoreCase = true) ||
        machine.nom.contains("Vélo", ignoreCase = true) ||
        machine.nom.contains("Rameur", ignoreCase = true) ||
        machine.nom.contains("Elliptique", ignoreCase = true) -> targetReps * 60 // Convertir en secondes
        else -> targetReps
    }

    // 7) NOTES DE RECOMMANDATION AMÉLIORÉES
    val notes = when (objectif) {
        "Force", "Puissance" -> "💪 Intensité: ${intensityPercentage.toInt()}% • Technique parfaite obligatoire • Repos complet"
        "Prise de masse", "Volume" -> "📈 Volume optimal: ${targetReps} reps • Tempo contrôlé • Tension musculaire maximale"
        "Endurance" -> "🏃 Rythme soutenu: ${targetReps} reps • Repos court • Respiration régulière"
        "Sèche" -> "🔥 Brûlage intensif • Repos court • Superset recommandé"
        else -> "💪 Recommandation personnalisée • Technique contrôlée • Progression adaptée"
    }

    val result = ExerciseRecommendation(
        sets = sets,
        reps = finalTargetReps,
        weight = recommendedWeight,
        restTime = restTime,
        notes = notes,
        tempo = machine.tempo ?: "3-1-2"
    )

    android.util.Log.d("Recommendation", "=== RÉSULTAT FINAL ===")
    android.util.Log.d("Recommendation", "Sets: ${result.sets}")
    android.util.Log.d("Recommendation", "Reps: ${result.reps}")
    android.util.Log.d("Recommendation", "Poids: ${result.weight} kg")
    android.util.Log.d("Recommendation", "Repos: ${result.restTime} sec")
    android.util.Log.d("Recommendation", "Notes: ${result.notes}")

    return result
}

// CALCUL DU POIDS DE DÉPART POUR DÉBUTANTS - AMÉLIORÉ
fun calculateStartingWeight(machine: Machine, profileData: ProfileData): Double {
    val age = calculateAge(profileData.dateNaissance)
    val isMale = profileData.genre.equals("Homme", ignoreCase = true)
    val objectif = profileData.objectif

    // Vérifier si c'est une machine cardio
    if (machine.categorie == CategorieMachine.CARDIO ||
        machine.nom.contains("Tapis", ignoreCase = true) ||
        machine.nom.contains("Vélo", ignoreCase = true) ||
        machine.nom.contains("Rameur", ignoreCase = true) ||
        machine.nom.contains("Plank", ignoreCase = true) ||
        machine.nom.contains("Gainage", ignoreCase = true) ||
        machine.nom.contains("Burpee", ignoreCase = true) ||
        machine.nom.contains("Mountain Climber", ignoreCase = true) ||
        machine.nom.contains("Jumping Jack", ignoreCase = true) ||
        machine.nom.contains("Squat Jump", ignoreCase = true) ||
        machine.nom.contains("Lunge", ignoreCase = true) ||
        machine.nom.contains("Wall Sit", ignoreCase = true) ||
        machine.nom.contains("Push-up", ignoreCase = true) ||
        machine.nom.contains("Pompe", ignoreCase = true)) {
        return 0.0 // Pas de poids pour cardio
    }

    // Poids de base selon le type d'exercice et le groupe musculaire
    val baseWeight = when {
        // Exercices de poitrine
        machine.nom.contains("Supine", ignoreCase = true) -> if (isMale) 60.0 else 45.0
        machine.nom.contains("Développé", ignoreCase = true) -> if (isMale) 30.0 else 20.0
        machine.nom.contains("Pec", ignoreCase = true) -> if (isMale) 25.0 else 15.0
        machine.nom.contains("Chest", ignoreCase = true) -> if (isMale) 25.0 else 15.0
        machine.nom.contains("Bench", ignoreCase = true) -> if (isMale) 30.0 else 20.0
        machine.nom.contains("Incline", ignoreCase = true) -> if (isMale) 25.0 else 15.0
        machine.nom.contains("Decline", ignoreCase = true) -> if (isMale) 20.0 else 12.0

        // Exercices de dos
        machine.nom.contains("Traction", ignoreCase = true) -> 0.0 // Poids du corps
        machine.nom.contains("Pull", ignoreCase = true) -> if (isMale) 20.0 else 15.0
        machine.nom.contains("Row", ignoreCase = true) -> if (isMale) 25.0 else 18.0
        machine.nom.contains("Lat", ignoreCase = true) -> if (isMale) 20.0 else 15.0
        machine.nom.contains("Back", ignoreCase = true) -> if (isMale) 25.0 else 18.0
        machine.nom.contains("Dos", ignoreCase = true) -> if (isMale) 25.0 else 18.0

        // Exercices de jambes
        machine.nom.contains("Squat", ignoreCase = true) -> if (isMale) 40.0 else 30.0
        machine.nom.contains("Presse", ignoreCase = true) -> if (isMale) 50.0 else 40.0
        machine.nom.contains("Leg", ignoreCase = true) -> if (isMale) 35.0 else 25.0
        machine.nom.contains("Extension", ignoreCase = true) -> if (isMale) 20.0 else 15.0
        machine.nom.contains("Flexion", ignoreCase = true) -> if (isMale) 25.0 else 20.0
        machine.nom.contains("Lunge", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Step", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Jambes", ignoreCase = true) -> if (isMale) 35.0 else 25.0

        // Exercices d'épaules
        machine.nom.contains("Shoulder", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Épaule", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Press", ignoreCase = true) -> if (isMale) 20.0 else 15.0
        machine.nom.contains("Lateral", ignoreCase = true) -> if (isMale) 8.0 else 5.0
        machine.nom.contains("Frontal", ignoreCase = true) -> if (isMale) 10.0 else 7.0

        // Exercices de bras
        machine.nom.contains("Curl", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Tricep", ignoreCase = true) -> if (isMale) 18.0 else 12.0
        machine.nom.contains("Bicep", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Bras", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Dips", ignoreCase = true) -> 0.0 // Poids du corps
        machine.nom.contains("Push-up", ignoreCase = true) -> 0.0 // Poids du corps

        // Exercices d'abdominaux
        machine.nom.contains("Abdo", ignoreCase = true) -> if (isMale) 10.0 else 8.0
        machine.nom.contains("Crunch", ignoreCase = true) -> if (isMale) 10.0 else 8.0
        machine.nom.contains("Core", ignoreCase = true) -> if (isMale) 12.0 else 10.0
        machine.nom.contains("Plank", ignoreCase = true) -> 0.0 // Poids du corps
        machine.nom.contains("Sit-up", ignoreCase = true) -> if (isMale) 5.0 else 3.0

        // Exercices de cardio (pas de poids)
        machine.nom.contains("Tapis", ignoreCase = true) -> 0.0
        machine.nom.contains("Vélo", ignoreCase = true) -> 0.0
        machine.nom.contains("Rameur", ignoreCase = true) -> 0.0
        machine.nom.contains("Elliptique", ignoreCase = true) -> 0.0
        machine.nom.contains("Stepper", ignoreCase = true) -> 0.0

        // Exercices de poids du corps
        machine.nom.contains("Burpee", ignoreCase = true) -> 0.0
        machine.nom.contains("Mountain", ignoreCase = true) -> 0.0
        machine.nom.contains("Jump", ignoreCase = true) -> 0.0
        machine.nom.contains("Wall", ignoreCase = true) -> 0.0

        // Machines spécifiques
        machine.nom.contains("Smith", ignoreCase = true) -> if (isMale) 25.0 else 18.0
        machine.nom.contains("Cable", ignoreCase = true) -> if (isMale) 15.0 else 10.0
        machine.nom.contains("Pulley", ignoreCase = true) -> if (isMale) 15.0 else 10.0

        // Autres exercices - utiliser une logique plus intelligente
        else -> {
            // Analyser le nom de la machine pour deviner le type d'exercice
            val machineName = machine.nom.lowercase()
            when {
                machineName.contains("press") -> if (isMale) 25.0 else 18.0
                machineName.contains("lift") -> if (isMale) 30.0 else 20.0
                machineName.contains("fly") -> if (isMale) 12.0 else 8.0
                machineName.contains("raise") -> if (isMale) 8.0 else 5.0
                machineName.contains("pull") -> if (isMale) 20.0 else 15.0
                machineName.contains("push") -> if (isMale) 20.0 else 15.0
                machineName.contains("dip") -> 0.0 // Poids du corps
                machineName.contains("up") -> 0.0 // Poids du corps
                else -> if (isMale) 18.0 else 12.0 // Poids par défaut réduit
            }
        }
    }

    // Ajustement selon l'âge
    val ageMultiplier = when {
        age < 25 -> 1.0
        age < 35 -> 0.95
        age < 50 -> 0.9
        else -> 0.85
    }

    // Ajustement selon l'objectif
    val objectiveMultiplier = when (objectif) {
        "Force", "Puissance" -> 0.8 // Commencer plus léger pour la force
        "Prise de masse", "Volume" -> 1.0 // Poids standard
        "Endurance" -> 0.7 // Plus léger pour l'endurance
        "Sèche" -> 0.9 // Légèrement plus léger
        else -> 1.0
    }

    val finalWeight = baseWeight * ageMultiplier * objectiveMultiplier

    // Arrondir à 2.5kg près pour faciliter l'utilisation
    val roundedWeight = (finalWeight / 2.5).roundToInt() * 2.5

    android.util.Log.d("Recommendation", "Poids de départ calculé: $roundedWeight kg (base: $baseWeight, âge: $age, genre: ${profileData.genre}, objectif: $objectif)")

    return roundedWeight
}

@Composable
fun AnimatedGifImage(
    imageUrl: String,
    contentDescription: String?,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current

    // Créer un ImageLoader avec support GIF
    val imageLoader = remember {
        ImageLoader.Builder(context)
            .components {
                add(GifDecoder.Factory())
            }
            .build()
    }

    // Container avec fond blanc
    Box(
        modifier = modifier
            .background(Color.White)
            .border(1.dp, Color.LightGray, RoundedCornerShape(8.dp))
    ) {
        AsyncImage(
            model = ImageRequest.Builder(context)
                .data(imageUrl)
                .build(),
            contentDescription = contentDescription,
            imageLoader = imageLoader,
            modifier = Modifier.fillMaxSize(),
            error = painterResource(id = R.drawable.ic_app_logo), // Placeholder en cas d'erreur
            contentScale = ContentScale.Fit
        )
    }
}

// Extension function pour convertir WorkoutEntry en WorkoutSession
fun WorkoutEntry.toWorkoutSession(): WorkoutSession {
    return WorkoutSession(
        workoutName = this.mode,
        exercises = this.exercises.map { exercise ->
            ExerciseSession(
                machine = MachineData.machines.find { it.nom == exercise.name } ?: MachineData.machines.first(),
                targetSets = exercise.sets,
                targetReps = exercise.reps,
                recommendedWeight = exercise.weight,
                restTime = 60
            )
        }
    )
}

// Fonction pour rafraîchir les recommandations après une séance
fun refreshRecommendations(context: Context) {
    android.util.Log.d("RecommendationRefresh", "🔄 Rafraîchissement des recommandations")
    // Cette fonction sera appelée après chaque séance pour forcer la mise à jour
    // des recommandations lors de la prochaine consultation
}

// Fonction pour récupérer la recommandation depuis l'API Django
suspend fun getRecommendationFromAPI(machineId: Int, context: Context): ExerciseRecommendation? {
    return try {
        android.util.Log.d("RecommendationAPI", "🔍 Début getRecommendationFromAPI pour machineId: $machineId")

        val apiService = ApiService.getInstance()
        apiService.initialize(context)

        // Vérifier si l'API est disponible
        val isApiAvailable = apiService.isApiAvailable()

        android.util.Log.d("RecommendationAPI", "🌐 État API - Disponible: $isApiAvailable")

        if (!isApiAvailable) {
            android.util.Log.w("RecommendationAPI", "⚠️ API non disponible - Utilisation du fallback local")
            return null
        }

        // Récupérer les machines depuis l'API
        val machines = apiService.getApi().getMachines()
        val machine = machines.find { it.id == machineId }
        if (machine == null) {
            android.util.Log.e("RecommendationAPI", "❌ Machine avec ID $machineId non trouvée dans l'API")
            return null
        }

        android.util.Log.d("RecommendationAPI", "✅ Machine trouvée depuis API: ${machine.nom}")
        android.util.Log.d("RecommendationAPI", "🌐 Tentative de connexion à l'API...")

        // Utiliser le nom de la machine depuis l'API
        val response = apiService.getApi().getRecommendationByName(machine.nom)

        android.util.Log.d("RecommendationAPI", "📡 Réponse API reçue")
        android.util.Log.d("RecommendationAPI", "   Success: ${response.success}")
        android.util.Log.d("RecommendationAPI", "   Data: ${response.data}")

        if (response.success && response.data != null) {
            val recommendation = response.data as RecommendationResponse

            android.util.Log.d("RecommendationAPI", "✅ Recommandation extraite:")
            android.util.Log.d("RecommendationAPI", "   Poids recommandé: ${recommendation.poids_recommande}kg")
            android.util.Log.d("RecommendationAPI", "   Séries: ${recommendation.series_recommandees}")
            android.util.Log.d("RecommendationAPI", "   Reps: ${recommendation.reps_recommandees}")
            android.util.Log.d("RecommendationAPI", "🎯 SUCCÈS API - Retour ExerciseRecommendation avec ${recommendation.poids_recommande}kg")

            // Construire des notes détaillées incluant le type d'exercice
            val notes = buildString {
                append("Recommandation basée sur votre progression")
                if (recommendation.notes.isNotEmpty()) {
                    append(" • ${recommendation.notes}")
                }
                append(" • Objectif: ${recommendation.objectif}")
                append(" • ${recommendation.series_recommandees} séries x ${recommendation.reps_recommandees} reps")
                append(" • Repos: ${recommendation.repos_recommande}s")
                append(" • Tempo: ${recommendation.tempo_recommande}")
            }

            val exerciseRecommendation = ExerciseRecommendation(
                sets = recommendation.series_recommandees,
                reps = recommendation.reps_recommandees,
                weight = recommendation.poids_recommande,
                restTime = recommendation.repos_recommande,
                notes = notes,
                tempo = recommendation.tempo_recommande
            )

            android.util.Log.d("RecommendationAPI", "🎯 Recommandation finale créée: ${exerciseRecommendation.weight}kg")
            exerciseRecommendation
        } else {
            android.util.Log.e("RecommendationAPI", "❌ Réponse API invalide ou échec")
            android.util.Log.e("RecommendationAPI", "   Success: ${response.success}")
            android.util.Log.e("RecommendationAPI", "   Data null: ${response.data == null}")
            if (response.message.isNotEmpty()) {
                android.util.Log.e("RecommendationAPI", "   Message: ${response.message}")
            }
            
            // Vérifier si c'est un problème d'authentification
            if (response.message.contains("authentifié", ignoreCase = true) || 
                response.message.contains("token", ignoreCase = true) ||
                response.message.contains("force_logout", ignoreCase = true)) {
                android.util.Log.w("RecommendationAPI", "🚪 Problème d'authentification détecté - Déconnexion nécessaire")
                // TODO: Déclencher la déconnexion ici
            }
            
            null
        }
    } catch (e: Exception) {
        android.util.Log.e("RecommendationAPI", "❌ Exception lors de la récupération: ${e.message}")
        android.util.Log.e("RecommendationAPI", "   Type d'erreur: ${e.javaClass.simpleName}")
        android.util.Log.e("RecommendationAPI", "   Stack trace: ${e.stackTraceToString()}")
        null
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CalendarEntryDetailScreen(
    entry: WorkoutEntry,
    workoutHistory: List<WorkoutEntry>,
    profileData: ProfileData,
    onBack: () -> Unit,
    onStartWorkout: (List<Machine>, String) -> Unit,
    onWorkoutHistoryChange: (List<WorkoutEntry>) -> Unit
) {
    val context = LocalContext.current
    var machinesList by remember { mutableStateOf<List<Machine>>(emptyList()) }

    // État local pour l'entrée actuelle (pour permettre les mises à jour immédiates)
    var currentEntry by remember { mutableStateOf(entry) }

    // Mettre à jour l'entrée locale quand l'entrée externe change
    LaunchedEffect(entry) {
        currentEntry = entry
    }

    // Forcer le rafraîchissement quand currentEntry change
    LaunchedEffect(currentEntry) {
        // Cette fonction vide force le rafraîchissement de l'interface
    }

    // Variables d'état pour le dialogue de remplacement
    var showExerciseReplacementDialog by remember { mutableStateOf(false) }
    var currentExerciseToReplace by remember { mutableStateOf<ExerciseRecord?>(null) }
    var alternativeExercises by remember { mutableStateOf<List<Machine>>(emptyList()) }

    // Fonction pour trouver les exercices alternatifs
    fun findAlternativeExercises(currentExercise: ExerciseRecord): List<Machine> {
        val currentMachine = machinesList.find { it.nom.equals(currentExercise.name, ignoreCase = true) }
        if (currentMachine == null) return emptyList()

        return machinesList.filter { alternative ->
            alternative.id != currentMachine.id && (
                alternative.groupeMusculairePrimaire == currentMachine.groupeMusculairePrimaire ||
                alternative.tags.any { tag -> currentMachine.tags.contains(tag) } ||
                alternative.categorie == currentMachine.categorie
            )
        }.take(10) // Limiter à 10 alternatives
    }

        // Fonction pour remplacer un exercice
    fun replaceExercise(oldExercise: ExerciseRecord, newMachine: Machine) {
        val newExercise = oldExercise.copy(name = newMachine.nom)
        val updatedExercises = currentEntry.exercises.map { if (it == oldExercise) newExercise else it }
        val updatedEntry = currentEntry.copy(exercises = updatedExercises)
        val updatedHistory = workoutHistory.map { if (it == entry) updatedEntry else it }

        // Mettre à jour l'état local immédiatement
        currentEntry = updatedEntry

        // Mettre à jour l'historique et forcer le rafraîchissement
        onWorkoutHistoryChange(updatedHistory)

        // Fermer le dialogue
        showExerciseReplacementDialog = false
        currentExerciseToReplace = null

        // Afficher une confirmation
        android.widget.Toast.makeText(context, "✅ ${oldExercise.name} remplacé par ${newMachine.nom}", android.widget.Toast.LENGTH_SHORT).show()
    }

    // Charger les machines depuis l'API
    LaunchedEffect(Unit) {
        try {
            val api = ApiService.getInstance().apply { initialize(context) }.getApi()
            val fetched = api.getMachines()
            if (fetched.isNotEmpty()) {
                val remoteMachines = fetched.mapNotNull { dto ->
                    try {
                        Machine(
                            id = dto.id,
                            nom = dto.nom,
                            description = dto.description ?: "",
                            instructions = dto.instructions ?: "",
                            categorie = CategorieMachine.values().find { it.name.equals(dto.categorie ?: "", true) }
                                ?: CategorieMachine.MUSCULATION,
                            groupeMusculairePrimaire = dto.groupe_musculaire_primaires?.firstOrNull()?.get("nom") ?: "",
                            incrementPoids = 2.5,
                            poidsMinimum = 0.0,
                            poidsMaximum = 200.0,
                            imageGif = dto.image_gif
                        )
                    } catch (_: Exception) { null }
                }
                machinesList = remoteMachines
            }
        } catch (e: Exception) {
            machinesList = MachineData.machines
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
    ) {
        // Header
        TopAppBar(
            title = {
                Text(
                    text = "Détails de la séance",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            },
            navigationIcon = {
                IconButton(onClick = onBack) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Retour",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Accent
            )
        )

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Informations générales
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "📅 ${currentEntry.date.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"))}",
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Mode: ${currentEntry.mode}",
                            fontSize = 14.sp,
                            color = Color(0xFF666666)
                        )

                        // Statut de l'entraînement
                        val today = LocalDate.now()
                        val isPastDate = currentEntry.date.isBefore(today)
                        val isCompleted = currentEntry.duration > 0

                        val statusText = when {
                            isCompleted -> "✅ Terminé"
                            isPastDate -> "⏰ En retard"
                            else -> "📅 Prévu pour aujourd'hui"
                        }

                        val statusColor = when {
                            isCompleted -> Color(0xFF4CAF50) // Vert
                            isPastDate -> Color(0xFFFF9800) // Orange
                            else -> Color(0xFF2196F3) // Bleu
                        }

                        Text(
                            text = statusText,
                            fontSize = 14.sp,
                            color = statusColor,
                            fontWeight = FontWeight.Bold
                        )

                        if (currentEntry.duration > 0) {
                            Text(
                                text = "Durée: ${currentEntry.duration} minutes",
                                fontSize = 14.sp,
                                color = Color(0xFF666666)
                            )
                        }
                        Text(
                            text = "Exercices: ${currentEntry.exercises.size}",
                            fontSize = 14.sp,
                            color = Color(0xFF666666)
                        )
                    }
                }
            }

            // Liste des exercices avec GIFs
            items(currentEntry.exercises) { exercise ->
                val machine = machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) } ?: Machine(
                    id = 0,
                    nom = exercise.name,
                    description = "",
                    instructions = "",
                    categorie = CategorieMachine.MUSCULATION,
                    groupeMusculairePrimaire = "",
                    incrementPoids = 2.5,
                    poidsMinimum = 0.0,
                    poidsMaximum = 200.0
                )

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = machine.nom,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Bold,
                                color = Accent,
                                modifier = Modifier.weight(1f)
                            )

                            // Icône de remplacement
                            IconButton(
                                onClick = {
                                    currentExerciseToReplace = exercise
                                    alternativeExercises = findAlternativeExercises(exercise)
                                    showExerciseReplacementDialog = true
                                }
                            ) {
                                Icon(
                                    imageVector = Icons.Default.SwapHoriz,
                                    contentDescription = "Remplacer cet exercice",
                                    tint = Accent,
                                    modifier = Modifier.size(24.dp)
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        // Affichage du GIF si présent
                        if (!machine.imageGif.isNullOrBlank()) {
                            AnimatedGifImage(
                                imageUrl = machine.imageGif,
                                contentDescription = "Démonstration GIF",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(150.dp)
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                        }

                        // Déterminer le type d'exercice basé sur la machine
                        val exerciseType = when {
                            machine.nom.contains("Tapis", ignoreCase = true) -> "Cardio"
                            machine.nom.contains("Vélo", ignoreCase = true) -> "Cardio"
                            machine.nom.contains("Rameur", ignoreCase = true) -> "Cardio"
                            machine.nom.contains("Elliptique", ignoreCase = true) -> "Cardio"
                            machine.categorie == CategorieMachine.MUSCULATION -> "Musculation"
                            machine.categorie == CategorieMachine.CARDIO -> "Cardio"
                            else -> "Autre"
                        }

                        Text(
                            text = "Type: $exerciseType • Poids: ${exercise.weight}kg",
                            fontSize = 14.sp,
                            color = Color(0xFF666666)
                        )

                        if (!machine.instructions.isNullOrBlank()) {
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Instructions: ${machine.instructions}",
                                fontSize = 12.sp,
                                color = Color(0xFF888888),
                                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                            )
                        }
                    }
                }
            }

            // Bouton selon le statut de l'entraînement
            item {
                val today = LocalDate.now()
                val isPastDate = currentEntry.date.isBefore(today)
                val isCompleted = currentEntry.duration > 0

                val buttonText = when {
                    isCompleted -> "🔄 Relancer cet entraînement"
                    isPastDate -> "🔄 Reprendre cet entraînement"
                    else -> "▶️ Commencer l'entraînement"
                }

                val buttonColor = when {
                    isCompleted -> Accent
                    isPastDate -> Color(0xFF9C27B0) // Violet pour les entraînements passés
                    else -> Color(0xFF4CAF50) // Vert pour commencer
                }

                Button(
                    onClick = {
                        val machines = currentEntry.exercises.map { exercise ->
                            machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) } ?: Machine(
                                id = 0,
                                nom = exercise.name,
                                description = "",
                                instructions = "",
                                categorie = CategorieMachine.MUSCULATION,
                                groupeMusculairePrimaire = "",
                                incrementPoids = 2.5,
                                poidsMinimum = 0.0,
                                poidsMaximum = 200.0
                            )
                        }
                        val workoutName = when {
                            isCompleted -> "Reprise ${currentEntry.date}"
                            isPastDate -> "Rattrapage ${currentEntry.date}"
                            else -> "Entraînement ${currentEntry.date}"
                        }
                        onStartWorkout(machines, workoutName)
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = buttonColor)
                ) {
                    Text(buttonText, color = Color.White)
                }
            }
        }
    }

    // Dialogue de remplacement d'exercice
    if (showExerciseReplacementDialog && currentExerciseToReplace != null) {
        AlertDialog(
            onDismissRequest = {
                showExerciseReplacementDialog = false
                currentExerciseToReplace = null
                alternativeExercises = emptyList() // Vider la liste des alternatives
            },
            title = {
                Text(
                    text = "Remplacer ${currentExerciseToReplace!!.name}",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            },
            text = {
                LazyColumn(
                    modifier = Modifier.height(300.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(alternativeExercises) { alternative ->
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = Color.White)
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        replaceExercise(currentExerciseToReplace!!, alternative)
                                    }
                                    .padding(16.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = alternative.nom,
                                        fontSize = 16.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = Accent
                                    )
                                    Text(
                                        text = "Groupe: ${alternative.groupeMusculairePrimaire}",
                                        fontSize = 12.sp,
                                        color = Color(0xFF666666)
                                    )
                                    Text(
                                        text = "Catégorie: ${alternative.categorie.displayName}",
                                        fontSize = 12.sp,
                                        color = Color(0xFF666666)
                                    )
                                }
                                Icon(
                                    imageVector = Icons.Default.ArrowForward,
                                    contentDescription = "Sélectionner",
                                    tint = Accent
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        showExerciseReplacementDialog = false
                        currentExerciseToReplace = null
                    }
                ) {
                    Text("Annuler")
                }
            }
        )
    }
}

// Fonction de diagnostic pour analyser les recommandations
fun diagnoseRecommendationIssue(
    machine: Machine,
    workoutHistory: List<WorkoutSession>,
    profileData: ProfileData
) {
    android.util.Log.d("Diagnostic", "=== DIAGNOSTIC RECOMMANDATION ===")
    android.util.Log.d("Diagnostic", "Machine: ${machine.nom}")
    android.util.Log.d("Diagnostic", "Genre: ${profileData.genre}")
    android.util.Log.d("Diagnostic", "Objectif: ${profileData.objectif}")
    android.util.Log.d("Diagnostic", "Âge: ${calculateAge(profileData.dateNaissance)}")
    android.util.Log.d("Diagnostic", "Historique total: ${workoutHistory.size} séances")

    // Analyser l'historique pour cette machine
    val exerciseRecords = workoutHistory.flatMap { it.exercises }
        .filter { it.machine.nom.equals(machine.nom, ignoreCase = true) }

    android.util.Log.d("Diagnostic", "Séances trouvées pour ${machine.nom}: ${exerciseRecords.size}")

    if (exerciseRecords.isEmpty()) {
        android.util.Log.w("Diagnostic", "❌ AUCUN HISTORIQUE TROUVÉ")
        android.util.Log.w("Diagnostic", "   Raison possible: Pas encore d'entraînement sur cette machine")
        android.util.Log.w("Diagnostic", "   Solution: Effectuer quelques séances pour créer un historique")
    } else {
        android.util.Log.d("Diagnostic", "✅ HISTORIQUE TROUVÉ")

        // Analyser les poids utilisés
        val allWeights = exerciseRecords.flatMap { exerciseSession ->
            exerciseSession.sets.map { set -> set.weight }
        }.filter { it > 0 }

        android.util.Log.d("Diagnostic", "Poids utilisés: ${allWeights.joinToString(", ")} kg")

        if (allWeights.isEmpty()) {
            android.util.Log.w("Diagnostic", "⚠️ AUCUN POIDS VALIDE TROUVÉ")
            android.util.Log.w("Diagnostic", "   Raison possible: Séances sans poids enregistré")
        } else {
            val maxWeight = allWeights.maxOrNull() ?: 0.0
            val avgWeight = allWeights.average()
            android.util.Log.d("Diagnostic", "Poids max: $maxWeight kg")
            android.util.Log.d("Diagnostic", "Poids moyen: $avgWeight kg")
        }
    }

    // Tester le calcul de poids de départ
    val startingWeight = calculateStartingWeight(machine, profileData)
    android.util.Log.d("Diagnostic", "Poids de départ calculé: $startingWeight kg")

    // Vérifier si c'est le poids par défaut problématique
    if (startingWeight == 20.0 || startingWeight == 15.0) {
        android.util.Log.w("Diagnostic", "⚠️ POIDS PAR DÉFAUT DÉTECTÉ")
        android.util.Log.w("Diagnostic", "   Machine: ${machine.nom}")
        android.util.Log.w("Diagnostic", "   Poids: $startingWeight kg")
        android.util.Log.w("Diagnostic", "   Raison: Aucun pattern spécifique trouvé pour cette machine")

        // Suggérer des améliorations
        android.util.Log.d("Diagnostic", "💡 SUGGESTIONS D'AMÉLIORATION:")
        android.util.Log.d("Diagnostic", "   1. Ajouter des patterns spécifiques pour ${machine.nom}")
        android.util.Log.d("Diagnostic", "   2. Effectuer quelques séances pour créer un historique")
        android.util.Log.d("Diagnostic", "   3. Vérifier la synchronisation avec la BDD")
    }

    android.util.Log.d("Diagnostic", "=== FIN DIAGNOSTIC ===")
}
