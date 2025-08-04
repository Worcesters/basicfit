package com.basicfit.app

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.platform.LocalContext
import io.github.boguszpawlowski.composecalendar.rememberCalendarState
import io.github.boguszpawlowski.composecalendar.StaticCalendar
import io.github.boguszpawlowski.composecalendar.day.DayState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.time.LocalDate
import java.time.YearMonth
import android.content.Context
import android.widget.Toast
import java.time.format.DateTimeFormatter
import androidx.compose.foundation.border
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.draw.clip
import androidx.compose.foundation.clickable
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions

@Composable
fun CalendarScreen(
    workoutHistory: List<WorkoutEntry>,
    onWorkoutHistoryChange: (List<WorkoutEntry>) -> Unit,
    onCsvImported: (List<WorkoutEntry>) -> Unit,
    onEntryClick: (WorkoutEntry) -> Unit,
    onGoToWorkout: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    // Ajout pour le bouton de vidage du calendrier
    var showClearDialog by remember { mutableStateOf(false) }

    // État pour la synchronisation avec la BDD
    var isLoadingFromDB by remember { mutableStateOf(false) }
    var lastSyncTime by remember { mutableStateOf(0L) }

    // State: mois actuellement affiché
    val currentMonth = remember { YearMonth.now() }
    val calendarState = rememberCalendarState(currentMonth)

    var draggedEntry by remember { mutableStateOf<WorkoutEntry?>(null) }

    // Fonction pour synchroniser avec la BDD
    fun syncWithDatabase() {
        if (isLoadingFromDB) return

        coroutineScope.launch {
            isLoadingFromDB = true
            try {
                val apiService = ApiService.getInstance()
                apiService.initialize(context)

                if (apiService.isApiAvailable()) {
                    val result = apiService.getCalendarHistory()
                    result.onSuccess { dbHistory ->
                        // Fusionner avec l'historique local (priorité aux données DB)
                        val mergedHistory = (workoutHistory + dbHistory)
                            .distinctBy { "${it.date}_${it.mode}_${it.duration}" }
                            .sortedBy { it.date }

                        onWorkoutHistoryChange(mergedHistory)
                        lastSyncTime = System.currentTimeMillis()

                        android.util.Log.d("CalendarSync", "✅ Synchronisation réussie: ${dbHistory.size} séances récupérées de la BDD")
                        Toast.makeText(context, "✅ Calendrier synchronisé avec la base de données", Toast.LENGTH_SHORT).show()
                    }.onFailure { error ->
                        android.util.Log.e("CalendarSync", "❌ Erreur de synchronisation: ${error.message}")
                        Toast.makeText(context, "❌ Erreur de synchronisation avec la BDD", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    android.util.Log.w("CalendarSync", "⚠️ API non disponible")
                    Toast.makeText(context, "⚠️ Serveur non accessible", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                android.util.Log.e("CalendarSync", "❌ Exception lors de la synchronisation: ${e.message}")
                Toast.makeText(context, "❌ Erreur de synchronisation", Toast.LENGTH_SHORT).show()
            } finally {
                isLoadingFromDB = false
            }
        }
    }

    // Synchronisation automatique au démarrage et toutes les 5 minutes
    LaunchedEffect(Unit) {
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastSyncTime > 5 * 60 * 1000) { // 5 minutes
            syncWithDatabase()
        }
    }

    // Launcher CSV (inchangé)
    val csvLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) {
            coroutineScope.launch {
                val imported = parseCsv(context, uri)
                if (imported.isNotEmpty()) {
                    onCsvImported(imported)
                    Toast.makeText(context, "Import réussi : ${imported.size} séances ajoutées", Toast.LENGTH_LONG).show()
                } else {
                    Toast.makeText(context, "Aucune donnée trouvée dans le fichier CSV", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
            .padding(8.dp)
    ) {
        // Header actions
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Start,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Button(
                onClick = { syncWithDatabase() },
                enabled = !isLoadingFromDB,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2196F3))
            ) {
                if (isLoadingFromDB) {
                    Text("🔄 Synchro...", color = Color.White)
                } else {
                    Text("🔄 Sync BDD", color = Color.White)
                }
            }

            Spacer(Modifier.width(8.dp))

            Button(
                onClick = { csvLauncher.launch(arrayOf("text/*", "application/*", "*/*")) },
                colors = ButtonDefaults.buttonColors(containerColor = Accent)
            ) { Text("📂 CSV", color = Color.White) }

            Spacer(Modifier.width(8.dp))

            Button(
                onClick = { showClearDialog = true },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F))
            ) { Text("🗑️ Vider", color = Color.White) }
        }

        Spacer(Modifier.height(8.dp))

        // Calendrier Compose
        LazyColumn(
            modifier = Modifier.fillMaxSize()
        ) {
            item {
                androidx.compose.material3.Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    shape = RoundedCornerShape(8.dp),
                    elevation = CardDefaults.cardElevation(4.dp)
                ) {
                    StaticCalendar(
                        calendarState = calendarState,
                        dayContent = { dayState ->
                            DayCell(
                                dayState = dayState,
                                workoutHistory = workoutHistory,
                                draggedEntry = draggedEntry,
                                onDragStart = { draggedEntry = it },
                                onDropOnDate = { date ->
                                    draggedEntry?.let { entry ->
                                        if (entry.date != date) {
                                            val updated = workoutHistory.map { if (it == entry) it.copy(date = date) else it }
                                            onWorkoutHistoryChange(updated)
                                        }
                                    }
                                    draggedEntry = null
                                },
                                onEntryClick = onEntryClick
                            )
                        }
                    )
                }
            }
        }

        // Pop-up de confirmation
        if (showClearDialog) {
            AlertDialog(
                onDismissRequest = { showClearDialog = false },
                confirmButton = {
                    TextButton(onClick = {
                        // Conserver uniquement les séances complétées
                        val remaining = workoutHistory.filter { it.duration > 0 }
                        onWorkoutHistoryChange(remaining)
                        showClearDialog = false
                    }) {
                        Text("Confirmer", color = Accent)
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showClearDialog = false }) {
                        Text("Annuler")
                    }
                },
                title = { Text("Confirmer la suppression") },
                text = { Text("Voulez-vous vraiment vider le calendrier des séances non terminées ?") }
            )
        }
    }

    // REMOVED: Auto-sync LaunchedEffect that was causing duplicate workouts
    // The synchronization now happens only when completing a workout in MainActivity
    // This prevents re-sending all completed workouts every time the history changes
}

