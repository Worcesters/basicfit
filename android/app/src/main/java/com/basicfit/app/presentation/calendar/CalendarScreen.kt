package com.basicfit.app.presentation.calendar

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.basicfit.app.data.models.WorkoutSession
import com.basicfit.app.data.repositories.CalendarStats
import com.basicfit.app.presentation.theme.*
import com.basicfit.app.utils.Logger
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.TextStyle
import java.util.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CalendarScreen(
    viewModel: CalendarViewModel = viewModel(),
    logger: Logger
) {
    val currentView by viewModel.currentView.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val successMessage by viewModel.successMessage.collectAsState()

    // Gestion des messages
    LaunchedEffect(errorMessage) {
        errorMessage?.let {
            logger.error("CALENDAR_UI", it)
        }
    }

    LaunchedEffect(successMessage) {
        successMessage?.let {
            logger.success("CALENDAR_UI", it)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(LightBackground, AccentLight)
                )
            )
    ) {
        // Barre de navigation des vues
        ViewNavigationBar(
            currentView = currentView,
            onViewChange = { viewModel.setView(it) }
        )

        // Messages de status
        errorMessage?.let { message ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
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
                    .padding(horizontal = 16.dp, vertical = 8.dp),
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
        when (currentView) {
            CalendarView.CALENDAR -> {
                CalendarViewContent(viewModel = viewModel, isLoading = isLoading)
            }
            CalendarView.HISTORY -> {
                HistoryViewContent(viewModel = viewModel, isLoading = isLoading)
            }
            CalendarView.IMPORT -> {
                ImportViewContent(viewModel = viewModel)
            }
            CalendarView.STATS -> {
                StatsViewContent(viewModel = viewModel)
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

@Composable
fun ViewNavigationBar(
    currentView: CalendarView,
    onViewChange: (CalendarView) -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color.White
        )
    ) {
        Row(
            modifier = Modifier.padding(8.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            ViewButton(
                text = "Calendrier",
                icon = Icons.Default.CalendarMonth,
                isSelected = currentView == CalendarView.CALENDAR,
                onClick = { onViewChange(CalendarView.CALENDAR) }
            )

            ViewButton(
                text = "Historique",
                icon = Icons.Default.History,
                isSelected = currentView == CalendarView.HISTORY,
                onClick = { onViewChange(CalendarView.HISTORY) }
            )

            ViewButton(
                text = "Import",
                icon = Icons.Default.Upload,
                isSelected = currentView == CalendarView.IMPORT,
                onClick = { onViewChange(CalendarView.IMPORT) }
            )

            ViewButton(
                text = "Stats",
                icon = Icons.Default.Analytics,
                isSelected = currentView == CalendarView.STATS,
                onClick = { onViewChange(CalendarView.STATS) }
            )
        }
    }
}

@Composable
fun ViewButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .clickable { onClick() }
            .background(if (isSelected) Mint.copy(alpha = 0.1f) else Color.Transparent)
            .padding(12.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            icon,
            contentDescription = text,
            tint = if (isSelected) Mint else TextSecondary,
            modifier = Modifier.size(20.dp)
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = text,
            color = if (isSelected) Mint else TextSecondary,
            fontSize = 12.sp,
            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
        )
    }
}

@Composable
fun CalendarViewContent(
    viewModel: CalendarViewModel,
    isLoading: Boolean
) {
    val currentMonth by viewModel.currentMonth.collectAsState()
    val datesWithWorkouts by viewModel.datesWithWorkouts.collectAsState()
    val selectedDate by viewModel.selectedDate.collectAsState()
    val selectedWorkouts by viewModel.selectedWorkouts.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // En-tête du calendrier
        item {
            CalendarHeader(
                currentMonth = currentMonth,
                onPreviousMonth = { viewModel.previousMonth() },
                onNextMonth = { viewModel.nextMonth() },
                onGoToToday = { viewModel.goToCurrentMonth() }
            )
        }

        // Grille du calendrier
        item {
            CalendarGrid(
                currentMonth = currentMonth,
                datesWithWorkouts = datesWithWorkouts,
                selectedDate = selectedDate,
                onDateSelect = { date ->
                    if (selectedDate == date) {
                        viewModel.clearSelectedDate()
                    } else {
                        viewModel.selectDate(date)
                    }
                }
            )
        }

        // Séances de la date sélectionnée
        if (selectedDate != null && selectedWorkouts.isNotEmpty()) {
            item {
                SelectedDateWorkouts(
                    date = selectedDate!!,
                    workouts = selectedWorkouts,
                    onDeleteWorkout = { workoutId -> viewModel.deleteWorkout(workoutId) }
                )
            }
        }

        if (isLoading) {
            item {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Mint)
                }
            }
        }
    }
}

