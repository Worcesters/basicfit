package com.basicfit.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.clickable
import androidx.compose.foundation.background
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.BorderStroke
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import androidx.compose.ui.platform.LocalContext

// Gestionnaire de données pour la persistance locale
object DataManager {
    private const val PREFS_NAME = "basicfit_data"
    private const val KEY_WORKOUT_HISTORY = "workout_history"
    private const val KEY_USER_PROFILE = "user_profile"
    private const val KEY_MACHINE_HISTORY = "machine_history"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    // Sauvegarder l'historique des séances
    fun saveWorkoutHistory(context: Context, history: List<WorkoutSession>) {
        val prefs = getPrefs(context)
        val gson = Gson()
        val json = gson.toJson(history)
        prefs.edit().putString(KEY_WORKOUT_HISTORY, json).apply()
    }

    // Charger l'historique des séances
    fun loadWorkoutHistory(context: Context): List<WorkoutSession> {
        val prefs = getPrefs(context)
        val json = prefs.getString(KEY_WORKOUT_HISTORY, null)
        if (json != null) {
            val gson = Gson()
            val type = object : TypeToken<List<WorkoutSession>>() {}.type
            return gson.fromJson(json, type)
        }
        return getDefaultWorkoutHistory() // Données par défaut si rien n'est sauvegardé
    }

    // Ajouter une nouvelle séance
    fun addWorkoutSession(context: Context, session: WorkoutSession) {
        val currentHistory = loadWorkoutHistory(context).toMutableList()
        currentHistory.add(0, session) // Ajouter en premier (plus récent)

        // Garder seulement les 50 dernières séances
        if (currentHistory.size > 50) {
            currentHistory.removeAt(currentHistory.size - 1)
        }

        saveWorkoutHistory(context, currentHistory)
    }

    // Sauvegarder le profil utilisateur
    fun saveUserProfile(context: Context, name: String, email: String) {
        val prefs = getPrefs(context)
        prefs.edit()
            .putString("user_name", name)
            .putString("user_email", email)
            .apply()
    }

    // Charger le profil utilisateur
    fun loadUserProfile(context: Context): Pair<String, String> {
        val prefs = getPrefs(context)
        val name = prefs.getString("user_name", "John Doe") ?: "John Doe"
        val email = prefs.getString("user_email", "user@basicfit.com") ?: "user@basicfit.com"
        return Pair(name, email)
    }

    // Effacer toutes les données (pour la déconnexion)
    fun clearAllData(context: Context) {
        val prefs = getPrefs(context)
        prefs.edit().clear().apply()
    }

    // Données par défaut pour commencer
    private fun getDefaultWorkoutHistory(): List<WorkoutSession> {
        return listOf(
            WorkoutSession(
                date = "Aujourd'hui",
                duration = 0,
                exercises = listOf("Première séance"),
                calories = 0,
                totalWeight = 0,
                performance = "🎯 Commencez votre parcours !"
            )
        )
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)

        setContent {
            BasicFitAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color.White
                ) {
                    BasicFitApp()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BasicFitApp() {
    val navController = rememberNavController()
    var isAuthenticated by remember { mutableStateOf(false) }

    val onAuthenticated: (Boolean) -> Unit = { authenticated ->
        isAuthenticated = authenticated
    }

    if (isAuthenticated) {
        // Interface principale avec navigation
        MainAppInterface(navController) {
            // Fonction de déconnexion
            isAuthenticated = false
        }
    } else {
        // Interface d'authentification
        AuthenticationInterface(navController, onAuthenticated)
    }
}

@Composable
fun AuthenticationInterface(navController: NavHostController, onAuthenticated: (Boolean) -> Unit) {
    NavHost(navController = navController, startDestination = "login") {
        composable("login") {
            LoginScreen(navController, onAuthenticated)
        }
        composable("register") {
            RegisterScreen(navController, onAuthenticated)
        }
    }
}

@Composable
fun MainAppInterface(navController: NavHostController, onLogout: () -> Unit) {
    Scaffold(
        bottomBar = {
            BottomNavigationBar(navController = navController)
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = "machines",
            modifier = Modifier.padding(paddingValues)
        ) {
            composable("machines") {
                MachinesScreen(navController)
            }
            composable("workouts") {
                WorkoutsScreen(navController)
            }
            composable("profile") {
                ProfileScreen(navController, onLogout)
            }
            composable("machine_detail/{machineName}") { backStackEntry ->
                val machineName = backStackEntry.arguments?.getString("machineName") ?: ""
                MachineDetailScreen(machineName, navController)
            }
            composable("workout_builder") {
                WorkoutBuilderScreen(navController)
            }
            composable("training_mode") {
                TrainingModeScreen(navController)
            }
            composable("active_workout/{trainingMode}/{selectedMachines}") { backStackEntry ->
                val trainingMode = backStackEntry.arguments?.getString("trainingMode") ?: "volume"
                val selectedMachines = backStackEntry.arguments?.getString("selectedMachines") ?: ""
                ActiveWorkoutScreen(navController, trainingMode, selectedMachines.split(","))
            }
            composable("machine_usage/{machineName}") { backStackEntry ->
                val machineName = backStackEntry.arguments?.getString("machineName") ?: ""
                MachineUsageScreen(machineName, navController)
            }
            composable("workout_recap/{workoutData}") { backStackEntry ->
                val workoutData = backStackEntry.arguments?.getString("workoutData") ?: ""
                WorkoutRecapScreen(navController, workoutData)
            }
            composable("workout_history") {
                WorkoutHistoryScreen(navController)
            }
        }
    }
}

@Composable
fun BottomNavigationBar(navController: NavController) {
    val items = listOf(
        BottomNavItem("machines", "Machines", Icons.Filled.FitnessCenter),
        BottomNavItem("workouts", "Entraînements", Icons.Filled.DirectionsRun),
        BottomNavItem("profile", "Profil", Icons.Filled.Person)
    )

    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    NavigationBar(
        containerColor = Color.White,
        contentColor = Color(0xFFFF6B35)
    ) {
        items.forEach { item ->
            NavigationBarItem(
                icon = {
                    Icon(
                        item.icon,
                        contentDescription = item.title,
                        tint = if (currentRoute == item.route) Color(0xFFFF6B35) else Color.Gray
                    )
                },
                label = {
                    Text(
                        item.title,
                        color = if (currentRoute == item.route) Color(0xFFFF6B35) else Color.Gray
                    )
                },
                selected = currentRoute == item.route,
                onClick = {
                    navController.navigate(item.route) {
                        popUpTo(navController.graph.startDestinationId)
                        launchSingleTop = true
                    }
                }
            )
        }
    }
}

@Composable
fun MachinesScreen(navController: NavController) {
    var machines by remember { mutableStateOf(listOf<String>()) }
    var isLoading by remember { mutableStateOf(true) }

    // Simulation de chargement des données
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(1000)
        machines = listOf(
            "Leg Press", "Chest Press", "Lat Pulldown",
            "Shoulder Press", "Leg Curl", "Bicep Curl",
            "Tricep Extension", "Treadmill", "Exercise Bike",
            "Smith Machine", "Cable Crossover", "Hack Squat"
        )
        isLoading = false
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Text(
            text = "Machines",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35),
            modifier = Modifier.padding(bottom = 16.dp)
        )

        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(
                    color = Color(0xFFFF6B35)
                )
            }
        } else {
            Text(
                text = "Machines disponibles",
                fontSize = 20.sp,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(machines) { machine ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                navController.navigate("machine_detail/$machine")
                            },
                        colors = CardDefaults.cardColors(
                            containerColor = Color(0xFFF5F5F5)
                        )
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = machine,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.Medium
                            )
                            Icon(
                                Icons.Filled.ArrowForward,
                                contentDescription = "Voir détails",
                                tint = Color(0xFFFF6B35)
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun WorkoutsScreen(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Entraînements",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35),
            modifier = Modifier.padding(bottom = 16.dp)
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFF5F5F5)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Séance d'aujourd'hui",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("• Chest Press - 3 séries")
                Text("• Leg Press - 3 séries")
                Text("• Lat Pulldown - 3 séries")
                Spacer(modifier = Modifier.height(16.dp))
                                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = {
                            navController.navigate("workout_builder")
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B35)
                        )
                    ) {
                        Text("Créer séance")
                    }
                    Button(
                        onClick = {
                            // Séance rapide avec machines prédéfinies
                            navController.navigate("training_mode")
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFF2C2C2C)
                        )
                    ) {
                        Text("Séance rapide")
                    }
                }
            }
        }
    }
}

