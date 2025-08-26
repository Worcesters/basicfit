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
import kotlinx.coroutines.isActive
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
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.font.FontWeight

@Composable
fun CalendarScreen(
    workoutHistory: List<WorkoutEntry>,
    onWorkoutHistoryChange: (List<WorkoutEntry>) -> Unit,
    onCsvImported: (List<WorkoutEntry>) -> Unit,
    onEntryClick: (WorkoutEntry) -> Unit,
    onGoToWorkout: () -> Unit,
    onStartWorkout: (List<Machine>, String) -> Unit = { _, _ -> }
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    // Ajout pour le bouton de vidage du calendrier
    var showClearDialog by remember { mutableStateOf(false) }
    var isClearingDatabase by remember { mutableStateOf(false) }

    // État pour la synchronisation avec la BDD
    var isLoadingFromDB by remember { mutableStateOf(false) }
    var lastSyncTime by remember { mutableStateOf(0L) }

    // State: mois actuellement affiché
    val currentMonth = remember { YearMonth.now() }
    val calendarState = rememberCalendarState(currentMonth)

    var draggedEntry by remember { mutableStateOf<WorkoutEntry?>(null) }

    // Fonction pour diagnostiquer les problèmes de sync (avec gestion de scope)
    fun runHealthCheck() {
        if (coroutineScope.isActive) {
            coroutineScope.launch {
                try {
                    val apiService = ApiService.getInstance()
                    apiService.initialize(context)

                    android.util.Log.d("CalendarSync", "🔍 Démarrage health check...")

                    if (apiService.isApiAvailable()) {
                        // Test de l'endpoint health
                        val healthResult = apiService.getApi().getCalendarHealth()
                        if (isActive) {
                            if (healthResult.success) {
                                android.util.Log.d("CalendarSync", "✅ Health check OK: ${healthResult.message}")
                                Toast.makeText(context, "🔍 Health check: API OK", Toast.LENGTH_SHORT).show()
                            } else {
                                android.util.Log.w("CalendarSync", "⚠️ Health check échoué: ${healthResult.message}")
                                Toast.makeText(context, "⚠️ Health check: ${healthResult.message}", Toast.LENGTH_SHORT).show()
                            }
                        }
                    } else {
                        if (isActive) {
                            android.util.Log.w("CalendarSync", "❌ API non disponible pour health check")
                            Toast.makeText(context, "❌ Health check: API non disponible", Toast.LENGTH_SHORT).show()
                        }
                    }
                } catch (e: Exception) {
                    if (isActive) {
                        android.util.Log.e("CalendarSync", "❌ Exception health check: ${e.message}")
                        Toast.makeText(context, "❌ Health check échoué: ${e.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }

    // Fonction pour synchroniser avec la BDD (améliorée avec gestion de scope)
    fun syncWithDatabase() {
        if (isLoadingFromDB) return

        // Vérifier que le scope est actif avant de lancer la coroutine
        if (coroutineScope.isActive) {
            coroutineScope.launch {
                isLoadingFromDB = true
                try {
                    val apiService = ApiService.getInstance()
                    apiService.initialize(context)

                    android.util.Log.d("CalendarSync", "🔄 Démarrage synchronisation calendrier...")

                    if (apiService.isApiAvailable()) {
                        val result = apiService.getCalendarHistory()
                        result.onSuccess { dbHistory ->
                            // Vérifier que le scope est toujours actif avant les opérations UI
                            if (isActive) {
                                android.util.Log.d("CalendarSync", "📊 Données reçues de l'API: ${dbHistory.size} séances")

                                // Log des premières entrées pour debug
                                dbHistory.take(3).forEachIndexed { index, entry ->
                                    android.util.Log.d("CalendarSync", "  [$index] Date: ${entry.date}, Mode: ${entry.mode}, Exercices: ${entry.exercises.size}")
                                }

                                // Fusionner avec l'historique local (priorité aux données DB)
                                val mergedHistory = (workoutHistory + dbHistory)
                                    .distinctBy { "${it.date}_${it.mode}_${it.duration}" }
                                    .sortedByDescending { it.date }

                                onWorkoutHistoryChange(mergedHistory)
                                lastSyncTime = System.currentTimeMillis()

                                android.util.Log.d("CalendarSync", "✅ Synchronisation réussie: ${dbHistory.size} séances de la BDD, ${mergedHistory.size} total après fusion")
                                Toast.makeText(context, "✅ Calendrier synchronisé (${dbHistory.size} séances)", Toast.LENGTH_SHORT).show()
                            }
                        }.onFailure { error ->
                            if (isActive) {
                                android.util.Log.e("CalendarSync", "❌ Erreur de synchronisation: ${error.message}", error)
                                Toast.makeText(context, "❌ Erreur sync: ${error.message}", Toast.LENGTH_LONG).show()
                            }
                        }
                    } else {
                        if (isActive) {
                            android.util.Log.w("CalendarSync", "⚠️ API non disponible")
                            Toast.makeText(context, "⚠️ Serveur non accessible", Toast.LENGTH_SHORT).show()
                        }
                    }
                } catch (e: Exception) {
                    if (isActive) {
                        android.util.Log.e("CalendarSync", "❌ Exception lors de la synchronisation: ${e.message}", e)
                        Toast.makeText(context, "❌ Exception sync: ${e.message}", Toast.LENGTH_LONG).show()
                    }
                } finally {
                    if (isActive) {
                        isLoadingFromDB = false
                    }
                }
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

    // Launcher CSV avec gestion correcte du scope
    val csvLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) {
            AppLogger.csv("CSV_LAUNCHER", "📂 Sélection fichier CSV: $uri")
            // Vérifier que le composant est toujours en composition avant de lancer la coroutine
            if (coroutineScope.isActive) {
                coroutineScope.launch {
                    try {
                        val imported = parseCsv(context, uri)
                        // Vérifier à nouveau que le scope est actif avant les opérations UI
                        if (isActive) {
                            if (imported.isNotEmpty()) {
                                AppLogger.success("CSV_LAUNCHER", "✅ Import CSV terminé: ${imported.size} séances")
                                onCsvImported(imported)
                                Toast.makeText(context, "Import réussi : ${imported.size} séances ajoutées", Toast.LENGTH_LONG).show()
                            } else {
                                AppLogger.w("CSV_LAUNCHER", "⚠️ Aucune données dans le fichier CSV")
                                Toast.makeText(context, "Aucune donnée trouvée dans le fichier CSV", Toast.LENGTH_LONG).show()
                            }
                        }
                    } catch (e: Exception) {
                        // Vérifier que le scope est toujours actif avant d'afficher l'erreur
                        if (isActive) {
                            AppLogger.e("CSV_LAUNCHER", "❌ Erreur lors de l'import CSV", e)
                            Toast.makeText(context, "Erreur lors de l'import: ${e.message}", Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        } else {
            AppLogger.w("CSV_LAUNCHER", "⚠️ Aucun fichier sélectionné")
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
                enabled = !isClearingDatabase,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F))
            ) {
                if (isClearingDatabase) {
                    Text("🗑️ Suppression...", color = Color.White)
                } else {
                    Text("🗑️ Vider BDD", color = Color.White)
                }
            }
        }

        Spacer(Modifier.height(8.dp))

        // State pour la date sélectionnée
        var selectedDate by remember { mutableStateOf<LocalDate?>(LocalDate.now()) }

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
                                onEntryClick = onEntryClick,
                                selectedDate = selectedDate,
                                onDateSelect = { selectedDate = it }
                            )
                        }
                    )
                }
            }

            // Section des détails de la journée sélectionnée
            selectedDate?.let { date ->
                val entriesForSelectedDate = workoutHistory.filter { it.date == date }
                if (entriesForSelectedDate.isNotEmpty()) {
                    item {
                        Spacer(modifier = Modifier.height(16.dp))
                        DayDetailsSection(
                            date = date,
                            entries = entriesForSelectedDate,
                            onEntryClick = onEntryClick,
                            onStartWorkout = onStartWorkout
                        )
                    }
                }
            }
        }

        // Pop-up de confirmation pour vider la BDD
        if (showClearDialog) {
            AlertDialog(
                onDismissRequest = { showClearDialog = false },
                confirmButton = {
                    TextButton(
                        onClick = {
                            if (coroutineScope.isActive) {
                                coroutineScope.launch {
                                    isClearingDatabase = true
                                    try {
                                        val apiService = ApiService.getInstance()
                                        apiService.initialize(context)

                                        if (apiService.isApiAvailable()) {
                                            val result = apiService.deleteAllSessions()
                                            if (isActive) {
                                                result.onSuccess { response ->
                                                    if (response.success) {
                                                        // Vider aussi l'historique local
                                                        onWorkoutHistoryChange(emptyList())
                                                        Toast.makeText(context, "✅ ${response.message} (${response.deleted_count} séances supprimées)", Toast.LENGTH_LONG).show()
                                                        android.util.Log.d("ClearDatabase", "✅ Suppression réussie: ${response.deleted_count} séances")
                                                    } else {
                                                        Toast.makeText(context, "❌ Erreur: ${response.message}", Toast.LENGTH_LONG).show()
                                                        android.util.Log.e("ClearDatabase", "❌ Erreur serveur: ${response.message}")
                                                    }
                                                }.onFailure { error ->
                                                    Toast.makeText(context, "❌ Erreur de connexion: ${error.message}", Toast.LENGTH_LONG).show()
                                                    android.util.Log.e("ClearDatabase", "❌ Erreur API: ${error.message}", error)
                                                }
                                            }
                                        } else {
                                            if (isActive) {
                                                Toast.makeText(context, "⚠️ Serveur non accessible", Toast.LENGTH_SHORT).show()
                                                android.util.Log.w("ClearDatabase", "⚠️ API non disponible")
                                            }
                                        }
                                    } catch (e: Exception) {
                                        if (isActive) {
                                            Toast.makeText(context, "❌ Exception: ${e.message}", Toast.LENGTH_LONG).show()
                                            android.util.Log.e("ClearDatabase", "❌ Exception lors de la suppression", e)
                                        }
                                    } finally {
                                        if (isActive) {
                                            isClearingDatabase = false
                                            showClearDialog = false
                                        }
                                    }
                                }
                            }
                        },
                        enabled = !isClearingDatabase
                    ) {
                        if (isClearingDatabase) {
                            Text("Suppression...", color = Color.Gray)
                        } else {
                            Text("Confirmer", color = Accent)
                        }
                    }
                },
                dismissButton = {
                    TextButton(
                        onClick = { showClearDialog = false },
                        enabled = !isClearingDatabase
                    ) {
                        Text("Annuler")
                    }
                },
                title = { Text("⚠️ Vider la base de données") },
                text = {
                    Text("Voulez-vous vraiment supprimer TOUS les entraînements simples de la base de données ?\n\n⚠️ Cette action est irréversible !")
                }
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
    onEntryClick: (WorkoutEntry) -> Unit,
    selectedDate: LocalDate?,
    onDateSelect: (LocalDate) -> Unit
) {
    val date = dayState.date
    val entriesToday = remember(workoutHistory) { workoutHistory.filter { it.date == date } }
    val hasCompleted = entriesToday.any { it.duration > 0 }
    val exercisesToday = remember(entriesToday) { entriesToday.flatMap { it.exercises } }

    val isToday = date == LocalDate.now()
    val isPast = date.isBefore(LocalDate.now())
    val isSelected = date == selectedDate

    // Déterminer la couleur de fond selon le statut
    val backgroundColor = when {
        isSelected -> Color(0xFF00C9A7).copy(alpha = 0.4f) // Fond mint pour sélection
        hasCompleted -> Color(0xFF4CAF50) // Vert pour terminé
        entriesToday.isNotEmpty() && isPast -> Color(0xFFFF5722) // Rouge pour en retard
        entriesToday.isNotEmpty() && !isPast -> Color(0xFFFF9800) // Orange pour à venir
        isToday -> Color(0xFF00C9A7).copy(alpha = 0.2f) // Fond mint clair pour aujourd'hui
        else -> Color.White // Blanc par défaut
    }

    Box(
        modifier = Modifier
            .aspectRatio(1f)
            .padding(2.dp)
            .background(backgroundColor, RoundedCornerShape(4.dp))
            .then(if (isToday) Modifier.border(3.dp, Color(0xFF00C9A7), RoundedCornerShape(4.dp)) else Modifier)
            .clickable {
                onDateSelect(date)
                if (entriesToday.isNotEmpty()) {
                    onEntryClick(entriesToday.first())
                }
            }
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

        // Afficher les détails des séances de façon plus lisible
        if (exercisesToday.isNotEmpty()) {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Icône ou emoji selon l'état
                Text(
                    text = when {
                        hasCompleted -> "✅"
                        isPast -> "❌"
                        else -> "📅"
                    },
                    fontSize = 14.sp
                )

                Text(
                    text = "${exercisesToday.size}",
                    fontSize = 11.sp,
                    color = if (backgroundColor == Color.White) Color.Black else Color.White,
                    fontWeight = androidx.compose.ui.text.font.FontWeight.Bold
                )

                if (exercisesToday.size > 1) {
                    Text(
                        text = "ex.",
                        fontSize = 8.sp,
                        color = if (backgroundColor == Color.White) Color.Black else Color.White
                    )
                }

                // Affichage de la durée si complétée
                if (hasCompleted) {
                    val completedEntry = entriesToday.first { it.duration > 0 }
                    Text(
                        text = "${completedEntry.duration}min",
                        fontSize = 7.sp,
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
    AppLogger.csv("CSV_IMPORT", "🚀 Début de l'import CSV depuis URI: $uri")
    val entriesByDate = mutableMapOf<LocalDate, MutableList<ExerciseRecord>>()
    var totalLines = 0
    var processedLines = 0
    var errorLines = 0

    try {
        context.contentResolver.openInputStream(uri)?.bufferedReader()?.useLines { lines ->
            val linesList = lines.toList()
            totalLines = linesList.size
            AppLogger.csv("CSV_IMPORT", "📊 Fichier CSV lu: $totalLines lignes (header inclus)")

            if (totalLines < 2) {
                AppLogger.w("CSV_IMPORT", "⚠️ Fichier CSV vide ou sans données (seulement header)")
                return@useLines
            }

            // Parser les headers de la première ligne
            val headerLine = linesList.first()
            val headers = headerLine.split(';', ',').map { it.trim().lowercase() }
            AppLogger.csv("CSV_IMPORT", "📋 Headers détectés: $headers")

            // Trouver les indices des colonnes (insensible à la casse)
            val machineIndex = headers.indexOfFirst { it.contains("machine") || it.contains("exercice") || it.contains("nom") }
            val dateIndex = headers.indexOfFirst { it.contains("date") }
            val typeIndex = headers.indexOfFirst { it.contains("type") || it.contains("categorie") || it.contains("mode") }
            val repsIndex = headers.indexOfFirst { it.contains("rep") || it.contains("repetition") }
            val setsIndex = headers.indexOfFirst { it.contains("set") || it.contains("serie") }
            val weightIndex = headers.indexOfFirst { it.contains("poids") || it.contains("weight") || it.contains("kg") }

            AppLogger.d("CSV_IMPORT", "   Machine col: $machineIndex, Date col: $dateIndex, Type col: $typeIndex")
            AppLogger.d("CSV_IMPORT", "   Reps col: $repsIndex, Sets col: $setsIndex, Weight col: $weightIndex")

            if (machineIndex == -1 || dateIndex == -1) {
                AppLogger.e("CSV_IMPORT", "❌ Colonnes obligatoires manquantes: machine=$machineIndex, date=$dateIndex")
                return@useLines
            }

            linesList.drop(1).forEachIndexed { index, line ->
                totalLines--
                AppLogger.d("CSV_IMPORT", "🔍 Ligne ${index + 2}: '$line'")

                if (line.trim().isEmpty()) {
                    AppLogger.w("CSV_IMPORT", "⚠️ Ligne ${index + 2} vide, ignorée")
                    return@forEachIndexed
                }

                val parts = line.split(';', ',').map { it.trim() }
                AppLogger.d("CSV_IMPORT", "📝 Parsage ligne ${index + 2}: ${parts.size} colonnes = $parts")

                // Vérifier que nous avons assez de colonnes
                if (parts.size <= maxOf(machineIndex, dateIndex)) {
                    AppLogger.e("CSV_IMPORT", "❌ Pas assez de colonnes ligne ${index + 2}: ${parts.size} colonnes, besoin de ${maxOf(machineIndex, dateIndex) + 1}")
                    errorLines++
                    return@forEachIndexed
                }

                // Extraire les valeurs selon les indices détectés
                val machineName = parts.getOrNull(machineIndex) ?: ""
                val dateStr = parts.getOrNull(dateIndex) ?: ""
                val typeStr = if (typeIndex >= 0 && typeIndex < parts.size) parts[typeIndex] else "musculation"

                // Extraire les valeurs optionnelles selon les indices détectés
                val repsStr = if (repsIndex >= 0 && repsIndex < parts.size) parts[repsIndex] else ""
                val setsStr = if (setsIndex >= 0 && setsIndex < parts.size) parts[setsIndex] else ""
                val weightStr = if (weightIndex >= 0 && weightIndex < parts.size) parts[weightIndex] else ""

                AppLogger.d("CSV_IMPORT", "   Machine: '$machineName', Date: '$dateStr', Type: '$typeStr'")
                AppLogger.d("CSV_IMPORT", "   Reps: '$repsStr', Sets: '$setsStr', Weight: '$weightStr'")

                // Parsing flexible de la date
                val dateFormats = listOf(
                    DateTimeFormatter.ISO_LOCAL_DATE,
                    DateTimeFormatter.ofPattern("dd/MM/yyyy"),
                    DateTimeFormatter.ofPattern("dd-MM-yyyy")
                )
                val parsedDate = dateFormats.firstNotNullOfOrNull { fmt ->
                    runCatching { LocalDate.parse(dateStr, fmt) }.getOrNull()
                }

                if (parsedDate == null) {
                    AppLogger.e("CSV_IMPORT", "❌ Impossible de parser la date '$dateStr' ligne ${index + 2}")
                    errorLines++
                    return@forEachIndexed
                }

                AppLogger.d("CSV_IMPORT", "   Date parsée: $parsedDate")

                // Parser les valeurs numériques si disponibles
                val parsedReps = if (repsStr.isNotEmpty()) {
                    if (repsStr.contains('-')) {
                        val bounds = repsStr.split('-').mapNotNull { it.toIntOrNull() }
                        if (bounds.size == 2) ((bounds[0] + bounds[1]) / 2.0).toInt() else 0
                    } else repsStr.toIntOrNull() ?: 0
                } else 0

                val parsedSets = setsStr.toIntOrNull() ?: 0
                val parsedWeight = weightStr.toDoubleOrNull() ?: 0.0

                // Déterminer les valeurs finales (colonnes détectées ou valeurs par défaut selon le type)
                val (finalSets, finalReps, finalWeight) = when {
                    // Si des valeurs ont été trouvées dans le CSV, les utiliser
                    parsedSets > 0 || parsedReps > 0 || parsedWeight > 0.0 -> {
                        Triple(
                            if (parsedSets > 0) parsedSets else 1,
                            if (parsedReps > 0) parsedReps else 1,
                            parsedWeight
                        )
                    }
                    // Sinon utiliser les valeurs par défaut selon le type
                    else -> when (typeStr.lowercase()) {
                        "cardio", "tapis", "vélo", "rameur" -> Triple(1, 30, 0.0) // 30 min cardio
                        "musculation", "force" -> Triple(3, 10, 50.0) // 3 séries de 10 reps
                        "gainage", "plank", "core" -> Triple(1, 60, 0.0) // 1 min gainage
                        else -> Triple(3, 10, 0.0) // Valeurs par défaut
                    }
                }

                AppLogger.d("CSV_IMPORT", "   Valeurs finales: ${finalSets}x${finalReps} @ ${finalWeight}kg")

                val record = ExerciseRecord(
                    name = machineName,
                    sets = finalSets,
                    reps = finalReps,
                    weight = finalWeight
                )
                entriesByDate.getOrPut(parsedDate) { mutableListOf() }.add(record)
                processedLines++
                AppLogger.success("CSV_IMPORT", "✅ Ligne ${index + 2} traitée avec succès")
            }
        }
    } catch (e: Exception) {
        AppLogger.e("CSV_IMPORT", "❌ Erreur fatale lors du parsing CSV: ${e.message}", e)
        return@withContext emptyList()
    }

    // Résumé du traitement
    val workoutEntries = entriesByDate.map { (date, records) ->
        WorkoutEntry(
            date = date,
            mode = "Import CSV",
            exercises = records,
            duration = 0, // Durée 0 = séance planifiée (non terminée)
            totalWeight = records.sumOf { it.weight * it.reps }
        )
    }

    AppLogger.success("CSV_IMPORT", "📊 Résumé import CSV:")
    AppLogger.i("CSV_IMPORT", "   • ${processedLines} lignes traitées avec succès")
    AppLogger.i("CSV_IMPORT", "   • ${errorLines} lignes avec erreurs")
    AppLogger.i("CSV_IMPORT", "   • ${entriesByDate.size} séances créées")
    AppLogger.i("CSV_IMPORT", "   • ${entriesByDate.values.sumOf { it.size }} exercices au total")

    return@withContext workoutEntries
}

@Composable
private fun DayDetailsSection(
    date: LocalDate,
    entries: List<WorkoutEntry>,
    onEntryClick: (WorkoutEntry) -> Unit,
    onStartWorkout: (List<Machine>, String) -> Unit
) {
    val context = LocalContext.current
    var machinesList by remember { mutableStateOf<List<Machine>>(emptyList()) }
    
    // Charger les machines depuis l'API
    LaunchedEffect(Unit) {
        try {
            val api = ApiService.getInstance().apply { initialize(context) }.getApi()
            val response = api.getMachines()
            if (response.results.isNotEmpty()) {
                val remoteMachines = response.results.mapNotNull { dto ->
                    try {
                        Machine(
                            id = dto.id,
                            nom = dto.nom,
                            description = dto.description ?: "",
                            instructions = dto.instructions ?: "",
                            categorie = CategorieMachine.values().find { it.displayName.equals(dto.categorie ?: "", true) }
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
            android.util.Log.e("MachinesAPI", "❌ Erreur chargement machines: ${e.message}")
            machinesList = emptyList()
        }
    }
    androidx.compose.material3.Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        shape = RoundedCornerShape(8.dp),
        elevation = CardDefaults.cardElevation(4.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // En-tête avec la date
            Text(
                text = "📅 ${date.format(DateTimeFormatter.ofPattern("dd MMMM yyyy"))}",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF333333)
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Liste des séances
            entries.forEach { entry ->
                WorkoutEntryItem(
                    entry = entry,
                    onClick = { onEntryClick(entry) },
                    onStartWorkout = if (entry.duration == 0) {
                        {
                            // Convertir WorkoutEntry en machines pour démarrer l'entraînement
                            val machines = entry.exercises.mapNotNull { exercise ->
                                // Chercher la vraie machine dans l'API par nom
                                val realMachine = machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) }
                                if (realMachine != null) {
                                    realMachine
                                } else {
                                    // Fallback si la machine n'est pas trouvée
                                    Machine(
                                        id = 0, // ID temporaire
                                        nom = exercise.name,
                                        nomAnglais = exercise.name,
                                        description = "Machine générée depuis calendrier",
                                        instructions = "Exercice importé depuis le calendrier",
                                        categorie = CategorieMachine.MUSCULATION,
                                        groupeMusculairePrimaire = "Général",
                                        imageGif = null,
                                        tempo = null
                                    )
                                }
                            }
                            onStartWorkout(machines, entry.mode)
                        }
                    } else null
                )
                if (entry != entries.last()) {
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
private fun WorkoutEntryItem(
    entry: WorkoutEntry,
    onClick: () -> Unit,
    onStartWorkout: (() -> Unit)? = null
) {
    androidx.compose.material3.Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        colors = CardDefaults.cardColors(
            containerColor = if (entry.duration > 0) Color(0xFFF1F8E9) else Color(0xFFFFF3E0)
        ),
        shape = RoundedCornerShape(8.dp)
    ) {
        Row(
            modifier = Modifier.padding(12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icône de statut
            Text(
                text = if (entry.duration > 0) "✅" else "📅",
                fontSize = 20.sp,
                modifier = Modifier.padding(end = 12.dp)
            )

            Column(modifier = Modifier.weight(1f)) {
                // Nom de la séance
                Text(
                    text = entry.mode,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF333333)
                )

                // Détails
                Text(
                    text = if (entry.duration > 0) {
                        "${entry.exercises.size} exercices • ${entry.duration} min • ${entry.totalWeight.toInt()}kg total"
                    } else {
                        "${entry.exercises.size} exercices planifiés"
                    },
                    fontSize = 12.sp,
                    color = Color(0xFF666666)
                )

                // Liste des exercices (limitée à 3)
                val displayExercises = entry.exercises.take(3)
                if (displayExercises.isNotEmpty()) {
                    Text(
                        text = displayExercises.joinToString(" • ") { it.name } +
                               if (entry.exercises.size > 3) " +${entry.exercises.size - 3}" else "",
                        fontSize = 11.sp,
                        color = Color(0xFF888888),
                        fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                    )
                }
            }

            // Bouton démarrer pour les séances non terminées ou icône pour les terminées
            if (onStartWorkout != null) {
                Button(
                    onClick = onStartWorkout,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFF00C9A7)
                    ),
                    modifier = Modifier.padding(start = 8.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.PlayArrow,
                            contentDescription = "Démarrer",
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Démarrer",
                            color = Color.White,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            } else {
                // Indicateur visuel pour les séances terminées
                Icon(
                    imageVector = Icons.Default.ChevronRight,
                    contentDescription = "Voir détails",
                    tint = Color(0xFF00C9A7),
                    modifier = Modifier.size(20.dp)
                )
            }
        }
    }
}
