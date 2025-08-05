package com.basicfit.app

import androidx.compose.foundation.Canvas
import com.basicfit.app.ExerciseRecord
import androidx.compose.foundation.background


import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.Paint
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import kotlin.math.max

// Data class pour les statistiques de séance
data class WorkoutSummary(
    val workoutName: String,
    val date: LocalDate,
    val duration: Int,
    val totalCalories: Int,
    val totalVolume: Double, // poids total soulevé
    val exercicesCompleted: List<ExerciseRecord>,
    val averageRest: Int,
    val personalRecords: List<String>
)

// Data class pour les comparaisons
data class WorkoutComparison(
    val exerciseName: String,
    val currentWeight: Double,
    val previousWeight: Double,
    val currentReps: Int,
    val previousReps: Int,
    val progression: Double, // en pourcentage
    val isImprovement: Boolean
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WorkoutSummaryScreen(
    workoutSummary: WorkoutSummary,
    workoutHistory: List<WorkoutEntry>,
    profileData: ProfileData,
    onContinue: () -> Unit
) {
    val context = LocalContext.current

    // Calculer les comparaisons avec les séances précédentes
    val comparisons = calculateWorkoutComparisons(workoutSummary, workoutHistory)
    val improvementCount = comparisons.count { it.isImprovement }
    val totalComparisons = comparisons.size

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
    ) {
        // Header
        TopAppBar(
            title = {
                Text(
                    text = "🎉 Récapitulatif de séance",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
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
            // Statistiques générales
            item {
                WorkoutStatsCard(workoutSummary = workoutSummary, profileData = profileData)
            }

            // Graphique de progression
            if (comparisons.isNotEmpty()) {
                item {
                    ProgressionGraphCard(comparisons = comparisons)
                }
            }

            // Comparaisons par exercice
            if (comparisons.isNotEmpty()) {
                item {
                    ExerciseComparisonsCard(
                        comparisons = comparisons,
                        improvementCount = improvementCount,
                        totalComparisons = totalComparisons
                    )
                }
            }

            // Records personnels
            if (workoutSummary.personalRecords.isNotEmpty()) {
                item {
                    PersonalRecordsCard(records = workoutSummary.personalRecords)
                }
            }

            // Conseils et recommandations
            item {
                RecommendationsCard(
                    workoutSummary = workoutSummary,
                    comparisons = comparisons,
                    profileData = profileData
                )
            }

            // Bouton continuer
            item {
                Spacer(modifier = Modifier.height(16.dp))

                Button(
                    onClick = onContinue,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Accent
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = Icons.Default.Home,
                            contentDescription = "Continuer",
                            tint = Color.White
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "✨ RETOUR À L'ACCUEIL",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color.White
                        )
                    }
                }
            }

            // Prochaine recommandation personnalisée (AVANT le bouton)
            item {
                NextRecommendationsCard(
                    workoutSummary = workoutSummary,
                    workoutHistory = workoutHistory,
                    profileData = profileData
                )
            }
        }
    }
}

@Composable
fun WorkoutStatsCard(
    workoutSummary: WorkoutSummary,
    profileData: ProfileData
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "📊 ${workoutSummary.workoutName}",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    icon = "⏱️",
                    label = "Durée",
                    value = "${workoutSummary.duration} min"
                )
                StatItem(
                    icon = "🔥",
                    label = "Calories",
                    value = "${workoutSummary.totalCalories}"
                )
                StatItem(
                    icon = "💪",
                    label = "Volume",
                    value = "${workoutSummary.totalVolume.toInt()} kg"
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    icon = "🏋️",
                    label = "Exercices",
                    value = "${workoutSummary.exercicesCompleted.size}"
                )
                StatItem(
                    icon = "📈",
                    label = "Séries totales",
                    value = "${workoutSummary.exercicesCompleted.sumOf { it.sets }}"
                )
                StatItem(
                    icon = "💤",
                    label = "Repos moy.",
                    value = "${workoutSummary.averageRest}s"
                )
            }
        }
    }
}

@Composable
fun StatItem(
    icon: String,
    label: String,
    value: String
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = icon,
            fontSize = 24.sp,
            modifier = Modifier.padding(bottom = 4.dp)
        )
        Text(
            text = value,
            fontSize = 18.sp,
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
fun ProgressionGraphCard(comparisons: List<WorkoutComparison>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "📈 Progression par exercice",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            // Graphique en barres simple
            Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
            ) {
                drawProgressionGraph(comparisons)
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Légende
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                LegendItem(color = Color(0xFF4CAF50), label = "Amélioration")
                LegendItem(color = Color(0xFFFF9800), label = "Stable")
                LegendItem(color = Color(0xFFF44336), label = "Régression")
            }
        }
    }
}

