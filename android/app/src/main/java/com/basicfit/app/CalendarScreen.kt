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

    // State: mois actuellement affiché
    val currentMonth = remember { YearMonth.now() }
    val calendarState = rememberCalendarState(currentMonth)

    var draggedEntry by remember { mutableStateOf<WorkoutEntry?>(null) }

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
                onClick = { csvLauncher.launch(arrayOf("text/*", "application/*", "*/*")) },
                colors = ButtonDefaults.buttonColors(containerColor = Accent)
            ) { Text("📂 Importer CSV", color = Color.White) }

            Spacer(Modifier.width(8.dp))

            Button(
                onClick = { showClearDialog = true },
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F)) // rouge pour alerte
            ) { Text("🗑️ Vider calendrier", color = Color.White) }
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
    val dayBackground = if (isToday) Color(0xFFFFF3E0) else Color.White // fond pêche clair pour aujourd'hui

    Box(
        modifier = Modifier
            .aspectRatio(1f)
            .padding(2.dp)
            .background(dayBackground, RoundedCornerShape(4.dp))
            .then(if (isToday) Modifier.border(2.dp, Accent, RoundedCornerShape(4.dp)) else Modifier)
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
            modifier = Modifier.padding(2.dp)
        )

        // Indicateur de complétion
        if (hasCompleted) {
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = "Terminé",
                tint = SoftBlue,
                modifier = Modifier
                    .size(12.dp)
                    .align(Alignment.TopEnd)
                    .padding(2.dp)
            )
        }

        Column(modifier = Modifier.fillMaxSize(), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
            val firstEx = exercisesToday.firstOrNull()
            if (firstEx != null) {
                val dotColor = when {
                    firstEx.name.contains("cardio", true) -> SoftBlue
                    firstEx.name.contains("dos", true) || firstEx.name.contains("row", true) -> Color(0xFF4285F4)
                    firstEx.name.contains("leg", true) || firstEx.name.contains("squat", true) -> Color(0xFF66BB6A)
                    else -> Accent
                }

                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .clip(CircleShape)
                        .background(dotColor)
                        .padding(1.dp)
                        .clickable { onEntryClick(entriesToday.first()) }
                        .pointerInput(Unit) {
                            detectDragGestures(onDragStart = { onDragStart(entriesToday.first()) }) { change, _ ->
                                change.consume()
                            }
                        }
                )
            }

            if (exercisesToday.size > 1) {
                 Text("+${exercisesToday.size - 1}", fontSize = 8.sp)
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

            if (parts.size != 4 && parts.size != 5) return@forEach // format inconnu

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
                    weight = utilisation
                )
                entriesByDate.getOrPut(date) { mutableListOf() }.add(record)
            }
        }
    }

    return@withContext entriesByDate.map { (date, records) ->
        WorkoutEntry(
            date = date,
            mode = "Import CSV",
            exercises = records,
            duration = 0,
            totalWeight = records.sumOf { it.weight * it.reps }
        )
    }
}
