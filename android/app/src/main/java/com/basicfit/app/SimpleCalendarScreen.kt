package com.basicfit.app

import android.content.Context
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.basicfit.app.data.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.InputStreamReader
import java.time.LocalDate
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SimpleCalendarScreen() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiService = remember { ApiService.getInstance().apply { initialize(context) } }

    // États pour la UI
    var sessions by remember { mutableStateOf<List<SimpleSession>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var showDeleteDialog by remember { mutableStateOf(false) }
    var showImportDialog by remember { mutableStateOf(false) }

    // État pour la synchronisation
    var lastSyncTime by remember { mutableStateOf(0L) }

    // Launcher pour sélection CSV
    val csvLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { uri ->
        if (uri != null) {
            coroutineScope.launch {
                importCsvFile(context, uri, apiService) { success, message ->
                    if (success) {
                        Toast.makeText(context, "Import réussi: $message", Toast.LENGTH_SHORT).show()
                        coroutineScope.launch {
                            loadSessions(apiService) { newSessions ->
                                sessions = newSessions
                            }
                        }
                    } else {
                        Toast.makeText(context, "Erreur import: $message", Toast.LENGTH_LONG).show()
                    }
                }
            }
        }
    }

    // Fonction pour charger les séances
    fun loadSessions() {
        if (isLoading) return
        
        coroutineScope.launch {
            isLoading = true
            errorMessage = null
            
            try {
                apiService.getSimpleSessions().onSuccess { newSessions ->
                    sessions = newSessions
                    lastSyncTime = System.currentTimeMillis()
                }.onFailure { error ->
                    errorMessage = error.message
                }
            } catch (e: Exception) {
                errorMessage = e.message
            } finally {
                isLoading = false
            }
        }
    }

    // Fonction pour supprimer toutes les séances
    fun deleteAllSessions() {
        coroutineScope.launch {
            isLoading = true
            try {
                apiService.deleteAllSessions().onSuccess { response ->
                    if (response.success) {
                        sessions = emptyList()
                        Toast.makeText(context, response.message, Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, "Erreur: ${response.message}", Toast.LENGTH_SHORT).show()
                    }
                }.onFailure { error ->
                    Toast.makeText(context, "Erreur: ${error.message}", Toast.LENGTH_SHORT).show()
                }
            } finally {
                isLoading = false
                showDeleteDialog = false
            }
        }
    }

    // Chargement automatique au démarrage
    LaunchedEffect(Unit) {
        loadSessions()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFFF5F5F5))
            .padding(16.dp)
    ) {
        // Header avec titre et actions
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(4.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "📅 Calendrier Simple CSV",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Import CSV avec format: machine,date,type",
                    fontSize = 14.sp,
                    color = TextSecondary
                )
                
                Spacer(modifier = Modifier.height(16.dp))

                // Boutons d'actions
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        onClick = { loadSessions() },
                        enabled = !isLoading,
                        colors = ButtonDefaults.buttonColors(containerColor = Accent),
                        modifier = Modifier.weight(1f)
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(16.dp),
                                color = Color.White,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        Text(if (isLoading) "Sync..." else "🔄 Sync")
                    }

                    Button(
                        onClick = { csvLauncher.launch(arrayOf("text/*", "application/*", "*/*")) },
                        colors = ButtonDefaults.buttonColors(containerColor = SoftBlue),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("📂 Import CSV")
                    }

                    Button(
                        onClick = { showDeleteDialog = true },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFE57373)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("🗑️ Vider")
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Affichage des erreurs
        errorMessage?.let { error ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFEBEE))
            ) {
                Text(
                    text = "❌ $error",
                    modifier = Modifier.padding(16.dp),
                    color = Color(0xFFD32F2F)
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
        }

        // Statistiques
        if (sessions.isNotEmpty()) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = AccentLight)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceAround
                ) {
                    StatCard("📊", sessions.size.toString(), "Total séances")
                    StatCard("📅", sessions.groupBy { it.date }.size.toString(), "Jours")
                    StatCard("🏋️", sessions.groupBy { it.machine }.size.toString(), "Machines")
                    StatCard("🔥", sessions.groupBy { it.type }.size.toString(), "Types")
                }
            }
            Spacer(modifier = Modifier.height(16.dp))
        }

        // Liste des séances
        if (sessions.isEmpty() && !isLoading) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "📭",
                        fontSize = 48.sp,
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "Aucune séance trouvée",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Importez un fichier CSV pour commencer",
                        fontSize = 14.sp,
                        color = TextSecondary,
                        textAlign = TextAlign.Center
                    )
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(
                    sessions.sortedByDescending { it.date }
                ) { session ->
                    SessionCard(session = session)
                }
            }
        }

        // Dialog de confirmation suppression
        if (showDeleteDialog) {
            AlertDialog(
                onDismissRequest = { showDeleteDialog = false },
                title = { Text("⚠️ Supprimer toutes les séances") },
                text = { 
                    Text("Cette action supprimera définitivement TOUTES vos séances de la base de données. Cette action ne peut pas être annulée.\n\nÊtes-vous sûr de vouloir continuer ?")
                },
                confirmButton = {
                    Button(
                        onClick = { deleteAllSessions() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F))
                    ) {
                        Text("Supprimer", color = Color.White)
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
}

@Composable
private fun StatCard(icon: String, value: String, label: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = icon,
            fontSize = 20.sp
        )
        Text(
            text = value,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = TextSecondary
        )
    }
}