@Composable
fun ProfileScreen(navController: NavController, onLogout: () -> Unit) {
    val context = LocalContext.current

    // Charger les données utilisateur et l'historique
    val userProfile = remember { DataManager.loadUserProfile(context) }
    val workoutHistory = remember { DataManager.loadWorkoutHistory(context) }
    val weeklyWorkouts = workoutHistory.size.coerceAtMost(7) // Simulation séances cette semaine
    val maxWeight = if (workoutHistory.isNotEmpty()) workoutHistory.maxOf { it.totalWeight } else 120
    val streak = workoutHistory.size.coerceAtMost(10) // Simulation streak

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "Profil",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35),
            modifier = Modifier.padding(bottom = 16.dp)
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFF5F5F5)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Filled.Person,
                        contentDescription = "Profil",
                        modifier = Modifier.size(64.dp),
                        tint = Color(0xFFFF6B35)
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Column {
                        Text(
                            text = userProfile.first,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Membre BasicFit",
                            color = Color.Gray
                        )
                        Text(
                            text = userProfile.second,
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                Text(
                    text = "Statistiques",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("🏋️ Séances totales: ${workoutHistory.size}")
                Text("📈 Record poids: ${maxWeight}kg")
                Text("🔥 Séances excellentes: ${workoutHistory.count { it.performance == "Excellent" }}")
                if (workoutHistory.isNotEmpty()) {
                    Text("⏱️ Temps total: ${workoutHistory.sumOf { it.duration }}min")
                    Text("🔥 Calories brûlées: ${workoutHistory.sumOf { it.calories }}kcal")
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Bouton pour voir l'historique des séances
        Button(
            onClick = {
                navController.navigate("workout_history")
            },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFFF6B35)
            )
        ) {
            Icon(
                Icons.Filled.History,
                contentDescription = "Historique",
                modifier = Modifier.size(20.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Voir l'historique des séances", fontSize = 16.sp)
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Bouton de déconnexion
        OutlinedButton(
            onClick = {
                // Effacer toutes les données locales avant déconnexion
                DataManager.clearAllData(context)
                // Appeler la fonction de déconnexion
                onLogout()
            },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.outlinedButtonColors(
                contentColor = Color.Red
            ),
            border = BorderStroke(1.dp, Color.Red)
        ) {
            Icon(
                Icons.Filled.ExitToApp,
                contentDescription = "Déconnexion",
                modifier = Modifier.size(20.dp),
                tint = Color.Red
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Se déconnecter", fontSize = 16.sp, color = Color.Red)
        }
    }
}

@Composable
fun MachineDetailScreen(machineName: String, navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Text(
                text = machineName,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFF5F5F5)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "Informations",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("Groupe musculaire: Pectoraux")
                Text("Difficulté: Intermédiaire")
                Text("Disponible: Oui")

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Dernières séances",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text("• 15/01/2024 - 3x12 à 80kg")
                Text("• 12/01/2024 - 3x10 à 85kg")
                Text("• 10/01/2024 - 3x8 à 90kg")

                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = {
                        navController.navigate("machine_usage/$machineName")
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFFF6B35)
                    )
                ) {
                    Text("Utiliser cette machine")
                }
            }
        }
    }
}

@Composable
fun WorkoutBuilderScreen(navController: NavController) {
    var selectedMachines by remember { mutableStateOf(setOf<String>()) }

    val availableMachines = listOf(
        "Chest Press", "Leg Press", "Lat Pulldown",
        "Shoulder Press", "Leg Curl", "Bicep Curl",
        "Tricep Extension", "Smith Machine", "Cable Crossover",
        "Hack Squat", "Treadmill", "Exercise Bike"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Text(
                text = "Créer votre séance",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        Text(
            text = "Sélectionnez vos machines (${selectedMachines.size})",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(availableMachines) { machine ->
                val isSelected = selectedMachines.contains(machine)
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            selectedMachines = if (isSelected) {
                                selectedMachines - machine
                            } else {
                                selectedMachines + machine
                            }
                        },
                    colors = CardDefaults.cardColors(
                        containerColor = if (isSelected) Color(0xFFFFE0B2) else Color(0xFFF5F5F5)
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = machine,
                            fontSize = 16.sp,
                            fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                            color = if (isSelected) Color(0xFFFF6B35) else Color.Black
                        )
                        if (isSelected) {
                            Icon(
                                Icons.Filled.CheckCircle,
                                contentDescription = "Sélectionné",
                                tint = Color(0xFFFF6B35)
                            )
                        }
                    }
                }
            }
        }

        if (selectedMachines.isNotEmpty()) {
            Button(
                onClick = {
                    navController.navigate("training_mode") {
                        // Passer les machines sélectionnées via un argument global
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFF6B35)
                )
            ) {
                Text("Choisir le mode d'entraînement")
            }
        }
    }
}

