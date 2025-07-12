package com.basicfit.app

import androidx.compose.foundation.Canvas
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StatisticsScreen(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>,
    onBack: () -> Unit
) {
    val context = LocalContext.current

    // Calculer les statistiques (uniquement séances complétées)
    val completedWorkouts = workoutHistory.filter { it.duration > 0 }
    val totalWorkouts = completedWorkouts.size
    val totalMinutes = completedWorkouts.sumOf { it.duration }
    val totalVolume = completedWorkouts.sumOf { it.totalWeight }
    val averageDuration = if (totalWorkouts > 0) totalMinutes / totalWorkouts else 0

    // Analyse des 30 derniers jours
    val last30Days = completedWorkouts.filter {
        ChronoUnit.DAYS.between(it.date, LocalDate.now()) <= 30
    }

    val frequencyPerWeek = (last30Days.size * 7) / 30.0

    // Exercices favoris
    val exerciseFrequency = completedWorkouts.flatMap { it.exercises }
        .groupBy { it.name }
        .mapValues { it.value.size }
        .toList()
        .sortedByDescending { it.second }

    // Progression des charges
    val progressionData = calculateWeightProgression(completedWorkouts)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
    ) {
        // Header
        TopAppBar(
            title = {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Retour",
                            tint = Color.White
                        )
                    }
                    Text(
                        text = "📊 Statistiques",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
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
            // Statistiques générales
            item {
                StatsOverviewCard(
                    totalWorkouts = totalWorkouts,
                    totalMinutes = totalMinutes,
                    totalVolume = totalVolume,
                    averageDuration = averageDuration,
                    frequencyPerWeek = frequencyPerWeek
                )
            }

            // Graphique de fréquence mensuelle
            item {
                MonthlyFrequencyCard(workoutHistory = workoutHistory)
            }

            // Progression des charges
            if (progressionData.isNotEmpty()) {
                item {
                    WeightProgressionCard(progressionData = progressionData)
                }
            }

            // Exercices favoris
            if (exerciseFrequency.isNotEmpty()) {
                item {
                    FavoriteExercisesCard(exerciseFrequency = exerciseFrequency.take(5))
                }
            }

            // Analyse par objectif
            item {
                ObjectiveAnalysisCard(
                    profileData = profileData,
                    workoutHistory = workoutHistory
                )
            }

            // Répartition par groupe musculaire
            item {
                MuscleGroupDistributionCard(workoutHistory = workoutHistory)
            }
        }
    }
}

@Composable
fun StatsOverviewCard(
    totalWorkouts: Int,
    totalMinutes: Int,
    totalVolume: Double,
    averageDuration: Int,
    frequencyPerWeek: Double
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
                text = "📈 Vue d'ensemble",
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
                    icon = "🏋️",
                    label = "Séances",
                    value = totalWorkouts.toString()
                )
                StatItem(
                    icon = "⏱️",
                    label = "Heures",
                    value = "${totalMinutes / 60}h${totalMinutes % 60}m"
                )
                StatItem(
                    icon = "💪",
                    label = "Volume",
                    value = "${(totalVolume / 1000).toInt()}T"
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                StatItem(
                    icon = "📊",
                    label = "Durée moy.",
                    value = "${averageDuration}min"
                )
                StatItem(
                    icon = "📅",
                    label = "Fréquence",
                    value = "${String.format("%.1f", frequencyPerWeek)}/sem"
                )
                StatItem(
                    icon = "🎯",
                    label = "Régularité",
                    value = if (frequencyPerWeek >= 3) "Excellent" else if (frequencyPerWeek >= 2) "Bon" else "À améliorer"
                )
            }
        }
    }
}

