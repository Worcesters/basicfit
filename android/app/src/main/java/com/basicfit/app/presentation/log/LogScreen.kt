package com.basicfit.app.presentation.log

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.basicfit.app.data.models.AppLog
import com.basicfit.app.data.models.LogLevel
import com.basicfit.app.data.repositories.LogStats
import com.basicfit.app.presentation.theme.*
import com.basicfit.app.utils.Logger
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LogScreen(
    viewModel: LogViewModel = viewModel(),
    logger: Logger
) {
    val currentView by viewModel.currentView.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val errorMessage by viewModel.errorMessage.collectAsState()
    val successMessage by viewModel.successMessage.collectAsState()
    val selectedLog by viewModel.selectedLog.collectAsState()

    // Gestion des messages
    LaunchedEffect(errorMessage) {
        errorMessage?.let {
            logger.error("LOG_UI", it)
        }
    }

    LaunchedEffect(successMessage) {
        successMessage?.let {
            logger.success("LOG_UI", it)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(LightBackground)
    ) {
        // Barre de navigation si pas en vue détails
        if (currentView != LogView.DETAILS) {
            LogNavigationBar(
                currentView = currentView,
                onViewChange = { viewModel.setView(it) },
                logCounts = viewModel.getLogCountByLevel()
            )
        }

        // Messages de status
        errorMessage?.let { message ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = ErrorRed.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = message,
                    color = ErrorRed,
                    modifier = Modifier.padding(16.dp),
                    fontWeight = FontWeight.SemiBold
                )
            }
        }

        successMessage?.let { message ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                colors = CardDefaults.cardColors(
                    containerColor = SuccessGreen.copy(alpha = 0.1f)
                )
            ) {
                Text(
                    text = message,
                    color = SuccessGreen,
                    modifier = Modifier.padding(16.dp),
                    fontWeight = FontWeight.SemiBold
                )
            }
        }

        // Contenu principal
        when (currentView) {
            LogView.LOGS -> {
                LogsViewContent(viewModel = viewModel, isLoading = isLoading)
            }
            LogView.STATS -> {
                StatsViewContent(viewModel = viewModel)
            }
            LogView.SETTINGS -> {
                SettingsViewContent(viewModel = viewModel)
            }
            LogView.DETAILS -> {
                selectedLog?.let { log ->
                    LogDetailsView(
                        log = log,
                        onBack = { viewModel.clearSelectedLog() }
                    )
                } ?: run {
                    // Retourner à la vue logs si aucun log sélectionné
                    LaunchedEffect(Unit) {
                        viewModel.setView(LogView.LOGS)
                    }
                }
            }
        }
    }

    // Effacer les messages après affichage
    LaunchedEffect(errorMessage, successMessage) {
        if (errorMessage != null || successMessage != null) {
            kotlinx.coroutines.delay(3000)
            viewModel.clearMessages()
        }
    }
}

@Composable
fun LogNavigationBar(
    currentView: LogView,
    onViewChange: (LogView) -> Unit,
    logCounts: Map<String, Int>
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(
            modifier = Modifier.padding(8.dp),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            LogViewButton(
                text = "Logs (${logCounts.values.sum()})",
                icon = Icons.Default.List,
                isSelected = currentView == LogView.LOGS,
                onClick = { onViewChange(LogView.LOGS) },
                badge = logCounts[LogLevel.ERROR.displayName] ?: 0,
                badgeColor = ErrorRed
            )

            LogViewButton(
                text = "Stats",
                icon = Icons.Default.Analytics,
                isSelected = currentView == LogView.STATS,
                onClick = { onViewChange(LogView.STATS) }
            )

            LogViewButton(
                text = "Actions",
                icon = Icons.Default.Settings,
                isSelected = currentView == LogView.SETTINGS,
                onClick = { onViewChange(LogView.SETTINGS) }
            )
        }
    }
}

