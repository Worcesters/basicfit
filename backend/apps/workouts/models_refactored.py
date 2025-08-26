"""
Modèles refactorisés pour séparer les séances effectuées du calendrier de planification
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta

from apps.core.models import TimeStampedModel
from apps.users.models import User
from apps.machines.models import Machine
from apps.core.models import ModeEntrainement


class SeanceEffectuee(TimeStampedModel):
    """
    Modèle pour les séances d'entraînement réellement effectuées
    Utilisé pour l'analyse intelligente et les recommandations
    """
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seances_effectuees',
        verbose_name="Utilisateur"
    )
    
    # Informations de la séance
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la séance"
    )
    date_debut = models.DateTimeField(
        verbose_name="Date de début"
    )
    date_fin = models.DateTimeField(
        verbose_name="Date de fin"
    )
    
    # Métriques générales
    volume_total = models.FloatField(
        default=0.0,
        help_text="Volume total (poids × reps × séries) de toute la séance",
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
    
    # Ressenti utilisateur
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
    
    class Meta:
        verbose_name = "Séance effectuée"
        verbose_name_plural = "Séances effectuées"
        ordering = ['-date_debut']
        indexes = [
            models.Index(fields=['utilisateur', 'date_debut']),
            models.Index(fields=['date_debut']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def duree_minutes(self):
        """Calcule la durée de la séance en minutes"""
        if self.date_debut and self.date_fin:
            delta = self.date_fin - self.date_debut
            return int(delta.total_seconds() / 60)
        return 0
    
    @property
    def date_seance(self):
        """Date de la séance (jour seulement)"""
        return self.date_debut.date()


class ExerciceEffectue(TimeStampedModel):
    """
    Modèle pour un exercice effectué dans une séance
    """
    seance = models.ForeignKey(
        SeanceEffectuee,
        on_delete=models.CASCADE,
        related_name='exercices',
        verbose_name="Séance"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    
    # Configuration réalisée
    nom_exercice = models.CharField(
        max_length=200,
        verbose_name="Nom de l'exercice"
    )
    ordre_dans_seance = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre dans la séance"
    )
    
    # Performance globale de l'exercice
    series_realisees = models.PositiveIntegerField(
        verbose_name="Séries réalisées"
    )
    repetitions_totales = models.PositiveIntegerField(
        verbose_name="Répétitions totales"
    )
    poids_moyen = models.FloatField(
        verbose_name="Poids moyen utilisé (kg)"
    )
    repos_moyen = models.PositiveIntegerField(
        default=90,
        help_text="Repos moyen entre séries en secondes",
        verbose_name="Repos moyen (s)"
    )
    
    # Métriques calculées
    volume_exercice = models.FloatField(
        default=0.0,
        help_text="Volume total de cet exercice",
        verbose_name="Volume exercice"
    )
    tonnage_exercice = models.FloatField(
        default=0.0,
        help_text="Tonnage de cet exercice",
        verbose_name="Tonnage exercice"
    )
    
    # Performance et réussite
    taux_reussite = models.FloatField(
        default=100.0,
        help_text="Pourcentage de réussite des séries prévues",
        verbose_name="Taux de réussite (%)"
    )
    charge_max_estimee = models.FloatField(
        null=True,
        blank=True,
        help_text="1RM estimé avec formule de Brzycki",
        verbose_name="1RM estimé (kg)"
    )
    
    class Meta:
        verbose_name = "Exercice effectué"
        verbose_name_plural = "Exercices effectués"
        ordering = ['seance', 'ordre_dans_seance']
    
    def __str__(self):
        return f"{self.nom_exercice} - {self.seance}"
    
    def calculer_metriques(self):
        """Calcule les métriques de l'exercice"""
        self.tonnage_exercice = self.poids_moyen * self.repetitions_totales
        self.volume_exercice = self.tonnage_exercice * self.series_realisees
        
        # Calcul du 1RM si on a les données
        if self.series_realisees > 0:
            reps_moyenne = self.repetitions_totales / self.series_realisees
            if reps_moyenne < 37:
                self.charge_max_estimee = round(
                    self.poids_moyen * (36 / (37 - reps_moyenne)), 2
                )
    
    def save(self, *args, **kwargs):
        """Override save pour calculer les métriques automatiquement"""
        self.calculer_metriques()
        super().save(*args, **kwargs)