@Composable
fun TrainingModeScreen(navController: NavController) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Text(
                text = "Mode d'entraînement",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        Text(
            text = "Choisissez votre objectif",
            fontSize = 18.sp,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.padding(bottom = 24.dp)
        )

        // Mode Endurance
        TrainingModeCard(
            title = "Endurance",
            description = "15-20 répétitions\n50-65% du 1RM\nAméliore l'endurance musculaire",
            color = Color(0xFF4CAF50),
            onClick = {
                val machines = "Chest Press,Leg Press,Lat Pulldown" // Machines par défaut pour séance rapide
                navController.navigate("active_workout/endurance/$machines")
            }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Mode Volume
        TrainingModeCard(
            title = "Volume musculaire",
            description = "8-12 répétitions\n65-75% du 1RM\nOptimal pour la croissance musculaire",
            color = Color(0xFFFF6B35),
            onClick = {
                val machines = "Chest Press,Leg Press,Lat Pulldown"
                navController.navigate("active_workout/volume/$machines")
            }
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Mode Puissance
        TrainingModeCard(
            title = "Puissance",
            description = "3-6 répétitions\n80-90% du 1RM\nDéveloppe la force maximale",
            color = Color(0xFFF44336),
            onClick = {
                val machines = "Chest Press,Leg Press,Lat Pulldown"
                navController.navigate("active_workout/puissance/$machines")
            }
        )
    }
}

@Composable
fun TrainingModeCard(
    title: String,
    description: String,
    color: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        colors = CardDefaults.cardColors(
            containerColor = color.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = title,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = description,
                fontSize = 14.sp,
                color = Color.Gray
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ActiveWorkoutScreen(navController: NavController, trainingMode: String, selectedMachines: List<String>) {
    var currentExercise by remember { mutableStateOf(0) }
    var currentSet by remember { mutableStateOf(1) }
    var isResting by remember { mutableStateOf(false) }
    var restTime by remember { mutableStateOf(90) }

    // Historique des dernières séances (simulé)
    val lastWorkoutData = remember {
        mutableMapOf(
            "Chest Press" to listOf(Triple(85, 8, "2024-01-15"), Triple(80, 10, "2024-01-12")),
            "Leg Press" to listOf(Triple(140, 6, "2024-01-15"), Triple(135, 8, "2024-01-12")),
            "Lat Pulldown" to listOf(Triple(70, 9, "2024-01-15"), Triple(65, 12, "2024-01-12")),
            "Shoulder Press" to listOf(Triple(55, 7, "2024-01-15"), Triple(50, 10, "2024-01-12")),
            "Leg Curl" to listOf(Triple(45, 10, "2024-01-15"), Triple(40, 12, "2024-01-12")),
            "Bicep Curl" to listOf(Triple(35, 8, "2024-01-15"), Triple(32, 10, "2024-01-12")),
            "Tricep Extension" to listOf(Triple(40, 9, "2024-01-15"), Triple(38, 11, "2024-01-12")),
            "Smith Machine" to listOf(Triple(110, 5, "2024-01-15"), Triple(105, 6, "2024-01-12")),
            "Cable Crossover" to listOf(Triple(30, 12, "2024-01-15"), Triple(28, 14, "2024-01-12")),
            "Hack Squat" to listOf(Triple(130, 10, "2024-01-15"), Triple(125, 10, "2024-01-12"))
        )
    }

    // Fonction pour calculer le 1RM selon la formule d'Epley
    fun calculate1RM(weight: Int, reps: Int): Int {
        return if (reps == 1) weight else (weight * (1 + reps / 30.0)).toInt()
    }

    // Calculer le 1RM basé sur les dernières séances
    fun getCalculated1RM(machine: String): Int {
        val history = lastWorkoutData[machine] ?: return 80
        val latest = history.firstOrNull() ?: return 80
        return calculate1RM(latest.first, latest.second)
    }

    // Temps de repos adapté selon le type d'exercice
    fun getRestTime(machine: String): Int {
        return when {
            machine.contains("Press") || machine.contains("Squat") -> 180 // Exercices composés: 3min
            machine.contains("Curl") || machine.contains("Extension") -> 90 // Isolation: 1.5min
            machine.contains("Cable") || machine.contains("Pulldown") -> 120 // Câbles: 2min
            machine.contains("Cardio") || machine.contains("Treadmill") || machine.contains("Bike") -> 60 // Cardio: 1min
            else -> 120 // Défaut: 2min
        }
    }

    // Fonction pour sauvegarder une série complétée avec progression intelligente
    fun saveCompletedSet(machine: String, weight: Int, reps: Int) {
        val currentHistory = lastWorkoutData[machine]?.toMutableList() ?: mutableListOf()
        currentHistory.add(0, Triple(weight, reps, "2024-01-18")) // Ajouter au début
        if (currentHistory.size > 10) currentHistory.removeAt(10) // Garder seulement les 10 dernières
        lastWorkoutData[machine] = currentHistory
    }

    // Fonction d'adaptation intelligente des poids pour la prochaine séance
    fun getAdaptedWeight(currentWeight: Int, currentReps: Int, targetReps: Int): Int {
        // Si l'utilisateur a dépassé les répétitions cibles de 2+ reps, augmenter le poids
        return when {
            currentReps >= targetReps + 2 -> {
                // Excellent performance, augmentation de 5-10%
                (currentWeight * 1.075).toInt() // +7.5% en moyenne
            }
            currentReps == targetReps + 1 -> {
                // Très bonne performance, augmentation modérée
                (currentWeight * 1.05).toInt() // +5%
            }
            currentReps == targetReps -> {
                // Performance parfaite, légère augmentation
                (currentWeight * 1.025).toInt() // +2.5%
            }
            currentReps >= targetReps - 1 -> {
                // Performance correcte, maintenir le poids
                currentWeight
            }
            else -> {
                // Performance insuffisante, réduire légèrement
                (currentWeight * 0.95).toInt() // -5%
            }
        }
    }

    // Calculer poids et reps selon le mode avec progression automatique
    fun getTrainingParams(machine: String): Triple<Int, Int, Int> {
        val calculated1RM = getCalculated1RM(machine)
        val baseParams = when (trainingMode) {
            "endurance" -> Pair((calculated1RM * 0.6).toInt(), 18) // 60% 1RM, 18 reps
            "volume" -> Pair((calculated1RM * 0.7).toInt(), 10)    // 70% 1RM, 10 reps
            "puissance" -> Pair((calculated1RM * 0.85).toInt(), 5) // 85% 1RM, 5 reps
            else -> Pair((calculated1RM * 0.7).toInt(), 10)
        }

        // Adapter le poids selon les dernières performances
        val history = lastWorkoutData[machine]
        val adaptedWeight = if (history?.isNotEmpty() == true) {
            val lastSession = history.first()
            getAdaptedWeight(lastSession.first, lastSession.second, baseParams.second)
        } else {
            baseParams.first
        }

        return Triple(adaptedWeight, baseParams.second, calculated1RM)
    }

    val exercises = selectedMachines.filter { it.isNotEmpty() }
    val currentMachine = if (exercises.isNotEmpty()) exercises[currentExercise] else "Machine"
    val (suggestedWeight, suggestedReps, calculated1RM) = getTrainingParams(currentMachine)

    var weight by remember { mutableStateOf(suggestedWeight.toString()) }
    var reps by remember { mutableStateOf(suggestedReps.toString()) }

    // Mettre à jour les suggestions quand on change d'exercice
    LaunchedEffect(currentExercise) {
        val (newWeight, newReps, _) = getTrainingParams(currentMachine)
        weight = newWeight.toString()
        reps = newReps.toString()
        restTime = getRestTime(currentMachine)
    }

    // Timer de repos
    LaunchedEffect(isResting) {
        if (isResting) {
            for (i in restTime downTo 0) {
                restTime = i
                kotlinx.coroutines.delay(1000)
            }
            isResting = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Column {
                Text(
                    text = "Mode: ${trainingMode.replaceFirstChar { it.uppercaseChar() }}",
                    fontSize = 16.sp,
                    color = Color.Gray
                )
                Text(
                    text = "Entraînement en cours",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
            }
        }

        if (isResting) {
            // Écran de repos
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE3F2FD)
                )
            ) {
                Column(
                    modifier = Modifier
                        .padding(20.dp)
                        .fillMaxWidth(),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "💤 Repos",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1976D2)
                    )
                    Text(
                        text = "${restTime}s",
                        fontSize = 64.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1976D2)
                    )
                    Text(
                        text = getRestTimeDescription(currentMachine),
                        fontSize = 14.sp,
                        color = Color.Gray,
                        modifier = Modifier.padding(top = 8.dp),
                        textAlign = TextAlign.Center
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Bouton pour passer le repos
                    Button(
                        onClick = {
                            isResting = false
                            restTime = 90
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B35)
                        )
                    ) {
                        Icon(
                            Icons.Filled.SkipNext,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Passer le repos")
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Button(
                        onClick = {
                            if (currentSet < 3) {
                                currentSet++
                                isResting = true
                                restTime = getRestTime(currentMachine)
                            } else if (currentExercise < exercises.size - 1) {
                                currentExercise++
                                currentSet = 1
                            } else {
                                // Créer les données de récapitulatif de l'entraînement
                                val workoutData = exercises.joinToString(",") { machine ->
                                    val history = lastWorkoutData[machine]?.firstOrNull()
                                    // Utiliser des valeurs par défaut réalistes selon le type de machine
                                    val defaultWeight = when {
                                        machine.contains("Leg Press") -> 100
                                        machine.contains("Chest Press") -> 70
                                        machine.contains("Lat Pulldown") -> 60
                                        machine.contains("Shoulder Press") -> 50
                                        machine.contains("Smith Machine") -> 80
                                        machine.contains("Hack Squat") -> 90
                                        machine.contains("Curl") -> 35
                                        machine.contains("Extension") -> 40
                                        else -> 60
                                    }
                                    val defaultReps = when {
                                        machine.contains("Press") || machine.contains("Pulldown") -> 12
                                        machine.contains("Squat") -> 8
                                        machine.contains("Curl") || machine.contains("Extension") -> 10
                                        else -> 10
                                    }
                                    "${machine}:${history?.first?.coerceIn(5, 300) ?: defaultWeight}:${history?.second?.coerceIn(1, 30) ?: defaultReps}"
                                }
                                navController.navigate("workout_recap/$workoutData")
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B35)
                        )
                    ) {
                        Text(
                            if (currentSet < 3) "Série terminée"
                            else if (currentExercise < exercises.size - 1) "Exercice suivant"
                            else "Terminer l'entraînement"
                        )
                    }
                }
            }
        } else {
            // Écran d'exercice normal
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFF5F5F5)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Exercice ${currentExercise + 1}/${exercises.size}",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF6B35)
                    )
                    Text(
                        text = currentMachine,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(vertical = 8.dp)
                    )

                    // Affichage des paramètres selon le mode
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = when(trainingMode) {
                                "endurance" -> Color(0xFF4CAF50).copy(alpha = 0.1f)
                                "puissance" -> Color(0xFFF44336).copy(alpha = 0.1f)
                                else -> Color(0xFFFF6B35).copy(alpha = 0.1f)
                            }
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(12.dp)
                        ) {
                            val modeColor = when(trainingMode) {
                                "endurance" -> Color(0xFF4CAF50)
                                "puissance" -> Color(0xFFF44336)
                                else -> Color(0xFFFF6B35)
                            }
                            val lastSession = lastWorkoutData[currentMachine]?.firstOrNull()
                            Text(
                                text = "📊 1RM calculé: ${calculated1RM}kg",
                                fontSize = 14.sp,
                                color = Color.Gray
                            )
                            Text(
                                text = "🎯 Recommandé: ${suggestedWeight}kg × ${suggestedReps} reps",
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                color = modeColor
                            )
                            lastSession?.let {
                                Text(
                                    text = "📈 Dernière séance: ${it.first}kg × ${it.second} reps",
                                    fontSize = 12.sp,
                                    color = Color.Gray,
                                    modifier = Modifier.padding(top = 4.dp)
                                )
                            }
                        }
                    }

                    Text(
                        text = "Série $currentSet/3",
                        fontSize = 16.sp,
                        color = Color.Gray
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Poids (kg)", fontWeight = FontWeight.Bold)
                            Text(weight, fontSize = 24.sp, color = Color(0xFFFF6B35))
                            Row {
                                IconButton(onClick = {
                                    val newWeight = (weight.toIntOrNull() ?: 80) - 5
                                    if (newWeight >= 0) weight = newWeight.toString()
                                }) {
                                    Icon(Icons.Filled.Remove, contentDescription = "Diminuer")
                                }
                                IconButton(onClick = {
                                    weight = ((weight.toIntOrNull() ?: 80) + 5).toString()
                                }) {
                                    Icon(Icons.Filled.Add, contentDescription = "Augmenter")
                                }
                            }
                        }

                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Répétitions", fontWeight = FontWeight.Bold)
                            Text(reps, fontSize = 24.sp, color = Color(0xFFFF6B35))
                            Row {
                                IconButton(onClick = {
                                    val newReps = (reps.toIntOrNull() ?: 12) - 1
                                    if (newReps >= 1) reps = newReps.toString()
                                }) {
                                    Icon(Icons.Filled.Remove, contentDescription = "Diminuer")
                                }
                                IconButton(onClick = {
                                    reps = ((reps.toIntOrNull() ?: 12) + 1).toString()
                                }) {
                                    Icon(Icons.Filled.Add, contentDescription = "Augmenter")
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                // Sauvegarder la série complétée
                                saveCompletedSet(
                                    currentMachine,
                                    weight.toIntOrNull() ?: suggestedWeight,
                                    reps.toIntOrNull() ?: suggestedReps
                                )

                                if (currentSet < 3) {
                                    currentSet++
                                    isResting = true
                                    restTime = getRestTime(currentMachine)
                                } else if (currentExercise < exercises.size - 1) {
                                    currentExercise++
                                    currentSet = 1
                                } else {
                                    // Créer les données de récapitulatif de l'entraînement
                                    val workoutData = exercises.joinToString(",") { machine ->
                                        val history = lastWorkoutData[machine]?.firstOrNull()
                                        // Utiliser des valeurs par défaut réalistes selon le type de machine
                                        val defaultWeight = when {
                                            machine.contains("Leg Press") -> 100
                                            machine.contains("Chest Press") -> 70
                                            machine.contains("Lat Pulldown") -> 60
                                            machine.contains("Shoulder Press") -> 50
                                            machine.contains("Smith Machine") -> 80
                                            machine.contains("Hack Squat") -> 90
                                            machine.contains("Curl") -> 35
                                            machine.contains("Extension") -> 40
                                            else -> 60
                                        }
                                        val defaultReps = when {
                                            machine.contains("Press") || machine.contains("Pulldown") -> 12
                                            machine.contains("Squat") -> 8
                                            machine.contains("Curl") || machine.contains("Extension") -> 10
                                            else -> 10
                                        }
                                        "${machine}:${history?.first?.coerceIn(5, 300) ?: defaultWeight}:${history?.second?.coerceIn(1, 30) ?: defaultReps}"
                                    }
                                    navController.navigate("workout_recap/$workoutData")
                                }
                            },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = Color(0xFFFF6B35)
                            )
                        ) {
                            Text(
                                if (currentSet < 3) "Série terminée"
                                else if (currentExercise < exercises.size - 1) "Exercice suivant"
                                else "Terminer l'entraînement"
                            )
                        }
                    }
                }
            }
        }
    }
}