@Composable
fun LogViewButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    isSelected: Boolean,
    onClick: () -> Unit,
    badge: Int = 0,
    badgeColor: Color = ErrorRed
) {
    Box {
        Column(
            modifier = Modifier
                .clip(RoundedCornerShape(12.dp))
                .clickable { onClick() }
                .background(if (isSelected) Mint.copy(alpha = 0.1f) else Color.Transparent)
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                icon,
                contentDescription = text,
                tint = if (isSelected) Mint else TextSecondary,
                modifier = Modifier.size(20.dp)
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = text,
                color = if (isSelected) Mint else TextSecondary,
                fontSize = 12.sp,
                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
            )
        }

        // Badge d'erreurs
        if (badge > 0) {
            Box(
                modifier = Modifier
                    .size(18.dp)
                    .background(badgeColor, RoundedCornerShape(9.dp))
                    .align(Alignment.TopEnd)
                    .offset(x = 4.dp, y = (-4).dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (badge > 99) "99+" else badge.toString(),
                    color = Color.White,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LogsViewContent(
    viewModel: LogViewModel,
    isLoading: Boolean
) {
    val filteredLogs by viewModel.filteredLogs.collectAsState()
    val selectedLogLevel by viewModel.selectedLogLevel.collectAsState()
    val selectedCategory by viewModel.selectedCategory.collectAsState()
    val availableCategories by viewModel.availableCategories.collectAsState()
    val availableLogLevels by viewModel.availableLogLevels.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Contrôles et filtres
        item {
            LogControlsCard(
                searchQuery = searchQuery,
                onSearchChange = { viewModel.updateSearchQuery(it) },
                selectedLogLevel = selectedLogLevel,
                selectedCategory = selectedCategory,
                availableLogLevels = availableLogLevels,
                availableCategories = availableCategories,
                onLogLevelChange = { viewModel.setLogLevelFilter(it) },
                onCategoryChange = { viewModel.setCategoryFilter(it) },
                onRefresh = { viewModel.refreshLogs() },
                onResetFilters = { viewModel.resetFilters() }
            )
        }

        // Liste des logs
        if (isLoading) {
            item {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = Mint)
                }
            }
        } else if (filteredLogs.isEmpty()) {
            item {
                EmptyLogsCard()
            }
        } else {
            items(filteredLogs) { log ->
                LogCard(
                    log = log,
                    onClick = {
                        viewModel.selectLog(log)
                        viewModel.setView(LogView.DETAILS)
                    }
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LogControlsCard(
    searchQuery: String,
    onSearchChange: (String) -> Unit,
    selectedLogLevel: LogLevel,
    selectedCategory: String,
    availableLogLevels: List<LogLevel>,
    availableCategories: List<String>,
    onLogLevelChange: (LogLevel) -> Unit,
    onCategoryChange: (String) -> Unit,
    onRefresh: () -> Unit,
    onResetFilters: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // Recherche
            OutlinedTextField(
                value = searchQuery,
                onValueChange = onSearchChange,
                label = { Text("Rechercher dans les logs") },
                leadingIcon = {
                    Icon(Icons.Default.Search, contentDescription = null)
                },
                trailingIcon = {
                    if (searchQuery.isNotEmpty()) {
                        IconButton(onClick = { onSearchChange("") }) {
                            Icon(Icons.Default.Clear, contentDescription = "Effacer")
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Mint,
                    focusedLabelColor = Mint
                )
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Filtres
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Niveau de log
                var expandedLevel by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = expandedLevel,
                    onExpandedChange = { expandedLevel = !expandedLevel },
                    modifier = Modifier.weight(1f)
                ) {
                    OutlinedTextField(
                        value = selectedLogLevel.displayName,
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Niveau") },
                        trailingIcon = {
                            ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedLevel)
                        },
                        modifier = Modifier
                            .menuAnchor()
                            .fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )

                    ExposedDropdownMenu(
                        expanded = expandedLevel,
                        onDismissRequest = { expandedLevel = false }
                    ) {
                        availableLogLevels.forEach { level ->
                            DropdownMenuItem(
                                text = { Text(level.displayName) },
                                onClick = {
                                    onLogLevelChange(level)
                                    expandedLevel = false
                                }
                            )
                        }
                    }
                }

                // Catégorie
                var expandedCategory by remember { mutableStateOf(false) }
                ExposedDropdownMenuBox(
                    expanded = expandedCategory,
                    onExpandedChange = { expandedCategory = !expandedCategory },
                    modifier = Modifier.weight(1f)
                ) {
                    OutlinedTextField(
                        value = selectedCategory,
                        onValueChange = {},
                        readOnly = true,
                        label = { Text("Catégorie") },
                        trailingIcon = {
                            ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedCategory)
                        },
                        modifier = Modifier
                            .menuAnchor()
                            .fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        )
                    )

                    ExposedDropdownMenu(
                        expanded = expandedCategory,
                        onDismissRequest = { expandedCategory = false }
                    ) {
                        availableCategories.forEach { category ->
                            DropdownMenuItem(
                                text = { Text(category) },
                                onClick = {
                                    onCategoryChange(category)
                                    expandedCategory = false
                                }
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = onResetFilters,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(Icons.Default.FilterAltOff, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Réinitialiser")
                }

                Button(
                    onClick = onRefresh,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = Mint)
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Actualiser")
                }
            }
        }
    }
}

@Composable
fun LogCard(
    log: AppLog,
    onClick: () -> Unit
) {
    val levelColor = when (log.level) {
        LogLevel.ERROR -> ErrorRed
        LogLevel.WARNING -> WarningOrange
        LogLevel.INFO -> InfoBlue
        LogLevel.DEBUG -> TextSecondary
        LogLevel.SUCCESS -> SuccessGreen
        else -> TextSecondary
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Row(
            modifier = Modifier.padding(16.dp)
        ) {
            // Indicateur de niveau
            Box(
                modifier = Modifier
                    .width(4.dp)
                    .height(48.dp)
                    .background(levelColor, RoundedCornerShape(2.dp))
            )

            Spacer(modifier = Modifier.width(12.dp))

            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = log.level.displayName,
                        color = levelColor,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Text(
                        text = log.getFormattedTimestamp(),
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                }

                Spacer(modifier = Modifier.height(4.dp))

                                    Text(
                        text = log.tag,
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold
                    )

                Spacer(modifier = Modifier.height(2.dp))

                Text(
                    text = log.message,
                    color = TextSecondary,
                    fontSize = 13.sp,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )

                if (log.exception != null) {
                    Spacer(modifier = Modifier.height(4.dp))

                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(
                            Icons.Default.BugReport,
                            contentDescription = "Exception disponible",
                            modifier = Modifier.size(12.dp),
                            tint = ErrorRed
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                        Text(
                            text = "Exception disponible",
                            color = ErrorRed,
                            fontSize = 11.sp,
                            fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
                        )
                    }
                }
            }

            Icon(
                Icons.Default.ChevronRight,
                contentDescription = "Voir détails",
                tint = TextSecondary,
                modifier = Modifier.size(16.dp)
            )
        }
    }
}

@Composable
fun EmptyLogsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Default.Receipt,
                contentDescription = null,
                modifier = Modifier.size(48.dp),
                tint = TextSecondary
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Aucun log trouvé",
                fontWeight = FontWeight.SemiBold,
                color = TextSecondary
            )

            Text(
                text = "Modifiez vos filtres ou effectuez des actions dans l'application",
                color = TextSecondary,
                fontSize = 14.sp,
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}

@Composable
fun LogDetailsView(
    log: AppLog,
    onBack: () -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // En-tête avec bouton retour
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(onClick = onBack) {
                    Icon(
                        Icons.Default.ArrowBack,
                        contentDescription = "Retour",
                        tint = Mint
                    )
                }

                Text(
                    text = "Détails du log",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = TextPrimary
                )
            }
        }

        // Détails du log
        item {
            LogDetailCard(log = log)
        }

        // Exception si disponible
        log.exception?.let { exception ->
            item {
                StackTraceCard(exception = exception)
            }
        }
    }
}