@Composable
private fun SessionCard(session: SimpleSession) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = session.machine,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium,
                        color = TextPrimary
                    )
                    Text(
                        text = session.date.format(DateTimeFormatter.ofPattern("dd/MM/yyyy")),
                        fontSize = 14.sp,
                        color = TextSecondary
                    )
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Card(
                        colors = CardDefaults.cardColors(
                            containerColor = when (session.type) {
                                SessionType.CARDIO -> Color(0xFFE3F2FD)
                                SessionType.MUSCULATION -> Color(0xFFF3E5F5)
                                SessionType.FORCE -> Color(0xFFFFE0B2)
                                SessionType.ENDURANCE -> Color(0xFFE8F5E8)
                                SessionType.GAINAGE -> Color(0xFFFFF3E0)
                                SessionType.AUTRE -> Color(0xFFF5F5F5)
                            }
                        )
                    ) {
                        Text(
                            text = session.type.displayName,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            color = when (session.type) {
                                SessionType.CARDIO -> Color(0xFF1976D2)
                                SessionType.MUSCULATION -> Color(0xFF7B1FA2)
                                SessionType.FORCE -> Color(0xFFE65100)
                                SessionType.ENDURANCE -> Color(0xFF388E3C)
                                SessionType.GAINAGE -> Color(0xFFF57C00)
                                SessionType.AUTRE -> Color(0xFF616161)
                            }
                        )
                    }
                }
            }

            // Informations supplémentaires si disponibles
            if (session.duree != null || session.note != null) {
                Spacer(modifier = Modifier.height(8.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    session.duree?.let { duree ->
                        Text(
                            text = "⏱️ ${duree}min",
                            fontSize = 12.sp,
                            color = TextSecondary
                        )
                    }
                    session.note?.let { note ->
                        Text(
                            text = "⭐ $note/10",
                            fontSize = 12.sp,
                            color = TextSecondary
                        )
                    }
                }
            }

            // Commentaire si disponible
            if (session.commentaire.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "💬 ${session.commentaire}",
                    fontSize = 12.sp,
                    color = TextSecondary,
                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                )
            }
        }
    }
}

// Fonctions utilitaires
private suspend fun loadSessions(
    apiService: ApiService,
    onResult: (List<SimpleSession>) -> Unit
) = withContext(Dispatchers.IO) {
    try {
        apiService.getSimpleSessions().onSuccess { sessions ->
            withContext(Dispatchers.Main) {
                onResult(sessions)
            }
        }
    } catch (e: Exception) {
        withContext(Dispatchers.Main) {
            onResult(emptyList())
        }
    }
}

private suspend fun importCsvFile(
    context: Context,
    uri: Uri,
    apiService: ApiService,
    onResult: (Boolean, String) -> Unit
) = withContext(Dispatchers.IO) {
    try {
        AppLogger.csv("SIMPLE_CSV", "🚀 Début import CSV simple depuis URI: $uri")
        
        // Lire le fichier CSV
        val csvContent = context.contentResolver.openInputStream(uri)?.use { inputStream ->
            BufferedReader(InputStreamReader(inputStream)).use { reader ->
                reader.readText()
            }
        } ?: throw Exception("Impossible de lire le fichier")

        AppLogger.d("SIMPLE_CSV", "📄 Fichier CSV lu: ${csvContent.length} caractères")
        AppLogger.d("SIMPLE_CSV", "   Premières lignes: ${csvContent.take(300)}...")
        
        if (csvContent.isBlank()) {
            AppLogger.w("SIMPLE_CSV", "⚠️ Fichier CSV vide")
            withContext(Dispatchers.Main) {
                onResult(false, "Le fichier CSV est vide")
            }
            return@withContext
        }

        // Importer via l'API
        AppLogger.api("SIMPLE_CSV", "📤 Appel API import CSV")
        apiService.importCsvSessions(csvContent).onSuccess { response ->
            AppLogger.success("SIMPLE_CSV", "✅ Réponse API reçue: success=${response.success}")
            AppLogger.d("SIMPLE_CSV", "   Message: ${response.message}")
            AppLogger.d("SIMPLE_CSV", "   Imported count: ${response.imported_count}")
            
            withContext(Dispatchers.Main) {
                if (response.success) {
                    onResult(true, "${response.imported_count} séances importées")
                } else {
                    AppLogger.w("SIMPLE_CSV", "⚠️ API success=false: ${response.message}")
                    onResult(false, response.message)
                }
            }
        }.onFailure { error ->
            AppLogger.e("SIMPLE_CSV", "❌ Échec appel API: ${error.message}", error)
            withContext(Dispatchers.Main) {
                onResult(false, error.message ?: "Erreur inconnue")
            }
        }
    } catch (e: Exception) {
        withContext(Dispatchers.Main) {
            onResult(false, e.message ?: "Erreur lors de la lecture du fichier")
        }
    }
}