// Fonction pour décrire le temps de repos
fun getRestTimeDescription(machine: String): String {
    return when {
        machine.contains("Press") || machine.contains("Squat") -> "Exercice composé - Repos long recommandé"
        machine.contains("Curl") || machine.contains("Extension") -> "Exercice d'isolation - Repos modéré"
        machine.contains("Cable") || machine.contains("Pulldown") -> "Exercice à poulie - Repos standard"
        else -> "Repos adapté à l'exercice"
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MachineUsageScreen(machineName: String, navController: NavController) {
    var currentSet by remember { mutableStateOf(1) }
    var weight by remember { mutableStateOf("80") }
    var reps by remember { mutableStateOf("12") }
    var restTime by remember { mutableStateOf(90) }
    var isResting by remember { mutableStateOf(false) }

    // Liste pour sauvegarder chaque série complétée avec ses valeurs spécifiques
    var completedSets by remember { mutableStateOf(listOf<Pair<String, String>>()) }

    // Historique des séances précédentes pour cette machine (simulé mais intelligent)
    val machineHistory = remember {
        mutableMapOf(
            "Chest Press" to listOf(Triple(80, 12, "2024-01-15"), Triple(75, 12, "2024-01-12")),
            "Leg Press" to listOf(Triple(140, 10, "2024-01-15"), Triple(135, 10, "2024-01-12")),
            "Lat Pulldown" to listOf(Triple(70, 12, "2024-01-15"), Triple(65, 12, "2024-01-12")),
            "Shoulder Press" to listOf(Triple(55, 10, "2024-01-15"), Triple(50, 10, "2024-01-12")),
            "Leg Curl" to listOf(Triple(45, 12, "2024-01-15"), Triple(40, 12, "2024-01-12")),
            "Bicep Curl" to listOf(Triple(35, 12, "2024-01-15"), Triple(32, 12, "2024-01-12")),
            "Tricep Extension" to listOf(Triple(40, 12, "2024-01-15"), Triple(38, 12, "2024-01-12")),
            "Smith Machine" to listOf(Triple(110, 8, "2024-01-15"), Triple(105, 8, "2024-01-12")),
            "Cable Crossover" to listOf(Triple(30, 15, "2024-01-15"), Triple(28, 15, "2024-01-12")),
            "Hack Squat" to listOf(Triple(130, 10, "2024-01-15"), Triple(125, 10, "2024-01-12"))
        )
    }

    // Fonction d'adaptation intelligente des poids pour cette machine
    fun getAdaptedWeight(currentWeight: Int, currentReps: Int, targetReps: Int): Int {
        return when {
            currentReps >= targetReps + 2 -> (currentWeight * 1.075).toInt() // +7.5%
            currentReps == targetReps + 1 -> (currentWeight * 1.05).toInt()  // +5%
            currentReps == targetReps -> (currentWeight * 1.025).toInt()     // +2.5%
            currentReps >= targetReps - 1 -> currentWeight                   // Maintenir
            else -> (currentWeight * 0.95).toInt()                          // -5%
        }
    }

    // Initialiser les poids suggérés basés sur l'historique
    LaunchedEffect(machineName) {
        val history = machineHistory[machineName]
        if (history?.isNotEmpty() == true) {
            val lastSession = history.first()
            val targetReps = 12 // Répétitions cibles standard
            val suggestedWeight = getAdaptedWeight(lastSession.first, lastSession.second, targetReps)
            weight = suggestedWeight.toString()
            reps = targetReps.toString()
        }
    }

    // Fonction pour sauvegarder une série et mettre à jour l'historique
    fun saveCompletedSetToHistory(weight: Int, reps: Int) {
        val currentHistory = machineHistory[machineName]?.toMutableList() ?: mutableListOf()
        currentHistory.add(0, Triple(weight, reps, "2024-01-18"))
        if (currentHistory.size > 10) currentHistory.removeAt(10)
        machineHistory[machineName] = currentHistory
    }

    LaunchedEffect(isResting) {
        if (isResting) {
            for (i in restTime downTo 0) {
                restTime = i
                kotlinx.coroutines.delay(1000)
            }
            isResting = false
            restTime = 90
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Column {
                Text(
                    text = machineName,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35)
                )
                // Afficher les suggestions basées sur l'historique
                val history = machineHistory[machineName]
                if (history?.isNotEmpty() == true) {
                    val lastSession = history.first()
                    Text(
                        text = "📈 Dernière: ${lastSession.first}kg × ${lastSession.second} reps",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }
        }

        if (isResting) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE3F2FD)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Repos",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1976D2)
                    )
                    Text(
                        text = "$restTime s",
                        fontSize = 48.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1976D2)
                    )
                    Text("Préparez-vous pour la série suivante")

                    Spacer(modifier = Modifier.height(20.dp))

                    // Bouton pour passer le repos
                    Button(
                        onClick = {
                            isResting = false
                            restTime = 90
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B35)
                        )
                    ) {
                        Icon(
                            Icons.Filled.SkipNext,
                            contentDescription = null,
                            modifier = Modifier.size(20.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Passer le repos")
                    }
                }
            }
        } else {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFF5F5F5)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "Série $currentSet/3",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF6B35)
                    )

                    // Afficher les recommandations intelligentes
                    val history = machineHistory[machineName]
                    if (history?.isNotEmpty() == true) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = Color(0xFFE8F5E8)
                            )
                        ) {
                            Column(
                                modifier = Modifier.padding(12.dp)
                            ) {
                                Text(
                                    text = "🎯 Recommandation intelligente",
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = Color(0xFF2E7D32)
                                )
                                Text(
                                    text = "Basé sur vos dernières performances",
                                    fontSize = 12.sp,
                                    color = Color.Gray
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceEvenly
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Poids (kg)", fontWeight = FontWeight.Bold)
                            Text(weight, fontSize = 32.sp, color = Color(0xFFFF6B35))
                            Row {
                                IconButton(onClick = {
                                    val newWeight = (weight.toIntOrNull() ?: 80) - 5
                                    if (newWeight >= 0) weight = newWeight.toString()
                                }) {
                                    Icon(Icons.Filled.Remove, contentDescription = "Diminuer")
                                }
                                IconButton(onClick = {
                                    weight = ((weight.toIntOrNull() ?: 80) + 5).toString()
                                }) {
                                    Icon(Icons.Filled.Add, contentDescription = "Augmenter")
                                }
                            }
                        }

                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("Répétitions", fontWeight = FontWeight.Bold)
                            Text(reps, fontSize = 32.sp, color = Color(0xFFFF6B35))
                            Row {
                                IconButton(onClick = {
                                    val newReps = (reps.toIntOrNull() ?: 12) - 1
                                    if (newReps >= 1) reps = newReps.toString()
                                }) {
                                    Icon(Icons.Filled.Remove, contentDescription = "Diminuer")
                                }
                                IconButton(onClick = {
                                    reps = ((reps.toIntOrNull() ?: 12) + 1).toString()
                                }) {
                                    Icon(Icons.Filled.Add, contentDescription = "Augmenter")
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    Button(
                        onClick = {
                            // Sauvegarder la série actuelle avec ses valeurs spécifiques
                            completedSets = completedSets + Pair(weight, reps)

                            // Sauvegarder dans l'historique pour la progression future
                            saveCompletedSetToHistory(
                                weight.toIntOrNull() ?: 80,
                                reps.toIntOrNull() ?: 12
                            )

                            if (currentSet < 3) {
                                currentSet++
                                isResting = true
                                restTime = 90
                            } else {
                                // Créer les données de récapitulatif avec l'exercice terminé - valeurs réalistes
                                val safeWeight = weight.toIntOrNull()?.coerceIn(5, 300) ?: 70
                                val safeReps = reps.toIntOrNull()?.coerceIn(1, 30) ?: 12
                                val workoutData = "$machineName,$safeWeight,$safeReps,$currentSet"
                                navController.navigate("workout_recap/$workoutData")
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color(0xFFFF6B35)
                        )
                    ) {
                        Text(
                            if (currentSet < 3) "Série terminée - Repos"
                            else "Terminer l'exercice"
                        )
                    }

                    // Bouton pour terminer l'entraînement et voir le récapitulatif
                    if (currentSet >= 2) { // Permettre de finir après au moins 2 séries
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedButton(
                            onClick = {
                                val safeWeight = weight.toIntOrNull()?.coerceIn(5, 300) ?: 70
                                val safeReps = reps.toIntOrNull()?.coerceIn(1, 30) ?: 12
                                val workoutData = "$machineName,$safeWeight,$safeReps,$currentSet"
                                navController.navigate("workout_recap/$workoutData")
                            },
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.outlinedButtonColors(
                                contentColor = Color(0xFFFF6B35)
                            )
                        ) {
                            Icon(
                                Icons.Filled.Assessment,
                                contentDescription = null,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Voir le récapitulatif de l'entraînement")
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Historique de la séance",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35)
        )

        // Afficher chaque série complétée avec ses valeurs spécifiques
        completedSets.forEachIndexed { index, (setWeight, setReps) ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE8F5E8)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Série ${index + 1}: ${setWeight}kg x $setReps reps ✓",
                        color = Color(0xFF2E7D32)
                    )

                    // Indicateur de performance par rapport à l'objectif
                    val targetReps = 12
                    val actualReps = setReps.toIntOrNull() ?: 0
                    val performanceIcon = when {
                        actualReps >= targetReps + 2 -> "🔥" // Excellent
                        actualReps >= targetReps -> "💪"     // Très bien
                        actualReps >= targetReps - 1 -> "✅"  // Bien
                        else -> "⚠️"                         // À améliorer
                    }
                    Text(
                        text = performanceIcon,
                        fontSize = 16.sp
                    )
                }
            }
        }

        // Afficher l'historique des séances précédentes
        if (machineHistory[machineName]?.size ?: 0 > 1) {
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "📊 Séances précédentes",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )

            machineHistory[machineName]?.drop(1)?.take(3)?.forEachIndexed { _, session ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 2.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFF8F8F8)
                    )
                ) {
                    Text(
                        text = "${session.third}: ${session.first}kg × ${session.second} reps",
                        modifier = Modifier.padding(8.dp),
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun WorkoutRecapScreen(navController: NavController, workoutData: String) {
    val context = LocalContext.current

    // Debug: Afficher les données reçues
    println("DEBUG: workoutData reçu = '$workoutData'")

    // Si workoutData est vide ou invalide, utiliser des données d'exemple
    val safeWorkoutData = if (workoutData.isBlank() || workoutData == "null") {
        "Chest Press:75:12:3,Leg Press:120:10:3,Lat Pulldown:65:12:3"
    } else {
        workoutData
    }

    // Parser les données d'entraînement avec support de formats multiples
    val exercisesList = safeWorkoutData.split(",").filter { it.isNotEmpty() }
    println("DEBUG: exercisesList = $exercisesList")

    // Données réalistes pour le calcul des calories par type d'exercice
    val exerciseCaloriesData = mapOf(
        "Chest Press" to 8.5f,      // kcal/min (exercice composé, haut du corps)
        "Leg Press" to 12.0f,       // kcal/min (exercice composé, gros muscles)
        "Lat Pulldown" to 7.5f,     // kcal/min (exercice composé, dos)
        "Shoulder Press" to 6.5f,   // kcal/min (exercice isolation, épaules)
        "Leg Curl" to 5.5f,         // kcal/min (exercice isolation, jambes)
        "Bicep Curl" to 4.0f,       // kcal/min (exercice isolation, petits muscles)
        "Tricep Extension" to 4.5f, // kcal/min (exercice isolation, triceps)
        "Smith Machine" to 10.0f,   // kcal/min (exercice composé, polyvalent)
        "Cable Crossover" to 6.0f,  // kcal/min (exercice isolation, pectoraux)
        "Hack Squat" to 11.0f       // kcal/min (exercice composé, jambes)
    )

    // Historique des séances précédentes pour comparaison
    val workoutHistory = remember {
        mapOf(
            "Chest Press" to listOf(
                Triple(75, 12, "2024-01-15"), // poids, reps par série, date
                Triple(70, 12, "2024-01-12")
            ),
            "Leg Press" to listOf(
                Triple(120, 10, "2024-01-15"),
                Triple(115, 10, "2024-01-12")
            ),
            "Lat Pulldown" to listOf(
                Triple(65, 12, "2024-01-15"),
                Triple(60, 12, "2024-01-12")
            )
        )
    }

    // Calculer les vraies statistiques de la séance
    var totalSets = 0        // Nombre total de séries
    var totalReps = 0        // Nombre total de répétitions
    var realDuration = 0     // Durée réelle calculée
    var totalCalories = 0f   // Calories réelles
    val exercisesDetails = mutableListOf<ExerciseDetail>()

    exercisesList.forEach { exerciseData ->
        println("DEBUG: traitement de exerciseData = '$exerciseData'")

        val parts = if (exerciseData.contains(":")) {
            exerciseData.split(":")
        } else {
            exerciseData.split(",")
        }

        println("DEBUG: parts = $parts")

        if (parts.size >= 3) {
            val machineName = parts[0].trim()
            // Ajouter des limites réalistes pour éviter des valeurs folles
            val weight = (parts[1].trim().toIntOrNull() ?: 0).coerceIn(5, 300) // Entre 5kg et 300kg max
            val reps = (parts[2].trim().toIntOrNull() ?: 0).coerceIn(1, 30)   // Entre 1 et 30 reps max
            val sets = if (parts.size > 3) (parts[3].trim().toIntOrNull() ?: 3).coerceIn(1, 5) else 3 // 1-5 séries max

            println("DEBUG: machineName='$machineName', weight=$weight, reps=$reps, sets=$sets")

            // Si toujours à 0, utiliser des valeurs par défaut
            val finalWeight = if (weight == 0) when {
                machineName.contains("Leg Press") -> 100
                machineName.contains("Chest Press") -> 75
                machineName.contains("Lat Pulldown") -> 65
                else -> 60
            } else weight

            val finalReps = if (reps == 0) when {
                machineName.contains("Press") || machineName.contains("Pulldown") -> 12
                machineName.contains("Squat") -> 8
                else -> 10
            } else reps

            // Calculs réels pour cet exercice
            val exerciseVolume = finalWeight * finalReps * sets
            val exerciseTotalReps = finalReps * sets

            // Durée réaliste : temps d'exécution + repos
            val executionTime = sets * 2  // 2 min par série (effort + récupération intra-série)
            val restTime = (sets - 1) * when {
                machineName.contains("Press") || machineName.contains("Squat") -> 3.0f // 3min entre séries
                machineName.contains("Curl") || machineName.contains("Extension") -> 1.5f // 1.5min
                else -> 2.0f // 2min par défaut
            }
            val exerciseDuration = (executionTime.toFloat() + restTime).toInt()

            // Calories spécifiques à l'exercice
            val caloriesPerMin = exerciseCaloriesData[machineName] ?: 6.0f
            val exerciseCalories = exerciseDuration.toFloat() * caloriesPerMin

            // Progression par rapport à la dernière séance
            val lastSession = workoutHistory[machineName]?.firstOrNull()
            val progression = if (lastSession != null) {
                // Comparer avec le poids de la dernière séance
                val lastWeight = lastSession.first
                val weightChange = finalWeight - lastWeight
                when {
                    weightChange > 10 -> "🚀 +${weightChange}kg"
                    weightChange > 0 -> "📈 +${weightChange}kg"
                    weightChange == 0 -> "🎯 Maintenu"
                    else -> "📉 ${weightChange}kg"
                }
            } else "🆕 Nouveau"

            // Évaluation de performance
            val targetReps = when (machineName) {
                "Chest Press", "Leg Press", "Lat Pulldown" -> 12
                "Smith Machine", "Hack Squat" -> 8
                else -> 10
            }
            val performance = when {
                finalReps >= targetReps + 2 -> "🔥 Excellent"
                finalReps >= targetReps -> "💪 Très bien"
                finalReps >= targetReps - 1 -> "✅ Bien"
                else -> "⚠️ À améliorer"
            }

            totalSets += sets
            totalReps += exerciseTotalReps
            realDuration += exerciseDuration
            totalCalories += exerciseCalories

            exercisesDetails.add(ExerciseDetail(
                name = machineName,
                sets = sets,
                weight = finalWeight,
                totalReps = exerciseTotalReps,
                volume = exerciseVolume,
                duration = exerciseDuration,
                calories = exerciseCalories,
                progression = progression,
                performance = performance
            ))

            println("DEBUG: exercice ajouté - $machineName: poids=${finalWeight}kg, calories=$exerciseCalories")
        }
    }

    println("DEBUG: totaux finaux - exercices=${exercisesDetails.size}, calories=$totalCalories, duration=$realDuration")

    // Si aucun exercice n'a été traité, utiliser des données d'exemple
    if (exercisesDetails.isEmpty()) {
        println("DEBUG: Aucun exercice traité, utilisation de données d'exemple")

        // Ajouter des exercices d'exemple
        val exampleExercises = listOf(
            Triple("Chest Press", 75, 12),
            Triple("Leg Press", 120, 10),
            Triple("Lat Pulldown", 65, 12)
        )

        exampleExercises.forEach { (machineName, weight, reps) ->
            val sets = 3
            val exerciseVolume = weight * reps * sets
            val exerciseTotalReps = reps * sets
            val exerciseDuration = 8 // durée d'exemple
            val exerciseCalories = exerciseDuration.toFloat() * (exerciseCaloriesData[machineName] ?: 6.0f)

            totalSets += sets
            totalReps += exerciseTotalReps
            realDuration += exerciseDuration
            totalCalories += exerciseCalories

            exercisesDetails.add(ExerciseDetail(
                name = machineName,
                sets = sets,
                weight = weight,
                totalReps = exerciseTotalReps,
                volume = exerciseVolume,
                duration = exerciseDuration,
                calories = exerciseCalories,
                progression = "📈 +5kg",
                performance = "💪 Très bien"
            ))
        }
    }

    // Calculer les comparaisons avec les séances précédentes
    val averageWeight = if (exercisesDetails.isNotEmpty()) {
        exercisesDetails.sumOf { it.weight } / exercisesDetails.size
    } else 0

    val previousAverageWeight = workoutHistory.values.mapNotNull { sessions ->
        sessions.firstOrNull()?.first
    }.average().takeIf { !it.isNaN() }?.toInt() ?: 0

    val intensityProgress = averageWeight - previousAverageWeight

    // Estimations réalistes supplémentaires
    val averageIntensity = if (totalReps > 0) exercisesDetails.sumOf { it.weight * it.totalReps } / totalReps else 0

    // Sauvegarder automatiquement la séance terminée dans l'historique
    LaunchedEffect(key1 = workoutData) {
        if (exercisesDetails.isNotEmpty()) {
            val currentDate = java.text.SimpleDateFormat("dd MMM yyyy", java.util.Locale.FRENCH).format(java.util.Date())
            val totalWeight = exercisesDetails.sumOf { it.weight * it.totalReps }
            val excellentCount = exercisesDetails.count { it.performance.contains("Excellent") }

            val sessionPerformance = when {
                excellentCount >= exercisesDetails.size * 0.7 -> "Excellent"
                excellentCount >= exercisesDetails.size * 0.4 -> "Très bien"
                else -> "Bien"
            }

            val newSession = WorkoutSession(
                date = currentDate,
                duration = realDuration,
                exercises = exercisesDetails.map { it.name },
                calories = totalCalories.toInt(),
                totalWeight = totalWeight,
                performance = sessionPerformance
            )

            DataManager.addWorkoutSession(context, newSession)
            println("DEBUG: Séance sauvegardée automatiquement - ${newSession.date}")
        }
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            // En-tête du récapitulatif avec performances
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFFF6B35)
                )
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        Icons.Filled.CheckCircle,
                        contentDescription = "Séance terminée",
                        modifier = Modifier.size(60.dp),
                        tint = Color.White
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        text = "🎉 Séance Terminée !",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )

                    Text(
                        text = when {
                            intensityProgress > 100 -> "Performance exceptionnelle ! 🚀"
                            intensityProgress > 0 -> "Excellente progression ! 📈"
                            intensityProgress == 0 -> "Performance maintenue 🎯"
                            else -> "Prochaine fois sera meilleure ! 💪"
                        },
                        fontSize = 16.sp,
                        color = Color.White.copy(alpha = 0.9f),
                        textAlign = TextAlign.Center
                    )
                }
            }
        }

        item {
            // Statistiques détaillées et réalistes
            Text(
                text = "📊 Statistiques détaillées",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                RealisticStatsCard(
                    title = "Durée",
                    value = "${realDuration}",
                    unit = "min",
                    icon = "⏱️",
                    change = "+5 min vs dernière",
                    modifier = Modifier.weight(1f)
                )

                RealisticStatsCard(
                    title = "Intensité",
                    value = "${averageIntensity}",
                    unit = "kg/rep",
                    icon = "💪",
                    change = "Moyenne séance",
                    modifier = Modifier.weight(1f)
                )
            }
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                RealisticStatsCard(
                    title = "Calories",
                    value = "${totalCalories.toInt()}",
                    unit = "kcal",
                    icon = "🔥",
                    change = "Calcul réaliste",
                    modifier = Modifier.weight(1f)
                )

                RealisticStatsCard(
                    title = "Séries",
                    value = "$totalSets",
                    unit = "réalisées",
                    icon = "🎯",
                    change = "$totalReps reps total",
                    modifier = Modifier.weight(1f)
                )
            }
        }

        item {
            // Métriques avancées
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFF8F9FA)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "📈 Métriques avancées",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF6B35)
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("💼 Intensité moyenne: ${averageIntensity}kg par rep")
                    Text("⚡ Densité d'entraînement: ${String.format("%.1f", totalReps.toFloat() / realDuration.toFloat())} reps/min")
                    Text("🔄 Temps de repos optimal respecté")
                    Text("🎯 ${exercisesDetails.count { it.performance.contains("Excellent") }} exercices excellents")
                }
            }
        }

        item {
            // Exercices détaillés avec vraies performances
            Text(
                text = "🎯 Détail des exercices",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        items(exercisesDetails) { exercise ->
            DetailedExerciseCard(exercise)
        }

        item {
            // Suggestions intelligentes pour la prochaine séance
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE8F5E8)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "🚀 Prochaine séance",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2E7D32)
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    exercisesDetails.forEach { exercise ->
                        val suggestion = when {
                            exercise.performance.contains("Excellent") ->
                                "${exercise.name}: +5kg ou +2 reps"
                            exercise.performance.contains("Très bien") ->
                                "${exercise.name}: +2.5kg ou +1 rep"
                            exercise.performance.contains("Bien") ->
                                "${exercise.name}: Maintenir le poids"
                            else ->
                                "${exercise.name}: -5kg et focus technique"
                        }
                        Text(
                            text = "• $suggestion",
                            fontSize = 14.sp,
                            color = Color(0xFF2E7D32),
                            modifier = Modifier.padding(vertical = 2.dp)
                        )
                    }
                }
            }
        }

        item {
            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = { navController.navigate("machines") },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFFF6B35)
                    )
                ) {
                    Text("Terminer")
                }

                OutlinedButton(
                    onClick = { /* Partager */ },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Color(0xFFFF6B35)
                    )
                ) {
                    Icon(Icons.Filled.Share, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Partager")
                }
            }
        }
    }
}