@Composable
fun LogDetailCard(log: AppLog) {
    val levelColor = when (log.level) {
        LogLevel.ERROR -> ErrorRed
        LogLevel.WARNING -> WarningOrange
        LogLevel.INFO -> InfoBlue
        LogLevel.DEBUG -> TextSecondary
        LogLevel.SUCCESS -> SuccessGreen
        else -> TextSecondary
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            // Niveau et timestamp
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = log.level.displayName,
                    color = levelColor,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )

                Text(
                    text = log.getFormattedTimestamp(),
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Tag
            LogDetailItem(
                label = "Tag",
                value = log.tag
            )

            Spacer(modifier = Modifier.height(12.dp))

            // ID
            LogDetailItem(
                label = "ID",
                value = log.id
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Message
            LogDetailItem(
                label = "Message",
                value = log.message,
                isLongText = true
            )

            log.details?.let { details ->
                Spacer(modifier = Modifier.height(12.dp))
                LogDetailItem(
                    label = "Détails",
                    value = details
                )
            }

            log.exception?.let { exception ->
                Spacer(modifier = Modifier.height(12.dp))
                LogDetailItem(
                    label = "Exception",
                    value = exception.message ?: "Aucun message"
                )
            }
        }
    }
}

@Composable
fun LogDetailItem(
    label: String,
    value: String,
    isLongText: Boolean = false
) {
    Column {
        Text(
            text = label,
            color = TextSecondary,
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = value,
            color = TextPrimary,
            fontSize = if (isLongText) 14.sp else 16.sp,
            fontFamily = if (isLongText) FontFamily.Default else FontFamily.Monospace
        )
    }
}