@Composable
fun LegendItem(color: Color, label: String) {
    Row(
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .background(color, RoundedCornerShape(2.dp))
        )
        Spacer(modifier = Modifier.width(4.dp))
        Text(
            text = label,
            fontSize = 12.sp,
            color = Color.Gray
        )
    }
}

fun DrawScope.drawProgressionGraph(comparisons: List<WorkoutComparison>) {
    if (comparisons.isEmpty()) return

    val barWidth = size.width / comparisons.size
    val maxProgression = comparisons.maxOfOrNull { kotlin.math.abs(it.progression) } ?: 1.0
    val zeroY = size.height / 2

    comparisons.forEachIndexed { index, comparison ->
        val barHeight = (comparison.progression / maxProgression * size.height / 2).toFloat()
        val x = index * barWidth + barWidth * 0.2f
        val barWidthActual = barWidth * 0.6f

        val color = when {
            comparison.isImprovement -> Color(0xFF4CAF50)
            comparison.progression == 0.0 -> Color(0xFFFF9800)
            else -> Color(0xFFF44336)
        }

        if (barHeight > 0) {
            // Barre positive (amélioration)
            drawRect(
                color = color,
                topLeft = Offset(x, zeroY - barHeight),
                size = androidx.compose.ui.geometry.Size(barWidthActual, barHeight)
            )
        } else {
            // Barre négative (régression)
            drawRect(
                color = color,
                topLeft = Offset(x, zeroY),
                size = androidx.compose.ui.geometry.Size(barWidthActual, -barHeight)
            )
        }
    }

    // Ligne zéro
    drawLine(
        color = Color.Gray,
        start = Offset(0f, zeroY),
        end = Offset(size.width, zeroY),
        strokeWidth = 2.dp.toPx()
    )
}

@Composable
fun ExerciseComparisonsCard(
    comparisons: List<WorkoutComparison>,
    improvementCount: Int,
    totalComparisons: Int
) {
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
                    text = "🔄 Comparaisons",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = Accent
                )
                Text(
                    text = "$improvementCount/$totalComparisons améliorés",
                    fontSize = 14.sp,
                    color = Color(0xFF4CAF50),
                    fontWeight = FontWeight.Medium
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            comparisons.forEach { comparison ->
                ComparisonItem(comparison = comparison)
                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
fun ComparisonItem(comparison: WorkoutComparison) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(
                color = if (comparison.isImprovement) Color(0xFFE8F5E8) else Color(0xFFFFF3E0),
                shape = RoundedCornerShape(8.dp)
            )
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = comparison.exerciseName,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = "${comparison.currentWeight.toInt()}kg × ${comparison.currentReps} (vs ${comparison.previousWeight.toInt()}kg × ${comparison.previousReps})",
                fontSize = 12.sp,
                color = Color.Gray
            )
        }

        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (comparison.isImprovement) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                contentDescription = if (comparison.isImprovement) "Amélioration" else "Régression",
                tint = if (comparison.isImprovement) Color(0xFF4CAF50) else Color(0xFFF44336),
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "${if (comparison.progression > 0) "+" else ""}${comparison.progression.toInt()}%",
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = if (comparison.isImprovement) Color(0xFF4CAF50) else Color(0xFFF44336)
            )
        }
    }
}

@Composable
fun PersonalRecordsCard(records: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = AccentLight)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "🏆 Records personnels !",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            records.forEach { record ->
                Row(
                    modifier = Modifier.padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "🎯",
                        fontSize = 16.sp,
                        modifier = Modifier.padding(end = 8.dp)
                    )
                    Text(
                        text = record,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }
    }
}

@Composable
fun RecommendationsCard(
    workoutSummary: WorkoutSummary,
    comparisons: List<WorkoutComparison>,
    profileData: ProfileData
) {
    val recommendations = generateWorkoutRecommendations(workoutSummary, comparisons, profileData)

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF3E5F5))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "💡 Recommandations",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            recommendations.forEach { recommendation ->
                Row(
                    modifier = Modifier.padding(vertical = 4.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Text(
                        text = "•",
                        fontSize = 14.sp,
                        color = Accent,
                        modifier = Modifier.padding(end = 8.dp, top = 2.dp)
                    )
                    Text(
                        text = recommendation,
                        fontSize = 14.sp,
                        lineHeight = 20.sp
                    )
                }
            }
        }
    }
}

