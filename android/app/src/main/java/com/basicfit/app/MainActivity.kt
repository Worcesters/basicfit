package com.basicfit.app

import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.view.WindowCompat
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.foundation.layout.navigationBarsPadding
import com.basicfit.app.data.api.NetworkConfig
import com.basicfit.app.data.models.User
import com.basicfit.app.di.AppModule
import com.basicfit.app.presentation.auth.AuthScreen
import com.basicfit.app.presentation.profile.ProfileScreen
import com.basicfit.app.presentation.machines.MachineScreen
import com.basicfit.app.presentation.training.TrainingScreen
import com.basicfit.app.presentation.calendar.CalendarScreen
import com.basicfit.app.presentation.log.LogScreen
import com.basicfit.app.presentation.theme.*
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var logger: Logger

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Configuration de la fenêtre
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.statusBarColor = LightBackground.copy(alpha = 0.95f).value.toInt()

        // Initialisation des dépendances
        sharedPreferences = getSharedPreferences("basicfit_prefs", Context.MODE_PRIVATE)
        logger = Logger()

        // Configuration réseau et injection de dépendances
        val apiService = NetworkConfig.createApiService(sharedPreferences, logger)
        AppModule.initialize(apiService)

        logger.info("APP", "Application BasicFit v2 démarrée")

        setContent {
            BasicFitApp(
                sharedPreferences = sharedPreferences,
                logger = logger
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BasicFitApp(
    sharedPreferences: SharedPreferences,
    logger: Logger
) {
    // État global de l'application
    var currentUser by remember { mutableStateOf<User?>(null) }
    var isAuthenticated by remember { mutableStateOf(false) }
    var selectedTab by remember { mutableStateOf(0) }
    var isLoading by remember { mutableStateOf(true) }

    val scope = rememberCoroutineScope()

    // Vérification de l'authentification au démarrage
    LaunchedEffect(Unit) {
        scope.launch {
            val token = sharedPreferences.getString("auth_token", null)
            if (token != null) {
                try {
                    // Tenter de récupérer le profil utilisateur
                    val profileResult = AppModule.authRepository.getCurrentUser()
                    if (profileResult.isSuccess) {
                        currentUser = profileResult.getOrNull()
                        isAuthenticated = true
                        logger.success("AUTH", "Utilisateur authentifié automatiquement")
                    } else {
                        // Token invalide, effacer
                        sharedPreferences.edit().clear().apply()
                        logger.info("AUTH", "Token expiré, connexion requise")
                    }
                } catch (e: Exception) {
                    logger.error("AUTH", "Erreur vérification auth", exception = e)
                }
            }
            isLoading = false
        }
    }

    MaterialTheme {
        if (isLoading) {
            // Écran de chargement
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    CircularProgressIndicator(
                        color = Mint,
                        modifier = Modifier.size(48.dp)
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Text(
                        text = "BasicFit",
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Bold,
                        color = Mint
                    )

                    Text(
                        text = "Chargement...",
                        color = TextSecondary
                    )
                }
            }
        } else if (!isAuthenticated) {
            // Écran d'authentification
            AuthScreen(
                onAuthSuccess = { user ->
                    currentUser = user
                    isAuthenticated = true
                    logger.success("AUTH", "Connexion réussie pour ${user.email}")
                },
                logger = logger
            )
        } else {
            // Interface principale avec onglets
            MainAppInterface(
                currentUser = currentUser,
                selectedTab = selectedTab,
                onTabSelected = { selectedTab = it },
                onLogout = {
                    scope.launch {
                        AppModule.authRepository.logout()
                        currentUser = null
                        isAuthenticated = false
                        selectedTab = 0
                        logger.info("AUTH", "Déconnexion utilisateur")
                    }
                },
                logger = logger
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainAppInterface(
    currentUser: User?,
    selectedTab: Int,
    onTabSelected: (Int) -> Unit,
    onLogout: () -> Unit,
    logger: Logger
) {
    Scaffold(
        bottomBar = {
            BottomNavigationBar(
                selectedTab = selectedTab,
                onTabSelected = onTabSelected
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (selectedTab) {
                0 -> ProfileScreen(
                    viewModel = AppModule.provideProfileViewModel()
                )
                1 -> MachineScreen(
                    viewModel = AppModule.provideMachineViewModel()
                )
                2 -> TrainingScreen(
                    viewModel = AppModule.provideTrainingViewModel(),
                    logger = logger
                )
                3 -> CalendarScreen(
                    viewModel = AppModule.provideCalendarViewModel(),
                    logger = logger
                )
                4 -> LogScreen(
                    viewModel = AppModule.provideLogViewModel(),
                    logger = logger
                )
            }
        }
    }
}

@Composable
fun BottomNavigationBar(
    selectedTab: Int,
    onTabSelected: (Int) -> Unit
) {
    NavigationBar(
        containerColor = Color.White,
        modifier = Modifier.navigationBarsPadding()
    ) {
        BottomNavItem(
            selected = selectedTab == 0,
            onClick = { onTabSelected(0) },
            icon = Icons.Default.Person,
            label = "Profil"
        )

        BottomNavItem(
            selected = selectedTab == 1,
            onClick = { onTabSelected(1) },
            icon = Icons.Default.FitnessCenter,
            label = "Machines"
        )

        BottomNavItem(
            selected = selectedTab == 2,
            onClick = { onTabSelected(2) },
            icon = Icons.Default.SportsMma,
            label = "Entraînement"
        )

        BottomNavItem(
            selected = selectedTab == 3,
            onClick = { onTabSelected(3) },
            icon = Icons.Default.CalendarMonth,
            label = "Calendrier"
        )

        BottomNavItem(
            selected = selectedTab == 4,
            onClick = { onTabSelected(4) },
            icon = Icons.Default.BugReport,
            label = "Log"
        )
    }
}

@Composable
fun RowScope.BottomNavItem(
    selected: Boolean,
    onClick: () -> Unit,
    icon: ImageVector,
    label: String
) {
    NavigationBarItem(
        selected = selected,
        onClick = onClick,
        icon = {
            Icon(
                icon,
                contentDescription = label,
                tint = if (selected) Mint else TextSecondary
            )
        },
        label = {
            Text(
                text = label,
                color = if (selected) Mint else TextSecondary,
                fontSize = 12.sp,
                fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
            )
        },
        colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Mint,
            selectedTextColor = Mint,
            unselectedIconColor = TextSecondary,
            unselectedTextColor = TextSecondary,
            indicatorColor = Mint.copy(alpha = 0.1f)
        )
    )
}