@Composable
fun StackTraceCard(stackTrace: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = ErrorRed.copy(alpha = 0.05f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.BugReport,
                    contentDescription = null,
                    tint = ErrorRed,
                    modifier = Modifier.size(20.dp)
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "Stack Trace",
                    color = ErrorRed,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = stackTrace,
                color = TextPrimary,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Color.Black.copy(alpha = 0.05f),
                        RoundedCornerShape(8.dp)
                    )
                    .padding(12.dp)
            )
        }
    }
}

@Composable
fun StackTraceCard(exception: Throwable) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = ErrorRed.copy(alpha = 0.05f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.BugReport,
                    contentDescription = null,
                    tint = ErrorRed,
                    modifier = Modifier.size(20.dp)
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "Exception",
                    color = ErrorRed,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = exception.stackTraceToString(),
                color = TextPrimary,
                fontSize = 12.sp,
                fontFamily = FontFamily.Monospace,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        Color.Black.copy(alpha = 0.05f),
                        RoundedCornerShape(8.dp)
                    )
                    .padding(12.dp)
            )
        }
    }
}

@Composable
fun StatsViewContent(
    viewModel: LogViewModel
) {
    val logStats by viewModel.logStats.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Statistiques des Logs",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        }

        logStats?.let { stats ->
            item {
                LogStatsOverviewCard(stats = stats)
            }

            if (stats.topCategories.isNotEmpty()) {
                item {
                    TopCategoriesCard(categories = stats.topCategories)
                }
            }

            if (stats.recentErrors.isNotEmpty()) {
                item {
                    RecentErrorsCard(
                        errors = stats.recentErrors,
                        onErrorClick = { log ->
                            viewModel.selectLog(log)
                            viewModel.setView(LogView.DETAILS)
                        }
                    )
                }
            }
        }
    }
}

@Composable
fun LogStatsOverviewCard(stats: LogStats) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(20.dp)
        ) {
            Text(
                text = "Aperçu général",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                LogStatItem(
                    value = stats.totalLogs.toString(),
                    label = "Total",
                    color = Mint
                )

                LogStatItem(
                    value = stats.errorCount.toString(),
                    label = "Erreurs",
                    color = ErrorRed
                )

                LogStatItem(
                    value = stats.warningCount.toString(),
                    label = "Avertissements",
                    color = WarningOrange
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                LogStatItem(
                    value = stats.infoCount.toString(),
                    label = "Info",
                    color = InfoBlue
                )

                LogStatItem(
                    value = stats.debugCount.toString(),
                    label = "Debug",
                    color = TextSecondary
                )

                // Espace vide pour équilibrer
                Box(modifier = Modifier.weight(1f))
            }
        }
    }
}

@Composable
fun LogStatItem(
    value: String,
    label: String,
    color: Color
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.fillMaxWidth()
    ) {
        Text(
            text = value,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = color
        )

        Text(
            text = label,
            fontSize = 12.sp,
            color = TextSecondary,
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
    }
}

@Composable
fun TopCategoriesCard(categories: List<Pair<String, Int>>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Top Catégories",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(12.dp))

            categories.forEach { (category, count) ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = category,
                        color = TextPrimary,
                        fontSize = 14.sp
                    )

                    Text(
                        text = count.toString(),
                        color = Mint,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))
            }
        }
    }
}

