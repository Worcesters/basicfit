package com.basicfit.app.presentation.auth

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
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
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.basicfit.app.data.models.User
import com.basicfit.app.di.AppModule
import com.basicfit.app.presentation.theme.*
import com.basicfit.app.utils.Logger
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AuthScreen(
    onAuthSuccess: (User) -> Unit,
    logger: Logger
) {
    var isLoginMode by remember { mutableStateOf(true) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var nom by remember { mutableStateOf("") }
    var prenom by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var isPasswordVisible by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    val scope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        Mint.copy(alpha = 0.1f),
                        SoftBlue.copy(alpha = 0.1f),
                        LightBackground
                    )
                )
            )
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo et titre
        Icon(
            Icons.Default.FitnessCenter,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = Mint
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "BasicFit",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = TextPrimary
        )
        
        Text(
            text = if (isLoginMode) "Connectez-vous" else "Créez votre compte",
            fontSize = 16.sp,
            color = TextSecondary,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Formulaire
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color.White.copy(alpha = 0.95f)
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                // Message d'erreur
                errorMessage?.let { error ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.errorContainer
                        )
                    ) {
                        Text(
                            text = error,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(12.dp),
                            fontSize = 14.sp
                        )
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                // Champs pour l'inscription
                if (!isLoginMode) {
                    OutlinedTextField(
                        value = prenom,
                        onValueChange = { prenom = it },
                        label = { Text("Prénom") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        ),
                        singleLine = true
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedTextField(
                        value = nom,
                        onValueChange = { nom = it },
                        label = { Text("Nom") },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        ),
                        singleLine = true
                    )
                    
                    Spacer(modifier = Modifier.height(12.dp))
                }
                
                // Email
                OutlinedTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = { Text("Email") },
                    modifier = Modifier.fillMaxWidth(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Mint,
                        focusedLabelColor = Mint
                    ),
                    leadingIcon = {
                        Icon(Icons.Default.Email, contentDescription = null)
                    },
                    singleLine = true
                )
                
                Spacer(modifier = Modifier.height(12.dp))
                
                // Mot de passe
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("Mot de passe") },
                    modifier = Modifier.fillMaxWidth(),
                    visualTransformation = if (isPasswordVisible) {
                        VisualTransformation.None
                    } else {
                        PasswordVisualTransformation()
                    },
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Mint,
                        focusedLabelColor = Mint
                    ),
                    leadingIcon = {
                        Icon(Icons.Default.Lock, contentDescription = null)
                    },
                    trailingIcon = {
                        IconButton(onClick = { isPasswordVisible = !isPasswordVisible }) {
                            Icon(
                                if (isPasswordVisible) Icons.Default.Visibility else Icons.Default.VisibilityOff,
                                contentDescription = if (isPasswordVisible) "Masquer" else "Afficher"
                            )
                        }
                    },
                    singleLine = true
                )
                
                // Confirmation mot de passe pour inscription
                if (!isLoginMode) {
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    OutlinedTextField(
                        value = confirmPassword,
                        onValueChange = { confirmPassword = it },
                        label = { Text("Confirmer le mot de passe") },
                        modifier = Modifier.fillMaxWidth(),
                        visualTransformation = PasswordVisualTransformation(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Mint,
                            focusedLabelColor = Mint
                        ),
                        leadingIcon = {
                            Icon(Icons.Default.Lock, contentDescription = null)
                        },
                        singleLine = true
                    )
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Bouton principal
                Button(
                    onClick = {
                        scope.launch {
                            if (isLoginMode) {
                                performLogin(email, password) { user, error ->
                                    if (user != null) {
                                        onAuthSuccess(user)
                                    } else {
                                        errorMessage = error
                                    }
                                    isLoading = false
                                }
                            } else {
                                performRegister(email, password, confirmPassword, nom, prenom) { user, error ->
                                    if (user != null) {
                                        onAuthSuccess(user)
                                    } else {
                                        errorMessage = error
                                    }
                                    isLoading = false
                                }
                            }
                            isLoading = true
                            errorMessage = null
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    ),
                    enabled = !isLoading && email.isNotBlank() && password.isNotBlank() &&
                            (isLoginMode || (nom.isNotBlank() && prenom.isNotBlank() && confirmPassword.isNotBlank())),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = Color.White,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Icon(
                            if (isLoginMode) Icons.Default.Login else Icons.Default.PersonAdd,
                            contentDescription = null
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            if (isLoginMode) "Se connecter" else "S'inscrire",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Bouton de basculement
                TextButton(
                    onClick = { 
                        isLoginMode = !isLoginMode
                        errorMessage = null
                        password = ""
                        confirmPassword = ""
                    },
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = if (isLoginMode) {
                            "Pas encore de compte ? S'inscrire"
                        } else {
                            "Déjà un compte ? Se connecter"
                        },
                        color = Mint,
                        fontSize = 14.sp
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Information version
        Text(
            text = "BasicFit v2.0 • Application de fitness",
            color = TextSecondary,
            fontSize = 12.sp,
            textAlign = TextAlign.Center
        )
    }
}

/**
 * Effectuer la connexion
 */
private suspend fun performLogin(
    email: String,
    password: String,
    callback: (User?, String?) -> Unit
) {
    try {
        val result = AppModule.authRepository.login(email, password)
        if (result.isSuccess) {
            val user = result.getOrNull()
            callback(user, null)
        } else {
            val error = result.exceptionOrNull()?.message ?: "Erreur de connexion"
            callback(null, error)
        }
    } catch (e: Exception) {
        callback(null, "Erreur réseau: ${e.message}")
    }
}

/**
 * Effectuer l'inscription
 */
private suspend fun performRegister(
    email: String,
    password: String,
    confirmPassword: String,
    nom: String,
    prenom: String,
    callback: (User?, String?) -> Unit
) {
    try {
        // Validations côté client
        if (password != confirmPassword) {
            callback(null, "Les mots de passe ne correspondent pas")
            return
        }
        
        if (password.length < 6) {
            callback(null, "Le mot de passe doit contenir au moins 6 caractères")
            return
        }
        
        if (!email.contains("@")) {
            callback(null, "Email invalide")
            return
        }
        
        val result = AppModule.authRepository.register(email, password, nom, prenom)
        if (result.isSuccess) {
            val user = result.getOrNull()
            callback(user, null)
        } else {
            val error = result.exceptionOrNull()?.message ?: "Erreur d'inscription"
            callback(null, error)
        }
    } catch (e: Exception) {
        callback(null, "Erreur réseau: ${e.message}")
    }
}