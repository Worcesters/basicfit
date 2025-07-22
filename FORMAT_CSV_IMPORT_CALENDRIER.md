# 📋 Format CSV pour l'Import dans le Calendrier

## 🎯 Format Attendu

Le fichier CSV doit contenir les colonnes suivantes (séparées par `;` ou `,`) :

### **Format Principal (4 colonnes)**
```csv
Machine;Date;Répétitions;Séries
Développé couché;2024-01-15;10-12;3
Squat;2024-01-15;8-10;4
Tapis de course;2024-01-16;30;1
```

### **Format Étendu (5 colonnes)**
```csv
Machine;Date;Répétitions;Séries;Poids
Développé couché;2024-01-15;10-12;3;60
Squat;2024-01-15;8-10;4;80
Tapis de course;2024-01-16;30;1;0
```

## 📊 Détails des Colonnes

### **1. Machine** (Obligatoire)
- **Nom exact** de la machine/exercice
- **Exemples** : "Développé couché", "Squat", "Tapis de course", "Plank"

### **2. Date** (Obligatoire)
- **Formats acceptés** :
  - `2024-01-15` (format ISO)
  - `15/01/2024` (format français)
  - `15-01-2024` (format avec tirets)

### **3. Répétitions** (Obligatoire)
- **Valeur unique** : `10`, `12`, `15`
- **Plage** : `10-12` (sera convertie en moyenne : 11)
- **Pour cardio** : Durée en minutes (ex: `30` pour 30 minutes)

### **4. Séries** (Obligatoire)
- **Nombre de séries** : `1`, `3`, `4`, `5`
- **Pour cardio** : Généralement `1`

### **5. Poids** (Optionnel)
- **Poids utilisé** en kg : `60`, `80`, `0`
- **Pour cardio** : Généralement `0`

## 📝 Exemples Complets

### **Exemple 1 : Séance Musculation**
```csv
Machine;Date;Répétitions;Séries;Poids
Développé couché;2024-01-15;10-12;3;60
Squat;2024-01-15;8-10;4;80
Presse à cuisses;2024-01-15;12-15;3;100
```

### **Exemple 2 : Séance Cardio**
```csv
Machine;Date;Répétitions;Séries;Poids
Tapis de course;2024-01-16;30;1;0
Vélo elliptique;2024-01-16;20;1;0
Rameur;2024-01-16;15;1;0
```

### **Exemple 3 : Séance Mixte**
```csv
Machine;Date;Répétitions;Séries;Poids
Développé couché;2024-01-17;10-12;3;65
Tapis de course;2024-01-17;20;1;0
Squat;2024-01-17;8-10;4;85
```

## 🔧 Fonctionnement de l'Import

### **Parsing Intelligent**
- **Séparateurs** : `;` ou `,` automatiquement détectés
- **Dates** : Formats multiples supportés
- **Répétitions** : Plages converties en moyenne
- **Poids** : Valeur par défaut `0` si manquante

### **Gestion des Erreurs**
- **Lignes invalides** : Ignorées silencieusement
- **Dates invalides** : Entrées ignorées
- **Valeurs manquantes** : Valeurs par défaut utilisées

### **Regroupement Automatique**
- **Par date** : Tous les exercices d'une même date sont regroupés
- **Séance unique** : Création d'une séance "Import CSV" par date

## 📱 Utilisation dans l'App

### **1. Préparer le fichier CSV**
```csv
Machine;Date;Répétitions;Séries;Poids
Développé couché;2024-01-15;10-12;3;60
Squat;2024-01-15;8-10;4;80
```

### **2. Importer dans l'app**
1. Aller dans l'onglet **Calendrier**
2. Cliquer sur **"📂 Importer CSV"**
3. Sélectionner le fichier CSV
4. Confirmation automatique

### **3. Résultat**
- **Séances créées** : Une séance par date dans le calendrier
- **Exercices ajoutés** : Tous les exercices du CSV
- **Poids enregistrés** : Valeurs importées ou 0 par défaut

## ⚠️ Points Importants

### **Noms de Machines**
- **Utiliser les noms exacts** des machines de l'app
- **Exporter d'abord** la liste des machines pour avoir les bons noms
- **Respecter la casse** : "Développé couché" et non "développé couché"

### **Format de Date**
- **Préférer le format ISO** : `2024-01-15`
- **Éviter les formats ambigus** : `01/02/2024` (jour/mois ou mois/jour ?)

### **Valeurs Numériques**
- **Utiliser des points** pour les décimales : `60.5`
- **Pas de virgules** dans les nombres
- **Poids en kg** uniquement

---

**💡 Conseil** : Exportez d'abord la liste des machines depuis l'app pour avoir les noms exacts à utiliser dans votre CSV !