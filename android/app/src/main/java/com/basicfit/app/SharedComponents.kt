package com.basicfit.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.time.format.DateTimeFormatter

@Composable
fun WorkoutDetailCard(
    workoutEntry: WorkoutEntry,
    onBack: () -> Unit,
    onStartWorkout: (WorkoutEntry) -> Unit = {}
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
            .padding(16.dp)
    ) {
        // Header avec bouton retour
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.Default.ArrowBack,
                    contentDescription = "Retour",
                    tint = Accent
                )
            }

            Text(
                text = "Détails de la séance",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Accent
            )

            Spacer(modifier = Modifier.width(48.dp)) // Pour centrer le titre
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Informations de la séance
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Séance du ${workoutEntry.date.format(DateTimeFormatter.ofPattern("dd/MM/yyyy"))}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Accent
                )

                if (workoutEntry.duration > 0) {
                    Text(
                        text = "Durée: ${workoutEntry.duration} minutes",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Bouton pour démarrer l'entraînement
                Button(
                    onClick = { onStartWorkout(workoutEntry) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = Accent)
                ) {
                    Text(
                        text = "🏋️ Démarrer l'entraînement",
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Liste des exercices avec GIFs
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(workoutEntry.exercises) { exercise ->
                ExerciseDetailCard(exercise = exercise)
            }
        }
    }
}

@Composable
fun ExerciseDetailCard(exercise: ExerciseRecord) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header de l'exercice
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = exercise.name,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Text(
                        text = "${exercise.sets} séries × ${exercise.reps} reps",
                        fontSize = 14.sp,
                        color = Color.Gray
                    )
                }

                Text(
                    text = "${exercise.weight.toInt()} kg",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color(0xFF4CAF50)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // GIF de démonstration (placeholder pour l'instant)
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFF0F0F0)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text(
                        text = "🎬 Démonstration",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Accent
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp)
                            .background(Color(0xFFE0E0E0)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "GIF de démonstration",
                            fontSize = 12.sp,
                            color = Color.Gray
                        )
                    }
                }
            }
        }
    }
}