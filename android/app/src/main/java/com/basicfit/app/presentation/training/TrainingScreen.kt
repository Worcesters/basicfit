package com.basicfit.app.presentation.training

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.basicfit.app.data.models.*
import com.basicfit.app.presentation.theme.*
import com.basicfit.app.utils.Logger

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrainingScreen(
    viewModel: TrainingViewModel = viewModel(),
    logger: Logger
) {
    val currentScreen by viewModel.currentScreen.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val successMessage by viewModel.successMessage.collectAsState()
    
    // Gestion des messages
    LaunchedEffect(errorMessage) {
        errorMessage?.let {
            logger.error("TRAINING_UI", it)
        }
    }
    
    LaunchedEffect(successMessage) {
        successMessage?.let {
            logger.success("TRAINING_UI", it)
        }
    }
    
    // Interface selon l'écran actuel
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(LightBackground, AccentLight)
                )
            )
    ) {
        // Messages de status
        errorMessage?.let { message ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = ErrorRed.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = message,
                    color = ErrorRed,
                    modifier = Modifier.padding(16.dp),
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
        
        successMessage?.let { message ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = SuccessGreen.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = message,
                    color = SuccessGreen,
                    modifier = Modifier.padding(16.dp),
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
        
        // Contenu principal
        when (currentScreen) {
            TrainingScreen.MACHINE_SELECTION -> {
                MachineSelectionScreen(viewModel = viewModel, isLoading = isLoading)
            }
            TrainingScreen.WORKOUT_IN_PROGRESS -> {
                WorkoutInProgressScreen(viewModel = viewModel)
            }
            TrainingScreen.WORKOUT_COMPLETED -> {
                WorkoutCompletedScreen(viewModel = viewModel)
            }
        }
    }
    
    // Effacer les messages après affichage
    LaunchedEffect(errorMessage, successMessage) {
        if (errorMessage != null || successMessage != null) {
            kotlinx.coroutines.delay(3000)
            viewModel.clearMessages()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MachineSelectionScreen(
    viewModel: TrainingViewModel,
    isLoading: Boolean
) {
    val machines by viewModel.filteredMachines.collectAsState()
    val selectedMachines by viewModel.selectedMachines.collectAsState()
    val workoutName by viewModel.workoutName.collectAsState()
    val trainingMode by viewModel.trainingMode.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()
    val recommendations by viewModel.recommendations.collectAsState()
    
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // En-tête de sélection
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White
                )
            ) {
                Column(
                    modifier = Modifier.padding(20.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Créer un entraînement",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        
                        IconButton(
                            onClick = { viewModel.loadMachines() }
                        ) {
                            Icon(
                                Icons.Default.Refresh,
                                contentDescription = "Rafraîchir",
                                tint = Mint
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Nom de l'entraînement
                    OutlinedTextField(
                        value = workoutName,
                        onValueChange = { viewModel.setWorkoutName(it) },
                        label = { Text("Nom de la séance") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Mode d'entraînement
                    Text(
                        text = "Mode d'entraînement",
                        fontWeight = FontWeight.SemiBold,
                        color = TextPrimary
                    )
                    
                    val modes = listOf("PRISE_MASSE", "SECHE", "FORCE", "ENDURANCE")
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        modes.forEach { mode ->
                            FilterChip(
                                onClick = { viewModel.setTrainingMode(mode) },
                                label = { 
                                    Text(
                                        text = mode.replace("_", " "),
                                        fontSize = 12.sp
                                    ) 
                                },
                                selected = trainingMode == mode,
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = Mint,
                                    selectedLabelColor = Color.White
                                )
                            )
                        }
                    }
                }
            }
        }
        
        // Barre de recherche
        item {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { viewModel.updateMachineSearch(it) },
                label = { Text("Rechercher une machine") },
                leadingIcon = {
                    Icon(Icons.Default.Search, contentDescription = null)
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(
                            onClick = { viewModel.updateMachineSearch("") }
                        ) {
                            Icon(Icons.Default.Clear, contentDescription = "Effacer")
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Mint,
                    focusedLabelColor = Mint
                )
            )
        }
        
        // Machines sélectionnées
        if (selectedMachines.isNotEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = Mint.copy(alpha = 0.1f)
                    )
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
                                text = "Machines sélectionnées (${selectedMachines.size}/10)",
                                fontWeight = FontWeight.SemiBold,
                                color = TextPrimary
                            )
                            
                            TextButton(
                                onClick = { viewModel.clearMachineSelection() }
                            ) {
                                Text("Effacer tout", color = ErrorRed)
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        selectedMachines.forEach { machine ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { viewModel.toggleMachineSelection(machine) },
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = machine.nom,
                                    color = TextPrimary
                                )
                                
                                Icon(
                                    Icons.Default.Check,
                                    contentDescription = "Sélectionnée",
                                    tint = SuccessGreen
                                )
                            }
                        }
                        
                        if (selectedMachines.isNotEmpty()) {
                            Spacer(modifier = Modifier.height(16.dp))
                            
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Button(
                                    onClick = { viewModel.loadIntelligentRecommendations() },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = SoftBlue
                                    ),
                                    enabled = !isLoading
                                ) {
                                    if (isLoading) {
                                        CircularProgressIndicator(
                                            modifier = Modifier.size(16.dp),
                                            color = Color.White
                                        )
                                    } else {
                                        Icon(Icons.Default.Psychology, contentDescription = null)
                                    }
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("Recommandations")
                                }
                                
                                Button(
                                    onClick = { viewModel.startWorkout() },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(
                                        containerColor = Mint
                                    ),
                                    enabled = workoutName.isNotBlank() && !isLoading
                                ) {
                                    Icon(Icons.Default.PlayArrow, contentDescription = null)
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("Démarrer")
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Liste des machines disponibles
        items(machines) { machine ->
            MachineSelectionCard(
                machine = machine,
                isSelected = selectedMachines.contains(machine),
                onSelectionChange = { viewModel.toggleMachineSelection(machine) }
            )
        }
        
        if (machines.isEmpty() && searchQuery.isNotEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            Icons.Default.SearchOff,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = TextSecondary
                        )
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Text(
                            text = "Aucune machine trouvée",
                            fontWeight = FontWeight.SemiBold,
                            color = TextSecondary
                        )
                        
                        Text(
                            text = "Essayez avec d'autres mots-clés",
                            color = TextSecondary
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MachineSelectionCard(
    machine: Machine,
    isSelected: Boolean,
    onSelectionChange: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onSelectionChange() },
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) Mint.copy(alpha = 0.1f) else Color.White
        ),
        border = if (isSelected) {
            androidx.compose.foundation.BorderStroke(2.dp, Mint)
        } else null
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = machine.nom,
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary,
                    fontSize = 16.sp
                )
                
                Text(
                    text = machine.description,
                    color = TextSecondary,
                    fontSize = 14.sp
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Text(
                    text = machine.groupeMusculaire,
                    color = Mint,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium
                )
            }
            
            if (isSelected) {
                Icon(
                    Icons.Default.CheckCircle,
                    contentDescription = "Sélectionnée",
                    tint = Mint,
                    modifier = Modifier.size(24.dp)
                )
            } else {
                Icon(
                    Icons.Default.AddCircleOutline,
                    contentDescription = "Ajouter",
                    tint = TextSecondary,
                    modifier = Modifier.size(24.dp)
                )
            }
        }
    }
}

