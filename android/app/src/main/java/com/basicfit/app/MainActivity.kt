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
import com.google.gson.reflect.TypeToken
import java.time.LocalDate
import java.time.Period
import java.time.format.DateTimeFormatter
import kotlinx.coroutines.delay
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.MainScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import kotlinx.coroutines.MainScope

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
    private val gson = Gson()

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
        val totalSessions = workoutHistory.size
        val totalMinutes = workoutHistory.sumOf { it.duration }
        val totalCalories = workoutHistory.sumOf { calculateBurnedCalories(loadProfileData().poids, it.duration, "Modéré") }
        return Triple(totalSessions, totalMinutes, totalCalories)
    }

    fun isUserLoggedIn(): Boolean {
        return prefs.getBoolean("is_logged_in", false)
    }

    fun setUserLoggedIn(isLoggedIn: Boolean) {
        prefs.edit().putBoolean("is_logged_in", isLoggedIn).apply()
    }

    fun clearUserData() {
        prefs.edit().clear().apply()
    }
}

// Fonctions utilitaires
fun calculateAge(dateNaissance: String): Int {
    return try {
        val birthDate = LocalDate.parse(dateNaissance, DateTimeFormatter.ofPattern("yyyy-MM-dd"))
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
    var workoutInProgress by remember { mutableStateOf(false) }
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

    if (!isLoggedIn) {
        // Écran de connexion/inscription
        AuthScreen(
            onLoginSuccess = { userProfile ->
                profileData = userProfile
                dataManager.saveProfileData(userProfile)
                dataManager.setUserLoggedIn(true)
                isLoggedIn = true

                // Synchroniser les données depuis le serveur
                val syncManager = SyncManager(context)
                kotlinx.coroutines.GlobalScope.launch {
                    try {
                        // Récupérer l'historique depuis le serveur
                        val serverHistory = syncManager.syncWorkoutHistory()
                        kotlinx.coroutines.MainScope().launch {
                            serverHistory.onSuccess { history ->
                                // Fusionner avec l'historique local si nécessaire
                                // Pour l'instant, on priorise les données serveur
                                // workoutHistory = convertServerHistoryToLocal(history)
                                // dataManager.saveWorkoutHistory(workoutHistory)
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
    } else if (workoutInProgress) {
        // Écran d'entraînement en cours
        WorkoutInProgressScreen(
            workoutName = currentWorkoutName,
            machines = currentWorkoutMachines,
            profileData = profileData,
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

                // Créer le récapitulatif
                val age = calculateAge(profileData.dateNaissance)
                val totalCalories = calculateWorkoutCaloriesImproved(exercisesCompleted, age, profileData.poids, profileData.genre)
                val personalRecords = findPersonalRecords(exercisesCompleted, workoutHistory)

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

                // Passer à l'écran de récapitulatif
                workoutInProgress = false
                currentWorkoutMachines = emptyList()
                currentWorkoutName = ""
                showWorkoutSummary = true
            },
            onExitWorkout = {
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
            onLogout = {
                dataManager.setUserLoggedIn(false)
                dataManager.clearUserData()
                isLoggedIn = false
                profileData = ProfileData("", "", "", 70.0, 170, "Homme", "Modéré", "Maintenir")
                workoutHistory = emptyList()
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
                                    errorMessage = response.message
                                }
                            }.onFailure { exception ->
                                errorMessage = "Erreur de connexion: ${exception.message}"
                            }
                            isLoading = false
                        }
                    } catch (e: Exception) {
                        MainScope().launch {
                            errorMessage = "Erreur de connexion: ${e.message}"
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
        Text(
            text = "💪",
            fontSize = 64.sp,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        Text(
            text = "Myc",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFE57373),
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
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
                        )

                        // Champs supplémentaires pour l'inscription
                        if (!isLoginMode) {
                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedTextField(
                                value = confirmPassword,
                                onValueChange = { confirmPassword = it },
                                label = { Text("Confirmer le mot de passe") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password)
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedTextField(
                                value = nom,
                                onValueChange = { nom = it },
                                label = { Text("Nom complet") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedTextField(
                                value = dateNaissance,
                                onValueChange = { dateNaissance = it },
                                label = { Text("Date de naissance (YYYY-MM-DD)") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                placeholder = { Text("1990-01-01") }
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
                                            containerColor = if (genre == genreOption) Color(0xFFE57373) else Color(0xFFF5F5F5),
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
                                            containerColor = if (niveauActivite == niveau) Color(0xFFE57373) else Color(0xFFF5F5F5),
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
                                            containerColor = if (objectif == obj) Color(0xFFE57373) else Color(0xFFF5F5F5),
                                            contentColor = if (objectif == obj) Color.White else Color(0xFF666666)
                                        )
                                    ) {
                                        Text(obj, fontSize = 12.sp)
                                    }
                                }
                            }
                        }

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
                                containerColor = Color(0xFFE57373)
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
                                color = Color(0xFFE57373)
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
    onLogout: () -> Unit
) {
    val navItems = listOf(
        NavigationItem("Profil", Icons.Default.Person),
        NavigationItem("Machines", Icons.Default.FitnessCenter),
        NavigationItem("Entraînement", Icons.Default.PlayArrow)
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
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
                containerColor = Color(0xFFE57373)
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
            }
        }

        // Bottom Navigation
        NavigationBar(
            containerColor = Color(0xFFE57373),
            contentColor = Color.White
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
                        indicatorColor = Color(0x30FFFFFF)
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
                        color = Color(0xFFE57373)
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
                            tint = Color(0xFFE57373)
                        )
                    }
                }

                // Indicateur de statut de connexion
                var connectionStatus by remember { mutableStateOf("Vérification...") }
                var isOnline by remember { mutableStateOf(false) }

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

                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (isOnline) Color(0xFFE8F5E8) else Color(0xFFFFEBEE)
                    )
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = connectionStatus,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = if (isOnline) Color(0xFF4CAF50) else Color(0xFFE57373)
                        )
                        Spacer(modifier = Modifier.weight(1f))
                        Button(
                            onClick = {
                                // Tester la connexion manuellement
                                GlobalScope.launch {
                                    try {
                                        val apiService = ApiService.getInstance()
                                        val serverReachable = apiService.isServerReachable()
                                        MainScope().launch {
                                            isOnline = serverReachable
                                            connectionStatus = if (serverReachable) "🟢 Connecté au serveur" else "🔴 Mode hors ligne"
                                        }
                                    } catch (e: Exception) {
                                        MainScope().launch {
                                            isOnline = false
                                            connectionStatus = "🔴 Mode hors ligne"
                                        }
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFE57373)
                            ),
                            modifier = Modifier.height(32.dp)
                        ) {
                            Text(
                                text = "🔄 Tester",
                                fontSize = 12.sp,
                                color = Color.White
                            )
                        }
                    }
                }
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
                        color = Color(0xFFE57373),
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
                        // Ajout autres champs...
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
                        color = Color(0xFFE57373),
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
                        color = Color(0xFFE57373),
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
                            color = Color(0xFFE57373),
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

        // Bouton de déconnexion
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
    }
}

@Composable
fun MachinesScreen(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>
) {
    var selectedCategory by remember { mutableStateOf<CategorieMachine?>(null) }
    var searchQuery by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Machines disponibles",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFE57373),
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Barre de recherche
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Rechercher une machine...") },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = "Rechercher",
                    tint = Color(0xFFE57373)
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
                focusedBorderColor = Color(0xFFE57373),
                focusedLabelColor = Color(0xFFE57373)
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
                        containerColor = if (selectedCategory == null) Color(0xFFE57373) else Color.White,
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
                        containerColor = if (selectedCategory == category) Color(0xFFE57373) else Color.White,
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
        val machinesFiltrees = MachineData.machines.filter { machine ->
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
                        color = Color(0xFFE57373)
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
                            NiveauDifficulte.AVANCE -> Color(0xFFE57373)
                            NiveauDifficulte.EXPERT -> Color(0xFFF44336)
                        },
                        fontWeight = FontWeight.Medium
                    )
                }

                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = if (expanded) "Réduire" else "Développer",
                    tint = Color(0xFFE57373)
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
                            color = Color(0xFFE57373)
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
                            color = Color(0xFFE57373)
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = machine.instructions,
                            fontSize = 12.sp,
                            color = Color(0xFF666666)
                        )
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
                color = Color(0xFFE57373)
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
                        color = Color(0xFFE57373),
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
                                containerColor = if (selectedMode == "manuel") Color(0xFFE57373) else Color(0xFFF5F5F5),
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
                                containerColor = if (selectedMode == "preset") Color(0xFFE57373) else Color(0xFFF5F5F5),
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
                            color = Color(0xFFE57373),
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
                                        containerColor = if (selectedPreset == preset) Color(0xFFE57373) else Color(0xFFF8F9FA)
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
                                            color = if (selectedPreset == preset) Color.White else Color(0xFFE57373)
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
                                color = Color(0xFFE57373),
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
                        containerColor = Color(0xFFE57373)
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
    var selectedCategory by remember { mutableStateOf<CategorieMachine?>(null) }

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
                color = Color(0xFFE57373),
                modifier = Modifier.padding(bottom = 12.dp)
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
                            containerColor = if (selectedCategory == null) Color(0xFFE57373) else Color.White,
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
                            containerColor = if (selectedCategory == category) Color(0xFFE57373) else Color.White,
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
                    color = Color(0xFFE57373),
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }

            // Liste des machines
            val machinesFiltrees = MachineData.machines.filter { machine ->
                selectedCategory == null || machine.categorie == selectedCategory
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
                            containerColor = if (isSelected) Color(0xFFE57373) else Color(0xFFF8F9FA)
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
            color = Color(0xFFE57373)
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
    MaterialTheme(
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WorkoutInProgressScreen(
    workoutName: String,
    machines: List<Machine>,
    profileData: ProfileData,
    onFinishWorkout: (Int, List<ExerciseRecord>) -> Unit,
    onExitWorkout: () -> Unit
) {
    val context = LocalContext.current  // Ajout de cette ligne manquante

    var currentWorkoutSession by remember {
        mutableStateOf(
            WorkoutSession(
                workoutName = workoutName,
                exercises = machines.map { machine ->
                    val recommendation = calculateWorkoutRecommendations(profileData, emptyList(), machine)
                    ExerciseSession(
                        machine = machine,
                        targetSets = recommendation.sets,
                        targetReps = recommendation.reps,
                        recommendedWeight = recommendation.weight,
                        restTime = recommendation.restTime
                    )
                }
            )
        )
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
                    IconButton(onClick = { showExitDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Quitter",
                            tint = Color.White
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color(0xFFE57373)
                )
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

                if (currentWorkoutSession.currentExerciseIndex < currentWorkoutSession.exercises.size) {
                    item {
                        // Exercice en cours
                        val currentExercise = currentWorkoutSession.exercises[currentWorkoutSession.currentExerciseIndex]
                        CurrentExerciseCard(
                            exerciseSession = currentExercise,
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
                            }
                        )
                    }
                }

                // Exercices suivants
                items(currentWorkoutSession.exercises.drop(currentWorkoutSession.currentExerciseIndex + 1)) { exercise ->
                    UpcomingExerciseCard(exerciseSession = exercise)
                }

                // Bouton terminer si séance finie
                if (currentWorkoutSession.isCompleted) {
                    item {
                        Button(
                            onClick = {
                                val duration = ((System.currentTimeMillis() - currentWorkoutSession.startTime) / 60000).toInt()
                                val exercisesCompleted = currentWorkoutSession.exercises.map { exercise ->
                                    ExerciseRecord(
                                        name = exercise.machine.nom,
                                        sets = exercise.sets.size,
                                        reps = exercise.sets.map { it.reps }.average().toInt(),
                                        weight = exercise.sets.map { it.weight }.average()
                                    )
                                }

                                // Sauvegarder localement
                                onFinishWorkout(duration, exercisesCompleted)

                                // Sauvegarder sur le serveur
                                val syncManager = SyncManager(context)
                                kotlinx.coroutines.GlobalScope.launch {
                                    try {
                                        syncManager.saveWorkoutToServer(
                                            nom = currentWorkoutSession.workoutName,
                                            dateDebut = java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")),
                                            dureeMinutes = duration,
                                            exercises = exercisesCompleted
                                        )
                                    } catch (e: Exception) {
                                        // Gérer l'erreur de synchronisation silencieusement
                                        // Les données sont déjà sauvegardées localement
                                    }
                                }
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
                    Text("Quitter", color = Color(0xFFE57373))
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
                color = Color(0xFFE57373),
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
                containerColor = Color(0xFFE57373)
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
                        color = Color(0xFFE57373)
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
                    color = Color(0xFFE57373)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = Color(0xFFE57373),
                trackColor = Color(0xFFE0E0E0)
            )
        }
    }
}

@Composable
fun CurrentExerciseCard(
    exerciseSession: ExerciseSession,
    onSetCompleted: (Double, Int) -> Unit
) {
    var weight by remember { mutableStateOf(exerciseSession.recommendedWeight.toString()) }
    var reps by remember { mutableStateOf(exerciseSession.targetReps.toString()) }

    val recommendation = remember(exerciseSession) {
        ExerciseRecommendation(
            sets = exerciseSession.targetSets,
            reps = exerciseSession.targetReps,
            weight = exerciseSession.recommendedWeight,
            restTime = exerciseSession.restTime,
            notes = generateExerciseNotes("Prise de masse", 25, exerciseSession.machine)
        )
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE))
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
                        color = Color(0xFFE57373)
                    )
                    Text(
                        text = exerciseSession.machine.groupeMusculairePrimaire,
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Text(
                    text = "Série ${exerciseSession.sets.size + 1}/${exerciseSession.targetSets}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFE57373)
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

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
                        color = Color(0xFFE57373)
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Poids: ${recommendation.weight.toInt()}kg • Reps: ${recommendation.reps} • Repos: ${recommendation.restTime}s",
                        fontSize = 12.sp,
                        color = Color(0xFF666666)
                    )
                    if (recommendation.notes.isNotEmpty()) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = recommendation.notes,
                            fontSize = 11.sp,
                            color = Color(0xFF666666)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Historique des séries terminées
            if (exerciseSession.sets.isNotEmpty()) {
                Text(
                    text = "Séries terminées:",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF666666)
                )
                Spacer(modifier = Modifier.height(8.dp))

                exerciseSession.sets.forEachIndexed { index, set ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Série ${index + 1}:",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                        Text(
                            text = "${set.weight.toInt()}kg × ${set.reps} reps",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF4CAF50)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))
            }

            // Saisie de la série actuelle
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = weight,
                    onValueChange = { weight = it },
                    label = { Text("Poids (kg)") },
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
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
                    containerColor = Color(0xFFE57373)
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

@Composable
fun UpcomingExerciseCard(
    exerciseSession: ExerciseSession
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF8F9FA))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
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
                    text = "${exerciseSession.targetSets} séries × ${exerciseSession.targetReps} reps",
                    fontSize = 12.sp,
                    color = Color.Gray
                )
            }

            Icon(
                imageVector = Icons.Default.AccessTime,
                contentDescription = "À venir",
                tint = Color.Gray,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

// Fonction pour calculer les recommandations d'entraînement
fun calculateWorkoutRecommendations(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    machine: Machine
): ExerciseRecommendation {
    val age = calculateAge(profileData.dateNaissance)
    val objectif = profileData.objectif

    // Utiliser la nouvelle fonction intelligente pour le poids
    val recommendedWeight = calculateSmartWeightRecommendation(
        machine = machine,
        workoutHistory = workoutHistory,
        targetReps = when (objectif) {
            "Force" -> 5
            "Prise de masse" -> 10
            "Endurance" -> 20
            "Sèche" -> 15
            else -> 10
        },
        objectif = objectif
    )

    // Recommandations selon l'objectif
    val (sets, reps, rest) = when (objectif) {
        "Force" -> Triple(5, 5, 180) // 5 séries, 5 reps, 3min repos
        "Prise de masse" -> Triple(4, 10, 90) // 4 séries, 10 reps, 1.5min repos
        "Endurance" -> Triple(3, 20, 60) // 3 séries, 20 reps, 1min repos
        "Sèche" -> Triple(4, 15, 75) // 4 séries, 15 reps, 1.25min repos
        else -> Triple(3, 12, 90) // Par défaut
    }

    return ExerciseRecommendation(
        sets = sets,
        reps = reps,
        weight = recommendedWeight,
        restTime = rest,
        notes = generateExerciseNotes(objectif, age, machine)
    )
}

data class ExerciseRecommendation(
    val sets: Int,
    val reps: Int,
    val weight: Double,
    val restTime: Int,
    val notes: String
)

fun generateExerciseNotes(objectif: String, age: Int, machine: Machine): String {
    val baseNotes = mutableListOf<String>()

    when (objectif) {
        "Force" -> {
            baseNotes.add("Concentrez-vous sur la technique")
            baseNotes.add("Charges lourdes, mouvement contrôlé")
            baseNotes.add("Repos complet entre séries")
        }
        "Prise de masse" -> {
            baseNotes.add("Tempo : 3 sec descente, 1 sec montée")
            baseNotes.add("Maximisez la tension musculaire")
            baseNotes.add("Échauffement important")
        }
        "Endurance" -> {
            baseNotes.add("Rythme soutenu")
            baseNotes.add("Charges modérées")
            baseNotes.add("Repos courts")
        }
        "Sèche" -> {
            baseNotes.add("Intensité élevée")
            baseNotes.add("Superset recommandé")
            baseNotes.add("Brûlage maximal")
        }
    }

    if (age > 50) {
        baseNotes.add("Échauffement prolongé recommandé")
    }

    if (machine.necessite_supervision) {
        baseNotes.add("⚠️ Supervision recommandée")
    }

    return baseNotes.joinToString(" • ")
}

// Fonction améliorée pour calculer les calories d'une séance
fun calculateWorkoutCaloriesImproved(
    exercises: List<ExerciseRecord>,
    age: Int,
    weight: Double,
    gender: String
): Int {
    val totalCalories = exercises.sumOf { exercise ->
        // Estimer l'intensité selon le poids et reps
        val intensity = when {
            exercise.weight > weight -> "Intense"
            exercise.weight > weight * 0.5 -> "Modéré"
            else -> "Léger"
        }

        val exerciseData = ExerciseCalorieData(
            name = exercise.name,
            sets = exercise.sets,
            reps = exercise.reps,
            weight = exercise.weight,
            restTime = 90, // Valeur par défaut
            intensity = intensity,
            oneRepMax = estimateOneRepMax(exercise.weight, exercise.reps)
        )

        calculateExerciseCalories(exerciseData, age, weight, gender)
    }

    return totalCalories
}

// Fonction pour trouver les records personnels
fun findPersonalRecords(
    currentExercises: List<ExerciseRecord>,
    workoutHistory: List<WorkoutEntry>
): List<String> {
    val records = mutableListOf<String>()

    // Créer un historique par exercice
    val exerciseHistory = workoutHistory.flatMap { workout ->
        workout.exercises.map { exercise ->
            Pair(exercise.name, exercise)
        }
    }.groupBy { it.first }

    currentExercises.forEach { currentExercise ->
        val history = exerciseHistory[currentExercise.name]?.map { it.second } ?: emptyList()

        if (history.isNotEmpty()) {
            val currentVolume = currentExercise.weight * currentExercise.reps
            val bestPreviousVolume = history.maxOfOrNull { it.weight * it.reps } ?: 0.0
            val bestPreviousWeight = history.maxOfOrNull { it.weight } ?: 0.0

            when {
                currentVolume > bestPreviousVolume -> {
                    records.add("${currentExercise.name} : Nouveau record de volume (${currentVolume.toInt()}kg)")
                }
                currentExercise.weight > bestPreviousWeight -> {
                    records.add("${currentExercise.name} : Nouveau record de poids (${currentExercise.weight.toInt()}kg)")
                }
            }
        } else {
            // Premier exercice de ce type
            records.add("${currentExercise.name} : Premier exercice enregistré !")
        }
    }

    return records
}

// Fonction pour calculer les recommandations de poids intelligentes
fun calculateSmartWeightRecommendation(
    machine: Machine,
    workoutHistory: List<WorkoutEntry>,
    targetReps: Int,
    objectif: String
): Double {
    // Récupérer l'historique de cet exercice
    val exerciseHistory = workoutHistory.flatMap { workout ->
        workout.exercises.filter { it.name == machine.nom }
    }.sortedBy { it.weight }

    if (exerciseHistory.isEmpty()) {
        // Première fois : recommandation basée sur le poids du corps
        return when (machine.groupeMusculairePrimaire) {
            "Pectoraux" -> 40.0
            "Dos" -> 35.0
            "Jambes" -> 60.0
            "Épaules" -> 20.0
            "Bras" -> 15.0
            else -> 30.0
        }
    }

    // Analyser les dernières performances
    val lastPerformances = exerciseHistory.takeLast(3)
    val lastPerformance = lastPerformances.last()

    // Calculer le 1RM basé sur la dernière performance
    val estimated1RM = estimateOneRepMax(lastPerformance.weight, lastPerformance.reps)

    // Analyser si l'utilisateur a réussi ses dernières séries
    val isProgressing = analyzeProgression(lastPerformances)

    // Calculer le poids recommandé selon l'objectif et la progression
    val targetWeight = when (objectif) {
        "Force" -> estimated1RM * 0.85 // 85% du 1RM pour 3-5 reps
        "Prise de masse" -> estimated1RM * 0.75 // 75% du 1RM pour 8-12 reps
        "Endurance" -> estimated1RM * 0.60 // 60% du 1RM pour 15+ reps
        "Sèche" -> estimated1RM * 0.70 // 70% du 1RM pour 12-15 reps
        else -> estimated1RM * 0.75
    }

    // Ajuster selon la progression
    val adjustedWeight = if (isProgressing) {
        // L'utilisateur progresse bien, on peut augmenter
        targetWeight * 1.05 // +5%
    } else {
        // L'utilisateur a des difficultés, on reste stable ou on diminue légèrement
        targetWeight * 0.95 // -5%
    }

    // S'assurer que le poids est dans les limites de la machine
    return adjustedWeight.coerceIn(machine.poidsMinimum, machine.poidsMaximum)
}

// Fonction pour analyser la progression des performances
fun analyzeProgression(performances: List<ExerciseRecord>): Boolean {
    if (performances.size < 2) return true

    val lastPerformance = performances.last()
    val previousPerformance = performances[performances.size - 2]

    // Calculer le volume (poids × reps) pour comparer
    val lastVolume = lastPerformance.weight * lastPerformance.reps
    val previousVolume = previousPerformance.weight * previousPerformance.reps

    // Considérer comme progression si:
    // - Volume augmenté
    // - Même volume mais plus de reps
    // - Même reps mais plus de poids
    return when {
        lastVolume > previousVolume -> true
        lastVolume == previousVolume && lastPerformance.reps >= previousPerformance.reps -> true
        lastPerformance.weight > previousPerformance.weight -> true
        else -> false
    }
}