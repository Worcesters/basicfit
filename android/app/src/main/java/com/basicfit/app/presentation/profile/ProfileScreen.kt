package com.basicfit.app.presentation.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.basicfit.app.data.models.User
import com.basicfit.app.data.models.UserStatistics
import com.basicfit.app.presentation.theme.*

/**
 * Écran du profil utilisateur
 * Affiche les informations personnelles et les statistiques d'entraînement
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel,
    onLogout: () -> Unit = {}
) {
    val currentUser by viewModel.currentUser.collectAsState()
    val statistics by viewModel.statistics.collectAsState()
    val isLoadingProfile by viewModel.isLoadingProfile.collectAsState()
    val isLoadingStats by viewModel.isLoadingStats.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val successMessage by viewModel.successMessage.collectAsState()
    val isEditMode by viewModel.isEditMode.collectAsState()
    
    // États pour les formulaires
    var nom by remember { mutableStateOf("") }
    var prenom by remember { mutableStateOf("") }
    var dateNaissance by remember { mutableStateOf("") }
    var poids by remember { mutableStateOf("") }
    var taille by remember { mutableStateOf("") }
    var genre by remember { mutableStateOf("") }
    var niveauActivite by remember { mutableStateOf("") }
    var objectif by remember { mutableStateOf("") }
    
    // Charger les statistiques au premier affichage
    LaunchedEffect(Unit) {
        viewModel.loadStatistics()
    }
    
    // Mettre à jour les champs quand l'utilisateur change
    LaunchedEffect(currentUser) {
        currentUser?.let { user ->
            nom = user.nom
            prenom = user.prenom
            dateNaissance = user.dateNaissance
            poids = if (user.poids > 0) user.poids.toString() else ""
            taille = if (user.taille > 0) user.taille.toString() else ""
            genre = user.genre
            niveauActivite = user.niveauActivite
            objectif = user.objectif
        }
    }
    
    // Gestion des messages
    LaunchedEffect(errorMessage) {
        if (errorMessage != null) {
            kotlinx.coroutines.delay(5000)
            viewModel.clearErrorMessage()
        }
    }
    
    LaunchedEffect(successMessage) {
        if (successMessage != null) {
            kotlinx.coroutines.delay(3000)
            viewModel.clearSuccessMessage()
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(LightBackground, Color.White)
                )
            )
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        
        // En-tête avec informations utilisateur
        ProfileHeader(
            user = currentUser,
            onEditClick = { viewModel.enableEditMode() },
            onLogoutClick = {
                viewModel.logout()
                onLogout()
            }
        )
        
        // Messages d'état
        errorMessage?.let { error ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Red.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = error,
                    modifier = Modifier.padding(16.dp),
                    color = Color.Red,
                    fontWeight = FontWeight.Medium
                )
            }
        }
        
        successMessage?.let { success ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Green.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = success,
                    modifier = Modifier.padding(16.dp),
                    color = Color.Green,
                    fontWeight = FontWeight.Medium
                )
            }
        }
        
        if (isEditMode) {
            // Mode édition
            ProfileEditForm(
                nom = nom,
                prenom = prenom,
                dateNaissance = dateNaissance,
                poids = poids,
                taille = taille,
                genre = genre,
                niveauActivite = niveauActivite,
                objectif = objectif,
                isLoading = isLoadingProfile,
                onNomChange = { nom = it },
                onPrenomChange = { prenom = it },
                onDateNaissanceChange = { dateNaissance = it },
                onPoidsChange = { poids = it },
                onTailleChange = { taille = it },
                onGenreChange = { genre = it },
                onNiveauActiviteChange = { niveauActivite = it },
                onObjectifChange = { objectif = it },
                onSaveClick = {
                    val poidsDouble = poids.toDoubleOrNull() ?: 0.0
                    val tailleInt = taille.toIntOrNull() ?: 0
                    
                    viewModel.updateProfile(
                        nom = nom,
                        prenom = prenom,
                        dateNaissance = dateNaissance,
                        poids = poidsDouble,
                        taille = tailleInt,
                        genre = genre,
                        niveauActivite = niveauActivite,
                        objectif = objectif
                    )
                },
                onCancelClick = { viewModel.disableEditMode() }
            )
        } else {
            // Mode affichage - Informations personnelles
            currentUser?.let { user ->
                ProfileInfoCard(user = user, viewModel = viewModel)
            }
            
            // Statistiques
            StatisticsCard(
                statistics = statistics,
                isLoading = isLoadingStats,
                onRefreshClick = { viewModel.loadStatistics() }
            )
        }
    }
}

@Composable
private fun ProfileHeader(
    user: User?,
    onEditClick: () -> Unit,
    onLogoutClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Mint.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                imageVector = Icons.Default.Person,
                contentDescription = null,
                modifier = Modifier.size(60.dp),
                tint = Mint
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = user?.getDisplayName() ?: "Utilisateur",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            
            Text(
                text = user?.email ?: "",
                fontSize = 14.sp,
                color = TextSecondary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = onEditClick,
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    )
                ) {
                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Modifier")
                }
                
                OutlinedButton(
                    onClick = onLogoutClick,
                    colors = ButtonDefaults.outlinedButtonColors(
                        contentColor = Color.Red
                    )
                ) {
                    Icon(
                        imageVector = Icons.Default.ExitToApp,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Déconnexion")
                }
            }
        }
    }
}

@Composable
private fun ProfileInfoCard(
    user: User,
    viewModel: ProfileViewModel
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "Informations personnelles",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            ProfileInfoRow(label = "Nom", value = user.nom.ifEmpty { "Non renseigné" })
            ProfileInfoRow(label = "Prénom", value = user.prenom.ifEmpty { "Non renseigné" })
            ProfileInfoRow(label = "Âge", value = user.getAge()?.let { "$it ans" } ?: "Non renseigné")
            ProfileInfoRow(label = "Poids", value = if (user.poids > 0) "${user.poids} kg" else "Non renseigné")
            ProfileInfoRow(label = "Taille", value = if (user.taille > 0) "${user.taille} cm" else "Non renseigné")
            ProfileInfoRow(label = "Genre", value = user.genre.ifEmpty { "Non renseigné" })
            ProfileInfoRow(label = "Niveau", value = user.niveauActivite.ifEmpty { "Non renseigné" })
            ProfileInfoRow(label = "Objectif", value = user.objectif.ifEmpty { "Maintenir" })
            
            // IMC si données disponibles
            val bmi = viewModel.calculateBMI()
            if (bmi != null) {
                Spacer(modifier = Modifier.height(12.dp))
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = SoftBlue.copy(alpha = 0.1f)
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "IMC: ${String.format("%.1f", bmi)}",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                        Text(
                            text = viewModel.getBMICategory(bmi),
                            fontSize = 14.sp,
                            color = TextSecondary
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ProfileInfoRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = "$label:",
            color = TextSecondary,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = value,
            color = TextPrimary,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.weight(2f),
            textAlign = TextAlign.End
        )
    }
}

@Composable
private fun StatisticsCard(
    statistics: UserStatistics?,
    isLoading: Boolean,
    onRefreshClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
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
                    text = "Statistiques d'entraînement",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = Mint
                    )
                } else {
                    IconButton(onClick = onRefreshClick) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Actualiser",
                            tint = Mint
                        )
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            if (statistics != null) {
                StatRow(label = "Séances totales", value = statistics.totalSeances.toString())
                StatRow(label = "Temps d'entraînement", value = "${statistics.totalMinutes} min")
                StatRow(label = "Calories brûlées", value = "${statistics.totalCalories} kcal")
                StatRow(label = "Séances excellentes", value = statistics.seancesExcellentes.toString())
                StatRow(label = "Record de poids", value = "${statistics.recordPoids} kg")
                StatRow(label = "Progression générale", value = "+${String.format("%.1f", statistics.progressionGenerale)} kg")
                
                if (statistics.exercicesFavoris.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "Exercices favoris:",
                        fontWeight = FontWeight.Medium,
                        color = TextSecondary
                    )
                    statistics.exercicesFavoris.take(3).forEach { exercice ->
                        Text(
                            text = "• $exercice",
                            color = TextPrimary,
                            modifier = Modifier.padding(start = 8.dp, top = 2.dp)
                        )
                    }
                }
            } else {
                Text(
                    text = "Aucune statistique disponible",
                    color = TextSecondary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
}

@Composable
private fun StatRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = "$label:",
            color = TextSecondary,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = value,
            color = TextPrimary,
            fontWeight = FontWeight.Medium,
            textAlign = TextAlign.End
        )
    }
}