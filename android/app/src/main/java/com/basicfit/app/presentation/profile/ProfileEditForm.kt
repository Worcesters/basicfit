package com.basicfit.app.presentation.profile

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.basicfit.app.presentation.theme.*

/**
 * Formulaire d'édition du profil utilisateur
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileEditForm(
    nom: String,
    prenom: String,
    dateNaissance: String,
    poids: String,
    taille: String,
    genre: String,
    niveauActivite: String,
    objectif: String,
    isLoading: Boolean,
    onNomChange: (String) -> Unit,
    onPrenomChange: (String) -> Unit,
    onDateNaissanceChange: (String) -> Unit,
    onPoidsChange: (String) -> Unit,
    onTailleChange: (String) -> Unit,
    onGenreChange: (String) -> Unit,
    onNiveauActiviteChange: (String) -> Unit,
    onObjectifChange: (String) -> Unit,
    onSaveClick: () -> Unit,
    onCancelClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Modifier le profil",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = TextPrimary
            )
            
            // Informations de base
            OutlinedTextField(
                value = nom,
                onValueChange = onNomChange,
                label = { Text("Nom") },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = {
                    Icon(imageVector = Icons.Default.Person, contentDescription = null)
                }
            )
            
            OutlinedTextField(
                value = prenom,
                onValueChange = onPrenomChange,
                label = { Text("Prénom") },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = {
                    Icon(imageVector = Icons.Default.Person, contentDescription = null)
                }
            )
            
            OutlinedTextField(
                value = dateNaissance,
                onValueChange = onDateNaissanceChange,
                label = { Text("Date de naissance (AAAA-MM-JJ)") },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = {
                    Icon(imageVector = Icons.Default.DateRange, contentDescription = null)
                },
                placeholder = { Text("1990-01-15") }
            )
            
            // Informations physiques
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedTextField(
                    value = poids,
                    onValueChange = onPoidsChange,
                    label = { Text("Poids (kg)") },
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    leadingIcon = {
                        Icon(imageVector = Icons.Default.FitnessCenter, contentDescription = null)
                    }
                )
                
                OutlinedTextField(
                    value = taille,
                    onValueChange = onTailleChange,
                    label = { Text("Taille (cm)") },
                    modifier = Modifier.weight(1f),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    leadingIcon = {
                        Icon(imageVector = Icons.Default.Height, contentDescription = null)
                    }
                )
            }
            
            // Genre
            Text(
                text = "Genre",
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            
            val genreOptions = listOf("Homme", "Femme", "Autre")
            genreOptions.forEach { option ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .selectable(
                            selected = (genre == option),
                            onClick = { onGenreChange(option) }
                        )
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = (genre == option),
                        onClick = { onGenreChange(option) },
                        colors = RadioButtonDefaults.colors(
                            selectedColor = Mint
                        )
                    )
                    Text(
                        text = option,
                        modifier = Modifier.padding(start = 8.dp)
                    )
                }
            }
            
            // Niveau d'activité
            Text(
                text = "Niveau d'activité",
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            
            val niveauOptions = listOf(
                "SEDENTAIRE" to "Sédentaire (peu ou pas d'exercice)",
                "LEGER" to "Léger (exercice léger 1-3 jours/semaine)",
                "MODERE" to "Modéré (exercice modéré 3-5 jours/semaine)",
                "ACTIF" to "Actif (exercice intense 6-7 jours/semaine)",
                "TRES_ACTIF" to "Très actif (exercice très intense 2x/jour)"
            )
            
            niveauOptions.forEach { (value, label) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .selectable(
                            selected = (niveauActivite == value),
                            onClick = { onNiveauActiviteChange(value) }
                        )
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = (niveauActivite == value),
                        onClick = { onNiveauActiviteChange(value) },
                        colors = RadioButtonDefaults.colors(
                            selectedColor = Mint
                        )
                    )
                    Text(
                        text = label,
                        modifier = Modifier.padding(start = 8.dp),
                        fontSize = 14.sp
                    )
                }
            }
            
            // Objectif
            Text(
                text = "Objectif d'entraînement",
                fontWeight = FontWeight.Medium,
                color = TextPrimary
            )
            
            val objectifOptions = listOf(
                "PRISE_MASSE" to "Prise de masse",
                "PERTE_POIDS" to "Perte de poids",
                "MAINTENIR" to "Maintenir la forme",
                "FORCE" to "Augmenter la force",
                "ENDURANCE" to "Améliorer l'endurance",
                "SECHE" to "Sèche/définition"
            )
            
            objectifOptions.forEach { (value, label) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .selectable(
                            selected = (objectif == value),
                            onClick = { onObjectifChange(value) }
                        )
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = (objectif == value),
                        onClick = { onObjectifChange(value) },
                        colors = RadioButtonDefaults.colors(
                            selectedColor = Mint
                        )
                    )
                    Text(
                        text = label,
                        modifier = Modifier.padding(start = 8.dp)
                    )
                }
            }
            
            // Boutons d'action
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = onCancelClick,
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading
                ) {
                    Text("Annuler")
                }
                
                Button(
                    onClick = onSaveClick,
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && nom.isNotBlank() && prenom.isNotBlank(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Mint
                    )
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(16.dp),
                            color = Color.White
                        )
                    } else {
                        Text("Enregistrer")
                    }
                }
            }
        }
    }
}