@Composable
fun WorkoutInProgressScreen(
    viewModel: TrainingViewModel
) {
    val activeWorkout by viewModel.activeWorkout.collectAsState()
    
    activeWorkout?.let { workout ->
        val currentExercise = workout.getCurrentExercise()
        val progress = viewModel.getWorkoutProgress()
        
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                WorkoutProgressCard(
                    workoutName = workout.workoutName,
                    progress = progress,
                    duration = workout.getDurationMinutes(),
                    currentExercise = "${workout.currentExerciseIndex + 1}/${workout.exercises.size}"
                )
            }
            
            currentExercise?.let { exercise ->
                item {
                    CurrentExerciseCard(
                        exercise = exercise,
                        onCompleteSet = { weight, reps, rest ->
                            viewModel.completeSet(weight, reps, rest)
                        }
                    )
                }
            }
            
            item {
                WorkoutControlsCard(
                    onPreviousExercise = { viewModel.moveToPreviousExercise() },
                    onNextExercise = { viewModel.moveToNextExercise() },
                    onCompleteWorkout = { viewModel.completeWorkout() },
                    onCancelWorkout = { viewModel.cancelWorkout() },
                    canGoPrevious = workout.currentExerciseIndex > 0,
                    canGoNext = workout.currentExerciseIndex < workout.exercises.size - 1
                )
            }
        }
    }
}