@Composable
fun CalendarHeader(
    currentMonth: LocalDate,
    onPreviousMonth: () -> Unit,
    onNextMonth: () -> Unit,
    onGoToToday: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onPreviousMonth) {
                Icon(
                    Icons.Default.ArrowBack,
                    contentDescription = "Mois précédent",
                    tint = Mint
                )
            }

            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = currentMonth.month.getDisplayName(TextStyle.FULL, Locale.FRENCH),
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )

                Text(
                    text = currentMonth.year.toString(),
                    fontSize = 16.sp,
                    color = TextSecondary
                )
            }

            IconButton(onClick = onNextMonth) {
                Icon(
                    Icons.Default.ArrowForward,
                    contentDescription = "Mois suivant",
                    tint = Mint
                )
            }
        }

        // Bouton retour aujourd'hui
        if (currentMonth != LocalDate.now().withDayOfMonth(1)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.Center
            ) {
                TextButton(onClick = onGoToToday) {
                    Icon(
                        Icons.Default.Today,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Aujourd'hui", color = Mint)
                }
            }
        }
    }
}

@Composable
fun CalendarGrid(
    currentMonth: LocalDate,
    datesWithWorkouts: Set<LocalDate>,
    selectedDate: LocalDate?,
    onDateSelect: (LocalDate) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Jours de la semaine
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                listOf("L", "M", "M", "J", "V", "S", "D").forEach { day ->
                    Text(
                        text = day,
                        fontWeight = FontWeight.SemiBold,
                        color = TextSecondary,
                        modifier = Modifier.weight(1f),
                        textAlign = TextAlign.Center
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Grille des dates
            val firstDayOfMonth = currentMonth.withDayOfMonth(1)
            val daysInMonth = currentMonth.lengthOfMonth()
            val startDayOfWeek = firstDayOfMonth.dayOfWeek.value - 1 // Lundi = 0

            LazyVerticalGrid(
                columns = GridCells.Fixed(7),
                modifier = Modifier.height(300.dp)
            ) {
                // Espaces vides au début
                items(startDayOfWeek) {
                    Spacer(modifier = Modifier.aspectRatio(1f))
                }

                // Jours du mois
                items(daysInMonth) { day ->
                    val date = currentMonth.withDayOfMonth(day + 1)
                    val hasWorkout = datesWithWorkouts.contains(date)
                    val isSelected = selectedDate == date
                    val isToday = date == LocalDate.now()

                    CalendarDayCell(
                        day = day + 1,
                        hasWorkout = hasWorkout,
                        isSelected = isSelected,
                        isToday = isToday,
                        onClick = { onDateSelect(date) }
                    )
                }
            }
        }
    }
}

@Composable
fun CalendarDayCell(
    day: Int,
    hasWorkout: Boolean,
    isSelected: Boolean,
    isToday: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .aspectRatio(1f)
            .padding(2.dp)
            .clip(CircleShape)
            .background(
                when {
                    isSelected -> Mint
                    isToday -> SoftBlue.copy(alpha = 0.3f)
                    hasWorkout -> Mint.copy(alpha = 0.2f)
                    else -> Color.Transparent
                }
            )
            .clickable { onClick() },
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = day.toString(),
            color = when {
                isSelected -> Color.White
                isToday -> TextPrimary
                hasWorkout -> Mint
                else -> TextPrimary
            },
            fontWeight = if (hasWorkout || isSelected || isToday) FontWeight.Bold else FontWeight.Normal,
            fontSize = 14.sp
        )

        // Indicateur de séance
        if (hasWorkout && !isSelected) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(Mint)
                    .align(Alignment.BottomCenter)
                    .offset(y = (-4).dp)
            )
        }
    }
}