data class BottomNavItem(
    val route: String,
    val title: String,
    val icon: ImageVector
)

data class ExerciseDetail(
    val name: String,
    val sets: Int,
    val weight: Int,
    val totalReps: Int,
    val volume: Int,
    val duration: Int,
    val calories: Float,
    val progression: String,
    val performance: String
)

@Composable
fun RealisticStatsCard(
    title: String,
    value: String,
    unit: String,
    icon: String,
    change: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = icon,
                fontSize = 24.sp
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = title,
                fontSize = 12.sp,
                color = Color.Gray,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = value,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF333333)
            )
            Text(
                text = unit,
                fontSize = 12.sp,
                color = Color.Gray
            )
            Text(
                text = change,
                fontSize = 10.sp,
                color = Color(0xFFFF6B35),
                fontWeight = FontWeight.Medium
            )
        }
    }
}

@Composable
fun DetailedExerciseCard(exercise: ExerciseDetail) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = exercise.name,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "${exercise.sets} séries • ${exercise.weight}kg • ${exercise.totalReps} reps total",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = exercise.performance,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = exercise.progression,
                        fontSize = 12.sp,
                        color = Color(0xFFFF6B35)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                MetricChip("${exercise.weight}kg", "Poids")
                MetricChip("${exercise.duration}min", "Durée")
                MetricChip("${exercise.calories.toInt()}", "kcal")
            }
        }
    }
}

