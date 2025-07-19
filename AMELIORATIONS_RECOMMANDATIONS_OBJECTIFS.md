# Améliorations des Recommandations selon les Objectifs

## Problème identifié

Les recommandations restaient toujours à 10 répétitions même pour les types "Puissance" ou "Endurance", ne prenant pas en compte les différents objectifs d'entraînement.

## Solutions implémentées

### 1. Mapping des objectifs amélioré

**Avant :**
```kotlin
val goalObjective = when (selectedGoal) {
    "Puissance" -> "Force"
    "Volume" -> "Prise de masse"
    "Endurance" -> "Endurance"
    else -> profileData.objectif
}
```

**Après :**
```kotlin
val goalObjective = when (selectedGoal) {
    "Puissance" -> "Puissance"
    "Volume" -> "Volume"
    "Endurance" -> "Endurance"
    else -> profileData.objectif
}
```

### 2. Logique de répétitions améliorée

**Nouvelle logique :**
```kotlin
val targetReps = when (objectif) {
    "Force", "Puissance" -> 4
    "Prise de masse", "Volume" -> 10
    "Endurance" -> 18
    "Sèche" -> 12
    "Maintenir" -> 10
    else -> 10
}
```

### 3. Sets et repos adaptés

**Sets et repos selon l'objectif :**
- **Puissance/Force** : 3-5 séries, repos 180-240s
- **Volume/Prise de masse** : 3-5 séries, repos 90-120s
- **Endurance** : 2-4 séries, repos 45-60s
- **Sèche** : 3-4 séries, repos 75-90s

### 4. Tempo adapté

**Tempo selon l'objectif :**
- **Puissance/Force** : "2-0-1" (explosif)
- **Volume/Prise de masse** : "3-1-2" (contrôlé)
- **Endurance** : "2-0-2" (régulier)
- **Sèche** : "2-0-2" (régulier)

### 5. Notes d'exercice améliorées

**Notes spécifiques selon l'objectif :**
- **Puissance/Force** : Technique, charges lourdes, repos complet
- **Volume/Prise de masse** : Tempo contrôlé, tension musculaire, échauffement
- **Endurance** : Rythme soutenu, charges modérées, repos courts
- **Sèche** : Intensité élevée, superset, brûlage maximal

### 6. Logs de débogage

Ajout de logs pour tracer l'objectif utilisé :
```kotlin
android.util.Log.d("Recommendation", "Objectif: $objectif, Machine: ${machine.nom}")
android.util.Log.d("Recommendation", "TargetReps: $targetReps")
```

## Résultats attendus

Maintenant, les recommandations devraient être :

- **Puissance** : 4 reps, 3-5 séries, repos 180-240s
- **Volume** : 10 reps, 3-5 séries, repos 90-120s
- **Endurance** : 18 reps, 2-4 séries, repos 45-60s

## Test

Pour vérifier que les améliorations fonctionnent :
1. Choisir un objectif (Puissance/Volume/Endurance)
2. Commencer un entraînement
3. Vérifier que les recommandations correspondent à l'objectif choisi
4. Consulter les logs pour confirmer l'objectif utilisé