@Composable
fun SelectedDateWorkouts(
    date: LocalDate,
    workouts: List<WorkoutSession>,
    onDeleteWorkout: (Int) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Séances du ${date.format(DateTimeFormatter.ofPattern("dd MMMM yyyy", Locale.FRENCH))}",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(12.dp))

            workouts.forEach { workout ->
                WorkoutCard(
                    workout = workout,
                    onDelete = { onDeleteWorkout(workout.id) }
                )

                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
fun HistoryViewContent(
    viewModel: CalendarViewModel,
    isLoading: Boolean
) {
    val workoutHistory by viewModel.workoutHistory.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Historique des séances",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )

                IconButton(onClick = { viewModel.refreshData() }) {
                    Icon(
                        Icons.Default.Refresh,
                        contentDescription = "Rafraîchir",
                        tint = Mint
                    )
                }
            }
        }

        if (isLoading) {
            item {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Mint)
                }
            }
        } else if (workoutHistory.isEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            Icons.Default.FitnessCenter,
                            contentDescription = null,
                            modifier = Modifier.size(48.dp),
                            tint = TextSecondary
                        )

                        Spacer(modifier = Modifier.height(16.dp))

                        Text(
                            text = "Aucune séance enregistrée",
                            fontWeight = FontWeight.SemiBold,
                            color = TextSecondary
                        )

                        Text(
                            text = "Commencez votre premier entraînement !",
                            color = TextSecondary
                        )
                    }
                }
            }
        } else {
            items(workoutHistory) { workout ->
                WorkoutCard(
                    workout = workout,
                    onDelete = { viewModel.deleteWorkout(workout.id) }
                )
            }
        }
    }
}

@Composable
fun WorkoutCard(
    workout: WorkoutSession,
    onDelete: () -> Unit
) {
    var showDeleteDialog by remember { mutableStateOf(false) }

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
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = workout.nom,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )

                    Text(
                        text = "${workout.getFormattedDate()} • ${workout.getFormattedDuration()}",
                        color = TextSecondary,
                        fontSize = 14.sp
                    )
                }

                IconButton(onClick = { showDeleteDialog = true }) {
                    Icon(
                        Icons.Default.Delete,
                        contentDescription = "Supprimer",
                        tint = ErrorRed
                    )
                }
            }

            if (workout.exercices.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = "Exercices (${workout.exercices.size}):",
                    fontWeight = FontWeight.Medium,
                    color = TextPrimary,
                    fontSize = 14.sp
                )

                workout.exercices.take(3).forEach { exercise ->
                    Text(
                        text = "• ${exercise.nom} - ${exercise.series}×${exercise.reps} (${exercise.poids}kg)",
                        color = TextSecondary,
                        fontSize = 13.sp
                    )
                }

                if (workout.exercices.size > 3) {
                    Text(
                        text = "... et ${workout.exercices.size - 3} autres",
                        color = TextSecondary,
                        fontSize = 13.sp,
                        fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                    )
                }
            }

            workout.noteRessenti?.let { note ->
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Ressenti: $note/10",
                    color = if (note >= 7) SuccessGreen else if (note >= 5) WarningOrange else ErrorRed,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }
    }

    // Dialog de confirmation de suppression
    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = { Text("Supprimer la séance") },
            text = { Text("Êtes-vous sûr de vouloir supprimer cette séance ? Cette action est irréversible.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        onDelete()
                        showDeleteDialog = false
                    }
                ) {
                    Text("Supprimer", color = ErrorRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) {
                    Text("Annuler")
                }
            }
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImportViewContent(
    viewModel: CalendarViewModel
) {
    val isImporting by viewModel.isImporting.collectAsState()
    var csvContent by remember { mutableStateOf("") }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Import CSV",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
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
                        text = "Format CSV attendu:",
                        fontWeight = FontWeight.SemiBold,
                        color = TextPrimary
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    Text(
                        text = "Date,Nom,Durée,Exercices,Note,Commentaire",
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                        fontSize = 12.sp,
                        color = TextSecondary
                    )
                }
            }
        }

        item {
            OutlinedTextField(
                value = csvContent,
                onValueChange = { csvContent = it },
                label = { Text("Contenu CSV") },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Mint,
                    focusedLabelColor = Mint
                ),
                maxLines = 10
            )
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = { csvContent = "" },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = TextSecondary
                    ),
                    enabled = csvContent.isNotEmpty() && !isImporting
                ) {
                    Icon(Icons.Default.Clear, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Effacer")
                }

                Button(
                    onClick = { viewModel.importCsvData(csvContent) },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    ),
                    enabled = csvContent.isNotEmpty() && !isImporting
                ) {
                    if (isImporting) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(16.dp),
                            color = Color.White
                        )
                    } else {
                        Icon(Icons.Default.Upload, contentDescription = null)
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(if (isImporting) "Import..." else "Importer")
                }
            }
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = WarningOrange.copy(alpha = 0.1f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = WarningOrange
                    )

                    Spacer(modifier = Modifier.width(12.dp))

                    Text(
                        text = "L'import remplacera les données existantes. Assurez-vous d'avoir une sauvegarde.",
                        color = WarningOrange,
                        fontSize = 14.sp
                    )
                }
            }
        }

        item {
            Button(
                onClick = {
                    // Launch in a coroutine scope
                    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Main).launch {
                        viewModel.clearAllSessions()
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = ErrorRed
                ),
                enabled = !isImporting
            ) {
                Icon(Icons.Default.DeleteForever, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Supprimer toutes les séances")
            }
        }
    }
}

