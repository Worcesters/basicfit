package com.basicfit.app.presentation.machines

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import coil.compose.AsyncImage
import coil.request.ImageRequest
import androidx.compose.ui.platform.LocalContext
import com.basicfit.app.data.models.Machine
import com.basicfit.app.presentation.theme.*

/**
 * Écran des machines d'exercice
 * Affiche la liste des machines avec recherche et filtres
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MachineScreen(
    viewModel: MachineViewModel,
    onMachineClick: (Machine) -> Unit = {}
) {
    val machines by viewModel.filteredMachines.collectAsState()
    val categories by viewModel.availableCategoryNames.collectAsState()
    val muscleGroups by viewModel.availableMuscleGroups.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val successMessage by viewModel.successMessage.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()
    val selectedCategory by viewModel.selectedCategory.collectAsState()
    val selectedMuscleGroup by viewModel.selectedMuscleGroup.collectAsState()
    
    var showMachineDetail by remember { mutableStateOf<Machine?>(null) }
    var showExportDialog by remember { mutableStateOf(false) }
    
    // Gestion des messages
    LaunchedEffect(errorMessage) {
        if (errorMessage != null) {
            kotlinx.coroutines.delay(5000)
            viewModel.clearMessages()
        }
    }
    
    LaunchedEffect(successMessage) {
        if (successMessage != null) {
            kotlinx.coroutines.delay(3000)
            viewModel.clearMessages()
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
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        
        // En-tête avec actions
        MachineHeader(
            totalMachines = machines.size,
            onExportClick = { showExportDialog = true },
            onRefreshClick = { viewModel.loadData() }
        )
        
        // Messages d'état
        errorMessage?.let { error ->
            MessageCard(message = error, isError = true)
        }
        
        successMessage?.let { success ->
            MessageCard(message = success, isError = false)
        }
        
        // Barre de recherche
        SearchBar(
            query = searchQuery,
            onQueryChange = viewModel::updateSearchQuery,
            onClearClick = { viewModel.updateSearchQuery("") }
        )
        
        // Filtres
        FilterSection(
            categories = categories,
            selectedCategory = selectedCategory,
            onCategorySelect = viewModel::selectCategory,
            muscleGroups = muscleGroups,
            selectedMuscleGroup = selectedMuscleGroup,
            onMuscleGroupSelect = viewModel::selectMuscleGroup,
            onResetFilters = viewModel::resetFilters
        )
        
        // Liste des machines
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    CircularProgressIndicator(color = Mint)
                    Text(
                        text = "Chargement des machines...",
                        color = TextSecondary
                    )
                }
            }
        } else if (machines.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.SearchOff,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = TextSecondary
                    )
                    Text(
                        text = if (searchQuery.isNotBlank() || selectedCategory != "Toutes" || selectedMuscleGroup != "Tous") 
                            "Aucune machine trouvée avec ces critères" 
                        else "Aucune machine disponible",
                        color = TextSecondary
                    )
                    if (searchQuery.isNotBlank() || selectedCategory != "Toutes" || selectedMuscleGroup != "Tous") {
                        OutlinedButton(
                            onClick = viewModel::resetFilters
                        ) {
                            Text("Réinitialiser les filtres")
                        }
                    }
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(machines) { machine ->
                    MachineCard(
                        machine = machine,
                        onClick = {
                            showMachineDetail = machine
                            onMachineClick(machine)
                        }
                    )
                }
            }
        }
    }
    
    // Dialogue de détail de machine
    showMachineDetail?.let { machine ->
        MachineDetailDialog(
            machine = machine,
            onDismiss = { showMachineDetail = null }
        )
    }
    
    // Dialogue d'export
    if (showExportDialog) {
        ExportDialog(
            onExport = {
                val exportContent = viewModel.exportMachines()
                // Ici on pourrait implémenter le partage via Intent
                showExportDialog = false
                exportContent
            },
            onDismiss = { showExportDialog = false }
        )
    }
}

@Composable
private fun MachineHeader(
    totalMachines: Int,
    onExportClick: () -> Unit,
    onRefreshClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Mint.copy(alpha = 0.1f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Machines d'exercice",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                Text(
                    text = "$totalMachines machines disponibles",
                    color = TextSecondary
                )
            }
            
            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                IconButton(onClick = onRefreshClick) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = "Actualiser",
                        tint = Mint
                    )
                }
                
                IconButton(onClick = onExportClick) {
                    Icon(
                        imageVector = Icons.Default.Download,
                        contentDescription = "Exporter",
                        tint = Mint
                    )
                }
            }
        }
    }
}

@Composable
private fun MessageCard(
    message: String,
    isError: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isError) 
                ErrorRed.copy(alpha = 0.1f) 
            else 
                SuccessGreen.copy(alpha = 0.1f)
        )
    ) {
        Text(
            text = message,
            modifier = Modifier.padding(16.dp),
            color = if (isError) ErrorRed else SuccessGreen,
            fontWeight = FontWeight.Medium
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    onClearClick: () -> Unit
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = Modifier.fillMaxWidth(),
        placeholder = { Text("Rechercher une machine...") },
        leadingIcon = {
            Icon(
                imageVector = Icons.Default.Search,
                contentDescription = null,
                tint = Mint
            )
        },
        trailingIcon = {
            if (query.isNotBlank()) {
                IconButton(onClick = onClearClick) {
                    Icon(
                        imageVector = Icons.Default.Clear,
                        contentDescription = "Effacer",
                        tint = TextSecondary
                    )
                }
            }
        }
    )
}

@Composable
private fun FilterSection(
    categories: List<String>,
    selectedCategory: String,
    onCategorySelect: (String) -> Unit,
    muscleGroups: List<String>,
    selectedMuscleGroup: String,
    onMuscleGroupSelect: (String) -> Unit,
    onResetFilters: () -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Filtres",
                fontSize = 16.sp,
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            
            if (selectedCategory != "Toutes" || selectedMuscleGroup != "Tous") {
                TextButton(onClick = onResetFilters) {
                    Text("Réinitialiser")
                }
            }
        }
        
        // Filtres par catégorie
        if (categories.isNotEmpty()) {
            Text(
                text = "Catégorie",
                fontSize = 14.sp,
                color = TextSecondary
            )
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(categories) { category ->
                    FilterChip(
                        selected = selectedCategory == category,
                        onClick = { onCategorySelect(category) },
                        label = { Text(category) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Mint.copy(alpha = 0.2f),
                            selectedLabelColor = TextPrimary
                        )
                    )
                }
            }
        }
        
        // Filtres par groupe musculaire
        if (muscleGroups.isNotEmpty()) {
            Text(
                text = "Groupe musculaire",
                fontSize = 14.sp,
                color = TextSecondary
            )
            LazyRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(muscleGroups) { muscleGroup ->
                    FilterChip(
                        selected = selectedMuscleGroup == muscleGroup,
                        onClick = { onMuscleGroupSelect(muscleGroup) },
                        label = { Text(muscleGroup) },
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = SoftBlue.copy(alpha = 0.2f),
                            selectedLabelColor = TextPrimary
                        )
                    )
                }
            }
        }
    }
}

@Composable
private fun MachineCard(
    machine: Machine,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Image de la machine
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(LightBackground),
                contentAlignment = Alignment.Center
            ) {
                if (machine.imageGif != null) {
                    AsyncImage(
                        model = ImageRequest.Builder(LocalContext.current)
                            .data(machine.imageGif)
                            .crossfade(true)
                            .build(),
                        contentDescription = machine.nom,
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.FitnessCenter,
                        contentDescription = null,
                        modifier = Modifier.size(32.dp),
                        tint = TextSecondary
                    )
                }
            }
            
            // Informations de la machine
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = machine.nom,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                
                if (machine.description.isNotBlank()) {
                    Text(
                        text = machine.description,
                        fontSize = 14.sp,
                        color = TextSecondary,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Catégorie
                    Box(
                        modifier = Modifier
                            .background(
                                color = Mint.copy(alpha = 0.1f),
                                shape = RoundedCornerShape(4.dp)
                            )
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = machine.getMainCategory(),
                            fontSize = 12.sp,
                            color = Mint,
                            fontWeight = FontWeight.Medium
                        )
                    }
                    
                    // Groupe musculaire
                    if (machine.groupeMusculaire.isNotBlank()) {
                        Box(
                            modifier = Modifier
                                .background(
                                    color = SoftBlue.copy(alpha = 0.1f),
                                    shape = RoundedCornerShape(4.dp)
                                )
                                .padding(horizontal = 8.dp, vertical = 4.dp)
                        ) {
                            Text(
                                text = machine.groupeMusculaire,
                                fontSize = 12.sp,
                                color = SoftBlue,
                                fontWeight = FontWeight.Medium
                            )
                        }
                    }
                }
            }
            
            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = TextSecondary
            )
        }
    }
}

@Composable
private fun MachineDetailDialog(
    machine: Machine,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
                    .padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // En-tête
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = machine.nom,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary,
                        modifier = Modifier.weight(1f)
                    )
                    
                    IconButton(onClick = onDismiss) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Fermer"
                        )
                    }
                }
                
                // Image
                if (machine.imageGif != null) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .background(LightBackground),
                        contentAlignment = Alignment.Center
                    ) {
                        AsyncImage(
                            model = ImageRequest.Builder(LocalContext.current)
                                .data(machine.imageGif)
                                .crossfade(true)
                                .build(),
                            contentDescription = machine.nom,
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                    }
                }
                
                // Informations détaillées
                DetailRow("Description", machine.description.ifEmpty { "Non disponible" })
                DetailRow("Catégorie", machine.getMainCategory())
                DetailRow("Groupe musculaire", machine.groupeMusculaire.ifEmpty { "Non spécifié" })
                DetailRow("Type d'exercice", if (machine.isCardio()) "Cardio" else "Musculation")
                DetailRow("Poids minimum", "${machine.poidsMinimum} kg")
                DetailRow("Poids maximum", "${machine.poidsMaximum} kg")
                DetailRow("Incrément", "${machine.incrementPoids} kg")
                
                // Instructions
                if (machine.instructions.isNotBlank()) {
                    Divider()
                    Text(
                        text = "Instructions d'utilisation",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold,
                        color = TextPrimary
                    )
                    Text(
                        text = machine.instructions,
                        fontSize = 14.sp,
                        color = TextSecondary,
                        lineHeight = 20.sp
                    )
                }
            }
        }
    }
}

@Composable
private fun DetailRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
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
            modifier = Modifier.weight(2f)
        )
    }
}

@Composable
private fun ExportDialog(
    onExport: () -> String,
    onDismiss: () -> Unit
) {
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "Exporter les machines",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                
                Text(
                    text = "Voulez-vous exporter la liste des machines en format texte ?",
                    color = TextSecondary
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Annuler")
                    }
                    
                    Button(
                        onClick = {
                            onExport()
                        },
                        modifier = Modifier.weight(1f),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Mint
                        )
                    ) {
                        Text("Exporter")
                    }
                }
            }
        }
    }
}