@Composable
fun WorkoutProgressCard(
    workoutName: String,
    progress: Float,
    duration: Int,
    currentExercise: String
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = workoutName,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            LinearProgressIndicator(
                progress = progress,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp),
                color = Mint,
                trackColor = AccentLight
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Exercice $currentExercise",
                    color = TextSecondary,
                    fontWeight = FontWeight.Medium
                )
                
                Text(
                    text = "${duration}min",
                    color = TextSecondary,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CurrentExerciseCard(
    exercise: ActiveExercise,
    onCompleteSet: (Double, Int, Int) -> Unit
) {
    var weight by remember { mutableStateOf(exercise.recommendation.poidsRecommande.toString()) }
    var reps by remember { mutableStateOf(exercise.recommendation.repetitionsRecommandees.toString()) }
    var rest by remember { mutableStateOf(exercise.recommendation.reposRecommande.toString()) }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (exercise.isCompleted) SuccessGreen.copy(alpha = 0.1f) else Color.White
        )
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = exercise.machine.nom,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                
                if (exercise.isCompleted) {
                    Icon(
                        Icons.Default.CheckCircle,
                        contentDescription = "Terminé",
                        tint = SuccessGreen,
                        modifier = Modifier.size(24.dp)
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Série ${exercise.currentSetIndex + 1}/${exercise.recommendation.seriesRecommandees}",
                color = TextSecondary,
                fontWeight = FontWeight.Medium
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (!exercise.isCompleted) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedTextField(
                        value = weight,
                        onValueChange = { weight = it },
                        label = { Text("Poids (kg)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                        modifier = Modifier.weight(1f),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )
                    
                    OutlinedTextField(
                        value = reps,
                        onValueChange = { reps = it },
                        label = { Text("Répétitions") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.weight(1f),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )
                    
                    OutlinedTextField(
                        value = rest,
                        onValueChange = { rest = it },
                        label = { Text("Repos (s)") },
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        modifier = Modifier.weight(1f),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Button(
                    onClick = {
                        val weightValue = weight.toDoubleOrNull() ?: exercise.recommendation.poidsRecommande
                        val repsValue = reps.toIntOrNull() ?: exercise.recommendation.repetitionsRecommandees
                        val restValue = rest.toIntOrNull() ?: exercise.recommendation.reposRecommande
                        onCompleteSet(weightValue, repsValue, restValue)
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    )
                ) {
                    Icon(Icons.Default.Check, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Valider la série")
                }
            }
            
            // Historique des séries
            if (exercise.completedSets.isNotEmpty()) {
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Séries effectuées:",
                    fontWeight = FontWeight.SemiBold,
                    color = TextPrimary
                )
                
                exercise.completedSets.forEachIndexed { index, set ->
                    Text(
                        text = "Série ${index + 1}: ${set.weight}kg × ${set.reps} (${set.restTime}s repos)",
                        color = TextSecondary,
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}

@Composable
fun WorkoutControlsCard(
    onPreviousExercise: () -> Unit,
    onNextExercise: () -> Unit,
    onCompleteWorkout: () -> Unit,
    onCancelWorkout: () -> Unit,
    canGoPrevious: Boolean,
    canGoNext: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Contrôles",
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = onPreviousExercise,
                    enabled = canGoPrevious,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = SoftBlue
                    )
                ) {
                    Icon(Icons.Default.ArrowBack, contentDescription = null)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Précédent")
                }
                
                Button(
                    onClick = onNextExercise,
                    enabled = canGoNext,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = SoftBlue
                    )
                ) {
                    Text("Suivant")
                    Spacer(modifier = Modifier.width(4.dp))
                    Icon(Icons.Default.ArrowForward, contentDescription = null)
                }
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onCancelWorkout,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.Close, contentDescription = null, tint = ErrorRed)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Abandonner", color = ErrorRed)
                }
                
                Button(
                    onClick = onCompleteWorkout,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = SuccessGreen
                    )
                ) {
                    Icon(Icons.Default.Save, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Terminer")
                }
            }
        }
    }
}

@Composable
fun WorkoutCompletedScreen(
    viewModel: TrainingViewModel
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = SuccessGreen.copy(alpha = 0.1f)
            )
        ) {
            Column(
                modifier = Modifier.padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Icon(
                    Icons.Default.EmojiEvents,
                    contentDescription = null,
                    modifier = Modifier.size(64.dp),
                    tint = SuccessGreen
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                Text(
                    text = "Séance terminée !",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Félicitations pour avoir terminé votre entraînement",
                    color = TextSecondary,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                Button(
                    onClick = { viewModel.startNewWorkout() },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    )
                ) {
                    Icon(Icons.Default.Add, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Nouvelle séance")
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                OutlinedButton(
                    onClick = { viewModel.backToMachineSelection() },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Retour à l'accueil")
                }
            }
        }
    }
}