@Composable
fun NextRecommendationsCard(
    workoutSummary: WorkoutSummary,
    workoutHistory: List<WorkoutEntry>,
    profileData: ProfileData
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFE3F2FD))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "🔮 Prochaine recommandation",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            val hasReco = workoutSummary.exercicesCompleted.isNotEmpty()
            if (hasReco) {
                workoutSummary.exercicesCompleted.forEach { exercise ->
                    // Récupérer la vraie machine depuis l'API ou la liste locale
                    val context = LocalContext.current
                    var machinesList by remember { mutableStateOf<List<Machine>>(emptyList()) }

                    // État pour la recommandation
                    var recommendation by remember { mutableStateOf<ExerciseRecommendation?>(null) }
                    var isLoading by remember { mutableStateOf(true) }
                    var debugInfo by remember { mutableStateOf("🔍 Chargement...") }

                    // Charger les machines et la recommandation
                    LaunchedEffect(exercise.name) {
                        try {
                            // Charger les machines depuis l'API
                            val apiService = ApiService.getInstance()
                            apiService.initialize(context)
                            val response = apiService.getApi().getMachines()
                            machinesList = response.results.map { machineDto ->
                                        Machine(
                                    id = machineDto.id,
                                    nom = machineDto.nom,
                                    description = machineDto.description ?: "",
                                    instructions = machineDto.instructions ?: "",
                                    categorie = when (machineDto.categorie) {
                                        "MUSCULATION" -> CategorieMachine.MUSCULATION
                                        "CARDIO" -> CategorieMachine.CARDIO
                                        else -> CategorieMachine.MUSCULATION
                                    },
                                    groupeMusculairePrimaire = machineDto.groupe_musculaire_primaires?.firstOrNull()?.get("nom") ?: "",
                                            incrementPoids = 2.5,
                                            poidsMinimum = 0.0,
                                            poidsMaximum = 200.0,
                                    imageGif = machineDto.image_gif
                                        )
                    }

                    // Chercher la vraie machine par nom
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

                            // Récupérer la recommandation depuis l'API avec retry
                            var apiRecommendation: ExerciseRecommendation? = null
                            var retryCount = 0
                            val maxRetries = 2

                            while (apiRecommendation == null && retryCount < maxRetries) {
                                try {
                                    debugInfo = "🔍 Tentative ${retryCount + 1} API pour: ${exercise.name}"
                                    android.util.Log.d("WorkoutSummary", "🔍 Tentative ${retryCount + 1} de récupération API pour: ${exercise.name}")
                                    apiRecommendation = getRecommendationFromAPI(machine.id, context)

                                    if (apiRecommendation != null) {
                                        debugInfo = "✅ API: ${apiRecommendation.weight}kg reçu"
                                        android.util.Log.d("WorkoutSummary", "✅ SUCCÈS API - Recommandation reçue: ${apiRecommendation.weight}kg pour ${exercise.name}")
                                        android.util.Log.d("WorkoutSummary", "   Détails API: ${apiRecommendation.sets} séries, ${apiRecommendation.reps} reps, repos ${apiRecommendation.restTime}s")
                                        recommendation = apiRecommendation
                                        break
                                    } else {
                                        debugInfo = "⚠️ API null, tentative ${retryCount + 1}"
                                        android.util.Log.w("WorkoutSummary", "⚠️ API retourne null, tentative ${retryCount + 1}")
                                        retryCount++
                                        if (retryCount < maxRetries) {
                                            kotlinx.coroutines.delay(1000) // Attendre 1 seconde avant retry
                                        }
                                    }
                                } catch (e: Exception) {
                                    debugInfo = "❌ Erreur API: ${e.message}"
                                    android.util.Log.e("WorkoutSummary", "❌ Erreur API tentative ${retryCount + 1}: ${e.message}")
                                    retryCount++
                                    if (retryCount < maxRetries) {
                                        kotlinx.coroutines.delay(1000) // Attendre 1 seconde avant retry
                                    }
                                }
                            }

                            // Si l'API échoue après tous les retries, utiliser le fallback local
                            if (apiRecommendation == null) {
                                debugInfo = "⚠️ API échouée, calcul local"
                                android.util.Log.w("WorkoutSummary", "⚠️ API échouée après ${maxRetries} tentatives, utilisation calcul local")
                                recommendation = calculateWorkoutRecommendations(
                                    machine = machine,
                                    workoutHistory = workoutHistory.map { it.toWorkoutSession() },
                                    profileData = profileData
                                )
                                debugInfo = "📊 Calcul local: ${recommendation?.weight}kg"
                                android.util.Log.d("WorkoutSummary", "📊 Calcul local: ${recommendation?.weight}kg")
                            }
                        } catch (e: Exception) {
                            android.util.Log.e("WorkoutSummary", "Erreur lors du chargement: ${e.message}")
                        } finally {
                            isLoading = false
                        }
                    }

                    if (isLoading) {
                        // Afficher un indicateur de chargement
                        Text(
                            text = "• ${exercise.name} : Chargement de la recommandation...",
                            fontSize = 14.sp,
                            color = Color.Gray,
                            modifier = Modifier.padding(vertical = 2.dp)
                        )
                    } else {
                        // Utiliser la recommandation de l'API ou le fallback intelligent
                        val reco = if (recommendation != null) {
                            val rec = recommendation
                            android.util.Log.d("WorkoutSummary", "🔍 DEBUG: recommendation n'est pas null")
                            android.util.Log.d("WorkoutSummary", "🔍 DEBUG: recommendation.weight = ${rec?.weight}")
                            android.util.Log.d("WorkoutSummary", "🔍 DEBUG: recommendation.sets = ${rec?.sets}")
                            android.util.Log.d("WorkoutSummary", "🔍 DEBUG: recommendation.reps = ${rec?.reps}")
                            rec
                        } else {
                            // Fallback intelligent basé sur l'historique
                            val machine = machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) }
                            val suggestedWeight = if (machine != null) {
                                calculateStartingWeight(machine, profileData)
                            } else {
                                0.0
                            }

                            // Utiliser le poids suggéré ou une valeur par défaut plus intelligente
                            val fallbackWeight = if (suggestedWeight > 0) suggestedWeight else {
                                // Calculer basé sur le type d'exercice
                                when {
                                    exercise.name.contains("Développé", ignoreCase = true) -> 30.0
                                    exercise.name.contains("Squat", ignoreCase = true) -> 40.0
                                    exercise.name.contains("Traction", ignoreCase = true) -> 0.0 // Poids du corps
                                    exercise.name.contains("Presse", ignoreCase = true) -> 25.0
                                    else -> 20.0
                                }
                            }

                            ExerciseRecommendation(
                        sets = 3,
                        reps = 10,
                                weight = fallbackWeight,
                        restTime = 90,
                                notes = "💪 Recommandation basée sur l'historique (API non disponible)"
                            )
                        }

                        android.util.Log.d("WorkoutSummary", "🎯 Recommandation finale pour ${exercise.name}: ${reco?.weight}kg")
                        android.util.Log.d("WorkoutSummary", "🔍 DEBUG FINAL: reco.weight = ${reco?.weight}, reco.sets = ${reco?.sets}, reco.reps = ${reco?.reps}")
                        android.util.Log.d("WorkoutSummary", "🔍 DEBUG FINAL: recommendation était null? ${recommendation == null}")
                        if (reco?.weight == 20.0 && recommendation == null) {
                            android.util.Log.w("WorkoutSummary", "⚠️ FALBACK 20kg utilisé pour ${exercise.name} - API non disponible")
                        }

                        val poids = if (reco?.weight != null && reco.weight > 0) {
                            val source = if (recommendation != null) "API" else "LOCAL"
                            debugInfo = "🚀 FINAL: ${reco.weight.toInt()}kg ($source)"
                            android.util.Log.d("WorkoutSummary", "🚀 AFFICHAGE FINAL: ${reco.weight.toInt()}kg pour ${exercise.name} (source: $source)")
                            "${reco.weight.toInt()}kg"
                        } else {
                            // Calculer une suggestion de poids de départ
                            val machine = machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) }
                            if (machine != null) {
                            val suggestedWeight = calculateStartingWeight(machine, profileData)
                            if (suggestedWeight > 0) "${suggestedWeight.toInt()}kg (suggestion)" else "À déterminer"
                            } else {
                                "À déterminer"
                        }
                    }
                        val reps = reco?.reps ?: 10
                        val sets = reco?.sets ?: 3
                        val rest = reco?.restTime ?: 90

                    // Affichage du GIF si présent
                        val machine = machinesList.find { it.nom.equals(exercise.name, ignoreCase = true) }
                        if (machine?.imageGif?.isNotBlank() == true) {
                        AnimatedGifImage(
                            imageUrl = machine.imageGif,
                            contentDescription = "Démonstration GIF",
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp)
                                .padding(vertical = 4.dp)
                        )
                    }

                    Text(
                        text = "• ${exercise.name} : $poids × $reps reps ($sets séries, repos $rest s)",
                        fontSize = 14.sp,
                        color = Color(0xFF2E2E2E),
                        modifier = Modifier.padding(vertical = 2.dp)
                    )

                    // DEBUG INFO - À afficher temporairement
                    Text(
                        text = "DEBUG: $debugInfo",
                        fontSize = 10.sp,
                        color = Color.Red,
                        modifier = Modifier.padding(start = 16.dp, top = 2.dp)
                    )

                        // Afficher les notes de recommandation si disponibles
                        if (reco?.notes?.isNotBlank() == true) {
                            Text(
                                text = "  ${reco.notes}",
                                fontSize = 12.sp,
                                color = Color.Gray,
                                modifier = Modifier.padding(start = 16.dp, bottom = 4.dp)
                            )
                        }
                    }
                }
            } else {
                Text(
                    text = "Aucune recommandation disponible pour la prochaine séance.",
                    fontSize = 14.sp,
                    color = Color.Gray,
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}

// Fonctions utilitaires
fun calculateWorkoutComparisons(
    currentWorkout: WorkoutSummary,
    workoutHistory: List<WorkoutEntry>
): List<WorkoutComparison> {
    val comparisons = mutableListOf<WorkoutComparison>()

    // Trouver la dernière séance similaire (même nom d'entraînement)
    val previousWorkout = workoutHistory
        .filter { it.mode == currentWorkout.workoutName }
        .maxByOrNull { it.date }

    if (previousWorkout != null) {
        currentWorkout.exercicesCompleted.forEach { currentExercise ->
            val previousExercise = previousWorkout.exercises.find { it.name == currentExercise.name }

            if (previousExercise != null) {
                // Calculer la progression basée sur le volume (poids × reps)
                val currentVolume = currentExercise.weight * currentExercise.reps
                val previousVolume = previousExercise.weight * previousExercise.reps
                val progression = ((currentVolume - previousVolume) / previousVolume * 100)

                comparisons.add(
                    WorkoutComparison(
                        exerciseName = currentExercise.name,
                        currentWeight = currentExercise.weight,
                        previousWeight = previousExercise.weight,
                        currentReps = currentExercise.reps,
                        previousReps = previousExercise.reps,
                        progression = progression,
                        isImprovement = progression > 0
                    )
                )
            }
        }
    }

    return comparisons
}

fun generateWorkoutRecommendations(
    workoutSummary: WorkoutSummary,
    comparisons: List<WorkoutComparison>,
    profileData: ProfileData
): List<String> {
    val recommendations = mutableListOf<String>()

    // Analyse de la durée
    when {
        workoutSummary.duration < 30 -> recommendations.add("Séance courte ! Essayez d'augmenter la durée à 45-60 minutes pour maximiser les gains.")
        workoutSummary.duration > 90 -> recommendations.add("Séance longue. Veillez à maintenir l'intensité sur toute la durée.")
    }

    // Analyse des améliorations
    val improvementRate = if (comparisons.isNotEmpty()) {
        comparisons.count { it.isImprovement }.toDouble() / comparisons.size
    } else 0.0

    when {
        improvementRate >= 0.8 -> recommendations.add("Excellente progression ! Continuez sur cette lancée.")
        improvementRate >= 0.5 -> recommendations.add("Bonne progression. Concentrez-vous sur les exercices où vous stagnez.")
        else -> recommendations.add("Progression limitée. Pensez à varier les exercices ou augmenter l'intensité.")
    }

    // Recommandations selon l'objectif
    when (profileData.objectif) {
        "Prise de masse" -> {
            recommendations.add("Pour la prise de masse : visez 8-12 répétitions avec des charges lourdes.")
            if (workoutSummary.averageRest < 90) {
                recommendations.add("Augmentez les temps de repos à 90-120 secondes pour optimiser la récupération.")
            }
        }
        "Force" -> {
            recommendations.add("Pour la force : privilégiez 1-5 répétitions avec charges maximales.")
            recommendations.add("Repos de 3-5 minutes recommandés entre les séries.")
        }
        "Endurance" -> {
            recommendations.add("Pour l'endurance : 15-25 répétitions avec repos courts (30-60s).")
        }
        "Sèche" -> {
            recommendations.add("Pour la sèche : maintenir l'intensité tout en augmentant le volume d'entraînement.")
        }
    }

    // Recommandation nutritionnelle
    recommendations.add("N'oubliez pas votre nutrition post-entraînement dans les 30 minutes suivant la séance !")

    return recommendations
}