class SerieEffectuee(TimeStampedModel):
    """
    Modèle pour une série effectuée d'un exercice
    """
    exercice = models.ForeignKey(
        ExerciceEffectue,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name="Exercice"
    )
    numero_serie = models.PositiveIntegerField(
        verbose_name="Numéro de série"
    )
    
    # Performance de la série
    repetitions_realisees = models.PositiveIntegerField(
        verbose_name="Répétitions réalisées"
    )
    repetitions_prevues = models.PositiveIntegerField(
        verbose_name="Répétitions prévues"
    )
    poids_utilise = models.FloatField(
        verbose_name="Poids utilisé (kg)"
    )
    repos_apres_serie = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Repos après cette série en secondes",
        verbose_name="Repos après série (s)"
    )
    
    # Métriques
    duree_serie = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée de la série en secondes",
        verbose_name="Durée série (s)"
    )
    note_effort = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Note d'effort perçu (RPE)",
        verbose_name="Note d'effort"
    )
    
    class Meta:
        verbose_name = "Série effectuée"
        verbose_name_plural = "Séries effectuées"
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


class CalendrierSeance(TimeStampedModel):
    """
    Modèle pour la planification/calendrier des séances
    Séparé des séances effectuées pour éviter la confusion
    """
    STATUTS_PLANIFICATION = [
        ('PLANIFIEE', 'Planifiée'),
        ('EN_COURS', 'En cours'),
        ('REPORTEE', 'Reportée'),
        ('ANNULEE', 'Annulée'),
        ('TERMINEE', 'Terminée'),  # Lien vers SeanceEffectuee créé
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='calendrier_seances',
        verbose_name="Utilisateur"
    )
    
    # Planification
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la séance planifiée"
    )
    date_prevue = models.DateTimeField(
        verbose_name="Date prévue"
    )
    duree_prevue = models.PositiveIntegerField(
        default=60,
        help_text="Durée prévue en minutes",
        verbose_name="Durée prévue (min)"
    )
    
    # Mode d'entraînement planifié
    mode_entrainement = models.ForeignKey(
        ModeEntrainement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Mode d'entraînement"
    )
    
    # Statut
    statut = models.CharField(
        max_length=15,
        choices=STATUTS_PLANIFICATION,
        default='PLANIFIEE',
        verbose_name="Statut"
    )
    
    # Lien vers la séance effectuée si réalisée
    seance_effectuee = models.OneToOneField(
        SeanceEffectuee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='planification_origine',
        verbose_name="Séance effectuée"
    )
    
    # Notes
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    commentaire = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )
    
    class Meta:
        verbose_name = "Séance planifiée"
        verbose_name_plural = "Séances planifiées"
        ordering = ['-date_prevue']
        indexes = [
            models.Index(fields=['utilisateur', 'date_prevue']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.date_prevue.strftime('%d/%m/%Y %H:%M')}"
    
    def marquer_comme_effectuee(self, seance_effectuee):
        """Marque cette planification comme réalisée"""
        self.statut = 'TERMINEE'
        self.seance_effectuee = seance_effectuee
        self.save()


class ExercicePlanifie(TimeStampedModel):
    """
    Modèle pour les exercices planifiés dans le calendrier
    """
    calendrier_seance = models.ForeignKey(
        CalendrierSeance,
        on_delete=models.CASCADE,
        related_name='exercices_planifies',
        verbose_name="Séance planifiée"
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )
    
    # Planification
    ordre_prevu = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre prévu"
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
        verbose_name="Poids prévu (kg)"
    )
    repos_prevu = models.PositiveIntegerField(
        default=90,
        help_text="Repos prévu entre séries en secondes",
        verbose_name="Repos prévu (s)"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    
    class Meta:
        verbose_name = "Exercice planifié"
        verbose_name_plural = "Exercices planifiés"
        ordering = ['calendrier_seance', 'ordre_prevu']
    
    def __str__(self):
        return f"{self.machine.nom} - {self.calendrier_seance}"