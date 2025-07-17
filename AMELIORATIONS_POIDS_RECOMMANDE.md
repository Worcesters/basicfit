# Améliorations du système de calcul de poids recommandé

## 🎯 Problème initial
- Le calcul de poids recommandé retournait des valeurs incorrectes quand il n'y avait pas d'historique
- Pas de distinction claire entre "pas d'historique" et "poids calculé"
- Interface utilisateur confuse

## ✅ Solutions implémentées

### 1. **Gestion des cas sans historique**
```kotlin
// Avant : Retournait des valeurs par défaut
val baseWeight = when (machine.groupeMusculairePrimaire) {
    "Pectoraux" -> 30.0
    // ...
}

// Après : Retourne 0.0 pour indiquer "à déterminer"
if (exerciseHistory.isEmpty()) {
    return 0.0
}
```

### 2. **Affichage amélioré dans l'interface**
```kotlin
// Affichage conditionnel selon l'historique
val weightDisplay = when {
    exerciseSession.recommendedWeight > 0 -> "${exerciseSession.recommendedWeight.toInt()} kg"
    exerciseSession.recommendedWeight == 0.0 -> "Poids à déterminer"
    else -> "Poids à déterminer"
}
```

### 3. **Suggestions de départ intelligentes**
```kotlin
// Nouvelle fonction pour calculer des suggestions
fun calculateSuggestedStartingWeight(machine: Machine, objectif: String): Double {
    val baseWeight = when {
        machine.groupeMusculairePrimaire.contains("Pectoraux", ignoreCase = true) -> 30.0
        machine.groupeMusculairePrimaire.contains("Dos", ignoreCase = true) -> 25.0
        // ...
    }
    return when (objectif) {
        "Force" -> baseWeight * 0.8
        "Prise de masse" -> baseWeight
        // ...
    }
}
```

### 4. **Interface utilisateur améliorée**

#### Placeholder intelligent :
```kotlin
placeholder = {
    Text(
        when {
            exerciseSession.recommendedWeight > 0 ->
                "Recommandé: ${exerciseSession.recommendedWeight.toInt()}kg"
            else -> {
                val suggested = calculateSuggestedStartingWeight(exerciseSession.machine, "Prise de masse")
                if (suggested > 0) "Suggestion: ${suggested.toInt()}kg" else "À déterminer"
            }
        }
    )
}
```

#### Affichage des suggestions :
```kotlin
// Afficher une suggestion si pas d'historique
if (exerciseSession.recommendedWeight == 0.0) {
    val suggestedWeight = calculateSuggestedStartingWeight(exerciseSession.machine, "Prise de masse")
    if (suggestedWeight > 0) {
        Text(
            text = "💡 Suggestion de départ: ${suggestedWeight.toInt()}kg",
            fontSize = 11.sp,
            color = Color(0xFF4CAF50),
            fontStyle = FontStyle.Italic
        )
    }
}
```

## 📊 Comportement par défaut

### **Sans historique** :
- ✅ Affiche "Poids à déterminer"
- ✅ Propose une suggestion basée sur le groupe musculaire
- ✅ Placeholder indique la suggestion
- ✅ Pas de confusion avec un poids calculé

### **Avec historique** :
- ✅ Calcule le poids recommandé basé sur le 1RM
- ✅ Affiche "Recommandé: X kg"
- ✅ Placeholder indique le poids recommandé
- ✅ S'adapte à la progression de l'utilisateur

### **Exercices cardio** :
- ✅ Retourne 0.0 (pas de poids)
- ✅ Affiche "Poids à déterminer"
- ✅ Pas de suggestion de poids

## 🔧 Fonctionnalités ajoutées

1. **Fonction `calculateSuggestedStartingWeight()`** : Calcule des suggestions basées sur le groupe musculaire
2. **Gestion d'erreur améliorée** : Placeholder "GIF non disponible" pour les images
3. **Logique de fallback** : Utilise `contains()` au lieu de `==` pour les groupes musculaires
4. **Interface plus claire** : Distinction visuelle entre recommandé et suggestion

## 🧪 Tests de validation

Le script `test_weight_calculation_logic.py` valide :
- ✅ Logique sans historique
- ✅ Logique avec historique
- ✅ Gestion cardio
- ✅ Suggestions basées sur groupes musculaires

## 🎯 Résultat final

L'application gère maintenant correctement :
- **Première utilisation** : Affiche "Poids à déterminer" + suggestion
- **Utilisations suivantes** : Calcule et affiche le poids recommandé
- **Progression** : S'adapte automatiquement aux performances
- **Interface claire** : L'utilisateur comprend la différence entre recommandé et suggestion