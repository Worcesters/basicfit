package com.basicfit.app.ui.auth

import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.basicfit.app.data.AuthManager
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit,
    authManager: AuthManager
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var showConnectionTest by remember { mutableStateOf(false) }

    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo et titre
        Icon(
            painter = painterResource(id = android.R.drawable.ic_menu_preferences),
            contentDescription = "BasicFit Logo",
            modifier = Modifier.size(80.dp),
            tint = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "BasicFit",
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )

        Text(
            text = "Connectez-vous à votre compte",
            fontSize = 16.sp,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Champ email
        OutlinedTextField(
            value = email,
            onValueChange = {
                email = it
                errorMessage = null
            },
            label = { Text("Email") },
            leadingIcon = {
                Icon(Icons.Default.Email, contentDescription = null)
            },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            enabled = !isLoading
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Champ mot de passe
        OutlinedTextField(
            value = password,
            onValueChange = {
                password = it
                errorMessage = null
            },
            label = { Text("Mot de passe") },
            leadingIcon = {
                Icon(Icons.Default.Lock, contentDescription = null)
            },
            trailingIcon = {
                IconButton(onClick = { passwordVisible = !passwordVisible }) {
                    Icon(
                        if (passwordVisible) Icons.Default.VisibilityOff else Icons.Default.Visibility,
                        contentDescription = if (passwordVisible) "Masquer" else "Afficher"
                    )
                }
            },
            visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            enabled = !isLoading
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Message d'erreur
        if (errorMessage != null) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Text(
                    text = errorMessage!!,
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    modifier = Modifier.padding(12.dp),
                    fontSize = 14.sp
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
        } else {
            Spacer(modifier = Modifier.height(24.dp))
        }

        // Bouton de connexion
        Button(
            onClick = {
                if (email.isBlank() || password.isBlank()) {
                    errorMessage = "Veuillez remplir tous les champs"
                    return@Button
                }

                scope.launch {
                    isLoading = true
                    val result = authManager.login(email.trim(), password)
                    isLoading = false

                    if (result.isSuccess) {
                        onLoginSuccess()
                    } else {
                        errorMessage = result.exceptionOrNull()?.message ?: "Erreur de connexion"
                    }
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = !isLoading
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.size(20.dp)
                )
            } else {
                Icon(Icons.Default.Login, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Se connecter", fontSize = 16.sp)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Bouton d'inscription
        OutlinedButton(
            onClick = onNavigateToRegister,
            modifier = Modifier.fillMaxWidth(),
            enabled = !isLoading
        ) {
            Icon(Icons.Default.PersonAdd, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Créer un compte")
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Test de connexion
        TextButton(
            onClick = {
                scope.launch {
                    showConnectionTest = true
                    val result = authManager.testConnection()
                    showConnectionTest = false

                    if (result.isSuccess) {
                        errorMessage = "✅ ${result.getOrNull()}"
                    } else {
                        errorMessage = "❌ ${result.exceptionOrNull()?.message}"
                    }
                }
            },
            enabled = !isLoading && !showConnectionTest
        ) {
            if (showConnectionTest) {
                CircularProgressIndicator(modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(8.dp))
            }
            Text(
                text = "Tester la connexion au serveur",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.primary
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Version en mode démo
        TextButton(
            onClick = {
                // Connexion démo avec données locales
                email = "demo@basicfit.com"
                password = "demo123"
                // Simuler une connexion réussie locale
                onLoginSuccess()
            }
        ) {
            Text(
                text = "Mode démo (données locales)",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.outline
            )
        }
    }
}