@Composable
fun MetricChip(value: String, label: String) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFFF5F5F5)
        )
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = value,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
            Text(
                text = label,
                fontSize = 10.sp,
                color = Color.Gray
            )
        }
    }
}

@Composable
fun BasicFitAppTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Color(0xFFFF6B35),
            secondary = Color(0xFF2C2C2C)
        ),
        content = content
    )
}

@Composable
fun LoginScreen(navController: NavController, onAuthenticated: (Boolean) -> Unit = {}) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        // Logo et titre
        Icon(
            Icons.Filled.FitnessCenter,
            contentDescription = "BasicFit",
            modifier = Modifier.size(80.dp),
            tint = Color(0xFFFF6B35)
        )

        Text(
            text = "BasicFit v2",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35),
            modifier = Modifier.padding(vertical = 16.dp)
        )

        Text(
            text = "Connectez-vous à votre compte",
            fontSize = 16.sp,
            color = Color.Gray,
            modifier = Modifier.padding(bottom = 32.dp)
        )

        // Champs de saisie
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            singleLine = true
        )

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Mot de passe") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp),
            visualTransformation = PasswordVisualTransformation(),
            singleLine = true
        )

        // Message d'erreur
        if (errorMessage.isNotEmpty()) {
            Text(
                text = errorMessage,
                color = Color.Red,
                fontSize = 14.sp,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        // Bouton de connexion
        Button(
            onClick = {
                isLoading = true
                errorMessage = ""
                // Simulation de connexion réussie
                onAuthenticated(true)
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFFF6B35)
            ),
            enabled = !isLoading && email.isNotEmpty() && password.isNotEmpty()
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    color = Color.White,
                    modifier = Modifier.size(20.dp)
                )
            } else {
                Text("Se connecter", fontSize = 16.sp)
            }
        }

        // Connexion rapide pour démo
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFF5F5F5)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "🚀 Connexion rapide (démo)",
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35),
                    modifier = Modifier.padding(bottom = 12.dp)
                )

                Button(
                    onClick = {
                        email = "admin@basicfit.com"
                        password = "admin123"
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF2C2C2C)
                    ),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("👨‍💼 Admin")
                }
            }
        }

        // Lien vers l'inscription
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(top = 24.dp)
        ) {
            Text("Pas encore de compte ? ", color = Color.Gray)
            TextButton(
                onClick = { navController.navigate("register") }
            ) {
                Text(
                    "S'inscrire",
                    color = Color(0xFFFF6B35),
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun RegisterScreen(navController: NavController, onAuthenticated: (Boolean) -> Unit = {}) {
    var email by remember { mutableStateOf("") }
    var prenom by remember { mutableStateOf("") }
    var nom by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(
                    Icons.Filled.PersonAdd,
                    contentDescription = "Inscription",
                    modifier = Modifier.size(60.dp),
                    tint = Color(0xFFFF6B35)
                )

                Text(
                    text = "Créer un compte",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFFFF6B35),
                    modifier = Modifier.padding(vertical = 16.dp)
                )
            }
        }

        item {
            OutlinedTextField(
                value = prenom,
                onValueChange = { prenom = it },
                label = { Text("Prénom") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
        }

        item {
            OutlinedTextField(
                value = nom,
                onValueChange = { nom = it },
                label = { Text("Nom") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
        }

        item {
            OutlinedTextField(
                value = email,
                onValueChange = { email = it },
                label = { Text("Email") },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                singleLine = true
            )
        }

        item {
            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("Mot de passe") },
                modifier = Modifier.fillMaxWidth(),
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                supportingText = { Text("Minimum 8 caractères", fontSize = 12.sp) }
            )
        }

        item {
            OutlinedTextField(
                value = confirmPassword,
                onValueChange = { confirmPassword = it },
                label = { Text("Confirmer le mot de passe") },
                modifier = Modifier.fillMaxWidth(),
                visualTransformation = PasswordVisualTransformation(),
                singleLine = true,
                isError = password.isNotEmpty() && confirmPassword.isNotEmpty() && password != confirmPassword,
                supportingText = {
                    if (password.isNotEmpty() && confirmPassword.isNotEmpty() && password != confirmPassword) {
                        Text("Les mots de passe ne correspondent pas", color = Color.Red, fontSize = 12.sp)
                    }
                }
            )
        }

        if (errorMessage.isNotEmpty()) {
            item {
                Text(
                    text = errorMessage,
                    color = Color.Red,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }
        }

        item {
            Button(
                onClick = {
                    isLoading = true
                    errorMessage = ""
                    // Simulation d'inscription réussie
                    onAuthenticated(true)
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFFFF6B35)
                ),
                enabled = !isLoading &&
                         email.isNotEmpty() &&
                         prenom.isNotEmpty() &&
                         nom.isNotEmpty() &&
                         password.length >= 8 &&
                         password == confirmPassword
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        color = Color.White,
                        modifier = Modifier.size(20.dp)
                    )
                } else {
                    Text("Créer mon compte", fontSize = 16.sp)
                }
            }
        }

        item {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Déjà un compte ? ", color = Color.Gray)
                TextButton(
                    onClick = { navController.navigate("login") }
                ) {
                    Text(
                        "Se connecter",
                        color = Color(0xFFFF6B35),
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        item {
            // Avantages de l'inscription
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFF5F5F5)
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(
                        text = "🎯 Avec votre compte :",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF6B35),
                        modifier = Modifier.padding(bottom = 12.dp)
                    )

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 4.dp)
                    ) {
                        Text("📊", fontSize = 20.sp, modifier = Modifier.padding(end = 8.dp))
                        Text("Suivi personnalisé de vos performances")
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 4.dp)
                    ) {
                        Text("🏋️", fontSize = 20.sp, modifier = Modifier.padding(end = 8.dp))
                        Text("Entraînements adaptatifs basés sur votre 1RM")
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier.padding(vertical = 4.dp)
                    ) {
                        Text("⏱️", fontSize = 20.sp, modifier = Modifier.padding(end = 8.dp))
                        Text("Timer de repos intelligent")
                    }
                }
            }
        }
    }
}