@Composable
fun StatsViewContent(
    viewModel: CalendarViewModel
) {
    val stats by viewModel.calendarStats.collectAsState()
    val workoutHistory by viewModel.workoutHistory.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Statistiques",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        }

        item {
            StatsOverviewCard(stats = stats)
        }

        if (workoutHistory.isNotEmpty()) {
            item {
                ExportCard(
                    onExport = { viewModel.exportToCSV() }
                )
            }
        }
    }
}

@Composable
fun StatsOverviewCard(
    stats: CalendarStats
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "Aperçu général",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    value = stats.totalSeances.toString(),
                    label = "Séances totales",
                    icon = Icons.Default.FitnessCenter,
                    color = Mint
                )

                StatItem(
                    value = "${stats.totalMinutes / 60}h${stats.totalMinutes % 60}",
                    label = "Temps total",
                    icon = Icons.Default.Schedule,
                    color = SoftBlue
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    value = "${stats.moyenneDuree}min",
                    label = "Durée moyenne",
                    icon = Icons.Default.Timer,
                    color = SuccessGreen
                )

                StatItem(
                    value = stats.seancesCeMois.toString(),
                    label = "Ce mois",
                    icon = Icons.Default.CalendarToday,
                    color = WarningOrange
                )
            }
        }
    }
}

@Composable
fun StatItem(
    value: String,
    label: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            icon,
            contentDescription = null,
            tint = color,
            modifier = Modifier.size(24.dp)
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = value,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )

        Text(
            text = label,
            fontSize = 12.sp,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun ExportCard(
    onExport: () -> String
) {
    var exportedContent by remember { mutableStateOf<String?>(null) }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Export des données",
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Exportez votre historique au format CSV",
                color = TextSecondary,
                fontSize = 14.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = { exportedContent = onExport() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = SoftBlue
                )
            ) {
                Icon(Icons.Default.Download, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Générer CSV")
            }

            exportedContent?.let { content ->
                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = "Export généré (${content.lines().size - 1} séances)",
                    color = SuccessGreen,
                    fontSize = 12.sp
                )
            }
        }
    }
}