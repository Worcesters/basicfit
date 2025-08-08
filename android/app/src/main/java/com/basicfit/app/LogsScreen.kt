package com.basicfit.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.content.Intent
import android.widget.Toast

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LogsScreen() {
    val logs by AppLogger.logs.collectAsState()
    val context = LocalContext.current
    val clipboardManager = LocalClipboardManager.current
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header avec actions
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "📋 Logs Application",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                // Bouton Clear
                IconButton(
                    onClick = { 
                        AppLogger.clear()
                        Toast.makeText(context, "Logs effacés", Toast.LENGTH_SHORT).show()
                    }
                ) {
                    Icon(
                        Icons.Default.Clear,
                        contentDescription = "Effacer les logs",
                        tint = Color.Red
                    )
                }
                
                // Bouton Export/Share
                IconButton(
                    onClick = {
                        val logsText = AppLogger.exportLogs()
                        if (logsText.isNotEmpty()) {
                            val shareIntent = Intent().apply {
                                action = Intent.ACTION_SEND
                                type = "text/plain"
                                putExtra(Intent.EXTRA_TEXT, logsText)
                                putExtra(Intent.EXTRA_SUBJECT, "BasicFit Logs")
                            }
                            context.startActivity(Intent.createChooser(shareIntent, "Partager les logs"))
                        } else {
                            Toast.makeText(context, "Aucun log à exporter", Toast.LENGTH_SHORT).show()
                        }
                    }
                ) {
                    Icon(
                        Icons.Default.Share,
                        contentDescription = "Partager les logs",
                        tint = Accent
                    )
                }
            }
        }
        
        // Stats rapides
        if (logs.isNotEmpty()) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 16.dp),
                colors = CardDefaults.cardColors(containerColor = AccentLight)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    LogStatItem("Total", logs.size.toString())
                    LogStatItem("Erreurs", logs.count { it.level == AppLogger.LogLevel.ERROR }.toString())
                    LogStatItem("CSV", logs.count { it.level == AppLogger.LogLevel.CSV }.toString())
                    LogStatItem("API", logs.count { it.level == AppLogger.LogLevel.API }.toString())
                }
            }
        }
        
        // Liste des logs
        if (logs.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(
                        "📝 Aucun log pour le moment",
                        fontSize = 18.sp,
                        color = TextSecondary
                    )
                    Text(
                        "Les logs d'activité apparaîtront ici",
                        fontSize = 14.sp,
                        color = TextSecondary,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                }
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                items(logs) { log ->
                    LogItemCard(
                        log = log,
                        onLongClick = {
                            clipboardManager.setText(AnnotatedString(log.toString()))
                            Toast.makeText(context, "Log copié", Toast.LENGTH_SHORT).show()
                        }
                    )
                }
            }
        }
    }
}

@Composable
private fun LogStatItem(label: String, value: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = value,
            fontSize = 20.sp,
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun LogItemCard(
    log: AppLogger.LogEntry,
    onLongClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = when (log.level) {
                AppLogger.LogLevel.ERROR -> Color.Red.copy(alpha = 0.1f)
                AppLogger.LogLevel.WARNING -> Color(0xFFFFA500).copy(alpha = 0.1f) // Orange
                AppLogger.LogLevel.SUCCESS -> Color.Green.copy(alpha = 0.1f)
                AppLogger.LogLevel.CSV -> Color.Magenta.copy(alpha = 0.1f)
                AppLogger.LogLevel.API -> Color.Cyan.copy(alpha = 0.1f)
                else -> Color.Gray.copy(alpha = 0.05f)
            }
        ),
        onClick = onLongClick
    ) {
        Row(
            modifier = Modifier
                .padding(12.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.Top
        ) {
            // Timestamp
            Text(
                text = log.timestamp,
                fontSize = 10.sp,
                color = TextSecondary,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.width(60.dp)
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            // Level indicator
            Text(
                text = log.level.emoji,
                fontSize = 12.sp,
                modifier = Modifier.width(24.dp)
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            // Tag
            Text(
                text = log.tag,
                fontSize = 11.sp,
                color = log.level.color,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.width(80.dp),
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
            
            Spacer(modifier = Modifier.width(8.dp))
            
            // Message
            Text(
                text = log.message,
                fontSize = 12.sp,
                color = TextPrimary,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier.weight(1f),
                lineHeight = 16.sp
            )
        }
    }
}