@Composable
private fun DayCell(
    dayState: DayState<*>,
    workoutHistory: List<WorkoutEntry>,
    draggedEntry: WorkoutEntry?,
    onDragStart: (WorkoutEntry) -> Unit,
    onDropOnDate: (LocalDate) -> Unit,
    onEntryClick: (WorkoutEntry) -> Unit
) {
    val date = dayState.date
    val entriesToday = remember(workoutHistory) { workoutHistory.filter { it.date == date } }
    val hasCompleted = entriesToday.any { it.duration > 0 }
    val exercisesToday = remember(entriesToday) { entriesToday.flatMap { it.exercises } }

    val isToday = date == LocalDate.now()
    val isPast = date.isBefore(LocalDate.now())

    // Déterminer la couleur de fond selon le statut
    val backgroundColor = when {
        hasCompleted -> Color(0xFF4CAF50) // Vert pour terminé
        entriesToday.isNotEmpty() && isPast -> Color(0xFFFF5722) // Rouge pour en retard
        entriesToday.isNotEmpty() && !isPast -> Color(0xFFFF9800) // Orange pour à venir
        isToday -> Color(0xFFFFF3E0) // Fond pêche clair pour aujourd'hui
        else -> Color.White // Blanc par défaut
    }

    Box(
        modifier = Modifier
            .aspectRatio(1f)
            .padding(2.dp)
            .background(backgroundColor, RoundedCornerShape(4.dp))
            .then(if (isToday) Modifier.border(2.dp, Accent, RoundedCornerShape(4.dp)) else Modifier)
            .then(
                if (entriesToday.isNotEmpty()) {
                    Modifier.clickable { onEntryClick(entriesToday.first()) }
                } else Modifier
            )
            .pointerInput(entriesToday) {
                detectDragGestures(onDragEnd = {
                    onDropOnDate(date)
                }) { change, _ ->
                    change.consume() // consume events during drag
                }
            },
        contentAlignment = Alignment.TopStart
    ) {

        // Numéro du jour
        Text(
            text = date.dayOfMonth.toString(),
            fontSize = 10.sp,
            modifier = Modifier.padding(2.dp),
            color = if (backgroundColor == Color.White) Color.Black else Color.White
        )

        // Indicateur de statut dans le coin supérieur droit
        if (entriesToday.isNotEmpty()) {
            val statusColor = when {
                hasCompleted -> Color(0xFF2E7D32) // Vert foncé
                isPast -> Color(0xFFD32F2F) // Rouge foncé
                else -> Color(0xFFE65100) // Orange foncé
            }

            Box(
                modifier = Modifier
                    .size(8.dp)
                    .align(Alignment.TopEnd)
                    .padding(2.dp)
                    .background(statusColor, CircleShape)
            )
        }

        // Afficher le nombre d'exercices au centre
        if (exercisesToday.isNotEmpty()) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = exercisesToday.size.toString(),
                    fontSize = 12.sp,
                    color = if (backgroundColor == Color.White) Color.Black else Color.White,
                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                )

                if (exercisesToday.size > 1) {
                    Text(
                        text = "exercices",
                        fontSize = 6.sp,
                        color = if (backgroundColor == Color.White) Color.Black else Color.White
                    )
                }
            }
        }
    }
}