@Composable
fun MonthlyFrequencyCard(workoutHistory: List<WorkoutEntry>) {
    val monthlyData = workoutHistory
        .groupBy { it.date.withDayOfMonth(1) }
        .mapValues { it.value.size }
        .toSortedMap()
        .toList()
        .takeLast(6)
        .toMap()

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "📅 Fréquence mensuelle",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            // Graphique en barres
            Canvas(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(150.dp)
            ) {
                drawMonthlyFrequencyChart(monthlyData)
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Légende
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                monthlyData.entries.toList().takeLast(3).forEach { (date, count) ->
                    Text(
                        text = "${date.format(DateTimeFormatter.ofPattern("MMM"))} ($count)",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun WeightProgressionCard(progressionData: List<Pair<String, List<Double>>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "📈 Progression des charges",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            progressionData.take(3).forEach { (exercise, weights) ->
                val base = weights.first()
                val progression = if (weights.size >= 2 && base != 0.0) {
                    ((weights.last() - base) / base * 100).toInt()
                } else 0

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = exercise,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Text(
                            text = "${weights.first().toInt()}kg → ${weights.last().toInt()}kg",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }

                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            imageVector = if (progression > 0) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                            contentDescription = "Progression",
                            tint = if (progression > 0) Color(0xFF4CAF50) else Color(0xFFF44336),
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "${if (progression > 0) "+" else ""}$progression%",
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (progression > 0) Color(0xFF4CAF50) else Color(0xFFF44336)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun FavoriteExercisesCard(exerciseFrequency: List<Pair<String, Int>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "⭐ Exercices favoris",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            exerciseFrequency.forEachIndexed { index, (exercise, count) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${index + 1}.",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold,
                            color = Accent,
                            modifier = Modifier.width(20.dp)
                        )
                        Text(
                            text = exercise,
                            fontSize = 14.sp,
                            modifier = Modifier.weight(1f)
                        )
                    }
                    Text(
                        text = "$count fois",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

@Composable
fun ObjectiveAnalysisCard(
    profileData: ProfileData,
    workoutHistory: List<WorkoutEntry>
) {
    val age = calculateAge(profileData.dateNaissance)
    val totalCalories = workoutHistory.sumOf {
        calculateBurnedCalories(profileData.poids, it.duration, "Modéré")
    }
    val goalCalories = calculateGoalBasedCalories(age, profileData.poids, profileData.taille, profileData.genre, profileData.niveauActivite, profileData.objectif)
    val recommendations = getObjectiveRecommendations(profileData.objectif, workoutHistory)

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFE8F5E8))
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "🎯 Analyse selon votre objectif",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            Text(
                text = "Objectif actuel : ${profileData.objectif}",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            Text(
                text = "Calories brûlées : $totalCalories kcal",
                fontSize = 14.sp,
                color = Color.Gray,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            Text(
                text = "Apport calorique recommandé : $goalCalories kcal/jour",
                fontSize = 14.sp,
                color = Color.Gray,
                modifier = Modifier.padding(bottom = 12.dp)
            )

            recommendations.forEach { recommendation ->
                Text(
                    text = "• $recommendation",
                    fontSize = 12.sp,
                    color = Color(0xFF666666),
                    modifier = Modifier.padding(vertical = 2.dp)
                )
            }
        }
    }
}

@Composable
fun MuscleGroupDistributionCard(workoutHistory: List<WorkoutEntry>) {
    val muscleGroups = workoutHistory.flatMap { it.exercises }
        .groupBy { getMuscleGroupFromExercise(it.name) }
        .mapValues { it.value.size }
        .toList()
        .sortedByDescending { it.second }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "🎯 Répartition par groupe musculaire",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            muscleGroups.forEach { (group, count) ->
                val totalCount = muscleGroups.sumOf { it.second }
                val percentage = if (totalCount > 0) (count.toFloat() / totalCount * 100).toInt() else 0

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = group,
                        fontSize = 14.sp,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        text = "$count ($percentage%)",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }
        }
    }
}

// Fonctions utilitaires
fun DrawScope.drawMonthlyFrequencyChart(monthlyData: Map<LocalDate, Int>) {
    if (monthlyData.isEmpty()) return

    val maxValue = monthlyData.values.maxOrNull() ?: 1
    val barWidth = size.width / monthlyData.size
    val barMaxHeight = size.height * 0.8f

    monthlyData.entries.forEachIndexed { index, (_, count) ->
        val barHeight = (count.toFloat() / maxValue * barMaxHeight)
        val x = index * barWidth + barWidth * 0.2f
        val barWidthActual = barWidth * 0.6f

        drawRect(
            color = Accent,
            topLeft = Offset(x, size.height - barHeight),
            size = androidx.compose.ui.geometry.Size(barWidthActual, barHeight)
        )
    }
}

fun calculateWeightProgression(workoutHistory: List<WorkoutEntry>): List<Pair<String, List<Double>>> {
    return workoutHistory.flatMap { it.exercises }
        .groupBy { it.name }
        .mapValues { (_, exercises) ->
            exercises.map { it.weight }
        }
        .filter { it.value.size >= 2 }
        .toList()
}

fun getObjectiveRecommendations(objectif: String, workoutHistory: List<WorkoutEntry>): List<String> {
    val recommendations = mutableListOf<String>()
    val totalWorkouts = workoutHistory.size

    when (objectif) {
        "Prise de masse" -> {
            recommendations.add("Privilégiez 3-4 séances par semaine avec charges lourdes")
            recommendations.add("Augmentez progressivement les poids de 2.5-5kg par semaine")
            if (totalWorkouts > 0) {
                recommendations.add("Maintenez une fréquence régulière pour optimiser la synthèse protéique")
            }
        }
        "Perdre du poids" -> {
            recommendations.add("Combinez musculation et cardio pour un déficit calorique")
            recommendations.add("Privilégiez les séances de 45-60 minutes")
            recommendations.add("Augmentez la fréquence à 4-5 séances par semaine")
        }
        "Force" -> {
            recommendations.add("Concentrez-vous sur les mouvements polyarticulaires")
            recommendations.add("Travaillez avec 85-95% de votre 1RM")
            recommendations.add("Repos longs entre séries (3-5 minutes)")
        }
        "Sèche" -> {
            recommendations.add("Maintenez l'intensité malgré le déficit calorique")
            recommendations.add("Privilégiez les superset et circuit training")
            recommendations.add("Augmentez le volume d'entraînement progressivement")
        }
    }

    return recommendations
}

fun getMuscleGroupFromExercise(exerciseName: String): String {
    return when {
        exerciseName.contains("Développé", ignoreCase = true) ||
        exerciseName.contains("Pec", ignoreCase = true) -> "Pectoraux"
        exerciseName.contains("Tirage", ignoreCase = true) ||
        exerciseName.contains("Rowing", ignoreCase = true) ||
        exerciseName.contains("Tractions", ignoreCase = true) -> "Dos"
        exerciseName.contains("Squat", ignoreCase = true) ||
        exerciseName.contains("Leg", ignoreCase = true) ||
        exerciseName.contains("Curl ischios", ignoreCase = true) -> "Jambes"
        exerciseName.contains("Curl biceps", ignoreCase = true) ||
        exerciseName.contains("Extension triceps", ignoreCase = true) -> "Bras"
        exerciseName.contains("Élévations", ignoreCase = true) ||
        exerciseName.contains("Militaire", ignoreCase = true) -> "Épaules"
        exerciseName.contains("Cardio", ignoreCase = true) ||
        exerciseName.contains("Tapis", ignoreCase = true) ||
        exerciseName.contains("Vélo", ignoreCase = true) ||
        exerciseName.contains("Rameur", ignoreCase = true) -> "Cardio"
        else -> "Autre"
    }
}
