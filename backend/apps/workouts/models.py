"""
Modèles pour les séances d'entraînement et la progression dans BasicFit
"""
import math
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from apps.core.models import TimeStampedModel
from apps.users.models import User
from apps.machines.models import Machine, VarianteMachine
from apps.core.models import ModeEntrainement


class SeanceEntrainement(TimeStampedModel):
    """
    Modèle pour une séance d'entraînement complète
    """
    STATUTS_SEANCE = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
        ('SUSPENDUE', 'Suspendue'),
    ]

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seances',
        verbose_name="Utilisateur"
    )
    mode_entrainement = models.ForeignKey(
        ModeEntrainement,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Mode d'entraînement"
    )
    nom = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nom de la séance"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    # Dates et durées
    date_prevue = models.DateTimeField(
        verbose_name="Date prévue"
    )
    date_debut = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de début"
    )
    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    duree_prevue = models.PositiveIntegerField(
        default=60,
        help_text="Durée prévue en minutes",
        verbose_name="Durée prévue (min)"
    )

    # Statut et métriques
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_SEANCE,
        default='PLANIFIEE',
        verbose_name="Statut"
    )
    note_ressenti = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note de ressenti de 1 à 10",
        verbose_name="Note de ressenti"
    )
    note_difficulte = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note de difficulté de 1 à 10",
        verbose_name="Note de difficulté"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    # Métriques physiques
    poids_utilisateur = models.FloatField(
        null=True,
        blank=True,
        help_text="Poids au moment de la séance en kg",
        verbose_name="Poids (kg)"
    )
    frequence_cardiaque_repos = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque au repos",
        verbose_name="FC repos (bpm)"
    )
    frequence_cardiaque_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque maximale atteinte",
        verbose_name="FC max (bpm)"
    )

    # Données calculées
    volume_total = models.FloatField(
        default=0.0,
        help_text="Volume total de la séance (poids × reps × séries)",
        verbose_name="Volume total"
    )
    tonnage_total = models.FloatField(
        default=0.0,
        help_text="Tonnage total soulevé en kg",
        verbose_name="Tonnage total (kg)"
    )
    nombre_exercices = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre d'exercices"
    )
    nombre_series_totales = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de séries totales"
    )

    # Métadonnées
    salle = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Salle"
    )
    partenaire_entrainement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Partenaire d'entraînement"
    )
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Température en degrés Celsius",
        verbose_name="Température (°C)"
    )

    class Meta:
        verbose_name = "Séance d'entraînement"
        verbose_name_plural = "Séances d'entraînement"
        ordering = ['-date_prevue']
        indexes = [
            models.Index(fields=['utilisateur', 'date_prevue']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        if self.nom:
            return f"{self.nom} - {self.date_prevue.strftime('%d/%m/%Y')}"
        return f"Séance du {self.date_prevue.strftime('%d/%m/%Y')}"

    @property
    def duree_reelle(self):
        """Calcule la durée réelle de la séance en minutes"""
        if self.date_debut and self.date_fin:
            delta = self.date_fin - self.date_debut
            return int(delta.total_seconds() / 60)
        return None

    @property
    def est_terminee(self):
        """Vérifie si la séance est terminée"""
        return self.statut == 'TERMINEE'

    def commencer_seance(self):
        """Démarre la séance"""
        self.date_debut = timezone.now()
        self.statut = 'EN_COURS'
        self.save(update_fields=['date_debut', 'statut'])

    def terminer_seance(self):
        """Termine la séance et calcule les métriques"""
        self.date_fin = timezone.now()
        self.statut = 'TERMINEE'
        self.calculer_metriques()
        self.save()

    def calculer_metriques(self):
        """Calcule les métriques de la séance"""
        exercices = self.exercices.all()

        self.nombre_exercices = exercices.count()
        self.nombre_series_totales = sum(ex.nombre_series for ex in exercices)
        self.volume_total = sum(ex.volume_total for ex in exercices)
        self.tonnage_total = sum(ex.tonnage_total for ex in exercices)


class ExerciceSeance(TimeStampedModel):
    """
    Modèle pour un exercice dans une séance
    """
    STATUTS_EXERCICE = [
        ('PLANIFIE', 'Planifié'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ECHOUE', 'Échoué'),
        ('ABANDONNE', 'Abandonné'),
    ]

    seance = models.ForeignKey(
        SeanceEntrainement,
        on_delete=models.CASCADE,
        related_name='exercices',
        verbose_name="Séance"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    variante = models.ForeignKey(
        VarianteMachine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Variante"
    )

    # Configuration de l'exercice
    ordre_dans_seance = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre dans la séance"
    )
    series_prevues = models.PositiveIntegerField(
        default=3,
        verbose_name="Séries prévues"
    )
    repetitions_prevues = models.PositiveIntegerField(
        default=10,
        verbose_name="Répétitions prévues"
    )
    poids_prevu = models.FloatField(
        help_text="Poids prévu en kg",
        verbose_name="Poids prévu (kg)"
    )
    repos_prevu = models.PositiveIntegerField(
        default=90,
        help_text="Repos prévu entre séries en secondes",
        verbose_name="Repos prévu (s)"
    )

    # Résultats
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_EXERCICE,
        default='PLANIFIE',
        verbose_name="Statut"
    )
    nombre_series = models.PositiveIntegerField(
        default=0,
        verbose_name="Séries réalisées"
    )
    repetitions_realisees = models.PositiveIntegerField(
        default=0,
        verbose_name="Répétitions totales réalisées"
    )
    poids_utilise = models.FloatField(
        null=True,
        blank=True,
        help_text="Poids réellement utilisé en kg",
        verbose_name="Poids utilisé (kg)"
    )

    # Métriques calculées
    volume_total = models.FloatField(
        default=0.0,
        help_text="Volume total (poids × reps × séries)",
        verbose_name="Volume total"
    )
    tonnage_total = models.FloatField(
        default=0.0,
        help_text="Tonnage total soulevé",
        verbose_name="Tonnage total"
    )
    charge_maximale_theorique = models.FloatField(
        null=True,
        blank=True,
        help_text="1RM estimé avec formule de Brzycki",
        verbose_name="1RM estimé (kg)"
    )

    # Temps et ressenti
    duree_totale = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée totale de l'exercice en secondes",
        verbose_name="Durée totale (s)"
    )
    note_ressenti = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Note de ressenti"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Exercice de séance"
        verbose_name_plural = "Exercices de séances"
        ordering = ['seance', 'ordre_dans_seance']
        unique_together = ['seance', 'ordre_dans_seance']

    def __str__(self):
        variante = f" ({self.variante.nom})" if self.variante else ""
        return f"{self.machine.nom}{variante} - {self.seance}"

    def calculer_1rm_brzycki(self, poids=None, repetitions=None):
        """
        Calcule le 1RM estimé avec la formule de Brzycki
        1RM ≈ Poids × (36 / (37 - reps))
        """
        if poids is None:
            poids = self.poids_utilise
        if repetitions is None:
            # Prendre les répétitions moyennes par série
            if self.nombre_series > 0:
                repetitions = self.repetitions_realisees / self.nombre_series
            else:
                repetitions = self.repetitions_prevues

        if poids and repetitions and repetitions < 37:
            return round(poids * (36 / (37 - repetitions)), 2)
        return None

    def calculer_metriques(self):
        """Calcule toutes les métriques de l'exercice"""
        if self.poids_utilise and self.repetitions_realisees:
            self.tonnage_total = self.poids_utilise * self.repetitions_realisees
            self.volume_total = self.tonnage_total * self.nombre_series

            # Calcul du 1RM si on a les données
            if self.nombre_series > 0:
                reps_moyenne = self.repetitions_realisees / self.nombre_series
                self.charge_maximale_theorique = self.calculer_1rm_brzycki(
                    self.poids_utilise, reps_moyenne
                )

    def save(self, *args, **kwargs):
        """Override save pour calculer les métriques automatiquement"""
        self.calculer_metriques()
        super().save(*args, **kwargs)


class SeriExercice(TimeStampedModel):
    """
    Modèle pour une série d'un exercice
    """
    STATUTS_SERIE = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('REUSSIE', 'Réussie'),
        ('ECHOUEE', 'Échouée'),
        ('PARTIELLE', 'Partielle'),
    ]

    exercice = models.ForeignKey(
        ExerciceSeance,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name="Exercice"
    )
    numero_serie = models.PositiveIntegerField(
        verbose_name="Numéro de série"
    )

    # Prévisions
    repetitions_prevues = models.PositiveIntegerField(
        verbose_name="Répétitions prévues"
    )
    poids_prevu = models.FloatField(
        verbose_name="Poids prévu (kg)"
    )
    repos_prevu = models.PositiveIntegerField(
        default=90,
        help_text="Repos après cette série en secondes",
        verbose_name="Repos prévu (s)"
    )

    # Résultats
    repetitions_realisees = models.PositiveIntegerField(
        default=0,
        verbose_name="Répétitions réalisées"
    )
    poids_utilise = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Poids utilisé (kg)"
    )
    repos_reel = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Repos réel en secondes",
        verbose_name="Repos réel (s)"
    )

    # Métriques
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_SERIE,
        default='PLANIFIEE',
        verbose_name="Statut"
    )
    duree_serie = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée de la série en secondes",
        verbose_name="Durée série (s)"
    )
    frequence_cardiaque_apres = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Fréquence cardiaque après la série",
        verbose_name="FC après série (bpm)"
    )
    note_effort = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note d'effort perçu (RPE)",
        verbose_name="Note d'effort"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )

    class Meta:
        verbose_name = "Série d'exercice"
        verbose_name_plural = "Séries d'exercices"
        ordering = ['exercice', 'numero_serie']
        unique_together = ['exercice', 'numero_serie']

    def __str__(self):
        return f"Série {self.numero_serie} - {self.exercice}"

    @property
    def est_reussie(self):
        """Vérifie si la série est réussie (toutes les reps prévues)"""
        return self.repetitions_realisees >= self.repetitions_prevues

    @property
    def pourcentage_reussite(self):
        """Calcule le pourcentage de réussite de la série"""
        if self.repetitions_prevues > 0:
            return min(100, (self.repetitions_realisees / self.repetitions_prevues) * 100)
        return 0