// Removed custom MonthHeader – we now use the default one from ComposeCalendar

// Fonction utilitaire pour parser le CSV et retourner une liste de WorkoutEntry
private suspend fun parseCsv(context: Context, uri: android.net.Uri): List<WorkoutEntry> = withContext(Dispatchers.IO) {
    val entriesByDate = mutableMapOf<LocalDate, MutableList<ExerciseRecord>>()

    context.contentResolver.openInputStream(uri)?.bufferedReader()?.useLines { lines ->
        lines.drop(1).forEach { line ->
            val parts = line.split(';', ',').map { it.trim() }

            // Support des formats : Machine;Date;Type OU Machine;Date;Répétitions;Séries;Poids
            when (parts.size) {
                3 -> {
                    // Format simplifié : Machine;Date;Type
                    val machineName = parts[0]
                    val dateStr = parts[1]
                    val typeStr = parts[2]

                    // Parsing flexible de la date
                    val dateFormats = listOf(
                        DateTimeFormatter.ISO_LOCAL_DATE,
                        DateTimeFormatter.ofPattern("dd/MM/yyyy"),
                        DateTimeFormatter.ofPattern("dd-MM-yyyy")
                    )
                    val parsedDate = dateFormats.firstNotNullOfOrNull { fmt ->
                        runCatching { LocalDate.parse(dateStr, fmt) }.getOrNull()
                    }

                    parsedDate?.let { date ->
                        // Déterminer les valeurs par défaut selon le type
                        val (sets, reps, weight) = when (typeStr.lowercase()) {
                            "cardio", "tapis", "vélo", "rameur" -> Triple(1, 30, 0.0) // 30 min cardio
                            "musculation", "force" -> Triple(3, 10, 50.0) // 3 séries de 10 reps
                            "gainage", "plank", "core" -> Triple(1, 60, 0.0) // 1 min gainage
                            else -> Triple(3, 10, 0.0) // Valeurs par défaut
                        }

                        val record = ExerciseRecord(
                            name = machineName,
                            sets = sets,
                            reps = reps,
                            weight = weight,
                            totalWeight = weight * sets
                        )
                        entriesByDate.getOrPut(date) { mutableListOf() }.add(record)
                    }
                }
                4, 5 -> {
                    // Format étendu : Machine;Date;Répétitions;Séries;Poids(optionnel)
                    val machineName = parts[0]
                    val dateStr = parts[1]
                    val repetitionStr = parts[2]
                    val serieStr = parts[3]
                    val utilisationStr = if (parts.size == 5) parts[4] else "0"

                    val utilisation = utilisationStr.toDoubleOrNull() ?: 0.0

                    // Repetitions : "10-12" -> moyenne, sinon valeur directe
                    val repetition = if (repetitionStr.contains('-')) {
                        val bounds = repetitionStr.split('-').mapNotNull { it.toIntOrNull() }
                        if (bounds.size == 2) ((bounds[0] + bounds[1]) / 2.0).toInt() else 0
                    } else repetitionStr.toIntOrNull() ?: 0

                    val serie = serieStr.toIntOrNull() ?: 0

                    // Parsing flexible de la date
                    val dateFormats = listOf(
                        DateTimeFormatter.ISO_LOCAL_DATE,
                        DateTimeFormatter.ofPattern("dd/MM/yyyy"),
                        DateTimeFormatter.ofPattern("dd-MM-yyyy")
                    )
                    val parsedDate = dateFormats.firstNotNullOfOrNull { fmt ->
                        runCatching { LocalDate.parse(dateStr, fmt) }.getOrNull()
                    }

                    parsedDate?.let { date ->
                        val record = ExerciseRecord(
                            name = machineName,
                            sets = serie,
                            reps = repetition,
                            weight = utilisation,
                            totalWeight = utilisation * serie
                        )
                        entriesByDate.getOrPut(date) { mutableListOf() }.add(record)
                    }
                }
                else -> return@forEach // format inconnu
            }
        }
    }

    return@withContext entriesByDate.map { (date, records) ->
        WorkoutEntry(
            date = date,
            mode = "Import CSV",
            exercises = records,
            duration = 0, // Durée 0 = séance planifiée (non terminée)
            totalWeight = records.sumOf { it.weight * it.reps }
        )
    }
}