@Composable
fun RecentErrorsCard(
    errors: List<AppLog>,
    onErrorClick: (AppLog) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = ErrorRed.copy(alpha = 0.05f)
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.ErrorOutline,
                    contentDescription = null,
                    tint = ErrorRed,
                    modifier = Modifier.size(20.dp)
                )

                Spacer(modifier = Modifier.width(8.dp))

                Text(
                    text = "Erreurs récentes",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = ErrorRed
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            errors.take(5).forEach { error ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onErrorClick(error) }
                        .padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = error.tag,
                            color = TextPrimary,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold
                        )

                        Text(
                            text = error.message,
                            color = TextSecondary,
                            fontSize = 12.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }

                    Icon(
                        Icons.Default.ChevronRight,
                        contentDescription = "Voir détails",
                        tint = TextSecondary,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun SettingsViewContent(
    viewModel: LogViewModel
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text(
                text = "Actions et Paramètres",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
        }

        // Actions de synchronisation
        item {
            SyncActionsCard(
                onUploadLogs = { viewModel.uploadLocalLogs() },
                onRefreshLogs = { viewModel.refreshLogs() }
            )
        }

        // Actions de test
        item {
            TestActionsCard(
                onAddTestLog = { level, tag, message ->
                    viewModel.addTestLog(level.name, tag, message)
                }
            )
        }

        // Actions de nettoyage
        item {
            CleanupActionsCard(
                onClearLocal = { viewModel.clearLocalLogs() },
                onClearServer = { viewModel.clearServerLogs() },
                onExport = { viewModel.exportLogs() }
            )
        }
    }
}

@Composable
fun SyncActionsCard(
    onUploadLogs: () -> Unit,
    onRefreshLogs: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Synchronisation",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = onUploadLogs,
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = Mint)
            ) {
                Icon(Icons.Default.CloudUpload, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Synchroniser avec le serveur")
            }

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedButton(
                onClick = onRefreshLogs,
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.CloudDownload, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Recharger depuis le serveur")
            }
        }
    }
}

@Composable
fun TestActionsCard(
    onAddTestLog: (LogLevel, String, String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Tests et Débogage",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { onAddTestLog(LogLevel.INFO, "TEST", "Log de test INFO généré") },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = InfoBlue)
                ) {
                    Text("Test INFO")
                }

                Button(
                    onClick = { onAddTestLog(LogLevel.WARNING, "TEST", "Log de test WARNING généré") },
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = WarningOrange)
                ) {
                    Text("Test WARN")
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Button(
                onClick = { onAddTestLog(LogLevel.ERROR, "TEST", "Log de test ERROR avec exception") },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
            ) {
                Icon(Icons.Default.BugReport, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Générer Erreur de Test")
            }
        }
    }
}

@Composable
fun CleanupActionsCard(
    onClearLocal: () -> Unit,
    onClearServer: () -> Unit,
    onExport: () -> String
) {
    var showClearDialog by remember { mutableStateOf(false) }
    var clearType by remember { mutableStateOf("") }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Gestion des Logs",
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimary
            )

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = { onExport() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = SoftBlue)
            ) {
                Icon(Icons.Default.Download, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Exporter les logs")
            }

            Spacer(modifier = Modifier.height(8.dp))

            OutlinedButton(
                onClick = {
                    clearType = "local"
                    showClearDialog = true
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Icon(Icons.Default.ClearAll, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Effacer logs locaux")
            }

            Spacer(modifier = Modifier.height(8.dp))

            Button(
                onClick = {
                    clearType = "server"
                    showClearDialog = true
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = ErrorRed)
            ) {
                Icon(Icons.Default.DeleteForever, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Effacer logs serveur")
            }
        }
    }

    // Dialog de confirmation
    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = {
                Text("Confirmer la suppression")
            },
            text = {
                Text(
                    if (clearType == "local") {
                        "Êtes-vous sûr de vouloir effacer tous les logs locaux ?"
                    } else {
                        "Êtes-vous sûr de vouloir effacer tous les logs du serveur ? Cette action est irréversible."
                    }
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        when (clearType) {
                            "local" -> onClearLocal()
                            "server" -> onClearServer()
                        }
                        showClearDialog = false
                    }
                ) {
                    Text("Confirmer", color = ErrorRed)
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) {
                    Text("Annuler")
                }
            }
        )
    }
}

/**
 * Formater le timestamp d'un log pour affichage
 */
private fun formatLogTimestamp(timestamp: String): String {
    return try {
        val dateTime = LocalDateTime.parse(timestamp)
        dateTime.format(DateTimeFormatter.ofPattern("dd/MM HH:mm:ss"))
    } catch (e: Exception) {
        timestamp
    }
}