class ProgressionMachine(TimeStampedModel):
    """
    Modèle pour suivre la progression sur une machine
    """
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progressions',
        verbose_name="Utilisateur"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    mode_entrainement = models.ForeignKey(
        ModeEntrainement,
        on_delete=models.CASCADE,
        verbose_name="Mode d'entraînement"
    )

    # Progression actuelle
    poids_actuel = models.FloatField(
        verbose_name="Poids actuel (kg)"
    )
    series_actuelles = models.PositiveIntegerField(
        default=3,
        verbose_name="Séries actuelles"
    )
    repetitions_actuelles = models.PositiveIntegerField(
        default=10,
        verbose_name="Répétitions actuelles"
    )

    # Dernière performance
    derniere_seance = models.ForeignKey(
        SeanceEntrainement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progressions_mises_a_jour',
        verbose_name="Dernière séance"
    )
    dernier_1rm = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Dernier 1RM (kg)"
    )

    # Métriques de progression
    nombre_seances_machine = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de séances sur cette machine"
    )
    progression_poids_total = models.FloatField(
        default=0.0,
        help_text="Progression totale en kg depuis le début",
        verbose_name="Progression poids total (kg)"
    )
    taux_reussite = models.FloatField(
        default=0.0,
        help_text="Taux de réussite en pourcentage",
        verbose_name="Taux de réussite (%)"
    )

    # Configuration de progression
    increment_automatique = models.BooleanField(
        default=True,
        verbose_name="Incrément automatique"
    )
    seuil_progression = models.FloatField(
        default=90.0,
        help_text="Seuil de réussite pour progression automatique (%)",
        verbose_name="Seuil de progression (%)"
    )

    # Dates importantes
    premiere_utilisation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Première utilisation"
    )
    derniere_progression = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière progression"
    )

    class Meta:
        verbose_name = "Progression sur machine"
        verbose_name_plural = "Progressions sur machines"
        unique_together = ['utilisateur', 'machine', 'mode_entrainement']
        ordering = ['utilisateur', 'machine']

    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.machine.nom} ({self.mode_entrainement})"

    def evaluer_progression(self, exercice_seance):
        """
        Évalue s'il faut progresser en poids basé sur la performance
        """
        if not self.increment_automatique:
            return False

        # Calculer le taux de réussite de cette séance
        series_reussies = 0
        for serie in exercice_seance.series.all():
            if serie.est_reussie:
                series_reussies += 1

        if exercice_seance.nombre_series > 0:
            taux_reussite_seance = (series_reussies / exercice_seance.nombre_series) * 100
        else:
            return False

        # Si le taux de réussite dépasse le seuil, on peut progresser
        if taux_reussite_seance >= self.seuil_progression:
            return True

        return False

    def progresser_poids(self):
        """Augmente le poids selon l'incrément de la machine"""
        increment = self.machine.increment_poids
        nouveau_poids = self.poids_actuel + increment

        if nouveau_poids <= self.machine.poids_maximum:
            ancien_poids = self.poids_actuel
            self.poids_actuel = nouveau_poids
            self.progression_poids_total += increment
            self.derniere_progression = timezone.now()
            self.save()

            return True, ancien_poids, nouveau_poids

        return False, self.poids_actuel, self.poids_actuel

    def recommander_prochaine_seance(self):
        """
        Recommande les paramètres pour la prochaine séance
        """
        series = self.mode_entrainement.series_recommandees
        repetitions = self.mode_entrainement.repetitions_recommandees

        return {
            'poids': self.poids_actuel,
            'series': series,
            'repetitions': repetitions,
            'repos': self.mode_entrainement.repos_entre_series,
        }