@Composable
fun WorkoutHistoryScreen(navController: NavController) {
    val context = LocalContext.current

    // Charger l'historique depuis le stockage local
    val workoutHistory = remember {
        mutableStateOf(DataManager.loadWorkoutHistory(context))
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header avec bouton retour
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.padding(bottom = 16.dp)
        ) {
            IconButton(
                onClick = { navController.popBackStack() }
            ) {
                Icon(
                    Icons.Filled.ArrowBack,
                    contentDescription = "Retour",
                    tint = Color(0xFFFF6B35)
                )
            }
            Text(
                text = "Historique des séances",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFFFF6B35)
            )
        }

        // Statistiques globales
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color(0xFFF8F9FA)
            )
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem("${workoutHistory.value.size}", "Séances")
                StatItem("${workoutHistory.value.sumOf { it.duration }}", "Min total")
                StatItem("${workoutHistory.value.sumOf { it.calories }}", "Calories")
                StatItem("${workoutHistory.value.count { it.performance == "Excellent" }}", "Excellentes")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Liste des séances
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(workoutHistory.value) { session ->
                WorkoutSessionCard(session)
            }
        }
    }
}

@Composable
fun StatItem(value: String, label: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFFFF6B35)
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = Color.Gray
        )
    }
}

@Composable
fun WorkoutSessionCard(session: WorkoutSession) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Header de la séance
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = session.date,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    val performanceIcon = when (session.performance) {
                        "Excellent" -> "🔥"
                        "Très bien" -> "💪"
                        "Bien" -> "✅"
                        else -> "⚠️"
                    }
                    Text(
                        text = performanceIcon,
                        fontSize = 16.sp,
                        modifier = Modifier.padding(end = 4.dp)
                    )
                    Text(
                        text = session.performance,
                        fontSize = 14.sp,
                        color = when (session.performance) {
                            "Excellent" -> Color(0xFFFF6B35)
                            "Très bien" -> Color(0xFF4CAF50)
                            "Bien" -> Color(0xFF2196F3)
                            else -> Color.Gray
                        },
                        fontWeight = FontWeight.Medium
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Métriques de la séance
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("⏱️ ${session.duration} min", fontSize = 12.sp, color = Color.Gray)
                Text("🔥 ${session.calories} kcal", fontSize = 12.sp, color = Color.Gray)
                Text("💪 ${session.totalWeight}kg", fontSize = 12.sp, color = Color.Gray)
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Exercices réalisés
            Text(
                text = "Exercices: ${session.exercises.joinToString(", ")}",
                fontSize = 12.sp,
                color = Color.Gray,
                maxLines = 2
            )
        }
    }
}

// Data class pour représenter une séance d'entraînement
data class WorkoutSession(
    val date: String,
    val duration: Int,
    val exercises: List<String>,
    val calories: Int,
    val totalWeight: Int,
    val performance: String
)

@Preview(showBackground = true)
@Composable
fun BasicFitAppPreview() {
    BasicFitAppTheme {
        BasicFitApp()
    }
}